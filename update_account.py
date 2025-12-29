#!/usr/bin/env python3
import sys
sys.path.insert(0, '/root/paper_trading_lab')

import os
os.environ['POLYGON_API_KEY'] = 'dummy'
os.environ['FINNHUB_API_KEY'] = 'dummy'

# Import after setting env vars
import importlib.util
spec = importlib.util.spec_from_file_location('agent', 'agent_v5.5.py')
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)

agent = agent_module.TradingAgent()
agent.update_account_status()
print('Account status updated successfully')
