"""CSV export helpers for threats, search results, alerts, and statistics."""
import csv
from io import StringIO
from typing import Iterable, List, Optional

from models.alert import AlertEvent
from models.threat import Threat


THREAT_HEADERS = [
    "id",
    "indicator",
    "indicator_type",
    "reputation",
    "severity",
    "confidence",
    "malware_family",
    "category",
    "country",
    "source",
    "description",
    "first_seen",
    "last_seen",
    "created_at",
]

ALERT_HEADERS = ["id", "alert_type", "title", "message", "severity", "is_read", "email_sent", "created_at"]


def _format_dt(value) -> str:
    if value is None:
        return ""
    return value.isoformat()


def threats_to_csv(threats: Iterable[Threat]) -> str:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=THREAT_HEADERS)
    writer.writeheader()
    for threat in threats:
        writer.writerow(
            {
                "id": threat.id,
                "indicator": threat.indicator,
                "indicator_type": threat.indicator_type,
                "reputation": threat.reputation,
                "severity": threat.severity,
                "confidence": threat.confidence,
                "malware_family": threat.malware_family,
                "category": threat.category,
                "country": threat.country,
                "source": threat.source,
                "description": threat.description,
                "first_seen": _format_dt(threat.first_seen),
                "last_seen": _format_dt(threat.last_seen),
                "created_at": _format_dt(threat.created_at),
            }
        )
    return buffer.getvalue()


def alerts_to_csv(events: List[AlertEvent]) -> str:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=ALERT_HEADERS)
    writer.writeheader()
    for event in events:
        writer.writerow(
            {
                "id": event.id,
                "alert_type": event.alert_type,
                "title": event.title,
                "message": event.message,
                "severity": event.severity,
                "is_read": event.is_read,
                "email_sent": event.email_sent,
                "created_at": _format_dt(event.created_at),
            }
        )
    return buffer.getvalue()


def stats_to_csv(stats: dict) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["metric", "value"])
    writer.writerow(["total_threats", stats.get("total_threats", 0)])

    writer.writerow([])
    writer.writerow(["severity", "count"])
    for key, value in (stats.get("severity_distribution") or {}).items():
        writer.writerow([key, value])

    writer.writerow([])
    writer.writerow(["country", "count"])
    for row in stats.get("top_countries") or []:
        writer.writerow([row.get("name"), row.get("count")])

    writer.writerow([])
    writer.writerow(["malware_family", "count"])
    for row in stats.get("top_malware") or []:
        writer.writerow([row.get("name"), row.get("count")])

    return buffer.getvalue()
