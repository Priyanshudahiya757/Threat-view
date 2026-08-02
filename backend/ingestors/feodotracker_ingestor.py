"""Live, real-time open threat ingestor for abuse.ch FeodoTracker Botnet C2 feed.

FeodoTracker tracks active Botnet Command & Control (C2) servers for malware
families such as Emotet, QakBot, Pikabot, Bumblebee, and IcedID.
Requires NO API key.

Endpoint: https://feodotracker.abuse.ch/downloads/ipblocklist.json
"""
import logging
from typing import Any, Dict, List

from ingestors.base_ingestor import BaseIngestor
from services.normalization_service import build_threat_dict
from utils.http_client import build_http_session

logger = logging.getLogger(__name__)

FEED_URL = "https://feodotracker.abuse.ch/downloads/ipblocklist.json"


class FeodoTrackerIngestor(BaseIngestor):
    source_name = "FeodoTracker"

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = build_http_session()

    def fetch(self) -> List[Dict[str, Any]]:
        try:
            response = self.session.get(FEED_URL, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception:
            logger.warning("FeodoTracker request failed for %s", FEED_URL, exc_info=True)
            return []

    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        threats = []

        for item in raw_data:
            ip = item.get("ip_address")
            if not ip:
                continue

            malware = item.get("malware") or "Unknown Botnet"
            status  = item.get("status") or "online"
            port    = item.get("port")
            first   = item.get("first_seen")
            last    = item.get("last_seen") or first

            is_online = (status == "online")
            severity  = "critical" if is_online else "high"
            confidence = 95 if is_online else 75

            desc = f"Active {malware} Botnet C2 server (Port {port}, Status: {status})."

            threats.append(
                build_threat_dict(
                    indicator=ip,
                    indicator_type="IP",
                    source=self.source_name,
                    category="Botnet C2",
                    malware_family=malware,
                    severity=severity,
                    confidence=confidence,
                    country=item.get("c2_country"),
                    description=desc,
                    first_seen=first,
                    last_seen=last,
                )
            )

        return threats
