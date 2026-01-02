# Repository Cleanup Plan

**Date**: January 2, 2026
**Current State**: 178 files (71 markdown files in root)
**Goal**: Organized structure with 5-10 core docs in root

---

## Proposed Structure

```
paper_trading_lab/
├── README.md                           # Quick start guide
├── TEDBOT_OVERVIEW.md                  # System architecture (current)
├── CRON_SCHEDULE.md                    # Automation schedule
├── PARKING_LOT.md                      # Future work tracker
├── tedbot_v_7_external_review.md       # Latest external review
│
├── docs/
│   ├── current/                        # Active reference docs
│   │   ├── LEARNING_SYSTEM_AUDIT.md
│   │   ├── DEPLOYMENT.md
│   │   ├── DASHBOARD_SETUP.md
│   │   ├── SYSTEM_VALIDATION_CHECKLIST.md
│   │   └── QUICK_REFERENCE.md
│   │
│   └── archive/                        # Historical documentation
│       ├── 2024-10/                    # October (setup phase)
│       ├── 2024-11/                    # November (early development)
│       ├── 2024-12/                    # December (major upgrades)
│       └── 2025-01/                    # January (v10+ improvements)
│
├── strategy_evolution/                 # Learning data (existing)
├── dashboard_data/                     # Dashboard files (existing)
├── daily_reviews/                      # Historical decisions (existing)
└── logs/                               # Operational logs (existing)
```

---

## Files to KEEP in Root (5 files)

**Essential operational documentation**:

1. **README.md** - Quick start guide for the system
2. **TEDBOT_OVERVIEW.md** - Current architecture & system design (v10.1)
3. **CRON_SCHEDULE.md** - Automation schedule (screener, learning, near-miss)
4. **PARKING_LOT.md** - Future work & improvements tracker
5. **tedbot_v_7_external_review.md** - Latest consolidated external review

---

## Files to Move to `docs/current/` (5 files)

**Active reference documentation**:

1. **LEARNING_SYSTEM_AUDIT.md** - Learning touchpoints & integration status
2. **DEPLOYMENT.md** - Server deployment instructions
3. **DASHBOARD_SETUP.md** - Dashboard configuration
4. **SYSTEM_VALIDATION_CHECKLIST.md** - Pre-deployment validation steps
5. **QUICK_REFERENCE.md** - Command reference guide

---

## Files to Archive (61 files)

### docs/archive/2024-10/ (October - Initial Setup)
- Claude_Deep_Research.md
- DEPLOYMENT.md (old version)
- ENTRY_QUALITY_RESEARCH_GUIDE.md
- IMPLEMENTATION_PLAN.md
- A+_SYSTEM_DOCUMENTATION.md

### docs/archive/2024-11/ (November - Early Development)
- LEARNING_SYSTEM_AUDIT_2025-11-14.md
- POSITION_FETCH_FIX_2025-11-17.md
- ALPACA_INTEGRATION_PLAN.md
- EARNINGS_DATA_SOURCES.md
- ENHANCEMENT_ROADMAP.md
- ENHANCEMENT_ROADMAP_V2.md
- ENHANCEMENT_ROADMAP_V3.md
- IMPROVEMENT_PARKING_LOT.md
- INSTAGRAM_AUTOMATION_PLAN.md
- LEARNING_SYSTEM_INTEGRATION.md
- LEARNING_SYSTEM_SUMMARY.md
- MARKET_SCREENER_DESIGN.md
- MASTER_STRATEGY_BLUEPRINT.md
- PHASE_4_PORTFOLIO_ROTATION_PLAN.md

