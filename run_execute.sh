#!/bin/bash
# Wrapper script for EXECUTE command
# Ensures proper environment and logging for cron

set -e

cd /root/paper_trading_lab
source venv/bin/activate
source /root/.env

# Run EXECUTE with logging
python3 agent_v4.3.py execute >> logs/execute.log 2>&1

exit 0
