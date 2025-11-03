#!/usr/bin/env python3
"""
Paper Trading Lab - Agent v5.6.0 - COMPOUND GROWTH ENABLED
SWING TRADING SYSTEM WITH INTELLIGENT LEARNING & OPTIMIZATION

MAJOR IMPROVEMENTS FROM v4.3:
1. GO command reviews EXISTING portfolio with 15-min delayed premarket data
2. Enforces swing trading rules: 2-day minimum hold, proper exit criteria
3. HOLD/EXIT/BUY decision logic instead of daily portfolio rebuild
4. Leverages Polygon.io 15-min delayed data for premarket gap analysis
5. True swing trading: positions held 3-7 days unless stops/targets hit

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
  - **Relative Strength Impact**: RS ≥3% vs RS <3% comparison
  - **Macro Event Impact**: Performance with/without nearby macro events
- Automated recommendations system:
  - Detects if HIGH conviction underperforming MEDIUM
  - Flags trades entered at VIX >30 (SHUTDOWN violations)
  - Identifies sector laggards outperforming leaders (RS validation)
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
  - Auto-rejects if RS <3% (sector laggards filtered out)
  - Calculates conviction level based on all factors
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
  - FOMC: 2 days before → 1 day after (4-day blackout)
  - CPI/NFP/PCE: 1 day before → day of (2-day blackout)
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
from datetime import datetime
from pathlib import Path
import traceback
import pytz

# Configuration
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
ALPHAVANTAGE_API_KEY = os.environ.get('ALPHAVANTAGE_API_KEY', '')
POLYGON_API_KEY = os.environ.get('POLYGON_API_KEY', '')
CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages'
CLAUDE_MODEL = 'claude-sonnet-4-5-20250929'
PROJECT_DIR = Path(__file__).parent

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
                    'Shares', 'Position_Size', 'Hold_Days', 'Return_Percent', 'Return_Dollars',
                    'Exit_Reason', 'Catalyst_Type', 'Sector',
                    'Confidence_Level', 'Stop_Loss', 'Price_Target',
                    'Thesis', 'What_Worked', 'What_Failed', 'Account_Value_After'
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
            lines.append(f"""
POSITION {i}: {ticker}
  Entry: ${data['entry_price']:.2f} ({data['days_held']} days ago)
  Yesterday Close: ${data['yesterday_close']:.2f}
  Premarket (~8:30 AM): ${data['premarket_price']:.2f}
  P&L: {data['pnl_percent']:+.1f}% total
  Gap Today: {data['gap_percent']:+.1f}%
  Stop Loss: ${data['stop_loss']:.2f} (-7% trigger)
  Target: ${data['price_target']:.2f} (+10% target)
  Catalyst: {data['catalyst']}
  Thesis: {data['thesis']}
