"""APScheduler-based runner (alternative to Celery)."""

import time

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.ingest.runner import JobTrackerRunner
from src.utils.logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


def run_tracker():
    """Run the job tracker."""
    logger.info("Starting scheduled job tracker run")
    
    runner = JobTrackerRunner(dry_run=False)
    stats = runner.run()
    
    logger.info(f"Scheduled run complete: {stats}")


def main():
    """Main entry point for APScheduler runner."""
    logger.info("Starting APScheduler runner")
    
    scheduler = BlockingScheduler()
    
    # Schedule job tracker to run every hour
    scheduler.add_job(
        run_tracker,
        trigger=CronTrigger(minute=0),  # Every hour at :00
        id="job_tracker_hourly",
        name="Run Job Tracker (hourly)",
        replace_existing=True,
    )
    
    logger.info("Scheduler started. Press Ctrl+C to exit.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    main()
