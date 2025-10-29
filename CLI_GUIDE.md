# 🎯 Job Tracker CLI - User Guide

## 🚀 Quick Start

Launch the interactive CLI:
```bash
./job_tracker.sh
```

Or directly:
```bash
python3 job_tracker_cli.py
```

---

## 📋 Menu Options

### 1️⃣ Run Full Scrape (All 327 Companies)
- Scrapes all companies in your watchlist
- **Time:** ~30-60 minutes
- **Result:** Updates database + exports + master log
- **Use when:** Weekly/daily full refresh

### 2️⃣ Run Single Company Scrape
- Scrape just one company quickly
- Enter company name (e.g., "Databricks", "Citadel")
- **Time:** 10-30 seconds per company
- **Use when:** Checking specific company updates

### 3️⃣ View Today's Statistics
Shows:
- 🔍 Jobs processed today
- 🆕 New jobs found today
- 🔄 Jobs updated
- ✅ Total active jobs
- 🏢 Companies scraped
- 🏆 Top companies with new jobs

### 4️⃣ View New Jobs (Last 24 Hours)
- Lists ALL new jobs from past 24 hours
- Shows: Company, Title, Location, URL, Category
- Perfect for daily review

### 5️⃣ View All-Time Statistics
Shows:
- 📊 Total jobs ever tracked
- ✅ Active vs inactive jobs
- 🏢 Total companies tracked
- 📅 First and most recent jobs
- 🏷️ Jobs by category
- 🏆 Top 15 companies

### 6️⃣ View Recent Export Files
- Lists 10 most recent export files
- Shows file size and modification time
- Files in `exports/` directory

### 7️⃣ Export Master Job Log (CSV)
- **Creates/Updates:** `MASTER_JOB_LOG.csv` (main file)
- **Creates copy:** `exports/master_log_[timestamp].csv`
- **Contains:** ALL jobs with full details
- **Automatically updated** after every scrape

### 8️⃣ Search Jobs by Keyword
- Search by title, company, or location
- Shows up to 50 matching active jobs
- Case-insensitive search

### 9️⃣ View Jobs by Company
- Enter company name
- Shows all active jobs for that company
- Groups by exact company name

### 0️⃣ Exit
- Safely exit the application

---

## 💾 Master Job Log

### What is it?
A comprehensive CSV file containing **ALL jobs** ever tracked by the system.

### Location:
```
MASTER_JOB_LOG.csv (main file, always up-to-date)
exports/master_log_[timestamp].csv (timestamped snapshots)
```

### Columns:
```csv
ID, Company, Title, Location, Remote, Category, Employment Type, 
Posted Date, First Seen, Last Seen, Is Active, URL, Tags
```

### When is it updated?
- ✅ After every full scrape (Option 1)
- ✅ After every single company scrape (Option 2)
- ✅ Manually via Option 7

### Example Usage:
```bash
# Open in Excel/Google Sheets
open MASTER_JOB_LOG.csv

# View in terminal
cat MASTER_JOB_LOG.csv | less

# Count total jobs
wc -l MASTER_JOB_LOG.csv

# Search for specific company
grep "Databricks" MASTER_JOB_LOG.csv
```

---

## 📊 Daily Workflow Example

### Morning Routine:
```bash
./job_tracker.sh

# In the menu:
1. Press '4' → View new jobs from last 24 hours
2. Press '3' → Check today's statistics
3. Press '7' → Export updated master log
```

### Weekly Deep Dive:
```bash
./job_tracker.sh

# In the menu:
1. Press '1' → Run full scrape (all companies)
   [Wait 30-60 minutes]
2. Press '4' → Review all new jobs
3. Press '5' → Check all-time stats
4. Press '8' → Search for specific tech (e.g., "python", "ML")
```

### Quick Company Check:
```bash
./job_tracker.sh

# In the menu:
1. Press '2' → Run single company scrape
   Enter: "Citadel"
2. Press '9' → View jobs by company
   Enter: "Citadel"
```

---

## 🎨 Sample Output

