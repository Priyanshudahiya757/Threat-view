"""The Threat model: one row per indicator of compromise (IOC), sourced
from one of the configured ingestors and normalized to a common shape
regardless of which feed it came from.
"""
from datetime import datetime, timezone

from database.db import db


class Threat(db.Model):
    __tablename__ = "threats"

    id = db.Column(db.Integer, primary_key=True)

    indicator = db.Column(db.String(512), nullable=False, index=True)
    indicator_type = db.Column(db.String(20), nullable=False, index=True)  # IP, Domain, URL, Hash, Email
    category = db.Column(db.String(100), nullable=True, index=True)
    malware_family = db.Column(db.String(100), nullable=True, index=True)
    reputation = db.Column(db.String(20), nullable=False, default="unknown", index=True)
    severity = db.Column(db.String(20), nullable=False, default="medium", index=True)
    confidence = db.Column(db.Integer, nullable=True)  # 0-100
    country = db.Column(db.String(100), nullable=True, index=True)
    source = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)

    first_seen = db.Column(db.DateTime, nullable=True)
    last_seen = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        # An indicator can legitimately show up in more than one feed, but
        # the same feed shouldn't report the same indicator twice -- that's
        # a re-ingest, not a new threat. This is what upsert_threats() in
        # threat_service.py relies on to decide insert-vs-update.
        db.UniqueConstraint("indicator", "source", name="uq_threat_indicator_source"),
    )

    def __repr__(self) -> str:
        return f"<Threat {self.indicator_type}:{self.indicator} from {self.source}>"
