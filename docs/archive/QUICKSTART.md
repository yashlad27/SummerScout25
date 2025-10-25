# Quick Start Guide - Job Tracker

Get your Summer 2026 internship tracker running in 5 minutes!

## 🚀 Fastest Way to Start (Docker)

```bash
# 1. Setup environment
cp .env.example .env

# 2. Add your Slack webhook (optional but recommended)
# Edit .env and add: SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# 3. Start everything
docker-compose up -d

# 4. Watch it work
docker-compose logs -f worker
```

That's it! The tracker will now:
- ✅ Run every hour automatically
- ✅ Scrape configured companies (Citadel, Two Sigma, Jane Street, etc.)
- ✅ Filter for Summer 2026 internships
- ✅ Classify by category (ML/AI, Security, Data)
- ✅ Send Slack/Email notifications for new jobs

## 🔍 Test Before Full Run

Want to test with one company first?

```bash
# Using Docker
docker-compose run --rm worker python -m src.ingest.runner --dry-run --company Citadel

# Or locally
poetry install
poetry run python -m src.ingest.runner --dry-run --company Citadel
```

## 📊 View Results

### Web UI (API)
Visit http://localhost:8000/docs

**Useful endpoints:**
- `/jobs` - List all jobs
- `/stats` - See statistics
- `/companies` - Companies with job counts

### Database
```bash
# Connect to database
docker exec -it job_tracker_db psql -U jobtracker -d job_tracker

# Query jobs
SELECT company, title, category, location FROM jobs WHERE is_active = true;
```

## ⚙️ Configuration

### Add More Companies

Edit `config/watchlist.yaml`:

```yaml
targets:
  - company: "Your Company"
    ats_type: "greenhouse"  # greenhouse, lever, or ashby
    careers_url: "https://careers.company.com"
    roles_include: ["intern", "summer 2026"]
    locations: ["New York", "Remote"]
    categories: ["ml_ai", "data_science"]
```

### Customize Categories

Edit `config/filters.yaml` to add keywords for different job types.

## 🔔 Notifications

### Slack (Recommended)

1. Create webhook: https://api.slack.com/messaging/webhooks
2. Add to `.env`: `SLACK_WEBHOOK_URL=https://hooks.slack.com/...`
3. Restart: `docker-compose restart worker beat`

### Email

Add to `.env`:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

## 📈 What Gets Tracked

**Categories:**
- 🤖 ML/AI - Machine Learning, Deep Learning, NLP
- 🔒 Cybersecurity - Security, Threat Detection
- 📊 Data Engineering - ETL, Pipelines, Big Data
- 🔬 Data Science - Analytics, Research
- ⚙️ ML Platform - MLOps, Infrastructure
- 🛡️ Platform Security - Cloud Security, DevSecOps

**Companies (Default):**
- Citadel, Two Sigma, Jane Street, HRT, D.E. Shaw
- Microsoft, Google
- (Add your own in `config/watchlist.yaml`)

## 🛠️ Common Commands

```bash
# View logs
docker-compose logs -f worker

# Restart services
docker-compose restart

# Stop everything
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Run migrations
docker-compose run --rm worker alembic upgrade head
```

## 🐛 Troubleshooting

**No jobs found?**
- Check company slug is correct
- Verify ATS type (greenhouse/lever/ashby)
- Test with `--dry-run --company "CompanyName"`

**Rate limited?**
- Lower `HTTP_MAX_RPS` in `.env` (e.g., `HTTP_MAX_RPS=1`)

**No notifications?**
- Check webhook URL is correct
- View logs: `docker-compose logs worker`
- Jobs must match filters (internship + summer 2026)

## 📚 Full Documentation

- **SETUP.md** - Detailed setup instructions
- **README.md** - Project overview
- **job_tracker_reference.txt** - Architecture reference
- **job_tracker_overview_mechanics.txt** - Deep dive

## 🎯 Next Steps

1. ✅ Get it running with Docker
2. ✅ Add your Slack webhook
3. ✅ Test with one company
4. ✅ Add more companies to watchlist
5. ✅ Customize categories/filters
6. ✅ Set up email notifications
7. ✅ Monitor and refine

Happy job hunting! 🎉
