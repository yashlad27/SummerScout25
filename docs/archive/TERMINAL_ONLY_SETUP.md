# Terminal-Only Setup (No Docker, No Email)

If you just want to see results in the terminal without Docker or email notifications.

## 🚀 Quick Setup

### 1. Install Python Dependencies

```bash
cd /Users/yashlad/Development/linkedin_job_scrapper

# Install Poetry (dependency manager)
curl -sSL https://install.python-poetry.org | python3 -

# Or use pip
pip3 install poetry

# Install dependencies
poetry install
```

### 2. Run Without Email/Database

```bash
# Dry run - shows results in terminal, no DB/email needed
poetry run python -m src.ingest.runner --dry-run

# Test one company
poetry run python -m src.ingest.runner --dry-run --company Citadel

# Test multiple companies
poetry run python -m src.ingest.runner --dry-run
```

## 📊 What You'll See

```
INFO - Processing Citadel (greenhouse)
INFO - Fetching Greenhouse jobs for Citadel
INFO - Found 45 jobs for Citadel
INFO - [DRY RUN] Would process: Citadel - Machine Learning Intern - Summer 2026 [ml_ai]
INFO - [DRY RUN] Would process: Citadel - Quantitative Research Intern [data_science]

============================================================
JOB TRACKER RUN SUMMARY
============================================================
Companies processed: 1
Jobs fetched:        45
Jobs filtered out:   38
Jobs new:            7
Jobs updated:        0
Notifications sent:  0
Errors:              0
============================================================
```

## 🎯 Using requirements.txt Instead of Poetry

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for some scrapers)
playwright install chromium

# Run
python -m src.ingest.runner --dry-run --company Citadel
```

## 📝 Save Results to File

```bash
# Save output to file
poetry run python -m src.ingest.runner --dry-run > jobs_$(date +%Y%m%d).txt

# Or with tee to see and save
poetry run python -m src.ingest.runner --dry-run | tee jobs_$(date +%Y%m%d).txt
```

## 🔄 Run Periodically (macOS Cron)

To run automatically every hour:

```bash
# Edit crontab
crontab -e

# Add this line (replace path):
0 * * * * cd /Users/yashlad/Development/linkedin_job_scrapper && /usr/local/bin/poetry run python -m src.ingest.runner --dry-run >> ~/job_tracker_output.log 2>&1
```

## ⚡ Pros and Cons

### ✅ Pros (Terminal Only)
- No Docker installation needed
- No database setup
- No email configuration
- Lightweight and fast
- Easy to debug

### ❌ Cons (Terminal Only)
- No persistence (can't track changes over time)
- No deduplication across runs
- No automatic notifications
- Must manually save output

## 🚀 Upgrade to Full Version Later

When you're ready for full features (DB, email, auto-scheduling):

1. Install Docker Desktop
2. Follow **DOCKER_SETUP.md**
3. Your job data will persist
4. Get automatic email alerts
5. Track job changes over time

## 💡 Hybrid Approach

You can also:
1. Use Docker for database only
2. Run manually with email
3. Use terminal for testing, email for monitoring

Example:
```bash
# Setup with Docker (gets DB)
docker-compose up -d db redis

# Wait for DB to start
sleep 5

# Run migrations
poetry run alembic upgrade head

# Create .env with email settings
cp .env.example .env
# Edit .env with your email

# Run with email notifications
poetry run python -m src.ingest.runner
```

This gives you email alerts without running the full Docker stack!
