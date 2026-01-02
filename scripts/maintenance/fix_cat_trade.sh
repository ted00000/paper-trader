#!/bin/bash
# Fix CAT trade exit reason in completed_trades.csv

CSV_FILE="trade_history/completed_trades.csv"

echo "Fixing CAT trade exit reason..."

# Create backup
cp "$CSV_FILE" "${CSV_FILE}.backup"
echo "✓ Created backup: ${CSV_FILE}.backup"

# Fix the exit reason for CAT trade
# Old: "PARTIAL EXIT (50%) - Price target hit at +11.6% (target was +10%). Selling half to lock gains, trailing stop on remaining 50% at $556.22 per profit target rules."
# New: "Target reached (+11.6%)"

sed -i.tmp 's|"PARTIAL EXIT (50%) - Price target hit at +11.6% (target was +10%). Selling half to lock gains.*"$|Target reached (+11.6%)|' "$CSV_FILE"

# Remove sed temp file
rm -f "${CSV_FILE}.tmp"

echo "✓ Updated CAT exit reason to: Target reached (+11.6%)"
echo ""
echo "To verify the change:"
echo "  tail -1 $CSV_FILE"
echo ""
echo "If something went wrong, restore from backup:"
echo "  cp ${CSV_FILE}.backup $CSV_FILE"
