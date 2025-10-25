# 🇮🇳 India Internship Tracker - Complete Plan

## 📋 Project Overview

Create a separate internship tracker for:
- **Target:** MS CS students in India
- **Focus:** Summer 2026 internships in India
- **Companies:** Indian tech companies + MNCs with India offices

---

## 🔍 APIs Available

### ✅ **RippleMatch**
- **Status:** Has unofficial API endpoints
- **Data:** Internships, full-time roles
- **Endpoints:** 
  - `https://ripplematch.com/api/opportunities/`
  - Filter by location, role type
- **Note:** Not official, may require scraping

### ❌ **Glassdoor**
- **Status:** No public API
- **Official:** Glassdoor API discontinued in 2017
- **Alternative:** Must use web scraping (violates ToS)
- **Recommendation:** Avoid

### ✅ **Better Alternatives:**
1. **AngelList (Wellfound)** - Has API for startups
2. **Internshala** - India's largest internship platform (requires scraping)
3. **LinkedIn Jobs API** - Official but expensive ($$$)
4. **Naukri/Indeed** - Require scraping

---

## 📂 Recommended File Structure

```
linkedin_job_scrapper/
├── README.md                          # Main docs
├── docker-compose.yml                 # Docker config
├── requirements.txt                   # Python deps
├── .env                              # Secrets (gitignored)
├── .gitignore
│
├── docs/                             # Documentation
│   ├── guides/                       # User guides
│   │   ├── ON_DEMAND_USAGE.md
│   │   └── BATCH_SCRAPING.md
│   ├── dev/                         # Developer docs
│   │   └── API.md
│   └── archive/                     # Old docs
│
├── scripts/                          # Shell scripts
│   ├── scrape.sh
│   ├── scrape_batch.sh
│   ├── show_jobs.sh
│   └── setup/                       # Setup scripts
│       └── install.sh
│
├── config/                           # Configuration
│   ├── us/                          # US internships
│   │   ├── watchlist.yaml
│   │   └── filters.yaml
│   └── india/                       # India internships (NEW)
│       ├── watchlist_india.yaml
│       └── filters_india.yaml
│
├── src/                              # Source code
│   ├── core/                        # Database models
│   ├── ingest/                      # Scrapers
│   │   ├── ats/                     # ATS-specific scrapers
│   │   └── regional/                # Regional scrapers (NEW)
│   │       ├── india.py
│   │       └── us.py
│   ├── app/                         # FastAPI backend
│   └── utils/                       # Utilities
│
├── frontend/                         # US dashboard
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── frontend-india/                   # India dashboard (NEW)
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── tests/                           # Tests
└── alembic/                         # DB migrations
```

---

## 🎯 Task List - India Internship Tracker

### Phase 1: Setup & Structure (30 min)
- [ ] 1.1 Reorganize current file structure
- [ ] 1.2 Create `config/india/` folder
- [ ] 1.3 Create `frontend-india/` folder
- [ ] 1.4 Create `src/ingest/regional/` folder
- [ ] 1.5 Update docker-compose.yml for dual frontends

### Phase 2: Indian Companies Watchlist (1 hour)
- [ ] 2.1 Research top 100 Indian tech companies
- [ ] 2.2 Identify career page URLs
- [ ] 2.3 Determine ATS types (Greenhouse, Lever, etc.)
- [ ] 2.4 Create `config/india/watchlist_india.yaml`
- [ ] 2.5 Create `config/india/filters_india.yaml`

**Indian Companies to Add:**
```
Product Companies:
- Flipkart, Swiggy, Zomato, Ola, PhonePe, Paytm
- Razorpay, Zerodha, CRED, Dream11, MPL
- Freshworks, Zoho, BrowserStack, Postman

MNCs with India Offices:
- Microsoft India, Google India, Amazon India
- Adobe India, Oracle India, SAP Labs
- Goldman Sachs Bangalore, JPMorgan Bangalore

IT Services:
- TCS, Infosys, Wipro, HCL, Tech Mahindra
- Accenture, Cognizant, Capgemini

Startups:
- Urban Company, Meesho, ShareChat, Unacademy
- PhysicsWallah, Udaan, Dunzo, Licious
```

