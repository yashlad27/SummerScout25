"""Celery tasks for scheduled job tracking."""

from celery import Celery

from src.core.config import get_settings
from src.ingest.runner import JobTrackerRunner
from src.scheduler.beat_schedule import CELERY_BEAT_SCHEDULE
from src.utils.logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "job_tracker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
    beat_schedule=CELERY_BEAT_SCHEDULE,  # Add beat schedule
)


@celery_app.task(name="tasks.run_job_tracker")
def run_job_tracker(company_filter: str | None = None) -> dict:
    """Run the job tracker pipeline.
    
    Args:
        company_filter: Optional company filter
        
    Returns:
        Run statistics
    """
    logger.info("Starting scheduled job tracker run")
    
    runner = JobTrackerRunner(dry_run=False)
    stats = runner.run(company_filter=company_filter)
    
    logger.info(f"Scheduled run complete: {stats}")
    return stats


@celery_app.task(name="tasks.run_job_tracker_for_company")
def run_job_tracker_for_company(company: str) -> dict:
    """Run job tracker for a specific company.
    
    Args:
        company: Company name
        
    Returns:
        Run statistics
    """
    logger.info(f"Starting job tracker run for {company}")
    
    runner = JobTrackerRunner(dry_run=False)
    stats = runner.run(company_filter=company)
    
    logger.info(f"Run complete for {company}: {stats}")
    return stats
