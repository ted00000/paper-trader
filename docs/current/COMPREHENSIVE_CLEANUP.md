# Comprehensive Repository Cleanup Plan

**Date**: January 2, 2026
**Current State**: 178 total files in root (completely disorganized)
**Goal**: Clean, professional repository structure

---

## Current Mess

### Files in Root Directory
- **71 markdown docs** (outdated audits, plans, guides)
- **23 Python test files** (old validation scripts)
- **20 shell scripts** (mix of active and obsolete)
- **13 text files** (old audit reports, crontab backups, screener output)
- **10 miscellaneous** (logo images, nginx configs, credentials)
- **2 JSON files** (screener output, universe tickers)

**Total chaos**: 178 files scattered everywhere

---

## Proposed Clean Structure

```
paper_trading_lab/
├── Core Documentation (5 files)
│   ├── README.md
│   ├── TEDBOT_OVERVIEW.md
│   ├── CRON_SCHEDULE.md
│   ├── PARKING_LOT.md
│   └── tedbot_v_7_external_review.md
│
├── Core Python Scripts (4 files)
│   ├── agent_v5.5.py
│   ├── market_screener.py
│   ├── learn_daily.py
│   ├── learn_weekly.py
│   ├── learn_monthly.py
│   └── update_near_miss_returns.py
│
├── Active Shell Scripts (7 files)
│   ├── run_screener.sh
│   ├── run_go.sh
│   ├── run_execute.sh
│   ├── run_analyze.sh
│   ├── run_near_miss_updater.sh
│   ├── start_dashboard.sh
│   └── verify_system.sh
│
├── Config Files (5 files)
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── requirements.txt
│   └── requirements_dashboard.txt
│
├── docs/
│   ├── current/                    # Active reference (5 files)
│   │   ├── DEPLOYMENT.md
│   │   ├── DASHBOARD_SETUP.md
│   │   ├── LEARNING_SYSTEM_AUDIT.md
│   │   ├── QUICK_REFERENCE.md
│   │   └── SYSTEM_VALIDATION_CHECKLIST.md
│   │
│   └── archive/                    # Historical documentation
│       ├── 2024-10/               # October docs
│       ├── 2024-11/               # November docs
│       ├── 2024-12/               # December docs
│       ├── 2025-01/               # January docs
│       └── audits/                # Old audit text files
│
├── tests/                          # Test scripts
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── legacy/                    # Old test scripts
│
├── scripts/                        # Utility scripts
│   ├── deployment/                # Deployment scripts
│   ├── backup/                    # Backup scripts
│   └── maintenance/               # Maintenance scripts
│
├── assets/                         # Static assets
│   ├── logos/                     # Logo images
│   └── configs/                   # Config templates (nginx, etc.)
│
├── data/                           # Data directories (existing)
│   ├── screener_candidates.json
│   ├── universe_tickers.json
│   ├── dashboard_data/
│   ├── strategy_evolution/
│   └── daily_reviews/
│
└── logs/                           # Log files (existing)
```

---

## Cleanup Categories

### 1. Test Files → `tests/` (25 files)

**Unit Tests** (move to `tests/unit/`):
- test_technical_indicators.py
- test_vix.py
- test_trailing_stops.py
- test_dynamic_targets.py
- test_entry_timing.py
- test_stage2_alignment.py
- test_post_earnings_drift.py
- test_gap_logic.py

**Integration Tests** (move to `tests/integration/`):
- test_alpaca_integration.py
- test_screener_quick.py
- test_enhanced_screener.py
- test_catalyst_detection.py
- test_insider_trading.py
- test_finnhub.py
- test_price_targets.py
- test_ba_price.py

**Legacy/Version Tests** (move to `tests/legacy/`):
- test_v2_enhancements.py
- test_v3_news_filtering.py
- test_v4_enhancements.py
- test_v5_law_firm_filter.py
- test_bug_fixes.py
- test_sector_concentration.py
- test_claude_independent_search.py
- test_cron_alpaca.sh
- ALPACA_TESTING_GUIDE.md

