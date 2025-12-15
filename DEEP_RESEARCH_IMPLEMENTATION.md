# Deep Research Implementation Summary - December 15, 2025

## Executive Summary

We've aligned the Tedbot screener to the **Entry Quality Scorecard methodology** from the Deep Research document. This is a fundamental architectural shift from "filter then score" to "score then rank" - aligning with best-in-class swing trading systems.

## The Problem We Solved

### Original System (BROKEN)
```
Hard Filters:
- Price >$5
- Market cap >$1B
- RS ≥3% (vs sector OR market) ← WRONG

Result: NVDA/LLY/ORCL filtered out despite Tier 1 catalysts
```

### Root Cause Analysis
We discovered **TWO separate issues**:

1. **Sector-Relative RS** (Dec 15 morning): When tech sector was strong (+48%), even NVDA (+50%) only had +2% RS vs XLK → FAILED filter
2. **Market-Relative RS** (Dec 15 afternoon): SPY only +3.1% over 3 months; stocks need +6%+ (SPY +3% + threshold +3%) to pass → Still FAILED

The fundamental problem: **We were using 3-MONTH momentum filters for a 3-7 DAY swing trading system.**

## The Solution: Deep Research Alignment

### New System (BEST-IN-CLASS)
```
Hard Filters (GO/NO-GO):
✅ Price >$10 (Deep Research spec)
✅ Liquidity >$50M daily volume (Deep Research spec)
✅ Catalyst presence (any Tier 1 or Tier 2)

Scoring Factors (0-100 points):
✅ RS (0-5 pts) - Technical Setup component
✅ Catalyst quality (0-30 pts)
✅ Technical setup (0-25 pts)
✅ Sector/market context (0-20 pts)
✅ Historical patterns (0-15 pts)
✅ Conviction/risk (0-10 pts)
```

### Deep Research Validation (Line 84-85)

> "AI implementation best practices recommend **hybrid approach with AI as decision assist rather than autonomous agent**: **rule-based filters for minimum liquidity (>$50M daily volume), price (>$10), and catalyst presence eliminate low-quality opportunities, then AI analyzes sentiment, evaluates catalyst magnitude, and ranks remaining candidates.**"

This is EXACTLY what we now do.

## Changes Implemented

### 1. Removed RS as Hard Filter
**Before:**
```python
MIN_RS_PCT = 3.0  # Minimum relative strength
if not rs_result['passed_filter']:
    return None  # REJECT
```

**After:**
```python
MIN_RS_PCT = None  # RS now scoring only
'passed_filter': True,  # ALWAYS PASS
```

### 2. RS as Scoring Factor (Entry Quality Scorecard)
**Deep Research Technical Setup - Relative Strength (0-5 points):**
```python
if rs > 5.0:
    rs_score_points = 5      # Excellent momentum
elif rs >= 3.0:
    rs_score_points = 3      # Good momentum
elif rs >= 1.0:
    rs_score_points = 2      # Modest momentum
else:
    rs_score_points = 0      # Weak momentum
```

### 3. Raised Price Minimum
```python
MIN_PRICE = 5.0  →  10.0  # Deep Research: >$10
```

### 4. Raised Liquidity Minimum
```python
MIN_DOLLAR_VOLUME = 20_000_000  →  50_000_000  # Deep Research: >$50M
```

### 5. Catalyst Presence Required
```python
# DEEP RESEARCH CATALYST FILTER:
# Hard filter: Catalyst presence required (any tier)
has_any_catalyst = has_tier1_catalyst or has_tier2_catalyst

if not has_any_catalyst:
    return None  # REJECT: No catalyst detected
```

## Expected Impact

### Screening Results
- **Before**: 126-131 stocks passed (with RS filter rejecting Tier 1 catalysts)
- **After**: Est. 300-500 stocks pass (catalyst presence + liquidity/price minimums)
- **Tier 1 Representation**: Should jump from 1.6% to 30-40% of output

