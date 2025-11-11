#!/bin/bash
# Wrapper script for Market Screener
# Ensures proper environment, logging, and status tracking for cron

# Exit on error
set -e

# Configuration
SCRIPT_DIR="/root/paper_trading_lab"
LOG_FILE="$SCRIPT_DIR/logs/screener.log"
STATUS_FILE="$SCRIPT_DIR/dashboard_data/operation_status/screener_status.json"
SCREENER_SCRIPT="market_screener.py"

# Create directories if they don't exist
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/dashboard_data/operation_status"

# Function to update status
update_status() {
    local status=$1
    local error=${2:-""}
    local timestamp=$(date -Iseconds)

    cat > "$STATUS_FILE" <<EOF
{
  "operation": "SCREENER",
  "last_run": "$timestamp",
  "status": "$status",
  "log_file": "$LOG_FILE",
  "error": "$error"
}
EOF
}

# Mark as starting
update_status "RUNNING"

# Change to script directory
cd "$SCRIPT_DIR" || {
    update_status "FAILED" "Could not change to directory $SCRIPT_DIR"
    exit 1
}

# Activate virtual environment
if [ ! -f "venv/bin/activate" ]; then
    update_status "FAILED" "Virtual environment not found at venv/bin/activate"
    exit 1
fi
source venv/bin/activate

# Load environment variables
if [ ! -f "/root/.env" ]; then
    update_status "FAILED" "Environment file not found at /root/.env"
    exit 1
fi
source /root/.env

# Verify screener script exists
if [ ! -f "$SCREENER_SCRIPT" ]; then
    update_status "FAILED" "Screener script not found: $SCREENER_SCRIPT"
    exit 1
fi

# Run screener with logging and error capture
echo "============================================================" >> "$LOG_FILE"
echo "Market Screener Starting: $(date)" >> "$LOG_FILE"
echo "============================================================" >> "$LOG_FILE"

if python3 "$SCREENER_SCRIPT" >> "$LOG_FILE" 2>&1; then
    # Success
    update_status "SUCCESS"
    echo "Market screener completed successfully: $(date)" >> "$LOG_FILE"
    exit 0
else
    # Failure
    EXIT_CODE=$?
    update_status "FAILED" "Market screener failed with exit code $EXIT_CODE"
    echo "Market screener failed with exit code $EXIT_CODE: $(date)" >> "$LOG_FILE"
    exit $EXIT_CODE
fi
