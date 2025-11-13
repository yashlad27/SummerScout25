#!/bin/bash
# Switch between optimized and full watchlist

set -e

OPTIMIZED="config/watchlist_optimized.yaml"
FULL="config/watchlist_full_257.yaml"
CURRENT="config/watchlist.yaml"

if [ "$1" == "optimized" ]; then
    if [ ! -f "$OPTIMIZED" ]; then
        echo "❌ Optimized watchlist not found. Run: python3 -c 'import yaml; ...' first"
        exit 1
    fi
    cp "$OPTIMIZED" "$CURRENT"
    echo "✅ Switched to OPTIMIZED watchlist (37 fast companies)"
    echo "   - Greenhouse: 23"
    echo "   - Lever: 8"
    echo "   - Workday: 6"
    echo "   - Estimated run time: 5-10 minutes"
elif [ "$1" == "full" ]; then
    if [ ! -f "$FULL" ]; then
        echo "❌ Full watchlist not found at $FULL"
        exit 1
    fi
    cp "$FULL" "$CURRENT"
    echo "✅ Switched to FULL watchlist (257 companies)"
    echo "   - Estimated run time: 60-90 minutes with timeouts"
else
    echo "Usage: ./switch_watchlist.sh [optimized|full]"
    echo ""
    echo "Current watchlist stats:"
    echo "  Total companies: $(grep -c '^- company:' $CURRENT || echo 'N/A')"
    echo ""
    echo "Available options:"
    echo "  optimized - Fast API-based companies only (37 companies, ~5-10 min)"
    echo "  full      - All 257 companies (~60-90 min with timeouts)"
    exit 1
fi
