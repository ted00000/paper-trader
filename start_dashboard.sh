#!/bin/bash
# Dashboard startup script - preserves credentials from .env

set -e

cd /root/paper_trading_lab

# Load environment variables WITHOUT shell expansion (preserves $ in password hash)
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ $line =~ ^#.*$ ]] && continue
    [[ -z $line ]] && continue

    # Remove leading 'export ' if present
    line="${line#export }"

    # Split on first '=' only
    if [[ $line =~ ^([^=]+)=(.*)$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"

        # Remove quotes if present
        value="${value%\"}"
        value="${value#\"}"

        # Export without shell expansion
        export "$key=$value"
    fi
done < /root/.env

# Set dashboard-specific variables
export DASHBOARD_SECRET_KEY=$(cat .secret_key)
export ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"

# Verify password hash is set
if [ -z "$ADMIN_PASSWORD_HASH" ]; then
    echo "ERROR: ADMIN_PASSWORD_HASH not found in /root/.env"
    exit 1
fi

echo "Environment check:"
echo "  ADMIN_USERNAME: $ADMIN_USERNAME"
echo "  ADMIN_PASSWORD_HASH: ${ADMIN_PASSWORD_HASH:0:20}..."
echo "  DASHBOARD_SECRET_KEY: ${DASHBOARD_SECRET_KEY:0:10}..."

# Kill any existing dashboard process
pkill -f dashboard_server.py 2>/dev/null || true
sleep 1

# Start the dashboard
echo ""
echo "Starting Tedbot Admin Dashboard..."
nohup ./venv/bin/python3 dashboard_server.py > /tmp/dashboard.log 2>&1 &

sleep 2

# Check if it started
if pgrep -f dashboard_server.py > /dev/null; then
    echo "✓ Dashboard started successfully"
    echo "✓ Access at: http://174.138.67.26:5000"
    echo "✓ Login: $ADMIN_USERNAME / (password from .env)"
else
    echo "✗ Dashboard failed to start. Check /tmp/dashboard.log"
    tail -20 /tmp/dashboard.log
    exit 1
fi
