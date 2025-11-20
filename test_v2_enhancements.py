#!/usr/bin/env python3
"""
Test V2 enhancements - Catalyst-first approach

Enhancements:
1. ✓ Earnings beat recency tiers (FRESH 0-3d, RECENT 4-7d, OLDER 8-30d)
2. ✓ M&A, FDA, major contract detection from news
3. ✓ Catalyst-first filtering (reject stocks with no catalyst + weak RS)
4. ✓ Increased scoring for confirmed catalysts
5. ✓ Downgraded insider buying from 20% to 15% (leading indicator)
"""

import os

# Set env vars BEFORE importing
os.environ['POLYGON_API_KEY'] = os.environ.get('POLYGON_API_KEY', 'cvPn7WbJ_eZe_iwMc1RiKe8Ua09QTKYo')
os.environ['FINNHUB_API_KEY'] = os.environ.get('FINNHUB_API_KEY', 'd4f6u59r01qkcvvgrh90d4f6u59r01qkcvvgrh9g')

from market_screener import MarketScreener

def main():
    print("=" * 80)
    print("SCREENER V2 - CATALYST-FIRST ENHANCEMENTS TEST")
    print("=" * 80)
    print("\nKey Changes:")
    print("  1. Earnings beat recency: FRESH (0-3d) > RECENT (4-7d) > OLDER (8-30d)")
    print("  2. M&A/FDA/Contract news detection with 25%/25%/20% boosts")
    print("  3. Catalyst-first filter: Requires catalyst OR strong RS (>7%)")
    print("  4. Insider buying downgraded: 20% → 15% (leading indicator)")
    print("  5. Fresh earnings beats: 15% → 20% boost")
    print()

    screener = MarketScreener()

    # Load earnings calendar
    print("Loading earnings calendar...")
    earnings_cal = screener.get_earnings_calendar()
    print(f"✓ Loaded {len(earnings_cal)} upcoming earnings events\n")

    # Test diverse tickers
    test_tickers = [
        # Tech
        'NVDA', 'AMD', 'AVGO', 'TSLA', 'AAPL', 'MSFT', 'META', 'GOOGL',
        # Healthcare (may have FDA news)
        'LLY', 'ABBV', 'BIIB', 'GILD', 'MRNA',
        # Finance
        'JPM', 'BAC', 'GS', 'MS',
        # Consumer
        'AMZN', 'COST', 'HD', 'WMT',
        # Industrial
        'BA', 'LMT', 'RTX', 'GE'
    ]

    print(f"Testing {len(test_tickers)} stocks...\n")

    candidates = []
    rejected_no_catalyst = 0
    rejected_rs = 0

    tier1_upgrades = 0
    tier1_ma_news = 0
    tier1_fda_news = 0
    tier1_contract_news = 0
    tier1_insider = 0
    tier2_fresh_beats = 0
    tier2_recent_beats = 0
    tier2_older_beats = 0

    for ticker in test_tickers:
        # Test RS filter first
        sector = screener.get_stock_sector(ticker)
        rs_result = screener.calculate_relative_strength(ticker, sector)

        if not rs_result['passed_filter']:
            rejected_rs += 1
            continue

        # Full scan
        result = screener.scan_stock(ticker)

        if result is None:
            rejected_no_catalyst += 1
            continue

        candidates.append(result)

        # Track catalyst types
        catalyst_tier = result.get('catalyst_tier', '')

        if 'Analyst Upgrade' in catalyst_tier:
            tier1_upgrades += 1
            print(f"✓ {ticker}: {catalyst_tier}")
            print(f"  Score: {result['composite_score']:.1f} | {result['why_selected']}")
            print()

        elif 'M&A News' in catalyst_tier:
            tier1_ma_news += 1
            print(f"✓ {ticker}: {catalyst_tier}")
            print(f"  Score: {result['composite_score']:.1f} | {result['why_selected']}")
            print()

        elif 'FDA News' in catalyst_tier:
            tier1_fda_news += 1
            print(f"✓ {ticker}: {catalyst_tier}")
            print(f"  Score: {result['composite_score']:.1f} | {result['why_selected']}")
            print()

        elif 'Contract News' in catalyst_tier:
            tier1_contract_news += 1
            print(f"✓ {ticker}: {catalyst_tier}")
            print(f"  Score: {result['composite_score']:.1f} | {result['why_selected']}")
            print()

        elif 'Insider Buying' in catalyst_tier:
            tier1_insider += 1
            # Don't print insider buying (too noisy)

        elif 'Fresh Earnings Beat' in catalyst_tier:
            tier2_fresh_beats += 1
            print(f"📊 {ticker}: {catalyst_tier}")
            print(f"  Score: {result['composite_score']:.1f} | {result['why_selected']}")
            print()

        elif 'Earnings Beat' in catalyst_tier:
            recency = result['earnings_surprises'].get('recency_tier', '')
            if recency == 'RECENT':
                tier2_recent_beats += 1
            else:
                tier2_older_beats += 1

    # Sort by score
    candidates.sort(key=lambda x: x['composite_score'], reverse=True)

    # Results
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"Stocks analyzed: {len(test_tickers)}")
    print(f"Rejected by RS filter: {rejected_rs}")
    print(f"Rejected by catalyst filter: {rejected_no_catalyst}")
    print(f"Passed all filters: {len(candidates)}")
    print()
    print("TIER 1 CATALYSTS FOUND:")
    print(f"  - Analyst upgrades: {tier1_upgrades}")
    print(f"  - M&A news: {tier1_ma_news}")
    print(f"  - FDA news: {tier1_fda_news}")
    print(f"  - Contract news: {tier1_contract_news}")
    print(f"  - Insider buying: {tier1_insider}")
    print()
    print("TIER 2 CATALYSTS FOUND:")
    print(f"  - Fresh earnings beats (0-3d): {tier2_fresh_beats}")
    print(f"  - Recent earnings beats (4-7d): {tier2_recent_beats}")
    print(f"  - Older earnings beats (8-30d): {tier2_older_beats}")

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
    print("✓ V2 enhancements test complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()
