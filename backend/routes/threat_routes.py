"""Blueprint for the core Threat resource: list/filter, fetch-by-id, and
the most-recent-indicators shortcut used by the dashboard's live feed.
"""
import logging

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from schemas.threat_schema import ThreatQuerySchema, ThreatSchema
from services import threat_service
from utils.pagination import serialize_pagination

logger = logging.getLogger(__name__)

threats_bp = Blueprint("threats", __name__)

_threat_schema = ThreatSchema()
_query_schema = ThreatQuerySchema()


@threats_bp.route("/threats", methods=["GET"])
def list_threats():
    """List and filter threat indicators.
    ---
    tags: [threats]
    summary: List threats
    parameters:
      - {in: query, name: page,           type: integer, default: 1}
      - {in: query, name: per_page,        type: integer, default: 20}
      - {in: query, name: severity,        type: string,  enum: [low, medium, high, critical]}
      - {in: query, name: indicator_type,  type: string,  enum: [IP, Domain, URL, Hash, Email]}
      - {in: query, name: reputation,      type: string,  enum: [malicious, suspicious, unknown, clean]}
      - {in: query, name: country,         type: string}
      - {in: query, name: source,          type: string}
      - {in: query, name: sort_by,         type: string,  default: created_at}
      - {in: query, name: order,           type: string,  enum: [asc, desc], default: desc}
    responses:
      200: {description: Paginated list of threat indicators}
    """
    try:
        args = _query_schema.load(request.args.to_dict())
    except ValidationError as err:
        return jsonify({"error": "invalid query parameters", "details": err.messages}), 400

    pagination = threat_service.query_threats(**args)
    return jsonify(serialize_pagination(pagination, _threat_schema))


@threats_bp.route("/threats/<int:threat_id>", methods=["GET"])
def get_threat(threat_id: int):
    """Get a single threat indicator by ID.
    ---
    tags: [threats]
    summary: Get threat by ID
    parameters:
      - {in: path, name: threat_id, type: integer, required: true}
    responses:
      200: {description: Threat object}
      404: {description: Not found}
    """
    threat = threat_service.get_threat_by_id(threat_id)
    if threat is None:
        return jsonify({"error": f"no threat found with id {threat_id}"}), 404
    return jsonify(_threat_schema.dump(threat))


@threats_bp.route("/recent", methods=["GET"])
def recent_threats():
    """Get the N most-recently ingested indicators.
    ---
    tags: [threats]
    summary: Recent threats
    parameters:
      - {in: query, name: limit, type: integer, default: 10, description: Max results (1-100)}
    responses:
      200: {description: Array of threat objects}
    """
    limit = request.args.get("limit", default=10, type=int) or 10
    limit = max(1, min(limit, 100))
    threats = threat_service.get_recent_threats(limit=limit)
    return jsonify(_threat_schema.dump(threats, many=True))
