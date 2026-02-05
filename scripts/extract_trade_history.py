#!/usr/bin/env python3
"""
Extract trade history from Alpaca to reconstruct missing CSV entries.

Run this on the production server to get entry/exit data for trades
that were executed but not logged to completed_trades.csv.

Usage:
    python scripts/extract_trade_history.py

Output: Prints trade data that can be used to populate the CSV.
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alpaca_broker import AlpacaBroker

def extract_trades():
    """Extract buy/sell pairs from Alpaca order history."""

    broker = AlpacaBroker()

    # Tickers that were sold but not logged (from Feb 5, 2026 EXIT command crash)
    missing_tickers = ['VIAV', 'PEN', 'GE', 'DVN', 'HII']

    print("=" * 80)
    print("TRADE HISTORY EXTRACTION")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    trades = []

    for ticker in missing_tickers:
        print(f"\n{ticker}:")
        print("-" * 40)

        # Get all orders for this ticker
        try:
            orders = broker.api.list_orders(
                status='all',
                symbols=[ticker],
                limit=100
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        buys = []
        sells = []

        for o in orders:
            if o.status == 'filled':
                order_data = {
                    'id': o.id,
                    'side': o.side,
                    'qty': int(o.filled_qty),
                    'price': float(o.filled_avg_price) if o.filled_avg_price else 0,
                    'filled_at': str(o.filled_at) if o.filled_at else str(o.submitted_at),
                    'type': o.type
                }

                if o.side == 'buy':
                    buys.append(order_data)
                else:
                    sells.append(order_data)

                print(f"  {o.side.upper():4} | {order_data['qty']:3} shares @ ${order_data['price']:.2f} | {o.type} | {order_data['filled_at'][:19]}")

        # Match buys to sells (most recent buy for each sell)
        if buys and sells:
            # Sort by date
            buys.sort(key=lambda x: x['filled_at'])
            sells.sort(key=lambda x: x['filled_at'])

            # For simplicity, match the most recent buy to the most recent sell
            buy = buys[-1]  # Most recent buy
            sell = sells[-1]  # Most recent sell (should be today)

            entry_price = buy['price']
            exit_price = sell['price']
            shares = sell['qty']

            return_pct = ((exit_price - entry_price) / entry_price) * 100
            return_dollars = shares * (exit_price - entry_price)

            entry_date = buy['filled_at'][:10]
            exit_date = sell['filled_at'][:10]

            # Calculate hold days
            try:
                entry_dt = datetime.strptime(entry_date, '%Y-%m-%d')
                exit_dt = datetime.strptime(exit_date, '%Y-%m-%d')
                hold_days = (exit_dt - entry_dt).days
            except:
                hold_days = 0

            trade = {
                'ticker': ticker,
                'entry_date': entry_date,
                'exit_date': exit_date,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'shares': shares,
                'hold_days': hold_days,
                'return_pct': return_pct,
                'return_dollars': return_dollars
            }
            trades.append(trade)

            print(f"\n  MATCHED TRADE:")
            print(f"    Entry: {entry_date} @ ${entry_price:.2f}")
            print(f"    Exit:  {exit_date} @ ${exit_price:.2f}")
            print(f"    Hold:  {hold_days} days")
            print(f"    Return: {return_pct:+.2f}% (${return_dollars:+.2f})")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY - CSV DATA")
    print("=" * 80)

    print("\nCSV format (copy to completed_trades.csv):")
    print("-" * 80)

    total_return = 0
    for t in trades:
        total_return += t['return_dollars']
        # Minimal CSV row - other columns can be empty or default
        trade_id = f"{t['ticker']}_{t['entry_date']}"
        print(f"{trade_id},{t['entry_date']},{t['exit_date']},{t['ticker']},,{t['entry_price']:.2f},{t['exit_price']:.2f},,{t['shares']},,,,{t['return_pct']:.2f},{t['return_dollars']:.2f},EXIT_COMMAND,claude_decision,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")

    print("-" * 80)
    print(f"\nTotal P&L from {len(trades)} trades: ${total_return:+.2f}")

    # Also output as JSON for easier parsing
    print("\n" + "=" * 80)
    print("JSON FORMAT (for programmatic use):")
    print("=" * 80)
    import json
    print(json.dumps(trades, indent=2))

if __name__ == "__main__":
    extract_trades()
