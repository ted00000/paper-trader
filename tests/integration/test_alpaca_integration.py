#!/usr/bin/env python3
"""
Test script to verify Alpaca integration in TradingAgent
This runs without triggering the main() CLI
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Prevent main() from running by temporarily removing argv
original_argv = sys.argv
sys.argv = ['test_script']

# Now import - need to use exec since filename has dots
with open('agent_v5.5.py', 'r') as f:
    code = f.read()
    # Remove the main execution block to prevent it from running
    code_lines = code.split('\n')
    filtered_lines = []
    skip_main = False
    for line in code_lines:
        if 'if __name__ ==' in line:
            skip_main = True
        if not skip_main:
            filtered_lines.append(line)
    exec('\n'.join(filtered_lines))

# Get TradingAgent from globals
TradingAgent = globals()['TradingAgent']

# Restore argv
sys.argv = original_argv

def main():
    print("\n" + "="*70)
    print("ALPACA INTEGRATION TEST")
    print("="*70)

    print("\n1. Initializing TradingAgent...")
    try:
        agent = TradingAgent()
        print("   ✓ Agent initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        return False

    print(f"\n2. Checking Alpaca availability...")
    print(f"   use_alpaca: {agent.use_alpaca}")

    if not agent.use_alpaca or not agent.broker:
        print("   ✗ Alpaca not available - check credentials and connection")
        return False

    print("   ✓ Alpaca broker is connected")

    print("\n3. Testing account access...")
    try:
        account = agent.broker.get_account()
        print(f"   ✓ Account Status: {account.status}")
        print(f"   ✓ Equity: ${float(account.equity):,.2f}")
        print(f"   ✓ Cash: ${float(account.cash):,.2f}")
        print(f"   ✓ Buying Power: ${float(account.buying_power):,.2f}")
    except Exception as e:
        print(f"   ✗ Failed to access account: {e}")
        return False

    print("\n4. Testing portfolio load...")
    try:
        portfolio = agent.load_current_portfolio()
        total_pos = portfolio.get('total_positions', 0)
        status = portfolio.get('portfolio_status', 'Unknown')
        print(f"   ✓ Portfolio loaded: {total_pos} positions")
        print(f"   ✓ Status: {status}")
    except Exception as e:
        print(f"   ✗ Failed to load portfolio: {e}")
        return False

    print("\n5. Testing position query...")
    try:
        positions = agent.broker.get_positions()
        print(f"   ✓ Alpaca positions: {len(positions)}")
        if positions:
            for pos in positions:
                print(f"      - {pos.symbol}: {pos.qty} shares @ ${float(pos.avg_entry_price):.2f}")
    except Exception as e:
        print(f"   ✗ Failed to query positions: {e}")
        return False

    print("\n6. Checking helper methods...")
    try:
        # Check if helper methods exist
        assert hasattr(agent, '_execute_alpaca_sell'), "Missing _execute_alpaca_sell method"
        assert hasattr(agent, '_execute_alpaca_buy'), "Missing _execute_alpaca_buy method"
        print("   ✓ Order execution methods present")
    except AssertionError as e:
        print(f"   ✗ {e}")
        return False

    print("\n" + "="*70)
    print("✓ ALL INTEGRATION TESTS PASSED")
    print("="*70)
    print("\nAlpaca integration is working correctly!")
    print("Ready for live trading cycle: GO → EXECUTE → ANALYZE")
    print("\nNext steps:")
    print("  1. Run during market hours to test with real data")
    print("  2. Monitor Alpaca dashboard for order execution")
    print("  3. Verify position sync between agent and Alpaca")
    print()

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
