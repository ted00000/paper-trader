# TedBot Backup & Recovery System

**Status:** ✅ ACTIVE
**Last Updated:** December 24, 2025
**Implementation:** Complete with 3-layer redundancy

---

## System Overview

Your trading data is now protected by a **comprehensive 3-layer backup system** with geographic redundancy and automated monitoring.

### Backup Layers

1. **Hourly Server Backups** (Layer 1)
   - Location: Server `/root/paper_trading_lab/backups/hourly/`
   - Frequency: Every hour
   - Retention: 168 backups (7 days)
   - Purpose: Fast recovery from recent issues

2. **Daily Off-Site Backups** (Layer 2)
   - Location: Your Mac `/Users/tednunes/Downloads/paper_trading_lab_backups/`
   - Frequency: Daily at 1:00 AM
   - Retention: 30 days
   - Purpose: Geographic redundancy, disaster recovery

3. **Health Monitoring** (Layer 3)
   - Frequency: Every 6 hours
   - Checks: File integrity, backup age, disk space
   - Alerts: Logs warnings/errors for review

---

## What's Backed Up

### Critical Files (Every Hour)
- ✅ `trade_history/completed_trades.csv` - Trade record (single source of truth)
- ✅ `portfolio_data/account_status.json` - Account summary
- ✅ `portfolio_data/current_portfolio.json` - Open positions
- ✅ `config/.env` - API keys and configuration

### Full Data (Daily Off-Site)
- ✅ All critical files above
- ✅ `daily_reviews/` - Decision history and analysis
- ✅ `strategy_evolution/` - Learning data and insights
- ✅ Backup manifests with timestamps

---

## Automated Schedule

### Server (174.138.67.26)
```bash
# Hourly backup - Every hour at :00
0 * * * * /root/paper_trading_lab/backup_hourly.sh

# Health monitor - Every 6 hours
0 */6 * * * /root/paper_trading_lab/backup_monitor.sh
```

### Your Mac
```bash
# Daily off-site backup - 1:00 AM every day
0 1 * * * /Users/tednunes/Downloads/paper_trading_lab/backup_daily_offsite.sh
```

---

## Recovery Scenarios

### Scenario 1: Recent Data Loss (Last Few Hours)
**Use: Hourly server backup**

```bash
# SSH to server
ssh root@174.138.67.26

# List available backups
ls -lt /root/paper_trading_lab/backups/hourly/

# Restore from latest backup
cd /root/paper_trading_lab
./restore_from_backup.sh latest

# Or restore from specific time
./restore_from_backup.sh 20251224_150000
```

**Recovery Time:** < 1 minute
**Data Loss:** Up to 1 hour

### Scenario 2: Data Loss (Last Few Days)
**Use: Daily off-site backup**

```bash
# On your Mac - List available backups
ls -lt /Users/tednunes/Downloads/paper_trading_lab_backups/

# Check what's in a backup
cat /Users/tednunes/Downloads/paper_trading_lab_backups/offsite_20251224/manifest.json

# Restore to server
rsync -az /Users/tednunes/Downloads/paper_trading_lab_backups/offsite_20251224/ \
  root@174.138.67.26:/root/paper_trading_lab/

# Restart dashboard API
ssh root@174.138.67.26 'systemctl restart dashboard-api-v2'
```

**Recovery Time:** 2-5 minutes
**Data Loss:** Up to 24 hours

### Scenario 3: Complete Server Failure
**Use: Latest off-site backup + git**

```bash
# 1. Set up new server with fresh code
git clone <repository> /root/paper_trading_lab

# 2. Restore data from your Mac
rsync -az /Users/tednunes/Downloads/paper_trading_lab_backups/latest/ \
  root@<new-server>:/root/paper_trading_lab/

# 3. Deploy dashboard
cd /Users/tednunes/Downloads/paper_trading_lab
./deploy_dashboard_v2.sh
```

**Recovery Time:** 10-30 minutes
**Data Loss:** Up to 24 hours

---

## Monitoring & Verification

### Check Backup Health
```bash
# On server
ssh root@174.138.67.26 '/root/paper_trading_lab/backup_monitor.sh'

# Expected output:
# ✅ HEALTHY
#   - XX backups available
#   - Latest backup: X hours old
#   - All critical files present
#   - Disk usage: XX%
```

### View Backup Logs
```bash
# Server hourly backup log
ssh root@174.138.67.26 'tail -50 /root/paper_trading_lab/logs/backup_hourly.log'

# Server health monitor log
ssh root@174.138.67.26 'tail -50 /root/paper_trading_lab/logs/backup_monitor.log'

# Local off-site backup log
tail -50 /Users/tednunes/Downloads/paper_trading_lab_backups/backup.log
```

### Manual Backup (Anytime)
```bash
# Server backup
ssh root@174.138.67.26 '/root/paper_trading_lab/backup_hourly.sh'

# Off-site backup
/Users/tednunes/Downloads/paper_trading_lab/backup_daily_offsite.sh
```

---

## Storage Usage

### Current Estimates
- **Per hourly backup:** ~32 KB
- **168 hourly backups (7 days):** ~5.4 MB
- **Per daily backup:** ~44 KB
- **30 daily backups:** ~1.3 MB

