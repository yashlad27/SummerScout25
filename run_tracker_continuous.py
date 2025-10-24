#!/usr/bin/env python3
"""
Continuous Job Tracker - Runs every 30 minutes
Checks all 107 companies for Summer 2026 internships
"""

import time
import logging
from datetime import datetime
from src.ingest.runner import JobTrackerRunner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_tracker.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Run job tracker continuously every 30 minutes."""
    
    logger.info("=" * 60)
    logger.info("🚀 STARTING CONTINUOUS JOB TRACKER")
    logger.info("=" * 60)
    logger.info("Tracking 107 companies for Summer 2026 internships")
    logger.info("Check interval: Every 30 minutes")
    logger.info("Email notifications: yashlad727@gmail.com")
    logger.info("=" * 60)
    
    run_count = 0
    
    while True:
        try:
            run_count += 1
            start_time = datetime.now()
            
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 RUN #{run_count} - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'='*60}")
            
            # Run the job tracker for all companies
            runner = JobTrackerRunner(dry_run=False)  # Set to False to actually save and send emails
            stats = runner.run_all()
            
            # Log summary
            logger.info(f"\n{'='*60}")
            logger.info(f"✅ RUN #{run_count} COMPLETE")
            logger.info(f"{'='*60}")
            logger.info(f"Companies processed: {stats['companies_processed']}")
            logger.info(f"Jobs fetched:        {stats['jobs_fetched']}")
            logger.info(f"Jobs filtered out:   {stats['jobs_filtered']}")
            logger.info(f"Jobs new:            {stats['jobs_new']}")
            logger.info(f"Jobs updated:        {stats['jobs_updated']}")
            logger.info(f"Notifications sent:  {stats['notifications_sent']}")
            logger.info(f"Errors:              {stats['errors']}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Duration:            {duration:.1f} seconds")
            
            # Wait 30 minutes before next run
            logger.info(f"\n💤 Sleeping for 30 minutes...")
            logger.info(f"Next run at: {datetime.now().replace(minute=(datetime.now().minute + 30) % 60).strftime('%H:%M:%S')}")
            logger.info(f"{'='*60}\n")
            
            time.sleep(1800)  # 30 minutes = 1800 seconds
            
        except KeyboardInterrupt:
            logger.info("\n\n⚠️  Received stop signal (Ctrl+C)")
            logger.info(f"Total runs completed: {run_count}")
            logger.info("Shutting down gracefully...")
            break
            
        except Exception as e:
            logger.error(f"\n❌ ERROR in run #{run_count}: {str(e)}", exc_info=True)
            logger.info("Waiting 5 minutes before retry...")
            time.sleep(300)  # Wait 5 minutes on error
            continue

if __name__ == "__main__":
    main()
