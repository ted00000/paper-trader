#!/usr/bin/env python3
"""
Test VIX data access with CBOE (official free source)
"""
import requests

print("=" * 70)
print("VIX DATA ACCESS TEST - CBOE")
print("=" * 70)

print("\n📊 Testing CBOE VIX Data (official source - free)")
print("-" * 70)

url = 'https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv'

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        lines = response.text.strip().split('\n')

        if len(lines) >= 2:
            print(f"✅ SUCCESS!")
            print(f"Total data rows: {len(lines) - 1}")

            # Show header
            header = lines[0]
            print(f"\nCSV Header: {header}")

            # Show last 5 trading days
            print("\nLast 5 trading days:")
            for line in lines[-6:-1]:
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

                # Determine regime
                if vix_close >= 35:
                    regime = "🚨 SHUTDOWN (VIX ≥ 35)"
                elif vix_close >= 30:
                    regime = "⚠️  CAUTIOUS (VIX 30-35)"
                else:
                    regime = "✅ NORMAL (VIX < 30)"

                print(f"Market Regime: {regime}")
        else:
            print(f"❌ FAILED: Not enough data")
    else:
        print(f"❌ FAILED with status {response.status_code}")
        print(f"Response: {response.text[:200]}")

except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("\nCBOE provides official VIX data for free, updated daily.")
print("This is the same data source used by financial institutions.")
print("\n" + "=" * 70)
