# 🚀 Quick Start Guide

## **One Command to Rule Them All:**

```bash
./start.sh
```

That's it! This single command will:
1. ✅ Check if Docker is running
2. ✅ Build images if needed
3. ✅ Create database tables
4. ✅ Start all services
5. ✅ Show you the status

---

## **Usage**

### **Start the Tracker:**
```bash
./start.sh
```

### **Stop the Tracker:**
```bash
docker-compose down
```

### **View Logs:**
```bash
# Worker logs (scraping activity)
docker-compose logs -f worker

# Scheduler logs
docker-compose logs -f beat
```

### **Export Jobs to Files:**
```bash
docker-compose run --rm worker python export_jobs.py
```
This creates:
- `jobs_export.csv` - Spreadsheet with all jobs
- `jobs_formatted.txt` - Easy-to-read text
- `jobs_by_category_*.txt` - Separate files per category

### **Run Scrape Immediately:**
```bash
docker-compose run --rm worker python -m src.ingest.runner
```

---

## **What It Does**

- 🔍 Scrapes 108 companies every 4 hours
- 📧 Sends ONE consolidated email with all new jobs
- 🎯 Filters for Summer 2026 internships
- 🏷️ Categories: ML/AI, Cybersecurity, Data Science, Data Engineering
- 📬 Delivers to: yashlad727@gmail.com

---

## **Schedule**

Runs automatically at:
- 12:00 AM
- 4:00 AM  
- 8:00 AM
- 12:00 PM
- 4:00 PM
- 8:00 PM

---

## **First Time Setup**

If this is your first time running:

1. Make sure Docker Desktop is installed and running
2. Run: `./start.sh`
3. Wait for the first scheduled run (or trigger manually)
4. Check your email!

---

## **Troubleshooting**

**Docker not running:**
```bash
# Start Docker Desktop, then run:
./start.sh
```

**Need to rebuild:**
```bash
docker-compose build
./start.sh
```

**Clear everything and restart:**
```bash
docker-compose down -v
./start.sh
```

---

## **That's All!**

Just run `./start.sh` whenever you want the tracker running.

Stop it with `docker-compose down` when you're done.

Simple! 🎉
