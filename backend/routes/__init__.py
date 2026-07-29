"""Blueprint registration, kept in one place so app.py doesn't need to
know about every individual blueprint module.
"""
from routes.health_routes import health_bp
from routes.auth_routes import auth_bp
from routes.threat_routes import threats_bp
from routes.stats_routes import stats_bp
from routes.search_routes import search_bp
from routes.report_routes import report_bp
from routes.alert_routes import alerts_bp
from routes.export_routes import export_bp
from routes.anomaly_routes import anomaly_bp


def register_blueprints(app) -> None:
    app.register_blueprint(health_bp,  url_prefix="/api")
    app.register_blueprint(auth_bp,    url_prefix="/api")
    app.register_blueprint(threats_bp, url_prefix="/api")
    app.register_blueprint(stats_bp,   url_prefix="/api")
    app.register_blueprint(search_bp,  url_prefix="/api")
    app.register_blueprint(report_bp,  url_prefix="/api")
    app.register_blueprint(alerts_bp,  url_prefix="/api")
    app.register_blueprint(export_bp,  url_prefix="/api")
    app.register_blueprint(anomaly_bp, url_prefix="/api")
