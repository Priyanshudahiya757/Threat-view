"""Blueprint exposing PDF report endpoints."""
from flask import Blueprint, jsonify, send_file

from services.report_service import generate_report
from utils.rbac import require_pro

report_bp = Blueprint("report", __name__)


@report_bp.route("/report/weekly", methods=["GET"])
@require_pro("Weekly threat reports")
def weekly_report():
    report_buffer = generate_report()
    report_buffer.seek(0)
    return send_file(
        report_buffer,
        mimetype="application/pdf",
        as_attachment=False,
        download_name="ThreatView_Weekly_Report.pdf",
    )