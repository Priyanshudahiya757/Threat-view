"""Ingestor for PhishTank's verified-phishing-URL feed.

PhishTank (operated by Cisco Talos) publishes a periodically-updated
JSON dump of phishing submissions. Anonymous polling is rate limited
(HTTP 509 once you're throttled); for a scheduled job like this one,
register a free application key at
https://www.phishtank.com/developer_info.php and point PHISHTANK_URL at
your personal keyed feed URL instead of the anonymous one.
"""
import logging
from typing import Any, Dict, List

from ingestors.base_ingestor import BaseIngestor
from services.normalization_service import build_threat_dict
from utils.http_client import build_http_session
from utils.threat_normalizer import extract_host_indicator

logger = logging.getLogger(__name__)


class PhishTankIngestor(BaseIngestor):
    source_name = "PhishTank"

    def __init__(self, feed_url: str, timeout: int = 15):
        self.feed_url = feed_url
        self.timeout = timeout
        self.session = build_http_session()

    def fetch(self) -> List[Dict[str, Any]]:
        # PhishTank explicitly asks integrators for a descriptive
        # User-Agent; blank or generic ones get rate limited harder.
        headers = {"User-Agent": "ThreatView-Ingestor/1.0 (threat intelligence aggregator)"}
        try:
            response = self.session.get(self.feed_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            try:
                return response.json()
            except Exception:
                logger.warning("PhishTank response could not be decoded as JSON from %s", self.feed_url, exc_info=True)
                return []
        except Exception:
            logger.warning("PhishTank feed unavailable at %s", self.feed_url, exc_info=True)
            # As a fallback, try the anonymous public feed endpoint if the
            # configured URL looks like a CDN or signed URL which may have
            # expired. This helps when users supply an app-key URL that has
            # rotating signatures or when PhishTank moved hosting.
            fallback = "https://data.phishtank.com/data/online-valid.json"
            if self.feed_url != fallback:
                try:
                    response = self.session.get(fallback, headers=headers, timeout=self.timeout)
                    response.raise_for_status()
                    try:
                        return response.json()
                    except Exception:
                        logger.warning("PhishTank fallback response not JSON from %s", fallback, exc_info=True)
                        return []
                except Exception:
                    logger.warning("PhishTank fallback also unavailable at %s", fallback, exc_info=True)
                    return []
            return []

    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        threats = []

        for entry in raw_data or []:
            url = entry.get("url")
            if not url:
                continue

            details = entry.get("details") or []
            country = details[0].get("country") if details else None
            is_verified = str(entry.get("verified", "")).strip().lower() in ("yes", "true", "y")
            target = entry.get("target") or "an unidentified brand"
            first_seen = entry.get("submission_time")
            last_seen = entry.get("verification_time") or entry.get("submission_time")
            url_confidence = 95 if is_verified else 60

            threats.append(
                build_threat_dict(
                    indicator=url,
                    indicator_type="URL",
                    source=self.source_name,
                    category="Phishing",
                    severity="high" if is_verified else "medium",
                    confidence=url_confidence,
                    country=country,
                    description=f"Phishing URL targeting {target}",
                    first_seen=first_seen,
                    last_seen=last_seen,
                )
            )

            host_info = extract_host_indicator(url)
            if host_info:
                host, host_type = host_info
                threats.append(
                    build_threat_dict(
                        indicator=host,
                        indicator_type=host_type,
                        source=self.source_name,
                        category="Phishing Host",
                        severity="medium",
                        confidence=max(30, url_confidence - 25),
                        country=country,
                        description=(
                            f"Host of a phishing URL targeting {target}. "
                            "Confirm before blocking the whole host if shared hosting is possible."
                        ),
                        first_seen=first_seen,
                        last_seen=last_seen,
                    )
                )

        return threats
