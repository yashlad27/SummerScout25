#!/bin/bash
# Show scraped jobs from database
# Usage: ./show_jobs.sh [company_name]

echo "======================================================================"
echo "📊 CURRENT JOB LISTINGS"
echo "======================================================================"
echo ""

# Start database if not running
if ! docker ps | grep -q job_tracker_db; then
    echo "🔧 Starting database..."
    docker-compose up -d db
    sleep 3
fi

if [ -n "$1" ]; then
    echo "🏢 Company: $1"
    echo ""
    docker-compose exec -T db psql -U jobtracker -d job_tracker -c "
    SELECT 
        title,
        location,
        DATE(created_at) as added
    FROM jobs 
    WHERE is_active = true 
      AND company ILIKE '%$1%'
    ORDER BY created_at DESC;
    "
else
    echo "🏢 All Companies"
    echo ""
    docker-compose exec -T db psql -U jobtracker -d job_tracker -c "
    SELECT 
        company,
        COUNT(*) as jobs,
        MAX(created_at)::date as last_updated
    FROM jobs 
    WHERE is_active = true
    GROUP BY company
    ORDER BY jobs DESC;
    "
fi

echo ""
echo "======================================================================"
echo "Total jobs: $(docker-compose exec -T db psql -U jobtracker -d job_tracker -t -c "SELECT COUNT(*) FROM jobs WHERE is_active = true;")"
echo "======================================================================"
