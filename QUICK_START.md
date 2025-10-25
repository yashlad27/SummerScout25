# 🚀 Quick Start Guide

## 🎯 Best Commands for YOUR Experience

### 1. Scrape Fraud Detection Companies (BEST MATCH)
```bash
./scrape_batch.sh fraud
```
**Companies**: Sift, Feedzai, BioCatch, Signifyd, Forter, Kount, Riskified, DataVisor, Socure, Arkose Labs, Castle

**Why**: Directly matches your Freecharge fraud detection work

---

### 2. Scrape Payment Infrastructure (VISA PROJECT MATCH)
```bash
./scrape_batch.sh payment
```
**Companies**: Adyen, Checkout.com, Modern Treasury, Lithic, Unit, Finix, Bolt, Rapyd, Nuvei, Payoneer, Wise, Remitly, Melio, Bill.com, Tipalti

**Why**: Perfect match for your Visa internship experience

---

### 3. Scrape Trading Firms (TRANSACTION PROCESSING)
```bash
./scrape_batch.sh trading
```
**Companies**: Citadel Securities, Virtu Financial, Tower Research Capital, Five Rings Capital, Belvedere Trading, Flow Traders, Millennium Management, Point72, Bridgewater Associates, etc.

**Why**: Value your low-latency transaction processing skills

---

## 📊 View Results

### After scraping, check:
1. **Dashboard**: http://localhost:8000
2. **Export Files**: `exports/` folder
   - `jobs_us_TIMESTAMP.txt` - Easy to read
   - `jobs_us_TIMESTAMP.xlsx` - Excel file
   - `summary_us_TIMESTAMP.txt` - Company breakdown

---

## 🔍 Search Specific Company

```bash
./scrape.sh "Sift"              # Single company
./scrape.sh "Citadel Securities"
./scrape.sh "Adyen"
```

---

## 📋 All Available Batches

Run without arguments to see all options:
```bash
./scrape_batch.sh
```

Output:
```
  🔥 RECOMMENDED FOR YOUR EXPERIENCE:
  fraud      - Fraud Detection (11 companies, ~2 min)
  payment    - Payment Infrastructure (15 companies, ~3 min)
  trading    - Trading Firms (15 companies, ~3 min)
  
  OTHER CATEGORIES:
  fintech    - General fintech (18 companies, ~3 min)
  bigtech    - FAANG + Big Tech (15 companies, ~6-8 min)
  security   - Cybersecurity (12 companies, ~2-3 min)
  ai         - AI/ML Startups (12 companies, ~2 min)
  banking    - Major banks (5 companies, ~3-4 min)
  ... and more
```

---

## 🇮🇳 India Internships

```bash
./scrape_india.sh              # All Indian companies
./scrape_india.sh "Flipkart"   # Specific company
```

Dashboard: http://localhost:8001

---

## ⚡ Quick Workflow

### Morning Routine (Get fresh jobs):
```bash
# 1. Scrape your top matches
./scrape_batch.sh fraud
./scrape_batch.sh payment
./scrape_batch.sh trading

# 2. Open dashboard
open http://localhost:8000

# 3. Check exports
open exports/
```

### Find Jobs Matching Your Skills:
1. Open `exports/jobs_us_TIMESTAMP.xlsx` in Excel
2. Filter by:
   - Category: `ml_ai`, `data_science`, `cybersecurity`
   - Location: Your preferred cities
   - Company: Search for specific names
3. Apply directly via the URLs in the spreadsheet

---

## 📈 Stats

- **Total US Companies**: 327
- **New Companies Added**: 140
- **Categories**: Fraud, Payment, Trading, Security, Fintech, Banking, etc.
- **Your Best Matches**: 50+ companies

---

## 🎯 Priority Application List

Based on your background (Freecharge fraud detection + Visa payment processing):

### Tier 1 - Apply First 🔥
1. **Sift** - ML fraud detection
2. **Feedzai** - Payment fraud ML
3. **Adyen** - Payment processing
4. **BioCatch** - Behavioral fraud detection
5. **Forter** - E-commerce fraud

### Tier 2 - Strong Matches 
6. **Citadel Securities** - HFT transaction processing
7. **Modern Treasury** - Payment infrastructure
8. **Signifyd** - Fraud prevention
9. **Virtu Financial** - Market making systems
10. **Lithic** - Card issuing platform

### Tier 3 - Great Opportunities
11. Checkout.com
12. Riskified
13. Tower Research Capital
14. DataVisor
15. Socure

---

## 🛠️ Troubleshooting

### Build/Install:
```bash
docker-compose build
```

### Reset Database:
```bash
docker-compose down -v
docker-compose up -d db
docker-compose run --rm migrate
```

### View Logs:
```bash
docker-compose logs -f worker
docker-compose logs -f api
```

---

## 💡 Pro Tips

1. **Run batch scrapes daily** - New jobs posted frequently
2. **Export to Excel** - Easier to filter and organize
3. **Focus on fraud/payment batches** - Best ROI for your profile
4. **Check dashboard after scraping** - Quick visual overview
5. **Use company-specific scrapes** - When you see a hot opportunity

---

## 🎓 Your Advantage

With your experience:
- ✅ Freecharge fraud detection → ML, transaction monitoring, risk systems
- ✅ Visa payment processing → Real-time systems, high-volume transactions
- ✅ Spring Boot, Java, PostgreSQL → Standard enterprise stack

You're a **perfect fit** for fraud detection platforms and payment infrastructure companies!

---

## 📞 Quick Commands Reference

```bash
# Scrape by category
./scrape_batch.sh fraud
./scrape_batch.sh payment
./scrape_batch.sh trading

# Scrape single company
./scrape.sh "Company Name"

# India tracker
./scrape_india.sh

# View options
./scrape_batch.sh

# Open dashboard
open http://localhost:8000
```

---

**Next Step**: Run `./scrape_batch.sh fraud` to get started! 🚀
