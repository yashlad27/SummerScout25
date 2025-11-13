#!/bin/bash
# Start the automated scheduler (runs scraper every 6 hours)

SCHEDULE=${1:-every_6_hours}

echo "⏰ Starting Automated Scheduler (schedule: $SCHEDULE)..."
echo "Press Ctrl+C to stop"
python scheduler.py --schedule "$SCHEDULE"
