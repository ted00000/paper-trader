# Agent v5.0 Upgrade Specification
## Swing Trading System with Proper Position Management

**Status:** Ready to implement
**Impact:** Major breaking changes
**Risk Level:** High - requires careful testing
**Estimated Time:** 2-3 hours to implement and test

---

## Overview

Upgrade from v4.3 (daily portfolio rebuild) to v5.0 (proper swing trading with position management).

### Key Changes:
1. GO command reviews existing portfolio instead of selecting 10 new stocks
2. Uses 15-min delayed premarket data for informed decisions
3. Enforces swing trading rules (minimum hold periods, proper exits)
4. HOLD/EXIT/BUY decision framework
5. Typical turnover: 0-3 positions/day (not 10/day)

---

## File Changes Required

###  1. `agent_v5.0.py` - New version (copy from v4.3)

#### A. Update `call_claude_api(self, command, context, premarket_data=None)`

**Signature Change:**
```python
def call_claude_api(self, command, context, premarket_data=None):
```

**New GO Prompt (when premarket_data provided):**
```python
if command == 'go' and premarket_data:
    # Build portfolio review prompt with premarket data
    portfolio_review = self._format_portfolio_review(premarket_data)

    user_message = f"""PORTFOLIO REVIEW - {today_date} @ 8:45 AM

CURRENT POSITIONS ({len(premarket_data)}):
{portfolio_review}

TASK: Review each position and decide HOLD / EXIT / REPLACE

SWING TRADING RULES (STRICTLY ENFORCE):
1. Minimum hold: 2 days (unless stop/target hit)
2. Maximum hold: 21 days (time stop)
3. Exit triggers:
   - Stop loss hit (-7%)
   - Price target hit (+10-15%)
   - Catalyst invalidated (news, guidance cut)
   - Time stop (21 days with <3% gain)
   - Better opportunity AND position flat/small loss AND age >= 2 days
4. DO NOT exit profitable positions just because it's a new day
5. DO NOT churn daily - let swings work (3-7 days typical)

OUTPUT REQUIRED - JSON at end:
{{
  "hold": ["AAPL", "MSFT"],  // Tickers to keep
  "exit": [
    {{"ticker": "TSLA", "reason": "Stop loss approaching, news turned negative"}}
  ],
  "buy": [  // New positions to fill vacant slots
    {{
      "ticker": "NVDA",
      "position_size": 100.00,
      "catalyst": "Earnings_Beat",
      "sector": "Technology",
      "confidence": "High",
      "thesis": "..."
    }}
  ]
}}

Provide full analysis BEFORE the JSON."""
```

**New GO Prompt (when no existing positions - initial build):**
```python
elif command == 'go' and not premarket_data:
    user_message = f"""BUILD INITIAL PORTFOLIO - {today_date}

No existing positions. Select 10 stocks with Tier 1 catalysts.

OUTPUT REQUIRED - JSON at end:
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
      "thesis": "..."
    }}
    // ... 10 total
  ]
}}
```

#### B. Add Helper Method: `_format_portfolio_review(self, premarket_data)`

```python
def _format_portfolio_review(self, premarket_data):
    """Format premarket data for Claude's review"""
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
```

#### C. Update `execute_go_command()` - Already done above

#### D. Completely Rewrite `execute_execute_command()`

**Current:** Loads pending, fetches prices, creates portfolio
**New:** Load pending decisions (hold/exit/buy), execute exits, enter new positions

```python
def execute_execute_command(self):
    """
    Execute EXECUTE command (9:30 AM) - SWING TRADING VERSION

    NEW v5.0 BEHAVIOR:
    1. Load pending decisions (hold/exit/buy)
    2. Load current portfolio
    3. Execute EXITS: Close positions marked for exit
    4. Keep HOLD positions (update prices only)
    5. Execute BUYS: Enter new positions
    6. Save updated portfolio
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
            reason = exit_decision.get('reason', 'Portfolio management decision')

            # Find position in current portfolio
            position = next((p for p in current_positions if p['ticker'] == ticker), None)
            if position:
                exit_price = market_prices.get(ticker, position.get('current_price', 0))
                closed_trade = self._close_position(position, exit_price, reason)
                closed_trades.append(closed_trade)
                print(f"   ✓ CLOSED {ticker}: {reason}")
    else:
        print("   No exits\n")

    # Process HOLDS (update prices)
    print("\n4. Updating HOLD positions...")
    updated_positions = []
    for position in current_positions:
        ticker = position['ticker']
        if ticker in hold_tickers:
            # Fetch current price
            market_prices = self.fetch_current_prices([ticker])
            current_price = market_prices.get(ticker, position.get('current_price', 0))

            position['current_price'] = current_price
            position['days_held'] = position.get('days_held', 0) + 1
            updated_positions.append(position)
            print(f"   ✓ {ticker}: ${current_price:.2f} (Day {position['days_held']})")

    # Process BUYS
    print("\n5. Entering NEW positions...")
    if buy_positions:
        tickers = [p['ticker'] for p in buy_positions]
        market_prices = self.fetch_current_prices(tickers)

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
        for trade in closed_trades:
            self._log_trade_to_csv(trade)

    # Update account status
    self.update_account_status()

    # Clean up pending file
    self.pending_file.unlink()

    print("="*60)
    print("EXECUTE COMMAND COMPLETE")
    print("="*60)
    print(f"\n✓ Portfolio Updated:")
    print(f"  - Closed: {len(closed_trades)} positions")
    print(f"  - Holding: {len([t for t in hold_tickers if t not in [e['ticker'] for e in exit_decisions]])} positions")
    print(f"  - Entered: {len(buy_positions)} new positions")
    print(f"  - Total Active: {len(updated_positions)} positions\n")

    return True
```

