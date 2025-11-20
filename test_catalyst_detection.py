#!/usr/bin/env python3
"""Test catalyst detection directly (skip RS filter)"""

import os

# Set env vars BEFORE importing
os.environ['POLYGON_API_KEY'] = "cvPn7WbJ_eZe_iwMc1RiKe8Ua09QTKYo"
os.environ['FINNHUB_API_KEY'] = "d4f6u59r01qkcvvgrh90d4f6u59r01qkcvvgrh9g"

from market_screener import MarketScreener

def main():
    print("=" * 80)
    print("CATALYST DETECTION TEST")
    print("=" * 80)

    screener = MarketScreener()

    # Test tickers
    tickers = ['NVDA', 'AAPL', 'MSFT', 'META', 'GOOGL', 'TSLA', 'AMD', 'BIIB', 'LLY']

    print("\nTesting analyst upgrades (14-day window)...")
    for ticker in tickers:
        result = screener.get_analyst_ratings(ticker)
        if result.get('catalyst_type') == 'analyst_upgrade':
            print(f"  ✓ {ticker}: {result['upgrade_count']} upgrades")
            for upgrade in result.get('recent_upgrades', []):
                print(f"    - {upgrade['firm']}: {upgrade['days_ago']} days ago")

    print("\nTesting insider buying clusters...")
    for ticker in tickers:
        result = screener.get_insider_transactions(ticker)
        if result.get('has_cluster'):
            print(f"  ✓ {ticker}: {result['buy_count']} insider buys")

    print("\nTesting earnings beats...")
    for ticker in tickers:
        result = screener.get_earnings_surprises(ticker)
        if result.get('has_beat'):
            print(f"  ✓ {ticker}: +{result['surprise_pct']}% beat ({result['days_ago']} days ago)")

    print("\n" + "=" * 80)
    print("Test complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()
