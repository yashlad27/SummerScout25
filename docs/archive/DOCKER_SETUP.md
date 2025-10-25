# Docker Setup Guide for macOS

Complete guide to install Docker and run the Job Tracker.

## ✅ Do You Need PostgreSQL and Redis?

**NO!** With Docker, you don't need to install PostgreSQL or Redis separately. Docker will handle everything automatically.

## 📦 What You Need to Install

### 1. Install Docker Desktop (macOS)

**Option A: Using Homebrew (Recommended)**

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker Desktop
brew install --cask docker
```

**Option B: Direct Download**

1. Visit: https://www.docker.com/products/docker-desktop
2. Download Docker Desktop for Mac (Apple Silicon or Intel)
3. Open the `.dmg` file and drag Docker to Applications
4. Launch Docker from Applications

### 2. Verify Docker Installation

```bash
# Check Docker is running
docker --version
docker-compose --version

# You should see versions like:
# Docker version 24.x.x
# Docker Compose version v2.x.x
```

## 🚀 Quick Start (Email Notifications Only)

### Step 1: Create Your Configuration File

```bash
cd /Users/yashlad/Development/linkedin_job_scrapper

# Copy the example file
cp .env.example .env
```

### Step 2: Configure Email (IMPORTANT!)

**You CANNOT use your regular Gmail password!** You need an App Password.

#### Get Gmail App Password:

1. Go to: https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Go to: https://myaccount.google.com/apppasswords
4. Select "Mail" and "Mac" 
5. Click "Generate"
6. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)

#### Edit `.env` File:

Open `.env` and update these lines:

```env
# Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=yashlad727@gmail.com
SMTP_PASS=abcdefghijklmnop     # <-- PUT YOUR 16-CHAR APP PASSWORD HERE (no spaces)
SMTP_FROM=yashlad727@gmail.com
SMTP_TO=yashlad727@gmail.com

# Leave Slack empty (we're not using it)
SLACK_WEBHOOK_URL=

# Database (Docker handles this automatically)
DATABASE_URL=postgresql+psycopg://jobtracker:changeme123@db:5432/job_tracker
REDIS_URL=redis://redis:6379/0
```

### Step 3: Start Docker Containers

```bash
# Make sure Docker Desktop is running (check menu bar)

# Start all services
docker-compose up -d

# This will:
# ✅ Download PostgreSQL and Redis images
# ✅ Build your application
# ✅ Run database migrations
# ✅ Start the job tracker
# ✅ Start the scheduler (runs every hour)
```

### Step 4: Watch It Work

```bash
# View logs
docker-compose logs -f worker

# You should see:
# - Jobs being fetched
# - Filtering happening
# - Email notifications being sent
```

## 📧 Test Email Notifications

### Quick Test Run

```bash
# Run once manually to test
docker-compose run --rm worker python -m src.ingest.runner --company Citadel

# If successful, you'll get an email with any new jobs found!
```

### Check Logs

```bash
# Check worker logs
docker-compose logs worker

# Check all services
docker-compose logs
```

## 🖥️ Terminal Notifications (Alternative)

If you want to see results in the terminal instead of email:

```bash
# Run in dry-run mode (shows results but doesn't send emails)
docker-compose run --rm worker python -m src.ingest.runner --dry-run

# Or run locally without Docker
poetry install
poetry run python -m src.ingest.runner --dry-run
```

## 🛠️ Common Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f worker
docker-compose logs -f beat

# Restart after config changes
docker-compose restart worker beat

# Rebuild after code changes
docker-compose up -d --build

# Remove everything (fresh start)
docker-compose down -v
docker-compose up -d --build
```

## 📊 Check What's Running

```bash
# See running containers
docker-compose ps

# You should see:
# - job_tracker_db (PostgreSQL)
# - job_tracker_redis
# - job_tracker_worker (processes jobs)
# - job_tracker_beat (scheduler)
# - job_tracker_api (optional web UI)
```

## 🌐 Access Web UI (Optional)

If you want to view jobs in a browser:

```bash
# Visit: http://localhost:8000/docs

# Useful endpoints:
# - http://localhost:8000/jobs - List all jobs
# - http://localhost:8000/stats - Statistics
# - http://localhost:8000/companies - Companies
```

## 🐛 Troubleshooting

### Docker Desktop Not Running

Error: `Cannot connect to the Docker daemon`

**Solution:** Open Docker Desktop from Applications

### No Emails Received

1. **Check Gmail App Password**: Make sure you used the app password, not regular password
2. **Check Logs**: `docker-compose logs worker` - look for email errors
3. **Check Spam Folder**: Gmail might filter these emails
4. **Verify SMTP Settings**: Make sure no typos in `.env`

### Port Already in Use

Error: `port is already allocated`

**Solution:**
```bash
# Stop conflicting service or change port in docker-compose.yml
# For PostgreSQL (port 5432):
lsof -ti:5432 | xargs kill -9

# Then restart Docker
docker-compose up -d
```

### Jobs Not Found

**Possible reasons:**
1. No Summer 2026 internships posted yet
2. Company uses different ATS than configured
3. Job titles don't match filters

**Test with dry-run:**
```bash
docker-compose run --rm worker python -m src.ingest.runner --dry-run --company Citadel
```

## 📝 What Gets Installed Automatically

When you run `docker-compose up -d`, Docker automatically:

1. ✅ Downloads PostgreSQL 16 image
2. ✅ Downloads Redis 7 image
3. ✅ Builds Python 3.11 environment
4. ✅ Installs all Python dependencies
5. ✅ Sets up the database
6. ✅ Runs migrations
7. ✅ Starts all services

**You don't need to install anything except Docker Desktop!**

## 🔄 Scheduler Settings

By default, the tracker runs **every hour**. To change:

Edit `src/scheduler/beat_schedule.py`:

```python
"run-job-tracker-hourly": {
    "task": "tasks.run_job_tracker",
    "schedule": crontab(minute=0),  # Every hour at :00
}

# For every 30 minutes:
# "schedule": crontab(minute="*/30"),

# For every 2 hours:
# "schedule": crontab(minute=0, hour="*/2"),
```

Then restart:
```bash
docker-compose restart beat
```

## ✅ Success Checklist

- [ ] Docker Desktop installed and running
- [ ] `.env` file created with Gmail App Password
- [ ] `docker-compose up -d` completed successfully
- [ ] `docker-compose ps` shows all services running
- [ ] Tested with `--dry-run --company Citadel`
- [ ] Received test email notification

## 🎯 Next Steps

1. **Let it run**: The scheduler will check for jobs every hour
2. **Check email**: You'll get notifications for new Summer 2026 internships
3. **Add companies**: Edit `config/watchlist.yaml` to track more companies
4. **Customize filters**: Edit `config/filters.yaml` for specific roles

## 📞 Need Help?

Check logs first:
```bash
docker-compose logs -f worker
```

Common log locations:
- Email errors: Look for "Failed to send email"
- Scraping errors: Look for "Failed to fetch"
- Database errors: Look for "database" or "SQL"
