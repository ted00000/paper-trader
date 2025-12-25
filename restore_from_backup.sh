#!/bin/bash
# Backup Restoration Script
# Restores trading data from a backup to recover from data loss or corruption
# USAGE: ./restore_from_backup.sh [backup_timestamp]
#   Example: ./restore_from_backup.sh 20251224_150000
#   Or: ./restore_from_backup.sh latest (to restore from most recent)

set -e

PROJECT_DIR="/root/paper_trading_lab"
BACKUP_DIR="$PROJECT_DIR/backups/hourly"

# Check if backup timestamp provided
if [ -z "$1" ]; then
  echo "Usage: $0 [backup_timestamp|latest]"
  echo ""
  echo "Available backups:"
  ls -1t "$BACKUP_DIR" | head -10
  exit 1
fi

# Determine backup path
if [ "$1" = "latest" ]; then
  BACKUP_PATH=$(ls -1td "$BACKUP_DIR"/backup_* | head -1)
  if [ -z "$BACKUP_PATH" ]; then
    echo "❌ ERROR: No backups found in $BACKUP_DIR"
    exit 1
  fi
else
  BACKUP_PATH="$BACKUP_DIR/backup_$1"
fi

# Verify backup exists
if [ ! -d "$BACKUP_PATH" ]; then
  echo "❌ ERROR: Backup not found: $BACKUP_PATH"
  echo ""
  echo "Available backups:"
  ls -1t "$BACKUP_DIR" | head -10
  exit 1
fi

echo "========================================="
echo "TedBot Data Restoration"
echo "========================================="
echo ""
echo "⚠️  WARNING: This will overwrite current data!"
echo ""
echo "Backup to restore:"
echo "  Path: $BACKUP_PATH"
echo "  Created: $(stat -c %y "$BACKUP_PATH" 2>/dev/null || stat -f %Sm "$BACKUP_PATH")"
echo ""

# Show manifest if available
if [ -f "$BACKUP_PATH/manifest.json" ]; then
  echo "Backup manifest:"
  cat "$BACKUP_PATH/manifest.json" | python3 -m json.tool 2>/dev/null || cat "$BACKUP_PATH/manifest.json"
  echo ""
fi

read -p "Are you sure you want to restore from this backup? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Restoration cancelled."
  exit 0
fi

# Create pre-restore backup of current state
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PRE_RESTORE_BACKUP="$PROJECT_DIR/backups/pre_restore_$TIMESTAMP"
echo ""
echo "Creating pre-restore backup of current state..."
mkdir -p "$PRE_RESTORE_BACKUP"
cp -r "$PROJECT_DIR/trade_history" "$PRE_RESTORE_BACKUP/" 2>/dev/null || true
cp -r "$PROJECT_DIR/portfolio_data" "$PRE_RESTORE_BACKUP/" 2>/dev/null || true
echo "✅ Current state backed up to: $PRE_RESTORE_BACKUP"

# Restore data
echo ""
echo "Restoring data..."

echo "[1/3] Restoring trade history..."
if [ -d "$BACKUP_PATH/trade_history" ]; then
  cp -f "$BACKUP_PATH/trade_history/"* "$PROJECT_DIR/trade_history/" 2>/dev/null || echo "  (no files to restore)"
  echo "  ✅ Trade history restored"
else
  echo "  ⚠️ No trade history in backup"
fi

echo "[2/3] Restoring portfolio data..."
if [ -d "$BACKUP_PATH/portfolio_data" ]; then
  cp -f "$BACKUP_PATH/portfolio_data/"* "$PROJECT_DIR/portfolio_data/" 2>/dev/null || echo "  (no files to restore)"
  echo "  ✅ Portfolio data restored"
else
  echo "  ⚠️ No portfolio data in backup"
fi

echo "[3/3] Restoring configuration..."
if [ -f "$BACKUP_PATH/config/.env" ]; then
  cp -f "$BACKUP_PATH/config/.env" "$PROJECT_DIR/.env" 2>/dev/null || echo "  (no .env to restore)"
  echo "  ✅ Configuration restored"
else
  echo "  ⚠️ No configuration in backup"
fi

# Restart services to pick up restored data
echo ""
echo "Restarting dashboard API to use restored data..."
systemctl restart dashboard-api-v2 2>/dev/null || echo "  ⚠️ Could not restart dashboard-api-v2 (may not be on server)"

echo ""
echo "========================================="
echo "✅ Restoration Complete"
echo "========================================="
echo ""
echo "Restored from: $BACKUP_PATH"
echo "Pre-restore backup: $PRE_RESTORE_BACKUP"
echo ""
echo "Next steps:"
echo "  1. Verify data at https://tedbot.ai"
echo "  2. Check account status: cat $PROJECT_DIR/portfolio_data/account_status.json"
echo "  3. If issues, restore from pre-restore backup: $PRE_RESTORE_BACKUP"
echo "========================================="
