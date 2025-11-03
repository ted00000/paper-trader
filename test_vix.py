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

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
