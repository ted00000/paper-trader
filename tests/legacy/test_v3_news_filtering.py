#!/usr/bin/env python3
"""
Test V3 news filtering - Same-day recency + negative sentiment

Key Changes:
1. M&A/FDA news must be 0-1 days old (not 3+ days)
2. Contract news must be 0-2 days old
3. Filter out negative news (investigations, offerings, downgrades)
"""

import os

# Set env vars BEFORE importing
os.environ['POLYGON_API_KEY'] = os.environ.get('POLYGON_API_KEY', 'cvPn7WbJ_eZe_iwMc1RiKe8Ua09QTKYo')
os.environ['FINNHUB_API_KEY'] = os.environ.get('FINNHUB_API_KEY', 'd4f6u59r01qkcvvgrh90d4f6u59r01qkcvvgrh9g')

from market_screener import MarketScreener

def main():
    print("=" * 80)
    print("V3 NEWS FILTERING TEST")
    print("=" * 80)
    print("\nEnhancements:")
    print("  1. M&A/FDA news: 0-1 days old only (reject 3+ day old news)")
    print("  2. Contract news: 0-2 days old only")
    print("  3. Negative sentiment filter (investigations, offerings, downgrades)")
    print()

    screener = MarketScreener()

    # Test tickers that HAD M&A news in previous scan
    test_tickers = [
        'AVDL',  # Had M&A news 3 days ago (should be REJECTED now)
        'BAC',   # Had selling news (should be REJECTED)
        'BILL',  # Had activist news (might pass if recent)
        'ADVM',  # Had investigation news (should be REJECTED)
        'ANNX',  # Had offering news (should be REJECTED)
        'BIIB',  # Our current holding
    ]

    print(f"Testing {len(test_tickers)} stocks with recent news...\n")

    for ticker in test_tickers:
        news_result = screener.get_news_score(ticker)

        catalyst_type = news_result.get('catalyst_type_news')
        news_age = news_result.get('catalyst_news_age_days')

        if catalyst_type:
            print(f"✓ {ticker}: {catalyst_type}")
            if news_age is not None:
                print(f"  Age: {news_age} days old")
            print(f"  Score: {news_result['scaled_score']:.1f}")
            print(f"  Keywords: {', '.join(news_result['keywords'][:5])}")
            print()
        else:
            print(f"✗ {ticker}: No valid catalyst (likely filtered out)")
            if news_result['count'] > 0:
                print(f"  Had {news_result['count']} articles but all rejected")
            print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\nExpected results:")
    print("  - AVDL: REJECTED (M&A news 3+ days old)")
    print("  - BAC: REJECTED (selling/reduction news)")
    print("  - ADVM: REJECTED (investigation news)")
    print("  - ANNX: REJECTED (dilutive offering news)")
    print("  - Only FRESH M&A/FDA news (0-1 days) should pass")

if __name__ == '__main__':
    main()
