# 🚀 Quick Reference Card

## ⚡ Most Common Commands

```bash
# Check if everything is running
docker ps

# View worker logs (see scraping activity)
docker logs -f job_tracker_worker

# Check how many jobs in database
docker exec job_tracker_worker python -c "from src.core.database import get_db_context; from src.core.models import Job; db = get_db_context().__enter__(); print(f'Total jobs: {db.query(Job).count()}')"

# Manually trigger scan for one company (TESTING)
docker-compose run --rm worker python -m src.ingest.runner --company "Google"

# Restart everything
docker-compose restart

# Stop everything
docker-compose down

# Start everything
docker-compose up -d
```

---

## 📊 Your Setup

| Item | Value |
|------|-------|
| **Companies Tracked** | 108 |
| **Scan Frequency** | Every 4 hours |
| **Email** | yashlad727@gmail.com |
| **Database** | PostgreSQL (Docker) |
| **Total Jobs Found** | Check with command above |

---

## 📧 Email Format

**Subject:** 🎯 X New Summer 2026 Internships Found!

**Content:**
- Summary (jobs found from X companies)
- ✅ Scanned 108 companies total
- Jobs grouped by category
- Expandable list of ALL 108 companies with status

---

## 🔒 Security Checklist

- [ ] Changed database password from `changeme123`
- [ ] Gmail 2FA enabled
- [ ] Read `SECURITY.md`
- [ ] `.env` file never committed to Git
- [ ] Regular backups scheduled

---

## 🆘 Emergency Commands

```bash
# Services not starting?
docker-compose down -v
docker-compose up -d --build

# Check for errors
docker logs job_tracker_worker | grep -i error

# Restart just worker and scheduler
docker-compose restart worker beat

# View all containers
docker ps -a
```

---

## 📁 Important Files

- **`START_HERE.md`** - Setup instructions
- **`SECURITY.md`** - Security guide
- **`IMPROVEMENTS_SUMMARY.md`** - What changed
- **`.env`** - Your credentials (NEVER commit!)
- **`config/watchlist.yaml`** - 108 companies list

---

## 🎯 Schedule

| Time | Action |
|------|--------|
| 12:00 AM | Scan all 108 companies |
| 4:00 AM | Scan all 108 companies |
| 8:00 AM | Scan all 108 companies |
| 12:00 PM | Scan all 108 companies |
| 4:00 PM | Scan all 108 companies |
| 8:00 PM | Scan all 108 companies |

---

**Keep it running. Check your email. Land that internship! 🎉**