### Phase 3: India-Specific Scrapers (2 hours)
- [ ] 3.1 Create Internshala scraper (biggest platform)
- [ ] 3.2 Create Naukri.com internship scraper
- [ ] 3.3 Create AngelList India scraper
- [ ] 3.4 Create RippleMatch India filter
- [ ] 3.5 Add location filters for Indian cities

### Phase 4: Frontend for India (2 hours)
- [ ] 4.1 Clone frontend to `frontend-india/`
- [ ] 4.2 Update branding ("India Internships 2026")
- [ ] 4.3 Add Indian city filters (Bangalore, Hyderabad, Pune, etc.)
- [ ] 4.4 Update currency to INR (stipend display)
- [ ] 4.5 Add "Remote India" filter
- [ ] 4.6 Update API endpoints to filter by country

### Phase 5: Database Schema Updates (1 hour)
- [ ] 5.1 Add `country` field to jobs table
- [ ] 5.2 Add `stipend_currency` field
- [ ] 5.3 Add migration for new fields
- [ ] 5.4 Update filters for India/US separation

### Phase 6: API Updates (1 hour)
- [ ] 6.1 Add `/jobs/india` endpoint
- [ ] 6.2 Add `/jobs/us` endpoint
- [ ] 6.3 Add country filter to main `/jobs` endpoint
- [ ] 6.4 Update stats to show country breakdown

### Phase 7: Scraping Scripts (30 min)
- [ ] 7.1 Create `scrape_india.sh`
- [ ] 7.2 Create `scrape_batch_india.sh`
- [ ] 7.3 Update docker-compose for dual scraping

### Phase 8: Testing (1 hour)
- [ ] 8.1 Test Indian company scrapers
- [ ] 8.2 Test frontend-india dashboard
- [ ] 8.3 Test dual-region workflow
- [ ] 8.4 Verify data separation

### Phase 9: Documentation (30 min)
- [ ] 9.1 Update README with dual-region info
- [ ] 9.2 Create India-specific usage guide
- [ ] 9.3 Document Indian company list

---

## 🚀 Implementation - Step by Step

### STEP 1: Reorganize Files (Do Now)

```bash
# Create new folders
mkdir -p config/us config/india
mkdir -p frontend-india
mkdir -p src/ingest/regional
mkdir -p scripts/setup
mkdir -p docs/guides docs/dev

# Move existing configs
mv config/watchlist.yaml config/us/
mv config/filters.yaml config/us/

# Move scripts
mv scrape.sh scrape_batch.sh show_jobs.sh scripts/

# Update permissions
chmod +x scripts/*.sh
```

### STEP 2: Create Indian Companies Watchlist

**File:** `config/india/watchlist_india.yaml`

```yaml
targets:
  # Product Companies
  - company: "Flipkart"
    url: "https://www.flipkartcareers.com/"
    source: "generic"
    country: "india"
  
  - company: "Swiggy"
    url: "https://careers.swiggy.com/"
    source: "greenhouse"
    country: "india"
  
  - company: "Zomato"
    url: "https://www.zomato.com/careers"
    source: "generic"
    country: "india"
  
  - company: "Razorpay"
    url: "https://razorpay.com/jobs/"
    source: "lever"
    country: "india"
  
  - company: "CRED"
    url: "https://careers.cred.club/"
    source: "generic"
    country: "india"
  
  # MNCs India Offices
  - company: "Microsoft India"
    url: "https://careers.microsoft.com/students/in"
    source: "generic"
    country: "india"
  
  - company: "Google India"
    url: "https://buildyourfuture.withgoogle.com/programs/internships/india"
    source: "generic"
    country: "india"
  
  - company: "Amazon India"
    url: "https://www.amazon.jobs/en/search?country[]=IND"
    source: "generic"
    country: "india"
  
  # Add 50+ more companies...
```

