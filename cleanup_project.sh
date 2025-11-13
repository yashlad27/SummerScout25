#!/bin/bash
# Project cleanup script - removes redundant and old files
# Created: November 1, 2025

echo "🧹 Starting Project Cleanup..."
echo ""

# Create backup directory
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "📦 Backup directory created: $BACKUP_DIR"
echo ""

# Function to backup and delete
backup_and_delete() {
    local file=$1
    if [ -f "$file" ]; then
        echo "  📄 Backing up: $file"
        cp "$file" "$BACKUP_DIR/"
        rm "$file"
        echo "  ✅ Deleted: $file"
    fi
}

echo "🗑️  Removing redundant documentation files..."
backup_and_delete "CLI_GUIDE.md"
backup_and_delete "FILTER_FIXES_SUMMARY.md"
backup_and_delete "FIXES_APPLIED.md"
backup_and_delete "INDIA_INTERNSHIP_TRACKER.md"
backup_and_delete "NEW_COMPANIES_ADDED.md"
backup_and_delete "PROGRESS_TRACKER.md"
backup_and_delete "PROJECT_STATUS.md"
backup_and_delete "QUICK_START.md"
backup_and_delete "WATCHLIST_FIXES.md"
echo ""

echo "🗑️  Removing old debugging/utility scripts..."
backup_and_delete "fix_scrapers.py"
backup_and_delete "fix_scrapers_v2.py"
backup_and_delete "deep_scan_failures.py"
backup_and_delete "analyze_failures.py"
backup_and_delete "test_filters.py"
backup_and_delete "add_new_companies.py"
echo ""

echo "🗑️  Removing redundant shell scripts..."
backup_and_delete "scrape.sh"
backup_and_delete "scrape_batch.sh"
backup_and_delete "scrape_india.sh"
backup_and_delete "show_jobs.sh"
backup_and_delete "job_tracker.sh"
backup_and_delete "run_scraper.sh"
backup_and_delete "run_dry_run.sh"
backup_and_delete "start_dashboard.sh"
backup_and_delete "start_scheduler.sh"
backup_and_delete "validate_links.sh"
echo ""

echo "🗑️  Removing temporary/result files..."
backup_and_delete "link_validation_results.yaml"
backup_and_delete "DEMO_PROGRESS.txt"
backup_and_delete "scrape_output.log"
echo ""

echo "========================================"
echo "✅ CLEANUP COMPLETE!"
echo "========================================"
echo ""
echo "📊 Summary:"
echo "  • Removed redundant documentation (8 files)"
echo "  • Removed old scripts (15 files)"
echo "  • Removed temporary files (3 files)"
echo "  • Total cleaned: ~26 files"
echo ""
echo "📦 All files backed up to: $BACKUP_DIR"
echo ""
echo "🔧 Kept essential files:"
echo "  • run.sh (main command runner)"
echo "  • dashboard.py (web UI)"
echo "  • scheduler.py (automation)"
echo "  • validate_job_links.py (utility)"
echo "  • verify_upgrades.py (verification)"
echo "  • job_tracker_cli.py (CLI)"
echo "  • cleanup_jobs.py (maintenance)"
echo "  • healthcheck.py (monitoring)"
echo "  • README.md, UPGRADES.md, IMPLEMENTATION_SUMMARY.md"
echo ""
echo "💡 To restore any file:"
echo "   cp $BACKUP_DIR/filename ."
echo ""
