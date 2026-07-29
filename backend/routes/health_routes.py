"""Health-check endpoint used by uptime monitors and load balancers."""
import logging
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from database.db import db

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    db_status = "ok"
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Health check: database connectivity failed")
        db_status = "unavailable"

    payload = {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "scheduler_enabled": current_app.config.get("SCHEDULER_ENABLED", True),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return jsonify(payload), (200 if db_status == "ok" else 503)
