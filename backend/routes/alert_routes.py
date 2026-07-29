"""Blueprint for alert rules, events, and brand monitoring."""
import logging

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from schemas.alert_schema import AlertEventSchema, AlertRuleSchema, BrandMonitorSchema
from services import alert_service, brand_monitor_service
from utils.pagination import serialize_pagination
from utils.rbac import require_pro

logger = logging.getLogger(__name__)

alerts_bp = Blueprint("alerts", __name__)

_rule_schema = AlertRuleSchema()
_event_schema = AlertEventSchema()
_brand_schema = BrandMonitorSchema()


@alerts_bp.route("/alerts/rules", methods=["GET"])
@require_pro("Custom alerts")
def list_rules():
    active_only = request.args.get("active_only", "false").lower() == "true"
    rules = alert_service.list_rules(active_only=active_only)
    return jsonify(_rule_schema.dump(rules, many=True))


@alerts_bp.route("/alerts/rules", methods=["POST"])
@require_pro("Custom alerts")
def create_rule():
    try:
        payload = _rule_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "invalid alert rule", "details": err.messages}), 400
    rule = alert_service.create_rule(payload)
    return jsonify(_rule_schema.dump(rule)), 201


@alerts_bp.route("/alerts/rules/<int:rule_id>", methods=["PUT"])
@require_pro("Custom alerts")
def update_rule(rule_id: int):
    try:
        payload = _rule_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": "invalid alert rule", "details": err.messages}), 400
    rule = alert_service.update_rule(rule_id, payload)
    if rule is None:
        return jsonify({"error": f"no alert rule found with id {rule_id}"}), 404
    return jsonify(_rule_schema.dump(rule))


@alerts_bp.route("/alerts/rules/<int:rule_id>", methods=["DELETE"])
@require_pro("Custom alerts")
def delete_rule(rule_id: int):
    if not alert_service.delete_rule(rule_id):
        return jsonify({"error": f"no alert rule found with id {rule_id}"}), 404
    return jsonify({"message": "alert rule deleted"})


@alerts_bp.route("/alerts/events", methods=["GET"])
@require_pro("Alert history")
def list_events():
    page = request.args.get("page", default=1, type=int) or 1
    per_page = request.args.get("per_page", default=20, type=int) or 20
    per_page = max(1, min(per_page, 100))
    unread_only = request.args.get("unread_only", "false").lower() == "true"
    pagination = alert_service.list_events(page=page, per_page=per_page, unread_only=unread_only)
    return jsonify(serialize_pagination(pagination, _event_schema))


@alerts_bp.route("/alerts/events/<int:event_id>/read", methods=["POST"])
@require_pro("Alert history")
def mark_read(event_id: int):
    event = alert_service.mark_event_read(event_id)
    if event is None:
        return jsonify({"error": f"no alert event found with id {event_id}"}), 404
    return jsonify(_event_schema.dump(event))


@alerts_bp.route("/alerts/events/read-all", methods=["POST"])
@require_pro("Alert history")
def mark_all_read():
    count = alert_service.mark_all_read()
    return jsonify({"marked_read": count})


@alerts_bp.route("/alerts/notifications/unread-count", methods=["GET"])
def unread_count():
    return jsonify({"unread_count": alert_service.unread_count()})


@alerts_bp.route("/alerts/brand-monitors", methods=["GET"])
@require_pro("Brand monitoring")
def list_brand_monitors():
    monitors = brand_monitor_service.list_monitors()
    return jsonify(_brand_schema.dump(monitors, many=True))


@alerts_bp.route("/alerts/brand-monitors", methods=["POST"])
@require_pro("Brand monitoring")
def create_brand_monitor():
    try:
        payload = _brand_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "invalid brand monitor", "details": err.messages}), 400
    monitor = brand_monitor_service.create_monitor(payload)
    brand_monitor_service.evaluate_brand_monitors()
    return jsonify(_brand_schema.dump(monitor)), 201


@alerts_bp.route("/alerts/brand-monitors/<int:monitor_id>", methods=["DELETE"])
@require_pro("Brand monitoring")
def delete_brand_monitor(monitor_id: int):
    if not brand_monitor_service.delete_monitor(monitor_id):
        return jsonify({"error": f"no brand monitor found with id {monitor_id}"}), 404
    return jsonify({"message": "brand monitor deleted"})
