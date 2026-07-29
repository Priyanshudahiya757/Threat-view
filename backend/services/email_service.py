"""Email notification delivery for alert events."""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app

logger = logging.getLogger(__name__)


def send_alert_email(to_address: str, subject: str, body: str) -> bool:
    """Send an alert email via configured SMTP. Logs and returns False when
    SMTP is not configured (development-friendly fallback).
    """
    if not to_address:
        return False

    host = current_app.config.get("SMTP_HOST", "")
    port = current_app.config.get("SMTP_PORT", 587)
    username = current_app.config.get("SMTP_USERNAME", "")
    password = current_app.config.get("SMTP_PASSWORD", "")
    sender = current_app.config.get("SMTP_FROM", username or "alerts@threatview.local")

    if not host:
        logger.info("SMTP not configured; alert email logged instead of sent to %s: %s", to_address, subject)
        logger.info("Alert body: %s", body)
        return False

    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = to_address
    message["Subject"] = f"[ThreatView] {subject}"
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            if current_app.config.get("SMTP_USE_TLS", True):
                server.starttls()
            if username and password:
                server.login(username, password)
            server.send_message(message)
        logger.info("Alert email sent to %s", to_address)
        return True
    except Exception:
        logger.exception("Failed to send alert email to %s", to_address)
        return False
