# PARKING LOT - Deferred Enhancements

**Last Updated:** December 28, 2025 (v8.0)
**Status:** Alpaca Integration COMPLETE, Dashboard Update Deferred
**Next Phase:** Validate Alpaca execution quality, then update dashboard

---

## ✅ COMPLETED (Phase 1 + Gap-Ups)

**Catalyst Types Added:**
1. ✅ Price Target Raises (Tier 2) - ~100 candidates/day
2. ✅ 52-Week High Breakouts (Tier 4) - ~30 candidates/day
3. ✅ Sector Rotation (Tier 3) - ~20-70 candidates/day
4. ✅ Gap-Ups (Tier 4) - ~20-40 candidates/day
5. ✅ Revenue Surprises (Tier 1 enhancement) - Already implemented

**Expected Impact:** 2/day → 170-240/day (85-120x increase)
**Cost:** $0 (all FREE or existing APIs)

---

## ✅ COMPLETED (v8.0 - Alpaca Integration)

**Agent-Side Integration:**
1. ✅ Portfolio loading from Alpaca API (real-time position sync)
2. ✅ Order execution via Alpaca API (all buys/sells)
3. ✅ EXECUTE command places market orders for new positions
4. ✅ ANALYZE command places market orders for stop/target exits
5. ✅ Safety features (position verification, buying power checks)
6. ✅ Graceful fallback to JSON if Alpaca unavailable
7. ✅ Environment setup (keys added to /root/.env)
8. ✅ Cron automation verified (all commands can access Alpaca)

**Status:** Agent now executes via real brokerage API, ready for autonomous trading

---

## 🅿️ PARKING LOT - Not Implemented (Low Priority)

### Dashboard Alpaca Integration (Deferred - Post-Validation)

**Current State:**
- Dashboard reads from JSON files (current_portfolio.json, account_status.json)
- Agent updates both Alpaca API AND JSON files (backward compatibility)
- Dashboard shows accurate data with slight delay (updated at 9:45 AM and 4:30 PM)

**What Needs Updating:**
- Backend API (`dashboard_v2/backend/api_enhanced.py`)
- Endpoints to modify:
  - `/api/v2/portfolio` - Read from Alpaca instead of JSON
  - `/api/v2/account` - Get account value from Alpaca
  - `/api/v2/positions` - Load positions from Alpaca
  - Header data - Real-time account value and P/L

**Why Deferred:**
- Wait 1-2 weeks to validate Alpaca integration works correctly
- If Alpaca has issues, dashboard still works from JSON files
- Gives time to catch any position sync problems before changing dashboard
- Not urgent - dashboard is accurate, just not real-time

**Complexity:** LOW (2-4 hours)
**Effort:** Replace JSON file reads with `broker.get_portfolio_summary()` calls
**ROI:** MEDIUM (real-time dashboard updates instead of twice-daily)

**Implementation Path (when ready):**
1. Add Alpaca credentials to dashboard backend environment
2. Import AlpacaBroker in api_enhanced.py
3. Replace JSON file reads with broker API calls
4. Add error handling (fallback to JSON if Alpaca fails)
5. Test with live dashboard
6. Deploy to production

**Trigger for Implementation:**
- After 5-10 successful trading days with Alpaca
- When position sync is verified stable
- User requests real-time dashboard updates

---

### Why Other Tasks Deferred:
- Current enhancements should provide 85-120x increase in candidate flow
- Need to validate quality and win rates before adding more
- Remaining tasks are complex, time-consuming, and lower ROI

### Catalyst Detection Tasks (Deferred):

#### 1. Contract/Guidance Magnitude Parsing
**Complexity:** HIGH (requires NLP/entity extraction)
**Effort:** 10-15 hours
**ROI:** LOW (contracts already detected via keywords + 8-K)

**Current State:**
- System detects contract news via keywords ("awarded", "contract", "$")
- System detects 8-K Item 1.01 filings (Material Agreement)
- Missing: Dollar value extraction ($500M contract vs $5M contract)

