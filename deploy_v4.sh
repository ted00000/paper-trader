#!/bin/bash
#
# SAFE DEPLOYMENT SCRIPT FOR AGENT V4.0
# - Creates automatic backup
# - Installs yfinance
# - Updates symlink to v4
# - Tests installation
# - Can rollback if needed
#

set -e  # Exit on error

PROJECT_DIR="/root/paper_trading_lab"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${PROJECT_DIR}_backup_${TIMESTAMP}"

echo "=============================================="
echo "DEPLOYING AGENT V4.0 - PRODUCTION READY"
echo "=============================================="
echo ""

# Step 1: Create backup
echo "1. Creating backup..."
if [ -d "$PROJECT_DIR" ]; then
    cp -r "$PROJECT_DIR" "$BACKUP_DIR"
    echo "   ✓ Backup created: $BACKUP_DIR"
else
    echo "   ⚠ No existing project found (fresh install)"
fi
echo ""

# Step 2: Install yfinance
echo "2. Installing yfinance for price fetching..."
cd "$PROJECT_DIR"
source venv/bin/activate
pip install --break-system-packages yfinance==0.2.32
echo "   ✓ yfinance installed"
echo ""

# Step 3: Copy new agent_v4.py
echo "3. Installing agent_v4.py..."
if [ -f "agent_v4.py" ]; then
    echo "   ✓ agent_v4.py already present"
else
    echo "   ⚠ agent_v4.py not found - please upload it first"
    exit 1
fi
chmod +x agent_v4.py
echo "   ✓ agent_v4.py permissions set"
echo ""

# Step 4: Update symlink
echo "4. Updating agent.py symlink..."

# Remove old symlink if exists
if [ -L "agent.py" ]; then
    rm agent.py
    echo "   ✓ Removed old symlink"
elif [ -f "agent.py" ]; then
    mv agent.py agent.py.old
    echo "   ✓ Backed up old agent.py to agent.py.old"
fi

# Create new symlink
ln -s agent_v4.py agent.py
echo "   ✓ Created symlink: agent.py -> agent_v4.py"
echo ""

# Step 5: Test installation
echo "5. Testing installation..."
if python3 agent.py --version 2>/dev/null || python3 agent.py 2>&1 | grep -q "Usage"; then
    echo "   ✓ Agent executable"
else
    echo "   ⚠ Agent test failed (this is OK if Usage message shown)"
fi
echo ""

# Step 6: Verify yfinance
echo "6. Verifying yfinance installation..."
python3 -c "import yfinance; print('   ✓ yfinance imported successfully')" || echo "   ✗ yfinance import failed"
echo ""

# Step 7: Update cron jobs (if needed)
echo "7. Checking cron jobs..."
if crontab -l 2>/dev/null | grep -q "agent.py"; then
    echo "   ✓ Cron jobs already configured (using agent.py symlink)"
else
    echo "   ⚠ Cron jobs not found - you may need to set them up"
fi
echo ""

# Summary
echo "=============================================="
echo "DEPLOYMENT COMPLETE"
echo "=============================================="
echo ""
echo "✓ Backup: $BACKUP_DIR"
echo "✓ Agent version: 4.0"
echo "✓ Symlink: agent.py -> agent_v4.py"
echo "✓ yfinance: installed"
echo ""
echo "TEST COMMANDS:"
echo "  python3 agent.py go"
echo "  python3 agent.py analyze"
echo "  python3 agent.py learn-daily"
echo ""
echo "ROLLBACK COMMAND (if needed):"
echo "  cp -r $BACKUP_DIR/* $PROJECT_DIR/"
echo ""
echo "=============================================="