#!/usr/bin/env python3
"""
Update account_status.json based on CSV trade data and Alpaca account.
"""

import os
import sys
import json
import csv
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_account():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    account_path = os.path.join(base_dir, "portfolio_data", "account_status.json")
    csv_path = os.path.join(base_dir, "trade_history", "completed_trades.csv")

    # Load current account
    with open(account_path, "r") as f:
        account = json.load(f)

    print("Before:")
    print(f"  realized_pl: ${account.get('realized_pl', 0):.2f}")
    print(f"  account_value: ${account.get('account_value', 0):.2f}")
    print(f"  cash_available: ${account.get('cash_available', 0):.2f}")
    print(f"  total_trades: {account.get('total_trades', 0)}")

    # Calculate realized P&L from CSV
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        trades = list(reader)

    realized_pl = sum(float(t["Return_Dollars"]) for t in trades)
    total_trades = len(trades)

    # Try to get live Alpaca data
    try:
        from alpaca_broker import AlpacaBroker
        broker = AlpacaBroker()
        alpaca_account = broker.get_account()
        positions = broker.get_positions()

        cash_available = float(alpaca_account.cash)
        account_value = float(alpaca_account.equity)
        positions_value = sum(float(p.market_value) for p in positions)
    except Exception as e:
        print(f"Warning: Could not get Alpaca data: {e}")
        # Fallback to calculation
        cash_available = 10000 - sum(float(t.get("Position_Size", 0)) for t in trades if t.get("Position_Size")) + realized_pl
        positions_value = 0
        account_value = cash_available + positions_value

    # Calculate win rate
    winners = sum(1 for t in trades if float(t["Return_Dollars"]) > 0)
    win_rate = (winners / total_trades * 100) if total_trades > 0 else 0

    # Calculate averages
    winning_trades = [float(t["Return_Percent"]) for t in trades if float(t["Return_Dollars"]) > 0]
    losing_trades = [float(t["Return_Percent"]) for t in trades if float(t["Return_Dollars"]) < 0]

    avg_winner = sum(winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loser = sum(losing_trades) / len(losing_trades) if losing_trades else 0

    # Calculate average hold time
    hold_times = []
    for t in trades:
        try:
            hold = int(float(t.get("Hold_Days", 0)))
            if hold > 0:
                hold_times.append(hold)
        except:
            pass
    avg_hold = sum(hold_times) / len(hold_times) if hold_times else 0

    # Update account
    account["realized_pl"] = round(realized_pl, 2)
    account["total_trades"] = total_trades
    account["cash_available"] = round(cash_available, 2)
    account["positions_value"] = round(positions_value, 2)
    account["account_value"] = round(account_value, 2)
    account["win_rate_percent"] = round(win_rate, 1)
    account["average_winner_percent"] = round(avg_winner, 2)
    account["average_loser_percent"] = round(avg_loser, 2)
    account["average_hold_time_days"] = round(avg_hold, 1)
    account["last_updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Save
    with open(account_path, "w") as f:
        json.dump(account, f, indent=2)

    print("\nAfter:")
    print(f"  realized_pl: ${account['realized_pl']:.2f}")
    print(f"  account_value: ${account['account_value']:.2f}")
    print(f"  cash_available: ${account['cash_available']:.2f}")
    print(f"  positions_value: ${account['positions_value']:.2f}")
    print(f"  total_trades: {account['total_trades']}")
    print(f"  win_rate: {account['win_rate_percent']}%")
    print(f"  avg_winner: +{account['average_winner_percent']}%")
    print(f"  avg_loser: {account['average_loser_percent']}%")
    print(f"  avg_hold: {account['average_hold_time_days']} days")

if __name__ == "__main__":
    update_account()
