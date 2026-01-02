# Agent v5.0 Deployment Guide

## Status: Ready to Deploy

All code is implemented, tested for syntax, and pushed to GitHub.
Ready for deployment and testing on production server.

---

## What Was Implemented

### Core Changes
1. **agent_v5.0.py** - Complete swing trading system
   - GO command reviews existing portfolio with premarket data
   - HOLD/EXIT/BUY decision framework
   - Enforces 2-day minimum hold, proper exit rules
   - Leverages 15-min delayed Polygon.io data

2. **Wrapper Scripts Updated**
   - run_go.sh → uses agent_v5.0.py
   - run_execute.sh → uses agent_v5.0.py
   - run_analyze.sh → uses agent_v5.0.py

3. **Symlink Created**
   - agent.py → agent_v5.0.py

4. **Helper Methods Added**
   - `_format_portfolio_review()` - Formats premarket data for Claude
   - `_close_position()` - Closes position and returns trade data
   - `_log_trade_to_csv()` - Logs closed trades to CSV
   - `load_current_portfolio()` - Loads portfolio from JSON

---

## Deployment Steps (On Production Server)

### 1. Pull Latest Code
```bash
cd /root/paper_trading_lab
git pull origin master
```

### 2. Verify Files
```bash
# Check symlink
ls -la agent.py
# Should show: agent.py -> agent_v5.0.py

# Check wrapper scripts
grep "agent_v5.0.py" run_*.sh
# All three should reference agent_v5.0.py
```

### 3. Verify Crontab (No Changes Needed)
```bash
crontab -l
```
Should show:
```
45 8 * * 1-5 /root/paper_trading_lab/run_go.sh
30 9 * * 1-5 /root/paper_trading_lab/run_execute.sh
30 16 * * 1-5 /root/paper_trading_lab/run_analyze.sh
```

Crontab doesn't need updates - it calls wrapper scripts which now use v5.0.

---

## Testing Plan

### Test 1: Initial Portfolio Build (Empty State)
**Current Status:** Portfolio is empty (clean slate)

```bash
cd /root/paper_trading_lab
python3 agent_v5.0.py go
```

**Expected Behavior:**
- Should detect 0 existing positions
- Should call Claude to select 10 new stocks
- Should save to `portfolio_data/pending_positions.json`
- JSON format: `{"hold": [], "exit": [], "buy": [10 stocks]}`

**Verify:**
```bash
cat portfolio_data/pending_positions.json | head -50
```

### Test 2: Execute Initial Positions
```bash
python3 agent_v5.0.py execute
```

**Expected Behavior:**
- Load pending decisions
- Process BUYS: Enter 10 new positions
- Save to `portfolio_data/current_portfolio.json`
- Each position should have:
  - entry_price, entry_date, days_held=0
  - stop_loss (-7%), price_target (+10%)
  - shares calculated from position_size

**Verify:**
```bash
cat portfolio_data/current_portfolio.json | head -80
```

### Test 3: Portfolio Review (Next Day Simulation)
**Wait until next trading day OR manually test:**

```bash
python3 agent_v5.0.py go
```

**Expected Behavior:**
- Should detect 10 existing positions
- Should fetch premarket prices (~8:30 AM data)
- Should calculate P&L and gaps for each position
- Should call Claude with portfolio review prompt
- Claude should decide HOLD/EXIT/BUY (not rebuild from scratch)
- Typical result: HOLD 7-10, EXIT 0-3, BUY 0-3

**Verify:**
```bash
cat portfolio_data/pending_positions.json
# Should show hold/exit/buy arrays with selective changes
```

### Test 4: Execute Hold/Exit/Buy Decisions
```bash
python3 agent_v5.0.py execute
```

**Expected Behavior:**
- Process EXITS: Close exited positions, log to CSV
- Process HOLDS: Update prices, increment days_held
- Process BUYS: Enter new positions
- Portfolio should reflect changes

**Verify:**
```bash
cat portfolio_data/current_portfolio.json
cat trade_history/completed_trades.csv
```

### Test 5: Analyze Command (Unchanged)
```bash
python3 agent_v5.0.py analyze
```

**Expected Behavior:**
- Should work exactly as before
- Updates prices, checks stops/targets
- Generates daily review

**Verify:**
```bash
cat analysis_reports/daily/review_YYYY-MM-DD.json
```

---

## Monitoring First Few Days

### What to Watch For:

1. **GO Command (8:45 AM)**
   - Check logs: `tail -50 logs/go.log`
   - Verify premarket data fetched successfully
   - Verify HOLD decisions > EXIT decisions (should hold most)
   - Verify exits have valid reasons per swing trading rules

2. **EXECUTE Command (9:30 AM)**
   - Check logs: `tail -50 logs/execute.log`
   - Verify correct number of exits/holds/buys processed
   - Verify portfolio position count is correct
   - Verify days_held increments each day

3. **Portfolio Turnover**
   - Should be 0-3 positions per day (not 10/day)
   - Most positions should hold 3-7 days
   - Only exit on valid triggers

4. **Learning System**
   - Closed trades logged to CSV correctly
   - Learning engines receive proper data

---

## Key Behavioral Changes

### v4.3 (OLD):
- GO: Selected 10 new stocks daily
- EXECUTE: Closed all old positions, entered 10 new
- Turnover: 10 positions/day (100% daily)
- Hold period: 1 day only

### v5.0 (NEW):
- GO: Reviews 10 existing positions with premarket data
- EXECUTE: Selective exits, keeps holds, enters new as needed
- Turnover: 0-3 positions/day (0-30% daily)
- Hold period: 2-21 days (3-7 days typical)

---

## Rollback Plan (If Issues Arise)

If v5.0 has critical issues:

```bash
cd /root/paper_trading_lab

# Restore v4.3
ln -sf agent_v4.3.py agent.py

# Update wrapper scripts
sed -i 's/agent_v5.0.py/agent_v4.3.py/g' run_*.sh

# Restore portfolio backup (if needed)
cp backups/pre_swing_system_*/current_portfolio.json portfolio_data/

# Verify
ls -la agent.py
grep "agent_v" run_*.sh
```

---

## Success Criteria

v5.0 is working correctly if:

1. ✓ First GO command builds 10-position portfolio
2. ✓ First EXECUTE enters all 10 positions
3. ✓ Second GO command reviews existing portfolio (not rebuild)
4. ✓ Second EXECUTE does selective exits (0-3 typically)
5. ✓ days_held increments daily for held positions
6. ✓ Closed trades logged to CSV correctly
7. ✓ Most positions held 2+ days before exit
8. ✓ ANALYZE command still works

---

## Questions Before Deployment?

- Does the swing trading logic make sense?
- Are the hold periods appropriate (2-21 days)?
- Are the exit rules clear and enforceable?
- Should we adjust stop loss (-7%) or target (+10%)?

Ready to deploy when you are!
