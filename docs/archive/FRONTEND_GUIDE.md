# 🎨 Frontend Dashboard Guide

## 🚀 Quick Start

### 1. Make Sure API is Running

The frontend needs the API server to be running:

```bash
# Check if API is running
docker ps | grep job_tracker_api

# If not running, start it
docker-compose up -d api
```

### 2. Access the Dashboard

Open your browser and go to:
```
http://localhost:8000
```

Or directly:
```
http://localhost:8000/dashboard
```

---

## 🎯 Features

### ✅ Real-Time Job Tracking
- **Auto-refresh every 60 seconds** - Always see the latest jobs
- **Manual refresh button** - Update on demand
- **Live statistics** - Total jobs, companies, new today

### 🔍 Smart Filtering
- **🇺🇸 US Locations Only** - Filter for United States positions (enabled by default)
- **Category filters** - ML/AI, Cybersecurity, Data Science, Data Engineering
- **Company search** - Find jobs by company name
- **Job title search** - Search by position title

### 📊 Dashboard Sections

1. **Statistics Cards**
   - 💼 Total Internships
   - 🏢 Companies Hiring
   - 🆕 New Today
   - 📧 Alerts Sent Today

2. **Companies Grid**
   - Shows top 20 companies with openings
   - Click any company to filter jobs
   - Shows job count per company

3. **Job Listings**
   - Full details for each internship
   - Direct "Apply Now" links
   - 🆕 NEW badge for jobs added today
   - Location, tags, and posting date

---

## 🇺🇸 US Location Filter

### How It Works

The dashboard **automatically filters** for United States positions by:

1. **Checking for US state codes**: CA, NY, TX, WA, etc.
2. **Recognizing US cities**: New York, San Francisco, Seattle, Boston, etc.
3. **Detecting US indicators**: "USA", "United States", "U.S."
4. **Excluding international**: Canada, UK, Singapore, India, etc.

### Supported US Locations

- **Major Tech Hubs**: San Francisco, Seattle, New York, Boston, Austin
- **Bay Area cities**: Mountain View, Palo Alto, Cupertino, Menlo Park
- **All 50 states**: Recognized by state codes
- **Remote**: Always included (assumed US-based)

### Toggle US Filter

The checkbox "🇺🇸 US Locations Only" is **checked by default**.
- ✅ **Checked** = Only show US positions (recommended)
- ⬜ **Unchecked** = Show all positions (including international)

---

## 🔍 Search & Filter Examples

### Search by Company
```
Type: "Google"
Result: Shows all Google internships
```

### Search by Job Title
```
Type: "Machine Learning"
Result: Shows all ML-related positions
```

### Filter by Category
```
Click: "🤖 ML/AI" button
Result: Shows only ML/AI internships
```

### Combined Filters
```
1. Click "🔒 Cybersecurity" category
2. Type "New York" in search
3. Keep "🇺🇸 US Only" checked
Result: US cybersecurity internships in NYC
```

---

## 🎨 Visual Features

### Color Coding
- **Blue**: Primary actions and categories
- **Green**: "Apply Now" buttons and new job badges
- **Purple gradient**: Background
- **White cards**: Clean, modern look

### Job Cards
- **Green border + 🆕 NEW badge** = Added today
- **Blue border** = Older positions
- **Company name** = Blue, clickable
- **Tags** = Category and keywords

### Responsive Design
- ✅ Desktop (1400px+)
- ✅ Tablet (768px - 1400px)
- ✅ Mobile (< 768px)

---

## 📱 Mobile Experience

On mobile devices:
- Stats grid shows 2 columns
- Filter tabs stack vertically
- Companies grid shows 1 column
- Touch-friendly buttons
- Optimized scrolling

---

## 🔄 Auto-Refresh

The dashboard **automatically refreshes** every 60 seconds:
- Updates statistics
- Loads new jobs
- Refreshes company counts
- Shows "Last updated" time

### Manual Refresh
Click the **🔄 Refresh** button anytime to update immediately.

---

## 🚨 Internship Validation

### How We Ensure Only Internships

The frontend validates jobs using:

1. **Title keywords**:
   - "intern"
   - "internship"
   - "summer 2026"
   - "co-op"
   - "coop"

2. **Tags**:
   - Checks job tags for internship indicators
   - Validates "summer-2026" tag

### Result
Only positions matching internship criteria are displayed!

---

## 🎯 Data Flow

```
Database (PostgreSQL)
    ↓
API Server (FastAPI) - Port 8000
    ↓
Frontend Dashboard (HTML/CSS/JS)
    ↓
Your Browser
```

