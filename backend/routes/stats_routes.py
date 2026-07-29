"""Blueprint for aggregate analytics backing the dashboard."""
from flask import Blueprint, jsonify, request

from services import stats_service

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/stats", methods=["GET"])
def get_stats():
    """Return aggregate statistics for the dashboard.
    ---
    tags: [stats]
    summary: Dashboard aggregate stats
    responses:
      200: {description: Stats object with severity distribution, top countries, top malware, latest threats}
    """
    return jsonify(stats_service.get_stats())


@stats_bp.route("/stats/malware-trends", methods=["GET"])
def malware_trends():
    """Top malware families by total count over a date window.
    ---
    tags: [stats]
    summary: Top malware families
    parameters:
      - {in: query, name: days, type: integer, default: 14, description: Lookback window in days (1-90)}
    responses:
      200:
        description: "List of name and count objects"
    """
    days = request.args.get("days", default=14, type=int) or 14
    days = max(1, min(days, 90))
    return jsonify({"items": stats_service.get_malware_trends(days=days)})


@stats_bp.route("/stats/malware-trends-timeseries", methods=["GET"])
def malware_trends_timeseries():
    """Daily counts per malware family — stacked area chart data.
    ---
    tags: [stats]
    summary: Malware family daily timeseries
    parameters:
      - {in: query, name: days,  type: integer, default: 14, description: Lookback window (1-90)}
      - {in: query, name: top_n, type: integer, default: 6,  description: Number of top families (1-10)}
    responses:
      200:
        description: "Timeseries data ready for stacked area chart"
    """
    days  = request.args.get("days",  default=14, type=int) or 14
    top_n = request.args.get("top_n", default=6,  type=int) or 6
    days  = max(1, min(days, 90))
    top_n = max(1, min(top_n, 10))
    return jsonify(stats_service.get_malware_trends_timeseries(days=days, top_n=top_n))


@stats_bp.route("/stats/threat-map", methods=["GET"])
def threat_map():
    """Geo-coded threat origin points for the world map.
    ---
    tags: [stats]
    summary: Threat map geo points
    responses:
      200:
        description: "List of country lat/lng points"
    """
    return jsonify({"points": stats_service.get_threat_map()})
