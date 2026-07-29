"""The User model represents a ThreatView operator account.
Supports JWT-based authentication with role-based access control.

Roles
-----
admin   – full access, can manage users and all settings
analyst – read/write access to threats, alerts, brand monitors
viewer  – read-only access
"""
import bcrypt
from datetime import datetime, timezone

from database.db import db

VALID_ROLES = {"admin", "analyst", "viewer"}


class User(db.Model):
    __tablename__ = "users"

    id           = db.Column(db.Integer, primary_key=True)
    email        = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    industry     = db.Column(db.String(100), nullable=True)
    role         = db.Column(db.String(50), nullable=False, default="analyst", index=True)
    is_active    = db.Column(db.Boolean, nullable=False, default=True)
    created_at   = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "email":        self.email,
            "company_name": self.company_name,
            "industry":     self.industry,
            "role":         self.role,
            "is_active":    self.is_active,
            "created_at":   self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<User {self.email} [{self.role}]>"

