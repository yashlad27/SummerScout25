#!/bin/bash
# One-Command Job Scraper
# Usage: ./scrape.sh [company_name]
# Example: ./scrape.sh Google
# Example: ./scrape.sh  (scrapes all companies)

set -e

echo "======================================================================"
echo "🚀 STARTING JOB SCRAPER"
echo "======================================================================"
echo ""

# Check if company filter provided
COMPANY_FILTER=""
if [ -n "$1" ]; then
    COMPANY_FILTER="--company \"$1\""
    echo "📋 Scraping: $1"
else
    echo "📋 Scraping: All 327 companies from US watchlist"
    echo "⏱️  Estimated time: 30-40 minutes"
    echo ""
    echo "💡 TIP: Use ./scrape_batch.sh for faster targeted scraping:"
    echo "   ./scrape_batch.sh fraud    (11 companies, ~2 min)"
    echo "   ./scrape_batch.sh payment  (15 companies, ~3 min)"
    echo "   ./scrape_batch.sh trading  (15 companies, ~3 min)"
fi
echo ""

# Start database and API for dashboard
echo "🔧 Starting database and API..."
docker-compose up -d db redis api
sleep 3

# Wait for database to be ready
echo "⏳ Waiting for database..."
until docker-compose exec -T db pg_isready -U jobtracker > /dev/null 2>&1; do
    sleep 1
done

# Run migrations
echo "📦 Running migrations..."
docker-compose run --rm migrate

# Run the scraper
echo ""
echo "======================================================================"
echo "🔍 SCRAPING JOBS..."
echo "======================================================================"
echo ""

if [ -n "$1" ]; then
    docker-compose run --rm worker python -m src.ingest.runner --company "$1"
else
    docker-compose run --rm worker python -m src.ingest.runner
fi

# Show results
echo ""
echo "======================================================================"
echo "📊 RESULTS"
echo "======================================================================"
echo ""

docker-compose exec -T db psql -U jobtracker -d job_tracker -c "
SELECT 
    company,
    COUNT(*) as total_jobs,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '1 hour') as new_jobs
FROM jobs 
WHERE is_active = true AND country = 'us'
GROUP BY company
ORDER BY total_jobs DESC
LIMIT 20;
"

echo ""
echo "📄 Generating export files..."
docker-compose run --rm worker python -m src.utils.export_jobs us

echo ""
echo "======================================================================"
echo "✅ SCRAPE COMPLETE"
echo "======================================================================"
echo ""
echo "🌐 Dashboard: http://localhost:8000"
echo "📊 View results in your browser!"
echo ""

# Ask what to do next
echo "What would you like to do?"
echo "  1) Keep dashboard running (recommended)"
echo "  2) Stop everything"
echo ""
read -p "Choice (1 or 2): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[2]$ ]]; then
    echo "🛑 Stopping all services..."
    docker-compose down
    echo "✅ Everything stopped!"
else
    echo "✅ Dashboard running at: http://localhost:8000"
    echo ""
    echo "To view: open http://localhost:8000"
    echo "To stop: docker-compose down"
    echo ""
    
    # Open browser automatically
    if command -v open &> /dev/null; then
        echo "🌐 Opening dashboard in browser..."
        sleep 1
        open http://localhost:8000
    fi
fi

echo ""
echo "======================================================================"
