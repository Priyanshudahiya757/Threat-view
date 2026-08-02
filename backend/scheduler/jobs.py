"""Ingestion job functions invoked by APScheduler. Each one pushes a
Flask app context so it can use the app's configured extensions (the DB
session) even though APScheduler runs it on a background thread, well
outside any request, then persists whatever the ingestor produced via
threat_service.
"""
import logging

logger = logging.getLogger(__name__)


def _evaluate_alerts_for_source(threat_dicts) -> None:
    from models.threat import Threat
    from services import alert_service, brand_monitor_service

    if not threat_dicts:
        return
    source = threat_dicts[0].get("source")
    indicators = [item["indicator"] for item in threat_dicts]
    threats = Threat.query.filter(Threat.source == source, Threat.indicator.in_(indicators)).all()
    if threats:
        alert_service.evaluate_rules_for_threats(threats)
    brand_monitor_service.evaluate_brand_monitors()


def run_alert_evaluation_job(app) -> dict:
    with app.app_context():
        from services import alert_service, brand_monitor_service

        logger.info("Starting alert evaluation job")
        brand_result = brand_monitor_service.evaluate_brand_monitors()
        return {"brand_alerts": brand_result.get("alerts_created", 0)}


def run_alienvault_job(app) -> dict:
    with app.app_context():
        logger.info("Starting AlienVault OTX ingestion job")
        if not app.config.get("OTX_API_KEY"):
            logger.warning("Skipping AlienVault OTX ingestion: OTX_API_KEY is not configured")
            return {"inserted": 0, "updated": 0, "skipped": True}
        # Import ingestor and threat upsert at runtime to avoid importing
        # these modules (which in turn import other app internals) during
        # global module import time. This prevents side effects when the
        # Flask CLI imports modules to discover the `app` object.
        from ingestors.alienvault_otx_ingestor import AlienVaultOTXIngestor
        from services.threat_service import upsert_threats

        ingestor = AlienVaultOTXIngestor(
            api_key=app.config["OTX_API_KEY"],
            base_url=app.config["OTX_BASE_URL"],
            timeout=app.config["HTTP_TIMEOUT_SECONDS"],
        )
        threats = ingestor.run()
        result = upsert_threats(threats) if threats else {"inserted": 0, "updated": 0}
        if threats and result.get("inserted", 0) > 0:
            _evaluate_alerts_for_source(threats[: result["inserted"] + result.get("updated", 0)])
        logger.info(
            "Finished AlienVault OTX ingestion job (%d indicators, inserted=%d updated=%d)",
            len(threats), result["inserted"], result["updated"],
        )
        return result


def run_phishtank_job(app) -> dict:
    with app.app_context():
        logger.info("Starting PhishTank ingestion job")
        if not app.config.get("PHISHTANK_URL"):
            logger.warning("Skipping PhishTank ingestion: PHISHTANK_URL is not configured")
            return {"inserted": 0, "updated": 0, "skipped": True}
        from ingestors.phishtank_ingestor import PhishTankIngestor
        from services.threat_service import upsert_threats

        ingestor = PhishTankIngestor(
            feed_url=app.config["PHISHTANK_URL"],
            timeout=app.config["HTTP_TIMEOUT_SECONDS"],
        )
        threats = ingestor.run()
        result = upsert_threats(threats) if threats else {"inserted": 0, "updated": 0}
        if threats and result.get("inserted", 0) > 0:
            _evaluate_alerts_for_source(threats[: result["inserted"] + result.get("updated", 0)])
        logger.info(
            "Finished PhishTank ingestion job (%d indicators, inserted=%d updated=%d)",
            len(threats), result["inserted"], result["updated"],
        )
        return result


def run_urlhaus_job(app) -> dict:
    with app.app_context():
        logger.info("Starting URLhaus ingestion job")
        from ingestors.urlhaus_ingestor import URLhausIngestor
        from services.threat_service import upsert_threats

        ingestor = URLhausIngestor(
            feed_url=app.config.get("URLHAUS_URL", ""),
            auth_key=app.config.get("URLHAUS_AUTH_KEY", ""),
            timeout=app.config.get("HTTP_TIMEOUT_SECONDS", 15),
        )
        threats = ingestor.run()
        result = upsert_threats(threats) if threats else {"inserted": 0, "updated": 0}
        if threats and result.get("inserted", 0) > 0:
            _evaluate_alerts_for_source(threats[: result["inserted"] + result.get("updated", 0)])
        logger.info(
            "Finished URLhaus ingestion job (%d indicators, inserted=%d updated=%d)",
            len(threats), result["inserted"], result["updated"],
        )
        return result


def run_feodotracker_job(app) -> dict:
    with app.app_context():
        logger.info("Starting FeodoTracker live threat ingestion job")
        from ingestors.feodotracker_ingestor import FeodoTrackerIngestor
        from services.threat_service import upsert_threats

        ingestor = FeodoTrackerIngestor(timeout=app.config.get("HTTP_TIMEOUT_SECONDS", 15))
        threats = ingestor.run()
        result = upsert_threats(threats) if threats else {"inserted": 0, "updated": 0}
        if threats and (result.get("inserted", 0) > 0 or result.get("updated", 0) > 0):
            _evaluate_alerts_for_source(threats[: result["inserted"] + result.get("updated", 0)])
        logger.info(
            "Finished FeodoTracker ingestion job (%d indicators, inserted=%d updated=%d)",
            len(threats), result.get("inserted", 0), result.get("updated", 0),
        )
        return result


def run_threatfox_job(app) -> dict:
    with app.app_context():
        logger.info("Starting ThreatFox live threat ingestion job")
        from ingestors.threatfox_ingestor import ThreatFoxIngestor
        from services.threat_service import upsert_threats

        ingestor = ThreatFoxIngestor(days=1, timeout=app.config.get("HTTP_TIMEOUT_SECONDS", 15))
        threats = ingestor.run()
        result = upsert_threats(threats) if threats else {"inserted": 0, "updated": 0}
        if threats and (result.get("inserted", 0) > 0 or result.get("updated", 0) > 0):
            _evaluate_alerts_for_source(threats[: result["inserted"] + result.get("updated", 0)])
        logger.info(
            "Finished ThreatFox ingestion job (%d indicators, inserted=%d updated=%d)",
            len(threats), result.get("inserted", 0), result.get("updated", 0),
        )
        return result
