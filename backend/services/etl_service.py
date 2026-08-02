"""Orchestration layer over the per-source ingestion jobs.

This provides a single manual ETL entry point that runs every source in
sequence. It is intentionally separate from the APScheduler wiring so
operators can trigger a full refresh without waiting for the next
scheduled interval.
"""
import logging
from datetime import datetime, timezone

from scheduler.jobs import run_alienvault_job, run_feodotracker_job, run_phishtank_job, run_threatfox_job, run_urlhaus_job

logger = logging.getLogger(__name__)

_JOBS = (
    ("FeodoTracker Live Feed", run_feodotracker_job),
    ("ThreatFox Live Feed", run_threatfox_job),
    ("AlienVault OTX", run_alienvault_job),
    ("PhishTank", run_phishtank_job),
    ("URLhaus", run_urlhaus_job),
)


def run_full_etl(app) -> dict:
    started_at = datetime.now(timezone.utc)
    logger.info("ETL run starting: %d source(s)", len(_JOBS))

    results = {}
    for name, job in _JOBS:
        try:
            results[name] = job(app) or {"inserted": 0, "updated": 0}
        except Exception as exc:
            logger.exception("ETL run: %s raised unexpectedly", name)
            results[name] = {"error": str(exc)}

    total_inserted = sum(r.get("inserted", 0) for r in results.values())
    total_updated = sum(r.get("updated", 0) for r in results.values())
    elapsed_seconds = (datetime.now(timezone.utc) - started_at).total_seconds()

    logger.info(
        "ETL run finished in %.1fs: inserted=%d updated=%d sources=%s",
        elapsed_seconds, total_inserted, total_updated, results,
    )
    return {
        "started_at": started_at.isoformat(),
        "elapsed_seconds": elapsed_seconds,
        "total_inserted": total_inserted,
        "total_updated": total_updated,
        "sources": results,
    }