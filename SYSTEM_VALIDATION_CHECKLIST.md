# System Validation Checklist
**Complete verification before Alpaca integration**

---

## Objective

Achieve 100% confidence that:
1. Entry/exit logic works correctly
2. All data flows to correct files
3. Learning system captures everything
4. Dashboards display accurate data
5. No silent failures or data loss

---

## Phase 1: Entry Logic Validation

### 1.1 GO Command - Decision Generation

**Test Date:** _____________

**Critical Files Created:**
- [ ] `/root/paper_trading_lab/portfolio_data/pending_positions.json` exists
- [ ] Contains `hold`, `exit`, `buy` arrays
- [ ] All decisions have required fields (ticker, catalyst, thesis, etc.)

**Decision Quality Checks:**
- [ ] BUY decisions have `position_size_pct` field (8-13%)
- [ ] BUY decisions have `conviction_level` (HIGH/MEDIUM-HIGH/MEDIUM)
- [ ] BUY decisions have `catalyst_tier` (Tier1/Tier2/Tier3)
- [ ] EXIT decisions have `reason` field explaining why
- [ ] HOLD decisions are just ticker strings

**Logging Verification:**
```bash
ssh root@174.138.67.26 'tail -100 /root/paper_trading_lab/logs/go.log'
```

**Look for:**
- [ ] Claude's decision JSON visible in logs
- [ ] No API errors or timeouts
- [ ] Portfolio rotation section (if 10/10 positions)
- [ ] VIX check completed
- [ ] News validation for all BUY decisions

**Status File:**
```bash
ssh root@174.138.67.26 'cat /root/paper_trading_lab/dashboard_data/operation_status/go_status.json'
```
- [ ] Status = "SUCCESS"
- [ ] Timestamp is recent (within 24 hours)

---

### 1.2 EXECUTE Command - Entry Execution

**Test Date:** _____________

**Entry Price Validation:**
```bash
# Check what prices were used
ssh root@174.138.67.26 'grep "ENTERED" /root/paper_trading_lab/logs/execute.log | tail -5'
```

**Critical Checks:**
- [ ] Price source is "intraday" (NOT "prev close ⚠️")
- [ ] Entry price > 0
- [ ] Shares calculated correctly (shares = position_size / entry_price)
- [ ] Position size matches conviction level (HIGH=13%, MEDIUM=10%, etc.)

**Portfolio File Updated:**
```bash
ssh root@174.138.67.26 'cat /root/paper_trading_lab/portfolio_data/current_portfolio.json' | python3 -m json.tool
```

**Verify Each New Position Has:**
- [ ] `ticker` - Stock symbol
- [ ] `entry_price` - Price paid (must be intraday, not prev close)
- [ ] `current_price` - Same as entry_price initially
- [ ] `entry_date` - Today's date (YYYY-MM-DD)
- [ ] `shares` - Fractional shares calculated
- [ ] `position_size` - Dollar amount invested
- [ ] `days_held` - Starts at 0
- [ ] `stop_loss` - Set correctly (entry * 0.93)
- [ ] `price_target` - Set correctly (entry * 1.10)
- [ ] `catalyst` - From GO decision
- [ ] `thesis` - From GO decision
- [ ] `conviction_level` - HIGH/MEDIUM-HIGH/MEDIUM
- [ ] `catalyst_tier` - Tier1/Tier2/Tier3
- [ ] `news_validation_score` - 0-20 score
- [ ] `supporting_factors` - 0-5 count
- [ ] `vix_at_entry` - VIX level when entered
- [ ] `market_regime` - NORMAL/CAUTIOUS/SHUTDOWN

**Account Status Updated:**
```bash
ssh root@174.138.67.26 'cat /root/paper_trading_lab/portfolio_data/account_status.json'
```
- [ ] `cash_available` reduced by position sizes
- [ ] `positions_value` increased
- [ ] `total_value` = cash + positions + realized_pl
- [ ] Math adds up correctly

**Daily Activity Updated:**
```bash
ssh root@174.138.67.26 'cat /root/paper_trading_lab/portfolio_data/daily_activity.json'
```
- [ ] `date` is TODAY (not yesterday)
- [ ] Shows any new entries in `recent_activity` (if we log entries - check code)

---

## Phase 2: Exit Logic Validation

### 2.1 EXECUTE Command - Planned Exits

