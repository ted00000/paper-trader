#!/usr/bin/env python3
"""
Migrate completed_trades.csv from old format to new format with Phase 2/3 columns
"""
import csv
import shutil
from pathlib import Path
from datetime import datetime

# File paths
csv_file = Path('/root/paper_trading_lab/trade_history/completed_trades.csv')
backup_file = Path(f'/root/paper_trading_lab/trade_history/completed_trades_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

# Old header (23 columns)
OLD_HEADER = [
    'Trade_ID', 'Entry_Date', 'Exit_Date', 'Ticker',
    'Premarket_Price', 'Entry_Price', 'Exit_Price', 'Gap_Percent',
    'Shares', 'Position_Size', 'Hold_Days', 'Return_Percent', 'Return_Dollars',
    'Exit_Reason', 'Catalyst_Type', 'Sector',
    'Confidence_Level', 'Stop_Loss', 'Price_Target',
    'Thesis', 'What_Worked', 'What_Failed', 'Account_Value_After'
]

# New header (33 columns)
NEW_HEADER = [
    'Trade_ID', 'Entry_Date', 'Exit_Date', 'Ticker',
    'Premarket_Price', 'Entry_Price', 'Exit_Price', 'Gap_Percent',
    'Shares', 'Position_Size', 'Position_Size_Percent', 'Hold_Days', 'Return_Percent', 'Return_Dollars',
    'Exit_Reason', 'Catalyst_Type', 'Catalyst_Tier', 'Catalyst_Age_Days',
    'News_Validation_Score', 'News_Exit_Triggered',
    'VIX_At_Entry', 'Market_Regime', 'Macro_Event_Near',
    'Relative_Strength', 'Stock_Return_3M', 'Sector_ETF',
    'Conviction_Level', 'Supporting_Factors',
    'Sector', 'Stop_Loss', 'Price_Target',
    'Thesis', 'What_Worked', 'What_Failed', 'Account_Value_After'
]

# Column mapping from old index to new index
OLD_TO_NEW_MAPPING = {
    0: 0,   # Trade_ID
    1: 1,   # Entry_Date
    2: 2,   # Exit_Date
    3: 3,   # Ticker
    4: 4,   # Premarket_Price
    5: 5,   # Entry_Price
    6: 6,   # Exit_Price
    7: 7,   # Gap_Percent
    8: 8,   # Shares
    9: 9,   # Position_Size
    # Position_Size_Percent (10) - NEW, default to 0
    10: 11,  # Hold_Days
    11: 12,  # Return_Percent
    12: 13,  # Return_Dollars
    13: 14,  # Exit_Reason
    14: 15,  # Catalyst_Type
    # Catalyst_Tier (16) - NEW, default to "Unknown"
    # Catalyst_Age_Days (17) - NEW, default to 0
    # News_Validation_Score (18) - NEW, default to 0
    # News_Exit_Triggered (19) - NEW, default to False
    # VIX_At_Entry (20) - NEW, default to 0.0
    # Market_Regime (21) - NEW, default to "Unknown"
    # Macro_Event_Near (22) - NEW, default to "None"
    # Relative_Strength (23) - NEW, default to 0.0
    # Stock_Return_3M (24) - NEW, default to 0.0
    # Sector_ETF (25) - NEW, default to "Unknown"
    # Conviction_Level (26) - NEW, default to "MEDIUM"
    # Supporting_Factors (27) - NEW, default to 0
    15: 28,  # Sector
    16: 26,  # Confidence_Level -> Conviction_Level
    17: 29,  # Stop_Loss
    18: 30,  # Price_Target
    19: 31,  # Thesis
    20: 32,  # What_Worked
    21: 33,  # What_Failed
    22: 34,  # Account_Value_After
}

def migrate_csv():
    """Migrate CSV from old format to new format"""

    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_file}")
        return False

    # Backup original
    print(f"📦 Creating backup: {backup_file}")
    shutil.copy2(csv_file, backup_file)

    # Read old data
    print(f"📖 Reading old CSV format...")
    old_rows = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        print(f"   Old header: {len(header)} columns")

        for row in reader:
            old_rows.append(row)

    print(f"   Found {len(old_rows)} trades to migrate")

    # Write new format
    print(f"✍️  Writing new CSV format...")
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Write new header
        writer.writerow(NEW_HEADER)

        # Write migrated rows
        for old_row in old_rows:
            new_row = [''] * len(NEW_HEADER)

            # Map old columns to new positions
            for old_idx, new_idx in OLD_TO_NEW_MAPPING.items():
                if old_idx < len(old_row):
                    new_row[new_idx] = old_row[old_idx]

            # Fill in defaults for new columns
            new_row[10] = 0  # Position_Size_Percent
            new_row[16] = 'Unknown'  # Catalyst_Tier
            new_row[17] = 0  # Catalyst_Age_Days
            new_row[18] = 0  # News_Validation_Score
            new_row[19] = False  # News_Exit_Triggered
            new_row[20] = 0.0  # VIX_At_Entry
            new_row[21] = 'Unknown'  # Market_Regime
            new_row[22] = 'None'  # Macro_Event_Near
            new_row[23] = 0.0  # Relative_Strength
            new_row[24] = 0.0  # Stock_Return_3M
            new_row[25] = 'Unknown'  # Sector_ETF
            new_row[27] = 0  # Supporting_Factors

            writer.writerow(new_row)

    print(f"✅ Migration complete!")
    print(f"   New header: {len(NEW_HEADER)} columns")
    print(f"   Migrated: {len(old_rows)} trades")
    print(f"   Backup saved to: {backup_file}")
    return True

if __name__ == '__main__':
    print("=" * 70)
    print("CSV FORMAT MIGRATION - OLD (23 cols) → NEW (33 cols)")
    print("=" * 70)
    print()

    success = migrate_csv()

    print()
    print("=" * 70)
    if success:
        print("✅ MIGRATION SUCCESSFUL")
    else:
        print("❌ MIGRATION FAILED")
    print("=" * 70)
