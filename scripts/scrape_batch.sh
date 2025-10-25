#!/usr/bin/env bash
# Batch Scraping Script - Scrape companies by category for better performance
# Usage: ./scrape_batch.sh [batch_type]
# Example: ./scrape_batch.sh fintech

set -e

echo "======================================================================"
echo "🚀 BATCH SCRAPING - By Company Type"
echo "======================================================================"
echo ""

# Batch types and their companies (using bash 4+ associative arrays)
declare -A BATCHES

# Fintech companies (Fast scraping - usually good career pages)
BATCHES[fintech]="Stripe,Coinbase,Affirm,Plaid,Brex,Ramp,Mercury,Gusto,Rippling,Marqeta,SoFi,Chime,Robinhood,PayPal,Block,Navan"

# FAANG + Big Tech (Can be slow)
BATCHES[bigtech]="Google,Meta,Amazon,Apple,Microsoft,Netflix,Tesla,Adobe,Salesforce,Oracle,IBM"

# Quant/Trading Firms (Usually fast)
BATCHES[quant]="Citadel,Two Sigma,Jane Street,HRT,D.E. Shaw,Jump Trading,Optiver,IMC Trading,Akuna Capital,Susquehanna,DRW"

# Cloud/Data Infrastructure (Medium speed)
BATCHES[cloud]="Databricks,Snowflake,Confluent,MongoDB,Elastic,HashiCorp,Splunk,Datadog"

# Cybersecurity (Fast)
BATCHES[security]="CrowdStrike,Palo Alto Networks,Okta,Zscaler,Wiz,Snyk,Rapid7,SentinelOne,Tenable,Fortinet,Lacework,Abnormal Security"

# AI/ML Startups (Very fast - small companies)
BATCHES[ai]="OpenAI,Anthropic,Scale AI,Hugging Face,Cohere,Weights & Biases,Replicate,Modal,Runway,Stability AI,Character.AI,Perplexity AI"

# Gaming (Medium speed)
BATCHES[gaming]="Unity,Roblox,Epic Games,Riot Games,Bungie"

# Social/Content (Can be slow)
BATCHES[social]="Reddit,Snap,Pinterest,TikTok,Twitch,Discord"

# Developer Tools (Fast)
BATCHES[devtools]="GitHub,GitLab,Atlassian,Postman,LaunchDarkly,Vercel,Supabase,PlanetScale,Railway,Render"

# Enterprise SaaS (Medium speed)
BATCHES[enterprise]="ServiceNow,Twilio,HubSpot,Asana,Notion,Airtable,Monday.com,ClickUp,Miro,Canva"

# Ride-sharing/Delivery (Medium speed)
BATCHES[mobility]="Uber,DoorDash,Instacart,Waymo,Cruise,Aurora,Zoox,Nuro"

# E-commerce (Medium speed)
BATCHES[ecommerce]="Shopify,Wayfair,Faire,Flexport,BigCommerce"

# Health Tech (Fast)
BATCHES[health]="Oscar Health,Ro,Hims & Hers,Tempus"

# EdTech (Fast)
BATCHES[edtech]="Coursera,Udemy,Duolingo,Quizlet,Grammarly"

# Data/Analytics (Fast)
BATCHES[data]="Fivetran,dbt Labs,Airbyte,Starburst Data,Census,Hightouch,Amplitude,Mixpanel"

# Banking/Financial Services (Can be slow)
BATCHES[banking]="JPMorgan Chase,Goldman Sachs,Morgan Stanley,Capital One,Bloomberg"

# Show available batches if no argument
if [ $# -eq 0 ]; then
    echo "Available batch types:"
    echo ""
    echo "  fintech    - Fintech companies (16 companies, ~2-3 min)"
    echo "  bigtech    - FAANG + Big Tech (11 companies, ~5-8 min)"
    echo "  quant      - Quant/Trading firms (11 companies, ~2-3 min)"
    echo "  cloud      - Cloud/Data Infrastructure (8 companies, ~2 min)"
    echo "  security   - Cybersecurity (12 companies, ~2-3 min)"
    echo "  ai         - AI/ML Startups (12 companies, ~2 min)"
    echo "  gaming     - Gaming companies (5 companies, ~1 min)"
    echo "  social     - Social/Content platforms (6 companies, ~3-4 min)"
    echo "  devtools   - Developer Tools (10 companies, ~2 min)"
    echo "  enterprise - Enterprise SaaS (10 companies, ~2-3 min)"
    echo "  mobility   - Ride-sharing/Delivery (8 companies, ~2-3 min)"
    echo "  ecommerce  - E-commerce (5 companies, ~1 min)"
    echo "  health     - Health Tech (4 companies, ~1 min)"
    echo "  edtech     - EdTech (5 companies, ~1 min)"
    echo "  data       - Data/Analytics (8 companies, ~2 min)"
    echo "  banking    - Banking/Financial (5 companies, ~3-4 min)"
    echo "  all        - All companies (187 companies, ~25-30 min)"
    echo ""
    echo "Usage: ./scrape_batch.sh [batch_type]"
    echo "Example: ./scrape_batch.sh fintech"
    echo ""
    exit 0
fi

BATCH_TYPE=$1

# Start database and API if not running
docker-compose up -d db redis api > /dev/null 2>&1
sleep 2

# Wait for database
echo "⏳ Waiting for database..."
until docker-compose exec -T db pg_isready -U jobtracker > /dev/null 2>&1; do
    sleep 1
done

# Run migrations
echo "📦 Running migrations..."
docker-compose run --rm migrate > /dev/null 2>&1

if [ "$BATCH_TYPE" == "all" ]; then
    echo "🔍 SCRAPING ALL 187 COMPANIES..."
    echo "⏱️  Estimated time: 25-30 minutes"
    echo ""
    docker-compose run --rm worker python -m src.ingest.runner
else
    # Check if batch exists
    if [ -z "${BATCHES[$BATCH_TYPE]}" ]; then
        echo "❌ Unknown batch type: $BATCH_TYPE"
        echo "Run './scrape_batch.sh' without arguments to see available batches"
        exit 1
    fi
    
    COMPANIES="${BATCHES[$BATCH_TYPE]}"
    COMPANY_COUNT=$(echo "$COMPANIES" | tr ',' '\n' | wc -l | tr -d ' ')
    
    echo "🔍 SCRAPING BATCH: $BATCH_TYPE"
    echo "📊 Companies: $COMPANY_COUNT"
    echo ""
    
    # Scrape each company in the batch
    IFS=',' read -ra COMPANY_ARRAY <<< "$COMPANIES"
    for company in "${COMPANY_ARRAY[@]}"; do
        echo "  → $company..."
        docker-compose run --rm worker python -m src.ingest.runner --company "$company" 2>&1 | grep -E "(Processing|Found|jobs)" | tail -2
    done
fi

# Show results
echo ""
echo "======================================================================"
echo "📊 BATCH RESULTS"
echo "======================================================================"
echo ""

docker-compose exec -T db psql -U jobtracker -d job_tracker -c "
SELECT 
    company,
    COUNT(*) as total_jobs,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '1 hour') as new_jobs
FROM jobs 
WHERE is_active = true
GROUP BY company
ORDER BY total_jobs DESC
LIMIT 20;
"

echo ""
echo "======================================================================"
echo "✅ BATCH SCRAPE COMPLETE"
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
