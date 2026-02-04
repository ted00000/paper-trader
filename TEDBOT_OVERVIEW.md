# Tedbot Trading System - Complete Overview

## What is Tedbot?

Tedbot is an **autonomous AI-powered catalyst-driven swing trading system** that uses Claude (Anthropic's AI) to identify, analyze, and trade stocks experiencing significant catalysts. The system operates fully autonomously with a $1,000 paper trading account, making data-driven decisions based on news events, technical analysis, market conditions, and continuous learning from past performance.

**Performance Target**: 90-92% of best-in-class professional trader performance
**Strategy**: Event-driven momentum trading (3-7 day holds, occasionally 30-60 days for post-earnings drift)
**Approach**: High-conviction, concentrated positions (10 max) with strict risk management
**Current Version**: v8.5 (Earnings Calendar Integration) - Live paper trading with real brokerage API execution

---

## 🔄 Complete System Architecture: Screener → Decision → Execution → Learning

Tedbot implements a **closed-loop autonomous trading system** with four interconnected stages:

```
┌─────────────────────────────────────────────────────────────────┐
│                    STAGE 1: IDENTIFICATION                       │
│              (Hybrid Screener - v10.1 Jan 2026)                 │
│  BINARY GATES + CLAUDE AI ARCHITECTURE                          │
│                                                                  │
│  PHILOSOPHY: "If it's not binary, Claude decides"               │
│                                                                  │
│  PHASE 1: BINARY HARD GATES (Objective only):                   │
│  • Scans 993 S&P 1500 stocks continuously                       │
│  • BINARY FILTERS (no interpretation):                          │
│    - Price ≥$10 (liquidity, institutional participation)        │
│    - Daily volume ≥$50M (execution quality)                     │
│    - Data freshness (traded in last 5 days)                     │
│  • NO keyword-based filtering removed:                          │
│    ❌ Negative news keywords (Claude decides)                   │
│    ❌ Catalyst keywords (Claude decides)                        │
│    ❌ Tier requirements (Claude decides)                        │
│  OUTPUT: ~250 stocks pass binary gates                          │
│                                                                  │
│  PHASE 2: CLAUDE AI CATALYST ANALYSIS:                          │
│  • Analyzes ALL ~250 stocks (vs 3-5 in v9.0) - 83x coverage    │
│  • Negative news detection (offerings, lawsuits, downgrades)    │
│  • Catalyst identification with nuance:                         │
│    - FDA Priority Review vs FDA delays                          │
│    - M&A target vs acquirer                                     │
│    - Earnings beat vs miss                                      │
│  • Tier classification (Tier 1/2/3/4/None)                      │
│  • Confidence scoring (High/Medium/Low)                         │
│  • Rate limiting: 5 concurrent, exponential backoff             │
│  • Cost: ~$0.07/run (~$2.10/month)                              │
│  OUTPUT: 35-40 high-quality candidates → screener_candidates.json│
│                                                                  │
│  PHASE 3: COMPOSITE SCORING & SELECTION:                        │
│  • RS percentile ranking across universe                        │
│  • Sector rotation analysis (11 sectors vs SPY)                │
│  • Claude's tier assignments integrated                         │
│  • Top 40 candidates selected for GO command                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STAGE 2: DECISION-MAKING (GO Command)              │
│                     (Claude AI Analysis)                         │
│                                                                  │
│  CONTEXT LOADED (load_optimized_context):                       │
│  • Strategy rules (8000 chars, auto-updated by learning)       │
│  • Learning database context (v8.1):                           │
│    - ACTIVE critical failures (surfaced until resolved)        │
│    - Catalyst performance stats by type                        │
│    - Actionable insights from past trades                      │
│  • Catalyst exclusions (<40% win rate triggers warnings)       │
│  • Current portfolio positions                                  │
│  • Account status                                               │
│                                                                  │
│  CLAUDE ANALYZES:                                               │
│  • VIX regime (5 levels: VERY_LOW → EXTREME)                   │
│  • Market breadth (HEALTHY/DEGRADED/UNHEALTHY)                 │
│  • Cluster-based conviction scoring (max 11 factors)           │
│    - Momentum cluster (cap +3): RS, sector strength            │
│    - Institutional cluster (cap +2): options, dark pool        │
│    - Catalyst cluster (no cap): tier, multi-catalyst, news     │
│    - Market cluster (cap +2): VIX conditions                   │
│  • Dynamic position sizing (6-13% based on conviction + regime)│
│  • Historical performance accountability                        │
│                                                                  │
│  DECISIONS:                                                      │
│  • BUY: 0-10 positions (skips trades if market UNHEALTHY)      │
│  • HOLD: Continue existing positions                            │
│  • EXIT: Flag positions for rotation if better opportunities   │
│  OUTPUT: pending_positions.json → EXECUTE command              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│     STAGE 3: EXECUTION (EXECUTE + EXIT + ANALYZE Commands)      │
│                    🔗 ALPACA API INTEGRATION (v8.2)             │
│                                                                  │
│  PORTFOLIO LOADING:                                              │
│  • Loads positions from Alpaca API (not JSON file - v8.0)      │
│  • Syncs real-time position data (shares, entry price, P/L)    │
│  • Graceful fallback to JSON if Alpaca unavailable             │
│                                                                  │
│  EXECUTE (9:45 AM - 15 min after market open):                  │
│  • Validates gap-aware entry (<3%: enter, 3-8%: caution, >8%: skip) │
│  • Checks bid-ask spread (skip if >0.5% - v7.0)                │
│  • Calculates position size (conviction × market breadth adj)  │
│  • Sets ATR-based stop loss (2.5x ATR, capped at -7% - v7.0)  │
│  • Sets price target (dynamic based on catalyst type)          │
│  • PLACES REAL ORDERS via Alpaca API:                          │
│    - BUY: Market orders for new positions                      │
│    - TRAILING STOP: Alpaca orders for +10% positions (v8.1)   │
│    - Validates buying power before buys                        │
│    - Logs all order IDs for tracking                           │
│                                                                  │
│  EXIT (3:45 PM - 15 min before market close) [NEW v8.2]:        │
│  • Fetches REAL-TIME prices from Alpaca (not delayed Polygon)  │
│  • Checks for Alpaca trailing stop fills                       │
│  • Applies exit rules:                                          │
│    - Stop loss (-7%)                                            │
│    - Price target (+10%)                                        │
│    - Time stop (21 days)                                        │
│    - News invalidation (score ≥70)                             │
│  • Claude reviews remaining positions for discretionary exits   │
│  • FAILSAFE: If Claude timeout (60s), executes auto rules only │
│  • PLACES SELL ORDERS via Alpaca - execute BEFORE close        │
│  • OUTPUT: Updates portfolio, logs closed trades to CSV         │
│                                                                  │
│  ANALYZE (4:30 PM - after market close) [REFACTORED v8.2]:      │
│  • NO ORDER EXECUTION - learning/summary only                   │
│  • Updates portfolio with closing prices for P&L display        │
│  • Creates daily activity summary                               │
│  • Calls Claude for performance analysis                        │
│  • Updates learning database                                    │
│  OUTPUT: Daily summary, learning insights                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STAGE 4: LEARNING (Continuous Improvement)         │
│                                                                  │
│  TRADE COMPLETION (when position exits):                        │
│  • Logs 63-column CSV with complete trade attribution:         │
│    - Technical: SMA50, EMA5, EMA20, ADX, Volume Ratio, Score   │
│    - Volume: Quality (EXCELLENT/STRONG/GOOD), Trending (T/F)   │
│    - Keywords: Matched keywords from news                       │
│    - News: Sources, article count                              │
│    - RS Rating: 0-100 percentile rank                          │
│    - Supporting Factors: Cluster-based conviction count        │
│    - VIX Regime: 5 levels (VERY_LOW → EXTREME)                 │
│    - Market Breadth Regime: 3 levels (HEALTHY/DEGRADED/UNHEALTHY) │
│    - System Version: v7.0 (tracks code version per trade)      │
│                                                                  │
│  SCHEDULED LEARNING ANALYSIS:                                   │
│  • DAILY (5:00 PM): 7-day tactical analysis (quick losers)     │
│  • WEEKLY (Fridays 5:30 PM): 30-day pattern detection          │
│  • MONTHLY (Last Sunday 6:00 PM): 90-day strategic review      │
│                                                                  │
│  LEARNING OUTPUTS:                                              │
│  • learning_database.json: Structured learning data (v8.1)     │
│    - Critical failures (ACTIVE/RESOLVED)                       │
│    - Catalyst performance by type                              │
│    - Market regime performance                                  │
│    - Entry/exit timing patterns                                │
│    - Hypotheses under test                                      │
│  • catalyst_exclusions.json: <40% win rate → exclusion list    │
│  • lessons_learned.md: Proven patterns (70%+) vs failures (<40%)│
│  • strategy_rules.md: Auto-updated position sizing rules       │
│  • catalyst_performance.csv: Win rates by catalyst type        │
│  SAVED TO: strategy_evolution/ directory                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │   FEEDBACK LOOP   │
                    │    CLOSES HERE    │
                    └──────────────────┘
                              ↓
              Learning insights loaded into STAGE 2
              (Claude sees historical performance in next GO command)
```

### Key System Properties

**Autonomy**: Runs 24/7 without human intervention
- Automated scheduling via cron (screener, GO, EXECUTE, ANALYZE, learning)
- Self-healing: AI failover if Claude API fails (holds positions, skips entries, logs failure)
- Self-improving: Learning system automatically excludes underperforming catalysts
- Health monitoring: Daily 5pm ET health checks with dashboard alerts

**Risk Management**: Institutional-grade safety mechanisms
- VIX shutdown: Stops trading at VIX >30, exits all at stops
- Market breadth filter: Reduces sizing by 40% in UNHEALTHY markets
- Cluster-based conviction: Prevents double-counting correlated signals (max 11 factors)
- Sector concentration: Max 2 per sector (3 in leading sectors)
- Liquidity filter: Min $50M daily volume prevents slippage

**Transparency**: Complete performance visibility
- Public dashboard: YTD/MTD returns, win rate, Sharpe ratio, max drawdown
- Regime analysis: Performance by VIX regime (5 levels) and market breadth (3 levels)
- Conviction tracking: HIGH/MEDIUM/LOW distribution and accuracy
- Sector attribution: Top performing sectors
- Version tracking: System_Version column tracks which code generated each trade

**Learning**: Closed-loop continuous improvement
- Trade → CSV (63 columns) → Learning (daily/weekly/monthly) → Insights (exclusions, lessons, rules) → Claude Context → Decision → Trade
- Historical performance directly informs future decisions
- Catalyst exclusions presented as warnings with accountability tracking
- Deviations from learning recommendations require explanation and are logged

---

## The Complete Trading Workflow

### Phase 1: Stock Identification (Hybrid Screener v10.1)

**Tool**: `market_screener.py`
**Schedule**: 7:00 AM ET daily (scans 993 S&P 1500 stocks)
**Data Sources**: Polygon.io (price/volume), Claude API (catalyst analysis)
**Architecture**: v10.1 - Binary Gates + Claude AI (January 1, 2026)

**PHILOSOPHY**: *"If it's not binary, Claude decides"*

#### Three-Phase Hybrid Architecture:

**PHASE 1: Binary Hard Gates** (Objective Filters Only)
   - **Price ≥ $10**: Liquidity, institutional participation
   - **Daily Volume ≥ $50M**: Execution quality, slippage prevention
   - **Data Freshness**: Traded in last 5 days (active stocks only)
   - **Result**: ~250 stocks pass binary gates (vs 5-10 with keyword filtering)

**PHASE 2: Claude AI Catalyst Analysis** (ALL Sentiment & Catalyst Decisions)
   - **Coverage**: Analyzes ALL ~250 stocks (vs 3-5 in v9.0) = **83x more coverage**
   - **Negative News Detection**:
     - Dilutive offerings, secondary offerings
     - Lawsuits, investigations, regulatory issues
     - Analyst downgrades, price target cuts
     - Guidance cuts, earnings misses
     - **Action**: Automatically rejects stocks with negative flags

   - **Catalyst Identification** with Nuanced Context:
     - **Tier 1** (FDA approvals/priority review, M&A targets >15%, earnings beats >10% + guidance raise)
     - **Tier 2** (Analyst upgrades, product launches, moderate earnings beats)
     - **Tier 3** (Sector rotation, industry tailwinds - supporting only)
     - **Tier 4** (52-week breakouts, gap-ups - technical)

   - **Critical Nuance Detection**:
     - "FDA Priority Review" (bullish Tier 1) vs "FDA delays review" (bearish reject)
     - "M&A target" (bullish Tier 1) vs "M&A acquirer" (often dilutive reject)
     - "Earnings beat" (bullish) vs "Earnings miss" (bearish reject)
     - "Upgraded to Buy" (bullish Tier 2) vs "Downgraded" (bearish reject)

   - **Confidence Scoring**: High/Medium/Low on each catalyst
   - **Multi-Catalyst Recognition**: Bonus for multiple catalysts (earnings + guidance + upgrade)
   - **Rate Limiting**: 5 concurrent workers, exponential backoff (2s, 4s, 8s, 16s, 32s)
   - **Cost**: ~$0.07 per run (~$2.10/month at daily frequency)
   - **Result**: 35-40 high-quality candidates accepted, 210+ rejected

**PHASE 3: Composite Scoring & Selection**

1. **RS Percentile Ranking** (IBD-Style 0-100)
     - Calculated across full universe (993 stocks)
     - 90+: Top 10% of market (elite)
     - 80-89: Top 20% (strong)
     - 70-79: Top 30% (good)
     - **Note**: RS is informational scoring factor, NOT hard filter

2. **Sector Rotation Analysis**
     - Tracks 11 sector ETFs vs SPY benchmark
     - **Leading Sectors**: >2% outperformance vs SPY (3-month)
     - **Lagging Sectors**: <-2% underperformance vs SPY
     - Prioritizes stocks from leading sectors in GO command

3. **Composite Score Calculation**
     - Integrates Claude's tier assignments
     - Base score from RS and technical setup
     - **Tier 1 High Confidence**: +15 points bonus
     - **Tier 2 High Confidence**: +10 points bonus
     - **Multi-Catalyst**: +5 points additional bonus

4. **Top 40 Selection**
     - Sorted by tier-first (Tier 1 > Tier 2 > Tier 3 > Tier 4)
     - Within each tier, sorted by composite score
     - Top 40 candidates selected for GO command analysis

**Output**: Top 40 catalyst-driven candidates saved to `screener_candidates.json`

#### v10.1 Results vs Previous (Keyword-Based):

| Metric | v9.0 (Keywords) | v10.1 (Hybrid) | Improvement |
|--------|-----------------|----------------|-------------|
| **Stocks Analyzed by Claude** | 3-5 | 249 | **83x more** |
| **Coverage** | 0.3% | 25% | **83x more** |
| **Tier 1 Finds** | 1 | 3 | **3x more** |
| **False Negatives** | High | Low | **Eliminated** |
| **Cost per Run** | $0.01 | $0.07 | **7x ($2.10/mo)** |

**Example Improvements** (Actual Results - Jan 1, 2026):
- ✅ AXSM FDA Priority Review: Now Tier 1 (was Tier 3 "sector rotation")
- ✅ BBIO M&A Speculation: Now Tier 1 (was filtered out by keywords)
- ✅ BA Pentagon Contract: Now Tier 1 (was filtered out by keywords)
- ✅ 429 Rate Limit Errors: All successfully retried with exponential backoff

---

### Phase 2: Morning Analysis (GO Command)

**Tool**: `agent_v5.5.py go`
**Schedule**: 9:00 AM ET daily (15 minutes before market open)
**Purpose**: Claude reviews screener candidates and selects best opportunities

#### Claude's Analysis Process:

1. **News Validation** (0-20 points)
   - Analyzes 3-5 most recent news articles
   - Scores catalyst strength, credibility, recency
   - Validates the story isn't already "played out"
   - Checks for negative sentiment or red flags

2. **VIX/Market Regime Check** (Regime-Dependent Tier Policy)
   - **VIX < 20**: GREEN (normal trading, all tiers accepted)
   - **VIX 20-25**: YELLOW (caution, reduce position sizing, all tiers accepted)
   - **VIX 25-30**: ORANGE (elevated risk, **Tier 1 or Tier 2 ONLY** - no Tier 3/4)
   - **VIX 30-35**: HIGH RISK (**Tier 1 ONLY** + News ≥15/20 required)
   - **VIX ≥ 35**: RED (SHUTDOWN - no new trades)

3. **Macro Event Check** (Event-Day Only Blackouts)
   - **FOMC Meeting**: Day of only (2:00 PM announcement + press conference)
   - **CPI Release**: Day of only (8:30 AM release, 9:45 AM entries are post-volatility)
   - **NFP (Jobs Report)**: Day of only (8:30 AM release)
   - **PCE (Inflation)**: Day of only (8:30 AM release)
   - **Policy**: Blocks ALL new entries on event day only (aligned with institutional best practices)
   - **Rationale**: Comprehensive screening process (RS, technical, institutional signals) handles volatility

4. **Market Breadth & Regime Filter** (Deep Research Alignment - Dec 15)
   - **Market Breadth**: % of stocks above 50-day MA (from screener data)
   - **Three Regimes** (breadth-based only):
     - **HEALTHY** (breadth ≥50%): 100% position sizing, 1.1x VIX multiplier
     - **DEGRADED** (breadth 40-49%): 80% position sizing, 1.0x VIX multiplier
     - **UNHEALTHY** (breadth <40%): 60% position sizing, 0.7x VIX multiplier
   - **Hard Filters** (GO/NO-GO eliminate low-quality opportunities):
     - Price >$10 (Deep Research spec)
     - Liquidity >$50M daily volume (Deep Research spec)
     - Catalyst presence required (Tier 1-4, regime-dependent acceptance)
     - Normal Markets (VIX <25): Tier 1, 2, 3, or 4 acceptable
     - Elevated Risk (VIX 25-30): Tier 1 or 2 ONLY (no Tier 3/4)
     - High Risk (VIX 30-35): Tier 1 ONLY + News ≥15/20
   - **Scoring Factors** (100-point Entry Quality Scorecard):
     - RS vs SPY is scoring factor (0-5 pts), NOT hard filter
     - Allows negative-RS stocks if strong catalyst present
     - AI evaluates full scorecard, selects best opportunities
   - Applied as multiplier to base conviction sizing

5. **Conviction Scoring** (Phase 4.1 - Cluster-Based)
   - **Prevents double-counting correlated signals via clustering**
   - **Momentum Cluster** (cap +3):
     - RS ≥90th percentile: +2 factors (DOUBLE WEIGHT)
     - RS 80-89th percentile: +1 factor
     - RS >7% sector outperformance: +1 factor
     - Leading sector (+2% vs SPY): +1 factor
   - **Institutional Cluster** (cap +2):
     - Unusual options flow: +1 factor
     - Dark pool accumulation: +1 factor
   - **Catalyst Cluster** (no cap - independent signals):
     - Tier 1 catalyst: +1 factor
     - Multi-catalyst: +1 factor
     - Revenue beat (EPS + Revenue): +1 factor
     - News score >15/20: +1 factor
   - **Market Conditions Cluster** (cap +2):
     - VIX <20: +1 factor
   - **Maximum possible score**: 11 factors (down from 14+ in Phase 3)

   - **Conviction Levels** (base sizing, before market breadth adjustment):
     - **HIGH** (7+ factors): 13% position size
     - **MEDIUM-HIGH** (5-6 factors): 11% position size
     - **MEDIUM** (3-4 factors): 10% position size
     - **SKIP** (<3 factors): Pass on trade
   - **Final Position Size** = Base Size × Market Breadth Adjustment
   - **Example**: HIGH conviction (13%) in DEGRADED market = 13% × 0.8 = 10.4% actual position

6. **Dynamic Profit Targets** (Enhancement 1.2)
   - **M&A targets**: +15% (stretch +20%)
   - **FDA approvals**: +15% (stretch +25%)
   - **Big earnings beats** (>20%): +12% (stretch +15%)
   - **Standard earnings beats**: +10%
   - **Tier 2 catalysts**: +8%
   - **Tier 3 (insider buying)**: +10% (longer hold: 10-20 days)

6. **Entry Timing Refinement** (Enhancement 1.6)
   - **Avoids** extended moves:
     - >5% above 20-day MA (wait for pullback)
     - 3x+ volume (climax, reversal risk)
     - Up >10% in 3 days (overheated)
     - RSI >70 (overbought)
   - **Entry Quality**:
     - GOOD: No timing issues
     - CAUTION: 1-2 issues
     - POOR: 3+ issues (skip or wait)

7. **Post-Earnings Drift Detection** (Enhancement 1.4)
   - **Strong PED** (Earnings +20%, Revenue +10%, Guidance raised):
     - Target: +12%, Hold: 30-60 days
   - **Medium PED** (Earnings +15%):
     - Target: +10%, Hold: 20-40 days

**Output**:
- BUY recommendations with conviction levels, position sizes, profit targets
- Detailed thesis for each position
- Saved to `daily_reviews/go_YYYYMMDD_HHMMSS.json`

---

### Phase 3: Trade Execution (EXECUTE Command)

**Tool**: `agent_v5.5.py execute`
**Schedule**: 9:45 AM ET daily (15 minutes after market open)
**Purpose**: Execute BUY orders and manage existing positions

#### Execution Logic:

1. **Position Capacity Check**
   - Max 10 positions at a time
   - If portfolio full → Skip to Portfolio Rotation evaluation

2. **Pre-Execution Validation**
   - Fetch current market price
   - Verify stock hasn't gapped >8% (gap-awareness)
   - Check if still in Stage 2 uptrend
   - Confirm volume and technical filters still valid

3. **Gap-Aware Entry** (Enhancement 0.1)
   - **Gap <3%**: Normal entry at market price
   - **Gap 3-5%**: Entry with caution (potential pullback)
   - **Gap 5-8%**: Wait for 1-day consolidation
   - **Gap >8%**: Skip (too extended, high reversal risk)

4. **Position Sizing** (Enhanced Phase 4)
   - **Base Conviction Sizing**:
     - HIGH (7+ factors): 13% base
     - MEDIUM-HIGH (5-6 factors): 11% base
     - MEDIUM (3-4 factors): 10% base
   - **Market Breadth Adjustment** (Phase 4.2):
     - HEALTHY market: 1.0x (no adjustment)
     - DEGRADED market: 0.8x (reduce by 20%)
     - UNHEALTHY market: 0.6x (reduce by 40%)
   - **Final Position Size** = Base × Breadth Adjustment
   - **Effective Range**: 6% (MEDIUM in UNHEALTHY) to 13% (HIGH in HEALTHY)
   - **Example**: HIGH conviction (13%) + DEGRADED market → 13% × 0.8 = 10.4% actual

5. **Stop Loss Calculation** (v7.0 ATR-Based)
   - Formula: `stop_pct = -min(2.5*ATR/entry_price, 0.07)`
   - Volatile stocks: ATR suggests wider stop → capped at -7%
   - Stable stocks: ATR suggests tighter stop → used as-is (e.g., -4%, -5%)
   - Logged to CSV: Stop_Loss (price), Stop_Pct (percentage)

6. **Price Target Calculation**
   - Based on catalyst type (see Dynamic Profit Targets above)
   - Trailing stop activates when target is hit

7. **Position Metadata Stored**
   ```
   - Entry date/time
   - Entry price
   - Position size (shares)
   - Stop loss price
   - Price target
   - Catalyst details
   - Conviction level
   - Supporting factors count
   - Technical indicators (50-day MA, 5/20 EMA, ADX, Volume ratio)
   - RS rating (0-100)
   - Volume quality (EXCELLENT/STRONG/GOOD)
   - Volume trending (True/False)
   ```

**Output**:
- Executed trades logged to `trade_history/completed_trades.csv`
- Current positions saved to `active_positions.json`
- Execution results saved to `daily_reviews/execute_YYYYMMDD_HHMMSS.json`

---

### Phase 4: Portfolio Rotation (When Portfolio Full)

**Triggered**: When portfolio has 10/10 positions AND new strong opportunities exist
**Purpose**: Swap underperforming positions for better opportunities

#### Quantitative Rotation Scoring (Enhancement 2.3):

**Exit Candidate Scoring** (0-100, higher = better to exit):
- Weak momentum (<0.3%/day): +30 points
- Stalling (>5 days, <+3% gain): +25 points
- Underwater (<-2%): +40 points
- Low-tier catalyst (Tier 2/3): +15 points
- **Threshold**: Must score ≥50 to be rotation candidate

**Entry Opportunity Scoring** (0-100, higher = better):
- Tier 1 catalyst: +40 points
- Fresh news (<24 hours): +30 points
- High news validation (>80/100): +20 points
- Strong RS rating (>75): +10 points
- **Threshold**: Must score ≥60 to be worth rotating into

**Rotation Decision**:
- Only recommends if exit score ≥50 AND entry score ≥60
- Calculates net score (entry score - (100 - exit score))
- Positive net score = favorable swap
- Claude provides final review and approval

**Output**:
- Exits underperformer
- Enters new opportunity
- Rotation metadata tracked in CSV

---

### Phase 5: Evening Analysis (ANALYZE Command)

**Tool**: `agent_v5.5.py analyze`
**Schedule**: 4:30 PM ET daily (30 minutes after market close)
**Purpose**: Review positions, check for exit conditions

#### Exit Decision Process:

1. **Fetch End-of-Day Prices**
   - Gets 4:00 PM market close prices
   - Calculates current P&L for all positions

2. **Exit Condition Checks**

   **AUTOMATIC EXITS** (Rule-Based):
   - **Stop Loss Hit**: Price ≤ ATR-based stop (2.5x ATR, capped at -7% max - v7.0)
   - **Target Hit with Trailing Stop**:
     - If price ≥ target, activate trailing stop
     - Lock in minimum +8% gain
     - Trail by 2% from peak
     - Exit when price falls 2% below peak
   - **Time-Based**:
     - Standard positions: 7 days max
     - PED positions: 60 days max
     - Stalling positions (>5 days, <+3%): Consider exit

3. **Gap-Aware Trailing Stop** (Enhancement 1.1)
   - If large gap (>5%) to target:
     - Wait 2 days for consolidation before activating trail
     - Prevents getting shaken out by gap volatility

4. **News Invalidation Check**
   - Claude analyzes recent news (since entry)
   - **Invalidation scenarios** (0-100 points):
     - Deal fell through (M&A): 100 pts → EXIT
     - FDA rejection: 100 pts → EXIT
     - Earnings restatement: 80 pts → EXIT
     - Guidance lowered: 60 pts → Consider exit
     - Negative analyst comments: 40 pts → Monitor
   - **Threshold**: >50 points = Recommend exit

5. **Claude Final Review**
   - Reviews all positions
   - Considers news, price action, market conditions
   - Can override rules for strategic holds
   - Provides exit reasoning for each sale

**Trailing Stop Example**:
```
Entry: $100
Target: $110 (+10%)
Day 1: $105 → Hold (below target)
Day 2: $110 → Trailing stop ACTIVATED at $108 (locks +8%)
Day 3: $112 → NEW PEAK, trailing stop → $109.76 (2% below $112)
Day 4: $115 → NEW PEAK, trailing stop → $112.70 (2% below $115)
Day 5: $113 → Hold (above $112.70 trail)
Day 6: $112.70 → TRAILING STOP HIT, EXIT at $112.70 (+12.7%)
```

**Output**:
- Exit decisions executed
- Trade results logged to CSV with:
  - Exit date/time
  - Exit price
  - Return %
  - Hold days
  - Exit reason (Target Hit, Stop Loss, News Invalidation, Time-Based, etc.)
  - What worked (thesis validation)
  - What failed (if applicable)
- Saved to `daily_reviews/analyze_YYYYMMDD_HHMMSS.json`

---

## Key Enhancements Summary

### Phase 0: Foundation (4 Enhancements)
1. **Gap-Aware Entry/Exit** (Enhancement 0.1)
2. **News Validation Scoring** (Enhancement 0.2)
3. **Sector Concentration Limits** (Enhancement 0.3)
4. **Market Regime Filter** (Enhancement 0.4)

### Phase 1: Core Trading Logic (6 Enhancements)
1. **Trailing Stops** (Enhancement 1.1) - Let winners run
2. **Dynamic Profit Targets** (Enhancement 1.2) - Catalyst-specific targets
3. **Conviction Scoring** (Enhancement 1.3) - Position sizing by strength
4. **Post-Earnings Drift** (Enhancement 1.4) - 30-60 day holds for big beats
5. **Stage 2 Alignment** (Enhancement 1.5) - Minervini trend filter
6. **Entry Timing Refinement** (Enhancement 1.6) - Avoid chasing

### Phase 2: Optimization (4 Enhancements)
1. **RS Rank Percentile** (Enhancement 2.1) - 0-100 RS ratings
2. **Volume Confirmation** (Enhancement 2.2) - Quality + trend scoring
3. **Portfolio Rebalancing** (Enhancement 2.3) - Quantitative rotation
4. **Performance Attribution** (Enhancement 2.4) - Track what works

### Phase 3: RS & Sector Intelligence (4 Enhancements) ✅ COMPLETED
1. **IBD-Style RS Percentile Ranking** (Enhancement 3.1) - Market-wide 0-100 ranking vs all stocks
2. **Sector Rotation Detection** (Enhancement 3.2) - Track 11 sectors vs SPY, prioritize leading sectors
3. **Institutional Activity Signals** (Enhancement 3.3) - Options flow + dark pool tracking
4. **GO Command Integration** (Enhancement 3.4) - Enhanced conviction scoring with Phase 3 data

### Phase 4: Risk Optimization & Anti-Overlap (8 Enhancements) ✅ COMPLETED
1. **Cluster-Based Conviction Scoring** (Enhancement 4.1) - Prevent double-counting correlated signals
   - Groups factors into 4 clusters: Momentum (cap +3), Institutional (cap +2), Catalyst (no cap), Market (cap +2)
   - Reduces max score from 14+ → 11 factors
2. **Market Breadth & Trend Filter** (Enhancement 4.2) - Regime-based position sizing
   - SPY trend + market breadth analysis
   - Three regimes: HEALTHY (1.0x), DEGRADED (0.8x), UNHEALTHY (0.6x)
   - Prevents overtrading in rotational/choppy markets
3. **Sector Concentration Reduction** (Enhancement 4.3) - Reduce correlated drawdown risk
   - Max 2 positions per sector (down from 3)
   - Exception: Allow 3 in top 2 leading sectors (+2% vs SPY)
4. **Liquidity Filter** (Enhancement 4.4) - Prevent execution slippage
   - Minimum $50M average daily dollar volume
   - Filters low-liquidity stocks at screener level
5. **VIX Regime Logging** (Enhancement 4.5) - Track market conditions for learning & attribution
   - Classifies VIX into 5 regimes: VERY_LOW (<15), LOW (15-20), ELEVATED (20-25), HIGH (25-30), EXTREME (≥30)
   - Logs VIX_Regime and Market_Breadth_Regime to CSV for every trade
   - Enables performance analysis across different market conditions
6. **AI Robustness & Failover** (Enhancement 4.6) - Graceful degradation when Claude API fails
   - GO command failure → HOLD existing positions, skip new entries
   - ANALYZE command failure → Skip commentary, core operations completed
   - Logs all failures to logs/claude_api_failures.json
   - Automatic retry on next command execution
7. **Operational Monitoring** (Enhancement 4.7) - Health checks, alerting, version tracking
   - health_check.py: Automated health monitoring (command execution, API connectivity, data freshness)
   - Dashboard integration for real-time health display
   - System version tracking (System_Version column in CSV)
   - Daily health checks at 5pm ET via cron
8. **Public Model Portfolio Display** (Enhancement 4.8) - Performance transparency & regime analysis
   - YTD/MTD returns with color-coded display
   - Win rate, avg gain/loss, max drawdown, Sharpe ratio
   - Conviction distribution tracking (HIGH/MEDIUM/LOW)
   - Performance by VIX regime (5 levels)
   - Performance by market breadth regime
   - Top sector performance attribution
   - Auto-refresh every 5 minutes on dashboard

---

## Performance Tracking & Learning

### Learning Command (python agent_v5.5.py learn)
Analyzes past performance across multiple dimensions:

1. **Conviction Accuracy**
   - Do HIGH conviction trades outperform MEDIUM?
   - Validates position sizing strategy

2. **Catalyst Tier Performance**
   - Which catalyst types deliver best returns?
   - Tier 1 vs Tier 2 vs Tier 3 comparison

3. **VIX Regime Performance**
   - How do different market conditions affect returns?
   - Validates risk-off thresholds

4. **News Score Effectiveness**
   - Does higher news validation = better returns?
   - Validates news filtering

5. **Relative Strength Impact**
   - RS positive (≥3%) vs RS negative (<3%)
   - Validates sector rotation strategy

6. **Enhancement Tracking** (NEW in Phase 2)
   - **RS Rating**: Elite (85+) vs Good (65-85) vs Weak (<65)
   - **Volume Quality**: EXCELLENT (3x) vs STRONG (2x) vs GOOD (1.5x)
   - **Volume Trending**: Trending Up vs Flat/Declining

**Output**: JSON reports saved to `learning_data/` for continuous improvement

---

## Data Storage & Audit Trail

### Files Created:

1. **`active_positions.json`** - Current portfolio (updated 3x daily)
2. **`trade_history/completed_trades.csv`** - Complete trade log with 50+ metrics
3. **`daily_reviews/go_*.json`** - Morning analysis (BUY recommendations)
4. **`daily_reviews/execute_*.json`** - Trade execution results
5. **`daily_reviews/analyze_*.json`** - Evening analysis (EXIT decisions)
6. **`screener_candidates.json`** - Latest screener results
7. **`learning_data/*.json`** - Performance attribution reports
8. **`daily_picks.json`** - Dashboard display (accepted + rejected picks)

### CSV Trade History Columns (63 fields):
- Basic: Ticker, Entry/Exit Date, Entry/Exit Price, Return %, Hold Days
- Position: Shares, Position Size $, Account Value Before/After
- Catalyst: Type, Tier, News Score, Catalyst Details
- Risk: Stop Loss, Stop_Pct (v7.1.1), Price Target, Max Drawdown
- Technical: 50-day MA, 5/20 EMA, ADX, Volume Ratio, Volume Quality, RS Rating
- Conviction: Level, Supporting Factors Count
- Market: VIX at Entry, Market Regime, Macro Events, VIX_Regime, Market_Breadth_Regime (Phase 4.5)
- System: System_Version (v4.7), Ruleset_Version (v7.1), Universe_Version (v7.1.1)
- Execution: Entry_Bid, Entry_Ask, Entry_Mid_Price, Entry_Spread_Pct, Slippage_Bps (v7.1)
- Exit: Reason, Trailing_Stop_Activated, Trailing_Stop_Price, Peak_Return_Pct (v7.1), What Worked, What Failed
- Rotation: Rotation Into Ticker, Rotation Reason (if applicable)

---

## Execution Schedule (Automated via Cron)

```
8:00 AM - Market Screener starts scanning
9:00 AM - GO command (Claude analyzes opportunities)
9:45 AM - EXECUTE command (Place BUY orders)
4:30 PM - ANALYZE command (Review positions, place SELL orders)
```

---

## Risk Management Framework

### Position-Level Risk:
- **Position sizing** (v7.0):
  - Base: 10-13% (MEDIUM to HIGH conviction)
  - Market breadth adjustment: 0.6x-1.0x multiplier
  - **Effective range**: 6% (MEDIUM in UNHEALTHY) to 13% (HIGH in HEALTHY)
  - **Typical max**: ~10-11% in normal/degraded markets
- **Stop loss** (v7.0 ATR-based): 2.5x ATR(14), capped at -7% maximum
  - Volatile stocks: -7% cap (prevents excessively wide stops)
  - Stable stocks: Tighter stops (e.g., -5% if ATR is low)
  - Adapts to each stock's natural volatility
- **Spread check** (v7.0): Skip trades if bid-ask spread >0.5%
- **Max hold time**: 7 days standard, 60 days for PED

### Portfolio-Level Risk:
- **Max positions**: 10 (diversification)
- **Sector concentration** (Phase 4.3): Max 2 positions per sector (3 allowed in top 2 leading sectors)
- **Sector rotation aware**: Prioritize leading sectors (+2% vs SPY)
- **Market breadth filter** (Phase 4.2): Reduces exposure in rotational/choppy markets
- **Liquidity floor** (Phase 4.4): Min $50M daily dollar volume (prevents slippage)
- **Market regime**: SHUTDOWN at VIX >30
- **Macro events**: Event-day only blackouts (FOMC, CPI, NFP, PCE) - aligned with institutional best practices

### Trade-Level Risk:
- **No revenge trading**: Each trade is independent
- **No averaging down**: Only one entry per position
- **No holding losers**: -7% stop is absolute

---

## Technology Stack

- **Language**: Python 3
- **AI Engine**: Claude Sonnet 4.5 (Anthropic)
- **Data Sources**:
  - Polygon.io (price/volume data)
  - Finnhub (news articles)
- **Infrastructure**:
  - DigitalOcean VPS (Ubuntu)
  - Automated via cron
- **Dashboard**: Flask web app for monitoring

---

## What Makes Tedbot Different?

1. **AI-Powered Analysis**: Claude reads and understands news like a human analyst
2. **Catalyst-Driven**: Trades on events, not just technicals
3. **Market-Wide RS Ranking**: IBD-style percentile scoring (only trades top 20% of stocks)
4. **Sector Rotation Awareness**: Prioritizes stocks from leading sectors (+2% vs SPY)
5. **Institutional Signal Detection**: Tracks options flow and dark pool activity (FREE via Polygon)
6. **Cluster-Based Conviction**: Prevents double-counting correlated signals (max 11 factors, down from 14+)
7. **Market Breadth Filter**: Regime-based position sizing (HEALTHY/DEGRADED/UNHEALTHY)
8. **Adaptive Position Sizing**: 6-13% sizing based on conviction + market conditions
9. **Liquidity-Aware**: $50M minimum volume filter prevents execution slippage
10. **Let Winners Run**: Trailing stops capture extended moves
11. **Quantitative + Qualitative**: Combines technical filters with AI reasoning
12. **Full Transparency**: Every decision logged and traceable
13. **Continuous Learning**: Performance attribution guides optimization
14. **AI Failover Safety**: Graceful degradation when Claude API unavailable (no catastrophic trades)
15. **Operational Monitoring**: Automated health checks, dashboard alerts, version tracking per trade
16. **Public Performance Display**: Real-time YTD/MTD metrics, regime analysis, complete transparency

---

## Example Trade Lifecycle

**Stock: NVDA**

**1. Identification (Screener):**
- Catalyst: Earnings beat +25%, revenue beat +15%, guidance raised
- Technical: Above 50-day MA, 5 EMA > 20 EMA, ADX 28, Volume 3.2x (EXCELLENT)
- RS: +12% vs SMH (sector), RS Rating: 85 (STRONG)
- Stage 2: All 5 checks pass ✓

**2. Analysis (GO - 9:00 AM):**
- News Score: 18/20 (5 articles, all positive, fresh <12hrs)
- VIX: 18 (GREEN - normal trading)
- Sector: Technology (Leading sector, +3.4% vs SPY)
- RS Percentile: 92 (top 8% of all stocks)
- Institutional Signals: Dark pool accumulation detected (2.1x volume)
- Conviction: HIGH (9 supporting factors)
  - Tier 1 catalyst ✓
  - RS >7% ✓
  - **RS 92nd percentile (top 10%)** ✓✓ (double weight)
  - **Leading sector (+3.4% vs SPY)** ✓
  - Fresh news (<12hrs) ✓
  - Volume >2x ✓
  - News >15/20 ✓
  - ADX >25 ✓
  - **Dark pool accumulation** ✓
  - **Revenue beat (EPS + Revenue)** ✓
- Position Size: 13% ($130)
- Target: +12% (Strong PED detected)
- Hold: 30-60 days (earnings drift)

**3. Execution (EXECUTE - 9:45 AM):**
- Entry Price: $140.00
- Gap: +2.5% (normal entry)
- Shares: 0.93 shares ($130 position - HIGH conviction 13%)
- Stop Loss: $130.20 (-7%)
- Price Target: $156.80 (+12%)

**4. Position Monitoring (EXIT @ 3:45 PM + ANALYZE @ 4:30 PM):**
- Day 1: $142 (+1.4%) → HOLD
- Day 2: $145 (+3.6%) → HOLD
- Day 3: $150 (+7.1%) → HOLD
- Day 10: $156.80 (+12%) → TRAILING STOP ACTIVATED at $145.60 (+8% locked)
- Day 15: $162 (+15.7%) → NEW PEAK, trail → $158.76
- Day 20: $165 (+17.9%) → NEW PEAK, trail → $161.70
- Day 22: $163 (+16.4%) → HOLD (above trail)
- Day 23 @ 3:45 PM: $161.70 → **ALPACA TRAILING STOP TRIGGERED - SELL EXECUTED**

**5. Trade Result:**
- Entry: $140.00
- Exit: $161.70
- Return: **+15.5%**
- Hold: 23 days
- Profit: $20.16 (from $130 position vs $12.37 from old $80 position)
- Exit Reason: "Trailing stop hit (peak was +17.9%)"
- What Worked: "Strong earnings catalyst, post-earnings drift as expected, excellent volume confirmation, market-leading RS percentile (92), leading sector (Technology), institutional accumulation"

---

## Common Questions

**Q: How much does it trade?**
A: Typically 2-5 new positions per week, depending on catalyst flow. Max 10 positions at once.

**Q: What's the win rate target?**
A: 65-70% after Phase 1 enhancements (was 55% baseline).

**Q: Average return per trade?**
A: Target +12-15% on winners (up from +8% baseline), -4% on losers.

**Q: How long are positions held?**
A: Average 3-7 days. Post-earnings drift positions: 30-60 days.

**Q: What sectors does it trade?**
A: Any sector, but limits to max 2 positions per sector to avoid concentration risk (3 allowed in top 2 leading sectors).

**Q: Can it trade options?**
A: No, stock-only for now. Options require different risk management.

**Q: Does it handle earnings announcements?**
A: Yes! It specifically looks for earnings beats and uses post-earnings drift strategy for strong beats (>15% surprise).

**Q: What happens in a market crash?**
A: SHUTDOWN mode activates at VIX >30. All positions exit at stops, no new trades until VIX <25.

---

**Last Updated**: February 4, 2026
**Version**: v8.5 (Earnings Calendar Integration)
**Status**: Live in production paper trading - 6-12 month results collection period

**Latest Update (v8.5 - Feb 4, 2026)**:
- **Earnings Calendar Integration**: Claude now sees when stocks report earnings
  - **Problem Solved (MRCY Lesson)**: MRCY bought Feb 3 morning, beat estimates after hours, crashed 14% on weak guidance
  - Screener fetches earnings dates from Polygon Benzinga API
  - Candidates show warnings: "⚠️ EARNINGS TODAY (after-hours)" or "⚡ Earnings in 3 days"
  - Strategy rules updated with explicit prohibitions:
    - ❌ Never buy stocks reporting earnings TODAY
    - ❌ Never buy stocks reporting earnings TOMORROW before open
  - Rationale: "Beat and retreat" pattern - beat can be priced in, guidance matters more

**Previous Update (v8.4 - Feb 4, 2026)**:
- **Full Data Transparency**: Claude now sees ALL quant data when making decisions
  - **Problem Solved**: Claude was being second-guessed by a "conviction gate" using data Claude never saw
  - RS percentile, options flow, dark pool signals now shown in candidate view
  - Philosophy: "Give the expert all the data, trust its judgment"
- **Conviction Override Removed**: No longer overrides Claude's position sizing
  - Was: If quant factors = SKIP → force 5% position (overriding Claude)
  - Now: Quant conviction logged for attribution analysis only
  - Claude's position size recommendation is trusted
- **Sanity Checks Added**: Catch broken outputs, not judgment calls
  - Position size clamped to 0-13% range (prevents >100% allocation bugs)
  - Negative/zero position sizes rejected
  - Does NOT second-guess valid decisions

**Previous Update (v8.3 - Feb 4, 2026)**:
- **News Score Override Removed**: Was overriding Claude with stale screener news scores
  - Problem: DVN had 15-point news score from screener, but no recent news - override blocked entry
  - Fix: Removed news_score override; Claude evaluates news quality directly

**Previous Update (v8.2 - Feb 3, 2026)**:
- **EXIT/ANALYZE Architecture Split**: Separates execution from learning
  - **Problem Solved**: Orders placed after market close (4:30 PM) queued overnight, creating stale position state for next day's GO
  - **New EXIT Command (3:45 PM)**: Pre-close position review with Claude + exit rules
    - Fetches REAL-TIME prices from Alpaca (not 15-min delayed Polygon)
    - Applies exit rules (stop loss -7%, target +10%, time stop 21d, news invalidation)
    - Claude reviews positions and recommends additional exits
    - Orders execute BEFORE market close at known prices
    - Failsafe: If Claude API times out (60s), executes automated rules only with full visibility logging
  - **Refactored ANALYZE Command (4:30 PM)**: Now learning-only, no order execution
    - Updates portfolio with closing prices for accurate P&L display
    - Creates daily activity summary from trade log
    - Calls Claude for performance analysis and learning insights
    - No order execution risk
  - **Benefits**:
    - Exits at known prices (no overnight gap risk)
    - Clean state for next morning's GO (no pending orders)
    - Symmetric timing: +15 min after open (EXECUTE), -15 min before close (EXIT)
    - Accurate learning data based on actual fills
- **RECHECK Pricing Fix**: Now uses Alpaca real-time prices (was calling non-existent method)
- **Updated Schedule**:
  - 7:00 AM: SCREEN (filter S&P 1500)
  - 9:00 AM: GO (Claude analyzes candidates)
  - 9:45 AM: EXECUTE (buy orders + trailing stops)
  - 10:30 AM: RECHECK (gap-skipped stocks)
  - 3:45 PM: EXIT (Claude + exit rules, same-day execution)
  - 4:30 PM: ANALYZE (summary + learning only)

**Previous Update (v8.1 - Feb 2, 2026)**:
- ✅ **Trailing Stop Architecture Overhaul**: Real-time broker execution instead of JSON tracking
  - **Problem Solved**: STX trailing stop failure (Jan 30) - JSON-only tracking cost 14% in lost gains
  - **GO Phase**: Identifies positions at +10% that need trailing stop protection
  - **EXECUTE Phase (9:45 AM)**: Places Alpaca native trailing stop orders at market open
  - **Alpaca Monitoring**: Broker monitors price in real-time, executes automatically when triggered
  - **ANALYZE Phase (4:30 PM)**: Reconciles any positions auto-sold by Alpaca
  - **Impact**: Positions now have 24/7 real-time trailing stop protection (was only 2x daily checks)
- ✅ **Institutional Learning System**: Structured learning database replaces markdown lessons
  - **New File**: `strategy_evolution/learning_database.json`
  - **Sections**: critical_failures (ACTIVE/RESOLVED), catalyst_performance, market_regime_performance, entry_timing_patterns, exit_timing_patterns, position_sizing_outcomes, hypotheses_under_test, actionable_insights
  - **Integration**: GO and ANALYZE load learning context automatically
  - **Auto-Updates**: Trade completions automatically update catalyst performance stats
  - **Critical Failure Surfacing**: ACTIVE failures prominently shown to Claude until RESOLVED
- ✅ **RECHECK Command Fix**: Returns success when nothing to recheck
  - **Problem**: Exit code 1 when no skipped stocks (incorrectly showed as "failed" in cron)
  - **Fix**: Valid "nothing to do" states now return success (exit code 0)
- ✅ **Dashboard Status Display Fix**: Frontend compatibility for purchased stocks
  - **Problem**: Purchased stocks showed as "Rejected" (frontend only knew ACCEPTED/SKIPPED/OWNED)
  - **Fix**: API returns ACCEPTED status with "✅ Purchased" in decision text

**Previous Update (v10.1 - Jan 1, 2026)**:
- ✅ **HYBRID SCREENER ARCHITECTURE**: Complete redesign - Binary Gates + Claude AI
  - **Philosophy**: "If it's not binary, Claude decides"
  - **Removed ALL keyword-based filtering**: No more false negatives
  - **Phase 1 - Binary Hard Gates**: Price ≥$10, Volume ≥$50M, Data freshness only
  - **Phase 2 - Claude AI Analysis**: Analyzes ALL ~250 stocks (83x more than v9.0)
    - Negative news detection (offerings, lawsuits, downgrades)
    - Catalyst identification with nuance (FDA Priority Review vs delays)
    - Tier classification (Tier 1/2/3/4/None)
    - Confidence scoring (High/Medium/Low)
  - **Phase 3 - Composite Scoring**: RS percentiles, sector rotation, top 40 selection
  - **Rate Limiting**: 5 concurrent workers, exponential backoff (2s, 4s, 8s, 16s, 32s)
  - **Cost**: ~$0.07/run (~$2.10/month) - 7x increase but worth it for quality
  - **Results** (Jan 1, 2026 test):
    - 249 stocks analyzed (vs 3-5 in v9.0)
    - 3 Tier 1 catalysts found: AXSM (FDA), BBIO (M&A), BA (Contract)
    - 35 total candidates accepted (vs 5-10 with keywords)
    - 0 max retries exceeded (all 429 errors successfully retried)
  - **Impact**: Eliminated false negatives like AXSM FDA Priority Review (was scored 4/20 by keywords, now correctly Tier 1)

**Previous Updates (v7.1.1 - Reporting & Analysis Tools - Dec 16)**:
- ✅ **Stop_Pct Column**: Added to CSV for stop distance distribution analysis
  - Tracks actual stop percentage used per trade (e.g., -5.2%, -7.0%)
  - Enables analysis: "What % of trades use ATR vs -7% cap?"
  - Distribution metrics: median, P25, P75, P90 stop distances
- ✅ **Universe_Version Tracking**: SHA256 hash of S&P 1500 constituent list
  - Prevents breadth drift due to constituent changes (IPOs, delistings)
  - Example: Dec 2025 (993 stocks) → v7.1.1-abc123de, Jan 2026 (1012 stocks) → v7.1.1-xyz789ab
  - Enables analysis: "Did performance change due to universe shift?"
- ✅ **Execution Cost Report**: Slippage distribution analysis by regime/spread
  - Script: reports/execution_cost_report.py
  - Analyzes median, P90, P99 slippage across: VIX regime, market breadth, entry spread, catalyst tier
  - Benchmarks: Median <5 bps (good), P90 <20 bps (acceptable)
- ✅ **Exit Quality Report**: Trailing stop effectiveness analysis
  - Script: reports/exit_quality_report.py
  - Analyzes: activation rate, peak returns, giveback distribution, capture rate
  - Benchmarks: 80%+ capture rate, <3% median giveback, 40%+ activation rate
- ✅ **Edge Attribution Report**: Expectancy analysis by multiple dimensions
  - Script: reports/edge_attribution_report.py
  - Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)
  - Analyzes edge by: catalyst tier/type, RS rating, volume quality, conviction, VIX regime, market breadth
  - Identifies which factors drive highest edge
