#!/bin/bash
# Run the job scraper in dry-run mode (no database changes)

echo "🧪 Starting Job Scraper (DRY RUN - no changes will be saved)..."
docker-compose run --rm worker python -m src.ingest.runner --dry-run "$@"