#### E. Add Helper Method: `_close_position(self, position, exit_price, reason)`

```python
def _close_position(self, position, exit_price, reason):
    """Close a position and return trade data for CSV logging"""
    entry_price = position.get('entry_price', 0)
    shares = position.get('shares', 0)
    position_size = position.get('position_size', 100)

    pnl_dollars = (exit_price - entry_price) * shares
    pnl_percent = ((exit_price - entry_price) / entry_price * 100) if entry_price > 0 else 0

    trade = {
        'ticker': position['ticker'],
        'entry_date': position.get('entry_date', ''),
        'entry_price': entry_price,
        'exit_price': exit_price,
        'shares': shares,
        'position_size': position_size,
        'days_held': position.get('days_held', 0),
        'pnl_percent': round(pnl_percent, 2),
        'pnl_dollars': round(pnl_dollars, 2),
        'exit_reason': reason,
        'catalyst': position.get('catalyst', ''),
        'sector': position.get('sector', ''),
        'thesis': position.get('thesis', '')
    }

    return trade
```

###  2. Update Wrapper Scripts

#### `run_go.sh`
```bash
#!/bin/bash
set -e
cd /root/paper_trading_lab
source venv/bin/activate
source /root/.env
python3 agent_v5.0.py go >> logs/go.log 2>&1
exit 0
```

#### `run_execute.sh`
```bash
#!/bin/bash
set -e
cd /root/paper_trading_lab
source venv/bin/activate
source /root/.env
python3 agent_v5.0.py execute >> logs/execute.log 2>&1
exit 0
```

#### `run_analyze.sh` - NO CHANGES (already works)

###  3. Create Symlink

```bash
cd /root/paper_trading_lab
ln -sf agent_v5.0.py agent.py
```

---

## Testing Plan

### Phase 1: Initial Portfolio Build (Empty State)
```bash
# Clear slate (already done)
python3 agent_v5.0.py go
# Should select 10 new stocks (no existing positions)

python3 agent_v5.0.py execute
# Should enter all 10 positions

# Verify:
cat portfolio_data/current_portfolio.json | head -40
```

### Phase 2: Next Day Review (With Existing Positions)
```bash
# Simulate next day
python3 agent_v5.0.py go
# Should:
# - Review 10 existing positions
# - Fetch premarket prices
# - Decide HOLD/EXIT/BUY
# - Probably HOLD most, EXIT 0-2, BUY 0-2

python3 agent_v5.0.py execute
# Should:
# - Close EXIT positions
# - Keep HOLD positions (update prices)
# - Enter BUY positions

# Verify portfolio updated correctly
cat portfolio_data/current_portfolio.json
```

### Phase 3: ANALYZE Still Works
```bash
python3 agent_v5.0.py analyze
# Should work unchanged (updates prices, checks stops/targets)
```

---

## Rollback Plan

If v5.0 fails:
```bash
cd /root/paper_trading_lab
ln -sf agent_v4.3.py agent.py
# Restore from backup:
cp backups/pre_swing_system_*/current_portfolio.json portfolio_data/
```

---

## Implementation Steps

1. ✅ Clean slate created
2.  Create agent_v5.0.py with all changes above
3.  Update wrapper scripts to use agent_v5.0.py
4.  Test GO command (initial portfolio build)
5.  Test EXECUTE command
6.  Test ANALYZE command (ensure unchanged)
7.  Test full cycle: GO → EXECUTE → ANALYZE
8.  Create symlink: `agent.py -> agent_v5.0.py`
9.  Update crontab (already uses wrapper scripts, no change needed)
10.  Commit all changes to git

---

## Risk Mitigation

**CRITICAL:** This is a major rewrite. We must:
1. Test thoroughly before deploying
2. Keep v4.3 available for rollback
3. Have backups of all data
4. Test during market hours to verify Polygon.io data works
5. Monitor first few days closely

**Estimated Implementation Time:** 2-3 hours including testing

---

## Decision Point

**Do you want to:**
A. Proceed with full implementation now (2-3 hour commitment)
B. Implement incrementally over multiple sessions
C. Review specification first, implement later

**My Recommendation:** Given it's late morning already, let's implement and test this carefully now while you're available to monitor. The system is currently in a clean state (empty portfolio), perfect for testing.

Your call - proceed?
