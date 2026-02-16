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

# Load and EXPORT environment variables (including FINNHUB_API_KEY)
if [ ! -f "config/.env" ]; then
    update_status "FAILED" "Environment file not found at config/.env"
    exit 1
fi

# Export all variables from config/.env
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
done < config/.env

# ============================================================
# MARKET HOLIDAY CHECK (v8.9.8)
# Skip trading on weekends and US market holidays
# ============================================================
if ! python3 market_holidays.py >> "$LOG_FILE" 2>&1; then
    echo "============================================================" >> "$LOG_FILE"
    echo "Market Screener SKIPPED (Market Closed): $(date)" >> "$LOG_FILE"
    echo "============================================================" >> "$LOG_FILE"
    update_status "SKIPPED" "Market closed (holiday or weekend)"
    exit 0
fi

# Verify screener script exists
if [ ! -f "$SCREENER_SCRIPT" ]; then
    update_status "FAILED" "Screener script not found: $SCREENER_SCRIPT"
    exit 1
fi

# Mark as starting
update_status "RUNNING"

# Run screener with logging and error capture
echo "============================================================" >> "$LOG_FILE"
echo "Market Screener Starting: $(date)" >> "$LOG_FILE"
echo "============================================================" >> "$LOG_FILE"

if python3 "$SCREENER_SCRIPT" >> "$LOG_FILE" 2>&1; then
    # Success - Extract stats from screener_candidates.json (v7.0 metrics)
    CANDIDATES_FILE="$SCRIPT_DIR/screener_candidates.json"
    if [ -f "$CANDIDATES_FILE" ]; then
        UNIVERSE_SIZE=$(python3 -c "import json; d=json.load(open('$CANDIDATES_FILE')); print(d.get('universe_size', 0))" 2>/dev/null || echo "0")
        CANDIDATES=$(python3 -c "import json; d=json.load(open('$CANDIDATES_FILE')); print(d.get('candidates_found', 0))" 2>/dev/null || echo "0")
        # v7.0: Market breadth replaces RS pass rate (RS is now scoring factor, not filter)
        BREADTH_PCT=$(python3 -c "import json; d=json.load(open('$CANDIDATES_FILE')); print(d.get('breadth_pct', 0))" 2>/dev/null || echo "0")
        BREADTH_TIMESTAMP=$(python3 -c "import json; d=json.load(open('$CANDIDATES_FILE')); print(d.get('breadth_timestamp', 'unknown'))" 2>/dev/null || echo "unknown")

        # Update status with stats
        TIMESTAMP=$(date -Iseconds)
        cat > "$STATUS_FILE" <<EOF
{
  "operation": "SCREENER",
  "last_run": "$TIMESTAMP",
  "status": "SUCCESS",
  "log_file": "$LOG_FILE",
  "error": "",
  "stats": {
    "universe_size": $UNIVERSE_SIZE,
    "candidates_found": $CANDIDATES,
    "breadth_pct": $BREADTH_PCT,
    "breadth_timestamp": "$BREADTH_TIMESTAMP"
  }
}
EOF
    else
        update_status "SUCCESS"
    fi

    echo "Market screener completed successfully: $(date)" >> "$LOG_FILE"
    exit 0
else
    # Failure
    EXIT_CODE=$?
    update_status "FAILED" "Market screener failed with exit code $EXIT_CODE"
    echo "Market screener failed with exit code $EXIT_CODE: $(date)" >> "$LOG_FILE"
    exit $EXIT_CODE
fi
