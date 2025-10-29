#!/bin/bash
# Wrapper script for GO command
# Ensures proper environment and logging for cron

set -e

cd /root/paper_trading_lab
source venv/bin/activate
source /root/.env

# Run GO with logging
python3 agent_v4.3.py go >> logs/go.log 2>&1

exit 0
