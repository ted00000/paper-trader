#!/bin/bash
# Backup current crontab to git-tracked file
# Run this after any crontab changes to preserve in version control

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CRONTAB_FILE="crontab_current.txt"

echo "Backing up current crontab..."

# Export current crontab
crontab -l > "$CRONTAB_FILE" 2>/dev/null || {
    echo "No crontab found or crontab is empty"
    exit 1
}

# Show what was backed up
echo "✓ Crontab backed up to: $CRONTAB_FILE"
echo ""
echo "Contents:"
cat "$CRONTAB_FILE"
echo ""
echo "To commit to git:"
echo "  git add $CRONTAB_FILE"
echo "  git commit -m 'Backup crontab'"
echo "  git push"
