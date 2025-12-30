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

---

## 🔍 MARKET SCREENER AUDIT - DEFERRED RECOMMENDATIONS
**Date Added:** December 30, 2025
**Context:** Third-party LLM audit after screener returned only 1 stock (Dec 30, holiday conditions)
**Audit Score:** 7.6/10 (up from 5.x) - Screener fixes successful, slight overshoot on strictness

### **What We're Implementing (Targeted Fixes)**
✅ **Tier-aware freshness:** Allow 72-96h for Tier 1 catalysts (vs. 48h for others)
✅ **Breakout maintenance soft scoring:** ≤3% full score, 3-6% partial, >6% reject
✅ **Near-miss logging (simplified):** Log stocks passing hard gates with composite_score ≥50
✅ **Low opportunity logging:** Flag when output <5 candidates

### **What We're SKIPPING (and Why)**

#### 1. Complete Hard/Soft Gate Restructure → DEFERRED
**Recommendation:** Restructure entire screener into 4 sections with centralized `qualifies_as_candidate()` function

**Why Skip:**
- **Too invasive** - Major refactoring during live trading is high-risk
- **Current structure works** - Code is well-organized and maintainable
- **Diminishing returns** - Targeted fixes solve 90% of the problem
- **Better timing** - Consider only if problems persist after targeted fixes

**Revisit IF:**
- Targeted fixes don't improve candidate counts to 10-30 in normal markets
- Code becomes unmaintainable due to complexity
- Major strategy change requires architectural overhaul

---

#### 2. Tier Quotas (Hard Caps per Tier) → SKIP
**Recommendation:** Hard caps like "Tier 1: max 15, Tier 2: max 15, Tier 4: max 10"

**Why Skip:**
- **Artificial constraints** - If 20 genuine Tier 1 earnings beats exist, why cap at 15?
- **Current TOP_N=40 works** - Global cap achieves output control without tier quotas
- **Quality over arbitrary limits** - Let natural quality determine tier distribution
- **Complexity without benefit** - Adds logic that might reject valid candidates arbitrarily

**Alternative Approach:**
- Keep global TOP_N cap (currently 40)
- Let scoring system naturally prioritize best candidates across all tiers
- Monitor tier distribution in daily logs (informational only)

**Revisit IF:**
- One tier consistently floods output (e.g., 38/40 are Tier 4 breakouts)
- Quality degrades because weak tiers crowd out strong tiers
- User explicitly requests tier balancing

---

#### 3. Widening Breakout Maintenance to 8% During Holidays → SKIP
**Recommendation:** Allow stocks 8% below 52-week high during holidays (vs. current 3%)

**Why Skip:**
- **Strategy drift** - 8% below high isn't a breakout, it's a pullback play
- **Momentum thesis breaks down** - Stocks 8% off highs have lost breakout energy
- **Defeats precision goal** - Loosening standards just to "get more names" is wrong approach
- **3-6% partial scoring sufficient** - Allows normal digestion without compromising thesis

**What We're Doing Instead:**
- Implementing 3-6% partial scoring (middle ground)
- Tier-aware freshness allows legitimate holiday setups to qualify
- Accept that 1-5 candidates on Dec 30 is CORRECT, not a bug

**Revisit IF:**
- After 2-3 months, data shows rejected 4-7% pullbacks outperform acceptances
- Consistently getting 0 candidates even in active markets
- Strategy evolves to include pullback entries (requires full thesis change)

---

#### 4. Complex Near-Miss Threshold Logic → SIMPLIFIED
**Recommendation:**
```
passed_universal_hard == True AND
(catalyst_score >= 8 OR news_scaled_score >= 25 OR tier in {1,2,4}) AND
len(rejection_reasons) <= 2
```

**Why Simplify:**
- **Over-engineered** - Too many conditions create edge cases and maintenance burden
- **Goal is transparency** - Want to see what almost qualified, not create another complex filter
- **Simpler is better** - Easier to audit, easier to understand

**What We're Doing Instead:**
```
passed_universal_hard_gates == True AND
composite_score >= 50
```

**Rationale:**
- Composite score already incorporates catalyst quality, RS, technical setup
- Score ≥50 means "had some merit but didn't make top 40"
- Simple rule, easy to audit, captures the learning signal we need

**Revisit IF:**
- Near-miss logs flood with obvious junk (threshold too low)
- Learning system can't extract signal from logs (need more granularity)
- User wants specific rejection reason analysis

---

#### 5. "Would Have Been Rank" Calculation → SKIP
**Recommendation:** Calculate hypothetical ranking for rejected stocks