**Test Scenario:** GO command decides to exit a position

**Verify Exit Decision Flow:**
```bash
# Check GO decided to exit
ssh root@174.138.67.26 'cat /root/paper_trading_lab/portfolio_data/pending_positions.json' | grep -A 5 '"exit"'
```

- [ ] EXIT array contains ticker and reason
- [ ] Reason is clear (e.g., "Target reached", "Stop loss hit")

**Verify Execution:**
```bash
ssh root@174.138.67.26 'grep "CLOSED" /root/paper_trading_lab/logs/execute.log | tail -5'
```

- [ ] Exit price source is "intraday" (NOT "prev close ⚠️")
- [ ] Exit reason logged correctly

**Verify Trade Logged to CSV:**
```bash
ssh root@174.138.67.26 'tail -3 /root/paper_trading_lab/trade_history/completed_trades.csv'
```

**CSV Columns Validation (37 total):**
- [ ] Column 1: `Trade_ID` (format: TICKER_YYYY-MM-DD)
- [ ] Column 2: `Entry_Date`
- [ ] Column 3: `Exit_Date` (today's date)
- [ ] Column 4: `Ticker`
- [ ] Column 6: `Entry_Price` (from position)
- [ ] Column 7: `Exit_Price` (from EXECUTE)
- [ ] Column 9: `Shares` (fractional, matches position)
- [ ] Column 10: `Position_Size` (dollar amount)
- [ ] Column 11: `Position_Size_Percent` (8-13%)
- [ ] Column 12: `Hold_Days` (days between entry and exit)
- [ ] Column 13: `Return_Percent` ((exit-entry)/entry * 100)
- [ ] Column 14: `Return_Dollars` ((exit-entry) * shares)
- [ ] Column 15: `Exit_Reason` (from EXIT decision)
- [ ] Column 16: `Exit_Type` (Strategic_Rotation, Stop_Loss, Target_Reached, etc.)
- [ ] Column 17: `Catalyst_Type` (from entry)
- [ ] Column 18: `Catalyst_Tier` (Tier1/Tier2/Tier3)
- [ ] Column 21: `News_Validation_Score` (0-20)
- [ ] Column 22: `VIX_At_Entry` (from entry)
- [ ] Column 28: `Conviction_Level` (HIGH/MEDIUM-HIGH/MEDIUM)
- [ ] Column 29: `Supporting_Factors` (0-5)
- [ ] Column 36: `Account_Value_After` (account value after trade)
- [ ] Column 37: `Rotation_Into_Ticker` (if rotation exit)
- [ ] Column 38: `Rotation_Reason` (if rotation exit)

**Math Validation:**
- [ ] Return_Percent = ((Exit_Price - Entry_Price) / Entry_Price) * 100
- [ ] Return_Dollars = (Exit_Price - Entry_Price) * Shares
- [ ] Hold_Days = Exit_Date - Entry_Date (in days)

---

### 2.2 ANALYZE Command - Automatic Exits

**Test Scenarios:**
- Stop loss hit
- Profit target reached
- News invalidation detected

**Verify Exit Detection:**
```bash
ssh root@174.138.67.26 'tail -100 /root/paper_trading_lab/logs/analyze.log | grep -A 5 "Stop loss\|Target reached\|News"'
```

- [ ] ANALYZE detects exit condition
- [ ] Logs reason clearly
- [ ] Closes position

**Verify Trade Logged (Same CSV checks as 2.1):**
```bash
ssh root@174.138.67.26 'tail -3 /root/paper_trading_lab/trade_history/completed_trades.csv'
```

- [ ] All 37 columns populated correctly
- [ ] Exit_Type is NOT "Strategic_Rotation" (should be Stop_Loss, Target_Reached, etc.)
- [ ] Rotation columns are EMPTY (no rotation for ANALYZE exits)

**Portfolio Updated:**
```bash
ssh root@174.138.67.26 'cat /root/paper_trading_lab/portfolio_data/current_portfolio.json'
```
- [ ] Position removed from portfolio
- [ ] Total positions count decreased
- [ ] Cash increased by exit proceeds

---

### 2.3 Portfolio Rotation Exits (Phase 4)

**Test Scenario:** Portfolio at 10/10, GO identifies weak position + strong opportunity

**Verify GO Rotation Logic:**
```bash
ssh root@174.138.67.26 'grep -A 20 "PORTFOLIO ROTATION" /root/paper_trading_lab/logs/go.log | tail -30'
```

- [ ] "Portfolio at capacity" message shows
- [ ] Claude evaluates rotation
- [ ] Rotation decision includes: ticker, target_ticker, reason, expected_net_gain

**Verify Rotation Metadata:**
```bash
ssh root@174.138.67.26 'cat /root/paper_trading_lab/portfolio_data/pending_positions.json' | python3 -m json.tool
```

**EXIT position should have:**
- [ ] `ticker` (position to exit)
- [ ] `reason` (rotation reason)
- [ ] `rotation_into_ticker` (target position)
- [ ] `rotation_reason` (full explanation)

**Verify Rotation in CSV:**
```bash
ssh root@174.138.67.26 'grep "Strategic_Rotation" /root/paper_trading_lab/trade_history/completed_trades.csv | tail -1'
```

- [ ] Column 16 `Exit_Type` = "Strategic_Rotation"
- [ ] Column 37 `Rotation_Into_Ticker` = target ticker (e.g., "NVDA")
- [ ] Column 38 `Rotation_Reason` = full explanation from Claude

---

## Phase 3: Learning System Validation

### 3.1 Daily Learning (learn_daily.py)

**Run Manually:**
```bash
ssh root@174.138.67.26 'cd /root/paper_trading_lab && source venv/bin/activate && python3 learn_daily.py'
```

**Verify Output File:**
```bash
ssh root@174.138.67.26 'cat /root/paper_trading_lab/strategy_evolution/daily_insights.json'
```

**Must Contain:**
- [ ] `date` - Run date
- [ ] `catalyst_performance` - Win rate by catalyst type
- [ ] `news_score_analysis` - Win rate by news validation score
- [ ] `tier_performance` - Win rate by Tier1/Tier2/Tier3
- [ ] `rotation_performance` - Win rate of rotations vs non-rotations (if any)
- [ ] `recommendations` - Suggested exclusions for bad catalysts

**Verify Exclusions Updated:**
```bash
ssh root@174.138.67.26 'cat /root/paper_trading_lab/catalyst_exclusions.json'
```

- [ ] Contains catalysts with <40% win rate
- [ ] Each entry has: catalyst, win_rate, sample_size, added_date

---

### 3.2 Weekly Learning (learn_weekly.py)

**Run Manually:**
```bash
ssh root@174.138.67.26 'cd /root/paper_trading_lab && source venv/bin/activate && python3 learn_weekly.py'
```

**Verify Report Created:**
```bash
ssh root@174.138.67.26 'ls -lh /root/paper_trading_lab/strategy_evolution/weekly_report_*.md'
```

**Report Must Include:**
- [ ] Overall win rate
- [ ] Win rate by conviction level (HIGH vs MEDIUM)
- [ ] Win rate by catalyst tier
- [ ] Win rate by exit type (rotation vs stop vs target)
- [ ] Avg hold time by outcome (winners vs losers)
- [ ] Best performing catalysts
- [ ] Worst performing catalysts
- [ ] Rotation analysis (if any rotations occurred)

---

### 3.3 Monthly Learning (learn_monthly.py)

**Run Manually:**
```bash
ssh root@174.138.67.26 'cd /root/paper_trading_lab && source venv/bin/activate && python3 learn_monthly.py'
```

**Verify Recommendations Created:**
```bash
ssh root@174.138.67.26 'cat /root/paper_trading_lab/dashboard_data/pending_actions.json'
```

**Must Contain:**
- [ ] `parameter_recommendations` - Suggested changes to thresholds
- [ ] `new_exclusions` - Catalysts to add to exclusion list
- [ ] `exclusion_removals` - Catalysts to remove (recovered performance)
- [ ] Each recommendation has: type, current_value, suggested_value, reasoning, data_support

**Example Parameters to Check:**
- News validation threshold (currently 10)
- Stop loss percentage (currently -7%)
- Position sizing by conviction (13%/11%/10%)
- Rotation momentum threshold (0.3%/day)

---

## Phase 4: Dashboard Validation

### 4.1 Public Dashboard (tedbot.ai)

**Visual Verification:**

**Portfolio Overview Section:**
- [ ] Account value shown correctly
- [ ] Cash available matches account_status.json
- [ ] Positions value matches sum of all position sizes
- [ ] Realized P&L matches completed_trades.csv sum

**Active Positions Table:**
- [ ] All 7 positions displayed (or current count)
- [ ] Ticker names correct
- [ ] Entry price matches current_portfolio.json
- [ ] Current price is TODAY's price (not yesterday's)
- [ ] P&L % calculated correctly: ((current-entry)/entry * 100)
- [ ] P&L $ calculated correctly: ((current-entry) * shares)
- [ ] Days held increments daily
- [ ] Catalyst displayed correctly

