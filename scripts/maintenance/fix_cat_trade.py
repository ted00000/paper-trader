#!/usr/bin/env python3
"""Fix CAT trade exit reason in CSV"""

import csv
import shutil
from pathlib import Path

CSV_FILE = Path('trade_history/completed_trades.csv')
BACKUP_FILE = Path('trade_history/completed_trades.csv.backup')

print("Fixing CAT trade exit reason...")

# Create backup
shutil.copy(CSV_FILE, BACKUP_FILE)
print(f"✓ Created backup: {BACKUP_FILE}")

# Read all rows
rows = []
with open(CSV_FILE, 'r', newline='') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    for row in reader:
        # Fix CAT trade
        if row.get('Ticker') == 'CAT' and 'PARTIAL EXIT' in row.get('Exit_Reason', ''):
            old_reason = row['Exit_Reason']
            row['Exit_Reason'] = 'Target reached (+11.6%)'
            print(f"✓ Updated CAT exit reason")
            print(f"  Old: {old_reason[:60]}...")
            print(f"  New: {row['Exit_Reason']}")

        rows.append(row)

# Write back
with open(CSV_FILE, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\n✓ Successfully updated {CSV_FILE}")
print("\nTo verify:")
print(f"  tail -1 {CSV_FILE}")
print("\nIf something went wrong, restore from backup:")
print(f"  cp {BACKUP_FILE} {CSV_FILE}")
