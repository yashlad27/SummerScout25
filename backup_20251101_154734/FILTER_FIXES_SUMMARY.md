# 🔧 Filter Pipeline Fixes - October 28, 2025

## ❌ **Problems Identified**

### 1. **PhD Positions Were Being INCLUDED (Wrong!)**
- The `internship.title_patterns` config had `"(?i)phd"` and `"(?i)doctoral"` as **positive matches**
- This meant the system was actively searching for and including PhD-only positions
- Result: PhD-only jobs were passing through when they should be excluded

### 2. **International Jobs Were Not Being Filtered**
- Jobs from Poland, Spain, Germany, Serbia, Denmark, France, Netherlands, Singapore, Hong Kong, etc. were passing through
- The location filter logic was too permissive - if a job listed multiple locations including one US city, it would pass
- Example: "Amsterdam, Netherlands; Belgrade, Serbia; Mountain View, California" would PASS because it contains California

### 3. **Generic Career Pages Were Treated as Jobs**
- Entries like "Internships", "Join our Talent Community", "Career Perspectives" were being saved as job postings
- These aren't actual job openings but general career information pages

### 4. **Undergrad-Only Positions Were Passing**
- No filter to exclude positions explicitly for undergraduates only
- Masters students may not be eligible for these

### 5. **No Description-Level Filtering**
- The negative keyword checks only looked at job titles
- PhD requirements in job descriptions were not being caught

---

## ✅ **Fixes Applied**

### 1. **Removed PhD from Positive Matches**
**Files:** `config/filters.yaml`, `config/us/filters.yaml`

**Before:**
```yaml
internship:
  title_patterns:
    - "(?i)phd"
    - "(?i)doctoral"
```

**After:**
```yaml
internship:
  title_patterns:
    - "(?i)graduate(?!.*phd)"  # Graduate but NOT PhD
    - "(?i)masters"
    - "(?i)master's"
```

### 2. **Added PhD-Only Exclusion Filter**
**Files:** `config/filters.yaml`, `config/us/filters.yaml`

Added new negative filter category:
```yaml
negatives:
  phd_only:
    - "(?i)\\bphd\\b.*(?:intern|graduate|student)"
    - "(?i)(?:intern|graduate|student).*\\bphd\\b"
    - "(?i)doctoral"
    - "(?i)ph\\.d\\."
```

This excludes jobs with titles/descriptions like:
- "PhD Intern"
- "Quantitative Researcher – PhD Graduate"
- "Software Developer Ph.D. Intern"

### 3. **Added Undergrad-Only Exclusion Filter**
```yaml
negatives:
  undergrad_only:
    - "(?i)undergraduate(?!.*graduate)"
    - "(?i)freshman|sophomore|junior(?!.*graduate)"
```

### 4. **Added Generic Career Page Filter**
```yaml
negatives:
  generic_pages:
    - "(?i)^internships?$"
    - "(?i)^internship programs?$"
    - "(?i)join.*talent.*community"
    - "(?i)^student.*opportunities?$"
    - "(?i)career.*perspectives"
    - "(?i)^undergraduates?$"
    - "(?i)early.*career$"
```

### 5. **Strengthened Location Filtering**
**File:** `src/ingest/classifier.py`

**Changes:**
- Expanded non-US location list to 60+ countries/cities
- Check BOTH title AND location fields for non-US indicators
- If ANY non-US location is found in the combined text, REJECT the job
- More strict about jobs with no location data - now requires clear US indicators in title

**New logic:**
```python
# Check both title and location for non-US indicators
combined_text = f"{title} {location}".lower()

for non_us_loc in non_us_locations:
    if non_us_loc in combined_text:
        return False  # Reject!
```

This now correctly rejects:
- "Software Engineering Intern (2026) Belgrade, Serbia"
- "Product Management Intern (2026) - Amsterdam"
- "Software Engineer II, Frontend (Checkout Experience International)Remote Poland"

### 6. **Enhanced Negative Keyword Checking**
**File:** `src/ingest/classifier.py`

- Now checks **both title AND description** for PhD keywords
- Added debug logging for each exclusion reason
- Checks all 4 negative categories: seniority, non_engineering, phd_only, undergrad_only, generic_pages

---

## 📊 **Expected Impact**

### Before Fixes:
- 1258 jobs fetched
- 1101 jobs filtered out (87.5%)
- 2 new jobs (0.2%)
- Many PhD, international, and generic pages were **incorrectly passing** through

### After Fixes (Expected):
- ✅ **All PhD-only positions will be excluded**
- ✅ **All international positions will be excluded**
- ✅ **Generic career pages will be excluded**
- ✅ **More actual Masters-eligible internships will be included**
- ✅ **US-only positions only**

The filter should now be **more precise** - excluding inappropriate jobs while including more relevant Masters-level internships.

---

## 🧪 **Testing the Fixes**

Run a test scrape:
```bash
# Test on a single company
./scrape.sh "Databricks"

# Or test full pipeline
./scrape_batch.sh
```

Check the logs for debug messages like:
- `Job 'X' excluded: PhD-only position`
- `Job 'Y' excluded: non-US location 'amsterdam'`
- `Job 'Z' excluded: generic career page`

---

## 🎯 **Recommendation**

The current system filters by:
1. ✅ Job type (internship/graduate)
2. ✅ Education level (Masters only, no PhD, no undergrad-only)
3. ✅ Location (US only)
4. ✅ Seniority (no senior/staff/manager)
5. ✅ Job category (engineering vs non-engineering)

**NOT filtering by:**
- Specific tech stack (Python, Java, React, Spark, etc.)

**Why:** Your watchlist includes 327 companies specifically chosen for their tech stacks. The companies themselves (Databricks, Citadel, HRT, etc.) use the technologies you listed. Rather than filtering individual job descriptions for tech keywords, it's better to trust that internships at these companies will involve relevant technologies.

If you want tech-specific filtering, we can add a description scanner that gives **priority/scoring** to jobs mentioning your tech stack, rather than hard-filtering them out.
