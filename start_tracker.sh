#!/bin/bash
# Easy start script for Job Tracker
# Runs continuously, checking all companies every 30 minutes

echo "======================================"
echo "🎯 JOB TRACKER - CONTINUOUS MODE"
echo "======================================"
echo "Companies: 107"
echo "Interval:  30 minutes"
echo "Email:     yashlad727@gmail.com"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run with Docker
docker-compose run --rm worker python run_tracker_continuous.py