### 2. Shell Scripts → `scripts/` (13 obsolete)

**Keep in Root** (7 active operational scripts):
- run_screener.sh
- run_go.sh
- run_execute.sh
- run_analyze.sh
- run_near_miss_updater.sh
- start_dashboard.sh
- verify_system.sh

**Move to `scripts/deployment/`**:
- deploy_dashboard_v2.sh
- deploy_v4.3.sh
- add_admin_to_nginx.sh
- init_data_files.sh

**Move to `scripts/backup/`**:
- backup_crontab.sh
- backup_daily_offsite.sh
- backup_hourly.sh
- backup_monitor.sh
- restore_from_backup.sh

**Move to `scripts/maintenance/`**:
- cleanup_repo.sh
- fix_cat_trade.sh
- reset_data.sh
- setup_monitoring.sh

### 3. Text Files → `docs/archive/audits/` (13 files)

**Old Audit Reports**:
- Comprehensive_Third_Party_Audit_Dec _17.txt
- Comprehensive_Third_Party_Audit_Dec_18.txt
- Third Party Screener Audit 29 Dec 2025.txt
- market screener audit 30 dec 25.txt
- market screener audit 31 Dec 2025.txt
- market screener audit recommendations 30 dec 25.txt

**Crontab Backups**:
- complete_crontab.txt
- crontab_current.txt
- crontab_v4.3.txt

**Screener Output Logs**:
- screener_output.txt
- screener_output_fixed.txt

**Keep in Root**:
- requirements.txt
- requirements_dashboard.txt

### 4. Miscellaneous → `assets/` (10 files)

**Move to `assets/logos/`**:
- TedBotLogo.jpg
- Tedbot Logo 2.jpg
- Tedbot Logo 3.png
- Tedbot.PNG

**Move to `assets/configs/`**:
- nginx_admin_config.conf
- trading-dashboard.nginx.conf
- dashboard.html

**Keep in Root** (hidden config):
- .dashboard_credentials
- .secret_key
- .env.example

### 5. Data Files → `data/` (2 files)

**Move to `data/`**:
- screener_candidates.json
- universe_tickers.json

---

## Execution Priority

### Phase 1: Critical Cleanup (Do First)
1. Create directory structure
2. Move test files to `tests/`
3. Move shell scripts to `scripts/`
4. Move text files to `docs/archive/audits/`

### Phase 2: Documentation (After Phase 1)
5. Move markdown docs to `docs/current/` and `docs/archive/`
6. Move miscellaneous files to `assets/`
7. Move data files to `data/`

### Phase 3: Final Touches
8. Update .gitignore to exclude `docs/archive/`, `tests/legacy/`
9. Create README.md files in each subdirectory
10. Commit and push

---

## Expected Result

**Root Directory** will contain ONLY:
- 5 core markdown docs (README, OVERVIEW, CRON, PARKING_LOT, external review)
- 6 core Python scripts (agent, screener, learners, near-miss updater)
- 7 operational shell scripts (run_*, start_*, verify_*)
- 5 config files (.env, .env.example, .gitignore, requirements.txt, requirements_dashboard.txt)
- Hidden credential files (.dashboard_credentials, .secret_key)

**Total in root: ~24 files** (down from 178)

All other files organized into:
- `docs/` - Documentation
- `tests/` - Test scripts
- `scripts/` - Utility scripts
- `assets/` - Static assets
- `data/` - Data files
- `logs/` - Log files (existing)
- `dashboard_data/` - Dashboard data (existing)
- `strategy_evolution/` - Learning data (existing)
- `daily_reviews/` - Historical decisions (existing)

---

## Benefits

1. **Professional Structure**: Repository looks like a real software project
2. **Easy Navigation**: Find files instantly instead of scrolling through 178 files
3. **Clear Separation**: Operational vs historical, active vs legacy
4. **Maintainable**: New files have obvious homes
5. **Git Efficient**: Can exclude archive/test directories from syncing