**Today's Activity Section:**
- [ ] Date is TODAY (format: YYYY-MM-DD)
- [ ] Shows trades closed today (or "No trades today")
- [ ] Each closed trade shows: ticker, P&L %, P&L $, hold days, exit reason
- [ ] Summary stats correct: winners, losers, total P&L

**System Status:**
- [ ] Win rate calculated from completed_trades.csv
- [ ] Total trades count matches CSV row count
- [ ] Avg return % matches CSV average
- [ ] Last updated timestamp is recent

---

### 4.2 Admin Dashboard (tedbot.ai/admin)

**Login:**
- [ ] Username/password authentication works
- [ ] Redirects to /admin after successful login

**Operations Status Panel:**
- [ ] GO operation shows recent timestamp
- [ ] EXECUTE operation shows recent timestamp
- [ ] ANALYZE operation shows recent timestamp
- [ ] All operations show "SUCCESS" status
- [ ] "View Log" buttons work for each operation
- [ ] Log modal shows last 200 lines of correct log file

**Recent Trades Section:**
- [ ] Shows last 10 completed trades
- [ ] Exit_Type displayed correctly
- [ ] Rotation_Into_Ticker shown for rotations
- [ ] All CSV data displayed correctly

**Pending Actions Section:**
- [ ] Shows parameter recommendations from learn_monthly
- [ ] Shows exclusion recommendations from learn_daily
- [ ] "Approve" and "Reject" buttons present (if implemented)