**Why Skip:**
- **Computational waste** - Ranking stocks we're rejecting adds processing time
- **Not actionable** - Knowing rejected stock "would have been #12" doesn't inform decisions
- **False precision** - Implies rejected stocks are comparable to accepted ones (they're not)
- **Log scores instead** - Can manually compare if needed

**What We're Doing Instead:**
- Log actual composite_score for near-misses
- Log rejection_reasons for context
- If needed, can manually sort near-miss logs by score for analysis

**Revisit IF:**
- Learning system specifically needs ranking data for ML model training
- User requests percentile analysis of rejected stocks
- Building automated rule adjustment system (not planned)

---

### **Philosophy: Precision Over Recall**

**Auditor's Perspective:** "Maximize signal capture" - ensure we never miss a good trade

**Our Perspective:** "Precision over recall" - better to miss a few good trades than flood Claude with mediocre names

**Why We're Right:**
- Claude evaluates 40 candidates/day, selects top 5-10 with scorecard ≥60
- System goal: 65-70% win rate (proven via backtesting)
- Flooding with 100+ candidates degrades Claude's signal-to-noise ratio
- "1 stock on Dec 30" is CORRECT given holiday conditions + low institutional activity

**The Audit Confirms:**
- Screener quality improved from 5.x → 7.6/10
- Noise problem solved (148 junk names → 1 quality name)
- Slight overshoot on strictness (targeted fixes address this)
- Core logic is sound

---

### **Decision Criteria for Revisiting Skipped Items**

**Revisit Architectural Refactor IF:**
- After 30 trading days, candidate count averages <10/day in normal markets
- Code complexity makes maintenance difficult
- Multiple bugs emerge from interaction between layers

**Revisit Tier Quotas IF:**
- One tier consistently represents >75% of output
- Quality metrics show tier imbalance correlates with poor performance
- User explicitly requests tier balancing

**Revisit 8% Maintenance Window IF:**
- After 60 trading days, data shows 4-7% pullbacks from highs outperform
- Strategy explicitly evolves to include pullback entries
- Consistently getting 0-1 candidates in active markets

**Revisit Complex Near-Miss Logic IF:**
- Simple version floods logs with obvious junk
- Learning system can't extract actionable insights
- Automated rule tuning system implemented (requires granular data)

**Revisit "Would Have Been Rank" IF:**
- Building ML model that requires training data with rankings
- User specifically requests percentile analysis of rejections
- Pattern emerges where near-misses consistently outperform acceptances

---

### **Implementation Priority (Next Steps)**

**Phase 1: Targeted Fixes (This Week)**
1. Implement tier-aware freshness (72-96h for Tier 1)
2. Implement breakout maintenance soft scoring (3-6% partial)
3. Add simplified near-miss logging (hard gates passed + score ≥50)
4. Add low opportunity day logging (<5 candidates)

**Phase 2: Validation (2-4 Weeks)**
1. Monitor candidate counts in normal market conditions
2. Review near-miss logs for patterns
3. Validate win rates remain ≥65%
4. Assess whether skipped recommendations need reconsideration

**Phase 3: Iterate (As Needed)**
1. If problems persist → revisit architectural refactor
2. If tier imbalance emerges → revisit tier quotas
3. If too strict in active markets → revisit maintenance windows
4. If learning system needs more data → revisit complex near-miss logic

---

**Status:** Audit reviewed, targeted fixes prioritized, skipped items documented with rationale
**Next Step:** Implement Phase 1 targeted fixes to market_screener.py

---

## 🐛 CRITICAL BUGS IDENTIFIED - THIRD-PARTY LOGIC AUDIT
**Date Added:** December 30, 2025 (Post-Audit)
**Source:** Third-party LLM logic audit (follow-up to 7.6/10 audit)

### **Bug #1: 48-Hour Freshness Math Error (CRITICAL)**

**Issue:**
- Code: `hours_since_last_trade > 48` (rejects after 48 hours)
- Comment: "5 trading days old... allows 3-day weekends + 1 buffer"
- Reality: 48 hours = 2 calendar days, NOT 5 trading days

**Impact:**
- Monday after 3-day weekend: Friday 4pm → Monday 7am = 63 hours → **REJECTED**
- Dec 30 (after Christmas): Many stocks rejected due to holiday closure
- Primary cause of "1 stock" output on Dec 30

**Why This Is Wrong:**
- Not a design choice - it's a **math error** in comments vs implementation
- Rejects stocks with fresh catalysts due to calendar, not quality
- Conflicts with our precision-over-recall strategy (broken precision, not intentional filtering)

**Fix: Change 48h → 96h Everywhere**
```python
# BEFORE (BUGGY):
if hours_since_last_trade > 48:  # ❌ Rejects 3-day weekends
    return None

# AFTER (FIXED):
if hours_since_last_trade > 96:  # ✅ Allows 4 calendar days (covers 3-day weekend + buffer)
    return None
```

**Locations to Fix:**
1. `detect_gap_up()` - Line ~780
2. `check_volume_surge()` - Line ~1270
3. `detect_52week_high_breakout()` - Line ~1380
4. `check_technical_setup()` - Line ~1320

**Rationale for 96 Hours:**
- 96 hours = 4 calendar days
- Covers: Fri 4pm → Tue 4pm (3-day weekend + 1 day buffer)
- Holiday weeks: Wed close → Mon open (5 calendar days with 96h limit)
- Still maintains freshness discipline (<4 days old is fresh)

**Status:** ✅ IMPLEMENTING (not parking lot - this is a bug)

---

### **Bug #2: M&A Target Detection Too Strict (HIGH PRIORITY)**

**Issue:**
Current logic requires ALL of:
1. Headline contains "acquisition/merger/acquire"
2. AND `is_target == True` (requires "acquired by", "to be acquired", "buyout offer")
3. AND ticker in headline

**Misses Common Headlines:**
- "Company X to acquire Company Y" → `is_target = False` (no "acquired by" phrase)
- Even though Y is clearly the target, we reject it
- This is standard financial press format

**Impact:**
- Missing Tier 1 M&A catalysts (highest institutional value)
- Undermines our "institutional-grade detection" thesis
- May be rejecting 20-30% of M&A targets

**Fix: Enhanced Detection with Confidence Levels**
```python
def is_ma_target_enhanced(article, ticker):
    """
    Three-tier detection:
    1. EXPLICIT: "acquired by", "to be acquired" → High confidence
    2. INFERRED: Ticker in Polygon tickers list + M&A keywords + NOT acquirer → Medium confidence
    3. NO_EVIDENCE: Reject
    """

    text = (article.get('title', '') + ' ' + article.get('description', '')).lower()

    # TIER 1: Explicit target phrases (HIGH CONFIDENCE)
    target_phrases = ['acquired by', 'to be acquired', 'buyout offer',
                      'takeover target', 'acquisition target', 'being bought by',
                      'sold to', 'agreed to be acquired']
    if any(phrase in text for phrase in target_phrases):
        return True, 'EXPLICIT'

    # TIER 2: Inferred from Polygon metadata (MEDIUM CONFIDENCE)
    ma_keywords = ['acquire', 'acquisition', 'merger', 'buyout', 'takeover']
    acquirer_phrases = ['to acquire', 'will acquire', 'acquires', 'acquiring', 'buys', 'to buy']

    article_tickers = article.get('tickers', [])
    if ticker in article_tickers:
        if any(kw in text for kw in ma_keywords):
            # Safety check: Is this ticker the ACQUIRER?
            ticker_lower = ticker.lower()
            if any(f"{ticker_lower} {phrase}" in text for phrase in acquirer_phrases):
                return False, 'LIKELY_ACQUIRER'  # Reject - buying company (stock often drops)
            else:
                return True, 'INFERRED_TARGET'  # Accept - likely the target (premium paid)

    return False, 'NO_EVIDENCE'
```

**Why This Approach:**
- ✅ Captures more Tier 1 catalysts (institutional M&A deals)
- ✅ Maintains precision (rejects acquirer, requires ticker in article metadata)
- ✅ Uses Polygon structured data (more reliable than pure NLP)
- ✅ Logs confidence level for auditing

**Risk Mitigation:**
- Log `EXPLICIT` vs `INFERRED_TARGET` detections separately
- Monitor for false positives (buying acquirer by mistake)
- Can tighten if we see bad trades

**Status:** ✅ IMPLEMENTING (conservative enhancement, logged for monitoring)

---

### **Bug #3: Rejection Reason Logging (DIAGNOSTIC)**

**Issue:**
- Can't tell WHY stocks are rejected
- Hard to debug "1 stock" days
- Can't validate if freshness bug or M&A bug is the primary cause

**Fix: Add Rejection Counters**
```python
# Track rejection reasons during scan
rejection_reasons = {
    'freshness_stale': 0,      # hours_since_last_trade > 96
    'ma_target_gating': 0,     # M&A keyword but not target
    'no_catalyst': 0,          # No Tier 1/2/3/4 catalyst
    'price_too_low': 0,        # Price < $10
    'volume_too_low': 0,       # Dollar volume < $50M
    'negative_news': 0         # Lawsuit/dilution/downgrade
}

# At end of scan
print(f"\n📊 REJECTION ANALYSIS:")
print(f"   Freshness (>96h): {rejection_reasons['freshness_stale']}")
print(f"   M&A target gating: {rejection_reasons['ma_target_gating']}")
print(f"   No catalyst: {rejection_reasons['no_catalyst']}")
print(f"   Price filter: {rejection_reasons['price_too_low']}")
print(f"   Volume filter: {rejection_reasons['volume_too_low']}")
print(f"   Negative news: {rejection_reasons['negative_news']}")
```

**Status:** ✅ IMPLEMENTING (helps validate other fixes)

---

## 📋 COMPLETE FIX LIST (7 Total Fixes)

### **CRITICAL BUGS (Do First)**
1. ✅ Fix 48h → 96h freshness bug (4 locations)
2. ✅ Fix market breadth calculation (COMPLETED Dec 30)
3. ✅ Enhanced M&A target detection (conservative approach)

### **AUDIT RECOMMENDATIONS (Phase 1)**
4. ✅ Tier-aware freshness (72-96h for Tier 1, integrates with Bug #1 fix)
5. ✅ Breakout maintenance soft scoring (≤3% full, 3-6% partial, >6% reject)
6. ✅ Near-miss logging (passed hard gates + score ≥50)
7. ✅ Low opportunity logging (<5 candidates flag)

### **DIAGNOSTIC (Enables Validation)**
8. ✅ Rejection reason logging (validates bug fixes)

---

**Status:** Ready to implement all 7 fixes systematically
**Next Step:** Begin implementation with careful verification at each step
