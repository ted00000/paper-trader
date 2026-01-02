#!/bin/bash
# Wrapper script for Near-Miss Forward Return Updater
# Ensures proper environment, logging, and status tracking for cron

# Exit on error
set -e

# Configuration
SCRIPT_DIR="/root/paper_trading_lab"
LOG_FILE="$SCRIPT_DIR/logs/near_miss_updater.log"
STATUS_FILE="$SCRIPT_DIR/dashboard_data/operation_status/near_miss_updater_status.json"
UPDATER_SCRIPT="update_near_miss_returns.py"

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
  "operation": "NEAR_MISS_UPDATER",
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

# Export all variables from .env
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

# Verify updater script exists
if [ ! -f "$UPDATER_SCRIPT" ]; then
    update_status "FAILED" "Updater script not found: $UPDATER_SCRIPT"
    exit 1
fi

# Run updater with logging and error capture
echo "============================================================" >> "$LOG_FILE"
echo "Near-Miss Updater Starting: $(date)" >> "$LOG_FILE"
echo "============================================================" >> "$LOG_FILE"

if python3 "$UPDATER_SCRIPT" >> "$LOG_FILE" 2>&1; then
    # Success
    update_status "SUCCESS"
    echo "Near-miss updater completed successfully: $(date)" >> "$LOG_FILE"
    exit 0
else
    # Failure
    EXIT_CODE=$?
    update_status "FAILED" "Near-miss updater failed with exit code $EXIT_CODE"
    echo "Near-miss updater failed with exit code $EXIT_CODE: $(date)" >> "$LOG_FILE"
    exit $EXIT_CODE
fi