""")
        return "\n".join(lines)

    def _close_position(self, position, exit_price, reason):
        """Close a position and return trade data for CSV logging"""
        entry_price = position.get('entry_price', 0)
        shares = position.get('shares', 0)
        position_size = position.get('position_size', 100)

        pnl_dollars = (exit_price - entry_price) * shares
        pnl_percent = ((exit_price - entry_price) / entry_price * 100) if entry_price > 0 else 0

        # Calculate actual hold days from entry date to now
        entry_date_str = position.get('entry_date', '')
        if entry_date_str:
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
            'days_held': days_held,
            'pnl_percent': round(pnl_percent, 2),
            'pnl_dollars': round(pnl_dollars, 2),
            'exit_reason': reason,
            'catalyst': position.get('catalyst', ''),
            'sector': position.get('sector', ''),
            'confidence': position.get('confidence', ''),
            'thesis': position.get('thesis', ''),
            'stop_loss': position.get('stop_loss', 0),
            'price_target': position.get('price_target', 0),
            'premarket_price': position.get('premarket_price', entry_price),
            'gap_percent': position.get('gap_percent', 0)
        }

        return trade

    def _log_trade_to_csv(self, trade):
        """
        Wrapper to log closed trade to CSV via log_completed_trade()
        Transforms trade dict from _close_position() to expected format
        """
        from datetime import datetime

        trade_data = {
            'trade_id': f"{trade['ticker']}_{trade['entry_date']}_{datetime.now().strftime('%Y%m%d')}",
            'entry_date': trade['entry_date'],
            'exit_date': datetime.now().strftime('%Y-%m-%d'),
            'ticker': trade['ticker'],
            'premarket_price': trade.get('premarket_price', 0),
            'entry_price': trade['entry_price'],
            'exit_price': trade['exit_price'],
            'gap_percent': trade.get('gap_percent', 0),
            'shares': trade['shares'],
            'position_size': trade['position_size'],
            'hold_days': trade['days_held'],
            'return_percent': trade['pnl_percent'],
            'return_dollars': trade['pnl_dollars'],
            'exit_reason': trade['exit_reason'],
            'catalyst_type': trade.get('catalyst', ''),
            'sector': trade.get('sector', ''),
            'confidence_level': trade.get('confidence', ''),
            'stop_loss': trade.get('stop_loss', 0),
            'price_target': trade.get('price_target', 0),
            'thesis': trade.get('thesis', ''),
            'what_worked': '',  # Will be filled by learning system
            'what_failed': '',  # Will be filled by learning system
            'account_value_after': 0  # Will be calculated after portfolio update
        }

        self.log_completed_trade(trade_data)

    def load_current_portfolio(self):
        """
        Load current portfolio from JSON file
        Returns empty portfolio structure if file doesn't exist
        """
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                return json.load(f)
        else:
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
    
    def fetch_current_prices(self, tickers):
        """
        Fetch current prices using Polygon.io API

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
        """

        if not POLYGON_API_KEY:
            print("   ⚠️ POLYGON_API_KEY not set - using entry prices")
            return {}

        prices = {}
        current_hour = datetime.now().hour
        is_after_market = current_hour >= 16  # After 4:00 PM

        print(f"   Fetching prices for {len(tickers)} tickers via Polygon.io...")

        for i, ticker in enumerate(tickers, 1):
            try:
                # Use snapshot endpoint for 15-min delayed price
                url = f'https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}?apiKey={POLYGON_API_KEY}'
                response = requests.get(url, timeout=10)
                data = response.json()

                if data.get('status') == 'OK' and 'ticker' in data:
                    ticker_data = data['ticker']
                    price = None
                    source = None

                    # PRIORITY 1: After market close (4:00 PM+), use today's closing price
                    if is_after_market and 'day' in ticker_data and ticker_data['day'] and 'c' in ticker_data['day']:
                        price = float(ticker_data['day']['c'])
                        source = "today's close"

                    # PRIORITY 2: Use most recent trade (for intraday or if day.c not available)
                    elif 'lastTrade' in ticker_data and ticker_data['lastTrade'] and 'p' in ticker_data['lastTrade']:
                        price = float(ticker_data['lastTrade']['p'])
                        source = "last trade"

                    # PRIORITY 3: Emergency fallback to yesterday's close (should rarely happen)
                    elif 'prevDay' in ticker_data and ticker_data['prevDay'] and 'c' in ticker_data['prevDay']:
                        price = float(ticker_data['prevDay']['c'])
                        source = "prev close ⚠️"

                    if price:
                        prices[ticker] = price
                        print(f"   [{i}/{len(tickers)}] {ticker}: ${price:.2f} ({source})")
                    else:
                        print(f"   [{i}/{len(tickers)}] {ticker}: No price data available")
                else:
                    # Debug: show what we actually received
                    if 'error' in data:
                        print(f"   [{i}/{len(tickers)}] {ticker}: API error - {data['error']}")
                    else:
                        print(f"   [{i}/{len(tickers)}] {ticker}: No data (status: {data.get('status', 'unknown')})")

                # No rate limiting needed for Starter plan (unlimited calls)
                # Small delay to be respectful to API
                time.sleep(0.1)

            except Exception as e:
                print(f"   ⚠️ Error fetching {ticker}: {e}")

        print(f"   ✓ Fetched {len(prices)}/{len(tickers)} prices")

        return prices

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
            # Fetch VIX (ticker: VIX) from Polygon.io
            url = f'https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/VIX?apiKey={POLYGON_API_KEY}'
            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get('status') == 'OK' and 'ticker' in data:
                ticker_data = data['ticker']

                # Get last trade price
                vix_level = None
                if 'lastTrade' in ticker_data and ticker_data['lastTrade']:
                    vix_level = float(ticker_data['lastTrade'].get('p', 0))
                elif 'day' in ticker_data and ticker_data['day']:
                    vix_level = float(ticker_data['day'].get('c', 0))

                if vix_level and vix_level > 0:
                    # Determine regime based on VIX level
                    if vix_level >= 35:
                        regime = 'SHUTDOWN'
                        message = f'VIX {vix_level:.1f} ≥35: SYSTEM SHUTDOWN - No new entries'
                    elif vix_level >= 30:
                        regime = 'CAUTIOUS'
                        message = f'VIX {vix_level:.1f} (30-35): HIGHEST CONVICTION ONLY'
                    else:
                        regime = 'NORMAL'
                        message = f'VIX {vix_level:.1f} <30: Normal operations'

                    return {
                        'vix': round(vix_level, 2),
                        'timestamp': datetime.now().isoformat(),
                        'regime': regime,
                        'message': message
                    }

            # If no data, try alternative method (index snapshot)
            print("   ⚠️ VIX data unavailable from ticker, assuming normal regime")
            return {
                'vix': 20.0,
                'timestamp': datetime.now().isoformat(),
                'regime': 'NORMAL',
                'message': 'VIX data unavailable - assumed normal regime'
            }

        except Exception as e:
            print(f"   ⚠️ Error fetching VIX: {e}")
            return {
                'vix': 20.0,
                'timestamp': datetime.now().isoformat(),
                'regime': 'NORMAL',
                'message': f'Error fetching VIX - assumed normal regime'
            }

    def check_macro_calendar(self, check_date=None):
        """
        Check if a date falls within blackout windows for major macro events

        Major events with blackout windows:
        - FOMC Meeting: 2 days before → 1 day after
        - CPI Release: 1 day before → day of
        - NFP (Jobs Report): 1 day before → day of
        - PCE (Inflation): 1 day before → day of

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
            ('2025-11-13', 'CPI', 'CPI Release'),
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

            # Define blackout windows
            if event_type == 'FOMC':
                # 2 days before → 1 day after
                from datetime import timedelta
                blackout_start = event_date - timedelta(days=2)
                blackout_end = event_date + timedelta(days=1)
            else:
                # CPI, NFP, PCE: 1 day before → day of
                from datetime import timedelta
                blackout_start = event_date - timedelta(days=1)
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

            if data.get('status') == 'OK' and 'results' in data and len(data['results']) >= 2:
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

        return {
            'relative_strength': round(relative_strength, 2),
            'stock_return_3m': stock_return,
            'sector_return_3m': sector_return,
            'sector_etf': sector_etf,
            'passed_filter': relative_strength >= 3.0  # Required threshold
        }

    def calculate_conviction_level(self, catalyst_tier, news_score, vix, relative_strength, multi_catalyst=False):
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

        # Count supporting factors
        if catalyst_tier == 'Tier1':
            supporting_factors += 1
            reasoning_parts.append('Tier 1 catalyst')

        if news_score >= 15:
            supporting_factors += 1
            reasoning_parts.append(f'Strong news ({news_score}/20)')
        elif news_score >= 10:
            supporting_factors += 1
            reasoning_parts.append(f'Good news ({news_score}/20)')

        if vix < 25:
            supporting_factors += 1
            reasoning_parts.append(f'Low VIX ({vix})')
        elif vix < 30:
            reasoning_parts.append(f'Moderate VIX ({vix})')

        if relative_strength >= 3.0:
            supporting_factors += 1
            reasoning_parts.append(f'Sector leader (RS +{relative_strength:.1f}%)')

        if multi_catalyst:
            supporting_factors += 1
            reasoning_parts.append('Multi-catalyst synergy')

        # REQUIRED FILTERS (auto-reject if failed)
        if relative_strength < 3.0:
            return {
                'conviction': 'SKIP',
                'position_size_pct': 0.0,
                'reasoning': f'Failed RS filter ({relative_strength:.1f}% <3%)',
                'supporting_factors': supporting_factors
            }

        if catalyst_tier != 'Tier1':
            return {
                'conviction': 'SKIP',
                'position_size_pct': 0.0,
                'reasoning': f'Not Tier 1 ({catalyst_tier})',
                'supporting_factors': supporting_factors
            }

        # CONVICTION DETERMINATION (based on supporting factors)
        if supporting_factors >= 5 and news_score >= 15 and vix < 25:
            conviction = 'HIGH'
            position_size = 13.0
        elif supporting_factors >= 4 and news_score >= 10 and vix < 30:
            conviction = 'MEDIUM-HIGH'
            position_size = 11.0
        elif supporting_factors >= 3 and news_score >= 5 and vix < 30:
            conviction = 'MEDIUM'
            position_size = 10.0
        else:
            conviction = 'SKIP'
            position_size = 0.0

        reasoning = ', '.join(reasoning_parts) if reasoning_parts else 'Insufficient factors'

        return {
            'conviction': conviction,
            'position_size_pct': position_size,
            'reasoning': reasoning,
            'supporting_factors': supporting_factors
        }

    # =====================================================================
    # LEARNING ENHANCEMENTS (Phase 5)
    # =====================================================================

    def analyze_performance_metrics(self, days=30):
        """
        Analyze performance across Phases 1-4 dimensions

        Returns comprehensive analysis of:
        - Conviction accuracy (HIGH vs MEDIUM win rates)
        - Catalyst tier performance (Tier1 vs Tier2)
        - VIX regime performance (<25, 25-30, 30-35)
        - News score correlation with returns
        - Relative strength effectiveness
        - Macro event impact

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

                user_message = f"""PORTFOLIO REVIEW - {today_date} @ 8:45 AM (Pre-market)

