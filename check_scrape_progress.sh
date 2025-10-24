#!/bin/bash
# Check scraping progress and verify all companies are being scraped

echo "======================================================================"
echo "🔍 JOB SCRAPER STATUS CHECK"
echo "======================================================================"
echo ""

echo "📋 Watchlist Configuration:"
echo "  Total companies: $(grep -c '^  - company:' config/watchlist.yaml)"
echo ""

echo "📊 Database Statistics:"
docker exec job_tracker_worker python -c "
from src.core.database import get_db_context
from src.core.models import Job
from sqlalchemy import func

with get_db_context() as db:
    total = db.query(Job).count()
    active = db.query(Job).filter(Job.is_active == True).count()
    companies = db.query(Job.company).distinct().count()
    
    print(f'  Total jobs in DB: {total}')
    print(f'  Active jobs: {active}')
    print(f'  Unique companies: {companies}')
"
echo ""

echo "🏢 Companies with Jobs:"
docker exec job_tracker_worker python -c "
from src.core.database import get_db_context
from src.core.models import Job
from sqlalchemy import func

with get_db_context() as db:
    companies = db.query(
        Job.company, 
        func.count(Job.id).label('count')
    ).filter(
        Job.is_active == True
    ).group_by(
        Job.company
    ).order_by(
        func.count(Job.id).desc()
    ).limit(10).all()
    
    print('  Top 10 companies with most jobs:')
    for company, count in companies:
        print(f'    • {company}: {count} jobs')
"
echo ""

echo "⏰ Schedule Status:"
echo "  Current schedule: Every 4 hours"
echo "  Times (UTC): 00:00, 04:00, 08:00, 12:00, 16:00, 20:00"
echo ""

echo "🔄 Services Status:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep job_tracker
echo ""

echo "======================================================================"
echo "✅ To watch live scraping:"
echo "  docker logs -f job_tracker_worker"
echo ""
echo "✅ To manually scrape all companies:"
echo "  docker-compose run --rm worker python -m src.ingest.runner"
echo ""
echo "✅ To check dashboard:"
echo "  http://localhost:8000"
echo "======================================================================"
