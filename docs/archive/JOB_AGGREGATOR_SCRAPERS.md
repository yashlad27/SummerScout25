# Job Aggregator Scrapers (Indeed, LinkedIn, Glassdoor)

## ⚠️ IMPORTANT WARNING

### **LinkedIn & Glassdoor: NOT RECOMMENDED** ❌

**LinkedIn:**
- ❌ Requires authentication
- ❌ Against Terms of Service
- ❌ Very aggressive anti-bot measures
- ❌ Will ban your account
- ✅ **Alternative**: Use company career pages or LinkedIn Talent Solutions API

**Glassdoor:**
- ❌ Requires authentication
- ❌ Has Cloudflare protection
- ❌ Heavy rate limiting
- ✅ **Alternative**: Use company career pages

### **Indeed: LIMITED USE** ⚠️

**Indeed:**
- ⚠️ Has rate limiting (can get blocked)
- ⚠️ Anti-bot measures (may require CAPTCHA)
- ⚠️ Not reliable for production
- ✅ **Better**: Use [Indeed Publisher API](https://www.indeed.com/publisher)
- ✅ **Best**: Use company career pages directly

---

## Why Company Career Pages Are Better

Your current setup (scraping company ATSs) is:
- ✅ **Legal**: Public career pages, no ToS violations
- ✅ **Reliable**: Direct from source, no aggregator delays
- ✅ **Accurate**: Most up-to-date information
- ✅ **Fast**: No rate limits from aggregators
- ✅ **Complete**: Full job descriptions

Job aggregators:
- ❌ Jobs may be outdated
- ❌ Missing details
- ❌ Rate limits
- ❌ Legal risks

---

## Usage (If You Really Want To Try Indeed)

### Add to Watchlist

```yaml
targets:
  # Example: Search Indeed for any company
  - company: "Google"
    ats_type: "indeed"
    careers_url: "https://www.indeed.com"  # Not used, but required
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Mountain View", "New York", "Remote"]
    categories: ["ml_ai", "data_science"]
```

### Run Test

```bash
# Test Indeed scraper for one company
docker-compose run --rm worker python -m src.ingest.runner --dry-run --company Google

# Watch for rate limiting errors
docker-compose logs -f worker | grep "Rate limited"
```

---

## Expected Issues

### **429 Rate Limit Error**
```
ERROR: Rate limited by Indeed. Please wait before retrying.
```
**Solution:** Increase delay between requests, or use Indeed Publisher API

### **403 Forbidden**
```
ERROR: Blocked by Indeed. Consider using Indeed Publisher API.
```
**Solution:** You've been detected as a bot. Use official API instead.

### **Empty Results**
- Indeed may have changed their HTML structure
- Anti-bot measures triggered
- No results for that search

---

## Recommended Approach

### **Instead of job aggregators, add more company career pages:**

```yaml
targets:
  # Direct company career pages (RECOMMENDED)
  - company: "Google"
    ats_type: "generic"
    careers_url: "https://careers.google.com/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Mountain View", "New York", "Remote"]
    categories: ["ml_ai", "data_science"]
    
  - company: "Netflix"
    ats_type: "generic"
    careers_url: "https://jobs.netflix.com/"
    roles_include: ["intern", "summer 2026", "internship"]
    locations: ["Los Gatos", "Remote"]
    categories: ["ml_ai", "data_science"]
```

---

## If You Need Indeed Publisher API

**Steps:**
1. Sign up at https://www.indeed.com/publisher
2. Get API key
3. Read documentation: https://opensource.indeedeng.io/api-documentation/
4. Implement proper API client (more reliable than scraping)

**Benefits:**
- ✅ No rate limits
- ✅ Legal
- ✅ Structured data
- ✅ More reliable

---

## Summary

### ✅ **DO USE:**
- Company career pages (your current 107 companies)
- ATS scrapers (Greenhouse, Lever, Ashby)
- Generic scrapers for company websites

### ❌ **DON'T USE:**
- LinkedIn scraper (will ban you)
- Glassdoor scraper (won't work)
- Indeed scraper (unreliable, rate limits)

### 💡 **YOUR CURRENT SETUP IS BEST:**
You already have 107 companies tracking directly from their career pages. This is:
- More reliable
- Faster
- Legal
- Complete

**Recommendation:** Keep using your current setup and add more companies directly instead of using aggregators.
