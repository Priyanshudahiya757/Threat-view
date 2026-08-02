"""Live, real-time open threat ingestor for abuse.ch ThreatFox API.

ThreatFox tracks recent indicators of compromise (IOCs) including malware hashes,
botnet IPs, phishing URLs, and C2 domains.
Requires NO API key.

Endpoint: POST https://threatfox-api.abuse.ch/v1/ with payload {"query": "get_iocs", "days": 1}
"""
import logging
from typing import Any, Dict, List

from ingestors.base_ingestor import BaseIngestor
from services.normalization_service import build_threat_dict
from utils.http_client import build_http_session

logger = logging.getLogger(__name__)

THREATFOX_API_URL = "https://threatfox-api.abuse.ch/v1/"


class ThreatFoxIngestor(BaseIngestor):
    source_name = "ThreatFox"

    def __init__(self, days: int = 1, timeout: int = 15):
        self.days = days
        self.timeout = timeout
        self.session = build_http_session()

    def fetch(self) -> Dict[str, Any]:
        payload = {"query": "get_iocs", "days": self.days}
        try:
            response = self.session.post(THREATFOX_API_URL, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception:
            logger.warning("ThreatFox request failed for %s", THREATFOX_API_URL, exc_info=True)
            return {"query_status": "error", "data": []}

    def normalize(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        if raw_data.get("query_status") != "ok":
            return []

        threats = []
        iocs = raw_data.get("data") or []

        for item in iocs:
            ioc = item.get("ioc")
            if not ioc:
                continue

            # Strip port from IP:port if needed
            ioc_val = ioc.split(":")[0] if ":" in ioc and not ioc.startswith("http") else ioc
            raw_type = item.get("ioc_type") or "url"
            malware  = item.get("malware_printable") or item.get("malware") or "Unknown Malware"
            confidence = item.get("confidence_level") or 80
            first    = item.get("first_seen")

            severity = "critical" if confidence >= 90 else "high"

            threats.append(
                build_threat_dict(
                    indicator=ioc_val,
                    indicator_type=raw_type,
                    source=self.source_name,
                    category=item.get("threat_type") or "malware",
                    malware_family=malware,
                    severity=severity,
                    confidence=confidence,
                    country=None,
                    description=f"ThreatFox IOC ({malware}, type: {raw_type}, threat_type: {item.get('threat_type')})",
                    first_seen=first,
                    last_seen=first,
                )
            )

        return threats