### Target Tickers (Claude's Dec 15 Picks)
| Ticker | Catalyst | Before | After |
|--------|----------|--------|-------|
| NVDA | AI chip earnings | ❌ Weak 3M RS | ✅ Has catalyst |
| LLY | Zepbound sales | ❌ Weak 3M RS | ✅ Has catalyst |
| ORCL | Cloud growth | ❌ Weak 3M RS | ✅ Has catalyst |
| MSFT | Azure AI | ❌ Weak 3M RS | ✅ Has catalyst |
| AVGO | AI chip momentum | ❌ Weak 3M RS | ✅ Has catalyst |
| AMD | Analyst upgrade | ✅ Pass | ✅ Pass |

### Win Rate & Gain Targets

**Deep Research scorecard thresholds** (Line 101):
- 80-100 points: 70-75% win rate
- 60-79 points: 60-70% win rate
- 40-59 points: 50-60% win rate

By letting AI evaluate the full 100-point scorecard (instead of pre-filtering with RS), we enable:
1. **Better stock selection** - Tier 1 catalysts aren't filtered out
2. **Conviction-based sizing** - Score/100 multiplier on position size
3. **Systematic improvement** - Track scorecard accuracy over time

## Workflow Changes

### Old Workflow
```
Screener (8:15 AM):
1. Hard filters: Price, MCap, RS ≥3%
2. Calculate composite score
3. Output top 50 (later 150)

GO Command (9:00 AM):
4. AI evaluates ~150 candidates
5. Most already pre-filtered by RS
6. Tier 1 catalysts missing
```

### New Workflow (Deep Research Aligned)
```
Screener (7:00 AM - earlier start for longer runtime):
1. Hard filters: Price >$10, Liquidity >$50M, Catalyst presence
2. Calculate RS as scoring factor (0-5 pts)
3. Calculate other scorecard components
4. Output ~300-500 catalyst stocks

GO Command (9:00 AM):
5. AI evaluates 100-point Entry Quality Scorecard
6. Ranks by total score (80-100 = best)
7. Selects top opportunities with conviction sizing
```

## Cron Schedule Update Needed

Based on 102-minute runtime from previous test:

**Current:**
```cron
15 8 * * 1-5 /root/paper_trading_lab/run_screener.sh  # 8:15 AM
0 9 * * 1-5 /root/paper_trading_lab/run_go.sh         # 9:00 AM
```

**Recommended:**
```cron
0 7 * * 1-5 /root/paper_trading_lab/run_screener.sh   # 7:00 AM (120-min buffer)
0 9 * * 1-5 /root/paper_trading_lab/run_go.sh          # 9:00 AM
```

Rationale:
- 102 minutes observed runtime (15:30-17:12)
- +18 minutes safety margin = 120 minutes total buffer
- More candidates (300-500 vs 150) may take longer
- Better to complete early than run late

## Technical Architecture

### Entry Quality Scorecard Components

**1. Catalyst Quality (0-30 points)**
- Earnings surprise magnitude: 3-12 pts
- Revenue performance: 2-8 pts
- Catalyst freshness: 0-5 pts
- Secondary catalysts: +5 pts bonus

**2. Technical Setup (0-25 points)**
- Trend alignment: 0-7 pts
- **Relative strength: 0-5 pts** ← NOW SCORING, NOT FILTERING
- Volume confirmation: 0-5 pts
- Price action setup: 0-5 pts
- Technical structure: 0-3 pts

**3. Sector and Market Context (0-20 points)**
- Sector strength: -2 to +4 pts
- Market regime: 0-5 pts
- Diversification: -2 to +4 pts
- Event timing: -5 to +2 pts

**4. Historical Pattern Match (0-15 points)**
- Catalyst quality: 0-4 pts
- Sector positioning: 0-2 pts
- Gap/technical: -1 to +3 pts
- Timing factors: 0-2 pts
- Seasonality: 0-2 pts
- Volume confirmation: -1 to +2 pts

**5. Conviction and Risk (0-10 points)**
- Entry conviction: 0-6 pts
- Risk adjustment: -2 to +4 pts

### Position Sizing Integration

