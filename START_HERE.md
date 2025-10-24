# 🚀 START HERE - Yash's Setup Guide

Step-by-step guide to get your job tracker running with email notifications.

## ❓ Your Questions Answered

### Do I need to download PostgreSQL and Redis?
**NO!** Docker will handle everything. You only need to install Docker Desktop.

### What about Slack?
**Not needed!** You'll get email notifications instead. Slack is optional and you don't need a paid subscription.

## 📋 What to Install

### 1. Install Docker Desktop (One-time setup)

**Download & Install:**
1. Go to: https://www.docker.com/products/docker-desktop
2. Download "Docker Desktop for Mac"
3. Open the downloaded file and drag Docker to Applications
4. Launch Docker from Applications folder
5. Wait for Docker to start (you'll see a whale icon in your menu bar)

**Verify it works:**
```bash
docker --version
# Should show: Docker version 24.x.x or similar
```

That's the ONLY thing you need to install! 🎉

## ⚙️ Configuration Steps

### Step 1: Create .env file

```bash
cd /Users/yashlad/Development/linkedin_job_scrapper

# Copy the example
cp .env.example .env
```

### Step 2: Get Gmail App Password (IMPORTANT!)

⚠️ **You CANNOT use "Y@$hL@d276" directly with Gmail!** You need a special app password.

**How to get it:**
1. Go to: https://myaccount.google.com/security
2. Under "Signing in to Google", enable **2-Step Verification** (if not already on)
3. Go back to: https://myaccount.google.com/apppasswords
4. For "Select app" → choose **Mail**
5. For "Select device" → choose **Mac**
6. Click **Generate**
7. You'll see a 16-character password like: `abcd efgh ijkl mnop`
8. **COPY THIS PASSWORD** (you'll use it in the next step)

### Step 3: Edit .env file

Open the `.env` file and update these lines:

```bash
# Use TextEdit or any editor
open -a TextEdit .env
```

**Change these lines:**
```env
# Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=yashlad727@gmail.com
SMTP_PASS=abcdefghijklmnop         👈 PUT YOUR 16-CHAR APP PASSWORD HERE (no spaces!)
SMTP_FROM=yashlad727@gmail.com
SMTP_TO=yashlad727@gmail.com

# Keep Slack empty (not using it)
SLACK_WEBHOOK_URL=

# Keep these as-is (Docker uses them automatically)
DATABASE_URL=postgresql+psycopg://jobtracker:changeme123@db:5432/job_tracker
REDIS_URL=redis://redis:6379/0
```

**Save the file!**

## 🚀 Start the Job Tracker

### Step 1: Make sure Docker Desktop is running
Look for the whale icon in your Mac menu bar (top right)

### Step 2: Start everything

```bash
cd /Users/yashlad/Development/linkedin_job_scrapper

# Start all services (first time will take 5-10 minutes)
docker-compose up -d
```

This will:
- ✅ Download PostgreSQL and Redis (automatic!)
- ✅ Build your job tracker
- ✅ Set up the database
- ✅ Start the scheduler (checks for jobs every hour)

### Step 3: Watch it work

```bash
# See what's happening
docker-compose logs -f worker

# You should see:
# - "Processing Citadel"
# - "Found X jobs"
# - "Sent email notification"
```

Press `Ctrl+C` to stop viewing logs (services keep running in background)

## 📧 Test Email Notification

Want to test right away? Run this:

```bash
# Manual test run for Citadel
docker-compose run --rm worker python -m src.ingest.runner --company Citadel

# Check your email (yashlad727@gmail.com)
# You should receive emails about any Summer 2026 internships found!
```

## 📊 See Jobs in Terminal (Alternative)

If you want to see results in terminal instead of email:

```bash
# Dry run - shows results but doesn't send email
docker-compose run --rm worker python -m src.ingest.runner --dry-run --company Citadel
```

## 🎯 What Happens Now?

1. **Every hour**, the tracker automatically:
   - Checks all companies in `config/watchlist.yaml`
   - Finds Summer 2026 internships
   - Filters for ML/AI, Cybersecurity, Data roles
   - **Sends you an email** for new jobs

2. **You'll get emails** like:
   ```
   Subject: 🆕 NEW [ml_ai] Machine Learning Intern - Summer 2026 — Citadel (New York)
   
   Position: Machine Learning Intern - Summer 2026
   Company: Citadel
   Location: New York, NY
   URL: https://...
   Tags: internship, summer-2026, ml_ai
   ```

## 🛠️ Useful Commands

```bash
# See if services are running
docker-compose ps

# View logs
docker-compose logs -f worker
docker-compose logs -f beat

# Stop everything
docker-compose down

# Restart after changing .env
docker-compose restart worker beat

# Fresh start (if something goes wrong)
docker-compose down -v
docker-compose up -d --build
```

## 🐛 Troubleshooting

### Not receiving emails?

1. **Check you used the APP PASSWORD** (not Y@$hL@d276)
2. **Check spam folder** in Gmail
3. **Check logs:** `docker-compose logs worker` - look for email errors
4. **Verify .env:** Make sure SMTP_PASS has no spaces

### Docker not starting?

1. Make sure Docker Desktop is running (whale icon in menu bar)
2. Try: `docker ps` - should not give errors

### No jobs found?

This is normal! It means:
- No new Summer 2026 internships posted yet
- Or jobs were already in database

**To test email is working:**
```bash
# Delete database and run again
docker-compose down -v
docker-compose up -d
docker-compose run --rm worker python -m src.ingest.runner --company Citadel
```

## ✅ Success Checklist

- [ ] Docker Desktop installed and running
- [ ] Got Gmail App Password (16 characters)
- [ ] Created `.env` file with your app password
- [ ] Ran `docker-compose up -d`
- [ ] Ran `docker-compose ps` - all services show "Up"
- [ ] Tested with `--company Citadel`
- [ ] Received test email at yashlad727@gmail.com

## 🎓 What's Being Tracked?

**Default companies:**
- Citadel, Two Sigma, Jane Street, HRT, D.E. Shaw
- Microsoft, Google

**Categories:**
- 🤖 Machine Learning / AI
- 🔒 Cybersecurity
- 📊 Data Engineering
- 🔬 Data Science

**Add more companies:** Edit `config/watchlist.yaml`

## 📞 Quick Reference

```bash
# Start tracker
docker-compose up -d

# View what's happening
docker-compose logs -f worker

# Test one company
docker-compose run --rm worker python -m src.ingest.runner --company "Citadel"

# See results in terminal (no email)
docker-compose run --rm worker python -m src.ingest.runner --dry-run

# Stop tracker
docker-compose down
```

## 🎉 You're All Set!

The tracker will now:
1. ✅ Run automatically every hour
2. ✅ Find Summer 2026 internships
3. ✅ Email you at yashlad727@gmail.com
4. ✅ Track changes over time

No need to install PostgreSQL, Redis, or anything else - Docker handles it all!

---

**Need help?** Check the logs first: `docker-compose logs -f worker`
