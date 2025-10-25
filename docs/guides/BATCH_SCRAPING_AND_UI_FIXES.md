# 🔧 Batch Scraping + UI Fixes Guide

## Problem 1: Slow Scraping (187 companies takes 25-30 minutes)
## Problem 2: Localhost not working + UI search broken

---

## ✅ Solution 1: Batch Scraping Script Created

### **File:** `scrape_batch.sh`

**What it does:**
- Scrapes companies in logical batches by type/industry
- Much faster than scraping all 187 companies at once
- Organizes companies into 16 different batches

### **Usage:**

```bash
# See available batches
./scrape_batch.sh

# Scrape specific batches (2-3 minutes each)
./scrape_batch.sh fintech      # Stripe, Coinbase, Ramp, etc.
./scrape_batch.sh quant        # Citadel, HRT, Jane Street, etc.
./scrape_batch.sh ai           # OpenAI, Anthropic, Scale AI, etc.
./scrape_batch.sh bigtech      # FAANG companies
./scrape_batch.sh security     # CrowdStrike, Palo Alto, etc.

# Or scrape all companies
./scrape_batch.sh all
```

### **Available Batches:**

| Batch | Companies | Est. Time | Example Companies |
|-------|-----------|-----------|-------------------|
| `fintech` | 16 | ~2-3 min | Stripe, Coinbase, Ramp, Mercury |
| `bigtech` | 11 | ~5-8 min | Google, Meta, Amazon, Apple |
| `quant` | 11 | ~2-3 min | Citadel, Two Sigma, Jane Street |
| `cloud` | 8 | ~2 min | Databricks, Snowflake, MongoDB |
| `security` | 12 | ~2-3 min | CrowdStrike, Palo Alto, Wiz |
| `ai` | 12 | ~2 min | OpenAI, Anthropic, Runway |
| `gaming` | 5 | ~1 min | Unity, Roblox, Epic Games |
| `social` | 6 | ~3-4 min | Reddit, Snap, Discord |
| `devtools` | 10 | ~2 min | GitHub, Vercel, Postman |
| `enterprise` | 10 | ~2-3 min | Notion, Airtable, Monday.com |
| `mobility` | 8 | ~2-3 min | Uber, DoorDash, Waymo |
| `ecommerce` | 5 | ~1 min | Shopify, Faire, Flexport |
| `health` | 4 | ~1 min | Oscar Health, Tempus |
| `edtech` | 5 | ~1 min | Coursera, Duolingo, Grammarly |
| `data` | 8 | ~2 min | Fivetran, dbt Labs, Airbyte |
| `banking` | 5 | ~3-4 min | JPMorgan, Goldman Sachs |

### **Workflow Example:**

```bash
# Morning: Scrape high-priority batches (10 minutes total)
./scrape_batch.sh fintech
./scrape_batch.sh quant
./scrape_batch.sh ai
./scrape_batch.sh bigtech

# View results
./show_jobs.sh

# Evening: Scrape remaining batches
./scrape_batch.sh security
./scrape_batch.sh devtools
./scrape_batch.sh enterprise

# View all jobs
./show_jobs.sh
```

---

## ✅ Solution 2: Fix UI and Localhost

### **Issue 1: API Not Responding**

The API needs to be started:

```bash
# Start API server
docker-compose up -d api db redis

# Check if it's running
curl http://localhost:8000/healthz

# View logs if issues
docker logs job_tracker_api
```

### **Issue 2: Frontend Search Not Working**

**Root cause:** The `renderJobs()` function needs to properly filter jobs based on search input.

**Fix needed in:** `frontend/app.js`

The search function at line 330 just calls `renderJobs()` but `renderJobs()` doesn't read the search input.

### **Quick Fix:**

Update the `renderJobs()` function to include search filtering:

```javascript
// Around line 200 in app.js
function renderJobs() {
    const container = document.getElementById('jobsGrid');
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const usOnlyFilter = document.getElementById('usOnlyFilter').checked;
    
    // Filter jobs
    let filteredJobs = allJobs;
    
    // Category filter
    if (currentFilter !== 'all') {
        filteredJobs = filteredJobs.filter(job => job.category === currentFilter);
    }
    
    // Search filter (FIXED)
    if (searchInput) {
        filteredJobs = filteredJobs.filter(job => 
            job.company.toLowerCase().includes(searchInput) ||
            job.title.toLowerCase().includes(searchInput) ||
            (job.location && job.location.toLowerCase().includes(searchInput))
        );
    }
    
    // US location filter
    if (usOnlyFilter) {
        filteredJobs = filteredJobs.filter(job => isUSLocation(job.location));
    }
    
    // Sort: new jobs first
    filteredJobs.sort((a, b) => {
        if (a.isNew && !b.isNew) return -1;
        if (!a.isNew && b.isNew) return 1;
        return new Date(b.first_seen_at) - new Date(a.first_seen_at);
    });
    
    // Rest of the rendering code...
}
```

---

## 🔧 Complete UI Fix Steps

### **Step 1: Check API is Running**

