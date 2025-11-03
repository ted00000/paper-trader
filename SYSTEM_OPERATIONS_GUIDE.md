# System Operations Guide
**Complete Operations, Monitoring, and Troubleshooting Reference**

---

## Quick Summary

Your system now has **comprehensive operation monitoring** with **zero manual intervention** required for troubleshooting.

### What's New

1. **✅ Robust Error Handling** - All operations automatically track status and capture errors
2. **✅ Admin Dashboard Operations Panel** - Real-time status monitoring with log viewing
3. **✅ System Health Check** - Automated validation of all files and configurations
4. **✅ Log Viewing** - Click-to-view logs for any operation from the dashboard
5. **✅ Auto-Refresh** - Dashboard updates every 30 seconds automatically

---

## Access Points

### Admin Dashboard
**URL:** https://tedbot.ai/admin
**Features:**
- Real-time operations status
- One-click log viewing
- Parameter approval workflow
- Trade history and exclusion overrides

### Public Dashboard
**URL:** https://tedbot.ai
**Features:**
- Portfolio performance
- Active positions
- Win rates
- Completed trades

---

## System Operations

### Automated Daily Schedule

```
8:45 AM (Mon-Fri)  → GO command (Portfolio review, generate recommendations)
9:45 AM (Mon-Fri)  → EXECUTE command (Execute GO decisions at market open)
4:30 PM (Mon-Fri)  → ANALYZE command (Update portfolio with closing prices)
5:00 PM (Mon-Fri)  → LEARN_DAILY (Analyze catalyst performance)
5:30 PM (Friday)   → LEARN_WEEKLY (Generate performance reports)
6:00 PM (Last Sun) → LEARN_MONTHLY (Parameter recommendations)
```

### Operation Status Indicators

**Status Colors:**
- 🟢 **GREEN** (HEALTHY) - Operation completed successfully, fresh data
- 🟡 **YELLOW** (WARNING) - Stale data (>48 hours) or minor issues
- 🔴 **RED** (FAILED) - Operation failed, requires attention
- ⚪ **GRAY** (UNKNOWN) - Operation never run

---

## Monitoring Operations

### Via Admin Dashboard (Recommended)

1. **Login** to https://tedbot.ai/admin
2. **View Operations Status** panel (auto-updates every 30 seconds)
3. **Click "View Log"** on any operation to see full output
4. **Check Overall Health** badge at top of Operations Status section

**What You'll See:**
- **Operation Name** (GO, EXECUTE, ANALYZE, etc.)
- **Status** (SUCCESS, RUNNING, FAILED)
- **Last Run** (e.g., "2.5h ago", "Just now")
- **Error Details** (if any failures)
- **View Log Button** (opens modal with last 200 lines)

### Via Command Line

```bash
# SSH into server
ssh root@174.138.67.26

# Run system health check
cd /root/paper_trading_lab
python3 system_health_check.py

# Check specific operation status
cat dashboard_data/operation_status/go_status.json
cat dashboard_data/operation_status/execute_status.json
cat dashboard_data/operation_status/analyze_status.json

# View logs directly
tail -100 logs/go.log
tail -100 logs/execute.log
tail -100 logs/analyze.log
```

---

## File Structure & Outputs

### Critical Files

```
/root/paper_trading_lab/
├── agent_v5.5.py                    # Main trading agent
├── run_go.sh                        # GO wrapper (robust error handling)
├── run_execute.sh                   # EXECUTE wrapper
├── run_analyze.sh                   # ANALYZE wrapper
├── system_health_check.py           # System validation script
├── operation_status.py              # Status tracking module
│
├── portfolio_data/                  # Portfolio state (updated by operations)
│   ├── pending_positions.json       # Created by GO
│   ├── current_portfolio.json       # Updated by EXECUTE & ANALYZE
│   ├── account_status.json          # Updated by EXECUTE & ANALYZE
│   └── daily_activity.json          # Updated by EXECUTE
│
├── logs/                            # Operation logs
│   ├── go.log                       # GO command output
│   ├── execute.log                  # EXECUTE command output
│   ├── analyze.log                  # ANALYZE command output
│   ├── learn_daily.log              # Daily learning output
│   ├── learn_weekly.log             # Weekly reports
│   └── learn_monthly.log            # Monthly recommendations
│
├── dashboard_data/                  # Dashboard state
│   ├── system_health.json           # Health check results
│   ├── pending_actions.json         # Parameter recommendations
│   └── operation_status/            # Real-time operation status
│       ├── go_status.json
│       ├── execute_status.json
│       ├── analyze_status.json
│       └── learn_daily_status.json
│
└── trade_history/                   # Historical data
    └── completed_trades.csv         # All closed trades
```

### Status File Format

```json
{
  "operation": "GO",
  "last_run": "2025-11-03T08:45:02",
  "status": "SUCCESS",
  "log_file": "/root/paper_trading_lab/logs/go.log",
  "error": null
}
```

