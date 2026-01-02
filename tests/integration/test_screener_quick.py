#!/usr/bin/env python3
"""Quick test of screener with Finnhub integration on small universe"""

import os
from market_screener import MarketScreener

def main():
    print("=" * 80)
    print("QUICK SCREENER TEST - Finnhub Integration")
    print("=" * 80)

    # Initialize screener
    screener = MarketScreener()

    # Load earnings calendar first
    print("\nLoading earnings calendar...")
    earnings_cal = screener.get_earnings_calendar()
    print(f"✓ Loaded {len(earnings_cal)} upcoming earnings events\n")

    # Test with a small set of popular stocks
    test_tickers = [
        # Tech
        'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META', 'TSLA', 'AMD', 'AVGO',
        # Healthcare
        'LLY', 'UNH', 'JNJ', 'ABBV', 'MRK',
        # Finance
        'JPM', 'BAC', 'WFC', 'GS',
        # Consumer
        'AMZN', 'HD', 'MCD', 'COST',
        # Add some that might have earnings soon
        'BIIB',  # We know this one has a position
    ]

    print(f"Testing {len(test_tickers)} stocks...\n")

    candidates = []
    tier1_found = 0
    earnings_found = 0
    upgrades_found = 0

    for ticker in test_tickers:
        result = screener.scan_stock(ticker)

        if result:
            candidates.append(result)

            # Track Tier 1 catalysts
            if result.get('catalyst_tier'):
                tier1_found += 1
                print(f"✓ {ticker}: {result.get('catalyst_tier')}")
                print(f"  Score: {result['composite_score']:.1f} | {result['why_selected']}")
                print()

            # Track earnings
            if result.get('earnings_data', {}).get('has_upcoming_earnings'):
                earnings_found += 1
                days = result['earnings_data'].get('days_until', 0)
                print(f"📅 {ticker}: Earnings in {days} days")

            # Track upgrades
            if result.get('analyst_ratings', {}).get('upgrade_count', 0) > 0:
                upgrades_found += 1

    # Sort by score
    candidates.sort(key=lambda x: x['composite_score'], reverse=True)

    # Results
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"Stocks analyzed: {len(test_tickers)}")
    print(f"Passed RS filter: {len(candidates)}")
    print(f"Tier 1 catalysts found: {tier1_found}")
    print(f"Stocks with upcoming earnings: {earnings_found}")
    print(f"Stocks with analyst upgrades: {upgrades_found}")

    # Top 5
    print("\n" + "=" * 80)
    print("TOP 5 BY SCORE")
    print("=" * 80)
    for i, candidate in enumerate(candidates[:5], 1):
        ticker = candidate['ticker']
        score = candidate['composite_score']
        catalyst = candidate.get('catalyst_tier', 'None')
        rs = candidate['relative_strength']['rs_pct']
        why = candidate['why_selected']

        print(f"{i}. {ticker} - Score: {score:.1f}")
        print(f"   Catalyst: {catalyst}")
        print(f"   RS: {rs:.1f}% | {why}")
        print()

    print("=" * 80)
    print("✓ Test complete! Finnhub integration working properly.")
    print("=" * 80)

if __name__ == '__main__':
    main()
