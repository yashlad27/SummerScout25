#!/usr/bin/env bash
# Batch Scraping Script - Scrape companies by category for better performance
# Usage: ./scrape_batch.sh [batch_type]
# Example: ./scrape_batch.sh fintech

set -e

echo "======================================================================"
echo "🚀 BATCH SCRAPING - By Company Type"
echo "======================================================================"
echo ""

# Function to get companies for a batch type (bash 3.x compatible)
get_batch_companies() {
    case "$1" in
        fraud)
            echo "Sift,Feedzai,BioCatch,Signifyd,Forter,Kount,Riskified,DataVisor,Socure,Arkose Labs,Castle"
            ;;
        payment)
            echo "Adyen,Checkout.com,Modern Treasury,Lithic,Unit,Finix,Bolt,Rapyd,Nuvei,Payoneer,Wise,Remitly,Melio,Bill.com,Tipalti"
            ;;
        trading)
            echo "Citadel Securities,Virtu Financial,Tower Research Capital,Five Rings Capital,Belvedere Trading,Flow Traders,Millennium Management,Point72,Bridgewater Associates,Voleon Group,PDT Partners,Radix Trading,Old Mission Capital,GTS,Schonfeld Strategic Advisors"
            ;;
        fintech)
            echo "Stripe,Coinbase,Affirm,Plaid,Brex,Ramp,Mercury,Gusto,Rippling,Marqeta,SoFi,Chime,Robinhood,PayPal,Block,Navan,Klarna,Upstart"
            ;;
        bigtech)
            echo "Google,Meta,Amazon,Apple,Microsoft,Netflix,Tesla,Adobe,Salesforce,Oracle,IBM,Cisco,VMware,Intuit,Workday"
            ;;
        quant)
            echo "Citadel,Two Sigma,Jane Street,HRT,D.E. Shaw,Jump Trading,Optiver,IMC Trading,Akuna Capital,Susquehanna,DRW"
            ;;
        cloud)
            echo "Databricks,Snowflake,Confluent,MongoDB,Elastic,HashiCorp,Splunk,Datadog"
            ;;
        security)
            echo "CrowdStrike,Palo Alto Networks,Okta,Zscaler,Wiz,Snyk,Rapid7,SentinelOne,Tenable,Fortinet,Lacework,Abnormal Security"
            ;;
        ai)
            echo "OpenAI,Anthropic,Scale AI,Hugging Face,Cohere,Weights & Biases,Replicate,Modal,Runway,Stability AI,Character.AI,Perplexity AI"
            ;;
        gaming)
            echo "Unity,Roblox,Epic Games,Riot Games,Bungie"
            ;;
        social)
            echo "Reddit,Snap,Pinterest,TikTok,Twitch,Discord"
            ;;
        devtools)
            echo "GitHub,GitLab,Atlassian,Postman,LaunchDarkly,Vercel,Supabase,PlanetScale,Railway,Render"
            ;;
        enterprise)
            echo "ServiceNow,Twilio,HubSpot,Asana,Notion,Airtable,Monday.com,ClickUp,Miro,Canva"
            ;;
        mobility)
            echo "Uber,DoorDash,Instacart,Waymo,Cruise,Aurora,Zoox,Nuro"
            ;;
        ecommerce)
            echo "Shopify,Wayfair,Faire,Flexport,BigCommerce"
            ;;
        health)
            echo "Oscar Health,Ro,Hims & Hers,Tempus"
            ;;
        edtech)
            echo "Coursera,Udemy,Duolingo,Quizlet,Grammarly"
            ;;
        data)
            echo "Fivetran,dbt Labs,Airbyte,Starburst Data,Census,Hightouch,Amplitude,Mixpanel"
            ;;
        banking)
            echo "JPMorgan Chase,Goldman Sachs,Morgan Stanley,Capital One,Bloomberg"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Show available batches if no argument
if [ $# -eq 0 ]; then
    echo "Available batch types:"
    echo ""
    echo "  🔥 RECOMMENDED FOR YOUR EXPERIENCE:"
    echo "  fraud      - Fraud Detection (Sift, Feedzai, BioCatch...) (11 companies, ~2 min)"
    echo "  payment    - Payment Infrastructure (Adyen, Stripe, Modern Treasury...) (15 companies, ~3 min)"
    echo "  trading    - Trading Firms (Citadel Securities, Virtu, Tower...) (15 companies, ~3 min)"
    echo ""
    echo "  OTHER CATEGORIES:"
    echo "  fintech    - Fintech companies (18 companies, ~3 min)"
    echo "  bigtech    - FAANG + Big Tech (15 companies, ~6-8 min)"
    echo "  quant      - Original Quant firms (11 companies, ~2-3 min)"
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
    echo "🔍 SCRAPING ALL 327 COMPANIES..."
    echo "⏱️  Estimated time: 30-40 minutes"
    echo ""
    docker-compose run --rm worker python -m src.ingest.runner
else
    # Get companies for this batch type
    COMPANIES=$(get_batch_companies "$BATCH_TYPE")
    
    # Check if batch exists
    if [ -z "$COMPANIES" ]; then
        echo "❌ Unknown batch type: $BATCH_TYPE"
        echo "Run './scrape_batch.sh' without arguments to see available batches"
        exit 1
    fi
    
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
