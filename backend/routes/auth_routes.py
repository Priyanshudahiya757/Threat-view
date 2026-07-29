"""Authentication routes: register, login, token refresh, logout, and /me."""
import logging
from functools import wraps

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from database.db import db
from models.user import User, VALID_ROLES

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _user_count() -> int:
    return User.query.count()


def require_role(*roles):
    """Decorator: JWT must be valid AND the identity's role must be in `roles`."""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            if user is None or not user.is_active:
                return jsonify({"error": "user not found or inactive"}), 401
            if user.role not in roles:
                return jsonify({"error": f"Requires role: {', '.join(roles)}"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    """Register a new user account.
    ---
    tags: [auth]
    summary: Register a new user
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [email, password, company_name]
          properties:
            email:        {type: string, example: admin@company.com}
            password:     {type: string, example: secret1234}
            company_name: {type: string, example: Acme Corp}
            industry:     {type: string, example: Finance}
            role:         {type: string, enum: [admin, analyst, viewer], example: analyst}
    responses:
      201:
        description: User created and JWT tokens returned
      400: {description: Validation error}
      409: {description: Email already registered}
    security: []
    """
    data = request.get_json() or {}
    email        = (data.get("email") or "").strip().lower()
    password     = data.get("password") or ""
    company_name = (data.get("company_name") or "").strip()
    role         = (data.get("role") or "analyst").strip().lower()

    if not email or not password or not company_name:
        return jsonify({"error": "email, password and company_name are required"}), 400
    if len(password) < 8:
        return jsonify({"error": "password must be at least 8 characters"}), 400
    if role not in VALID_ROLES:
        return jsonify({"error": f"role must be one of {sorted(VALID_ROLES)}"}), 400

    is_first_user = _user_count() == 0

    # After the first user, only admins may register new users.
    if not is_first_user:
        from flask_jwt_extended import verify_jwt_in_request
        try:
            verify_jwt_in_request()
            caller_id = get_jwt_identity()
            caller = db.session.get(User, caller_id)
            if caller is None or caller.role != "admin":
                return jsonify({"error": "Only admins can register new users"}), 403
        except Exception:
            return jsonify({"error": "Authentication required to register additional users"}), 401

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409

    user = User(
        email=email,
        company_name=company_name,
        industry=data.get("industry"),
        role="admin" if is_first_user else role,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    logger.info("User registered: %s (role=%s)", email, user.role)

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({
        "user":          user.to_dict(),
        "access_token":  access_token,
        "refresh_token": refresh_token,
    }), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """Authenticate and receive JWT tokens.
    ---
    tags: [auth]
    summary: Login
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [email, password]
          properties:
            email:    {type: string, example: admin@company.com}
            password: {type: string, example: secret1234}
    responses:
      200:
        description: Login successful — returns user object + access/refresh tokens
      400: {description: Missing fields}
      401: {description: Invalid credentials}
    security: []
    """
    data     = request.get_json() or {}
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if user is None or not user.is_active or not user.check_password(password):
        return jsonify({"error": "invalid email or password"}), 401

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    logger.info("User logged in: %s", email)
    return jsonify({
        "user":          user.to_dict(),
        "access_token":  access_token,
        "refresh_token": refresh_token,
    })


@auth_bp.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Obtain a new access token using a valid refresh token.
    ---
    tags: [auth]
    summary: Refresh access token
    responses:
      200: {description: New access token issued}
      401: {description: Refresh token invalid or expired}
    """
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    if user is None or not user.is_active:
        return jsonify({"error": "user not found or inactive"}), 401
    return jsonify({"access_token": create_access_token(identity=str(user_id))})


@auth_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def me():
    """Return the authenticated user's profile.
    ---
    tags: [auth]
    summary: Get current user profile
    responses:
      200: {description: User profile object}
      401: {description: Not authenticated}
      404: {description: User not found}
    """
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "user not found"}), 404
    return jsonify(user.to_dict())


@auth_bp.route("/auth/users", methods=["GET"])
@require_role("admin")
def list_users():
    """List all users. Admin only."""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])
