#!/usr/bin/env python3
"""
Test V4 enhancements - RS bypass + SEC 8-K detection

Key Changes:
1. ✓ RS filter bypass for fresh M&A/FDA news (0-1 days old)
2. ✓ SEC 8-K filing detection for M&A and major contracts
"""

import os

# Set env vars BEFORE importing
os.environ['POLYGON_API_KEY'] = os.environ.get('POLYGON_API_KEY', 'cvPn7WbJ_eZe_iwMc1RiKe8Ua09QTKYo')
os.environ['FINNHUB_API_KEY'] = os.environ.get('FINNHUB_API_KEY', 'd4f6u59r01qkcvvgrh90d4f6u59r01qkcvvgrh9g')

from market_screener import MarketScreener

def main():
    print("=" * 80)
    print("V4 ENHANCEMENTS TEST")
    print("=" * 80)
    print("\nNew Features:")
    print("  1. RS filter bypass for fresh M&A/FDA news (0-1 days old)")
    print("  2. SEC 8-K filing detection (M&A, major contracts)")
    print()
    print("Expected Results:")
    print("  - Stocks with fresh M&A/FDA news bypass RS filter")
    print("  - Stocks with RS < 3% but no fresh catalyst still rejected")
    print("  - SEC 8-K filings detected and labeled as Tier 1")
    print()

    screener = MarketScreener()

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

    print(f"Testing {len(test_tickers)} stocks...\\n")

    candidates = []
    rs_bypassed = 0
    sec_8k_found = 0
    fresh_ma_fda = 0
    rejected_rs = 0

    for ticker in test_tickers:
        result = screener.scan_stock(ticker)

        if result:
            candidates.append(result)

            # Check if RS was bypassed (RS < 3% but still passed)
            rs_pct = result['relative_strength']['rs_pct']
            has_fresh_catalyst = (
                result['catalyst_signals'].get('catalyst_type_news') in ['M&A_news', 'FDA_news'] and
                result['catalyst_signals'].get('catalyst_news_age_days') is not None and
                result['catalyst_signals'].get('catalyst_news_age_days') <= 1
            )
            has_8k = result['sec_8k_filings'].get('has_recent_8k', False)

            if rs_pct < 3.0 and (has_fresh_catalyst or has_8k):
                rs_bypassed += 1
                print(f"🔓 {ticker}: RS BYPASSED (RS={rs_pct:.1f}%)")
                print(f"   Reason: {result['catalyst_tier']}")
                print(f"   Score: {result['composite_score']:.1f}")
                print()

            # Count fresh M&A/FDA
            if has_fresh_catalyst:
                fresh_ma_fda += 1
                print(f"🔥 {ticker}: FRESH CATALYST")
                print(f"   {result['catalyst_tier']}")
                print(f"   Age: {result['catalyst_signals'].get('catalyst_news_age_days')} days")
                print()

            # Count SEC 8-K filings
            if has_8k:
                sec_8k_found += 1
                print(f"📄 {ticker}: SEC 8-K FILING DETECTED")
                print(f"   Type: {result['sec_8k_filings'].get('catalyst_type_8k')}")
                print(f"   Filed: {result['sec_8k_filings'].get('filing_date')}")
                print()
        else:
            rejected_rs += 1

    # Sort by score
    candidates.sort(key=lambda x: x['composite_score'], reverse=True)

    # Results
    print("\\n" + "=" * 80)
    print("V4 TEST RESULTS")
    print("=" * 80)
    print(f"Stocks analyzed: {len(test_tickers)}")
    print(f"Rejected by RS filter: {rejected_rs}")
    print(f"Passed all filters: {len(candidates)}")
    print()
    print("V4 ENHANCEMENTS:")
    print(f"  - RS filter bypassed: {rs_bypassed} stocks")
    print(f"  - Fresh M&A/FDA news (0-1 days): {fresh_ma_fda} stocks")
    print(f"  - SEC 8-K filings detected: {sec_8k_found} stocks")

    # Top 10
    print("\\n" + "=" * 80)
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
    print("✓ V4 enhancements test complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()
