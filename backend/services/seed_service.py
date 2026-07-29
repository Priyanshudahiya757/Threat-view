"""Bootstrap sample data for a fresh ThreatView install.

If enabled via `SEED_SAMPLE_DATA`, this runs once at app startup and
inserts a realistic but fully synthetic threat set only when the table
exists and is empty. It is intentionally idempotent so it never
overwrites live data.
"""
import logging
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import inspect

from database.db import db
from models.threat import Threat

logger = logging.getLogger(__name__)

_SAMPLE_THREATS = [
    dict(indicator="203.0.113.45", indicator_type="IP", source="AlienVault OTX",
         category="Botnet C2", severity="high", confidence=82, country="Russia",
         description="Command-and-control node observed across multiple botnet pulses.", age_days=2),
    dict(indicator="198.51.100.23", indicator_type="IP", source="AlienVault OTX",
         category="Scanning", severity="medium", confidence=60, country="China",
         description="Host observed conducting broad port-scanning activity.", age_days=5),
    dict(indicator="192.0.2.88", indicator_type="IP", source="URLhaus",
         category="Malware Hosting", severity="high", confidence=88, country="Netherlands",
         description="IP hosting multiple malware payload URLs.", age_days=1),
    dict(indicator="203.0.113.201", indicator_type="IP", source="AlienVault OTX",
         category="Brute Force", severity="medium", confidence=55, country="Brazil",
         description="Source of repeated SSH brute-force attempts.", age_days=9),
    dict(indicator="198.51.100.150", indicator_type="IP", source="AlienVault OTX",
         category="Botnet C2", severity="critical", confidence=91, country="Iran",
         description="Active C2 infrastructure for a tracked malware family.", age_days=0),
    dict(indicator="malicious-update.test", indicator_type="Domain", source="AlienVault OTX",
         category="Malware C2", severity="high", confidence=78, country="Ukraine",
         description="Domain used to distribute fake software update prompts.", age_days=3),
    dict(indicator="secure-verification.example", indicator_type="Domain", source="PhishTank",
         category="Phishing", severity="high", confidence=85, country="United States",
         description="Credential-harvesting domain impersonating an account verification flow.", age_days=1),
    dict(indicator="freegift-rewards.test", indicator_type="Domain", source="PhishTank",
         category="Phishing", severity="medium", confidence=65, country="India",
         description="Domain used in a gift-card reward scam campaign.", age_days=12),
    dict(indicator="cdn-analytics-track.invalid", indicator_type="Domain", source="AlienVault OTX",
         category="Tracking", severity="low", confidence=40, country="Germany",
         description="Domain associated with aggressive third-party tracking scripts.", age_days=20),
    dict(indicator="bank0famerica-secure.test", indicator_type="Domain", source="PhishTank",
         category="Phishing", severity="critical", confidence=96, country="United States",
         description="Typosquat domain actively harvesting banking credentials.", age_days=0),
    dict(indicator="http://198.51.100.77/dl/setup.exe", indicator_type="URL", source="URLhaus",
         category="malware_download", severity="high", confidence=90, country="France",
         description="Malware distribution URL (tags: trojan, dropper).", age_days=1),
    dict(indicator="https://account-verify-support.example/login", indicator_type="URL", source="PhishTank",
         category="Phishing", severity="critical", confidence=93, country="Canada",
         description="Phishing URL targeting a major webmail provider.", age_days=2),
    dict(indicator="http://192.0.2.14/panel/gate.php", indicator_type="URL", source="AlienVault OTX",
         category="Malware C2", severity="high", confidence=80, country="Vietnam",
         description="C2 check-in endpoint for a tracked malware family.", age_days=6),
    dict(indicator="https://invoice-payment-alert.test/pay", indicator_type="URL", source="PhishTank",
         category="Phishing", severity="medium", confidence=62, country="United Kingdom",
         description="Phishing URL disguised as an overdue invoice notice.", age_days=14),
    dict(indicator="http://203.0.113.99/wp-content/uploads/x.php", indicator_type="URL", source="URLhaus",
         category="malware_download", severity="medium", confidence=58, country="Poland",
         description="Malware distribution URL (tags: webshell).", age_days=8),
    dict(indicator="8f14e45fceea167a5a36dedd4bea2543d9f1a1a5a5f3b2e9c0d1e2f3a4b5c6d", indicator_type="Hash",
         source="AlienVault OTX", category="Trojan", severity="high", confidence=75, country=None,
         description="SHA-256 of a trojan sample distributed via phishing attachments.", age_days=4),
    dict(indicator="1a79a4d60de6718e8e5b326e338ae533e12b1f3e6c9d0a1b2c3d4e5f6a7b8c9", indicator_type="Hash",
         source="AlienVault OTX", category="Ransomware", severity="critical", confidence=97, country=None,
         description="SHA-256 of an active ransomware payload.", age_days=0),
    dict(indicator="5d41402abc4b2a76b9719d911017c592", indicator_type="Hash",
         source="URLhaus", category="malware_download", severity="medium", confidence=55, country=None,
         description="MD5 of a payload served from a tracked distribution URL.", age_days=10),
    dict(indicator="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85", indicator_type="Hash",
         source="AlienVault OTX", category="Info Stealer", severity="high", confidence=83, country=None,
         description="SHA-256 of an info-stealer sample harvesting browser credentials.", age_days=3),
    dict(indicator="a94a8fe5ccb19ba61c4c0873d391e987982fbbd3", indicator_type="Hash",
         source="AlienVault OTX", category="Backdoor", severity="low", confidence=35, country=None,
         description="SHA-1 of a low-confidence backdoor sample.", age_days=25),
]


