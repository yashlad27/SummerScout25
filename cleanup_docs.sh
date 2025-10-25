#!/bin/bash
# Cleanup unnecessary documentation files

echo "🧹 Cleaning up documentation files..."
echo ""

# Move important docs to docs/ folder
mkdir -p docs

# Keep these files
echo "✅ Keeping essential files:"
echo "  - README.md (main documentation)"
echo "  - ON_DEMAND_USAGE.md (usage guide)"
echo ""

# Files to archive
echo "📦 Archiving old documentation to docs/archive/:"
mkdir -p docs/archive

OLD_DOCS=(
    "ADD_REMAINING.md"
    "DASHBOARD_READY.md"
    "DOCKER_SETUP.md"
    "FRONTEND_GUIDE.md"
    "IMPROVEMENTS_SUMMARY.md"
    "JOB_AGGREGATOR_SCRAPERS.md"
    "NOTIFICATION_CHANGES.md"
    "QUICKSTART.md"
    "QUICK_REFERENCE.md"
    "QUICK_START.md"
    "RUN_OPTIONS.md"
    "SCHEDULE_CONFIG.md"
    "SETUP.md"
    "START_HERE.md"
    "TERMINAL_ONLY_SETUP.md"
    "WATCH_SCRAPER.md"
)

for doc in "${OLD_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        mv "$doc" docs/archive/
        echo "  ✓ $doc"
    fi
done

# Keep important ones
mv docs/archive/CONTRIBUTING.md . 2>/dev/null || true
mv docs/archive/SECURITY.md . 2>/dev/null || true

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📁 Current structure:"
echo "  README.md           - Main documentation"
echo "  ON_DEMAND_USAGE.md  - Usage guide"
echo "  CONTRIBUTING.md     - Contribution guidelines"
echo "  SECURITY.md         - Security policy"
echo "  docs/archive/       - Old documentation"
echo ""
echo "Ready for GitHub! 🚀"