**Trade History Override Section:**
- [ ] Shows exclusion list from catalyst_exclusions.json
- [ ] Each exclusion shows: catalyst, win_rate, sample_size, date
- [ ] Can remove exclusions (if implemented)

---

## Phase 5: Price Data Validation

### 5.1 Price Source Verification

**During Market Hours (9:30 AM - 4:00 PM):**

**Run EXECUTE or ANALYZE manually:**
```bash
ssh root@174.138.67.26 'cd /root/paper_trading_lab && source venv/bin/activate && source /root/.env && python3 agent_v5.5.py analyze 2>&1 | grep "Fetching prices" -A 15'
```

**Verify:**
- [ ] Price source is "intraday" (NOT "prev close ⚠️")
- [ ] Prices are reasonable (not 0, not negative)
- [ ] Prices match real market data (spot check with Yahoo Finance)

**After Market Close (4:00 PM - next day 9:30 AM):**
- [ ] Price source is "today's close" (NOT "prev close ⚠️")
- [ ] Prices are EOD prices from TODAY (not yesterday)

**Weekend/Holiday:**
- [ ] Price source is "prev close ⚠️" (acceptable, market closed)

---

### 5.2 Price Math Validation

**Pick one position from current_portfolio.json:**
```bash
ssh root@174.138.67.26 'python3 -c "
import json
data = json.load(open(\"/root/paper_trading_lab/portfolio_data/current_portfolio.json\"))
pos = data[\"positions\"][0]
print(f\"Ticker: {pos[\"ticker\"]}\")
print(f\"Entry: \${pos[\"entry_price\"]:.2f}\")
print(f\"Current: \${pos[\"current_price\"]:.2f}\")
print(f\"Shares: {pos[\"shares\"]:.4f}\")
print(f\"P&L %: {pos[\"unrealized_gain_pct\"]:.2f}%\")
print(f\"P&L \$: \${pos[\"unrealized_gain_dollars\"]:.2f}\")
print(\"---\")
print(f\"Manual Calc P&L %: {((pos[\"current_price\"] - pos[\"entry_price\"]) / pos[\"entry_price\"] * 100):.2f}%\")
print(f\"Manual Calc P&L \$: {((pos[\"current_price\"] - pos[\"entry_price\"]) * pos[\"shares\"]):.2f}\")
"'
```

