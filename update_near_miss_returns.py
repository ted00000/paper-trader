#!/usr/bin/env python3
"""
NEAR-MISS FORWARD RETURN UPDATER (v10.4)
=========================================

Updates the near_miss_log.csv with forward returns (5d, 10d, 20d) after
sufficient trading days have passed since the rejection date.

Purpose:
    Learn if hard gates are rejecting tomorrow's winners by comparing
    near-miss performance to accepted candidates.

Schedule:
    Run daily at 8:00 PM ET (after market close)
    Updates any records where sufficient time has passed

Philosophy:
    "Are we rejecting tomorrow's winners? Let the data decide."

Author: Paper Trading Lab
Version: 10.4
Created: 2026-01-01
"""

import os
import csv
import requests
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# Configuration
ET = ZoneInfo('America/New_York')
PROJECT_DIR = Path(__file__).parent
POLYGON_API_KEY = os.environ.get('POLYGON_API_KEY', '')
NEAR_MISS_LOG_PATH = PROJECT_DIR / 'strategy_evolution' / 'near_miss_log.csv'

# Trading days thresholds (approximate - we'll check actual calendar days)
# NYSE is closed on weekends + holidays, so we use calendar days as proxy
DAYS_5_TRADING = 7   # ~5 trading days (1 week)
DAYS_10_TRADING = 14  # ~10 trading days (2 weeks)
DAYS_20_TRADING = 30  # ~20 trading days (1 month)


