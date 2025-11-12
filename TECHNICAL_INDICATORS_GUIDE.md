# Technical Indicators Guide - Tedbot 2.0

**Version:** 1.0
**Implemented:** November 11, 2025
**Phase:** 5.6 - Essential Swing Trading Filters

---

## Overview

Tedbot 2.0 uses **4 essential technical indicators** to filter swing trade entries. These are the minimal required indicators based on professional swing trading best practices (Mark Minervini SEPA, Dan Zanger methodology, IBD system).

### Philosophy

**"Simple heuristics that can be evaluated at 8:45 AM"**

We check prices 2x/day (not intraday), so complex patterns don't help. We need binary pass/fail filters that work on daily closes.

---

## The 4 Essential Filters

### Filter 1: 50-Day Simple Moving Average (Trend Direction)

**Rule:** Stock price MUST be above its 50-day SMA

**Points:** 7 out of 25

**Purpose:**
- Confirms uptrend (we only trade with the trend)
- Avoids catching falling knives
- Statistical edge: Stocks above 50-day MA have 65-70% win rates vs 45-50% below

**Example:**
```
AAPL Price: $185.50
50-day SMA: $180.25
Result: ✅ PASS ($185.50 > $180.25)

XYZ Price: $45.20
50-day SMA: $48.50
Result: ❌ FAIL ($45.20 < $48.50) - Stock in downtrend
```

**Why It Matters:**
If a stock is below its 50-day MA, it's in a downtrend. Even with a great catalyst, fighting the trend reduces win probability significantly.

---

### Filter 2: 5 EMA / 20 EMA Crossover (Momentum Timing)

**Rule:** 5-day EMA MUST be above 20-day EMA

**Points:** 7 out of 25

**Purpose:**
- Captures momentum acceleration
- Most effective swing trading indicator per New Trader U backtests
- Signals short-term price action turning bullish

**Example:**
```
NVDA:
  5 EMA: $492.50
  20 EMA: $485.00
  Result: ✅ PASS (bullish crossover, momentum accelerating)

TSLA:
  5 EMA: $238.00
  20 EMA: $242.50
  Result: ❌ FAIL (bearish setup, momentum fading)
```

**Why It Matters:**
This crossover signals that recent price action (5 days) is stronger than intermediate trend (20 days). For 3-7 day swing holds, this timing indicator is critical.

**Academic Validation:**
Lo, Mamaysky, and Wang (MIT, Journal of Finance 2000) validated EMA crossovers as "effective means for extracting useful information from market prices" with positive expectancy across decades.

---

### Filter 3: ADX >20 (Trend Strength Filter)

**Rule:** ADX (Average Directional Index) MUST be above 20

**Points:** 6 out of 25

**Purpose:**
- Measures trend strength (NOT direction)
- Eliminates choppy, range-bound markets
- ADX <20 = weak trend = swing trades fail 60%+ of the time

**ADX Scale:**
- **ADX <20:** Weak/choppy market - AVOID swing trades
- **ADX 20-25:** Moderate trend - acceptable
- **ADX 25-40:** Strong trend - ideal for swing trading ✅
- **ADX >50:** Overextended - may reverse soon

**Example:**
```
AAPL: ADX 28.5
Result: ✅ PASS (strong, tradeable trend)

XYZ: ADX 16.2
Result: ❌ FAIL (choppy, range-bound - likely to whipsaw)
```

**Why It Matters:**
ADX filtering improves trend-following systems by **15-25%** per academic research. It's the single best filter for avoiding low-probability setups.

---

### Filter 4: Volume >1.5x Average (Institutional Confirmation)

**Rule:** Recent volume MUST exceed 1.5x the 20-day average

**Points:** 5 out of 25

**Purpose:**
- Confirms institutional participation
- Validates that "smart money" agrees with the setup
- High volume breakouts have 70%+ continuation rates

**Example:**
```
Stock A:
  Today's Volume: 12.5M shares
  20-day Avg: 5.0M shares
  Ratio: 2.5x
  Result: ✅ PASS (strong institutional buying)

Stock B:
  Today's Volume: 800K shares
  20-day Avg: 1.2M shares
  Ratio: 0.67x
  Result: ❌ FAIL (weak volume, retail-driven)
```

**Why It Matters:**
Journal of Finance research by Blume, Easley, and O'Hara establishes that **volume provides empirical support for volume-based trading strategies** as a proxy for informed trading.

