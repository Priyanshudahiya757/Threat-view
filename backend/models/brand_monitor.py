"""Brand monitoring configuration for phishing feed domain matches."""
from datetime import datetime, timezone

from database.db import db


class BrandMonitor(db.Model):
    __tablename__ = "brand_monitors"

    id = db.Column(db.Integer, primary_key=True)
    company_domain = db.Column(db.String(255), nullable=False, unique=True, index=True)
    notify_dashboard = db.Column(db.Boolean, nullable=False, default=True)
    notify_email = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<BrandMonitor {self.company_domain}>"
