"""Brand monitoring against phishing feed indicators."""
import logging
from typing import Dict, List, Optional

from database.db import db
from models.brand_monitor import BrandMonitor
from services import alert_service, threat_service

logger = logging.getLogger(__name__)


def list_monitors(active_only: bool = False) -> List[BrandMonitor]:
    query = BrandMonitor.query
    if active_only:
        query = query.filter(BrandMonitor.is_active.is_(True))
    return query.order_by(BrandMonitor.created_at.desc()).all()


def get_monitor(monitor_id: int) -> Optional[BrandMonitor]:
    return db.session.get(BrandMonitor, monitor_id)


def create_monitor(data: dict) -> BrandMonitor:
    domain = data["company_domain"].strip().lower().removeprefix("www.")
    monitor = BrandMonitor(company_domain=domain, **{k: v for k, v in data.items() if k != "company_domain"})
    db.session.add(monitor)
    db.session.commit()
    logger.info("Brand monitor created for domain=%s", domain)
    return monitor


def delete_monitor(monitor_id: int) -> bool:
    monitor = get_monitor(monitor_id)
    if monitor is None:
        return False
    db.session.delete(monitor)
    db.session.commit()
    return True


def _indicator_contains_domain(indicator: str, domain: str) -> bool:
    text = (indicator or "").lower()
    needle = domain.lower()
    return needle in text


def evaluate_brand_monitors() -> Dict[str, int]:
    monitors = list_monitors(active_only=True)
    if not monitors:
        return {"alerts_created": 0}

    indicators = threat_service.get_phishing_indicators()
    created = 0

    for monitor in monitors:
        domain = monitor.company_domain
        for threat in indicators:
            if _indicator_contains_domain(threat.indicator, domain):
                title = f"Brand Alert: {domain} impersonation detected"
                if alert_service._recent_duplicate(None, threat.id, title):
                    continue
                alert_service.create_brand_alert(
                    threat,
                    domain,
                    monitor.email,
                    monitor.notify_email,
                )
                created += 1

    logger.info("Brand monitor evaluation complete: alerts_created=%d", created)
    return {"alerts_created": created}