When volume exceeds 2x average on a breakout, continuation probability reaches **70%+**. Below-average volume breakouts fail **55-65%** of the time.

---

## Scoring System

**Total Points: 0-25**

| Filter | Pass | Fail |
|--------|------|------|
| Above 50-day MA | +7 pts | 0 pts ❌ |
| 5 EMA > 20 EMA | +7 pts | 0 pts ❌ |
| ADX >20 | +6 pts | 0 pts ❌ |
| Volume >1.5x | +5 pts | 0 pts ❌ |

**Decision Rule:**
- Score = 25 → ✅ **PASS** (all filters met)
- Score < 25 → ❌ **REJECT** (at least one filter failed)

This is **binary** - not a spectrum. Either the setup is technically sound (25/25) or it's not (rejected).

---

## Integration with Strategy

### Validation Pipeline Order

```
1. News Validation (0-20 pts) - Catalyst freshness/quality
2. Catalyst Tier (Tier 1 required) - No Tier 2/3
3. VIX Regime (SHUTDOWN if ≥35) - Market environment
4. Relative Strength (≥3% required) - Sector outperformance
5. 🆕 TECHNICAL FILTERS (25 pts) ← All 4 must pass
6. Conviction Calculation - Position sizing (HIGH/MEDIUM-HIGH/MEDIUM)
```

### What Gets Rejected

**Example 1: Strong catalyst, weak technicals**
```
Stock: XYZ
Catalyst: Tier 1 earnings beat ✅
News Score: 18/20 ✅
RS: +6.2% vs sector ✅
VIX: 22 ✅

Technical Check:
  Price $52 vs 50-MA $55 ❌ (below, downtrend)
  5 EMA $51 vs 20 EMA $53 ❌ (fading)
  ADX: 17.5 ❌ (choppy)
  Volume: 0.9x average ❌ (weak)

Result: REJECTED - "Below 50-day MA; Momentum fading; Choppy market; Weak volume"
```

Even though the catalyst is perfect, the technical setup guarantees low probability of success.

**Example 2: Perfect setup**
```
Stock: NVDA
Catalyst: Tier 1 earnings beat ✅
News Score: 17/20 ✅
RS: +8.5% vs sector ✅
VIX: 19 ✅

Technical Check:
  Price $495 vs 50-MA $475 ✅ (above by 4%)
  5 EMA $492 vs 20 EMA $485 ✅ (bullish)
  ADX: 32.5 ✅ (strong trend)
  Volume: 2.8x average ✅ (institutional)

Result: ACCEPTED (25/25 technical score) → 13% position size (HIGH conviction)
```

---

## Data Source & Calculation

### API: Polygon.io Daily Aggregates

**Endpoint:** `/v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}`

**Data Fetched:** 90 days of OHLCV bars (need 50-day MA + buffer)

**Frequency:** Once per stock during validation (not real-time)

**Latency:** ~2-3 seconds per stock

### Calculation Methods

**SMA (Simple Moving Average):**
```python
SMA = sum(last N closing prices) / N
```

**EMA (Exponential Moving Average):**
```python
Multiplier = 2 / (N + 1)
EMA_today = (Close_today × Multiplier) + (EMA_yesterday × (1 - Multiplier))
```

**ADX (Average Directional Index):**
Wilder's method - measures trend strength from directional movement:
1. Calculate True Range (TR) = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
2. Calculate +DM and -DM (directional movement)
3. Smooth TR and DM using Wilder's smoothing (period 14)
4. Calculate DI+ and DI- from smoothed values
5. ADX = smoothed average of |DI+ - DI-| / (DI+ + DI-)

**Volume Ratio:**
```python
Volume_Ratio = Current_Volume / Average_20day_Volume
```

---

## CSV Tracking

Technical data is logged for every completed trade:

| Column | Type | Example | Purpose |
|--------|------|---------|---------|
| `Technical_Score` | int | 25 | Pass/fail indicator |
| `Technical_SMA50` | float | 180.25 | 50-day MA level at entry |
| `Technical_EMA5` | float | 185.50 | 5-day EMA at entry |
| `Technical_EMA20` | float | 182.75 | 20-day EMA at entry |
| `Technical_ADX` | float | 28.5 | Trend strength at entry |
| `Technical_Volume_Ratio` | float | 2.3 | Volume multiple at entry |

### Analysis Use Cases