### API Endpoints Used

1. **GET /stats** - Dashboard statistics
2. **GET /jobs?limit=500** - All jobs
3. **GET /companies** - Companies with openings

---

## ⚙️ Configuration

### Change API URL

If running API on different port, edit `frontend/app.js`:

```javascript
// Line 2
const API_BASE_URL = 'http://localhost:8000';

// Change to your API URL
const API_BASE_URL = 'http://localhost:9000';
```

### Change Refresh Interval

Default is 60 seconds. To change, edit `frontend/app.js`:

```javascript
// Line 3
const REFRESH_INTERVAL = 60000; // 60 seconds

// Change to 30 seconds
const REFRESH_INTERVAL = 30000;
```

---

## 🐛 Troubleshooting

### "Failed to load data. Make sure the API server is running"

**Solution:**
```bash
# Check API is running
docker ps | grep job_tracker_api

# Start API if not running
docker-compose up -d api

# Check API is accessible
curl http://localhost:8000/healthz
```

### "No Internships Found"

**Possible causes:**
1. No jobs in database yet
2. Filters too restrictive
3. US filter excluding all jobs

**Solution:**
```bash
# Run scraper to get jobs
docker-compose run --rm worker python -m src.ingest.runner --company "Google"

# Or clear filters in dashboard
- Uncheck "US Only"
- Select "All Categories"
- Clear search box
```

### Dashboard not loading

**Check:**
1. API server running on port 8000
2. Browser JavaScript enabled
3. No browser console errors (F12)

**Restart API:**
```bash
docker-compose restart api
```

---

## 📊 Performance

### Loading Speed
- Initial load: < 2 seconds
- Refresh: < 1 second
- Handles 500+ jobs smoothly

### Optimizations
- Client-side filtering (instant)
- Efficient rendering
- Auto-refresh without page reload
- Minimal API calls

---

## 🎨 Customization

### Change Colors

Edit `frontend/styles.css`:

```css
:root {
    --primary-color: #3498db;  /* Blue */
    --secondary-color: #2ecc71; /* Green */
    /* Change to your colors */
}
```

### Add More Categories

Edit `frontend/index.html`:

```html
<button class="filter-tab" data-category="YOUR_CATEGORY" onclick="filterByCategory('YOUR_CATEGORY')">
    🔧 Your Category
</button>
```

---

## 📈 Statistics Explained

### Total Internships
All active internship positions in database

### Companies Hiring
Number of unique companies with openings

### New Today
Jobs first seen today (useful for daily checks)

### Alerts Sent Today
Email notifications sent today (from worker)

---

## 🔒 Security

### Safe Browsing
- ✅ XSS protection (HTML escaping)
- ✅ CORS enabled for localhost
- ✅ No sensitive data exposed
- ✅ Opens job links in new tab

### Production Deployment

For production, update CORS in `src/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["GET"],  # Only GET requests
    allow_headers=["*"],
)
```

---

## 🚀 Access Methods

### Method 1: Direct Browser
```
http://localhost:8000/
```

### Method 2: Via Dashboard Route
```
http://localhost:8000/dashboard
```

### Method 3: Direct File (No API)
```bash
# Open file directly (limited features)
open frontend/index.html
```

**Note:** Direct file access won't load data (needs API).

---

## 📱 Sharing

### On Local Network

1. Find your IP address:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

2. Share URL:
```
http://YOUR_IP:8000/
```

Example: `http://192.168.1.100:8000/`

**Note:** Firewall may block external access.

---

## ✅ Features Checklist

- [x] Real-time job listings
- [x] 🇺🇸 US location filter
- [x] Internship validation
- [x] Company search
- [x] Category filtering
- [x] Auto-refresh (60s)
- [x] Manual refresh button
- [x] Statistics dashboard
- [x] New job badges
- [x] Mobile responsive
- [x] Direct apply links
- [x] Clean, modern UI

---

## 🎉 You're All Set!

**Your dashboard is ready!**

1. ✅ Filters for US positions only
2. ✅ Shows only internships
3. ✅ Real-time updates
4. ✅ Beautiful, modern interface

**Access it at:** http://localhost:8000/

---

## 📚 Files

- **`frontend/index.html`** - Main HTML structure
- **`frontend/styles.css`** - All styling
- **`frontend/app.js`** - JavaScript logic
- **`src/app/main.py`** - API server (updated with CORS)

---

**Enjoy your new dashboard! Track those Summer 2026 internships! 🎯**
