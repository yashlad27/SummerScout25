# 🎨 Progress Tracker Feature

## ✨ New Features Added

All scraping scripts now have **beautiful ASCII progress tracking** with:
- ✅ Real-time progress bar with █ blocks
- ✅ Company counter (X of Y)
- ✅ Elapsed time tracker
- ✅ Estimated time remaining
- ✅ Percentage complete
- ✅ Beautiful box-drawing characters

---

## 📺 What It Looks Like

### Batch Scraping (./scrape_batch.sh fraud)

```
╔════════════════════════════════════════════════════════════════╗
║  PROGRESS: [████████████████████████████░░░░░░░░░░] 65%
║  Company: 7 of 11  |  Remaining: 4
║  Elapsed: 1m 23s  |  Est. Time Left: 0m 47s
╚════════════════════════════════════════════════════════════════╝

  🔍 Scraping: Forter
  2025-10-25 20:15:34,055 - Processing Forter (greenhouse)
  2025-10-25 20:15:37,120 - Found 12 jobs for Forter
```

When complete:
```
╔════════════════════════════════════════════════════════════════╗
║  ✅ COMPLETE: 100%  [████████████████████████████████████████] 
║  Total Companies: 11
║  Total Time: 2m 15s
╚════════════════════════════════════════════════════════════════╝
```

---

### Full US Scrape (./scrape.sh)

```
╔════════════════════════════════════════════════════════════════╗
║  Starting full scrape of 323 companies
║  This will take approximately 30-40 minutes
╚════════════════════════════════════════════════════════════════╝

...scraping in progress...

╔════════════════════════════════════════════════════════════════╗
║  [████████████████░░░░░░░░░░░░░░░░░░░░░░░░] 42%
║  Progress: 135/323  |  Remaining: 188
║  Est. Time Left: 18m 35s
╚════════════════════════════════════════════════════════════════╝
```

Final:
```
╔════════════════════════════════════════════════════════════════╗
║  ✅ SCRAPING COMPLETE
║  Total Time: 32m 18s
╚════════════════════════════════════════════════════════════════╝
```

---

### India Scrape (./scrape_india.sh)

```
╔════════════════════════════════════════════════════════════════╗
║  Starting India scrape of 32 companies
║  This will take approximately 5-8 minutes
╚════════════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════════════════╗
║  [████████████████████████████░░░░░░░░░░░░] 72%
║  Progress: 23/32  |  Remaining: 9
║  Est. Time Left: 1m 47s
╚════════════════════════════════════════════════════════════════╝
```

---

## 🚀 Commands with Progress Tracking

### All scripts now show progress!

```bash
# Batch scraping - shows per-company progress
./scrape_batch.sh fraud      # 11 companies with live counter
./scrape_batch.sh payment    # 15 companies with live counter
./scrape_batch.sh trading    # 15 companies with live counter
./scrape_batch.sh bigtech    # 15 companies with live counter

# Full US scrape - shows overall progress
./scrape.sh                  # 323 companies with live progress

# India scrape - shows overall progress
./scrape_india.sh            # 32 companies with live progress

# Single company - simple output (no progress bar)
./scrape.sh "Sift"
./scrape_india.sh "Flipkart"
```

---

## 📊 Progress Information Shown

### For Each Script:

1. **Progress Bar**
   - 40-character wide ASCII bar
   - Uses █ for filled, ░ for empty
   - Updates in real-time

2. **Company Counter**
   - Current position (e.g., "7 of 11")
   - Remaining companies

3. **Time Tracking**
   - Elapsed time (minutes:seconds)
   - Estimated time remaining (calculated from average)

4. **Percentage Complete**
   - Shown as XX%
   - Updates with each company

5. **Final Summary**
   - Total companies processed
   - Total time taken
   - Displayed in a nice box

---

## 💡 How It Works

### Batch Scripts (`scrape_batch.sh`)
- Processes one company at a time
- Updates progress after each company completes
- Shows company name being scraped
- Calculates average time per company
- Estimates remaining time based on actual performance

### Full Scripts (`scrape.sh`, `scrape_india.sh`)
- Monitors the Python runner output
- Detects when each company starts processing
- Queries database for completion count
- Updates progress in real-time
- Shows estimated time based on current pace

---

## 🎯 Example Usage

### Quick fraud detection jobs:
```bash
./scrape_batch.sh fraud
```

Output:
```
╔════════════════════════════════════════════════════════════════╗
║  PROGRESS: [████████████████████░░░░░░░░░░░░░░░░░░] 54%
║  Company: 6 of 11  |  Remaining: 5
║  Elapsed: 1m 12s  |  Est. Time Left: 1m 2s
╚════════════════════════════════════════════════════════════════╝

  🔍 Scraping: Riskified
```

---

## ✅ Benefits

1. **See Progress**: Know exactly where you are
2. **Time Management**: See how long it will take
3. **Plan Ahead**: Estimate remaining time
4. **Beautiful UI**: Nice ASCII art display
5. **Real-time Updates**: Live progress tracking

---

## 🎨 Box Drawing Characters Used

```
╔ ═ ╗  (top border)
║     ║  (sides)
╚ ═ ╝  (bottom border)

█ (filled block)
░ (empty block)
```

---

## 📝 Notes

- Progress bars update after each company
- Time estimates become more accurate as scraping progresses
- Single company scrapes don't show progress bars (not needed)
- All timing is in minutes and seconds
- Total companies counts are hardcoded but accurate

---

**Enjoy watching your scraper work in real-time!** 🚀
