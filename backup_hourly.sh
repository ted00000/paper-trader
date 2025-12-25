#!/bin/bash
# Hourly Automated Backup Script - Server-side
# Creates timestamped backups of critical trading data
# Rotates backups to keep last 168 hours (7 days)

set -e

PROJECT_DIR="/root/paper_trading_lab"
BACKUP_DIR="$PROJECT_DIR/backups/hourly"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_$TIMESTAMP"

# Create backup directory structure
mkdir -p "$BACKUP_DIR"

# Create timestamped backup
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
mkdir -p "$BACKUP_PATH"

echo "========================================="
echo "TedBot Hourly Backup - $(date)"
echo "========================================="

# Backup critical data files
echo "[1/4] Backing up trade history..."
mkdir -p "$BACKUP_PATH/trade_history"
cp -f "$PROJECT_DIR/trade_history/completed_trades.csv" "$BACKUP_PATH/trade_history/" 2>/dev/null || echo "  (no trade history)"

echo "[2/4] Backing up portfolio data..."
mkdir -p "$BACKUP_PATH/portfolio_data"
cp -f "$PROJECT_DIR/portfolio_data/account_status.json" "$BACKUP_PATH/portfolio_data/" 2>/dev/null || echo "  (no account status)"
cp -f "$PROJECT_DIR/portfolio_data/current_portfolio.json" "$BACKUP_PATH/portfolio_data/" 2>/dev/null || echo "  (no current portfolio)"

echo "[3/4] Backing up configuration..."
mkdir -p "$BACKUP_PATH/config"
cp -f "$PROJECT_DIR/.env" "$BACKUP_PATH/config/" 2>/dev/null || echo "  (no .env file)"

echo "[4/4] Creating backup manifest..."
cat > "$BACKUP_PATH/manifest.json" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "backup_type": "hourly",
  "files_backed_up": [
    "trade_history/completed_trades.csv",
    "portfolio_data/account_status.json",
    "portfolio_data/current_portfolio.json",
    "config/.env"
  ],
  "account_snapshot": $(cat "$PROJECT_DIR/portfolio_data/account_status.json" 2>/dev/null || echo '{"status": "file not found"}')
}
EOF

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)
echo "✅ Backup created: $BACKUP_NAME ($BACKUP_SIZE)"

# Rotation: Keep only last 168 backups (7 days * 24 hours)
echo ""
echo "Rotating old backups (keeping last 168 hours)..."
BACKUP_COUNT=$(ls -1d "$BACKUP_DIR"/backup_* 2>/dev/null | wc -l)

if [ "$BACKUP_COUNT" -gt 168 ]; then
  DELETE_COUNT=$((BACKUP_COUNT - 168))
  ls -1td "$BACKUP_DIR"/backup_* | tail -n "$DELETE_COUNT" | xargs rm -rf
  echo "✅ Deleted $DELETE_COUNT old backups"
else
  echo "✅ Currently have $BACKUP_COUNT backups (within 168 limit)"
fi

# Summary
echo ""
echo "========================================="
echo "Backup Summary:"
echo "  Location: $BACKUP_PATH"
echo "  Size: $BACKUP_SIZE"
echo "  Total backups: $(ls -1d "$BACKUP_DIR"/backup_* 2>/dev/null | wc -l)"
echo "========================================="