- ✅ **ATR Stop Terminology Fix**: Changed "floor" to "cap" with explicit formula
  - Formula: stop_pct = -min(2.5*ATR/entry_price, 0.07)
  - Clarifies: -7% is maximum loss cap, system uses tighter of ATR vs cap

**Previous Updates (v7.1 - Validation Improvements - Dec 15)**:
- ✅ **RULESET_VERSION Tracking**: SHA256 hash of trading rules (prevents policy drift)
  - Hash includes: GO prompt + strategy_rules.md + catalyst_exclusions.json
  - Logged to CSV: Ruleset_Version (e.g., v7.1-31cd61c9)
  - Enables clean A/B testing without confounding variables
- ✅ **Slippage Modeling**: Track execution costs beyond bid-ask spread
  - Added 5 CSV columns: Entry_Bid, Entry_Ask, Entry_Mid_Price, Entry_Spread_Pct, Slippage_Bps
  - Calculate: slippage_bps = (fill_price - mid_price) / mid_price * 10000
  - Enables distribution analysis: median, P90, P99 slippage
- ✅ **Canonical Exit Policy**: ONE authoritative trailing stop policy documented
  - Fixed THREE contradictory policies in docs
  - Canonical: Lock +8%, trail -2% from peak
  - Added 3 CSV columns: Trailing_Stop_Activated, Trailing_Stop_Price, Peak_Return_Pct
  - Complete audit trail of exit decisions