```python
# Deep Research methodology
base_allocation = 10%  # Standard
conviction_multiplier = total_score / 100  # 0.80-1.00 for top setups
volatility_adjustment = calculate_atr_adjustment()  # 0.7-1.0x
market_regime = get_vix_adjustment()  # 0.7-1.1x

final_size = base_allocation × conviction × volatility × regime
```

Example:
- Total Score: 85 (exceptional setup)
- Conviction: 0.85
- Normal volatility: 1.0x
- VIX <20: 1.1x
- **Final Size: 10% × 0.85 × 1.0 × 1.1 = 9.35%**

## Files Modified

### market_screener.py
**Lines Changed:**
- 48-56: Screening parameters (MIN_RS_PCT, MIN_PRICE, MIN_DAILY_VOLUME_USD)
- 577-605: RS calculation (scoring only, always pass filter)
- 1868-1869: Removed RS hard filter check
- 1897-1904: Added catalyst presence requirement
- 1911-1921: Updated liquidity filter to $50M

**Key Functions:**
- `calculate_relative_strength()`: Returns `passed_filter=True` always, adds `rs_score_points`
- `screen_stock()`: No longer rejects based on RS, requires catalyst presence

## Testing Status

**Current Test**: Running screener with Deep Research filters (started 17:59 ET)

**Expected Results**:
- ✅ More stocks pass initial screening (300-500 vs 126-131)
- ✅ NVDA/LLY/ORCL included if they have detectable catalysts
- ✅ Tier 1 representation increases dramatically
- ✅ AI gets better candidate pool for 100-point evaluation

**Validation Criteria**:
1. Target tickers present in output (if catalysts detected)
2. Tier distribution: ~30-40% Tier 1, ~30% Tier 2, ~30% Tier 3
3. No "No Catalyst" stocks in output (hard filter prevents this)
4. RS range includes negative values (no longer filtered)

## Next Steps

1. ✅ Monitor current screener test completion
2. ⏳ Verify NVDA/LLY/ORCL appear in output
3. ⏳ Analyze tier distribution vs previous runs
4. ⏳ Update cron schedule (7:00 AM screener, 9:00 AM GO)
5. ⏳ Run GO command with new candidate pool
6. ⏳ Monitor first live trading day with new filters

## Success Metrics

### Short-term (1 week)
- [ ] NVDA/LLY/ORCL pass screening when catalysts present
- [ ] Tier 1 stocks: >30% of output (was 1.6%)
- [ ] Portfolio fills with 3-5 positions daily
- [ ] Win rate: >50% (establishing baseline)

### Medium-term (1 month)
- [ ] Win rate: 60%+ (Deep Research target)
- [ ] Avg gain per winner: 5-10% (3-7 day holds)
- [ ] Portfolio diversification: 5-8 positions
- [ ] No "zero trades" weeks

### Long-term (3 months)
- [ ] Win rate: 65-70% (Deep Research exceptional setups)
- [ ] Monthly returns: +8-12% (academic PEAD research)
- [ ] Max drawdown: <15%
- [ ] Sharpe ratio: >1.5

## References

1. **Deep Research Document**: [Claude_Deep_Research.md](./Claude_Deep_Research.md)
   - Line 84-85: Hard filters specification
   - Line 91-101: Entry Quality Scorecard
   - Line 109: Technical filters minimum requirements

2. **Diagnostic Reports**:
   - [DIAGNOSTIC_REPORT_DEC15.md](./DIAGNOSTIC_REPORT_DEC15.md)
   - [RS_FILTER_DIAGNOSIS.md](./RS_FILTER_DIAGNOSIS.md)
   - [RS_FILTER_POSTMORTEM.md](./RS_FILTER_POSTMORTEM.md)

3. **Academic Foundation**:
   - Bernard & Thomas: Post-Earnings Announcement Drift
   - Moskowitz & Grinblatt: Industry Momentum
   - Moreira & Muir: Volatility-Managed Portfolios

---

**Status**: Deep Research implementation complete, test in progress
**Date**: December 15, 2025, 6:15 PM ET
**Commit**: f8b6cd7 "Align screener to Deep Research - RS scoring not filtering"
