#!/bin/bash
# Wrapper script for ANALYZE command
# Ensures proper environment and logging for cron

set -e

cd /root/paper_trading_lab
source venv/bin/activate
source /root/.env

# Run ANALYZE with logging
python3 agent_v4.3.py analyze >> logs/analyze.log 2>&1

exit 0