**Previous Updates (v7.0 - Execution Realism & Deep Research - Dec 15)**:
- ✅ **v7.0 Execution Improvements**: Addressing third-party analysis feedback on execution realism
  - **ATR-Based Stops**: 2.5x ATR(14) with -7% maximum loss cap (system uses TIGHTER of the two)
    - Volatile stocks: ATR may suggest -12%, system caps at -7% (limits max loss)
    - Stable stocks: ATR may suggest -4%, system uses -4% (tighter than cap)
    - Adapts to each stock's volatility while preventing excessive losses
  - **Spread/Slippage Checking**: Skip trades if bid-ask spread >0.5%
    - Prevents expensive execution on illiquid catalyst names
    - Market orders at 9:45 AM no longer erode edge on wide spreads
    - Preserves theoretical alpha by avoiding execution cost
  - **Breadth Timing Fix**: Market breadth calculated at 7:00 AM (screener time), used at 9:00 AM (GO time)
    - Prevents lookahead bias from using end-of-day breadth for intraday decisions
    - Timestamped in screener output for transparency
    - GO command uses pre-calculated breadth value
- ✅ **Phase 1 + Gap-Ups Complete (Dec 18)**: Added 4 new catalyst types for 14.5x improvement in candidate flow
  - **Price Target Raises (Tier 2)**: Analyst price targets raised >20% (~100 candidates/day)
  - **52-Week High Breakouts (Tier 4)**: Fresh breakouts with volume >150% (~30 candidates/day)
  - **Sector Rotation (Tier 3)**: Stocks in sectors outperforming SPY by >5% (~20-70 candidates/day)
  - **Gap-Ups (Tier 4)**: Opening gaps >3% with volume >120% (~20-40 candidates/day)
  - **Expected Flow**: 170-240 candidates/day (was 2 baseline, 85-120x increase)
  - **Zero API Costs**: All detection uses existing free APIs (Finnhub, Polygon, FMP)
  - **Deferred to Parking Lot**: Buyback detection, earnings acceleration, contract magnitude parsing (low ROI)
