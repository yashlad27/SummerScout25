# 🚀 How to Run the Job Tracker

You have **3 ways** to run the tracker. All check **107 companies** every **30 minutes**.

---

## ✅ **Option 1: Use Docker (RECOMMENDED)**

**Easiest way - runs automatically in background**

```bash
# Start everything
docker-compose up -d

# Check logs
docker-compose logs -f worker beat

# Stop
docker-compose down
```

**What happens:**
- ✅ Runs every 30 minutes automatically
- ✅ Emails you at yashlad727@gmail.com
- ✅ Keeps running even if you close terminal
- ✅ Tracks all 107 companies

---

## ✅ **Option 2: Standalone Continuous Script**

**Run in your terminal - see live output**

```bash
# With Docker
./start_tracker.sh

# OR without Docker (need Python setup)
python3 run_tracker_continuous.py
```

**What happens:**
- ✅ Runs every 30 minutes
- ✅ Shows live progress in terminal
- ✅ Keeps running until you press Ctrl+C
- ✅ Logs to `job_tracker.log` file

**Stop:** Press `Ctrl+C`

---

## ✅ **Option 3: One-Time Manual Run**

**Test or run once**

```bash
# Test mode (no emails, no save)
docker-compose run --rm worker python -m src.ingest.runner --dry-run

# Real run (saves to DB, sends emails)
docker-compose run --rm worker python -m src.ingest.runner

# Test one company
docker-compose run --rm worker python -m src.ingest.runner --company "Citadel"
```

---

## 📊 **What Gets Tracked**

### **107 Companies Including:**
- **FAANG+**: Amazon, Meta, Apple, Google, Microsoft, NVIDIA
- **Trading**: Citadel, Two Sigma, Jane Street, HRT, DRW, IMC, Jump Trading, Optiver
- **Fintech**: Stripe, PayPal, Robinhood, Coinbase, Brex, Plaid
- **Cybersecurity**: CrowdStrike, Palo Alto, Okta, Zscaler, Wiz, Snyk
- **Data**: Databricks, Snowflake, Confluent, MongoDB, Palantir
- **And 80+ more!**

### **Filters:**
- ✅ **Summer 2026 internships only**
- ✅ **Categories**: ML/AI, Cybersecurity, Data Engineering, Data Science
- ✅ **Locations**: NYC, SF, Seattle, Chicago, Boston, Austin, Remote, etc.

---

## 📧 **Notifications**

**Email:** yashlad727@gmail.com

**You'll get emails for:**
- 🆕 New job postings
- 🔄 Updated job descriptions
- 🎯 Jobs matching your categories

**Example email:**
```
Subject: 🆕 NEW [ml_ai] Machine Learning Intern - Summer 2026 — Citadel

Position: Machine Learning Intern - Summer 2026
Company: Citadel
Location: New York, NY
Categories: ml_ai, data_science
URL: https://...
```

---

## 🔧 **Useful Commands**

```bash
# See what's running
docker-compose ps

# View logs
docker-compose logs -f worker
docker-compose logs -f beat

# Restart after config changes
docker-compose restart worker beat

# Rebuild after code changes
docker-compose up -d --build

# Check database
docker exec -it job_tracker_db psql -U jobtracker -d job_tracker
```

---

## ⏱️ **Schedule**

**Default:** Every **30 minutes**

**To change:**
1. Edit `src/scheduler/beat_schedule.py`
2. Change `crontab(minute="*/30")` to:
   - Every 15 min: `crontab(minute="*/15")`
   - Every hour: `crontab(minute=0)`
   - Every 2 hours: `crontab(minute=0, hour="*/2")`
3. Rebuild: `docker-compose up -d --build`

---

## 📝 **Logs**

**View logs:**
```bash
# Docker logs
docker-compose logs -f worker

# Standalone script logs
tail -f job_tracker.log
```

**Log location:**
- Docker: `docker-compose logs`
- Standalone: `job_tracker.log`

---

## ✅ **Recommended: Option 1 (Docker)**

**Why:**
- Runs in background automatically
- Restarts if crashes
- No need to keep terminal open
- Easy to start/stop

**Just run:**
```bash
docker-compose up -d
```

**That's it!** You'll get emails every time new Summer 2026 internships are posted! 🎉
