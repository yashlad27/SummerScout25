#!/usr/bin/env python3
"""
Automated scheduler to run job scraper periodically.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from src.ingest.runner import JobTrackerRunner
from src.ingest.health_monitor import HealthMonitor
from src.utils.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class JobScraperScheduler:
    """Automated scheduler for running job scraper."""
    
    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.runner = JobTrackerRunner()
        self.health_monitor = HealthMonitor()
    
    def run_scraper(self):
        """Run the job scraper."""
        logger.info("=" * 70)
        logger.info(f"🤖 Automated Scraper Run Started at {datetime.now()}")
        logger.info("=" * 70)
        
        try:
            # Run the scraper
            stats = self.runner.run()
            
            # Log summary
            logger.info("\n📊 Run Summary:")
            logger.info(f"   Companies processed: {stats['companies_processed']}")
            logger.info(f"   Jobs fetched: {stats['jobs_fetched']}")
            logger.info(f"   New jobs: {stats['jobs_new']}")
            logger.info(f"   Updated jobs: {stats['jobs_updated']}")
            logger.info(f"   Errors: {stats['errors']}")
            logger.info(f"   Notifications sent: {stats['notifications_sent']}")
            
            # Get health summary
            health_summary = self.health_monitor.get_health_summary()
            logger.info(f"\n💊 Health Summary:")
            logger.info(f"   Healthy: {health_summary['healthy']}/{health_summary['total']}")
            logger.info(f"   Degraded: {health_summary['degraded']}")
            logger.info(f"   Failed: {health_summary['failed']}")
            
            # Check for failing URLs
            failing_urls = self.health_monitor.get_failing_urls(min_failures=5)
            if failing_urls:
                logger.warning(f"\n⚠️  {len(failing_urls)} URLs failing (5+ failures):")
                for url_info in failing_urls[:5]:  # Show top 5
                    logger.warning(f"   - {url_info['company']} ({url_info['ats_type']}): {url_info['failure_count']} failures")
            
        except Exception as e:
            logger.error(f"❌ Scraper run failed: {e}", exc_info=True)
        
        logger.info("=" * 70)
        logger.info(f"✅ Automated Scraper Run Completed at {datetime.now()}")
        logger.info("=" * 70 + "\n")
    
    def start(self, schedule: str = "every_6_hours"):
        """
        Start the scheduler.
        
        Args:
            schedule: Schedule type
                - 'every_6_hours': Run every 6 hours
                - 'every_4_hours': Run every 4 hours
                - 'daily': Run daily at 9 AM and 6 PM
                - 'custom': Use cron expression
        """
        if schedule == "every_6_hours":
            # Run every 6 hours
            self.scheduler.add_job(
                self.run_scraper,
                'interval',
                hours=6,
                id='scraper_job',
                name='Job Scraper (Every 6 Hours)'
            )
            logger.info("📅 Scheduler configured: Every 6 hours")
        
        elif schedule == "every_4_hours":
            # Run every 4 hours
            self.scheduler.add_job(
                self.run_scraper,
                'interval',
                hours=4,
                id='scraper_job',
                name='Job Scraper (Every 4 Hours)'
            )
            logger.info("📅 Scheduler configured: Every 4 hours")
        
        elif schedule == "daily":
            # Run twice daily: 9 AM and 6 PM
            self.scheduler.add_job(
                self.run_scraper,
                CronTrigger(hour='9,18', minute=0),
                id='scraper_job',
                name='Job Scraper (Daily at 9 AM and 6 PM)'
            )
            logger.info("📅 Scheduler configured: Daily at 9 AM and 6 PM")
        
        else:
            logger.error(f"Unknown schedule: {schedule}")
            return
        
        # Run immediately on start
        logger.info("🚀 Running initial scrape...")
        self.run_scraper()
        
        # Start scheduler
        logger.info("⏰ Scheduler started. Press Ctrl+C to stop.")
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("\n👋 Scheduler stopped by user")
            self.scheduler.shutdown()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Job Scraper Scheduler')
    parser.add_argument(
        '--schedule',
        choices=['every_6_hours', 'every_4_hours', 'daily'],
        default='every_6_hours',
        help='Schedule frequency'
    )
    
    args = parser.parse_args()
    
    scheduler = JobScraperScheduler()
    scheduler.start(schedule=args.schedule)


if __name__ == "__main__":
    main()