- ✅ **Deep Research Implementation (Dec 15)**: Complete architectural shift to Entry Quality Scorecard methodology
  - **BREAKING CHANGE**: RS is now scoring factor (0-5 pts), NOT hard filter
  - Hard filters: Price >$10, Liquidity >$50M, Catalyst presence required
  - AI evaluates 100-point scorecard for best opportunities
  - Target: 60-70% win rate, 8-12% monthly returns (academic PEAD research)
  - Aligns with Deep Research: "rule-based filters eliminate low-quality opportunities, then AI analyzes sentiment"
  - Prevents filtering out NVDA/LLY/ORCL with weak 3M RS but strong catalysts
- ✅ **Blackout Policy Update (Dec 10)**: Changed to event-day only (FOMC, CPI, NFP, PCE) - aligned with institutional best practices, reduces December blackout days from 57% to 29%

**Latest Update (v8.0 - Dec 28, 2025)**:
- ✅ **Alpaca Paper Trading Integration**: Complete migration from JSON simulation to real brokerage API
  - **Portfolio Loading**: Positions load from Alpaca API (real-time sync)
  - **Order Execution**: All buys/sells execute via Alpaca market orders
  - **EXECUTE Command**: Places BUY orders for new positions, SELL orders for Claude exits
  - **ANALYZE Command**: Places SELL orders when stop loss/target/time stop triggered
  - **Safety Features**: Position verification, buying power checks, graceful fallback to JSON
  - **Environment**: $100,000 paper trading account (no real money)
  - **Purpose**: 6-12 month validation to collect realistic execution data (slippage, fills, timing)
  - **Deployment**: Fully autonomous via cron (no manual intervention required)
  - **Testing**: All cron environment tests passing, ready for live market hours
  - **Next Phase**: Validate order execution quality, compare to JSON simulation baseline

