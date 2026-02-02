#!/usr/bin/env python3
"""
Paper Trading Lab - Agent v5.7.1 - AI-FIRST WITH EXPLICIT DECISIONS
SWING TRADING SYSTEM WITH INTELLIGENT LEARNING & OPTIMIZATION

**CRITICAL UPDATE (v5.7.1 - Jan 12, 2026 - Third-Party Refinements):**
- EXPLICIT DECISION FIELD: Claude must choose ENTER | ENTER_SMALL | PASS (prevents accidental trades)
- TIGHTENED SIZING FOR TESTING: 6-10% range (vs 5-13%) for first 5-10 days - cleaner signal validation
- STRUCTURED CONFIDENCE: HIGH | MEDIUM | LOW (machine-readable, auditable)
- PASS TARGET: 30-40% of candidates to ensure selectivity (quality over quantity)

**v5.7 Foundation (Jan 12, 2026):**
- AI-FIRST ARCHITECTURE: Claude is primary decision authority with full technical data
- Full technical indicators added to screener output (RSI, ADX, 20-MA dist, 3-day return, EMA cross)
- Threshold context provided as GUIDELINES, not hard rules - Claude weighs all factors holistically
- Position sizing as risk dial - Claude modulates risk based on conviction + technical setup
- Non-catastrophic validation blocks removed (tier, conviction) - only catastrophic checks remain
- Risk flags stored for learning (forward return analysis will show if protective)
- Catastrophic checks still enforced: VIX shutdown, macro blackout, halted stocks

**IMPORTANT NOTE (v7.1 - Dec 2025):**
- RS (Relative Strength) is now used for SCORING ONLY, not filtering
- RS >3% requirement was removed in v7.0 (Deep Research update)
- RS is calculated and adds 0-5 points to composite score
- Historical changelog references to "RS ≥3% filter" are from older versions

MAJOR IMPROVEMENTS FROM v4.3:
1. GO command reviews EXISTING portfolio with 15-min delayed premarket data
2. Enforces swing trading rules: 2-day minimum hold, proper exit criteria
3. HOLD/EXIT/BUY decision logic instead of daily portfolio rebuild
4. Leverages Polygon.io 15-min delayed data for premarket gap analysis
5. True swing trading: positions held 3-7 days unless stops/targets hit

v5.6.1 - PHASE 5.6: TECHNICAL INDICATORS (2025-11-11):
** MAJOR FEATURE RELEASE - 4 ESSENTIAL SWING TRADING FILTERS **
- Implemented comprehensive technical analysis module
  - fetch_daily_bars(): Fetches 90 days of OHLCV data from Polygon.io
  - calculate_sma(): Simple Moving Average calculation
  - calculate_ema(): Exponential Moving Average calculation
  - calculate_adx(): ADX (Average Directional Index) for trend strength
  - calculate_technical_score(): 0-25 point scoring with 4 required filters
- 4 Essential Technical Filters (ALL must pass):
  - Filter 1: Price above 50-day SMA (7 pts) - Trend direction filter
  - Filter 2: 5 EMA > 20 EMA (7 pts) - Momentum timing signal
  - Filter 3: ADX >20 (6 pts) - Trend strength, avoids choppy markets
  - Filter 4: Volume >1.5x average (5 pts) - Institutional confirmation
- GO command Phase 5.6 integration:
  - Technical scoring runs AFTER RS filter, BEFORE conviction calculation
  - Auto-rejects stocks failing ANY of the 4 technical filters
  - Prevents entries on stocks below 50 MA (downtrends)
  - Prevents entries on weak momentum (5 EMA < 20 EMA)
  - Prevents entries in choppy markets (ADX <20)
  - Prevents entries with weak volume (<1.5x average)
- Enhanced CSV tracking with 6 new columns:
  - Technical_Score (0-25 points)
  - Technical_SMA50 (price level)
  - Technical_EMA5 (price level)
  - Technical_EMA20 (price level)
  - Technical_ADX (trend strength 0-100)
  - Technical_Volume_Ratio (current/average)
- Detailed technical validation logging:
  - Shows exactly which filters passed/failed
  - Displays current price vs MAs, ADX value, volume multiple
  - Helps understand why stocks were rejected
- Research-backed implementation:
  - Based on Mark Minervini SEPA methodology
  - Aligned with Dan Zanger volume/MA requirements
  - IBD-style relative strength + technical confirmation
  - Academic validation: Lo, Mamaysky, Wang (MIT, Journal of Finance 2000)
  - 15-25% improvement in trend-following systems per research

v5.6.0 - COMPOUND GROWTH (2025-10-31):
** CRITICAL FIX: Position sizing now compounds with account growth **
- Position sizes now calculated from CURRENT account value (not fixed $1000)
- Example: With +$100 profit, 10% position = $110 (not $100)
- Losses also reduce position sizes proportionally
- Formula: position_size = (pct / 100) * (STARTING_CAPITAL + realized_pl)
- Cash tracking prevents over-allocation
- Money earns money - exponential growth potential enabled
- FIXED: Previous version left profits in cash without reinvestment

v5.5.0 - PHASE 5: LEARNING ENHANCEMENTS (2025-10-31):
** FINAL PHASE - COMPLETE SYSTEM **
- Implemented comprehensive performance analysis system
  - analyze_performance_metrics(days): Multi-dimensional analysis
  - Analyzes: Conviction accuracy, Tier performance, VIX regime, News effectiveness, RS impact, Macro events
  - Returns detailed statistics with win rates and avg returns per category
  - Generates automated recommendations for strategy calibration
- Added "learn" command to CLI
  - Usage: python agent.py learn [days]
  - Default: 30-day analysis period
  - Prints formatted performance report to console
  - Saves analysis to JSON files for tracking over time
- Performance analysis categories:
  - **Conviction Accuracy**: Win rate by HIGH/MEDIUM-HIGH/MEDIUM
  - **Catalyst Tier Performance**: Tier1 vs Tier2 vs Tier3 results
  - **VIX Regime Performance**: Win rate by VIX buckets (<15, 15-20, 20-25, 25-30, >30)
  - **News Score Effectiveness**: Returns by news score (0-5, 5-10, 10-15, 15-20)
  - **Relative Strength Impact**: Higher RS (≥3%) vs Lower RS (<3%) performance comparison
  - **Macro Event Impact**: Performance with/without nearby macro events
- Automated recommendations system:
  - Detects if HIGH conviction underperforming MEDIUM
  - Flags trades entered at VIX >30 (SHUTDOWN violations)
  - Analyzes RS percentile impact on win rates (scoring factor analysis)
  - Warns if weak news scores getting through (filter bypass)
- Learning data persistence:
  - Saves to learning_data/monthly_analysis_YYYY-MM-DD.json
  - Maintains learning_data/latest_monthly_analysis.json
  - Enables trend tracking across multiple periods
- Added pandas dependency to requirements.txt
- Complete integration with Phases 1-4 CSV columns
- Designed per MASTER_STRATEGY_BLUEPRINT Phase 5 specifications

v5.4.0 - PHASE 4: CONVICTION SIZING + RELATIVE STRENGTH (2025-10-31):
** MAJOR FEATURE RELEASE **
- Implemented relative strength calculator (3-month performance vs sector)
  - get_3month_return(): Fetches 90-day returns from Polygon.io
  - calculate_relative_strength(): Stock vs sector ETF comparison
  - SECTOR_ETF_MAP: All 11 S&P sectors mapped to ETFs
  - REQUIRED FILTER: Stock must outperform sector by ≥3%
- Implemented conviction-based position sizing system
  - calculate_conviction_level(): Determines HIGH/MEDIUM-HIGH/MEDIUM/SKIP
  - Supporting factors: Tier1, News≥10, VIX<30, RS≥3%, Multi-catalyst
  - Position sizes: HIGH 13%, MEDIUM-HIGH 11%, MEDIUM 10%, SKIP 0%
  - 5+ factors + News≥15 + VIX<25 → HIGH conviction
  - 4+ factors + News≥10 + VIX<30 → MEDIUM-HIGH conviction
  - 3+ factors + News≥5 + VIX<30 → MEDIUM conviction
- GO command Phase 4 integration:
  - Calculates relative strength for each BUY recommendation
  - RS used for scoring only (0-5 points based on RS percentile, NOT a filter)
  - Calculates conviction level based on all factors (cluster-based, max 11)
  - Position size determined by conviction (overrides Phase 2 tier sizing)
  - Prints detailed validation: RS%, conviction, supporting factors
- Enhanced CSV tracking with 5 new columns:
  - Relative_Strength (stock vs sector %)
  - Stock_Return_3M (90-day return %)
  - Sector_ETF (which ETF used for comparison)
  - Conviction_Level (HIGH/MEDIUM-HIGH/MEDIUM/SKIP)
  - Supporting_Factors (count 0-5+)
- Designed per MASTER_STRATEGY_BLUEPRINT Phase 4 specifications

v5.3.0 - PHASE 3: VIX FILTER + MACRO CALENDAR (2025-10-31):
** MAJOR FEATURE RELEASE **
- Implemented VIX-based market regime detection
  - fetch_vix_level(): Fetches VIX from Polygon.io
  - VIX ≥35: SYSTEM SHUTDOWN (no new entries)
  - VIX 30-35: CAUTIOUS (Tier 1 + News ≥15 only)
  - VIX <30: NORMAL operations
- Implemented macro event calendar with blackout windows
  - check_macro_calendar(): Checks for FOMC, CPI, NFP, PCE events
  - ALL EVENTS: Day-of only (event-day blackout, aligned with institutional best practices)
  - FOMC: Day of (2:00 PM announcement + presser)
  - CPI/NFP/PCE: Day of (8:30 AM releases, 9:45 AM entries are post-volatility)
  - Auto-blocks ALL entries during blackout periods
- GO command regime-aware filtering (Phase 3 integration):
  - Checks VIX and macro calendar BEFORE individual validation
  - Applies regime-specific filtering to BUY recommendations
  - Enriches validated positions with: vix_at_entry, market_regime, macro_event_near
- Enhanced CSV tracking with 3 new columns:
  - VIX_At_Entry (float)
  - Market_Regime (NORMAL/CAUTIOUS/SHUTDOWN)
  - Macro_Event_Near (FOMC/CPI/NFP/PCE/None)
- Designed per MASTER_STRATEGY_BLUEPRINT Phase 3 specifications

v5.2.0 - PHASE 2: CATALYST TIER SYSTEM (2025-10-31):
** MAJOR FEATURE RELEASE **
- Implemented 3-tier catalyst classification system (Tier 1/2/3)
  - classify_catalyst_tier(): Classifies catalysts by quality and conviction
  - Tier 1: High conviction (Earnings +guidance, multi-catalyst, FDA, etc.)
  - Tier 2: Medium conviction (conditional entry)
  - Tier 3: Skip (meme stocks, stale catalysts, small caps)
- Automatic position sizing based on catalyst tier (8-15%)
- Catalyst age validation with type-specific limits:
  - Earnings: ≤5 days, Upgrades: ≤2 days, Binary events: ≤1 day
- Auto-rejects Tier 3 catalysts (pre-market gaps >15%, meme stocks, <$1B cap)
- Enhanced CSV tracking with new columns:
  - Catalyst_Tier, Catalyst_Age_Days, Position_Size_Percent
  - News_Validation_Score, News_Exit_Triggered
- GO command now validates using BOTH Phase 1 (news) AND Phase 2 (tiers)
- Designed per MASTER_STRATEGY_BLUEPRINT Phase 2 specifications

v5.1.0 - PHASE 1: NEWS MONITORING (2025-10-31):
** MAJOR FEATURE RELEASE **
- Added Polygon.io News API integration for real-time news monitoring
- GO command: News validation scores (0-20 pts) for entry decisions
  - Catalyst freshness scoring (0-5 pts)
  - Momentum acceleration scoring (0-5 pts)
  - Multi-catalyst detection (0-10 pts)
  - Contradicting news penalty (negative pts)
  - Auto-reject stale/weak catalysts (score <5)
- ANALYZE command: News invalidation scores (0-100 pts) for exit decisions
  - Negative keyword scoring (critical/severe/moderate/mild)
  - Context amplifiers (quantified dollar amounts, percentages)
  - Source credibility weighting (Bloomberg 1.0x, retail 0.25x)
  - Recency bonus (breaking news <1h gets +10 pts)
  - Auto-exit on score ≥70 (BEFORE stop loss hit)
- Created learning_data/news_monitoring_log.csv for tracking
- News checks integrated into portfolio management workflow
- Designed per MASTER_STRATEGY_BLUEPRINT Phase 1 specifications

v5.0.6 DAILY ACTIVITY FIX (2025-10-30):
- Fixed "Today's Activity" to show ALL trades closed today (by exit_date from CSV)
- Previously only showed trades closed in current ANALYZE execution
- Now includes trades closed in both EXECUTE and ANALYZE commands

v5.0.5 CRITICAL TIMING FIX (2025-10-30):
- Fixed 15-minute delay pricing logic in fetch_current_prices()
- Now checks day.c (today's close) BEFORE prevDay.c (yesterday's close)
- Updated cron schedule: EXECUTE 9:45 AM, ANALYZE 4:30 PM (accounting for delay)
- Prevents stale price data causing missed stop losses (BA case: -10.4% undetected)

v5.0.4 HOLD DAYS FIX (2025-10-30):
- Fixed hold days calculation to use actual date difference
- Previously showed 0 days when should show 1+ (wasn't incrementing on exit)

v5.0.3 STANDARDIZATION (2025-10-30):
- Standardized exit reasons to simple, consistent format
- Examples: "Target reached (+11.6%)", "Stop loss (-8.2%)", "Time stop (21 days)"

v5.0.2 ALIGNMENT (2025-10-30):
- Aligned code with simplified exit strategy (full exits only, no partials)
- Updated strategy_rules.md and code documentation
- Fixed dashboard return calculation (removed double-counting)

v5.0.1 FIX (2025-10-30):
- Fixed cash tracking bug: System now properly calculates cash_available
- Cash = Starting capital - Invested positions + Realized P&L
- Account value = Positions + Cash (previously was missing returned capital)

WORKFLOW (Phase 1 - News Monitoring Integrated):
  8:45 AM - GO command:
    - Load current portfolio (yesterday's positions)
    - Fetch premarket prices (~8:30 AM via Polygon.io)
    - Calculate gaps and P&L
    - Decide: HOLD (keep positions) / EXIT (stop/target/catalyst fail) / BUY (fill vacancies)
    - ** NEW: Validate BUY recommendations with news (score 0-20) **
    - Save validated decisions to pending_positions.json

  9:45 AM - EXECUTE command (CHANGED from 9:30 AM):
    - Load pending decisions
    - Execute exits for positions marked EXIT
    - Enter new positions marked BUY
    - Update portfolio with 9:30 AM market open prices (available at 9:45 AM with 15-min delay)

  4:30 PM - ANALYZE command:
    - ** NEW: Check news invalidation (score 0-100) BEFORE price checks **
    - Auto-exit if news score ≥70 (catalyst invalidated)
    - Update all prices to 4:00 PM closing prices (available at 4:30 PM with 15-min delay)
    - Check stops/targets, close if hit
    - Log completed trades to CSV

SWING TRADING RULES ENFORCED:
- Positions held minimum 2 days unless stop/target hit
- Maximum 21 days (time stop)
- Stop loss: -7% from entry
- Price target: +10-15% from entry
- Exit only on: stop hit, target hit, catalyst invalidated, time stop
- Typical portfolio turnover: 0-3 positions per day

Usage:
  python3 agent_v5.0.py go       # 8:45 AM - Review & decide
  python3 agent_v5.0.py execute  # 9:45 AM - Execute trades (was 9:30 AM)
  python3 agent_v5.0.py analyze  # 4:50 PM - Update & close (was 4:30 PM)
"""

import os
import sys
import json
import csv
import re
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
import traceback
import pytz
import hashlib

# SendGrid for email notifications
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

# Alpaca Integration (v7.2 - Phase 1: Paper Trading)
try:
    from alpaca_broker import AlpacaBroker
    ALPACA_AVAILABLE = True
except ImportError:
    print("⚠️  AlpacaBroker not available - using JSON file portfolio tracking")
    ALPACA_AVAILABLE = False

# Configuration
ET = pytz.timezone('America/New_York')  # Eastern Time for trading operations
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
ALPHAVANTAGE_API_KEY = os.environ.get('ALPHAVANTAGE_API_KEY', '')
POLYGON_API_KEY = os.environ.get('POLYGON_API_KEY', '')
CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages'
CLAUDE_MODEL = 'claude-sonnet-4-5-20250929'
PROJECT_DIR = Path(__file__).parent

# System version tracking (Enhancement 4.7)
SYSTEM_VERSION = 'v8.0'  # Alpaca Paper Trading Integration (real brokerage API execution)

# v7.1: Ruleset versioning for policy drift prevention
def get_ruleset_version():
    """
    Calculate hash of trading rules to prevent policy drift (v7.1 validation improvement)

    Returns ruleset version string like: v7.0-3f2a1c8d

    Hash includes:
    - GO command prompt template (swing trading rules, technical filters, output format)
    - strategy_evolution/strategy_rules.md (entry/exit criteria, risk management)
    - strategy_evolution/catalyst_exclusions.json (excluded catalysts list)

    This enables tracking if strategy changes mid-evaluation period, preventing
    confounding variables when assessing system performance.
    """
    try:
        combined_content = ""

        # Component 1: GO command prompt template (lines 3648-3770 in call_claude_api)
        # Extract the EXACT text used in GO command prompts
        go_prompt_portfolio_review = """SWING TRADING RULES (STRICTLY ENFORCE):
1. Minimum hold: 2 days (unless stop/target hit or catalyst invalidated)
2. Maximum hold: 21 days (time stop)
3. Exit triggers ONLY:
   - Stop loss hit or approaching (-7%)
   - Price target hit (+10-15%)
   - Catalyst invalidated (news, guidance cut, sector reversal)
   - Time stop (21 days with <3% gain)
   - Better opportunity exists AND position is flat/small loss AND age >= 2 days
4. DO NOT exit profitable positions just because it's a new day
5. DO NOT churn daily - let swings work (3-7 days typical)
6. If position is working (profitable, catalyst intact), HOLD it

**NEW POSITIONS: AI-FIRST HOLISTIC DECISION MAKING**

You have full authority to decide which stocks to BUY based on holistic analysis of ALL factors.
The only hard blocks are catastrophic checks (VIX ≥35, macro blackout, halted/delisted stocks).

**TECHNICAL INDICATOR REFERENCE (Guidelines, NOT Hard Rules):**
Each candidate includes full technical indicators. Our model typically looks for these characteristics
when multiple factors co-exist, but you should weigh ALL factors holistically:

- RSI <70: Momentum not overextended (values >70 suggest overbought, but catalyst breakouts often run hot)
- ADX >20: Strong trend vs choppy action (values >25 indicate powerful trend)
- Volume >1.5x: Institutional participation (higher = stronger conviction)
- Above 50-MA: Uptrend confirmation (distance from MA shows extension level)
- 5 EMA > 20 EMA: Short-term momentum accelerating
- Distance from 20-MA <10%: Not overextended (values >15% may indicate parabolic move)
- 3-Day Return <15%: Sustainable momentum (values >20% may indicate exhaustion)

**HOLISTIC DECISION FRAMEWORK:**
- One or two indicators marginally outside guidelines is ACCEPTABLE if catalyst quality is strong
- Example: RSI 75 + strong FDA catalyst = may still be excellent entry (catalyst-driven breakout expected to run hot)
- Example: Extended 12% above 20-MA + $2.6B contract win = momentum justified by fundamentals
- Values DRAMATICALLY off guidelines require pause: RSI >85, extended >25%, or weak volume <1.0x
- Use your judgment to weigh: catalyst tier + news quality + relative strength + technical setup together

**DECISION TYPES (Required - Choose One Per Candidate):**

You must classify each recommendation with an explicit decision:
- ENTER: Standard entry, normal position sizing (6-10%)
- ENTER_SMALL: Reduced entry for speculative/uncertain setups (5-6% max)
- PASS: Do not enter - catalyst interesting but insufficient conviction or excessive risk

PASS is expected on 30-40% of candidates. Do not force trades on marginal setups.
Quality over quantity is critical for system success.

Examples:
- Strong FDA catalyst + RSI 72 + good volume = ENTER at 9%
- Contract win + RSI 85 + extended 18% = ENTER_SMALL at 6%
- Analyst upgrade + weak volume + Tier 3 = PASS (don't recommend)

**POSITION SIZING = RISK DIAL (TESTING PHASE):**

⚠️  TESTING MODE: Using tightened range (6-10%) for initial validation (5-10 days).
Range will widen to 5-13% after 15-20 successful trades.

For ENTER decisions:
- 9-10%: HIGH conviction - Tier 1 catalyst + strong technicals + HIGH confidence
- 7-8%: MEDIUM conviction - Strong catalyst, some technical heat + MEDIUM confidence
- 6-7%: MEDIUM/LOW conviction - Solid catalyst, multiple risk flags

For ENTER_SMALL decisions:
- 5-6%: LOW conviction - Speculative setup, concerning risk indicators

Use the full range - variance in sizing demonstrates risk discrimination."""

        go_prompt_initial_build = """**CATALYST-DRIVEN TRADING WITH HOLISTIC ANALYSIS**

You are the primary decision authority. Focus on finding stocks with strong catalysts and use all available
data to make holistic decisions. Only catastrophic checks will hard-block entries (VIX ≥35, macro blackout, halted stocks).

**CATALYST PRIORITY (Quality Over Quantity):**
- Prefer Tier 1 catalysts: Earnings beats + guidance, FDA approvals, major M&A, multi-catalyst events
- Tier 2 acceptable with strong technical setup: Analyst upgrades, sector momentum, product launches
- Better to recommend 5-7 high-quality stocks than force 10 mediocre picks
- Every recommendation needs a clear, specific catalyst you can articulate

**TECHNICAL INDICATOR GUIDELINES (Reference, NOT Hard Rules):**
Each candidate includes comprehensive technical data. Our model typically looks for these characteristics
when factors co-exist, but you should weigh ALL factors together:

- RSI <70: Momentum sustainable (>70 is overbought, but catalyst breakouts can run hot to RSI 75-80)
- ADX >20: Strong trend vs chop (>25 = powerful trend)
- Volume >1.5x: Institutional buying (higher = stronger)
- Above 50-MA: Uptrend intact (distance shows extension level)
- 5 EMA > 20 EMA: Short-term momentum positive
- Distance from 20-MA <10%: Not overextended (>15% may indicate parabolic)
- 3-Day Return <15%: Sustainable pace (>20% may signal exhaustion)

**HOLISTIC DECISION FRAMEWORK:**
- Marginally outside guidelines (RSI 72, extended 11%) is FINE if catalyst is strong
- Catalyst-driven breakouts EXPECT hot technicals - don't penalize FDA/M&A/contract wins for momentum
- Dramatically off requires caution: RSI >85, extended >25%, volume <1.0x, or multiple red flags
- Weigh catalyst quality + news score + RS + volume + technical setup together

**POSITION SIZING = RISK DIAL:**
Express your conviction through position sizing:
- 10-13%: High conviction - strong catalyst + aligned technicals
- 7-10%: Good opportunity - catalyst strong, some technical heat (high RSI, extended)
- 5-7%: Starter position - solid catalyst, multiple risk flags
- 3-5%: Speculative - intriguing setup but imperfect

Use sizing to manage risk on stocks that have good catalysts but concerning technicals."""

        combined_content += go_prompt_portfolio_review + "\n" + go_prompt_initial_build

        # Component 2: strategy_rules.md
        strategy_file = PROJECT_DIR / 'strategy_evolution' / 'strategy_rules.md'
        if strategy_file.exists():
            combined_content += "\n" + strategy_file.read_text()

        # Component 3: catalyst_exclusions.json
        exclusions_file = PROJECT_DIR / 'strategy_evolution' / 'catalyst_exclusions.json'
        if exclusions_file.exists():
            combined_content += "\n" + exclusions_file.read_text()

        # Calculate SHA256 hash (first 8 chars for readability)
        hash_obj = hashlib.sha256(combined_content.encode('utf-8'))
        hash_short = hash_obj.hexdigest()[:8]

        return f"{SYSTEM_VERSION}-{hash_short}"

    except Exception as e:
        # Fallback if hash calculation fails
        print(f"⚠️ Warning: Could not calculate ruleset version: {e}")
        return f"{SYSTEM_VERSION}-unknown"

# Calculate ruleset version at module load time
RULESET_VERSION = get_ruleset_version()

def get_universe_version():
    """
    Calculate hash of S&P 1500 universe tickers (v7.1.1 - Universe stability tracking)

    Prevents breadth drift due to constituent changes. For example:
    - Dec 2025: 993 stocks in universe → v7.1.1-abc123de
    - Jan 2026: 1012 stocks (IPOs added) → v7.1.1-xyz789ab

    This enables analysis like: "Did performance change due to strategy or universe shift?"

    Returns: universe version string (e.g., v7.1.1-abc123de)
    """
    try:
        # Load universe tickers from screener output
        universe_file = PROJECT_DIR / 'universe_tickers.json'

        if not universe_file.exists():
            return f"{SYSTEM_VERSION}-no_universe"

        with open(universe_file, 'r') as f:
            universe_data = json.load(f)

        # Sort tickers for consistent hashing (order doesn't matter)
        tickers = sorted(universe_data.get('tickers', []))

        # Calculate SHA256 hash (first 8 chars)
        hash_obj = hashlib.sha256(','.join(tickers).encode('utf-8'))
        hash_short = hash_obj.hexdigest()[:8]

        return f"{SYSTEM_VERSION}-{hash_short}"

    except Exception as e:
        # Fallback if hash calculation fails
        print(f"⚠️ Warning: Could not calculate universe version: {e}")
        return f"{SYSTEM_VERSION}-unknown"

# Calculate universe version at module load time
UNIVERSE_VERSION = get_universe_version()

class TradingAgent:
    """Production-ready trading agent v4.3 - Complete implementation"""

    def __init__(self):
        self.project_dir = PROJECT_DIR
        self.portfolio_file = self.project_dir / 'portfolio_data' / 'current_portfolio.json'
        self.account_file = self.project_dir / 'portfolio_data' / 'account_status.json'
        self.trades_csv = self.project_dir / 'trade_history' / 'completed_trades.csv'
        self.pending_file = self.project_dir / 'portfolio_data' / 'pending_positions.json'
        self.exclusions_file = self.project_dir / 'strategy_evolution' / 'catalyst_exclusions.json'
        self.daily_activity_file = self.project_dir / 'portfolio_data' / 'daily_activity.json'

        # Initialize Alpaca broker (v7.2 - Phase 1: Paper Trading Integration)
        self.broker = None
        self.use_alpaca = False
        if ALPACA_AVAILABLE:
            try:
                self.broker = AlpacaBroker()
                self.use_alpaca = True
                print("✓ Alpaca broker connected (paper trading mode)")
            except Exception as e:
                print(f"⚠️  Alpaca broker initialization failed: {e}")
                print("   Falling back to JSON file portfolio tracking")
                self.broker = None
                self.use_alpaca = False

        # Ensure required data files exist
        self._ensure_data_files()

    def _ensure_data_files(self):
        """
        Auto-create required data files if they don't exist.
        Prevents 404 errors on dashboard after git pull.
        """
        # Ensure completed_trades.csv exists with headers
        if not self.trades_csv.exists():
            self.trades_csv.parent.mkdir(parents=True, exist_ok=True)
            with open(self.trades_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Trade_ID', 'Entry_Date', 'Exit_Date', 'Ticker',
                    'Premarket_Price', 'Entry_Price', 'Exit_Price', 'Gap_Percent',
                    'Entry_Bid', 'Entry_Ask', 'Entry_Mid_Price', 'Entry_Spread_Pct', 'Slippage_Bps',  # v7.1 - Execution cost tracking
                    'Shares', 'Position_Size', 'Position_Size_Percent', 'Hold_Days', 'Return_Percent', 'Return_Dollars',
                    'Exit_Reason', 'Exit_Type', 'Catalyst_Type', 'Catalyst_Tier', 'Catalyst_Age_Days',
                    'News_Validation_Score', 'News_Exit_Triggered',
                    'VIX_At_Entry', 'Market_Regime', 'Macro_Event_Near',
                    'VIX_Regime', 'Market_Breadth_Regime',  # Phase 4 regime tracking
                    'System_Version',  # Enhancement 4.7 - Track code version per trade
                    'Ruleset_Version',  # v7.1 - Track trading rules version (policy drift prevention)
                    'Universe_Version',  # v7.1.1 - Track S&P 1500 constituent list (breadth stability)
                    'Relative_Strength', 'Stock_Return_3M', 'Sector_ETF',
                    'Conviction_Level', 'Supporting_Factors',
                    'Technical_Score', 'Technical_SMA50', 'Technical_EMA5', 'Technical_EMA20', 'Technical_ADX', 'Technical_Volume_Ratio',
                    'Volume_Quality', 'Volume_Trending_Up',  # Enhancement 2.2
                    'Keywords_Matched', 'News_Sources', 'News_Article_Count',  # Enhancement 2.5: Catalyst learning
                    'Sector', 'Stop_Loss', 'Stop_Pct', 'Price_Target',  # v7.1.1 - Added Stop_Pct for distribution analysis
                    'Trailing_Stop_Activated', 'Trailing_Stop_Price', 'Peak_Return_Pct',  # v7.1 - Exit policy tracking
                    'Thesis', 'What_Worked', 'What_Failed', 'Account_Value_After',
                    'Rotation_Into_Ticker', 'Rotation_Reason'
                ])

        # Ensure daily_activity.json exists
        if not self.daily_activity_file.exists():
            self.daily_activity_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.daily_activity_file, 'w') as f:
                json.dump({"recent_activity": [], "recently_closed": []}, f, indent=2)

        # Ensure account_status.json exists
        if not self.account_file.exists():
            self.account_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.account_file, 'w') as f:
                json.dump({
                    "account_value": 1000.00,
                    "cash_balance": 1000.00,
                    "positions_value": 0.00,
                    "total_return_percent": 0.00,
                    "total_return_dollars": 0.00,
                    "last_updated": ""
                }, f, indent=2)

        # Ensure current_portfolio.json exists
        if not self.portfolio_file.exists():
            self.portfolio_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.portfolio_file, 'w') as f:
                json.dump({
                    "positions": [],
                    "total_positions": 0,
                    "portfolio_value": 1000.00,
                    "cash_balance": 1000.00,
                    "last_updated": ""
                }, f, indent=2)

    def _format_portfolio_review(self, premarket_data):
        """Format premarket data for Claude's portfolio review"""
        lines = []
        for i, (ticker, data) in enumerate(premarket_data.items(), 1):
            # Check if using fallback price
            price_source = data.get('price_source', 'live')
            price_note = " ⚠️ (using yesterday's close - live data unavailable)" if price_source != 'live' else ""

            lines.append(f"""
POSITION {i}: {ticker}
  Entry: ${data['entry_price']:.2f} ({data['days_held']} days ago)
  Yesterday Close: ${data['yesterday_close']:.2f}
  Premarket (~8:30 AM): ${data['premarket_price']:.2f}{price_note}
  P&L: {data['pnl_percent']:+.1f}% total
  Gap Today: {data['gap_percent']:+.1f}%
  Stop Loss: ${data['stop_loss']:.2f} (-7% trigger)
  Target: ${data['price_target']:.2f} (+10% target)
  Catalyst: {data['catalyst']}
  Thesis: {data['thesis']}
""")
        return "\n".join(lines)

    def analyze_premarket_gap(self, ticker, current_price, previous_close):
        """
        Enhancement 0.1: Analyze premarket gap and determine entry/exit strategy

        BIIB Lesson: Stock gapped +11.7% premarket, then faded to +7.3% at open.
        Large gaps often fade intraday - need smart entry timing.

        Gap Classifications:
        - EXHAUSTION GAP (≥8%): Likely to fade, wait or skip
        - BREAKAWAY GAP (5-7.9%): Strong but wait for consolidation
        - CONTINUATION GAP (2-4.9%): Tradeable, wait 15min
        - NORMAL (<2%): Enter at open
        """
        # Handle None values gracefully
        if previous_close is None or current_price is None:
            return {
                'gap_pct': 0,
                'classification': 'UNKNOWN',
                'entry_strategy': 'PROCEED',
                'reasoning': 'Unable to calculate gap (missing price data)',
                'recommended_action': 'Enter at current price',
                'should_enter_at_open': True,
                'should_exit_at_open': False,
                'risk_level': 'MEDIUM'
            }

        gap_pct = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0

        if gap_pct >= 8.0:
            return {
                'gap_pct': gap_pct,
                'classification': 'EXHAUSTION_GAP',
                'entry_strategy': 'WAIT_FOR_PULLBACK_OR_SKIP',
                'reasoning': f'Gap {gap_pct:+.1f}% too large, high fade risk',
                'recommended_action': 'Wait for gap fill to support or skip entirely',
                'should_enter_at_open': False,
                'should_exit_at_open': False,  # Let it consolidate
                'risk_level': 'HIGH'
            }
        elif gap_pct >= 5.0:
            return {
                'gap_pct': gap_pct,
                'classification': 'BREAKAWAY_GAP',
                'entry_strategy': 'WAIT_30MIN_THEN_PULLBACK',
                'reasoning': f'Gap {gap_pct:+.1f}% strong, let it consolidate first',
                'recommended_action': 'First pullback to VWAP or gap support after 30min',
                'should_enter_at_open': False,
                'should_exit_at_open': False,  # Wait for consolidation
                'risk_level': 'MEDIUM'
            }
        elif gap_pct >= 2.0:
            return {
                'gap_pct': gap_pct,
                'classification': 'CONTINUATION_GAP',
                'entry_strategy': 'ENTER_AT_945AM',
                'reasoning': f'Gap {gap_pct:+.1f}% reasonable, wait for opening volatility',
                'recommended_action': 'Enter at 9:45 AM after opening rush',
                'should_enter_at_open': False,  # Wait 15min
                'should_exit_at_open': True,  # Can exit normally
                'risk_level': 'LOW'
            }
        elif gap_pct <= -3.0:
            return {
                'gap_pct': gap_pct,
                'classification': 'GAP_DOWN',
                'entry_strategy': 'ENTER_AT_OPEN_BUYING_WEAKNESS',
                'reasoning': f'Gap {gap_pct:+.1f}% down, buying weakness',
                'recommended_action': 'Enter at open if thesis intact',
                'should_enter_at_open': True,
                'should_exit_at_open': True,
                'risk_level': 'MEDIUM'
            }
        else:
            return {
                'gap_pct': gap_pct,
                'classification': 'NORMAL',
                'entry_strategy': 'ENTER_AT_OPEN',
                'reasoning': f'Gap {gap_pct:+.1f}% minimal',
                'recommended_action': 'Normal entry at market open',
                'should_enter_at_open': True,
                'should_exit_at_open': True,
                'risk_level': 'LOW'
            }

    def get_dynamic_profit_target(self, catalyst_tier, catalyst_type, catalyst_details=None):
        """
        Enhancement 1.2: Calculate catalyst-specific profit targets backed by historical data

        Research-backed targets:
        - M&A targets: Average gain +15-25% from announcement to close (4-6 months)
        - FDA approvals: Average +12-18% in first 5-10 days
        - Earnings beats (>15%): Average +8-10% in post-earnings drift (5-10 days)
        - Analyst upgrades: Average +6-8% in 5-7 days

        Returns dict with target_pct, optional stretch_target, and rationale
        """
        catalyst_type_str = catalyst_type.lower() if isinstance(catalyst_type, str) else ''

        if catalyst_tier == 'Tier1' or catalyst_tier == 'Tier 1':
            # M&A Catalyst
            if 'm&a' in catalyst_type_str or 'merger' in catalyst_type_str or 'acquisition' in catalyst_type_str:
                is_target = catalyst_details.get('is_target', False) if catalyst_details else False
                if is_target:
                    return {
                        'target_pct': 15.0,  # Conservative for 5-10 day hold
                        'stretch_target': 20.0,  # Full deal premium
                        'rationale': 'M&A target, deal premium capture',
                        'expected_hold_days': '5-10 days (or until deal close)'
                    }
                else:
                    return {
                        'target_pct': 8.0,  # Acquirer typically doesn't run as much
                        'stretch_target': None,
                        'rationale': 'M&A acquirer (not target)',
                        'expected_hold_days': '3-5 days'
                    }

            # FDA Approval
            elif 'fda' in catalyst_type_str or 'approval' in catalyst_type_str:
                return {
                    'target_pct': 15.0,
                    'stretch_target': 25.0,  # Blockbuster approvals
                    'rationale': 'FDA approval, major catalyst',
                    'expected_hold_days': '5-10 days'
                }

            # Earnings Beat / Post-Earnings Drift
            elif 'earnings' in catalyst_type_str or 'post_earnings_drift' in catalyst_type_str:
                surprise_pct = catalyst_details.get('surprise_pct', 0) if catalyst_details else 0
                if surprise_pct >= 20:
                    return {
                        'target_pct': 12.0,  # Big beats get higher targets
                        'stretch_target': 15.0,
                        'rationale': f'Earnings beat +{surprise_pct:.0f}%, strong drift expected',
                        'expected_hold_days': '5-10 days (post-earnings drift)'
                    }
                else:
                    return {
                        'target_pct': 10.0,
                        'stretch_target': None,
                        'rationale': f'Earnings beat +{surprise_pct:.0f}%',
                        'expected_hold_days': '5-7 days'
                    }

            # Major Contract
            elif 'contract' in catalyst_type_str:
                return {
                    'target_pct': 12.0,
                    'stretch_target': None,
                    'rationale': 'Major contract announcement',
                    'expected_hold_days': '5-7 days'
                }

            # Analyst Upgrade (Tier 1 only if from top firms)
            elif 'analyst' in catalyst_type_str or 'upgrade' in catalyst_type_str:
                firm = catalyst_details.get('firm', '') if catalyst_details else ''
                if firm in ['Goldman Sachs', 'Morgan Stanley', 'JP Morgan', 'BofA']:
                    return {
                        'target_pct': 12.0,
                        'stretch_target': None,
                        'rationale': f'Top-tier upgrade from {firm}',
                        'expected_hold_days': '5-7 days'
                    }
                else:
                    return {
                        'target_pct': 8.0,
                        'stretch_target': None,
                        'rationale': 'Analyst upgrade',
                        'expected_hold_days': '3-5 days'
                    }

            # Default Tier 1
            return {
                'target_pct': 10.0,
                'stretch_target': None,
                'rationale': 'Tier 1 catalyst',
                'expected_hold_days': '5-7 days'
            }

        elif catalyst_tier == 'Tier2' or catalyst_tier == 'Tier 2':
            # Tier 2 catalysts - less powerful
            return {
                'target_pct': 8.0,
                'stretch_target': None,
                'rationale': 'Tier 2 catalyst',
                'expected_hold_days': '3-5 days'
            }

        elif catalyst_tier == 'Tier3' or catalyst_tier == 'Tier 3':
            # Insider buying - longer timeframe, standard target
            return {
                'target_pct': 10.0,  # But over longer period (10-20 days)
                'stretch_target': None,
                'rationale': 'Insider buying (leading indicator)',
                'expected_hold_days': '10-20 days (longer hold)'
            }

        # Default fallback
        return {
            'target_pct': 10.0,
            'stretch_target': None,
            'rationale': 'Standard target',
            'expected_hold_days': '5-7 days'
        }

    def check_stage2_alignment(self, ticker):
        """
        Enhancement 1.5: Mark Minervini Stage 2 alignment check

        Stage 2 = Confirmed uptrend. Only trade stocks in Stage 2 to avoid:
        - Stage 1: Basing (no trend)
        - Stage 3: Topping (uptrend ending)
        - Stage 4: Declining (downtrend)

        Stage 2 Criteria (SEPA methodology):
        1. Stock above 150-day MA and 200-day MA
        2. 150-day MA above 200-day MA (trend alignment)
        3. 200-day MA trending up (not declining)
        4. Stock within 25% of 52-week high (near leadership)
        5. 50-day MA above 150-day and 200-day (short-term strength)

        Returns:
        - stage2: Boolean (True if all criteria met)
        - details: Dict with all metrics for logging
        """
        try:
            # Fetch 260 trading days (~52 weeks + buffer)
            end_date = datetime.now(ET).strftime('%Y-%m-%d')
            start_date = (datetime.now(ET) - timedelta(days=400)).strftime('%Y-%m-%d')

            response = requests.get(
                f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}',
                params={'apiKey': POLYGON_API_KEY, 'limit': 50000},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()

            if not data.get('results') or len(data['results']) < 200:
                return {'stage2': False, 'error': 'Insufficient data', 'ticker': ticker}

            # Extract closing prices
            prices = [bar['c'] for bar in data['results']]

            if len(prices) < 200:
                return {'stage2': False, 'error': f'Only {len(prices)} days of data', 'ticker': ticker}

            current_price = prices[-1]

            # Calculate moving averages
            ma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else None
            ma_150 = sum(prices[-150:]) / 150 if len(prices) >= 150 else None
            ma_200 = sum(prices[-200:]) / 200

            # Calculate 200 MA trend (compare current 200 MA to 20 days ago)
            ma_200_20d_ago = sum(prices[-220:-20]) / 200 if len(prices) >= 220 else ma_200
            ma_200_rising = ma_200 > ma_200_20d_ago

            # 52-week high
            week_52_high = max(prices[-252:]) if len(prices) >= 252 else max(prices)

            # Stage 2 checks
            above_150_200 = current_price > ma_150 and current_price > ma_200
            ma_alignment = ma_150 > ma_200 if ma_150 else False
            ma_50_strong = ma_50 > ma_150 and ma_50 > ma_200 if ma_50 else False
            near_highs = current_price >= week_52_high * 0.75  # Within 25% of 52W high

            # All criteria must pass for Stage 2
            stage2 = all([
                above_150_200,
                ma_alignment,
                ma_200_rising,
                near_highs,
                ma_50_strong
            ])

            return {
                'stage2': stage2,
                'ticker': ticker,
                'current_price': current_price,
                'ma_50': ma_50,
                'ma_150': ma_150,
                'ma_200': ma_200,
                'ma_200_rising': ma_200_rising,
                'week_52_high': week_52_high,
                'distance_from_52w_high_pct': round(((current_price / week_52_high) - 1) * 100, 1),
                'above_150_200': above_150_200,
                'ma_alignment': ma_alignment,
                'ma_50_strong': ma_50_strong,
                'near_highs': near_highs,
                'checks_passed': sum([above_150_200, ma_alignment, ma_200_rising, near_highs, ma_50_strong])
            }

        except Exception as e:
            return {'stage2': False, 'error': str(e), 'ticker': ticker}

    def enforce_sector_concentration(self, new_positions, current_portfolio, leading_sectors=None):
        """
        Enhancement 1.3 + 4.3: Enforce sector concentration limits to reduce correlation risk

        Prevents scenarios like 3 tech stocks (NVDA, AMD, AVGO) crashing together
        causing 20%+ portfolio loss.

        Rules (Phase 4 Enhanced):
        - Maximum 2 positions per sector (20% of portfolio) - REDUCED from 3
        - EXCEPTION: Allow 3 positions if sector is in top 2 leading sectors (+3% vs SPY)
        - Maximum 2 positions per industry (20% of portfolio)
        - Alert if 2+ positions in same sub-sector (high correlation warning)

        Args:
            new_positions: List of positions to validate
            current_portfolio: Current portfolio positions
            leading_sectors: List of top 2 leading sectors (from screener data)

        Returns:
        - accepted_positions: List of positions that passed validation
        - rejected_positions: List of positions with rejection reasons
        """
        MAX_PER_SECTOR = 2  # PHASE 4.3: Reduced from 3 → 2 (20% max per sector)
        MAX_PER_SECTOR_LEADING = 3  # Exception for top 2 leading sectors
        MAX_PER_INDUSTRY = 2  # 20% max per industry (e.g., Semiconductors, Biotech)

        # Default to empty list if no leading sectors provided
        if leading_sectors is None:
            leading_sectors = []

        # Log leading sectors for visibility
        if leading_sectors:
            print(f"\n   Top 2 Leading Sectors (allowed 3 positions): {', '.join(leading_sectors[:2])}")

        # Count current holdings by sector and industry
        # v5.7.1: current_portfolio may contain ticker strings (from hold_positions) or dicts (from existing_positions)
        # Since we removed enforcement, just count new positions for display
        sector_counts = {}
        industry_counts = {}

        # Validate new positions
        accepted_positions = []
        rejected_positions = []

        for new_pos in new_positions:
            ticker = new_pos.get('ticker')
            sector = new_pos.get('sector', 'Unknown')
            industry = new_pos.get('industry', 'Unknown')

            # v5.7.1: REMOVED sector/industry concentration limits
            # Claude is responsible for portfolio allocation decisions in GO prompt
            # Non-catastrophic risk - allocation is optimization, not safety
            # Claude has diversification guidelines and documents his allocation rationale
            #
            # Old logic: Hard-blocked positions if sector >2 or industry >2
            # New logic: Claude decides allocation, explains reasoning in analysis

            # Position accepted
            accepted_positions.append(new_pos)
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
            industry_counts[industry] = industry_counts.get(industry, 0) + 1

        print(f"\n   ✅ Sector diversification (Claude's allocation):")
        for sector, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(accepted_positions) * 100) if len(accepted_positions) > 0 else 0
            print(f"      {sector}: {count} positions ({pct:.0f}%)")
        print(f"      Total accepted: {len(accepted_positions)} positions")

        return accepted_positions, rejected_positions

    def check_entry_timing(self, ticker, current_price):
        """
        Enhancement 1.6: Entry timing refinement - avoid chasing extended moves

        Checks:
        - Not extended >5% above 20-day MA (wait for pullback)
        - Volume not 3x+ average (climax volume, reversal risk)
        - Not up >10% in last 3 days (overheated)
        - RSI not >70 (overbought)

        Returns:
        - entry_quality: 'GOOD', 'CAUTION', or 'POOR'
        - wait_for_pullback: Boolean
        - reasons: List of timing issues
        """
        try:
            # Fetch 30 days of data (20-day MA + buffer)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')

            response = requests.get(
                f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}',
                params={'apiKey': POLYGON_API_KEY, 'limit': 50},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if 'results' not in data:
                return {
                    'entry_quality': 'UNKNOWN',
                    'wait_for_pullback': False,
                    'reasons': ['Insufficient data for entry timing check']
                }

            results = response.json()['results']
            if len(results) < 20:
                return {
                    'entry_quality': 'UNKNOWN',
                    'wait_for_pullback': False,
                    'reasons': ['Insufficient price history (<20 days)']
                }

            # Extract prices and volumes
            prices = [r['c'] for r in results]
            volumes = [r['v'] for r in results]

            # Calculate 20-day MA
            ma_20 = sum(prices[-20:]) / 20

            # Calculate average volume (exclude today)
            avg_volume = sum(volumes[-20:-1]) / 19 if len(volumes) > 1 else volumes[-1]

            # Current metrics
            current_volume = volumes[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

            # Distance from 20-day MA
            distance_from_ma20_pct = ((current_price - ma_20) / ma_20) * 100

            # 3-day change
            if len(prices) >= 4:
                price_3d_ago = prices[-4]
                change_3d_pct = ((current_price - price_3d_ago) / price_3d_ago) * 100
            else:
                change_3d_pct = 0

            # Calculate RSI (14-period)
            rsi = self._calculate_rsi(prices, period=14)

            # Entry timing checks
            timing_issues = []
            too_extended = distance_from_ma20_pct > 5.0
            climax_volume = volume_ratio > 3.0
            too_hot = change_3d_pct > 10.0
            overbought = rsi > 70

            if too_extended:
                timing_issues.append(f'Extended {distance_from_ma20_pct:+.1f}% above 20-day MA (wait for pullback)')
            if climax_volume:
                timing_issues.append(f'Climax volume {volume_ratio:.1f}x average (reversal risk)')
            if too_hot:
                timing_issues.append(f'Up {change_3d_pct:+.1f}% in 3 days (overheated)')
            if overbought:
                timing_issues.append(f'RSI {rsi:.0f} overbought (>70)')

            # Determine entry quality
            issue_count = len(timing_issues)
            if issue_count == 0:
                entry_quality = 'GOOD'
                wait_for_pullback = False
            elif issue_count <= 2:
                entry_quality = 'CAUTION'
                wait_for_pullback = too_extended or too_hot  # Wait if extended or overheated
            else:
                entry_quality = 'POOR'
                wait_for_pullback = True

            return {
                'entry_quality': entry_quality,
                'wait_for_pullback': wait_for_pullback,
                'reasons': timing_issues,
                'distance_from_ma20_pct': distance_from_ma20_pct,
                'volume_ratio': volume_ratio,
                'change_3d_pct': change_3d_pct,
                'rsi': rsi,
                'ma_20': ma_20
            }

        except Exception as e:
            print(f"⚠️ Entry timing check failed for {ticker}: {e}")
            return {
                'entry_quality': 'UNKNOWN',
                'wait_for_pullback': False,
                'reasons': [f'Error: {str(e)}']
            }

    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return 50.0  # Neutral if insufficient data

        # Calculate price changes
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]

        # Separate gains and losses
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]

        # Calculate average gain and loss
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0  # All gains

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def detect_post_earnings_drift(self, ticker, catalyst_details):
        """
        Enhancement 1.4: Post-Earnings Drift (PED) detection

        Academic research (Bernard & Thomas 1989, Chan et al. 1996) shows:
        - Earnings surprises >15% lead to 8-12% drift over 30-60 days
        - Revenue surprises >10% confirm quality beat
        - Guidance raises signal sustained outperformance

        Returns:
        - drift_expected: Boolean
        - target_pct: Higher target for PED positions (12% vs 10%)
        - hold_period: Extended hold (30-60 days vs 3-7)
        - confidence: HIGH/MEDIUM/LOW
        - reasoning: Explanation
        """
        # Check if this is an earnings catalyst
        catalyst_type = catalyst_details.get('catalyst_type', '')
        if 'earnings' not in catalyst_type.lower():
            return {
                'drift_expected': False,
                'reasoning': 'Not an earnings catalyst'
            }

        # Get earnings surprise percentage
        earnings_surprise_pct = catalyst_details.get('earnings_surprise_pct', 0)
        revenue_surprise_pct = catalyst_details.get('revenue_surprise_pct', 0)
        guidance_raised = catalyst_details.get('guidance_raised', False)

        # PED Criteria (based on academic research)
        # Strong PED: Earnings surprise ≥20%, revenue surprise ≥10%, guidance raised
        # Medium PED: Earnings surprise ≥15%
        # Weak/None: Earnings surprise <15%

        if earnings_surprise_pct >= 20 and revenue_surprise_pct >= 10 and guidance_raised:
            return {
                'drift_expected': True,
                'target_pct': 12.0,
                'hold_period': '30-60 days',
                'confidence': 'HIGH',
                'reasoning': f'Strong PED: Earnings +{earnings_surprise_pct:.0f}%, Revenue +{revenue_surprise_pct:.0f}%, Guidance raised',
                'ped_strength': 'STRONG'
            }
        elif earnings_surprise_pct >= 20 and revenue_surprise_pct >= 10:
            return {
                'drift_expected': True,
                'target_pct': 12.0,
                'hold_period': '30-60 days',
                'confidence': 'HIGH',
                'reasoning': f'Strong PED: Earnings +{earnings_surprise_pct:.0f}%, Revenue +{revenue_surprise_pct:.0f}%',
                'ped_strength': 'STRONG'
            }
        elif earnings_surprise_pct >= 15:
            return {
                'drift_expected': True,
                'target_pct': 10.0,
                'hold_period': '20-40 days',
                'confidence': 'MEDIUM',
                'reasoning': f'Medium PED: Earnings +{earnings_surprise_pct:.0f}%',
                'ped_strength': 'MEDIUM'
            }
        else:
            return {
                'drift_expected': False,
                'reasoning': f'Earnings surprise {earnings_surprise_pct:.0f}% below PED threshold (15%)'
            }

    def _close_position(self, position, exit_price, reason):
        """Close a position and return trade data for CSV logging"""
        entry_price = position.get('entry_price', 0)
        shares = position.get('shares', 0)
        position_size = position.get('position_size', 100)

        pnl_dollars = (exit_price - entry_price) * shares
        pnl_percent = ((exit_price - entry_price) / entry_price * 100) if entry_price > 0 else 0

        # Calculate actual hold days from entry date to now (handle both YYYY-MM-DD and ISO format)
        entry_date_str = position.get('entry_date', '')
        if entry_date_str:
            if 'T' in entry_date_str:
                entry_date = datetime.fromisoformat(entry_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            else:
                entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d')
            days_held = (datetime.now() - entry_date).days
        else:
            days_held = position.get('days_held', 0)

        trade = {
            'ticker': position['ticker'],
            'entry_date': entry_date_str,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'shares': shares,
            'position_size': position_size,
            'position_size_percent': position.get('position_size_percent', 0),
            'days_held': days_held,
            'pnl_percent': round(pnl_percent, 2),
            'pnl_dollars': round(pnl_dollars, 2),
            'exit_reason': reason,
            'catalyst': position.get('catalyst', ''),
            'catalyst_tier': position.get('catalyst_tier', 'Unknown'),
            'catalyst_age_days': position.get('catalyst_age_days', 0),
            'news_validation_score': position.get('news_validation_score', 0),
            'news_exit_triggered': position.get('news_exit_triggered', False),
            'vix_at_entry': position.get('vix_at_entry', 0.0),
            'market_regime': position.get('market_regime', 'Unknown'),
            'macro_event_near': position.get('macro_event_near', 'None'),
            'vix_regime': position.get('vix_regime', 'UNKNOWN'),
            'market_breadth_regime': position.get('market_breadth_regime', 'UNKNOWN'),
            'relative_strength': position.get('relative_strength', 0.0),
            'stock_return_3m': position.get('stock_return_3m', 0.0),
            'sector_etf': position.get('sector_etf', 'Unknown'),
            'conviction_level': position.get('conviction_level') or position.get('confidence', 'MEDIUM').upper(),
            'supporting_factors': position.get('supporting_factors', 0),
            'sector': position.get('sector', ''),
            'confidence': position.get('confidence', ''),
            'thesis': position.get('thesis', ''),
            'stop_loss': position.get('stop_loss', 0),
            'stop_pct': position.get('stop_pct', 0),  # v7.1.1 - Stop distance percentage
            'price_target': position.get('price_target', 0),
            'premarket_price': position.get('premarket_price', entry_price),
            'gap_percent': position.get('gap_percent', 0),
            # v7.1 - Execution cost tracking fields
            'entry_bid': position.get('entry_bid', 0),
            'entry_ask': position.get('entry_ask', 0),
            'entry_mid_price': position.get('entry_mid_price', 0),
            'entry_spread_pct': position.get('entry_spread_pct', 0),
            'slippage_bps': position.get('slippage_bps', 0),
            # v7.1 - Exit policy tracking fields
            'trailing_stop_active': position.get('trailing_stop_active', False),
            'trailing_stop_price': position.get('trailing_stop_price', 0),
            'peak_return_pct': position.get('peak_return_pct', 0)
        }

        return trade

    def _execute_alpaca_sell(self, ticker, shares, reason):
        """
        Execute sell order via Alpaca (v7.2 - Stage 3)

        Args:
            ticker: Stock symbol
            shares: Number of shares to sell
            reason: Exit reason for logging

        Returns:
            Tuple of (success: bool, message: str, order_id: str or None)
        """
        if not self.use_alpaca or not self.broker:
            return False, "Alpaca not available - using JSON tracking", None

        try:
            # Safety check: Verify we actually have this position in Alpaca
            position = self.broker.get_position(ticker)
            if not position:
                return False, f"No Alpaca position found for {ticker}", None

            # Calculate shares to sell (use all if shares > position qty)
            shares_to_sell = min(int(shares), int(float(position.qty)))

            if shares_to_sell <= 0:
                return False, f"Invalid quantity: {shares_to_sell}", None

            # Place market sell order
            print(f"      📤 Placing Alpaca SELL order: {shares_to_sell} shares of {ticker}")
            order = self.broker.place_market_order(ticker, shares_to_sell, side='sell')

            print(f"      ✓ Alpaca order placed: {order.id} (status: {order.status})")
            return True, f"Sold {shares_to_sell} shares via Alpaca", order.id

        except Exception as e:
            error_msg = f"Alpaca sell failed: {str(e)}"
            print(f"      ⚠️ {error_msg}")
            return False, error_msg, None

    def _execute_alpaca_buy(self, ticker, position_size_dollars, entry_price):
        """
        Execute buy order via Alpaca (v7.2 - Stage 3)

        Args:
            ticker: Stock symbol
            position_size_dollars: Dollar amount to invest
            entry_price: Expected entry price (for share calculation)

        Returns:
            Tuple of (success: bool, message: str, order_id: str or None, actual_shares: int)
        """
        if not self.use_alpaca or not self.broker:
            return False, "Alpaca not available - using JSON tracking", None, 0

        try:
            # Calculate shares from dollar amount
            shares = int(position_size_dollars / entry_price)

            if shares <= 0:
                return False, f"Invalid quantity: {shares} (${position_size_dollars:.2f} / ${entry_price:.2f})", None, 0

            # Safety check: Verify we have enough buying power
            account = self.broker.get_account()
            buying_power = float(account.buying_power)

            if position_size_dollars > buying_power:
                return False, f"Insufficient buying power: ${buying_power:.2f} < ${position_size_dollars:.2f}", None, 0

            # Place market buy order
            print(f"      📤 Placing Alpaca BUY order: {shares} shares of {ticker} (~${position_size_dollars:.2f})")
            order = self.broker.place_market_order(ticker, shares, side='buy')

            print(f"      ✓ Alpaca order placed: {order.id} (status: {order.status})")
            return True, f"Bought {shares} shares via Alpaca", order.id, shares

        except Exception as e:
            error_msg = f"Alpaca buy failed: {str(e)}"
            print(f"      ⚠️ {error_msg}")
            return False, error_msg, None, 0

    def _log_trade_to_csv(self, trade):
        """
        Wrapper to log closed trade to CSV via log_completed_trade()
        Transforms trade dict from _close_position() to expected format
        """
        from datetime import datetime

        # Get account value after this trade
        account_value_after = 0
        if self.account_file.exists():
            with open(self.account_file, 'r') as f:
                account_data = json.load(f)
                account_value_after = account_data.get('account_value', 0)

        # Determine exit type
        exit_type = self._determine_exit_type(trade['exit_reason'], trade)

        trade_data = {
            'trade_id': f"{trade['ticker']}_{trade['entry_date']}",
            'entry_date': trade['entry_date'],
            'exit_date': datetime.now().strftime('%Y-%m-%d'),
            'ticker': trade['ticker'],
            'premarket_price': trade.get('premarket_price', 0),
            'entry_price': trade['entry_price'],
            'exit_price': trade['exit_price'],
            'gap_percent': trade.get('gap_percent', 0),
            'entry_bid': trade.get('entry_bid', 0),  # v7.1 - Execution cost tracking
            'entry_ask': trade.get('entry_ask', 0),
            'entry_mid_price': trade.get('entry_mid_price', 0),
            'entry_spread_pct': trade.get('entry_spread_pct', 0),
            'slippage_bps': trade.get('slippage_bps', 0),
            'shares': trade['shares'],
            'position_size': trade['position_size'],
            'position_size_percent': trade.get('position_size_percent', 0),
            'hold_days': trade['days_held'],
            'return_percent': trade['pnl_percent'],
            'return_dollars': trade['pnl_dollars'],
            'exit_reason': trade['exit_reason'],
            'exit_type': exit_type,
            'catalyst_type': trade.get('catalyst', ''),
            'catalyst_tier': trade.get('catalyst_tier', 'Unknown'),
            'catalyst_age_days': trade.get('catalyst_age_days', 0),
            'news_validation_score': trade.get('news_validation_score', 0),
            'news_exit_triggered': trade.get('news_exit_triggered', False),
            'vix_at_entry': trade.get('vix_at_entry', 0.0),
            'market_regime': trade.get('market_regime', 'Unknown'),
            'macro_event_near': trade.get('macro_event_near', 'None'),
            'vix_regime': trade.get('vix_regime', 'UNKNOWN'),
            'market_breadth_regime': trade.get('market_breadth_regime', 'UNKNOWN'),
            'system_version': SYSTEM_VERSION,
            'ruleset_version': RULESET_VERSION,  # v7.1 - Track trading rules version
            'universe_version': UNIVERSE_VERSION,  # v7.1.1 - Track S&P 1500 constituent list
            'relative_strength': trade.get('relative_strength', 0.0),
            'stock_return_3m': trade.get('stock_return_3m', 0.0),
            'sector_etf': trade.get('sector_etf', 'Unknown'),
            'conviction_level': trade.get('conviction_level', 'MEDIUM'),
            'supporting_factors': trade.get('supporting_factors', 0),
            'technical_score': trade.get('technical_score', 0),  # Phase 5.6
            'technical_sma50': trade.get('technical_sma50', 0.0),
            'technical_ema5': trade.get('technical_ema5', 0.0),
            'technical_ema20': trade.get('technical_ema20', 0.0),
            'technical_adx': trade.get('technical_adx', 0.0),
            'technical_volume_ratio': trade.get('technical_volume_ratio', 0.0),
            'volume_quality': trade.get('volume_quality', ''),  # Enhancement 2.2
            'volume_trending_up': trade.get('volume_trending_up', False),  # Enhancement 2.2
            'keywords_matched': trade.get('keywords_matched', ''),  # Enhancement 2.5
            'news_sources': trade.get('news_sources', ''),  # Enhancement 2.5
            'news_article_count': trade.get('news_article_count', 0),  # Enhancement 2.5
            'sector': trade.get('sector', ''),
            'stop_loss': trade.get('stop_loss', 0),
            'stop_pct': trade.get('stop_pct', 0),  # v7.1.1 - Stop distance percentage
            'price_target': trade.get('price_target', 0),
            'trailing_stop_activated': trade.get('trailing_stop_active', False),  # v7.1 - Exit policy tracking
            'trailing_stop_price': trade.get('trailing_stop_price', 0),
            'peak_return_pct': trade.get('peak_return_pct', 0),
            'thesis': trade.get('thesis', ''),
            'what_worked': '',  # Will be filled by learning system
            'what_failed': '',  # Will be filled by learning system
            'account_value_after': account_value_after,
            'rotation_into_ticker': trade.get('rotation_into_ticker', ''),
            'rotation_reason': trade.get('rotation_reason', '')
        }

        self.log_completed_trade(trade_data)

    def load_current_portfolio(self):
        """
        Load current portfolio from Alpaca or JSON file (v7.2 - Alpaca Integration)

        Priority:
        1. If Alpaca connected: Load from broker positions
        2. Fallback: Load from JSON file
        3. Default: Return empty portfolio structure

        Returns empty portfolio structure if no positions found
        """
        # Try Alpaca first (if connected)
        if self.use_alpaca and self.broker:
            try:
                positions = self.broker.get_positions()

                if not positions:
                    # No positions in Alpaca - return empty portfolio
                    return {
                        'positions': [],
                        'total_positions': 0,
                        'portfolio_value': self.broker.get_account_value(),
                        'last_updated': datetime.now().isoformat(),
                        'portfolio_status': 'Empty - No active positions'
                    }

                # Load supplementary metadata from JSON file (entry_date, catalyst, thesis, etc.)
                json_metadata = {}
                if self.portfolio_file.exists():
                    try:
                        with open(self.portfolio_file, 'r') as f:
                            json_portfolio = json.load(f)
                            for pos in json_portfolio.get('positions', []):
                                ticker = pos.get('ticker')
                                if ticker:
                                    json_metadata[ticker] = pos
                    except (json.JSONDecodeError, Exception):
                        pass  # Ignore JSON errors, use Alpaca defaults

                # Convert Alpaca positions to Tedbot format, merging with JSON metadata
                portfolio_positions = []
                for pos in positions:
                    ticker = pos.symbol
                    metadata = json_metadata.get(ticker, {})

                    # Calculate days held from stored entry_date
                    entry_date_str = metadata.get('entry_date', datetime.now().isoformat())
                    try:
                        entry_dt = datetime.fromisoformat(entry_date_str.replace('Z', '+00:00'))
                        if entry_dt.tzinfo:
                            entry_dt = entry_dt.replace(tzinfo=None)
                        days_held = (datetime.now() - entry_dt).days
                    except:
                        days_held = 0

                    portfolio_positions.append({
                        'ticker': ticker,
                        'shares': float(pos.qty),
                        'entry_price': float(pos.avg_entry_price),
                        'current_price': float(pos.current_price),
                        'position_size': float(pos.market_value),
                        'days_held': days_held,
                        'unrealized_gain_pct': float(pos.unrealized_plpc) * 100,
                        'unrealized_gain_dollars': float(pos.unrealized_pl),
                        # Merge from JSON metadata (preserves original entry data)
                        'catalyst': metadata.get('catalyst', 'Unknown'),
                        'thesis': metadata.get('thesis', 'Position tracking'),
                        'stop_loss': metadata.get('stop_loss', float(pos.avg_entry_price) * 0.93),
                        'price_target': metadata.get('price_target', float(pos.avg_entry_price) * 1.10),
                        'entry_date': entry_date_str,
                        # Preserve additional metadata if available
                        'catalyst_tier': metadata.get('catalyst_tier'),
                        'tier_name': metadata.get('tier_name'),
                        'conviction_level': metadata.get('conviction_level'),
                        'news_score': metadata.get('news_score'),
                        'relative_strength': metadata.get('relative_strength'),
                        'rs_rating': metadata.get('rs_rating'),
                        'vix_at_entry': metadata.get('vix_at_entry'),
                        'market_regime': metadata.get('market_regime'),
                        # CRITICAL: Preserve trailing stop data from JSON (set by ANALYZE)
                        'trailing_stop_active': metadata.get('trailing_stop_active', False),
                        'trailing_stop_price': metadata.get('trailing_stop_price'),
                        'peak_price': metadata.get('peak_price'),
                        'peak_return_pct': metadata.get('peak_return_pct'),
                    })

                account = self.broker.get_account()

                return {
                    'positions': portfolio_positions,
                    'total_positions': len(portfolio_positions),
                    'portfolio_value': float(account.equity),
                    'cash_balance': float(account.cash),
                    'last_updated': datetime.now().isoformat(),
                    'portfolio_status': f'{len(portfolio_positions)} active positions'
                }

            except Exception as e:
                print(f"⚠️  Failed to load portfolio from Alpaca: {e}")
                print("   Falling back to JSON file...")
                # Fall through to JSON loading

        # Fallback to JSON file (original behavior)
        if self.portfolio_file.exists():
            try:
                with open(self.portfolio_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️  Corrupted portfolio JSON: {e}")
                print("   Returning empty portfolio")

        # Return empty portfolio structure
            # Return empty portfolio structure
            return {
                'positions': [],
                'total_positions': 0,
                'portfolio_value': 0,
                'last_updated': '',
                'portfolio_status': 'Empty - No active positions'
            }

    # =====================================================================
    # ALPHA VANTAGE PRICE FETCHING
    # =====================================================================
    
    def fetch_current_prices(self, tickers, max_retries=2):
        """
        Fetch current prices using Polygon.io API with retry logic

        STARTER PLAN ($29/mo) - 15-MINUTE DELAYED DATA:
        - Unlimited API calls (no daily/minute rate limits)

        TIMING LOGIC (accounting for 15-min delay):
        - At 9:45 AM EXECUTE: Gets 9:30 AM market open prices (9:30 + 15min = 9:45)
        - At 4:50 PM ANALYZE: Gets 4:00 PM market close prices (4:00 + 15min + buffer = 4:50)

        FIELD PRIORITY:
        1. day.c - Today's official closing price (best after 4:15 PM)
        2. lastTrade.p - Most recent trade (for intraday)
        3. prevDay.c - Yesterday's close (emergency fallback only)

        This ensures we get TODAY's closing prices, not yesterday's stale data.

        Args:
            tickers: List of ticker symbols to fetch prices for
            max_retries: Number of retry attempts for failed fetches (default 2)

        Returns:
            dict: {ticker: price} for successfully fetched prices
        """

        if not POLYGON_API_KEY:
            print("   ⚠️ POLYGON_API_KEY not set - using entry prices")
            return {}

        prices = {}
        failed_tickers = []
        current_hour = datetime.now().hour
        is_after_market = current_hour >= 16  # After 4:00 PM

        print(f"   Fetching prices for {len(tickers)} tickers via Polygon.io...")

        for i, ticker in enumerate(tickers, 1):
            price_fetched = False

            for attempt in range(max_retries + 1):
                try:
                    # Use snapshot endpoint for 15-min delayed price
                    url = f'https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}?apiKey={POLYGON_API_KEY}'
                    response = requests.get(url, timeout=10)
                    data = response.json()

                    if data.get('status') == 'OK' and 'ticker' in data:
                        ticker_data = data['ticker']
                        price = None
                        source = None

                        # PRIORITY 1: Use today's price (day.c) if available (works during AND after market)
                        if 'day' in ticker_data and ticker_data['day'] and 'c' in ticker_data['day']:
                            price = float(ticker_data['day']['c'])
                            # Validate price is non-zero (0 means no trading data yet)
                            if price > 0:
                                source = "today's close" if is_after_market else "intraday"
                            else:
                                price = None  # Skip $0 prices

                        # PRIORITY 2: Use most recent minute bar (for intraday when day.c not available)
                        if not price and 'min' in ticker_data and ticker_data['min'] and 'c' in ticker_data['min']:
                            price = float(ticker_data['min']['c'])
                            if price > 0:
                                source = "recent min"
                            else:
                                price = None

                        # PRIORITY 3: Use most recent trade (if available)
                        if not price and 'lastTrade' in ticker_data and ticker_data['lastTrade'] and 'p' in ticker_data['lastTrade']:
                            price = float(ticker_data['lastTrade']['p'])
                            if price > 0:
                                source = "last trade"
                            else:
                                price = None

                        # PRIORITY 4: Emergency fallback to yesterday's close (should rarely happen)
                        if not price and 'prevDay' in ticker_data and ticker_data['prevDay'] and 'c' in ticker_data['prevDay']:
                            price = float(ticker_data['prevDay']['c'])
                            if price > 0:
                                source = "prev close ⚠️"
                            else:
                                price = None

                        if price and price > 0:
                            prices[ticker] = price
                            retry_str = f" (retry {attempt})" if attempt > 0 else ""
                            print(f"   [{i}/{len(tickers)}] {ticker}: ${price:.2f} ({source}){retry_str}")
                            price_fetched = True
                            break
                        else:
                            if attempt < max_retries:
                                print(f"   [{i}/{len(tickers)}] {ticker}: No price data, retrying...")
                                time.sleep(1)  # Wait 1 second before retry
                            else:
                                print(f"   [{i}/{len(tickers)}] {ticker}: No price data available (after {max_retries} retries)")
                                failed_tickers.append(ticker)
                    else:
                        # Debug: show what we actually received
                        if attempt < max_retries:
                            error_msg = data.get('error', f"status: {data.get('status', 'unknown')}")
                            print(f"   [{i}/{len(tickers)}] {ticker}: {error_msg}, retrying...")
                            time.sleep(1)  # Wait 1 second before retry
                        else:
                            if 'error' in data:
                                print(f"   [{i}/{len(tickers)}] {ticker}: API error - {data['error']} (after {max_retries} retries)")
                            else:
                                print(f"   [{i}/{len(tickers)}] {ticker}: No data (status: {data.get('status', 'unknown')}) (after {max_retries} retries)")
                            failed_tickers.append(ticker)
                            break

                    # No rate limiting needed for Starter plan (unlimited calls)
                    # Small delay to be respectful to API
                    if not price_fetched:
                        time.sleep(0.1)

                except Exception as e:
                    if attempt < max_retries:
                        print(f"   [{i}/{len(tickers)}] {ticker}: Error ({e}), retrying...")
                        time.sleep(1)  # Wait 1 second before retry
                    else:
                        print(f"   ⚠️ Error fetching {ticker} after {max_retries} retries: {e}")
                        failed_tickers.append(ticker)
                        break

            # Small delay between tickers
            if price_fetched:
                time.sleep(0.1)

        success_count = len(prices)
        total_count = len(tickers)
        print(f"   ✓ Fetched {success_count}/{total_count} prices")

        if failed_tickers:
            print(f"   ⚠️ Failed to fetch prices for: {', '.join(failed_tickers)}")

        return prices

    def calculate_atr(self, ticker, period=14):
        """
        Calculate Average True Range for volatility-aware stops (v7.0)

        ATR measures stock volatility in dollars, enabling dynamic stops that
        adapt to each stock's natural price movement. A 2.5x ATR stop gives
        room for normal volatility while protecting against adverse moves.

        Args:
            ticker: Stock ticker symbol
            period: Lookback period in days (default 14, industry standard)

        Returns:
            float: ATR value in dollars, or None if data unavailable

        Example:
            ATR = $5.00, entry = $100
            Stop = $100 - (2.5 * $5) = $87.50 (-12.5%)

            For volatile stocks (high ATR), stop is wider
            For stable stocks (low ATR), stop is tighter
        """
        if not POLYGON_API_KEY:
            return None

        try:
            # Fetch OHLC data for past period+1 days (need previous close for TR)
            from datetime import timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period + 10)  # Extra buffer for weekends

            # Use Polygon aggregates endpoint (bars)
            url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date.strftime("%Y-%m-%d")}/{end_date.strftime("%Y-%m-%d")}?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}'
            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get('status') == 'OK' and 'results' in data:
                bars = data['results']

                if len(bars) < period + 1:
                    return None  # Not enough data

                # Calculate True Range for each day
                true_ranges = []
                for i in range(1, len(bars)):
                    high = bars[i]['h']
                    low = bars[i]['l']
                    prev_close = bars[i-1]['c']

                    # TR = max(high-low, abs(high-prev_close), abs(low-prev_close))
                    tr = max(
                        high - low,
                        abs(high - prev_close),
                        abs(low - prev_close)
                    )
                    true_ranges.append(tr)

                # ATR = average of last 'period' true ranges
                if len(true_ranges) >= period:
                    atr = sum(true_ranges[-period:]) / period
                    return round(atr, 2)
                else:
                    return None
            else:
                return None

        except Exception as e:
            print(f"   ⚠️ ATR calculation failed for {ticker}: {e}")
            return None

    def check_bid_ask_spread(self, ticker):
        """
        Check bid-ask spread to prevent expensive execution (v7.0)

        Wide spreads indicate illiquid stocks where market orders can be costly.
        Skip trades if spread >0.5% to avoid giving away edge to market makers.

        Args:
            ticker: Stock ticker symbol

        Returns:
            dict: {
                'spread_pct': float,     # Spread as % of mid-price
                'should_skip': bool,     # True if spread >0.5%
                'mid_price': float,      # (bid + ask) / 2
                'bid': float,
                'ask': float
            }

        Example:
            Bid: $99.80, Ask: $100.20, Mid: $100.00
            Spread: $0.40 / $100 = 0.40% → should_skip=False (OK to trade)

            Bid: $99.00, Ask: $101.00, Mid: $100.00
            Spread: $2.00 / $100 = 2.00% → should_skip=True (too expensive)
        """
        if not POLYGON_API_KEY:
            return {'spread_pct': 0.0, 'should_skip': False, 'mid_price': None, 'bid': None, 'ask': None}

        try:
            # Use Polygon snapshot endpoint for real-time quotes
            url = f'https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}?apiKey={POLYGON_API_KEY}'
            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get('status') == 'OK' and 'ticker' in data:
                ticker_data = data['ticker']

                # Get bid/ask from lastQuote
                if 'lastQuote' in ticker_data:
                    bid = ticker_data['lastQuote'].get('p')  # bid price
                    ask = ticker_data['lastQuote'].get('P')  # ask price

                    if bid and ask and bid > 0 and ask > 0:
                        mid_price = (bid + ask) / 2
                        spread_dollars = ask - bid
                        spread_pct = (spread_dollars / mid_price) * 100

                        return {
                            'spread_pct': round(spread_pct, 3),
                            'should_skip': spread_pct > 0.5,  # Skip if >0.5%
                            'mid_price': round(mid_price, 2),
                            'bid': round(bid, 2),
                            'ask': round(ask, 2)
                        }

            # If no bid/ask data, allow trade (assume reasonable spread)
            return {'spread_pct': 0.0, 'should_skip': False, 'mid_price': None, 'bid': None, 'ask': None}

        except Exception as e:
            print(f"   ⚠️ Spread check failed for {ticker}: {e}")
            # On error, allow trade (don't block on data failure)
            return {'spread_pct': 0.0, 'should_skip': False, 'mid_price': None, 'bid': None, 'ask': None}

    # =====================================================================
    # NEWS MONITORING SYSTEM (Phase 1)
    # =====================================================================

    def fetch_polygon_news(self, ticker, limit=10, days_back=5):
        """
        Fetch recent news articles for a ticker from Polygon.io News API

        Args:
            ticker: Stock ticker symbol
            limit: Number of articles to fetch (default 10, max 1000)
            days_back: How many days back to search (default 5)

        Returns:
            List of article dictionaries with structure:
            {
                'id': str,
                'title': str,
                'article_url': str,
                'author': str,
                'description': str,
                'published_utc': str (RFC3339),
                'keywords': [str],
                'tickers': [str],
                'insights': [{'ticker': str, 'sentiment': str, 'sentiment_reasoning': str}],
                'publisher': {'name': str, ...},
                'age_hours': float  # Calculated age in hours
            }
        """
        if not POLYGON_API_KEY:
            print(f"   ⚠️ POLYGON_API_KEY not set - skipping news fetch")
            return []

        try:
            # Calculate date range
            from datetime import timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            # Format as YYYY-MM-DD
            published_utc_gte = start_date.strftime('%Y-%m-%d')

            # Build URL
            url = f'https://api.polygon.io/v2/reference/news'
            params = {
                'ticker': ticker,
                'published_utc.gte': published_utc_gte,
                'order': 'desc',  # Most recent first
                'limit': limit,
                'apiKey': POLYGON_API_KEY
            }

            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if data.get('status') == 'OK' and 'results' in data:
                articles = data['results']

                # Calculate age for each article
                for article in articles:
                    pub_time = datetime.fromisoformat(article['published_utc'].replace('Z', '+00:00'))
                    age = datetime.now(pytz.UTC) - pub_time
                    article['age_hours'] = age.total_seconds() / 3600

                print(f"   ✓ Fetched {len(articles)} news articles for {ticker}")
                return articles
            else:
                print(f"   ⚠️ No news articles found for {ticker}")
                return []

        except Exception as e:
            print(f"   ⚠️ Error fetching news for {ticker}: {e}")
            return []

    def calculate_news_validation_score(self, ticker, catalyst_type, catalyst_age_days):
        """
        Calculate news validation score (0-20 points) for ENTRY decisions (GO command)

        Scoring breakdown:
        1. Catalyst Freshness (0-5 pts)
        2. Momentum Acceleration (0-5 pts)
        3. Multi-Catalyst Detection (0-10 pts)
        4. Contradicting News Penalty (negative pts)

        Returns:
            {
                'score': int (0-20),
                'freshness_score': int (0-5),
                'momentum_score': int (0-5),
                'multi_catalyst_score': int (0-10),
                'contradiction_penalty': int (negative),
                'decision': str ('VALIDATED-HIGH' | 'VALIDATED-MEDIUM' | 'VALIDATED-LOW' | 'REJECTED'),
                'articles_analyzed': int,
                'key_findings': [str]
            }
        """

        # Fetch recent news (last 5 days)
        articles = self.fetch_polygon_news(ticker, limit=20, days_back=5)

        if not articles:
            # No news = neutral score (doesn't boost or hurt)
            return {
                'score': 5,
                'freshness_score': 0,
                'momentum_score': 0,
                'multi_catalyst_score': 0,
                'contradiction_penalty': 0,
                'decision': 'VALIDATED-LOW',
                'articles_analyzed': 0,
                'key_findings': ['No recent news articles found']
            }

        freshness_score = 0
        momentum_score = 0
        multi_catalyst_score = 0
        contradiction_penalty = 0
        key_findings = []

        # 1. CATALYST FRESHNESS SCORE (0-5 pts)
        if catalyst_type in ['Earnings_Beat', 'Earnings']:
            if catalyst_age_days <= 2:
                freshness_score = 5
                key_findings.append('FRESH earnings (0-2 days)')
            elif catalyst_age_days <= 5:
                freshness_score = 3
                key_findings.append('Moderate earnings (3-5 days)')
            elif catalyst_age_days <= 10:
                freshness_score = 1
                key_findings.append('STALE earnings (6-10 days)')
            else:
                freshness_score = 0
                key_findings.append('REJECTED - earnings >10 days old')

        elif catalyst_type in ['Analyst_Upgrade', 'Upgrade']:
            if catalyst_age_days <= 1:
                freshness_score = 5
                key_findings.append('FRESH upgrade (0-1 days)')
            elif catalyst_age_days <= 3:
                freshness_score = 2
                key_findings.append('Moderate upgrade (2-3 days)')
            else:
                freshness_score = 0
                key_findings.append('REJECTED - upgrade >3 days old')

        elif catalyst_type in ['FDA_Approval', 'Binary_Event', 'FDA', 'Contract_Win']:
            if catalyst_age_days <= 1:
                freshness_score = 5
                key_findings.append('FRESH binary event (0-1 days)')
            else:
                freshness_score = 0
                key_findings.append('REJECTED - binary event >1 day old')

        else:
            # Other catalyst types: moderate freshness scoring
            if catalyst_age_days <= 3:
                freshness_score = 3
            elif catalyst_age_days <= 7:
                freshness_score = 1

        # 2. MOMENTUM ACCELERATION SCORE (0-5 pts)
        # Count articles in last 24 hours
        recent_articles = [a for a in articles if a['age_hours'] <= 24]

        if len(recent_articles) >= 5:
            momentum_score = 5
            key_findings.append(f'STRONG momentum ({len(recent_articles)} articles in 24h)')
        elif len(recent_articles) >= 3:
            momentum_score = 3
            key_findings.append(f'MODERATE momentum ({len(recent_articles)} articles in 24h)')
        elif len(recent_articles) >= 1:
            momentum_score = 1
            key_findings.append(f'WEAK momentum ({len(recent_articles)} articles in 24h)')
        else:
            momentum_score = 0
            key_findings.append('FADING momentum (no articles in 24h)')

        # Check for analyst pile-on (multiple upgrades)
        upgrade_keywords = ['upgrade', 'initiates', 'raises target', 'raises price target']
        upgrades_48h = 0
        for article in [a for a in articles if a['age_hours'] <= 48]:
            title_lower = article.get('title', '').lower()
            if any(kw in title_lower for kw in upgrade_keywords):
                upgrades_48h += 1

        if upgrades_48h >= 3:
            momentum_score += 5
            key_findings.append(f'Analyst PILE-ON detected ({upgrades_48h} upgrades in 48h)')
        elif upgrades_48h >= 2:
            momentum_score += 3
        elif upgrades_48h >= 1:
            momentum_score += 1

        momentum_score = min(momentum_score, 5)  # Cap at 5

        # 3. MULTI-CATALYST DETECTION (0-10 pts)
        catalyst_keywords = {
            'earnings': ['earnings', 'eps beat', 'revenue beat', 'quarterly results'],
            'upgrade': ['upgrade', 'initiates', 'raises target', 'price target'],
            'contract': ['contract', 'deal', 'partnership', 'acquisition'],
            'fda': ['fda', 'approval', 'cleared', 'authorized'],
            'breakout': ['breakout', 'all-time high', 'new high']
        }

        detected_catalysts = set()
        for article in recent_articles[:10]:  # Check 10 most recent
            title_lower = article.get('title', '').lower()
            desc_lower = article.get('description', '').lower()
            combined = f"{title_lower} {desc_lower}"

            for cat_type, keywords in catalyst_keywords.items():
                if any(kw in combined for kw in keywords):
                    detected_catalysts.add(cat_type)

        if len(detected_catalysts) >= 2:
            multi_catalyst_score = 5
            key_findings.append(f'MULTI-CATALYST: {", ".join(detected_catalysts)}')

        # 4. CONTRADICTING NEWS CHECK (Penalty)
        negative_keywords = {
            'mild': ['concerns', 'weakness', 'below', 'disappointing', 'challenges', 'headwinds'],
            'moderate': ['miss', 'downgrade', 'cut', 'suspend', 'delay'],
            'severe': ['charge', 'writedown', 'impairment', 'investigation', 'lawsuit', 'fraud']
        }

        for article in recent_articles[:5]:  # Check 5 most recent
            title_lower = article.get('title', '').lower()
            desc_lower = article.get('description', '').lower()
            combined = f"{title_lower} {desc_lower}"

            # Check negative keywords
            for severity, keywords in negative_keywords.items():
                for kw in keywords:
                    if kw in combined:
                        if severity == 'severe':
                            contradiction_penalty -= 5
                            key_findings.append(f'⚠️ SEVERE negative: {kw}')
                        elif severity == 'moderate':
                            contradiction_penalty -= 3
                            key_findings.append(f'⚠️ Negative keyword: {kw}')
                        elif severity == 'mild':
                            contradiction_penalty -= 1

        # CALCULATE TOTAL SCORE
        total_score = freshness_score + momentum_score + multi_catalyst_score + contradiction_penalty

        # DECISION MATRIX
        if total_score >= 15:
            decision = 'VALIDATED-HIGH'
        elif total_score >= 10:
            decision = 'VALIDATED-MEDIUM'
        elif total_score >= 5:
            decision = 'VALIDATED-LOW'
        else:
            decision = 'REJECTED'

        return {
            'score': total_score,
            'freshness_score': freshness_score,
            'momentum_score': momentum_score,
            'multi_catalyst_score': multi_catalyst_score,
            'contradiction_penalty': contradiction_penalty,
            'decision': decision,
            'articles_analyzed': len(articles),
            'key_findings': key_findings
        }

    def calculate_news_invalidation_score(self, ticker):
        """
        Calculate news invalidation score (0-100 points) for EXIT decisions (ANALYZE command)

        Scoring breakdown:
        1. Negative Keyword Scoring (base points)
        2. Context Amplifiers (quantified damage)
        3. Source Credibility Multiplier
        4. Recency Bonus

        Returns:
            {
                'score': int (0-100+),
                'decision': str ('CRITICAL' | 'STRONG' | 'MODERATE' | 'MILD' | 'NORMAL'),
                'should_exit': bool,
                'articles_analyzed': int,
                'triggering_articles': [
                    {
                        'title': str,
                        'published': str,
                        'score': int,
                        'keywords_found': [str],
                        'source': str
                    }
                ]
            }
        """

        # Fetch very recent news (last 2 days)
        articles = self.fetch_polygon_news(ticker, limit=15, days_back=2)

        if not articles:
            return {
                'score': 0,
                'decision': 'NORMAL',
                'should_exit': False,
                'articles_analyzed': 0,
                'triggering_articles': []
            }

        # NEGATIVE KEYWORDS (Base Scoring)
        NEGATIVE_KEYWORDS = {
            'critical': ['charge', 'writedown', 'impairment', 'investigation', 'fraud', 'bankruptcy'],  # 50 pts each
            'severe': ['delay', 'downgrade', 'cut guidance', 'miss', 'suspend', 'lawsuit', 'warning'],  # 40 pts each
            'moderate': ['concerns', 'weakness', 'below', 'disappointing', 'decline', 'fall'],         # 25 pts each
            'mild': ['challenges', 'headwinds', 'competitive', 'pressure']                              # 10 pts each
        }

        # SOURCE CREDIBILITY WEIGHTS
        SOURCE_WEIGHTS = {
            'bloomberg': 1.0,
            'reuters': 1.0,
            'wsj': 1.0,
            'wall street journal': 1.0,
            'marketwatch': 0.75,
            'cnbc': 0.75,
            'seeking alpha': 0.5,
            'seeking_alpha': 0.5,
            'benzinga': 0.5,
            'yahoo': 0.5
        }

        triggering_articles = []
        max_score = 0

        for article in articles:
            article_score = 0
            keywords_found = []

            title = article.get('title', '').lower()
            desc = article.get('description', '').lower()
            combined = f"{title} {desc}"

            # 1. NEGATIVE KEYWORD SCORING
            for severity, keywords in NEGATIVE_KEYWORDS.items():
                for kw in keywords:
                    if kw in combined:
                        if severity == 'critical':
                            article_score += 50
                        elif severity == 'severe':
                            article_score += 40
                        elif severity == 'moderate':
                            article_score += 25
                        elif severity == 'mild':
                            article_score += 10
                        keywords_found.append(f"{kw} ({severity})")

            # 2. CONTEXT AMPLIFIERS
            # Quantified dollar amounts: "$4.9B charge", "$500M loss"
            import re
            dollar_matches = re.findall(r'\$[\d.]+[BMK]', combined)
            if dollar_matches:
                article_score += 15
                keywords_found.append(f"quantified: {', '.join(dollar_matches)}")

            # Quantified percentages: "-12%", "down 20%"
            percent_matches = re.findall(r'[-−]?\d+\.?\d*%', combined)
            if percent_matches:
                article_score += 10
                keywords_found.append(f"quantified: {', '.join(percent_matches)}")

            # Strong negative modifiers
            strong_negatives = ['significantly', 'sharply', 'plunge', 'collapse', 'crash']
            if any(sn in combined for sn in strong_negatives):
                article_score += 5
                keywords_found.append("strong negative modifier")

            # Multiple keywords in single article
            if len(keywords_found) >= 3:
                article_score += 10
                keywords_found.append("multiple keywords detected")

            # 3. SOURCE CREDIBILITY MULTIPLIER
            publisher_name = article.get('publisher', {}).get('name', '').lower()
            source_weight = 0.5  # Default for unknown sources

            for source, weight in SOURCE_WEIGHTS.items():
                if source in publisher_name:
                    source_weight = weight
                    break

            article_score = int(article_score * source_weight)

            # 4. RECENCY BONUS
            age_hours = article.get('age_hours', 999)
            if age_hours < 1:
                article_score += 10
                keywords_found.append("BREAKING NEWS (<1h)")
            elif age_hours < 4:
                article_score += 5
                keywords_found.append("recent news (<4h)")

            # Track this article if it has any negative content
            if article_score > 0:
                triggering_articles.append({
                    'title': article.get('title', 'Unknown'),
                    'published': article.get('published_utc', 'Unknown'),
                    'age_hours': round(age_hours, 1),
                    'score': article_score,
                    'keywords_found': keywords_found,
                    'source': publisher_name
                })

                max_score = max(max_score, article_score)

        # DECISION MATRIX
        if max_score >= 85:
            decision = 'CRITICAL'
            should_exit = True
        elif max_score >= 70:
            decision = 'STRONG'
            should_exit = True
        elif max_score >= 50:
            decision = 'MODERATE'
            should_exit = False
        elif max_score >= 30:
            decision = 'MILD'
            should_exit = False
        else:
            decision = 'NORMAL'
            should_exit = False

        # Sort triggering articles by score (highest first)
        triggering_articles.sort(key=lambda x: x['score'], reverse=True)

        return {
            'score': max_score,
            'decision': decision,
            'should_exit': should_exit,
            'articles_analyzed': len(articles),
            'triggering_articles': triggering_articles[:3]  # Top 3 worst articles
        }

    def log_news_monitoring(self, ticker, event_type, result, entry_price=None, exit_price=None):
        """
        Log news monitoring events to learning_data/news_monitoring_log.csv

        Args:
            ticker: Stock ticker
            event_type: 'VALIDATION' or 'INVALIDATION'
            result: Result dictionary from calculate_news_validation_score() or calculate_news_invalidation_score()
            entry_price: Entry price (optional)
            exit_price: Exit price (optional)
        """
        log_dir = self.project_dir / 'learning_data'
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / 'news_monitoring_log.csv'

        # Create header if file doesn't exist
        if not log_file.exists():
            with open(log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Date', 'Time', 'Ticker', 'Event_Type', 'Score', 'Decision',
                    'Articles_Analyzed', 'Key_Findings', 'Entry_Price', 'Exit_Price', 'Outcome_Pct'
                ])

        # Append log entry
        with open(log_file, 'a', newline='') as f:
            writer = csv.writer(f)

            now = datetime.now()
            date = now.strftime('%Y-%m-%d')
            time_str = now.strftime('%H:%M:%S')

            # Extract key info
            score = result.get('score', 0)
            decision = result.get('decision', 'UNKNOWN')
            articles = result.get('articles_analyzed', 0)

            # Format key findings
            if event_type == 'VALIDATION':
                findings = '; '.join(result.get('key_findings', [])[:3])
            else:  # INVALIDATION
                triggering = result.get('triggering_articles', [])
                if triggering:
                    findings = triggering[0].get('title', 'No details')[:100]
                else:
                    findings = 'No negative news'

            # Calculate outcome
            outcome_pct = None
            if entry_price and exit_price:
                outcome_pct = round(((exit_price - entry_price) / entry_price) * 100, 2)

            writer.writerow([
                date, time_str, ticker, event_type, score, decision,
                articles, findings, entry_price, exit_price, outcome_pct
            ])

    # =====================================================================
    # CATALYST TIER SYSTEM (Phase 2)
    # =====================================================================

    def classify_catalyst_tier(self, catalyst_type, catalyst_details=None):
        """
        Classify catalyst into Tier 1 (HIGH), Tier 2 (CONDITIONAL), or Tier 3 (SKIP)

        Args:
            catalyst_type: Type of catalyst (e.g., 'Earnings_Beat', 'Analyst_Upgrade', etc.)
            catalyst_details: Optional dict with additional context:
                - earnings_beat_pct: How much earnings beat consensus (%)
                - guidance_raised: Boolean, was guidance raised?
                - analyst_firm: Name of analyst firm
                - price_target_increase: Price target increase (%)
                - sector_stock_count: Number of stocks moving in sector
                - volume_multiple: Volume vs average (e.g., 2.5 = 2.5x average)
                - multi_catalyst: Boolean, are there multiple catalysts?
                - market_cap: Company market cap

        Returns:
            {
                'tier': 'Tier1' | 'Tier2' | 'Tier3',
                'tier_name': str (e.g., 'High Conviction'),
                'reasoning': str (why this tier was assigned),
                'position_size_pct': float (8-15%),
                'expected_hold_days': str (e.g., '3-5 days'),
                'target_pct': float (e.g., 12%)
            }
        """

        details = catalyst_details or {}

        # TIER 1: HIGH CONVICTION CATALYSTS

        # A. Earnings Beat + Guidance Raise
        if catalyst_type in ['Earnings_Beat', 'Earnings']:
            earnings_beat = details.get('earnings_beat_pct', 0)
            guidance_raised = details.get('guidance_raised', False)

            if earnings_beat >= 10 and guidance_raised:
                return {
                    'tier': 'Tier1',
                    'tier_name': 'High Conviction - Earnings Beat + Guidance',
                    'reasoning': f'EPS beat {earnings_beat}% with guidance raise',
                    'position_size_pct': 12.0,
                    'expected_hold_days': '3-5 days',
                    'target_pct': 13.0
                }
            elif earnings_beat >= 5:
                return {
                    'tier': 'Tier2',
                    'tier_name': 'Medium Conviction - Small Earnings Beat',
                    'reasoning': f'EPS beat {earnings_beat}% but no guidance raise',
                    'position_size_pct': 8.0,
                    'expected_hold_days': '2-4 days',
                    'target_pct': 10.0
                }
            else:
                return {
                    'tier': 'Tier3',
                    'tier_name': 'Skip - Weak Earnings',
                    'reasoning': f'EPS beat <5% ({earnings_beat}%)',
                    'position_size_pct': 0.0,
                    'expected_hold_days': 'N/A',
                    'target_pct': 0.0
                }

        # B. Multi-Catalyst Synergy
        elif catalyst_type == 'Multi_Catalyst':
            return {
                'tier': 'Tier1',
                'tier_name': 'High Conviction - Multi-Catalyst Synergy',
                'reasoning': '2+ catalysts present simultaneously (+15-25% win rate boost)',
                'position_size_pct': 13.0,
                'expected_hold_days': '3-7 days',
                'target_pct': 14.0
            }

        # C. Major Analyst Upgrade
        elif catalyst_type in ['Analyst_Upgrade', 'Upgrade']:
            analyst_firm = details.get('analyst_firm', '').lower()
            price_target_increase = details.get('price_target_increase', 0)

            # Top-tier firms
            top_tier_firms = ['goldman', 'morgan stanley', 'jpmorgan', 'jpm', 'bofa', 'citi']

            if any(firm in analyst_firm for firm in top_tier_firms) and price_target_increase >= 15:
                return {
                    'tier': 'Tier1',
                    'tier_name': 'High Conviction - Major Analyst Upgrade',
                    'reasoning': f'Top-tier firm upgrade with {price_target_increase}% PT increase',
                    'position_size_pct': 11.0,
                    'expected_hold_days': '2-4 days',
                    'target_pct': 10.0
                }
            else:
                return {
                    'tier': 'Tier2',
                    'tier_name': 'Medium Conviction - Smaller Firm Upgrade',
                    'reasoning': f'Upgrade from {analyst_firm or "smaller firm"}',
                    'position_size_pct': 8.0,
                    'expected_hold_days': '2-3 days',
                    'target_pct': 8.0
                }

        # D. Strong Sector Momentum
        elif catalyst_type in ['Sector_Momentum', 'Sector']:
            sector_stock_count = details.get('sector_stock_count', 1)
            volume_multiple = details.get('volume_multiple', 1.0)

            if sector_stock_count >= 3 and volume_multiple >= 2.0:
                return {
                    'tier': 'Tier1',
                    'tier_name': 'High Conviction - Strong Sector Momentum',
                    'reasoning': f'{sector_stock_count} stocks moving, {volume_multiple}x volume',
                    'position_size_pct': 10.0,
                    'expected_hold_days': '5-10 days',
                    'target_pct': 11.0
                }
            else:
                return {
                    'tier': 'Tier2',
                    'tier_name': 'Medium Conviction - Weak Sector Momentum',
                    'reasoning': f'Only {sector_stock_count} stocks, {volume_multiple}x volume',
                    'position_size_pct': 8.0,
                    'expected_hold_days': '3-5 days',
                    'target_pct': 9.0
                }

        # E. Confirmed Technical Breakout
        elif catalyst_type in ['Technical_Breakout', 'Breakout']:
            volume_multiple = details.get('volume_multiple', 1.0)

            if volume_multiple >= 2.0:
                return {
                    'tier': 'Tier1',
                    'tier_name': 'High Conviction - Confirmed Breakout',
                    'reasoning': f'Breakout with {volume_multiple}x volume (institutional buying)',
                    'position_size_pct': 9.0,
                    'expected_hold_days': '2-5 days',
                    'target_pct': 10.0
                }
            else:
                return {
                    'tier': 'Tier2',
                    'tier_name': 'Medium Conviction - Low-Volume Breakout',
                    'reasoning': f'Breakout with only {volume_multiple}x volume',
                    'position_size_pct': 8.0,
                    'expected_hold_days': '2-3 days',
                    'target_pct': 8.0
                }

        # F. FDA Approval / Binary Event
        elif catalyst_type in ['FDA_Approval', 'FDA', 'Binary_Event']:
            return {
                'tier': 'Tier1',
                'tier_name': 'High Conviction - Binary Event',
                'reasoning': 'FDA approval (must enter within 24h - inverted-J pattern)',
                'position_size_pct': 10.0,
                'expected_hold_days': '1-3 days',
                'target_pct': 12.0
            }

        # G. Contract Win / M&A
        elif catalyst_type in ['Contract_Win', 'M&A', 'Merger']:
            return {
                'tier': 'Tier1',
                'tier_name': 'High Conviction - Contract/M&A',
                'reasoning': 'Major contract win or M&A announcement',
                'position_size_pct': 10.0,
                'expected_hold_days': '2-5 days',
                'target_pct': 11.0
            }

        # TIER 3: AUTO-EXCLUDE CATALYSTS

        # Meme stocks
        elif catalyst_type == 'Meme_Stock':
            return {
                'tier': 'Tier3',
                'tier_name': 'Skip - Meme Stock',
                'reasoning': 'Sentiment-driven, no fundamental edge',
                'position_size_pct': 0.0,
                'expected_hold_days': 'N/A',
                'target_pct': 0.0
            }

        # Pre-market gap >15%
        elif catalyst_type == 'Large_Gap':
            gap_pct = details.get('gap_percent', 0)
            if gap_pct > 15:
                return {
                    'tier': 'Tier3',
                    'tier_name': 'Skip - Large Gap',
                    'reasoning': f'Gap {gap_pct}% >15% (80%+ fade probability)',
                    'position_size_pct': 0.0,
                    'expected_hold_days': 'N/A',
                    'target_pct': 0.0
                }

        # Small cap (<$1B)
        market_cap = details.get('market_cap_billions', 999)
        if market_cap < 1.0:
            return {
                'tier': 'Tier3',
                'tier_name': 'Skip - Small Cap',
                'reasoning': f'Market cap ${market_cap}B <$1B (illiquid)',
                'position_size_pct': 0.0,
                'expected_hold_days': 'N/A',
                'target_pct': 0.0
            }

        # Default: Unknown catalyst type -> Tier 2 (conditional)
        return {
            'tier': 'Tier2',
            'tier_name': 'Medium Conviction - Unknown Catalyst',
            'reasoning': f'Catalyst type: {catalyst_type}',
            'position_size_pct': 8.0,
            'expected_hold_days': '2-5 days',
            'target_pct': 9.0
        }

    def check_catalyst_age_validity(self, catalyst_type, catalyst_age_days):
        """
        Check if catalyst is too stale to trade

        Returns:
            {
                'is_valid': bool,
                'reason': str
            }
        """

        # Earnings: Must be ≤5 days old
        if catalyst_type in ['Earnings_Beat', 'Earnings']:
            if catalyst_age_days <= 5:
                return {'is_valid': True, 'reason': f'Fresh earnings ({catalyst_age_days} days)'}
            else:
                return {'is_valid': False, 'reason': f'Stale earnings ({catalyst_age_days} days >5 day limit)'}

        # Analyst Upgrades: Must be ≤2 days old
        elif catalyst_type in ['Analyst_Upgrade', 'Upgrade']:
            if catalyst_age_days <= 2:
                return {'is_valid': True, 'reason': f'Fresh upgrade ({catalyst_age_days} days)'}
            else:
                return {'is_valid': False, 'reason': f'Stale upgrade ({catalyst_age_days} days >2 day limit)'}

        # Binary Events (FDA, M&A): Must be ≤1 day old
        elif catalyst_type in ['FDA_Approval', 'FDA', 'Binary_Event', 'Contract_Win', 'M&A']:
            if catalyst_age_days <= 1:
                return {'is_valid': True, 'reason': f'Fresh binary event ({catalyst_age_days} days)'}
            else:
                return {'is_valid': False, 'reason': f'Stale binary event ({catalyst_age_days} days >1 day limit)'}

        # Other catalysts: 3-day general limit
        else:
            if catalyst_age_days <= 3:
                return {'is_valid': True, 'reason': f'Fresh catalyst ({catalyst_age_days} days)'}
            else:
                return {'is_valid': False, 'reason': f'Stale catalyst ({catalyst_age_days} days >3 day limit)'}

    # =====================================================================
    # VIX FILTER + MACRO CALENDAR (Phase 3)
    # =====================================================================

    def fetch_vix_level(self):
        """
        Fetch current VIX (CBOE Volatility Index) from Polygon.io

        Returns:
            {
                'vix': float (e.g., 18.5),
                'timestamp': str,
                'regime': str ('NORMAL' | 'CAUTIOUS' | 'SHUTDOWN'),
                'message': str
            }
        """

        if not POLYGON_API_KEY:
            print("   ⚠️ POLYGON_API_KEY not set - VIX check skipped")
            return {
                'vix': 20.0,  # Assume normal
                'timestamp': datetime.now().isoformat(),
                'regime': 'NORMAL',
                'message': 'API key not set - assumed normal regime'
            }

        try:
            vix_level = None
            source = None

            # Fetch from CBOE (official VIX source - free)
            try:
                # CBOE publishes daily VIX data as CSV
                url = 'https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv'
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    if len(lines) >= 2:
                        # Get last line (most recent data)
                        last_line = lines[-1]
                        parts = last_line.split(',')
                        # CSV format: DATE,OPEN,HIGH,LOW,CLOSE
                        if len(parts) >= 5:
                            vix_level = float(parts[4])  # Close price
                            source = 'CBOE'
                            print(f"   ℹ️ Using CBOE VIX: {vix_level:.2f}")
            except Exception as e:
                print(f"   ℹ️ CBOE VIX unavailable: {e}")

            # If we got VIX data, use it
            if vix_level and vix_level > 0:
                # Determine regime based on VIX level
                if vix_level >= 35:
                    regime = 'SHUTDOWN'
                    message = f'VIX {vix_level:.1f} ≥35: SYSTEM SHUTDOWN - No new entries (source: {source})'
                elif vix_level >= 30:
                    regime = 'CAUTIOUS'
                    message = f'VIX {vix_level:.1f} (30-35): HIGHEST CONVICTION ONLY (source: {source})'
                else:
                    regime = 'NORMAL'
                    message = f'VIX {vix_level:.1f} <30: Normal operations (source: {source})'

                return {
                    'vix': round(vix_level, 2),
                    'timestamp': datetime.now().isoformat(),
                    'regime': regime,
                    'message': message,
                    'source': source
                }

            # If CBOE failed, fall back to assumption
            print("   ⚠️ VIX data unavailable from CBOE, assuming normal regime")
            return {
                'vix': 20.0,
                'timestamp': datetime.now().isoformat(),
                'regime': 'NORMAL',
                'message': 'VIX data unavailable - assumed normal regime',
                'source': 'assumption'
            }

        except Exception as e:
            print(f"   ⚠️ Error fetching VIX: {e}")
            return {
                'vix': 20.0,
                'timestamp': datetime.now().isoformat(),
                'regime': 'NORMAL',
                'message': f'Error fetching VIX - assumed normal regime',
                'source': 'assumption'
            }

    def check_market_breadth(self):
        """
        PHASE 4.2: Market Breadth & Trend Filter

        Checks market health to avoid trading during rotational/choppy conditions.
        Catalyst-driven swing strategies perform poorly when:
        - Market is in downtrend (SPY below key MAs)
        - Breadth is poor (< 40% of stocks above 50-day MA)
        - Rotational environment (sectors whipsawing)

        Returns:
            {
                'spy_above_50d': bool,
                'spy_above_200d': bool,
                'breadth_pct': float (% of screener stocks above 50-day MA),
                'market_healthy': bool,
                'regime': str ('HEALTHY' | 'DEGRADED' | 'UNHEALTHY'),
                'position_size_adjustment': float (1.0 = normal, 0.8 = reduce 20%),
                'message': str
            }
        """
        try:
            # Fetch SPY data for trend check (200 days needed for 200-day MA)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=250)  # ~1 year

            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            url = f'https://api.polygon.io/v2/aggs/ticker/SPY/range/1/day/{start_str}/{end_str}?apiKey={POLYGON_API_KEY}'
            response = requests.get(url, timeout=10)
            data = response.json()

            spy_above_50d = False
            spy_above_200d = False

            if data.get('status') in ['OK', 'DELAYED'] and 'results' in data:
                results = data['results']

                if len(results) >= 200:
                    current_price = results[-1]['c']

                    # Calculate 50-day and 200-day MAs
                    ma_50 = sum([r['c'] for r in results[-50:]]) / 50
                    ma_200 = sum([r['c'] for r in results[-200:]]) / 200

                    spy_above_50d = current_price > ma_50
                    spy_above_200d = current_price > ma_200

            # v7.0: Use pre-calculated breadth from screener (prevent lookahead bias)
            # Screener calculates breadth at 7:00 AM and saves to screener_candidates.json
            # GO command (9:00 AM) uses that pre-calculated value
            # This ensures we don't use end-of-day breadth data for intraday decisions
            screener_data = self.load_screener_candidates()
            breadth_pct = 0
            breadth_timestamp = 'unknown'

            if screener_data:
                # v7.0: Use pre-calculated breadth if available (preferred)
                if 'breadth_pct' in screener_data:
                    breadth_pct = screener_data['breadth_pct']
                    breadth_timestamp = screener_data.get('breadth_timestamp', screener_data.get('scan_time', 'unknown'))
                # Fallback: Calculate from candidates (legacy support)
                elif screener_data.get('candidates'):
                    candidates = screener_data['candidates']
                    total = len(candidates)
                    above_50d = sum(1 for c in candidates if c.get('technical_setup', {}).get('above_50d_sma', False))
                    breadth_pct = (above_50d / total * 100) if total > 0 else 0
                    breadth_timestamp = screener_data.get('scan_time', 'unknown')

            # Determine market regime (BREADTH-BASED ONLY - aligned with institutional best practices)
            # Comprehensive individual stock screening (Stage 2, RS top 20%, Tier 1 catalysts, 7% stops)
            # provides better protection than blunt SPY filter for catalyst-driven strategy
            #
            # HEALTHY: Breadth ≥50% (majority of stocks in uptrends)
            # DEGRADED: Breadth 40-49% (mixed/rotational market)
            # UNHEALTHY: Breadth <40% (defensive/weak market)

            if breadth_pct >= 50:
                regime = 'HEALTHY'
                adjustment = 1.0
                message = f'✓ Market HEALTHY: Breadth {breadth_pct:.0f}% (majority in uptrends) [as of {breadth_timestamp}]'
            elif breadth_pct >= 40:
                regime = 'DEGRADED'
                adjustment = 0.8  # Reduce position sizes by 20%
                message = f'⚠️ Market DEGRADED: Breadth {breadth_pct:.0f}% (rotational market) - reducing size 20% [as of {breadth_timestamp}]'
            else:
                regime = 'UNHEALTHY'
                adjustment = 0.6  # Reduce position sizes by 40%
                message = f'⚠️ Market UNHEALTHY: Breadth {breadth_pct:.0f}% (defensive market) - reducing size 40% [as of {breadth_timestamp}]'

            return {
                'spy_above_50d': spy_above_50d,
                'spy_above_200d': spy_above_200d,
                'breadth_pct': round(breadth_pct, 1),
                'breadth_timestamp': breadth_timestamp,  # v7.0: Include timestamp for transparency
                'market_healthy': regime == 'HEALTHY',
                'regime': regime,
                'position_size_adjustment': adjustment,
                'message': message
            }

        except Exception as e:
            # On error, assume healthy (don't block trading on API failures)
            print(f"   ⚠️ Market breadth check failed: {e}")
            return {
                'spy_above_50d': True,
                'spy_above_200d': True,
                'breadth_pct': 50.0,
                'market_healthy': True,
                'regime': 'HEALTHY',
                'position_size_adjustment': 1.0,
                'message': 'Market breadth check failed - assuming healthy'
            }

    def check_macro_calendar(self, check_date=None):
        """
        Check if a date falls within blackout windows for major macro events

        Major events with blackout windows (EVENT-DAY ONLY):
        - FOMC Meeting: Day of only (2:00 PM announcement + press conference)
        - CPI Release: Day of only (8:30 AM release)
        - NFP (Jobs Report): Day of only (8:30 AM release)
        - PCE (Inflation): Day of only (8:30 AM release)

        Note: Day-before restrictions removed (aligned with institutional best practices).
        Comprehensive screening process (RS, technical, institutional signals) handles volatility.

        Args:
            check_date: Date to check (datetime object, defaults to today)

        Returns:
            {
                'is_blackout': bool,
                'event_type': str ('FOMC' | 'CPI' | 'NFP' | 'PCE' | None),
                'event_date': str,
                'message': str
            }
        """

        if check_date is None:
            check_date = datetime.now()

        # Convert to date for comparison
        check_date = check_date.date() if hasattr(check_date, 'date') else check_date

        # 2025 Macro Calendar (hardcoded for reliability)
        # Format: (event_date, event_type, description)
        macro_events_2025 = [
            # FOMC Meetings (2-day before, 1-day after blackout)
            ('2025-01-29', 'FOMC', 'FOMC Meeting'),
            ('2025-03-19', 'FOMC', 'FOMC Meeting'),
            ('2025-05-07', 'FOMC', 'FOMC Meeting'),
            ('2025-06-18', 'FOMC', 'FOMC Meeting'),
            ('2025-07-30', 'FOMC', 'FOMC Meeting'),
            ('2025-09-17', 'FOMC', 'FOMC Meeting'),
            ('2025-11-05', 'FOMC', 'FOMC Meeting'),
            ('2025-12-17', 'FOMC', 'FOMC Meeting'),

            # CPI Release (1-day before, day of blackout) - typically mid-month
            # ('2025-11-13', 'CPI', 'CPI Release'),  # CANCELLED - Government shutdown
            ('2025-12-11', 'CPI', 'CPI Release'),

            # NFP (Jobs Report) - First Friday of each month (1-day before, day of blackout)
            ('2025-11-07', 'NFP', 'Jobs Report'),
            ('2025-12-05', 'NFP', 'Jobs Report'),

            # PCE (Inflation) - End of month (1-day before, day of blackout)
            ('2025-11-26', 'PCE', 'PCE Release'),
            ('2025-12-23', 'PCE', 'PCE Release'),
        ]

        # Check each event
        for event_date_str, event_type, description in macro_events_2025:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()

            # Define blackout windows - EVENT-DAY ONLY (aligned with institutional best practices)
            # Comprehensive screening (RS, technical filters, institutional signals) handles volatility
            from datetime import timedelta

            if event_type == 'FOMC':
                # FOMC: Day of only (2:00 PM announcement + press conference)
                # Avoid new entries during presser volatility, but allow day before/after
                blackout_start = event_date
                blackout_end = event_date
            else:
                # CPI, NFP, PCE: Day of only (8:30 AM releases)
                # 9:45 AM entries are 75 min after release - volatility settled
                blackout_start = event_date
                blackout_end = event_date

            # Check if check_date falls in blackout window
            if blackout_start <= check_date <= blackout_end:
                return {
                    'is_blackout': True,
                    'event_type': event_type,
                    'event_date': event_date_str,
                    'message': f'{event_type} blackout ({description} on {event_date_str})'
                }

        # No blackout
        return {
            'is_blackout': False,
            'event_type': None,
            'event_date': None,
            'message': 'No macro events - safe to trade'
        }

    # =====================================================================
    # RELATIVE STRENGTH + CONVICTION SIZING (Phase 4)
    # =====================================================================

    # Sector to ETF mapping (11 S&P sectors)
    SECTOR_ETF_MAP = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Financials': 'XLF',
        'Consumer Discretionary': 'XLY',
        'Industrials': 'XLI',
        'Consumer Staples': 'XLP',
        'Energy': 'XLE',
        'Utilities': 'XLU',
        'Real Estate': 'XLRE',
        'Materials': 'XLB',
        'Communication Services': 'XLC'
    }

    def get_3month_return(self, ticker):
        """
        Get 3-month return for a ticker using Polygon.io

        Returns: Float (percentage return over 3 months, e.g., 15.5 = +15.5%)
        """
        if not POLYGON_API_KEY:
            return 0.0  # Can't calculate without API

        try:
            from datetime import timedelta

            # Calculate date range (90 days ago to today)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)

            # Format dates for Polygon API
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            # Use aggregates (bars) endpoint for historical data
            # Get first bar (90 days ago) and last bar (today)
            url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_str}/{end_str}?apiKey={POLYGON_API_KEY}'
            response = requests.get(url, timeout=15)
            data = response.json()

            # Accept both 'OK' and 'DELAYED' status (delayed data is fine for our purposes)
            if data.get('status') in ['OK', 'DELAYED'] and 'results' in data and len(data['results']) >= 2:
                results = data['results']

                # First close (90 days ago) and last close (today)
                first_close = results[0]['c']
                last_close = results[-1]['c']

                # Calculate percentage return
                return_pct = ((last_close - first_close) / first_close) * 100
                return round(return_pct, 2)

            return 0.0  # Not enough data

        except Exception as e:
            print(f"   ⚠️ Error calculating 3M return for {ticker}: {e}")
            return 0.0

    def calculate_relative_strength(self, ticker, sector):
        """
        Calculate stock's 3-month performance vs its sector ETF

        Args:
            ticker: Stock ticker
            sector: Sector name (e.g., 'Technology', 'Healthcare')

        Returns:
            {
                'relative_strength': float (e.g., 5.2 = outperforming sector by 5.2%),
                'stock_return_3m': float,
                'sector_return_3m': float,
                'sector_etf': str,
                'passed_filter': bool (True if RS ≥3%)
            }
        """

        # Get sector ETF
        sector_etf = self.SECTOR_ETF_MAP.get(sector, 'SPY')  # Default to S&P 500 if unknown sector

        # Calculate returns
        stock_return = self.get_3month_return(ticker)
        sector_return = self.get_3month_return(sector_etf)

        # Relative strength = stock return - sector return
        relative_strength = stock_return - sector_return

        # Enhancement 2.1: RS Rank Percentile (0-100 scale)
        # Map RS to percentile-style rating
        if relative_strength >= 15:
            rs_rating = 95
        elif relative_strength >= 10:
            rs_rating = 85
        elif relative_strength >= 7:
            rs_rating = 75
        elif relative_strength >= 5:
            rs_rating = 65
        elif relative_strength >= 3:
            rs_rating = 55  # Minimum acceptable
        elif relative_strength >= 0:
            rs_rating = 40
        else:
            # Underperforming sector
            rs_rating = max(0, 30 + relative_strength * 2)  # -15% RS = 0 rating

        return {
            'relative_strength': round(relative_strength, 2),
            'rs_rating': int(rs_rating),  # 0-100 percentile-style score
            'stock_return_3m': stock_return,
            'sector_return_3m': sector_return,
            'sector_etf': sector_etf,
            'passed_filter': True  # v7.1: RS now scoring only, not a filter
        }

    # =====================================================================
    # TECHNICAL INDICATORS MODULE (Phase 5.6 - Essential Swing Trading Filters)
    # =====================================================================

    def fetch_daily_bars(self, ticker, days=90):
        """
        Fetch daily price bars for technical analysis

        Args:
            ticker: Stock ticker symbol
            days: Number of days of history to fetch (default 90 for moving averages)

        Returns:
            List of bar dictionaries with OHLCV data, or empty list on error
            Each bar: {'date': 'YYYY-MM-DD', 'open': float, 'high': float, 'low': float, 'close': float, 'volume': int}
        """
        if not POLYGON_API_KEY:
            return []

        try:
            from datetime import timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_str}/{end_str}?apiKey={POLYGON_API_KEY}'
            response = requests.get(url, timeout=15)
            data = response.json()

            if data.get('status') in ['OK', 'DELAYED'] and 'results' in data:
                bars = []
                for bar in data['results']:
                    bars.append({
                        'date': datetime.fromtimestamp(bar['t'] / 1000).strftime('%Y-%m-%d'),
                        'open': bar['o'],
                        'high': bar['h'],
                        'low': bar['l'],
                        'close': bar['c'],
                        'volume': bar['v']
                    })
                return bars

            return []

        except Exception as e:
            print(f"   ⚠️ Error fetching bars for {ticker}: {e}")
            return []

    def calculate_sma(self, bars, period):
        """Calculate Simple Moving Average"""
        if len(bars) < period:
            return None

        closes = [bar['close'] for bar in bars[-period:]]
        return sum(closes) / period

    def calculate_ema(self, bars, period):
        """Calculate Exponential Moving Average"""
        if len(bars) < period:
            return None

        closes = [bar['close'] for bar in bars]

        # Start with SMA for first period
        sma = sum(closes[:period]) / period
        multiplier = 2 / (period + 1)

        ema = sma
        for close in closes[period:]:
            ema = (close * multiplier) + (ema * (1 - multiplier))

        return ema

    def calculate_adx(self, bars, period=14):
        """
        Calculate ADX (Average Directional Index)

        ADX measures trend strength (not direction):
        - ADX >25 = Strong trend (good for swing trading)
        - ADX 20-25 = Moderate trend
        - ADX <20 = Weak/choppy (avoid swing trades)

        Returns: Float (0-100, typically 10-60 range)
        """
        if len(bars) < period + 1:
            return None

        try:
            # Calculate True Range and Directional Movement
            tr_list = []
            plus_dm_list = []
            minus_dm_list = []

            for i in range(1, len(bars)):
                high = bars[i]['high']
                low = bars[i]['low']
                prev_close = bars[i-1]['close']

                # True Range = max of:
                # - High - Low
                # - |High - Previous Close|
                # - |Low - Previous Close|
                tr = max(
                    high - low,
                    abs(high - prev_close),
                    abs(low - prev_close)
                )
                tr_list.append(tr)

                # Directional Movement
                plus_dm = max(high - bars[i-1]['high'], 0) if (high - bars[i-1]['high']) > (bars[i-1]['low'] - low) else 0
                minus_dm = max(bars[i-1]['low'] - low, 0) if (bars[i-1]['low'] - low) > (high - bars[i-1]['high']) else 0

                plus_dm_list.append(plus_dm)
                minus_dm_list.append(minus_dm)

            if len(tr_list) < period:
                return None

            # Smooth TR and DM using Wilder's smoothing
            atr = sum(tr_list[:period]) / period
            plus_di_smooth = sum(plus_dm_list[:period]) / period
            minus_di_smooth = sum(minus_dm_list[:period]) / period

            for i in range(period, len(tr_list)):
                atr = (atr * (period - 1) + tr_list[i]) / period
                plus_di_smooth = (plus_di_smooth * (period - 1) + plus_dm_list[i]) / period
                minus_di_smooth = (minus_di_smooth * (period - 1) + minus_dm_list[i]) / period

            # Calculate DI+ and DI-
            plus_di = 100 * (plus_di_smooth / atr) if atr > 0 else 0
            minus_di = 100 * (minus_di_smooth / atr) if atr > 0 else 0

            # Calculate DX and ADX
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0

            # ADX is smoothed DX
            adx = dx  # Simplified - in production would smooth this further

            return round(adx, 2)

        except Exception as e:
            print(f"   ⚠️ Error calculating ADX: {e}")
            return None

    def calculate_technical_score(self, ticker):
        """
        Calculate technical setup score using 4 essential swing trading filters

        This implements the minimal essential technical requirements from swing trading best practices:
        1. 50-day SMA (trend direction filter)
        2. 5 EMA / 20 EMA crossover (momentum timing)
        3. ADX >20 (trend strength, avoiding chop)
        4. Volume >1.5x average (institutional confirmation)

        Returns:
            {
                'passed': bool,
                'score': int (0-25 points),
                'reason': str (if failed),
                'details': {
                    'price': float,
                    'sma50': float,
                    'ema5': float,
                    'ema20': float,
                    'adx': float,
                    'volume_ratio': float,
                    'above_50ma': bool,
                    'ema_bullish': bool,
                    'trend_strong': bool,
                    'volume_confirmed': bool
                }
            }
        """

        # Fetch 90 days of history (need 50-day MA + buffer)
        bars = self.fetch_daily_bars(ticker, days=90)

        if len(bars) < 50:
            return {
                'passed': False,
                'score': 0,
                'reason': f'Insufficient data ({len(bars)} bars, need 50+)',
                'details': {}
            }

        try:
            current_price = bars[-1]['close']

            # 1. TREND FILTER: 50-day SMA
            sma50 = self.calculate_sma(bars, 50)
            above_50ma = current_price > sma50 if sma50 else False

            # 2. MOMENTUM FILTER: 5 EMA / 20 EMA
            ema5 = self.calculate_ema(bars, 5)
            ema20 = self.calculate_ema(bars, 20)
            ema_bullish = (ema5 > ema20) if (ema5 and ema20) else False

            # 3. TREND STRENGTH: ADX
            adx = self.calculate_adx(bars, period=14)
            trend_strong = adx > 20 if adx else False

            # 4. VOLUME CONFIRMATION (Enhancement 2.2)
            if len(bars) >= 20:
                avg_volume = sum([bar['volume'] for bar in bars[-20:]]) / 20
                current_volume = bars[-1]['volume']
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0

                # Enhancement 2.2: Volume quality rating
                if volume_ratio >= 3.0:
                    volume_quality = 'EXCELLENT'  # Institutional surge
                elif volume_ratio >= 2.0:
                    volume_quality = 'STRONG'     # High conviction
                elif volume_ratio >= 1.5:
                    volume_quality = 'GOOD'       # Acceptable
                else:
                    volume_quality = 'WEAK'       # Below threshold

                # Enhancement 2.2: Volume trend (increasing over 5 days?)
                if len(bars) >= 5:
                    recent_volumes = [bar['volume'] for bar in bars[-5:]]
                    avg_recent = sum(recent_volumes) / 5
                    avg_prior = sum([bar['volume'] for bar in bars[-25:-5]]) / 20 if len(bars) >= 25 else avg_volume
                    volume_trending_up = avg_recent > avg_prior * 1.2 if avg_prior > 0 else False
                else:
                    volume_trending_up = False

                volume_confirmed = volume_ratio >= 1.5
            else:
                volume_ratio = 0
                volume_quality = 'WEAK'
                volume_trending_up = False
                volume_confirmed = False

            # BUILD SCORE (0-25 points possible)
            score = 0
            failed_filters = []

            # Filter 1: Above 50-day MA (7 points) - REQUIRED
            if above_50ma:
                score += 7
            else:
                failed_filters.append(f'Below 50-day MA (${current_price:.2f} < ${sma50:.2f})')

            # Filter 2: 5 EMA > 20 EMA (7 points) - REQUIRED
            if ema_bullish:
                score += 7
            else:
                failed_filters.append(f'Momentum fading (5 EMA ${ema5:.2f} < 20 EMA ${ema20:.2f})')

            # Filter 3: ADX >20 (6 points) - REQUIRED
            if trend_strong:
                score += 6
            else:
                failed_filters.append(f'Choppy market (ADX {adx:.1f} <20)')

            # Filter 4: Volume >1.5x (5 points) - REQUIRED
            if volume_confirmed:
                score += 5
            else:
                failed_filters.append(f'Weak volume ({volume_ratio:.1f}x average)')

            # DECISION: Must pass ALL 4 filters (score = 25) to proceed
            passed = (score == 25)

            details = {
                'price': round(current_price, 2),
                'sma50': round(sma50, 2) if sma50 else None,
                'ema5': round(ema5, 2) if ema5 else None,
                'ema20': round(ema20, 2) if ema20 else None,
                'adx': round(adx, 2) if adx else None,
                'volume_ratio': round(volume_ratio, 2),
                'volume_quality': volume_quality,           # Enhancement 2.2
                'volume_trending_up': volume_trending_up,   # Enhancement 2.2
                'above_50ma': above_50ma,
                'ema_bullish': ema_bullish,
                'trend_strong': trend_strong,
                'volume_confirmed': volume_confirmed
            }

            if passed:
                # Enhancement 2.2: Show volume quality in reason
                vol_indicator = '↑' if volume_trending_up else ''
                return {
                    'passed': True,
                    'score': 25,
                    'reason': f'All technical filters passed (${current_price:.2f}, ADX {adx:.1f}, {volume_ratio:.1f}x {volume_quality}{vol_indicator})',
                    'details': details
                }
            else:
                return {
                    'passed': False,
                    'score': score,
                    'reason': '; '.join(failed_filters),
                    'details': details
                }

        except Exception as e:
            return {
                'passed': False,
                'score': 0,
                'reason': f'Error calculating technical score: {e}',
                'details': {}
            }

    def calculate_conviction_level(self, catalyst_tier, news_score, vix, relative_strength, multi_catalyst=False,
                                   rs_percentile=None, sector_leading=False, sector_vs_spy=0,
                                   options_flow=None, dark_pool=None, revenue_beat=False):
        """
        Determine conviction level based on multiple factors

        Conviction levels determine position sizing:
        - HIGH: 13% (12-15% range)
        - MEDIUM-HIGH: 11%
        - MEDIUM: 10% (standard)
        - SKIP: 0% (do not enter)

        Args:
            catalyst_tier: 'Tier1', 'Tier2', or 'Tier3'
            news_score: News validation score (0-20)
            vix: VIX level
            relative_strength: Stock's 3M performance vs sector (%)
            multi_catalyst: Boolean, are there multiple catalysts?
            rs_percentile: IBD-style RS percentile rank (0-100) [NEW]
            sector_leading: Boolean, is stock's sector leading the market? [NEW]
            sector_vs_spy: Sector performance vs SPY (%) [NEW]
            options_flow: Dict with options flow data [NEW]
            dark_pool: Dict with dark pool activity data [NEW]
            revenue_beat: Boolean, did stock beat on revenue too? [NEW]

        Returns:
            {
                'conviction': str ('HIGH' | 'MEDIUM-HIGH' | 'MEDIUM' | 'SKIP'),
                'position_size_pct': float (0-13%),
                'reasoning': str,
                'supporting_factors': int (count of positive factors)
            }
        """

        supporting_factors = 0
        reasoning_parts = []

        # PHASE 4.1: CLUSTER-BASED SCORING
        # Prevents double-counting correlated signals by grouping into clusters with caps
        #
        # OLD PROBLEM:
        # - RS percentile + RS vs sector + sector leading + ADX all measure momentum
        # - Could get +2 (RS 90th) + +1 (RS >7%) + +1 (leading sector) = +4 for same thing
        #
        # NEW SOLUTION:
        # - Cluster 1 (Momentum): Cap at +3 total
        # - Cluster 2 (Institutional): Cap at +2 total
        # - Cluster 3 (Catalyst): No cap (these are independent)
        # - Cluster 4 (Market Conditions): Cap at +2 total

        # === CLUSTER 1: MOMENTUM (cap +3) ===
        momentum_factors = 0
        momentum_parts = []

        # RS Percentile (strongest signal, gets priority)
        if rs_percentile is not None:
            if rs_percentile >= 90:  # Top 10%
                momentum_factors += 2  # DOUBLE WEIGHT
                momentum_parts.append(f'RS {rs_percentile}th percentile')
            elif rs_percentile >= 80:  # Top 20%
                momentum_factors += 1
                momentum_parts.append(f'RS {rs_percentile}th percentile')

        # RS vs Sector (only count if RS percentile didn't max out contribution)
        if momentum_factors < 3 and relative_strength >= 7.0:
            momentum_factors += 1
            momentum_parts.append(f'Strong sector RS (+{relative_strength:.1f}%)')
        elif momentum_factors < 3 and relative_strength >= 3.0:
            # Lower threshold gets partial credit only if room
            if momentum_factors < 2:  # Don't add if already have 2+ points
                momentum_parts.append(f'RS +{relative_strength:.1f}%')

        # Leading Sector (only if room in momentum cluster)
        if momentum_factors < 3 and sector_leading and sector_vs_spy > 2.0:
            momentum_factors += 1
            momentum_parts.append(f'Leading sector ({sector_vs_spy:+.1f}% vs SPY)')

        # Cap at +3
        momentum_factors = min(momentum_factors, 3)
        supporting_factors += momentum_factors

        if momentum_parts:
            reasoning_parts.append(f"Momentum: {', '.join(momentum_parts)}")

        # === CLUSTER 2: INSTITUTIONAL SIGNALS (cap +2) ===
        institutional_factors = 0
        institutional_parts = []

        if options_flow and options_flow.get('has_unusual_activity'):
            institutional_factors += 1
            signal = options_flow.get('signal_type', 'unusual_activity')
            institutional_parts.append(f'Options: {signal}')

        if dark_pool and dark_pool.get('has_unusual_activity'):
            institutional_factors += 1
            signal = dark_pool.get('signal_type', 'accumulation')
            institutional_parts.append(f'Dark pool: {signal}')

        # Cap at +2
        institutional_factors = min(institutional_factors, 2)
        supporting_factors += institutional_factors

        if institutional_parts:
            reasoning_parts.append(f"Institutional: {', '.join(institutional_parts)}")

        # === CLUSTER 3: CATALYST QUALITY (no cap - independent signals) ===
        catalyst_factors = 0
        catalyst_parts = []

        if catalyst_tier == 'Tier1':
            catalyst_factors += 1
            catalyst_parts.append('Tier 1')

        if multi_catalyst:
            catalyst_factors += 1
            catalyst_parts.append('Multi-catalyst')

        if revenue_beat:
            catalyst_factors += 1
            catalyst_parts.append('Revenue beat')

        if news_score >= 15:
            catalyst_factors += 1
            catalyst_parts.append(f'Strong news ({news_score}/20)')
        elif news_score >= 10:
            catalyst_factors += 1
            catalyst_parts.append(f'Good news ({news_score}/20)')

        supporting_factors += catalyst_factors

        if catalyst_parts:
            reasoning_parts.append(f"Catalyst: {', '.join(catalyst_parts)}")

        # === CLUSTER 4: MARKET CONDITIONS (cap +2) ===
        market_factors = 0
        market_parts = []

        if vix < 20:
            market_factors += 1
            market_parts.append(f'Low VIX ({vix})')
        elif vix < 25:
            market_factors += 1
            market_parts.append(f'Normal VIX ({vix})')

        # Cap at +2 (room for future market condition factors)
        market_factors = min(market_factors, 2)
        supporting_factors += market_factors

        if market_parts:
            reasoning_parts.append(f"Market: {', '.join(market_parts)}")

        # CONVICTION DETERMINATION (based on cluster-adjusted supporting factors)
        # v5.7: Tier requirement removed - Claude decides with full context
        # Tier now affects position sizing, not admission
        # PHASE 4.1: New thresholds based on cluster caps
        # Max possible: Momentum +3, Institutional +2, Catalyst +4, Market +2 = 11 total
        #
        # HIGH (7+ factors): Need strong signals across multiple clusters
        # MEDIUM-HIGH (5-6 factors): Good signals in 2-3 clusters
        # MEDIUM (3-4 factors): Minimal acceptable (catalyst + one other cluster)
        # SKIP (<3 factors): Insufficient conviction

        if supporting_factors >= 7 and news_score >= 15 and vix < 25:
            conviction = 'HIGH'
            position_size = 13.0
        elif supporting_factors >= 5 and news_score >= 10 and vix < 30:
            conviction = 'MEDIUM-HIGH'
            position_size = 11.0
        elif supporting_factors >= 3 and news_score >= 5 and vix < 30:
            conviction = 'MEDIUM'
            position_size = 10.0
        else:
            conviction = 'SKIP'
            position_size = 0.0

        # Build final reasoning with cluster breakdown
        cluster_summary = f"{supporting_factors} factors: " + ' | '.join(reasoning_parts) if reasoning_parts else 'Insufficient factors'

        return {
            'conviction': conviction,
            'position_size_pct': position_size,
            'reasoning': cluster_summary,
            'supporting_factors': supporting_factors
        }

    # =====================================================================
    # LEARNING ENHANCEMENTS (Phase 5)
    # =====================================================================

    def analyze_performance_metrics(self, days=30):
        """
        Analyze performance across Phases 0-4 dimensions
        Enhancement 2.4: Added Phase 0-2 enhancement tracking

        Returns comprehensive analysis of:
        - Conviction accuracy (HIGH vs MEDIUM win rates)
        - Catalyst tier performance (Tier1 vs Tier2)
        - VIX regime performance (<25, 25-30, 30-35)
        - News score correlation with returns
        - Relative strength effectiveness
        - Macro event impact
        - Phase 0-2 enhancement effectiveness (NEW)

        Args:
            days: Number of days to analyze (default 30)

        Returns:
            Dictionary with analysis results and recommendations
        """

        if not self.trades_csv.exists():
            return {'error': 'No trade history available'}

        import pandas as pd

        # Load trade history
        df = pd.read_csv(self.trades_csv)

        if len(df) == 0:
            return {'error': 'No completed trades'}

        # Filter to recent trades
        df['Exit_Date'] = pd.to_datetime(df['Exit_Date'])
        cutoff_date = datetime.now() - timedelta(days=days)
        df_recent = df[df['Exit_Date'] >= cutoff_date]

        if len(df_recent) == 0:
            return {'error': f'No trades in last {days} days'}

        analysis = {
            'period_days': days,
            'total_trades': len(df_recent),
            'total_return_pct': df_recent['Return_Percent'].sum(),
            'avg_return_pct': df_recent['Return_Percent'].mean(),
            'win_rate': (df_recent['Return_Percent'] > 0).sum() / len(df_recent) * 100,
            'avg_hold_days': df_recent['Hold_Days'].mean(),
        }

        # CONVICTION ACCURACY ANALYSIS
        conviction_stats = {}
        for conviction in ['HIGH', 'MEDIUM-HIGH', 'MEDIUM']:
            subset = df_recent[df_recent['Conviction_Level'] == conviction]
            if len(subset) > 0:
                conviction_stats[conviction] = {
                    'count': len(subset),
                    'win_rate': (subset['Return_Percent'] > 0).sum() / len(subset) * 100,
                    'avg_return': subset['Return_Percent'].mean(),
                    'total_return': subset['Return_Percent'].sum()
                }

        analysis['conviction_accuracy'] = conviction_stats

        # CATALYST TIER PERFORMANCE
        tier_stats = {}
        for tier in ['Tier1', 'Tier2', 'Tier3']:
            subset = df_recent[df_recent['Catalyst_Tier'] == tier]
            if len(subset) > 0:
                tier_stats[tier] = {
                    'count': len(subset),
                    'win_rate': (subset['Return_Percent'] > 0).sum() / len(subset) * 100,
                    'avg_return': subset['Return_Percent'].mean()
                }

        analysis['tier_performance'] = tier_stats

        # VIX REGIME PERFORMANCE
        vix_stats = {}
        df_recent['VIX_Bucket'] = pd.cut(
            df_recent['VIX_At_Entry'],
            bins=[0, 15, 20, 25, 30, 100],
            labels=['<15 (calm)', '15-20 (normal)', '20-25 (elevated)', '25-30 (high)', '>30 (extreme)']
        )
        for bucket in df_recent['VIX_Bucket'].unique():
            if pd.notna(bucket):
                subset = df_recent[df_recent['VIX_Bucket'] == bucket]
                vix_stats[str(bucket)] = {
                    'count': len(subset),
                    'win_rate': (subset['Return_Percent'] > 0).sum() / len(subset) * 100,
                    'avg_return': subset['Return_Percent'].mean()
                }

        analysis['vix_regime_performance'] = vix_stats

        # NEWS SCORE EFFECTIVENESS
        news_buckets = {}
        df_recent['News_Bucket'] = pd.cut(
            df_recent['News_Validation_Score'],
            bins=[0, 5, 10, 15, 20],
            labels=['0-5 (weak)', '5-10 (moderate)', '10-15 (strong)', '15-20 (excellent)']
        )
        for bucket in df_recent['News_Bucket'].unique():
            if pd.notna(bucket):
                subset = df_recent[df_recent['News_Bucket'] == bucket]
                news_buckets[str(bucket)] = {
                    'count': len(subset),
                    'win_rate': (subset['Return_Percent'] > 0).sum() / len(subset) * 100,
                    'avg_return': subset['Return_Percent'].mean()
                }

        analysis['news_score_effectiveness'] = news_buckets

        # RELATIVE STRENGTH EFFECTIVENESS
        rs_positive = df_recent[df_recent['Relative_Strength'] >= 3]
        rs_negative = df_recent[df_recent['Relative_Strength'] < 3]

        analysis['relative_strength_impact'] = {
            'rs_positive': {
                'count': len(rs_positive),
                'win_rate': (rs_positive['Return_Percent'] > 0).sum() / len(rs_positive) * 100 if len(rs_positive) > 0 else 0,
                'avg_return': rs_positive['Return_Percent'].mean() if len(rs_positive) > 0 else 0
            },
            'rs_negative': {
                'count': len(rs_negative),
                'win_rate': (rs_negative['Return_Percent'] > 0).sum() / len(rs_negative) * 100 if len(rs_negative) > 0 else 0,
                'avg_return': rs_negative['Return_Percent'].mean() if len(rs_negative) > 0 else 0
            }
        }

        # MACRO EVENT IMPACT
        with_macro = df_recent[df_recent['Macro_Event_Near'] != 'None']
        without_macro = df_recent[df_recent['Macro_Event_Near'] == 'None']

        analysis['macro_event_impact'] = {
            'with_macro': {
                'count': len(with_macro),
                'win_rate': (with_macro['Return_Percent'] > 0).sum() / len(with_macro) * 100 if len(with_macro) > 0 else 0,
                'avg_return': with_macro['Return_Percent'].mean() if len(with_macro) > 0 else 0
            },
            'without_macro': {
                'count': len(without_macro),
                'win_rate': (without_macro['Return_Percent'] > 0).sum() / len(without_macro) * 100 if len(without_macro) > 0 else 0,
                'avg_return': without_macro['Return_Percent'].mean() if len(without_macro) > 0 else 0
            }
        }

        # Enhancement 2.4: PHASE 0-2 ENHANCEMENT TRACKING
        enhancement_tracking = {}

        # Enhancement 2.1: RS Rating effectiveness
        if 'RS_Rating' in df_recent.columns:
            rs_elite = df_recent[df_recent['RS_Rating'] >= 85]  # Elite
            rs_good = df_recent[(df_recent['RS_Rating'] >= 65) & (df_recent['RS_Rating'] < 85)]  # Good
            rs_weak = df_recent[df_recent['RS_Rating'] < 65]  # Weak

            enhancement_tracking['rs_rating'] = {
                'elite_85plus': {
                    'count': len(rs_elite),
                    'win_rate': (rs_elite['Return_Percent'] > 0).sum() / len(rs_elite) * 100 if len(rs_elite) > 0 else 0,
                    'avg_return': rs_elite['Return_Percent'].mean() if len(rs_elite) > 0 else 0
                },
                'good_65to85': {
                    'count': len(rs_good),
                    'win_rate': (rs_good['Return_Percent'] > 0).sum() / len(rs_good) * 100 if len(rs_good) > 0 else 0,
                    'avg_return': rs_good['Return_Percent'].mean() if len(rs_good) > 0 else 0
                },
                'weak_below65': {
                    'count': len(rs_weak),
                    'win_rate': (rs_weak['Return_Percent'] > 0).sum() / len(rs_weak) * 100 if len(rs_weak) > 0 else 0,
                    'avg_return': rs_weak['Return_Percent'].mean() if len(rs_weak) > 0 else 0
                }
            }

        # Enhancement 2.2: Volume Quality effectiveness
        if 'Volume_Quality' in df_recent.columns:
            vol_excellent = df_recent[df_recent['Volume_Quality'] == 'EXCELLENT']
            vol_strong = df_recent[df_recent['Volume_Quality'] == 'STRONG']
            vol_good = df_recent[df_recent['Volume_Quality'] == 'GOOD']

            enhancement_tracking['volume_quality'] = {
                'excellent_3x': {
                    'count': len(vol_excellent),
                    'win_rate': (vol_excellent['Return_Percent'] > 0).sum() / len(vol_excellent) * 100 if len(vol_excellent) > 0 else 0,
                    'avg_return': vol_excellent['Return_Percent'].mean() if len(vol_excellent) > 0 else 0
                },
                'strong_2x': {
                    'count': len(vol_strong),
                    'win_rate': (vol_strong['Return_Percent'] > 0).sum() / len(vol_strong) * 100 if len(vol_strong) > 0 else 0,
                    'avg_return': vol_strong['Return_Percent'].mean() if len(vol_strong) > 0 else 0
                },
                'good_1.5x': {
                    'count': len(vol_good),
                    'win_rate': (vol_good['Return_Percent'] > 0).sum() / len(vol_good) * 100 if len(vol_good) > 0 else 0,
                    'avg_return': vol_good['Return_Percent'].mean() if len(vol_good) > 0 else 0
                }
            }

        # Volume trending up effectiveness
        if 'Volume_Trending_Up' in df_recent.columns:
            vol_trending = df_recent[df_recent['Volume_Trending_Up'] == True]
            vol_flat = df_recent[df_recent['Volume_Trending_Up'] == False]

            enhancement_tracking['volume_trending'] = {
                'trending_up': {
                    'count': len(vol_trending),
                    'win_rate': (vol_trending['Return_Percent'] > 0).sum() / len(vol_trending) * 100 if len(vol_trending) > 0 else 0,
                    'avg_return': vol_trending['Return_Percent'].mean() if len(vol_trending) > 0 else 0
                },
                'flat_declining': {
                    'count': len(vol_flat),
                    'win_rate': (vol_flat['Return_Percent'] > 0).sum() / len(vol_flat) * 100 if len(vol_flat) > 0 else 0,
                    'avg_return': vol_flat['Return_Percent'].mean() if len(vol_flat) > 0 else 0
                }
            }

        analysis['enhancement_tracking'] = enhancement_tracking

        # Enhancement 2.5: CATALYST & KEYWORD LEARNING
        catalyst_learning = {}

        # Catalyst Type Performance
        if 'Catalyst_Type' in df_recent.columns:
            catalyst_performance = {}
            for catalyst_type in df_recent['Catalyst_Type'].unique():
                if pd.isna(catalyst_type) or catalyst_type == '':
                    continue
                catalyst_trades = df_recent[df_recent['Catalyst_Type'] == catalyst_type]
                catalyst_performance[catalyst_type] = {
                    'count': len(catalyst_trades),
                    'win_rate': (catalyst_trades['Return_Percent'] > 0).sum() / len(catalyst_trades) * 100 if len(catalyst_trades) > 0 else 0,
                    'avg_return': catalyst_trades['Return_Percent'].mean() if len(catalyst_trades) > 0 else 0,
                    'best_trade': catalyst_trades['Return_Percent'].max() if len(catalyst_trades) > 0 else 0,
                    'worst_trade': catalyst_trades['Return_Percent'].min() if len(catalyst_trades) > 0 else 0
                }
            # Sort by win rate (descending)
            catalyst_performance = dict(sorted(catalyst_performance.items(), key=lambda x: x[1]['win_rate'], reverse=True))
            catalyst_learning['catalyst_type_performance'] = catalyst_performance

        # Keyword Effectiveness
        if 'Keywords_Matched' in df_recent.columns:
            keyword_stats = {}
            for _, row in df_recent.iterrows():
                keywords_str = row.get('Keywords_Matched', '')
                if pd.isna(keywords_str) or keywords_str == '':
                    continue
                keywords = keywords_str.split(',')
                for keyword in keywords:
                    keyword = keyword.strip()
                    if keyword == '':
                        continue
                    if keyword not in keyword_stats:
                        keyword_stats[keyword] = {'count': 0, 'wins': 0, 'total_return': 0}
                    keyword_stats[keyword]['count'] += 1
                    if row['Return_Percent'] > 0:
                        keyword_stats[keyword]['wins'] += 1
                    keyword_stats[keyword]['total_return'] += row['Return_Percent']

            # Calculate win rates and avg returns
            keyword_performance = {}
            for keyword, stats in keyword_stats.items():
                if stats['count'] >= 3:  # Only include keywords with 3+ trades
                    keyword_performance[keyword] = {
                        'count': stats['count'],
                        'win_rate': (stats['wins'] / stats['count']) * 100,
                        'avg_return': stats['total_return'] / stats['count']
                    }
            # Sort by win rate (descending)
            keyword_performance = dict(sorted(keyword_performance.items(), key=lambda x: x[1]['win_rate'], reverse=True))
            catalyst_learning['keyword_performance'] = keyword_performance

        # News Source Effectiveness
        if 'News_Sources' in df_recent.columns:
            source_stats = {}
            for _, row in df_recent.iterrows():
                sources_str = row.get('News_Sources', '')
                if pd.isna(sources_str) or sources_str == '':
                    continue
                sources = sources_str.split(',')
                for source in sources:
                    source = source.strip()
                    if source == '' or source == 'Unknown':
                        continue
                    if source not in source_stats:
                        source_stats[source] = {'count': 0, 'wins': 0, 'total_return': 0}
                    source_stats[source]['count'] += 1
                    if row['Return_Percent'] > 0:
                        source_stats[source]['wins'] += 1
                    source_stats[source]['total_return'] += row['Return_Percent']

            # Calculate win rates and avg returns
            source_performance = {}
            for source, stats in source_stats.items():
                if stats['count'] >= 3:  # Only include sources with 3+ trades
                    source_performance[source] = {
                        'count': stats['count'],
                        'win_rate': (stats['wins'] / stats['count']) * 100,
                        'avg_return': stats['total_return'] / stats['count']
                    }
            # Sort by win rate (descending)
            source_performance = dict(sorted(source_performance.items(), key=lambda x: x[1]['win_rate'], reverse=True))
            catalyst_learning['news_source_performance'] = source_performance

        # Catalyst Tier Performance
        if 'Catalyst_Tier' in df_recent.columns:
            tier_performance = {}
            for tier in ['Tier1', 'Tier 1', 'Tier2', 'Tier 2', 'Tier3', 'Tier 3']:
                tier_trades = df_recent[df_recent['Catalyst_Tier'] == tier]
                if len(tier_trades) > 0:
                    tier_performance[tier] = {
                        'count': len(tier_trades),
                        'win_rate': (tier_trades['Return_Percent'] > 0).sum() / len(tier_trades) * 100,
                        'avg_return': tier_trades['Return_Percent'].mean()
                    }
            catalyst_learning['tier_performance'] = tier_performance

        analysis['catalyst_learning'] = catalyst_learning

        # RECOMMENDATIONS
        recommendations = []

        # Conviction accuracy check
        if 'HIGH' in conviction_stats and 'MEDIUM' in conviction_stats:
            if conviction_stats['HIGH']['win_rate'] < conviction_stats['MEDIUM']['win_rate']:
                recommendations.append('⚠️ HIGH conviction underperforming MEDIUM - review conviction criteria')

        # VIX threshold check
        if '>30 (extreme)' in vix_stats:
            if vix_stats['>30 (extreme)']['count'] > 0:
                recommendations.append('⚠️ Trades entered at VIX >30 detected - verify SHUTDOWN logic')

        # Relative strength validation
        if rs_positive and rs_negative:
            if rs_negative['win_rate'] > rs_positive['win_rate']:
                recommendations.append('⚠️ Sector laggards outperforming leaders - review RS threshold')

        # News score validation
        if '0-5 (weak)' in news_buckets and news_buckets['0-5 (weak)']['count'] > 0:
            recommendations.append('⚠️ Trades with weak news scores detected - verify news filter')

        # Enhancement 2.5: Catalyst learning recommendations
        if 'catalyst_learning' in analysis and 'catalyst_type_performance' in analysis['catalyst_learning']:
            catalyst_perf = analysis['catalyst_learning']['catalyst_type_performance']
            # Flag underperforming catalyst types
            for catalyst, stats in catalyst_perf.items():
                if stats['count'] >= 5 and stats['win_rate'] < 40:
                    recommendations.append(f"⚠️ Catalyst '{catalyst}' underperforming: {stats['win_rate']:.0f}% win rate over {stats['count']} trades - consider avoiding")
                elif stats['count'] >= 5 and stats['win_rate'] >= 70:
                    recommendations.append(f"✅ Catalyst '{catalyst}' high performance: {stats['win_rate']:.0f}% win rate - prioritize these")

        if 'catalyst_learning' in analysis and 'keyword_performance' in analysis['catalyst_learning']:
            keyword_perf = analysis['catalyst_learning']['keyword_performance']
            # Flag best and worst performing keywords
            if keyword_perf:
                best_keywords = list(keyword_perf.items())[:3]  # Top 3
                for keyword, stats in best_keywords:
                    if stats['win_rate'] >= 70:
                        recommendations.append(f"🎯 High-value keyword '{keyword}': {stats['win_rate']:.0f}% win rate ({stats['count']} trades)")
                worst_keywords = list(keyword_perf.items())[-3:]  # Bottom 3
                for keyword, stats in worst_keywords:
                    if stats['win_rate'] < 40:
                        recommendations.append(f"❌ Weak keyword '{keyword}': {stats['win_rate']:.0f}% win rate - investigate why")

        if 'catalyst_learning' in analysis and 'news_source_performance' in analysis['catalyst_learning']:
            source_perf = analysis['catalyst_learning']['news_source_performance']
            # Flag best news sources
            if source_perf:
                best_sources = list(source_perf.items())[:3]
                for source, stats in best_sources:
                    if stats['win_rate'] >= 70:
                        recommendations.append(f"📰 Reliable source '{source}': {stats['win_rate']:.0f}% win rate ({stats['count']} trades)")

        analysis['recommendations'] = recommendations

        return analysis

    def save_learning_analysis(self, analysis, report_type='monthly'):
        """
        Save learning analysis to JSON file for tracking over time

        Args:
            analysis: Dictionary from analyze_performance_metrics()
            report_type: 'daily', 'weekly', or 'monthly'
        """

        learning_dir = self.project_dir / 'learning_data'
        learning_dir.mkdir(exist_ok=True)

        # Create timestamped filename
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f'{report_type}_analysis_{timestamp}.json'
        filepath = learning_dir / filename

        with open(filepath, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

        print(f"   ✓ Saved {report_type} analysis to {filename}")

        # Also update the latest analysis file
        latest_file = learning_dir / f'latest_{report_type}_analysis.json'
        with open(latest_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

    # =====================================================================
    # MARKET SCREENER INTEGRATION
    # =====================================================================

    def load_screener_candidates(self):
        """
        Load pre-screened candidates from market screener

        Returns: Dict with screener results, or None if not available
        """
        screener_file = self.project_dir / 'screener_candidates.json'

        print(f"\n🔍 DEBUG: Checking for screener file: {screener_file}")

        if not screener_file.exists():
            print(f"   ❌ DEBUG: File does not exist")
            return None

        print(f"   ✅ DEBUG: File exists")

        try:
            with open(screener_file, 'r') as f:
                data = json.load(f)

            print(f"   ✅ DEBUG: JSON loaded successfully")

            # Check if screener ran today
            scan_date = data.get('scan_date', '')
            today = datetime.now().strftime('%Y-%m-%d')

            print(f"   📅 DEBUG: scan_date={scan_date}, today={today}")

            if scan_date != today:
                print(f"   ⚠️ Screener data is stale (from {scan_date})")
                return None

            candidate_count = len(data.get('candidates', []))
            print(f"   ✅ DEBUG: Date matches, returning data with {candidate_count} candidates")

            return data

        except Exception as e:
            print(f"   ⚠️ Error loading screener results: {e}")
            import traceback
            traceback.print_exc()
            return None

    def format_screener_candidates(self, screener_data):
        """
        Format screener candidates for Claude

        Returns: String with formatted candidate list INCLUDING NEWS CONTENT
        """
        if not screener_data or not screener_data.get('candidates'):
            print(f"   ⚠️ DEBUG: format_screener_candidates returning None (no data or no candidates)")
            return None

        candidates = screener_data['candidates']

        output = f"PRE-SCREENED CANDIDATES (Top {len(candidates)} from S&P 1500 scan):\n\n"
        output += f"Scanned: {screener_data['universe_size']} stocks\n"
        output += f"Candidates found: {screener_data['candidates_found']} stocks with catalysts\n"
        output += f"Market breadth: {screener_data.get('breadth_pct', 'N/A')}% (stocks above 50-day MA)\n"
        output += f"Top candidates: {len(candidates)}\n\n"

        output += "TOP CANDIDATES (sorted by composite score):\n"
        output += "=" * 80 + "\n\n"

        for candidate in candidates[:15]:  # Show top 15 with full news (reduced from 25 due to news content)
            rank = candidate['rank']
            ticker = candidate['ticker']
            score = candidate['composite_score']
            sector = candidate['sector']

            rs = candidate['relative_strength']
            news = candidate['catalyst_signals']
            vol = candidate['volume_analysis']
            tech = candidate['technical_setup']

            output += f"{rank}. {ticker} ({sector}) - Score: {score:.1f}/100\n"
            output += f"   RS: +{rs['rs_pct']}% vs {rs['sector_etf']} "
            output += f"(stock: +{rs['stock_return_3m']}%, sector: +{rs['sector_return_3m']}%)\n"
            output += f"   News: {news['score']}/20 ({news['count']} articles"
            if news['keywords']:
                output += f", keywords: {', '.join(news['keywords'][:5])}"
            output += ")\n"

            # NEW: Include actual news headlines for catalyst verification
            if news.get('top_articles'):
                output += f"   📰 Recent News Headlines:\n"
                for i, article in enumerate(news['top_articles'][:3], 1):  # Top 3 articles
                    output += f"      {i}. [{article['published']}] {article['title']}\n"
                    if article['description']:
                        output += f"         {article['description'][:150]}...\n"

            output += f"   Volume: {vol['volume_ratio']:.1f}x average "
            output += f"({vol['yesterday_volume']:,} vs {vol['avg_volume_20d']:,})\n"
            output += f"   Technical: {tech['distance_from_52w_high_pct']:.1f}% from 52w high "
            output += f"(${tech['current_price']:.2f} vs ${tech['high_52w']:.2f})\n"

            # Add full technical indicators for holistic decision making
            output += f"   📊 Technical Indicators:\n"
            output += f"      RSI(14): {tech.get('rsi', 'N/A')}"
            if tech.get('rsi'):
                if tech['rsi'] > 70:
                    output += " (overbought)"
                elif tech['rsi'] < 30:
                    output += " (oversold)"
            output += "\n"

            output += f"      ADX(14): {tech.get('adx', 'N/A')}"
            if tech.get('adx'):
                if tech['adx'] > 25:
                    output += " (strong trend)"
                elif tech['adx'] < 20:
                    output += " (weak trend)"
            output += "\n"

            output += f"      Distance from 20-MA: "
            if tech.get('distance_from_20ma_pct') is not None:
                dist_20ma = tech['distance_from_20ma_pct']
                output += f"{'+' if dist_20ma > 0 else ''}{dist_20ma:.1f}%"
                if dist_20ma > 10:
                    output += " (extended)"
                elif dist_20ma < -5:
                    output += " (below MA)"
            else:
                output += "N/A"
            output += "\n"

            output += f"      3-Day Return: "
            if tech.get('three_day_return_pct') is not None:
                three_day = tech['three_day_return_pct']
                output += f"{'+' if three_day > 0 else ''}{three_day:.1f}%"
                if three_day > 15:
                    output += " (hot momentum)"
                elif three_day < -10:
                    output += " (recent weakness)"
            else:
                output += "N/A"
            output += "\n"

            output += f"      EMA Cross: 5 EMA {'above' if tech.get('ema_5_above_20') else 'below'} 20 EMA"
            if tech.get('ema_5') and tech.get('ema_20'):
                output += f" (${tech['ema_5']:.2f} vs ${tech['ema_20']:.2f})"
            output += "\n"

            output += f"      50-MA Position: {'Above' if tech.get('above_50d_sma') else 'Below'} 50-day MA"
            if tech.get('distance_from_50ma_pct') is not None:
                output += f" ({'+' if tech['distance_from_50ma_pct'] > 0 else ''}{tech['distance_from_50ma_pct']:.1f}%)"
            output += "\n"

            output += f"   Why: {candidate['why_selected']}\n\n"

        if len(candidates) > 15:
            output += f"\n... and {len(candidates) - 15} more candidates available\n"
            output += f"(News details shown for top 15 only to manage context size)\n"

        return output

    # =====================================================================
    # CLAUDE API INTEGRATION
    # =====================================================================

    def call_claude_api(self, command, context, premarket_data=None):
        """Call Claude API with optimized context and retry logic

        Args:
            command: Command to execute ('go', 'execute', 'analyze')
            context: Project context from load_optimized_context()
            premarket_data: Optional dict of premarket data for existing positions
        """

        if not CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY environment variable not set")

        headers = {
            'x-api-key': CLAUDE_API_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }

        if command == 'go':
            today_date = datetime.now().strftime('%A, %B %d, %Y')

            if premarket_data:
                # PORTFOLIO REVIEW MODE - Review existing positions
                portfolio_review = self._format_portfolio_review(premarket_data)

                # Load screener candidates for vacant slots
                screener_data = self.load_screener_candidates()
                screener_section = ""
                vacant_slots = 10 - len(premarket_data)

                print(f"\n🔍 DEBUG: screener_data={'LOADED' if screener_data else 'NONE'}")
                print(f"   Vacant slots: {vacant_slots}")

                if screener_data and vacant_slots > 0:
                    print(f"   ✅ DEBUG: Building screener section...")
                    screener_section = f"\n\n{'='*70}\nAVAILABLE OPPORTUNITIES FOR {vacant_slots} VACANT SLOTS:\n{'='*70}\n\n"
                    formatted_candidates = self.format_screener_candidates(screener_data)
                    print(f"   ✅ DEBUG: Formatted candidates length: {len(formatted_candidates) if formatted_candidates else 0}")
                    screener_section += formatted_candidates
                    screener_section += f"\n\n{'='*70}\n"
                    print(f"   ✅ DEBUG: Final screener section length: {len(screener_section)}")
                else:
                    if not screener_data:
                        print(f"   ❌ DEBUG: No screener_data")
                    if vacant_slots <= 0:
                        print(f"   ❌ DEBUG: No vacant slots (portfolio full)")

                user_message = f"""PORTFOLIO REVIEW - {today_date} @ 8:45 AM (Pre-market)

CURRENT POSITIONS ({len(premarket_data)}):
{portfolio_review}
{screener_section}
TASK: Review each position and decide HOLD / EXIT / REPLACE

SWING TRADING RULES (STRICTLY ENFORCE):
1. Minimum hold: 2 days (unless stop/target hit or catalyst invalidated)
2. Maximum hold: 21 days (time stop)
3. Exit triggers ONLY:
   - Stop loss hit or approaching (-7%)
   - Price target hit (+10-15%)
   - Catalyst invalidated (news, guidance cut, sector reversal)
   - Time stop (21 days with <3% gain)
   - Better opportunity exists AND position is flat/small loss AND age >= 2 days
4. DO NOT exit profitable positions just because it's a new day
5. DO NOT churn daily - let swings work (3-7 days typical)
6. If position is working (profitable, catalyst intact), HOLD it

**NEW POSITIONS: AI-FIRST HOLISTIC DECISION MAKING**

You have full authority to decide which stocks to BUY based on holistic analysis of ALL factors.
The only hard blocks are catastrophic checks (VIX ≥35, macro blackout, halted/delisted stocks).

**TECHNICAL INDICATOR REFERENCE (Guidelines, NOT Hard Rules):**
Each candidate includes full technical indicators. Our model typically looks for these characteristics
when multiple factors co-exist, but you should weigh ALL factors holistically:

- RSI <70: Momentum not overextended (values >70 suggest overbought, but catalyst breakouts often run hot)
- ADX >20: Strong trend vs choppy action (values >25 indicate powerful trend)
- Volume >1.5x: Institutional participation (higher = stronger conviction)
- Above 50-MA: Uptrend confirmation (distance from MA shows extension level)
- 5 EMA > 20 EMA: Short-term momentum accelerating
- Distance from 20-MA <10%: Not overextended (values >15% may indicate parabolic move)
- 3-Day Return <15%: Sustainable momentum (values >20% may indicate exhaustion)

**HOLISTIC DECISION FRAMEWORK:**
- One or two indicators marginally outside guidelines is ACCEPTABLE if catalyst quality is strong
- Example: RSI 75 + strong FDA catalyst = may still be excellent entry (catalyst-driven breakout expected to run hot)
- Example: Extended 12% above 20-MA + $2.6B contract win = momentum justified by fundamentals
- Values DRAMATICALLY off guidelines require pause: RSI >85, extended >25%, or weak volume <1.0x
- Use your judgment to weigh: catalyst tier + news quality + relative strength + technical setup together

**DECISION TYPES (Required - Choose One Per Candidate):**

You must classify each recommendation with an explicit decision:
- ENTER: Standard entry, normal position sizing (6-10%)
- ENTER_SMALL: Reduced entry for speculative/uncertain setups (5-6% max)
- PASS: Do not enter - catalyst interesting but insufficient conviction or excessive risk

PASS is expected on 30-40% of candidates. Do not force trades on marginal setups.
Quality over quantity is critical for system success.

Examples:
- Strong FDA catalyst + RSI 72 + good volume = ENTER at 9%
- Contract win + RSI 85 + extended 18% = ENTER_SMALL at 6%
- Analyst upgrade + weak volume + Tier 3 = PASS (don't recommend)

**POSITION SIZING = RISK DIAL (TESTING PHASE):**

⚠️  TESTING MODE: Using tightened range (6-10%) for initial validation (5-10 days).
Range will widen to 5-13% after 15-20 successful trades.

For ENTER decisions:
- 9-10%: HIGH conviction - Tier 1 catalyst + strong technicals + HIGH confidence
- 7-8%: MEDIUM conviction - Strong catalyst, some technical heat + MEDIUM confidence
- 6-7%: MEDIUM/LOW conviction - Solid catalyst, multiple risk flags

For ENTER_SMALL decisions:
- 5-6%: LOW conviction - Speculative setup, concerning risk indicators

Use the full range - variance in sizing demonstrates risk discrimination.

**PORTFOLIO DIVERSIFICATION (Your Responsibility):**

You have full authority to construct portfolio allocation based on current opportunities.
Diversification is important, but balance it against opportunity quality.

Guidelines:
- Avoid concentration risk: Generally aim for <40% in any single sector
- Temporary over-allocation acceptable: If sector has exceptional catalysts (multiple FDA approvals, policy shift), 40-50% may be justified
- Explain your reasoning: If recommending sector concentration, articulate why opportunities warrant it
- Quality over arbitrary limits: Better to own 4 excellent Healthcare stocks than force 2 mediocre stocks for "balance"
- Market regime matters: In sector rotation periods, concentration in leading sectors is appropriate
- Document allocation rationale: Include sector breakdown and justification in your analysis

Your job: Analyze opportunities holistically, construct best risk-adjusted portfolio, use allocation as a tool not a constraint.

PREMARKET ANALYSIS:
- Use gap_percent to gauge overnight sentiment
- Large gaps (>5%) may signal catalyst change
- Small gaps (<2%) are normal volatility

CRITICAL OUTPUT REQUIREMENT - JSON at end:
```json
{{
  "hold": ["TICKER1", "TICKER2"],
  "exit": [
    {{"ticker": "TICKER3", "reason": "Specific reason following exit rules above"}}
  ],
  "buy": [
    {{
      "ticker": "NVDA",
      "decision": "ENTER",
      "confidence_level": "HIGH",
      "position_size_pct": 9.0,
      "catalyst": "Earnings_Beat",
      "sector": "Technology",
      "thesis": "One sentence thesis"
    }},
    {{
      "ticker": "AXSM",
      "decision": "ENTER_SMALL",
      "confidence_level": "MEDIUM",
      "position_size_pct": 6.0,
      "catalyst": "FDA_Approval",
      "sector": "Healthcare",
      "thesis": "One sentence thesis"
    }}
  ]
}}
```

**NEW REQUIRED FIELDS (v5.7.1):**
- decision: Must be "ENTER" or "ENTER_SMALL" (do NOT include PASS stocks in buy array)
- confidence_level: Must be "HIGH", "MEDIUM", or "LOW"
- position_size_pct: Use decimal (9.0, not 100.00)

**CRITICAL:** A ticker can ONLY appear in ONE array (hold, exit, or buy). Never put the same ticker in multiple arrays.
Do not include tickers you are PASSing on in the buy array - simply omit them.

Provide full analysis of each position BEFORE the JSON. Justify all exits against the rules above."""

            else:
                # INITIAL BUILD MODE - No existing positions
                # Try to load pre-screened candidates
                screener_data = self.load_screener_candidates()
                screener_section = ""

                if screener_data:
                    screener_section = self.format_screener_candidates(screener_data)
                    instruction = "Select the BEST 10 stocks from the pre-screened candidates below."
                else:
                    instruction = "Select 10 stocks with Tier 1 catalysts. Focus on well-known, liquid stocks."

                user_message = f"""BUILD INITIAL PORTFOLIO - {today_date}

No existing positions. {instruction}

**CATALYST-DRIVEN TRADING WITH HOLISTIC ANALYSIS**

You are the primary decision authority. Focus on finding stocks with strong catalysts and use all available
data to make holistic decisions. Only catastrophic checks will hard-block entries (VIX ≥35, macro blackout, halted stocks).

**CATALYST PRIORITY (Quality Over Quantity):**
- Prefer Tier 1 catalysts: Earnings beats + guidance, FDA approvals, major M&A, multi-catalyst events
- Tier 2 acceptable with strong technical setup: Analyst upgrades, sector momentum, product launches
- Better to recommend 5-7 high-quality stocks than force 10 mediocre picks
- Every recommendation needs a clear, specific catalyst you can articulate

**TECHNICAL INDICATOR GUIDELINES (Reference, NOT Hard Rules):**
Each candidate includes comprehensive technical data. Our model typically looks for these characteristics
when factors co-exist, but you should weigh ALL factors together:

- RSI <70: Momentum sustainable (>70 is overbought, but catalyst breakouts can run hot to RSI 75-80)
- ADX >20: Strong trend vs chop (>25 = powerful trend)
- Volume >1.5x: Institutional buying (higher = stronger)
- Above 50-MA: Uptrend intact (distance shows extension level)
- 5 EMA > 20 EMA: Short-term momentum positive
- Distance from 20-MA <10%: Not overextended (>15% may indicate parabolic)
- 3-Day Return <15%: Sustainable pace (>20% may signal exhaustion)

**HOLISTIC DECISION FRAMEWORK:**
- Marginally outside guidelines (RSI 72, extended 11%) is FINE if catalyst is strong
- Catalyst-driven breakouts EXPECT hot technicals - don't penalize FDA/M&A/contract wins for momentum
- Dramatically off requires caution: RSI >85, extended >25%, volume <1.0x, or multiple red flags
- Weigh catalyst quality + news score + RS + volume + technical setup together

**POSITION SIZING = RISK DIAL:**
Express your conviction through position sizing:
- 10-13%: High conviction - strong catalyst + aligned technicals
- 7-10%: Good opportunity - catalyst strong, some technical heat (high RSI, extended)
- 5-7%: Starter position - solid catalyst, multiple risk flags
- 3-5%: Speculative - intriguing setup but imperfect

Use sizing to manage risk on stocks that have good catalysts but concerning technicals.

"""
                if screener_section:
                    user_message += screener_section + "\n"

                user_message += """
**PORTFOLIO DIVERSIFICATION (Your Responsibility):**

You have full authority to construct portfolio allocation based on current opportunities.
Diversification is important, but balance it against opportunity quality.

Guidelines:
- Avoid concentration risk: Generally aim for <40% in any single sector
- Temporary over-allocation acceptable: If sector has exceptional catalysts (multiple FDA approvals, policy shift), 40-50% may be justified
- Explain your reasoning: If recommending sector concentration, articulate why opportunities warrant it
- Quality over arbitrary limits: Better to own 4 excellent Healthcare stocks than force 2 mediocre stocks for "balance"
- Market regime matters: In sector rotation periods, concentration in leading sectors is appropriate
- Document allocation rationale: Include sector breakdown and justification in your analysis

Your job: Analyze opportunities holistically, construct best risk-adjusted portfolio, use allocation as a tool not a constraint.

SELECTION CRITERIA:
- MUST have Tier 1 catalyst (verified from recent news/earnings)
- Prioritize highest composite scores (if screener data available)
- Look for multiple confirming signals (RS + news + volume)
- Favor recent catalysts (last 3-7 days)
- Diversify across sectors when multiple Tier 1 opportunities exist (but prioritize quality over arbitrary balance)
- All stocks will be validated through catastrophic checks only

CRITICAL OUTPUT REQUIREMENT - JSON at end:
```json
{{
  "hold": [],
  "exit": [],
  "buy": [
    {{
      "ticker": "AAPL",
      "position_size": 100.00,
      "catalyst": "Earnings_Beat",
      "sector": "Technology",
      "confidence": "High",
      "thesis": "One sentence thesis"
    }}
  ]
}}
```

DO NOT include entry_price, stop_loss, or price_target - system will calculate from real market prices.
Every position must have position_size: 100.00 exactly."""
        elif command == 'analyze':
            # ANALYZE command - best-in-class prompt with structured output
            today_date = datetime.now().strftime('%A, %B %d, %Y')
            current_time = datetime.now().strftime('%I:%M %p')

            # Calculate next trading day
            from datetime import timedelta
            next_day = datetime.now() + timedelta(days=1)
            # Skip weekends
            while next_day.weekday() >= 5:  # Saturday = 5, Sunday = 6
                next_day += timedelta(days=1)
            next_trading_day = next_day.strftime('%A, %B %d')

            user_message = f"""# DAILY PORTFOLIO ANALYSIS - {today_date} ({current_time} ET)

## YOUR TASK
Analyze today's portfolio performance and provide **actionable intelligence** for tomorrow's trading session.

## ANALYSIS FRAMEWORK

### 1. PORTFOLIO HEALTH CHECK
Review the portfolio JSON and account status provided in context. Calculate and report:
- **Total P&L Today**: Sum of unrealized_gain_dollars across all positions
- **Winners vs Losers**: Count positions with positive vs negative unrealized_gain_pct
- **Best Performer**: Ticker with highest unrealized_gain_pct
- **Worst Performer**: Ticker with lowest unrealized_gain_pct
- **Account Utilization**: positions_value / account_value (target: 50-60% invested)

### 2. POSITION-BY-POSITION REVIEW
For EACH position in the portfolio, evaluate:

**Exit Triggers (check all):**
- ❌ **Stop Loss**: Is current_price ≤ stop_loss? → EXIT TOMORROW
- ✅ **Profit Target**: Is unrealized_gain_pct ≥ +10%? → Consider taking profits
- ⏰ **Time Stop**: Is days_held ≥ 21? → EXIT (capital tied up too long)
- 📉 **Stagnant**: Is days_held ≥ 10 AND |unrealized_gain_pct| < 3%? → Consider exit for better opportunity
- 🔴 **Deep Red**: Is unrealized_gain_pct < -5%? → Monitor closely, may hit stop soon

**Trailing Stop Status** (if position has trailing_stop_active = true):
- Report peak_return_pct vs current unrealized_gain_pct
- If current < peak by >2%, trailing stop may trigger

**Thesis Check:**
- Is the original catalyst still valid?
- Any negative news since entry that invalidates thesis?

### 3. SECTOR EXPOSURE
Group positions by sector (from catalyst field or ticker industry):
- Flag if >30% concentrated in any single sector
- Note any correlated risk (e.g., multiple semiconductor stocks)

### 4. TOMORROW'S ACTION ITEMS
Provide specific, actionable recommendations:

**MANDATORY EXITS** (non-negotiable):
- List any positions that hit stop_loss, time_stop, or catalyst invalidation

**SUGGESTED EXITS** (your recommendation with reasoning):
- Positions you recommend exiting with brief rationale

**POSITIONS TO MONITOR** (watch closely):
- Approaching stop loss (within 2%)
- Approaching profit target (within 2%)
- Significant overnight news expected

**HOLD WITH CONFIDENCE**:
- Strong positions with intact thesis

### 5. MARKET CONTEXT (Brief)
- Overall market sentiment today (1-2 sentences max)
- Any macro events tomorrow that could impact portfolio

## OUTPUT FORMAT
Use this exact structure with markdown headers. Be concise and data-driven.
Do NOT include generic commentary or filler text.
Every statement should be backed by specific numbers from the portfolio data.

**Next Trading Day: {next_trading_day}**
Any exit recommendations should specify "Exit at market open on {next_trading_day}"
"""
        else:
            user_message = command

        system_prompt = f"""You are the Paper Trading Lab assistant.

Project Context:
{context}

Execute the user's command following the PROJECT_INSTRUCTIONS.md guidelines.

CRITICAL: When executing 'go' command, you MUST include a properly formatted JSON block at the end of your response."""

        payload = {
            'model': CLAUDE_MODEL,
            'max_tokens': 8192,  # Increased from 4096 to handle full response with JSON
            'system': system_prompt,
            'messages': [{'role': 'user', 'content': user_message}]
        }

        # Retry logic with exponential backoff
        max_retries = 3
        base_timeout = 120  # Increased from 60 to 120 seconds

        for attempt in range(max_retries):
            try:
                timeout = base_timeout * (attempt + 1)  # 120s, 240s, 360s
                print(f"   API call attempt {attempt + 1}/{max_retries} (timeout: {timeout}s)...")

                response = requests.post(
                    CLAUDE_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )
                response.raise_for_status()

                return response.json()

            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"   ⚠️ Timeout after {timeout}s. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"   ✗ Failed after {max_retries} attempts")
                    raise

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"   ⚠️ Request error: {type(e).__name__}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"   ✗ Failed after {max_retries} attempts")
                    raise
    
    def load_optimized_context(self, command):
        """
        Load optimized context for command.

        INSTITUTIONAL LEARNING INTEGRATION (Jan 2026):
        Context now includes structured learning data from learning_database.json:
        - Critical system failures (ACTIVE failures shown prominently)
        - Catalyst performance metrics with statistical confidence
        - Market regime performance data
        - Exit timing patterns (for ANALYZE)
        - Actionable insights derived from data
        """

        context = {}

        # Load instructions
        instructions_file = self.project_dir / 'PROJECT_INSTRUCTIONS.md'
        if instructions_file.exists():
            context['instructions'] = instructions_file.read_text()[:5000]

        # Load strategy rules (limit to 8000 chars to prevent timeout)
        strategy_file = self.project_dir / 'strategy_evolution' / 'strategy_rules.md'
        if strategy_file.exists():
            context['strategy'] = strategy_file.read_text()[:8000]

        # Load catalyst exclusions with performance data
        exclusions = self.load_catalyst_exclusions()
        if exclusions:
            context['exclusions'] = '\n'.join([
                f"- {e['catalyst']}: {e.get('win_rate', 0):.1f}% win rate over {e.get('total_trades', 0)} trades - {e.get('reasoning', 'Poor performance')}"
                for e in exclusions
            ])
        else:
            context['exclusions'] = 'None (all catalysts available)'

        # INSTITUTIONAL LEARNING: Load structured learning context (Jan 2026)
        # This replaces the old unstructured lessons_learned.md with data-driven insights
        context['learning'] = self.get_learning_context_for_command(command)

        # Load portfolio
        if self.portfolio_file.exists():
            context['portfolio'] = self.portfolio_file.read_text()

        # Load account status
        if self.account_file.exists():
            context['account'] = self.account_file.read_text()

        context_str = f"""
PROJECT INSTRUCTIONS:
{context.get('instructions', 'Not found')}

STRATEGY RULES (AUTO-UPDATED BY LEARNING):
{context.get('strategy', 'Not found')}

============================================================
LEARNING DATABASE (Institutional Grade - Auto-Updated)
============================================================
{context.get('learning', 'Learning database initializing...')}

⚠️  EXCLUDED PATTERNS:
The following patterns have shown poor results. You may still use them if you have strong conviction,
but explain your reasoning and consider what makes this situation different from past failures.
Your decisions will be tracked for accountability.
{context.get('exclusions', 'None')}

CURRENT PORTFOLIO:
{context.get('portfolio', 'Not initialized')}

ACCOUNT STATUS:
{context.get('account', 'Not initialized')}
"""

        return context_str
    
    def load_catalyst_exclusions(self):
        """Load list of catalysts to avoid based on learning"""

        if not self.exclusions_file.exists():
            return []

        try:
            with open(self.exclusions_file, 'r') as f:
                data = json.load(f)
                return data.get('excluded_catalysts', [])
        except Exception as e:
            print(f"⚠️ Warning: Failed to load exclusions from {self.exclusions_file}: {e}")
            return []

    def log_exclusion_override(self, ticker, catalyst, reasoning, exclusion_data):
        """Log when Claude overrides an exclusion (for dashboard monitoring)"""

        log_file = self.project_dir / 'logs' / 'exclusion_overrides.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ticker': ticker,
            'catalyst': catalyst,
            'reasoning': reasoning,
            'historical_win_rate': exclusion_data.get('win_rate', 0),
            'historical_trades': exclusion_data.get('total_trades', 0),
            'result': 'PENDING'  # Will be updated when trade closes
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def load_catalyst_performance(self):
        """
        Load historical catalyst performance data from catalyst_performance.csv

        Returns dict with catalyst types as keys and performance metrics as values.
        This data is used to inform Claude about which catalyst types have worked well
        historically, enabling data-driven decision making.

        Learning System Integration (Jan 2026):
        - Updated weekly by learn_weekly.py
        - Provides win rates, avg returns, and sample size confidence
        - Enables Claude to prioritize proven catalyst types
        """
        catalyst_file = self.project_dir / 'strategy_evolution' / 'catalyst_performance.csv'

        if not catalyst_file.exists():
            return {}

        performance = {}
        try:
            with open(catalyst_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    catalyst_type = row.get('Catalyst_Type', '')
                    if not catalyst_type:
                        continue

                    total_trades = int(row.get('Total_Trades', 0))
                    if total_trades == 0:
                        continue  # Skip catalysts with no data

                    performance[catalyst_type] = {
                        'total_trades': total_trades,
                        'win_rate': float(row.get('Win_Rate_Percent', 0)),
                        'avg_return': float(row.get('Net_Avg_Return_Percent', 0)),
                        'avg_hold_days': float(row.get('Avg_Hold_Days', 0)),
                        'best_trade': float(row.get('Best_Trade_Percent', 0)),
                        'worst_trade': float(row.get('Worst_Trade_Percent', 0)),
                        'confidence': row.get('Sample_Size_Confidence', 'Low')
                    }
        except Exception as e:
            print(f"⚠️ Warning: Failed to load catalyst performance: {e}")
            return {}

        return performance

    def get_catalyst_performance_summary(self):
        """
        Generate a human-readable summary of catalyst performance for Claude.

        This is included in the GO command context so Claude can make informed
        decisions about which catalyst types to prioritize.

        Format:
        - Top performers with high confidence
        - Underperformers to approach with caution
        - New/untested catalyst types
        """
        performance = self.load_catalyst_performance()

        if not performance:
            return "No historical catalyst performance data available yet. Focus on Tier 1 catalysts with strong news validation."

        # Sort by win rate, then by sample size
        sorted_catalysts = sorted(
            performance.items(),
            key=lambda x: (x[1]['win_rate'], x[1]['total_trades']),
            reverse=True
        )

        lines = []

        # Top performers (win rate > 50% with Medium/High confidence)
        top_performers = [
            (cat, stats) for cat, stats in sorted_catalysts
            if stats['win_rate'] > 50 and stats['confidence'] in ['Medium', 'High']
        ]
        if top_performers:
            lines.append("📈 TOP PERFORMING CATALYSTS (prioritize these):")
            for cat, stats in top_performers[:5]:
                lines.append(f"   • {cat}: {stats['win_rate']:.0f}% win rate, {stats['avg_return']:+.1f}% avg return ({stats['total_trades']} trades, {stats['confidence']} confidence)")

        # Underperformers (win rate < 40% with at least 5 trades)
        underperformers = [
            (cat, stats) for cat, stats in sorted_catalysts
            if stats['win_rate'] < 40 and stats['total_trades'] >= 5
        ]
        if underperformers:
            lines.append("\n⚠️ UNDERPERFORMING CATALYSTS (approach with caution):")
            for cat, stats in underperformers[:3]:
                lines.append(f"   • {cat}: {stats['win_rate']:.0f}% win rate over {stats['total_trades']} trades")

        # Low sample size (< 5 trades)
        low_sample = [
            (cat, stats) for cat, stats in sorted_catalysts
            if stats['total_trades'] < 5
        ]
        if low_sample:
            lines.append(f"\nℹ️ {len(low_sample)} catalyst types have <5 trades (insufficient data for confidence)")

        return '\n'.join(lines) if lines else "Catalyst performance data is being collected. Make decisions based on catalyst tier and news quality."

    def calculate_statistical_significance(self, wins, total, baseline_rate=0.50):
        """
        Calculate if a win rate is statistically significantly different from baseline.

        Uses binomial test approximation (z-test for proportions).
        Returns True if the result is unlikely to be due to chance.

        Args:
            wins: Number of winning trades
            total: Total number of trades
            baseline_rate: Expected win rate (default 50%)

        Returns:
            dict with:
                - is_significant: Boolean
                - p_value_approx: Approximate p-value
                - confidence_level: 'Low' | 'Medium' | 'High'
        """
        import math

        if total < 5:
            return {
                'is_significant': False,
                'p_value_approx': 1.0,
                'confidence_level': 'Low',
                'reason': 'Insufficient sample size (<5 trades)'
            }

        observed_rate = wins / total

        # Standard error for proportion
        se = math.sqrt(baseline_rate * (1 - baseline_rate) / total)

        if se == 0:
            return {
                'is_significant': False,
                'p_value_approx': 1.0,
                'confidence_level': 'Low',
                'reason': 'Zero standard error'
            }

        # Z-score
        z = (observed_rate - baseline_rate) / se

        # Approximate p-value using normal distribution CDF approximation
        # For a two-tailed test
        abs_z = abs(z)

        # P-value approximation (simplified)
        if abs_z > 3.0:
            p_value = 0.003  # Very significant
        elif abs_z > 2.58:
            p_value = 0.01   # Highly significant (99% confidence)
        elif abs_z > 1.96:
            p_value = 0.05   # Significant (95% confidence)
        elif abs_z > 1.645:
            p_value = 0.10   # Marginally significant (90% confidence)
        else:
            p_value = 0.5    # Not significant

        # Determine confidence level based on sample size and significance
        if total >= 25 and p_value < 0.05:
            confidence_level = 'High'
        elif total >= 10 and p_value < 0.10:
            confidence_level = 'Medium'
        else:
            confidence_level = 'Low'

        return {
            'is_significant': p_value < 0.05,
            'p_value_approx': p_value,
            'z_score': z,
            'confidence_level': confidence_level,
            'observed_rate': observed_rate,
            'sample_size': total
        }

    # =====================================================================
    # INSTITUTIONAL LEARNING DATABASE (Jan 2026)
    # =====================================================================

    def load_learning_database(self):
        """
        Load the structured learning database.

        This is the primary source of learning data for Claude.
        Contains:
        - Critical failures and their resolution status
        - Catalyst performance metrics
        - Market regime performance
        - Entry/exit timing patterns
        - Active hypotheses under test
        - Actionable insights
        """
        db_file = self.project_dir / 'strategy_evolution' / 'learning_database.json'

        if not db_file.exists():
            return None

        try:
            with open(db_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"   Warning: Failed to load learning database: {e}")
            return None

    def save_learning_database(self, db):
        """Save the learning database with timestamp update."""
        db_file = self.project_dir / 'strategy_evolution' / 'learning_database.json'

        db['last_updated'] = datetime.now().isoformat()

        try:
            with open(db_file, 'w') as f:
                json.dump(db, f, indent=2)
            return True
        except Exception as e:
            print(f"   Error: Failed to save learning database: {e}")
            return False

    def get_learning_context_for_command(self, command):
        """
        Generate command-specific learning context for Claude.

        Different commands need different learning context:
        - GO: Full context (failures, catalyst performance, insights)
        - SCREEN: Catalyst performance only (for prioritization)
        - ANALYZE: Exit patterns and failure learnings
        - EXECUTE: System status only

        Returns a formatted string for inclusion in prompts.
        """
        db = self.load_learning_database()

        if not db:
            return "Learning database not yet initialized."

        lines = []

        # CRITICAL FAILURES - Always show ACTIVE failures prominently
        active_failures = [
            f for f in db.get('critical_failures', {}).get('failures', [])
            if f.get('status') == 'ACTIVE'
        ]

        if active_failures:
            lines.append("=" * 60)
            lines.append("CRITICAL SYSTEM FAILURES (UNRESOLVED)")
            lines.append("=" * 60)
            for failure in active_failures:
                lines.append(f"\nFAILURE: {failure.get('summary', 'Unknown')}")
                lines.append(f"Date: {failure.get('date')}")
                lines.append(f"Impact: {failure.get('impact', {})}")
                lines.append(f"Lesson: {failure.get('lesson_for_claude', 'None')}")
            lines.append("")

        # RESOLVED FAILURES - Brief mention of recent resolutions
        resolved_failures = [
            f for f in db.get('critical_failures', {}).get('failures', [])
            if f.get('status') == 'RESOLVED' and f.get('fix_implemented')
        ]

        if resolved_failures and command in ['go', 'analyze']:
            lines.append("Recent System Fixes (for awareness):")
            for failure in resolved_failures[-3:]:  # Last 3 only
                lines.append(f"  - {failure.get('summary')} [FIXED {failure.get('fix_implemented')}]")
            lines.append("")

        # CATALYST PERFORMANCE - For GO and SCREEN
        if command in ['go', 'screen']:
            catalyst_perf = db.get('catalyst_performance', {}).get('catalysts', {})

            # Find catalysts with actual data
            catalysts_with_data = [
                (name, stats) for name, stats in catalyst_perf.items()
                if stats.get('total_trades', 0) > 0
            ]

            if catalysts_with_data:
                # Sort by win rate
                catalysts_with_data.sort(key=lambda x: x[1].get('win_rate_pct', 0), reverse=True)

                lines.append("CATALYST PERFORMANCE (Data-Driven):")
                for name, stats in catalysts_with_data:
                    win_rate = stats.get('win_rate_pct', 0)
                    total = stats.get('total_trades', 0)
                    avg_return = stats.get('net_avg_return_pct', 0)
                    confidence = stats.get('confidence', 'LOW')

                    emoji = "" if win_rate >= 60 else "" if win_rate >= 50 else ""
                    lines.append(f"  {emoji} {name}: {win_rate:.0f}% win rate, {avg_return:+.1f}% avg ({total} trades, {confidence})")
                lines.append("")
            else:
                lines.append("CATALYST PERFORMANCE: Insufficient trade data. Prioritize Tier 1 catalysts.")
                lines.append("")

        # MARKET REGIME - For GO
        if command == 'go':
            regime_perf = db.get('market_regime_performance', {}).get('regimes', {})

            regimes_with_data = [
                (name, stats) for name, stats in regime_perf.items()
                if stats.get('total_trades', 0) >= 5
            ]

            if regimes_with_data:
                lines.append("MARKET REGIME PERFORMANCE:")
                for name, stats in regimes_with_data:
                    lines.append(f"  {name}: {stats.get('win_rate_pct', 0):.0f}% win rate, optimal size {stats.get('optimal_position_size_pct')}%")
                lines.append("")

        # EXIT PATTERNS - For ANALYZE
        if command == 'analyze':
            exit_patterns = db.get('exit_timing_patterns', {}).get('exit_types', {})

            exits_with_data = [
                (name, stats) for name, stats in exit_patterns.items()
                if stats.get('total', 0) > 0
            ]

            if exits_with_data:
                lines.append("EXIT TYPE PERFORMANCE:")
                for name, stats in exits_with_data:
                    total = stats.get('total', 0)
                    avg_return = stats.get('avg_return_pct', stats.get('avg_loss_pct', 0))
                    lines.append(f"  {name}: {total} exits, {avg_return:+.1f}% avg")
                lines.append("")

        # ACTIONABLE INSIGHTS - For all commands
        insights = db.get('actionable_insights', {}).get('insights', [])
        active_insights = [i for i in insights if i.get('priority') not in ['RESOLVED', 'DISMISSED']]

        if active_insights:
            lines.append("ACTIONABLE INSIGHTS:")
            for insight in active_insights[:5]:  # Top 5
                lines.append(f"  [{insight.get('type')}] {insight.get('message')}")
            lines.append("")

        # EXCLUDED PATTERNS - For GO and SCREEN
        if command in ['go', 'screen']:
            excluded = db.get('excluded_patterns', {}).get('patterns', [])
            if excluded:
                lines.append("EXCLUDED PATTERNS (Poor Performance):")
                for pattern in excluded:
                    lines.append(f"  - {pattern.get('name')}: {pattern.get('reason')}")
                lines.append("")

        return '\n'.join(lines) if lines else "No learning data available yet."

    def update_learning_from_trade(self, trade_data):
        """
        Update learning database after a trade closes.

        This is called automatically when a position is closed.
        Updates:
        - Catalyst performance stats
        - Market regime performance
        - Exit type statistics
        - Conviction level outcomes

        Args:
            trade_data: Dict with trade details (from completed_trades.csv format)
        """
        db = self.load_learning_database()
        if not db:
            print("   Warning: Cannot update learning - database not found")
            return

        # Extract trade details
        catalyst_type = trade_data.get('catalyst_type', 'Unknown')
        return_pct = float(trade_data.get('return_percent', 0))
        hold_days = int(trade_data.get('hold_days', 0))
        exit_type = trade_data.get('exit_type', 'unknown')
        conviction = trade_data.get('conviction_level', 'MEDIUM')
        market_regime = trade_data.get('market_regime', 'uncertain')
        ticker = trade_data.get('ticker', '')

        is_winner = return_pct > 0

        # Update catalyst performance
        catalyst_type_key = catalyst_type.replace(' ', '_').replace('-', '_')
        if catalyst_type_key in db.get('catalyst_performance', {}).get('catalysts', {}):
            cat_stats = db['catalyst_performance']['catalysts'][catalyst_type_key]

            cat_stats['total_trades'] = cat_stats.get('total_trades', 0) + 1
            if is_winner:
                cat_stats['winners'] = cat_stats.get('winners', 0) + 1
            else:
                cat_stats['losers'] = cat_stats.get('losers', 0) + 1

            # Recalculate averages
            total = cat_stats['total_trades']
            winners = cat_stats['winners']
            losers = cat_stats['losers']

            cat_stats['win_rate_pct'] = round((winners / total) * 100, 1) if total > 0 else 0

            # Update best/worst
            if return_pct > cat_stats.get('best_trade_pct', 0):
                cat_stats['best_trade_pct'] = round(return_pct, 2)
            if return_pct < cat_stats.get('worst_trade_pct', 0):
                cat_stats['worst_trade_pct'] = round(return_pct, 2)

            # Running average return
            prev_avg = cat_stats.get('net_avg_return_pct', 0)
            cat_stats['net_avg_return_pct'] = round(prev_avg + (return_pct - prev_avg) / total, 2)

            # Running average hold days
            prev_hold = cat_stats.get('avg_hold_days', 0)
            cat_stats['avg_hold_days'] = round(prev_hold + (hold_days - prev_hold) / total, 1)

            # Add to sample trades (keep last 10)
            sample = cat_stats.get('sample_trades', [])
            sample.append({
                'ticker': ticker,
                'return_pct': round(return_pct, 2),
                'hold_days': hold_days,
                'date': datetime.now().strftime('%Y-%m-%d')
            })
            cat_stats['sample_trades'] = sample[-10:]

            # Update confidence level
            if total >= 25:
                cat_stats['confidence'] = 'HIGH'
            elif total >= 10:
                cat_stats['confidence'] = 'MEDIUM'
            elif total >= 5:
                cat_stats['confidence'] = 'LOW'
            else:
                cat_stats['confidence'] = 'INSUFFICIENT_DATA'

        # Update market regime performance
        regime_key = market_regime.lower().replace(' ', '_').replace('-', '_')
        if regime_key in db.get('market_regime_performance', {}).get('regimes', {}):
            regime_stats = db['market_regime_performance']['regimes'][regime_key]

            regime_stats['total_trades'] = regime_stats.get('total_trades', 0) + 1
            total = regime_stats['total_trades']

            prev_win_rate = regime_stats.get('win_rate_pct', 0) * (total - 1) / 100
            new_wins = prev_win_rate + (1 if is_winner else 0)
            regime_stats['win_rate_pct'] = round((new_wins / total) * 100, 1)

            prev_avg = regime_stats.get('avg_return_pct', 0)
            regime_stats['avg_return_pct'] = round(prev_avg + (return_pct - prev_avg) / total, 2)

        # Update exit type statistics
        exit_key = exit_type.lower().replace(' ', '_').replace('-', '_')
        if exit_key in db.get('exit_timing_patterns', {}).get('exit_types', {}):
            exit_stats = db['exit_timing_patterns']['exit_types'][exit_key]

            exit_stats['total'] = exit_stats.get('total', 0) + 1
            total = exit_stats['total']

            prev_avg = exit_stats.get('avg_return_pct', exit_stats.get('avg_loss_pct', 0))
            exit_stats['avg_return_pct'] = round(prev_avg + (return_pct - prev_avg) / total, 2)

        # Update conviction level outcomes
        conviction_key = conviction.upper().replace('-', '_')
        if conviction_key in db.get('position_sizing_outcomes', {}).get('by_conviction', {}):
            conv_stats = db['position_sizing_outcomes']['by_conviction'][conviction_key]

            conv_stats['total_trades'] = conv_stats.get('total_trades', 0) + 1
            total = conv_stats['total_trades']

            prev_win_rate = conv_stats.get('win_rate_pct', 0) * (total - 1) / 100
            new_wins = prev_win_rate + (1 if is_winner else 0)
            conv_stats['win_rate_pct'] = round((new_wins / total) * 100, 1)

            prev_avg = conv_stats.get('avg_return_pct', 0)
            conv_stats['avg_return_pct'] = round(prev_avg + (return_pct - prev_avg) / total, 2)

        # Save updated database
        self.save_learning_database(db)
        print(f"   Learning updated: {catalyst_type} trade ({return_pct:+.1f}%)")

    def add_critical_failure(self, failure_id, summary, impact, root_causes, lesson_for_claude,
                            ticker=None, category='SYSTEM', severity='HIGH'):
        """
        Log a critical system failure for tracking and learning.

        Args:
            failure_id: Unique ID for the failure
            summary: Brief description
            impact: Dict with impact metrics
            root_causes: List of root cause strings
            lesson_for_claude: What Claude should learn from this
            ticker: Optional ticker if position-specific
            category: EXECUTION | ANALYSIS | SYSTEM | DATA
            severity: HIGH | MEDIUM | LOW
        """
        db = self.load_learning_database()
        if not db:
            return

        failure = {
            'id': failure_id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'ACTIVE',
            'category': category,
            'severity': severity,
            'ticker': ticker,
            'summary': summary,
            'impact': impact,
            'root_causes': root_causes,
            'fix_implemented': None,
            'fix_description': None,
            'lesson_for_claude': lesson_for_claude
        }

        db['critical_failures']['failures'].append(failure)
        self.save_learning_database(db)
        print(f"   Critical failure logged: {failure_id}")

    def resolve_critical_failure(self, failure_id, fix_description):
        """Mark a critical failure as resolved."""
        db = self.load_learning_database()
        if not db:
            return

        for failure in db.get('critical_failures', {}).get('failures', []):
            if failure.get('id') == failure_id:
                failure['status'] = 'RESOLVED'
                failure['fix_implemented'] = datetime.now().strftime('%Y-%m-%d')
                failure['fix_description'] = fix_description
                break

        self.save_learning_database(db)
        print(f"   Critical failure resolved: {failure_id}")

    def add_actionable_insight(self, insight_type, message, priority='NORMAL'):
        """
        Add an actionable insight for Claude to act on.

        Args:
            insight_type: STRATEGY | SYSTEM_FIX | PERFORMANCE | RISK
            message: The insight message
            priority: CRITICAL | HIGH | NORMAL | LOW
        """
        db = self.load_learning_database()
        if not db:
            return

        insight = {
            'type': insight_type,
            'priority': priority,
            'message': message,
            'date_added': datetime.now().strftime('%Y-%m-%d')
        }

        db['actionable_insights']['insights'].append(insight)

        # Keep only last 50 insights
        db['actionable_insights']['insights'] = db['actionable_insights']['insights'][-50:]

        self.save_learning_database(db)

    # =====================================================================
    # JSON PARSING AND PORTFOLIO CREATION
    # =====================================================================
    
    def extract_json_from_response(self, response_text):
        """Extract JSON block from Claude's response"""

        # Method 1: Try to find JSON in ```json code blocks (most common)
        json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response_text)
        if json_match:
            try:
                json_str = json_match.group(1)
                result = json.loads(json_str)
                if 'hold' in result or 'exit' in result or 'buy' in result:
                    return result
            except json.JSONDecodeError as e:
                print(f"   ⚠️ JSON code block parsing error: {e}")

        # Method 2: Try to find JSON in ``` code blocks (no json tag)
        json_match = re.search(r'```\s*(\{[\s\S]*?\})\s*```', response_text)
        if json_match:
            try:
                json_str = json_match.group(1)
                result = json.loads(json_str)
                if 'hold' in result or 'exit' in result or 'buy' in result:
                    return result
            except json.JSONDecodeError as e:
                print(f"   ⚠️ Code block parsing error: {e}")

        # Method 3: Fallback - look for raw JSON with "hold" key (GO command format)
        json_match = re.search(r'\{[^{}]*"hold"[^{}]*\}', response_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(0))
                return result
            except Exception as e:
                print(f"   ⚠️ Fallback hold-key JSON parsing error: {e}")

        # Method 4: Try to find any JSON object with expected keys
        # Look for JSON starting with { and containing hold/exit/buy
        for key in ['hold', 'exit', 'buy']:
            pattern = rf'\{{[^{{}}]*"{key}"[^{{}}]*\}}'
            json_match = re.search(pattern, response_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(0))
                    return result
                except Exception:
                    pass

        # Debug: Log what we received if nothing worked
        print(f"   ⚠️ Could not extract JSON. Response length: {len(response_text)}")
        print(f"   ⚠️ Response preview: {response_text[:500]}...")

        return None
    
    def update_portfolio_from_json(self, portfolio_data):
        """
        Update portfolio files from parsed JSON
        Used by EXECUTE command to create portfolio from pending selections
        """
        
        if not portfolio_data or 'positions' not in portfolio_data:
            print("   ⚠️ No valid portfolio data to update")
            return False
        
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        positions = []
        for pos in portfolio_data['positions']:
            # Calculate shares from position size and entry price
            entry_price = float(pos.get('entry_price', 0))
            position_size = float(pos.get('position_size', 100))
            shares = position_size / entry_price if entry_price > 0 else 0
            
            # Validate and fix stop_loss and price_target
            stop_loss = float(pos.get('stop_loss', 0))
            price_target = float(pos.get('price_target', 0))

            # Safety check: stop_loss must be below entry, target must be above
            if stop_loss >= entry_price or stop_loss == 0:
                stop_loss = entry_price * 0.90  # 10% stop loss
                print(f"   ⚠️ Fixed invalid stop_loss for {pos.get('ticker')}: ${stop_loss:.2f}")

            if price_target <= entry_price or price_target == 0:
                price_target = entry_price * 1.10  # 10% profit target
                print(f"   ⚠️ Fixed invalid price_target for {pos.get('ticker')}: ${price_target:.2f}")

            position = {
                "ticker": pos.get('ticker', ''),
                "entry_date": datetime.now().strftime('%Y-%m-%d'),
                "entry_price": entry_price,
                "shares": shares,
                "position_size": position_size,
                "current_price": entry_price,  # Will be updated by analyze
                "unrealized_gain_pct": 0.00,
                "unrealized_gain_dollars": 0.00,
                "catalyst": pos.get('catalyst', ''),
                "sector": pos.get('sector', ''),
                "confidence": pos.get('confidence', 'Medium'),
                "stop_loss": round(stop_loss, 2),
                "price_target": round(price_target, 2),
                "thesis": pos.get('thesis', ''),
                "days_held": 0
            }
            positions.append(position)
        
        # Create portfolio file
        portfolio_file_data = {
            "last_updated": now,
            "portfolio_status": f"Active - {len(positions)} positions",
            "total_positions": len(positions),
            "positions": positions,
            "closed_positions": []
        }
        
        with open(self.portfolio_file, 'w') as f:
            json.dump(portfolio_file_data, f, indent=2)
        
        print(f"   ✓ Created portfolio: {len(positions)} positions")
        
        # Update account status
        self.update_account_status()
        
        return True
    
    def update_account_status(self):
        """
        Update account_status.json with current portfolio value
        FIXED v5.0.1: Properly tracks cash from closed positions
        """

        # Starting capital (constant)
        STARTING_CAPITAL = 10000.00

        # Calculate current portfolio value (current market value, not cost basis)
        portfolio_value = 0.00
        cost_basis = 0.00
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                portfolio = json.load(f)
                for pos in portfolio.get('positions', []):
                    # Use current_price * shares for actual market value
                    current_price = pos.get('current_price', pos.get('entry_price', 0))
                    shares = pos.get('shares', 0)
                    entry_price = pos.get('entry_price', 0)

                    # FIXED: Cost basis = entry_price * shares (what we actually paid)
                    # NOT position_size (which was the allocation amount)
                    position_cost = entry_price * shares

                    portfolio_value += current_price * shares
                    cost_basis += position_cost

        # Calculate realized P&L from CSV (total profit/loss)
        realized_pl = 0.00
        total_trades = 0
        winners = []
        losers = []
        hold_times = []

        if self.trades_csv.exists():
            with open(self.trades_csv, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Trade_ID'):
                        total_trades += 1
                        return_dollars = float(row.get('Return_Dollars', 0))
                        return_pct = float(row.get('Return_Percent', 0))
                        hold_days = int(row.get('Hold_Days', 0))

                        realized_pl += return_dollars
                        hold_times.append(hold_days)

                        if return_pct > 0:
                            winners.append(return_pct)
                        else:
                            losers.append(return_pct)

        # FIXED: Calculate cash properly
        # Cash = Starting capital - Cost basis of positions + Realized P&L
        # Note: Use cost_basis (what we spent), not portfolio_value (current market value)
        cash_available = STARTING_CAPITAL - cost_basis + realized_pl

        # Account value = positions + cash
        # OR equivalently: STARTING_CAPITAL + realized_pl
        account_value = portfolio_value + cash_available

        # Calculate statistics
        win_rate = (len(winners) / total_trades * 100) if total_trades > 0 else 0.0
        avg_hold_time = sum(hold_times) / len(hold_times) if hold_times else 0.0
        avg_winner = sum(winners) / len(winners) if winners else 0.0
        avg_loser = sum(losers) / len(losers) if losers else 0.0

        unrealized_pl = portfolio_value - cost_basis

        account = {
            'account_value': round(account_value, 2),
            'cash_available': round(cash_available, 2),
            'positions_value': round(portfolio_value, 2),  # Current market value
            'cost_basis': round(cost_basis, 2),  # What we paid for positions
            'realized_pl': round(realized_pl, 2),
            'unrealized_pl': round(unrealized_pl, 2),  # Unrealized gain/loss
            'total_trades': total_trades,
            'win_rate_percent': round(win_rate, 2),
            'average_hold_time_days': round(avg_hold_time, 1),
            'average_winner_percent': round(avg_winner, 2),
            'average_loser_percent': round(avg_loser, 2),
            'last_updated': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        }

        with open(self.account_file, 'w') as f:
            json.dump(account, f, indent=2)

        unrealized_pl = portfolio_value - cost_basis
        print(f"   ✓ Updated account status: ${account_value:.2f} (Positions: ${portfolio_value:.2f} + Cash: ${cash_available:.2f}, Realized P&L: ${realized_pl:+.2f}, Unrealized P&L: ${unrealized_pl:+.2f})")
    
    # =====================================================================
    # VALIDATION AND LOGGING
    # =====================================================================
    
    def validate_trade_decisions(self, claude_response):
        """Validate that Claude's picks don't violate learned rules"""
        
        exclusions = self.load_catalyst_exclusions()
        
        if not exclusions:
            return True, []
        
        violations = []
        response_text = claude_response.lower()
        
        for excluded in exclusions:
            catalyst_name = excluded.get('catalyst', '').lower()
            if catalyst_name in response_text:
                violations.append(
                    f"⚠️ WARNING: {excluded['catalyst']} "
                    f"(win rate: {excluded['win_rate']:.1f}%) was mentioned despite being excluded"
                )
        
        return len(violations) == 0, violations
    
    def save_response(self, command, response):
        """Save Claude's response to daily reviews"""
        
        reviews_dir = self.project_dir / 'daily_reviews'
        reviews_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = reviews_dir / f'{command}_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(response, f, indent=2)

    def send_go_report_email(self, hold_positions, exit_positions, buy_positions, portfolio, trailing_stop_positions=None):
        """Send daily GO report email via SendGrid"""
        if not SENDGRID_AVAILABLE:
            print("   ⚠️ SendGrid not available, skipping email")
            return False

        api_key = os.environ.get('SENDGRID_API_KEY')
        from_email = os.environ.get('SENDGRID_FROM_EMAIL')
        to_emails = os.environ.get('SENDGRID_TO_EMAILS', '').split(',')

        if not api_key or not from_email or not to_emails[0]:
            print("   ⚠️ SendGrid not configured, skipping email")
            return False

        try:
            # Build email content
            today = datetime.now().strftime('%b %d, %Y')

            # Today's Decisions section
            trailing_count = len(trailing_stop_positions) if trailing_stop_positions else 0
            decisions_text = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TODAY'S DECISIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOLD: {len(hold_positions)} positions
EXIT: {len(exit_positions)} positions
BUY:  {len(buy_positions)} new positions
TRAILING STOPS: {trailing_count} positions
"""
            # Add new entries details
            if buy_positions:
                decisions_text += "\n📈 NEW ENTRIES:\n"
                for buy in buy_positions:
                    ticker = buy.get('ticker', 'N/A') if isinstance(buy, dict) else buy
                    if isinstance(buy, dict):
                        price = buy.get('entry_price', 0)
                        catalyst = buy.get('catalyst', 'N/A')
                        conviction = buy.get('conviction', 'MEDIUM')
                        decisions_text += f"• {ticker} @ ~${price:.2f}\n"
                        decisions_text += f"  Catalyst: {catalyst}\n"
                        decisions_text += f"  Conviction: {conviction}\n"
                    else:
                        decisions_text += f"• {ticker}\n"
            else:
                decisions_text += "\n📈 NEW ENTRIES:\n• None today\n"

            # Add exits details
            if exit_positions:
                decisions_text += "\n🚪 EXITS:\n"
                for exit_pos in exit_positions:
                    ticker = exit_pos.get('ticker', 'N/A') if isinstance(exit_pos, dict) else exit_pos
                    if isinstance(exit_pos, dict):
                        reason = exit_pos.get('reason', 'N/A')
                        decisions_text += f"• {ticker} - {reason}\n"
                    else:
                        decisions_text += f"• {ticker}\n"
            else:
                decisions_text += "\n🚪 EXITS:\n• None today\n"

            # Add trailing stops details (if any)
            if trailing_stop_positions:
                decisions_text += "\n🛡️ TRAILING STOPS (placed at 9:45 AM):\n"
                for ts in trailing_stop_positions:
                    ticker = ts.get('ticker', 'N/A')
                    return_pct = ts.get('return_pct', 0)
                    decisions_text += f"• {ticker} (+{return_pct:.1f}%) - 2% trailing stop\n"

            # Current Portfolio section
            portfolio_text = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CURRENT PORTFOLIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            positions = portfolio.get('positions', [])
            # Sort by return percentage descending
            sorted_positions = sorted(positions, key=lambda x: x.get('unrealized_gain_pct', 0), reverse=True)

            for pos in sorted_positions:
                ticker = pos.get('ticker', 'N/A')
                pnl_pct = pos.get('unrealized_gain_pct', 0)
                days = pos.get('days_held', 0)

                # Color indicator
                if pnl_pct > 0.5:
                    indicator = "🟢"
                elif pnl_pct < -0.5:
                    indicator = "🔴"
                else:
                    indicator = "⚪"

                portfolio_text += f"{ticker:<6} {pnl_pct:+6.1f}%  {indicator}  Day {days}\n"

            # Combine email body
            email_body = decisions_text + portfolio_text

            # Create and send email
            message = Mail(
                from_email=from_email,
                to_emails=to_emails,
                subject=f"📊 TedBot GO Report - {today}",
                plain_text_content=email_body
            )

            sg = SendGridAPIClient(api_key)
            response = sg.send(message)

            if response.status_code in [200, 201, 202]:
                print(f"   ✓ GO report email sent to {', '.join(to_emails)}")
                return True
            else:
                print(f"   ⚠️ Email send failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"   ⚠️ Email error: {str(e)}")
            return False

    # =====================================================================
    # POSITION MANAGEMENT
    # =====================================================================
    
    def standardize_exit_reason(self, position, exit_price, claude_reason=None):
        """
        Standardize exit reasons to simple, consistent format

        Returns standardized reason string with actual percentage
        Examples:
        - "Target reached (+11.6%)"
        - "Stop loss (-8.2%)"
        - "Time stop (21 days)"
        - "Catalyst failed (+2.1%)"
        """
        entry_price = position.get('entry_price', exit_price)
        return_pct = ((exit_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0

        # Determine exit type from Claude's reason or actual performance
        reason_lower = (claude_reason or '').lower()

        # Check for target hit
        if 'target' in reason_lower or return_pct >= 10:
            return f"Target reached ({return_pct:+.1f}%)"

        # Check for stop loss
        elif 'stop' in reason_lower or return_pct <= -7:
            return f"Stop loss ({return_pct:+.1f}%)"

        # Check for time stop
        elif 'time' in reason_lower or 'days' in reason_lower:
            days_held = position.get('days_held', 0)
            return f"Time stop ({days_held} days)"

        # Check for catalyst failure
        elif 'catalyst' in reason_lower or 'thesis' in reason_lower or 'invalid' in reason_lower:
            return f"Catalyst failed ({return_pct:+.1f}%)"

        # Default: Portfolio management
        else:
            return f"Portfolio decision ({return_pct:+.1f}%)"

    def check_position_exits(self, position, current_price):
        """
        Check if position should be closed based on stops/targets/news (FULL EXIT only)

        Exit Rules (Phase 1 - News Monitoring Integrated):
        1. News Invalidation: Score ≥70 (PRIORITY - check first)
        2. Stop Loss: -7% from entry (exit 100%)
        3. Price Target: +10% from entry (exit 100%)
        4. Time Stop: 21 days held (exit 100%)

        No partial exits - simplicity over complexity
        """

        ticker = position['ticker']
        entry_price = position['entry_price']
        stop_loss = position.get('stop_loss', entry_price * 0.93)  # -7%
        price_target = position.get('price_target', entry_price * 1.10)  # +10%

        return_pct = ((current_price - entry_price) / entry_price) * 100

        # PRIORITY 1: Check news invalidation (Phase 1)
        # This catches thesis-breaking news BEFORE it becomes a big loss
        try:
            news_result = self.calculate_news_invalidation_score(ticker)

            if news_result['should_exit']:
                # Log news invalidation event
                self.log_news_monitoring(
                    ticker=ticker,
                    event_type='INVALIDATION',
                    result=news_result,
                    entry_price=entry_price,
                    exit_price=current_price
                )

                # Format exit reason with news details
                if news_result['triggering_articles']:
                    top_article = news_result['triggering_articles'][0]
                    exit_reason = f"Catalyst invalidated - {top_article['title'][:50]}"
                else:
                    exit_reason = "Catalyst invalidated - negative news"

                print(f"      ⚠️ NEWS INVALIDATION: {ticker} (score: {news_result['score']})")
                if news_result['triggering_articles']:
                    print(f"         Article: {news_result['triggering_articles'][0]['title'][:80]}")

                return True, exit_reason, return_pct

        except Exception as e:
            print(f"      ⚠️ News check failed for {ticker}: {e}")
            # Continue to other exit checks if news check fails

        # PRIORITY 2: Check stop loss (-7%)
        if current_price <= stop_loss:
            standardized_reason = self.standardize_exit_reason(position, current_price, 'stop loss')
            return True, standardized_reason, return_pct

        # PRIORITY 3: Check profit target / trailing stop (Enhancement 1.1)
        # Once position hits target, activate trailing stop to let winners run
        if current_price >= price_target:
            # Enhancement 1.1: Trailing stop logic
            # Check if we should use trailing stop or exit immediately

            # Get gap percentage if available (from today's premarket)
            gap_pct = position.get('gap_percent', 0)

            # Gap-aware trailing stop activation
            if gap_pct >= 5.0:
                # Large gap: Wait for consolidation before trailing
                days_since_gap = position.get('days_since_large_gap', 0)

                if days_since_gap < 2:
                    # Still in gap volatility period - don't trail yet, just hold
                    position['days_since_large_gap'] = days_since_gap + 1
                    print(f"      🎯 {ticker} at +{return_pct:.1f}% after {gap_pct:+.1f}% gap, waiting for consolidation (day {days_since_gap + 1}/2)")
                    return False, 'Hold (gap consolidation)', return_pct

            # Activate or update trailing stop
            if not position.get('trailing_stop_active'):
                # First time hitting target - activate trailing stop
                position['trailing_stop_active'] = True
                position['trailing_stop_price'] = entry_price * 1.08  # Lock in +8% minimum (for JSON tracking)
                position['peak_price'] = current_price
                position['peak_return_pct'] = return_pct

                # CRITICAL: Place Alpaca trailing stop order for REAL-TIME execution
                # Alpaca will monitor continuously and sell if price drops 2% from peak
                if self.use_alpaca and self.broker:
                    shares = position.get('shares', 0)
                    if shares > 0:
                        success, msg, order_id = self.broker.place_trailing_stop_order(
                            ticker=ticker,
                            qty=int(shares),
                            trail_percent=2.0  # 2% trailing stop
                        )
                        if success:
                            position['alpaca_trailing_order_id'] = order_id
                            print(f"      🎯 {ticker} hit +{return_pct:.1f}% target!")
                            print(f"      📤 ALPACA TRAILING STOP PLACED: {int(shares)} shares, 2% trail (Order: {order_id})")
                            print(f"      → Alpaca will auto-sell if price drops 2% from peak")
                        else:
                            print(f"      🎯 {ticker} hit +{return_pct:.1f}% target, trailing stop activated at +8%")
                            print(f"      ⚠️ Alpaca trailing stop failed: {msg}")
                            print(f"      → Using JSON tracking as fallback (checked at 9:45 AM / 4:30 PM)")
                else:
                    print(f"      🎯 {ticker} hit +{return_pct:.1f}% target, trailing stop activated at +8% (${position['trailing_stop_price']:.2f})")
                    print(f"      → No Alpaca connection - using JSON tracking (checked at 9:45 AM / 4:30 PM)")

                return False, 'Hold (trailing active)', return_pct

            # Trailing stop already active - update peak tracking (for visibility)
            if current_price > position.get('peak_price', 0):
                position['peak_price'] = current_price
                position['peak_return_pct'] = return_pct
                # Update JSON tracking price (Alpaca handles the real trailing)
                position['trailing_stop_price'] = current_price * 0.98
                print(f"      📈 {ticker} new peak: +{return_pct:.1f}%")

                # Check if Alpaca trailing stop exists
                if self.use_alpaca and self.broker:
                    has_order, order_id, trail_pct = self.broker.has_trailing_stop_order(ticker)
                    if has_order:
                        print(f"      → Alpaca trailing stop active (Order: {order_id}, trail: {trail_pct}%)")
                    else:
                        # Re-place trailing stop if it was somehow lost
                        shares = position.get('shares', 0)
                        if shares > 0:
                            success, msg, order_id = self.broker.place_trailing_stop_order(
                                ticker=ticker,
                                qty=int(shares),
                                trail_percent=2.0
                            )
                            if success:
                                position['alpaca_trailing_order_id'] = order_id
                                print(f"      📤 Re-placed Alpaca trailing stop (Order: {order_id})")

            # Fallback check: If Alpaca trailing stop doesn't exist, use JSON tracking
            # (This catches cases where Alpaca order was canceled or failed)
            if not self.use_alpaca or not self.broker:
                if current_price <= position.get('trailing_stop_price', price_target):
                    peak_pct = position.get('peak_return_pct', return_pct)
                    exit_reason = f"Trailing stop at +{return_pct:.1f}% (peak +{peak_pct:.1f}%)"
                    return True, exit_reason, return_pct

            # Still trailing, hold position (Alpaca will handle the actual exit)
            return False, 'Hold (trailing)', return_pct

        # PRIORITY 4: Check time stop (21 days standard, 90 days for PED)
        entry_date_str = position['entry_date']
        entry_date = datetime.fromisoformat(entry_date_str.replace('Z', '+00:00')).replace(tzinfo=None) if 'T' in entry_date_str else datetime.strptime(entry_date_str, '%Y-%m-%d')
        days_held = (datetime.now() - entry_date).days

        # Enhancement 1.4: Extended hold period for PED positions
        is_ped = position.get('is_ped_candidate', False)
        max_hold_days = position.get('max_hold_days', 21)

        if days_held >= max_hold_days:
            if is_ped:
                standardized_reason = f"PED time stop ({days_held} days)"
            else:
                standardized_reason = self.standardize_exit_reason(position, current_price, 'time stop')
            return True, standardized_reason, return_pct

        return False, 'Hold', return_pct
    
    def close_position(self, position, exit_price, exit_reason):
        """Close a position and prepare trade data for CSV logging"""

        entry_price = position['entry_price']
        shares = position['shares']

        return_pct = ((exit_price - entry_price) / entry_price) * 100
        return_dollars = (exit_price - entry_price) * shares

        entry_date_str = position['entry_date']
        entry_date = datetime.fromisoformat(entry_date_str.replace('Z', '+00:00')).replace(tzinfo=None) if 'T' in entry_date_str else datetime.strptime(entry_date_str, '%Y-%m-%d')
        exit_date = datetime.now()
        hold_days = (exit_date - entry_date).days

        # Determine exit type from exit_reason
        exit_type = self._determine_exit_type(exit_reason, position)

        # Get current account value
        account_data = {}
        if self.account_file.exists():
            with open(self.account_file, 'r') as f:
                account_data = json.load(f)

        account_value_after = account_data.get('account_value', 1000.00)

        trade_data = {
            'trade_id': f"{position['ticker']}_{position['entry_date']}",
            'entry_date': position['entry_date'],
            'exit_date': exit_date.strftime('%Y-%m-%d'),
            'ticker': position['ticker'],
            'premarket_price': position.get('premarket_price', entry_price),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'gap_percent': position.get('gap_percent', 0),
            'shares': shares,
            'position_size': position['position_size'],
            'hold_days': hold_days,
            'return_percent': return_pct,
            'return_dollars': return_dollars,
            'exit_reason': exit_reason,
            'exit_type': exit_type,
            'catalyst_type': position.get('catalyst', 'Unknown'),
            'sector': position.get('sector', 'Unknown'),
            'confidence_level': position.get('confidence', 'Medium'),
            'stop_loss': position.get('stop_loss', 0),
            'price_target': position.get('price_target', 0),
            'thesis': position.get('thesis', ''),
            'what_worked': 'Auto-closed by system' if 'Target' in exit_reason else '',
            'what_failed': 'Hit stop loss' if 'Stop' in exit_reason else '',
            'account_value_after': account_value_after,
            'rotation_into_ticker': position.get('rotation_into_ticker', ''),
            'rotation_reason': position.get('rotation_reason', '')
        }

        return trade_data

    def _determine_exit_type(self, exit_reason, position):
        """Determine exit type category from exit reason"""
        reason_lower = exit_reason.lower()

        if 'rotation' in reason_lower or 'strategic' in reason_lower:
            return 'Strategic_Rotation'
        elif 'stop' in reason_lower:
            return 'Stop_Loss'
        elif 'target' in reason_lower:
            return 'Target_Reached'
        elif 'time' in reason_lower or 'days' in reason_lower:
            return 'Time_Stop'
        elif 'news' in reason_lower or 'invalid' in reason_lower:
            return 'News_Invalidation'
        else:
            return 'Other'
    
    def log_completed_trade(self, trade_data):
        """Write completed trade to CSV for learning system"""

        if not self.trades_csv.exists():
            self.trades_csv.parent.mkdir(parents=True, exist_ok=True)
            with open(self.trades_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Trade_ID', 'Entry_Date', 'Exit_Date', 'Ticker',
                    'Premarket_Price', 'Entry_Price', 'Exit_Price', 'Gap_Percent',
                    'Entry_Bid', 'Entry_Ask', 'Entry_Mid_Price', 'Entry_Spread_Pct', 'Slippage_Bps',  # v7.1 - Execution cost tracking
                    'Shares', 'Position_Size', 'Position_Size_Percent', 'Hold_Days', 'Return_Percent', 'Return_Dollars',
                    'Exit_Reason', 'Exit_Type', 'Catalyst_Type', 'Catalyst_Tier', 'Catalyst_Age_Days',
                    'News_Validation_Score', 'News_Exit_Triggered',
                    'VIX_At_Entry', 'Market_Regime', 'Macro_Event_Near',
                    'VIX_Regime', 'Market_Breadth_Regime',  # Phase 4 regime tracking
                    'System_Version',  # Enhancement 4.7 - Track code version per trade
                    'Ruleset_Version',  # v7.1 - Track trading rules version (policy drift prevention)
                    'Universe_Version',  # v7.1.1 - Track S&P 1500 constituent list (breadth stability)
                    'Relative_Strength', 'Stock_Return_3M', 'Sector_ETF',
                    'Conviction_Level', 'Supporting_Factors',
                    'Technical_Score', 'Technical_SMA50', 'Technical_EMA5', 'Technical_EMA20', 'Technical_ADX', 'Technical_Volume_Ratio',
                    'Volume_Quality', 'Volume_Trending_Up',  # Enhancement 2.2
                    'Keywords_Matched', 'News_Sources', 'News_Article_Count',  # Enhancement 2.5: Catalyst learning
                    'Sector', 'Stop_Loss', 'Stop_Pct', 'Price_Target',  # v7.1.1 - Added Stop_Pct for distribution analysis
                    'Trailing_Stop_Activated', 'Trailing_Stop_Price', 'Peak_Return_Pct',  # v7.1 - Exit policy tracking
                    'Thesis', 'What_Worked', 'What_Failed', 'Account_Value_After',
                    'Rotation_Into_Ticker', 'Rotation_Reason'
                ])

        # Bug #3 fix: Check for duplicate trade_id to prevent duplicate records
        trade_id = trade_data.get('trade_id', '')
        if self.trades_csv.exists() and trade_id:
            with open(self.trades_csv, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Trade_ID') == trade_id:
                        print(f"   ⚠️ DUPLICATE PREVENTED: Trade {trade_id} already exists in CSV")
                        print(f"      Existing exit: {row.get('Exit_Date')} at ${row.get('Exit_Price')} ({row.get('Return_Percent')}%)")
                        print(f"      Attempted: {trade_data.get('exit_date')} at ${trade_data.get('exit_price')} ({trade_data.get('return_percent')}%)")
                        return  # Don't log duplicate

        with open(self.trades_csv, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                trade_data.get('trade_id', ''),
                trade_data.get('entry_date', ''),
                trade_data.get('exit_date', ''),
                trade_data.get('ticker', ''),
                trade_data.get('premarket_price', 0),
                trade_data.get('entry_price', 0),
                trade_data.get('exit_price', 0),
                trade_data.get('gap_percent', 0),
                trade_data.get('entry_bid', 0),  # v7.1 - Execution cost tracking
                trade_data.get('entry_ask', 0),
                trade_data.get('entry_mid_price', 0),
                trade_data.get('entry_spread_pct', 0),
                trade_data.get('slippage_bps', 0),
                trade_data.get('shares', 0),
                trade_data.get('position_size', 0),
                trade_data.get('position_size_percent', 0),
                trade_data.get('hold_days', 0),
                trade_data.get('return_percent', 0),
                trade_data.get('return_dollars', 0),
                trade_data.get('exit_reason', ''),
                trade_data.get('exit_type', ''),
                trade_data.get('catalyst_type', ''),
                trade_data.get('catalyst_tier', 'Unknown'),
                trade_data.get('catalyst_age_days', 0),
                trade_data.get('news_validation_score', 0),
                trade_data.get('news_exit_triggered', False),
                trade_data.get('vix_at_entry', 0.0),
                trade_data.get('market_regime', 'Unknown'),
                trade_data.get('macro_event_near', 'None'),
                trade_data.get('vix_regime', 'UNKNOWN'),  # Phase 4 VIX regime
                trade_data.get('market_breadth_regime', 'UNKNOWN'),  # Phase 4 market breadth
                trade_data.get('system_version', SYSTEM_VERSION),  # Phase 4.7 - Track code version
                trade_data.get('ruleset_version', RULESET_VERSION),  # v7.1 - Track trading rules version
                trade_data.get('universe_version', UNIVERSE_VERSION),  # v7.1.1 - Track S&P 1500 constituent list
                trade_data.get('relative_strength', 0.0),
                trade_data.get('stock_return_3m', 0.0),
                trade_data.get('sector_etf', 'Unknown'),
                trade_data.get('conviction_level', 'MEDIUM'),
                trade_data.get('supporting_factors', 0),
                trade_data.get('technical_score', 0),
                trade_data.get('technical_sma50', 0.0),
                trade_data.get('technical_ema5', 0.0),
                trade_data.get('technical_ema20', 0.0),
                trade_data.get('technical_adx', 0.0),
                trade_data.get('technical_volume_ratio', 0.0),
                trade_data.get('volume_quality', ''),  # Enhancement 2.2
                trade_data.get('volume_trending_up', False),  # Enhancement 2.2
                trade_data.get('keywords_matched', ''),  # Enhancement 2.5: Catalyst learning
                trade_data.get('news_sources', ''),  # Enhancement 2.5
                trade_data.get('news_article_count', 0),  # Enhancement 2.5
                trade_data.get('sector', ''),
                trade_data.get('stop_loss', 0),
                trade_data.get('stop_pct', 0),  # v7.1.1 - Stop distance percentage
                trade_data.get('price_target', 0),
                trade_data.get('trailing_stop_activated', False),  # v7.1 - Exit policy tracking
                trade_data.get('trailing_stop_price', 0),
                trade_data.get('peak_return_pct', 0),
                trade_data.get('thesis', ''),
                trade_data.get('what_worked', ''),
                trade_data.get('what_failed', ''),
                trade_data.get('account_value_after', 0),
                trade_data.get('rotation_into_ticker', ''),
                trade_data.get('rotation_reason', '')
            ])

        print(f"   ✓ Logged trade to CSV: {trade_data.get('ticker')} "
              f"({trade_data.get('return_percent', 0):.2f}%)")

        # INSTITUTIONAL LEARNING: Update learning database with trade outcome (Jan 2026)
        try:
            self.update_learning_from_trade(trade_data)
        except Exception as e:
            print(f"   Warning: Failed to update learning database: {e}")
    
    def update_portfolio_prices_and_check_exits(self):
        """
        CRITICAL FUNCTION - The heart of the ANALYZE command

        1. Detect positions auto-sold by Alpaca trailing stops
        2. Fetch current prices for all positions
        3. Update P&L for each position
        4. Check if any stops/targets hit
        5. Close positions that need closing
        6. Update portfolio and account JSON files
        7. Log closed trades to CSV

        Returns: List of closed trades
        """

        print("\n" + "="*60)
        print("PORTFOLIO UPDATE & EXIT CHECKING")
        print("="*60 + "\n")

        if not self.portfolio_file.exists():
            print("   ⚠️ No portfolio file found")
            return []

        with open(self.portfolio_file, 'r') as f:
            portfolio = json.load(f)

        positions = portfolio.get('positions', [])

        if not positions:
            print("   ℹ No positions to update")
            return []

        # STEP 0: Check for positions auto-sold by Alpaca trailing stops
        alpaca_closed_trades = []
        if self.use_alpaca and self.broker:
            print("0. Checking for Alpaca trailing stop fills...")
            alpaca_positions = {p.symbol: p for p in self.broker.get_positions()}

            for position in positions[:]:  # Iterate copy to allow removal
                ticker = position['ticker']
                if position.get('trailing_stop_active') and ticker not in alpaca_positions:
                    # Position had trailing stop and is no longer in Alpaca = sold!
                    print(f"   🔔 {ticker} was AUTO-SOLD by Alpaca trailing stop!")

                    # Try to get the fill price from closed orders
                    exit_price = position.get('trailing_stop_price', position.get('current_price', 0))
                    try:
                        closed_orders = self.broker.get_orders_for_symbol(ticker, status='closed')
                        for order in closed_orders:
                            if order.type == 'trailing_stop' and order.status == 'filled':
                                exit_price = float(order.filled_avg_price)
                                print(f"      Fill price: ${exit_price:.2f}")
                                break
                    except Exception as e:
                        print(f"      ⚠️ Could not fetch fill price: {e}")

                    # Create trade record
                    peak_pct = position.get('peak_return_pct', 0)
                    entry_price = position.get('entry_price', 0)
                    return_pct = ((exit_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
                    exit_reason = f"Alpaca trailing stop (peak +{peak_pct:.1f}%)"

                    trade_data = self.close_position(position, exit_price, exit_reason)
                    self.log_completed_trade(trade_data)
                    alpaca_closed_trades.append(trade_data)

                    # Remove from positions list
                    positions.remove(position)
                    print(f"      ✓ Logged: {ticker} exited at ${exit_price:.2f} ({return_pct:+.1f}%)")

            if alpaca_closed_trades:
                print(f"   ✓ {len(alpaca_closed_trades)} position(s) auto-closed by Alpaca\n")
            else:
                print("   ✓ No Alpaca trailing stop fills detected\n")

        print(f"1. Updating {len(positions)} positions...")

        tickers = [pos['ticker'] for pos in positions]

        print("\n2. Fetching current market prices...")
        current_prices = self.fetch_current_prices(tickers)
        
        print("\n3. Checking exits and updating positions...")
        
        positions_to_keep = []
        closed_trades = []
        
        for position in positions:
            ticker = position['ticker']
            
            # Get current price (use entry price if fetch failed)
            current_price = current_prices.get(ticker, position['current_price'])
            
            # Update position metrics
            entry_price = position['entry_price']
            unrealized_gain_pct = ((current_price - entry_price) / entry_price) * 100
            unrealized_gain_dollars = (current_price - entry_price) * position['shares']
            
            position['current_price'] = current_price
            position['unrealized_gain_pct'] = round(unrealized_gain_pct, 2)
            position['unrealized_gain_dollars'] = round(unrealized_gain_dollars, 2)
            
            # Update days held (handle both YYYY-MM-DD and ISO format with time)
            entry_date_str = position['entry_date']
            if 'T' in entry_date_str:
                entry_date = datetime.fromisoformat(entry_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            else:
                entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d')
            position['days_held'] = (datetime.now() - entry_date).days
            
            # Check if position should be closed
            should_close, exit_reason, return_pct = self.check_position_exits(
                position, current_price
            )
            
            if should_close:
                print(f"   🚪 CLOSING: {ticker} - {exit_reason} ({return_pct:+.2f}%)")

                # v7.2 Stage 3b: Execute sell order via Alpaca (if available)
                alpaca_success, alpaca_msg, order_id = self._execute_alpaca_sell(
                    ticker,
                    position.get('shares', 0),
                    exit_reason
                )
                if alpaca_success:
                    print(f"      ✓ Alpaca: {alpaca_msg} (Order: {order_id})")
                elif "not available" not in alpaca_msg:
                    # Log Alpaca failures (but don't block the exit if Alpaca fails)
                    print(f"      ⚠️ Alpaca: {alpaca_msg}")
                    print(f"      → Continuing with JSON portfolio tracking")

                # Create trade record
                trade_data = self.close_position(position, current_price, exit_reason)

                # Log to CSV
                self.log_completed_trade(trade_data)

                closed_trades.append(trade_data)
            else:
                print(f"   ✓ {ticker}: ${current_price:.2f} ({unrealized_gain_pct:+.2f}%) - {exit_reason}")
                positions_to_keep.append(position)
        
        # Update portfolio file
        portfolio['positions'] = positions_to_keep
        portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        portfolio['portfolio_status'] = f"Active - {len(positions_to_keep)} positions"
        portfolio['total_positions'] = len(positions_to_keep)
        
        with open(self.portfolio_file, 'w') as f:
            json.dump(portfolio, f, indent=2)
        
        # Update account status
        print("\n4. Updating account status...")
        self.update_account_status()

        # Combine Alpaca auto-closed trades with manual closes
        all_closed_trades = alpaca_closed_trades + closed_trades

        print(f"\n✓ Portfolio updated: {len(positions_to_keep)} open, {len(all_closed_trades)} closed")
        if alpaca_closed_trades:
            print(f"   ({len(alpaca_closed_trades)} by Alpaca trailing stop, {len(closed_trades)} by exit check)")

        return all_closed_trades
    
    # =====================================================================
    # PORTFOLIO ROTATION (PHASE 4)
    # =====================================================================

    def evaluate_portfolio_rotation(self, hold_positions, new_opportunities, premarket_data):
        """
        Phase 4: Evaluate strategic rotation opportunities when portfolio is full
        Enhancement 2.3: Added quantitative rotation scoring

        Args:
            hold_positions: List of current positions being held
            new_opportunities: List of BUY recommendations from Claude
            premarket_data: Current price/P&L data for positions

        Returns:
            Dict with rotation decisions or empty if no rotations recommended
        """

        if len(hold_positions) < 10 or len(new_opportunities) == 0:
            return {'rotations': []}

        print("\n" + "="*70)
        print("PORTFOLIO ROTATION EVALUATION")
        print("="*70)
        print(f"Portfolio Status: {len(hold_positions)}/10 positions (FULL)")
        print(f"New Opportunities: {len(new_opportunities)} strong signals identified")
        print()

        # Enhancement 2.3: Quantitative rotation scoring
        rotation_candidates = self._score_rotation_candidates(hold_positions, new_opportunities)

        if len(rotation_candidates) == 0:
            print("   ✓ No quantitative rotation candidates identified\n")
            return {'rotations': []}

        print(f"   → {len(rotation_candidates)} candidate rotation(s) identified by quantitative scoring")
        print()

        # Build context for Claude with detailed position analysis
        context = self._build_rotation_context(hold_positions, new_opportunities, premarket_data, rotation_candidates)

        # Ask Claude to evaluate rotation opportunities
        print("Calling Claude to evaluate rotation opportunities...")
        response = self.call_claude_api('rotation_evaluation', context)

        # Extract rotation decisions
        decisions = self.extract_json_from_response(response)

        if not decisions or not decisions.get('rotations'):
            print("   ✓ No rotations recommended - holding current portfolio\n")
            return {'rotations': []}

        rotations = decisions['rotations']
        print(f"   ✓ Claude recommends {len(rotations)} rotation(s):\n")

        for rot in rotations:
            print(f"     EXIT: {rot['ticker']} → ENTER: {rot['target_ticker']}")
            print(f"     Reason: {rot['reason']}")
            print(f"     Expected Net Gain: {rot.get('expected_net_gain', 'N/A')}")
            print()

        return decisions

    def _score_rotation_candidates(self, hold_positions, new_opportunities):
        """
        Enhancement 2.3: Quantitative rotation scoring

        Scores each hold position as a rotation candidate based on:
        - Weak momentum (<0.3%/day)
        - Stalling (days > 5 and unrealized < +3%)
        - Catalyst aging (>3 days)

        Returns list of dicts with rotation recommendations
        """
        candidates = []

        for pos in hold_positions:
            ticker = pos['ticker']
            days_held = pos.get('days_held', 0)
            unrealized_pct = pos.get('unrealized_gain_pct', 0)
            catalyst_tier = pos.get('catalyst_tier', 'Unknown')

            # Calculate momentum velocity
            momentum = unrealized_pct / max(days_held, 1)

            # Rotation score (0-100, higher = better candidate to exit)
            rotation_score = 0
            rotation_reasons = []

            # Weak momentum (<0.3%/day): +30 points
            if momentum < 0.3:
                rotation_score += 30
                rotation_reasons.append(f'Weak momentum {momentum:+.2f}%/day')

            # Stalling position (>5 days, <+3%): +25 points
            if days_held > 5 and unrealized_pct < 3.0:
                rotation_score += 25
                rotation_reasons.append(f'Stalling at {unrealized_pct:+.1f}% after {days_held} days')

            # Losing position: +40 points
            if unrealized_pct < -2.0:
                rotation_score += 40
                rotation_reasons.append(f'Underwater {unrealized_pct:+.1f}%')

            # Low tier catalyst (Tier 2/3): +15 points
            if 'Tier2' in catalyst_tier or 'Tier3' in catalyst_tier or 'Tier 2' in catalyst_tier or 'Tier 3' in catalyst_tier:
                rotation_score += 15
                rotation_reasons.append(f'Lower tier catalyst ({catalyst_tier})')

            # Only recommend rotation if score >= 50
            if rotation_score >= 50:
                # Find best replacement opportunity
                best_opp = None
                best_opp_score = 0

                for opp in new_opportunities:
                    opp_score = 0
                    opp_tier = opp.get('catalyst_tier', '')
                    opp_news = opp.get('news_validation_score', 0)
                    opp_age = opp.get('catalyst_age_hours', 999)

                    # Tier 1 catalyst: +40 points
                    if 'Tier1' in opp_tier or 'Tier 1' in opp_tier:
                        opp_score += 40

                    # Fresh catalyst (<24hrs): +30 points
                    if opp_age < 24:
                        opp_score += 30

                    # High news validation (>80): +20 points
                    if opp_news > 80:
                        opp_score += 20

                    # Strong RS rating (>75): +10 points
                    if opp.get('rs_rating', 0) > 75:
                        opp_score += 10

                    if opp_score > best_opp_score:
                        best_opp_score = opp_score
                        best_opp = opp

                # Only recommend if new opportunity is significantly better (score >60)
                if best_opp and best_opp_score >= 60:
                    candidates.append({
                        'exit_ticker': ticker,
                        'exit_score': rotation_score,
                        'exit_reasons': rotation_reasons,
                        'enter_ticker': best_opp['ticker'],
                        'enter_score': best_opp_score,
                        'enter_catalyst': best_opp.get('catalyst', 'Unknown'),
                        'net_score': best_opp_score - (100 - rotation_score)  # Positive = good swap
                    })

        # Sort by net_score (best rotations first)
        candidates.sort(key=lambda x: x['net_score'], reverse=True)

        return candidates

    def _build_rotation_context(self, hold_positions, new_opportunities, premarket_data, rotation_candidates=None):
        """Build detailed context string for rotation evaluation"""

        context = "PORTFOLIO ROTATION EVALUATION\n\n"
        context += "="*70 + "\n\n"

        # Current holdings analysis
        context += "CURRENT HOLDINGS (10/10 - Portfolio Full):\n"
        context += "-"*70 + "\n\n"

        for pos in hold_positions:
            ticker = pos['ticker']
            entry_price = pos.get('entry_price', 0)
            current_price = pos.get('current_price', entry_price)
            days_held = pos.get('days_held', 0)
            catalyst = pos.get('catalyst', 'Unknown')
            catalyst_tier = pos.get('catalyst_tier', 'Unknown')
            unrealized_pct = pos.get('unrealized_gain_pct', 0)

            # Calculate momentum velocity
            velocity = unrealized_pct / max(days_held, 1)

            context += f"Ticker: {ticker}\n"
            context += f"  Current P&L: {unrealized_pct:+.2f}% (${current_price:.2f} vs ${entry_price:.2f})\n"
            context += f"  Days Held: {days_held} | Momentum: {velocity:+.2f}%/day\n"
            context += f"  Catalyst: {catalyst} ({catalyst_tier})\n"
            context += f"  Entry: {pos.get('entry_date', 'Unknown')}\n"
            context += "\n"

        # Enhancement 2.3: Quantitative rotation candidates
        if rotation_candidates:
            context += "\n" + "="*70 + "\n\n"
            context += f"QUANTITATIVE ROTATION CANDIDATES ({len(rotation_candidates)}):\n"
            context += "-"*70 + "\n\n"

            for cand in rotation_candidates:
                context += f"EXIT: {cand['exit_ticker']} (Score: {cand['exit_score']}/100)\n"
                context += f"  Reasons: {', '.join(cand['exit_reasons'])}\n"
                context += f"ENTER: {cand['enter_ticker']} (Score: {cand['enter_score']}/100)\n"
                context += f"  Catalyst: {cand['enter_catalyst']}\n"
                context += f"  Net Score: {cand['net_score']:+d} (Positive = favorable swap)\n"
                context += "\n"

        # New opportunities analysis
        context += "\n" + "="*70 + "\n\n"
        context += f"NEW OPPORTUNITIES ({len(new_opportunities)} signals):\n"
        context += "-"*70 + "\n\n"

        for opp in new_opportunities:
            context += f"Ticker: {opp['ticker']}\n"
            context += f"  Catalyst: {opp.get('catalyst', 'Unknown')} ({opp.get('catalyst_tier', 'Unknown')})\n"
            context += f"  Thesis: {opp.get('thesis', 'N/A')[:150]}...\n"
            context += f"  News Score: {opp.get('news_validation_score', 0)}/100\n"
            context += f"  Catalyst Age: {opp.get('catalyst_age_hours', 'Unknown')} hours\n"
            context += "\n"

        # Rotation guidance
        context += "\n" + "="*70 + "\n\n"
        context += "ROTATION DECISION CRITERIA:\n\n"
        context += "Consider rotating IF:\n"
        context += "1. WEAK POSITION: Low momentum (<0.3%/day), stalling thesis, or underperforming\n"
        context += "2. STRONG OPPORTUNITY: Tier 1 catalyst, fresh (<24hrs), high validation (>80/100)\n"
        context += "3. NET POSITIVE EV: Expected gain from new > current position + exit cost\n\n"
        context += "AVOID rotating IF:\n"
        context += "- Position has strong momentum (>0.5%/day)\n"
        context += "- Position near target (+8% or more)\n"
        context += "- New opportunity is stale (>48hrs) or low conviction\n"
        context += "- Would cause excessive churn (>3 rotations/week)\n\n"
        context += "="*70 + "\n\n"
        context += "TASK: Should we rotate any positions?\n\n"
        context += "Return JSON in this format:\n"
        context += "{\n"
        context += '  "rotations": [\n'
        context += '    {\n'
        context += '      "ticker": "XYZ",  // Position to exit\n'
        context += '      "reason": "Stalling at +2% after 8 days, momentum fading",\n'
        context += '      "target_ticker": "NVDA",  // New position to enter\n'
        context += '      "target_rationale": "Fresh Tier 1 earnings beat, 95/100 validation",\n'
        context += '      "expected_net_gain": "+6-8% vs holding to stop",\n'
        context += '      "confidence": "HIGH"\n'
        context += '    }\n'
        context += '  ]\n'
        context += "}\n\n"
        context += "If NO rotations recommended, return: {\"rotations\": []}\n"

        return context

    # =====================================================================
    # COMMAND EXECUTION
    # =====================================================================

    def execute_go_command(self):
        """
        Execute GO command (8:45 AM) - SWING TRADING VERSION

        NEW v5.0 BEHAVIOR:
        1. Load current portfolio (existing positions from yesterday)
        2. Fetch 15-min delayed premarket prices for existing positions
        3. Calculate premarket gaps and P&L for each position
        4. Ask Claude to review and decide: HOLD / EXIT / REPLACE
        5. For vacancies, Claude selects new positions
        6. Save decisions to pending_positions.json for EXECUTE to handle

        This implements proper swing trading: positions held 3-7 days,
        only exited on stops/targets/catalyst failures, not daily churn.
        """

        print("\n" + "="*60)
        print("EXECUTING 'GO' COMMAND - PORTFOLIO REVIEW (Swing Trading)")
        print("Agent v5.7.1 - AI-FIRST WITH EXPLICIT DECISIONS (Testing Phase)")
        print("="*60 + "\n")

        # Step 1: Load current portfolio
        print("1. Loading current portfolio...")
        current_portfolio = self.load_current_portfolio()
        existing_positions = current_portfolio.get('positions', [])
        print(f"   ✓ Loaded {len(existing_positions)} existing positions\n")

        # Step 2: Fetch premarket prices for existing positions
        premarket_data = {}
        if existing_positions:
            print("2. Fetching premarket prices (15-min delayed, ~8:30 AM)...")
            tickers = [p['ticker'] for p in existing_positions]
            premarket_prices = self.fetch_current_prices(tickers)

            for pos in existing_positions:
                ticker = pos['ticker']
                entry_price = pos.get('entry_price', 0)
                current_price = pos.get('current_price', entry_price)  # Yesterday's close
                days_held = pos.get('days_held', 0)

                # Use fetched premarket price if available, otherwise fall back to yesterday's close
                if ticker in premarket_prices:
                    premarket_price = premarket_prices[ticker]
                    price_source = "live"
                else:
                    # CRITICAL: If price fetch failed, use yesterday's close as fallback
                    # This ensures positions are NEVER silently dropped from review
                    premarket_price = current_price
                    price_source = "fallback (yesterday's close)"
                    print(f"   ⚠️ {ticker}: Using fallback price ${premarket_price:.2f} (yesterday's close)")

                # Calculate metrics using the price (live or fallback)
                pnl_percent = ((premarket_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
                gap_percent = ((premarket_price - current_price) / current_price * 100) if current_price > 0 else 0

                # ALWAYS add position to premarket_data - never skip due to failed price fetch
                premarket_data[ticker] = {
                    'entry_price': entry_price,
                    'yesterday_close': current_price,
                    'premarket_price': premarket_price,
                    'pnl_percent': round(pnl_percent, 2),
                    'gap_percent': round(gap_percent, 2),
                    'days_held': days_held,
                    'stop_loss': pos.get('stop_loss', 0),
                    'price_target': pos.get('price_target', 0),
                    'thesis': pos.get('thesis', ''),
                    'catalyst': pos.get('catalyst', ''),
                    'price_source': price_source  # Track if we're using live or fallback price
                }

                if price_source == "live":
                    gap_str = f"Gap: {gap_percent:+.1f}%" if abs(gap_percent) > 0.5 else "No gap"
                    print(f"   {ticker}: ${premarket_price:.2f} ({pnl_percent:+.1f}% total, {gap_str}, Day {days_held})")

            print(f"   ✓ Prepared {len(premarket_data)}/{len(existing_positions)} positions for review")
            print()
        else:
            print("2. No existing positions - building initial portfolio\n")

        # Step 3: Load context and call Claude for review
        print("3. Loading context for portfolio review...")
        context = self.load_optimized_context('go')
        print("   ✓ Context loaded\n")

        print("4. Calling Claude for position review and decisions...")

        # AI FAILOVER: Graceful degradation if Claude API fails
        try:
            response = self.call_claude_api('go', context, premarket_data)
            content_blocks = response.get('content', [])
            response_text = content_blocks[0].get('text', '') if content_blocks else ''
            print("   ✓ Response received\n")
        except Exception as e:
            # CRITICAL: Claude API failure - enter degraded mode
            error_type = type(e).__name__
            error_msg = str(e)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            print(f"\n{'='*70}")
            print(f"🚨 CLAUDE API FAILURE - DEGRADED MODE ACTIVATED")
            print(f"{'='*70}")
            print(f"   Error Type: {error_type}")
            print(f"   Error Message: {error_msg}")
            print(f"   Timestamp: {timestamp}")
            print(f"\n   DEGRADED MODE BEHAVIOR:")
            print(f"   - Skipping all new entries (no BUY recommendations)")
            print(f"   - Continuing to HOLD existing positions")
            print(f"   - Rule-based EXIT monitoring active (stops, time limits)")
            print(f"   - System will retry Claude API on next GO command")
            print(f"{'='*70}\n")

            # Log the failure for monitoring
            log_entry = {
                'timestamp': timestamp,
                'command': 'go',
                'error_type': error_type,
                'error_message': error_msg,
                'degraded_mode': True,
                'action_taken': 'Skipped new entries, held existing positions'
            }

            # Save failure log
            log_file = self.project_dir / 'logs' / 'claude_api_failures.json'
            log_file.parent.mkdir(exist_ok=True)

            existing_logs = []
            if log_file.exists():
                try:
                    existing_logs = json.loads(log_file.read_text())
                except Exception as e:
                    print(f"⚠️ Warning: Failed to load existing failure logs: {e}")
                    pass

            existing_logs.append(log_entry)
            log_file.write_text(json.dumps(existing_logs, indent=2))

            # Return degraded mode decisions: HOLD all existing, no new entries
            decisions = {
                'hold': [pos['ticker'] for pos in existing_positions] if existing_positions else [],
                'exit': [],
                'buy': []
            }

            # Create a minimal response for logging
            response_text = f"DEGRADED MODE: Claude API unavailable. Holding {len(decisions['hold'])} positions, no new entries."

            print("   ✓ Degraded mode decisions generated\n")

        # Step 4: Extract decisions from Claude's response (or degraded mode)
        print("5. Extracting decisions from response...")

        if not response_text or response_text.startswith('DEGRADED MODE:'):
            # Degraded mode: use the pre-generated decisions
            print("   ℹ️ Using degraded mode decisions (AI failover active)")
        else:
            # Normal mode: extract from Claude response
            decisions = self.extract_json_from_response(response_text)

            if not decisions:
                print("   ✗ No valid JSON found in response\n")
                return False

        # Step 5: Process decisions and create pending file
        hold_positions = decisions.get('hold', [])
        exit_positions = decisions.get('exit', [])
        buy_positions = decisions.get('buy', [])

        # VALIDATION: Filter HOLD/EXIT to only include tickers that actually exist in portfolio
        # This prevents Claude from hallucinating positions that don't exist
        actual_portfolio = self.load_current_portfolio()
        actual_tickers = set(p.get('ticker', '') for p in actual_portfolio.get('positions', []))

        if hold_positions and not actual_tickers:
            print(f"   ⚠️ Claude returned {len(hold_positions)} HOLD positions but portfolio is empty!")
            print(f"      Clearing phantom HOLD positions: {hold_positions}")
            hold_positions = []
        elif hold_positions:
            phantom_holds = [t for t in hold_positions if t not in actual_tickers]
            if phantom_holds:
                print(f"   ⚠️ Removing phantom HOLD tickers not in portfolio: {phantom_holds}")
                hold_positions = [t for t in hold_positions if t in actual_tickers]

        if exit_positions and not actual_tickers:
            phantom_exits = [e.get('ticker') if isinstance(e, dict) else e for e in exit_positions]
            print(f"   ⚠️ Claude returned EXIT positions but portfolio is empty: {phantom_exits}")
            exit_positions = []

        # VALIDATION: Check for ticker exclusivity (Bug #1 fix)
        hold_tickers = set(hold_positions)
        exit_tickers = set([e['ticker'] if isinstance(e, dict) else e for e in exit_positions])
        buy_tickers = set([b['ticker'] if isinstance(b, dict) else b for b in buy_positions])

        # Find duplicates across arrays
        all_tickers = []
        for t in hold_tickers: all_tickers.append(('hold', t))
        for t in exit_tickers: all_tickers.append(('exit', t))
        for t in buy_tickers: all_tickers.append(('buy', t))

        ticker_counts = {}
        for array_name, ticker in all_tickers:
            if ticker not in ticker_counts:
                ticker_counts[ticker] = []
            ticker_counts[ticker].append(array_name)

        duplicates = {t: arrays for t, arrays in ticker_counts.items() if len(arrays) > 1}

        if duplicates:
            print("   ⚠️ VALIDATION ERROR: Tickers in multiple arrays!")
            for ticker, arrays in duplicates.items():
                print(f"      {ticker}: {', '.join(arrays)}")
                # Resolve: If in exit, remove from hold/buy. If in buy, remove from hold.
                if 'exit' in arrays:
                    if ticker in hold_tickers:
                        hold_positions = [t for t in hold_positions if t != ticker]
                        print(f"      → Removed {ticker} from HOLD (exits take priority)")
                    buy_positions = [b for b in buy_positions if (b['ticker'] if isinstance(b, dict) else b) != ticker]
                elif 'buy' in arrays and 'hold' in arrays:
                    hold_positions = [t for t in hold_positions if t != ticker]
                    print(f"      → Removed {ticker} from HOLD (buys take priority)")
            print()

        print(f"   ✓ HOLD: {len(hold_positions)} positions")
        print(f"   ✓ EXIT: {len(exit_positions)} positions")
        print(f"   ✓ BUY:  {len(buy_positions)} new positions\n")

        # Step 5.3: PHASE 4 - Portfolio Rotation (when portfolio full)
        if len(hold_positions) >= 10 and len(buy_positions) > 0:
            print("5.3 Portfolio at capacity - evaluating rotation opportunities...")
            rotation_decision = self.evaluate_portfolio_rotation(
                hold_positions=hold_positions,
                new_opportunities=buy_positions,
                premarket_data=premarket_data
            )

            # Process rotation decisions
            if rotation_decision.get('rotations'):
                for rotation in rotation_decision['rotations']:
                    exit_ticker = rotation['ticker']
                    target_ticker = rotation['target_ticker']
                    rotation_reason = rotation['reason']

                    # Find the position to rotate out
                    rotated_position = None
                    for i, pos in enumerate(hold_positions):
                        if pos.get('ticker') == exit_ticker:
                            rotated_position = hold_positions.pop(i)
                            break

                    if rotated_position:
                        # Add rotation metadata
                        rotated_position['rotation_into_ticker'] = target_ticker
                        rotated_position['rotation_reason'] = rotation_reason
                        rotated_position['exit_reason'] = f"Strategic rotation for {target_ticker}: {rotation_reason}"

                        # Move to exit list
                        exit_positions.append(rotated_position)

                        print(f"   ✓ Rotation: {exit_ticker} → {target_ticker}")
                        print(f"      Reason: {rotation_reason}")

                print(f"   ✓ Processed {len(rotation_decision['rotations'])} rotation(s)\n")

                # Update decision counts
                print(f"   ✓ UPDATED - HOLD: {len(hold_positions)}, EXIT: {len(exit_positions)}, BUY: {len(buy_positions)}\n")
            else:
                print()

        # Step 5.4: PHASE 3-4 - Check VIX, Macro Calendar, and Market Breadth
        print("5.4 Checking market regime (Phase 3-4: VIX + Macro + Breadth)...")

        # Fetch VIX level
        vix_result = self.fetch_vix_level()
        print(f"   {vix_result['message']}")

        # Check macro calendar
        macro_result = self.check_macro_calendar()
        print(f"   {macro_result['message']}")

        # PHASE 4.2: Check market breadth & trend
        breadth_result = self.check_market_breadth()
        print(f"   {breadth_result['message']}")

        # Determine if we should proceed with BUY recommendations
        can_enter_positions = True
        regime_adjustment = None

        if vix_result['regime'] == 'SHUTDOWN':
            # VIX ≥35: No new entries at all
            print(f"   🚨 SYSTEM SHUTDOWN: VIX {vix_result['vix']} ≥35")
            print(f"   ✗ Blocking ALL {len(buy_positions)} BUY recommendations")
            buy_positions = []  # Clear all BUY recommendations
            can_enter_positions = False

        elif vix_result['regime'] == 'CAUTIOUS':
            # VIX 30-35: Only highest conviction (Tier 1 with news score ≥15)
            print(f"   ⚠️ CAUTIOUS MODE: VIX {vix_result['vix']} (30-35)")
            print(f"   → Filtering for HIGHEST CONVICTION ONLY (Tier 1 + News ≥15)")
            regime_adjustment = 'HIGHEST_CONVICTION_ONLY'

        # Store original buy_positions for daily picks tracking
        original_buy_positions = buy_positions.copy()

        if macro_result['is_blackout']:
            # Macro event blackout: No new entries
            print(f"   🚨 MACRO BLACKOUT: {macro_result['event_type']} on {macro_result['event_date']}")
            print(f"   ✗ Blocking ALL {len(buy_positions)} BUY recommendations")
            buy_positions = []  # Clear all BUY recommendations
            can_enter_positions = False

        print()

        # Step 5.5: PHASE 1-4 - Validate BUY recommendations OR track blocked picks
        validated_buys = []
        all_picks = []  # Track all picks (accepted + rejected) for dashboard - ALWAYS initialize

        # Load screener data for enhanced conviction factors
        screener_data = self.load_screener_candidates()
        screener_lookup = {}
        sector_rotation = {}

        if screener_data:
            # Create ticker lookup for fast access to screener candidate data
            for candidate in screener_data.get('candidates', []):
                screener_lookup[candidate['ticker']] = candidate

            # Extract sector rotation data
            sector_rotation = screener_data.get('sector_rotation', {})
            leading_sectors = sector_rotation.get('leading_sectors', [])
            print(f"   ℹ️  Loaded screener data: {len(screener_lookup)} candidates, Leading sectors: {', '.join(leading_sectors) if leading_sectors else 'None'}")

            # Check if Claude was actually shown candidates (only happens when there are vacant slots)
            # If portfolio was full, Claude wasn't asked about new entries
            portfolio = self.load_current_portfolio()
            current_position_count = portfolio.get('total_positions', 0)
            vacant_slots = 10 - current_position_count

            if vacant_slots > 0:
                # Claude WAS shown candidates - mark PASSed ones as REJECTED
                candidates_shown_to_claude = screener_data.get('candidates', [])[:15]
                buy_tickers_from_claude = set(bp.get('ticker') for bp in original_buy_positions if bp.get('ticker'))

                for candidate in candidates_shown_to_claude:
                    ticker = candidate.get('ticker', '')
                    if ticker and ticker not in buy_tickers_from_claude:
                        # Claude PASSed on this candidate - track as REJECTED
                        all_picks.append({
                            'ticker': ticker,
                            'status': 'REJECTED',
                            'conviction': 'PASS',
                            'position_size_pct': 0,
                            'catalyst': candidate.get('claude_catalyst', {}).get('catalyst_type', 'Unknown'),
                            'catalyst_tier': candidate.get('claude_catalyst', {}).get('tier', 'Unknown'),
                            'tier_name': f"Screener Validated - {candidate.get('claude_catalyst', {}).get('tier', 'Unknown')}",
                            'news_score': 0,
                            'relative_strength': candidate.get('relative_strength', {}).get('stock_return_3m', 0),
                            'vix': vix_result['vix'],
                            'supporting_factors': 0,
                            'reasoning': 'Claude PASS - Did not meet selection criteria',
                            'rejection_reasons': ['Claude PASS - Not selected for entry']
                        })
            else:
                # Portfolio was FULL - Claude wasn't asked about new entries
                # Mark candidates as SKIPPED (not evaluated), not REJECTED
                print(f"   ℹ️  Portfolio full ({current_position_count}/10) - candidates not shown to Claude")
                candidates_not_evaluated = screener_data.get('candidates', [])[:15]
                for candidate in candidates_not_evaluated:
                    ticker = candidate.get('ticker', '')
                    if ticker:
                        all_picks.append({
                            'ticker': ticker,
                            'status': 'SKIPPED',
                            'conviction': 'N/A',
                            'position_size_pct': 0,
                            'catalyst': candidate.get('claude_catalyst', {}).get('catalyst_type', 'Unknown'),
                            'catalyst_tier': candidate.get('claude_catalyst', {}).get('tier', 'Unknown'),
                            'tier_name': f"Screener Validated - {candidate.get('claude_catalyst', {}).get('tier', 'Unknown')}",
                            'news_score': 0,
                            'relative_strength': candidate.get('relative_strength', {}).get('stock_return_3m', 0),
                            'vix': vix_result['vix'],
                            'supporting_factors': 0,
                            'reasoning': 'Portfolio full - not evaluated',
                            'rejection_reasons': ['Portfolio full (10/10) - not shown to Claude']
                        })
        else:
            print(f"   ⚠️  No screener data available - conviction scoring will use limited factors")

        if original_buy_positions:
            print("5.5 Validating BUY recommendations (Phases 1-4: Full validation pipeline)...")

            for buy_pos in original_buy_positions:
                ticker = buy_pos.get('ticker', 'UNKNOWN')
                catalyst_type = buy_pos.get('catalyst', 'Unknown')
                catalyst_age = buy_pos.get('catalyst_age_days', 0)
                catalyst_details = buy_pos.get('catalyst_details', {})
                sector = buy_pos.get('sector', 'Unknown')

                # v5.7.1: Handle explicit decision and confidence fields
                decision = buy_pos.get('decision', 'ENTER')  # Default to ENTER for backward compatibility
                confidence_level = buy_pos.get('confidence_level', 'MEDIUM')

                # ENTER_SMALL: Cap position sizing
                if decision == 'ENTER_SMALL':
                    original_size = buy_pos.get('position_size_pct', 6.0)
                    buy_pos['position_size_pct'] = min(original_size, 6.0)
                    print(f"   ℹ️  {ticker}: ENTER_SMALL decision - capping position at 6% (Claude requested {original_size:.1f}%)")

                validation_passed = True
                rejection_reasons = []

                # Auto-reject if blackout or shutdown
                if not can_enter_positions:
                    validation_passed = False
                    if vix_result['regime'] == 'SHUTDOWN':
                        rejection_reasons.append(f"System shutdown: VIX {vix_result['vix']} ≥35")
                    elif macro_result['is_blackout']:
                        rejection_reasons.append(f"Macro blackout: {macro_result['event_type']} on {macro_result['event_date']}")

                try:
                    # Skip detailed validation during blackouts (just track the rejection)
                    if not can_enter_positions:
                        # Create minimal pick data for blackout scenario
                        all_picks.append({
                            'ticker': ticker,
                            'status': 'REJECTED',
                            'conviction': 'N/A',
                            'position_size_pct': 0,
                            'catalyst': catalyst_type,
                            'catalyst_tier': 'Unknown',
                            'tier_name': 'Unknown',
                            'news_score': 0,
                            'relative_strength': 0,
                            'vix': vix_result['vix'],
                            'supporting_factors': 0,
                            'reasoning': buy_pos.get('reasoning', ''),
                            'rejection_reasons': rejection_reasons
                        })
                        print(f"   ✗ {ticker}: REJECTED - {rejection_reasons[0]}")
                        continue  # Skip to next position

                    # LEARNED EXCLUSIONS: Check if catalyst was historically poor (soft warning)
                    exclusions = self.load_catalyst_exclusions()
                    excluded_catalysts = {e['catalyst'].lower(): e for e in exclusions}

                    if catalyst_type.lower() in excluded_catalysts:
                        excl = excluded_catalysts[catalyst_type.lower()]

                        # Log usage of excluded catalyst (Claude made this choice with full context)
                        print(f"   ⚠️  {ticker}: Using historically poor catalyst '{catalyst_type}'")
                        print(f"      Historical: {excl['win_rate']:.1f}% win rate over {excl['total_trades']} trades")
                        print(f"      Claude's reasoning: {buy_pos.get('reasoning', 'Not specified')}")

                        # Log for dashboard accountability tracking
                        self.log_exclusion_override(
                            ticker,
                            catalyst_type,
                            buy_pos.get('reasoning', 'Claude chose despite historical underperformance'),
                            excl
                        )

                        # Mark position for close monitoring
                        buy_pos['used_excluded_catalyst'] = True
                        buy_pos['exclusion_win_rate'] = excl['win_rate']
                        buy_pos['requires_close_monitoring'] = True

                    # PHASE 2: Check catalyst tier
                    tier_result = self.classify_catalyst_tier(catalyst_type, catalyst_details)

                    # v5.7: Tier 3 auto-reject removed - Claude makes holistic decision
                    # Log tier for sizing context only
                    if tier_result['tier'] == 'Tier3':
                        print(f"   ℹ️  {ticker}: Tier 3 catalyst ({tier_result['reasoning']}) - risk flag for sizing")
                        if 'risk_flags' not in buy_pos:
                            buy_pos['risk_flags'] = []
                        buy_pos['risk_flags'].append(f"tier3: {tier_result['reasoning']}")

                    # Check catalyst age validity
                    age_check = self.check_catalyst_age_validity(catalyst_type, catalyst_age)
                    if not age_check['is_valid']:
                        validation_passed = False
                        rejection_reasons.append(age_check['reason'])

                    # HYBRID SCREENER v9.0 (Dec 31, 2025): News validation removed
                    # ARCHITECTURAL FIX: Data should be fetched BEFORE Claude analyzes, not used to veto after
                    #
                    # Old (BROKEN) flow:
                    #   1. Screener (7 AM): Keyword matching for catalysts
                    #   2. GO (8:45 AM): Claude sees top 15, makes recommendations
                    #   3. Validation: Re-fetches news, vetoes Claude if score < 5
                    #
                    # New (v9.0) flow:
                    #   1. Screener (7 AM): Claude analyzes 200-300 stocks with news
                    #   2. GO (8:45 AM): Claude sees top 40 with Claude's tier classifications
                    #   3. Validation: Only applies safety rails (buying power, VIX, macro blackouts)
                    #
                    # We trust Claude's catalyst analysis from screener + GO command.
                    # Validation no longer re-fetches news or vetoes based on automated scoring.

                    # PHASE 1: News validation - INFORMATIONAL ONLY (no veto)
                    # Keep the function call for logging/monitoring, but don't reject based on score
                    news_result = self.calculate_news_validation_score(
                        ticker=ticker,
                        catalyst_type=catalyst_type,
                        catalyst_age_days=catalyst_age
                    )

                    # Log validation event (for monitoring only)
                    self.log_news_monitoring(
                        ticker=ticker,
                        event_type='VALIDATION',
                        result=news_result
                    )

                    # v9.0: DO NOT VETO based on news score - trust Claude's analysis
                    # The news_result is kept for logging/learning purposes only
                    # if news_result['score'] < 5:  # REMOVED - no longer vetoes
                    #     validation_passed = False
                    #     rejection_reasons.append(f"News score too low ({news_result['score']}/20}")

                    # PHASE 3: Apply regime-based filtering
                    if regime_adjustment == 'HIGHEST_CONVICTION_ONLY':
                        # v9.0: VIX 30-35 only accepts Tier 1 (removed news score requirement)
                        # Trust Claude's tier classification from screener, don't re-check news score
                        if tier_result['tier'] != 'Tier1':
                            validation_passed = False
                            rejection_reasons.append(f"VIX {vix_result['vix']} - requires Tier1 only")

                    # PHASE 4: Relative Strength + Conviction Sizing
                    rs_result = self.calculate_relative_strength(ticker, sector)
                    # NOTE: RS filter removed in v7.1 - RS now used for scoring only

                    # PHASE 5.6: Technical Filters (4 essential swing trading indicators)
                    # v5.6 (Jan 11, 2026): SOFT FLAGS ONLY - Log warnings but don't block entries
                    # Rationale: Screener finds catalyst momentum, these filters reject momentum
                    # Solution: Convert to risk context for learning, not veto power
                    print(f"   📊 Checking technical setup for {ticker}...")
                    tech_result = self.calculate_technical_score(ticker)

                    # Extract current price from technical result for later use
                    current_price = tech_result.get('details', {}).get('price', 0)

                    # Log technical setup as risk flag, but DON'T reject
                    if not tech_result['passed']:
                        print(f"   ⚠️  Technical risk flag: {tech_result['reason']}")
                        # Store flag for learning but don't block entry
                        if 'risk_flags' not in buy_pos:
                            buy_pos['risk_flags'] = []
                        buy_pos['risk_flags'].append(f"technical: {tech_result['reason']}")
                    else:
                        print(f"   ✓ Technical passed: {tech_result['reason']}")

                    # Enhancement 1.5: Stage 2 Alignment Check (Minervini)
                    # v5.6 (Jan 11, 2026): SOFT FLAGS ONLY - Stage 2 is for trend-following, not catalyst momentum
                    print(f"   📈 Checking Stage 2 alignment for {ticker}...")
                    stage2_result = self.check_stage2_alignment(ticker)

                    if not stage2_result['stage2']:
                        if 'error' in stage2_result:
                            reason = f"Stage 2 check failed: {stage2_result['error']}"
                        else:
                            reason = f"Not in Stage 2 ({stage2_result['checks_passed']}/5 checks passed)"
                        print(f"   ⚠️  Stage 2 risk flag: {reason}")
                        # Store flag for learning but don't block entry
                        if 'risk_flags' not in buy_pos:
                            buy_pos['risk_flags'] = []
                        buy_pos['risk_flags'].append(f"stage2: {reason}")
                    else:
                        distance_52w = stage2_result['distance_from_52w_high_pct']
                        print(f"   ✓ Stage 2: Confirmed uptrend ({distance_52w:+.0f}% from 52W high)")

                    # Always store Stage 2 data for position metadata
                    buy_pos['stage2_data'] = stage2_result

                    # Enhancement 1.6: Entry Timing Check
                    # v5.6 (Jan 11, 2026): SOFT FLAGS ONLY - Entry timing rejects catalyst momentum
                    # Catalyst stocks are EXPECTED to be extended/overbought (that's the momentum from news)
                    print(f"   ⏱️  Checking entry timing for {ticker}...")
                    timing_result = self.check_entry_timing(ticker, current_price)

                    if timing_result['wait_for_pullback']:
                        reason = f"Entry timing concern: {', '.join(timing_result['reasons'])}"
                        print(f"   ⚠️  Entry Timing risk flag: {timing_result['entry_quality']}")
                        for timing_reason in timing_result['reasons']:
                            print(f"      - {timing_reason}")
                        # Store flag for learning but don't block entry
                        if 'risk_flags' not in buy_pos:
                            buy_pos['risk_flags'] = []
                        buy_pos['risk_flags'].append(f"entry_timing: {', '.join(timing_result['reasons'])}")
                    elif timing_result['entry_quality'] == 'CAUTION':
                        print(f"   ⚠️  Entry Timing: CAUTION - {timing_result['entry_quality']}")
                        for timing_reason in timing_result['reasons']:
                            print(f"      - {timing_reason}")
                        # Store caution flag
                        if 'risk_flags' not in buy_pos:
                            buy_pos['risk_flags'] = []
                        buy_pos['risk_flags'].append(f"entry_timing_caution: {', '.join(timing_result['reasons'])}")
                    else:
                        print(f"   ✓ Entry Timing: {timing_result['entry_quality']} (RSI: {timing_result.get('rsi', 0):.0f}, {timing_result.get('distance_from_ma20_pct', 0):+.1f}% from 20MA)")

                    # Always store timing data for position metadata
                    buy_pos['timing_data'] = timing_result

                    # Enhancement 1.4: Post-Earnings Drift Check
                    print(f"   📈 Checking for post-earnings drift potential...")
                    ped_result = self.detect_post_earnings_drift(ticker, catalyst_details)

                    if ped_result['drift_expected']:
                        print(f"   ✓ PED Detected: {ped_result['confidence']} confidence")
                        print(f"      {ped_result['reasoning']}")
                        print(f"      Target: +{ped_result['target_pct']:.0f}%, Hold: {ped_result['hold_period']}")
                        # Store PED data for position metadata
                        buy_pos['ped_data'] = ped_result
                        buy_pos['is_ped_candidate'] = True
                        # Override max hold period for PED positions
                        buy_pos['max_hold_days'] = 90  # Extended hold for drift
                    else:
                        print(f"   ℹ️  PED: {ped_result['reasoning']}")
                        buy_pos['is_ped_candidate'] = False

                    # Calculate conviction level (determines final position size)
                    multi_catalyst = catalyst_type == 'Multi_Catalyst' or catalyst_details.get('multi_catalyst', False)

                    # Extract enhanced data from screener if available
                    screener_candidate = screener_lookup.get(ticker, {})
                    rs_percentile = screener_candidate.get('relative_strength', {}).get('rs_percentile')
                    options_flow = screener_candidate.get('options_flow')
                    dark_pool = screener_candidate.get('dark_pool')
                    revenue_beat = screener_candidate.get('revenue_surprise', {}).get('has_beat', False)

                    # Check if stock's sector is leading
                    sector_perf = sector_rotation.get('sector_performance', {}).get(sector, {})
                    sector_leading = sector_perf.get('is_leading', False)
                    sector_vs_spy = sector_perf.get('vs_spy', 0)

                    # BUG FIX (Jan 2, 2026): Use screener's tier classification instead of recalculating
                    # The screener already ran Claude analysis and classified tiers - trust it
                    screener_tier = screener_candidate.get('catalyst_tier')

                    # BUG FIX (Jan 30, 2026): Use screener's actual catalyst type, not "Screener Validated"
                    # The screener has the real catalyst (Earnings_Beat, M&A_Target, etc.) in claude_catalyst
                    screener_catalyst_type = screener_candidate.get('claude_catalyst', {}).get('catalyst_type')
                    if screener_catalyst_type and screener_catalyst_type != 'Unknown' and screener_catalyst_type != 'None':
                        catalyst_type = screener_catalyst_type
                        buy_pos['catalyst'] = screener_catalyst_type  # Update position with real catalyst
                        print(f"   ℹ️  Using screener catalyst: {screener_catalyst_type}")

                    if screener_tier:
                        # Override tier_result with screener's tier (more accurate)
                        tier_result['tier'] = screener_tier.replace(' ', '')  # 'Tier 1' → 'Tier1'
                        # Use actual catalyst type in tier_name if available
                        if screener_catalyst_type and screener_catalyst_type != 'Unknown':
                            tier_result['tier_name'] = f'{screener_catalyst_type} ({screener_tier})'
                        else:
                            tier_result['tier_name'] = f'Screener Validated - {screener_tier}'
                        tier_result['reasoning'] = 'Tier assigned by screener Claude analysis'
                        print(f"   ℹ️  Using screener tier: {screener_tier}")

                    conviction_result = self.calculate_conviction_level(
                        catalyst_tier=tier_result['tier'],
                        news_score=news_result['score'],
                        vix=vix_result['vix'],
                        relative_strength=rs_result['relative_strength'],
                        multi_catalyst=multi_catalyst,
                        rs_percentile=rs_percentile,
                        sector_leading=sector_leading,
                        sector_vs_spy=sector_vs_spy,
                        options_flow=options_flow,
                        dark_pool=dark_pool,
                        revenue_beat=revenue_beat
                    )

                    # v5.7: Conviction SKIP no longer blocks entry - becomes sizing guidance
                    # Claude already made the decision; we respect it and adjust risk via size
                    if conviction_result['conviction'] == 'SKIP':
                        print(f"   ⚠️  {ticker}: Low conviction ({conviction_result['reasoning']}) - reducing to starter position")
                        if 'risk_flags' not in buy_pos:
                            buy_pos['risk_flags'] = []
                        buy_pos['risk_flags'].append(f"low_conviction: {conviction_result['reasoning']}")
                        # Override position size to starter level (5%)
                        buy_pos['position_size_pct'] = 5.0
                    elif conviction_result['conviction'] == 'LOW':
                        print(f"   ⚠️  {ticker}: Low conviction - smaller position size")
                        buy_pos['position_size_pct'] = 6.0

                    # If all validations pass, accept the position
                    if validation_passed:
                        # Enrich position with all Phase data (1-5.6)
                        buy_pos['catalyst_tier'] = tier_result['tier']
                        buy_pos['tier_name'] = tier_result['tier_name']
                        buy_pos['tier_reasoning'] = tier_result['reasoning']
                        buy_pos['news_score'] = news_result['score']
                        buy_pos['vix_at_entry'] = vix_result['vix']
                        buy_pos['market_regime'] = vix_result['regime']

                        # VIX Regime Classification (for learning & attribution)
                        vix = vix_result['vix']
                        if vix < 15:
                            vix_regime = 'VERY_LOW'  # Complacency risk
                        elif vix < 20:
                            vix_regime = 'LOW'  # Ideal for swing trading
                        elif vix < 25:
                            vix_regime = 'ELEVATED'  # Caution
                        elif vix < 30:
                            vix_regime = 'HIGH'  # High risk
                        else:
                            vix_regime = 'EXTREME'  # Shutdown mode
                        buy_pos['vix_regime'] = vix_regime

                        buy_pos['macro_event_near'] = macro_result['event_type'] or 'None'
                        buy_pos['relative_strength'] = rs_result['relative_strength']
                        buy_pos['rs_rating'] = rs_result['rs_rating']  # Enhancement 2.1
                        buy_pos['stock_return_3m'] = rs_result['stock_return_3m']
                        buy_pos['sector_etf'] = rs_result['sector_etf']
                        buy_pos['conviction_level'] = conviction_result['conviction']

                        # PHASE 4.2: Apply market breadth adjustment to position size
                        # BUG FIX (Jan 21, 2026): Don't override position_size_pct if already set by SKIP/LOW logic
                        # The v5.7 SKIP handling at lines 5950-5961 sets position_size_pct to 5.0 or 6.0
                        # We should NOT overwrite that with 0.0 from conviction_result
                        existing_size = buy_pos.get('position_size_pct', 0)
                        if existing_size > 0:
                            # Position size was already set (e.g., by Claude's recommendation or SKIP override)
                            # Apply breadth adjustment to the existing size, not conviction's 0
                            base_position_size = existing_size
                        else:
                            base_position_size = conviction_result['position_size_pct']

                        breadth_adjustment = breadth_result['position_size_adjustment']
                        adjusted_position_size = base_position_size * breadth_adjustment

                        # Only update if we have a valid size (don't set to 0)
                        if adjusted_position_size > 0:
                            buy_pos['position_size_pct'] = adjusted_position_size
                        buy_pos['position_size_base'] = base_position_size  # Store original for reference
                        buy_pos['market_breadth_adjustment'] = breadth_adjustment  # Store adjustment factor
                        buy_pos['market_breadth_regime'] = breadth_result['regime']  # Store regime

                        buy_pos['target_pct'] = tier_result['target_pct']
                        buy_pos['supporting_factors'] = conviction_result['supporting_factors']

                        # Phase 5.6: Technical indicators
                        buy_pos['technical_score'] = tech_result['score']
                        buy_pos['technical_sma50'] = tech_result['details'].get('sma50')
                        buy_pos['technical_ema5'] = tech_result['details'].get('ema5')
                        buy_pos['technical_ema20'] = tech_result['details'].get('ema20')
                        buy_pos['technical_adx'] = tech_result['details'].get('adx')
                        buy_pos['technical_volume_ratio'] = tech_result['details'].get('volume_ratio')
                        buy_pos['volume_quality'] = tech_result['details'].get('volume_quality')  # Enhancement 2.2
                        buy_pos['volume_trending_up'] = tech_result['details'].get('volume_trending_up')  # Enhancement 2.2

                        # Enhancement 2.5: Extract keywords and news sources for learning
                        catalyst_signals = catalyst_details.get('catalyst_signals', {})
                        keywords_matched = catalyst_signals.get('keywords', [])
                        top_articles = catalyst_signals.get('top_articles', [])
                        news_sources = [article.get('url', '').split('/')[2] if '/' in article.get('url', '') else 'Unknown' for article in top_articles[:3]]

                        buy_pos['keywords_matched'] = ','.join(keywords_matched) if keywords_matched else ''
                        buy_pos['news_sources'] = ','.join(news_sources) if news_sources else ''
                        buy_pos['news_article_count'] = len(top_articles)

                        validated_buys.append(buy_pos)

                        # Add to daily picks (accepted)
                        all_picks.append({
                            'ticker': ticker,
                            'status': 'ACCEPTED',
                            'conviction': conviction_result['conviction'],
                            'position_size_pct': buy_pos.get('position_size_pct', conviction_result['position_size_pct']),
                            'catalyst': catalyst_type,
                            'catalyst_tier': tier_result['tier'],
                            'tier_name': tier_result['tier_name'],
                            'news_score': news_result['score'],
                            'relative_strength': rs_result['relative_strength'],
                            'vix': vix_result['vix'],
                            'supporting_factors': conviction_result['supporting_factors'],
                            'reasoning': buy_pos.get('reasoning', ''),
                            'rejection_reasons': []
                        })

                        print(f"   ✓ {ticker}: {conviction_result['conviction']} - {rs_result['relative_strength']:+.1f}% RS (Rating: {rs_result['rs_rating']})")
                        print(f"      Catalyst: {tier_result['tier_name']}")
                        print(f"      News: {news_result['score']}/20, RS: {rs_result['relative_strength']:+.1f}% (Rating: {rs_result['rs_rating']}/100), VIX: {vix_result['vix']}")
                        print(f"      Position Size: {conviction_result['position_size_pct']}% ({conviction_result['conviction']})")
                        print(f"      Reasoning: {conviction_result['reasoning']}")
                    else:
                        # Add to daily picks (rejected)
                        all_picks.append({
                            'ticker': ticker,
                            'status': 'REJECTED',
                            'conviction': conviction_result.get('conviction', 'N/A') if 'conviction_result' in locals() else 'N/A',
                            'position_size_pct': 0,
                            'catalyst': catalyst_type,
                            'catalyst_tier': tier_result.get('tier', 'Unknown') if 'tier_result' in locals() else 'Unknown',
                            'tier_name': tier_result.get('tier_name', 'Unknown') if 'tier_result' in locals() else 'Unknown',
                            'news_score': news_result.get('score', 0) if 'news_result' in locals() else 0,
                            'relative_strength': rs_result.get('relative_strength', 0) if 'rs_result' in locals() else 0,
                            'vix': vix_result['vix'],
                            'supporting_factors': conviction_result.get('supporting_factors', 0) if 'conviction_result' in locals() else 0,
                            'reasoning': buy_pos.get('reasoning', ''),
                            'rejection_reasons': rejection_reasons
                        })

                        print(f"   ✗ {ticker}: REJECTED")
                        for reason in rejection_reasons:
                            print(f"      - {reason}")

                except Exception as e:
                    # If validation fails due to error, keep position (don't block on API errors)
                    print(f"   ⚠️ {ticker}: Validation error ({e}) - keeping position with default tier")
                    buy_pos['catalyst_tier'] = 'Tier2'
                    buy_pos['position_size_pct'] = 10.0

                    # CRITICAL: Ensure sector is preserved from screener data or Claude's recommendation
                    if 'sector' not in buy_pos or not buy_pos['sector']:
                        if ticker in screener_lookup:
                            buy_pos['sector'] = screener_lookup[ticker].get('sector', 'Unknown')
                            buy_pos['industry'] = screener_lookup[ticker].get('industry', 'Unknown')
                        else:
                            buy_pos['sector'] = 'Unknown'
                            buy_pos['industry'] = 'Unknown'

                    validated_buys.append(buy_pos)

                    # Add to daily picks for dashboard tracking (ACCEPTED with validation error note)
                    all_picks.append({
                        'ticker': ticker,
                        'status': 'ACCEPTED',
                        'conviction': buy_pos.get('confidence', 'N/A'),  # Use Claude's confidence
                        'position_size_pct': 10.0,
                        'catalyst': catalyst_type,
                        'catalyst_tier': 'Tier2',
                        'tier_name': 'Tier 2 (Default - Validation Error)',
                        'news_score': 0,
                        'relative_strength': 0,
                        'vix': vix_result['vix'],
                        'supporting_factors': 0,
                        'reasoning': buy_pos.get('thesis', 'Validation error - kept with defaults'),
                        'rejection_reasons': []
                    })

            # Replace buy_positions with validated list
            buy_positions = validated_buys
            print(f"   ✓ Validated: {len(validated_buys)} BUY positions passed checks\n")

        # Step 5.6: Enhancement 1.3 + 4.3 - Enforce Sector Concentration Limits
        if buy_positions:
            print("5.6 Enforcing sector concentration limits (Enhancement 1.3 + 4.3)...")

            # Get top 2 leading sectors from screener data (for Phase 4.3 exception)
            leading_sectors_list = sector_rotation.get('leading_sectors', []) if sector_rotation else []

            # Get current portfolio for sector analysis
            accepted_buys, rejected_buys = self.enforce_sector_concentration(
                new_positions=buy_positions,
                current_portfolio=existing_positions + hold_positions,  # Include HOLD positions
                leading_sectors=leading_sectors_list  # PHASE 4.3: Pass leading sectors for exception
            )

            # Log rejections
            if rejected_buys:
                print(f"\n   Sector/Industry rejections:")
                for reject in rejected_buys:
                    print(f"      ✗ {reject['ticker']}: {reject['reason']}")

                    # Track rejected picks for dashboard accountability
                    all_picks.append({
                        'ticker': reject['ticker'],
                        'status': 'REJECTED',
                        'conviction': 'N/A',
                        'position_size_pct': 0,
                        'catalyst': 'Unknown',
                        'catalyst_tier': 'Unknown',
                        'tier_name': 'Unknown',
                        'news_score': 0,
                        'relative_strength': 0,
                        'vix': vix_result.get('vix', 0),
                        'supporting_factors': 0,
                        'reasoning': reject['reason'],
                        'rejection_reasons': [reject['reason']],
                        'sector': reject['sector'],
                        'industry': reject['industry']
                    })

            # Update buy_positions with concentration-filtered list
            buy_positions = accepted_buys
            print(f"   ✓ Final BUY list: {len(buy_positions)} positions (after concentration enforcement)\n")

        # Save daily picks for dashboard visibility (ALWAYS save, even if 0 picks)
        self.save_daily_picks(all_picks, vix_result, macro_result)

        # Step 5.7: Identify positions needing trailing stop orders (Jan 2026 fix)
        # Trailing stops should be placed at market open (EXECUTE), not at 4:30 PM (ANALYZE)
        print("5.7 Identifying positions for trailing stop protection...")
        trailing_stop_positions = []

        for ticker in hold_positions:
            # Get position data
            position = next((p for p in existing_positions if p['ticker'] == ticker), None)
            if not position:
                continue

            entry_price = position.get('entry_price', 0)
            if entry_price <= 0:
                continue

            # Get premarket price
            pm_data = premarket_data.get(ticker, {})
            current_price = pm_data.get('premarket_price', position.get('current_price', entry_price))

            # Calculate current return
            return_pct = ((current_price - entry_price) / entry_price) * 100

            # Check if position qualifies for trailing stop (+10% or more)
            if return_pct >= 10.0:
                # Check if already has an Alpaca trailing stop order
                has_alpaca_order = False
                if self.use_alpaca and self.broker:
                    has_order, order_id, trail_pct = self.broker.has_trailing_stop_order(ticker)
                    has_alpaca_order = has_order

                if not has_alpaca_order:
                    shares = int(position.get('shares', 0))
                    trailing_stop_positions.append({
                        'ticker': ticker,
                        'shares': shares,
                        'entry_price': entry_price,
                        'current_price': current_price,
                        'return_pct': round(return_pct, 1),
                        'trail_percent': 2.0  # 2% trailing stop
                    })
                    print(f"   📤 {ticker}: +{return_pct:.1f}% gain → needs trailing stop (2% trail)")
                else:
                    print(f"   ✓ {ticker}: +{return_pct:.1f}% gain → already has Alpaca trailing stop")

        if trailing_stop_positions:
            print(f"   ✓ {len(trailing_stop_positions)} positions need trailing stop orders at market open")
        else:
            print("   ✓ No positions currently qualify for trailing stop protection")
        print()

        # Step 6: Build pending_positions.json
        print("6. Building pending positions file...")
        pending = {
            'decision_time': datetime.now().isoformat(),
            'hold': hold_positions,
            'exit': exit_positions,
            'buy': buy_positions,
            'trailing_stops': trailing_stop_positions  # NEW: Trailing stops to place at market open
        }

        with open(self.pending_file, 'w') as f:
            json.dump(pending, f, indent=2)
        print("   ✓ Saved to pending_positions.json\n")

        # Step 7: Save response for learning
        print("7. Saving response...")
        self.save_response('go', response)
        print("   ✓ Complete\n")

        print("="*60)
        print("GO COMMAND COMPLETE")
        print("="*60)
        print(f"\n✓ Portfolio Review Complete:")
        print(f"  - HOLD: {len(hold_positions)} positions")
        print(f"  - EXIT: {len(exit_positions)} positions (will close at 9:30 AM)")
        print(f"  - BUY:  {len(buy_positions)} new positions (will enter at 9:30 AM)")
        if trailing_stop_positions:
            print(f"  - TRAILING STOPS: {len(trailing_stop_positions)} positions (Alpaca orders at 9:45 AM)")
        print(f"\n✓ Run 'execute' command at 9:45 AM to execute these decisions\n")

        # Send GO report email
        print("8. Sending GO report email...")
        portfolio = self.load_current_portfolio()
        self.send_go_report_email(hold_positions, exit_positions, buy_positions, portfolio, trailing_stop_positions)

        return True
    
    def execute_execute_command(self):
        """
        Execute EXECUTE command (9:30 AM) - SWING TRADING VERSION

        NEW v5.0 BEHAVIOR:
        1. Load pending decisions (hold/exit/buy)
        2. Load current portfolio
        3. Execute EXITS: Close positions marked for exit
        4. Keep HOLD positions (update prices, increment days_held)
        5. Execute BUYS: Enter new positions
        6. Save updated portfolio and log closed trades
        """

        print("\n" + "="*60)
        print("EXECUTING 'EXECUTE' - POSITION ENTRY/EXIT (Market Open)")
        print("="*60 + "\n")

        # Load pending decisions
        if not self.pending_file.exists():
            print("   ✗ No pending decisions found")
            print("   Run 'go' command first\n")
            return False

        print("1. Loading pending decisions...")
        with open(self.pending_file, 'r') as f:
            pending = json.load(f)

        hold_tickers = pending.get('hold', [])
        exit_decisions = pending.get('exit', [])
        buy_positions = pending.get('buy', [])
        trailing_stop_orders = pending.get('trailing_stops', [])  # NEW: Trailing stops to place

        print(f"   ✓ HOLD: {len(hold_tickers)} positions")
        print(f"   ✓ EXIT: {len(exit_decisions)} positions")
        print(f"   ✓ BUY:  {len(buy_positions)} new positions")
        print(f"   ✓ TRAILING STOPS: {len(trailing_stop_orders)} positions\n")

        # Load current portfolio
        print("2. Loading current portfolio...")
        current_portfolio = self.load_current_portfolio()
        current_positions = current_portfolio.get('positions', [])
        print(f"   ✓ Loaded {len(current_positions)} current positions\n")

        # Process EXITS
        print("3. Processing EXITS...")
        closed_trades = []
        exited_tickers = set()  # Track which tickers were exited (Bug #5 fix)
        if exit_decisions:
            exit_tickers = [e['ticker'] for e in exit_decisions]
            tickers_to_fetch = list(set(exit_tickers + [p['ticker'] for p in current_positions]))
            market_prices = self.fetch_current_prices(tickers_to_fetch)

            for exit_decision in exit_decisions:
                ticker = exit_decision['ticker']
                claude_reason = exit_decision.get('reason', 'Portfolio management decision')
                execution_timing = exit_decision.get('execution_timing', '')

                # Find position in current portfolio
                position = next((p for p in current_positions if p['ticker'] == ticker), None)
                if position:
                    exit_price = market_prices.get(ticker, position.get('current_price', 0))
                    entry_price = position.get('entry_price', 0)
                    price_target = position.get('price_target', entry_price * 1.10)
                    stop_loss = position.get('stop_loss', entry_price * 0.93)

                    # Enhancement 0.1: Gap-aware exit logic
                    # Check if stock gapped significantly (need previous close)
                    previous_close = position.get('current_price', entry_price)  # Yesterday's close
                    gap_analysis = self.analyze_premarket_gap(ticker, exit_price, previous_close)

                    # Bug #2 & #4 fix: Validate exit conditions
                    should_execute_exit = True
                    rejection_reason = None

                    # Enhancement 0.1: Large gap-up to target - DON'T exit yet (BIIB lesson)
                    if (gap_analysis['gap_pct'] >= 5.0 and
                        exit_price >= price_target and
                        not gap_analysis['should_exit_at_open']):
                        should_execute_exit = False
                        rejection_reason = f"Large gap to target ({gap_analysis['gap_pct']:+.1f}%), wait for consolidation"
                        print(f"      ⚠️ {ticker}: {gap_analysis['classification']} detected")
                        print(f"         {gap_analysis['reasoning']}")
                        print(f"         Recommended: {gap_analysis['recommended_action']}")
                        print(f"         → HOLDING instead of exiting (let position consolidate)")

                    # Check if this is a conditional exit (Bug #4)
                    elif gap_analysis['gap_pct'] >= 5.0:
                        # Log gap but don't block exit if stop/other reason
                        print(f"      ℹ️  {ticker}: {gap_analysis['classification']} ({gap_analysis['gap_pct']:+.1f}%)")
                    if execution_timing and ('if price' in execution_timing.lower() or '≥' in execution_timing or '>=' in execution_timing):
                        # Extract price condition if present (e.g., "if price ≥$181.50")
                        print(f"      ⚠️ Conditional exit detected: {execution_timing}")
                        # For now, always check if target/stop conditions are met

                    # Bug #2 fix: Validate exit makes sense given actual price
                    return_pct = ((exit_price - entry_price) / entry_price * 100) if entry_price > 0 else 0

                    # Check if claiming target hit but price below target
                    if 'target' in claude_reason.lower() and exit_price < price_target:
                        should_execute_exit = False
                        rejection_reason = f"Target claimed but price ${exit_price:.2f} < target ${price_target:.2f} ({return_pct:+.1f}% < +10%)"

                    # Check if price is between stop and target (no valid exit reason)
                    elif exit_price > stop_loss and exit_price < price_target:
                        # Only allow if catalyst invalidated or other valid reason
                        if 'catalyst' not in claude_reason.lower() and 'time' not in claude_reason.lower() and 'rotation' not in claude_reason.lower():
                            should_execute_exit = False
                            rejection_reason = f"Price ${exit_price:.2f} between stop ${stop_loss:.2f} and target ${price_target:.2f} - no valid exit reason"

                    if should_execute_exit:
                        # Standardize the exit reason (converts Claude's freeform text to consistent format)
                        standardized_reason = self.standardize_exit_reason(position, exit_price, claude_reason)

                        # v7.2 Stage 3: Execute sell order via Alpaca (if available)
                        alpaca_success, alpaca_msg, order_id = self._execute_alpaca_sell(
                            ticker,
                            position.get('shares', 0),
                            standardized_reason
                        )
                        if alpaca_success:
                            print(f"      ✓ Alpaca: {alpaca_msg} (Order: {order_id})")
                        elif "not available" not in alpaca_msg:
                            # Log Alpaca failures (but don't block the exit if Alpaca fails)
                            print(f"      ⚠️ Alpaca: {alpaca_msg}")
                            print(f"      → Continuing with JSON portfolio tracking")

                        closed_trade = self._close_position(position, exit_price, standardized_reason)
                        closed_trades.append(closed_trade)
                        exited_tickers.add(ticker)  # Track this ticker was exited
                        print(f"   ✓ CLOSED {ticker}: {standardized_reason}")
                    else:
                        print(f"   ✗ REJECTED EXIT for {ticker}: {rejection_reason}")
                        print(f"      → Moved to HOLD instead")
                        # Add to hold list instead
                        if ticker not in hold_tickers:
                            hold_tickers.append(ticker)
                else:
                    print(f"   ⚠️ {ticker} not found in portfolio")
        else:
            print("   No exits\n")

        # Process HOLDS (update prices, increment days)
        print("\n4. Updating HOLD positions...")
        updated_positions = []
        if hold_tickers:
            hold_prices = self.fetch_current_prices(hold_tickers)

            for position in current_positions:
                ticker = position['ticker']
                # Bug #5 fix: Skip tickers that were just exited
                if ticker in exited_tickers:
                    continue  # Don't re-add exited positions
                if ticker in hold_tickers:
                    current_price = hold_prices.get(ticker, position.get('current_price', 0))

                    position['current_price'] = current_price
                    position['days_held'] = position.get('days_held', 0) + 1

                    # Calculate unrealized P&L
                    entry_price = position.get('entry_price', 0)
                    shares = position.get('shares', 0)
                    if entry_price > 0:
                        pnl_pct = ((current_price - entry_price) / entry_price * 100)
                        pnl_dollars = (current_price - entry_price) * shares
                        position['unrealized_gain_pct'] = round(pnl_pct, 2)
                        position['unrealized_gain_dollars'] = round(pnl_dollars, 2)

                    updated_positions.append(position)
                    print(f"   ✓ {ticker}: ${current_price:.2f} (Day {position['days_held']}, {position.get('unrealized_gain_pct', 0):+.1f}%)")
        else:
            print("   No positions to hold\n")

        # Process BUYS
        print("\n5. Entering NEW positions...")
        # Track held positions count BEFORE adding new buys (for accurate reporting)
        held_positions_count = len(updated_positions)

        if buy_positions:
            # Calculate current account value for position sizing (COMPOUND GROWTH)
            STARTING_CAPITAL = 10000.00
            portfolio_value = sum(p.get('position_size', 0) for p in updated_positions)

            # Calculate realized P&L from completed trades
            realized_pl = 0.00
            if self.trades_csv.exists():
                with open(self.trades_csv, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('Trade_ID'):
                            realized_pl += float(row.get('Return_Dollars', 0))

            # Current account value = starting capital + all profits/losses
            current_account_value = STARTING_CAPITAL + realized_pl

            # Cash available = account value - currently invested positions
            cash_available = current_account_value - portfolio_value

            print(f"   Account Value: ${current_account_value:.2f} (Cash: ${cash_available:.2f}, Invested: ${portfolio_value:.2f})")

            buy_tickers = [p['ticker'] for p in buy_positions]
            market_prices = self.fetch_current_prices(buy_tickers)

            # Enhancement 0.1: Fetch previous closes for gap analysis
            # Need to get yesterday's close for all buy candidates
            previous_closes = {}
            for ticker in buy_tickers:
                try:
                    # Fetch 2-day history to get previous close
                    bars = requests.get(
                        f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")}/{datetime.now().strftime("%Y-%m-%d")}',
                        params={'apiKey': POLYGON_API_KEY},
                        timeout=10
                    ).json()
                    if bars.get('results') and len(bars['results']) >= 2:
                        previous_closes[ticker] = bars['results'][-2]['c']  # Previous day close
                except Exception as e:
                    print(f"⚠️ Warning: Failed to fetch previous close for {ticker}: {e}")
                    previous_closes[ticker] = None

            for pos in buy_positions:
                ticker = pos['ticker']
                if ticker in market_prices:
                    entry_price = market_prices[ticker]
                    if not entry_price or entry_price <= 0:
                        print(f"   ⚠️ SKIPPED {ticker}: Invalid entry price ({entry_price})")
                        continue
                    previous_close = previous_closes.get(ticker) or (entry_price * 0.98)  # Fallback estimate

                    # v7.0: Check bid-ask spread to prevent expensive execution
                    spread_check = self.check_bid_ask_spread(ticker)
                    if spread_check['should_skip']:
                        print(f"   ⚠️ SKIPPED {ticker}: Spread too wide ({spread_check['spread_pct']:.2%}) - would erode edge")
                        print(f"      Bid: ${spread_check['bid']:.2f}, Ask: ${spread_check['ask']:.2f}, Mid: ${spread_check['mid_price']:.2f}")
                        print(f"      Illiquid stock - market order could be costly")
                        continue  # Skip this entry

                    # v7.1: Store bid/ask for slippage tracking (execution cost validation)
                    entry_bid = spread_check.get('bid', 0)
                    entry_ask = spread_check.get('ask', 0)
                    entry_mid_price = spread_check.get('mid_price', entry_price)
                    entry_spread_pct = spread_check.get('spread_pct', 0)

                    # Enhancement 0.1: Gap-aware entry logic
                    gap_analysis = self.analyze_premarket_gap(ticker, entry_price, previous_close)

                    # Check if we should skip entry due to large gap
                    if not gap_analysis['should_enter_at_open']:
                        print(f"   ⚠️ SKIPPED {ticker}: {gap_analysis['classification']} detected ({gap_analysis['gap_pct']:+.1f}%)")
                        print(f"      {gap_analysis['reasoning']}")
                        print(f"      Recommended: {gap_analysis['recommended_action']}")
                        print(f"      → Will re-check at 10:15 AM (run 'python agent_v5.5.py recheck')")

                        # Save to skipped_for_gap.json for 10:15 AM recheck
                        skipped_file = self.project_dir / 'skipped_for_gap.json'
                        skipped_stocks = []
                        if skipped_file.exists():
                            try:
                                with open(skipped_file) as f:
                                    skipped_data = json.load(f)
                                    # Only keep today's skipped stocks
                                    today = datetime.now().strftime('%Y-%m-%d')
                                    if skipped_data.get('date') == today:
                                        skipped_stocks = skipped_data.get('stocks', [])
                            except:
                                pass

                        skipped_stocks.append({
                            'ticker': ticker,
                            'original_entry_price': entry_price,
                            'previous_close': previous_close,
                            'gap_pct': gap_analysis['gap_pct'],
                            'classification': gap_analysis['classification'],
                            'position_data': pos,  # Full position data for entry
                            'skipped_at': datetime.now().strftime('%H:%M:%S')
                        })

                        with open(skipped_file, 'w') as f:
                            json.dump({
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'stocks': skipped_stocks
                            }, f, indent=2, default=str)

                        continue  # Skip this entry

                    # Log gap info for awareness
                    if abs(gap_analysis['gap_pct']) >= 2.0:
                        print(f"   ℹ️  {ticker}: {gap_analysis['classification']} ({gap_analysis['gap_pct']:+.1f}%) - {gap_analysis['entry_strategy']}")

                    # COMPOUND GROWTH: Calculate position size based on CURRENT account value
                    position_size_pct = pos.get('position_size_pct', 10.0)
                    position_size_dollars = round((position_size_pct / 100) * current_account_value, 2)

                    # Ensure we don't exceed available cash
                    if position_size_dollars > cash_available:
                        position_size_dollars = round(cash_available, 2)
                        print(f"   ⚠️ {ticker}: Reduced size to available cash ${cash_available:.2f}")

                    # Enhancement 1.2: Calculate dynamic profit target based on catalyst
                    catalyst_tier = pos.get('catalyst_tier', 'Tier2')
                    catalyst_type = pos.get('catalyst', 'Unknown')
                    catalyst_details = pos.get('catalyst_details', {})

                    target_info = self.get_dynamic_profit_target(catalyst_tier, catalyst_type, catalyst_details)
                    dynamic_target_pct = target_info['target_pct']
                    target_rationale = target_info['rationale']

                    pos['entry_price'] = entry_price
                    pos['current_price'] = entry_price
                    pos['entry_date'] = datetime.now().strftime('%Y-%m-%d')
                    pos['days_held'] = 0
                    pos['position_size'] = position_size_dollars  # Store actual dollar amount
                    pos['shares'] = position_size_dollars / entry_price

                    # v7.1: Calculate slippage (execution cost beyond spread)
                    # Slippage = (fill_price - mid_price) / mid_price * 10000 bps
                    # Positive = paid more than mid, negative = paid less than mid
                    if entry_mid_price is not None and entry_mid_price > 0:
                        slippage_bps = ((entry_price - entry_mid_price) / entry_mid_price) * 10000
                        pos['entry_bid'] = entry_bid
                        pos['entry_ask'] = entry_ask
                        pos['entry_mid_price'] = entry_mid_price
                        pos['entry_spread_pct'] = entry_spread_pct
                        pos['slippage_bps'] = round(slippage_bps, 2)
                    else:
                        # Fallback if mid_price unavailable
                        pos['entry_bid'] = 0
                        pos['entry_ask'] = 0
                        pos['entry_mid_price'] = entry_price
                        pos['entry_spread_pct'] = 0
                        pos['slippage_bps'] = 0

                    # v7.0: ATR-based stops (2.5x ATR, capped at -7%)
                    atr = self.calculate_atr(ticker, period=14)
                    if atr and atr > 0:
                        # Stop = entry - (2.5 * ATR), but not wider than -7%
                        atr_stop_distance = atr * 2.5
                        atr_stop = entry_price - atr_stop_distance
                        max_stop = entry_price * 0.93  # -7% cap for safety
                        pos['stop_loss'] = round(max(atr_stop, max_stop), 2)  # Use tighter of the two
                        stop_pct = ((pos['stop_loss'] - entry_price) / entry_price) * 100
                        pos['stop_pct'] = round(stop_pct, 2)  # v7.1.1 - Track stop distance for distribution analysis
                        print(f"      Stop: ${pos['stop_loss']:.2f} ({stop_pct:.1f}%) - ATR-based (ATR=${atr:.2f}, 2.5x=${atr_stop_distance:.2f})")
                    else:
                        # Fallback to -7% if ATR unavailable
                        pos['stop_loss'] = round(entry_price * 0.93, 2)
                        pos['stop_pct'] = -7.0  # v7.1.1 - Fixed stop percentage
                        print(f"      Stop: ${pos['stop_loss']:.2f} (-7.0%) - Fixed (ATR unavailable)")

                    pos['price_target'] = round(entry_price * (1 + dynamic_target_pct/100), 2)  # Dynamic target
                    pos['target_pct'] = dynamic_target_pct  # Store for reference
                    pos['target_rationale'] = target_rationale
                    pos['stretch_target'] = target_info.get('stretch_target')
                    pos['expected_hold_days'] = target_info.get('expected_hold_days', '5-7 days')
                    pos['unrealized_gain_pct'] = 0.0
                    pos['unrealized_gain_dollars'] = 0.0

                    # Update cash available for next position
                    cash_available -= position_size_dollars

                    # v7.2 Stage 3: Execute buy order via Alpaca (if available)
                    alpaca_success, alpaca_msg, order_id, actual_shares = self._execute_alpaca_buy(
                        ticker,
                        position_size_dollars,
                        entry_price
                    )
                    if alpaca_success:
                        print(f"      ✓ Alpaca: {alpaca_msg} (Order: {order_id})")
                        # Update shares if Alpaca returned actual quantity
                        if actual_shares > 0:
                            pos['shares'] = actual_shares
                    elif "not available" not in alpaca_msg:
                        # Log Alpaca failures (but don't block the entry if Alpaca fails)
                        print(f"      ⚠️ Alpaca: {alpaca_msg}")
                        print(f"      → Continuing with JSON portfolio tracking")

                    updated_positions.append(pos)
                    print(f"   ✓ ENTERED {ticker}: ${entry_price:.2f}, {pos['shares']:.2f} shares (${position_size_dollars:.2f} = {position_size_pct}% of ${current_account_value:.2f})")
                    print(f"      Target: +{dynamic_target_pct}% (${pos['price_target']:.2f}) - {target_rationale}")
                else:
                    print(f"   ⚠️ {ticker}: Failed to fetch price")
        else:
            print("   No new entries\n")

        # Save updated portfolio
        print("\n6. Saving updated portfolio...")
        portfolio = {
            'positions': updated_positions,
            'total_positions': len(updated_positions),
            'portfolio_value': sum(p.get('position_size', 100) for p in updated_positions),
            'last_updated': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'portfolio_status': f"Active - {len(updated_positions)} positions"
        }

        with open(self.portfolio_file, 'w') as f:
            json.dump(portfolio, f, indent=2)
        print("   ✓ Portfolio saved\n")

        # Log closed trades to CSV
        if closed_trades:
            print("7. Logging closed trades to CSV...")
            for trade in closed_trades:
                self._log_trade_to_csv(trade)
            print(f"   ✓ Logged {len(closed_trades)} closed trades\n")

        # Update account status
        print("8. Updating account status...")
        self.update_account_status()
        print("   ✓ Account status updated\n")

        # Create daily activity summary (always update, even if no trades)
        print("9. Creating daily activity summary...")
        self.create_daily_activity_summary(closed_trades)
        print()

        # Step 10: Place Alpaca trailing stop orders for qualifying positions
        print("10. Placing trailing stop orders...")
        trailing_stops_placed = 0
        if trailing_stop_orders and self.use_alpaca and self.broker:
            for ts_order in trailing_stop_orders:
                ticker = ts_order['ticker']
                shares = ts_order['shares']
                trail_percent = ts_order.get('trail_percent', 2.0)
                return_pct = ts_order.get('return_pct', 0)

                # Verify position still exists (wasn't exited)
                if ticker in exited_tickers:
                    print(f"   ⚠️ {ticker}: Skipping - position was exited")
                    continue

                # Place the trailing stop order with Alpaca
                success, msg, order_id = self.broker.place_trailing_stop_order(
                    ticker=ticker,
                    qty=shares,
                    trail_percent=trail_percent
                )

                if success:
                    trailing_stops_placed += 1
                    print(f"   ✓ {ticker}: Trailing stop placed ({trail_percent}% trail) - protecting +{return_pct:.1f}% gain")

                    # Update portfolio position to reflect trailing stop is active
                    for pos in updated_positions:
                        if pos['ticker'] == ticker:
                            pos['trailing_stop_active'] = True
                            pos['alpaca_trailing_order_id'] = order_id
                            break
                else:
                    print(f"   ✗ {ticker}: Failed to place trailing stop - {msg}")

            print(f"   ✓ {trailing_stops_placed}/{len(trailing_stop_orders)} trailing stops placed")

            # Re-save portfolio with trailing stop updates
            if trailing_stops_placed > 0:
                updated_portfolio = {
                    'account_value': portfolio_value,
                    'cash_available': cash_available,
                    'positions': updated_positions,
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                with open(self.portfolio_file, 'w') as f:
                    json.dump(updated_portfolio, f, indent=2)
        else:
            print("   ✓ No trailing stop orders to place")
        print()

        # Save execute response for dashboard tracking
        print("11. Saving execute summary...")
        execute_summary = {
            "command": "execute",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "closed": len(closed_trades),
                "holding": held_positions_count,
                "entered": len(updated_positions) - held_positions_count,
                "total_active": len(updated_positions),
                "trailing_stops_placed": trailing_stops_placed
            },
            "closed_trades": [
                {
                    "ticker": t.get("ticker"),
                    "exit_price": t.get("exit_price", 0),
                    "pnl_pct": t.get("pnl_percent", 0),
                    "reason": t.get("exit_reason", "Unknown")
                }
                for t in closed_trades
            ],
            "new_entries": [{"ticker": b.get("ticker"), "entry_price": b.get("entry_price")} for b in buy_positions if b.get("entry_price")],
            "trailing_stops": [{"ticker": ts.get("ticker"), "return_pct": ts.get("return_pct")} for ts in trailing_stop_orders]
        }
        self.save_response("execute", execute_summary)
        print("   ✓ Execute summary saved\n")

        # Clean up pending file
        self.pending_file.unlink()

        print("="*60)
        print("EXECUTE COMMAND COMPLETE")
        print("="*60)
        print(f"\n✓ Portfolio Updated:")
        print(f"  - Closed: {len(closed_trades)} positions")
        print(f"  - Holding: {held_positions_count} positions")
        print(f"  - Entered: {len(updated_positions) - held_positions_count} new positions")
        print(f"  - Total Active: {len(updated_positions)} positions")
        if trailing_stops_placed > 0:
            print(f"  - Trailing Stops: {trailing_stops_placed} Alpaca orders placed (real-time protection)")
        print()

        return True

    def save_daily_picks(self, all_picks, vix_result, macro_result):
        """
        Save daily picks (all opportunities analyzed) for admin dashboard visibility
        Shows what Claude looked at, what passed/failed, and why
        """
        et_tz = pytz.timezone('America/New_York')
        today = datetime.now(et_tz).strftime('%Y-%m-%d')

        # Sort picks: ACCEPTED first (by conviction), then REJECTED, then SKIPPED
        accepted = [p for p in all_picks if p['status'] == 'ACCEPTED']
        rejected = [p for p in all_picks if p['status'] == 'REJECTED']
        skipped = [p for p in all_picks if p['status'] == 'SKIPPED']

        # Sort accepted by conviction level (HIGH > MEDIUM-HIGH > MEDIUM)
        conviction_order = {'HIGH': 3, 'MEDIUM-HIGH': 2, 'MEDIUM': 1, 'SKIP': 0, 'N/A': 0}
        accepted_sorted = sorted(accepted, key=lambda x: (
            conviction_order.get(x['conviction'], 0),
            x['news_score'],
            x['relative_strength']
        ), reverse=True)

        # Sort rejected by tier (Tier1 rejected are more noteworthy than Tier3)
        tier_order = {'Tier1': 3, 'Tier2': 2, 'Tier3': 1, 'Unknown': 0}
        rejected_sorted = sorted(rejected, key=lambda x: (
            tier_order.get(x['catalyst_tier'], 0),
            x['news_score']
        ), reverse=True)

        # Sort skipped by tier (for visibility)
        skipped_sorted = sorted(skipped, key=lambda x: (
            tier_order.get(x['catalyst_tier'], 0),
            x['relative_strength']
        ), reverse=True)

        daily_picks = {
            'date': today,
            'time': datetime.now(et_tz).strftime('%H:%M:%S ET'),
            'market_conditions': {
                'vix': vix_result['vix'],
                'regime': vix_result['regime'],
                'macro_event': macro_result.get('event_type') or 'None',
                'macro_blackout': macro_result['is_blackout']
            },
            'summary': {
                'total_analyzed': len(all_picks),
                'accepted': len(accepted),
                'rejected': len(rejected),
                'skipped': len(skipped),
                'high_conviction': len([p for p in accepted if p['conviction'] == 'HIGH']),
                'medium_high_conviction': len([p for p in accepted if p['conviction'] == 'MEDIUM-HIGH']),
                'medium_conviction': len([p for p in accepted if p['conviction'] == 'MEDIUM'])
            },
            'picks': accepted_sorted + rejected_sorted + skipped_sorted
        }

        # Save to dashboard_data directory
        daily_picks_file = self.project_dir / 'dashboard_data' / 'daily_picks.json'
        daily_picks_file.parent.mkdir(parents=True, exist_ok=True)

        with open(daily_picks_file, 'w') as f:
            json.dump(daily_picks, f, indent=2)

        print(f"   ✓ Saved daily picks: {len(accepted)} accepted, {len(rejected)} rejected, {len(skipped)} skipped (portfolio full)")

    def create_daily_activity_summary(self, closed_trades):
        """
        Create daily activity summary for dashboard
        Shows ALL trades closed today (by exit_date), not just from this execution

        This ensures "Today's Activity" shows complete picture:
        - Trades closed in morning EXECUTE command
        - Trades closed in evening ANALYZE command
        """

        # Get current portfolio to see what's still open
        open_positions = []
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                portfolio = json.load(f)
                open_positions = portfolio.get('positions', [])

        # Read ALL trades from CSV and filter by today's exit date
        # Use Eastern Time for consistency with trading hours
        et_tz = pytz.timezone('America/New_York')
        today = datetime.now(et_tz).strftime('%Y-%m-%d')
        all_trades_today = []

        if self.trades_csv.exists():
            import csv
            with open(self.trades_csv, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Exit_Date') == today:
                        # Convert CSV row to trade dict format
                        all_trades_today.append({
                            'ticker': row['Ticker'],
                            'entry_date': row['Entry_Date'],
                            'exit_date': row['Exit_Date'],
                            'entry_price': float(row['Entry_Price']),
                            'exit_price': float(row['Exit_Price']),
                            'shares': float(row['Shares']),
                            'hold_days': int(row['Hold_Days']),
                            'return_percent': float(row['Return_Percent']),
                            'return_dollars': float(row['Return_Dollars']),
                            'exit_reason': row['Exit_Reason'],
                            'catalyst_type': row['Catalyst_Type'],
                            'thesis': row['Thesis']
                        })

        # Calculate summary stats from ALL today's trades
        total_closed = len(all_trades_today)
        winners = [t for t in all_trades_today if t['return_percent'] > 0]
        losers = [t for t in all_trades_today if t['return_percent'] <= 0]
        total_pl_dollars = sum(t['return_dollars'] for t in all_trades_today)

        # Create activity summary
        activity = {
            'date': today,
            'time': datetime.now(et_tz).strftime('%H:%M:%S ET'),
            'summary': {
                'positions_closed': total_closed,
                'winners': len(winners),
                'losers': len(losers),
                'total_pl_dollars': round(total_pl_dollars, 2),
                'open_positions': len(open_positions)
            },
            'closed_today': [
                {
                    'ticker': t['ticker'],
                    'entry_date': t['entry_date'],
                    'exit_date': t['exit_date'],
                    'entry_price': t['entry_price'],
                    'exit_price': t['exit_price'],
                    'shares': t['shares'],
                    'hold_days': t['hold_days'],
                    'return_percent': round(t['return_percent'], 2),
                    'return_dollars': round(t['return_dollars'], 2),
                    'exit_reason': t['exit_reason'],
                    'catalyst': t['catalyst_type'],
                    'thesis': t['thesis']
                }
                for t in all_trades_today
            ]
        }

        # Save to file
        with open(self.daily_activity_file, 'w') as f:
            json.dump(activity, f, indent=2)

        print(f"   ✓ Created daily activity summary: {total_closed} closed, ${total_pl_dollars:.2f} P&L")

    def execute_recheck_command(self):
        """
        Execute RECHECK command (10:15 AM)

        Re-evaluates stocks that were skipped at 9:45 AM due to gap-up.
        If the gap has settled (price pulled back or reduced), execute entry.

        Research basis: "Wait 30min for pullback to VWAP" strategy for 2-5% gaps.

        Returns:
            True: Command completed successfully (including when nothing to recheck)
            False: Command failed due to an actual error
        """
        print("\n" + "="*60)
        print("RECHECK COMMAND - Gap Settlement Re-evaluation")
        print("="*60)

        # Load skipped stocks
        skipped_file = self.project_dir / 'skipped_for_gap.json'
        if not skipped_file.exists():
            print("\n✓ No skipped stocks file found.")
            print("   This is normal - no stocks were skipped for gaps during EXECUTE.")
            print("   RECHECK completed successfully (nothing to do).")
            return True  # SUCCESS - nothing to recheck is a valid outcome

        with open(skipped_file) as f:
            skipped_data = json.load(f)

        today = datetime.now().strftime('%Y-%m-%d')
        if skipped_data.get('date') != today:
            print(f"\n✓ Skipped stocks file is from {skipped_data.get('date')}, not today ({today}).")
            print("   This is normal - the file is stale from a previous day.")
            print("   RECHECK completed successfully (nothing to do today).")
            return True  # SUCCESS - nothing to recheck today is a valid outcome

        stocks = skipped_data.get('stocks', [])
        if not stocks:
            print("\n✓ No stocks were skipped for gaps today.")
            return True

        print(f"\n📋 Found {len(stocks)} stock(s) skipped at 9:45 AM for gap re-evaluation:\n")

        # Load current portfolio
        portfolio = self.load_portfolio()
        current_account_value = portfolio.get('account_value', 10000)
        cash_available = portfolio.get('cash_available', current_account_value)
        positions = portfolio.get('positions', [])

        entered_count = 0
        still_skipped = []
        entered_positions = []  # Track for dashboard

        for stock in stocks:
            ticker = stock['ticker']
            original_gap = stock['gap_pct']
            previous_close = stock['previous_close']
            original_price = stock['original_entry_price']
            pos_data = stock['position_data']

            print(f"   Checking {ticker} (was {original_gap:+.1f}% gap at 9:45 AM)...")

            # Get current price
            current_price = self.get_current_price(ticker)
            if not current_price:
                print(f"      ❌ Could not get current price for {ticker}")
                still_skipped.append(stock)
                continue

            # Calculate current gap from previous close
            current_gap = ((current_price - previous_close) / previous_close) * 100

            # Calculate price change since 9:45 AM
            price_change_since_945 = ((current_price - original_price) / original_price) * 100

            print(f"      Previous close: ${previous_close:.2f}")
            print(f"      9:45 AM price:  ${original_price:.2f} ({original_gap:+.1f}% gap)")
            print(f"      Current price:  ${current_price:.2f} ({current_gap:+.1f}% from close)")
            print(f"      Change since 9:45: {price_change_since_945:+.1f}%")

            # Decision logic for gap settlement
            # Enter if:
            # 1. Gap has reduced to <2% (normal entry territory), OR
            # 2. Price has pulled back at least 1% from 9:45 AM price (pullback entry), OR
            # 3. Current gap is <3% and original was 2-5% range (gap settling)
            should_enter = False
            entry_reason = ""

            if current_gap < 2.0:
                should_enter = True
                entry_reason = f"Gap settled to {current_gap:+.1f}% (below 2% threshold)"
            elif price_change_since_945 <= -1.0:
                should_enter = True
                entry_reason = f"Pullback of {price_change_since_945:.1f}% from 9:45 AM price"
            elif original_gap <= 5.0 and current_gap < 3.0:
                should_enter = True
                entry_reason = f"Gap reduced from {original_gap:+.1f}% to {current_gap:+.1f}%"

            if should_enter:
                print(f"      ✓ GAP SETTLED: {entry_reason}")
                print(f"      → Executing entry at ${current_price:.2f}...")

                # Calculate position size
                position_size_pct = pos_data.get('position_size_pct', 10.0)
                position_size_dollars = round((position_size_pct / 100) * current_account_value, 2)

                if position_size_dollars > cash_available:
                    position_size_dollars = round(cash_available, 2)
                    print(f"      ⚠️ Reduced size to available cash ${cash_available:.2f}")

                # Create position - copy ALL fields from original for learning engine
                new_position = {
                    'ticker': ticker,
                    'entry_price': current_price,
                    'current_price': current_price,
                    'entry_date': datetime.now().strftime('%Y-%m-%d'),
                    'days_held': 0,
                    'position_size': position_size_dollars,
                    'shares': position_size_dollars / current_price,
                    'position_size_pct': position_size_pct,
                    # RECHECK-specific fields
                    'entry_type': 'RECHECK',  # Mark as recheck entry for learning
                    'original_gap': original_gap,
                    'entry_gap': current_gap,
                    'gap_settlement_reason': entry_reason,
                    # Copy ALL learning-relevant fields from original position
                    'catalyst': pos_data.get('catalyst', 'Unknown'),
                    'catalyst_tier': pos_data.get('catalyst_tier', 'Tier2'),
                    'catalyst_details': pos_data.get('catalyst_details', {}),
                    'catalyst_age_days': pos_data.get('catalyst_age_days', 0),
                    'conviction': pos_data.get('conviction', 'Medium'),
                    'conviction_level': pos_data.get('conviction_level', 'MEDIUM'),
                    'supporting_factors': pos_data.get('supporting_factors', 0),
                    'sector': pos_data.get('sector', 'Unknown'),
                    'thesis': pos_data.get('thesis', ''),
                    'technical_score': pos_data.get('technical_score', 0),
                    'technical_sma50': pos_data.get('technical_sma50', 0.0),
                    'technical_ema5': pos_data.get('technical_ema5', 0.0),
                    'technical_ema20': pos_data.get('technical_ema20', 0.0),
                    'technical_adx': pos_data.get('technical_adx', 0.0),
                    'technical_volume_ratio': pos_data.get('technical_volume_ratio', 0.0),
                    'relative_strength': pos_data.get('relative_strength', 0.0),
                    'stock_return_3m': pos_data.get('stock_return_3m', 0.0),
                    'sector_etf': pos_data.get('sector_etf', 'Unknown'),
                    'news_validation_score': pos_data.get('news_validation_score', 0),
                    'keywords_matched': pos_data.get('keywords_matched', ''),
                    'news_sources': pos_data.get('news_sources', ''),
                    'news_article_count': pos_data.get('news_article_count', 0),
                    'vix_at_entry': pos_data.get('vix_at_entry', 0.0),
                    'market_regime': pos_data.get('market_regime', 'Unknown'),
                    'macro_event_near': pos_data.get('macro_event_near', 'None'),
                    'volume_quality': pos_data.get('volume_quality', ''),
                    'volume_trending_up': pos_data.get('volume_trending_up', False),
                }

                # Set stop loss (simple 5% for recheck entries)
                new_position['stop_loss'] = round(current_price * 0.95, 2)

                # Set profit target
                catalyst_tier = pos_data.get('catalyst_tier', 'Tier2')
                if catalyst_tier == 'Tier1':
                    new_position['profit_target'] = round(current_price * 1.08, 2)
                else:
                    new_position['profit_target'] = round(current_price * 1.05, 2)

                positions.append(new_position)
                cash_available -= position_size_dollars
                entered_count += 1
                entered_positions.append(new_position)  # Track for dashboard

                print(f"      ✓ ENTERED: {new_position['shares']:.2f} shares @ ${current_price:.2f}")
                print(f"        Stop: ${new_position['stop_loss']:.2f}, Target: ${new_position['profit_target']:.2f}")
            else:
                print(f"      ✗ Gap NOT settled: still {current_gap:+.1f}% (need <2% or pullback)")
                print(f"        Skipping - will not enter today")
                still_skipped.append({**stock, 'final_gap': current_gap})

        # Save updated portfolio
        if entered_count > 0:
            portfolio['positions'] = positions
            portfolio['cash_available'] = cash_available
            self.save_portfolio(portfolio)
            print(f"\n✓ Portfolio updated with {entered_count} new position(s)")

        # Clear the skipped file (processed for today)
        skipped_file.unlink()
        print(f"\n✓ Cleared skipped stocks file")

        # Summary
        print(f"\n{'='*60}")
        print(f"RECHECK SUMMARY")
        print(f"{'='*60}")
        print(f"   Stocks checked:  {len(stocks)}")
        print(f"   Entered:         {entered_count}")
        print(f"   Still skipped:   {len(still_skipped)}")

        if still_skipped:
            print(f"\n   Stocks not entered (gap didn't settle):")
            for s in still_skipped:
                print(f"      - {s['ticker']}: {s.get('final_gap', s['gap_pct']):+.1f}% gap")

        # Save RECHECK response for dashboard (shows in EXECUTE modal)
        recheck_summary = {
            "command": "recheck",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "stocks_checked": len(stocks),
                "entered": entered_count,
                "still_skipped": len(still_skipped),
            },
            "new_entries": [
                {
                    "ticker": p.get("ticker"),
                    "entry_price": p.get("entry_price"),
                    "original_gap": p.get("original_gap"),
                    "entry_gap": p.get("entry_gap"),
                    "settlement_reason": p.get("gap_settlement_reason")
                }
                for p in entered_positions
            ],
            "skipped_stocks": [
                {
                    "ticker": s.get("ticker"),
                    "original_gap": s.get("gap_pct"),
                    "final_gap": s.get("final_gap", s.get("gap_pct"))
                }
                for s in still_skipped
            ]
        }
        self.save_response("recheck", recheck_summary)
        print(f"\n   ✓ Recheck summary saved for dashboard")

        return True

    def execute_analyze_command(self):
        """
        Execute ANALYZE command (4:30 PM)

        SAME AS v4.2 - No changes needed:
        - Fetch current prices (Alpha Vantage)
        - Update portfolio with latest P&L
        - Check stop losses and profit targets
        - Close positions that hit exits
        - Log closed trades to CSV
        - Update account status
        - Call Claude for analysis and commentary
        - Create daily activity summary for dashboard
        """

        print("\n" + "="*60)
        print("EXECUTING 'ANALYZE' COMMAND - EVENING PERFORMANCE UPDATE")
        print("="*60 + "\n")

        # Update prices and check exits
        closed_trades = self.update_portfolio_prices_and_check_exits()

        # ALWAYS create daily activity summary (picks up ALL trades closed today from CSV)
        print("\n4. Creating daily activity summary...")
        self.create_daily_activity_summary(closed_trades)
        print()

        # Call Claude for analysis
        print("\n" + "="*60)
        print("CALLING CLAUDE FOR ANALYSIS")
        print("="*60 + "\n")

        print("1. Loading optimized context...")
        context = self.load_optimized_context('analyze')
        print("   ✓ Context loaded\n")

        print("2. Calling Claude API for performance analysis...")

        # AI FAILOVER: Graceful degradation if Claude API fails
        try:
            response = self.call_claude_api('analyze', context)
            print("   ✓ Response received\n")

            print("3. Saving response...")
            self.save_response('analyze', response)
            print("   ✓ Complete\n")

        except Exception as e:
            # ANALYZE command failure - log but continue (not critical)
            error_type = type(e).__name__
            error_msg = str(e)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            print(f"\n{'='*70}")
            print(f"⚠️ CLAUDE API FAILURE - ANALYZE COMMAND")
            print(f"{'='*70}")
            print(f"   Error Type: {error_type}")
            print(f"   Error Message: {error_msg}")
            print(f"   Timestamp: {timestamp}")
            print(f"\n   IMPACT: Daily analysis not generated")
            print(f"   - All position exits/holds already processed")
            print(f"   - Trade logging completed successfully")
            print(f"   - Only missing: Claude's commentary on performance")
            print(f"{'='*70}\n")

            # Log the failure
            log_entry = {
                'timestamp': timestamp,
                'command': 'analyze',
                'error_type': error_type,
                'error_message': error_msg,
                'degraded_mode': True,
                'action_taken': 'Skipped Claude analysis, core operations completed'
            }

            log_file = self.project_dir / 'logs' / 'claude_api_failures.json'
            log_file.parent.mkdir(exist_ok=True)

            existing_logs = []
            if log_file.exists():
                try:
                    existing_logs = json.loads(log_file.read_text())
                except Exception as e:
                    print(f"⚠️ Warning: Failed to load existing failure logs: {e}")
                    pass

            existing_logs.append(log_entry)
            log_file.write_text(json.dumps(existing_logs, indent=2))

            print("   ℹ️ ANALYZE gracefully skipped - all critical operations complete\n")

        print("="*60)
        print("ANALYZE COMMAND COMPLETE")
        print("="*60)
        if closed_trades:
            print(f"\n✓ {len(closed_trades)} positions closed and logged to CSV")
        print()

        return True

# =====================================================================
# MAIN EXECUTION
# =====================================================================

def main():
    """Main execution"""
    
    if len(sys.argv) < 2:
        print("\nUsage: python agent.py [go|execute|recheck|analyze|learn]")
        print("\nCommands:")
        print("  go       - Select 10 stocks (8:45 AM)")
        print("  execute  - Enter positions (9:45 AM)")
        print("  recheck  - Re-evaluate gap-skipped stocks (10:15 AM)")
        print("  analyze  - Update & close positions (4:30 PM)")
        print("  learn    - Analyze performance metrics (Phase 5)")
        sys.exit(1)

    command = sys.argv[1].lower()

    print(f"\n{'='*60}")
    print(f"Paper Trading Lab Agent v8.0 (Alpaca Integration)")
    et_tz = pytz.timezone('America/New_York')
    print(f"Time: {datetime.now(et_tz).strftime('%Y-%m-%d %H:%M:%S ET')}")
    print(f"{'='*60}")

    agent = TradingAgent()

    try:
        if command == 'go':
            success = agent.execute_go_command()
        elif command == 'execute':
            success = agent.execute_execute_command()
        elif command == 'recheck':
            success = agent.execute_recheck_command()
        elif command == 'analyze':
            success = agent.execute_analyze_command()
        elif command == 'learn':
            # Phase 5: Learning analysis
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            print(f"\nAnalyzing performance over last {days} days...\n")

            analysis = agent.analyze_performance_metrics(days=days)

            if 'error' in analysis:
                print(f"⚠️ {analysis['error']}\n")
                success = False
            else:
                # Print summary
                print("="*60)
                print(f"PERFORMANCE ANALYSIS - Last {days} Days")
                print("="*60)
                print(f"\nOverall Performance:")
                print(f"  Total Trades: {analysis['total_trades']}")
                print(f"  Win Rate: {analysis['win_rate']:.1f}%")
                print(f"  Avg Return: {analysis['avg_return_pct']:.2f}%")
                print(f"  Total Return: {analysis['total_return_pct']:.2f}%")
                print(f"  Avg Hold Days: {analysis['avg_hold_days']:.1f}")

                # Conviction accuracy
                if analysis['conviction_accuracy']:
                    print(f"\nConviction Accuracy:")
                    for conviction, stats in analysis['conviction_accuracy'].items():
                        print(f"  {conviction}: {stats['count']} trades, {stats['win_rate']:.1f}% win rate, {stats['avg_return']:.2f}% avg")

                # Tier performance
                if analysis['tier_performance']:
                    print(f"\nCatalyst Tier Performance:")
                    for tier, stats in analysis['tier_performance'].items():
                        print(f"  {tier}: {stats['count']} trades, {stats['win_rate']:.1f}% win rate, {stats['avg_return']:.2f}% avg")

                # VIX regime
                if analysis['vix_regime_performance']:
                    print(f"\nVIX Regime Performance:")
                    for regime, stats in analysis['vix_regime_performance'].items():
                        print(f"  {regime}: {stats['count']} trades, {stats['win_rate']:.1f}% win rate, {stats['avg_return']:.2f}% avg")

                # Recommendations
                if analysis['recommendations']:
                    print(f"\nRecommendations:")
                    for rec in analysis['recommendations']:
                        print(f"  {rec}")

                # Save analysis
                agent.save_learning_analysis(analysis, 'monthly')

                print("\n" + "="*60)
                print("LEARNING ANALYSIS COMPLETE")
                print("="*60 + "\n")
                success = True
        else:
            print(f"\nERROR: Unknown command '{command}'")
            print("Valid commands: go, execute, analyze, learn")
            sys.exit(1)
        
        if success:
            print("="*60)
            print(f"{command.upper()} COMMAND COMPLETED SUCCESSFULLY")
            print("="*60 + "\n")
        else:
            print("="*60)
            print(f"{command.upper()} COMMAND FAILED")
            print("="*60 + "\n")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"FATAL ERROR: {e}")
        print("="*60)
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()