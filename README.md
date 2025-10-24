# Job Tracker - Summer 2026 Internships

Automated tracker for ML/AI, Cybersecurity, Data Engineering, and Data Science internship openings for Summer 2026.

## Features

- 🎯 **Targeted Tracking**: Monitors specific companies and ATS platforms
- 🔍 **Smart Filtering**: ML/AI, Cybersecurity, Data Engineering categories
- 🔔 **Real-time Alerts**: Slack, Email, and Pushover notifications
- 🔄 **Change Detection**: Tracks job updates and modifications
- 🚫 **Deduplication**: Hash-based identity and change tracking
- 📊 **PostgreSQL Storage**: Versioned job data with full history

## Architecture

```
┌─────────────┐
│  Scheduler  │ (Celery Beat / APScheduler)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│  Scraper Registry               │
│  ├─ Greenhouse                  │
│  ├─ Lever                       │
│  ├─ Ashby                       │
│  ├─ SmartRecruiters             │
│  └─ Generic HTML                │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│ Normalizer  │──────▶│   Filters    │
└─────────────┘      └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Deduper     │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐      ┌──────────────┐
                     │  PostgreSQL  │──────▶│  Notifiers   │
                     └──────────────┘      └──────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database and notification settings
```

### 3. Setup Database

```bash
# Run migrations
poetry run alembic upgrade head
```

### 4. Configure Watchlist

Edit `config/watchlist.yaml` to add/remove companies:

```yaml
targets:
  - company: "Your Company"
    ats_type: "greenhouse"  # or lever, ashby, etc.
    roles_include: ["intern", "summer 2026"]
    locations: ["New York", "Remote"]
    categories: ["ml_ai", "data_science"]
```

### 5. Run the Tracker

**One-time run:**
```bash
poetry run python -m src.ingest.runner
```

**Automated with Docker:**
```bash
docker-compose up -d
```

## Project Structure

```
job-tracker/
├── config/
│   ├── watchlist.yaml       # Companies to track
│   └── filters.yaml         # Classification rules
├── src/
│   ├── app/                 # FastAPI backend
│   ├── core/                # Database models
│   ├── ingest/              # ATS scrapers
│   │   ├── ats/             # Per-ATS implementations
│   │   ├── base.py          # Base scraper class
│   │   └── registry.py      # Scraper registry
│   ├── scheduler/           # Job scheduling
│   └── utils/               # Utilities
├── tests/                   # Tests
├── alembic/                 # Database migrations
├── docker-compose.yml       # Docker setup
└── pyproject.toml           # Dependencies
```

## Supported ATS Platforms

- ✅ Greenhouse
- ✅ Lever
- ✅ Ashby
- ✅ SmartRecruiters
- ✅ Workday
- ✅ Generic HTML (with Playwright)

## Categories

The tracker classifies jobs into:
- **ml_ai**: Machine Learning, AI, Deep Learning
- **cybersecurity**: Security, Threat Detection, Incident Response
- **data_engineering**: ETL, Data Pipelines, Big Data
- **data_science**: Analytics, Research Scientists
- **ml_platform**: MLOps, ML Infrastructure
- **platform_security**: Cloud Security, DevSecOps

## Notifications

Configure in `.env`:

**Slack:**
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
```

**Email:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

## Adding New Companies

1. Identify the ATS type (check network tab on their careers page)
2. Add to `config/watchlist.yaml`
3. Run with `--dry-run` to test:
   ```bash
   poetry run python -m src.ingest.runner --dry-run --company "Company Name"
   ```

## Development

**Run tests:**
```bash
poetry run pytest
```

**Format code:**
```bash
poetry run black src/
poetry run ruff check src/
```

**Type checking:**
```bash
poetry run mypy src/
```

## Compliance

- ⚠️ **No LinkedIn scraping** - violates ToS
- ✅ Uses official ATS JSON endpoints
- ✅ Respects `robots.txt`
- ✅ Rate limiting (1-3 RPS per domain)
- ✅ Exponential backoff on errors

## License

MIT

## Author

Yash Lad - 2025