- [ ] Manual calc P&L % matches `unrealized_gain_pct`
- [ ] Manual calc P&L $ matches `unrealized_gain_dollars`
- [ ] No rounding errors >$0.10

---

## Phase 6: Data Flow Integrity

### 6.1 Entry → CSV Flow

**Trace one trade from entry to CSV:**

**1. Entry (EXECUTE):**
```bash
ssh root@174.138.67.26 'grep "ENTERED AAPL" /root/paper_trading_lab/logs/execute.log | tail -1'
```
Record: ticker, entry_price, shares, position_size, conviction_level

**2. Portfolio File:**
```bash
ssh root@174.138.67.26 'python3 -c "
import json
data = json.load(open(\"/root/paper_trading_lab/portfolio_data/current_portfolio.json\"))
pos = [p for p in data[\"positions\"] if p[\"ticker\"] == \"AAPL\"][0]
print(json.dumps(pos, indent=2))
"'
```
- [ ] All fields from EXECUTE log match portfolio file

**3. Exit (ANALYZE or EXECUTE):**
```bash
ssh root@174.138.67.26 'grep "CLOSED AAPL" /root/paper_trading_lab/logs/analyze.log | tail -1'
```
Record: exit_price, exit_reason

**4. CSV:**
```bash
ssh root@174.138.67.26 'grep "AAPL_" /root/paper_trading_lab/trade_history/completed_trades.csv | tail -1'
```

**Verify Data Consistency:**
- [ ] Entry_Price in CSV = entry_price from EXECUTE log
- [ ] Exit_Price in CSV = exit_price from exit log
- [ ] Shares in CSV = shares from portfolio file
- [ ] Position_Size in CSV = position_size from portfolio file
- [ ] Conviction_Level in CSV = conviction_level from GO decision
- [ ] Catalyst_Tier in CSV = catalyst_tier from GO decision
- [ ] Return_Percent = ((exit-entry)/entry * 100)
- [ ] Return_Dollars = (exit-entry) * shares
- [ ] All 37 columns populated (no empty cells except rotation if not applicable)

---

### 6.2 CSV → Learning Flow

**Verify Learning Scripts Read CSV Correctly:**

**1. Count trades in CSV:**
```bash
ssh root@174.138.67.26 'wc -l /root/paper_trading_lab/trade_history/completed_trades.csv'
```
Record count (subtract 1 for header)

**2. Run learn_daily manually and check output:**
```bash
ssh root@174.138.67.26 'cd /root/paper_trading_lab && source venv/bin/activate && python3 learn_daily.py 2>&1 | grep "Total trades"'
```

- [ ] Trade count matches CSV row count
- [ ] No "failed to parse" errors
- [ ] All catalysts from CSV appear in analysis

---

### 6.3 Learning → Dashboard Flow

**1. Generate monthly recommendations:**
```bash
ssh root@174.138.67.26 'cd /root/paper_trading_lab && source venv/bin/activate && python3 learn_monthly.py'
```

**2. Check pending_actions.json created:**
```bash
ssh root@174.138.67.26 'cat /root/paper_trading_lab/dashboard_data/pending_actions.json'
```

**3. Verify admin dashboard shows recommendations:**
- [ ] Navigate to https://tedbot.ai/admin
- [ ] Pending Actions section shows recommendations
- [ ] Recommendations match pending_actions.json

---

## Phase 7: Error Handling Validation

### 7.1 API Failures

**Test Scenario: Polygon API down or rate limited**

**Simulate:**
```bash
# Temporarily break API key
ssh root@174.138.67.26 'cd /root/paper_trading_lab && source venv/bin/activate && POLYGON_API_KEY=invalid python3 -c "
from agent_v5 import TradingAgent
agent = TradingAgent()
prices = agent.fetch_current_prices([\"NVDA\"])
print(prices)
"'
```

**Verify:**
- [ ] System doesn't crash
- [ ] Logs error clearly
- [ ] Falls back to previous prices (or skips operation gracefully)
- [ ] Operation status shows "FAILED" with error message

---

### 7.2 Missing Files

**Test Scenario: portfolio file deleted**

**Simulate:**
```bash
ssh root@174.138.67.26 'mv /root/paper_trading_lab/portfolio_data/current_portfolio.json /tmp/backup_portfolio.json'
```

**Run ANALYZE:**
```bash
ssh root@174.138.67.26 'cd /root/paper_trading_lab && source venv/bin/activate && source /root/.env && python3 agent_v5.5.py analyze 2>&1 | tail -20'
```