### STEP 3: Create India Scraper

**File:** `src/ingest/regional/india.py`

```python
"""India-specific job scraper."""

from src.ingest.base import BaseScraper

class InternshalaScaper(BaseScraper):
    """Scrape internships from Internshala (India's largest platform)."""
    
    source = "internshala"
    base_url = "https://internshala.com"
    
    def fetch(self):
        # Scrape Internshala listings
        # Filter for tech internships
        # Return normalized jobs
        pass

class NaukriInternshipScraper(BaseScraper):
    """Scrape internships from Naukri.com."""
    
    source = "naukri"
    base_url = "https://www.naukri.com/internship-jobs"
    
    def fetch(self):
        # Scrape Naukri listings
        pass
```

### STEP 4: Create India Frontend

**File:** `frontend-india/index.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>🇮🇳 India Tech Internships 2026</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>🇮🇳 India Tech Internships - Summer 2026</h1>
        <p>Tracking 100+ Indian companies</p>
    </header>
    
    <!-- Indian city filters -->
    <div class="city-filters">
        <button data-city="bangalore">Bangalore</button>
        <button data-city="hyderabad">Hyderabad</button>
        <button data-city="pune">Pune</button>
        <button data-city="delhi-ncr">Delhi NCR</button>
        <button data-city="mumbai">Mumbai</button>
        <button data-city="remote">Remote India</button>
    </div>
    
    <!-- Rest of dashboard -->
</body>
</html>
```

### STEP 5: Update docker-compose.yml

```yaml
services:
  # Existing services...
  
  # India Frontend (port 8001)
  api-india:
    build: .
    ports:
      - "8001:8000"
    environment:
      - REGION=india
    volumes:
      - ./frontend-india:/app/frontend
    command: uvicorn src.app.main:app --host 0.0.0.0 --port 8000
```

### STEP 6: Create Scraping Scripts

**File:** `scripts/scrape_india.sh`

```bash
#!/usr/bin/env bash
# Scrape Indian companies

docker-compose up -d db redis api-india
docker-compose run --rm worker python -m src.ingest.runner \
    --config config/india/watchlist_india.yaml \
    --country india

echo "🌐 View dashboard: http://localhost:8001"
```

---

## 🔑 Key Differences: US vs India

| Feature | US Tracker | India Tracker |
|---------|-----------|---------------|
| **Port** | 8000 | 8001 |
| **Companies** | 187 US companies | 100+ Indian companies |
| **Platforms** | Company careers pages | Internshala, Naukri, company pages |
| **Locations** | US cities | Indian cities (Bangalore, Hyderabad, etc.) |
| **Currency** | USD | INR |
| **Config** | `config/us/` | `config/india/` |
| **Frontend** | `frontend/` | `frontend-india/` |

---

## 📊 Estimated Timeline

- **File reorganization:** 30 min
- **India watchlist:** 1 hour
- **India scrapers:** 2 hours  
- **India frontend:** 2 hours
- **Testing:** 1 hour
- **Total:** ~6-7 hours

---

## 🎯 Quick Start (After Implementation)

```bash
# US internships
./scripts/scrape.sh
open http://localhost:8000

# India internships  
./scripts/scrape_india.sh
open http://localhost:8001

# Both simultaneously
docker-compose up -d
```

---

## ⚠️ Important Notes

1. **Internshala requires login** - May need account for API access
2. **Naukri has rate limits** - Be careful with scraping
3. **AngelList has API** - Use official endpoints when possible
4. **Glassdoor = Avoid** - No API, ToS violation
5. **RippleMatch** - Unofficial API, may break

---

## 🚀 Next Steps

Should I start implementing this? Which phase would you like to begin with?

1. **Reorganize files** (quick, 5 min)
2. **Create Indian companies list** (need research)
3. **Build India frontend** (2 hours)
4. **Create scrapers** (2 hours)

Let me know which to prioritize!