**Why Deferred:**
- Requires entity extraction or regex parsing of dollar amounts
- High false positive rate (mentions of OTHER companies' contracts)
- Would need ticker-specific validation (NLP model or paid service)
- Marginal improvement over existing keyword detection

**Implementation Path (if needed later):**
- Option A: Use OpenAI API for entity extraction ($$$)
- Option B: Build regex patterns for dollar amounts (brittle, high maintenance)
- Option C: Use financial news NLP service like AlphaSense ($$$$)

---

#### 2. Share Buyback Detection
**Complexity:** HIGH (requires 8-K parsing + news NLP)
**Effort:** 12-18 hours
**ROI:** MEDIUM (buybacks are Tier 3 catalyst, ~10-20 candidates/day)

**Current State:**
- System does NOT detect buyback announcements
- Would be Tier 3 catalyst (similar to insider buying)

**Why Deferred:**
- Requires parsing SEC 8-K Item 8.01 (Other Events) or Item 7.01 (Regulation FD)
- 8-K filings are unstructured text (not machine-readable JSON)
- News keyword detection prone to false positives
- Lower priority than Tier 2/4 catalysts

**Implementation Path (if needed later):**
- Step 1: Use SEC EDGAR API to fetch 8-K filings for Item 7.01/8.01
- Step 2: Parse filing text for buyback keywords ("repurchase", "buyback", "$X billion")
- Step 3: Extract buyback size as % of market cap
- Step 4: Score based on magnitude (>5% of market cap = strong signal)
- Alternative: Use news API with buyback keywords + ticker validation

---

#### 3. Earnings Acceleration Detection
**Complexity:** MEDIUM (requires multi-quarter API calls)
**Effort:** 8-12 hours
**ROI:** MEDIUM (~20-30 candidates/day, enhances existing earnings beats)

**Current State:**
- System detects single-quarter earnings beats
- Missing: Quarter-over-quarter acceleration (Q1: +10%, Q2: +15%, Q3: +20%)

**Why Deferred:**
- Requires fetching 3-4 quarters of earnings data per stock
- Increases API calls (993 stocks × 4 quarters = ~4,000 API calls/day)
- FMP Free tier limit: 250 calls/day (would need paid tier)
- Finnhub earnings API has limited historical data

**Implementation Path (if needed later):**
- Step 1: Upgrade to FMP paid tier ($40/month) or use Polygon earnings API
- Step 2: Fetch last 4 quarters of EPS data per stock
- Step 3: Calculate QoQ growth rates
- Step 4: Detect acceleration pattern (improving growth rates)
- Step 5: Score based on acceleration magnitude
- Expected catalyst: "3-quarter earnings acceleration (+10% → +15% → +20%)"

---

#### 4. Insider Transaction Weighting by Size/Title
**Complexity:** MEDIUM (requires transaction amount parsing)
**Effort:** 6-10 hours
**ROI:** LOW (marginal improvement to existing insider buying detection)

**Current State:**
- System detects insider buying clusters (3+ transactions in 30 days)
- Treats all transactions equally (no size weighting)
- Treats all insiders equally (CEO = director = 10% owner)

**Why Deferred:**
- Finnhub insider API provides transaction details (shares, price, title)
- Would need to calculate dollar value of each transaction
- Would need to weight by title (CEO > CFO > Director)
- Marginal improvement (insider buying already Tier 3, heavily discounted)

**Implementation Path (if needed later):**
- Step 1: Parse Finnhub insider transaction data for share count + price
- Step 2: Calculate total dollar value per transaction
- Step 3: Implement title weighting:
  - CEO/CFO: 3x weight
  - Board members: 2x weight
  - Other officers: 1x weight
  - 10%+ owners: 4x weight
- Step 4: Require minimum $100k transaction size to count
- Step 5: Score based on total weighted dollar volume

---

## 📊 DECISION CRITERIA FOR REVISITING

**Revisit Dashboard Integration IF:**

1. **Alpaca Integration Validated:**
   - After 5-10 successful trading days with Alpaca
   - Position sync verified stable between agent and Alpaca
   - No order execution errors or sync issues
   - THEN: Update dashboard to read from Alpaca API

2. **User Requests Real-Time Updates:**
   - User wants to see positions update throughout the day
   - Current twice-daily updates (9:45 AM, 4:30 PM) insufficient
   - THEN: Implement real-time Alpaca dashboard integration

**Revisit Catalyst Detection Tasks IF:**

1. **Candidate Count Still Too Low:**
   - After production testing, if screener produces <100 candidates/day
   - AND win rate is still 65-70% (quality maintained)
   - THEN: Add buyback detection or earnings acceleration

2. **Quality Degradation:**
   - If win rate drops below 60% with new catalysts
   - THEN: DO NOT add more catalysts, focus on quality filters instead

3. **Specific User Request:**
   - If user explicitly wants buyback detection or earnings acceleration
   - OR if user identifies specific gap in catalyst coverage

4. **Budget Increase:**
   - If user approves paid API tier (FMP $40/month, AlphaSense $1000+/month)
   - THEN: Can implement earnings acceleration or contract magnitude parsing

---

## 🎯 RECOMMENDATION

**v8.0 Alpaca Integration is complete - focus on validation.**

**Dashboard Integration:**
- Current setup works (accurate data, twice-daily updates)
- Wait 1-2 weeks to validate Alpaca execution quality
- Update dashboard only after confirming position sync is stable
- LOW PRIORITY - not blocking any features

**Catalyst Detection:**
- Phase 1 + Gap-Ups should be sufficient for 6-12 months
- Expected flow: 170-240 candidates/day (17-24% hit rate)
- Claude evaluates 200 opportunities daily
- Accepts top 5-10 (scorecard ≥60 points)
- This is MORE THAN SUFFICIENT for a 10-position portfolio

**Only revisit parking lot if:**
- Alpaca integration validated (5-10 trading days) → Update dashboard
- Candidate count drops below 100/day in production → Add catalysts
- User explicitly requests specific enhancement
- Market regime changes make technical catalysts less effective

---

**Status:** v8.0 complete, dashboard update documented in parking lot
**Next Step:** Monitor Alpaca execution quality for 1-2 weeks
