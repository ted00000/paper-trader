#!/usr/bin/env python3
"""
Test V5 law firm spam filter + acquirer/target detection

Key Changes:
1. ✓ Filter out law firm investigation spam
2. ✓ Detect acquirer vs target (only keep targets)
3. ✓ Fix news age accuracy
"""

import os

# Set env vars BEFORE importing
os.environ['POLYGON_API_KEY'] = os.environ.get('POLYGON_API_KEY', 'cvPn7WbJ_eZe_iwMc1RiKe8Ua09QTKYo')
os.environ['FINNHUB_API_KEY'] = os.environ.get('FINNHUB_API_KEY', 'd4f6u59r01qkcvvgrh90d4f6u59r01qkcvvgrh9g')

from market_screener import MarketScreener

def main():
    print("=" * 80)
    print("V5 LAW FIRM SPAM FILTER + ACQUIRER/TARGET DETECTION TEST")
    print("=" * 80)
    print("\nNew Features:")
    print("  1. Law firm spam filter (shareholder alerts, investigations)")
    print("  2. Acquirer vs target detection (only keep targets)")
    print("  3. Fixed news age accuracy")
    print()
    print("Expected Results:")
    print("  - AVDL: REJECTED (law firm spam from Nov 19)")
    print("  - ADVM: REJECTED (law firm investigation)")
    print("  - AKRO: REJECTED (law firm investigation)")
    print("  - AXTA: May pass if has target language")
    print("  - ADBE: REJECTED (acquirer, not target)")
    print("  - CETX: REJECTED (acquirer, not target)")
    print()

    screener = MarketScreener()

    # Test tickers from V4 scan that were rejected
    test_tickers = [
        'AVDL',  # Law firm spam (should be REJECTED)
        'ADVM',  # Law firm investigation (should be REJECTED)
        'AKRO',  # Law firm investigation (should be REJECTED)
        'AXTA',  # M&A target with opposition (may pass filter)
        'ADBE',  # Acquirer (should be REJECTED)
        'CETX',  # Acquirer (should be REJECTED)
        'BAC',   # Test existing position
        'BRY',   # Test candidate
    ]

    print(f"Testing {len(test_tickers)} stocks...\\n")

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
            if news_result['top_articles']:
                print(f"  Top article: {news_result['top_articles'][0]['title'][:80]}")
            print()
        else:
            print(f"✗ {ticker}: No valid catalyst (filtered out)")
            if news_result['count'] > 0:
                print(f"  Had {news_result['count']} articles but all rejected/filtered")
                if news_result['top_articles']:
                    print(f"  Sample: {news_result['top_articles'][0]['title'][:80]}")
            print()

    print("=" * 80)
    print("V5 TEST COMPLETE")
    print("=" * 80)
    print("\\nExpected filtering:")
    print("  - AVDL: Law firm spam filtered out")
    print("  - ADVM: Law firm investigation filtered out")
    print("  - AKRO: Law firm investigation filtered out")
    print("  - ADBE: Acquirer filtered out (buying Semrush)")
    print("  - CETX: Acquirer filtered out (buying Invocon)")
    print("  - Only M&A TARGETS should pass")

if __name__ == '__main__':
    main()
