#!/usr/bin/env python3
"""
Paper Trading Lab - Agent v5.0.6
SWING TRADING SYSTEM - PROPER POSITION MANAGEMENT

MAJOR IMPROVEMENTS FROM v4.3:
1. GO command reviews EXISTING portfolio with 15-min delayed premarket data
2. Enforces swing trading rules: 2-day minimum hold, proper exit criteria
3. HOLD/EXIT/BUY decision logic instead of daily portfolio rebuild
4. Leverages Polygon.io 15-min delayed data for premarket gap analysis
5. True swing trading: positions held 3-7 days unless stops/targets hit

v5.0.1 FIX (2025-10-30):
- Fixed cash tracking bug: System now properly calculates cash_available
- Cash = Starting capital - Invested positions + Realized P&L
- Account value = Positions + Cash (previously was missing returned capital)

v5.0.2 ALIGNMENT (2025-10-30):
- Aligned code with simplified exit strategy (full exits only, no partials)
- Updated strategy_rules.md and code documentation
- Fixed dashboard return calculation (removed double-counting)

v5.0.3 STANDARDIZATION (2025-10-30):
- Standardized exit reasons to simple, consistent format
- Examples: "Target reached (+11.6%)", "Stop loss (-8.2%)", "Time stop (21 days)"

v5.0.4 HOLD DAYS FIX (2025-10-30):
- Fixed hold days calculation to use actual date difference
- Previously showed 0 days when should show 1+ (wasn't incrementing on exit)

v5.0.5 CRITICAL TIMING FIX (2025-10-30):
- Fixed 15-minute delay pricing logic in fetch_current_prices()
- Now checks day.c (today's close) BEFORE prevDay.c (yesterday's close)
- Updated cron schedule: EXECUTE 9:45 AM, ANALYZE 4:50 PM (accounting for delay)
- Prevents stale price data causing missed stop losses (BA case: -10.4% undetected)

v5.0.6 DAILY ACTIVITY FIX (2025-10-30):
- Fixed "Today's Activity" to show ALL trades closed today (by exit_date from CSV)
- Previously only showed trades closed in current ANALYZE execution
- Now includes trades closed in both EXECUTE and ANALYZE commands

WORKFLOW (Adjusted for 15-minute Polygon delay):
  8:45 AM - GO command:
    - Load current portfolio (yesterday's positions)
    - Fetch premarket prices (~8:30 AM via Polygon.io)
    - Calculate gaps and P&L
    - Decide: HOLD (keep positions) / EXIT (stop/target/catalyst fail) / BUY (fill vacancies)
    - Save decisions to pending_positions.json

  9:45 AM - EXECUTE command (CHANGED from 9:30 AM):
    - Load pending decisions
    - Execute exits for positions marked EXIT
    - Enter new positions marked BUY
    - Update portfolio with 9:30 AM market open prices (available at 9:45 AM with 15-min delay)

  4:50 PM - ANALYZE command (CHANGED from 4:30 PM):
    - Update all prices to 4:00 PM closing prices (available at 4:50 PM with 15-min delay + buffer)
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
Pay special attention to CATALYST EXCLUSIONS - do not use any catalyst types that are marked as excluded.

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
        
        # Load catalyst exclusions
        exclusions = self.load_catalyst_exclusions()
        if exclusions:
            context['exclusions'] = '\n'.join([
                f"- {e['catalyst']}: {e.get('reason', 'Poor performance')}" 
                for e in exclusions
            ])
        else:
            context['exclusions'] = 'None'
        
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

⚠️ CATALYST EXCLUSIONS (DO NOT USE THESE):
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
        Check if position should be closed based on stops/targets (FULL EXIT only)

        Exit Rules (Simplified Strategy):
        1. Stop Loss: -7% from entry (exit 100%)
        2. Price Target: +10% from entry (exit 100%)
        3. Time Stop: 21 days held (exit 100%)

        No partial exits - simplicity over complexity
        """

        entry_price = position['entry_price']
        stop_loss = position.get('stop_loss', entry_price * 0.93)  # -7%
        price_target = position.get('price_target', entry_price * 1.10)  # +10%

        return_pct = ((current_price - entry_price) / entry_price) * 100

        # Check stop loss (-7%)
        if current_price <= stop_loss:
            standardized_reason = self.standardize_exit_reason(position, current_price, 'stop loss')
            return True, standardized_reason, return_pct

        # Check profit target (+10%)
        if current_price >= price_target:
            standardized_reason = self.standardize_exit_reason(position, current_price, 'target')
            return True, standardized_reason, return_pct

        # Check time stop (21 days)
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
                    'Shares', 'Position_Size', 'Hold_Days', 'Return_Percent', 'Return_Dollars',
                    'Exit_Reason', 'Catalyst_Type', 'Sector',
                    'Confidence_Level', 'Stop_Loss', 'Price_Target',
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
                trade_data.get('hold_days', 0),
                trade_data.get('return_percent', 0),
                trade_data.get('return_dollars', 0),
                trade_data.get('exit_reason', ''),
                trade_data.get('catalyst_type', ''),
                trade_data.get('sector', ''),
                trade_data.get('confidence_level', ''),
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
            buy_tickers = [p['ticker'] for p in buy_positions]
            market_prices = self.fetch_current_prices(buy_tickers)

            for pos in buy_positions:
                ticker = pos['ticker']
                if ticker in market_prices:
                    entry_price = market_prices[ticker]
                    pos['entry_price'] = entry_price
                    pos['current_price'] = entry_price
                    pos['entry_date'] = datetime.now().strftime('%Y-%m-%d')
                    pos['days_held'] = 0
                    pos['shares'] = pos.get('position_size', 100) / entry_price
                    pos['stop_loss'] = round(entry_price * 0.93, 2)  # -7%
                    pos['price_target'] = round(entry_price * 1.10, 2)  # +10%
                    pos['unrealized_gain_pct'] = 0.0
                    pos['unrealized_gain_dollars'] = 0.0

                    updated_positions.append(pos)
                    print(f"   ✓ ENTERED {ticker}: ${entry_price:.2f}, {pos['shares']:.2f} shares")
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
        print("\nUsage: python agent.py [go|execute|analyze]")
        print("\nCommands:")
        print("  go       - Select 10 stocks (8:45 AM)")
        print("  execute  - Enter positions (9:30 AM)")
        print("  analyze  - Update & close positions (4:30 PM)")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    print(f"\n{'='*60}")
    print(f"Paper Trading Lab Agent v5.0")
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
        else:
            print(f"\nERROR: Unknown command '{command}'")
            print("Valid commands: go, execute, analyze")
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