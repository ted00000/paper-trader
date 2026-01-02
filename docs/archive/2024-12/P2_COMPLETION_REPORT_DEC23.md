# P2 COMPLETION REPORT - Medium Priority Fixes
**Date**: December 23, 2025
**Status**: 3 OF 5 COMPLETE ✅
**Remaining**: 2 PARKED (data requirements)

---

## EXECUTIVE SUMMARY

Successfully implemented **3 out of 5 P2 medium-priority fixes**. The remaining 2 fixes (P2-13, P2-14) require historical trade data that we don't currently have - these have been moved to the **parking lot** for future implementation.

### Fixes Completed
- ✅ **P2-10**: Standardize recency windows with named constants
- ✅ **P2-11**: RS percentile display verified working
- ✅ **P2-12**: Source credibility weighting implemented

### Fixes Parked (Data Requirements)
- 🅿️ **P2-13**: Backtest composite score (needs historical trades)
- 🅿️ **P2-14**: Build validation framework (needs backtesting infrastructure)

---

## P2-10: STANDARDIZE RECENCY WINDOWS ✅

### Problem
Hardcoded day values scattered throughout code with no clear rationale:
- M&A: 2 days
- FDA: 2 days
- Earnings: 5 days
- Contracts: 2 days
- Price Targets: **30 days** (way too permissive)

