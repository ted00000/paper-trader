#!/usr/bin/env python3
"""
Paper Trading Lab - Agent v4.3
PRODUCTION READY - COMPLETE AND TESTED

CRITICAL IMPROVEMENTS FROM v4.2:
1. Split GO (selection @8:45) from EXECUTE (entry @9:30 with real prices)
2. Fixed account calculation to include realized P&L from CSV
3. Real market open prices for entries (via Alpha Vantage GLOBAL_QUOTE)

WORKFLOW:
  8:45 AM - GO command: Select 10 stocks, save to pending_positions.json
  9:30 AM - EXECUTE command: Load pending, fetch real prices, create portfolio
  4:30 PM - ANALYZE command: Update prices, check exits, log trades to CSV

NOTE ON ALPHA VANTAGE FREE TIER:
- At 9:30 AM, GLOBAL_QUOTE returns YESTERDAY'S CLOSE (not real-time)
- This is acceptable for paper trading (entry prices ~1-3% off)
- When upgraded to premium ($50/month), same code gets real-time prices
- No code changes needed for live trading transition

Usage:
  python3 agent.py go       # 8:45 AM - Select stocks
  python3 agent.py execute  # 9:30 AM - Enter positions
  python3 agent.py analyze  # 4:30 PM - Update & close
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
    
    # =====================================================================
    # ALPHA VANTAGE PRICE FETCHING
    # =====================================================================
    
    def fetch_current_prices(self, tickers):
        """
        Fetch current prices using Polygon.io API

        STARTER PLAN ($29/mo):
        - 15-minute delayed data (perfect for swing trading)
        - Unlimited API calls (no daily/minute rate limits)
        - At 9:30 AM EXECUTE: Gets ~9:15 AM prices
        - At 4:30 PM ANALYZE: Gets ~4:15 PM prices (essentially closing prices)

        This is ideal for swing trading with multi-day holds.
        """

        if not POLYGON_API_KEY:
            print("   ⚠️ POLYGON_API_KEY not set - using entry prices")
            return {}

        prices = {}

        print(f"   Fetching prices for {len(tickers)} tickers via Polygon.io...")

        for i, ticker in enumerate(tickers, 1):
            try:
                # Use snapshot endpoint for 15-min delayed price
                url = f'https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}?apiKey={POLYGON_API_KEY}'
                response = requests.get(url, timeout=10)
                data = response.json()

                if data.get('status') == 'OK' and 'ticker' in data:
                    ticker_data = data['ticker']

                    # Try to get last trade price (most recent)
                    if 'lastTrade' in ticker_data and ticker_data['lastTrade']:
                        price = float(ticker_data['lastTrade']['p'])
                        prices[ticker] = price
                        print(f"   [{i}/{len(tickers)}] {ticker}: ${price:.2f}")
                    # Fallback to previous day close if no recent trade
                    elif 'prevDay' in ticker_data and ticker_data['prevDay']:
                        price = float(ticker_data['prevDay']['c'])
                        prices[ticker] = price
                        print(f"   [{i}/{len(tickers)}] {ticker}: ${price:.2f} (prev close)")
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
    
    def call_claude_api(self, command, context):
        """Call Claude API with optimized context and retry logic"""

        if not CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY environment variable not set")

        headers = {
            'x-api-key': CLAUDE_API_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }

        if command == 'go':
            user_message = """Execute the 'go' command: Select 10 stocks for the portfolio.

CRITICAL OUTPUT REQUIREMENT:
At the END of your analysis, you MUST output a JSON block in this EXACT format:
```json
{
  "positions": [
    {
      "ticker": "AAPL",
      "entry_price": 175.50,
      "position_size": 100.00,
      "catalyst": "Earnings_Beat",
      "sector": "Technology",
      "confidence": "High",
      "thesis": "Strong Q4 earnings with iPhone growth",
      "stop_loss": 163.28,
      "price_target": 193.05
    }
  ],
  "total_positions": 10,
  "portfolio_value": 1000.00
}
```

CRITICAL: position_size must ALWAYS be exactly 100.00 (dollars, not shares).
DO NOT calculate shares in the JSON - the system will calculate shares later based on real market prices.
Every position must have position_size: 100.00

CRITICAL: stop_loss and price_target calculation rules:
- stop_loss = entry_price * 0.90 (10% below entry - where we exit to cut losses)
- price_target = entry_price * 1.10 (10% above entry - where we take profits)
- Example: If entry_price is $100, then stop_loss = $90.00 and price_target = $110.00
- Stop loss must ALWAYS be BELOW entry price
- Price target must ALWAYS be ABOVE entry price

