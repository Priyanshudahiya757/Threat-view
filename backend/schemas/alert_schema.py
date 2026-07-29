"""Marshmallow schemas for alert rules and events."""
from marshmallow import Schema, fields, validate

from utils.constants import ALERT_RULE_TYPES, SEVERITIES


class AlertRuleSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    rule_type = fields.Str(required=True, validate=validate.OneOf(ALERT_RULE_TYPES))
    rule_value = fields.Str(required=True, validate=validate.Length(min=1, max=512))
    notify_dashboard = fields.Bool(load_default=True)
    notify_email = fields.Bool(load_default=False)
    email = fields.Email(allow_none=True)
    is_active = fields.Bool(load_default=True)
    created_at = fields.DateTime(dump_only=True)


class AlertEventSchema(Schema):
    id = fields.Int(dump_only=True)
    rule_id = fields.Int(allow_none=True)
    threat_id = fields.Int(allow_none=True)
    alert_type = fields.Str()
    title = fields.Str()
    message = fields.Str()
    severity = fields.Str(validate=validate.OneOf(SEVERITIES))
    is_read = fields.Bool()
    email_sent = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    threat = fields.Nested("ThreatSchema", dump_only=True, allow_none=True)


class BrandMonitorSchema(Schema):
    id = fields.Int(dump_only=True)
    company_domain = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    notify_dashboard = fields.Bool(load_default=True)
    notify_email = fields.Bool(load_default=False)
    email = fields.Email(allow_none=True)
    is_active = fields.Bool(load_default=True)
    created_at = fields.DateTime(dump_only=True)
