#!/bin/bash
# Run the job scraper for all companies

echo "🚀 Starting Job Scraper..."
docker-compose run --rm worker python -m src.ingest.runner "$@"
