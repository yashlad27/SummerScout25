# 🔍 How to Monitor the Scraper

## 📺 Watch Scraper Live (Recommended)

### Option 1: Watch Worker Logs (Real-Time Updates)
```bash
docker logs -f job_tracker_worker
```

**What you'll see when scraping:**
```
Processing Google (generic)
Fetching jobs from https://careers.google.com/
Found 15 jobs for Google
New job: Google - Machine Learning Intern
New job: Google - Software Engineer Intern
Sent email notification
```

**Press `Ctrl+C` to stop watching**

---

### Option 2: Watch Scheduler Logs
```bash
docker logs -f job_tracker_beat
```

**What you'll see:**
```
Scheduler: Sending due task tasks.run_job_tracker
```

---

### Option 3: Watch Both at Once
```bash
# In one terminal:
docker logs -f job_tracker_worker

# In another terminal:
docker logs -f job_tracker_beat
```

---

## 🚀 Manually Trigger a Scrape Now

### Scrape All Companies (Takes ~5 minutes)
```bash
docker-compose run --rm worker python -m src.ingest.runner
```

### Scrape One Company (Quick Test)
```bash
docker-compose run --rm worker python -m src.ingest.runner --company "Google"
```

**You'll see live output like:**
```
Processing Google (generic)
Fetching jobs from https://careers.google.com/
Found 15 jobs for Google
Jobs new: 3
Jobs updated: 12
Notifications sent: 1
```

---

## 📊 Check Scraper Status

### See Current Status
```bash
curl http://localhost:8000/scraper-status
```

### Check Jobs in Database
```bash
docker exec job_tracker_worker python -c "from src.core.database import get_db_context; from src.core.models import Job; db = get_db_context().__enter__(); print(f'Total jobs: {db.query(Job).count()}')"
```

---

## ⏰ Automatic Scraping Schedule

**Default Schedule:** Every 4 hours
- 12:00 AM (midnight)
- 4:00 AM
- 8:00 AM
- 12:00 PM (noon)
- 4:00 PM
- 8:00 PM

**Set in:** `src/scheduler/beat_schedule.py`

---

## 🔔 Get Notified When Scraper Runs

### Check Email
New jobs are sent to: **yashlad727@gmail.com**

Email includes:
- ✅ List of all 108 companies scanned
- ✅ New jobs found
- ✅ Which companies had new openings

---

## 🐛 Troubleshooting

### Scraper Not Running?

**1. Check if worker is running:**
```bash
docker ps | grep worker
```

**2. Check for errors:**
```bash
docker logs job_tracker_worker --tail 100 | grep -i error
```

**3. Restart worker:**
```bash
docker-compose restart worker beat
```

**4. Manually trigger:**
```bash
docker-compose run --rm worker python -m src.ingest.runner --company "Google"
```

---

## 📈 Monitor Scraper Performance

### See Last 100 Log Lines
```bash
docker logs job_tracker_worker --tail 100
```

### Search for Specific Company
```bash
docker logs job_tracker_worker | grep "Processing Google"
```

### Count Jobs Found
```bash
docker logs job_tracker_worker | grep "jobs_new"
```

---

## 💡 Pro Tips

1. **Leave logs running in a terminal window** to see scraping happen in real-time
2. **Check dashboard** at http://localhost:8000 - countdown timer shows when next scrape runs
3. **Email is the easiest way** to know when new jobs are found
4. **Manual scrapes don't interfere** with automatic schedule

---

## 🎯 Quick Commands Summary

```bash
# Watch scraper live
docker logs -f job_tracker_worker

# Manually scrape all companies
docker-compose run --rm worker python -m src.ingest.runner

# Manually scrape one company
docker-compose run --rm worker python -m src.ingest.runner --company "Google"

# Check status
curl http://localhost:8000/scraper-status

# Restart scraper
docker-compose restart worker beat
```

---

**Your scraper is running! Check the dashboard or run a manual scrape to see it in action.** 🚀
