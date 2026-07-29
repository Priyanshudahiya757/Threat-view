"""Reusable JSON response envelope helpers.

Not yet adopted by the existing endpoints (`/api/health`, `/api/stats`,
`/api/search`, `/api/threats`) -- those already return the shapes the
live React frontend is built against (plain resource bodies, `{"error":
...}` on failure, and `{items, page, per_page, total_items, total_pages}`
for lists; see routes/threat_routes.py and routes/health_routes.py).
Wrapping those in the `{"success": ...}` envelope below would change
their response bodies and requires a matching frontend update, so this
module exists as scaffolding for new routes rather than a retrofit of
working ones.
"""
from typing import Any, Optional

from flask import jsonify


def success_response(data: Any = None, message: Optional[str] = None, status: int = 200):
    """Standard success envelope: `{"success": true, "data": ...}`,
    with an optional human-readable `message`.
    """
    payload = {"success": True, "data": data}
    if message is not None:
        payload["message"] = message
    return jsonify(payload), status


def error_response(message: str, status: int = 400, details: Any = None):
    """Standard error envelope: `{"success": false, "error": ...}`,
    with optional structured `details` (e.g. Marshmallow validation
    errors).
    """
    payload = {"success": False, "error": message}
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status


def paginated_response(
    items: list,
    page: int,
    per_page: int,
    total: int,
    message: Optional[str] = None,
    status: int = 200,
):
    """Standard paginated envelope: the page of `items` plus a nested
    `pagination` block, inside the same success shape as
    `success_response()`.
    """
    pages = (total + per_page - 1) // per_page if per_page else 0
    payload = {
        "success": True,
        "data": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1,
        },
    }
    if message is not None:
        payload["message"] = message
    return jsonify(payload), status
