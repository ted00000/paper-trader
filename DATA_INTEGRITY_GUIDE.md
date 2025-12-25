# TedBot Data Integrity Guide

**Last Updated:** 2025-12-24
**Reset Date:** 2025-12-24
**Purpose:** Ensure single source of truth and prevent data inconsistencies

---

## Data Reset Summary (December 24, 2025)

All trading data has been **clean slated** to ensure data integrity going forward:

- ✅ **completed_trades.csv**: Reset to header only (0 trades)
- ✅ **account_status.json**: Reset to $1000.00 starting capital
- ✅ **current_portfolio.json**: Reset to empty (0 positions)
- ✅ **Learning data**: Archived to `learning_archive_20251224/`
- ✅ **Daily reviews**: Archived to `daily_reviews/archive_20251224/`

**All historical data preserved in:**
- `data_backup_20251224/` - Full backup of all data files
- `learning_archive_20251224/` - Learning data archive
- `daily_reviews/archive_20251224/` - Review history archive

---

## Single Source of Truth

### 1. Trade History
**File:** `trade_history/completed_trades.csv`
**Source of Truth:** YES - This is the ONLY source of completed trade data
**Updated By:** `agent_v5.5.py` → `log_completed_trade()` method (line 4529)
**Read By:**
- Dashboard API (`api_enhanced.py`)
- Learning systems (`learn_daily.py`, `learn_weekly.py`, `learn_monthly.py`)
- Performance reports
- `update_account_status()` method (calculates realized P&L)

**Data Integrity Features:**
- ✅ Duplicate prevention (line 4559-4569): Checks for existing Trade_ID before append
- ✅ Append-only: Never modifies existing rows
- ✅ Header auto-creation (line 4532-4557): Creates CSV with proper headers if missing

**CRITICAL:** Trades are written to CSV immediately when positions are closed. No intermediate storage.

---

### 2. Account Status
**File:** `portfolio_data/account_status.json`
**Source of Truth:** DERIVED from completed_trades.csv
**Updated By:** `agent_v5.5.py` → `update_account_status()` method (line 4182)
**Read By:**
- Dashboard API (`api_enhanced.py` → `/api/v2/overview`)
- Agent operations (displays current account value)

**Calculation Logic (Line 4182-4256):**
```python
# 1. Calculate current portfolio value (sum of open positions)
portfolio_value = sum(position.position_size for position in current_portfolio.json)

# 2. Calculate realized P&L from CSV (single source of truth)
realized_pl = sum(row.Return_Dollars for row in completed_trades.csv)

# 3. Calculate cash available
cash_available = STARTING_CAPITAL - portfolio_value + realized_pl

# 4. Calculate account value
account_value = portfolio_value + cash_available
# OR equivalently: STARTING_CAPITAL + realized_pl
```

**Data Flow:**
```
completed_trades.csv → update_account_status() → account_status.json → Dashboard API
```

**CRITICAL:** Account status is ALWAYS recalculated from CSV. Never manually edit account_status.json.

---

### 3. Current Portfolio (Open Positions)
**File:** `portfolio_data/current_portfolio.json`
**Source of Truth:** YES - This is the ONLY source of open positions
**Updated By:**
- `agent_v5.5.py` → Opens positions during GO command
- `agent_v5.5.py` → Removes positions when closed (triggers CSV write)

**Read By:**
- GO command (reviews existing positions)
- Dashboard API (displays active positions)
- `update_account_status()` (calculates invested capital)

**Structure:**
```json
{
  "positions": [
    {
      "ticker": "AAPL",
      "entry_date": "2025-12-24",
      "entry_price": 150.00,
      "shares": 6,
      "position_size": 900.00,
      "stop_loss": 139.50,
      "price_target": 165.00,
      "thesis": "...",
      ...
    }
  ],
  "cash": 100.00,
  "total_value": 1000.00,
  "last_updated": "2025-12-24T10:00:00Z"
}
```

---

### 4. Daily Reviews (Analyze Output)
**Directory:** `daily_reviews/`
**Naming:** `analyze_YYYYMMDD_HHMMSS.json` and `go_YYYYMMDD_HHMMSS.json`
**Source of Truth:** NO - These are REPORTS only, not data sources
**Purpose:** Historical record of decision-making and reasoning

**IMPORTANT:** Daily reviews are for audit/learning purposes only. They do NOT feed into account calculations or dashboard data. The CSV is the authoritative trade record.

---

