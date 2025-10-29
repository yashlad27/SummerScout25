# 🎯 InternTracker

**On-demand command-line tool to track Summer 2026 tech internships across 108 top companies.**

No cloud required. No 24/7 running. Just scrape when you want, get results, done.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## ✨ Features

- 🚀 **On-Demand Scraping** - Run only when you need it
- 🖥️ **Interactive CLI** - Full-featured terminal app for managing jobs
- 🎯 **327 Companies** - FAANG, quant firms, unicorn startups, fintech
- 🇺🇸 **US Positions Only** - Automatically filtered
- 💼 **Internship Focus** - Summer 2026 Masters-eligible positions
- 📊 **Smart Filtering** - ML/AI, Cybersecurity, Data Engineering, Data Science
- 🔔 **Email Notifications** - Get alerts for new postings
- 💾 **Master CSV Log** - Comprehensive job database updated automatically
- 📈 **Statistics Dashboard** - Track daily/all-time metrics
- 🪶 **Lightweight** - Docker stops when done

## 🎬 Demo

### Interactive CLI (NEW!)
```bash
# Launch interactive terminal app
$ ./job_tracker.sh

================================================================================
🎯  JOB TRACKER - Interactive CLI
================================================================================

📋 MAIN MENU:
--------------------------------------------------------------------------------
  1. 🚀 Run Full Scrape (All 327 Companies)
  2. 🎯 Run Single Company Scrape
  3. 📊 View Today's Statistics
  4. 🆕 View New Jobs (Last 24 Hours)
  5. 📈 View All-Time Statistics
  6. 📁 View Recent Export Files
  7. 💾 Export Master Job Log (CSV)
  8. 🔍 Search Jobs by Keyword
  9. 🏢 View Jobs by Company
  0. ❌ Exit
--------------------------------------------------------------------------------
👉 Select an option (0-9):
```

### Command Line
```bash
# Scrape all 327 companies
$ ./scrape_batch.sh

# Scrape single company
$ ./scrape.sh "Databricks"

# View results
$ ./show_jobs.sh
```

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed
- 5GB disk space

### Setup (One-Time)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/InternTracker.git
cd InternTracker

# 2. Create environment file
cp .env.example .env

# 3. (Optional) Add your Gmail for notifications
nano .env  # Add SMTP settings

# 4. Build Docker images
docker-compose build
```

### Usage

#### 🖥️ **Interactive CLI (Recommended)**
```bash
# Launch full-featured terminal app
./job_tracker.sh

# Features:
# - Run scrapes (full or single company)
# - View today's statistics & new jobs
# - Search jobs by keyword
# - Export master CSV log (auto-updated)
# - Track all-time metrics
```
📖 **[Full CLI Guide](CLI_GUIDE.md)**

#### ⌨️ **Command Line**
```bash
# Scrape all companies (30-60 minutes)
./scrape_batch.sh

# Scrape one company (10-30 seconds)
./scrape.sh "Databricks"

# View results in terminal
./show_jobs.sh              # All jobs
./show_jobs.sh "NVIDIA"     # Jobs from specific company