CURRENT POSITIONS ({len(premarket_data)}):
{portfolio_review}

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
      "position_size": 100.00,
      "catalyst": "Earnings_Beat",
      "sector": "Technology",
      "confidence": "High",
      "thesis": "One sentence thesis"
    }}
  ]
}}
```

Provide full analysis of each position BEFORE the JSON. Justify all exits against the rules above."""

            else:
                # INITIAL BUILD MODE - No existing positions
                user_message = f"""BUILD INITIAL PORTFOLIO - {today_date}

No existing positions. Select 10 stocks with Tier 1 catalysts for swing trading (3-7 day holds).

TIER 1 CATALYSTS ONLY:
- Earnings beats with raised guidance
- Strong sector momentum with clear catalyst
- Major analyst upgrades (top-tier firms)
- Confirmed technical breakouts (2x volume)
- Binary event winners (FDA, M&A, contracts)

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
        """Load optimized context for command"""
        
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
        
        # Load portfolio
        if self.portfolio_file.exists():
            context['portfolio'] = self.portfolio_file.read_text()
        
        # Load account status
        if self.account_file.exists():
            context['account'] = self.account_file.read_text()
        
        # Load recent lessons
        lessons_file = self.project_dir / 'strategy_evolution' / 'lessons_learned.md'
        if lessons_file.exists():
            context['lessons'] = lessons_file.read_text()[-2000:]
        
        context_str = f"""
PROJECT INSTRUCTIONS:
{context.get('instructions', 'Not found')}

STRATEGY RULES (AUTO-UPDATED BY LEARNING):
{context.get('strategy', 'Not found')}

⚠️  HISTORICALLY UNDERPERFORMING CATALYSTS:
The following catalysts have shown poor results. You may still use them if you have strong conviction,
but explain your reasoning and consider what makes this situation different from past failures.
Your decisions will be tracked for accountability.

{context.get('exclusions', 'None')}

CURRENT PORTFOLIO:
{context.get('portfolio', 'Not initialized')}

ACCOUNT STATUS:
{context.get('account', 'Not initialized')}

RECENT LESSONS LEARNED:
{context.get('lessons', 'None yet')}
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
        except:
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

    # =====================================================================
    # JSON PARSING AND PORTFOLIO CREATION
    # =====================================================================
    
    def extract_json_from_response(self, response_text):
        """Extract JSON block from Claude's response"""
        
        # Try to find JSON in code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        
        if json_match:
            try:
                json_str = json_match.group(1)
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"   ⚠️ JSON parsing error: {e}")
                return None
        
        # Fallback: look for raw JSON object
        json_match = re.search(r'\{[\s\S]*"positions"[\s\S]*\}', response_text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
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
        STARTING_CAPITAL = 1000.00

        # Calculate current portfolio value (sum of all position sizes)
        portfolio_value = 0.00
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                portfolio = json.load(f)
                for pos in portfolio.get('positions', []):
                    portfolio_value += pos.get('position_size', 0)

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
        # Cash = Starting capital - Currently invested + All P&L
        # Example: Start $1000, invest $900 (9 pos), +$11.63 profit = $111.63 cash
        cash_available = STARTING_CAPITAL - portfolio_value + realized_pl

        # Account value = positions + cash
        # OR equivalently: STARTING_CAPITAL + realized_pl
        account_value = portfolio_value + cash_available

        # Calculate statistics
        win_rate = (len(winners) / total_trades * 100) if total_trades > 0 else 0.0
        avg_hold_time = sum(hold_times) / len(hold_times) if hold_times else 0.0
        avg_winner = sum(winners) / len(winners) if winners else 0.0
        avg_loser = sum(losers) / len(losers) if losers else 0.0

        account = {
            'account_value': round(account_value, 2),
            'cash_available': round(cash_available, 2),
            'positions_value': round(portfolio_value, 2),
            'realized_pl': round(realized_pl, 2),
            'total_trades': total_trades,
            'win_rate_percent': round(win_rate, 2),
            'average_hold_time_days': round(avg_hold_time, 1),
            'average_winner_percent': round(avg_winner, 2),
            'average_loser_percent': round(avg_loser, 2),
            'last_updated': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        }

        with open(self.account_file, 'w') as f:
            json.dump(account, f, indent=2)

        print(f"   ✓ Updated account status: ${account_value:.2f} (Positions: ${portfolio_value:.2f} + Cash: ${cash_available:.2f}, Realized P&L: ${realized_pl:+.2f})")
    
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

        # PRIORITY 3: Check profit target (+10%)
        if current_price >= price_target:
            standardized_reason = self.standardize_exit_reason(position, current_price, 'target')
            return True, standardized_reason, return_pct

        # PRIORITY 4: Check time stop (21 days)
        entry_date = datetime.strptime(position['entry_date'], '%Y-%m-%d')
        days_held = (datetime.now() - entry_date).days

        if days_held >= 21:
            standardized_reason = self.standardize_exit_reason(position, current_price, 'time stop')
            return True, standardized_reason, return_pct

        return False, 'Hold', return_pct
    
    def close_position(self, position, exit_price, exit_reason):
        """Close a position and prepare trade data for CSV logging"""
        
        entry_price = position['entry_price']
        shares = position['shares']
        
        return_pct = ((exit_price - entry_price) / entry_price) * 100
        return_dollars = (exit_price - entry_price) * shares
        
        entry_date = datetime.strptime(position['entry_date'], '%Y-%m-%d')
        exit_date = datetime.now()
        hold_days = (exit_date - entry_date).days
        
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
            'catalyst_type': position.get('catalyst', 'Unknown'),
            'sector': position.get('sector', 'Unknown'),
            'confidence_level': position.get('confidence', 'Medium'),
            'stop_loss': position.get('stop_loss', 0),
            'price_target': position.get('price_target', 0),
            'thesis': position.get('thesis', ''),
            'what_worked': 'Auto-closed by system' if 'Target' in exit_reason else '',
            'what_failed': 'Hit stop loss' if 'Stop' in exit_reason else '',
            'account_value_after': account_value_after
        }
        
        return trade_data
    
    def log_completed_trade(self, trade_data):
        """Write completed trade to CSV for learning system"""
        
        if not self.trades_csv.exists():
            self.trades_csv.parent.mkdir(parents=True, exist_ok=True)
            with open(self.trades_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Trade_ID', 'Entry_Date', 'Exit_Date', 'Ticker',
                    'Premarket_Price', 'Entry_Price', 'Exit_Price', 'Gap_Percent',
                    'Shares', 'Position_Size', 'Position_Size_Percent', 'Hold_Days', 'Return_Percent', 'Return_Dollars',
                    'Exit_Reason', 'Catalyst_Type', 'Catalyst_Tier', 'Catalyst_Age_Days',
                    'News_Validation_Score', 'News_Exit_Triggered',
                    'VIX_At_Entry', 'Market_Regime', 'Macro_Event_Near',
                    'Relative_Strength', 'Stock_Return_3M', 'Sector_ETF',
                    'Conviction_Level', 'Supporting_Factors',
                    'Sector', 'Stop_Loss', 'Price_Target',
                    'Thesis', 'What_Worked', 'What_Failed', 'Account_Value_After'
                ])

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
                trade_data.get('shares', 0),
                trade_data.get('position_size', 0),
                trade_data.get('position_size_percent', 0),
                trade_data.get('hold_days', 0),
                trade_data.get('return_percent', 0),
                trade_data.get('return_dollars', 0),
                trade_data.get('exit_reason', ''),
                trade_data.get('catalyst_type', ''),
                trade_data.get('catalyst_tier', 'Unknown'),
                trade_data.get('catalyst_age_days', 0),
                trade_data.get('news_validation_score', 0),
                trade_data.get('news_exit_triggered', False),
                trade_data.get('vix_at_entry', 0.0),
                trade_data.get('market_regime', 'Unknown'),
                trade_data.get('macro_event_near', 'None'),
                trade_data.get('relative_strength', 0.0),
                trade_data.get('stock_return_3m', 0.0),
                trade_data.get('sector_etf', 'Unknown'),
                trade_data.get('conviction_level', 'MEDIUM'),
                trade_data.get('supporting_factors', 0),
                trade_data.get('sector', ''),
                trade_data.get('stop_loss', 0),
                trade_data.get('price_target', 0),
                trade_data.get('thesis', ''),
                trade_data.get('what_worked', ''),
                trade_data.get('what_failed', ''),
                trade_data.get('account_value_after', 0)
            ])
        
        print(f"   ✓ Logged trade to CSV: {trade_data.get('ticker')} "
              f"({trade_data.get('return_percent', 0):.2f}%)")
    
    def update_portfolio_prices_and_check_exits(self):
        """
        CRITICAL FUNCTION - The heart of the ANALYZE command
        
        1. Fetch current prices for all positions
        2. Update P&L for each position
        3. Check if any stops/targets hit
        4. Close positions that need closing
        5. Update portfolio and account JSON files
        6. Log closed trades to CSV
        
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
            
            # Update days held
            entry_date = datetime.strptime(position['entry_date'], '%Y-%m-%d')
            position['days_held'] = (datetime.now() - entry_date).days
            
            # Check if position should be closed
            should_close, exit_reason, return_pct = self.check_position_exits(
                position, current_price
            )
            
            if should_close:
                print(f"   🚪 CLOSING: {ticker} - {exit_reason} ({return_pct:+.2f}%)")
                
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
        
        print(f"\n✓ Portfolio updated: {len(positions_to_keep)} open, {len(closed_trades)} closed")
        
        return closed_trades
    
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
                if ticker in premarket_prices:
                    entry_price = pos.get('entry_price', 0)
                    current_price = pos.get('current_price', entry_price)  # Yesterday's close
                    premarket_price = premarket_prices[ticker]

                    # Calculate metrics
                    pnl_percent = ((premarket_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
                    gap_percent = ((premarket_price - current_price) / current_price * 100) if current_price > 0 else 0
                    days_held = pos.get('days_held', 0)

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
                        'catalyst': pos.get('catalyst', '')
                    }

                    gap_str = f"Gap: {gap_percent:+.1f}%" if abs(gap_percent) > 0.5 else "No gap"
                    print(f"   {ticker}: ${premarket_price:.2f} ({pnl_percent:+.1f}% total, {gap_str}, Day {days_held})")
            print()
        else:
            print("2. No existing positions - building initial portfolio\n")

        # Step 3: Load context and call Claude for review
        print("3. Loading context for portfolio review...")
        context = self.load_optimized_context('go')
        print("   ✓ Context loaded\n")

        print("4. Calling Claude for position review and decisions...")
        response = self.call_claude_api('go', context, premarket_data)
        response_text = response.get('content', [{}])[0].get('text', '')
        print("   ✓ Response received\n")

        # Step 4: Extract decisions from Claude's response
        print("5. Extracting decisions from response...")
        decisions = self.extract_json_from_response(response_text)

        if not decisions:
            print("   ✗ No valid JSON found in response\n")
            return False

        # Step 5: Process decisions and create pending file
        hold_positions = decisions.get('hold', [])
        exit_positions = decisions.get('exit', [])
        buy_positions = decisions.get('buy', [])

        print(f"   ✓ HOLD: {len(hold_positions)} positions")
        print(f"   ✓ EXIT: {len(exit_positions)} positions")
        print(f"   ✓ BUY:  {len(buy_positions)} new positions\n")

        # Step 5.4: PHASE 3 - Check VIX and Macro Calendar
        print("5.4 Checking market regime (Phase 3: VIX + Macro Calendar)...")

        # Fetch VIX level
        vix_result = self.fetch_vix_level()
        print(f"   {vix_result['message']}")

        # Check macro calendar
        macro_result = self.check_macro_calendar()
        print(f"   {macro_result['message']}")

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

        if macro_result['is_blackout']:
            # Macro event blackout: No new entries
            print(f"   🚨 MACRO BLACKOUT: {macro_result['event_type']} on {macro_result['event_date']}")
            print(f"   ✗ Blocking ALL {len(buy_positions)} BUY recommendations")
            buy_positions = []  # Clear all BUY recommendations
            can_enter_positions = False

        print()

        # Step 5.5: PHASE 1-4 - Validate BUY recommendations
        if buy_positions and can_enter_positions:
            print("5.5 Validating BUY recommendations (Phases 1-4: Full validation pipeline)...")
            validated_buys = []

            for buy_pos in buy_positions:
                ticker = buy_pos.get('ticker', 'UNKNOWN')
                catalyst_type = buy_pos.get('catalyst', 'Unknown')
                catalyst_age = buy_pos.get('catalyst_age_days', 0)
                catalyst_details = buy_pos.get('catalyst_details', {})
                sector = buy_pos.get('sector', 'Unknown')

                validation_passed = True
                rejection_reasons = []

                try:
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

                    # Auto-reject Tier 3 catalysts
                    if tier_result['tier'] == 'Tier3':
                        validation_passed = False
                        rejection_reasons.append(f"Tier 3 catalyst: {tier_result['reasoning']}")

                    # Check catalyst age validity
                    age_check = self.check_catalyst_age_validity(catalyst_type, catalyst_age)
                    if not age_check['is_valid']:
                        validation_passed = False
                        rejection_reasons.append(age_check['reason'])

                    # PHASE 1: Check news validation
                    news_result = self.calculate_news_validation_score(
                        ticker=ticker,
                        catalyst_type=catalyst_type,
                        catalyst_age_days=catalyst_age
                    )

                    # Log validation event
                    self.log_news_monitoring(
                        ticker=ticker,
                        event_type='VALIDATION',
                        result=news_result
                    )

                    # News score must be ≥5
                    if news_result['score'] < 5:
                        validation_passed = False
                        rejection_reasons.append(f"News score too low ({news_result['score']}/20)")

                    # PHASE 3: Apply regime-based filtering
                    if regime_adjustment == 'HIGHEST_CONVICTION_ONLY':
                        # VIX 30-35: Only accept Tier 1 with news score ≥15
                        if tier_result['tier'] != 'Tier1' or news_result['score'] < 15:
                            validation_passed = False
                            rejection_reasons.append(f"VIX {vix_result['vix']} - requires Tier1 + News≥15")

                    # PHASE 4: Relative Strength + Conviction Sizing
                    rs_result = self.calculate_relative_strength(ticker, sector)

                    # Check relative strength filter (≥3% required)
                    if not rs_result['passed_filter']:
                        validation_passed = False
                        rejection_reasons.append(f"Failed RS filter ({rs_result['relative_strength']:.1f}% <3%)")

                    # Calculate conviction level (determines final position size)
                    multi_catalyst = catalyst_type == 'Multi_Catalyst' or catalyst_details.get('multi_catalyst', False)
                    conviction_result = self.calculate_conviction_level(
                        catalyst_tier=tier_result['tier'],
                        news_score=news_result['score'],
                        vix=vix_result['vix'],
                        relative_strength=rs_result['relative_strength'],
                        multi_catalyst=multi_catalyst
                    )

                    # Conviction may downgrade to SKIP based on factors
                    if conviction_result['conviction'] == 'SKIP':
                        validation_passed = False
                        rejection_reasons.append(f"Conviction: {conviction_result['reasoning']}")

                    # If all validations pass, accept the position
                    if validation_passed:
                        # Enrich position with all Phase data (1-4)
                        buy_pos['catalyst_tier'] = tier_result['tier']
                        buy_pos['tier_name'] = tier_result['tier_name']
                        buy_pos['tier_reasoning'] = tier_result['reasoning']
                        buy_pos['news_score'] = news_result['score']
                        buy_pos['vix_at_entry'] = vix_result['vix']
                        buy_pos['market_regime'] = vix_result['regime']
                        buy_pos['macro_event_near'] = macro_result['event_type'] or 'None'
                        buy_pos['relative_strength'] = rs_result['relative_strength']
                        buy_pos['stock_return_3m'] = rs_result['stock_return_3m']
                        buy_pos['sector_etf'] = rs_result['sector_etf']
                        buy_pos['conviction_level'] = conviction_result['conviction']
                        buy_pos['position_size_pct'] = conviction_result['position_size_pct']  # Phase 4 overrides Phase 2
                        buy_pos['target_pct'] = tier_result['target_pct']
                        buy_pos['supporting_factors'] = conviction_result['supporting_factors']

                        validated_buys.append(buy_pos)

                        print(f"   ✓ {ticker}: {conviction_result['conviction']} - {rs_result['relative_strength']:+.1f}% RS")
                        print(f"      Catalyst: {tier_result['tier_name']}")
                        print(f"      News: {news_result['score']}/20, RS: {rs_result['relative_strength']:+.1f}%, VIX: {vix_result['vix']}")
                        print(f"      Position Size: {conviction_result['position_size_pct']}% ({conviction_result['conviction']})")
                        print(f"      Reasoning: {conviction_result['reasoning']}")
                    else:
                        print(f"   ✗ {ticker}: REJECTED")
                        for reason in rejection_reasons:
                            print(f"      - {reason}")

                except Exception as e:
                    # If validation fails due to error, keep position (don't block on API errors)
                    print(f"   ⚠️ {ticker}: Validation error ({e}) - keeping position with default tier")
                    buy_pos['catalyst_tier'] = 'Tier2'
                    buy_pos['position_size_pct'] = 10.0
                    validated_buys.append(buy_pos)

            # Replace buy_positions with validated list
            buy_positions = validated_buys
            print(f"   ✓ Validated: {len(validated_buys)} BUY positions passed checks\n")

        # Step 6: Build pending_positions.json
        print("6. Building pending positions file...")
        pending = {
            'decision_time': datetime.now().isoformat(),
            'hold': hold_positions,
            'exit': exit_positions,
            'buy': buy_positions
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
        print(f"\n✓ Run 'execute' command at 9:30 AM to execute these decisions\n")

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

        print(f"   ✓ HOLD: {len(hold_tickers)} positions")
        print(f"   ✓ EXIT: {len(exit_decisions)} positions")
        print(f"   ✓ BUY:  {len(buy_positions)} new positions\n")

        # Load current portfolio
        print("2. Loading current portfolio...")
        current_portfolio = self.load_current_portfolio()
        current_positions = current_portfolio.get('positions', [])
        print(f"   ✓ Loaded {len(current_positions)} current positions\n")

        # Process EXITS
        print("3. Processing EXITS...")
        closed_trades = []
        if exit_decisions:
            exit_tickers = [e['ticker'] for e in exit_decisions]
            tickers_to_fetch = list(set(exit_tickers + [p['ticker'] for p in current_positions]))
            market_prices = self.fetch_current_prices(tickers_to_fetch)

            for exit_decision in exit_decisions:
                ticker = exit_decision['ticker']
                claude_reason = exit_decision.get('reason', 'Portfolio management decision')

                # Find position in current portfolio
                position = next((p for p in current_positions if p['ticker'] == ticker), None)
                if position:
                    exit_price = market_prices.get(ticker, position.get('current_price', 0))

                    # Standardize the exit reason (converts Claude's freeform text to consistent format)
                    standardized_reason = self.standardize_exit_reason(position, exit_price, claude_reason)

                    closed_trade = self._close_position(position, exit_price, standardized_reason)
                    closed_trades.append(closed_trade)
                    print(f"   ✓ CLOSED {ticker}: {standardized_reason}")
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
        if buy_positions:
            # Calculate current account value for position sizing (COMPOUND GROWTH)
            STARTING_CAPITAL = 1000.00
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

            for pos in buy_positions:
                ticker = pos['ticker']
                if ticker in market_prices:
                    entry_price = market_prices[ticker]

                    # COMPOUND GROWTH: Calculate position size based on CURRENT account value
                    position_size_pct = pos.get('position_size_pct', 10.0)
                    position_size_dollars = round((position_size_pct / 100) * current_account_value, 2)

                    # Ensure we don't exceed available cash
                    if position_size_dollars > cash_available:
                        position_size_dollars = round(cash_available, 2)
                        print(f"   ⚠️ {ticker}: Reduced size to available cash ${cash_available:.2f}")

                    pos['entry_price'] = entry_price
                    pos['current_price'] = entry_price
                    pos['entry_date'] = datetime.now().strftime('%Y-%m-%d')
                    pos['days_held'] = 0
                    pos['position_size'] = position_size_dollars  # Store actual dollar amount
                    pos['shares'] = position_size_dollars / entry_price
                    pos['stop_loss'] = round(entry_price * 0.93, 2)  # -7%
                    pos['price_target'] = round(entry_price * 1.10, 2)  # +10%
                    pos['unrealized_gain_pct'] = 0.0
                    pos['unrealized_gain_dollars'] = 0.0

                    # Update cash available for next position
                    cash_available -= position_size_dollars

                    updated_positions.append(pos)
                    print(f"   ✓ ENTERED {ticker}: ${entry_price:.2f}, {pos['shares']:.2f} shares (${position_size_dollars:.2f} = {position_size_pct}% of ${current_account_value:.2f})")
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

        # Clean up pending file
        self.pending_file.unlink()

        print("="*60)
        print("EXECUTE COMMAND COMPLETE")
        print("="*60)
        print(f"\n✓ Portfolio Updated:")
        print(f"  - Closed: {len(closed_trades)} positions")
        print(f"  - Holding: {len(updated_positions) - len(buy_positions)} positions")
        print(f"  - Entered: {len(buy_positions)} new positions")
        print(f"  - Total Active: {len(updated_positions)} positions\n")

        return True
    
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
        response = self.call_claude_api('analyze', context)
        print("   ✓ Response received\n")

        print("3. Saving response...")
        self.save_response('analyze', response)
        print("   ✓ Complete\n")

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
        print("\nUsage: python agent.py [go|execute|analyze|learn]")
        print("\nCommands:")
        print("  go       - Select 10 stocks (8:45 AM)")
        print("  execute  - Enter positions (9:30 AM)")
        print("  analyze  - Update & close positions (4:30 PM)")
        print("  learn    - Analyze performance metrics (Phase 5)")
        sys.exit(1)

    command = sys.argv[1].lower()

    print(f"\n{'='*60}")
    print(f"Paper Trading Lab Agent v5.4.0")
    et_tz = pytz.timezone('America/New_York')
    print(f"Time: {datetime.now(et_tz).strftime('%Y-%m-%d %H:%M:%S ET')}")
    print(f"{'='*60}")

    agent = TradingAgent()

    try:
        if command == 'go':
            success = agent.execute_go_command()
        elif command == 'execute':
            success = agent.execute_execute_command()
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