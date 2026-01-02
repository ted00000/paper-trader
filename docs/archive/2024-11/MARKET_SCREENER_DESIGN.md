# MARKET SCREENER SYSTEM - Design Document

## 🎯 Purpose

Replace Claude's guesswork stock selection with a real market screener that scans the S&P 1500 universe daily to find stocks with genuine Tier 1 catalysts and strong relative strength.

**Problem Solved:** Previously, Claude AI suggested stocks based on its training data (NVDA, PLTR, etc.) without knowing if they had real catalysts or met our RS filters. This resulted in 0/10 stocks passing validation.

**Solution:** Pre-screen the market for stocks that meet our baseline criteria, then let Claude pick the best 10 from real opportunities.

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ 8:30 AM - Market Screener (NEW)                             │
│                                                               │
│ 1. Load S&P 1500 ticker list                                │
│ 2. For each ticker:                                          │
│    - Calculate 3-month RS vs sector (must be ≥3%)           │
│    - Fetch recent news (last 7 days)                        │
│    - Calculate volume surge (vs 20-day avg)                 │
│    - Check for 52-week high proximity                       │
│ 3. Score and rank candidates                                │
│ 4. Save top 50 to screener_candidates.json                  │
│                                                               │
│ Output: 50 pre-qualified stocks with metrics                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 8:45 AM - GO Command (MODIFIED)                             │
│                                                               │
│ 1. Load screener_candidates.json                            │
│ 2. Pass candidates to Claude: "Pick best 10 from these 50"  │
│ 3. Claude analyzes and selects 10                           │
│ 4. Validation pipeline runs (Phase 1-4)                     │
│ 5. Save accepted picks to pending_positions.json            │
│                                                               │
│ Output: 0-10 stocks ready to trade                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 9:45 AM - EXECUTE Command (UNCHANGED)                       │
│                                                               │
│ Executes trades from pending_positions.json                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Screener Logic

### Phase 1: Universe Filter (S&P 1500)
- Start with all S&P 1500 stocks (~1,500 tickers)
- Filter out:
  - Stocks < $5 (penny stocks)
  - Market cap < $1B (liquidity issues)
  - No price data available

**Expected Output:** ~1,400 valid tickers

### Phase 2: Relative Strength Filter (CRITICAL)
For each stock:
1. Get 3-month return (90 days) from Polygon
2. Get sector ETF 3-month return
3. Calculate RS = stock_return - sector_return
4. **REJECT if RS < 3%**

**Expected Output:** ~300-500 stocks (top 20-30% by RS)

### Phase 3: Catalyst Detection
For remaining stocks, check for recent catalysts (last 7 days):

**A. News Volume & Quality**
- Fetch last 20 news articles (Polygon API)
- Score based on:
  - Keywords: "earnings", "guidance", "beat", "upgrade", "FDA", "approval", "contract"
  - Recency: Last 3 days = higher score
  - Publisher quality: WSJ, Bloomberg, Reuters = higher score
- Score 0-20 (same as validation pipeline)

**B. Volume Surge**
- Compare yesterday's volume to 20-day average
- Volume ratio > 2.0x = institutional interest
- Score 0-10

**C. Technical Setup**
- Distance from 52-week high
- Within 5% of high = breakout candidate
- Score 0-10

### Phase 4: Composite Scoring & Ranking
```
Composite Score = (RS_score * 0.40) +      # Relative strength (most important)
                  (News_score * 0.30) +     # Catalyst strength
                  (Volume_score * 0.20) +   # Institutional interest
                  (Technical_score * 0.10)  # Breakout potential

Where:
- RS_score = min(RS_pct / 15 * 100, 100)  # 15%+ RS = perfect score
- News_score = (news_score / 20) * 100     # 20/20 = perfect score
- Volume_score = min(volume_ratio / 3 * 100, 100)  # 3x+ volume = perfect
- Technical_score = (100 - distance_from_high_pct * 2)  # Closer = better
```

### Phase 5: Output Top 50
- Sort by composite score (descending)
- Take top 50 candidates
- Save to `screener_candidates.json` with full metrics

---

## 📁 Output Format: screener_candidates.json

