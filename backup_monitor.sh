#!/bin/bash
# Backup Health Monitor - Checks backup integrity and alerts on issues
# Can be run manually or via cron to verify backup system health

set -e

PROJECT_DIR="/root/paper_trading_lab"
BACKUP_DIR="$PROJECT_DIR/backups/hourly"

echo "========================================="
echo "TedBot Backup Health Monitor"
echo "$(date)"
echo "========================================="
echo ""

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
  echo "❌ CRITICAL: Backup directory does not exist: $BACKUP_DIR"
  exit 1
fi

# Count backups
BACKUP_COUNT=$(ls -1d "$BACKUP_DIR"/backup_* 2>/dev/null | wc -l)
echo "[1/5] Backup Count Check"
echo "  Total backups: $BACKUP_COUNT"

if [ "$BACKUP_COUNT" -eq 0 ]; then
  echo "  ❌ CRITICAL: No backups found!"
  exit 1
elif [ "$BACKUP_COUNT" -lt 24 ]; then
  echo "  ⚠️ WARNING: Less than 24 hours of backups available"
else
  echo "  ✅ Healthy: $BACKUP_COUNT backups available"
fi

# Check age of most recent backup
echo ""
echo "[2/5] Backup Recency Check"
LATEST_BACKUP=$(ls -1td "$BACKUP_DIR"/backup_* 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
  echo "  ❌ CRITICAL: No backups found"
  exit 1
fi

BACKUP_AGE=$(($(date +%s) - $(stat -c %Y "$LATEST_BACKUP" 2>/dev/null || stat -f %m "$LATEST_BACKUP")))
BACKUP_AGE_HOURS=$((BACKUP_AGE / 3600))

echo "  Latest backup: $(basename "$LATEST_BACKUP")"
echo "  Age: $BACKUP_AGE_HOURS hours ago"

if [ "$BACKUP_AGE_HOURS" -gt 2 ]; then
  echo "  ❌ CRITICAL: Latest backup is over 2 hours old!"
  exit 1
else
  echo "  ✅ Healthy: Recent backup found"
fi

# Check critical files in latest backup
echo ""
echo "[3/5] File Integrity Check"
CRITICAL_FILES=(
  "trade_history/completed_trades.csv"
  "portfolio_data/account_status.json"
  "portfolio_data/current_portfolio.json"
  "manifest.json"
)

ALL_FILES_OK=true
for file in "${CRITICAL_FILES[@]}"; do
  if [ -f "$LATEST_BACKUP/$file" ]; then
    FILE_SIZE=$(stat -c %s "$LATEST_BACKUP/$file" 2>/dev/null || stat -f %z "$LATEST_BACKUP/$file")
    echo "  ✅ $file ($FILE_SIZE bytes)"
  else
    echo "  ❌ MISSING: $file"
    ALL_FILES_OK=false
  fi
done

if [ "$ALL_FILES_OK" = false ]; then
  echo "  ❌ CRITICAL: Some critical files are missing from backup!"
  exit 1
fi

# Check total backup size
echo ""
echo "[4/5] Backup Size Analysis"
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "  Total backup storage: $TOTAL_SIZE"
echo "  Average per backup: $(du -sh "$LATEST_BACKUP" | cut -f1)"

# Check disk space
echo ""
echo "[5/5] Disk Space Check"
DISK_USAGE=$(df -h "$BACKUP_DIR" | tail -1 | awk '{print $5}' | sed 's/%//')
echo "  Disk usage: $DISK_USAGE%"

if [ "$DISK_USAGE" -gt 90 ]; then
  echo "  ❌ CRITICAL: Disk usage above 90%!"
  exit 1
elif [ "$DISK_USAGE" -gt 80 ]; then
  echo "  ⚠️ WARNING: Disk usage above 80%"
else
  echo "  ✅ Healthy: Sufficient disk space"
fi

# Summary
echo ""
echo "========================================="
echo "Backup Health Summary: ✅ HEALTHY"
echo "  - $BACKUP_COUNT backups available"
echo "  - Latest backup: $BACKUP_AGE_HOURS hours old"
echo "  - All critical files present"
echo "  - Disk usage: $DISK_USAGE%"
echo "========================================="
exit 0
