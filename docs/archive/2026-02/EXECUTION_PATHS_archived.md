# Tedbot Execution Paths - Complete System Flow Documentation

**Version**: v8.9.9
**Last Updated**: February 19, 2026

This document exhaustively describes every execution path through the Tedbot system, including primary flows, edge cases, and error handling.

---

## Changelog (v8.9.9)

| Change | Description |
|--------|-------------|
| **Earnings Timing HARD RULE** | No entry if stock reports earnings within 24 hours (MRCY lesson) |
| **Merger Arbitrage Rules** | Spread ≥5%, don't chase >15% pop, technical warnings still apply (MASI lesson) |
| **Custom Stop Support** | GO can recommend tighter stops (-1% to -7%), EXECUTE enforces -7% ceiling |
| **ANALYZE Fully Autonomous** | Removed "Your decision" language - all recommendations are commands |
| **RECHECK Permission Fix** | Fixed chmod +x on run_recheck.sh for cron execution |
| **skipped_for_gap.json Logging** | Added explicit error handling and confirmation logging |

---

## Table of Contents

1. [Primary Daily Flow](#1-primary-daily-flow)
2. [Entry Scenarios](#2-entry-scenarios)
3. [Exit Scenarios](#3-exit-scenarios)
4. [Position Sync Scenarios](#4-position-sync-scenarios)
5. [Error Handling Scenarios](#5-error-handling-scenarios)
6. [Dashboard Data Flow](#6-dashboard-data-flow)

---

## 1. Primary Daily Flow

### 1.1 SCREEN Command (7:00 AM ET)

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
│   ├── Batch analyze ~250 stocks (5 concurrent)
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

**Dashboard Impact**: None directly (GO command reads this file)

---

### 1.2 GO Command (9:00 AM ET)

**Purpose**: Claude analyzes candidates and current portfolio, makes BUY/HOLD/EXIT decisions

**Execution Path**:
```
agent_v5.5.py go
├── Load current portfolio (active_positions.json)
├── Fetch premarket prices (Polygon.io)
├── Load context
│   ├── strategy_rules.md
│   ├── learning_database.json
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

### 1.3 EXECUTE Command (9:45 AM ET)

**Purpose**: Execute BUY/SELL orders via Alpaca, place stop-losses and trailing stops

**Execution Path**:
```
agent_v5.5.py execute
├── Load pending_positions.json
├── Load current portfolio
├── STEP 2.5: Position Sync Check (v8.9.8)
│   ├── Get Alpaca positions
│   ├── For each JSON position NOT in Alpaca:
│   │   ├── Detect as externally sold
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
└── Save execute response
```

**Files Written**:
| File | Content |
|------|---------|
| `active_positions.json` | Updated portfolio |
| `trade_history/completed_trades.csv` | Closed trade records |
| `portfolio_data/account_status.json` | Account value, P&L |
| `portfolio_data/daily_activity.json` | Today's trades summary |
| `daily_reviews/execute_YYYYMMDD_HHMMSS.json` | Execution results |
| `logs/execute.log` | Execution log |

**Dashboard Impact**:
- Today page shows new entries and exits
- Command Center shows position count
- Account value updates

---

### 1.4 RECHECK Command (10:15 AM ET)

**Purpose**: Re-evaluate stocks that were skipped due to gaps at 9:45 AM

**v8.9.9 Fixes**:
- Fixed run_recheck.sh permission (chmod +x) for cron execution
- Added explicit error handling and logging when saving skipped_for_gap.json

**Execution Path**:
```
agent_v5.5.py recheck
├── Load skipped_for_gap.json (v8.9.9: explicit error logging if missing)
├── If no skipped stocks OR stale date:
│   └── Return SUCCESS (nothing to do)
├── Fetch current Alpaca prices
├── For each skipped stock:
│   ├── Check if gap has normalized (<3%)
│   ├── If yes: Execute entry via _execute_alpaca_buy()
│   └── If no: Keep skipped
├── Update portfolio
└── Create daily activity summary
```

**Files Written**:
| File | Content |
|------|---------|
| `active_positions.json` | Updated if entries made |
| `portfolio_data/daily_activity.json` | Updated if entries made |
| `daily_reviews/recheck_YYYYMMDD_HHMMSS.json` | Recheck results |
| `logs/recheck.log` | Execution log |

**Dashboard Impact**: Today page updates if new entries made

---

### 1.5 EXIT Command (3:45 PM ET)

**Purpose**: Pre-close position review, execute same-day exits

**Execution Path**:
```
agent_v5.5.py exit
├── Load current portfolio
├── STEP 1: Position Sync Check (v8.9.8)
│   ├── Get Alpaca positions
│   ├── For each JSON position NOT in Alpaca:
│   │   ├── Detect as externally sold
│   │   ├── Get fill price from Alpaca orders
│   │   ├── Determine exit reason (trailing stop, stop-loss, manual)
│   │   ├── Log trade to CSV
│   │   └── Remove from portfolio
│   └── OUTPUT: alpaca_closed_trades[]
├── If all positions closed:
│   ├── Update daily activity (v8.9.8 fix)
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
| `active_positions.json` | Updated portfolio |
| `trade_history/completed_trades.csv` | Closed trade records |
| `portfolio_data/account_status.json` | Account value |
| `portfolio_data/daily_activity.json` | Today's activity |
| `daily_reviews/exit_YYYYMMDD_HHMMSS.json` | Exit results |
| `logs/exit.log` | Execution log |

**Dashboard Impact**:
- Today page shows closed trades
- Account value updates
- Trailing stop visibility (v8.7)

---

### 1.6 ANALYZE Command (4:30 PM ET)

**Purpose**: End-of-day summary, learning, NO order execution

**Autonomy Note (v8.9.9)**: This is a 100% autonomous system. ALL ANALYZE recommendations are COMMANDS for the next trading day, not suggestions. There is no human review between ANALYZE and the next GO/EXECUTE.

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
| `active_positions.json` | EOD prices updated |
| `portfolio_data/daily_activity.json` | Final daily summary |
| `portfolio_data/account_status.json` | EOD account value |
| `daily_reviews/analyze_YYYYMMDD_HHMMSS.json` | Analysis + recommendations |
| `logs/analyze.log` | Execution log |

**Dashboard Impact**:
- Account value finalized for day
- Today page shows complete activity
- Analytics updated

---

## 2. Entry Scenarios

### 2.0 Hard Blocks (v8.9.9)

**These conditions ALWAYS block entry - no exceptions:**

| Block | Condition | Rationale |
|-------|-----------|-----------|
| **VIX ≥35** | Market too volatile | Historically poor win rate |
| **Macro Blackout** | FOMC/CPI/NFP/PCE day | Binary event risk |
| **Halted/Delisted** | Cannot trade | Obvious |
| **Earnings Timing** | Reports within 24 hours | MRCY lesson (Feb 4, 2026) - gap risk unacceptable |

**Earnings Timing Rule**:
```
If candidate shows "📅 Earnings: <date>" within 24 hours:
├── PASS immediately
├── No exceptions for M&A, bidding wars, etc.
└── This is a HARD RULE - gap risk is unacceptable
```

### 2.0.1 Merger Arbitrage Entry Rules (v8.9.9)

**Background**: Merger arb IS different from momentum trading, but entry timing still matters.

**Rules** (MASI lesson - Feb 2026):
| Rule | Threshold | Rationale |
|------|-----------|-----------|
| **Spread Minimum** | ≥5% to deal price | <5% not worth opportunity cost |
| **Don't Chase Pop** | Wait if already >15% up on news | Entry timing matters |
| **Technical Warnings** | RSI >75 + climax volume = bad entry | Even for arb |
| **Time Value** | Calculate implied return | 2.5% over 4 months = poor annualized |

**Path**:
```
GO (Merger Arb Candidate)
├── Calculate spread to deal price
├── If spread <5%: PASS
├── If already ran >15% on announcement: WAIT for pullback
├── If RSI >75 + extended technicals: PASS or wait
└── Calculate annualized return vs opportunity cost
```

---

### 2.1 Normal Entry (Gap < 3%)

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
├── Add to active_positions.json
├── Update account_status.json
└── Update daily_activity.json
```

**Custom Stop Support (v8.9.9)**:
- GO can specify `custom_stop_pct` (-1% to -7%) for tighter risk management
- EXECUTE enforces -7% ceiling (custom stop can never be wider)
- Example: TPH with -3% custom stop = tighter risk for volatile catalyst

**Logging**:
- `logs/execute.log`: "✓ Bought X shares of TICKER at $Y"
- `logs/execute.log`: "Stop: $X.XX (-Y.Y%) - Custom (GO recommendation)" (if custom)
- `daily_activity.json`: Entry added to `new_entries[]`

**Dashboard**: Today page shows entry with conviction level

---

### 2.2 Gap Entry (3-8% Gap)

**Trigger**: GO recommends BUY, gap 3-8% at EXECUTE time

**Path**:
```
EXECUTE
├── Detect gap in caution zone
├── Log warning but proceed
├── Execute entry (same as normal)
└── Note gap in position metadata
```

**Logging**:
- `logs/execute.log`: "⚠️ TICKER: Gap 5.2% - entering with caution"

---

### 2.3 Skipped Entry (Gap > 8%)

**Trigger**: GO recommends BUY, gap > 8% at EXECUTE time

**Path**:
```
EXECUTE
├── Detect excessive gap
├── Skip entry
├── Save to skipped_for_gaps.json
└── Log skip reason

RECHECK (10:15 AM)
├── Load skipped stocks
├── Fetch current prices
├── If gap normalized: Execute entry
└── If still gapped: Remain skipped
```

**Logging**:
- `logs/execute.log`: "⚠️ TICKER: Gap 12.3% - SKIPPED"
- `skipped_for_gaps.json`: Stock added for RECHECK

**Dashboard**: Today page shows as "Skipped (Gap)"

---

### 2.4 Portfolio Full (10 Positions)

**Trigger**: GO wants to BUY but portfolio has 10 positions

**Path**:
```
GO
├── Detect portfolio full
├── Skip screener analysis for new entries
├── Focus on HOLD/EXIT decisions only
└── Save daily_picks with status "SKIPPED (Portfolio Full)"
```

**Dashboard**: Today page shows "Portfolio Full" status

---

## 3. Exit Scenarios

### 3.1 Stop Loss Exit (Automated)

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
├── Removes from active_positions.json
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

**Logging**:
- `completed_trades.csv`: Exit_Type = "Stop_Loss"
- `logs/exit.log`: "🚪 TICKER: EXIT - Stop loss (-7.0%)"

**Dashboard**: Today page shows exit with red return

---

### 3.2 Trailing Stop Exit

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

**Logging**:
- `completed_trades.csv`: Exit_Type = "Trailing_Stop"
- `logs/execute.log`: "🔔 TICKER was AUTO-SOLD by Alpaca trailing stop!"

**Dashboard**:
- EXIT shows trailing stops active (v8.7)
- Today page shows exit with peak return noted

---

### 3.3 Price Target Exit

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

**Logging**:
- `completed_trades.csv`: Exit_Type = "Target_Hit"
- `logs/exit.log`: "🎯 TICKER: EXIT - Target hit (+12.5%)"

---

### 3.4 Time Stop Exit

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

**Logging**:
- `completed_trades.csv`: Exit_Type = "Time_Stop"

---

### 3.5 Claude Discretionary Exit

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

**Logging**:
- `completed_trades.csv`: Exit_Reason = "Claude Exit: [reasoning]"
- `logs/exit.log`: "→ Claude recommends EXIT: TICKER"

---

### 3.6 News Invalidation Exit

**Trigger**: Negative news invalidates original thesis

**Path**:
```
EXIT (3:45 PM)
├── Fetch recent news for each position
├── Claude analyzes news impact
├── If invalidation score > 70:
│   └── Recommend exit with news context
├── Execute exit
└── Log: "News invalidation (score: X)"
```

**Logging**:
- `completed_trades.csv`: Exit_Type = "News_Invalidation"

---

### 3.7 External Sale Detection (v8.9.8)

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

**Logging**:
- `logs/execute.log`: "🔔 TICKER was SOLD externally (not in Alpaca)!"
- `completed_trades.csv`: Exit_Reason includes detection method

---

## 4. Position Sync Scenarios

### 4.1 JSON-Alpaca Mismatch (Position Missing from Alpaca)

**Detection**: EXECUTE or EXIT position sync check

**Path**: See 3.7 External Sale Detection

---

### 4.2 Alpaca Has Extra Position (Not in JSON)

**Current Behavior**: Not explicitly handled (rare edge case)

**Potential Causes**:
- Manual buy via Alpaca dashboard
- System crash after Alpaca buy but before JSON save

**Impact**: Position won't be managed by Tedbot until manually reconciled

---

### 4.3 Price/Shares Mismatch

**Detection**: Account status update compares JSON vs Alpaca

**Path**:
```
EXECUTE or EXIT
├── Compare JSON values to Alpaca values
├── If discrepancy detected:
│   ├── Log warning with both values
│   └── Use Alpaca values as source of truth
└── Continue with Alpaca values
```

**Logging**:
- `logs/execute.log`: "⚠️ Alpaca sync: Cash discrepancy $X, Equity discrepancy $Y"

---

## 5. Error Handling Scenarios

### 5.1 Claude API Timeout

**Trigger**: Claude doesn't respond within timeout (120s GO, 60s EXIT)

**Path (GO)**:
```
GO
├── API call times out
├── Retry with 2x timeout (240s)
├── If still fails:
│   ├── Enter DEGRADED MODE
│   ├── HOLD all existing positions
│   ├── Skip new entries
│   ├── Log failure to claude_api_failures.json
│   └── Return SUCCESS (graceful degradation)
```

**Path (EXIT)**:
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

**Logging**:
- `logs/claude_api_failures.json`: Failure details
- `logs/go.log` or `logs/exit.log`: "⚠️ FAILSAFE MODE"

**Dashboard**: Shows degraded/failsafe status in operations

---

### 5.2 Claude Returns No JSON

**Trigger**: Claude writes analysis but forgets JSON block

**Path (v8.9.7)**:
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

**Logging**:
- `logs/go.log`: "⚠️ No JSON found in response, retrying full GO call..."

---

### 5.3 Alpaca Order Failure

**Trigger**: Alpaca rejects order (insufficient funds, wash trade, etc.)

**Path**:
```
EXECUTE
├── Submit order to Alpaca
├── Order rejected
├── Log failure reason
├── Continue with JSON tracking (fallback)
└── Position managed without Alpaca order
```

**Logging**:
- `logs/execute.log`: "⚠️ Alpaca: [error message]"

---

### 5.4 Duplicate Trade ID (v8.9.8 Fixed)

**Trigger**: Same ticker bought twice on same date

**Previous Behavior**: Second trade blocked, not logged

**Current Behavior (v8.9.8)**:
```
Trade ID format: TICKER_ENTRY-DATE_to_EXIT-DATE
Example: ROK_2026-02-06_to_2026-02-12

This ensures uniqueness even if same ticker
bought and sold multiple times.
```

---

### 5.5 Wash Trade Detection

**Trigger**: Alpaca detects buy-sell-buy pattern too quickly

**Path**:
```
EXECUTE
├── Buy order succeeds
├── Attempt stop-loss placement
├── Alpaca rejects: "wash trade detected"
├── Wait 3 seconds (v8.9.5)
├── Retry stop-loss placement
└── If still fails: Log warning, continue without stop-loss
```

**Logging**:
- `logs/execute.log`: "⚠️ Alpaca stop-loss failed: wash trade detected"

---

## 6. Dashboard Data Flow

### 6.1 Overview Page

**Data Sources**:
| Metric | Source File | Update Frequency |
|--------|-------------|------------------|
| Account Value | `account_status.json` | Every command |
| Total Return | `account_status.json` | Every command |
| Positions | `active_positions.json` | Every command |
| Recent Trades | `completed_trades.csv` | On exits |
| Win Rate | `completed_trades.csv` | On exits |
| Sharpe Ratio | Calculated from CSV | On exits |

**API Endpoint**: `GET /api/v2/overview`

---

### 6.2 Today Page

**Data Sources**:
| Section | Source File | Update Trigger |
|---------|-------------|----------------|
| Screening Decisions | `daily_picks.json` | GO command |
| New Entries | `daily_activity.json` | EXECUTE command |
| Exits | `daily_activity.json` | EXECUTE/EXIT command |
| Trailing Stops Active | `exit_*.json` | EXIT command |

**API Endpoint**: `GET /api/v2/screening-decisions`

**Update Flow**:
```
GO → daily_picks.json (screening decisions)
EXECUTE → daily_activity.json (entries + exits)
EXIT → daily_activity.json (exits)
ANALYZE → daily_activity.json (final summary)
```

---

### 6.3 Analytics Page

**Data Sources**:
| Chart | Source | Calculation |
|-------|--------|-------------|
| Equity Curve | `completed_trades.csv` | Cumulative returns |
| Catalyst Performance | `completed_trades.csv` | Group by Catalyst_Type |
| Monthly Returns | `completed_trades.csv` | Group by month |
| Win Rate by Tier | `completed_trades.csv` | Group by Catalyst_Tier |

**API Endpoints**:
- `GET /api/v2/equity-curve`
- `GET /api/v2/catalyst-performance`
- `GET /api/v2/analytics/monthly-returns`

---

### 6.4 Alpaca Status Indicator

**States**:
| Color | Meaning | Detection |
|-------|---------|-----------|
| GREEN | Connected, synced | Alpaca API responds, position count matches |
| YELLOW | Connected, mismatch | Alpaca API responds, position count differs |
| RED | Disconnected | Alpaca API fails |

**API Endpoint**: `GET /api/v2/alpaca-status`

---

## Appendix: File Reference

### Portfolio Data Files
| File | Purpose | Written By |
|------|---------|------------|
| `active_positions.json` | Current open positions | EXECUTE, EXIT, ANALYZE |
| `pending_positions.json` | Decisions awaiting execution | GO |
| `account_status.json` | Account value, cash, P&L | All commands |
| `daily_activity.json` | Today's entries/exits | EXECUTE, EXIT, ANALYZE |
| `daily_picks.json` | Screener decisions | GO |
| `skipped_for_gaps.json` | Stocks skipped for RECHECK | EXECUTE |

### Trade History
| File | Purpose | Written By |
|------|---------|------------|
| `completed_trades.csv` | All closed trades (63 columns) | EXECUTE, EXIT |

### Daily Reviews
| File Pattern | Purpose | Written By |
|--------------|---------|------------|
| `go_YYYYMMDD_HHMMSS.json` | GO command output | GO |
| `execute_YYYYMMDD_HHMMSS.json` | EXECUTE results | EXECUTE |
| `exit_YYYYMMDD_HHMMSS.json` | EXIT results | EXIT |
| `analyze_YYYYMMDD_HHMMSS.json` | ANALYZE output + recommendations | ANALYZE |
| `recheck_YYYYMMDD_HHMMSS.json` | RECHECK results | RECHECK |

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

*Document generated for Tedbot v8.9.9*
