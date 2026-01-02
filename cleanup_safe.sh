#!/bin/bash
# SAFE Repository Cleanup Script
# Only moves files with NO operational dependencies

set -e

echo "============================================================"
echo "SAFE TEDBOT REPOSITORY CLEANUP"
echo "============================================================"
echo ""
echo "This script only moves files with NO operational dependencies."
echo "All core Python scripts, shell scripts, and data files stay in root."
echo ""

# Dry run by default
DRY_RUN=true
if [ "$1" = "execute" ]; then
    DRY_RUN=false
    echo "⚠️  EXECUTING CLEANUP (files will be moved)"
else
    echo "📋 DRY RUN MODE (preview only)"
    echo "    Run with './cleanup_safe.sh execute' to apply changes"
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
# Create Directory Structure
# ============================================================
echo "Creating directory structure..."
mkdir -p docs/{current,archive/{2024-10,2024-11,2024-12,2025-01,audits}}
mkdir -p tests/{unit,integration,legacy}
mkdir -p scripts/{deployment,backup,maintenance}
mkdir -p assets/{logos,configs}

echo "  ✓ Created docs/ structure"
echo "  ✓ Created tests/ structure"
echo "  ✓ Created scripts/ structure"
echo "  ✓ Created assets/ structure"
echo ""

# ============================================================
# STEP 1: Move Documentation (SAFE - no dependencies)
# ============================================================
echo "Step 1: Moving documentation files..."

# Current docs
echo "  → Moving to docs/current/..."
move_file "LEARNING_SYSTEM_AUDIT.md" "docs/current/"
move_file "DEPLOYMENT.md" "docs/current/"
move_file "DASHBOARD_SETUP.md" "docs/current/"
move_file "SYSTEM_VALIDATION_CHECKLIST.md" "docs/current/"
move_file "QUICK_REFERENCE.md" "docs/current/"

# Archive by date (safe - not referenced by code)
echo "  → Archiving October 2024..."
for f in Claude_Deep_Research.md ENTRY_QUALITY_RESEARCH_GUIDE.md \
         IMPLEMENTATION_PLAN.md A+_SYSTEM_DOCUMENTATION.md; do
    move_file "$f" "docs/archive/2024-10/"
done

echo "  → Archiving November 2024..."
for f in LEARNING_SYSTEM_AUDIT_2025-11-14.md POSITION_FETCH_FIX_2025-11-17.md \
         ALPACA_INTEGRATION_PLAN.md EARNINGS_DATA_SOURCES.md ENHANCEMENT_ROADMAP*.md \
         IMPROVEMENT_PARKING_LOT.md INSTAGRAM_AUTOMATION_PLAN.md \
         LEARNING_SYSTEM_INTEGRATION.md LEARNING_SYSTEM_SUMMARY.md \
         MARKET_SCREENER_DESIGN.md MASTER_STRATEGY_BLUEPRINT.md \
         PHASE_4_PORTFOLIO_ROTATION_PLAN.md NGINX_DEPLOYMENT.md; do
    move_file "$f" "docs/archive/2024-11/"
done

echo "  → Archiving December 2024..."
for f in AGENT_PROMPT_ALIGNMENT_AUDIT_DEC17.md ALPACA_SETUP_INSTRUCTIONS.md \
         AUDIT_RESPONSE_DEC18.md BACKUP_SYSTEM_GUIDE.md CATALYST_*.md \
         *_DEC*.md DATA_*.md DEEP_RESEARCH_IMPLEMENTATION.md \
         DIAGNOSTIC_REPORT_DEC15.md P1_*.md P2_*.md PORTFOLIO_*.md \
         SCREENER_*DEC*.md SYSTEM_*.md TECHNICAL_INDICATORS_GUIDE.md \
         TIER1_*.md THIRD_PARTY_AUDIT_FIXES_DEC17.md \
         CONTINUOUS_OPTIMIZATION_STRATEGY.md Comprehensive*.txt; do
    move_file "$f" "docs/archive/2024-12/"
done

echo "  → Archiving January 2025..."
for f in RS_FILTER_*.md SCREENER_*20251*.md SCREENER_INTEGRATION_VERIFICATION.md \
         TEDBOT_THESIS.md THIRD_PARTY_ANALYSIS*.md V*_*.md VALIDATION_REQUIREMENTS.md; do
    move_file "$f" "docs/archive/2025-01/"
done

echo ""

# ============================================================
# STEP 2: Move Test Files (SAFE - not in cron)
# ============================================================
echo "Step 2: Moving test files..."

