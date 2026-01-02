# Tedbot Cron Schedule

## Current Automated Jobs

### 1. Market Screener (Primary Discovery)
**Script**: `run_screener.sh`
**Schedule**: `0 7 * * 1-5` (7:00 AM ET, Monday-Friday)
**Duration**: ~5-10 minutes
**Purpose**: Scan S&P 1500 universe for high-probability candidates
**Output**: `screener_candidates.json` (top 40 stocks)

**Cron Entry**:
```bash
0 7 * * 1-5 /root/paper_trading_lab/run_screener.sh
```

---

### 2. Near-Miss Forward Return Updater (v10.4)
**Script**: `run_near_miss_updater.sh`
**Schedule**: `0 20 * * *` (8:00 PM ET, daily)
**Duration**: ~1-2 minutes
**Purpose**: Track performance of rejected near-miss stocks
**Output**: Updates `strategy_evolution/near_miss_log.csv` with forward returns

**Cron Entry**:
```bash
0 20 * * * /root/paper_trading_lab/run_near_miss_updater.sh
```

**Details**:
- Runs daily after market close (4:00 PM) + data settlement (4 hours)
- Updates any near-miss records where:
  - 5+ days have passed → fills Forward_5d column
  - 10+ days have passed → fills Forward_10d column
  - 20+ days have passed → fills Forward_20d column
- Incremental: only fills empty columns (idempotent)
- Generates summary statistics (average return, win rate)

**Learning Objective**:
Compare near-miss performance to accepted candidates to determine if gates are:
- **Too strict**: Rejecting tomorrow's winners → Lower thresholds
- **Appropriate**: Near-misses underperform → Keep current gates
- **Too loose**: Need tighter controls → Raise thresholds

---

## Manual Operations

### GO Command (Decision Making)
**Run**: `python3 agent_v5.5.py go`
**Schedule**: Manual, 9:00 AM ET (15 min before open)
**Purpose**: Claude analyzes screener candidates and selects top 10
**Output**: `pending_positions.json`

### EXECUTE Command (Trade Execution)
**Run**: `python3 agent_v5.5.py execute`
**Schedule**: Manual, 9:45 AM ET (15 min after open)
**Purpose**: Execute trades from pending_positions.json
**Output**: Updated `current_portfolio.json`, `daily_picks.csv`

### ANALYZE Command (End-of-Day Review)
**Run**: `python3 agent_v5.5.py analyze`
**Schedule**: Manual, 4:15 PM ET (after market close)
**Purpose**: Exit management, strategy learning, performance reporting
**Output**: `daily_reviews/`, updated `strategy_context.json`

---

## Installation Status

✅ **Near-miss updater is ACTIVE in cron** (added 2026-01-01)

Current cron entry:
```bash
0 20 * * * /root/paper_trading_lab/run_near_miss_updater.sh
```

To verify:
```bash
crontab -l | grep near_miss
```

## Monitoring

### Check Last Run Status
```bash
# Screener status
cat /root/paper_trading_lab/dashboard_data/operation_status/screener_status.json

# Near-miss updater status
cat /root/paper_trading_lab/dashboard_data/operation_status/near_miss_updater_status.json
```

### View Logs
```bash
# Screener log
tail -100 /root/paper_trading_lab/logs/screener.log

# Near-miss updater log
tail -100 /root/paper_trading_lab/logs/near_miss_updater.log
```

### Check Near-Miss Performance
```bash
# View CSV
cat /root/paper_trading_lab/strategy_evolution/near_miss_log.csv

# Count updates
tail -n +2 /root/paper_trading_lab/strategy_evolution/near_miss_log.csv | awk -F, '{if ($12 != "") count5++; if ($13 != "") count10++; if ($14 != "") count20++} END {print "5-day:", count5, "| 10-day:", count10, "| 20-day:", count20}'
```

---

**Last Updated**: 2026-01-01
**Version**: v10.4 (Near-Miss Learning)