### docs/archive/2024-12/ (December - Major Upgrades)
- AGENT_PROMPT_ALIGNMENT_AUDIT_DEC17.md
- ALPACA_SETUP_INSTRUCTIONS.md
- ALPACA_TESTING_GUIDE.md
- AUDIT_RESPONSE_DEC18.md
- BACKUP_SYSTEM_GUIDE.md
- CATALYST_AUDIT.md
- CATALYST_COVERAGE_STATUS_DEC19.md
- CONTINUOUS_OPTIMIZATION_STRATEGY.md
- DATA_INTEGRITY_GUIDE.md
- DATA_SOURCES_AUDIT_DEC17.md
- DEEP_RESEARCH_IMPLEMENTATION.md
- DIAGNOSTIC_REPORT_DEC15.md
- P1_AUDIT_REPORT_DEC23.md
- P2_COMPLETION_REPORT_DEC23.md
- PORTFOLIO_STRATEGY_ALIGNMENT_DEC17.md
- RS_AUDIT_COMPLETE_DEC17.md
- SCREENER_AUDIT_DEC23.md
- SCREENER_STATUS_DEC23.md
- SYSTEM_AUDIT_REPORT_v6.0.md
- SYSTEM_CONSISTENCY_AUDIT_DEC17.md
- SYSTEM_OPERATIONS_GUIDE.md
- TECHNICAL_INDICATORS_GUIDE.md
- THIRD_PARTY_AUDIT_FIXES_DEC17.md
- TIER1_COMPLETE_DEC19.md
- TIER1_UPGRADE_DEC19.md
- Comprehensive_Third_Party_Audit_Dec _17.txt
- Comprehensive_Third_Party_Audit_Dec_18.txt

### docs/archive/2025-01/ (January - v10+ Improvements)
- RS_FILTER_DIAGNOSIS.md
- RS_FILTER_POSTMORTEM.md
- SCREENER_AUDIT_20251229.md
- SCREENER_FIXES_20251229.md
- SCREENER_IMPLEMENTATION_SUMMARY.md
- SCREENER_INTEGRATION_VERIFICATION.md
- TEDBOT_THESIS.md
- THIRD_PARTY_ANALYSIS_SUMMARY.md
- THIRD_PARTY_ANALYSIS_v6.0.md
- V5_DEPLOYMENT_GUIDE.md
- V5_UPGRADE_SPEC.md
- V6.0_DEPLOYMENT_SUMMARY.md
- V7.0_IMPLEMENTATION.md
- V7.1_VALIDATION_IMPROVEMENTS.md
- VALIDATION_REQUIREMENTS.md
- market screener audit 31 Dec 2025.txt

---

## Additional Cleanup

### Remove Obsolete Files
- Old .txt audit files (replaced by current reviews)
- Duplicate planning documents (merged into PARKING_LOT.md)
- Deprecated guides (functionality now in current docs)

### Update .gitignore
Add archive exclusion:
```
# Archive documentation (local reference only)
docs/archive/
```

---

## Execution Steps

1. **Create directory structure**:
   ```bash
   mkdir -p docs/{current,archive/{2024-10,2024-11,2024-12,2025-01}}
   ```

2. **Move current docs**:
   ```bash
   mv LEARNING_SYSTEM_AUDIT.md docs/current/
   mv DEPLOYMENT.md docs/current/
   mv DASHBOARD_SETUP.md docs/current/
   mv SYSTEM_VALIDATION_CHECKLIST.md docs/current/
   mv QUICK_REFERENCE.md docs/current/
   ```

3. **Archive by date** (see categories above)

4. **Git commit**:
   ```bash
   git add -A
   git commit -m "Clean up repository - organize documentation

   - Keep 5 core docs in root (README, OVERVIEW, CRON, PARKING_LOT, external review)
   - Move 5 active docs to docs/current/
   - Archive 61 historical docs by date (Oct-Jan)
   - Result: Clean root with essential operational docs only"

   git push origin master
   ```

5. **Update README.md** with new structure

---

## Result

**Before**: 71 markdown files in root (overwhelming)
**After**: 5 core docs in root + organized archive (clean)

**Root directory** will contain only:
- Essential operational docs (README, OVERVIEW, CRON, PARKING_LOT)
- Latest external review (tedbot_v_7_external_review.md)
- Python scripts (agent_v5.5.py, market_screener.py, etc.)
- Config files (.env, .gitignore, etc.)

Everything else will be organized by date or moved to `docs/current/` for active reference.
