"""Celery tasks for scheduled job tracking."""

from celery import Celery

from src.core.config import get_settings
from src.ingest.runner import JobTrackerRunner
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

# Load configuration from celeryconfig.py
celery_app.config_from_object('celeryconfig')

logger.info("Celery app configured with automatic schedule")


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
