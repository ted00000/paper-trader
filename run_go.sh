#!/bin/bash
# Wrapper script for GO command
# Ensures proper environment, logging, and status tracking for cron

# Exit on error
set -e

# Configuration
SCRIPT_DIR="/root/paper_trading_lab"
LOG_FILE="$SCRIPT_DIR/logs/go.log"
STATUS_FILE="$SCRIPT_DIR/dashboard_data/operation_status/go_status.json"
AGENT_SCRIPT="agent_v5.5.py"

# Create log directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/dashboard_data/operation_status"

# Function to update status
update_status() {
    local status=$1
    local error=${2:-""}
    local timestamp=$(date -Iseconds)

    cat > "$STATUS_FILE" <<EOF
{
  "operation": "GO",
  "last_run": "$timestamp",
  "status": "$status",
  "log_file": "$LOG_FILE",
  "error": "$error"
}
EOF
}

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
if [ ! -f "config/.env" ]; then
    update_status "FAILED" "Environment file not found at config/.env"
    exit 1
fi
source config/.env

# ============================================================
# MARKET HOLIDAY CHECK (v8.9.8)
# Skip trading on weekends and US market holidays
# ============================================================
if ! python3 market_holidays.py >> "$LOG_FILE" 2>&1; then
    echo "============================================================" >> "$LOG_FILE"
    echo "GO Command SKIPPED (Market Closed): $(date)" >> "$LOG_FILE"
    echo "============================================================" >> "$LOG_FILE"
    update_status "SKIPPED" "Market closed (holiday or weekend)"
    exit 0  # Exit successfully - skipping is expected behavior
fi

# Verify agent script exists
if [ ! -f "$AGENT_SCRIPT" ]; then
    update_status "FAILED" "Agent script not found: $AGENT_SCRIPT"
    exit 1
fi

# Mark as starting
update_status "RUNNING"

# Run GO with logging and error capture
echo "============================================================" >> "$LOG_FILE"
echo "GO Command Starting: $(date)" >> "$LOG_FILE"
echo "============================================================" >> "$LOG_FILE"

if python3 "$AGENT_SCRIPT" go >> "$LOG_FILE" 2>&1; then
    # Success
    update_status "SUCCESS"
    echo "GO command completed successfully: $(date)" >> "$LOG_FILE"
    exit 0
else
    # Failure
    EXIT_CODE=$?
    update_status "FAILED" "GO command failed with exit code $EXIT_CODE"
    echo "GO command failed with exit code $EXIT_CODE: $(date)" >> "$LOG_FILE"
    exit $EXIT_CODE
fi
