"""Shared enums referenced by both the Marshmallow schemas (input
validation) and the ingestion normalization layer (output shaping), so
the two layers can't silently drift apart.
"""

INDICATOR_TYPES = ["IP", "Domain", "URL", "Hash", "Email"]
SEVERITIES = ["low", "medium", "high", "critical"]
REPUTATIONS = ["malicious", "suspicious", "unknown", "clean"]

SUBSCRIPTION_TIERS = ["free", "pro"]
PRO_TIERS = {"pro", "enterprise", "starter"}

ALERT_RULE_TYPES = ["industry", "severity", "malware_family", "ioc_type", "country", "keyword"]
ALERT_CHANNELS = ["dashboard", "email", "both"]