def _threats_table_exists() -> bool:
    try:
        return inspect(db.engine).has_table(Threat.__tablename__)
    except Exception:
        return False


from models.user import User
from models.alert import AlertRule, AlertEvent
from models.brand_monitor import BrandMonitor

def seed_if_empty() -> int:
    if not _threats_table_exists():
        logger.info("Skipping seed: threats table does not exist yet (run migrations first).")
        return 0

    # 1. Seed Threats if empty
    threats_seeded = 0
    if Threat.query.count() == 0:
        now = datetime.now(timezone.utc)
        rows = []
        for sample in _SAMPLE_THREATS:
            data = dict(sample)
            age = data.pop("age_days")
            seen = now - timedelta(days=age, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            rows.append(Threat(first_seen=seen, last_seen=seen, created_at=seen, **data))

        db.session.bulk_save_objects(rows)
        db.session.commit()
        threats_seeded = len(rows)
        logger.info("Seeded %d sample threats.", threats_seeded)

    # 2. Seed Admin User if empty
    if User.query.count() == 0:
        admin = User(
            email="admin@threatview.io",
            company_name="ThreatView Security",
            industry="Cybersecurity",
            role="admin",
            is_active=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        logger.info("Seeded default admin user: admin@threatview.io")

    # 3. Seed Alert Rules if empty
    if AlertRule.query.count() == 0:
        rule1 = AlertRule(
            name="Critical Severity Alert",
            rule_type="severity",
            rule_value="critical",
            is_active=True
        )
        rule2 = AlertRule(
            name="Phishing Indicator Alert",
            rule_type="category",
            rule_value="Phishing",
            is_active=True
        )
        db.session.add_all([rule1, rule2])
        db.session.commit()
        logger.info("Seeded default alert rules.")

    # 4. Seed Brand Monitor if empty
    if BrandMonitor.query.count() == 0:
        bm = BrandMonitor(
            company_domain="threatview.io",
            notify_dashboard=True,
            is_active=True
        )
        db.session.add(bm)
        db.session.commit()
        logger.info("Seeded default brand monitor for threatview.io")

    return threats_seeded