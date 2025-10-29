#!/bin/bash
# Initialize required data files for paper trading system
# Run this after git clone or if data files are missing

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Initializing paper trading data files..."

# Create completed_trades.csv if it doesn't exist
if [ ! -f "trade_history/completed_trades.csv" ]; then
    echo "Creating trade_history/completed_trades.csv..."
    cat > trade_history/completed_trades.csv << 'EOF'
Trade_ID,Entry_Date,Exit_Date,Ticker,Premarket_Price,Entry_Price,Exit_Price,Gap_Percent,Shares,Position_Size,Hold_Days,Return_Percent,Return_Dollars,Exit_Reason,Catalyst_Type,Sector,Confidence_Level,Stop_Loss,Price_Target,Thesis,What_Worked,What_Failed,Account_Value_After
EOF
    chmod 644 trade_history/completed_trades.csv
    echo "  ✓ Created trade_history/completed_trades.csv"
else
    echo "  ✓ trade_history/completed_trades.csv already exists"
fi

# Create daily_activity.json if it doesn't exist
if [ ! -f "portfolio_data/daily_activity.json" ]; then
    echo "Creating portfolio_data/daily_activity.json..."
    echo '{"recent_activity": [], "recently_closed": []}' > portfolio_data/daily_activity.json
    chmod 644 portfolio_data/daily_activity.json
    echo "  ✓ Created portfolio_data/daily_activity.json"
else
    echo "  ✓ portfolio_data/daily_activity.json already exists"
fi

# Create account_status.json if it doesn't exist
if [ ! -f "portfolio_data/account_status.json" ]; then
    echo "Creating portfolio_data/account_status.json..."
    cat > portfolio_data/account_status.json << 'EOF'
{
  "account_value": 1000.00,
  "cash_balance": 1000.00,
  "positions_value": 0.00,
  "total_return_percent": 0.00,
  "total_return_dollars": 0.00,
  "last_updated": ""
}
EOF
    chmod 644 portfolio_data/account_status.json
    echo "  ✓ Created portfolio_data/account_status.json"
else
    echo "  ✓ portfolio_data/account_status.json already exists"
fi

# Create current_portfolio.json if it doesn't exist
if [ ! -f "portfolio_data/current_portfolio.json" ]; then
    echo "Creating portfolio_data/current_portfolio.json..."
    cat > portfolio_data/current_portfolio.json << 'EOF'
{
  "positions": [],
  "total_positions": 0,
  "portfolio_value": 1000.00,
  "cash_balance": 1000.00,
  "last_updated": ""
}
EOF
    chmod 644 portfolio_data/current_portfolio.json
    echo "  ✓ Created portfolio_data/current_portfolio.json"
else
    echo "  ✓ portfolio_data/current_portfolio.json already exists"
fi

echo ""
echo "Data file initialization complete!"
echo ""
echo "Verify files:"
ls -lh trade_history/completed_trades.csv
ls -lh portfolio_data/daily_activity.json
ls -lh portfolio_data/account_status.json
ls -lh portfolio_data/current_portfolio.json
