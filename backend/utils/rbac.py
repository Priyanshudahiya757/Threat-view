"""Role-based access control built on Flask-JWT-Extended.

Replaces the previous header-sniffing tier system (X-Subscription-Tier)
with real JWT authentication.  Every protected endpoint now requires a
valid access token; role-specific endpoints additionally check the
caller's `role` claim via `require_role`.

Backward-compat shim
--------------------
`init_rbac(app)` is kept so `app.py` doesn't need changing.  It now
installs a before_request hook that populates `g.current_user` for any
request that carries a valid token (optional – does NOT reject tokenless
requests; route decorators handle enforcement).
"""
import logging
from functools import wraps

from flask import g, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from database.db import db

logger = logging.getLogger(__name__)


def init_rbac(app) -> None:
    """Install an optional before_request hook that silently loads the
    current user from the JWT when one is present.  Routes that require
    auth use @jwt_required() (or @require_role) explicitly."""

    @app.before_request
    def _load_user_context():
        g.current_user = None
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id is not None:
                from models.user import User
                g.current_user = db.session.get(User, user_id)
        except Exception:
            pass


def require_role(*roles):
    """Decorator: JWT must be valid AND the caller's role must be in *roles*.

    Usage::

        @bp.route("/admin-only")
        @require_role("admin")
        def admin_only(): ...

        @bp.route("/analysts-or-admins")
        @require_role("admin", "analyst")
        def analysts(): ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from flask_jwt_extended import jwt_required
            # Verify JWT presence first
            try:
                verify_jwt_in_request()
            except Exception as exc:
                return jsonify({"error": "authentication required", "detail": str(exc)}), 401

            user_id = get_jwt_identity()
            from models.user import User
            user = db.session.get(User, user_id)
            if user is None or not user.is_active:
                return jsonify({"error": "user not found or inactive"}), 401
            if user.role not in roles:
                logger.info(
                    "RBAC denied %s for role=%s (requires %s)",
                    fn.__name__, user.role, roles,
                )
                return jsonify({"error": f"Requires role: {', '.join(sorted(roles))}"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ── Legacy alias (kept so existing imports don't break) ───────────────────────
def require_pro(feature: str = "This feature"):
    """Replaced by JWT auth. Now simply requires any valid JWT token."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception as exc:
                return jsonify({"error": "authentication required"}), 401
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_api_access(fn):
    """Legacy alias – now simply requires a valid JWT."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({"error": "authentication required"}), 401
        return fn(*args, **kwargs)
    return wrapper

