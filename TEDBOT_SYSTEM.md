# Tedbot Trading System - Complete Documentation

**Version:** v10.5 (February 2026)
**Status:** Live Paper Trading with Alpaca Integration
**Starting Capital:** $10,000

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture & Daily Pipeline](#2-architecture--daily-pipeline)
3. [Command Execution Paths](#3-command-execution-paths)
4. [Entry Scenarios](#4-entry-scenarios)
5. [Exit Scenarios](#5-exit-scenarios)
6. [Position Sync & Alpaca Integration](#6-position-sync--alpaca-integration)
7. [Risk Management](#7-risk-management)
8. [Learning System](#8-learning-system)
9. [Error Handling](#9-error-handling)
10. [Dashboard & Data Flow](#10-dashboard--data-flow)
11. [Honest Assessment: Strengths & Limitations](#11-honest-assessment-strengths--limitations)
12. [Parameters Reference](#12-parameters-reference)
13. [File Reference](#13-file-reference)
14. [Version History](#14-version-history)

---

## 1. System Overview

### What is Tedbot?

Tedbot is an **autonomous AI-powered catalyst-driven swing trading system** that uses Claude (Anthropic's AI) to identify, analyze, and trade stocks experiencing significant catalysts. The system operates fully autonomously with a paper trading account, making data-driven decisions based on news events, technical analysis, market conditions, and continuous learning from past performance.

**Performance Target**: 90-92% of best-in-class professional trader performance
**Strategy**: Event-driven momentum trading (3-7 day holds, occasionally 30-60 days for post-earnings drift)
**Approach**: High-conviction, concentrated positions (10 max) with strict risk management

### Key System Properties

**Autonomy**: Runs 24/7 without human intervention
- Automated scheduling via cron (screener, GO, EXECUTE, EXIT, ANALYZE, learning)
- Self-healing: AI failover if Claude API fails (holds positions, skips entries, logs failure)
- Self-improving: Learning system automatically excludes underperforming catalysts
- Health monitoring: Daily 5pm ET health checks with dashboard alerts

**Risk Management**: Institutional-grade safety mechanisms
- VIX shutdown: Stops trading at VIX >35, cautious mode at 30-35
- Market breadth filter: Reduces sizing by 40% in UNHEALTHY markets
- Cluster-based conviction: Prevents double-counting correlated signals (max 11 factors)
- Sector concentration: Max 2 per sector (3 in leading sectors)
- Liquidity filter: Min $50M daily volume prevents slippage

**Transparency**: Complete performance visibility
- Public dashboard: YTD/MTD returns, win rate, Sharpe ratio, max drawdown
- Regime analysis: Performance by VIX regime (5 levels) and market breadth (3 levels)
- Conviction tracking: HIGH/MEDIUM/LOW distribution and accuracy
- Version tracking: System_Version column tracks which code generated each trade

**Learning**: Closed-loop continuous improvement
- Trade → CSV (56+ columns) → Learning (daily/weekly/monthly) → Insights → Claude Context → Decision → Trade
- Historical performance directly informs future decisions
- Entry Quality tracking: GOOD/CAUTION/POOR entries analyzed for win rate differences

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Screening | Python + Polygon.io | Market data, news, technicals |
| Decision Layer | Claude Sonnet 4.5 | Portfolio construction, exit decisions |
| Catalyst Screening | Claude Haiku 4.5 | News analysis at scale |
| Execution | Alpaca Markets API | Real-time paper trading orders |
| Risk Framework | Custom Python | ATR stops, gap analysis, spread checks |
| Dashboard | React + Flask API | Real-time monitoring |

---

## 2. Architecture & Daily Pipeline

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    STAGE 1: IDENTIFICATION                       │
│              (Hybrid Screener - Binary Gates + Claude AI)        │
│                                                                  │
│  PHILOSOPHY: "If it's not binary, Claude decides"               │
│                                                                  │
│  PHASE 1: BINARY HARD GATES (Objective only):                   │
│  • Scans 993 S&P 1500 stocks continuously                       │
│  • BINARY FILTERS (no interpretation):                          │
│    - Price ≥$10 (liquidity, institutional participation)        │
│    - Daily volume ≥$50M (execution quality)                     │
│    - Data freshness (traded in last 5 days)                     │
│  OUTPUT: ~250 stocks pass binary gates                          │
│                                                                  │
│  PHASE 2: CLAUDE AI CATALYST ANALYSIS:                          │
│  • Analyzes ALL ~250 stocks with prompt caching                 │
│  • Negative news detection (offerings, lawsuits, downgrades)    │
│  • Catalyst identification with nuance                          │
│  • Tier classification (Tier 1/2/3/4/None)                      │
│  • Confidence scoring (High/Medium/Low)                         │
│  OUTPUT: 35-40 high-quality candidates                          │
│                                                                  │
│  PHASE 3: COMPOSITE SCORING & SELECTION:                        │
│  • RS percentile ranking across universe                        │
│  • Sector rotation analysis (11 sectors vs SPY)                 │
│  • Top 40 candidates selected for GO command                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STAGE 2: DECISION-MAKING (GO Command)              │
│                     (Claude AI Analysis)                         │
│                                                                  │
│  CONTEXT LOADED:                                                 │
│  • Strategy rules, learning database, catalyst exclusions       │
│  • Previous ANALYZE recommendations                              │
│  • Current portfolio positions, account status                  │
│  • Entry quality performance data (v10.5)                       │
│                                                                  │
│  CLAUDE ANALYZES:                                                │
│  • VIX regime (5 levels: VERY_LOW → EXTREME)                    │
│  • Market breadth (HEALTHY/DEGRADED/UNHEALTHY)                  │
│  • Cluster-based conviction scoring (max 11 factors)            │
│  • Dynamic position sizing (6-13% based on conviction + regime) │
│                                                                  │
│  DECISIONS:                                                      │
│  • BUY: 0-10 positions                                          │
│  • HOLD: Continue existing positions                             │
│  • EXIT: Flag positions for closure                              │
│  OUTPUT: pending_positions.json → EXECUTE command               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│     STAGE 3: EXECUTION (EXECUTE + EXIT + ANALYZE Commands)      │
│                    ALPACA API INTEGRATION                        │
│                                                                  │
│  EXECUTE (9:45 AM):                                              │
│  • Validates gap-aware entry (<3%: enter, 3-8%: caution, >8%: skip)│
│  • Checks bid-ask spread (skip if >0.5%)                        │
│  • Places BUY orders via Alpaca API                              │
│  • Places stop-loss orders (ATR-based, -7% cap)                  │
│  • Places trailing stop orders for +10% positions                │
│                                                                  │
│  EXIT (3:45 PM):                                                 │
│  • Fetches real-time prices from Alpaca                          │
│  • Applies exit rules (stop loss, target, time stop)            │
│  • Claude reviews for discretionary exits                        │
│  • Places SELL orders via Alpaca - executes before close         │
│                                                                  │
│  ANALYZE (4:30 PM):                                              │
│  • NO ORDER EXECUTION - learning/summary only                    │
│  • Updates portfolio with closing prices                         │
│  • Creates daily activity summary                                │
│  • Updates learning database                                     │
│  OUTPUT: Daily summary, learning insights                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STAGE 4: LEARNING (Continuous Improvement)         │
│                                                                  │
│  TRADE COMPLETION (when position exits):                        │
│  • Logs 56+ column CSV with complete trade attribution          │
│  • Entry Quality tracked (GOOD/CAUTION/POOR) - v10.5            │
│                                                                  │
│  LEARNING DATABASE UPDATES:                                      │
│  • Catalyst performance by type                                  │
│  • Entry timing patterns by quality                              │
│  • Exit type statistics                                          │
│  • Market regime performance                                     │
│                                                                  │
│  FEEDBACK LOOP:                                                  │
│  Learning insights loaded into STAGE 2                           │
│  (Claude sees historical performance in next GO command)        │
└─────────────────────────────────────────────────────────────────┘
```

### Automated Schedule (Eastern Time)

| Time | Command | Purpose |
|------|---------|---------|
| 7:00 AM | **SCREEN** | Scan S&P 1500, calculate breadth, validate catalysts |
| 9:00 AM | **GO** | Claude analyzes top candidates, builds portfolio decisions |
| 9:45 AM | **EXECUTE** | Place orders via Alpaca with spread/gap validation |
| 10:15 AM | **RECHECK** | Re-evaluate stocks skipped due to gap at open |
| 3:45 PM | **EXIT** | Claude reviews positions for end-of-day exits |
| 4:30 PM | **ANALYZE** | Update performance metrics, extract learnings |

---

## 3. Command Execution Paths

### 3.1 SCREEN Command (7:00 AM ET)

**Purpose**: Filter S&P 1500 universe to ~40 catalyst candidates

**Execution Path**:
```
market_screener.py
├── Load S&P 1500 constituents (993 stocks)
├── PHASE 1: Binary Hard Gates
│   ├── Price ≥ $10
│   ├── Daily volume ≥ $50M
│   └── Data freshness (traded in last 5 days)
│   └── OUTPUT: ~250 stocks pass
├── PHASE 2: Claude AI Catalyst Analysis
│   ├── Batch analyze ~250 stocks (5 concurrent, prompt caching)
│   ├── Negative news detection
│   ├── Catalyst identification (Tier 1/2/3/4)
│   ├── Confidence scoring (High/Medium/Low)
│   └── OUTPUT: 35-40 candidates accepted
├── PHASE 3: Composite Scoring
│   ├── RS percentile ranking
│   ├── Sector rotation analysis
│   └── Top 40 selection
└── Save to screener_candidates.json
```

**Files Written**:
| File | Content |
|------|---------|
| `screener_candidates.json` | 40 candidates with catalyst data, RS scores |
| `logs/screener.log` | Execution log |

---

### 3.2 GO Command (9:00 AM ET)

**Purpose**: Claude analyzes candidates and current portfolio, makes BUY/HOLD/EXIT decisions

**Execution Path**:
```
agent_v5.5.py go
├── Load current portfolio (current_portfolio.json)
├── Fetch premarket prices (Polygon.io)
├── Load context
│   ├── strategy_rules.md
│   ├── learning_database.json (including entry quality stats - v10.5)
│   ├── catalyst_exclusions.json
│   └── Previous ANALYZE recommendations
├── Call Claude API for portfolio review
│   ├── SUCCESS: Extract JSON decisions
│   ├── NO JSON: Retry full GO call (v8.9.7)
│   └── API FAILURE: Degraded mode (HOLD all)
├── Check market regime
│   ├── VIX level (5 regimes)
│   ├── Market breadth
│   └── Macro events (FOMC, CPI, NFP, PCE)
├── If vacant slots + candidates available:
│   └── Call Claude for new entries
├── Identify trailing stop candidates (+10% positions)
├── Save pending_positions.json
│   ├── hold: [tickers]
│   ├── exit: [{ticker, reason}]
│   ├── buy: [{ticker, size, catalyst, thesis}]
│   └── trailing_stops: [{ticker, shares, trail_percent}]
├── Save GO response (daily_reviews/go_*.json)
└── Send GO report email
```

**Files Written**:
| File | Content |
|------|---------|
| `pending_positions.json` | Decisions for EXECUTE |
| `daily_reviews/go_YYYYMMDD_HHMMSS.json` | Full Claude response |
| `portfolio_data/daily_picks.json` | Screener decisions for dashboard |
| `logs/go.log` | Execution log |

**Dashboard Impact**:
- Today page shows screening decisions (accepted/rejected/owned)
- Command Center shows GO status

---

### 3.3 EXECUTE Command (9:45 AM ET)

**Purpose**: Execute BUY/SELL orders via Alpaca, place stop-losses and trailing stops

**Execution Path**:
```
agent_v5.5.py execute
├── Load pending_positions.json
├── Load current portfolio
├── STEP 2.5: Position Sync Check
│   ├── Get Alpaca positions
│   ├── For each JSON position NOT in Alpaca:
│   │   ├── Detect as externally sold (trailing stop/stop-loss)
│   │   ├── Get fill price from Alpaca orders
│   │   ├── Log trade to CSV
│   │   └── Remove from portfolio
│   └── OUTPUT: alpaca_auto_closed[]
├── STEP 3: Process EXITs
│   ├── For each exit decision:
│   │   ├── Validate exit conditions
│   │   ├── Execute Alpaca sell order
│   │   ├── Log trade to CSV
│   │   └── Remove from portfolio
│   └── OUTPUT: closed_trades[]
├── STEP 4: Update HOLD positions
│   ├── Fetch current prices
│   ├── Update P&L calculations
│   └── Place missing stop-loss orders
├── STEP 5: Enter NEW positions
│   ├── For each buy decision:
│   │   ├── Gap check (<3%: enter, 3-8%: caution, >8%: skip)
│   │   ├── Validate Alpaca order success (v10.5 - skip if fails)
│   │   ├── Execute Alpaca buy order
│   │   ├── Wait 3 seconds (wash trade prevention)
│   │   ├── Place stop-loss order
│   │   └── Add to portfolio
│   └── OUTPUT: new_entries[]
├── STEP 6: Save portfolio
├── STEP 7: Log closed trades to CSV
├── STEP 8: Update account status
├── STEP 9: Create daily activity summary
├── STEP 10: Place trailing stop orders
│   └── For qualifying positions (+10%):
│       ├── Cancel existing stop-loss
│       └── Place Alpaca trailing stop order
└── Delete pending_positions.json
```

**Execute Summary Output (v10.5)**:
```
  - Alpaca Auto-Closed: X positions (trailing stops/stop-losses)
  - System Closed: Y positions (exit commands)
```

**Files Written**:
| File | Content |
|------|---------|
| `current_portfolio.json` | Updated portfolio |
| `trade_history/completed_trades.csv` | Closed trade records |
| `portfolio_data/account_status.json` | Account value, P&L |
| `portfolio_data/daily_activity.json` | Today's trades summary |
| `daily_reviews/execute_YYYYMMDD_HHMMSS.json` | Execution results |
| `logs/execute.log` | Execution log |

---

### 3.4 RECHECK Command (10:15 AM ET)

**Purpose**: Re-evaluate stocks that were skipped due to gaps at 9:45 AM

**Execution Path**:
```
agent_v5.5.py recheck
├── Load skipped_for_gap.json
├── If no skipped stocks OR stale date:
│   └── Return SUCCESS (nothing to do)
├── Fetch current Alpaca prices
├── For each skipped stock:
│   ├── Check if gap has normalized (<3%)
│   ├── If yes: Execute entry via _execute_alpaca_buy()
│   └── If no: Keep skipped
├── Update portfolio
├── Create daily activity summary
└── Delete skipped_for_gap.json
```

**Files Written**:
| File | Content |
|------|---------|
| `current_portfolio.json` | Updated if entries made |
| `portfolio_data/daily_activity.json` | Updated if entries made |
| `daily_reviews/recheck_YYYYMMDD_HHMMSS.json` | Recheck results |
| `logs/recheck.log` | Execution log |

---

### 3.5 EXIT Command (3:45 PM ET)

**Purpose**: Pre-close position review, execute same-day exits

**Execution Path**:
```
agent_v5.5.py exit
├── Load current portfolio
├── STEP 1: Position Sync Check
│   ├── Get Alpaca positions
│   ├── For each JSON position NOT in Alpaca:
│   │   ├── Detect as externally sold
│   │   ├── Get fill price from Alpaca orders
│   │   ├── Determine exit reason (trailing stop, stop-loss, manual)
│   │   ├── Log trade to CSV
│   │   └── Remove from portfolio
│   └── OUTPUT: alpaca_closed_trades[]
├── If all positions closed:
│   ├── Update daily activity
│   └── Return SUCCESS (early exit)
├── STEP 2: Fetch real-time Alpaca prices
├── STEP 3: Apply automated exit rules
│   ├── Stop loss hit (-7% or ATR-based)
│   ├── Price target hit (+10%)
│   ├── Time stop (21 days standard, 60 days PED)
│   └── OUTPUT: auto_exits[], positions_for_review[]
├── STEP 4: Fetch news for positions
├── STEP 5: Call Claude for exit review
│   ├── SUCCESS: Parse exit recommendations
│   ├── TIMEOUT (60s): Failsafe mode (auto rules only)
│   └── OUTPUT: claude_exits[]
├── STEP 6: Execute exits
│   ├── For each exit (auto + claude):
│   │   ├── Execute Alpaca sell order
│   │   ├── Log trade to CSV
│   │   └── Remove from portfolio
│   └── OUTPUT: closed_trades[]
├── STEP 7: Update portfolio and account
├── Save exit summary
└── Update daily activity
```

**Files Written**:
| File | Content |
|------|---------|
| `current_portfolio.json` | Updated portfolio |
| `trade_history/completed_trades.csv` | Closed trade records |
| `portfolio_data/account_status.json` | Account value |
| `portfolio_data/daily_activity.json` | Today's activity |
| `daily_reviews/exit_YYYYMMDD_HHMMSS.json` | Exit results |
| `logs/exit.log` | Execution log |

---

### 3.6 ANALYZE Command (4:30 PM ET)

**Purpose**: End-of-day summary, learning, NO order execution

**Autonomy Note**: This is a 100% autonomous system. ALL ANALYZE recommendations are COMMANDS for the next trading day, not suggestions.

**Execution Path**:
```
agent_v5.5.py analyze
├── Load current portfolio
├── Fetch closing prices
├── Update portfolio with EOD values
├── Create daily activity summary (reads from CSV)
├── Call Claude for performance analysis
│   ├── 🔴 MANDATORY EXITS → Execute at next market open
│   ├── 🟠 RECOMMENDED EXITS → Execute unless new info changes thesis
│   └── 🟢 HOLD positions with notes
├── Update learning database
├── Save ANALYZE recommendations for next GO
└── Update account status
```

**Files Written**:
| File | Content |
|------|---------|
| `current_portfolio.json` | EOD prices updated |
| `portfolio_data/daily_activity.json` | Final daily summary |
| `portfolio_data/account_status.json` | EOD account value |
| `daily_reviews/analyze_YYYYMMDD_HHMMSS.json` | Analysis + recommendations |
| `logs/analyze.log` | Execution log |

---

## 4. Entry Scenarios

### 4.0 Hard Blocks (Always Block Entry)

| Block | Condition | Rationale |
|-------|-----------|-----------|
| **VIX ≥35** | Market too volatile | Historically poor win rate |
| **Macro Blackout** | FOMC/CPI/NFP/PCE day | Binary event risk |
| **Halted/Delisted** | Cannot trade | Obvious |
| **Earnings Timing** | Reports within 24 hours | Gap risk unacceptable |

### 4.1 Normal Entry (Gap < 3%)

**Trigger**: GO recommends BUY, gap < 3% at EXECUTE time

**Path**:
```
EXECUTE
├── Validate buying power
├── Execute Alpaca market buy
├── Wait 3 seconds (wash trade prevention)
├── Calculate stop-loss:
│   ├── If custom_stop_pct specified by GO: Use that (capped at -7%)
│   ├── Otherwise: ATR-based stop (max -7%)
├── Place Alpaca stop-loss order
├── Add to current_portfolio.json
├── Update account_status.json
└── Update daily_activity.json
```

### 4.2 Gap Entry (3-8% Gap)

**Trigger**: GO recommends BUY, gap 3-8% at EXECUTE time

**Path**:
```
EXECUTE
├── Detect gap in caution zone
├── Log warning but proceed
├── Execute entry (same as normal)
└── Note gap in position metadata
```

### 4.3 Skipped Entry (Gap > 8%)

**Trigger**: GO recommends BUY, gap > 8% at EXECUTE time

**Path**:
```
EXECUTE
├── Detect excessive gap
├── Skip entry
├── Save to skipped_for_gap.json
└── Log skip reason

RECHECK (10:15 AM)
├── Load skipped stocks
├── Fetch current prices
├── If gap normalized: Execute entry
└── If still gapped: Remain skipped
```

### 4.4 Portfolio Full (10 Positions)

**Trigger**: GO wants to BUY but portfolio has 10 positions

**Path**:
```
GO
├── Detect portfolio full
├── Skip screener analysis for new entries
├── Focus on HOLD/EXIT decisions only
└── Save daily_picks with status "SKIPPED (Portfolio Full)"
```

### 4.5 Alpaca Order Failure (v10.5)

**Trigger**: Alpaca rejects buy order (e.g., price too high for allocation)

**Path**:
```
EXECUTE
├── Submit order to Alpaca
├── Order rejected (e.g., "Invalid quantity: 0")
├── Log failure reason
├── Skip adding to portfolio (v10.5 fix)
├── Return cash to available balance
└── Continue with next buy
```

**Note**: Prior to v10.5, positions were added to JSON even when Alpaca failed, creating "phantom positions."

---

## 5. Exit Scenarios

### 5.1 Stop Loss Exit (Automated)

**Trigger**: Position hits -7% (or ATR-based stop)

**Path A - Alpaca Stop-Loss Triggers (Intraday)**:
```
Alpaca
├── Price hits stop-loss price
├── Executes sell automatically
└── Position removed from Alpaca

EXECUTE or EXIT (next run)
├── Position sync detects missing position
├── Fetches fill price from Alpaca orders
├── Logs trade: "Alpaca stop-loss triggered"
├── Removes from current_portfolio.json
└── Updates daily_activity.json
```

**Path B - EXIT Command Detects Stop (3:45 PM)**:
```
EXIT
├── Fetch real-time prices
├── Detect price ≤ stop_loss
├── Add to auto_exits[]
├── Execute Alpaca sell
├── Log trade: "Stop loss (-X.X%)"
└── Update portfolio
```

### 5.2 Trailing Stop Exit

**Trigger**: Position reached +10%, trailing stop placed, then triggered

**Path**:
```
EXECUTE (Day N - Position at +10%)
├── Identify qualifying position
├── Cancel existing stop-loss order
├── Place Alpaca trailing stop (2% trail)
├── Update position: trailing_stop_active = True
└── Log trailing stop order ID

Alpaca (Intraday - Any Day)
├── Price peaks then drops 2% from peak
├── Trailing stop triggers
└── Position auto-sold

EXECUTE or EXIT (Next Run)
├── Position sync detects missing position
├── Fetches fill price from Alpaca orders
├── Determines exit was trailing stop
├── Logs trade: "Alpaca trailing stop (peak +X.X%)"
└── Updates portfolio
```

### 5.3 Price Target Exit

**Trigger**: Position reaches profit target (+10% or catalyst-specific)

**Path**:
```
EXIT (3:45 PM)
├── Fetch real-time prices
├── Detect price ≥ price_target
├── Check if trailing stop should activate instead
│   ├── If trailing stop eligible: Place trailing stop, HOLD
│   └── If not: Add to auto_exits[]
├── Execute Alpaca sell
└── Log trade: "Target hit (+X.X%)"
```

### 5.4 Time Stop Exit

**Trigger**: Position held beyond max hold period

**Path**:
```
EXIT (3:45 PM)
├── Calculate hold days
├── Check against limits:
│   ├── Standard: 21 days
│   └── PED (Post-Earnings Drift): 60 days
├── If exceeded: Add to auto_exits[]
├── Execute Alpaca sell
└── Log trade: "Time stop (X days)"
```

### 5.5 Claude Discretionary Exit

**Trigger**: Claude recommends exit based on news/analysis

**Path**:
```
EXIT (3:45 PM)
├── Present positions to Claude with:
│   ├── Current P&L
│   ├── Recent news
│   └── Hold duration
├── Claude returns exit_recommendations[]
├── For each recommendation:
│   ├── Validate position exists
│   ├── Execute Alpaca sell
│   └── Log with Claude's reasoning
└── Update portfolio
```

### 5.6 External Sale Detection

**Trigger**: Position sold outside normal flow (manual, external stop-loss)

**Path**:
```
EXECUTE or EXIT
├── Get Alpaca positions
├── Compare to JSON portfolio
├── For each JSON position NOT in Alpaca:
│   ├── Query Alpaca closed orders
│   ├── Find matching fill
│   ├── Determine exit reason:
│   │   ├── trailing_stop → "Alpaca trailing stop"
│   │   ├── stop → "Alpaca stop-loss triggered"
│   │   ├── market → "Manual sell via Alpaca"
│   │   └── other → "Position closed externally"
│   ├── Log trade to CSV
│   └── Remove from portfolio
└── Continue with normal flow
```

---

## 6. Position Sync & Alpaca Integration

### 6.1 Order Flow

**Buy Orders**:
1. Calculate position size in dollars
2. Convert to shares based on current price
3. Place market buy order via Alpaca
4. Wait 3 seconds (wash trade prevention)
5. Place stop-loss order at calculated stop price
6. Record Alpaca order IDs for tracking

**Sell Orders**:
1. Cancel any open orders for the ticker (stops)
2. Wait 3 seconds (share release time)
3. Place market sell order
4. Record fill price as exit price

### 6.2 Portfolio Synchronization

The system maintains two sources of truth:
- **JSON files**: Position data, entry prices, catalysts, thesis
- **Alpaca**: Actual shares held, current market value

At each EXECUTE/EXIT run:
1. Compare JSON positions to Alpaca positions
2. Log any discrepancies
3. Use Alpaca values for account equity/cash
4. Maintain JSON for strategy metadata

### 6.3 JSON-Alpaca Mismatch Handling

**Position Missing from Alpaca**:
- Detected as externally sold
- Fill price retrieved from Alpaca orders
- Trade logged to CSV
- Position removed from JSON

**Alpaca Has Extra Position**:
- Current behavior: Not explicitly handled (rare edge case)
- Position won't be managed by Tedbot until manually reconciled

**Price/Shares Mismatch**:
- Log warning with both values
- Use Alpaca values as source of truth

---

## 7. Risk Management

### 7.1 Position-Level Risk

| Parameter | Value | Method |
|-----------|-------|--------|
| Stop Loss | ATR*2.5 or -7% cap | Use tighter of the two |
| Position Size | 6-13% | Conviction + breadth adjustment |
| Spread Check | Skip if >0.5% | Prevents costly execution |
| Max Hold | 21 days (60 for PED) | Time stop |

**ATR Stop Example**:
- Entry: $100, ATR-14: $2.00
- ATR Stop: $100 - ($2 * 2.5) = $95.00 (-5%)
- Max Stop: $93.00 (-7%)
- **Used: $95.00** (tighter, respects volatility)

### 7.2 Portfolio-Level Risk

| Parameter | Value |
|-----------|-------|
| Max Positions | 10 |
| Sector Concentration | Max 2 per sector (3 in leading) |
| Liquidity Floor | Min $50M daily volume |
| Margin | None (cash only) |

### 7.3 Market Regime Risk

**VIX Levels**:
| VIX | Regime | Action |
|-----|--------|--------|
| < 15 | VERY_LOW | Normal trading |
| 15-20 | LOW | Normal trading |
| 20-25 | ELEVATED | Caution, reduce sizing |
| 25-30 | HIGH | Tier 1/2 only |
| 30-35 | CAUTIOUS | Tier 1 only + News ≥15 |
| ≥ 35 | SHUTDOWN | Block ALL new entries |

**Market Breadth**:
| Breadth | Regime | Position Multiplier |
|---------|--------|---------------------|
| ≥ 50% | HEALTHY | 1.0x |
| 40-49% | DEGRADED | 0.8x |
| < 40% | UNHEALTHY | 0.6x |

### 7.4 Dynamic Profit Targets

| Catalyst Type | Target | Stretch | Typical Hold |
|---------------|--------|---------|--------------|
| M&A Target | 15% | 20% | 5-10 days |
| FDA Approval | 15% | 25% | 5-10 days |
| Earnings Beat > 20% | 12% | 15% | 5-10 days |
| Major Contract | 12% | - | 5-7 days |
| Top-Firm Analyst Upgrade | 12% | - | 5-7 days |
| Tier 2 (Standard) | 8% | - | 3-5 days |
| Insider Buying | 10% | - | 10-20 days |

### 7.5 Entry Timing Quality (v10.5)

**Entry Quality Assessment**:
| Quality | Criteria | Expected Win Rate |
|---------|----------|-------------------|
| GOOD | RSI <70, <5% above MA20, <10% 3-day change | Higher |
| CAUTION | 1-2 timing issues | Medium |
| POOR | 3+ timing issues | Lower |

The learning system tracks win rates by entry quality and surfaces insights to Claude:
- "CAUTION entries (45%) underperform GOOD entries (68%)"
- "Consider PASSING on entries flagged 'CAUTION - wait for pullback'"

---

## 8. Learning System

### 8.1 Trade Completion Logging

When a position exits, 56+ columns are logged to CSV:

**Core Fields**: Trade_ID, Ticker, Entry_Date, Exit_Date, Entry_Price, Exit_Price, Return_Percent, Return_Dollars, Shares, Days_Held

**Catalyst Fields**: Catalyst_Type, Catalyst_Tier, News_Score, Catalyst_Details

**Technical Fields**: SMA50, EMA5, EMA20, ADX, Volume_Ratio, Technical_Score, RS_Rating

**Entry Quality Fields (v10.5)**: Entry_Quality, Entry_RSI, Entry_MA20_Distance, Entry_3Day_Change

**Risk Fields**: Stop_Loss, Stop_Pct, Price_Target, Max_Drawdown

**Market Fields**: VIX_At_Entry, VIX_Regime, Market_Breadth_Regime

**Exit Fields**: Exit_Type, Exit_Reason, Trailing_Stop_Activated, Peak_Return_Pct

### 8.2 Learning Database Structure

**File**: `strategy_evolution/learning_database.json`

**Sections**:
- `critical_failures`: ACTIVE/RESOLVED failures with lessons
- `catalyst_performance`: Win rates by catalyst type
- `entry_timing_patterns.by_quality`: Win rates by GOOD/CAUTION/POOR (v10.5)
- `exit_type_performance`: Stats by exit type
- `market_regime_performance`: Performance by VIX regime
- `actionable_insights`: Data-driven recommendations

### 8.3 Learning Context in GO Command

Claude receives learning context including:
- Active critical failures (surfaced until resolved)
- Catalyst win rates by type
- Entry quality performance comparison (v10.5)
- Actionable insights from past trades

**Example Insight**:
```
📊 DATA INSIGHT: CAUTION entries (45%) underperform GOOD entries (68%)
   → Consider PASSING on entries flagged 'CAUTION - wait for pullback'
```

---

## 9. Error Handling

### 9.1 Claude API Timeout

**GO Command**:
```
GO
├── API call times out (120s)
├── Retry with 2x timeout (240s)
├── If still fails:
│   ├── Enter DEGRADED MODE
│   ├── HOLD all existing positions
│   ├── Skip new entries
│   ├── Log failure to claude_api_failures.json
│   └── Return SUCCESS (graceful degradation)
```

**EXIT Command**:
```
EXIT
├── API call times out (60s)
├── Enter FAILSAFE MODE
├── Execute auto rules only:
│   ├── Stop loss exits
│   ├── Target exits
│   └── Time stop exits
├── Skip Claude discretionary exits
└── Log failsafe activation
```

### 9.2 Claude Returns No JSON

```
GO
├── Extract JSON from response
├── No JSON found
├── Retry FULL GO call with same context
├── Extract JSON from retry response
├── If still no JSON:
│   └── Return failure
└── Continue with extracted decisions
```

### 9.3 Alpaca Order Failure

```
EXECUTE
├── Submit order to Alpaca
├── Order rejected
├── Log failure reason
├── Skip position (v10.5 - don't add phantom)
└── Continue with next order
```

### 9.4 Wash Trade Detection

```
EXECUTE
├── Buy order succeeds
├── Attempt stop-loss placement
├── Alpaca rejects: "wash trade detected"
├── Wait 3 seconds
├── Retry stop-loss placement
└── If still fails: Log warning, continue without stop-loss
```

---

## 10. Dashboard & Data Flow

### 10.1 Overview Page

| Metric | Source File | Update Frequency |
|--------|-------------|------------------|
| Account Value | `account_status.json` | Every command |
| Total Return | `account_status.json` | Every command |
| Positions | `current_portfolio.json` | Every command |
| Recent Trades | `completed_trades.csv` | On exits |
| Win Rate | `completed_trades.csv` | On exits |

### 10.2 Today Page

| Section | Source File | Update Trigger |
|---------|-------------|----------------|
| Screening Decisions | `daily_picks.json` | GO command |
| New Entries | `daily_activity.json` | EXECUTE command |
| Exits | `daily_activity.json` | EXECUTE/EXIT command |
| Trailing Stops Active | `exit_*.json` | EXIT command |

**Update Flow**:
```
GO → daily_picks.json (screening decisions)
EXECUTE → daily_activity.json (entries + exits)
EXIT → daily_activity.json (exits)
ANALYZE → daily_activity.json (final summary)
```

### 10.3 Alpaca Status Indicator

| Color | Meaning | Detection |
|-------|---------|-----------|
| GREEN | Connected, synced | Alpaca API responds, position count matches |
| YELLOW | Connected, mismatch | Alpaca API responds, position count differs |
| RED | Disconnected | Alpaca API fails |

---

## 11. Honest Assessment: Strengths & Limitations

### What This System IS

1. **Systematic and Rules-Based** - Every decision follows explicit, auditable rules. The screening, scoring, sizing, and exit logic are deterministic and reproducible.

2. **Catalyst-Driven with Quantitative Discipline** - The edge hypothesis is clear: stocks with fresh, material catalysts (M&A, FDA, earnings) tend to exhibit momentum that can be captured in 3-21 day holding periods.

3. **Risk-Aware by Design** - ATR-based stops, position-size caps, VIX regime gates, breadth adjustments, gap analysis, and spread checks provide multiple layers of risk control.

4. **AI-Augmented, Not AI-Dependent** - The LLM provides judgment on news quality and catalyst validity, but the quantitative framework provides discipline. Claude cannot override stops, sizing rules, or regime gates.

5. **Fully Automated Pipeline** - From screening to execution to monitoring, the system runs without manual intervention.

6. **Broker-Integrated** - Real-time order execution via Alpaca with actual stop-loss orders provides institutional-grade risk management.

### What This System IS NOT

1. **Not a Statistical Arbitrage Model** - There is no covariance matrix, no mean-reversion signal, no pairs trading. The alpha source is event-driven momentum.

2. **Not Backtested with Statistical Rigor** - Parameters are based on practitioner research, not optimized over historical data with walk-forward validation.

3. **Not a High-Frequency System** - Holding periods are 3-21 days. No intraday trading.

4. **Not Diversified Across Strategies** - Single strategy (catalyst momentum). No mean-reversion, volatility selling, or macro overlay.

5. **Not Yet Validated with Live Capital** - Currently in paper trading validation phase.

### The Role of the LLM

The LLM (Claude) serves a specific, bounded role:

- **Screener Stage (Haiku)**: Classifies news into catalyst tiers and detects negative flags.
- **GO Stage (Sonnet)**: Constructs portfolio from pre-validated candidates.
- **EXIT Stage (Sonnet)**: Reviews positions for exit decisions.

**Critical Constraint**: Claude's decisions are validated and bounded by the quantitative framework. It cannot:
- Enter positions that fail binary gates
- Size positions above conviction limits
- Override VIX regime shutdowns
- Skip stop-loss exits
- Hold beyond time stops

### Classification

| Dimension | Discretionary | TedBot | Institutional Quant |
|-----------|---------------|--------|---------------------|
| Universe selection | Gut feel | Systematic | Systematic |
| Signal generation | Experience | Rules + AI | Statistical models |
| Position sizing | Variable | Conviction formula | Kelly/Risk parity |
| Risk management | Mental stops | ATR + Alpaca stops | VaR/CVaR models |
| Execution | Manual | Automated + Alpaca | Algorithmic |
| Backtesting | None | Limited | Rigorous walk-forward |

**Verdict**: TedBot is a **systematic event-driven trading system with AI-augmented catalyst validation and broker-integrated execution**. It has institutional-grade screening and risk controls, but lacks statistical backtesting rigor and multi-strategy diversification.

### Path to Institutional Grade

To bridge the gap, the system would need:
1. Walk-forward backtesting of catalyst signals over 5+ years
2. Parameter sensitivity analysis
3. Portfolio-level risk metrics (max drawdown constraints, Sharpe targets)
4. Strategy diversification
5. Validated 12+ month track record

---

## 12. Parameters Reference

### Core Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Universe | S&P 1500 | Constituent file |
| Min Price | $10 | Institutional floor |
| Min Market Cap | $1B | Liquidity requirement |
| Min Daily Volume | $50M | Execution quality |
| Top Candidates | 40 | Presented to Claude |
| Max Positions | 10 | Portfolio limit |
| Position Size Range | 6-13% | Conviction-based |
| Stop Loss | ATR*2.5 or -7% cap | Dynamic |
| Profit Targets | 8-25% | Catalyst-specific |
| Max Hold | 21 days (60 PED) | Time stop |
| Min Hold | 2 days | Anti-churn |

### VIX & Regime Parameters

| Parameter | Value |
|-----------|-------|
| VIX Shutdown | ≥ 35 |
| VIX Cautious | 30-34 (Tier 1 only) |
| Spread Limit | 0.50% |
| Gap Skip | ≥ 8% |
| Gap Caution | 3-8% |
| Breadth Healthy | ≥ 50% |
| Breadth Degraded | 40-49% |
| Breadth Unhealthy | < 40% |

### Timing Parameters

| Parameter | Value |
|-----------|-------|
| Wash Trade Delay | 3 seconds |
| API Timeout (GO) | 120s, retry 240s |
| API Timeout (EXIT) | 60s |

---

## 13. File Reference

### Portfolio Data Files

| File | Purpose | Written By |
|------|---------|------------|
| `portfolio_data/current_portfolio.json` | Current open positions | EXECUTE, EXIT, ANALYZE |
| `portfolio_data/pending_positions.json` | Decisions awaiting execution | GO |
| `portfolio_data/account_status.json` | Account value, cash, P&L | All commands |
| `portfolio_data/daily_activity.json` | Today's entries/exits | EXECUTE, EXIT, ANALYZE |
| `portfolio_data/daily_picks.json` | Screener decisions | GO |
| `skipped_for_gap.json` | Stocks skipped for RECHECK | EXECUTE |

### Trade History

| File | Purpose | Written By |
|------|---------|------------|
| `trade_history/completed_trades.csv` | All closed trades (56+ columns) | EXECUTE, EXIT |

### Daily Reviews

| File Pattern | Purpose | Written By |
|--------------|---------|------------|
| `daily_reviews/go_YYYYMMDD_HHMMSS.json` | GO command output | GO |
| `daily_reviews/execute_YYYYMMDD_HHMMSS.json` | EXECUTE results | EXECUTE |
| `daily_reviews/exit_YYYYMMDD_HHMMSS.json` | EXIT results | EXIT |
| `daily_reviews/analyze_YYYYMMDD_HHMMSS.json` | ANALYZE output | ANALYZE |
| `daily_reviews/recheck_YYYYMMDD_HHMMSS.json` | RECHECK results | RECHECK |

### Learning Files

| File | Purpose |
|------|---------|
| `strategy_evolution/learning_database.json` | Structured learning data |
| `strategy_evolution/lessons_learned.md` | Human-readable lessons |
| `strategy_evolution/catalyst_exclusions.json` | Poor performers to avoid |

### Logs

| File | Purpose |
|------|---------|
| `logs/screener.log` | Screener execution |
| `logs/go.log` | GO command execution |
| `logs/execute.log` | EXECUTE command execution |
| `logs/exit.log` | EXIT command execution |
| `logs/analyze.log` | ANALYZE command execution |
| `logs/recheck.log` | RECHECK command execution |
| `logs/claude_api_failures.json` | API failure tracking |

---

## 14. Version History

### v10.5 (February 23, 2026)
- **Entry Quality Learning**: Track GOOD/CAUTION/POOR entries with win rate analysis
- **Execute Report Enhancement**: Separate "Alpaca Auto-Closed" vs "System Closed" display
- **Phantom Position Fix**: Skip adding positions when Alpaca order fails
- **Learning Database Fixes**: Dynamic catalyst/exit type creation, entry timing patterns

### v10.4 (February 2026)
- **Prompt Caching**: 90% cost reduction on screener via Anthropic prompt caching

### v8.9.9 (February 2026)
- **Earnings Timing HARD RULE**: No entry if stock reports within 24 hours
- **Merger Arbitrage Rules**: Spread ≥5%, don't chase >15% pop
- **Custom Stop Support**: GO can recommend tighter stops (-1% to -7%)
- **ANALYZE Fully Autonomous**: All recommendations are commands

### v8.9.7 (February 2026)
- **JSON Extraction Retry**: Full context retry when Claude forgets JSON block
- **Prompt Improvements**: JSON requirement at START of prompts

### v8.2 (February 2026)
- **EXIT/ANALYZE Split**: Separates execution (3:45 PM) from learning (4:30 PM)
- **Real-time Alpaca Prices**: EXIT uses live prices, not delayed Polygon

### v8.1 (February 2026)
- **Trailing Stop Architecture**: Real Alpaca orders instead of JSON tracking
- **Institutional Learning System**: Structured learning_database.json

### v8.0 (December 2025)
- **Alpaca Integration**: Complete migration from JSON simulation to broker API

### v7.0 (December 2025)
- **ATR-Based Stops**: 2.5x ATR with -7% cap
- **Spread Checking**: Skip trades if spread >0.5%
- **Breadth Timing Fix**: Calculate at screener time, use at GO time

---

*Document consolidated February 23, 2026. System version v10.5.*
*Previous docs archived: TEDBOT_OVERVIEW.md, docs/METHODOLOGY.md, docs/EXECUTION_PATHS.md*
