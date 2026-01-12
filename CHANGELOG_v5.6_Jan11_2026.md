# Agent v5.6 - Soft Guard Rails (Jan 11, 2026)

## Critical Update: Zero Position Entry Fix

### Problem Diagnosed
- System ran Jan 6-9 with 100% rejection rate
- 16 stocks recommended by Claude → 16 rejected by guard rails → 0 positions entered
- Root cause: Architectural conflict between screener (finds momentum) and guard rails (reject momentum)

### Solution Implemented
**Converted technical guard rails from HARD BLOCKS to SOFT FLAGS**

### Changes Made (agent_v5.5.py)

#### 1. Technical Filters (Lines 5606-5619)
**Before**: Rejected stocks failing technical filters (50-MA, EMA cross, ADX, volume)
**After**: Logs risk flags but allows entry
```
⚠️ Technical risk flag: Below 50-day MA
```

#### 2. Stage 2 Alignment (Lines 5621-5637)
**Before**: Rejected stocks not in Minervini Stage 2
**After**: Logs risk flags but allows entry
```
⚠️ Stage 2 risk flag: Not in Stage 2 (3/5 checks passed)
```

#### 3. Entry Timing (Lines 5639-5658)
**Before**: Rejected stocks with RSI >70, extended >5%, or 3-day return >10%
**After**: Logs risk flags but allows entry
```
⚠️ Entry Timing risk flag: RSI 77 (overbought), Extended 119% in 3 days
```

### What Still HARD BLOCKS (Catastrophic Only)
✅ VIX shutdown (≥35)
✅ Macro blackout (FOMC, CPI)
✅ Tier 3 catalysts
✅ Stock halted/delisted
✅ Liquidity collapse

### Risk Flags Stored in Position Data
All risk flags saved to `buy_pos['risk_flags']` array for learning:
- `technical: Below 50-day MA`
- `stage2: Not in Stage 2`
- `entry_timing: RSI 77 (overbought), Extended 119%`

Forward return updater will analyze if these flags correlate with worse outcomes.

### Version Identification
- Header updated: "Agent v5.6 - SOFT GUARD RAILS (CATALYST MOMENTUM OPTIMIZED)"
- GO command logs: "Agent v5.6 - SOFT GUARD RAILS (Catalyst Momentum Optimized)"
- Backup created: `agent_v5.5_backup_jan11.py`

### Expected Outcomes (2-Week Test)
1. **Entry count**: 3-8 Tier 1 positions (vs 0 currently)
2. **Risk flags logged**: All technical concerns documented
3. **Learning enabled**: Forward return analysis shows if flags are protective
4. **Claude's judgment tested**: Does catalyst quality override technical heat?

### Monitoring Instructions
1. Check daily GO logs for risk flag patterns
2. Review `pending_positions.json` to see which stocks entered with flags
3. After 2 weeks, analyze closed_trades.csv for correlation:
   - Do high_rsi flags predict losses?
   - Do subpar_volume flags predict failures?
   - Are thresholds (RSI 70, volume 1.5x) correct?

### Rollback Plan
If outcomes are catastrophic (>80% loss rate):
- Restore from `agent_v5.5_backup_jan11.py`
- Selectively re-enable specific hard blocks based on data

### Third-Party Validation
External review confirmed:
- ✅ Root cause diagnosis correct
- ✅ Zero-entry outcome is deterministic incompatibility, not bug
- ✅ Solution: Reclassify guard rails from veto to risk context
- ✅ One layer should decide eligibility (Claude), others inform risk

### Philosophy Change
**Before**: "Find catalyst momentum, then reject if too hot"
**After**: "Find catalyst momentum, log concerns, trust Claude's judgment"

The system now operates coherently: screener finds what it's designed to find, Claude makes final call with full context, guard rails inform risk but don't override strategy.