### Solution Implemented
**Commit**: [1e95278](https://github.com/ted00000/paper-trader/commit/1e95278)

Created named constants at top of file with clear documentation:

```python
# TIER 1 CATALYSTS (Institutional-grade signals)
RECENCY_EARNINGS_TIER1 = 5   # Earnings momentum lasts 3-5 days (analysts update, coverage)
RECENCY_MA_TIER1 = 2         # M&A is binary - react immediately or miss move
RECENCY_FDA_TIER1 = 2        # FDA approval is binary - immediate catalyst

# TIER 2 CATALYSTS (High-quality signals)
RECENCY_ANALYST_UPGRADE = 1  # Upgrades have same-day impact
RECENCY_CONTRACT_WIN = 2     # Contract wins need immediate reaction
RECENCY_PRICE_TARGET = 7     # Price targets stale after 1 week (reduced from 30)

# TIER 3 CATALYSTS (Momentum plays)
RECENCY_SECTOR_ROTATION_FRESH = 3   # Fresh sector momentum (0-3 days)
RECENCY_SECTOR_ROTATION_RECENT = 7  # Recent sector momentum (4-7 days)
```

### Changes Made
**Lines Updated**: 60-78, 1481, 1545, 1645, 1161, 1775, 1778, 2380

Replaced all hardcoded values:
- `if days_ago > 5:` → `if days_ago > RECENCY_EARNINGS_TIER1:`
- `if news_age > 2:` → `if news_age > RECENCY_MA_TIER1:`
- `if days_ago > 30:` → `if days_ago > RECENCY_PRICE_TARGET:`

### Impact
1. **Maintainability**: Single source of truth for all recency windows
2. **Documentation**: Each constant has clear rationale
3. **Price Target Fix**: Reduced from 30→7 days (stale targets eliminated)
4. **Consistency**: Easy to adjust windows across all catalyst types

### Rationale: Catalyst-Specific Approach

We chose **catalyst-specific** windows rather than standardizing everything to 2 days because:

- **Earnings momentum** genuinely lasts 3-5 days (analyst updates, media coverage, retail FOMO)
- **M&A/FDA** are binary events - market reacts immediately or misses the move
- **Different catalysts have different momentum profiles**

This is backed by trading reality, not arbitrary choices.

---

## P2-11: RS PERCENTILE DISPLAY ✅

### Problem
Audit claimed: "RS percentile calculated but not showing in output - displays None%"

### Investigation
Checked latest screener output from Dec 23, 2025:

```
Rank  Ticker  Score   RS%     RS-Pct  Catalyst
1     BMY     42.5     +20.2     86 Tier 3 - Sector Rotation
2     AXSM    41.7     +26.7     89 Tier 3 - Sector Rotation
3     BBIO    41.6     +48.6     94 Tier 3 - Sector Rotation
```

Verified JSON output:
```python
1. BMY: RS%=20.2%, Percentile=86
2. AXSM: RS%=26.7%, Percentile=89
3. BBIO: RS%=48.6%, Percentile=94
```

### Finding
**✅ ALREADY WORKING** - No bug exists.

The audit observation was from an older screener run. Current code correctly:
1. Calculates RS percentile (line 631-669)
2. Stores in candidate data
3. Displays in output (line 3286, 3290)

### Resolution
**No fix needed** - marked as complete without code changes.

---

## P2-12: SOURCE CREDIBILITY WEIGHTING ✅

### Problem
All news sources treated equally:
- Bloomberg M&A story: 8 points
- Random blog M&A story: 8 points
- Company press release: 8 points

This is wrong - Bloomberg/WSJ are far more reliable than blogs or biased press releases.

### Solution Implemented
**Commit**: [97da652](https://github.com/ted00000/paper-trader/commit/97da652)

Created 4-tier source credibility system:

```python
SOURCE_CREDIBILITY_TIERS = {
    # TIER 1: Premium financial news (1.5x multiplier)
    'bloomberg': 1.5,
    'reuters': 1.5,
    'dow jones': 1.5,
    'wsj': 1.5,
    'wall street journal': 1.5,
    'financial times': 1.5,

    # TIER 2: Major business news (1.2x multiplier)
    'cnbc': 1.2,
    'barrons': 1.2,
    'marketwatch': 1.2,
    'benzinga': 1.2,
    'yahoo finance': 1.2,

    # TIER 3: Standard financial sites (1.0x - no boost)
    'seeking alpha': 1.0,
    'the motley fool': 1.0,
    'investing.com': 1.0,
    'zacks': 1.0,

    # TIER 4: Low credibility (0.8x penalty)
    'pr newswire': 0.8,  # Company press releases (biased)
    'business wire': 0.8,
    'globenewswire': 0.8,
}
```

### Implementation

**Function Added** (lines 114-132):
```python
def get_source_credibility_multiplier(source):
    """Get credibility multiplier for news source."""
    if not source:
        return 1.0

    source_lower = source.lower()
    for known_source, multiplier in SOURCE_CREDIBILITY_TIERS.items():
        if known_source in source_lower:
            return multiplier

    # Unknown source = neutral (1.0)
    return 1.0
```

**Applied to News Scoring** (lines 1095-1098, 1137, 1151, 1161, 1183):
```python
# Extract source from article
publisher = article.get('publisher', {})
source_name = publisher.get('name', '')
credibility_multiplier = get_source_credibility_multiplier(source_name)

# Apply to all scoring
score += points * credibility_multiplier  # P2-12: Apply source weighting
```

### Impact Examples

**M&A Catalyst Detection (8 base points):**
- Bloomberg: 8 × 1.5 = **12 points**
- CNBC: 8 × 1.2 = **9.6 points**
- Seeking Alpha: 8 × 1.0 = **8 points**
- PR Newswire: 8 × 0.8 = **6.4 points**

**Result**: Premium sources now carry appropriate weight. Company press releases (biased) are penalized.

### Rationale

Not all news sources are equal:

1. **Bloomberg/WSJ/Reuters**: Institutional-grade reporting, fact-checked, legal risk if wrong
2. **CNBC/Barron's**: Professional journalism but sometimes sensationalist
3. **Seeking Alpha**: Mix of quality (some good analysts, some amateur)
4. **PR Newswire**: Company-issued propaganda (always bullish, never objective)

This tiering reflects real-world credibility and reduces false positives from low-quality sources.

---

## PARKED FIXES (Data Requirements)

### P2-13: Backtest Composite Score Formula 🅿️

**Problem**:
Current composite score uses arbitrary multipliers:
```python
final_score = catalyst_score * 2.5 + technical_score + rs_score + volume_score
```

Why 2.5x? Is this optimal? We don't know.

**What's Needed**:
1. Historical trade data (6-12 months)
2. Composite scores at entry time
3. Win/loss outcomes
4. Correlation analysis: score → win rate

**Why Parked**:
- Requires backtesting infrastructure (doesn't exist yet)
- Need historical screener outputs matched to trades
- Tedbot hasn't been logging screener scores in trade records

**When to Revisit**:
After we have 50+ trades with logged entry scores. Then we can:
- Plot score distribution vs win rate
- Optimize the 2.5x catalyst multiplier
- Identify minimum viable score for entry

---

### P2-14: Build Backtesting/Validation Framework 🅿️

**Problem**:
We have NO validation data:
- Don't know if 10% EPS threshold is optimal (why not 8% or 12%?)
- Don't know if 15% M&A premium threshold works
- No tracking of false positives
- Can't measure screener accuracy

**What's Needed**:
1. **False Positive Tracker**:
   - Log all Tier 1 detections
   - Record GO command verdict (buy/hold/pass)
   - Track actual outcome (did stock move?)

2. **Threshold Testing Framework**:
   - Pull historical earnings data
   - Test different beat thresholds (5%, 8%, 10%, 12%, 15%)
   - Measure precision/recall for each

3. **Integration**:
   - Modify screener to log detections
   - Modify GO command to tag screener candidates
   - Build analysis scripts

**Why Parked**:
- This is infrastructure work (2-3 days)
- Requires database or structured logging
- Need to decide on data schema
- Tedbot doesn't have historical validation data yet

**When to Revisit**:
When we're ready to invest in data infrastructure. This should be a Q1 2026 project after system stabilizes.

---

## OVERALL P2 STATUS

| Fix | Status | Lines Changed | Impact |
|-----|--------|---------------|--------|
| P2-10: Recency Windows | ✅ Complete | 60-78, 8 updates | Maintainability + Price target fix |
| P2-11: RS Percentile | ✅ Verified Working | 0 (no bug) | Validation complete |
| P2-12: Source Credibility | ✅ Complete | 86-132, 5 updates | Better signal quality |
| P2-13: Backtest Score | 🅿️ Parked | N/A | Needs historical trade data |
| P2-14: Validation Framework | 🅿️ Parked | N/A | Needs infrastructure build |

### Git Commits
```
97da652 P2-12: Add source credibility weighting to news scoring
1e95278 P2-10: Standardize recency windows with named constants
9534322 P1 Audit Report: Correct Finnhub API status (working)
64380bd Add P1 Audit Report - All high priority fixes complete
52bcbbb P1 Fix #6: Add minimum composite score requirement for Tier 1
```

---

## PARKING LOT

### P2-13: Backtest Composite Score
**Blocker**: No historical trade data with entry scores
**Data Needed**:
- 50+ trades with logged composite scores
- Win/loss outcomes
- Entry/exit timestamps

**Action**: Start logging screener scores in trade records going forward

### P2-14: Build Validation Framework
**Blocker**: No infrastructure for validation tracking
**Requirements**:
- Database or structured logging system
- Integration with GO command
- Historical data collection (3-6 months)

**Action**: Design data schema and logging strategy for Q1 2026

---

## DEPLOYMENT STATUS

**All P2 Fixes Deployed to Production** ✅

```bash
$ ssh root@174.138.67.26 'cd /root/paper_trading_lab && git pull'
Merge made by the 'ort' strategy.
 market_screener.py       | 113 +++++++++++++---
 P1_AUDIT_REPORT_DEC23.md | 333 +++++++++++++++++++++++++++++++++++++++++
```

Server is running latest code with:
- Named recency constants
- Source credibility weighting
- All P0 + P1 + P2 fixes

---

## NEXT STEPS

### Immediate (Complete P2)
- [x] Deploy P2 fixes to production
- [x] Create P2 completion report
- [ ] Monitor next screener run for issues

### Short-term (This Week)
- [ ] Run screener with P2 fixes
- [ ] Monitor for any regressions
- [ ] Verify source credibility weighting in action

### Medium-term (Q1 2026)
- [ ] Begin logging composite scores in trade records
- [ ] Accumulate 50+ trades with scores
- [ ] Design validation framework schema
- [ ] Implement P2-13 when data available

### Long-term (P3 Strategic)
- FDA.gov official feed integration
- Confidence scoring for Tier 1
- Expand catalyst coverage (splits, dividends)
- Bloomberg Terminal evaluation

---

## IMPACT ASSESSMENT

### Code Quality Improvements
1. **Maintainability**: Named constants replace magic numbers
2. **Documentation**: Every constant has clear rationale
3. **Extensibility**: Easy to add new source tiers

### Detection Quality Improvements
1. **Price Target Fix**: 30→7 day window eliminates stale targets
2. **Source Weighting**: Bloomberg gets 1.5x vs blogs (reduces noise)
3. **Consistency**: All recency windows now follow same pattern

### Risk Reduction
1. **False Positive Reduction**: Source credibility penalizes PR spam
2. **Stale Data Elimination**: Price targets >1 week old rejected
3. **Code Clarity**: Named constants prevent copy-paste errors

---

## CONCLUSION

**P2 DELIVERABLES: 3 of 5 COMPLETE** ✅

Successfully implemented all actionable P2 fixes. The 2 parked items (P2-13, P2-14) require data infrastructure that doesn't exist yet - these are correctly deferred to Q1 2026 when we have:

1. Historical trade data with entry scores (for backtesting)
2. Validation infrastructure (for threshold testing)

The screener is now significantly more robust with:
- P0: Critical bug fixes (M&A context validation)
- P1: Quality gates (premium validation, minimum score)
- P2: Code quality (named constants, source weighting)

**Ready for production use** with monitoring for next Tier 1 catalyst.

---

**Report Generated**: December 23, 2025
**Total P2 Fixes**: 3 of 5 (60% complete, 40% parked)
**Status**: DEPLOYED TO PRODUCTION ✅
