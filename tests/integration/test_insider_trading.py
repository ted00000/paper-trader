#!/usr/bin/env python3
"""Test if Finnhub insider trading API works on free tier"""

import os
import requests
from datetime import datetime, timedelta

def test_insider_transactions():
    """Test insider transactions API endpoint"""

    finnhub_key = os.environ.get('FINNHUB_API_KEY', '')

    if not finnhub_key:
        print("❌ FINNHUB_API_KEY not set in environment")
        return False

    print(f"Testing with API key: {finnhub_key[:20]}...")
    print()

    # Test with a known stock that likely has insider activity
    test_ticker = 'AAPL'

    # Insider transactions endpoint
    url = 'https://finnhub.io/api/v1/stock/insider-transactions'
    params = {
        'symbol': test_ticker,
        'from': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
        'to': datetime.now().strftime('%Y-%m-%d'),
        'token': finnhub_key
    }

    print(f"Testing insider transactions for {test_ticker}...")
    print(f"Date range: Last 90 days")
    print()

    try:
        response = requests.get(url, params=params, timeout=10)

        print(f"Response status: {response.status_code}")

        if response.status_code == 403:
            print("❌ FORBIDDEN - Insider transactions require paid tier")
            print()
            print("This endpoint is NOT available on free tier")
            return False

        if response.status_code == 429:
            print("❌ RATE LIMIT - Too many requests")
            return False

        if response.status_code != 200:
            print(f"❌ ERROR - Status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False

        data = response.json()

        # Check if we got data
        if isinstance(data, dict) and 'data' in data:
            transactions = data['data']
            print(f"✅ SUCCESS - Got {len(transactions)} insider transactions")
            print()

            if transactions:
                print("Sample transactions:")
                for txn in transactions[:3]:
                    name = txn.get('name', 'Unknown')
                    shares = txn.get('share', 0)
                    change = txn.get('change', 0)
                    filing_date = txn.get('filingDate', 'Unknown')
                    transaction_date = txn.get('transactionDate', 'Unknown')

                    print(f"  • {name}")
                    print(f"    Shares: {shares:,} | Change: {change:,}")
                    print(f"    Transaction: {transaction_date} | Filed: {filing_date}")
                    print()

            print("✅ Insider transactions API IS AVAILABLE on free tier!")
            return True

        elif isinstance(data, list):
            print(f"✅ SUCCESS - Got {len(data)} insider transactions")
            print()

            if data:
                print("Sample transactions:")
                for txn in data[:3]:
                    print(f"  Transaction: {txn}")
                    print()

            print("✅ Insider transactions API IS AVAILABLE on free tier!")
            return True

        else:
            print(f"⚠️  Unexpected response format: {type(data)}")
            print(f"Data: {data}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("FINNHUB INSIDER TRADING API TEST")
    print("=" * 60)
    print()

    success = test_insider_transactions()

    print()
    print("=" * 60)
    if success:
        print("RESULT: Insider trading data is AVAILABLE")
        print("We can implement this as part of the enhancements!")
    else:
        print("RESULT: Insider trading data is NOT AVAILABLE")
        print("We'll skip this and implement the 5 free enhancements only")
    print("=" * 60)
