"""Main runner for job scraping pipeline."""

import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from src.core.config import get_config_loader
from src.core.database import get_db_context
from src.core.models import Job
from src.ingest.classifier import JobClassifier, JobFilter
from src.ingest.deduper import JobDeduper
from src.ingest.batch_processor import BatchJobProcessor
from src.ingest.normalizer import JobNormalizer
from src.ingest.registry import get_scraper
from src.ingest.schemas import WatchlistTarget
from src.utils.logging_config import get_logger, setup_logging
from src.utils.notifiers import NotificationManager
from src.utils.excel_exporter import ExcelExporter

logger = get_logger(__name__)


class JobTrackerRunner:
    """Main runner for the job tracking pipeline."""
    
    def __init__(self, dry_run: bool = False, max_workers: int = 5, batch_size: int = 50):
        """Initialize runner.
        
        Args:
            dry_run: If True, don't persist to database or send notifications
            max_workers: Maximum number of parallel scrapers
            batch_size: Number of jobs to insert per batch
        """
        self.dry_run = dry_run
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.normalizer = JobNormalizer()
        self.classifier = JobClassifier()
        self.job_filter = JobFilter()
        
        logger.info(f"Initialized JobTrackerRunner (dry_run={dry_run}, parallel={max_workers}, batch={batch_size})")
    
    def run(self, company_filter: str | None = None, config_path: str | None = None, country: str = "us") -> dict[str, Any]:
        """Run the job tracking pipeline.
        
        Args:
            company_filter: Optional company name filter
            config_path: Optional path to watchlist config file
            country: Country for jobs (us or india)
            
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
        
        # Collect all new and updated job IDs for batch notification
        all_new_job_ids = []
        all_updated_job_ids = []
        companies_scanned = []
        
        # Load watchlist from specified path or default
        config_loader = get_config_loader()
        if config_path:
            import yaml
            from pathlib import Path
            with open(Path(config_path), 'r') as f:
                watchlist_config = yaml.safe_load(f)
        else:
            watchlist_config = config_loader.load_watchlist()
        targets = watchlist_config.get("targets", [])
        
        if not targets:
            logger.warning("No targets in watchlist")
            return stats
        
        # Filter targets if company filter specified
        if company_filter:
            targets = [t for t in targets if company_filter.lower() in t["company"].lower()]
            logger.info(f"Filtered to {len(targets)} targets matching '{company_filter}'")
        
        # Process targets in parallel
        logger.info(f"🚀 Starting parallel scrape of {len(targets)} companies (workers={self.max_workers})...")
        logger.info("=" * 60)
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scraping tasks
            future_to_target = {}
            for idx, target_config in enumerate(targets, 1):
                try:
                    target = WatchlistTarget(**target_config)
                    target_country = target.country if hasattr(target, 'country') and target.country else country
                    
                    future = executor.submit(self._process_target_safe, target, target_country, idx, len(targets))
                    future_to_target[future] = target.company
                    companies_scanned.append(target.company)
                except Exception as e:
                    logger.error(f"Failed to submit target {target_config.get('company')}: {e}")
                    stats["errors"] += 1
            
            # Process completed tasks as they finish
            for future in as_completed(future_to_target):
                company = future_to_target[future]
                try:
                    target_stats, new_job_ids, updated_job_ids = future.result()
                    
                    # Collect new and updated job IDs
                    all_new_job_ids.extend(new_job_ids)
                    all_updated_job_ids.extend(updated_job_ids)
                    
                    # Aggregate stats
                    for key in stats:
                        if key in target_stats:
                            stats[key] += target_stats[key]
                    
                    stats["companies_processed"] += 1
                
                except Exception as e:
                    logger.error(f"Failed to process {company}: {e}")
                    stats["errors"] += 1
        
        # Send consolidated notification for all new and updated jobs
        if (all_new_job_ids or all_updated_job_ids) and not self.dry_run:
            total_jobs = len(all_new_job_ids) + len(all_updated_job_ids)
            logger.info(f"Sending consolidated notification for {len(all_new_job_ids)} new + {len(all_updated_job_ids)} updated jobs")
            with get_db_context() as db:
                # Fetch the jobs in this session
                from src.core.models import Job
                all_job_ids = all_new_job_ids + all_updated_job_ids
                jobs = db.query(Job).filter(Job.id.in_(all_job_ids)).all()
                
                notification_manager = NotificationManager(db)
                notification_manager.notify_batch(
                    jobs, 
                    companies_scanned=companies_scanned,
                    new_count=len(all_new_job_ids),
                    updated_count=len(all_updated_job_ids)
                )
                db.commit()  # Commit the alerts
                stats["notifications_sent"] = 1  # One batch email
        
        # Print final summary
        logger.info("=" * 60)
        logger.info("✅ Pipeline Complete!")
        logger.info(f"   Companies processed: {stats['companies_processed']}")
        logger.info(f"   Jobs fetched: {stats['jobs_fetched']}")
        logger.info(f"   Jobs filtered out: {stats['jobs_filtered']}")
        logger.info(f"   New jobs: {stats['jobs_new']}")
        logger.info(f"   Updated jobs: {stats['jobs_updated']}")
        logger.info(f"   Errors: {stats['errors']}")
        logger.info(f"   Notifications: {stats['notifications_sent']}")
        logger.info("=" * 60)
        
        # Export to Excel if not dry run
        if not self.dry_run and (stats['jobs_new'] > 0 or stats['jobs_updated'] > 0):
            self._export_to_excel()
        
        return stats
    
    def _process_target_safe(self, target: WatchlistTarget, country: str, idx: int, total: int) -> tuple[dict[str, Any], list, list]:
        """Thread-safe wrapper for processing a target with logging.
        
        Args:
            target: Watchlist target
            country: Country for jobs
            idx: Index of target in list
            total: Total number of targets
            
        Returns:
            Tuple of (statistics, new job IDs, updated job IDs)
        """
        logger.info(f"[{idx}/{total}] 📍 {target.company} ({target.ats_type})")
        start_time = time.time()
        
        try:
            stats, new_ids, updated_ids = self._process_target(target, country)
            elapsed = time.time() - start_time
            logger.info(f"   ✅ {target.company}: {stats['jobs_new']} new, {stats['jobs_updated']} updated ({elapsed:.1f}s)")
            return stats, new_ids, updated_ids
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"   ❌ {target.company} failed after {elapsed:.1f}s: {e}")
            raise
    
    def _process_target(self, target: WatchlistTarget, country: str = "us") -> tuple[dict[str, Any], list, list]:
        """Process a single watchlist target.
        
        Args:
            target: Watchlist target
            country: Country for jobs (us or india)
            
        Returns:
            Tuple of (statistics dictionary, list of new job IDs, list of updated job IDs)
        """
        stats = {
            "jobs_fetched": 0,
            "jobs_filtered": 0,
            "jobs_new": 0,
            "jobs_updated": 0,
            "notifications_sent": 0,
        }
        
        new_job_ids = []
        updated_job_ids = []
        
        # Get scraper
        scraper = get_scraper(target)
        if not scraper:
            logger.warning(f"⚠️  No scraper available for {target.ats_type}")
            return stats, new_job_ids, updated_job_ids
        
        # Fetch raw jobs with retry mechanism
        raw_jobs = self._fetch_with_retry(scraper, target.company, max_retries=2)
        stats["jobs_fetched"] = len(raw_jobs)
        
        if not raw_jobs:
            logger.info(f"   ➜ 0 jobs found")
            return stats, new_job_ids, updated_job_ids
        
        # Process jobs using batch processor for better performance
        with get_db_context() as db:
            batch_processor = BatchJobProcessor(db, batch_size=self.batch_size)
            
            for raw_job in raw_jobs:
                try:
                    # Normalize
                    normalized_job = self.normalizer.normalize(raw_job)
                    
                    # Set country
                    normalized_job.country = country
                    
                    # Classify
                    category = self.classifier.classify(normalized_job)
                    
                    # Filter
                    should_include, reason = self.job_filter.should_include(normalized_job)
                    
                    if not should_include:
                        logger.debug(f"Filtered out: {normalized_job.title} ({reason})")
                        stats["jobs_filtered"] += 1
                        continue
                    
                    # Add tags
                    tags = self.job_filter.add_tags(normalized_job)
                    
                    # Add to batch processor
                    if not self.dry_run:
                        batch_processor.add_job(normalized_job, category, tags)
                    else:
                        # Dry run - just log
                        logger.info(
                            f"[DRY RUN] Would process: {normalized_job.company} - "
                            f"{normalized_job.title} [{category}]"
                        )
                        stats["jobs_new"] += 1
                
                except Exception as e:
                    logger.error(f"Failed to process job {raw_job.source_id}: {e}")
                    continue
            
            # Flush remaining jobs in batch
            if not self.dry_run:
                batch_processor.flush()
                db.commit()
                
                # Get stats from batch processor
                new_ids, updated_ids = batch_processor.get_stats()
                new_job_ids.extend(new_ids)
                updated_job_ids.extend(updated_ids)
                stats["jobs_new"] = len(new_ids)
                stats["jobs_updated"] = len(updated_ids)
        
        logger.info(f"   ➜ Found {stats['jobs_fetched']} jobs, included {stats['jobs_new']} new, {stats['jobs_updated']} updated")
        return stats, new_job_ids, updated_job_ids
    
    def _fetch_with_retry(self, scraper, company_name: str, max_retries: int = 2):
        """Fetch jobs with retry mechanism for transient failures.
        
        Args:
            scraper: Scraper instance
            company_name: Name of company being scraped
            max_retries: Maximum number of retry attempts
            
        Returns:
            List of raw jobs
        """
        for attempt in range(max_retries + 1):
            try:
                raw_jobs = scraper.fetch()
                return raw_jobs
            except Exception as e:
                error_msg = str(e)
                
                # Don't retry on certain errors
                if any(x in error_msg for x in ["404", "Not Found", "DNS", "HTTP2 protocol error", "Blocked"]):
                    logger.error(f"   ❌ Non-retryable error for {company_name}: {error_msg[:100]}")
                    return []
                
                # Retry on timeout or transient errors
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 5  # 5s, 10s
                    logger.warning(f"   ⚠️  Attempt {attempt + 1} failed for {company_name}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"   ❌ All {max_retries + 1} attempts failed for {company_name}")
                    return []
        
        return []
    
    def _export_to_excel(self):
        """Export scraped jobs to Excel file."""
        try:
            exporter = ExcelExporter()
            
            # Export all active jobs
            filepath = exporter.export_jobs()
            
            if filepath:
                logger.info(f"📊 Excel export saved to: {filepath}")
                
                # Also export by category
                filepath_cat = exporter.export_by_category()
                if filepath_cat:
                    logger.info(f"📊 Category export saved to: {filepath_cat}")
            
        except Exception as e:
            logger.error(f"Failed to export to Excel: {e}")


def main():
    """CLI entry point."""
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Job Tracker Runner - High Performance Edition")
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
    parser.add_argument(
        "--config",
        type=str,
        help="Path to watchlist config file (e.g., config/india/watchlist_india.yaml)",
    )
    parser.add_argument(
        "--country",
        type=str,
        default="us",
        choices=["us", "india"],
        help="Country for jobs (us or india)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of parallel workers for scraping (default: 5, max recommended: 10)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of jobs to process per database batch (default: 50)",
    )
    
    args = parser.parse_args()
    
    runner = JobTrackerRunner(
        dry_run=args.dry_run,
        max_workers=args.workers,
        batch_size=args.batch_size
    )
    stats = runner.run(
        company_filter=args.company,
        config_path=args.config,
        country=args.country
    )
    
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
