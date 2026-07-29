"""Data-access layer for the Threat resource. Routes and scheduler jobs
call into this module instead of touching SQLAlchemy directly, so query
construction and the ingest-time dedup logic live in exactly one place.
"""
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import g
from sqlalchemy import or_

from database.db import db
from models.threat import Threat
from services.normalization_service import detect_indicator_type

logger = logging.getLogger(__name__)


def _apply_history_window(query):
    cutoff = getattr(g, "history_cutoff", None)
    if cutoff is not None:
        query = query.filter(Threat.created_at >= cutoff)
    return query


def upsert_threats(threat_dicts: List[Dict[str, Any]]) -> Dict[str, int]:
    """Insert indicators we haven't seen before; for ones we have,
    refresh last_seen/confidence/severity instead of creating a
    duplicate row.
    """
    if not threat_dicts:
        return {"inserted": 0, "updated": 0}

    source = threat_dicts[0]["source"]
    incoming_indicators = {t["indicator"] for t in threat_dicts}

    existing_rows = Threat.query.filter(
        Threat.source == source, Threat.indicator.in_(incoming_indicators)
    ).all()
    existing_by_indicator = {row.indicator: row for row in existing_rows}

    inserted, updated = 0, 0
    new_rows = []

    for data in threat_dicts:
        existing = existing_by_indicator.get(data["indicator"])
        if existing:
            existing.last_seen = data["last_seen"]
            existing.confidence = data["confidence"]
            existing.severity = data["severity"]
            existing.reputation = data.get("reputation") or existing.reputation
            existing.malware_family = data.get("malware_family") or existing.malware_family
            existing.description = data["description"] or existing.description
            updated += 1
        else:
            new_rows.append(Threat(**data))
            inserted += 1

    if new_rows:
        db.session.bulk_save_objects(new_rows)
    db.session.commit()

    logger.info("upsert_threats[%s]: inserted=%d updated=%d", source, inserted, updated)
    return {"inserted": inserted, "updated": updated}


def get_threat_by_id(threat_id: int) -> Optional[Threat]:
    query = Threat.query.filter(Threat.id == threat_id)
    query = _apply_history_window(query)
    return query.first()


def query_threats(
    page: int = 1,
    per_page: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
    severity: Optional[str] = None,
    indicator_type: Optional[str] = None,
    source: Optional[str] = None,
    category: Optional[str] = None,
    country: Optional[str] = None,
    malware_family: Optional[str] = None,
    reputation: Optional[str] = None,
    since: Optional[datetime] = None,
):
    """Filtered, sorted, paginated threat listing backing GET /api/threats."""
    query = Threat.query
    query = _apply_history_window(query)

    if severity:
        query = query.filter(Threat.severity == severity)
    if indicator_type:
        query = query.filter(Threat.indicator_type == indicator_type)
    if source:
        query = query.filter(Threat.source.ilike(source))
    if category:
        query = query.filter(Threat.category.ilike(category))
    if country:
        query = query.filter(Threat.country.ilike(country))
    if malware_family:
        query = query.filter(Threat.malware_family.ilike(f"%{malware_family}%"))
    if reputation:
        query = query.filter(Threat.reputation == reputation)
    if since:
        query = query.filter(Threat.created_at >= since)

    sort_column = getattr(Threat, sort_by, Threat.created_at)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    return query.paginate(page=page, per_page=per_page, error_out=False)


def search_threats(
    term: str,
    page: int = 1,
    per_page: int = 20,
    indicator_type: Optional[str] = None,
    reputation: Optional[str] = None,
):
    """Search IOCs by value with optional type and reputation filters."""
    like_term = f"%{term}%"
    query = Threat.query.filter(
        or_(
            Threat.indicator.ilike(like_term),
            Threat.description.ilike(like_term),
            Threat.category.ilike(like_term),
            Threat.country.ilike(like_term),
            Threat.malware_family.ilike(like_term),
        )
    )
    query = _apply_history_window(query)

    if indicator_type:
        query = query.filter(Threat.indicator_type == indicator_type)
    else:
        detected = detect_indicator_type(term.strip())
        if detected != "URL":
            query = query.filter(Threat.indicator_type == detected)

    if reputation:
        query = query.filter(Threat.reputation == reputation)

    query = query.order_by(Threat.created_at.desc())
    return query.paginate(page=page, per_page=per_page, error_out=False)


def get_recent_threats(limit: int = 10) -> List[Threat]:
    query = Threat.query.order_by(Threat.created_at.desc())
    query = _apply_history_window(query)
    return query.limit(limit).all()


def get_threats_for_export(filters: Optional[dict] = None) -> List[Threat]:
    query = Threat.query
    query = _apply_history_window(query)
    filters = filters or {}

    for field in ("severity", "indicator_type", "source", "country", "reputation"):
        value = filters.get(field)
        if value:
            query = query.filter(getattr(Threat, field).ilike(value) if field in ("source",) else getattr(Threat, field) == value)

    return query.order_by(Threat.created_at.desc()).all()


def get_phishing_indicators(limit: int = 500) -> List[Threat]:
    """Return recent phishing-related indicators for brand monitoring."""
    query = Threat.query.filter(
        or_(
            Threat.source.ilike("%PhishTank%"),
            Threat.category.ilike("%phish%"),
            Threat.indicator_type.in_(["Domain", "URL", "Email"]),
        )
    ).order_by(Threat.created_at.desc())
    return query.limit(limit).all()