**Verify:**
- [ ] System creates empty portfolio (doesn't crash)
- [ ] OR logs error clearly and exits gracefully
- [ ] Operation status shows issue

**Restore:**
```bash
ssh root@174.138.67.26 'mv /tmp/backup_portfolio.json /root/paper_trading_lab/portfolio_data/current_portfolio.json'
```

---

### 7.3 Malformed Data

**Test Scenario: Corrupted CSV**

**Simulate:**
```bash
# Add malformed row to CSV
ssh root@174.138.67.26 'echo "CORRUPT,DATA,HERE" >> /root/paper_trading_lab/trade_history/completed_trades.csv'
```

**Run learn_daily:**
```bash
ssh root@174.138.67.26 'cd /root/paper_trading_lab && source venv/bin/activate && python3 learn_daily.py 2>&1 | tail -20'
```

**Verify:**
- [ ] Skips corrupted row (doesn't crash)
- [ ] Logs warning about unparseable row
- [ ] Continues processing good rows

**Cleanup:**
```bash
# Remove corrupted row
ssh root@174.138.67.26 'head -n -1 /root/paper_trading_lab/trade_history/completed_trades.csv > /tmp/clean.csv && mv /tmp/clean.csv /root/paper_trading_lab/trade_history/completed_trades.csv'
```

---

## Phase 8: Cron Job Validation

### 8.1 Verify Cron Schedule

```bash
ssh root@174.138.67.26 'crontab -l'
```

**Verify:**
- [ ] GO: 45 8 * * 1-5 (8:45 AM Mon-Fri)
- [ ] EXECUTE: 45 9 * * 1-5 (9:45 AM Mon-Fri)
- [ ] ANALYZE: 30 16 * * 1-5 (4:30 PM Mon-Fri)
- [ ] LEARN_DAILY: 0 17 * * 1-5 (5:00 PM Mon-Fri)
- [ ] LEARN_WEEKLY: 30 17 * * 5 (5:30 PM Friday)
- [ ] LEARN_MONTHLY: 0 18 * * 0 (6:00 PM Last Sunday)

---

### 8.2 Verify Cron Execution

**Check operation status files:**
```bash
ssh root@174.138.67.26 'ls -lh /root/paper_trading_lab/dashboard_data/operation_status/*.json'
```

- [ ] go_status.json timestamp is 8:45 AM today
- [ ] execute_status.json timestamp is 9:45 AM today
- [ ] analyze_status.json timestamp is 4:30 PM today

**Check logs:**
```bash
ssh root@174.138.67.26 'ls -lh /root/paper_trading_lab/logs/*.log'
```

- [ ] go.log updated today at 8:45 AM
- [ ] execute.log updated today at 9:45 AM
- [ ] analyze.log updated today at 4:30 PM

---

## Phase 9: End-to-End Full Cycle Test

### 9.1 Complete Trading Cycle

**Goal:** Trace one position from idea → entry → hold → exit → CSV → learning

**Day 1 (8:45 AM):**
- [ ] GO identifies opportunity
- [ ] Creates pending decision with ticker=TEST
- [ ] Decision has conviction_level, catalyst_tier, news_score

**Day 1 (9:45 AM):**
- [ ] EXECUTE enters TEST position
- [ ] Uses intraday price
- [ ] Position added to current_portfolio.json
- [ ] Account status updated (cash reduced)

**Day 2-5 (4:30 PM daily):**
- [ ] ANALYZE updates TEST current_price
- [ ] P&L recalculated daily
- [ ] Days_held increments
- [ ] No exit triggers hit yet

**Day 6 (4:30 PM):**
- [ ] ANALYZE detects exit condition (target reached or stop hit)
- [ ] Closes TEST position
- [ ] Trade logged to CSV with all 37 columns
- [ ] Position removed from current_portfolio.json
- [ ] Cash increased by exit proceeds

**Day 6 (5:00 PM):**
- [ ] LEARN_DAILY processes TEST trade
- [ ] Catalyst performance updated
- [ ] If catalyst performed poorly, added to exclusions

**Dashboard:**
- [ ] TEST appears in completed trades
- [ ] Win rate updated
- [ ] Portfolio value reflects exit proceeds

---

## Phase 10: Rotation-Specific Validation

### 10.1 Full Rotation Cycle

**Setup:** Wait for portfolio to reach 10/10 positions

**Day N (8:45 AM GO):**
- [ ] GO detects portfolio at capacity
- [ ] Strong Tier1 opportunity identified
- [ ] Rotation evaluation triggered
- [ ] Claude identifies weak position (low momentum)
- [ ] Rotation decision made: EXIT weak → BUY strong

**Pending file verification:**
```bash
ssh root@174.138.67.26 'cat /root/paper_trading_lab/portfolio_data/pending_positions.json' | python3 -m json.tool
```

**EXIT decision must have:**
- [ ] `ticker` (weak position)
- [ ] `reason` (rotation explanation)
- [ ] `rotation_into_ticker` (strong opportunity)
- [ ] `rotation_reason` (full Claude reasoning)

**Day N (9:45 AM EXECUTE):**
- [ ] EXECUTE closes weak position
- [ ] Exit logged to CSV with Exit_Type = "Strategic_Rotation"
- [ ] Rotation_Into_Ticker = target ticker
- [ ] Rotation_Reason = Claude's reasoning
- [ ] Strong position entered immediately after

**CSV Validation:**
```bash
ssh root@174.138.67.26 'tail -2 /root/paper_trading_lab/trade_history/completed_trades.csv'
```

**Row 1 (rotated exit):**
- [ ] Exit_Type = "Strategic_Rotation"
- [ ] Rotation_Into_Ticker = "TARGET"
- [ ] Rotation_Reason = full explanation

**Row 2 (rotation target entry):**
- [ ] Trade_ID = "TARGET_YYYY-MM-DD"
- [ ] Entry immediately after rotation exit

**Learning Verification:**

**Day N (5:00 PM LEARN_DAILY):**
- [ ] Rotation identified in daily insights
- [ ] Rotation performance tracked separately
- [ ] If rotation loses money, flagged in recommendations

---

## Final Validation Summary

### Critical Pre-Alpaca Requirements

**Must Pass 100%:**
- [ ] All entry prices use "intraday" (not "prev close")
- [ ] All exit prices use today's data
- [ ] All 37 CSV columns populated correctly
- [ ] Math is correct (P&L %, P&L $, position size)
- [ ] Daily activity updates every day (even if 0 trades)
- [ ] Learning scripts read CSV without errors
- [ ] Dashboard shows accurate current data
- [ ] Rotation metadata flows through correctly

**High Priority (Must Pass 95%):**
- [ ] Cron jobs run on schedule
- [ ] Operation status files update correctly
- [ ] No silent failures in logs
- [ ] Error handling prevents crashes

**Nice to Have (Should Pass 80%):**
- [ ] Malformed data handled gracefully
- [ ] API failures don't break system
- [ ] Admin dashboard shows all features

---

## Testing Schedule

**Week 1: Manual Testing**
- [ ] Monday: Entry logic validation (Phase 1)
- [ ] Tuesday: Exit logic validation (Phase 2)
- [ ] Wednesday: Learning validation (Phase 3)
- [ ] Thursday: Dashboard validation (Phase 4)
- [ ] Friday: Price validation (Phase 5)

**Week 2: Integration Testing**
- [ ] Monday: Data flow integrity (Phase 6)
- [ ] Tuesday: Error handling (Phase 7)
- [ ] Wednesday: Cron jobs (Phase 8)
- [ ] Thursday: End-to-end cycle (Phase 9)
- [ ] Friday: Rotation validation (Phase 10)

**Week 3: Live Monitoring**
- [ ] Run system without intervention
- [ ] Monitor logs daily
- [ ] Track any anomalies
- [ ] Fix any issues found
- [ ] Re-test failed areas

**Week 4: Final Sign-Off**
- [ ] Review all checklist items
- [ ] All critical items passing
- [ ] No blocking issues
- [ ] Document any known limitations
- [ ] **GREEN LIGHT FOR ALPACA INTEGRATION**

---

## Sign-Off

**System Validated By:** _________________
**Date:** _________________
**Confidence Level:** _____ %
**Blocking Issues:** _________________
**Known Limitations:** _________________

**Ready for Alpaca Integration?** [ ] YES [ ] NO

**If NO, what needs to be fixed:**
1. _________________
2. _________________
3. _________________

---

## Notes

Use this space to document any issues found during testing:

