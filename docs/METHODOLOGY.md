# TedBot Trading System - Methodology & Architecture

**Version:** 5.5 (January 2026)
**Status:** Paper Trading (Validation Phase)
**Starting Capital:** $10,000

---

## Executive Summary

TedBot is a **systematic, rules-based swing trading system** that combines quantitative screening with AI-augmented decision-making. It operates a daily pipeline that screens the S&P 1500 universe through multiple quantitative filters, uses Claude (Anthropic's LLM) as a catalyst-validation and portfolio-construction layer, and executes trades with regime-aware position sizing and dynamic risk management.

The system is not a black-box statistical arbitrage model. It is a **catalyst-driven momentum strategy** that uses explicit, auditable rules at every stage. The AI layer provides judgment on news quality and catalyst validity - something traditional quant models struggle with - while the quantitative framework provides discipline, risk controls, and systematic execution.

---

## Table of Contents

1. [System Architecture & Daily Pipeline](#1-system-architecture--daily-pipeline)
2. [Universe & Screening Methodology](#2-universe--screening-methodology)
3. [Portfolio Construction (GO Command)](#3-portfolio-construction-go-command)
4. [Risk Management & Execution](#4-risk-management--execution)
5. [Portfolio Monitoring & Exits](#5-portfolio-monitoring--exits)
6. [Honest Assessment: Strengths & Limitations](#6-honest-assessment-strengths--limitations)

---

## 1. System Architecture & Daily Pipeline

### Automated Schedule (Eastern Time)

| Time | Operation | Purpose |
|------|-----------|---------|
| 7:00 AM | **SCREEN** | Scan S&P 1500, calculate breadth, validate catalysts |
| 9:00 AM | **GO** | Claude analyzes top candidates, builds portfolio decisions |
| 9:45 AM | **EXECUTE** | Place orders via Alpaca with spread/gap validation |
| 4:30 PM | **ANALYZE** | Update prices, check exits, log performance |

### Technology Stack

- **Screening:** Python + Polygon.io API (market data, news, technicals)
- **Decision Layer:** Claude Sonnet 4.5 (portfolio construction) + Claude Haiku 3.5 (catalyst screening)
- **Execution:** Alpaca Markets Paper Trading API
- **Risk Framework:** Custom Python (ATR stops, gap analysis, spread checks)

---

## 2. Universe & Screening Methodology

### 2.1 Starting Universe

**S&P 1500 Composite** (~1,500 stocks)
- S&P 500 (large-cap)
- S&P MidCap 400
- S&P SmallCap 600

Loaded from maintained constituent file. This universe provides institutional-grade liquidity while offering sufficient breadth for catalyst-driven opportunities across market capitalizations.

### 2.2 Binary Gate Filters (Hard Requirements)

Every stock must pass ALL gates before further analysis. These are non-negotiable:

| Gate | Threshold | Rationale |
|------|-----------|-----------|
| **Minimum Price** | $10.00 | Institutional participation floor |
| **Market Cap** | $1 Billion | Eliminates illiquid micro-caps |
| **Daily Dollar Volume** | $25-40M (regime-aware) | Ensures executable position sizes |
| **Data Freshness** | Last trade within 120 hours | Accounts for holiday gaps |

**Regime-Aware Volume Gate:**
- Normal conditions: $25M daily notional
- Holiday weeks: $15M (reduced liquidity expected)
- Risk-off (VIX >25): $40M (demand higher liquidity in stress)

### 2.3 Catalyst Detection & Validation

After passing binary gates, each stock's news is fetched from Polygon.io (7-day lookback window) and analyzed for catalyst presence.

**Claude Haiku 3.5** performs catalyst classification at scale (cost-efficient at $0.25/1M input tokens, temperature=0 for determinism):

**Tier 1 Catalysts (Highest Conviction):**
- FDA approvals / priority review designations
- M&A targets (>15% acquisition premium)
- Earnings beats >10% with raised guidance
- Major contract wins >$100M

**Tier 2 Catalysts (Moderate Conviction):**
- Analyst upgrades with >10% price target increase
- Guidance raises without earnings surprise
- Product launches, strategic partnerships
- Moderate earnings beats (5-10%)

**Tier 3 Catalysts (Supporting Only):**
- Sector rotation / industry tailwinds
- Insider buying clusters
- Upcoming earnings anticipation

**Tier 4 Catalysts (Technical):**
- 52-week high breakouts with volume confirmation
- Significant gap-ups (>5%)

**Automatic Rejections (Negative News Detection):**
- Dilutive offerings / secondary offerings
- Lawsuits / SEC investigations / class actions
- Analyst downgrades
- Guidance cuts / earnings misses
- Clinical trial failures / FDA rejections

### 2.4 Composite Scoring System

Each candidate receives a composite score based on **tier-weighted factors:**

#### Base Score Weights by Catalyst Tier:

| Factor | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|--------|--------|--------|--------|--------|
| Relative Strength | 20% | 25% | 40% | 35% |
| News Score | 20% | 20% | 10% | 5% |
| Volume Score | 10% | 10% | 5% | 15% |
| Technical Score | 10% | 5% | 5% | 5% |

**Design Rationale:** Tier 1 catalysts weight news and RS equally (the catalyst IS the edge). Tier 3/4 catalysts weight RS heavily (momentum must compensate for weaker catalysts).

#### Catalyst Score Points:

| Signal | Points | Weight Multiplier |
|--------|--------|-------------------|
| M&A / FDA news | 25 | Tier-dependent (0.4-1.0x) |
| Fresh earnings beat (0-3d) | 20 | Tier-dependent |
| Analyst upgrade | 20 | Tier-dependent |
| Contract win | 20 | Tier-dependent |
| Insider buying cluster | 15 | Tier-dependent |
| 52-week breakout | 10 | Tier-dependent |

**Magnitude Bonuses (additive):**
- M&A premium >= 30%: +10 points
- FDA breakthrough designation: +12 points
- Contract value >= $1B: +10 points
- Guidance raise >= 20%: +8 points

#### Relative Strength Calculation:

```
RS = Stock_3M_Return - SPY_3M_Return
```

After full scan, IBD-style percentile ranking calculated:
- 99th = Top 1% of universe
- 90th+ = Exceptional momentum
- 80th+ = Strong momentum
- <50th = Below average (penalized)

#### Volume Score:

```
Volume_Score = min((Yesterday_Volume / Median_20d_Volume) / 3 * 100, 100)
```

Uses **median** (not mean) for stability against single-day spikes. 3x average volume = perfect score.

#### Technical Score:

Primary metric: **Distance from 52-week high**
```
Score = max(100 - (Distance_Pct * 2), 0)
```

Supporting indicators (informational, not scored): RSI-14, ADX-14, EMA crossovers, 50-day SMA position.

### 2.5 Final Selection: Top 40 Candidates

**Tier-Based Quota System** prevents lower-quality catalysts from crowding out institutional-grade signals:

1. Tier 1 candidates: Top 60 by composite score
2. Tier 2 candidates: Top 50
3. Tier 3 candidates: Top 40
4. Combined, sorted by composite score, trimmed to **40 candidates**

**Multi-Factor Tie-Breaking** (eliminates alphabetical bias):
1. Composite score (primary)
2. RS percentile (secondary)
3. Average volume / liquidity (tertiary)

### 2.6 Market Breadth Calculation

Calculated during screening as a **regime indicator** for downstream position sizing:

```
Breadth = (Stocks above 50-day SMA) / (Total stocks scanned) * 100
```

- >= 50%: HEALTHY (normal sizing)
- 40-49%: DEGRADED (reduce position sizes 20%)
- < 40%: UNHEALTHY (reduce position sizes 40%)

---

## 3. Portfolio Construction (GO Command)

### 3.1 Decision Model

**Model:** Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

Claude receives the top 15 screener candidates (from the 40) along with:
- Full portfolio state (existing positions with P&L, days held, catalysts)
- Market conditions (VIX level, breadth regime, macro calendar)
- Strategy rules and historical performance data
- Each candidate's technical indicators, news articles, catalyst classification

Claude returns a structured JSON decision:
```json
{
  "hold": ["TICKER1", "TICKER2"],
  "exit": [{"ticker": "X", "reason": "Specific exit reason"}],
  "buy": [{"ticker": "Y", "decision": "ENTER", "position_size_pct": 10.0, ...}]
}
```

### 3.2 Entry Decisions

**ENTER:** Standard entry (position size 6-10%)
- High conviction setup: strong catalyst + confirming technicals + good volume

**ENTER_SMALL:** Reduced entry (position size 5-6%)
- Speculative setup: uncertain catalyst, extended technicals, or elevated risk

**PASS:** Do not enter (omitted from buy array)
- Expected on 30-40% of candidates presented

### 3.3 Conviction-Based Position Sizing

After Claude's decisions, the system applies a **quantitative conviction overlay** using cluster-based factor counting:

#### Factor Clusters:

**Cluster 1 - Momentum (max +3 points):**
- RS percentile >= 90th: +2 (double weight - priority signal)
- RS percentile >= 80th: +1
- RS vs sector >= 7%: +1
- Leading sector (vs SPY +2%): +1

**Cluster 2 - Institutional Signals (max +2 points):**
- Unusual options activity: +1
- Dark pool activity: +1

**Cluster 3 - Catalyst Quality (uncapped):**
- Tier 1 catalyst: +1
- Multi-catalyst setup: +1
- Revenue beat: +1
- News score >= 15: +1
- News score >= 10: +1

**Cluster 4 - Market Conditions (max +2 points):**
- VIX < 20: +1
- VIX 20-25: +1

#### Position Sizing by Conviction:

| Conviction | Factors | Position Size |
|------------|---------|---------------|
| HIGH | 7+ factors, news >= 15, VIX < 25 | 13% |
| MEDIUM-HIGH | 5-6 factors, news >= 10 | 11% |
| MEDIUM | 3-4 factors, news >= 5 | 10% |
| SKIP (low) | < 3 factors | 5% (starter) |

**Breadth Adjustment Applied:**
- HEALTHY market: 1.0x (no change)
- DEGRADED market: 0.8x (e.g., 10% becomes 8%)
- UNHEALTHY market: 0.6x (e.g., 10% becomes 6%)

### 3.4 VIX Regime Gates

| VIX Level | Regime | Action |
|-----------|--------|--------|
| >= 35 | SHUTDOWN | Block ALL new entries |
| 30-34 | CAUTIOUS | Only Tier 1 + news >= 15 |
| < 30 | NORMAL | Proceed with standard rules |

### 3.5 Validation Pipeline

After Claude's decisions, before execution, each position passes through:

1. **Phantom Position Filter** - Validates HOLD/EXIT tickers actually exist in portfolio (prevents LLM hallucination)
2. **News Validation** - Confirms catalyst freshness (0-20 score)
3. **Relative Strength Validation** - Confirms momentum still intact
4. **Sector Concentration Check** - Guidelines for < 40% single-sector exposure (Claude documents rationale for exceptions)

### 3.6 Portfolio Rotation (When Full)

When portfolio is at maximum capacity (10 positions) and superior opportunities appear:

**Exit Candidate Scoring (quantitative):**
- Weak momentum (< 0.3%/day): +30 points
- Stalling position (> 5 days, < +3%): +25 points
- Losing position (< -2%): +40 points
- Low-tier catalyst (Tier 2/3): +15 points

**Entry Opportunity Scoring:**
- Tier 1 catalyst: +40 points
- Fresh catalyst (< 24h): +30 points
- High news validation (> 80): +20 points
- Strong RS (> 75th percentile): +10 points

Rotation recommended when exit score >= 50 AND opportunity score >= 60.

---

## 4. Risk Management & Execution

### 4.1 Pre-Execution Checks

Before any order is placed, three safeguards must pass:

#### Gap Analysis

| Gap Classification | Size | Action |
|-------------------|------|--------|
| EXHAUSTION_GAP | >= 8% | Skip entry entirely |
| BREAKAWAY_GAP | 5-7.9% | Skip (wait for consolidation) |
| CONTINUATION_GAP | 2-4.9% | Delay entry 15 minutes |
| NORMAL | < 2% | Enter at open |
| GAP_DOWN | <= -3% | Enter (buy weakness) |

#### Bid-Ask Spread Check

```
Spread_Pct = (Ask - Bid) / Mid_Price * 100
Skip if Spread_Pct > 0.50%
```

Prevents costly execution in illiquid names where market orders would erode the edge.

#### Cash Availability

Position size capped at available cash. No margin used.

### 4.2 Stop-Loss Methodology

**Primary: ATR-Based Dynamic Stops**

```
ATR_Stop = Entry_Price - (ATR_14 * 2.5)
Max_Stop = Entry_Price * 0.93  (-7% cap)
Final_Stop = max(ATR_Stop, Max_Stop)  // Use tighter of the two
```

**Design:** The 2.5x ATR stop gives each stock room proportional to its volatility, while the -7% hard cap prevents catastrophic single-position loss regardless of volatility.

**Example:**
- Entry: $100, ATR-14: $2.00
- ATR Stop: $100 - ($2 * 2.5) = $95.00 (-5%)
- Max Stop: $93.00 (-7%)
- **Used: $95.00** (tighter, respects volatility)

**Fallback (ATR unavailable):** Fixed -7% stop.

### 4.3 Dynamic Profit Targets

Targets are **catalyst-specific**, based on empirical research on post-catalyst price behavior:

| Catalyst Type | Target | Stretch | Typical Hold |
|--------------|--------|---------|--------------|
| M&A Target | 15% | 20% | 5-10 days |
| FDA Approval | 15% | 25% | 5-10 days |
| Earnings Beat > 20% | 12% | 15% | 5-10 days |
| Major Contract | 12% | - | 5-7 days |
| Top-Firm Analyst Upgrade | 12% | - | 5-7 days |
| Tier 2 (Standard) | 8% | - | 3-5 days |
| Insider Buying | 10% | - | 10-20 days |

### 4.4 Execution via Alpaca

- **Order Type:** Market orders (simplicity, guaranteed fill for liquid names)
- **Slippage Tracking:** Records bid/ask at entry, calculates execution cost in basis points
- **Position Sizing:** Dollar-based (% of account value), converted to shares at execution

---

## 5. Portfolio Monitoring & Exits

### 5.1 Exit Priority Hierarchy

Checked daily at 4:30 PM (ANALYZE command):

1. **Catalyst Invalidation** (HIGHEST PRIORITY)
   - Thesis-breaking news detected (offering, lawsuit, downgrade)
   - Exit immediately regardless of P&L

2. **Stop Loss**
   - Price <= ATR-based stop (or -7% cap)
   - Exit 100%

3. **Profit Target + Trailing Stop**
   - Price >= dynamic target
   - Activate trailing stop (lock in +8%, trail 2% below peak)
   - Exit when trailing stop hit

4. **Time Stop**
   - Standard: 21 days maximum hold
   - PED (Post-Earnings Drift): Extended hold period
   - Exit 100%

### 5.2 Trailing Stop Mechanics

Once profit target is hit:
1. Trailing stop activates at entry + 8% (locks in gains)
2. As price rises, trailing stop follows at current_price * 0.98 (2% below)
3. Exit when price drops to trailing stop level

**Gap-Aware Exception:** If target is hit via a large gap (>= 5%), wait for consolidation before activating trail (prevents whipsaw on gap-and-fade patterns).

### 5.3 Position Tracking

Each position maintains:
- Entry price, date, shares
- Current price, unrealized P&L
- Days held (incremented daily)
- Stop loss, price target
- Catalyst type and tier
- Trailing stop status
- Bid/ask at entry, slippage in bps

### 5.4 Trade Logging

All closed trades logged to CSV with:
- Entry/exit dates and prices
- Return percentage
- Catalyst type and tier
- Exit reason (standardized)
- Days held
- Slippage data

---

## 6. Honest Assessment: Strengths & Limitations

### What This System IS

1. **Systematic and Rules-Based** - Every decision follows explicit, auditable rules. The screening, scoring, sizing, and exit logic are deterministic and reproducible.

2. **Catalyst-Driven with Quantitative Discipline** - The edge hypothesis is clear: stocks with fresh, material catalysts (M&A, FDA, earnings) tend to exhibit momentum that can be captured in 3-21 day holding periods. This is well-documented in academic literature (post-earnings drift, merger arbitrage, event-driven momentum).

3. **Risk-Aware by Design** - ATR-based stops, position-size caps, VIX regime gates, breadth adjustments, gap analysis, and spread checks provide multiple layers of risk control before and after entry.

4. **AI-Augmented, Not AI-Dependent** - The LLM layer provides judgment on news quality and catalyst validity (something traditional NLP/keyword models do poorly), but the quantitative framework provides discipline. Claude cannot override stops, sizing rules, or regime gates.

5. **Fully Automated Pipeline** - From screening to execution to monitoring, the system runs without manual intervention. All decisions are logged for analysis.

### What This System IS NOT

1. **Not a Statistical Arbitrage Model** - There is no covariance matrix, no mean-reversion signal, no pairs trading, no factor model in the traditional quant sense. The alpha source is event-driven momentum, not statistical mispricing.

2. **Not Backtested with Statistical Rigor** - Parameters (7% stop, 2.5x ATR, tier weights, scoring points) are based on practitioner research and domain knowledge, not optimized over historical data with walk-forward validation. This is both a weakness (unknown Sharpe ratio) and a strength (no overfitting to past data).

3. **Not a High-Frequency System** - Holding periods are 3-21 days. There is no intraday trading, no market microstructure exploitation, no latency sensitivity.

4. **Not Diversified Across Strategies** - Single strategy (catalyst momentum). No mean-reversion, no volatility selling, no macro overlay. Concentration risk in strategy type.

5. **Not Yet Validated with Live Capital** - Currently in paper trading validation phase. Track record is being established. No audited returns exist.

### The Role of the LLM

The LLM (Claude) serves a specific, bounded role:

- **Screener Stage (Haiku):** Classifies news into catalyst tiers and detects negative flags. This replaces traditional NLP keyword matching with contextual understanding (e.g., distinguishing "Company A acquires B" from "Company B is acquired by A" - the target vs acquirer distinction matters enormously for expected return).

- **GO Stage (Sonnet):** Constructs the portfolio from pre-validated candidates. Claude sees the same quantitative data a human analyst would (technicals, news, RS rankings) and makes entry/pass/exit decisions. The quantitative conviction system then overlays position sizing.

**Critical Constraint:** Claude's decisions are validated and bounded by the quantitative framework. It cannot:
- Enter positions that fail binary gates
- Size positions above conviction limits
- Override VIX regime shutdowns
- Skip stop-loss exits
- Hold beyond time stops

### Classification

This system occupies the space between **discretionary trading** and **fully quantitative**:

| Dimension | Discretionary | TedBot | Institutional Quant |
|-----------|---------------|--------|---------------------|
| Universe selection | Gut feel | Systematic (S&P 1500) | Systematic |
| Signal generation | Experience | Rules + AI judgment | Statistical models |
| Position sizing | Variable | Conviction formula | Kelly/Risk parity |
| Risk management | Mental stops | ATR + regime gates | VaR/CVaR models |
| Execution | Manual | Automated + checks | Algorithmic |
| Backtesting | None | Limited | Rigorous walk-forward |
| Parameter optimization | None | Research-based | Statistical |
| Strategy diversification | Single | Single | Multi-strategy |

**Verdict:** TedBot is a **systematic event-driven trading system with AI-augmented catalyst validation**. It has institutional-grade screening architecture and risk controls, but lacks the statistical backtesting rigor and multi-strategy diversification of a true quantitative fund. It is significantly more disciplined and systematic than a solo developer's discretionary trading, but honestly cannot claim to be a "quant platform" in the institutional sense without validated out-of-sample performance data.

### Path to Institutional Grade

To bridge the gap, the system would need:
1. **Walk-forward backtesting** of catalyst signals over 5+ years of historical data
2. **Parameter sensitivity analysis** (how robust are the 7% stop, tier weights, etc.)
3. **Portfolio-level risk metrics** (max drawdown constraints, Sharpe targets, correlation monitoring)
4. **Strategy diversification** (adding mean-reversion, volatility, or macro strategies)
5. **Validated track record** (12+ months of live or paper performance with proper benchmarking)

---

## Appendix A: Key Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Universe | S&P 1500 | Maintained constituent file |
| Min Price | $10 | Institutional floor |
| Min Market Cap | $1B | Liquidity requirement |
| Min Daily Volume | $25-40M | Regime-aware |
| Top Candidates | 40 | Presented to Claude |
| Max Positions | 10 | Portfolio limit |
| Position Size Range | 5-13% | Conviction-based |
| Stop Loss | ATR*2.5 or -7% cap | Dynamic |
| Profit Targets | 8-25% | Catalyst-specific |
| Max Hold | 21 days | Time stop |
| Min Hold | 2 days | Anti-churn |
| VIX Shutdown | >= 35 | Block entries |
| VIX Cautious | 30-34 | Tier 1 only |
| Spread Limit | 0.50% | Skip if wider |
| Gap Skip | >= 5% | Wait/skip |
| Breadth Healthy | >= 50% | Full sizing |
| Breadth Degraded | 40-49% | Reduce 20% |
| Breadth Unhealthy | < 40% | Reduce 40% |

## Appendix B: Data Sources

| Source | Purpose | Cost Tier |
|--------|---------|-----------|
| Polygon.io | Market data, news, technicals, snapshots | Paid API |
| Anthropic Claude | Catalyst validation, portfolio construction | Pay-per-token |
| Alpaca Markets | Paper trading execution | Free (paper) |

## Appendix C: Automation Schedule

```
07:00 ET  SCREEN   Scan 1,500 stocks, calculate breadth, validate catalysts
09:00 ET  GO       Claude analyzes top 15, makes entry/hold/exit decisions
09:45 ET  EXECUTE  Place orders with gap/spread validation
16:30 ET  ANALYZE  Update prices, check exits, log performance
```

---

*Document generated January 23, 2026. System version 5.5.*
