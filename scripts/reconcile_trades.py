#!/usr/bin/env python3
"""
Reconcile CSV trade data with Alpaca order history.
Calculates true realized P&L from Alpaca fills.
"""

import os
import sys
import csv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alpaca_broker import AlpacaBroker
from collections import defaultdict

def reconcile():
    broker = AlpacaBroker()
    orders = broker.api.list_orders(status="all", limit=500)
    filled = [o for o in orders if o.status == "filled"]

    # Group by symbol
    trades = defaultdict(list)
    for o in filled:
        trades[o.symbol].append({
            "side": o.side,
            "qty": float(o.filled_qty),
            "price": float(o.filled_avg_price),
            "date": str(o.filled_at)[:10]
        })

    # Calculate Alpaca P&L for all closed trades
    print("=" * 60)
    print("ALPACA TRUE P&L BY TRADE")
    print("=" * 60)

    total_alpaca = 0
    closed_trades = []

    for symbol in sorted(trades.keys()):
        orders_list = trades[symbol]
        buys = sorted([o for o in orders_list if o["side"] == "buy"], key=lambda x: x["date"])
        sells = sorted([o for o in orders_list if o["side"] == "sell"], key=lambda x: x["date"])

        # Match each sell to its corresponding buy
        for i, sell in enumerate(sells):
            if i < len(buys):
                buy = buys[i]
                shares = min(buy["qty"], sell["qty"])
                pl = shares * (sell["price"] - buy["price"])
                total_alpaca += pl
                closed_trades.append({
                    "symbol": symbol,
                    "entry_date": buy["date"],
                    "entry_price": buy["price"],
                    "exit_date": sell["date"],
                    "exit_price": sell["price"],
                    "shares": shares,
                    "return": pl
                })
                pct = (sell["price"] - buy["price"]) / buy["price"] * 100
                print(f"{symbol:6} | {shares:4.0f} sh | ${buy['price']:8.2f} -> ${sell['price']:8.2f} | {pct:+6.2f}% | ${pl:+8.2f}")

    print("-" * 60)
    print(f"TOTAL ALPACA REALIZED P&L: ${total_alpaca:.2f}")

    # Read current CSV
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "trade_history", "completed_trades.csv")

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    csv_total = sum(float(r["Return_Dollars"]) for r in csv_rows)

    print(f"\nCSV TOTAL: ${csv_total:.2f}")
    print(f"CSV TRADES: {len(csv_rows)}")
    print(f"ALPACA CLOSED: {len(closed_trades)}")
    print(f"\nDIFFERENCE: ${total_alpaca - csv_total:.2f}")

    # Check for missing trades
    csv_symbols = set()
    for r in csv_rows:
        # Extract base symbol from trade ID
        tid = r["Trade_ID"]
        symbol = tid.split("_")[0]
        csv_symbols.add((symbol, r["Entry_Date"][:10]))

    alpaca_symbols = set((t["symbol"], t["entry_date"]) for t in closed_trades)

    missing = alpaca_symbols - csv_symbols
    if missing:
        print("\nMISSING FROM CSV:")
        for sym, date in missing:
            for t in closed_trades:
                if t["symbol"] == sym and t["entry_date"] == date:
                    print(f"  {sym} entered {date}: ${t['return']:+.2f}")

if __name__ == "__main__":
    reconcile()
