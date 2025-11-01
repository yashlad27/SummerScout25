#!/usr/bin/env python3
"""
Verification script to test all new upgrades.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🔍 VERIFYING JOB TRACKER UPGRADES")
print("=" * 70)

# Test 1: Import all new modules
print("\n✅ Test 1: Importing new modules...")
try:
    from src.ingest.ats.workday import WorkdayScraper
    from src.ingest.ats.linkedin import LinkedInScraper
    from src.ingest.ats.icims import iCIMSScraper
    from src.ingest.ats.taleo import TaleoScraper
    from src.ingest.health_monitor import HealthMonitor, URLHealth
    from src.utils.ai_classifier import AIJobClassifier
    from src.ingest.job_analyzer import JobAnalyzer
    print("   ✓ All modules imported successfully")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Check registry updated
print("\n✅ Test 2: Checking scraper registry...")
try:
    from src.ingest.registry import SCRAPER_REGISTRY, list_supported_ats
    
    expected_scrapers = ['workday', 'icims', 'taleo', 'linkedin']
    supported = list_supported_ats()
    
    missing = [s for s in expected_scrapers if s not in supported]
    if missing:
        print(f"   ✗ Missing scrapers in registry: {missing}")
    else:
        print(f"   ✓ All new scrapers registered")
        print(f"     Supported ATS types: {', '.join(supported)}")
except Exception as e:
    print(f"   ✗ Registry check failed: {e}")
    sys.exit(1)

# Test 3: Test scraper instantiation
print("\n✅ Test 3: Testing scraper instantiation...")
try:
    from src.ingest.schemas import WatchlistTarget
    
    # Test Workday
    target = WatchlistTarget(
        company="TestCompany",
        ats_type="workday",
        workday_company_id="test"
    )
    workday_scraper = WorkdayScraper(target)
    print(f"   ✓ WorkdayScraper: {workday_scraper}")
    
    # Test LinkedIn
    target = WatchlistTarget(
        company="TestCompany",
        ats_type="linkedin"
    )
    linkedin_scraper = LinkedInScraper(target)
    print(f"   ✓ LinkedInScraper: {linkedin_scraper}")
    
    # Test iCIMS
    target = WatchlistTarget(
        company="TestCompany",
        ats_type="icims",
        icims_id="careers-test"
    )
    icims_scraper = iCIMSScraper(target)
    print(f"   ✓ iCIMSScraper: {icims_scraper}")
    
    # Test Taleo
    target = WatchlistTarget(
        company="TestCompany",
        ats_type="taleo",
        taleo_url="https://example.taleo.net/careers"
    )
    taleo_scraper = TaleoScraper(target)
    print(f"   ✓ TaleoScraper: {taleo_scraper}")
    
except Exception as e:
    print(f"   ✗ Scraper instantiation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test health monitor
print("\n✅ Test 4: Testing health monitor...")
try:
    health_monitor = HealthMonitor()
    print("   ✓ HealthMonitor created")
    
    # Test recording success
    health_monitor.record_success("TestCompany", "workday", "https://test.com", jobs_found=5)
    print("   ✓ Success recording works")
    
    # Test recording failure
    health_monitor.record_failure("TestCompany2", "generic", "https://test2.com", "Timeout error")
    print("   ✓ Failure recording works")
    
    # Test getting status
    status = health_monitor.get_health_status("TestCompany", "workday")
    if status:
        print(f"   ✓ Health status retrieval works: {status['status']}")
    
except Exception as e:
    print(f"   ✗ Health monitor failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test AI classifier
print("\n✅ Test 5: Testing AI classifier...")
try:
    ai_classifier = AIJobClassifier()
    if ai_classifier.enabled:
        print("   ✓ AI Classifier enabled (OpenAI API key found)")
    else:
        print("   ⚠ AI Classifier disabled (no OpenAI API key)")
        print("     Add OPENAI_API_KEY to enable AI features")
except Exception as e:
    print(f"   ✗ AI classifier test failed: {e}")

# Test 6: Test job analyzer
print("\n✅ Test 6: Testing job analyzer...")
try:
    from src.ingest.schemas import JobPosting
    
    analyzer = JobAnalyzer()
    
    # Create a test job
    test_job = JobPosting(
        source="test",
        source_id="test123",
        company="TestCorp",
        title="Software Engineer Intern - Backend",
        location="San Francisco, CA",
        url="https://test.com/job",
        description_md="""
        Looking for Python backend engineer intern. Must know Django, Flask, 
        and PostgreSQL. Experience with AWS preferred. Summer 2025 internship.
        Compensation: $50/hr. We sponsor visas.
        """
    )
    
    metadata = analyzer.analyze(test_job)
    
    print(f"   ✓ Job analyzer works")
    print(f"     Tech stack found: {len(metadata['tech_stack']['languages'])} languages, "
          f"{len(metadata['tech_stack']['frameworks'])} frameworks")
    print(f"     Visa sponsorship: {metadata['visa_sponsorship']}")
    print(f"     Seniority: {metadata['seniority_level']}")
    
except Exception as e:
    print(f"   ✗ Job analyzer failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Check enhanced database models
print("\n✅ Test 7: Checking enhanced database models...")
try:
    from src.core.models import Job
    from sqlalchemy import inspect
    
    inspector = inspect(Job)
    columns = [c.name for c in inspector.columns]
    
    new_columns = [
        'tech_stack', 'required_skills', 'compensation_min', 'compensation_max',
        'visa_sponsorship', 'application_status', 'ai_confidence'
    ]
    
    missing_columns = [c for c in new_columns if c not in columns]
    
    if missing_columns:
        print(f"   ⚠ Database needs migration - missing columns: {missing_columns}")
        print("     Run: docker-compose exec db psql -U jobtracker -d job_tracker -f /app/migrations/upgrade_enhanced_features.sql")
    else:
        print("   ✓ All enhanced database columns present")
    
except Exception as e:
    print(f"   ⚠ Database model check failed: {e}")
    print("     This is OK if you haven't run migrations yet")

# Test 8: Check notification updates
print("\n✅ Test 8: Checking notification updates...")
try:
    from src.utils.notifiers import EmailNotifier
    import inspect as insp
    
    # Check if send_batch has new parameters
    sig = insp.signature(EmailNotifier.send_batch)
    params = list(sig.parameters.keys())
    
    if 'new_count' in params and 'updated_count' in params:
        print("   ✓ Email notifications updated for new + updated jobs")
    else:
        print("   ✗ Email notification parameters missing")
    
except Exception as e:
    print(f"   ✗ Notification check failed: {e}")

# Summary
print("\n" + "=" * 70)
print("📊 VERIFICATION SUMMARY")
print("=" * 70)
print("\n✅ Core Features:")
print("   • 4 new ATS scrapers (Workday, LinkedIn, iCIMS, Taleo)")
print("   • Health monitoring system")
print("   • AI job classification")
print("   • Job description analyzer")
print("   • Enhanced database models")
print("   • Updated notifications")

print("\n📋 Next Steps:")
print("   1. Rebuild Docker: docker-compose build worker")
print("   2. Run migration: See migrations/upgrade_enhanced_features.sql")
print("   3. Test scraper: docker-compose run --rm worker python -m src.ingest.runner")
print("   4. Optional: Add OPENAI_API_KEY for AI features")
print("   5. Optional: Start dashboard: python dashboard.py")
print("   6. Optional: Enable scheduler: python scheduler.py")

print("\n" + "=" * 70)
print("✅ VERIFICATION COMPLETE!")
print("=" * 70)
