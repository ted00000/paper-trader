#!/usr/bin/env python3
"""Test what price target data is available from Finnhub"""

import os
import requests
from datetime import datetime, timedelta

finnhub_key = os.environ.get('FINNHUB_API_KEY', 'd4f6u59r01qkcvvgrh90d4f6u59r01qkcvvgrh9g')

# Test with AAPL
ticker = 'AAPL'

print("Testing analyst upgrades/downgrades endpoint for price targets...")
url = 'https://finnhub.io/api/v1/stock/upgrade-downgrade'
params = {
    'symbol': ticker,
    'from': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
    'to': datetime.now().strftime('%Y-%m-%d'),
    'token': finnhub_key
}

response = requests.get(url, params=params, timeout=10)
ratings = response.json()

print(f"\nSample ratings data for {ticker}:")
print(f"Total ratings: {len(ratings) if isinstance(ratings, list) else 0}")

if isinstance(ratings, list) and ratings:
    print("\nFirst 3 ratings:")
    for i, rating in enumerate(ratings[:3], 1):
        print(f"\n#{i}:")
        for key, value in rating.items():
            print(f"  {key}: {value}")

print("\n" + "="*60)
print("Testing price target endpoint...")
url2 = 'https://finnhub.io/api/v1/stock/price-target'
params2 = {
    'symbol': ticker,
    'token': finnhub_key
}

response2 = requests.get(url2, params=params2, timeout=10)
print(f"Status: {response2.status_code}")

if response2.status_code == 200:
    pt_data = response2.json()
    print(f"\nPrice Target Data for {ticker}:")
    for key, value in pt_data.items():
        print(f"  {key}: {value}")
else:
    print(f"Price targets not available: {response2.text[:200]}")
