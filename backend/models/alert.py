"""Alert rules and triggered alert events for the ThreatView alert engine."""
from datetime import datetime, timezone

from database.db import db


class AlertRule(db.Model):
    __tablename__ = "alert_rules"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    rule_type = db.Column(db.String(50), nullable=False, index=True)
    rule_value = db.Column(db.String(512), nullable=False)
    notify_dashboard = db.Column(db.Boolean, nullable=False, default=True)
    notify_email = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    events = db.relationship("AlertEvent", backref="rule", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AlertRule {self.name} ({self.rule_type}={self.rule_value})>"


class AlertEvent(db.Model):
    __tablename__ = "alert_events"

    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey("alert_rules.id"), nullable=True, index=True)
    threat_id = db.Column(db.Integer, db.ForeignKey("threats.id"), nullable=True, index=True)
    alert_type = db.Column(db.String(50), nullable=False, default="rule", index=True)
    title = db.Column(db.String(300), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False, default="medium")
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    email_sent = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    threat = db.relationship("Threat", backref="alert_events")

    def __repr__(self) -> str:
        return f"<AlertEvent {self.title}>"
