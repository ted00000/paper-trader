#!/usr/bin/env python3
"""
Paper Trading Lab - Agent v4.3
CRITICAL FIXES:
1. Split GO (selection @8:45) from EXECUTE (entry with real 9:31 prices)
2. Fixed account calculation (includes realized P&L from CSV)
3. Real market open prices for entries

Usage:
  python3 agent.py go       # 8:45 AM - Select stocks, save to pending
  python3 agent.py execute  # 9:31 AM - Enter with real open prices
  python3 agent.py analyze  # 4:30 PM - Update & close positions
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
CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages'
CLAUDE_MODEL = 'claude-sonnet-4-5-20250929'
PROJECT_DIR = Path(__file__).parent

class TradingAgent:
    """Production-ready trading agent v4.3"""
    
    def __init__(self):
        self.project_dir = PROJECT_DIR
        self.portfolio_file = self.project_dir / 'portfolio_data' / 'current_portfolio.json'
        self.account_file = self.project_dir / 'portfolio_data' / 'account_status.json'
        self.trades_csv = self.project_dir / 'trade_history' / 'completed_trades.csv'
        self.pending_file = self.project_dir / 'portfolio_data' / 'pending_positions.json'
        self.exclusions_file = self.project_dir / 'strategy_evolution' / 'catalyst_exclusions.json'
    
    def fetch_current_prices(self, tickers):
        """Fetch current prices using Alpha Vantage API"""
        
        if not ALPHAVANTAGE_API_KEY:
            print("   ⚠️ ALPHAVANTAGE_API_KEY not set - using entry prices")
            return {}
        
        prices = {}
        
        print(f"   Fetching prices for {len(tickers)} tickers via Alpha Vantage...")
        
        for i, ticker in enumerate(tickers, 1):
            try:
                url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHAVANTAGE_API_KEY}'
                response = requests.get(url, timeout=10)
                data = response.json()
                
                if 'Global Quote' in data and data['Global Quote']:
                    price = float(data['Global Quote']['05. price'])
                    prices[ticker] = price
                    print(f"   [{i}/{len(tickers)}] {ticker}: ${price:.2f}")
                else:
                    print(f"   [{i}/{len(tickers)}] {ticker}: No data")
                
                time.sleep(12)
                
            except Exception as e:
                print(f"   [{i}/{len(tickers)}] {ticker}: Error - {e}")
        
        return prices
    
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
            user_message = """Execute the 'go' command: Analyze pre-market and select 10 stocks.

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
      "thesis": "Strong Q4 earnings",
      "stop_loss": 163.28,
      "price_target": 193.05
    }
  ],
  "total_positions": 10
}
```

Include your analysis BEFORE the JSON block."""
        else:
            user_message = command
        
        system_prompt = f"""You are the Paper Trading Lab assistant.

Project Context:
{context}

Execute the user's command following the PROJECT_INSTRUCTIONS.md guidelines.
Pay special attention to CATALYST EXCLUSIONS - do not use any catalyst types that are marked as excluded."""
        
        payload = {
            'model': CLAUDE_MODEL,
            'max_tokens': 4096,
            'system': system_prompt,
            'messages': [{'role': 'user', 'content': user_message}]
        }
        
        response = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        return response.json()
    
    def load_optimized_context(self, command):
        """Load optimized context for command"""
        
        context = {}
        
        instructions_file = self.project_dir / 'PROJECT_INSTRUCTIONS.md'
        if instructions_file.exists():
            context['instructions'] = instructions_file.read_text()[:5000]
        
        strategy_file = self.project_dir / 'strategy_evolution' / 'strategy_rules.md'
        if strategy_file.exists():
            context['strategy'] = strategy_file.read_text()
        
        exclusions = self.load_catalyst_exclusions()
        if exclusions:
            context['exclusions'] = '\n'.join([f"- {e['catalyst']}: {e.get('reason', 'Poor performance')}" for e in exclusions])
        else:
            context['exclusions'] = 'None'
        
        if self.portfolio_file.exists():
            context['portfolio'] = self.portfolio_file.read_text()
        
        if self.account_file.exists():
            context['account'] = self.account_file.read_text()
        
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
    
    def save_response(self, command, response):
        """Save Claude's response to daily_reviews"""
        
        reviews_dir = self.project_dir / 'daily_reviews'
        reviews_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = reviews_dir / f"{timestamp}_{command}.md"
        
        response_text = response.get('content', [{}])[0].get('text', '')
        
        with open(filename, 'w') as f:
            f.write(f"# {command.upper()} Command Response\n\n")
            f.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}\n\n")
            f.write(response_text)
    
    def validate_trade_decisions(self, response_text):
        """Validate that Claude's picks don't violate learned rules"""
        
        exclusions = self.load_catalyst_exclusions()
        
        if not exclusions:
            return True, []
        
        violations = []
        
        for exc in exclusions:
            catalyst = exc.get('catalyst', '')
            if catalyst.lower() in response_text.lower():
                violations.append(f"Possible use of excluded catalyst: {catalyst}")
        
        return len(violations) == 0, violations
    
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
                "position_size": float(pos.get('position_size', 100)),
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
            "closed_positions": []
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
        
        return True
    
    def execute_go_command(self):
        """Execute GO command: Select stocks at 8:45 AM, save to pending"""
        
        print("\n" + "="*60)
        print("EXECUTING 'GO' - STOCK SELECTION (Pre-Market)")
        print("="*60 + "\n")
        
        print("1. Loading optimized context...")
        context = self.load_optimized_context('go')
        print("   ✓ Context loaded\n")
        
        print("2. Calling Claude API for stock selection...")
        response = self.call_claude_api('go', context)
        print("   ✓ Response received\n")
        
        response_text = response.get('content', [{}])[0].get('text', '')
        
        print("3. Extracting JSON from response...")
        portfolio_json = self.extract_json_from_response(response_text)
        
        if portfolio_json:
            portfolio_json['selection_time'] = datetime.now().isoformat()
            with open(self.pending_file, 'w') as f:
                json.dump(portfolio_json, f, indent=2)
            print(f"   ✓ Saved {len(portfolio_json.get('positions', []))} selections to pending\n")
        else:
            print("   ⚠️ No JSON found - selections not saved\n")
        
        print("4. Validating selections...")
        is_valid, violations = self.validate_trade_decisions(response_text)
        
        if violations:
            print("   ⚠️ VALIDATION WARNINGS:")
            for v in violations:
                print(f"      {v}")
            print()
        else:
            print("   ✓ All selections validated\n")
        
        print("5. Saving response...")
        self.save_response('go', response)
        print("   ✓ Complete\n")
        
        return True
    
    def execute_execute_command(self):
        """Execute EXECUTE command: Enter positions at 9:31 AM with real prices"""
        
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
        
        print("2. Fetching real market open prices...")
        tickers = [p['ticker'] for p in positions]
        real_prices = self.fetch_current_prices(tickers)
        print()
        
        print("3. Updating positions with real prices...")
        for pos in positions:
            ticker = pos['ticker']
            if ticker in real_prices:
                pos['entry_price'] = real_prices[ticker]
                pos['current_price'] = real_prices[ticker]
                pos['shares'] = pos.get('position_size', 100) / real_prices[ticker]
                print(f"   ✓ {ticker}: Entry=${real_prices[ticker]:.2f}, Shares={pos['shares']:.2f}")
            else:
                print(f"   ⚠️ {ticker}: Using estimated price ${pos.get('entry_price', 0):.2f}")
        print()
        
        print("4. Creating portfolio...")
        success = self.update_portfolio_from_json({'positions': positions})
        
        if success:
            print("   ✓ Portfolio created\n")
            
            print("5. Deleting pending file...")
            self.pending_file.unlink()
            print("   ✓ Pending file deleted\n")
        else:
            print("   ✗ Portfolio creation failed\n")
        
        return success
    
    def check_position_exits(self, position, current_price):
        """Check if position should be closed (stop loss or profit target)"""
        
        entry_price = position['entry_price']
        stop_loss = position.get('stop_loss', 0)
        price_target = position.get('price_target', 0)
        
        return_pct = ((current_price - entry_price) / entry_price) * 100
        
        if stop_loss > 0 and current_price <= stop_loss:
            return True, "Stop Loss Hit", return_pct
        
        if price_target > 0 and current_price >= price_target:
            return True, "Price Target Reached", return_pct
        
        return False, "", return_pct
    
    def close_position(self, position, exit_price, exit_reason):
        """Close a position and create trade record"""
        
        entry_price = position['entry_price']
        shares = position['shares']
        
        return_pct = ((exit_price - entry_price) / entry_price) * 100
        return_dollars = (exit_price - entry_price) * shares
        
        entry_date = datetime.strptime(position['entry_date'], '%Y-%m-%d')
        exit_date = datetime.now()
        hold_days = (exit_date - entry_date).days
        
        if self.account_file.exists():
            with open(self.account_file, 'r') as f:
                account_data = json.load(f)
        else:
            account_data = {}
        
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
        """Log a completed trade to CSV"""
        
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
    
    def update_portfolio_prices_and_check_exits(self):
        """Update prices and check for exits"""
        
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
        
        print("\n3. Checking for exits (stops/targets)...")
        
        updated_positions = []
        closed_positions = []
        closed_trades = []
        
        total_unrealized_pnl = 0
        
        for position in positions:
            ticker = position['ticker']
            
            if ticker in current_prices:
                current_price = current_prices[ticker]
            else:
                current_price = position.get('current_price', position['entry_price'])
                print(f"   ⚠️ Using last known price for {ticker}: ${current_price:.2f}")
            
            position['current_price'] = current_price
            
            entry_price = position['entry_price']
            shares = position['shares']
            
            unrealized_gain_pct = ((current_price - entry_price) / entry_price) * 100
            unrealized_gain_dollars = (current_price - entry_price) * shares
            
            position['unrealized_gain_pct'] = unrealized_gain_pct
            position['unrealized_gain_dollars'] = unrealized_gain_dollars
            
            entry_date = datetime.strptime(position['entry_date'], '%Y-%m-%d')
            position['days_held'] = (datetime.now() - entry_date).days
            
            should_exit, reason, return_pct = self.check_position_exits(position, current_price)
            
            if should_exit:
                print(f"   🚪 CLOSING {ticker}: {reason} ({return_pct:+.2f}%)")
                
                trade_data = self.close_position(position, current_price, reason)
                closed_trades.append(trade_data)
                closed_positions.append(position)
                
            else:
                updated_positions.append(position)
                total_unrealized_pnl += unrealized_gain_dollars
                
                status = "🟢" if unrealized_gain_pct > 0 else "🔴"
                print(f"   {status} HOLDING {ticker}: {unrealized_gain_pct:+.2f}% (${unrealized_gain_dollars:+.2f})")
        
        print(f"\n4. Results:")
        print(f"   • Still open: {len(updated_positions)} positions")
        print(f"   • Closed: {len(closed_positions)} positions")
        print(f"   • Total unrealized P&L: ${total_unrealized_pnl:+.2f}")
        
        print("\n5. Updating portfolio JSON...")
        
        portfolio['positions'] = updated_positions
        portfolio['closed_positions'] = closed_positions
        portfolio['total_positions'] = len(updated_positions)
        portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        portfolio['portfolio_status'] = f"Active - {len(updated_positions)} positions"
        
        with open(self.portfolio_file, 'w') as f:
            json.dump(portfolio, f, indent=2)
        
        print("   ✓ Portfolio updated")
        
        print("\n6. Updating account status...")
        self.update_account_status(updated_positions, closed_trades)
        print("   ✓ Account status updated")
        
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
        """Update account_status.json - FIXED to include realized P&L from CSV"""
        
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
        
        # ⭐ KEY FIX: Read realized P&L from CSV
        realized_pnl = 0.00
        if self.trades_csv.exists():
            try:
                with open(self.trades_csv, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('Return_Dollars'):
                            realized_pnl += float(row['Return_Dollars'])
            except Exception as e:
                print(f"   ⚠️ Error reading trades CSV: {e}")
        
        # Calculate unrealized P&L from open positions
        original_investment_open = sum(pos['position_size'] for pos in open_positions)
        unrealized_pnl = sum(pos.get('unrealized_gain_dollars', 0) for pos in open_positions)
        
        # ⭐ CORRECT CALCULATION:
        starting_capital = 1000.00
        account_value = starting_capital + realized_pnl + unrealized_pnl
        cash_remaining = starting_capital + realized_pnl - original_investment_open
        
        # Update stats from closed_trades in current batch
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
            
            if trade['return_percent'] > account['best_trade']['return_percent']:
                account['best_trade'] = {
                    'ticker': trade['ticker'],
                    'date': trade['exit_date'],
                    'return_percent': trade['return_percent'],
                    'return_dollars': trade['return_dollars']
                }
            
            if not account['worst_trade']['ticker'] or trade['return_percent'] < account['worst_trade']['return_percent']:
                account['worst_trade'] = {
                    'ticker': trade['ticker'],
                    'date': trade['exit_date'],
                    'return_percent': trade['return_percent'],
                    'return_dollars': trade['return_dollars']
                }
        
        # Update overall account stats with CORRECT values
        account['account_value'] = round(account_value, 2)
        account['cash_remaining'] = round(cash_remaining, 2)
        account['total_invested'] = round(original_investment_open, 2)
        account['realized_pnl'] = round(realized_pnl, 2)
        account['unrealized_pnl'] = round(unrealized_pnl, 2)
        account['starting_capital'] = starting_capital
        
        total_return_dollars = realized_pnl + unrealized_pnl
        account['total_return_dollars'] = round(total_return_dollars, 2)
        account['total_return_percent'] = round((total_return_dollars / starting_capital) * 100, 2)
        
        if account['total_trades_completed'] > 0:
            account['overall_win_rate'] = round((account['winning_trades'] / account['total_trades_completed']) * 100, 2)
        
        # Calculate averages from CSV
        if self.trades_csv.exists():
            winners = []
            losers = []
            hold_times = []
            
            try:
                with open(self.trades_csv, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('Return_Percent'):
                            return_pct = float(row['Return_Percent'])
                            if return_pct > 0:
                                winners.append(return_pct)
                            elif return_pct < 0:
                                losers.append(return_pct)
                        
                        if row.get('Hold_Days'):
                            hold_times.append(float(row['Hold_Days']))
                
                if winners:
                    account['average_winner_percent'] = round(sum(winners) / len(winners), 2)
                if losers:
                    account['average_loser_percent'] = round(sum(losers) / len(losers), 2)
                if hold_times:
                    account['average_hold_time_days'] = round(sum(hold_times) / len(hold_times), 2)
            except Exception as e:
                print(f"   ⚠️ Error calculating averages: {e}")
        
        account['last_updated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        with open(self.account_file, 'w') as f:
            json.dump(account, f, indent=2)
    
    def execute_analyze_command(self):
        """Execute ANALYZE command: Update prices and check exits"""
        
        print("\n" + "="*60)
        print("EXECUTING 'ANALYZE' - EVENING PERFORMANCE UPDATE")
        print("="*60 + "\n")
        
        closed_trades = self.update_portfolio_prices_and_check_exits()
        
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
            print(f"\n✓ {len(closed_trades)} positions closed and logged")
        print()
        
        return True

def main():
    """Main execution"""
    
    if len(sys.argv) < 2:
        print("Usage: python agent.py [go|execute|analyze]")
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
    