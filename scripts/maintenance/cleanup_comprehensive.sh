#!/bin/bash
# Comprehensive Repository Cleanup Script
# Organizes ALL files (docs, tests, scripts, assets) into clean structure

set -e

echo "============================================================"
echo "COMPREHENSIVE TEDBOT REPOSITORY CLEANUP"
echo "============================================================"
echo ""

# Dry run by default
DRY_RUN=true
if [ "$1" = "execute" ]; then
    DRY_RUN=false
    echo "⚠️  EXECUTING CLEANUP (files will be moved)"
else
    echo "📋 DRY RUN MODE (preview only)"
    echo "    Run with './cleanup_comprehensive.sh execute' to apply changes"
fi
echo ""

# Helper function
move_file() {
    local file="$1"
    local dest="$2"

    if [ ! -f "$file" ]; then
        return
    fi

    if $DRY_RUN; then
        echo "  [DRY RUN] $file → $dest"
    else
        mv "$file" "$dest" && echo "  ✓ $file → $dest"
    fi
}

# ============================================================
# STEP 1: Create Directory Structure
# ============================================================
echo "Step 1: Creating directory structure..."
mkdir -p docs/{current,archive/{2024-10,2024-11,2024-12,2025-01,audits}}
mkdir -p tests/{unit,integration,legacy}
mkdir -p scripts/{deployment,backup,maintenance}
mkdir -p assets/{logos,configs}
mkdir -p data

echo "  ✓ Created docs/ (current, archive)"
echo "  ✓ Created tests/ (unit, integration, legacy)"
echo "  ✓ Created scripts/ (deployment, backup, maintenance)"
echo "  ✓ Created assets/ (logos, configs)"
echo "  ✓ Created data/"
echo ""

# ============================================================
# STEP 2: Move Documentation
# ============================================================
echo "Step 2: Moving documentation files..."

# Current docs
echo "  → Moving to docs/current/..."
move_file "LEARNING_SYSTEM_AUDIT.md" "docs/current/"
move_file "DEPLOYMENT.md" "docs/current/"
move_file "DASHBOARD_SETUP.md" "docs/current/"
move_file "SYSTEM_VALIDATION_CHECKLIST.md" "docs/current/"
move_file "QUICK_REFERENCE.md" "docs/current/"

# October archives
echo "  → Archiving October 2024..."
move_file "Claude_Deep_Research.md" "docs/archive/2024-10/"
move_file "ENTRY_QUALITY_RESEARCH_GUIDE.md" "docs/archive/2024-10/"
move_file "IMPLEMENTATION_PLAN.md" "docs/archive/2024-10/"
move_file "A+_SYSTEM_DOCUMENTATION.md" "docs/archive/2024-10/"

# November archives
echo "  → Archiving November 2024..."
for f in LEARNING_SYSTEM_AUDIT_2025-11-14.md POSITION_FETCH_FIX_2025-11-17.md \
         ALPACA_INTEGRATION_PLAN.md EARNINGS_DATA_SOURCES.md ENHANCEMENT_ROADMAP*.md \
         IMPROVEMENT_PARKING_LOT.md INSTAGRAM_AUTOMATION_PLAN.md \
         LEARNING_SYSTEM_INTEGRATION.md LEARNING_SYSTEM_SUMMARY.md \
         MARKET_SCREENER_DESIGN.md MASTER_STRATEGY_BLUEPRINT.md \
         PHASE_4_PORTFOLIO_ROTATION_PLAN.md NGINX_DEPLOYMENT.md; do
    move_file "$f" "docs/archive/2024-11/"
done

# December archives
echo "  → Archiving December 2024..."
for f in AGENT_PROMPT_ALIGNMENT_AUDIT_DEC17.md ALPACA_SETUP_INSTRUCTIONS.md \
         ALPACA_TESTING_GUIDE.md AUDIT_RESPONSE_DEC18.md BACKUP_SYSTEM_GUIDE.md \
         CATALYST_*.md *_DEC*.md *DEC*.md DATA_*.md DEEP_RESEARCH_IMPLEMENTATION.md \
         DIAGNOSTIC_REPORT_DEC15.md P1_*.md P2_*.md PORTFOLIO_*.md RS_AUDIT_*.md \
         SCREENER_AUDIT_DEC23.md SCREENER_STATUS_DEC23.md SYSTEM_*.md \
         TECHNICAL_INDICATORS_GUIDE.md TIER1_*.md Comprehensive*.txt; do
    move_file "$f" "docs/archive/2024-12/"
done

