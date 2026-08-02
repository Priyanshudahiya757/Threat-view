"""Ingestor for abuse.ch's URLhaus recent-malware-URLs feed.

Supports both API with Auth-Key and free public CSV export fallback
(https://urlhaus.abuse.ch/downloads/csv_recent/) requiring no API key.
"""
import csv
import logging
from typing import Any, Dict, List

from ingestors.base_ingestor import BaseIngestor
from services.normalization_service import build_threat_dict
from utils.http_client import build_http_session
from utils.threat_normalizer import classify_host

logger = logging.getLogger(__name__)

PUBLIC_CSV_URL = "https://urlhaus.abuse.ch/downloads/csv_recent/"


class URLhausIngestor(BaseIngestor):
    source_name = "URLhaus"

    def __init__(self, feed_url: str = "", auth_key: str = "", limit: int = 1000, timeout: int = 15):
        self.feed_url = (feed_url or "").rstrip("/")
        self.auth_key = auth_key
        self.limit = limit
        self.timeout = timeout
        self.session = build_http_session()

    def fetch(self) -> Dict[str, Any]:
        # Option A: API key provided
        if self.auth_key and self.feed_url:
            url = f"{self.feed_url}/limit/{self.limit}/"
            headers = {"Auth-Key": self.auth_key}
            try:
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                if response.status_code == 200:
                    return response.json()
            except Exception:
                logger.warning("URLhaus API request failed, falling back to public feed", exc_info=True)

        # Option B: Public CSV fallback (Free, no key needed)
        try:
            response = self.session.get(PUBLIC_CSV_URL, timeout=self.timeout)
            response.raise_for_status()
            lines = [line for line in response.text.splitlines() if not line.startswith("#")]
            reader = csv.reader(lines)
            urls = []
            for row in reader:
                if len(row) >= 8:
                    # id, dateadded, url, url_status, last_online, threat, tags, reporter
                    urls.append({
                        "url": row[2],
                        "url_status": row[3],
                        "threat": row[5],
                        "tags": [t.strip() for t in row[6].split(",") if t.strip()],
                        "date_added": row[1],
                    })
            return {"query_status": "ok", "urls": urls[:self.limit]}
        except Exception:
            logger.warning("URLhaus public feed request failed for %s", PUBLIC_CSV_URL, exc_info=True)
            return {"query_status": "unavailable", "urls": []}

    def normalize(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        if raw_data.get("query_status") != "ok":
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

        return threats
