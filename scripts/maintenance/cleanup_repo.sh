#!/bin/bash
# Repository Cleanup Script
# Organizes documentation into clean structure

set -e

echo "============================================================"
echo "TEDBOT REPOSITORY CLEANUP"
echo "============================================================"
echo ""

# Dry run by default, pass "execute" to actually move files
DRY_RUN=true
if [ "$1" = "execute" ]; then
    DRY_RUN=false
    echo "⚠️  EXECUTING CLEANUP (files will be moved)"
else
    echo "📋 DRY RUN MODE (preview only)"
    echo "    Run with './cleanup_repo.sh execute' to apply changes"
fi
echo ""

# Create directory structure
echo "Creating directory structure..."
mkdir -p docs/{current,archive/{2024-10,2024-11,2024-12,2025-01}}
echo "  ✓ Created docs/current/"
echo "  ✓ Created docs/archive/2024-{10,11,12}/"
echo "  ✓ Created docs/archive/2025-01/"
echo ""

# Helper function to move files
move_file() {
    local file="$1"
    local dest="$2"

    if [ ! -f "$file" ]; then
        return
    fi

    if $DRY_RUN; then
        echo "  [DRY RUN] Would move: $file → $dest"
    else
        mv "$file" "$dest" && echo "  ✓ Moved: $file → $dest"
    fi
}

# STEP 1: Move to docs/current/
echo "Moving active reference docs to docs/current/..."
move_file "LEARNING_SYSTEM_AUDIT.md" "docs/current/"
move_file "DEPLOYMENT.md" "docs/current/"
move_file "DASHBOARD_SETUP.md" "docs/current/"
move_file "SYSTEM_VALIDATION_CHECKLIST.md" "docs/current/"
move_file "QUICK_REFERENCE.md" "docs/current/"
echo ""

# STEP 2: Archive October 2024
echo "Archiving October 2024 docs..."
move_file "Claude_Deep_Research.md" "docs/archive/2024-10/"
move_file "ENTRY_QUALITY_RESEARCH_GUIDE.md" "docs/archive/2024-10/"
move_file "IMPLEMENTATION_PLAN.md" "docs/archive/2024-10/"
move_file "A+_SYSTEM_DOCUMENTATION.md" "docs/archive/2024-10/"
echo ""

# STEP 3: Archive November 2024
echo "Archiving November 2024 docs..."
move_file "LEARNING_SYSTEM_AUDIT_2025-11-14.md" "docs/archive/2024-11/"
move_file "POSITION_FETCH_FIX_2025-11-17.md" "docs/archive/2024-11/"
move_file "ALPACA_INTEGRATION_PLAN.md" "docs/archive/2024-11/"
move_file "EARNINGS_DATA_SOURCES.md" "docs/archive/2024-11/"
move_file "ENHANCEMENT_ROADMAP.md" "docs/archive/2024-11/"
move_file "ENHANCEMENT_ROADMAP_V2.md" "docs/archive/2024-11/"
move_file "ENHANCEMENT_ROADMAP_V3.md" "docs/archive/2024-11/"
move_file "IMPROVEMENT_PARKING_LOT.md" "docs/archive/2024-11/"
move_file "INSTAGRAM_AUTOMATION_PLAN.md" "docs/archive/2024-11/"
move_file "LEARNING_SYSTEM_INTEGRATION.md" "docs/archive/2024-11/"
move_file "LEARNING_SYSTEM_SUMMARY.md" "docs/archive/2024-11/"
move_file "MARKET_SCREENER_DESIGN.md" "docs/archive/2024-11/"
move_file "MASTER_STRATEGY_BLUEPRINT.md" "docs/archive/2024-11/"
move_file "PHASE_4_PORTFOLIO_ROTATION_PLAN.md" "docs/archive/2024-11/"
move_file "NGINX_DEPLOYMENT.md" "docs/archive/2024-11/"
echo ""