# Master CSV log (auto-updated after scrapes)
open MASTER_JOB_LOG.csv     # All jobs in Excel/CSV format
```

**Clean up:**
```bash
docker-compose down         # Stop Docker
```

That's it! Docker automatically starts when scraping and stops when done.

## 🏢 Tracked Companies (108)

**Quant/Trading Firms:**
Citadel, Two Sigma, Jane Street, HRT, D.E. Shaw, Jump Trading, Optiver, IMC, Akuna Capital, Susquehanna (SIG), Virtu Financial, DRW, Five Rings, Old Mission, Belvedere Trading, Tower Research

**FAANG+ Tech:**
Google, Meta, Amazon, Apple, Netflix, Microsoft, Adobe, Salesforce, Oracle, IBM

**AI/ML Companies:**
OpenAI, Anthropic, Scale AI, Hugging Face, Cohere

**Cloud/Infrastructure:**
Databricks, Snowflake, MongoDB, Confluent, HashiCorp

**Cybersecurity:**
CrowdStrike, Palo Alto Networks, Zscaler, Okta, SentinelOne, CrowdStrike

**Plus 60+ more** including fintech, autonomous vehicles, gaming, and enterprise software companies.

[Full list in `config/watchlist.yaml`](config/watchlist.yaml)

## 🛠️ How It Works

1. **Scraper visits** each company's career page
2. **Extracts** job listings using Playwright (headless browser)
3. **Filters** for:
   - Internships only
   - US locations only
   - Summer 2026 positions
   - ML/AI, Cybersecurity, Data Engineering, Data Science roles
4. **Saves** to PostgreSQL database
5. **Sends email** if new jobs found
6. **Shuts down** Docker when complete

### Supported ATS Platforms

- ✅ Greenhouse (Stripe, Airbnb, Robinhood)
- ✅ Lever (Netflix, Lyft, Figma)
- ✅ Ashby (OpenAI, Anthropic, Scale AI)
- ✅ SmartRecruiters (LinkedIn, Bosch)
- ✅ Workday (Oracle, IBM)
- ✅ Generic HTML (with Playwright for all others)

## 📊 Job Categories

Jobs are automatically classified into:

- **ML/AI** - Machine Learning, Deep Learning, NLP, Computer Vision
- **Cybersecurity** - Security Engineering, Threat Detection, Incident Response  
- **Data Engineering** - ETL, Data Pipelines, Big Data, Spark
- **Data Science** - Analytics, Research Scientists, Data Analysts

## 📧 Email Notifications

Get notified when new jobs are found!

**Setup Gmail notifications:**

1. [Create Gmail App Password](https://support.google.com/accounts/answer/185833)
2. Edit `.env`:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password  # 16-character app password
SMTP_FROM=your-email@gmail.com
SMTP_TO=your-email@gmail.com
```

3. Run scraper - you'll get email with new jobs!

## ➕ Adding Companies

1. Open `config/watchlist.yaml`
2. Add company:
```yaml
  - company: "Your Company"
    url: "https://careers.company.com/jobs"
    source: generic  # or greenhouse, lever, ashby, etc.
```
3. Test:
```bash
./scrape.sh "Your Company"
```

## 🖥️ Optional: Web Dashboard

View jobs in your browser:

```bash
# Start dashboard
docker-compose up -d api db

# Open browser
open http://localhost:8000

# Stop when done
docker-compose down
```

**Features:**
- 📊 Live statistics
- 🔍 Search jobs
- 🏢 Filter by company
- 📱 Filter by category
- ⏰ Countdown to next scrape

## 📁 Project Structure

```
InternTracker/
├── scrape.sh              # Main scraper command
├── show_jobs.sh           # View results
├── config/
│   └── watchlist.yaml     # 108 companies
├── src/
│   ├── ingest/            # Scrapers
│   ├── core/              # Database models  
│   └── app/               # Optional web dashboard
├── frontend/              # Dashboard UI
└── docker-compose.yml     # Docker setup
```

## ⚖️ Legal & Ethics

- ✅ **Respectful scraping** - 1-3 requests/second per domain
- ✅ **Public data only** - Career pages accessible to everyone
- ✅ **Respects robots.txt** - Follows site guidelines
- ❌ **No LinkedIn** - Against their Terms of Service
- ✅ **Rate limiting** - Doesn't overload servers
- ✅ **User-Agent** - Identifies as bot

## 🤝 Contributing

Contributions welcome!

- Add more companies
- Improve filtering logic
- Add new ATS platforms
- Fix bugs

## 📝 License

MIT License - see [LICENSE](LICENSE)

## 👤 Author

**Yash Lad**
- GitHub: [@yashlad](https://github.com/yashlad)
- Email: yashlad727@gmail.com

## ⭐ Star History

If this helped your job search, please star the repo!

## 🙏 Acknowledgments

- Inspired by [Simplify Jobs](https://simplify.jobs/) internship tracker
- Built with FastAPI, PostgreSQL, Playwright
- Companies data from public career pages

---

**Happy job hunting! 🎯**
