#!/bin/bash
# Validate all job links from the watchlist

echo "🔍 Validating job links from watchlist..."
python validate_job_links.py
echo ""
echo "✅ Results saved to: link_validation_results.yaml"
