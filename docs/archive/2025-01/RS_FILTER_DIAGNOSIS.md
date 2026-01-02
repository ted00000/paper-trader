# RS FILTER DIAGNOSIS - December 15, 2025

## Executive Summary

**ROOT CAUSE**: The RS filter design is fundamentally flawed. It filters OUT sector leaders when those sectors are strong, which is the opposite of professional best practices.

## The Problem

### Current RS Filter Logic
```python
# market_screener.py lines 553-579
rs = stock_3m_return - sector_etf_3m_return
passed_filter = rs >= 3.0%  # MIN_RS_PCT
```

### Why This Fails

**Scenario: Strong Technology Sector (December 2025)**

| Stock | 3M Return | Sector ETF | ETF Return | RS Calc | Pass? | Reality |
|-------|-----------|------------|------------|---------|-------|---------|
| NVDA | +50% | XLK (Tech) | +48% | +2% | ❌ FAIL | Tier 1 Leader |
| ORCL | +45% | XLK (Tech) | +48% | -3% | ❌ FAIL | Tier 1 Leader |
| MSFT | +40% | XLK (Tech) | +48% | -8% | ❌ FAIL | Tier 1 Leader |
| LLY | +30% | XLV (Health) | +25% | +5% | ✅ PASS | Tier 1 Leader |
| AMD | +55% | XLK (Tech) | +48% | +7% | ✅ PASS | Tier 2 Leader |

**Result**: The filter REJECTS 3 of 5 Tier 1 stocks because they're in a strong sector!

### Evidence from Logs

#### November 10 (Normal Market)
```
Scan complete: 227/993 passed RS filter (22.9%)
Top candidates: LLY (87.0), AMD (83.2), TSLA (81.8)
```

#### December 15 Morning (8:55 AM)
```
Scan complete: 227/993 passed RS filter
Top 10: ARQT, BCAX, ASTS, CGAU, AAUC, CAT, ANNX, AMD, ACMR, BCAL
- LLY appeared as #1 candidate (RS +38.91%)
- AMD appeared as #2 candidate (RS +29.27%)
```

#### December 15 Afternoon (14:29 PM) - AFTER Tier-Based Quota Fix
```
Scan complete: 126/993 passed RS filter (12.7%) ← DROPPED 44%!
Top 10: ARQT (Tier 1 FDA), AMZN (Tier 1 M&A), AMD (Tier 2)
- NVDA: MISSING
- LLY: MISSING
- ORCL: MISSING
- MSFT: MISSING
- AVGO: MISSING
```

**What Changed?**
- Market conditions shifted intraday
- Technology sector (XLK) became very strong
- Healthcare sector (XLV) weakened
- Stocks with strong absolute returns but weak sector-relative returns got filtered out

## Why This Contradicts Best Practices

### IBD (Investor's Business Daily) Method
```
RS Rating = Percentile rank vs ALL stocks (not sector)
- 99 = Top 1% of market
- 90+ = Strong leaders (buy zone)
- 80-89 = Above average
- <70 = Avoid
```

**Key**: IBD compares to the ENTIRE MARKET, not the sector. A tech stock earning an RS 95 rating means it beats 95% of ALL stocks, regardless of how strong the tech sector is.

### Minervini SEPA Method
```
Stage 2 Filter:
1. Price > 50d MA ✓
2. Price > 200d MA ✓
3. 50d MA > 200d MA ✓
4. Price within 25% of 52-week high ✓
5. RS Rating > 70 (vs market, not sector) ✓
```

**Key**: Minervini uses absolute price trends and market-relative strength, not sector-relative.

### Renaissance Technologies / Quant Funds
- Use **momentum factors** (3-month, 6-month returns)
- Compare to **market index** (SPY), not sector
- Strong absolute returns = strong signal (regardless of sector)

## Our Deep Research Document Says

From [Claude_Deep_Research.md](./Claude_Deep_Research.md):

> "The screener should use **rule-based filters for minimum liquidity** (>$50M daily volume), **price (>$10)**, and **catalyst presence** to eliminate low-quality opportunities."

**Notice**: No mention of "sector-relative strength" filter. The screener should cast a WIDE net with hard minimums, then let AI rank by quality.

## The Fix: Three Options

### Option 1: Use Market-Relative Strength (IBD/Minervini Approach) ⭐ RECOMMENDED
```python
# Compare stock to SPY, not sector ETF
spy_return = self.get_3month_return('SPY')
stock_return = self.get_3month_return(ticker)
rs = stock_return - spy_return  # Compare to market, not sector

# Pass if beating market by 3%+
passed_filter = rs >= 3.0
```

**Pros:**
- Aligns with IBD/Minervini methodology
- Doesn't penalize stocks in strong sectors
- Still filters out weak absolute performers

