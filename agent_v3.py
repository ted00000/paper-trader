#!/usr/bin/env python3
"""
Paper Trading Lab - Production Agent v3.0
COMPLETE WORKING VERSION with JSON parsing and portfolio updates

Key improvements over v2.0:
- Claude outputs structured JSON
- Agent parses JSON and updates portfolio files
- Proper error handling
- Complete closed loop
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
    """Production-ready trading agent with complete JSON parsing"""
    
    def __init__(self):
        self.project_dir = PROJECT_DIR
        self.portfolio_file = self.project_dir / 'portfolio_data' / 'current_portfolio.json'
        self.account_file = self.project_dir / 'portfolio_data' / 'account_status.json'
        self.trades_csv = self.project_dir / 'trade_history' / 'completed_trades.csv'
        self.exclusions_file = self.project_dir / 'strategy_evolution' / 'catalyst_exclusions.json'
        
    def call_claude_api(self, command, context):
        """Call Claude API with optimized context"""
        
        if not CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY environment variable not set")
        
        headers = {
            'x-api-key': CLAUDE_API_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }
        
        # CRITICAL FIX: Enhanced prompt that demands JSON output
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
        
        # Always load: Instructions, Strategy, Exclusions
        instructions_file = self.project_dir / 'PROJECT_INSTRUCTIONS.md'
        if instructions_file.exists():
            context['instructions'] = instructions_file.read_text()
        
        strategy_file = self.project_dir / 'strategy_evolution' / 'strategy_rules.md'
        if strategy_file.exists():
            context['strategy'] = strategy_file.read_text()
        
        # Load catalyst exclusions (CRITICAL)
        exclusions = self.load_catalyst_exclusions()
        if exclusions:
            context['exclusions'] = json.dumps(exclusions, indent=2)
        
        # For 'go' command: load portfolio and recent lessons
        if command == 'go':
            if self.portfolio_file.exists():
                context['portfolio'] = self.portfolio_file.read_text()
            
            if self.account_file.exists():
                context['account'] = self.account_file.read_text()
            
            # Load only LAST 500 lines of lessons (most recent)
            lessons_file = self.project_dir / 'strategy_evolution' / 'lessons_learned.md'
            if lessons_file.exists():
                with open(lessons_file, 'r') as f:
                    lines = f.readlines()
                    context['lessons'] = ''.join(lines[-500:])
        
        # For 'analyze' command: load portfolio and trade history
        elif command == 'analyze':
            if self.portfolio_file.exists():
                context['portfolio'] = self.portfolio_file.read_text()
            
            if self.account_file.exists():
                context['account'] = self.account_file.read_text()
        
        # Format context string
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
        
        # Look for JSON code block
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
        """Update portfolio files from parsed JSON"""
        
        if not portfolio_data or 'positions' not in portfolio_data:
            print("   ⚠️ No valid portfolio data to update")
            return False
        
        # Build complete portfolio structure
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
        
        # Update portfolio file
        portfolio_file_data = {
            "last_updated": now,
            "portfolio_status": f"Active - {len(positions)} positions",
            "total_positions": len(positions),
            "positions": positions
        }
        
        with open(self.portfolio_file, 'w') as f:
            json.dump(portfolio_file_data, f, indent=2)
        
        print(f"   ✓ Updated portfolio: {len(positions)} positions")
        
        # Update account status
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
    
    def extract_completed_trades_from_portfolio(self):
        """Extract closed positions from portfolio and log to CSV"""
        
        if not self.portfolio_file.exists():
            return []
        
        with open(self.portfolio_file, 'r') as f:
            portfolio = json.load(f)
        
        closed = portfolio.get('closed_positions', [])
        
        if closed:
            print(f"\n   Found {len(closed)} closed positions to log:")
            for trade in closed:
                self.log_completed_trade(trade)
            
            portfolio['closed_positions'] = []
            with open(self.portfolio_file, 'w') as f:
                json.dump(portfolio, f, indent=2)
        
        return closed
    
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
        """Execute morning 'go' command with JSON parsing and portfolio update"""
        
        print("\n" + "="*60)
        print("EXECUTING 'GO' COMMAND - MORNING TRADING DECISIONS")
        print("="*60 + "\n")
        
        # Load context
        print("1. Loading optimized context...")
        context = self.load_optimized_context('go')
        print("   ✓ Context loaded\n")
        
        # Call Claude
        print("2. Calling Claude API for trading decisions...")
        response = self.call_claude_api('go', context)
        response_text = response.get('content', [{}])[0].get('text', '')
        print("   ✓ Response received\n")
        
        # CRITICAL NEW STEP: Extract JSON and update portfolio
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
            print("   NOTE: This may be expected for analysis-only responses\n")
        
        # Validate decisions
        print("5. Validating trade decisions against learned rules...")
        is_valid, violations = self.validate_trade_decisions(response_text)
        
        if violations:
            print("   ⚠️ VALIDATION WARNINGS:")
            for v in violations:
                print(f"      {v}")
            print()
        else:
            print("   ✓ All decisions validated\n")
        
        # Save response
        print("6. Saving response...")
        self.save_response('go', response)
        print("   ✓ Complete\n")
        
        return True
    
    def execute_analyze_command(self):
        """Execute evening 'analyze' command with CSV logging"""
        
        print("\n" + "="*60)
        print("EXECUTING 'ANALYZE' COMMAND - EVENING PERFORMANCE UPDATE")
        print("="*60 + "\n")
        
        # Load context
        print("1. Loading optimized context...")
        context = self.load_optimized_context('analyze')
        print("   ✓ Context loaded\n")
        
        # Call Claude
        print("2. Calling Claude API for performance analysis...")
        response = self.call_claude_api('analyze', context)
        print("   ✓ Response received\n")
        
        # Save response
        print("3. Saving response...")
        self.save_response('analyze', response)
        print("   ✓ Complete\n")
        
        # CRITICAL: Log completed trades to CSV
        print("4. Checking for completed trades to log...")
        closed_trades = self.extract_completed_trades_from_portfolio()
        
        if closed_trades:
            print(f"   ✓ Logged {len(closed_trades)} completed trades to CSV\n")
        else:
            print("   ℹ No completed trades to log\n")
        
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
    print(f"Paper Trading Lab Agent v3.0")
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