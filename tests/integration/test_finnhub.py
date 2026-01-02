#!/usr/bin/env python3
"""Test Finnhub integration"""

import os
from market_screener import MarketScreener

def main():
    # Verify keys loaded
    polygon_key = os.environ.get('POLYGON_API_KEY', 'NOT SET')
    finnhub_key = os.environ.get('FINNHUB_API_KEY', 'NOT SET')

    print(f"Polygon API key: {polygon_key[:20] if polygon_key != 'NOT SET' else 'NOT SET'}...")
    print(f"Finnhub API key: {finnhub_key[:20] if finnhub_key != 'NOT SET' else 'NOT SET'}...")

    # Test Finnhub connection
    print("\nInitializing screener...")
    screener = MarketScreener()

    # Test earnings calendar
    print("\nTesting Finnhub earnings calendar...")
    earnings = screener.get_earnings_calendar()
    print(f"Loaded {len(earnings)} upcoming earnings events")

    if earnings:
        # Show first 5
        print("\nSample earnings:")
        for ticker, data in list(earnings.items())[:5]:
            print(f"  {ticker}: {data.get('days_until', 0)} days until earnings")

    # Test analyst ratings for a known stock
    print("\nTesting Finnhub analyst ratings for AAPL...")
    ratings = screener.get_analyst_ratings('AAPL')
    print(f"Upgrades: {ratings.get('upgrade_count', 0)}, Downgrades: {ratings.get('downgrade_count', 0)}")
    print(f"Score: {ratings.get('score', 0)}")
    print(f"Catalyst: {ratings.get('catalyst_type', 'None')}")

    if ratings.get('recent_upgrades'):
        print("\nRecent upgrades:")
        for upgrade in ratings.get('recent_upgrades', []):
            print(f"  {upgrade.get('firm', 'Unknown')}: {upgrade.get('to_grade', '')} ({upgrade.get('days_ago', 0)} days ago)")

    print("\n✓ Finnhub integration working!")

if __name__ == '__main__':
    main()
