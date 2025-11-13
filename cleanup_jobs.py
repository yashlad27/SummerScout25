#!/usr/bin/env python3
"""
Job Cleanup Script

This script marks jobs as inactive based on various criteria:
1. Jobs not seen in the last N days (default: 30)
2. Duplicate jobs that should be removed
3. Jobs from deactivated watchlist companies
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.database import get_db_context
from src.core.models import Job, Watchlist
from sqlalchemy import and_, func
from src.utils.logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


class JobCleanup:
    """Handle job cleanup operations."""
    
    def __init__(self, dry_run: bool = True):
        """
        Initialize cleanup handler.
        
        Args:
            dry_run: If True, only show what would be cleaned up
        """
        self.dry_run = dry_run
    
    def mark_stale_jobs_inactive(self, days: int = 30) -> int:
        """
        Mark jobs as inactive if not seen in the last N days.
        
        Args:
            days: Number of days threshold
            
        Returns:
            Number of jobs marked inactive
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with get_db_context() as db:
            # Find jobs that haven't been seen since the cutoff date
            stale_jobs = db.query(Job).filter(
                and_(
                    Job.is_active == True,
                    Job.last_seen_at < cutoff_date
                )
            ).all()
            
            count = len(stale_jobs)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would mark {count} stale jobs as inactive (not seen in {days} days)")
                
                # Show sample jobs
                if stale_jobs:
                    logger.info("Sample stale jobs:")
                    for job in stale_jobs[:10]:
                        days_since = (datetime.utcnow() - job.last_seen_at).days
                        logger.info(f"  - {job.company}: {job.title} (last seen {days_since} days ago)")
            else:
                # Actually mark them inactive
                for job in stale_jobs:
                    job.is_active = False
                
                db.commit()
                logger.info(f"Marked {count} stale jobs as inactive")
            
            return count
    
    def remove_jobs_from_inactive_companies(self) -> int:
        """
        Mark jobs as inactive if their company is no longer in the active watchlist.
        
        Returns:
            Number of jobs marked inactive
        """
        with get_db_context() as db:
            # Get all active companies from watchlist
            active_companies = db.query(Watchlist.company).filter(
                Watchlist.is_active == True
            ).all()
            active_company_names = [c[0] for c in active_companies]
            
            # Find jobs from companies not in the watchlist
            orphaned_jobs = db.query(Job).filter(
                and_(
                    Job.is_active == True,
                    ~Job.company.in_(active_company_names)
                )
            ).all()
            
            count = len(orphaned_jobs)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would mark {count} jobs from inactive companies as inactive")
                
                # Show companies
                if orphaned_jobs:
                    companies = set(job.company for job in orphaned_jobs)
                    logger.info(f"Companies not in watchlist: {sorted(companies)[:20]}")
            else:
                for job in orphaned_jobs:
                    job.is_active = False
                
                db.commit()
                logger.info(f"Marked {count} jobs from inactive companies as inactive")
            
            return count
    
    def get_cleanup_stats(self) -> dict:
        """
        Get statistics about jobs that need cleanup.
        
        Returns:
            Dictionary with cleanup statistics
        """
        with get_db_context() as db:
            total_jobs = db.query(Job).count()
            active_jobs = db.query(Job).filter(Job.is_active == True).count()
            inactive_jobs = db.query(Job).filter(Job.is_active == False).count()
            
            # Jobs not seen in last 30 days
            cutoff_30 = datetime.utcnow() - timedelta(days=30)
            stale_30_days = db.query(Job).filter(
                and_(
                    Job.is_active == True,
                    Job.last_seen_at < cutoff_30
                )
            ).count()
            
            # Jobs not seen in last 60 days
            cutoff_60 = datetime.utcnow() - timedelta(days=60)
            stale_60_days = db.query(Job).filter(
                and_(
                    Job.is_active == True,
                    Job.last_seen_at < cutoff_60
                )
            ).count()
            
            # Jobs not seen in last 90 days
            cutoff_90 = datetime.utcnow() - timedelta(days=90)
            stale_90_days = db.query(Job).filter(
                and_(
                    Job.is_active == True,
                    Job.last_seen_at < cutoff_90
                )
            ).count()
            
            return {
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "inactive_jobs": inactive_jobs,
                "stale_30_days": stale_30_days,
                "stale_60_days": stale_60_days,
                "stale_90_days": stale_90_days,
            }
    
    def print_stats(self):
        """Print cleanup statistics."""
        stats = self.get_cleanup_stats()
        
        print("\n" + "=" * 80)
        print("JOB CLEANUP STATISTICS")
        print("=" * 80)
        print(f"📊 Total Jobs in Database:     {stats['total_jobs']:,}")
        print(f"✅ Active Jobs:                {stats['active_jobs']:,}")
        print(f"❌ Inactive Jobs:              {stats['inactive_jobs']:,}")
        print()
        print("🕐 Stale Jobs (Still Active):")
        print(f"   • Not seen in 30 days:      {stats['stale_30_days']:,}")
        print(f"   • Not seen in 60 days:      {stats['stale_60_days']:,}")
        print(f"   • Not seen in 90 days:      {stats['stale_90_days']:,}")
        print("=" * 80)
    
    def cleanup_all(self, days: int = 30) -> dict:
        """
        Run all cleanup operations.
        
        Args:
            days: Number of days threshold for stale jobs
            
        Returns:
            Dictionary with cleanup results
        """
        results = {}
        
        logger.info(f"Starting cleanup (dry_run={self.dry_run}, stale_threshold={days} days)")
        
        # Mark stale jobs inactive
        results['stale_jobs'] = self.mark_stale_jobs_inactive(days)
        
        # Remove jobs from inactive companies
        results['orphaned_jobs'] = self.remove_jobs_from_inactive_companies()
        
        return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Clean up old and inactive jobs in the job tracker database"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days since last seen to mark jobs as inactive (default: 30)",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only show statistics, don't perform cleanup",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform cleanup (default is dry-run mode)",
    )
    parser.add_argument(
        "--stale-only",
        action="store_true",
        help="Only mark stale jobs inactive, skip other cleanup",
    )
    
    args = parser.parse_args()
    
    cleanup = JobCleanup(dry_run=not args.execute)
    
    if args.stats_only:
        cleanup.print_stats()
        return 0
    
    print("\n" + "=" * 80)
    if args.execute:
        print("⚠️  CLEANUP MODE: LIVE - Changes will be made to the database!")
    else:
        print("🔍 DRY RUN MODE - No changes will be made")
    print("=" * 80)
    
    # Show stats first
    cleanup.print_stats()
    
    # Confirm if executing
    if args.execute:
        print("\n⚠️  WARNING: This will mark jobs as inactive in the database!")
        confirm = input("Type 'yes' to proceed: ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelled")
            return 1
    
    print()
    
    # Run cleanup
    if args.stale_only:
        results = {'stale_jobs': cleanup.mark_stale_jobs_inactive(args.days)}
    else:
        results = cleanup.cleanup_all(args.days)
    
    # Print results
    print("\n" + "=" * 80)
    print("CLEANUP RESULTS")
    print("=" * 80)
    for key, count in results.items():
        print(f"{key}: {count} jobs")
    print("=" * 80)
    
    if not args.execute:
        print("\n💡 To actually perform cleanup, add --execute flag")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