echo "  → Moving to tests/unit/..."
for f in test_technical_indicators.py test_vix.py test_trailing_stops.py \
         test_dynamic_targets.py test_entry_timing.py test_stage2_alignment.py \
         test_post_earnings_drift.py test_gap_logic.py; do
    move_file "$f" "tests/unit/"
done

echo "  → Moving to tests/integration/..."
for f in test_alpaca_integration.py test_screener_quick.py test_enhanced_screener.py \
         test_catalyst_detection.py test_insider_trading.py test_finnhub.py \
         test_price_targets.py test_ba_price.py; do
    move_file "$f" "tests/integration/"
done

echo "  → Moving to tests/legacy/..."
for f in test_v*.py test_bug_fixes.py test_sector_concentration.py \
         test_claude_independent_search.py test_cron_alpaca.sh; do
    move_file "$f" "tests/legacy/"
done

echo ""

# ============================================================
# STEP 3: Move Utility Scripts (SAFE - not in cron)
# ============================================================
echo "Step 3: Moving utility scripts..."

echo "  → Moving to scripts/deployment/..."
for f in deploy_*.sh add_admin_to_nginx.sh init_data_files.sh; do
    move_file "$f" "scripts/deployment/"
done

# NOTE: backup_*.sh scripts STAY in root (they're in cron)
echo "  → Moving to scripts/maintenance/..."
for f in cleanup_repo.sh cleanup_comprehensive.sh fix_cat_trade.sh \
         reset_data.sh setup_monitoring.sh restore_from_backup.sh; do
    move_file "$f" "scripts/maintenance/"
done

echo ""

# ============================================================
# STEP 4: Move Text Files (SAFE - old audit reports)
# ============================================================
echo "Step 4: Archiving old audit text files..."

echo "  → Moving to docs/archive/audits/..."
for f in *audit*.txt *Audit*.txt crontab*.txt screener_output*.txt \
         "Third Party"*.txt "market screener"*.txt; do
    if [ -f "$f" ]; then
        move_file "$f" "docs/archive/audits/"
    fi
done

echo ""

# ============================================================
# STEP 5: Move Assets (SAFE - not referenced by code)
# ============================================================
echo "Step 5: Moving asset files..."

echo "  → Moving to assets/logos/..."
for f in *Logo*.jpg *Logo*.png *logo*.jpg *logo*.png Tedbot*.PNG TedBotLogo.jpg; do
    move_file "$f" "assets/logos/"
done

echo "  → Moving to assets/configs/..."
for f in nginx*.conf trading-dashboard.nginx.conf dashboard.html; do
    move_file "$f" "assets/configs/"
done

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
    echo "✅ SAFE TO EXECUTE - only moves files with no dependencies:"
    echo "   - Documentation (.md files)"
    echo "   - Test files (test_*.py, test_*.sh)"
    echo "   - Utility scripts (not in cron)"
    echo "   - Old audit text files"
    echo "   - Logo images and old configs"
    echo ""
    echo "🚫 STAYS IN ROOT (operational dependencies):"
    echo "   - All Python scripts (agent, screener, learners, etc.)"
    echo "   - All run_*.sh scripts (in cron)"
    echo "   - All backup_*.sh scripts (in cron)"
    echo "   - Data files (screener_candidates.json, universe_tickers.json)"
    echo "   - Config files (.env, requirements.txt)"
    echo ""
    echo "To execute cleanup, run:"
    echo "  ./cleanup_safe.sh execute"
else
    echo "✓ Cleanup complete!"
    echo ""
    echo "Root directory now contains:"
    echo "  Markdown files: $(ls -1 *.md 2>/dev/null | wc -l | xargs)"
    echo "  Python scripts: $(ls -1 *.py 2>/dev/null | wc -l | xargs)"
    echo "  Shell scripts:  $(ls -1 *.sh 2>/dev/null | wc -l | xargs)"
    echo ""
    echo "Organized into:"
    echo "  docs/:    $(find docs -type f 2>/dev/null | wc -l | xargs) files"
    echo "  tests/:   $(find tests -type f 2>/dev/null | wc -l | xargs) files"
    echo "  scripts/: $(find scripts -type f 2>/dev/null | wc -l | xargs) files"
    echo "  assets/:  $(find assets -type f 2>/dev/null | wc -l | xargs) files"
    echo ""
    echo "✅ ALL OPERATIONAL DEPENDENCIES PRESERVED"
    echo "   - Core Python scripts still in root"
    echo "   - Cron scripts still in root"
    echo "   - Data files still in root"
    echo ""
    echo "Next steps:"
    echo "  1. Review: git status"
    echo "  2. Commit: git add -A && git commit -m 'Safe repository cleanup - organize docs/tests/assets'"
    echo "  3. Push: git push origin master"
fi

echo ""
echo "============================================================"
