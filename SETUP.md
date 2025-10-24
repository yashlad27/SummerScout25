# Job Tracker - Setup Guide

Complete setup instructions for the Summer 2026 Internship Job Tracker.

## Prerequisites

- Python 3.11+
- PostgreSQL 16+ (or use Docker)
- Redis (or use Docker)
- Poetry (recommended) or pip

## Option 1: Docker Setup (Recommended)

### 1. Clone and Configure

```bash
cd /path/to/linkedin_job_scrapper
cp .env.example .env
```

### 2. Edit `.env` File

Add your notification credentials:

```env
# Slack (optional but recommended)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=your-email@gmail.com
SMTP_TO=your-email@gmail.com
```

### 3. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis
- Database migrations
- Celery worker
- Celery beat (scheduler)
- API server (port 8000)

### 4. View Logs

```bash
docker-compose logs -f worker
docker-compose logs -f beat
```

### 5. Access API

Visit http://localhost:8000/docs for the interactive API documentation.

## Option 2: Local Setup

### 1. Install Dependencies

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
poetry run playwright install chromium
```

### 3. Setup PostgreSQL

Create a database:

```sql
CREATE DATABASE job_tracker;
CREATE USER jobtracker WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE job_tracker TO jobtracker;
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your database and notification settings:

```env
DATABASE_URL=postgresql+psycopg://jobtracker:your_password@localhost:5432/job_tracker
REDIS_URL=redis://localhost:6379/0
# ... add notification settings
```

### 5. Run Migrations

```bash
poetry run alembic upgrade head
```

### 6. Test the Setup

Run a dry-run for one company:

```bash
poetry run python -m src.ingest.runner --dry-run --company Citadel
```

### 7. Run the Tracker

**One-time execution:**
```bash
poetry run python -m src.ingest.runner
```

**With scheduler (APScheduler):**
```bash
poetry run python -m src.scheduler.apscheduler_runner
```

**With Celery:**
```bash
# Terminal 1: Start worker
poetry run celery -A src.scheduler.tasks worker --loglevel=info

# Terminal 2: Start beat
poetry run celery -A src.scheduler.tasks beat --loglevel=info
```

## Configuration

### Adding Companies

Edit `config/watchlist.yaml`:

```yaml
targets:
  - company: "YourCompany"
    ats_type: "greenhouse"  # or lever, ashby, etc.
    careers_url: "https://careers.yourcompany.com"
    roles_include: ["intern", "summer 2026"]
    locations: ["New York", "Remote"]
    categories: ["ml_ai", "data_science"]
```

### Customizing Filters

Edit `config/filters.yaml` to:
- Add new categories
- Modify keyword patterns
- Adjust location filters
- Change internship patterns

## Notification Setup

### Slack

1. Create a Slack app at https://api.slack.com/apps
2. Enable "Incoming Webhooks"
3. Create a webhook for your channel
4. Add webhook URL to `.env`

### Email (Gmail)

1. Enable 2-factor authentication
2. Generate an app password: https://myaccount.google.com/apppasswords
3. Add credentials to `.env`

## Testing

Run tests:

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=src tests/

# Specific test file
poetry run pytest tests/test_hashing.py -v
```

## Troubleshooting

### Database Connection Issues

Check PostgreSQL is running:
```bash
psql -U jobtracker -d job_tracker -h localhost
```

### Rate Limiting

If you encounter rate limits:
- Increase `HTTP_MAX_RPS` in `.env` (lower the value)
- Reduce scraping frequency in scheduler

### No Jobs Found

1. Check company slug in watchlist
2. Try `--dry-run --company "CompanyName"` to debug
3. Check ATS type is correct
4. Verify careers URL is accessible

## Monitoring

### View Statistics

Visit http://localhost:8000/stats (if API is running)

### Database Queries

```sql
-- View active jobs
SELECT company, title, category, posted_at 
FROM jobs 
WHERE is_active = true 
ORDER BY posted_at DESC;

-- Count by company
SELECT company, COUNT(*) 
FROM jobs 
WHERE is_active = true 
GROUP BY company;

-- Recent alerts
SELECT * FROM alerts 
ORDER BY sent_at DESC 
LIMIT 10;
```

## Updating

To update the tracker:

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

## Production Deployment

For production:

1. Change database password in `.env`
2. Set `ENVIRONMENT=production`
3. Configure Sentry for error tracking
4. Use proper secrets management
5. Set up backups for PostgreSQL
6. Monitor logs and metrics

## Need Help?

- Check logs: `docker-compose logs -f`
- Review `job_tracker_reference.txt`
- Review `job_tracker_overview_mechanics.txt`
