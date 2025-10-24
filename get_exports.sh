#!/bin/bash

# Script to copy exported files from Docker container to local directory

echo "📦 Copying exported job files from container..."
echo ""

# Create exports directory if it doesn't exist
mkdir -p exports

# Copy files
echo "Copying jobs_export.csv..."
docker cp job_tracker_worker:/app/jobs_export.csv exports/ 2>/dev/null || echo "  ⚠️  File not found"

echo "Copying jobs_formatted.txt..."
docker cp job_tracker_worker:/app/jobs_formatted.txt exports/ 2>/dev/null || echo "  ⚠️  File not found"

echo "Copying category files..."
docker cp job_tracker_worker:/app/jobs_by_category_ml_ai.txt exports/ 2>/dev/null || echo "  ⚠️  ML/AI file not found"
docker cp job_tracker_worker:/app/jobs_by_category_data_science.txt exports/ 2>/dev/null || echo "  ⚠️  Data Science file not found"
docker cp job_tracker_worker:/app/jobs_by_category_data_engineering.txt exports/ 2>/dev/null || echo "  ⚠️  Data Engineering file not found"
docker cp job_tracker_worker:/app/jobs_by_category_cybersecurity.txt exports/ 2>/dev/null || echo "  ⚠️  Cybersecurity file not found"
docker cp job_tracker_worker:/app/jobs_by_category_uncategorized.txt exports/ 2>/dev/null || echo "  ⚠️  Uncategorized file not found"

echo ""
echo "✅ Done! Check the 'exports' directory:"
echo ""
ls -lh exports/ 2>/dev/null || echo "No files found"
echo ""
echo "📂 Open exports directory: open exports/"