Include your full analysis and reasoning BEFORE the JSON block, but the JSON MUST be present at the end for the system to parse."""
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
        CRITICAL FIX: Now includes realized P&L from CSV
        """
        
        # Calculate current portfolio value
        portfolio_value = 0.00
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                portfolio = json.load(f)
                for pos in portfolio.get('positions', []):
                    portfolio_value += pos.get('position_size', 0)
        
        # Calculate realized P&L from CSV
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
        
        # CRITICAL: Account value = current positions + realized P&L
        # Starting capital is implicit (if we started with $1000 and have
        # $1050 in positions + $50 realized, account_value = $1100)
        account_value = portfolio_value + realized_pl
        
        # Calculate statistics
        win_rate = (len(winners) / total_trades * 100) if total_trades > 0 else 0.0
        avg_hold_time = sum(hold_times) / len(hold_times) if hold_times else 0.0
        avg_winner = sum(winners) / len(winners) if winners else 0.0
        avg_loser = sum(losers) / len(losers) if losers else 0.0
        
        account = {
            'account_value': round(account_value, 2),
            'cash_available': 0.00,  # Always fully invested
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
        
        print(f"   ✓ Updated account status: ${account_value:.2f} (Positions: ${portfolio_value:.2f} + Realized: ${realized_pl:.2f})")
    
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
    
    def check_position_exits(self, position, current_price):
        """Check if position should be closed based on stops/targets"""
        
        entry_price = position['entry_price']
        stop_loss = position.get('stop_loss', entry_price * 0.93)
        price_target = position.get('price_target', entry_price * 1.10)
        
        return_pct = ((current_price - entry_price) / entry_price) * 100
        
        # Check stop loss
        if current_price <= stop_loss:
            return True, 'Stop Loss Hit', return_pct
        
        # Check profit target
        if current_price >= price_target:
            return True, 'Price Target Reached', return_pct
        
        # Check time stop (21 days)
        entry_date = datetime.strptime(position['entry_date'], '%Y-%m-%d')
        days_held = (datetime.now() - entry_date).days
        
        if days_held >= 21:
            return True, 'Time Stop (21 days)', return_pct
        
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
            'entry_price': entry_price,
            'exit_price': exit_price,
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
                    'Entry_Price', 'Exit_Price', 'Shares', 'Position_Size',
                    'Hold_Days', 'Return_Percent', 'Return_Dollars', 
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
                trade_data.get('entry_price', 0),
                trade_data.get('exit_price', 0),
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
        Execute GO command (8:45 AM)
        
        NEW v4.3 BEHAVIOR:
        - Call Claude to select 10 stocks
        - Extract JSON with selections
        - Save to pending_positions.json (NOT current_portfolio.json)
        - Validate selections against exclusions
        - DO NOT create portfolio yet (wait for EXECUTE command)
        """
        
        print("\n" + "="*60)
        print("EXECUTING 'GO' COMMAND - STOCK SELECTION")
        print("="*60 + "\n")
        
        print("1. Loading optimized context...")
        context = self.load_optimized_context('go')
        print("   ✓ Context loaded\n")
        
        print("2. Calling Claude API for stock selections...")
        response = self.call_claude_api('go', context)
        response_text = response.get('content', [{}])[0].get('text', '')
        print("   ✓ Response received\n")
        
        print("3. Extracting JSON from response...")
        portfolio_json = self.extract_json_from_response(response_text)

        if portfolio_json:
            # NEW: Fetch real prices for selected stocks and update JSON
            print(f"   ✓ Extracted {len(portfolio_json.get('positions', []))} selections\n")

            print("4. Fetching real prices for selected stocks...")
            positions = portfolio_json.get('positions', [])
            tickers = [p['ticker'] for p in positions]
            real_prices = self.fetch_current_prices(tickers)

            # Update positions with real prices
            for pos in positions:
                ticker = pos['ticker']
                if ticker in real_prices:
                    old_price = pos.get('entry_price', 0)
                    pos['entry_price'] = real_prices[ticker]
                    # Recalculate stop_loss and price_target based on real price
                    pos['stop_loss'] = round(real_prices[ticker] * 0.90, 2)
                    pos['price_target'] = round(real_prices[ticker] * 1.10, 2)
                    print(f"   ✓ {ticker}: Updated ${old_price:.2f} → ${real_prices[ticker]:.2f}")
            print()

            # Save to PENDING file with real prices
            portfolio_json['selection_time'] = datetime.now().isoformat()
            with open(self.pending_file, 'w') as f:
                json.dump(portfolio_json, f, indent=2)
            print(f"   ✓ Saved selections to pending with real prices\n")
        else:
            print("   ⚠️ No JSON found - selections not saved\n")

        print("5. Validating selections...")
        is_valid, violations = self.validate_trade_decisions(response_text)

        if violations:
            print("   ⚠️ VALIDATION WARNINGS:")
            for v in violations:
                print(f"      {v}")
            print()
        else:
            print("   ✓ All selections validated\n")

        print("6. Saving response...")
        self.save_response('go', response)
        print("   ✓ Complete\n")
        
        print("="*60)
        print("GO COMMAND COMPLETE")
        print("="*60)
        print("\n✓ Stocks selected and saved to pending_positions.json")
        print("✓ Run 'execute' command at 9:30 AM to enter positions\n")
        
        return True
    
    def execute_execute_command(self):
        """
        Execute EXECUTE command (9:30 AM)
        
        NEW v4.3 BEHAVIOR:
        - Load pending selections from pending_positions.json
        - Fetch REAL market prices (Alpha Vantage GLOBAL_QUOTE)
        - Update positions with actual prices
        - Calculate shares based on real prices
        - Create current_portfolio.json
        - Delete pending file
        
        NOTE: Free Alpha Vantage returns yesterday's close at 9:30 AM.
        This is acceptable for paper trading. Upgrade to premium for real-time.
        """
        
        print("\n" + "="*60)
        print("EXECUTING 'EXECUTE' - POSITION ENTRY (Market Open)")
        print("="*60 + "\n")
        
        if not self.pending_file.exists():
            print("   ✗ No pending selections found")
            print("   Run 'go' command first\n")
            return False
        
        print("1. Loading pending selections...")
        with open(self.pending_file, 'r') as f:
            pending = json.load(f)
        
        positions = pending.get('positions', [])
        print(f"   ✓ Loaded {len(positions)} pending positions\n")
        
        print("2. Fetching real market prices...")
        tickers = [p['ticker'] for p in positions]
        real_prices = self.fetch_current_prices(tickers)
        print()
        
        print("3. Updating positions with real prices...")
        for pos in positions:
            ticker = pos['ticker']
            if ticker in real_prices:
                # Update with real market price
                pos['entry_price'] = real_prices[ticker]
                pos['current_price'] = real_prices[ticker]
                # Recalculate shares based on real price
                pos['shares'] = pos.get('position_size', 100) / real_prices[ticker]
                print(f"   ✓ {ticker}: Entry=${real_prices[ticker]:.2f}, "
                      f"Shares={pos['shares']:.2f}")
            else:
                # Use estimated price from GO command
                print(f"   ⚠️ {ticker}: Using estimated price ${pos.get('entry_price', 0):.2f}")
        print()
        
        print("4. Creating portfolio...")
        success = self.update_portfolio_from_json({'positions': positions})
        
        if success:
            print("   ✓ Portfolio created\n")
            
            print("5. Cleaning up pending file...")
            self.pending_file.unlink()
            print("   ✓ Pending file deleted\n")
            
            print("="*60)
            print("EXECUTE COMMAND COMPLETE")
            print("="*60)
            print(f"\n✓ Entered {len(positions)} positions at market prices")
            print("✓ Run 'analyze' command at 4:30 PM to update\n")
            
            return True
        else:
            print("   ✗ Portfolio creation failed\n")
            return False
    
    def create_daily_activity_summary(self, closed_trades):
        """
        Create daily activity summary for dashboard
        Shows what happened today: positions closed, P&L summary
        """

        # Get current portfolio to see what's still open
        open_positions = []
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r') as f:
                portfolio = json.load(f)
                open_positions = portfolio.get('positions', [])

        # Calculate summary stats
        total_closed = len(closed_trades)
        winners = [t for t in closed_trades if t['return_percent'] > 0]
        losers = [t for t in closed_trades if t['return_percent'] <= 0]

        total_pl_dollars = sum(t['return_dollars'] for t in closed_trades)

        # Create activity summary
        activity = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
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
                for t in closed_trades
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

        # Create daily activity summary for dashboard
        if closed_trades:
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
    print(f"Paper Trading Lab Agent v4.3")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
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