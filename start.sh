#!/bin/bash

# Job Tracker - One-Command Startup Script
# Usage: ./start.sh

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          🚀 JOB TRACKER - STARTUP SCRIPT                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is running
echo "📋 Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Check if we need to build
echo "🔧 Checking if images need to be built..."
if ! docker images | grep -q "linkedin_job_scrapper-worker"; then
    echo "🔨 Building Docker images (this may take a few minutes)..."
    docker-compose build
    echo "✅ Images built successfully"
else
    echo "✅ Images already built"
fi
echo ""

# Create database tables if needed
echo "🗄️  Setting up database..."
docker-compose up -d db redis
sleep 3

# Check if tables exist
TABLES=$(docker exec job_tracker_db psql -U jobtracker -d job_tracker -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='jobs';" 2>/dev/null || echo "0")

if [ "$TABLES" = "0" ] || [ -z "$TABLES" ]; then
    echo "📦 Creating database tables..."
    docker-compose run --rm worker python -c "from src.core.models import Job, JobVersion, Watchlist, Alert; from src.core.database import Base, engine; Base.metadata.create_all(engine); print('✅ Tables created!')"
else
    echo "✅ Database tables already exist"
fi
echo ""

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d
echo ""

# Wait a moment for services to stabilize
sleep 2

# Show status
echo "📊 Service Status:"
docker-compose ps
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ JOB TRACKER IS RUNNING!                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📧 Email notifications: yashlad727@gmail.com"
echo "⏰ Schedule: Every 4 hours (12am, 4am, 8am, 12pm, 4pm, 8pm)"
echo "🏢 Companies tracked: 108"
echo "🎯 Categories: ML/AI, Cybersecurity, Data Science, Data Engineering"
echo ""
echo "📋 Useful Commands:"
echo "   View logs:          docker-compose logs -f worker"
echo "   View schedule:      docker-compose logs -f beat"
echo "   Export jobs:        docker-compose run --rm worker python export_jobs.py"
echo "   Run scrape now:     docker-compose run --rm worker python -m src.ingest.runner"
echo "   Stop tracker:       docker-compose down"
echo ""
echo "🎉 All set! Jobs will be scraped automatically every 4 hours."
echo ""