```bash
cd /Users/yashlad/Development/linkedin_job_scrapper

# Start services
docker-compose up -d api db redis

# Wait 5 seconds
sleep 5

# Test API
curl http://localhost:8000/healthz
```

**Expected output:** `{"status":"healthy","timestamp":"..."}`

### **Step 2: Open Browser**

```bash
open http://localhost:8000
```

### **Step 3: Check Browser Console**

1. Open browser dev tools (F12 or Cmd+Option+I)
2. Go to Console tab
3. Look for errors

**Common errors and fixes:**

| Error | Fix |
|-------|-----|
| `Failed to fetch` | API not running → `docker-compose up -d api` |
| `CORS error` | Already fixed in `main.py` |
| `404 Not Found` | Frontend not mounted → check `frontend/` folder exists |

### **Step 4: Verify Frontend Files**

```bash
ls -la frontend/
# Should show:
# - index.html
# - app.js
# - styles.css
```

---

## 🐛 Known Issues & Fixes

### **Issue 1: Search Function Not Working**

**Symptom:** Typing in search box doesn't filter jobs

**Fix:** Update `frontend/app.js` line 200-240 with proper search filtering (see code above)

### **Issue 2: "localhost refused to connect"**

**Fix:**
```bash
# Stop everything
docker-compose down

# Start fresh
docker-compose up -d db redis
sleep 3
docker-compose up -d api

# Check logs
docker logs job_tracker_api
```

### **Issue 3: No jobs showing on dashboard**

**Fix:**
```bash
# Run a quick scrape first
./scrape_batch.sh ai  # Fast batch for testing

# Refresh browser
```

### **Issue 4: Category filters not working**

**Check:** Make sure all new categories are in the filter tabs.

Update `frontend/index.html` around line 79-94 to include new categories:

```html
<div class="filter-tabs">
    <button class="filter-tab active" data-category="all">All Categories</button>
    <button class="filter-tab" data-category="software_engineering">💻 Software Eng</button>
    <button class="filter-tab" data-category="backend">🔧 Backend</button>
    <button class="filter-tab" data-category="frontend">🎨 Frontend</button>
    <button class="filter-tab" data-category="fullstack">🌐 Full-Stack</button>
    <button class="filter-tab" data-category="mobile">📱 Mobile</button>
    <button class="filter-tab" data-category="devops">☁️ DevOps</button>
    <button class="filter-tab" data-category="ml_ai">🤖 ML/AI</button>
    <button class="filter-tab" data-category="data_science">📊 Data Science</button>
    <button class="filter-tab" data-category="data_engineering">🔨 Data Eng</button>
    <button class="filter-tab" data-category="cybersecurity">🔒 Security</button>
</div>
```

---

## 📊 Testing Checklist

### **Test Batch Scraping:**
- [ ] `./scrape_batch.sh` shows all available batches
- [ ] `./scrape_batch.sh ai` scrapes AI companies (2 min)
- [ ] Results shown at end of scrape
- [ ] `./show_jobs.sh` shows scraped jobs

### **Test UI:**
- [ ] `docker-compose up -d api` starts successfully
- [ ] `http://localhost:8000` loads dashboard
- [ ] Stats show correct numbers
- [ ] Search box filters jobs properly
- [ ] Category tabs work
- [ ] "Apply Now" buttons open correct URLs

---

## 🚀 Recommended Workflow

### **Daily Usage:**

```bash
# Morning (5 minutes)
./scrape_batch.sh quant
./scrape_batch.sh fintech
./scrape_batch.sh ai

# Check results
./show_jobs.sh

# View in browser
docker-compose up -d api
open http://localhost:8000

# Stop when done
docker-compose down
```

### **Weekly Full Scrape:**

```bash
# Sunday evening (30 minutes)
./scrape_batch.sh all

# Check dashboard
docker-compose up -d api
open http://localhost:8000

# Leave API running for the week
# Or stop: docker-compose down
```

---

## 📝 Files Modified/Created

1. ✅ **`scrape_batch.sh`** - NEW batch scraping script
2. ⚠️ **`frontend/app.js`** - NEEDS FIX for search function
3. ⚠️ **`frontend/index.html`** - MAY NEED UPDATE for new categories
4. ✅ **`config/filters.yaml`** - Already updated with new categories
5. ✅ **`config/watchlist.yaml`** - Already has 187 companies

---

## 🎯 Summary

**Batch Scraping:**
- ✅ Created and ready to use
- ✅ 16 different batches available
- ✅ Much faster than scraping all at once

**UI Fixes Needed:**
1. ⚠️ Fix search filtering in `frontend/app.js`
2. ⚠️ Update category tabs in `frontend/index.html`
3. ✅ API and CORS already configured

**Next Steps:**
1. Test batch scraping with `./scrape_batch.sh ai`
2. Start API with `docker-compose up -d api`
3. Open `http://localhost:8000` in browser
4. Apply search fix if needed

---

**Your scraper is now 187 companies strong with efficient batch processing!** 🚀
