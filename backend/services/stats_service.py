"""Aggregation queries backing GET /api/stats."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from database.db import db
from models.threat import Threat
from schemas.threat_schema import ThreatSchema

_threat_schema = ThreatSchema()

# Approximate map coordinates for common countries in threat data
_COUNTRY_COORDS = {
    "United States": {"lat": 37.09, "lng": -95.71, "code": "US"},
    "Russia": {"lat": 61.52, "lng": 105.32, "code": "RU"},
    "China": {"lat": 35.86, "lng": 104.19, "code": "CN"},
    "Germany": {"lat": 51.16, "lng": 10.45, "code": "DE"},
    "Netherlands": {"lat": 52.13, "lng": 5.29, "code": "NL"},
    "United Kingdom": {"lat": 55.37, "lng": -3.43, "code": "GB"},
    "France": {"lat": 46.22, "lng": 2.21, "code": "FR"},
    "India": {"lat": 20.59, "lng": 78.96, "code": "IN"},
    "Brazil": {"lat": -14.23, "lng": -51.92, "code": "BR"},
    "Iran": {"lat": 32.42, "lng": 53.68, "code": "IR"},
    "Ukraine": {"lat": 48.37, "lng": 31.16, "code": "UA"},
    "Canada": {"lat": 56.13, "lng": -106.34, "code": "CA"},
    "Vietnam": {"lat": 14.05, "lng": 108.27, "code": "VN"},
    "Poland": {"lat": 51.91, "lng": 19.14, "code": "PL"},
}


def _base_query():
    return Threat.query


def get_stats() -> dict:
    total_threats = _base_query().count()

    severity_rows = (
        db.session.query(Threat.severity, func.count(Threat.id))
        .filter(Threat.id.in_(_base_query().with_entities(Threat.id)))
        .group_by(Threat.severity)
        .all()
    )
    severity_distribution = {severity: count for severity, count in severity_rows}

    latest_threats = _base_query().order_by(Threat.created_at.desc()).limit(5).all()

    return {
        "total_threats": total_threats,
        "severity_distribution": severity_distribution,
        "top_countries": _top_n(Threat.country),
        "top_categories": _top_n(Threat.category),
        "top_malware": _top_n(Threat.malware_family),
        "latest_threats": _threat_schema.dump(latest_threats, many=True),
    }


def get_malware_trends(days: int = 14) -> list:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    query = _base_query().filter(Threat.created_at >= cutoff, Threat.malware_family.isnot(None))

    rows = (
        db.session.query(Threat.malware_family, func.count(Threat.id).label("count"))
        .filter(Threat.id.in_(query.with_entities(Threat.id)))
        .group_by(Threat.malware_family)
        .order_by(func.count(Threat.id).desc())
        .limit(10)
        .all()
    )
    return [{"name": name, "count": count} for name, count in rows]


def get_threat_map() -> list:
    countries = _top_n(Threat.country, limit=20)
    points = []
    for entry in countries:
        name = entry["name"]
        coords = _COUNTRY_COORDS.get(name)
        if coords:
            points.append(
                {
                    "country": name,
                    "code": coords["code"],
                    "lat": coords["lat"],
                    "lng": coords["lng"],
                    "count": entry["count"],
                }
            )
        else:
            points.append({"country": name, "code": None, "lat": None, "lng": None, "count": entry["count"]})
    return points


def get_malware_trends_timeseries(days: int = 14, top_n: int = 6) -> dict:
    """Return per-day counts for the top-N malware families over the last
    `days` days, in a format ready for a stacked area/bar chart.

    Returns
    -------
    {
      "dates": ["2024-01-01", ...],
      "families": ["Mirai", "Emotet", ...],
      "series": [
        {"date": "2024-01-01", "Mirai": 4, "Emotet": 2, ...},
        ...
      ]
    }
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # 1. Find top-N families by total count over the window
    top_families_rows = (
        db.session.query(Threat.malware_family, func.count(Threat.id).label("cnt"))
        .filter(Threat.created_at >= cutoff, Threat.malware_family.isnot(None))
        .group_by(Threat.malware_family)
        .order_by(func.count(Threat.id).desc())
        .limit(top_n)
        .all()
    )
    families = [row.malware_family for row in top_families_rows]
    if not families:
        return {"dates": [], "families": [], "series": []}

    # 2. Build a date spine for the window
    today = datetime.now(timezone.utc).date()
    spine = [(today - timedelta(days=i)) for i in range(days - 1, -1, -1)]
    date_strs = [d.isoformat() for d in spine]

    # 3. Query daily counts for each family
    rows = (
        db.session.query(
            func.date(Threat.created_at).label("day"),
            Threat.malware_family,
            func.count(Threat.id).label("cnt"),
        )
        .filter(
            Threat.created_at >= cutoff,
            Threat.malware_family.in_(families),
        )
        .group_by(func.date(Threat.created_at), Threat.malware_family)
        .all()
    )

    # 4. Pivot into a dict keyed by (day_str, family)
    lookup: dict = {}
    for row in rows:
        day_str = str(row.day)[:10]  # ensure YYYY-MM-DD
        lookup[(day_str, row.malware_family)] = row.cnt

    # 5. Build the series array
    series = []
    for d in date_strs:
        entry = {"date": d}
        for fam in families:
            entry[fam] = lookup.get((d, fam), 0)
        series.append(entry)

    return {"dates": date_strs, "families": families, "series": series}


def _top_n(column, limit: int = 10) -> list:
    rows = (
        db.session.query(column, func.count(Threat.id).label("count"))
        .filter(column.isnot(None))
        .filter(Threat.id.in_(_base_query().with_entities(Threat.id)))
        .group_by(column)
        .order_by(func.count(Threat.id).desc())
        .limit(limit)
        .all()
    )
    return [{"name": value, "count": count} for value, count in rows]
