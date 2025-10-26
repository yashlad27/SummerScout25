#!/bin/bash
# India Internship Scraper
# Usage: ./scrape_india.sh [company_name]

set -e

echo "======================================================================"
echo "🇮🇳 INDIA INTERNSHIP SCRAPER - Summer 2026"
echo "======================================================================"
echo ""

# Check if company filter provided
if [ -n "$1" ]; then
    echo "📋 Scraping: $1"
else
    echo "📋 Scraping: All Indian companies"
fi
echo ""

# Start database and India API
echo "🔧 Starting services..."
docker-compose up -d db redis api-india
sleep 3

# Wait for database
echo "⏳ Waiting for database..."
until docker-compose exec -T db pg_isready -U jobtracker > /dev/null 2>&1; do
    sleep 1
done

# Run migrations
echo "📦 Running migrations..."
docker-compose run --rm migrate

# Run scraper with India config
echo ""
echo "======================================================================"
echo "🔍 SCRAPING INDIAN COMPANIES..."
echo "======================================================================"
echo ""

START_TIME=$(date +%s)

if [ -n "$1" ]; then
    # Single company - simple mode
    docker-compose run --rm worker python -m src.ingest.runner \
        --config config/india/watchlist_india.yaml \
        --country india \
        --company "$1"
else
    # Full scrape with progress tracking
    TOTAL_COMPANIES=32
    PROCESSED=0
    
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  🚀 Starting India scrape of $TOTAL_COMPANIES companies"
    echo "║  ⏱️  Estimated time: 5-8 minutes"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Run scraper and parse output for progress
    docker-compose run --rm worker python -m src.ingest.runner \
        --config config/india/watchlist_india.yaml \
        --country india 2>&1 | while IFS= read -r line; do
        echo "$line"
        
        # Extract company processing info and count
        if [[ "$line" =~ "Processing "(.+)" \(" ]]; then
            PROCESSED=$((PROCESSED + 1))
            COMPANY="${BASH_REMATCH[1]}"
            REMAINING=$((TOTAL_COMPANIES - PROCESSED))
            PERCENT=$((PROCESSED * 100 / TOTAL_COMPANIES))
            
            # Calculate timing
            CURRENT_TIME=$(date +%s)
            ELAPSED=$((CURRENT_TIME - START_TIME))
            ELAPSED_MIN=$((ELAPSED / 60))
            ELAPSED_SEC=$((ELAPSED % 60))
            
            # Estimate remaining time
            if [ "$PROCESSED" -gt 0 ]; then
                AVG_TIME=$((ELAPSED / PROCESSED))
                EST_REMAINING=$((AVG_TIME * REMAINING))
                EST_MIN=$((EST_REMAINING / 60))
                EST_SEC=$((EST_REMAINING % 60))
            else
                EST_MIN=0
                EST_SEC=0
            fi
            
            # Progress bar
            BAR_WIDTH=40
            FILLED=$((PERCENT * BAR_WIDTH / 100))
            EMPTY=$((BAR_WIDTH - FILLED))
            
            # Generate bars (handle edge cases)
            if [ $FILLED -gt 0 ]; then
                BAR=$(printf '█%.0s' $(seq 1 $FILLED))
            else
                BAR=""
            fi
            
            if [ $EMPTY -gt 0 ]; then
                EMPTY_BAR=$(printf '░%.0s' $(seq 1 $EMPTY))
            else
                EMPTY_BAR=""
            fi
            
            echo ""
            echo "╔════════════════════════════════════════════════════════════════╗"
            echo "║  PROGRESS: [$BAR$EMPTY_BAR] $PERCENT%"
            echo "║  Company: $PROCESSED of $TOTAL_COMPANIES  |  Remaining: $REMAINING"
            echo "║  Elapsed: ${ELAPSED_MIN}m ${ELAPSED_SEC}s  |  Est. Left: ${EST_MIN}m ${EST_SEC}s"
            echo "╚════════════════════════════════════════════════════════════════╝"
        fi
    done
fi

# Final timing
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))
TOTAL_MIN=$((TOTAL_TIME / 60))
TOTAL_SEC=$((TOTAL_TIME % 60))

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ INDIA SCRAPING COMPLETE"
echo "║  Total Time: ${TOTAL_MIN}m ${TOTAL_SEC}s"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Show results
echo ""
echo "======================================================================"
echo "📊 INDIA RESULTS"
echo "======================================================================"
echo ""

docker-compose exec -T db psql -U jobtracker -d job_tracker -c "
SELECT 
    company,
    COUNT(*) as total_jobs,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '1 hour') as new_jobs
FROM jobs 
WHERE is_active = true AND country = 'india'
GROUP BY company
ORDER BY total_jobs DESC
LIMIT 20;
"

echo ""
echo "📄 Generating export files..."
docker-compose run --rm worker python -m src.utils.export_jobs india

echo ""
echo "======================================================================"
echo "✅ INDIA SCRAPE COMPLETE"
echo "======================================================================"
echo ""
echo "🌐 Dashboard: http://localhost:8001"
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
    echo "✅ Dashboard running at: http://localhost:8001"
    echo ""
    echo "To view: open http://localhost:8001"
    echo "To stop: docker-compose down"
    echo ""
    
    # Open browser automatically
    if command -v open &> /dev/null; then
        echo "🌐 Opening dashboard in browser..."
        sleep 1
        open http://localhost:8001
    fi
fi

echo ""
echo "======================================================================"
