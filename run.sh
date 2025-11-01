#!/bin/bash
# Master script for job tracker operations

show_help() {
    cat << EOF
🎯 Job Tracker - Command Reference
====================================

Usage: ./run.sh <command> [options]

Commands:
  scrape              Run the job scraper for all companies
  scrape-company      Run scraper for specific company (e.g., ./run.sh scrape-company "Citadel")
  dry-run             Run scraper in dry-run mode (no database changes)
  dashboard           Start the web dashboard on http://localhost:5000
  scheduler           Start automated scheduler (runs every 6 hours)
  validate            Validate all job links from watchlist
  rebuild             Rebuild Docker worker image
  migrate             Run database migration
  health              Show health status of all URLs
  verify              Run verification tests
  help                Show this help message

Examples:
  ./run.sh scrape                      # Scrape all companies
  ./run.sh scrape-company "Google"     # Scrape only Google
  ./run.sh dry-run                     # Test run without saving
  ./run.sh dashboard                   # Start web UI
  ./run.sh scheduler                   # Auto-run every 6 hours

====================================
EOF
}

case "$1" in
    scrape)
        shift
        echo "🚀 Starting Job Scraper..."
        docker-compose run --rm worker python -m src.ingest.runner "$@"
        ;;
    
    scrape-company)
        if [ -z "$2" ]; then
            echo "❌ Error: Company name required"
            echo "Usage: ./run.sh scrape-company \"CompanyName\""
            exit 1
        fi
        echo "🚀 Starting Job Scraper for: $2"
        docker-compose run --rm worker python -m src.ingest.runner --company "$2"
        ;;
    
    dry-run)
        shift
        echo "🧪 Starting Job Scraper (DRY RUN)..."
        docker-compose run --rm worker python -m src.ingest.runner --dry-run "$@"
        ;;
    
    dashboard)
        echo "📊 Starting Web Dashboard..."
        echo "Open: http://localhost:5000"
        python dashboard.py
        ;;
    
    scheduler)
        SCHEDULE=${2:-every_6_hours}
        echo "⏰ Starting Scheduler (${SCHEDULE})..."
        python scheduler.py --schedule "$SCHEDULE"
        ;;
    
    validate)
        echo "🔍 Validating job links..."
        python validate_job_links.py
        ;;
    
    rebuild)
        echo "🔨 Rebuilding Docker worker..."
        docker-compose build worker
        ;;
    
    migrate)
        echo "📊 Running database migration..."
        docker-compose exec -T db psql -U jobtracker -d job_tracker < migrations/upgrade_enhanced_features.sql
        echo "✅ Migration complete!"
        ;;
    
    health)
        echo "💊 Checking URL health status..."
        docker-compose run --rm worker python -c "
from src.ingest.health_monitor import HealthMonitor
health = HealthMonitor()
summary = health.get_health_summary()
print(f'\n📊 Health Summary:')
print(f'  Healthy: {summary[\"healthy\"]}/{summary[\"total\"]}')
print(f'  Degraded: {summary[\"degraded\"]}')
print(f'  Failed: {summary[\"failed\"]}\n')
failing = health.get_failing_urls(min_failures=3)
if failing:
    print(f'⚠️  {len(failing)} URLs failing (3+ failures):')
    for url in failing[:10]:
        print(f'  - {url[\"company\"]} ({url[\"ats_type\"]}): {url[\"failure_count\"]} failures')
else:
    print('✅ No failing URLs!')
"
        ;;
    
    verify)
        echo "🔍 Running verification tests..."
        python verify_upgrades.py
        ;;
    
    help|--help|-h|"")
        show_help
        ;;
    
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
