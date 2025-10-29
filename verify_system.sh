#!/bin/bash
# Comprehensive system verification for Paper Trading Lab
# Run this to ensure everything is ready for tomorrow's trading

set -e  # Exit on any error

echo "========================================================================"
echo "PAPER TRADING LAB - SYSTEM VERIFICATION"
echo "========================================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ERRORS=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

function check_fail() {
    echo -e "${RED}✗${NC} $1"
    ERRORS=$((ERRORS + 1))
}

function check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "1. CHECKING ENVIRONMENT VARIABLES"
echo "----------------------------------------"

# Check CLAUDE_API_KEY
if [ -z "$CLAUDE_API_KEY" ]; then
    check_fail "CLAUDE_API_KEY not set"
else
    check_pass "CLAUDE_API_KEY is set (${#CLAUDE_API_KEY} chars)"
fi

# Check POLYGON_API_KEY
if [ -z "$POLYGON_API_KEY" ]; then
    check_fail "POLYGON_API_KEY not set"
else
    check_pass "POLYGON_API_KEY is set (${#POLYGON_API_KEY} chars)"
fi

echo ""
echo "2. CHECKING DIRECTORY STRUCTURE"
echo "----------------------------------------"

# Check critical directories
for dir in portfolio_data trade_history daily_reviews strategy_evolution; do
    if [ -d "$dir" ]; then
        check_pass "Directory exists: $dir"
    else
        check_fail "Directory missing: $dir"
    fi
done

echo ""
echo "3. CHECKING REQUIRED FILES"
echo "----------------------------------------"

# Check agent file
if [ -f "agent_v4.3.py" ]; then
    check_pass "Agent file exists: agent_v4.3.py"
else
    check_fail "Agent file missing: agent_v4.3.py"
fi

# Check dashboard
if [ -f "dashboard.html" ]; then
    check_pass "Dashboard exists: dashboard.html"
else
    check_fail "Dashboard missing: dashboard.html"
fi

echo ""
echo "4. CHECKING PYTHON ENVIRONMENT"
echo "----------------------------------------"

# Check if venv exists
if [ -d "venv" ]; then
    check_pass "Virtual environment exists"

    # Activate venv and check packages
    source venv/bin/activate

    # Check critical packages
    for pkg in anthropic requests; do
        if python3 -c "import $pkg" 2>/dev/null; then
            check_pass "Python package installed: $pkg"
        else
            check_fail "Python package missing: $pkg"
        fi
    done

else
    check_fail "Virtual environment missing - run: python3 -m venv venv && source venv/bin/activate && pip install anthropic requests"
fi

echo ""
echo "5. TESTING POLYGON.IO API"
echo "----------------------------------------"

if [ -n "$POLYGON_API_KEY" ]; then
    response=$(curl -s "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/AAPL?apiKey=$POLYGON_API_KEY")

    if echo "$response" | grep -q '"status":"OK"'; then
        price=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['ticker']['lastTrade']['p'])" 2>/dev/null || echo "N/A")
        check_pass "Polygon.io API working - AAPL price: \$$price"
    else
        check_fail "Polygon.io API error: $(echo $response | head -c 100)"
    fi
else
    check_warn "Skipping API test (no API key)"
fi

echo ""
echo "6. TESTING AGENT EXECUTION"
echo "----------------------------------------"

# Test that agent runs without errors
if [ -f "agent_v4.3.py" ]; then
    output=$(python3 agent_v4.3.py 2>&1)

    if echo "$output" | grep -q "Usage:"; then
        check_pass "Agent executes correctly (shows usage)"
    else
        check_fail "Agent execution error: $output"
    fi
fi

echo ""
echo "7. CHECKING DATA FILES"
echo "----------------------------------------"

# Check that data files were created by agent init
files=(
    "portfolio_data/account_status.json"
    "portfolio_data/current_portfolio.json"
    "portfolio_data/daily_activity.json"
    "trade_history/completed_trades.csv"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        size=$(ls -lh "$file" | awk '{print $5}')
        check_pass "Data file exists: $file ($size)"
    else
        check_fail "Data file missing: $file"
    fi
done

echo ""
echo "8. CHECKING CRON CONFIGURATION"
echo "----------------------------------------"

# Check if crontab is set up
if crontab -l 2>/dev/null | grep -q "agent_v4.3.py"; then
    check_pass "Crontab entries found"

    # Show cron schedule
    echo ""
    echo "Current cron schedule:"
    crontab -l | grep "agent_v4.3.py" | while read line; do
        echo "  $line"
    done
else
    check_warn "No crontab entries found for agent_v4.3.py"
fi

echo ""
echo "9. CHECKING FILE PERMISSIONS"
echo "----------------------------------------"

# Check that agent is executable
if [ -x "agent_v4.3.py" ]; then
    check_pass "agent_v4.3.py is executable"
else
    check_warn "agent_v4.3.py not executable - setting chmod +x"
    chmod +x agent_v4.3.py
fi

# Check log directory permissions
if [ -d "logs" ]; then
    if [ -w "logs" ]; then
        check_pass "logs/ directory is writable"
    else
        check_fail "logs/ directory not writable"
    fi
else
    check_warn "logs/ directory doesn't exist - creating it"
    mkdir -p logs
fi

echo ""
echo "========================================================================"
echo "VERIFICATION SUMMARY"
echo "========================================================================"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo ""
    echo "System is ready for tomorrow's trading!"
    echo ""
    echo "Tomorrow's schedule (Eastern Time):"
    echo "  8:45 AM - GO command (select 10 stocks)"
    echo "  9:30 AM - EXECUTE command (enter positions with real prices)"
    echo "  4:30 PM - ANALYZE command (update prices, close positions)"
    echo ""
    exit 0
else
    echo -e "${RED}✗ FOUND $ERRORS ERROR(S)${NC}"
    echo ""
    echo "Please fix the errors above before tomorrow's trading session."
    echo ""
    exit 1
fi
