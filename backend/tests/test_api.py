"""Unit tests for ThreatView Authentication, Threats, Stats, Search, and AI Anomaly Detection APIs."""
import pytest
from app import create_app
from database.db import db
from models.user import User
from models.threat import Threat
from datetime import datetime, timezone


@pytest.fixture
def app():
    app = create_app("testing")
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-jwt-secret-key-12345678901234567890",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"


def test_auth_flow(client):
    # 1. Register first user (automatically admin)
    reg_payload = {
        "email": "admin@threatview.io",
        "password": "Password123!",
        "company_name": "ThreatView Sec",
        "industry": "Cybersecurity",
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.get_json()
    assert "access_token" in reg_data
    assert reg_data["user"]["role"] == "admin"

    # 2. Login
    login_res = client.post("/api/auth/login", json={
        "email": "admin@threatview.io",
        "password": "Password123!",
    })
    assert login_res.status_code == 200
    token = login_res.get_json()["access_token"]

    # 3. Access /auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.get_json()["email"] == "admin@threatview.io"


def test_threat_and_search_api(client, app):
    with app.app_context():
        t1 = Threat(
            indicator="192.168.1.100",
            indicator_type="IP",
            severity="critical",
            reputation="malicious",
            confidence=95,
            source="FeodoTracker",
            country="US",
            malware_family="Emotet",
            first_seen=datetime.now(timezone.utc)
        )
        db.session.add(t1)
        db.session.commit()

    # List threats
    res = client.get("/api/threats")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["indicator"] == "192.168.1.100"

    # Search with explicit indicator_type & reputation filter
    search_res = client.get("/api/search?q=192.168.1.100&indicator_type=IP&reputation=malicious")
    assert search_res.status_code == 200
    search_data = search_res.get_json()
    assert len(search_data["items"]) == 1


def test_ai_anomaly_detection_api(client, app):
    with app.app_context():
        # Seed 15 sample threats for IsolationForest
        for i in range(15):
            t = Threat(
                indicator=f"10.0.0.{i}",
                indicator_type="IP",
                severity="high" if i % 2 == 0 else "low",
                reputation="suspicious" if i % 3 == 0 else "clean",
                confidence=50 + i * 3,
                source="AbuseCH",
                country="US",
                first_seen=datetime.now(timezone.utc)
            )
            db.session.add(t)
        db.session.commit()

    res = client.get("/api/ai/anomalies?top_n=5&contamination=0.1")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_analyzed"] == 15
    assert len(data["anomalies"]) <= 5
    assert "score_distribution" in data
