#!/usr/bin/env python3
"""Fix CAT trade hold_days from 0 to 1"""

import csv
from pathlib import Path
from datetime import datetime

CSV_FILE = Path('trade_history/completed_trades.csv')

print("Fixing CAT hold_days...")

# Read all rows
rows = []
with open(CSV_FILE, 'r', newline='') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    for row in reader:
        # Fix CAT trade hold_days
        if row.get('Ticker') == 'CAT':
            entry_date = datetime.strptime(row['Entry_Date'], '%Y-%m-%d')
            exit_date = datetime.strptime(row['Exit_Date'], '%Y-%m-%d')
            actual_days = (exit_date - entry_date).days

            old_days = row['Hold_Days']
            row['Hold_Days'] = str(actual_days)
            print(f"✓ Updated CAT hold_days: {old_days} → {actual_days}")

        rows.append(row)

# Write back
with open(CSV_FILE, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\n✓ Successfully updated {CSV_FILE}")
