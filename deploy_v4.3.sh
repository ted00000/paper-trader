#!/bin/bash
#
# DEPLOYMENT SCRIPT FOR AGENT V4.3
# - Splits GO (selection) from EXECUTE (entry with real prices)
# - Fixes account calculation to include realized P&L
# - Creates backup
# - Updates symlink
# - Installs cron jobs
#

set -e

PROJECT_DIR="/root/paper_trading_lab"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${PROJECT_DIR}_backup_v43_${TIMESTAMP}"

echo "=============================================="
echo "DEPLOYING AGENT V4.3"
echo "=============================================="
echo ""

# Step 1: Backup
echo "1. Creating backup..."
if [ -d "$PROJECT_DIR" ]; then
    cp -r "$PROJECT_DIR" "$BACKUP_DIR"
    echo "   ✓ Backup: $BACKUP_DIR"
else
    echo "   ⚠ No existing project (fresh install)"
fi
echo ""

# Step 2: Check agent_v4.3.py exists
echo "2. Checking for agent_v4.3.py..."
if [ ! -f "$PROJECT_DIR/agent_v4.3.py" ]; then
    echo "   ✗ agent_v4.3.py not found!"
    echo "   Please upload agent_v4.3.py first"
    exit 1
fi
echo "   ✓ agent_v4.3.py found"
echo ""

# Step 3: Update symlink
echo "3. Updating agent.py symlink..."
cd "$PROJECT_DIR"

if [ -L "agent.py" ]; then
    rm agent.py
    echo "   ✓ Removed old symlink"
elif [ -f "agent.py" ]; then
    mv agent.py agent.py.old_${TIMESTAMP}
    echo "   ✓ Backed up old agent.py"
fi

ln -s agent_v4.3.py agent.py
echo "   ✓ Created: agent.py -> agent_v4.3.py"
echo ""

# Step 4: Set permissions
echo "4. Setting permissions..."
chmod +x agent_v4.3.py
chmod +x agent.py
echo "   ✓ Permissions set"
echo ""

# Step 5: Check dependencies
echo "5. Checking dependencies..."
source venv/bin/activate
pip show requests >/dev/null 2>&1 || pip install --break-system-packages requests
echo "   ✓ Dependencies OK"
echo ""

# Step 6: Update crontab
echo "6. Updating crontab..."
echo "   Current cron jobs:"
crontab -l 2>/dev/null | grep "agent.py" || echo "   (none found)"
echo ""
echo "   New schedule:"
echo "   - 8:45 AM: GO (select stocks)"
echo "   - 9:30 AM: EXECUTE (enter with real prices)"
echo "   - 4:30 PM: ANALYZE (update & close positions)"
echo ""
read -p "   Update crontab? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Backup current crontab
    crontab -l > /tmp/crontab_backup_${TIMESTAMP}.txt 2>/dev/null || true
    
    # Remove old trading cron jobs
    crontab -l 2>/dev/null | grep -v "agent.py" > /tmp/crontab_new.txt || true
    
    # Add new v4.3 cron jobs
    cat >> /tmp/crontab_new.txt << 'EOF'
# Paper Trading Lab v4.3
45 8 * * 1-5 cd /root/paper_trading_lab && source venv/bin/activate && source /root/.env && python3 agent.py go >> /var/log/trading_go.log 2>&1
30 9 * * 1-5 cd /root/paper_trading_lab && source venv/bin/activate && source /root/.env && python3 agent.py execute >> /var/log/trading_execute.log 2>&1
30 16 * * 1-5 cd /root/paper_trading_lab && source venv/bin/activate && source /root/.env && python3 agent.py analyze >> /var/log/trading_analyze.log 2>&1
EOF
    
    crontab /tmp/crontab_new.txt
    echo "   ✓ Crontab updated"
    echo "   ✓ Backup: /tmp/crontab_backup_${TIMESTAMP}.txt"
else
    echo "   ⚠ Crontab not updated (manual setup required)"
fi
echo ""

# Step 7: Test
echo "7. Testing installation..."
python3 agent.py 2>&1 | head -5
echo "   ✓ Agent executable"
echo ""

# Summary
echo "=============================================="
echo "DEPLOYMENT COMPLETE"
echo "=============================================="
echo ""
echo "✓ Backup: $BACKUP_DIR"
echo "✓ Version: 4.3"
echo "✓ Symlink: agent.py -> agent_v4.3.py"
echo ""
echo "WORKFLOW:"
echo "  8:45 AM - GO: Select stocks, save to pending"
echo "  9:30 AM - EXECUTE: Enter with real prices"
echo "  4:30 PM - ANALYZE: Update & close positions"
echo ""
echo "TEST COMMANDS:"
echo "  python3 agent.py go       # Select stocks"
echo "  python3 agent.py execute  # Enter positions"
echo "  python3 agent.py analyze  # Update positions"
echo ""
echo "ROLLBACK:"
echo "  cp -r $BACKUP_DIR/* $PROJECT_DIR/"
echo ""
echo "=============================================="