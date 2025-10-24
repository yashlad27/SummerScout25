"""Main runner for job scraping pipeline."""

import argparse
from typing import Any

from src.core.config import get_config_loader
from src.core.database import get_db_context
from src.ingest.classifier import JobClassifier, JobFilter
from src.ingest.deduper import JobDeduper
from src.ingest.normalizer import JobNormalizer
from src.ingest.registry import get_scraper
from src.ingest.schemas import WatchlistTarget
from src.utils.logging_config import get_logger, setup_logging
from src.utils.notifiers import NotificationManager

logger = get_logger(__name__)


class JobTrackerRunner:
    """Main runner for the job tracking pipeline."""
    
    def __init__(self, dry_run: bool = False):
        """Initialize runner.
        
        Args:
            dry_run: If True, don't persist to database or send notifications
        """
        self.dry_run = dry_run
        self.normalizer = JobNormalizer()
        self.classifier = JobClassifier()
        self.job_filter = JobFilter()
        
        logger.info(f"Initialized JobTrackerRunner (dry_run={dry_run})")
    
    def run(self, company_filter: str | None = None) -> dict[str, Any]:
        """Run the job tracking pipeline.
        
        Args:
            company_filter: Optional company name filter
            
        Returns:
            Dictionary with run statistics
        """
        stats = {
            "companies_processed": 0,
            "jobs_fetched": 0,
            "jobs_filtered": 0,
            "jobs_new": 0,
            "jobs_updated": 0,
            "notifications_sent": 0,
            "errors": 0,
        }
        
        # Load watchlist
        config_loader = get_config_loader()
        watchlist_config = config_loader.load_watchlist()
        targets = watchlist_config.get("targets", [])
        
        if not targets:
            logger.warning("No targets in watchlist")
            return stats
        
        # Filter targets if company filter specified
        if company_filter:
            targets = [t for t in targets if company_filter.lower() in t["company"].lower()]
            logger.info(f"Filtered to {len(targets)} targets matching '{company_filter}'")
        
        # Process each target
        for target_config in targets:
            try:
                target = WatchlistTarget(**target_config)
                target_stats = self._process_target(target)
                
                # Aggregate stats
                for key in stats:
                    if key in target_stats:
                        stats[key] += target_stats[key]
                
                stats["companies_processed"] += 1
            
            except Exception as e:
                logger.error(f"Failed to process target {target_config.get('company')}: {e}")
                stats["errors"] += 1
                continue
        
        logger.info(f"Pipeline complete: {stats}")
        return stats
    
    def _process_target(self, target: WatchlistTarget) -> dict[str, Any]:
        """Process a single watchlist target.
        
        Args:
            target: Watchlist target
            
        Returns:
            Statistics dictionary
        """
        stats = {
            "jobs_fetched": 0,
            "jobs_filtered": 0,
            "jobs_new": 0,
            "jobs_updated": 0,
            "notifications_sent": 0,
        }
        
        logger.info(f"Processing {target.company} ({target.ats_type})")
        
        # Get scraper
        scraper = get_scraper(target)
        if not scraper:
            logger.warning(f"No scraper available for {target.ats_type}")
            return stats
        
        # Fetch raw jobs
        raw_jobs = scraper.fetch()
        stats["jobs_fetched"] = len(raw_jobs)
        
        if not raw_jobs:
            logger.info(f"No jobs found for {target.company}")
            return stats
        
        # Process each job
        with get_db_context() as db:
            deduper = JobDeduper(db)
            notification_manager = NotificationManager(db)
            
            for raw_job in raw_jobs:
                try:
                    # Normalize
                    normalized_job = self.normalizer.normalize(raw_job)
                    
                    # Classify
                    category = self.classifier.classify(normalized_job)
                    normalized_job.category = category
                    
                    # Filter
                    should_include, reason = self.job_filter.should_include(normalized_job)
                    
                    if not should_include:
                        logger.debug(f"Filtered out: {normalized_job.title} ({reason})")
                        stats["jobs_filtered"] += 1
                        continue
                    
                    # Add tags
                    tags = self.job_filter.add_tags(normalized_job)
                    normalized_job.tags = tags
                    
                    # Deduplicate and persist
                    if not self.dry_run:
                        db_job, is_new = deduper.process_job(normalized_job)
                        
                        if is_new:
                            stats["jobs_new"] += 1
                            logger.info(f"New job: {db_job.company} - {db_job.title}")
                            
                            # Send notification
                            notification_manager.notify(db_job, alert_type="new")
                            stats["notifications_sent"] += 1
                        else:
                            stats["jobs_updated"] += 1
                    else:
                        # Dry run - just log
                        logger.info(
                            f"[DRY RUN] Would process: {normalized_job.company} - "
                            f"{normalized_job.title} [{normalized_job.category}]"
                        )
                        stats["jobs_new"] += 1
                
                except Exception as e:
                    logger.error(f"Failed to process job {raw_job.source_id}: {e}")
                    continue
        
        return stats


def main():
    """CLI entry point."""
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Job Tracker Runner")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without persisting to database or sending notifications",
    )
    parser.add_argument(
        "--company",
        type=str,
        help="Filter to specific company name (case-insensitive substring match)",
    )
    
    args = parser.parse_args()
    
    runner = JobTrackerRunner(dry_run=args.dry_run)
    stats = runner.run(company_filter=args.company)
    
    print("\n" + "=" * 60)
    print("JOB TRACKER RUN SUMMARY")
    print("=" * 60)
    print(f"Companies processed: {stats['companies_processed']}")
    print(f"Jobs fetched:        {stats['jobs_fetched']}")
    print(f"Jobs filtered out:   {stats['jobs_filtered']}")
    print(f"Jobs new:            {stats['jobs_new']}")
    print(f"Jobs updated:        {stats['jobs_updated']}")
    print(f"Notifications sent:  {stats['notifications_sent']}")
    print(f"Errors:              {stats['errors']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