**Previous Updates (Phase 4 - Risk Optimization & Institutional Enhancements)**:
- ✅ Phase 4.1: Cluster-based conviction scoring (prevents double-counting correlated signals)
- ✅ Phase 4.2: Market breadth & trend filter (regime-based position sizing)
- ✅ Phase 4.3: Sector concentration reduction (max 2 per sector, 3 in leading sectors)
- ✅ Phase 4.4: Liquidity filter (min $50M daily volume prevents slippage)
- ✅ Phase 4.5: VIX regime logging (tracks market conditions for learning & attribution)
- ✅ Phase 4.6: AI robustness & failover (graceful degradation when Claude API fails)
- ✅ Phase 4.7: Operational monitoring (health checks, dashboard alerts, version tracking)
- ✅ Phase 4.8: Public model portfolio display (YTD/MTD metrics, regime analysis, transparency)

**Previous Updates**:
- ✅ Phase 3: IBD-style RS percentile ranking, sector rotation detection, institutional signals
- ✅ Phase 2: RS rank percentile, volume confirmation, portfolio rebalancing, performance attribution
- ✅ Phase 1: Trailing stops, dynamic targets, conviction scoring, post-earnings drift, Stage 2 alignment
- ✅ Phase 0: Gap-aware entry/exit, news validation, sector concentration, market regime filter
