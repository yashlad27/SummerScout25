# ⏰ Automatic Scraping Schedule Configuration

## 📋 Current Schedule

Your job tracker is configured to run **automatically every 4 hours**:

- **00:00** (Midnight)
- **04:00** (4 AM)
- **08:00** (8 AM)
- **12:00** (Noon)
- **16:00** (4 PM)
- **20:00** (8 PM)

**All times are in UTC timezone.**

---

## 📁 Configuration Files

### 1. **`celeryconfig.py`** (Main Configuration)
Located in project root. Contains all Celery settings including the automatic schedule.

```python
beat_schedule = {
    'scrape-all-companies-every-4-hours': {
        'task': 'tasks.run_job_tracker',
        'schedule': crontab(minute=0, hour='*/4'),
        'options': {
            'expires': 14400,  # Expire after 4 hours
        },
    },
}
```

### 2. **`src/scheduler/beat_schedule.py`** (Legacy)
Backup schedule definition. The main config now loads from `celeryconfig.py`.

### 3. **`src/scheduler/tasks.py`** (Celery Tasks)
Defines the actual scraping tasks that get scheduled.

---

## 🔧 How to Change the Schedule

### Option 1: Edit `celeryconfig.py` (Recommended)

1. **Open** `celeryconfig.py`
2. **Modify** the `beat_schedule` dict
3. **Rebuild** Docker containers
4. **Restart** services

### Option 2: Pre-configured Examples

Uncomment any of these in `celeryconfig.py`:

#### Every 2 Hours
```python
beat_schedule['scrape-every-2-hours'] = {
    'task': 'tasks.run_job_tracker',
    'schedule': crontab(minute=0, hour='*/2'),
}
```

#### Every 6 Hours
```python
beat_schedule['scrape-every-6-hours'] = {
    'task': 'tasks.run_job_tracker',
    'schedule': crontab(minute=0, hour='*/6'),
}
```

#### Daily at 9 AM
```python
beat_schedule['scrape-daily-9am'] = {
    'task': 'tasks.run_job_tracker',
    'schedule': crontab(minute=0, hour=9),
}
```

#### Twice Daily (9 AM and 5 PM)
```python
beat_schedule['scrape-twice-daily'] = {
    'task': 'tasks.run_job_tracker',
    'schedule': crontab(minute=0, hour='9,17'),
}
```

#### Weekdays Only at 9 AM
```python
beat_schedule['scrape-weekdays'] = {
    'task': 'tasks.run_job_tracker',
    'schedule': crontab(minute=0, hour=9, day_of_week='1-5'),
}
```

---

## 🎯 Advanced: Company-Specific Schedules

Scrape specific companies more frequently:

### Google Every Hour
```python
beat_schedule['scrape-google-hourly'] = {
    'task': 'tasks.run_job_tracker_for_company',
    'schedule': crontab(minute=0),  # Every hour
    'args': ('Google',),
}
```

### FAANG Companies Every 2 Hours
```python
for company in ['Google', 'Meta', 'Amazon', 'Apple', 'Netflix']:
    beat_schedule[f'scrape-{company.lower()}-every-2hrs'] = {
        'task': 'tasks.run_job_tracker_for_company',
        'schedule': crontab(minute=0, hour='*/2'),
        'args': (company,),
    }
```

---

## 📊 Verify Schedule

### Check Current Schedule
```bash
python verify_schedule.py
```

**Output:**
```
🔍 CELERY BEAT SCHEDULE VERIFICATION
======================================================================

✅ celeryconfig.py found and loaded

📊 Found 1 scheduled tasks:

📋 Task: scrape-all-companies-every-4-hours
   └─ Runs: tasks.run_job_tracker
   └─ Schedule: <crontab: 0 */4 * * * (m/h/d/dM/MY)>
   └─ Frequency: Every 4 hours
   └─ Run times: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC

⏰ NEXT SCHEDULED RUNS
======================================================================

Current time (UTC): 2025-10-24 23:50:00

📅 scrape-all-companies-every-4-hours:
   └─ Next run: 2025-10-25 00:00:00 UTC
   └─ Time until: 0h 10m
```

---

## 🔄 Apply Changes

After editing `celeryconfig.py`:

### 1. Rebuild Docker Images
```bash
docker-compose build worker beat
```

### 2. Restart Services
```bash
docker-compose restart worker beat
```

### 3. Verify Schedule Loaded
```bash
docker logs job_tracker_beat | grep "schedule"
```

---

## 📺 Monitor Scheduler

### Watch Scheduler Logs
```bash
docker logs -f job_tracker_beat
```

**You'll see:**
```
[2025-10-24 23:50:00] Scheduler: Sending due task tasks.run_job_tracker
```

### Watch Worker Logs
```bash
docker logs -f job_tracker_worker
```

**You'll see:**
```
Starting scheduled job tracker run
Processing Google (generic)
Fetching jobs from https://careers.google.com/
```

---

## 🐛 Troubleshooting

### Schedule Not Running?

**1. Check if Beat scheduler is running:**
```bash
docker ps | grep beat
```

**2. Check Beat logs for errors:**
```bash
docker logs job_tracker_beat
```

**3. Verify schedule is loaded:**
```bash
docker logs job_tracker_beat | grep "beat_schedule"
```

**4. Restart services:**
```bash
docker-compose restart beat worker
```

---

## 📝 Crontab Syntax Reference

```
crontab(minute=0, hour='*/4')
        ↑           ↑
        |           └─ Hour (*/4 = every 4 hours)
        └──────────── Minute (0 = on the hour)
```

### Common Patterns

| Pattern | Description |
|---------|-------------|
| `minute=0, hour='*/4'` | Every 4 hours (00:00, 04:00, 08:00, etc.) |
| `minute=0, hour='*/2'` | Every 2 hours |
| `minute='*/30'` | Every 30 minutes |
| `minute=0, hour=9` | Daily at 9:00 |
| `minute=0, hour='9,17'` | Daily at 9:00 and 17:00 |
| `minute=0, hour=9, day_of_week='1-5'` | Weekdays at 9:00 |
| `minute=0, hour=0, day_of_month=1` | First day of month at midnight |

---

## 🎯 Best Practices

### 1. **Don't Scrape Too Frequently**
- Respect website rate limits
- Avoid getting blocked
- Every 4 hours is a good balance

### 2. **Use Expiration Times**
- Set `expires` to prevent task pileup
- Should be less than schedule interval

### 3. **Monitor Performance**
- Check scraper logs regularly
- Watch for timeouts or errors
- Adjust schedule if needed

### 4. **Test Changes**
- Always test manually first:
  ```bash
  docker-compose run --rm worker python -m src.ingest.runner
  ```
- Then enable automatic schedule

---

## ✅ Quick Commands

```bash
# Verify schedule configuration
python verify_schedule.py

# Manually trigger scrape (testing)
docker-compose run --rm worker python -m src.ingest.runner

# Check when next scrape runs
curl http://localhost:8000/scraper-status

# Watch scheduler
docker logs -f job_tracker_beat

# Watch scraper
docker logs -f job_tracker_worker

# Restart after config changes
docker-compose build worker beat
docker-compose restart worker beat
```

---

## 📍 Your Current Setup

**Schedule File:** `celeryconfig.py`  
**Frequency:** Every 4 hours  
**Times:** 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC  
**Companies:** All 108 companies in watchlist  
**Notifications:** Email to yashlad727@gmail.com  

---

**Your automatic schedule is configured and ready!** 🚀

Check the dashboard at http://localhost:8000 to see the countdown timer.