# STEP 4: Archive December 2024
echo "Archiving December 2024 docs..."
move_file "AGENT_PROMPT_ALIGNMENT_AUDIT_DEC17.md" "docs/archive/2024-12/"
move_file "ALPACA_SETUP_INSTRUCTIONS.md" "docs/archive/2024-12/"
move_file "ALPACA_TESTING_GUIDE.md" "docs/archive/2024-12/"
move_file "AUDIT_RESPONSE_DEC18.md" "docs/archive/2024-12/"
move_file "BACKUP_SYSTEM_GUIDE.md" "docs/archive/2024-12/"
move_file "CATALYST_AUDIT.md" "docs/archive/2024-12/"
move_file "CATALYST_COVERAGE_STATUS_DEC19.md" "docs/archive/2024-12/"
move_file "CONTINUOUS_OPTIMIZATION_STRATEGY.md" "docs/archive/2024-12/"
move_file "DATA_INTEGRITY_GUIDE.md" "docs/archive/2024-12/"
move_file "DATA_SOURCES_AUDIT_DEC17.md" "docs/archive/2024-12/"
move_file "DEEP_RESEARCH_IMPLEMENTATION.md" "docs/archive/2024-12/"
move_file "DIAGNOSTIC_REPORT_DEC15.md" "docs/archive/2024-12/"
move_file "P1_AUDIT_REPORT_DEC23.md" "docs/archive/2024-12/"
move_file "P2_COMPLETION_REPORT_DEC23.md" "docs/archive/2024-12/"
move_file "PORTFOLIO_STRATEGY_ALIGNMENT_DEC17.md" "docs/archive/2024-12/"
move_file "RS_AUDIT_COMPLETE_DEC17.md" "docs/archive/2024-12/"
move_file "SCREENER_AUDIT_DEC23.md" "docs/archive/2024-12/"
move_file "SCREENER_STATUS_DEC23.md" "docs/archive/2024-12/"
move_file "SYSTEM_AUDIT_REPORT_v6.0.md" "docs/archive/2024-12/"
move_file "SYSTEM_CONSISTENCY_AUDIT_DEC17.md" "docs/archive/2024-12/"
move_file "SYSTEM_OPERATIONS_GUIDE.md" "docs/archive/2024-12/"
move_file "TECHNICAL_INDICATORS_GUIDE.md" "docs/archive/2024-12/"
move_file "THIRD_PARTY_AUDIT_FIXES_DEC17.md" "docs/archive/2024-12/"
move_file "TIER1_COMPLETE_DEC19.md" "docs/archive/2024-12/"
move_file "TIER1_UPGRADE_DEC19.md" "docs/archive/2024-12/"
move_file "Comprehensive_Third_Party_Audit_Dec _17.txt" "docs/archive/2024-12/"
move_file "Comprehensive_Third_Party_Audit_Dec_18.txt" "docs/archive/2024-12/"
echo ""

# STEP 5: Archive January 2025
echo "Archiving January 2025 docs..."
move_file "RS_FILTER_DIAGNOSIS.md" "docs/archive/2025-01/"
move_file "RS_FILTER_POSTMORTEM.md" "docs/archive/2025-01/"
move_file "SCREENER_AUDIT_20251229.md" "docs/archive/2025-01/"
move_file "SCREENER_FIXES_20251229.md" "docs/archive/2025-01/"
move_file "SCREENER_IMPLEMENTATION_SUMMARY.md" "docs/archive/2025-01/"
move_file "SCREENER_INTEGRATION_VERIFICATION.md" "docs/archive/2025-01/"
move_file "TEDBOT_THESIS.md" "docs/archive/2025-01/"
move_file "THIRD_PARTY_ANALYSIS_SUMMARY.md" "docs/archive/2025-01/"
move_file "THIRD_PARTY_ANALYSIS_v6.0.md" "docs/archive/2025-01/"
move_file "V5_DEPLOYMENT_GUIDE.md" "docs/archive/2025-01/"
move_file "V5_UPGRADE_SPEC.md" "docs/archive/2025-01/"
move_file "V6.0_DEPLOYMENT_SUMMARY.md" "docs/archive/2025-01/"
move_file "V7.0_IMPLEMENTATION.md" "docs/archive/2025-01/"
move_file "V7.1_VALIDATION_IMPROVEMENTS.md" "docs/archive/2025-01/"
move_file "VALIDATION_REQUIREMENTS.md" "docs/archive/2025-01/"
move_file "market screener audit 31 Dec 2025.txt" "docs/archive/2025-01/"
echo ""

# Summary
echo "============================================================"
echo "CLEANUP SUMMARY"
echo "============================================================"
echo ""

if $DRY_RUN; then
    echo "This was a DRY RUN. No files were moved."
    echo ""
    echo "To execute cleanup, run:"
    echo "  ./cleanup_repo.sh execute"
else
    echo "✓ Cleanup complete!"
    echo ""
    echo "Files remaining in root:"
    ls -1 *.md 2>/dev/null | wc -l | xargs echo "  "
    echo ""
    echo "Organized documentation:"
    find docs -type f -name "*.md" | wc -l | xargs echo "  docs/ contains:"
    echo ""
    echo "Next steps:"
    echo "  1. Review the changes"
    echo "  2. Commit with: git add -A && git commit -m 'Clean up repository documentation'"
    echo "  3. Push with: git push origin master"
fi

echo ""
echo "============================================================"
