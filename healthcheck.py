#!/usr/bin/env python3
"""
Comprehensive health check for Job Tracker system.
Verifies all components are working correctly.
"""

import sys
from datetime import datetime

from src.core.config import get_settings
from src.core.database import get_db_context
from src.core.models import Job, Alert
from src.utils.logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


def check_database():
    """Check database connectivity and schema."""
    print("\n🔍 Checking Database...")
    try:
        with get_db_context() as db:
            # Test connection
            job_count = db.query(Job).count()
            alert_count = db.query(Alert).count()
            
            # Get recent jobs
            recent_jobs = db.query(Job).order_by(Job.created_at.desc()).limit(5).all()
            
            print(f"  ✅ Database connected")
            print(f"  📊 Total jobs: {job_count}")
            print(f"  📧 Total alerts: {alert_count}")
            
            if recent_jobs:
                print(f"\n  📋 Most recent jobs:")
                for job in recent_jobs:
                    print(f"    - {job.company}: {job.title} ({job.category or 'uncategorized'})")
            
            return True
            
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False


def check_configuration():
    """Check configuration settings."""
    print("\n🔍 Checking Configuration...")
    settings = get_settings()
    
    checks = {
        "Database URL": bool(settings.database_url),
        "Redis URL": bool(settings.redis_url),
        "SMTP Server": bool(settings.smtp_server),
        "SMTP User": bool(settings.smtp_user),
        "SMTP Password": bool(settings.smtp_pass),
    }
    
    all_ok = True
    for check_name, result in checks.items():
        status = "✅" if result else "⚠️"
        print(f"  {status} {check_name}: {'Configured' if result else 'Missing'}")
        if not result and "SMTP" not in check_name:
            all_ok = False
    
    return all_ok


def check_watchlist():
    """Check watchlist configuration."""
    print("\n🔍 Checking Watchlist...")
    try:
        from src.core.config import get_config_loader
        
        config_loader = get_config_loader()
        watchlist = config_loader.load_watchlist()
        targets = watchlist.get("targets", [])
        
        print(f"  ✅ Watchlist loaded")
        print(f"  🏢 Companies configured: {len(targets)}")
        
        # Show sample companies
        if targets:
            print(f"\n  📋 Sample companies:")
            for target in targets[:5]:
                print(f"    - {target.get('company')} ({target.get('ats_type')})")
            
            if len(targets) > 5:
                print(f"    ... and {len(targets) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Watchlist error: {e}")
        return False


def check_scrapers():
    """Check available scrapers."""
    print("\n🔍 Checking Scrapers...")
    try:
        from src.ingest.registry import list_supported_ats
        
        ats_types = list_supported_ats()
        print(f"  ✅ Scrapers available: {len(ats_types)}")
        print(f"  🔧 Supported ATS types:")
        for ats_type in ats_types:
            print(f"    - {ats_type}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Scraper error: {e}")
        return False


def check_notifiers():
    """Check notification system."""
    print("\n🔍 Checking Notifiers...")
    try:
        from src.core.database import get_db_context
        from src.utils.notifiers import NotificationManager
        
        with get_db_context() as db:
            notifier_manager = NotificationManager(db)
            channels = list(notifier_manager.notifiers.keys())
            
            print(f"  ✅ Notification manager initialized")
            print(f"  📧 Active channels: {', '.join(channels) if channels else 'None'}")
            
            if not channels:
                print(f"  ⚠️  No notification channels configured")
            
            return True
            
    except Exception as e:
        print(f"  ❌ Notifier error: {e}")
        return False


def main():
    """Run all health checks."""
    print("=" * 70)
    print("🏥 JOB TRACKER HEALTH CHECK")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    checks = [
        ("Configuration", check_configuration),
        ("Database", check_database),
        ("Watchlist", check_watchlist),
        ("Scrapers", check_scrapers),
        ("Notifiers", check_notifiers),
    ]
    
    results = {}
    for check_name, check_func in checks:
        results[check_name] = check_func()
    
    print("\n" + "=" * 70)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 70)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL CHECKS PASSED - System is healthy!")
    else:
        print("⚠️  SOME CHECKS FAILED - Review errors above")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
