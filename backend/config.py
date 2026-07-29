"""Application configuration.

Values are read from environment variables -- loaded from a local .env
file via python-dotenv in development; in production the real
environment should supply these directly (e.g. via your platform's
secrets manager), and .env should never be committed.
"""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base config shared by every environment."""

    # --- Required (see .env.example) ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES  = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES",  900))   # 15 min
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 604800)) # 7 days
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///threatview.db")
    OTX_API_KEY = os.environ.get("OTX_API_KEY", "")
    PHISHTANK_APP_KEY = os.environ.get("PHISHTANK_APP_KEY", "")
    URLHAUS_URL = os.environ.get("URLHAUS_URL", "https://urlhaus-api.abuse.ch/v1/urls/recent")

    # --- Optional, with sensible defaults ---
    OTX_BASE_URL = os.environ.get("OTX_BASE_URL", "https://otx.alienvault.com/api/v1")
    # Keep URLHAUS_AUTH_KEY as primary; accept URLHAUS_API_KEY as a compatibility alias.
    URLHAUS_AUTH_KEY = os.environ.get("URLHAUS_AUTH_KEY") or os.environ.get("URLHAUS_API_KEY", "")
    PHISHTANK_URL = os.environ.get(
        "PHISHTANK_URL",
        f"https://data.phishtank.com/data/{PHISHTANK_APP_KEY}/online-valid.json" if PHISHTANK_APP_KEY else "https://data.phishtank.com/data/online-valid.json",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    SCHEDULER_ENABLED = os.environ.get("SCHEDULER_ENABLED", "true").lower() == "true"
    INGESTION_INTERVAL_MINUTES = int(os.environ.get("INGESTION_INTERVAL_MINUTES", 60))
    HTTP_TIMEOUT_SECONDS = int(os.environ.get("HTTP_TIMEOUT_SECONDS", 15))

    SEED_SAMPLE_DATA = os.environ.get("SEED_SAMPLE_DATA", "true").lower() == "true"

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    COMPANY_NAME = os.environ.get("COMPANY_NAME", "ThreatView Security Operations")
    COMPANY_FOOTER = os.environ.get("COMPANY_FOOTER", "Confidential — For authorized personnel only")

    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM = os.environ.get("SMTP_FROM", "")
    SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SCHEDULER_ENABLED = False
    SEED_SAMPLE_DATA = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
