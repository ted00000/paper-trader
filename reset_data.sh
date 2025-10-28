#!/bin/bash
#
# RESET DATA - Clean slate for Paper Trading Lab
# Use this to clear all test data and start fresh
#

set -e

PROJECT_DIR="/root/paper_trading_lab"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=============================================="
echo "RESETTING PAPER TRADING LAB DATA"
echo "=============================================="
echo ""

# Confirm
read -p "This will delete all trading data. Continue? (yes/no) " -r
echo ""
if [[ ! $REPLY =~ ^yes$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Backup current data
echo "1. Creating backup..."
BACKUP_DIR="${PROJECT_DIR}/backups/data_backup_${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

# Backup files if they exist
[ -f "$PROJECT_DIR/portfolio_data/current_portfolio.json" ] && cp "$PROJECT_DIR/portfolio_data/current_portfolio.json" "$BACKUP_DIR/"
[ -f "$PROJECT_DIR/portfolio_data/account_status.json" ] && cp "$PROJECT_DIR/portfolio_data/account_status.json" "$BACKUP_DIR/"
[ -f "$PROJECT_DIR/portfolio_data/pending_positions.json" ] && cp "$PROJECT_DIR/portfolio_data/pending_positions.json" "$BACKUP_DIR/"
[ -f "$PROJECT_DIR/trade_history/completed_trades.csv" ] && cp "$PROJECT_DIR/trade_history/completed_trades.csv" "$BACKUP_DIR/"

echo "   ✓ Backup saved: $BACKUP_DIR"
echo ""

# Reset portfolio data
echo "2. Resetting portfolio data..."

cat > "$PROJECT_DIR/portfolio_data/current_portfolio.json" << 'EOF'
{
  "last_updated": "Not yet initialized",
  "portfolio_status": "Awaiting first 'go' command",
  "total_positions": 0,
  "positions": [],
  "closed_positions": []
}
EOF

cat > "$PROJECT_DIR/portfolio_data/account_status.json" << 'EOF'
{
  "account_value": 1000.00,
  "cash_available": 0.00,
  "positions_value": 0.00,
  "realized_pl": 0.00,
  "total_trades": 0,
  "win_rate_percent": 0.00,
  "average_hold_time_days": 0.0,
  "average_winner_percent": 0.00,
  "average_loser_percent": 0.00,
  "last_updated": "Not yet initialized"
}
EOF

# Remove pending positions if exists
[ -f "$PROJECT_DIR/portfolio_data/pending_positions.json" ] && rm "$PROJECT_DIR/portfolio_data/pending_positions.json"

echo "   ✓ Portfolio data reset"
echo ""

# Reset trade history (keep headers)
echo "3. Resetting trade history..."

cat > "$PROJECT_DIR/trade_history/completed_trades.csv" << 'EOF'
Trade_ID,Entry_Date,Exit_Date,Ticker,Entry_Price,Exit_Price,Shares,Position_Size,Hold_Days,Return_Percent,Return_Dollars,Exit_Reason,Catalyst_Type,Sector,Confidence_Level,Stop_Loss,Price_Target,Thesis,What_Worked,What_Failed,Account_Value_After
EOF

echo "   ✓ Trade history cleared"
echo ""

# Reset catalyst exclusions
echo "4. Resetting catalyst exclusions..."

cat > "$PROJECT_DIR/strategy_evolution/catalyst_exclusions.json" << 'EOF'
{
  "excluded_catalysts": [],
  "last_updated": "2025-10-28 00:00:00",
  "note": "These catalysts have been automatically excluded by the learning engine due to poor performance"
}
EOF

echo "   ✓ Catalyst exclusions cleared"
echo ""

# Clear daily reviews (optional)
read -p "5. Clear daily_reviews folder? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "$PROJECT_DIR/daily_reviews" ]; then
        rm -rf "$PROJECT_DIR/daily_reviews"/*
        echo "   ✓ Daily reviews cleared"
    else
        echo "   ℹ No daily_reviews folder found"
    fi
else
    echo "   ⊘ Skipped daily_reviews"
fi
echo ""

# Summary
echo "=============================================="
echo "RESET COMPLETE"
echo "=============================================="
echo ""
echo "✓ All trading data reset to clean slate"
echo "✓ Account value: $1,000"
echo "✓ Positions: 0"
echo "✓ Trade history: Empty"
echo "✓ Catalyst exclusions: Empty"
echo ""
echo "Backup saved to: $BACKUP_DIR"
echo ""
echo "Ready for fresh start!"
echo "Next step: Wait for 8:45 AM cron to run 'go' command"
echo ""
echo "=============================================="
