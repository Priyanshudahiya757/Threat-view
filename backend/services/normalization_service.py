"""Shared helpers for turning heterogeneous feed data into the common
Threat shape. Centralizing the mapping tables here means each ingestor
only needs to know its own API's field names, not the target schema's
quirks -- and if a new feed shows up later, only this file needs a new
entry, not every consumer of "normalized threat" dicts.
"""
from datetime import datetime, timezone
from typing import Optional

from utils.constants import INDICATOR_TYPES, REPUTATIONS, SEVERITIES

# Maps the various type labels each upstream feed uses onto our four
# canonical indicator types. Unrecognized labels fall back to "URL",
# since that's the most common indicator type across all three feeds.
_INDICATOR_TYPE_MAP = {
    "ipv4": "IP",
    "ipv6": "IP",
    "ip": "IP",
    "domain": "Domain",
    "hostname": "Domain",
    "url": "URL",
    "uri": "URL",
    "filehash-md5": "Hash",
    "filehash-sha1": "Hash",
    "filehash-sha256": "Hash",
    "filehash-pehash": "Hash",
    "filehash-imphash": "Hash",
    "md5": "Hash",
    "sha1": "Hash",
    "sha256": "Hash",
}


def derive_reputation(severity: Optional[str], confidence: Optional[int]) -> str:
    """Map severity and confidence into a coarse reputation label."""
    sev = (severity or "medium").strip().lower()
    score = confidence or 0
    if sev in ("critical", "high") and score >= 70:
        return "malicious"
    if sev in ("critical", "high", "medium"):
        return "suspicious"
    if sev == "low" and score < 30:
        return "unknown"
    return "suspicious"


def detect_indicator_type(indicator: str) -> str:
    """Best-effort indicator type detection from the raw value."""
    text = (indicator or "").strip()
    if not text:
        return "URL"
    if "@" in text and "." in text.split("@")[-1]:
        return "Email"
    if text.startswith(("http://", "https://", "ftp://")):
        return "URL"
    if len(text) in (32, 40, 64) and all(c in "0123456789abcdefABCDEF" for c in text):
        return "Hash"
    try:
        import ipaddress
        ipaddress.ip_address(text)
        return "IP"
    except ValueError:
        pass
    if "." in text and " " not in text and not text.startswith("/"):
        return "Domain"
    return "URL"


def map_indicator_type(raw_type: str) -> str:
    """Normalize a source-specific indicator type label into one of
    IP / Domain / URL / Hash / Email.
    """
    return _INDICATOR_TYPE_MAP.get((raw_type or "").strip().lower(), "URL")


def normalize_severity(value: Optional[str]) -> str:
    """Anything we don't recognize is treated as "medium" rather than
    rejected outright -- a slightly-wrong severity shouldn't drop an
    otherwise-good indicator.
    """
    value = (value or "").strip().lower()
    return value if value in SEVERITIES else "medium"


def parse_datetime(value) -> Optional[datetime]:
    """Best-effort timestamp parsing across feeds that all format
    timestamps slightly differently (OTX's ISO 8601 "created" field vs.
    URLhaus's "YYYY-MM-DD HH:MM:SS UTC" strings, for example). Returns
    None on anything unparseable rather than raising, since one bad
    timestamp shouldn't sink an entire ingestion run.
    """
    if not value:
        return None
    if isinstance(value, datetime):
        return value

    text = str(value).strip().replace("Z", "+00:00")

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d %H:%M:%S UTC", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    return None


def build_threat_dict(
    indicator: str,
    indicator_type: str,
    source: str,
    category: Optional[str] = None,
    malware_family: Optional[str] = None,
    severity: Optional[str] = None,
    confidence: Optional[int] = None,
    country: Optional[str] = None,
    description: Optional[str] = None,
    first_seen=None,
    last_seen=None,
) -> dict:
    """The single place that defines what a "normalized threat" dict
    looks like. Every ingestor calls this so threat_service always
    receives an identical shape regardless of which upstream feed it
    came from.

    `indicator_type` may be passed either already-canonical ("URL") or
    as a raw feed-specific label ("ipv4") -- both are accepted so
    callers don't have to remember which form each feed provides.
    """
    now = datetime.now(timezone.utc)
    normalized_type = indicator_type if indicator_type in INDICATOR_TYPES else map_indicator_type(indicator_type)
    if normalized_type == "URL" and indicator_type not in INDICATOR_TYPES:
        detected = detect_indicator_type(indicator)
        if detected != "URL":
            normalized_type = detected

    normalized_severity = normalize_severity(severity)
    family = malware_family or category

    return {
        "indicator": indicator.strip(),
        "indicator_type": normalized_type,
        "source": source,
        "category": category,
        "malware_family": family,
        "reputation": derive_reputation(normalized_severity, confidence),
        "severity": normalized_severity,
        "confidence": confidence,
        "country": country,
        "description": description,
        "first_seen": parse_datetime(first_seen) or now,
        "last_seen": parse_datetime(last_seen) or now,
    }
