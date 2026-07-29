"""Ingestor for abuse.ch's URLhaus recent-malware-URLs feed.

abuse.ch requires an Auth-Key on every API call (free at
https://auth.abuse.ch/) since their platform-wide authentication
rollout -- requests without one are rejected with a 401.

API reference: https://urlhaus.abuse.ch/api/
Endpoint used here: GET /v1/urls/recent/limit/<n>/, header `Auth-Key`.
"""
import logging
from typing import Any, Dict, List

from ingestors.base_ingestor import BaseIngestor
from services.normalization_service import build_threat_dict
from utils.http_client import build_http_session
from utils.threat_normalizer import classify_host

logger = logging.getLogger(__name__)


class URLhausIngestor(BaseIngestor):
    source_name = "URLhaus"

    def __init__(self, feed_url: str, auth_key: str, limit: int = 1000, timeout: int = 15):
        self.feed_url = feed_url.rstrip("/")
        self.auth_key = auth_key
        self.limit = limit
        self.timeout = timeout
        self.session = build_http_session()

    def fetch(self) -> Dict[str, Any]:
        if not self.auth_key:
            logger.warning("Skipping URLhaus fetch: URLHAUS_AUTH_KEY is not configured")
            return {"query_status": "missing-auth-key", "urls": []}

        url = f"{self.feed_url}/limit/{self.limit}/"
        headers = {"Auth-Key": self.auth_key}
        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except Exception:
            logger.warning("URLhaus request failed for %s", url, exc_info=True)
            return {"query_status": "unavailable", "urls": []}
        return response.json()

    def normalize(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        if raw_data.get("query_status") != "ok":
            logger.warning("URLhaus returned query_status=%s", raw_data.get("query_status"))
            return []

        threats = []

        for entry in raw_data.get("urls", []):
            url = entry.get("url")
            if not url:
                continue

            tags = entry.get("tags") or []
            is_online = entry.get("url_status") == "online"
            category = entry.get("threat") or "malware_download"
            date_added = entry.get("date_added")
            tag_text = ", ".join(tags) if tags else "none"

            threats.append(
                build_threat_dict(
                    indicator=url,
                    indicator_type="URL",
                    source=self.source_name,
                    category=category,
                    severity="high" if is_online else "medium",
                    confidence=90,
                    country=None,
                    description=f"Malware distribution URL (tags: {tag_text})",
                    first_seen=date_added,
                    last_seen=date_added,
                )
            )

            host = entry.get("host")
            if host:
                threats.append(
                    build_threat_dict(
                        indicator=host,
                        indicator_type=classify_host(host),
                        source=self.source_name,
                        category=category,
                        severity="medium",
                        confidence=70,
                        country=None,
                        description=f"Host serving a malware distribution URL (tags: {tag_text})",
                        first_seen=date_added,
                        last_seen=date_added,
                    )
                )

        return threats
