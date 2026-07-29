"""Blueprint for free-text indicator search."""
from flask import Blueprint, jsonify, request

from schemas.threat_schema import ThreatSchema
from services import threat_service
from utils.pagination import serialize_pagination

search_bp = Blueprint("search", __name__)
_threat_schema = ThreatSchema()


@search_bp.route("/search", methods=["GET"])
def search():
    """Search threat indicators by value.
    ---
    tags: [search]
    summary: Free-text IOC search
    parameters:
      - {in: query, name: q,              type: string,  required: true, description: Search term (IP / domain / hash / URL)}
      - {in: query, name: indicator_type, type: string,  enum: [IP, Domain, URL, Hash, Email]}
      - {in: query, name: reputation,     type: string,  enum: [malicious, suspicious, unknown, clean]}
      - {in: query, name: page,           type: integer, default: 1}
      - {in: query, name: per_page,       type: integer, default: 20}
    responses:
      200: {description: Paginated search results with query echoed back}
      400: {description: Missing q parameter}
    """
    term = request.args.get("q", "", type=str).strip()
    if not term:
        return jsonify({"error": "query parameter 'q' is required"}), 400

    page           = request.args.get("page",           default=1,  type=int) or 1
    per_page       = request.args.get("per_page",       default=20, type=int) or 20
    per_page       = max(1, min(per_page, 100))
    indicator_type = request.args.get("indicator_type") or request.args.get("type")
    reputation     = request.args.get("reputation")

    pagination = threat_service.search_threats(
        term, page=page, per_page=per_page,
        indicator_type=indicator_type or None,
        reputation=reputation or None,
    )
    payload = serialize_pagination(pagination, _threat_schema)
    payload["query"] = term
    return jsonify(payload)
