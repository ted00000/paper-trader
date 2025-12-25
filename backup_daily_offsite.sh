#!/bin/bash
# Daily Off-Server Backup Script - Run on Local Mac
# Syncs critical data from server to local machine for geographic redundancy
# Keeps 30-day rolling backup history

set -e

SERVER="root@174.138.67.26"
PROJECT_DIR="/root/paper_trading_lab"
LOCAL_BACKUP_ROOT="/Users/tednunes/Downloads/paper_trading_lab_backups"
TIMESTAMP=$(date +%Y%m%d)
BACKUP_NAME="offsite_$TIMESTAMP"

# Create local backup directory structure
mkdir -p "$LOCAL_BACKUP_ROOT"

echo "========================================="
echo "TedBot Daily Off-Site Backup - $(date)"
echo "========================================="
echo ""

# Create timestamped backup directory
BACKUP_PATH="$LOCAL_BACKUP_ROOT/$BACKUP_NAME"
mkdir -p "$BACKUP_PATH"

echo "[1/5] Syncing trade history from server..."
mkdir -p "$BACKUP_PATH/trade_history"
rsync -az --progress "$SERVER:$PROJECT_DIR/trade_history/" "$BACKUP_PATH/trade_history/" || echo "  ⚠️ Trade history sync failed"

echo ""
echo "[2/5] Syncing portfolio data from server..."
mkdir -p "$BACKUP_PATH/portfolio_data"
rsync -az --progress "$SERVER:$PROJECT_DIR/portfolio_data/" "$BACKUP_PATH/portfolio_data/" || echo "  ⚠️ Portfolio data sync failed"

echo ""
echo "[3/5] Syncing daily reviews from server..."
mkdir -p "$BACKUP_PATH/daily_reviews"
rsync -az --progress "$SERVER:$PROJECT_DIR/daily_reviews/" "$BACKUP_PATH/daily_reviews/" --exclude='archive_*' || echo "  ⚠️ Daily reviews sync failed"

echo ""
echo "[4/5] Syncing learning data from server..."
mkdir -p "$BACKUP_PATH/strategy_evolution"
rsync -az --progress "$SERVER:$PROJECT_DIR/strategy_evolution/" "$BACKUP_PATH/strategy_evolution/" || echo "  ⚠️ Strategy evolution sync failed"

echo ""
echo "[5/5] Creating backup manifest..."

# Get account status from server
ACCOUNT_STATUS=$(ssh "$SERVER" "cat $PROJECT_DIR/portfolio_data/account_status.json 2>/dev/null" || echo '{"status": "unavailable"}')

cat > "$BACKUP_PATH/manifest.json" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "backup_type": "daily_offsite",
  "server": "$SERVER",
  "local_path": "$BACKUP_PATH",
  "account_snapshot": $ACCOUNT_STATUS,
  "files_synced": [
    "trade_history/",
    "portfolio_data/",
    "daily_reviews/",
    "strategy_evolution/"
  ]
}
EOF

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)
echo "✅ Off-site backup complete: $BACKUP_NAME ($BACKUP_SIZE)"

# Rotation: Keep only last 30 days
echo ""
echo "Rotating old backups (keeping last 30 days)..."
find "$LOCAL_BACKUP_ROOT" -maxdepth 1 -name "offsite_*" -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null || true

BACKUP_COUNT=$(ls -1d "$LOCAL_BACKUP_ROOT"/offsite_* 2>/dev/null | wc -l | tr -d ' ')
echo "✅ Currently have $BACKUP_COUNT daily backups"

# Create latest symlink for easy access
rm -f "$LOCAL_BACKUP_ROOT/latest"
ln -s "$BACKUP_PATH" "$LOCAL_BACKUP_ROOT/latest"

# Summary
echo ""
echo "========================================="
echo "Off-Site Backup Summary:"
echo "  Server: $SERVER"
echo "  Local Path: $BACKUP_PATH"
echo "  Size: $BACKUP_SIZE"
echo "  Total backups: $BACKUP_COUNT"
echo "  Latest: $LOCAL_BACKUP_ROOT/latest"
echo "========================================="
echo ""
echo "To restore from this backup:"
echo "  rsync -az $BACKUP_PATH/ $SERVER:$PROJECT_DIR/"
echo "========================================="