### Total Storage Required
- **Server:** ~10 MB (hourly backups)
- **Local Mac:** ~2 MB (daily backups)
- **Combined:** ~12 MB total

**Cost:** Negligible - less than 0.1% of available disk space

---

## Data Protection Guarantees

### ✅ What You're Protected Against
1. **Accidental deletion** - Recover from any of 168+ backups
2. **Data corruption** - Restore known-good state from backup
3. **Server failure** - Full recovery from off-site backup
4. **Trading errors** - Revert to pre-error state
5. **Ransomware** - Off-site backups are isolated
6. **Disk failure** - Geographic redundancy (server + Mac)

### ⏱️ Recovery Time Objectives
- **Recent data loss (< 1 hour):** < 1 minute
- **Recent data loss (< 24 hours):** 2-5 minutes
- **Complete disaster recovery:** 10-30 minutes

### 📊 Data Loss Objectives
- **Maximum data loss:** 24 hours (worst case)
- **Typical data loss:** < 1 hour (with hourly backups)
- **Zero data loss scenario:** Manual backup before risky operations

---

## Best Practices

### Before Risky Operations
```bash
# Create immediate backup before manual changes
ssh root@174.138.67.26 '/root/paper_trading_lab/backup_hourly.sh'
```

### Weekly Verification (Recommended)
```bash
# 1. Check backup health
ssh root@174.138.67.26 '/root/paper_trading_lab/backup_monitor.sh'

# 2. Verify off-site backup exists
ls -lt /Users/tednunes/Downloads/paper_trading_lab_backups/ | head -5

# 3. Check backup logs for errors
ssh root@174.138.67.26 'grep -i error /root/paper_trading_lab/logs/backup_*.log'
```

### Monthly Test Recovery (Recommended)
```bash
# Test restore process (dry run)
# 1. Pick a random backup
# 2. Restore to temporary location
# 3. Verify data integrity
# 4. Delete test restoration

# This ensures recovery procedures work when needed
```

---

## Troubleshooting

### Issue: Hourly backups not running
```bash
# Check cron is running
ssh root@174.138.67.26 'systemctl status cron'

# View crontab
ssh root@174.138.67.26 'crontab -l | grep backup'

# Check logs
ssh root@174.138.67.26 'tail -100 /root/paper_trading_lab/logs/backup_hourly.log'
```

### Issue: Off-site backup failing
```bash
# Test SSH connection
ssh root@174.138.67.26 'echo "Connection OK"'

# Test rsync manually
rsync -avz root@174.138.67.26:/root/paper_trading_lab/trade_history/ /tmp/test_sync/

# Check local crontab
crontab -l | grep backup
```

### Issue: Disk space full
```bash
# Check server disk usage
ssh root@174.138.67.26 'df -h /root/paper_trading_lab/backups'

# Manually clean old backups (keeps last 100)
ssh root@174.138.67.26 'cd /root/paper_trading_lab/backups/hourly && ls -1td backup_* | tail -n +101 | xargs rm -rf'

# Check local Mac disk usage
du -sh /Users/tednunes/Downloads/paper_trading_lab_backups/
```

---

## Scripts Reference

### Available Scripts

1. **backup_hourly.sh** (Server)
   - Creates timestamped backup of critical files
   - Rotates backups (keeps 168 hours)
   - Logs to `logs/backup_hourly.log`

2. **backup_daily_offsite.sh** (Mac)
   - Syncs full data from server to local machine
   - Rotates backups (keeps 30 days)
   - Creates `latest` symlink for easy access

3. **backup_monitor.sh** (Server)
   - Validates backup integrity
   - Checks backup age and file presence
   - Alerts on issues

4. **restore_from_backup.sh** (Server)
   - Interactive restoration tool
   - Creates pre-restore backup
   - Restarts services automatically

### Manual Operations

```bash
# Create immediate backup
ssh root@174.138.67.26 '/root/paper_trading_lab/backup_hourly.sh'

# Run health check
ssh root@174.138.67.26 '/root/paper_trading_lab/backup_monitor.sh'

# Create off-site backup
/Users/tednunes/Downloads/paper_trading_lab/backup_daily_offsite.sh

# Restore from backup
ssh root@174.138.67.26 '/root/paper_trading_lab/restore_from_backup.sh latest'
```

---

## Contact & Support

**Backup System Status:** ✅ Fully Operational
**Next Review Date:** Weekly monitoring recommended
**Critical Alerts:** Check logs in `/root/paper_trading_lab/logs/backup_*.log`

**Emergency Recovery Contact:**
- Data Integrity Guide: `DATA_INTEGRITY_GUIDE.md`
- Backup logs: `logs/backup_*.log`
- Off-site backups: `/Users/tednunes/Downloads/paper_trading_lab_backups/`

---

## System Health Checklist

- [x] Hourly server backups enabled
- [x] Daily off-site backups enabled
- [x] Backup health monitoring active
- [x] 168-hour retention configured
- [x] 30-day off-site retention configured
- [x] Recovery procedures tested
- [x] Geographic redundancy established
- [x] Automated rotation working

**Status:** All systems operational ✅

---

*Last backup health check: Automated every 6 hours*
*Last successful backup: View logs for real-time status*
*Recovery tested: December 24, 2025*