### 5. Learning Data
**Files:**
- `lessons_learned/` - Weekly and monthly learning insights
- `strategy_evolution/` - Strategy calibration history

**Source of Truth:** DERIVED from completed_trades.csv
**Updated By:** Learning scripts (`learn_daily.py`, `learn_weekly.py`, `learn_monthly.py`)
**Purpose:** Pattern recognition and strategy optimization

**IMPORTANT:** Learning data is regenerated from the CSV. It can be safely deleted/archived.

---

## Data Integrity Guarantees

### ✅ What's Guaranteed:
1. **No duplicate trades** - Trade_ID checked before CSV append (line 4559-4569)
2. **Account value = Starting capital + CSV P&L** - Always recalculated from source
3. **Single write location** - Trades only written to CSV, never to multiple files
4. **Append-only CSV** - Historical data never modified
5. **Atomic operations** - Positions removed from current_portfolio.json when written to CSV

### ⚠️ What to NEVER Do:
1. ❌ **Manually edit completed_trades.csv** - Use agent commands only
2. ❌ **Manually edit account_status.json** - This file is auto-generated
3. ❌ **Delete CSV rows** - Archive the entire file instead
4. ❌ **Trust daily review JSONs for account value** - They're snapshots, not sources
5. ❌ **Create duplicate Trade_IDs** - Format is `{TICKER}_{ENTRY_DATE}`

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADING OPERATIONS                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Open Position   │
                    └──────────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ current_portfolio.json     │ ← Single source for open positions
                │ (positions array updated)  │
                └────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Close Position   │
                    └──────────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ log_completed_trade()      │
                │ - Remove from portfolio    │
                │ - Write to CSV             │
                │ - Duplicate check          │
                └────────────────────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ completed_trades.csv       │ ← SINGLE SOURCE OF TRUTH
                │ (append trade row)         │
                └────────────────────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ update_account_status()    │
                │ - Read ALL trades from CSV │
                │ - Calculate realized P&L   │
                │ - Update account_status    │
                └────────────────────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ account_status.json        │ ← DERIVED DATA
                │ (overwritten each update)  │
                └────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Dashboard API   │
                    │  api_enhanced.py │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Dashboard UI    │
                    │  (User sees data)│
                    └──────────────────┘
```

---

## Verification Commands

### Check Data Consistency:
```bash
# On server - verify CSV trade count
ssh root@174.138.67.26 'wc -l /root/paper_trading_lab/trade_history/completed_trades.csv'
# Should show: 1 (header only after reset)

# On server - verify account status
ssh root@174.138.67.26 'cat /root/paper_trading_lab/portfolio_data/account_status.json'
# Should show: account_value: 1000.0, realized_pl: 0.0

# On server - verify no open positions
ssh root@174.138.67.26 'cat /root/paper_trading_lab/portfolio_data/current_portfolio.json'
# Should show: positions: []
```

### Run System Health Check:
```bash
cd /root/paper_trading_lab
python3 system_health_check.py
```

---

## Recovery Procedures

### If Data Inconsistency Detected:

1. **Stop trading operations immediately**
2. **Backup current state:**
   ```bash
   cd /root/paper_trading_lab
   mkdir -p data_backup_$(date +%Y%m%d_%H%M%S)
   cp -r trade_history/ portfolio_data/ daily_reviews/ data_backup_$(date +%Y%m%d_%H%M%S)/
   ```

3. **Verify CSV integrity:**
   ```bash
   # Check for duplicate Trade_IDs
   cut -d',' -f1 trade_history/completed_trades.csv | sort | uniq -d
   # Should return nothing (no duplicates)
   ```

4. **Regenerate account_status.json:**
   ```python
   # Run agent to recalculate from CSV
   python3 agent_v5.5.py
   # In Python shell:
   from agent_v5.5 import TradingAgent
   agent = TradingAgent()
   agent.update_account_status()
   ```

5. **Compare with backups:**
   ```bash
   diff trade_history/completed_trades.csv data_backup_20251224/trade_history/completed_trades.csv
   ```

---

## Contact and Support

**Data Integrity Issues:** Check this guide first, then review `agent_v5.5.py` code
**Backup Location:** `/root/paper_trading_lab/data_backup_20251224/`
**Last Clean Slate:** December 24, 2025

---

## Version History

- **v1.0 (2025-12-24):** Initial documentation after data reset
  - Clean slate all data files
  - Documented single source of truth architecture
  - Verified duplicate prevention system
  - Confirmed CSV → account_status flow
