"""Alert engine: rule CRUD, evaluation, and notification dispatch."""
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import or_

from database.db import db
from models.alert import AlertEvent, AlertRule
from models.threat import Threat
from services.email_service import send_alert_email

logger = logging.getLogger(__name__)

_RECENT_EVENT_WINDOW_MINUTES = 60


def list_rules(active_only: bool = False) -> List[AlertRule]:
    query = AlertRule.query
    if active_only:
        query = query.filter(AlertRule.is_active.is_(True))
    return query.order_by(AlertRule.created_at.desc()).all()


def get_rule(rule_id: int) -> Optional[AlertRule]:
    return db.session.get(AlertRule, rule_id)


def create_rule(data: dict) -> AlertRule:
    rule = AlertRule(**data)
    db.session.add(rule)
    db.session.commit()
    logger.info("Created alert rule id=%s name=%s", rule.id, rule.name)
    return rule


def update_rule(rule_id: int, data: dict) -> Optional[AlertRule]:
    rule = get_rule(rule_id)
    if rule is None:
        return None
    for key, value in data.items():
        if hasattr(rule, key):
            setattr(rule, key, value)
    db.session.commit()
    return rule


def delete_rule(rule_id: int) -> bool:
    rule = get_rule(rule_id)
    if rule is None:
        return False
    db.session.delete(rule)
    db.session.commit()
    return True


def list_events(page: int = 1, per_page: int = 20, unread_only: bool = False):
    query = AlertEvent.query
    if unread_only:
        query = query.filter(AlertEvent.is_read.is_(False))
    query = query.order_by(AlertEvent.created_at.desc())
    return query.paginate(page=page, per_page=per_page, error_out=False)


def mark_event_read(event_id: int) -> Optional[AlertEvent]:
    event = db.session.get(AlertEvent, event_id)
    if event is None:
        return None
    event.is_read = True
    db.session.commit()
    return event


def mark_all_read() -> int:
    updated = AlertEvent.query.filter(AlertEvent.is_read.is_(False)).update({"is_read": True})
    db.session.commit()
    return updated


def unread_count() -> int:
    return AlertEvent.query.filter(AlertEvent.is_read.is_(False)).count()


def _matches_rule(threat: Threat, rule: AlertRule) -> bool:
    value = (rule.rule_value or "").strip().lower()
    if not value:
        return False

    if rule.rule_type == "severity":
        return (threat.severity or "").lower() == value
    if rule.rule_type == "malware_family":
        return value in (threat.malware_family or "").lower()
    if rule.rule_type == "ioc_type":
        return (threat.indicator_type or "").lower() == value
    if rule.rule_type == "country":
        return value in (threat.country or "").lower()
    if rule.rule_type == "industry":
        haystack = " ".join(
            filter(None, [threat.category, threat.description, threat.malware_family, threat.source])
        ).lower()
        return value in haystack
    if rule.rule_type == "keyword":
        haystack = " ".join(
            filter(
                None,
                [
                    threat.indicator,
                    threat.description,
                    threat.category,
                    threat.malware_family,
                    threat.country,
                    threat.source,
                ],
            )
        ).lower()
        return value in haystack
    return False


def _recent_duplicate(rule_id: Optional[int], threat_id: int, title: str) -> bool:
    from datetime import datetime, timedelta, timezone

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=_RECENT_EVENT_WINDOW_MINUTES)
    query = AlertEvent.query.filter(
        AlertEvent.threat_id == threat_id,
        AlertEvent.title == title,
        AlertEvent.created_at >= cutoff,
    )
    if rule_id is not None:
        query = query.filter(AlertEvent.rule_id == rule_id)
    return query.first() is not None


def _create_event(
    *,
    rule: Optional[AlertRule],
    threat: Threat,
    alert_type: str,
    title: str,
    message: str,
) -> Optional[AlertEvent]:
    if _recent_duplicate(rule.id if rule else None, threat.id, title):
        return None

    event = AlertEvent(
        rule_id=rule.id if rule else None,
        threat_id=threat.id,
        alert_type=alert_type,
        title=title,
        message=message,
        severity=threat.severity or "medium",
    )
    db.session.add(event)
    db.session.flush()

    notify_email = rule.notify_email if rule else False
    email = rule.email if rule else None
    if notify_email and email:
        sent = send_alert_email(email, title, message)
        event.email_sent = sent

    db.session.commit()
    logger.info("Alert event created: %s (threat_id=%s)", title, threat.id)
    return event


def evaluate_rules_for_threats(threats: List[Threat]) -> Dict[str, int]:
    """Evaluate all active alert rules against newly ingested threats."""
    rules = list_rules(active_only=True)
    if not rules or not threats:
        return {"events_created": 0}

    created = 0
    for threat in threats:
        for rule in rules:
            if _matches_rule(threat, rule):
                event = _create_event(
                    rule=rule,
                    threat=threat,
                    alert_type="rule",
                    title=f"Alert: {rule.name}",
                    message=(
                        f"Rule '{rule.name}' matched {threat.indicator_type} "
                        f"{threat.indicator} (severity={threat.severity}, source={threat.source})."
                    ),
                )
                if event:
                    created += 1
    return {"events_created": created}


def create_brand_alert(threat: Threat, domain: str, email: Optional[str], notify_email: bool) -> AlertEvent:
    title = f"Brand Alert: {domain} impersonation detected"
    message = (
        f"Your monitored domain '{domain}' appears in a phishing indicator: "
        f"{threat.indicator} (source={threat.source}, severity={threat.severity})."
    )
    event = AlertEvent(
        rule_id=None,
        threat_id=threat.id,
        alert_type="brand",
        title=title,
        message=message,
        severity=threat.severity or "high",
    )
    db.session.add(event)
    db.session.flush()
    if notify_email and email:
        event.email_sent = send_alert_email(email, title, message)
    db.session.commit()
    return event


def get_events_for_export(limit: int = 1000) -> List[AlertEvent]:
    return AlertEvent.query.order_by(AlertEvent.created_at.desc()).limit(limit).all()
