# 🚀 On-Demand Job Scraper

**No always-running Docker! Run only when you need it.**

---

## ⚡ Quick Start (3 Commands)

### **1. Scrape All Companies (10-15 minutes)**
```bash
./scrape.sh
```

### **2. Scrape One Company (Fast - 5 seconds)**
```bash
./scrape.sh "Google"
```

### **3. View Results**
```bash
./show_jobs.sh
```

**That's it!** Docker stops automatically when done.

---

## 📋 Common Commands

### **Scrape Specific Companies:**
```bash
./scrape.sh "Microsoft"
./scrape.sh "Meta"
./scrape.sh "Amazon"
./scrape.sh "NVIDIA"
./scrape.sh "Databricks"
```

### **View Jobs by Company:**
```bash
./show_jobs.sh "Google"
./show_jobs.sh "Citadel"
```

### **View All Jobs:**
```bash
./show_jobs.sh
```

### **Stop Everything:**
```bash
docker-compose down
```

---

## 🎯 Typical Workflow

### **Morning: Check New Jobs**
```bash
# Scrape all companies
./scrape.sh

# When done, view results
./show_jobs.sh

# Stop Docker
docker-compose down
```

**Done! Your laptop is free.**

---

### **Targeting Specific Companies**
```bash
# Just check FAANG companies
./scrape.sh "Google"
./scrape.sh "Meta"
./scrape.sh "Amazon"
./scrape.sh "Apple"
./scrape.sh "Netflix"

# View what you found
./show_jobs.sh

# Stop
docker-compose down
```

---

## 📊 What the Scraper Does

1. ✅ Starts minimal Docker (just database)
2. ✅ Runs scraper
3. ✅ Shows summary of results
4. ✅ Asks if you want to stop Docker
5. ✅ Shuts down (saves battery)

---

## 💾 Data Persistence

**Your data is saved between runs!**

- Database stored in Docker volume
- Even after stopping Docker, data remains
- Next time you scrape, it:
  - Updates existing jobs
  - Adds new jobs
  - Marks removed jobs as inactive

---

## ⏱️ How Long Does It Take?

| Command | Time |
|---------|------|
| `./scrape.sh` | **10-15 min** (all 108 companies) |
| `./scrape.sh "Google"` | **5-10 sec** (one company) |
| `./show_jobs.sh` | **Instant** |
| Startup/Shutdown | **3-5 sec** |

---

## 🔋 Battery Friendly

**Docker runs ONLY while scraping:**

```
Before scrape:   Docker OFF (0% battery)
During scrape:   Docker ON  (~15 min)
After scrape:    Docker OFF (0% battery)
```

**Much better than 24/7 running!**

---

## 📈 Examples

### **Example 1: Quick Daily Check**
```bash
# Morning routine (15 minutes total)
./scrape.sh

# Output shows:
# ✅ 108 companies processed
# ✅ 5 new jobs found
# ✅ 72 jobs updated

# View results
./show_jobs.sh

# Stop
docker-compose down
```

---

### **Example 2: Target High-Priority Companies**
```bash
# Check quant firms (2 minutes)
./scrape.sh "Citadel"
./scrape.sh "Two Sigma"
./scrape.sh "Jane Street"
./scrape.sh "HRT"
./scrape.sh "D.E. Shaw"

# View all results
./show_jobs.sh

# Stop
docker-compose down
```

---

### **Example 3: Weekly Deep Scrape**
```bash
# Sunday evening: Full scrape
./scrape.sh

# Review all companies with openings
./show_jobs.sh

# Check specific companies
./show_jobs.sh "NVIDIA"
./show_jobs.sh "Databricks"

# Stop when done
docker-compose down
```

---

## 🛠️ Advanced Usage

### **Export Results to CSV**
```bash
# Start database
docker-compose up -d db

# Export to CSV
docker-compose exec -T db psql -U jobtracker -d job_tracker -c "
COPY (
    SELECT company, title, location, url, created_at
    FROM jobs 
    WHERE is_active = true
    ORDER BY company, title
) TO STDOUT WITH CSV HEADER;" > jobs.csv

# View in Excel or Google Sheets
open jobs.csv

# Stop
docker-compose down
```

---

### **Count Jobs by Category**
```bash
# Start database if needed
docker-compose up -d db

# Check by category
docker-compose exec -T db psql -U jobtracker -d job_tracker -c "
SELECT 
    category,
    COUNT(*) as jobs
FROM jobs 
WHERE is_active = true
GROUP BY category
ORDER BY jobs DESC;
"
```

---

### **Find New Jobs from Last Run**
```bash
docker-compose up -d db

docker-compose exec -T db psql -U jobtracker -d job_tracker -c "
SELECT 
    company,
    title,
    location,
    created_at
FROM jobs 
WHERE created_at > NOW() - INTERVAL '24 hours'
  AND is_active = true
ORDER BY created_at DESC;
"
```

---

## 🎨 Customize Your Scraper

### **Change Companies to Scrape**

Edit `config/watchlist.yaml`:
```yaml
targets:
  - company: "Your Favorite Company"
    url: "https://careers.company.com"
    source: generic
```

Then scrape:
```bash
./scrape.sh "Your Favorite Company"
```

---

### **Filter by Location**

The scraper already filters for:
- ✅ United States only
- ✅ Internships only
- ✅ Summer 2026

No changes needed!

---

## 🚫 What You DON'T Need

❌ **No need for:**
- Cloud deployment
- 24/7 running Docker
- Celery scheduler
- Beat worker
- API server (unless you want the dashboard)

✅ **You only need:**
- Database (starts/stops on demand)
- Worker (runs only during scrape)

---

## 📱 Want the Dashboard?

If you want to view results in a browser:

```bash
# Start API + database
docker-compose up -d api db

# Open browser
open http://localhost:8000

# When done
docker-compose down
```

---

## 🐛 Troubleshooting

### **"Database connection failed"**
```bash
# Make sure database is running
docker-compose up -d db
sleep 3
./scrape.sh
```

### **"Permission denied"**
```bash
chmod +x scrape.sh
chmod +x show_jobs.sh
```

### **"Port already in use"**
```bash
# Stop everything first
docker-compose down
# Then try again
./scrape.sh
```

### **Scraper is slow or timing out**
```bash
# Scrape one company at a time
./scrape.sh "Google"
./scrape.sh "Microsoft"
# etc.
```

---

## ✅ Benefits of On-Demand Mode

| Feature | 24/7 Mode | On-Demand Mode |
|---------|-----------|----------------|
| **Battery usage** | High | Minimal |
| **CPU usage** | Constant | Only during scrape |
| **RAM usage** | ~2GB always | 0GB when stopped |
| **Control** | Automatic | You decide when |
| **Data** | Always current | Current when you scrape |
| **Flexibility** | Fixed schedule | Scrape anytime |

---

## 🎯 Perfect For:

✅ Running on your laptop  
✅ Checking jobs when you want  
✅ Saving battery on the go  
✅ Testing specific companies  
✅ Weekly/daily manual checks  
✅ Full control over timing  

---

## 📞 Quick Reference Card

```bash
# SCRAPING
./scrape.sh                    # All companies
./scrape.sh "CompanyName"      # One company

# VIEWING
./show_jobs.sh                 # All jobs
./show_jobs.sh "CompanyName"   # Jobs from one company

# CLEANUP
docker-compose down            # Stop everything

# DASHBOARD (optional)
docker-compose up -d api db    # Start web interface
open http://localhost:8000     # View in browser
```

---

**You now have a lightweight, on-demand job scraper!** 🚀

**No cloud needed. No always-running Docker. Just scrape when you want.** 🎉