def get_stock_price(ticker, date_str):
    """
    Get stock closing price for a specific date using Polygon API.

    Args:
        ticker: Stock symbol
        date_str: Date in YYYY-MM-DD format

    Returns:
        float: Closing price, or None if unavailable
    """
    if not POLYGON_API_KEY:
        print(f"   ⚠️ WARNING: POLYGON_API_KEY not set - cannot fetch prices")
        return None

    try:
        # Use daily aggregates endpoint
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{date_str}/{date_str}"
        response = requests.get(url, params={'apiKey': POLYGON_API_KEY}, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get('results', [])

        if results:
            return results[0].get('c')  # Closing price
        else:
            # No data for this exact date (weekend/holiday) - try next trading day
            next_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{next_date}/{next_date}"
            response = requests.get(url, params={'apiKey': POLYGON_API_KEY}, timeout=10)
            data = response.json()
            results = data.get('results', [])

            if results:
                return results[0].get('c')
            else:
                return None

    except Exception as e:
        print(f"   ❌ Error fetching price for {ticker} on {date_str}: {e}")
        return None


def calculate_forward_return(rejection_price, future_price):
    """
    Calculate forward return percentage.

    Args:
        rejection_price: Price at rejection time
        future_price: Price N days later

    Returns:
        float: Return percentage (e.g., 5.2 for +5.2%)
    """
    if rejection_price == 0 or future_price is None:
        return None

    return ((future_price - rejection_price) / rejection_price) * 100


def update_near_miss_returns():
    """
    Main function to update near-miss log with forward returns.

    Process:
        1. Read near_miss_log.csv
        2. For each row, check if 5/10/20 days have passed
        3. If yes and Forward_Xd is empty, fetch price and calculate return
        4. Update the CSV with new forward returns
    """
    print("=" * 60)
    print("NEAR-MISS FORWARD RETURN UPDATER (v10.4)")
    print("=" * 60)
    print(f"Date: {datetime.now(ET).strftime('%Y-%m-%d')}")
    print(f"Time: {datetime.now(ET).strftime('%H:%M:%S')} ET\n")

    if not NEAR_MISS_LOG_PATH.exists():
        print("   ⚠️ WARNING: near_miss_log.csv not found")
        print(f"   Expected at: {NEAR_MISS_LOG_PATH}")
        print("   Nothing to update.\n")
        return

    # Read all rows
    rows = []
    with open(NEAR_MISS_LOG_PATH, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total_rows = len(rows)
    print(f"Loaded {total_rows} near-miss records\n")

    if total_rows == 0:
        print("   No records to update.\n")
        return

    # Track updates
    updated_5d = 0
    updated_10d = 0
    updated_20d = 0

    today = datetime.now(ET).date()

    # Process each row
    for i, row in enumerate(rows, 1):
        ticker = row['Ticker']
        rejection_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
        rejection_price = float(row['Price'])

        days_since_rejection = (today - rejection_date).days

        # Check if we need to update any forward return columns
        needs_update = False

        # 5-day forward return
        if not row['Forward_5d'] and days_since_rejection >= DAYS_5_TRADING:
            target_date = rejection_date + timedelta(days=DAYS_5_TRADING)
            future_price = get_stock_price(ticker, target_date.strftime('%Y-%m-%d'))

            if future_price:
                forward_return = calculate_forward_return(rejection_price, future_price)
                row['Forward_5d'] = f"{forward_return:.2f}" if forward_return is not None else ""
                updated_5d += 1
                needs_update = True
                print(f"   [{i}/{total_rows}] {ticker}: 5d return = {forward_return:.2f}%")

        # 10-day forward return
        if not row['Forward_10d'] and days_since_rejection >= DAYS_10_TRADING:
            target_date = rejection_date + timedelta(days=DAYS_10_TRADING)
            future_price = get_stock_price(ticker, target_date.strftime('%Y-%m-%d'))

            if future_price:
                forward_return = calculate_forward_return(rejection_price, future_price)
                row['Forward_10d'] = f"{forward_return:.2f}" if forward_return is not None else ""
                updated_10d += 1
                needs_update = True
                print(f"   [{i}/{total_rows}] {ticker}: 10d return = {forward_return:.2f}%")

        # 20-day forward return
        if not row['Forward_20d'] and days_since_rejection >= DAYS_20_TRADING:
            target_date = rejection_date + timedelta(days=DAYS_20_TRADING)
            future_price = get_stock_price(ticker, target_date.strftime('%Y-%m-%d'))

            if future_price:
                forward_return = calculate_forward_return(rejection_price, future_price)
                row['Forward_20d'] = f"{forward_return:.2f}" if forward_return is not None else ""
                updated_20d += 1
                needs_update = True
                print(f"   [{i}/{total_rows}] {ticker}: 20d return = {forward_return:.2f}%")

    # Write updated CSV
    if updated_5d > 0 or updated_10d > 0 or updated_20d > 0:
        with open(NEAR_MISS_LOG_PATH, 'w', newline='') as f:
            fieldnames = ['Date', 'Ticker', 'Gate_Failed', 'Threshold', 'Actual_Value', 'Margin_Pct',
                         'Price', 'Market_Cap', 'Volume_20d', 'RS_Pct', 'Sector',
                         'Forward_5d', 'Forward_10d', 'Forward_20d']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\n✓ Updated {updated_5d} records with 5-day returns")
        print(f"✓ Updated {updated_10d} records with 10-day returns")
        print(f"✓ Updated {updated_20d} records with 20-day returns")
        print(f"✓ Changes saved to {NEAR_MISS_LOG_PATH}\n")
    else:
        print("\n   No updates needed (insufficient time has passed for all records)\n")

    # Summary statistics (if we have any complete data)
    complete_5d = [float(row['Forward_5d']) for row in rows if row['Forward_5d']]
    complete_10d = [float(row['Forward_10d']) for row in rows if row['Forward_10d']]
    complete_20d = [float(row['Forward_20d']) for row in rows if row['Forward_20d']]

    if complete_5d or complete_10d or complete_20d:
        print("=" * 60)
        print("NEAR-MISS PERFORMANCE SUMMARY")
        print("=" * 60)

        if complete_5d:
            avg_5d = sum(complete_5d) / len(complete_5d)
            winners_5d = len([r for r in complete_5d if r > 0])
            print(f"5-Day Returns ({len(complete_5d)} stocks):")
            print(f"   Average: {avg_5d:+.2f}%")
            print(f"   Winners: {winners_5d}/{len(complete_5d)} ({winners_5d/len(complete_5d)*100:.1f}%)")

        if complete_10d:
            avg_10d = sum(complete_10d) / len(complete_10d)
            winners_10d = len([r for r in complete_10d if r > 0])
            print(f"\n10-Day Returns ({len(complete_10d)} stocks):")
            print(f"   Average: {avg_10d:+.2f}%")
            print(f"   Winners: {winners_10d}/{len(complete_10d)} ({winners_10d/len(complete_10d)*100:.1f}%)")

        if complete_20d:
            avg_20d = sum(complete_20d) / len(complete_20d)
            winners_20d = len([r for r in complete_20d if r > 0])
            print(f"\n20-Day Returns ({len(complete_20d)} stocks):")
            print(f"   Average: {avg_20d:+.2f}%")
            print(f"   Winners: {winners_20d}/{len(complete_20d)} ({winners_20d/len(complete_20d)*100:.1f}%)")

        print("=" * 60)

    print("\n✓ Near-miss forward return update completed successfully")


if __name__ == '__main__':
    update_near_miss_returns()
