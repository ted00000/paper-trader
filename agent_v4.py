#!/usr/bin/env python3
"""
Paper Trading Lab - Production Agent v4.0
COMPLETE WORKING VERSION with price fetching, position management, and CSV logging

Major improvements over v3.0:
- Real-time price fetching via yfinance
- Automatic stop loss and profit target checking
- Proper position closing and CSV logging
- Complete portfolio updates in analyze command
- Tested and verified data flow

This is the PRODUCTION READY version.
"""

import os
import sys
import json
import csv
import re
import requests
from datetime import datetime, timedelta
from pathlib import Path
import traceback

# Configuration
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages'
CLAUDE_MODEL = 'claude-sonnet-4-5-20250929'
PROJECT_DIR = Path(__file__).parent

class TradingAgent:
    """Production-ready trading agent with complete automation"""
    
    def __init__(self):
        self.project_dir = PROJECT_DIR
        self.portfolio_file = self.project_dir / 'portfolio_data' / 'current_portfolio.json'
        self.account_file = self.project_dir / 'portfolio_data' / 'account_status.json'
        self.trades_csv = self.project_dir / 'trade_history' / 'completed_trades.csv'
        self.exclusions_file = self.project_dir / 'strategy_evolution' / 'catalyst_exclusions.json'
        
    def fetch_current_prices(self, tickers):
        """Fetch current prices for list of tickers using yfinance"""
        
        try:
            import yfinance as yf
        except ImportError:
            print("   ⚠️ yfinance not installed - using entry prices")
            return {}
        
        prices = {}
        
        print(f"   Fetching prices for {len(tickers)} tickers...")
        
        try:
            # Fetch all tickers at once for efficiency
            tickers_str = ' '.join(tickers)
            data = yf.download(tickers_str, period='1d', interval='1m', progress=False)
            
            if len(tickers) == 1:
                # Single ticker
                if not data.empty and 'Close' in data.columns:
                    prices[tickers[0]] = float(data['Close'].iloc[-1])
            else:
                # Multiple tickers
                if not data.empty and 'Close' in data.columns:
                    for ticker in tickers:
                        try:
                            price = float(data['Close'][ticker].iloc[-1])
                            prices[ticker] = price
                        except:
                            print(f"   ⚠️ Could not fetch price for {ticker}")
            
            print(f"   ✓ Fetched {len(prices)}/{len(tickers)} prices")
            
        except Exception as e:
            print(f"   ⚠️ Price fetch error: {e}")
        
        return prices
    
    def check_position_exits(self, position, current_price):
        """Check if position should be closed based on stops/targets"""
        
        entry_price = position['entry_price']
        stop_loss = position.get('stop_loss', entry_price * 0.93)  # Default -7%
        price_target = position.get('price_target', entry_price * 1.10)  # Default +10%
        
        # Calculate current return
        return_pct = ((current_price - entry_price) / entry_price) * 100
        
        # Check stop loss
        if current_price <= stop_loss:
            return True, 'Stop Loss Hit', return_pct
        
        # Check price target
        if current_price >= price_target:
            return True, 'Price Target Reached', return_pct
        
        # Check time stop (21 days)
        entry_date = datetime.strptime(position['entry_date'], '%Y-%m-%d')
        days_held = (datetime.now() - entry_date).days
        
        if days_held >= 21:
            return True, 'Time Stop (21 days)', return_pct
        
        return False, 'Hold', return_pct
    
    def close_position(self, position, exit_price, exit_reason):
        """Close a position and prepare for CSV logging"""
        
        entry_price = position['entry_price']
        shares = position['shares']
        
        # Calculate returns
        return_pct = ((exit_price - entry_price) / entry_price) * 100
        return_dollars = (exit_price - entry_price) * shares
        
        # Calculate hold time
        entry_date = datetime.strptime(position['entry_date'], '%Y-%m-%d')
        exit_date = datetime.now()
        hold_days = (exit_date - entry_date).days
        
        # Load current account value
        account_data = {}
        if self.account_file.exists():
            with open(self.account_file, 'r') as f:
                account_data = json.load(f)
        
        account_value_after = account_data.get('account_value', 1000.00)
        
        # Create trade record for CSV
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
    
    def update_portfolio_prices_and_check_exits(self):
        """
        CRITICAL FUNCTION - The heart of the analyze command
        
        1. Fetch current prices for all positions
        2. Update P&L for each position
        3. Check if any stops/targets hit
        4. Close positions that need to be closed
        5. Update portfolio and account JSON files
        6. Log closed trades to CSV
        """
        
        print("\n" + "="*60)
        print("PORTFOLIO UPDATE & EXIT CHECKING")
        print("="*60 + "\n")
        
        # Load current portfolio
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
        
        # Get all tickers
        tickers = [pos['ticker'] for pos in positions]
        
        # Fetch current prices
        print("\n2. Fetching current market prices...")
        current_prices = self.fetch_current_prices(tickers)
        
        # Update positions and check exits
        print("\n3. Checking for exits (stops/targets)...")
        
        updated_positions = []
        closed_positions = []
        closed_trades = []
        
        total_unrealized_pnl = 0
        
        for position in positions:
            ticker = position['ticker']
            
            # Get current price (or keep entry price if fetch failed)
            if ticker in current_prices:
                current_price = current_prices[ticker]
            else:
                current_price = position.get('current_price', position['entry_price'])
                print(f"   ⚠️ Using last known price for {ticker}: ${current_price:.2f}")
            
            # Update position with current price
            position['current_price'] = current_price
            
            # Calculate P&L
            entry_price = position['entry_price']
            shares = position['shares']
            
            unrealized_gain_pct = ((current_price - entry_price) / entry_price) * 100
            unrealized_gain_dollars = (current_price - entry_price) * shares
            
            position['unrealized_gain_pct'] = unrealized_gain_pct
            position['unrealized_gain_dollars'] = unrealized_gain_dollars
            
            # Update days held
            entry_date = datetime.strptime(position['entry_date'], '%Y-%m-%d')
            position['days_held'] = (datetime.now() - entry_date).days
            
            # Check if should exit
            should_exit, reason, return_pct = self.check_position_exits(position, current_price)
            
            if should_exit:
                print(f"   🚪 CLOSING {ticker}: {reason} ({return_pct:+.2f}%)")
                
                # Close the position
                trade_data = self.close_position(position, current_price, reason)
                closed_trades.append(trade_data)
                closed_positions.append(position)
                
            else:
                # Keep position open
                updated_positions.append(position)
                total_unrealized_pnl += unrealized_gain_dollars
                
                status = "🟢" if unrealized_gain_pct > 0 else "🔴"
                print(f"   {status} HOLDING {ticker}: {unrealized_gain_pct:+.2f}% (${unrealized_gain_dollars:+.2f})")
        
        print(f"\n4. Results:")
        print(f"   • Still open: {len(updated_positions)} positions")
        print(f"   • Closed: {len(closed_positions)} positions")
        print(f"   • Total unrealized P&L: ${total_unrealized_pnl:+.2f}")
        
        # Update portfolio JSON
        print("\n5. Updating portfolio JSON...")
        
        portfolio['positions'] = updated_positions
        portfolio['closed_positions'] = closed_positions  # Keep for reference
        portfolio['total_positions'] = len(updated_positions)
        portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        portfolio['portfolio_status'] = f"Active - {len(updated_positions)} positions"
        
        with open(self.portfolio_file, 'w') as f:
            json.dump(portfolio, f, indent=2)
        
        print("   ✓ Portfolio updated")
        
        # Update account status
        print("\n6. Updating account status...")
        self.update_account_status(updated_positions, closed_trades)
        print("   ✓ Account status updated")
        
        # Log closed trades to CSV
        if closed_trades:
            print(f"\n7. Logging {len(closed_trades)} closed trades to CSV...")
            for trade in closed_trades:
                self.log_completed_trade(trade)
            print("   ✓ Trades logged")
        
        print("\n" + "="*60)
        print("PORTFOLIO UPDATE COMPLETE")
        print("="*60 + "\n")
        
        return closed_trades
    
    def update_account_status(self, open_positions, closed_trades):
        """Update account_status.json with latest metrics"""
        
        # Load current account data
        if self.account_file.exists():
            with open(self.account_file, 'r') as f:
                account = json.load(f)
        else:
            account = {
                'account_value': 1000.00,
                'starting_capital': 1000.00,
                'total_return_dollars': 0.00,
                'total_return_percent': 0.00,
                'total_trading_days': 0,
                'total_trades_completed': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'overall_win_rate': 0.00,
                'current_win_streak': 0,
                'current_loss_streak': 0,
                'longest_win_streak': 0,
                'longest_loss_streak': 0,
                'best_trade': {'ticker': '', 'date': '', 'return_percent': 0.00, 'return_dollars': 0.00},
                'worst_trade': {'ticker': '', 'date': '', 'return_percent': 0.00, 'return_dollars': 0.00},
                'best_day': {'date': '', 'portfolio_return_percent': 0.00, 'portfolio_return_dollars': 0.00},
                'worst_day': {'date': '', 'portfolio_return_percent': 0.00, 'portfolio_return_dollars': 0.00},
                'average_hold_time_days': 0.00,
                'average_winner_percent': 0.00,
                'average_loser_percent': 0.00,
                'largest_drawdown_percent': 0.00
            }
        
        # Calculate current portfolio value
        cash = account.get('cash_remaining', 0.00)
        invested = sum(pos['position_size'] for pos in open_positions)
        unrealized_pnl = sum(pos.get('unrealized_gain_dollars', 0) for pos in open_positions)
        
        current_value = cash + invested + unrealized_pnl
        
        # Update with closed trades
        for trade in closed_trades:
            account['total_trades_completed'] += 1
            
            if trade['return_percent'] > 0:
                account['winning_trades'] += 1
                account['current_win_streak'] += 1
                account['current_loss_streak'] = 0
                
                if account['current_win_streak'] > account['longest_win_streak']:
                    account['longest_win_streak'] = account['current_win_streak']
            else:
                account['losing_trades'] += 1
                account['current_loss_streak'] += 1
                account['current_win_streak'] = 0
                
                if account['current_loss_streak'] > account['longest_loss_streak']:
                    account['longest_loss_streak'] = account['current_loss_streak']
            
            # Update best/worst trade
            if trade['return_percent'] > account['best_trade']['return_percent']:
                account['best_trade'] = {
                    'ticker': trade['ticker'],
                    'date': trade['exit_date'],
                    'return_percent': trade['return_percent'],
                    'return_dollars': trade['return_dollars']
                }
            
            if trade['return_percent'] < account['worst_trade']['return_percent']:
                account['worst_trade'] = {
                    'ticker': trade['ticker'],
                    'date': trade['exit_date'],
                    'return_percent': trade['return_percent'],
                    'return_dollars': trade['return_dollars']
                }
        
        # Update overall stats
        account['account_value'] = current_value
        account['cash_remaining'] = cash
        account['total_invested'] = invested
        account['total_return_dollars'] = current_value - account['starting_capital']
        account['total_return_percent'] = ((current_value - account['starting_capital']) / account['starting_capital']) * 100
        
        if account['total_trades_completed'] > 0:
            account['overall_win_rate'] = (account['winning_trades'] / account['total_trades_completed']) * 100
        
        # Calculate averages from CSV
        if self.trades_csv.exists():
            winners = []
            losers = []
            hold_times = []
            
            with open(self.trades_csv, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Trade_ID'):
                        return_pct = float(row.get('Return_Percent', 0))
                        hold_days = int(row.get('Hold_Days', 0))
                        
                        hold_times.append(hold_days)
                        
                        if return_pct > 0:
                            winners.append(return_pct)
                        else:
                            losers.append(return_pct)
            
            if hold_times:
                account['average_hold_time_days'] = sum(hold_times) / len(hold_times)
            
            if winners:
                account['average_winner_percent'] = sum(winners) / len(winners)
            
            if losers:
                account['average_loser_percent'] = sum(losers) / len(losers)
        
        account['last_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        # Save updated account
        with open(self.account_file, 'w') as f:
            json.dump(account, f, indent=2)
    
    def call_claude_api(self, command, context):
        """Call Claude API with optimized context"""
        
        if not CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY environment variable not set")
        
        headers = {
            'x-api-key': CLAUDE_API_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }
        
        if command == 'go':
            user_message = """Execute the 'go' command: Build/update the 10-position portfolio.

CRITICAL OUTPUT REQUIREMENT:
At the END of your analysis, you MUST output a JSON block in this EXACT format:
```json
{
  "positions": [
    {
      "ticker": "AAPL",
      "entry_price": 175.50,
      "shares": 57.0,
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
            'max_tokens': 16000,
            'system': system_prompt,
            'messages': [{'role': 'user', 'content': user_message}]
        }
        
        try:
            response = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Claude API call failed: {e}")
    
    def load_optimized_context(self, command):
        """Load only essential context to stay within token limits"""
        
        context = {}
        
        instructions_file = self.project_dir / 'PROJECT_INSTRUCTIONS.md'
        if instructions_file.exists():
            context['instructions'] = instructions_file.read_text()
        
        strategy_file = self.project_dir / 'strategy_evolution' / 'strategy_rules.md'
        if strategy_file.exists():
            context['strategy'] = strategy_file.read_text()
        
        exclusions = self.load_catalyst_exclusions()
        if exclusions:
            context['exclusions'] = json.dumps(exclusions, indent=2)
        
        if command == 'go':
            if self.portfolio_file.exists():
                context['portfolio'] = self.portfolio_file.read_text()
            
            if self.account_file.exists():
                context['account'] = self.account_file.read_text()
            
            lessons_file = self.project_dir / 'strategy_evolution' / 'lessons_learned.md'
            if lessons_file.exists():
                with open(lessons_file, 'r') as f:
                    lines = f.readlines()
                    context['lessons'] = ''.join(lines[-500:])
        
        elif command == 'analyze':
            if self.portfolio_file.exists():
                context['portfolio'] = self.portfolio_file.read_text()
            
            if self.account_file.exists():
                context['account'] = self.account_file.read_text()
        
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
    
    def extract_json_from_response(self, response_text):
        """Extract JSON block from Claude's response"""
        
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        
        if json_match:
            try:
                json_str = json_match.group(1)
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"   ⚠️ JSON parsing error: {e}")
                return None
        
        json_match = re.search(r'\{[\s\S]*"positions"[\s\S]*\}', response_text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        return None
    
    def update_portfolio_from_json(self, portfolio_data):
        """Update portfolio files from parsed JSON"""
        
        if not portfolio_data or 'positions' not in portfolio_data:
            print("   ⚠️ No valid portfolio data to update")
            return False
        
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        positions = []
        for pos in portfolio_data['positions']:
            position = {
                "ticker": pos.get('ticker', ''),
                "entry_date": datetime.now().strftime('%Y-%m-%d'),
                "entry_price": float(pos.get('entry_price', 0)),
                "shares": float(pos.get('shares', 0)),
                "position_size": float(pos.get('entry_price', 0)) * float(pos.get('shares', 0)),
                "current_price": float(pos.get('entry_price', 0)),
                "unrealized_gain_pct": 0.00,
                "unrealized_gain_dollars": 0.00,
                "catalyst": pos.get('catalyst', ''),
                "sector": pos.get('sector', ''),
                "confidence": pos.get('confidence', 'Medium'),
                "stop_loss": float(pos.get('stop_loss', 0)),
                "price_target": float(pos.get('price_target', 0)),
                "thesis": pos.get('thesis', ''),
                "days_held": 0
            }
            positions.append(position)
        
        portfolio_file_data = {
            "last_updated": now,
            "portfolio_status": f"Active - {len(positions)} positions",
            "total_positions": len(positions),
            "positions": positions,
            "closed_positions": []  # Initialize for later use
        }
        
        with open(self.portfolio_file, 'w') as f:
            json.dump(portfolio_file_data, f, indent=2)
        
        print(f"   ✓ Updated portfolio: {len(positions)} positions")
        
        total_invested = sum(p['position_size'] for p in positions)
        cash_remaining = 1000.00 - total_invested
        total_value = total_invested + cash_remaining

        account_data = {
            "account_value": total_value,
            "cash_remaining": cash_remaining,
            "total_invested": total_invested,
            "starting_capital": 1000.00,
            "total_return_dollars": 0.00,
            "total_return_percent": 0.00,
            "total_trading_days": 1,
            "total_trades_completed": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "overall_win_rate": 0.00,
            "current_win_streak": 0,
            "current_loss_streak": 0,
            "longest_win_streak": 0,
            "longest_loss_streak": 0,
            "best_trade": {"ticker": "", "date": "", "return_percent": 0.00, "return_dollars": 0.00},
            "worst_trade": {"ticker": "", "date": "", "return_percent": 0.00, "return_dollars": 0.00},
            "best_day": {"date": "", "portfolio_return_percent": 0.00, "portfolio_return_dollars": 0.00},
            "worst_day": {"date": "", "portfolio_return_percent": 0.00, "portfolio_return_dollars": 0.00},
            "average_hold_time_days": 0.00,
            "average_winner_percent": 0.00,
            "average_loser_percent": 0.00,
            "largest_drawdown_percent": 0.00,
            "last_updated": now
        }
        
        with open(self.account_file, 'w') as f:
            json.dump(account_data, f, indent=2)
        
        print(f"   ✓ Updated account status: ${total_value:.2f}")
        
        return True
    
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
                violations.append(f"⚠️ WARNING: {excluded['catalyst']} (win rate: {excluded['win_rate']:.1f}%) was mentioned despite being excluded")
        
        return len(violations) == 0, violations
    
    def log_completed_trade(self, trade_data):
        """Write completed trade to CSV for learning"""
        
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
        
        print(f"   ✓ Logged trade to CSV: {trade_data.get('ticker')} ({trade_data.get('return_percent', 0):.2f}%)")
    
    def save_response(self, command, response_data):
        """Save API response to file"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_dir = self.project_dir / 'daily_reviews'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        response_text = response_data.get('content', [{}])[0].get('text', '')
        
        filename = f"{timestamp}_{command}.md"
        output_file = output_dir / filename
        
        with open(output_file, 'w') as f:
            f.write(f"# {command.upper()} Command Response\n\n")
            f.write(f"**Timestamp:** {timestamp}\n\n")
            f.write("---\n\n")
            f.write(response_text)
        
        print(f"   ✓ Response saved to: {output_file}")
    
    def execute_go_command(self):
        """Execute morning 'go' command with validation"""
        
        print("\n" + "="*60)
        print("EXECUTING 'GO' COMMAND - MORNING TRADING DECISIONS")
        print("="*60 + "\n")
        
        print("1. Loading optimized context...")
        context = self.load_optimized_context('go')
        print("   ✓ Context loaded\n")
        
        print("2. Calling Claude API for trading decisions...")
        response = self.call_claude_api('go', context)
        response_text = response.get('content', [{}])[0].get('text', '')
        print("   ✓ Response received\n")
        
        print("3. Parsing portfolio data from response...")
        portfolio_json = self.extract_json_from_response(response_text)
        
        if portfolio_json:
            print("   ✓ JSON extracted successfully\n")
            
            print("4. Updating portfolio files...")
            success = self.update_portfolio_from_json(portfolio_json)
            
            if success:
                print("   ✓ Portfolio files updated\n")
            else:
                print("   ⚠️ Portfolio update failed\n")
        else:
            print("   ⚠️ No JSON found in response - portfolio not updated\n")
        
        print("5. Validating trade decisions against learned rules...")
        is_valid, violations = self.validate_trade_decisions(response_text)
        
        if violations:
            print("   ⚠️ VALIDATION WARNINGS:")
            for v in violations:
                print(f"      {v}")
            print()
        else:
            print("   ✓ All decisions validated\n")
        
        print("6. Saving response...")
        self.save_response('go', response)
        print("   ✓ Complete\n")
        
        return True
    
    def execute_analyze_command(self):
        """
        Execute evening 'analyze' command with COMPLETE functionality:
        - Fetch current prices
        - Update portfolio
        - Check exits
        - Log trades to CSV
        - Update account status
        """
        
        print("\n" + "="*60)
        print("EXECUTING 'ANALYZE' COMMAND - EVENING PERFORMANCE UPDATE")
        print("="*60 + "\n")
        
        # CRITICAL NEW STEP: Update portfolio with real prices and check exits
        closed_trades = self.update_portfolio_prices_and_check_exits()
        
        # Now call Claude for analysis and commentary
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
        
        # Summary
        print("="*60)
        print("ANALYZE COMMAND COMPLETE")
        print("="*60)
        if closed_trades:
            print(f"\n✓ {len(closed_trades)} positions closed and logged")
        print()
        
        return True
    
    def execute_learn_command(self, tier='daily'):
        """Execute learning command (daily/weekly/monthly)"""
        
        print("\n" + "="*60)
        print(f"EXECUTING 'LEARN' COMMAND - {tier.upper()} LEARNING CYCLE")
        print("="*60 + "\n")
        
        try:
            if tier == 'daily':
                from learn_daily import DailyLearning
                engine = DailyLearning()
            elif tier == 'weekly':
                from learn_weekly import WeeklyLearning
                engine = WeeklyLearning()
            elif tier == 'monthly':
                from learn_monthly import MonthlyLearning
                engine = MonthlyLearning()
            else:
                raise ValueError(f"Unknown learning tier: {tier}")
            
            engine.run_learning_cycle()
            return True
            
        except ImportError as e:
            print(f"   ✗ Learning module not found: {e}")
            print(f"   ℹ Ensure learn_{tier}.py is in the project directory")
            return False
        except Exception as e:
            print(f"   ✗ Learning cycle failed: {e}")
            traceback.print_exc()
            return False

def main():
    """Main execution"""
    
    if len(sys.argv) < 2:
        print("Usage: python agent.py [go|analyze|learn-daily|learn-weekly|learn-monthly]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    print(f"\n{'='*60}")
    print(f"Paper Trading Lab Agent v4.0")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print(f"{'='*60}")
    
    agent = TradingAgent()
    
    try:
        if command == 'go':
            success = agent.execute_go_command()
        elif command == 'analyze':
            success = agent.execute_analyze_command()
        elif command in ['learn-daily', 'learn-weekly', 'learn-monthly']:
            tier = command.split('-')[1]
            success = agent.execute_learn_command(tier)
        else:
            print(f"\nERROR: Unknown command '{command}'")
            print("Valid commands: go, analyze, learn-daily, learn-weekly, learn-monthly")
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
    