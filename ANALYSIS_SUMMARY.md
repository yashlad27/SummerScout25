# Job Scraper Analysis & Configuration Update

## Executive Summary
Analyzed the LinkedIn job scraper configuration and updated filters to match your requirements:
- ✅ MSCS/Data Science/AI/ML/Cybersecurity roles
- ✅ CompTIA certifications
- ✅ Summer 2026 internships
- ✅ F1 visa support filtering
- ✅ US locations only

---

## Key Findings

### 1. URL Validation Results
- **Total Companies**: 257
- **Companies with active jobs**: 29 (11%)
- **Companies with no current openings**: 228 (89%)
- **Broken/timeout URLs**: 0
- **Success rate**: 100% (all URLs are valid)

### 2. Timeout Issues
During actual scraping, many companies timeout (60s limit exceeded):
- **Root cause**: Companies using "generic" scraper (Playwright) take longer
- **Affected companies**: Microsoft, Amazon, Confluent, DoorDash, Cloudflare, etc.
- **Working well**: Companies with structured APIs (Greenhouse, Lever, Workday)

### 3. Job Distribution by ATS Type
- **Greenhouse**: ~100 companies - Fast, reliable API
- **Lever**: ~30 companies - Fast, reliable API
- **Workday**: ~20 companies - Moderate speed
- **Generic**: ~100 companies - Slow, prone to timeouts
- **Indeed**: Blocked by bot detection

---

## Changes Made

### 1. Updated `config/filters.yaml`

#### Added CompTIA Certification Filters
```yaml
cybersecurity:
  title_any:
    - "(?i)comptia"
    - "(?i)security\\+|sec\\+"
    - "(?i)network\\+|net\\+"
    - "(?i)cysa\\+|ceh"
    - "(?i)cissp|ccna security"
  description_hints:
    - "(?i)comptia|security\\+|network\\+"
    - "(?i)certifications.*security"
```

#### Added F1 Visa Support Filters
```yaml
visa:
  positive_indicators:
    - "(?i)visa.*sponsor"
    - "(?i)sponsor.*visa"
    - "(?i)f-?1.*visa"
    - "(?i)opt.*eligible"
    - "(?i)cpt.*eligible"
    - "(?i)international.*student"
  
  negative_indicators:
    - "(?i)must.*be.*authorized.*work"
    - "(?i)us.*citizen.*required"
    - "(?i)no.*visa.*sponsor"
    - "(?i)cannot.*sponsor"
    - "(?i)security.*clearance.*required"
```

### 2. Updated `src/ingest/classifier.py`
- Integrated visa sponsorship filtering into `JobFilter` class
- Added `_excludes_visa_sponsorship()` method
- Jobs explicitly stating "no visa sponsorship" are now filtered out

---

## Current Filter Criteria

Your jobs must match:
1. **Internship/Co-op**: Title or description contains intern, co-op, summer 2026
2. **Categories**: ML/AI, Data Science, Data Engineering, Cybersecurity
3. **Education**: Master's students (no PhD-only, no undergrad-only)
4. **Location**: US cities only (NY, SF, Boston, Chicago, Seattle, Austin, Remote)
5. **Visa**: No explicit "must have work authorization" requirements
6. **Timeline**: Summer 2026

Jobs are filtered out if they contain:
- Senior/Staff/Principal/Lead/Manager titles
- Non-engineering roles (Sales, Marketing, HR, etc.)
- Non-US locations
- PhD-only or undergrad-only requirements
- Explicit visa restrictions

---

## Recommendations

### Option 1: Quick Fix (Recommended)
Keep all 257 companies but accept that ~90% won't have matching jobs:
- Pros: Comprehensive coverage, no jobs missed
- Cons: Slow scraping (60+ minutes), many timeouts
- Best for: Weekly/bi-weekly runs

### Option 2: Optimized Watchlist
Create a curated list of ~50 reliable companies:
- Focus on Greenhouse/Lever companies (fast APIs)
- Prioritize companies known for intern programs
- Remove companies that consistently timeout
- Pros: Faster (5-10 min), fewer failures
- Cons: Might miss some opportunities

### Option 3: Hybrid Approach
Run two separate scrapes:
1. **Daily**: Top 30 companies with high intern hiring rates
2. **Weekly**: Full 257 company list for comprehensive coverage

---

## Companies Currently With Jobs (29 Total)

### Quantitative Trading (7 companies)
- Belvedere Trading (8 jobs)
- Voleon Group (73 jobs)
- Hudson River Trading
- Two Sigma
- D.E. Shaw
- Citadel
- Optiver

### Cybersecurity (11 companies)
- Feedzai (40 jobs)
- Forter (38 jobs)
- Riskified (28 jobs)
- Arkose Labs (18 jobs)
- Recorded Future (63 jobs)
- KnowBe4 (76 jobs)
- Dragos (21 jobs)
- Tanium (131 jobs)
- Orca Security (17 jobs)
- ComplyAdvantage (27 jobs)
- Jumio (17 jobs)

### Fintech (11 companies)
- Finix (14 jobs)
- Pagaya (12 jobs)
- Payoneer (100 jobs)
- Melio (17 jobs)
- Bill.com (73 jobs)
- MoneyLion (42 jobs)
- Prosper (9 jobs)
- Upstart (93 jobs)
- StockX (17 jobs)
- BigID (12 jobs)
- Alloy (7 jobs)

---

## Testing Your Configuration

### Test Single Company
```bash
./run.sh scrape-company "Citadel"
```

### Test 10 Companies
```bash
head -n 100 config/watchlist.yaml > config/watchlist_test.yaml
# Edit docker-compose.yml to use watchlist_test.yaml
./run.sh scrape
```

### View Results
```bash
./run.sh dashboard
# Open http://localhost:5000
```

---

## Next Steps

1. **Test the updated filters**:
   ```bash
   ./run.sh scrape-company "Databricks"
   ```

2. **Review filtered jobs**: Check that visa/certification filters work correctly

3. **Choose your approach**: Full list vs. optimized vs. hybrid

4. **Schedule regular runs**:
   ```bash
   ./run.sh scheduler  # Runs every 6 hours
   ```

5. **Monitor email notifications**: You'll get alerts for new matching jobs

---

## Files Modified
- `config/filters.yaml` - Added CompTIA and F1 visa filters
- `src/ingest/classifier.py` - Integrated visa filtering into JobFilter class
- `ANALYSIS_SUMMARY.md` - This document

## Files Generated
- `link_validation_results.yaml` - Validation results for all 257 companies
- `validation_results.txt` - Detailed validation log