**Status Values:**
- `RUNNING` - Operation currently executing
- `SUCCESS` - Completed successfully
- `FAILED` - Failed with error (see `error` field)
- `NEVER_RUN` - Operation hasn't run yet

---

## Troubleshooting Guide

### Issue: Operation Shows as FAILED

**Symptoms:**
- Red indicator in dashboard
- Error message in operation card
- Dashboard data not updating

**Steps:**

1. **View the log** from admin dashboard (click "View Log" button)

2. **Common Errors & Fixes:**

   **Error:** `agent_v5.0.py: No such file or directory`
   - **Fix:** Wrapper script referencing wrong version
   - **Solution:** Edit run_*.sh and change to `agent_v5.5.py`

   **Error:** `Virtual environment not found`
   - **Fix:** Python venv missing or broken
   - **Solution:** Rebuild venv:
     ```bash
     cd /root/paper_trading_lab
     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ```

   **Error:** `Environment file not found`
   - **Fix:** ~/.env missing
   - **Solution:** Check ~/.env exists with all required variables

   **Error:** `API key invalid`
   - **Fix:** Anthropic or Polygon API key expired/invalid
   - **Solution:** Update keys in ~/.env

3. **Manually run operation** to test:
   ```bash
   cd /root/paper_trading_lab
   source venv/bin/activate
   source /root/.env

   # Test GO
   python3 agent_v5.5.py go

   # Test EXECUTE
   python3 agent_v5.5.py execute

   # Test ANALYZE
   python3 agent_v5.5.py analyze
   ```

4. **Check crontab** is correct:
   ```bash
   crontab -l | grep -E 'go|execute|analyze'
   ```

### Issue: Operation Never Runs

**Symptoms:**
- Status shows "NEVER_RUN" or very old timestamp
- No recent log entries

**Steps:**

1. **Check cron is running:**
   ```bash
   systemctl status cron
   ```

2. **Check crontab schedule:**
   ```bash
   crontab -l
   ```

3. **Check for cron errors:**
   ```bash
   tail -50 /var/mail/root
   ```

4. **Manually trigger** to test:
   ```bash
   /root/paper_trading_lab/run_go.sh
   ```

### Issue: Dashboard Not Showing Operations

**Symptoms:**
- Operations Status panel shows "Loading..." forever
- No operation cards displayed

**Steps:**

1. **Check operation status files exist:**
   ```bash
   ls -la /root/paper_trading_lab/dashboard_data/operation_status/
   ```

2. **Run health check:**
   ```bash
   cd /root/paper_trading_lab
   python3 system_health_check.py
   ```

3. **Check dashboard server logs:**
   ```bash
   # If running in screen
   screen -r dashboard

   # Check for errors in browser console (F12)
   ```

4. **Restart dashboard:**
   ```bash
   screen -r dashboard
   # Ctrl+C to stop
   ./start_dashboard.sh
   # Ctrl+A then D to detach
   ```

### Issue: Data Not Updating on Public Dashboard

**Symptoms:**
- tedbot.ai showing old data
- Timestamps not current

**Steps:**

1. **Check portfolio files timestamp:**
   ```bash
   ls -lh /root/paper_trading_lab/portfolio_data/*.json
   ```

2. **Check ANALYZE ran recently:**
   ```bash
   tail -50 /root/paper_trading_lab/logs/analyze.log
   ```

3. **Browser cache issue:**
   - Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
   - Clear cache for tedbot.ai

4. **Check nginx serving correct directory:**
   ```bash
   cat /etc/nginx/sites-available/trading-dashboard | grep root
   ```

---

## Running Operations Manually

### When to Run Manually

- **After fixing an error** - Test the fix works
- **After system downtime** - Bring data up to date
- **For testing** - Verify changes before deploying

### Manual Commands

```bash
# Always run from correct directory with environment
cd /root/paper_trading_lab
source venv/bin/activate
source /root/.env

# GO - Generate position recommendations
python3 agent_v5.5.py go

# EXECUTE - Execute pending trades
python3 agent_v5.5.py execute

# ANALYZE - Update portfolio with latest prices
python3 agent_v5.5.py analyze

# Learning scripts
python3 learn_daily.py
python3 learn_weekly.py
python3 learn_monthly.py

# System health check
python3 system_health_check.py
```

### Safe Manual Workflow

```bash
# 1. Check current state
python3 system_health_check.py

# 2. Run ANALYZE to update portfolio
python3 agent_v5.5.py analyze

# 3. Check status updated
cat dashboard_data/operation_status/analyze_status.json

# 4. Refresh dashboard
# Visit: https://tedbot.ai/admin
```

---

## System Health Check

### Running Health Check

```bash
cd /root/paper_trading_lab
python3 system_health_check.py
```

### What It Checks

1. **Required Files** - All scripts and configurations present
2. **Required Directories** - All data directories exist
3. **Operation Status** - All operations ran recently and successfully
4. **File References** - Wrapper scripts reference correct agent version
5. **Environment Variables** - All required vars set in ~/.env

### Example Output

