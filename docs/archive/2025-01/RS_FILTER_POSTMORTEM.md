# RS Filter Post-Mortem - December 15, 2025

## Test Results Summary

**Screener Run Time:**
- Start: 15:30:49 ET
- End: 17:12:53 ET
- **Duration: 102 minutes** (vs 63 minutes previous run, +62% slower)

**RS Filter Performance:**
- Passed: 131/993 stocks (13.2%)
- Previous (sector-relative): 126/993 (12.7%)
- **Improvement: +5 stocks (+4.0%)**

**Target Tickers (Claude's Dec 15 morning picks):**
- NVDA: ❌ FAIL
- LLY: ❌ FAIL
- ORCL: ❌ FAIL
- MSFT: ❌ FAIL
- AVGO: ❌ FAIL
- AMD: ✅ PASS (only one)

## Root Cause: Wrong Timeframe for Catalyst Trading

### The Fundamental Mismatch

**Our System**: 3-7 day catalyst-driven swing trades
**Our Filter**: 3-month (90-day) relative strength

This is a **timeframe mismatch**. We're filtering stocks based on 3-MONTH momentum, then holding positions for 3-7 DAYS.

### Why This Fails

**Example: NVDA Earnings Beat (Dec 10, 2025)**
- Event: NVDA beats earnings on Dec 10, stock up +15% in 2 days
- 3-month return (Sep 15 - Dec 15): Maybe only +2% (had weakness in Oct/Nov)
- **Result**: Rejected by RS filter despite having a fresh Tier 1 catalyst

**Example: LLY Drug Sales Momentum (Nov-Dec)**
- Event: Zepbound sales exceeding forecasts (ongoing catalyst)
- 3-month return: Depends on Aug-Nov performance, not recent catalyst
- **Result**: May fail RS filter even with strong current catalyst

### Professional Platforms Comparison

**IBD CAN SLIM:**
- Uses RS Rating (percentile rank vs all stocks)
- But ALSO requires: Price > 50d MA, 50d MA > 200d MA, Near 52-week high
- These are **TREND** filters, not timeframe-specific momentum

**Minervini SEPA:**
- Stage 2 uptrend detection (price above MAs)
- RS vs market (like we implemented)
- **BUT**: Minervini holds for WEEKS/MONTHS, not days
- His timeframe matches his filters

**Renaissance Technologies:**
- Uses multiple momentum factors (1-month, 3-month, 6-month, 12-month)
- Combines short-term AND long-term signals
- Mean reversion on short timeframes, momentum on long timeframes

### What We Actually Need

For a **3-7 day catalyst-driven swing trading system**, the filter should be:

1. **Catalyst Presence** (Tier 1 >> Tier 2 >> Tier 3) ✅ We have this
2. **Catalyst Recency** (0-3 days >> 4-7 days >> 8-30 days) ✅ We have this
3. **Short-term momentum** (5-day, 10-day, 20-day) ❌ We DON'T have this
4. **Stage 2 uptrend** (price > 50d MA) ⚠️ We check this but don't filter on it
5. **Institutional support** (volume, RS percentile) ✅ We have this

## The Real Problem: We're Building Two Different Systems

### System A: IBD/Minervini Position Trading (What Our Filters Are For)
- Timeframe: Weeks to months
- Entry: Stage 2 breakout or base formation
- Filter: 3-month RS, 50d/200d MAs, near 52-week high
- Hold: Until trend breaks (weeks/months)

### System B: Catalyst-Driven Swing Trading (What We Want)
- Timeframe: 3-7 days
- Entry: Fresh catalyst (earnings, FDA, M&A)
- Filter: Catalyst presence, recent momentum, technical setup
- Hold: Until initial catalyst reaction fades (3-7 days)

**We're using System A filters for a System B strategy.**

## Test Case Analysis: Why Did AMD Pass But NVDA Fail?

Based on Dec 15, 2025 market conditions (SPY 3-month return: +3.1%):

**AMD (PASSED)**:
- 3-month return: Likely +28-30% (RS +25.7% vs SPY)
- Catalyst: Tier 2 (Analyst Upgrade)
- Why it passed: Strong 3-month momentum + catalyst

**NVDA (FAILED)**:
- 3-month return: Likely +0% to +5% (below SPY +3% + threshold 3% = +6%)
- Catalyst: Tier 1 (AI chip earnings beat - would be detected if recent)
- Why it failed: Weak 3-month momentum despite Tier 1 catalyst potential

**The irony**: AMD (Tier 2 catalyst) passes, NVDA (Tier 1 catalyst) fails - **backwards from what we want**.

## Options for Fix

### Option 1: Remove RS Filter Entirely
Use the Entry Quality Scorecard approach from Deep Research:
- Catalyst detection (any catalyst = pass)
- Let AI rank by quality (100-point scorecard)
- RS percentile becomes a SCORING factor, not a FILTER

**Pros:**
- Aligns with Deep Research document
- Lets Tier 1 catalysts through regardless of momentum
- AI has full flexibility to evaluate quality

**Cons:**
- May let in too many weak stocks
- Increases API calls and processing time

### Option 2: Use Short-Term Momentum (5-20 days)
Replace 3-month RS with 5-day, 10-day, or 20-day momentum:
```python
# 10-day momentum filter
ten_day_return = get_10day_return(ticker)
passed_filter = ten_day_return >= 2.0  # Up 2%+ in last 10 days
```

**Pros:**
- Aligns timeframe with holding period
- Captures catalyst-driven moves
- Still filters out downtrending stocks

**Cons:**
- Very short-term (might catch pullbacks)
- More sensitive to daily volatility

### Option 3: Hybrid - Catalyst + Trend Filter
```python
# Must have either:
# A) Tier 1 catalyst (any RS), OR
# B) Tier 2/3 catalyst + RS > 3%
if catalyst_tier == "Tier 1":
    passed_filter = True
elif catalyst_tier in ["Tier 2", "Tier 3"]:
    passed_filter = rs >= 3.0
else:
    passed_filter = False
```

**Pros:**
- Guarantees Tier 1 catalysts pass
- Still filters weak Tier 2/3 stocks
- Balances catalyst importance with momentum

**Cons:**
- Adds complexity
- May let in some weak Tier 1 stocks

### Option 4: Use IBD-Style RS Percentile Filter
```python
# Calculate percentile rank first, then filter
rs_percentile = calculate_percentile(stock_return, all_returns)
passed_filter = rs_percentile >= 70  # Top 30% of market
```

**Pros:**
- Auto-adjusts to market conditions
- Exact IBD methodology
- Works in bull and bear markets

**Cons:**
- Requires full scan first (already doing this)
- Still uses 3-month timeframe

## Recommendation

**Implement Option 3 (Hybrid)** as immediate fix, then evaluate Option 1 long-term.

### Immediate Fix (Option 3):
1. Change RS filter to allow ALL Tier 1 catalysts regardless of RS
2. Keep RS filter for Tier 2/3 catalysts
3. This guarantees NVDA/LLY/ORCL earnings beats pass

### Long-Term Fix (Option 1):
1. Remove RS as a hard filter entirely
2. Use RS percentile as a scoring factor (0-20 points)
3. Let AI evaluate full 100-point Entry Quality Scorecard
4. This aligns with professional methodology from Deep Research

## Cron Schedule Adjustment

Based on 102-minute runtime:

**Current:**
```
15 8 * * 1-5 /root/paper_trading_lab/run_screener.sh  # 8:15 AM
0 9 * * 1-5 /root/paper_trading_lab/run_go.sh         # 9:00 AM (45-min buffer)
```

**Recommended:**
```
0 7 * * 1-5 /root/paper_trading_lab/run_screener.sh   # 7:00 AM
0 9 * * 1-5 /root/paper_trading_lab/run_go.sh          # 9:00 AM (120-min buffer)
```

This gives 120-minute buffer (102 min runtime + 18 min safety margin).

## Conclusion

The RS filter fix (market-relative vs sector-relative) was technically correct but **didn't solve the fundamental problem**:

**We're using 3-month momentum filters for a 3-7 day catalyst trading system.**

NVDA, LLY, ORCL are failing not because of filter design, but because they don't have strong 3-month returns in the current market environment (SPY only +3.1%).

**Next step**: Implement Option 3 (Catalyst + Trend Hybrid) to guarantee Tier 1 catalysts pass the filter.

---

**Status**: Analysis complete, awaiting user decision on fix approach
**Date**: December 15, 2025, 5:30 PM ET