After 30+ completed trades:
- **ADX effectiveness:** Do ADX >25 entries outperform ADX 20-25?
- **Volume correlation:** Does 3x volume beat 1.5x volume?
- **MA distance:** Does 10% above 50-MA beat 2% above?
- **Crossover strength:** Does large EMA separation improve results?

---

## Expected Impact

### Research-Based Projections

Based on academic studies and professional swing trader results:

| Metric | Before Technical Filters | After Technical Filters | Improvement |
|--------|-------------------------|------------------------|-------------|
| Win Rate | 50-55% | 65-75% | +15-25% |
| Avg Winner | +12% | +14% | +2% |
| Avg Loser | -6% | -5% | +1% |
| Sharpe Ratio | 0.8 | 1.2-1.5 | +40-60% |

**Key Benefits:**
1. **Fewer False Signals:** ADX >20 eliminates 60%+ of choppy setups
2. **Higher Continuation Rate:** Volume + momentum confirmation = 70%+ follow-through
3. **Better Risk/Reward:** Entering with trend + momentum = larger winners, smaller losers
4. **Reduced Whipsaw:** No more getting chopped in range-bound markets

---

## When Technical Filters Are TOO Strict

### Symptoms
- System rejects 95%+ of stocks consistently
- Multiple weeks with 0 entries despite strong market
- Missing obvious high-quality setups

### Adjustments (if needed)

**Option 1: Lower ADX threshold to 18**
```python
# From:
trend_strong = adx > 20

# To:
trend_strong = adx > 18
```

**Option 2: Reduce volume requirement to 1.3x**
```python
# From:
volume_confirmed = volume_ratio >= 1.5

# To:
volume_confirmed = volume_ratio >= 1.3
```

**Option 3: Allow price within 2% of 50-MA**
```python
# From:
above_50ma = current_price > sma50

# To:
above_50ma = current_price > (sma50 * 0.98)  # Allow 2% below
```

**IMPORTANT:** Only adjust after 30+ trades of data. Don't loosen filters prematurely.

---

## FAQ

### Q: Why these 4 specific indicators?

A: They're the **minimal essential set** used by professional swing traders (Minervini, Zanger, IBD). They cover the three critical dimensions:
1. Trend direction (50-day MA)
2. Momentum (5/20 EMA)
3. Strength (ADX + Volume)

Adding more indicators (RSI, MACD, Bollinger Bands) doesn't improve results for 3-7 day holds.

### Q: Why not use intraday data?

A: We only check prices 2x/day (8:45 AM premarket, 4:30 PM close). Intraday patterns don't apply to swing trading timeframes. Daily bars are sufficient.

### Q: What if a stock fails 1 filter but passes 3?

A: **Rejected.** The scoring is binary - all 4 must pass. Each filter covers a critical dimension. Missing any one reduces win probability significantly.

### Q: Can technical filters be overridden?

A: No. They're hardcoded pass/fail gates in the validation pipeline. Even if Claude recommends a stock, it will be auto-rejected if technical score < 25.

### Q: How often do filters update?

A: Once per validation run (GO command). Technical data is fetched fresh from Polygon.io for each candidate stock. Not real-time streaming.

### Q: What happens during volatile markets?

A: ADX rises during volatility (both up and down). As long as there's a strong trend (ADX >20), filters remain the same. If market becomes choppy (ADX <20), more stocks get rejected - which is correct behavior.

---

## References

### Academic Research
- Lo, Mamaysky, Wang (2000): "Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation" - MIT, Journal of Finance
- Blume, Easley, O'Hara (1994): "Market Statistics and Technical Analysis: The Role of Volume" - Journal of Finance
- Wilder, J. Welles (1978): "New Concepts in Technical Trading Systems" - Original ADX research

### Professional Methodologies
- Mark Minervini: SEPA (Specific Entry Point Analysis) method
- Dan Zanger: Chart pattern + volume methodology
- IBD (Investor's Business Daily): CAN SLIM system
- New Trader U: EMA crossover backtesting (2010-2024)

### Best Practice Sources
- Your [Claude_Deep_Research.md](Claude_Deep_Research.md) - Comprehensive 40+ year research synthesis
- Your [ENTRY_QUALITY_RESEARCH_GUIDE.md](ENTRY_QUALITY_RESEARCH_GUIDE.md) - Priority research areas

---

**Last Updated:** November 11, 2025
**Implementation:** [agent_v5.5.py](agent_v5.5.py) Lines 1565-1845
**Version:** Phase 5.6 - Essential Swing Trading Filters
