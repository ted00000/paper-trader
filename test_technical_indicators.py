#!/usr/bin/env python3
"""
Test script for technical indicators module
Tests the 4 essential filters on popular stocks
"""

import sys
import os

# Ensure the agent can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("TECHNICAL INDICATORS TEST SUITE")
print("=" * 70)
print()

# Test if we can import the agent
try:
    from agent_v5_5 import TradingAgent
    print("✓ Agent module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import agent: {e}")
    print("\nTrying direct import from agent_v5.5.py...")
    import importlib.util
    spec = importlib.util.spec_from_file_location("agent", "./agent_v5.5.py")
    agent_module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(agent_module)
        TradingAgent = agent_module.TradingAgent
        print("✓ Agent loaded via direct import")
    except Exception as e2:
        print(f"✗ Failed to load agent: {e2}")
        sys.exit(1)

print()
print("Initializing TradingAgent...")
try:
    agent = TradingAgent()
    print("✓ Agent initialized")
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("TESTING TECHNICAL FILTERS")
print("=" * 70)
print()

# Test stocks: Mix of strong/weak technical setups
test_stocks = [
    ('AAPL', 'Apple - Large cap tech'),
    ('NVDA', 'NVIDIA - Momentum leader'),
    ('TSLA', 'Tesla - Volatile growth'),
    ('SPY', 'S&P 500 ETF - Market benchmark')
]

for ticker, description in test_stocks:
    print(f"\n{'=' * 70}")
    print(f"Testing {ticker} ({description})")
    print('=' * 70)

    try:
        result = agent.calculate_technical_score(ticker)

        print(f"\n  Result: {'✓ PASSED' if result['passed'] else '✗ FAILED'}")
        print(f"  Score: {result['score']}/25 points")
        print(f"  Reason: {result['reason']}")

        if result.get('details'):
            print(f"\n  Technical Details:")
            details = result['details']

            if details.get('price'):
                print(f"    Current Price: ${details['price']:.2f}")

            if details.get('sma50'):
                print(f"    50-day SMA: ${details['sma50']:.2f} ({'✓' if details.get('above_50ma') else '✗'} Above)")

            if details.get('ema5') and details.get('ema20'):
                print(f"    5 EMA: ${details['ema5']:.2f}")
                print(f"    20 EMA: ${details['ema20']:.2f} ({'✓' if details.get('ema_bullish') else '✗'} Bullish)")

            if details.get('adx'):
                print(f"    ADX: {details['adx']:.1f} ({'✓' if details.get('trend_strong') else '✗'} Strong trend >20)")

            if details.get('volume_ratio'):
                print(f"    Volume Ratio: {details['volume_ratio']:.2f}x ({'✓' if details.get('volume_confirmed') else '✗'} >1.5x)")

        print()

    except Exception as e:
        print(f"  ✗ Error testing {ticker}: {e}")
        import traceback
        traceback.print_exc()

print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