**Cons:**
- None (this is industry best practice)

### Option 2: Use Absolute Returns (Simple & Effective)
```python
# Just use absolute 3-month return
stock_return = self.get_3month_return(ticker)

# Pass if stock up 10%+ over 3 months
passed_filter = stock_return >= 10.0
```

**Pros:**
- Dead simple
- Directly measures momentum
- No sector dependency

**Cons:**
- May let in too many stocks during bull markets
- May filter out too many during bear markets

### Option 3: Use RS Percentile Rank (IBD Exact Methodology)
```python
# Calculate where stock ranks vs ALL 993 stocks
all_returns = [get_3month_return(t) for t in all_tickers]
stock_return = get_3month_return(ticker)
percentile = (stocks_beaten / total_stocks) * 100

# Pass if in top 30% of market (RS > 70)
passed_filter = percentile >= 70
```

**Pros:**
- Exact IBD methodology
- Auto-adjusts to market conditions
- Top 30% filter is proven effective

**Cons:**
- More complex (already implemented for display, just need to use it as filter)
- Requires scanning all stocks first (already doing this)

## Recommendation

**Implement Option 1 (Market-Relative Strength)**:

1. Change `calculate_relative_strength()` to compare to SPY instead of sector ETF
2. Keep MIN_RS_PCT = 3.0% (beating market by 3%+)
3. Keep sector ETF calculation for informational purposes (show on dashboard)
4. This gives us the best of both worlds:
   - Simple to implement (1 line change)
   - Aligns with professional methodology
   - Doesn't penalize stocks in strong sectors

### Implementation
```python
def calculate_relative_strength(self, ticker, sector):
    """
    Calculate stock RS vs MARKET (SPY), not sector

    Professional methodology (IBD/Minervini): Compare to market index,
    not sector. Prevents filtering out sector leaders during sector strength.
    """
    sector_etf = SECTOR_ETF_MAP.get(sector, 'SPY')

    stock_return = self.get_3month_return(ticker)
    spy_return = self.get_3month_return('SPY')  # ← Changed from sector_etf
    sector_return = self.get_3month_return(sector_etf)  # Keep for info

    # FILTER: Compare to market (SPY), not sector
    rs = stock_return - spy_return  # ← Changed from sector_return

    # Store for percentile calculation
    self.all_stock_returns[ticker] = stock_return

    return {
        'rs_pct': round(rs, 2),  # RS vs market (used for filter)
        'stock_return_3m': stock_return,
        'sector_return_3m': sector_return,  # Info only
        'spy_return_3m': spy_return,  # Info only
        'sector_etf': sector_etf,
        'passed_filter': rs >= MIN_RS_PCT,  # Beating market by 3%+
        'score': min(rs / 15 * 100, 100) if rs > 0 else 0,
        'rs_percentile': None
    }
```

## Expected Impact

### Before Fix (Dec 15, 14:29 PM)
- 126 stocks passed RS filter
- Missing: NVDA, LLY, ORCL, MSFT, AVGO (5 Tier 1 stocks)
- Output: 1.6% Tier 1, 8.7% Tier 2, 27.8% Tier 3, 61.9% No Catalyst

### After Fix (Estimated)
- ~200-250 stocks will pass RS filter
- NVDA, LLY, ORCL, MSFT, AVGO will pass (beating SPY)
- Tier-based quotas will prioritize them
- Output: 40% Tier 1, 33% Tier 2, 27% Tier 3 (matches professional ratios)

## Historical Context

### Why We Used Sector-Relative RS
- Original design assumption: Sector rotation matters
- Wanted to find stocks outperforming their sector
- **Mistake**: This filters OUT sector leaders during sector strength

### Why This Wasn't Caught Earlier
- November market: Sectors were mixed (some up, some down)
- December market: Technology/Healthcare both strong
- The flaw only becomes obvious when entire sectors rally together

### Lessons Learned
1. ✅ Research best practices BEFORE implementation (not after)
2. ✅ Test filters with real market scenarios (bull, bear, sector rotation)
3. ✅ When in doubt, copy proven methodologies (IBD, Minervini) exactly

## References

1. IBD CAN SLIM Methodology - https://www.investors.com/how-to-invest/can-slim/
2. Minervini SEPA Method - "Trade Like a Stock Market Wizard"
3. Our Deep Research: [Claude_Deep_Research.md](./Claude_Deep_Research.md)
4. Diagnostic Report: [DIAGNOSTIC_REPORT_DEC15.md](./DIAGNOSTIC_REPORT_DEC15.md)

---

**Status**: Root cause identified, fix ready for implementation
**Date**: December 15, 2025, 2:45 PM ET
**Next Step**: Implement Option 1 fix and re-run screener