# January archives
echo "  → Archiving January 2025..."
for f in RS_FILTER_*.md SCREENER_*20251*.md SCREENER_INTEGRATION_VERIFICATION.md \
         TEDBOT_THESIS.md THIRD_PARTY_ANALYSIS*.md V*_*.md VALIDATION_REQUIREMENTS.md; do
    move_file "$f" "docs/archive/2025-01/"
done

echo ""

# ============================================================
# STEP 3: Move Test Files
# ============================================================
echo "Step 3: Moving test files..."

# Unit tests
echo "  → Moving to tests/unit/..."
for f in test_technical_indicators.py test_vix.py test_trailing_stops.py \
         test_dynamic_targets.py test_entry_timing.py test_stage2_alignment.py \
         test_post_earnings_drift.py test_gap_logic.py; do
    move_file "$f" "tests/unit/"
done

# Integration tests
echo "  → Moving to tests/integration/..."
for f in test_alpaca_integration.py test_screener_quick.py test_enhanced_screener.py \
         test_catalyst_detection.py test_insider_trading.py test_finnhub.py \
         test_price_targets.py test_ba_price.py; do
    move_file "$f" "tests/integration/"
done

# Legacy tests
echo "  → Moving to tests/legacy/..."
for f in test_v*.py test_bug_fixes.py test_sector_concentration.py \
         test_claude_independent_search.py test_cron_alpaca.sh; do
    move_file "$f" "tests/legacy/"
done

echo ""

# ============================================================
# STEP 4: Move Shell Scripts
# ============================================================
echo "Step 4: Organizing shell scripts..."

# Deployment scripts
echo "  → Moving to scripts/deployment/..."
for f in deploy_*.sh add_admin_to_nginx.sh init_data_files.sh; do
    move_file "$f" "scripts/deployment/"
done

# Backup scripts
echo "  → Moving to scripts/backup/..."
for f in backup_*.sh restore_from_backup.sh; do
    move_file "$f" "scripts/backup/"
done

# Maintenance scripts
echo "  → Moving to scripts/maintenance/..."
for f in cleanup_repo.sh fix_cat_trade.sh reset_data.sh setup_monitoring.sh; do
    move_file "$f" "scripts/maintenance/"
done

echo ""

# ============================================================
# STEP 5: Move Text Files
# ============================================================
echo "Step 5: Archiving text files..."

echo "  → Moving to docs/archive/audits/..."
for f in *.txt; do
    # Skip requirements files
    if [[ "$f" != "requirements"* ]]; then
        move_file "$f" "docs/archive/audits/"
    fi
done

echo ""

# ============================================================
# STEP 6: Move Miscellaneous Files
# ============================================================
echo "Step 6: Organizing assets..."

# Logos
echo "  → Moving to assets/logos/..."
for f in *Logo*.jpg *Logo*.png Tedbot.PNG TedBotLogo.jpg; do
    move_file "$f" "assets/logos/"
done

# Configs
echo "  → Moving to assets/configs/..."
for f in nginx*.conf dashboard.html; do
    move_file "$f" "assets/configs/"
done

echo ""

# ============================================================
# STEP 7: Move Data Files
# ============================================================
echo "Step 7: Moving data files..."

echo "  → Moving to data/..."
move_file "screener_candidates.json" "data/"
move_file "universe_tickers.json" "data/"

echo ""

# ============================================================
# SUMMARY
# ============================================================
echo "============================================================"
echo "CLEANUP SUMMARY"
echo "============================================================"
echo ""

if $DRY_RUN; then
    echo "This was a DRY RUN. No files were moved."
    echo ""
    echo "Review the plan above. To execute cleanup, run:"
    echo "  ./cleanup_comprehensive.sh execute"
else
    echo "✓ Cleanup complete!"
    echo ""
    echo "Root directory now contains:"
    echo "  Markdown files: $(ls -1 *.md 2>/dev/null | wc -l | xargs)"
    echo "  Python scripts: $(ls -1 *.py 2>/dev/null | wc -l | xargs)"
    echo "  Shell scripts:  $(ls -1 *.sh 2>/dev/null | wc -l | xargs)"
    echo ""
    echo "Organized into:"
    echo "  docs/:    $(find docs -type f | wc -l | xargs) files"
    echo "  tests/:   $(find tests -type f | wc -l | xargs) files"
    echo "  scripts/: $(find scripts -type f | wc -l | xargs) files"
    echo "  assets/:  $(find assets -type f | wc -l | xargs) files"
    echo "  data/:    $(find data -type f 2>/dev/null | wc -l | xargs) files"
    echo ""
    echo "Next steps:"
    echo "  1. Review the changes: git status"
    echo "  2. Commit: git add -A && git commit -m 'Comprehensive repository cleanup'"
    echo "  3. Push: git push origin master"
fi

echo ""
echo "============================================================"