```json
{
  "scan_date": "2025-11-10",
  "scan_time": "08:30:00 ET",
  "universe_size": 1500,
  "candidates_found": 50,
  "filters_applied": {
    "min_rs_pct": 3.0,
    "min_price": 5.0,
    "min_market_cap": 1000000000
  },
  "candidates": [
    {
      "ticker": "NVDA",
      "rank": 1,
      "composite_score": 87.5,
      "sector": "Technology",
      "price": 145.32,
      "market_cap": 3500000000000,

      "relative_strength": {
        "rs_pct": 12.5,
        "stock_return_3m": 18.3,
        "sector_return_3m": 5.8,
        "sector_etf": "XLK",
        "score": 83.3
      },

      "catalyst_signals": {
        "news_score": 18,
        "news_count": 20,
        "recent_keywords": ["earnings", "beat", "AI"],
        "score": 90.0
      },

      "volume_analysis": {
        "volume_ratio": 2.8,
        "avg_volume_20d": 45000000,
        "yesterday_volume": 126000000,
        "score": 93.3
      },

      "technical_setup": {
        "distance_from_52w_high_pct": 2.1,
        "is_near_high": true,
        "score": 95.8
      },

      "why_selected": "Strong RS (+12.5%), high news score (18/20), 2.8x volume surge, near 52w high"
    }
  ]
}
```

---

## 🧠 Learning System Integration

### Data to Track for Learning

**1. Daily Screening Results** (`strategy_evolution/screener_history.csv`)
```csv
Date,Total_Scanned,RS_Pass,Top50_Avg_Score,Min_RS,Max_RS,Avg_News_Score
2025-11-10,1500,342,72.3,3.1,18.7,12.4
```

**2. Screener vs Selection Analysis** (`strategy_evolution/screener_picks.csv`)
```csv
Date,Ticker,Screener_Rank,Screener_Score,Claude_Selected,Validation_Passed,Entry_Price,Exit_Price,Return_Pct
2025-11-10,NVDA,1,87.5,Yes,Yes,145.32,152.10,4.66
2025-11-10,PLTR,3,84.2,Yes,No,,,
```

**3. Learning Questions to Answer Weekly**
- What screener rank produces best returns? (Top 10? Top 20?)
- Which scoring components correlate with success? (RS? News? Volume?)
- Are we weighting components correctly? (40/30/20/10?)
- Should RS threshold be higher? (3% → 5%?)
- Does news score predict holding period success?
- Do volume surges predict better entries?

**4. Monthly Optimization**
Based on learning data, adjust:
- Composite score weightings
- RS minimum threshold
- Top N candidates to pass to Claude
- News scoring algorithm
- Volume surge significance

---

## ⚙️ Technical Implementation

### New Files Created
1. **`market_screener.py`** - Main screener logic
2. **`run_screener.sh`** - Wrapper script for cron
3. **`screener_candidates.json`** - Daily output (overwritten each day)
4. **`strategy_evolution/screener_history.csv`** - Historical scan results
5. **`strategy_evolution/screener_picks.csv`** - Track screener → selection → result

### Modified Files
1. **`agent_v5.5.py`** - GO command loads screener results
2. **`crontab`** - Add 8:30 AM screener job
3. **`PROJECT_INSTRUCTIONS.md`** - Document new workflow
4. **`daily_picks.csv`** - Add screener_rank and screener_score columns

### API Usage Impact
- **Polygon calls per day:** ~1,500 (S&P 1500 stocks)
- **Duration:** ~5-10 minutes
- **Rate limit:** Unlimited with Starter plan
- **Delay:** 15 minutes (acceptable for historical data)

### Error Handling
- If screener fails → GO command falls back to current behavior
- If screener produces < 10 candidates → GO command supplements with Claude picks
- All errors logged to `logs/screener.log`

---

## 📈 Success Metrics

### Week 1 Validation
- Compare screener picks vs Claude-only picks
- Measure: How many stocks pass validation? (target: 5-10 per day)
- Track: Screener rank vs final performance

### Month 1 Analysis
- Win rate by screener rank (1-10 vs 11-20 vs 21-30)
- Average return by composite score quartile
- Correlation: RS vs actual holding period return
- Correlation: News score vs exit reason

### Ongoing Optimization
- Quarterly review of scoring weights
- Adjust filters based on market regime (bull/bear)
- Consider adding momentum factors (50-day MA, MACD)

---

## 🔄 Future Enhancements

### Phase 2 (After 30 days of data)
- Machine learning model to optimize composite score
- Sector rotation signals (which sectors screening well?)
- Catalyst type detection (earnings vs upgrades vs technical)

### Phase 3 (After 90 days)
- Real-time intraday rescreening (2 PM check)
- Breakout alerts during market hours
- Integration with Alpaca for live trading

---

## 📝 Documentation Requirements

All changes must update:
1. **This file** (MARKET_SCREENER_DESIGN.md) - Design decisions
2. **PROJECT_INSTRUCTIONS.md** - User workflow changes
3. **SYSTEM_OPERATIONS_GUIDE.md** - Operational procedures
4. **Code comments** - Inline documentation
5. **Learning journal** - Weekly screener performance notes

---

**Document Version:** 1.0
**Created:** 2025-11-10
**Last Updated:** 2025-11-10
**Status:** Implementation in progress
