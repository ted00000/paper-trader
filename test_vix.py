#!/usr/bin/env python3
"""
Test VIX data access with Polygon Indices Basic
"""
import os
import sys
import requests

# Load environment variables
if os.path.exists('/root/.env'):
    with open('/root/.env') as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('"').strip("'")

POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

if not POLYGON_API_KEY:
    print("❌ POLYGON_API_KEY not found in environment")
    sys.exit(1)

print("=" * 70)
print("VIX DATA ACCESS TEST")
print("=" * 70)

# Test 1: Previous day close (primary method)
print("\n📊 Test 1: Previous Day Close (/v2/aggs/ticker/I:VIX/prev)")
print("-" * 70)
url1 = f'https://api.polygon.io/v2/aggs/ticker/I:VIX/prev?adjusted=true&apiKey={POLYGON_API_KEY}'
try:
    response = requests.get(url1, timeout=10)
    print(f"Status Code: {response.status_code}")
    data = response.json()

    if data.get('status') == 'OK' and 'results' in data and len(data['results']) > 0:
        result = data['results'][0]
        vix_close = result.get('c')
        vix_date = result.get('t')  # timestamp
        print(f"✅ SUCCESS!")
        print(f"VIX Close: {vix_close}")
        print(f"Timestamp: {vix_date}")
        print(f"Full result: {result}")
    else:
        print(f"❌ FAILED")
        print(f"Status: {data.get('status')}")
        print(f"Message: {data.get('message', 'No message')}")
        print(f"Full response: {data}")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Snapshot (fallback method)
print("\n📊 Test 2: Current Snapshot (/v3/snapshot/indices/I:VIX)")
print("-" * 70)
url2 = f'https://api.polygon.io/v3/snapshot/indices/I:VIX?apiKey={POLYGON_API_KEY}'
try:
    response = requests.get(url2, timeout=10)
    print(f"Status Code: {response.status_code}")
    data = response.json()

    if data.get('status') == 'OK' and 'results' in data:
        results = data['results']
        vix_value = results.get('value')
        print(f"✅ SUCCESS!")
        print(f"VIX Value: {vix_value}")
        print(f"Full results: {results}")
    else:
        print(f"❌ FAILED")
        print(f"Status: {data.get('status')}")
        print(f"Message: {data.get('message', 'No message')}")
        print(f"Full response: {data}")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Yahoo Finance (free fallback)
print("\n📊 Test 3: Yahoo Finance CSV (%5EVIX)")
print("-" * 70)
url3 = 'https://query1.finance.yahoo.com/v7/finance/download/%5EVIX?period1=0&period2=9999999999&interval=1d&events=history'
try:
    response = requests.get(url3, timeout=10)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        lines = response.text.strip().split('\n')
        if len(lines) >= 2:
            print(f"✅ SUCCESS!")
            print(f"Total data rows: {len(lines) - 1}")

            # Show last 3 days
            print("\nLast 3 trading days:")
            for line in lines[-4:-1]:
                parts = line.split(',')
                if len(parts) >= 5:
                    date = parts[0]
                    close = parts[4]
                    print(f"  {date}: VIX Close = {close}")

            # Most recent
            last_line = lines[-1]
            parts = last_line.split(',')
            if len(parts) >= 5:
                vix_close = float(parts[4])
                vix_date = parts[0]
                print(f"\n📍 MOST RECENT: {vix_date} - VIX = {vix_close:.2f}")
        else:
            print(f"❌ FAILED: Not enough data")
    else:
        print(f"❌ FAILED with status {response.status_code}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print("Based on test results:")
print("- If Test 1 or 2 passed: Polygon Indices access works")
print("- If only Test 3 passed: Use Yahoo Finance fallback (free)")
print("- System will automatically try Polygon first, then Yahoo")
print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
