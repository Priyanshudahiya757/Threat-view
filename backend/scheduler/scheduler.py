"""APScheduler wiring. `init_scheduler(app)` runs once from the app
factory and registers the three feed-ingestion jobs on a shared interval
trigger, each with an immediate first run so the database isn't empty
for a full interval after a fresh deploy.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler

from scheduler.jobs import run_alert_evaluation_job, run_alienvault_job, run_phishtank_job, run_urlhaus_job

logger = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None


def init_scheduler(app) -> Optional[BackgroundScheduler]:
    global _scheduler

    if not app.config.get("SCHEDULER_ENABLED", True):
        logger.info("Scheduler disabled via config; no ingestion jobs registered")
        return None

    if _scheduler is not None and _scheduler.running:
        return _scheduler

    interval = app.config.get("INGESTION_INTERVAL_MINUTES", 60)
    scheduler = BackgroundScheduler(timezone="UTC")
    now = datetime.now(timezone.utc)

    jobs = (
        ("alienvault_otx_job", run_alienvault_job),
        ("phishtank_job", run_phishtank_job),
        ("urlhaus_job", run_urlhaus_job),
        ("alert_evaluation_job", run_alert_evaluation_job),
    )
    for job_id, job_func in jobs:
        scheduler.add_job(
            func=job_func,
            args=[app],
            trigger="interval",
            minutes=interval,
            id=job_id,
            next_run_time=now,  # fire once immediately, then every `interval` minutes
            replace_existing=True,
        )

    scheduler.start()
    _scheduler = scheduler
    logger.info("Scheduler started: %d ingestion jobs every %d minute(s)", len(jobs), interval)
    return scheduler