### Today's Statistics:
```
📊 Today's Statistics
================================================================================
📅 Date: 2025-10-28

🔍 Jobs Processed Today:      247
🆕 New Jobs Found:            15
🔄 Jobs Updated:              232
✅ Total Active Jobs:         133
🏢 Companies Scraped:         45

🏆 Top Companies with New Jobs Today:
--------------------------------------------------------------------------------
  • Databricks: 4 jobs
  • Citadel: 3 jobs
  • HRT: 2 jobs
  • Voleon Group: 2 jobs
  • D.E. Shaw: 1 jobs
```

### New Jobs Display:
```
🆕 New Jobs (Last 24 Hours)
================================================================================
Found 15 new jobs:

🏢 Databricks
📋 Data Science Intern (2026 Start)
📍 San Francisco, California
🔗 https://www.databricks.com/company/careers/...
📅 First Seen: 2025-10-28 14:32
🏷️  Category: data_science
--------------------------------------------------------------------------------
```

---

## 🔧 Technical Details

### Database Connection:
- Uses SQLAlchemy with PostgreSQL
- Reads from same database as scraping pipeline
- No modifications to existing data structure

### Performance:
- Statistics queries are optimized with indexes
- Search limited to 50 results for speed
- Master log writes are atomic

### Error Handling:
- Database connection errors caught and displayed
- Invalid inputs handled gracefully
- Keyboard interrupt (Ctrl+C) exits cleanly

---

## 📁 File Structure

```
linkedin_job_scrapper/
├── job_tracker_cli.py          # Main CLI application
├── job_tracker.sh              # Launcher script
├── MASTER_JOB_LOG.csv          # Master log (auto-updated)
├── exports/
│   ├── jobs_us_20251028.txt   # Text exports
│   ├── jobs_us_20251028.xlsx  # Excel exports
│   └── master_log_*.csv       # Master log snapshots
└── CLI_GUIDE.md               # This guide
```

---

## 💡 Pro Tips

### 1. Master Log in Excel
- Open `MASTER_JOB_LOG.csv` in Excel/Google Sheets
- Use filters to sort by company, category, date
- Create pivot tables for analysis

### 2. Search Efficiently
- Use Option 8 with keywords like:
  - "python" → Python-related jobs
  - "ML" → Machine Learning positions
  - "Remote" → Remote opportunities
  - "San Francisco" → Location-specific

### 3. Track New Jobs Daily
- Run Option 4 every morning
- Export master log (Option 7) weekly
- Keep snapshots in `exports/` for history

### 4. Monitor Specific Companies
- Use Option 9 to track favorite companies
- Run Option 2 for quick single-company updates

### 5. Statistics for Reports
- Option 5 gives great overview for tracking progress
- Option 3 shows daily activity

---

## 🐛 Troubleshooting

### Database Connection Error:
```bash
# Make sure database is running
docker-compose up -d postgres

# Check connection
psql postgresql://user:password@localhost:5432/job_tracker
```

### Module Not Found:
```bash
# Make sure you're in the project directory
cd /path/to/linkedin_job_scrapper

# Verify Python path
python3 -c "import sys; print(sys.path)"
```

### Permission Denied:
```bash
# Make scripts executable
chmod +x job_tracker.sh job_tracker_cli.py
```

---

## 🎯 Next Steps

1. **Run your first scrape:**
   ```bash
   ./job_tracker.sh
   # Press '1' for full scrape
   ```

2. **Check results:**
   ```bash
   # Press '4' to see new jobs
   # Press '7' to export master log
   ```

3. **Open master log:**
   ```bash
   open MASTER_JOB_LOG.csv
   ```

4. **Set up daily routine:**
   - Morning: Check new jobs (Option 4)
   - Weekly: Full scrape (Option 1)
   - Monthly: Review all-time stats (Option 5)

---

## ✨ Features Summary

✅ **Interactive Menu** - Easy navigation with numbered options  
✅ **Full Scraping** - All 327 companies with one command  
✅ **Single Company** - Quick updates for specific companies  
✅ **Real-time Stats** - Today's activity and all-time metrics  
✅ **New Jobs View** - See what's new in last 24 hours  
✅ **Master CSV Log** - Comprehensive job database in CSV format  
✅ **Auto-Update** - Master log updated after every scrape  
✅ **Search & Filter** - Find jobs by keyword or company  
✅ **Export History** - Timestamped snapshots for tracking  
✅ **Clean UI** - Color-coded, emoji-enhanced, easy to read  

Enjoy tracking your internship opportunities! 🚀
