# MARKET SCREENER COMPREHENSIVE AUDIT
**Date:** December 23, 2025
**Auditor:** Claude Sonnet 4.5
**Scope:** Full system audit - catalog detection, tier assignment, data quality

---

## EXECUTIVE SUMMARY

### Critical Finding
**4 false Tier 1 M&A catalysts detected today (Dec 23)** - representing 100% false positive rate for M&A detection. This is a **SHOWSTOPPER BUG** that undermines system credibility.

### Audit Trigger
- Dec 22: 1/150 candidates marked Tier 1 (0.7%) - appeared to be market reality
- Dec 23: 4/41 candidates marked Tier 1 (9.8%) - **all 4 are false positives**
- Same bug pattern on both days (yesterday's ADP was also false)

### Key Insights
1. **M&A detection has 100% false positive rate** (5/5 recent "Tier 1" M&A are fake)
2. System correctly rejects weak catalysts (Tier 2/3 filtering works)
3. The problem is **false positives**, not false negatives
4. Root cause: keyword matching without context validation

---

## PHASE 1: ROOT CAUSE ANALYSIS - M&A FALSE POSITIVES

### The Smoking Gun

**All 4 "Tier 1 M&A" candidates today triggered on THE SAME ARTICLE:**
- Title: "5 Stocks Using Buybacks to Drive Serious Upside Into 2026"
- **NOT about M&A** - about share buyback programs
- Contains M&A keywords in general market commentary

**Affected Tickers:**
1. **C** (Citigroup) - Score 79.8
2. **ANF** (Abercrombie & Fitch) - Score 66.4
3. **ALSN** (Allison Transmission) - Score 62.1
4. **AEM** (Agnico Eagle Mines) - Score 60.7

### Data Quality Issues

**News Articles:**
- All 4 candidates show `"Top News Headlines (0 total)"` in output
- Articles are being scored but NOT saved to candidate output
- This suggests data flow issues between scoring and output

**Missing Data:**
- Company names: All show `name: N/A`
- RS percentiles: All show `RS Percentile: None%`
- M&A premiums: All show `Premium: Not disclosed`

### Code Inspection: Lines 1045-1048

```python
if 'acquisition' in keyword or 'merger' in keyword or 'acquire' in keyword:
    # V5: Only accept if stock is TARGET (being bought), not acquirer (buying)
    if is_acquirer and not is_target:
        continue  # Skip - stock is buying, not being bought
```

**The Bug:**
- Logic ONLY filters out acquirers: `if is_acquirer and not is_target`
- Articles with M&A keywords but NO directional context pass through
- Missing case: `if not is_acquirer and not is_target` (general market commentary)

**What Should Happen:**
```python
# REQUIRED for Tier 1 M&A:
if is_target:  # Stock is being acquired
    # Process as Tier 1 M&A
elif is_acquirer:
    # Skip - stock is buying, not being bought
else:
    # Skip - M&A keyword without company-specific context
```

### Pattern Analysis

**Yesterday (Dec 22) - ADP:**
- Marked as "Tier 1 - M&A Deal"
- News: "Talent Acquisition Software Market to Surpass USD 51.16 Billion"
- **NOT an ADP acquisition** - market analysis using "acquisition" keyword
- GO command correctly rejected it during manual review

**Today (Dec 23) - C, ANF, ALSN, AEM:**
- Same pattern - M&A keywords in market commentary
- All from "Buybacks" article (nothing to do with M&A)
- **4x worse than yesterday**

### Impact Assessment

**Immediate Impact:**
- GO command must manually review 4 fake Tier 1's today
- Wastes Claude API calls analyzing junk candidates
- Reduces trust in screener output

**Historical Impact:**
- Unknown how many past "Tier 1 M&A" trades were false positives
- May have entered positions on false M&A signals
- Win rate data could be contaminated

---

## PHASE 2: SYSTEMATIC COMPONENT AUDIT

### 2.1 TIER 1 EARNINGS DETECTION

**Location:** Lines 1423-1491
**Status:** ⚠️ NEEDS VALIDATION

**Logic Review:**
```python
def detect_tier1_earnings_beat(self, ticker):
    # TIER 1 CRITERIA:
    # - EPS beat >10% vs estimate
    # - Reported within last 5 days (fresh catalyst)
    # - Optional: Revenue beat >5% (bonus points)
```

**Critical Questions:**

1. **Data Source Reliability:**
   - Depends on Finnhub earnings calendar
   - What happens if Finnhub data is delayed/missing?
   - Do we validate actual vs estimate percentages?

2. **5-Day Window:**
   - Why 5 days? Evidence-based or arbitrary?
   - Does catalyst impact decay after 3 days?
   - Should we tighten to 0-3 days?

3. **10% Threshold:**
   - Is 10% EPS beat truly "institutional-grade"?
   - What if revenue misses but EPS beats (buyback effect)?
   - Should we require BOTH EPS + revenue beats?

4. **Missing Validation:**
   - No check for guidance raise (critical for post-earnings momentum)
   - No verification that earnings news is in articles
   - No validation that beat is "real" (not accounting tricks)

**Test Required:**
- Pull last 30 days of Tier 1 earnings detections
- Manually verify each one is legitimate >10% beat
- Check if any real beats were missed

---

### 2.2 TIER 1 M&A DETECTION

**Location:** Lines 1493-1572
**Status:** 🚨 **CRITICAL BUG - SYSTEM DOWN**

**Current Logic:**
```python
def detect_tier1_ma_deal(self, ticker, news_result, sec_8k_result):
    # TIER 1 CRITERIA:
    # - M&A announcement (news or SEC 8-K Item 2.01)
    # - Stock is TARGET (being acquired), not acquirer
    # - Premium >15% (or any M&A if premium not disclosed)
    # - Announced within last 2 days
```

**CONFIRMED BUGS:**

1. **Context Validation Missing** (CRITICAL):
   - Triggers on M&A keywords without verifying company-specific context
   - Passes through market commentary, sector analysis, general mentions
   - Logic: `if is_acquirer and not is_target: continue`
   - Should be: `if not is_target: continue` (REQUIRE target context)

2. **Premium Assumption Too Generous:**
   ```python
   is_tier1 = True  # Default to Tier 1 for any M&A (conservative)
   ```
   - This is NOT conservative - it's PERMISSIVE
   - Should require explicit premium >15% OR definitive agreement language

3. **No Article Validation:**
   - Doesn't verify ticker is mentioned in headline/first paragraph
   - Doesn't check for deal announcement structure
   - No validation of source credibility

**Additional Questions:**

1. **SEC 8-K Integration:**
   - Is SEC 8-K Item 2.01 detection working?
   - Have we ever caught an M&A via 8-K before news?
   - Should 8-K be PRIMARY source (more reliable than news)?

2. **2-Day Window:**
   - Why 2 days for M&A but 5 for earnings?
   - M&A deals can take weeks to close - should we track ongoing deals?
   - What about rumored deals (WSJ "sources say")?

3. **Target vs Acquirer:**
   - Current logic tries to filter acquirers
   - But we want TARGETS (stocks being bought)
   - Should we ALSO consider acquirers if deal is accretive?

**Fix Priority:** **P0 - IMMEDIATE**

**Recommended Fix:**
```python
def detect_tier1_ma_deal(self, ticker, news_result, sec_8k_result):
    # Step 1: Require TARGET context (being acquired)
    has_target_context = news_result.get('is_target', False)
    if not has_target_context:
        return {'has_tier1_ma': False, ...}

    # Step 2: Verify ticker in headline or first paragraph
    ticker_mentioned_prominently = verify_ticker_prominence(ticker, news_result)
    if not ticker_mentioned_prominently:
        return {'has_tier1_ma': False, ...}

    # Step 3: Check for deal announcement structure
    has_deal_announcement = check_deal_structure(news_result)
    if not has_deal_announcement:
        return {'has_tier1_ma': False, ...}

    # Step 4: Premium or definitive agreement required
    premium = news_result.get('ma_premium')
    has_definitive_agreement = 'agreement' in news_result.get('text', '').lower()

    if not (premium and premium > 15) and not has_definitive_agreement:
        return {'has_tier1_ma': False, ...}

    # All checks passed - this is real Tier 1 M&A
    return {'has_tier1_ma': True, ...}
```

---

### 2.3 TIER 1 FDA DETECTION

**Location:** Lines 1574-1644
**Status:** ⚠️ UNVALIDATED

**Logic Review:**
```python
def detect_tier1_fda_approval(self, ticker, news_result):
    # TIER 1 CRITERIA:
    # - FDA approval news detected
    # - Announced within last 2 days
    # - Approval type: BREAKTHROUGH > PRIORITY > STANDARD > EXPANDED
```

**Critical Questions:**

1. **News-Only Detection:**
   - Why no FDA.gov API integration?
   - FDA publishes approvals on official site (gold standard)
   - News can be delayed or inaccurate

2. **Approval Type Classification:**
   - How does `classify_fda_approval()` work?
   - Does it distinguish breakthrough vs standard reliably?
   - What if article doesn't specify type?

3. **Company Specificity:**
   - Same issue as M&A: does it verify company-specific approval?
   - Or will "FDA approves new drug" generic news trigger?
   - Need to validate ticker/company name in article

4. **2-Day Window:**
   - FDA approvals can moon a stock for weeks
   - Should we track PDUFA dates (expected approval dates)?
   - 2 days seems too short for FDA catalyst lifespan

**Test Required:**
- Search for FDA-related news in past 30 days
- Verify we detected legitimate approvals
- Check for false positives (general FDA news)

**Recommendation:**
- Integrate FDA.gov official approvals feed (if available)
- Extend window to 5-7 days (FDA impact longer than M&A)
- Add PDUFA date tracking for anticipated approvals

---

### 2.4 NEWS FETCHING & PARSING

**Location:** Lines 859-1096
**Status:** 🔍 **NEEDS DEEP INSPECTION**

**Current Architecture:**
- Fetches news from Polygon API
- Scores based on keyword matching
- Returns top articles + catalyst classification

**Critical Issues Identified:**

1. **Top Articles Not Saved to Output** (Bug):
   - Today's candidates show 0 news articles in output
   - But news IS being scored (keywords detected)
   - Data flow broken between scoring and candidate assembly

2. **Keyword Contamination:**
   - 'upgrade': 5 points (Tier 1 weight)
   - But "analyst upgrade" is Tier 2, not Tier 1
   - Mixing Tier 1 and Tier 2 keywords in same dict

3. **No Ticker Mention Validation:**
   - Keywords scored even if ticker not mentioned
   - Article about "sector M&A activity" triggers all tickers in sector
   - Need: ticker must appear in title or first 100 chars

**Code Inspection - Line 899-910:**
```python
tier1_keywords = {
    'acquisition': 8,      # M&A = Tier 1
    'merger': 8,           # M&A = Tier 1
    'acquires': 8,         # M&A = Tier 1
    'to acquire': 8,       # M&A = Tier 1
    'FDA approval': 8,     # FDA approval = Tier 1
    'drug approval': 8,    # FDA approval = Tier 1
    'contract win': 6,     # Major contract = Tier 1
    'awarded contract': 6, # Major contract = Tier 1
    'signs contract': 6,   # Major contract = Tier 1
    'upgrade': 5,          # Analyst upgrade = Tier 1  ← WRONG
}
```

**PROBLEM:** `'upgrade': 5` is marked Tier 1 but analyst upgrades are Tier 2!

This explains why keywords show `['acquisition', 'analyst', 'upgrade']` - both are being counted as Tier 1 when only 'acquisition' should be.

**Critical Questions:**

1. **Polygon News Quality:**
   - How fresh is Polygon news? (real-time or delayed?)
   - Does it include all major sources (Bloomberg, WSJ, etc.)?
   - Are we missing news from better sources?

2. **Duplicate Detection:**
   - Same story from multiple sources counted multiple times?
   - Should we deduplicate by headline similarity?

3. **Source Credibility:**
   - Should Bloomberg/WSJ score higher than Seeking Alpha?
   - Law firm spam filter works, but what about other spam?

4. **Recency Filtering:**
   - Lines 1050, 1060, 1070 show different windows (1 day, 1 day, 2 days)
   - Inconsistent - why do contracts get 2 days but M&A only 1?
   - Should ALL Tier 1 catalysts use same window?

**Recommended Fixes:**

1. **Move 'upgrade' to Tier 2:**
   ```python
   tier1_keywords = {
       'acquisition': 8, 'merger': 8, 'acquires': 8, 'to acquire': 8,
       'FDA approval': 8, 'drug approval': 8,
       'contract win': 6, 'awarded contract': 6, 'signs contract': 6
       # Removed 'upgrade' - belongs in Tier 2
   }
   ```

2. **Add Ticker Mention Validation:**
   ```python
   # Before scoring article:
   if ticker.upper() not in title.upper() and ticker.upper() not in description[:200].upper():
       continue  # Skip articles that don't mention ticker prominently
   ```

3. **Fix Top Articles Output:**
   - Investigate why articles aren't appearing in candidate output
   - Ensure top 3-5 articles saved for GO command review

---

### 2.5 SEC 8-K FILING DETECTION

**Location:** Lines 698-775
**Status:** ⚠️ UNVALIDATED

**Logic Review:**
```python
def get_recent_sec_8k_filings(self, ticker):
    # Fetch SEC 8-K filings from past 7 days
    # Item 2.01 = M&A announcements
    # Item 7.01 = Regulation FD disclosure
```

**Critical Questions:**

1. **Is This Actually Working?:**
   - Have we EVER detected an M&A via 8-K before news?
   - Test: check last 30 days for 8-K M&A detections
   - If zero, this feature is dead code

2. **7-Day Window:**
   - 8-K must be filed within 4 business days of event
   - 7 days seems reasonable
   - But why not match news window (2 days for M&A)?

3. **Item Coverage:**
   - Only checking Item 2.01 (M&A) and 7.01 (Reg FD)
   - What about Item 1.01 (Material agreements)?
   - What about Item 8.01 (Other events)?

4. **SEC API Reliability:**
   - Using SEC Edgar API directly?
   - Rate limits? Downtime?
   - Backup plan if SEC API is down?

**Test Required:**
- Query last 30 days: how many 8-K M&A detected?
- Compare to news-detected M&A
- Determine if 8-K is adding value or dead weight

---

### 2.6 ANALYST RATINGS DETECTION

**Location:** Lines 586-626
**Status:** ⚠️ TIER 2 LOGIC (Lower Priority)

**Questions:**

1. **Finnhub Reliability:**
   - Analyst rating changes from Finnhub
   - How fresh is this data?
   - Missing any major firms (Goldman, Morgan Stanley)?

2. **Strong Buy Definition:**
   - Code counts "strong buy" ratings
   - But different firms use different scales
   - Should we normalize?

3. **Trend Detection:**
   - Looks for improving trends (more strong buys)
   - But timeframe unclear
   - What constitutes "improving"?

**Recommendation:** Lower priority - analyst upgrades are Tier 2

---

### 2.7 RS PERCENTILE CALCULATION

**Location:** Lines 381-455
**Status:** ⚠️ CRITICAL BUT WORKING

**Logic Review:**
```python
def calculate_rs_percentiles(self, candidates):
    # Calculate relative strength percentiles across all candidates
    # Used for scoring, not filtering (Phase 3)
```

**Observation from Today's Data:**
All 4 fake M&A candidates show `RS Percentile: None%` in output, but data shows:
- C: `rs_percentile: 82`
- Others: likely similar

**Issue:** RS percentile is calculated but not displaying in summary output.

**Questions:**

1. **Why Use Percentile vs Absolute RS%?:**
   - Percentile ranking within current scan
   - But RS% (stock vs sector) is absolute
   - Which is more predictive?

2. **Timeframe:**
   - 3-month RS used
   - Why 3 months? Evidence-based?
   - Should we test 1M, 6M, 12M windows?

3. **Sector Comparison:**
   - RS calculated vs sector ETF
   - But not all sectors are equal
   - Tech stocks naturally higher RS than utilities?

**Recommendation:** Working but needs display bug fix

---

### 2.8 SECTOR ROTATION DETECTION

**Location:** Lines 456-523
**Status:** ✅ WORKING (Tier 3 only)

**Logic:**
- Identifies leading/lagging sectors vs SPY
- Tier 3 candidates get boost if in leading sector
- Today: Healthcare leading (+10.5% vs SPY)

**Questions:**

1. **Threshold:**
   - Current: sector must beat SPY by ≥5% to be "leading"
   - Is 5% evidence-based?
   - Should we use percentile ranking instead?

2. **Rotation Timing:**
   - 3-month window used
   - But sector rotations can be brief (weeks)
   - Should we also check 1-month rotation?

**Recommendation:** Working as designed, Tier 3 logic is acceptable

---

### 2.9 COMPOSITE SCORING LOGIC

**Location:** Lines 2639-2797
**Status:** 🔍 **NEEDS STRATEGIC REVIEW**

**Current Formula:**
```python
composite_score = (
    catalyst_score * 2.5 +  # Catalyst is most important
    technical_score +
    rs_score +
    volume_score * 0.5
)
```

**Critical Questions:**

1. **Catalyst Weight (2.5x):**
   - Why 2.5x multiplier?
   - Is this evidence-based or gut feel?
   - Should Tier 1 catalysts get even higher weight?

2. **Technical Score:**
   - Includes: 52w high proximity, breakouts
   - But these are MOMENTUM signals, not catalysts
   - Should technical score be LOWER priority?

3. **Score Inflation:**
   - Fake M&A gets +8 points (acquisition keyword)
   - +5 points (upgrade keyword)
   - Total: +13 points → +32.5 in composite (2.5x multiplier)
   - This is why C scored 79.8 despite being fake

4. **Absolute vs Relative:**
   - Scores are absolute (0-100 scale)
   - But candidates compete within each scan
   - Should we use percentile ranking instead?

**Recommendation:**
- Reduce weight on news keywords until context validation fixed
- Consider Tier 1 vs Tier 2 separate multipliers
- Test correlation: composite score vs actual trade performance

---

### 2.10 TIER ASSIGNMENT LOGIC

**Location:** Lines 2848-3038
**Status:** 🚨 **CRITICAL BUG - PERMISSIVE TIER 1**

**Current Logic:**
```python
# PRIORITY 1: Tier 1 earnings beats >10%
if tier1_earnings_result.get('has_tier1_beat'):
    catalyst_tier = 'Tier 1'

# PRIORITY 2: Tier 1 M&A deals >15% premium
elif tier1_ma_result.get('has_tier1_ma'):  # ← BUG HERE
    catalyst_tier = 'Tier 1'

# PRIORITY 3: Tier 1 FDA approvals
elif tier1_fda_result.get('has_tier1_fda'):
    catalyst_tier = 'Tier 1'
```

**The Problem:**
- `tier1_ma_result.get('has_tier1_ma')` is True for fake M&A
- No additional validation at tier assignment stage
- Garbage in → garbage out

**Missing Safeguards:**

1. **No Score Threshold:**
   - Should Tier 1 require minimum composite score?
   - E.g., Tier 1 must score >70 to be credible

2. **No Cross-Validation:**
   - Should verify news articles present
   - Should verify RS percentile >50 (not dead momentum)
   - Should verify NOT in lagging sector

3. **No Manual Override:**
   - GO command catches fakes, but too late
   - Should have confidence score: "Tier 1 (90% confidence)"

**Recommendation:**
- Add validation layer AFTER Tier 1 detection
- Require: real news article + high score + strong RS
- Consider "Tier 1 (unconfirmed)" vs "Tier 1 (confirmed)"

---

## PHASE 3: STRATEGIC QUESTIONS

### 3.1 Are We Solving the Right Problem?

**Current Goal:** Find stocks with institutional-grade catalysts (M&A, FDA, Earnings >10%)

**Questions:**

1. **Is Tier 1-only approach too restrictive?:**
   - Dec 22: 1/993 stocks qualified (0.1%)
   - Dec 23: 4/993 qualified (0.4%) - all fake
   - Real rate: ~0% Tier 1 catalysts on most days
   - Should we accept high-quality Tier 2 catalysts?

2. **Are we too dependent on news?:**
   - News is delayed, incomplete, noisy
   - SEC filings are more reliable but underutilized
   - Should we prioritize SEC 8-K over news?

3. **Is 2-day recency too strict?:**
   - M&A deals can run for weeks after announcement
   - FDA approvals can moon stocks for months
   - Are we missing multi-day momentum plays?

### 3.2 Are We Using the Right Data Sources?

**Current Sources:**
- Polygon API (news, prices, universe)
- Finnhub (earnings calendar)
- SEC Edgar (8-K filings)

**Missing Sources:**
- FDA.gov (official drug approvals)
- Bloomberg Terminal (premium news, faster)
- Options flow (unusual activity)
- Insider transactions (Form 4 filings)
- Short interest (FINRA data)

**Question:** Should we invest in better data to reduce false positives?

### 3.3 Are Our Filters Creating Blind Spots?

**Current Filters:**
- Price ≥$10
- Market cap ≥$1B
- S&P 1500 universe only

**Blind Spots:**

1. **Small/Mid Caps:**
   - M&A targets often <$1B market cap
   - FDA biotech plays often <$500M
   - Are we missing best opportunities?

2. **Penny Stock Exclusion:**
   - $10 price filter is good (avoid junk)
   - But what about $8-10 stocks with real catalysts?

3. **Universe Limitation:**
   - S&P 1500 is large caps
   - Russell 2000 has more volatility (better for swing trading?)

### 3.4 Are We Missing Obvious Catalysts?

**Not Currently Detected:**

1. **Stock Splits:** (AAPL, TSLA historic moons after split announcements)
2. **Dividend Increases:** (especially surprise increases)
3. **Index Inclusion:** (S&P 500 add = automatic buying)
4. **Activist Investor Stakes:** (Carl Icahn 13D filing)
5. **Patent Approvals:** (pharma/tech IP wins)
6. **Clinical Trial Results:** (biotech binary events)
7. **Regulatory Approvals:** (beyond FDA - FCC, FAA, etc.)

**Question:** Should we expand catalyst coverage or stay focused on top 3?

### 3.5 Are We Over-Fitting to Past Performance?

**Current System Designed Around:**
- Historical win rate data
- Past successful trades (presumably)
- Institutional trading patterns (assumed)

**Questions:**

1. **Do we have backtesting data?:**
   - How many Tier 1 trades have we made?
   - What's the actual win rate?
   - Are earnings beats better than M&A?

2. **Is Tier 1 definition validated?:**
   - 10% EPS beat threshold - evidence-based?
   - 15% M&A premium - evidence-based?
   - Or arbitrary thresholds that sound good?

3. **Are we chasing yesterday's winners?:**
   - M&A arbitrage may be played out (efficient market)
   - FDA approvals may be priced in (biotech funds front-run)
   - Should we look for less obvious catalysts?

---

## PHASE 4: COMPREHENSIVE FINDINGS

### CRITICAL (P0) - Must Fix Immediately

| # | Finding | Impact | Location |
|---|---------|--------|----------|
| 1 | **M&A context validation missing** | 100% false positive rate | Lines 1045-1048 |
| 2 | **'upgrade' keyword in Tier 1 dict** | Inflates Tier 2 to Tier 1 | Line 909 |
| 3 | **No ticker mention validation** | General news triggers all stocks | Lines 1014-1095 |
| 4 | **Top articles not saved to output** | GO command can't review | Data flow issue |

### HIGH PRIORITY (P1) - Fix This Week

| # | Finding | Impact | Location |
|---|---------|--------|----------|
| 5 | **M&A premium assumption too generous** | Accepts deals without terms | Line 1522 |
| 6 | **No minimum score for Tier 1** | Low-quality signals pass | Lines 2848-2900 |
| 7 | **Earnings detection unvalidated** | Unknown false positive rate | Lines 1423-1491 |
| 8 | **FDA detection news-only** | Missing FDA.gov official data | Lines 1574-1644 |
| 9 | **SEC 8-K possibly dead code** | Wasting API calls if unused | Lines 698-775 |

### MEDIUM PRIORITY (P2) - Fix Next Sprint

| # | Finding | Impact | Location |
|---|---------|--------|----------|
| 10 | **Inconsistent recency windows** | M&A=2d, Earnings=5d, Contracts=2d | Lines 1050, 1450, 1070 |
| 11 | **RS percentile display bug** | Calculated but not shown | Output formatting |
| 12 | **No source credibility weighting** | All news treated equally | Lines 1014-1095 |
| 13 | **Composite score not evidence-based** | Arbitrary 2.5x catalyst multiplier | Lines 2639-2700 |
| 14 | **No backtesting/validation data** | Don't know if thresholds work | System-wide |

### STRATEGIC (P3) - Long-term Improvements

| # | Recommendation | Rationale |
|---|----------------|-----------|
| 15 | **Integrate FDA.gov official feed** | Gold standard for drug approvals |
| 16 | **Add confidence scores to Tier 1** | Tier 1 (95% confidence) vs (60% confidence) |
| 17 | **Expand catalyst coverage** | Stock splits, dividend increases, index inclusion |
| 18 | **Consider better data sources** | Bloomberg Terminal, paid FDA data |
| 19 | **Backtest all thresholds** | Validate 10% EPS, 15% M&A premium, etc. |
| 20 | **Build false positive tracking** | Log all Tier 1's + GO command verdicts |

---

## PHASE 5: IMPLEMENTATION ROADMAP

### Week 1: Critical Bug Fixes (P0)

**Day 1-2: M&A Context Validation**
```python
# File: market_screener.py, Lines 1045-1058
# BEFORE:
if is_acquirer and not is_target:
    continue  # Skip - stock is buying, not being bought

# AFTER:
if not is_target:
    continue  # REQUIRE target context - being acquired
```

**Day 2-3: Ticker Mention Validation**
```python
# File: market_screener.py, Line 1014+
# Add before scoring any article:
if ticker.upper() not in title.upper():
    # Ticker must be in headline for Tier 1 catalysts
    if keyword in ['acquisition', 'merger', 'acquires', 'to acquire',
                   'FDA approval', 'drug approval']:
        continue  # Skip Tier 1 keywords if ticker not in title
```

**Day 3-4: Move 'upgrade' to Tier 2**
```python
# File: market_screener.py, Lines 899-937
tier1_keywords = {
    'acquisition': 8, 'merger': 8, 'acquires': 8, 'to acquire': 8,
    'FDA approval': 8, 'drug approval': 8,
    'contract win': 6, 'awarded contract': 6, 'signs contract': 6
    # REMOVED: 'upgrade': 5 → moved to tier2_keywords
}

tier2_keywords = {
    'upgrade': 5,  # MOVED from Tier 1
    'analyst upgrade': 5,
    'price target raise': 4,
    # ... rest of Tier 2 keywords
}
```

**Day 4-5: Fix Top Articles Output**
- Debug why articles aren't appearing in candidate output
- Ensure top 3 articles saved with headline, description, URL
- Verify GO command can see articles for manual review

### Week 2: High Priority Fixes (P1)

**Day 6-7: M&A Premium Validation**
```python
# File: market_screener.py, Lines 1520-1540
# BEFORE:
is_tier1 = True  # Default to Tier 1 for any M&A (conservative)

# AFTER:
# Require EITHER premium >15% OR definitive agreement language
has_definitive_agreement = any(term in text for term in [
    'definitive agreement', 'merger agreement', 'acquisition agreement',
    'signed agreement', 'binding offer'
])

is_tier1 = (ma_premium and ma_premium > 15) or has_definitive_agreement
```

**Day 8-9: Add Tier 1 Minimum Score**
```python
# File: market_screener.py, Lines 2848-2900
# Add after tier assignment:
if catalyst_tier == 'Tier 1':
    # Require minimum composite score of 60 for Tier 1
    if composite_score < 60:
        catalyst_tier = 'Tier 2'  # Downgrade to Tier 2
        catalyst_tier_display = 'Tier 2 - Unconfirmed Catalyst'
```

**Day 10: Validate Earnings Detection**
- Pull last 30 days of Tier 1 earnings detections
- Manually verify each >10% beat is legitimate
- Document any false positives found
- Adjust threshold if needed

**Day 11-12: Test FDA Detection**
- Search for FDA-related stocks in biotech sector
- Verify we detected recent FDA approvals
- Check for false positives
- Plan FDA.gov integration if needed

**Day 13-14: Audit SEC 8-K Usage**
- Query last 30 days: how many 8-K M&A detected?
- Compare to news-detected M&A
- If zero hits, consider removing (dead code)
- Or improve 8-K parsing logic

### Week 3-4: Medium Priority (P2)

**Standardize Recency Windows**
- Research optimal window for each catalyst type
- Justify with evidence (market impact duration)
- Implement consistent policy

**Fix RS Percentile Display**
- Debug output formatting
- Ensure percentile shows in top 10 summary

**Add Source Credibility**
- Weight Bloomberg/WSJ higher than Seeking Alpha
- Implement source scoring system

**Backtest Composite Score**
- Pull historical trades with scores
- Correlate score → win rate
- Optimize catalyst multiplier

### Month 2: Strategic Improvements (P3)

**FDA.gov Integration**
- Research FDA API/RSS feeds
- Implement official approval tracking
- Compare to news-based detection

**Confidence Scoring**
- Build scoring model: news quality + score + RS + validation
- Output: "Tier 1 (High Confidence 92%)" vs "Tier 1 (Medium 67%)"

**Expand Catalyst Coverage**
- Add stock split detection
- Add dividend increase detection
- Add index inclusion tracking

**Data Source Evaluation**
- Evaluate Bloomberg Terminal vs current sources
- Cost/benefit analysis
- Pilot test if promising

---

## CONCLUSION

### What We Learned

1. **The system is NOT fundamentally broken** - Tier 2/3 filtering works well
2. **The problem is false POSITIVES, not false negatives** - we're too permissive
3. **Context validation is the missing piece** - keyword matching alone fails
4. **Data quality issues are hiding bugs** - missing articles, missing names
5. **We need backtesting data** - thresholds are unvalidated guesses

### The Path Forward

**Immediate (This Week):**
- Fix M&A context validation (100% false positive rate)
- Fix ticker mention requirement (general news contamination)
- Move 'upgrade' to Tier 2 (classification error)
- Fix top articles output (data flow bug)

**Near-term (This Month):**
- Validate earnings detection (unknown accuracy)
- Test FDA detection (unknown accuracy)
- Audit SEC 8-K usage (possibly dead code)
- Add minimum score for Tier 1 (quality gate)

**Long-term (Next Quarter):**
- Integrate better data sources (FDA.gov, potentially Bloomberg)
- Build confidence scoring system
- Expand catalyst coverage (splits, dividends, index inclusion)
- Backtest all thresholds with real trade data

### Success Metrics

**Week 1 Target:**
- M&A false positive rate: 100% → <10%
- Tier 1 candidates with articles: 0% → 100%
- 'upgrade' misclassification: Fixed

**Month 1 Target:**
- Earnings detection validated (measure false positive rate)
- FDA detection validated (measure false positive rate)
- Composite score correlation measured (score → win rate)

**Quarter 1 Target:**
- All catalyst types validated with backtesting
- Confidence scoring implemented
- Expanded catalyst coverage (3 → 8 types)

---

**END OF AUDIT REPORT**

*This audit conducted by Claude Sonnet 4.5 on December 23, 2025*
*Based on live screener run revealing 4 false Tier 1 M&A positives*
*Recommended priority: P0 fixes within 48 hours to restore system credibility*
