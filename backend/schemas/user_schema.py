"""Marshmallow schema for the User resource. Not wired to a route yet
(see models/user.py), but ready for the account/subscription endpoints
planned next.
"""
from marshmallow import Schema, fields, validate

VALID_SUBSCRIPTIONS = ["free", "starter", "pro", "enterprise"]


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    company_name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    industry = fields.Str(allow_none=True)
    email = fields.Email(required=True)
    subscription = fields.Str(validate=validate.OneOf(VALID_SUBSCRIPTIONS), load_default="free")
    created_at = fields.DateTime(dump_only=True)
