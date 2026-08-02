"""Cron endpoints for serverless environments (e.g., Vercel)."""
import os
from flask import Blueprint, jsonify, current_app, request

from scheduler.jobs import (
    run_alienvault_job,
    run_phishtank_job,
    run_urlhaus_job,
    run_alert_evaluation_job,
)

cron_bp = Blueprint("cron", __name__)

@cron_bp.route("/cron/ingest", methods=["GET", "POST"])
def ingest_cron():
    """Trigger data ingestion manually or via Vercel Cron.
    ---
    tags: [cron]
    summary: Run background ingestion jobs synchronously
    """
    # Vercel sends CRON_SECRET as a Bearer token if configured
    cron_secret = os.environ.get("CRON_SECRET")
    if cron_secret:
        auth_header = request.headers.get("Authorization")
        if auth_header != f"Bearer {cron_secret}":
            return jsonify({"error": "Unauthorized cron request"}), 401

    try:
        # We must pass the actual app object, not the LocalProxy proxy object,
        # but since we are in an active request context, jobs will run successfully.
        app = current_app._get_current_object()
        
        run_alienvault_job(app)
        run_phishtank_job(app)
        run_urlhaus_job(app)
        run_alert_evaluation_job(app)
        
        return jsonify({"status": "success", "message": "Synchronous ingestion completed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
