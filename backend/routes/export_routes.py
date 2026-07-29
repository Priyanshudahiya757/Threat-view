"""Blueprint for CSV export endpoints (Pro tier only)."""
from flask import Blueprint, Response, jsonify, request

from services import alert_service, export_service, stats_service, threat_service
from utils.rbac import require_pro

export_bp = Blueprint("export", __name__)


@export_bp.route("/export/threats", methods=["GET"])
@require_pro("CSV export")
def export_threats():
    filters = {
        "severity": request.args.get("severity"),
        "indicator_type": request.args.get("indicator_type"),
        "source": request.args.get("source"),
        "country": request.args.get("country"),
        "reputation": request.args.get("reputation"),
    }
    threats = threat_service.get_threats_for_export(filters)
    csv_data = export_service.threats_to_csv(threats)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=threatview_threats.csv"},
    )


@export_bp.route("/export/search", methods=["GET"])
@require_pro("CSV export")
def export_search():
    term = request.args.get("q", "", type=str).strip()
    if not term:
        return jsonify({"error": "query parameter 'q' is required"}), 400
    indicator_type = request.args.get("indicator_type")
    pagination = threat_service.search_threats(term, page=1, per_page=5000, indicator_type=indicator_type)
    csv_data = export_service.threats_to_csv(pagination.items)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=threatview_search_{term[:30]}.csv"},
    )


@export_bp.route("/export/alerts", methods=["GET"])
@require_pro("CSV export")
def export_alerts():
    events = alert_service.get_events_for_export()
    csv_data = export_service.alerts_to_csv(events)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=threatview_alerts.csv"},
    )


@export_bp.route("/export/stats", methods=["GET"])
@require_pro("CSV export")
def export_stats():
    stats = stats_service.get_stats()
    stats["top_malware"] = stats_service.get_malware_trends()
    csv_data = export_service.stats_to_csv(stats)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=threatview_stats.csv"},
    )
