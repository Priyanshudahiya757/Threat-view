"""Marshmallow schemas for the Threat resource: one for (de)serializing
rows, one for validating the query-string filters on GET /api/threats.
"""
from marshmallow import Schema, fields, validate, pre_load

from utils.constants import INDICATOR_TYPES, REPUTATIONS, SEVERITIES

VALID_SORT_FIELDS = ["created_at", "updated_at", "first_seen", "last_seen", "severity", "confidence"]


class ThreatSchema(Schema):
    id = fields.Int(dump_only=True)
    indicator = fields.Str(required=True, validate=validate.Length(min=1, max=512))
    indicator_type = fields.Str(required=True, validate=validate.OneOf(INDICATOR_TYPES))
    category = fields.Str(allow_none=True)
    malware_family = fields.Str(allow_none=True)
    reputation = fields.Str(validate=validate.OneOf(REPUTATIONS), load_default="unknown")
    severity = fields.Str(validate=validate.OneOf(SEVERITIES), load_default="medium")
    confidence = fields.Int(allow_none=True, validate=validate.Range(min=0, max=100))
    country = fields.Str(allow_none=True)
    source = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    first_seen = fields.DateTime(allow_none=True)
    last_seen = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ThreatQuerySchema(Schema):
    """Validates and coerces the query-string params on GET /api/threats.

    Optional filter fields deliberately have no `load_default`: if the
    caller omits them, they're absent from the loaded dict entirely, so
    `threat_service.query_threats(**args)` falls back to its own
    (also-None) defaults instead of receiving an explicit None.
    """

    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))
    sort_by = fields.Str(load_default="created_at", validate=validate.OneOf(VALID_SORT_FIELDS))
    order = fields.Str(load_default="desc", validate=validate.OneOf(["asc", "desc"]))
    severity = fields.Str(validate=validate.OneOf(SEVERITIES))
    indicator_type = fields.Str(validate=validate.OneOf(INDICATOR_TYPES))
    source = fields.Str()
    category = fields.Str()
    country = fields.Str()
    indicator_type = fields.Str(validate=validate.OneOf(INDICATOR_TYPES))
    malware_family = fields.Str()
    reputation = fields.Str(validate=validate.OneOf(REPUTATIONS))
    since = fields.DateTime()

    @pre_load
    def accept_limit_alias(self, data, **kwargs):
        """Allow `limit` as an alias for `per_page` for older callers."""
        if "limit" in data:
            data = dict(data)
            limit_value = data.pop("limit")
            data.setdefault("per_page", limit_value)
        return data