```
======================================================================
PAPER TRADING LAB - SYSTEM HEALTH CHECK
Time: 2025-11-03 10:30:00
======================================================================

✅ PASSED CHECKS:
----------------------------------------------------------------------
  ✓ agent_v5.5.py: Main trading agent
  ✓ run_go.sh: GO wrapper script (correct version)
  ✓ run_execute.sh: EXECUTE wrapper script (correct version)
  ✓ run_analyze.sh: ANALYZE wrapper script (correct version)
  ✓ GO: Log updated 2.5 hours ago
  ✓ GO: Last run successful
  ✓ EXECUTE: Output fresh (2.5 hours old)

⚠️  WARNINGS:
----------------------------------------------------------------------
  ⚠ ANALYZE: Log not updated in 50.2 hours

🚨 CRITICAL ISSUES:
----------------------------------------------------------------------
  ✗ LEARN_DAILY: Log file missing (logs/learn_daily.log)

======================================================================
SUMMARY: 12 passed, 1 warnings, 1 critical
======================================================================
```

---

## Deployment Checklist

### After Making Changes

When you update any system files, follow this checklist:

- [ ] **Test locally** if possible
- [ ] **Push to server:**
  ```bash
  # On local machine
  git add .
  git commit -m "Description of changes"
  git push origin master

  # On server
  ssh root@174.138.67.26
  cd /root/paper_trading_lab
  git pull
  ```
- [ ] **Run health check:**
  ```bash
  python3 system_health_check.py
  ```
- [ ] **Test operations manually:**
  ```bash
  ./run_go.sh
  ./run_execute.sh
  ./run_analyze.sh
  ```
- [ ] **Restart dashboard:**
  ```bash
  screen -r dashboard
  # Ctrl+C, then ./start_dashboard.sh
  ```
- [ ] **Check admin dashboard:** https://tedbot.ai/admin
- [ ] **Verify crontab:** `crontab -l`

---

## Best Practices

### Daily Monitoring

1. **Check admin dashboard** once per day
2. **Verify all operations green** in Operations Status panel
3. **Review any FAILED operations** immediately
4. **Check for pending actions** requiring approval

### Weekly Review

1. **Review completed trades** section in admin dashboard
2. **Check exclusion overrides** - Did Claude's overrides work?
3. **Monitor win rate trends** in System Status
4. **Review weekly report** (generated Friday 5:30 PM)

### Monthly Tasks

1. **Review parameter recommendations** (last Sunday 6:00 PM)
2. **Approve or reject recommendations** in admin dashboard
3. **Apply approved changes** to agent_v5.5.py
4. **Run system health check** to verify everything current

---

## Emergency Procedures

### System Completely Down

```bash
# 1. SSH into server
ssh root@174.138.67.26

# 2. Check system health
cd /root/paper_trading_lab
python3 system_health_check.py

# 3. Check cron is running
systemctl status cron

# 4. Check for errors
tail -100 /var/mail/root

# 5. Manually run operations to bring up to date
./run_go.sh
./run_execute.sh
./run_analyze.sh

# 6. Verify dashboard server running
screen -r dashboard

# 7. Check admin dashboard
# Visit: https://tedbot.ai/admin
```

### Critical Operation Failing Repeatedly

```bash
# 1. View full log
tail -200 logs/[operation].log

# 2. Check status file
cat dashboard_data/operation_status/[operation]_status.json

# 3. Test manually with verbose output
cd /root/paper_trading_lab
source venv/bin/activate
source /root/.env
python3 agent_v5.5.py [command] 2>&1 | tee test_output.log

# 4. Contact support with test_output.log
```

---

## Support & Maintenance

### Log Rotation

Logs are appended indefinitely. To prevent disk space issues:

```bash
# Check log sizes
du -h logs/*.log

# Rotate old logs (optional)
cd logs
for log in *.log; do
    mv "$log" "$log.$(date +%Y%m%d)"
    gzip "$log.$(date +%Y%m%d)"
done
```

### Backup Critical Data

```bash
# Backup trade history
cp trade_history/completed_trades.csv ~/backups/trades_$(date +%Y%m%d).csv

# Backup portfolio state
cp -r portfolio_data ~/backups/portfolio_$(date +%Y%m%d)

# Backup learning data
cp catalyst_exclusions.json ~/backups/exclusions_$(date +%Y%m%d).json
```

---

## Summary

**You now have:**

✅ **Zero-friction monitoring** - Operations status visible at a glance
✅ **One-click log viewing** - No more SSH required for troubleshooting
✅ **Automated error tracking** - Every operation logs success/failure
✅ **Self-documenting system** - Health check validates everything
✅ **Real-time updates** - Dashboard refreshes automatically

**Your workflow:**

1. Check admin dashboard daily
2. Review operations status (all green = good)
3. Click "View Log" if any issues
4. Approve monthly parameter recommendations
5. Done!

No more manual log tailing, no more guessing what failed, no more "pain in the ass" troubleshooting sessions.

**Questions?** Check this guide or run `python3 system_health_check.py` for diagnostics.
