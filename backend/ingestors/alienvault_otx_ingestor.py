"""Ingestor for AlienVault OTX (Open Threat Exchange), now operated under
LevelBlue. OTX groups indicators into "pulses" (a themed collection of
IOCs); we pull every pulse the configured account is subscribed to and
flatten each pulse's indicator list into individual Threat rows.

API reference: https://otx.alienvault.com/api -- auth via the
`X-OTX-API-KEY` header, endpoint `/pulses/subscribed`.
"""
import logging
from typing import Any, Dict, List

from ingestors.base_ingestor import BaseIngestor
from services.normalization_service import build_threat_dict
from utils.http_client import build_http_session

logger = logging.getLogger(__name__)


class AlienVaultOTXIngestor(BaseIngestor):
    source_name = "AlienVault OTX"

    def __init__(self, api_key: str, base_url: str, timeout: int = 15, max_pages: int = 5):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        # OTX paginates subscribed pulses via a `next` URL. Cap how many
        # pages we'll follow per run so a very large subscription list
        # can't turn an hourly job into an unbounded crawl.
        self.max_pages = max_pages
        self.session = build_http_session()

    def fetch(self) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("Skipping AlienVault OTX fetch: OTX_API_KEY is not configured")
            return []

        headers = {"X-OTX-API-KEY": self.api_key}
        url = f"{self.base_url}/pulses/subscribed"
        pulses: List[Dict[str, Any]] = []

        for _ in range(self.max_pages):
            try:
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
            except Exception:
                logger.warning("AlienVault OTX request failed for %s", url, exc_info=True)
                return []
            payload = response.json()
            pulses.extend(payload.get("results", []))

            url = payload.get("next")
            if not url:
                break

        return pulses

    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        threats = []

        for pulse in raw_data:
            pulse_name = pulse.get("name") or "OTX Pulse"
            pulse_description = pulse.get("description")
            targeted_countries = pulse.get("targeted_countries") or []
            country = targeted_countries[0] if targeted_countries else None

            for indicator in pulse.get("indicators", []):
                value = indicator.get("indicator")
                if not value:
                    continue

                threats.append(
                    build_threat_dict(
                        indicator=value,
                        indicator_type=indicator.get("type", ""),
                        source=self.source_name,
                        category=pulse_name,
                        severity="medium",
                        confidence=75,
                        country=country,
                        description=indicator.get("description") or pulse_description,
                        first_seen=indicator.get("created"),
                        last_seen=indicator.get("created"),
                    )
                )

        return threats
