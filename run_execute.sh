#!/bin/bash
# Wrapper script for EXECUTE command
# Ensures proper environment, logging, and status tracking for cron

# Exit on error
set -e

# Configuration
SCRIPT_DIR="/root/paper_trading_lab"
LOG_FILE="$SCRIPT_DIR/logs/execute.log"
STATUS_FILE="$SCRIPT_DIR/dashboard_data/operation_status/execute_status.json"
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
  "operation": "EXECUTE",
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

# Verify agent script exists
if [ ! -f "$AGENT_SCRIPT" ]; then
    update_status "FAILED" "Agent script not found: $AGENT_SCRIPT"
    exit 1
fi

# Run EXECUTE with logging and error capture
echo "============================================================" >> "$LOG_FILE"
echo "EXECUTE Command Starting: $(date)" >> "$LOG_FILE"
echo "============================================================" >> "$LOG_FILE"

if python3 "$AGENT_SCRIPT" execute >> "$LOG_FILE" 2>&1; then
    # Success
    update_status "SUCCESS"
    echo "EXECUTE command completed successfully: $(date)" >> "$LOG_FILE"
    exit 0
else
    # Failure
    EXIT_CODE=$?
    update_status "FAILED" "EXECUTE command failed with exit code $EXIT_CODE"
    echo "EXECUTE command failed with exit code $EXIT_CODE: $(date)" >> "$LOG_FILE"
    exit $EXIT_CODE
fi
