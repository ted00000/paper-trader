#!/bin/bash
# Quick deployment for agent_v4.2.py (Alpha Vantage version)

echo "Deploying agent_v4.2.py with Alpha Vantage..."
cd /root/paper_trading_lab

# Backup
echo "Creating backup..."
BACKUP="/root/paper_trading_lab_backup_v42_$(date +%Y%m%d_%H%M%S)"
cp -r /root/paper_trading_lab "$BACKUP"
echo "✓ Backup: $BACKUP"

# Update symlink
echo "Updating symlink..."
rm -f agent.py
ln -s agent_v4.2.py agent.py
echo "✓ agent.py -> agent_v4.2.py"

# Verify Alpha Vantage key
echo "Checking environment..."
source /root/.env
if [ -z "$ALPHAVANTAGE_API_KEY" ]; then
    echo "⚠️  WARNING: ALPHAVANTAGE_API_KEY not set in /root/.env"
    echo "   Add: export ALPHAVANTAGE_API_KEY=\"your-key\""
else
    echo "✓ Alpha Vantage API key configured"
fi

echo ""
echo "============================================"
echo "DEPLOYMENT COMPLETE"
echo "============================================"
echo "Test: python3 agent.py analyze"
echo "Cron will use new version automatically"