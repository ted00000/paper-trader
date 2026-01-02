#!/usr/bin/env python3
"""Test enhanced screener with new catalyst detection"""

import os
from market_screener import MarketScreener

def main():
    print("=" * 80)
    print("ENHANCED SCREENER TEST - New Catalyst Detection")
    print("=" * 80)
    print("\nEnhancements:")
    print("  ✓ Analyst upgrade window: 7 → 14 days")
    print("  ✓ Earnings beats detection (after reporting)")
    print("  ✓ Insider trading detection (clustered buying)")
    print("  ✓ Pre-earnings REMOVED as Tier 1")
    print()

    # Initialize screener
    screener = MarketScreener()

    # Load earnings calendar first
    print("Loading earnings calendar...")
    earnings_cal = screener.get_earnings_calendar()
    print(f"✓ Loaded {len(earnings_cal)} upcoming earnings events\n")

    # Test with diverse tickers
    test_tickers = [
        # Tech with likely activity
        'NVDA', 'AMD', 'AVGO', 'TSLA',
        # Healthcare
        'LLY', 'ABBV', 'BIIB',
        # Finance
        'JPM', 'BAC', 'GS',
        # Consumer
        'AMZN', 'COST', 'HD',
        # Others
        'AAPL', 'MSFT', 'META', 'GOOGL'
    ]

    print(f"Testing {len(test_tickers)} stocks...\n")

    candidates = []
    tier1_found = 0
    tier2_found = 0
    upgrades_found = 0
    insider_buying_found = 0
    earnings_beats_found = 0

    for ticker in test_tickers:
        result = screener.scan_stock(ticker)

        if result:
            candidates.append(result)

            # Track catalysts
            catalyst_tier = result.get('catalyst_tier')

            if catalyst_tier:
                if 'Tier 1' in catalyst_tier:
                    tier1_found += 1
                    print(f"✓ {ticker}: {catalyst_tier}")
                    print(f"  Score: {result['composite_score']:.1f} | {result['why_selected']}")

                    # Show details
                    if 'Upgrade' in catalyst_tier:
                        upgrades_found += 1
                        upgrades = result['analyst_ratings'].get('recent_upgrades', [])
                        if upgrades:
                            print(f"  Details: {upgrades[0].get('firm')} - {upgrades[0].get('days_ago')} days ago")

                    if 'Insider' in catalyst_tier:
                        insider_buying_found += 1
                        buys = result['insider_transactions'].get('buy_count', 0)
                        print(f"  Details: {buys} insider buy transactions")

                    print()

                elif 'Tier 2' in catalyst_tier:
                    tier2_found += 1
                    earnings_beats_found += 1
                    print(f"📊 {ticker}: {catalyst_tier}")
                    print(f"  Score: {result['composite_score']:.1f}")
                    surprise = result['earnings_surprises'].get('surprise_pct', 0)
                    days = result['earnings_surprises'].get('days_ago', 0)
                    print(f"  Beat: +{surprise}% surprise ({days} days ago)")
                    print()

    # Sort by score
    candidates.sort(key=lambda x: x['composite_score'], reverse=True)

    # Results
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"Stocks analyzed: {len(test_tickers)}")
    print(f"Passed RS filter: {len(candidates)}")
    print(f"Tier 1 catalysts found: {tier1_found}")
    print(f"  - Analyst upgrades: {upgrades_found}")
    print(f"  - Insider buying clusters: {insider_buying_found}")
    print(f"Tier 2 catalysts found: {tier2_found}")
    print(f"  - Earnings beats: {earnings_beats_found}")

    # Top 10
    print("\n" + "=" * 80)
    print("TOP 10 BY SCORE")
    print("=" * 80)
    for i, candidate in enumerate(candidates[:10], 1):
        ticker = candidate['ticker']
        score = candidate['composite_score']
        catalyst = candidate.get('catalyst_tier', 'None')
        rs = candidate['relative_strength']['rs_pct']
        why = candidate['why_selected'][:60]

        print(f"{i}. {ticker} - Score: {score:.1f}")
        print(f"   Catalyst: {catalyst}")
        print(f"   RS: {rs:.1f}% | {why}")
        print()

    print("=" * 80)
    print("✓ Enhanced screener test complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()
