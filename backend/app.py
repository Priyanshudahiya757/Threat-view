"""Flask application factory for the ThreatView backend API."""
import logging
import time

from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager

import models  # noqa: F401  registers model classes with SQLAlchemy metadata
from config import config_by_name
from database.db import db, migrate
from routes import register_blueprints
from services.seed_service import seed_if_empty
from utils.logging_config import configure_logging

logger = logging.getLogger(__name__)


def create_app(env: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(env, config_by_name["development"]))

    configure_logging(app)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    JWTManager(app)
    _init_swagger(app)

    register_blueprints(app)
    _register_root_routes(app)
    _register_error_handlers(app)
    _register_request_logging(app)

    from utils.rbac import init_rbac
    init_rbac(app)

    if app.config.get("SEED_SAMPLE_DATA", True):
        with app.app_context():
            seed_if_empty()

    return app


def _register_root_routes(app: Flask) -> None:
    @app.route("/")
    @app.route("/api")
    def api_root():
        return jsonify({
            "name": "ThreatView REST API",
            "version": "2.0.0",
            "status": "online",
            "documentation": "/api/docs/",
            "endpoints": {
                "health": "/api/health",
                "auth": "/api/auth/login",
                "threats": "/api/threats",
                "search": "/api/search?q=",
                "stats": "/api/stats",
                "ai_anomalies": "/api/ai/anomalies",
                "reports": "/api/reports/threat-landscape",
                "swagger_ui": "/api/docs/"
            }
        })


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.exception("Unhandled server error: %s", error)
        return jsonify({"error": "internal server error"}), 500


def _register_request_logging(app: Flask) -> None:
    @app.before_request
    def _start_timer():
        request._start_time = time.time()

    @app.after_request
    def _log_request(response):
        elapsed_ms = (time.time() - getattr(request, "_start_time", time.time())) * 1000
        logger.info("%s %s -> %d (%.1fms)", request.method, request.path, response.status_code, elapsed_ms)
        return response


def _init_swagger(app: Flask) -> None:
    """Configure Flasgger to expose Swagger UI at /api/docs."""
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/api/docs/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/",
    }
    
    @app.route("/api/docs")
    def swagger_redirect():
        from flask import redirect
        return redirect("/api/docs/")
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "ThreatView API",
            "description": (
                "REST API for the ThreatView threat-intelligence platform.\n\n"
                "**Authentication**: All protected endpoints require a Bearer JWT token "
                "obtained from `POST /api/auth/login`.\n\n"
                "Pass the token in the Authorization header: `Bearer <token>`"
            ),
            "version": "2.0.0",
            "contact": {"name": "ThreatView"},
        },
        "basePath": "/api",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "BearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Enter: **Bearer &lt;JWT&gt;**",
            }
        },
        "security": [{"BearerAuth": []}],
        "tags": [
            {"name": "auth",    "description": "Authentication — register, login, refresh"},
            {"name": "threats", "description": "Threat indicators — list, filter, detail"},
            {"name": "search",  "description": "Free-text IOC search"},
            {"name": "stats",   "description": "Aggregate analytics and malware trends"},
            {"name": "alerts",  "description": "Alert rules and triggered events"},
            {"name": "export",  "description": "CSV data export"},
            {"name": "report",  "description": "PDF weekly report"},
            {"name": "health",  "description": "API health check"},
        ],
    }
    Swagger(app, config=swagger_config, template=swagger_template)
