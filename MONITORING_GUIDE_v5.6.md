# Monitoring Guide - Agent v5.6 Soft Guard Rails Test
## 2-Week Test Period: Jan 12-25, 2026

---

## What Changed in v5.6

**Before (v5.5)**: Technical guard rails BLOCKED entries
- RSI >70 → REJECT
- Extended >5% above 20-MA → REJECT
- Volume <1.5x → REJECT
- ADX <20 → REJECT
- Not Stage 2 → REJECT

**Result**: 100% rejection rate (16 recommendations, 0 positions entered)

**After (v5.6)**: Technical guard rails LOG WARNINGS only
- RSI >70 → ⚠️ Risk flag logged, entry ALLOWED
- Extended >5% → ⚠️ Risk flag logged, entry ALLOWED
- Volume <1.5x → ⚠️ Risk flag logged, entry ALLOWED
- All risk flags stored for learning

**Expected Result**: 3-8 Tier 1 positions entered per day

---

## Daily Monitoring Checklist

### 1. Morning Check (After GO Command - 8:50 AM ET)

**Check GO log for version confirmation:**
```bash
ssh root@174.138.67.26
cd /root/paper_trading_lab
tail -50 logs/go.log
```

**Look for:**
```
EXECUTING 'GO' COMMAND - PORTFOLIO REVIEW (Swing Trading)
Agent v5.6 - SOFT GUARD RAILS (Catalyst Momentum Optimized)
```

**Count risk flags vs entries:**
```bash
# Count risk flags
grep "⚠️.*risk flag" logs/go.log | wc -l

# Count BUY positions validated
grep "validated successfully" logs/go.log | wc -l
```

### 2. Market Open Check (After EXECUTE - 9:35 AM ET)

**Verify positions entered:**
```bash
cat portfolio_data/current_portfolio.json | jq '.positions | length'
```

**Expected**: 3-8 positions (vs 0 in previous week)

**Check which stocks had risk flags:**
```bash
cat portfolio_data/pending_positions.json | jq '.buy[] | select(.risk_flags != null) | {ticker, risk_flags}'
```

### 3. Dashboard Review (Daily)

**Login**: https://164.92.75.167/dashboard
**Credentials**: admin / SuperTed2025

**Check "Daily Picks" section:**
- How many stocks had risk flags?
- Which flags are most common?
- Are flagged stocks performing worse?

### 4. End of Day Review

**Check closed trades:**
```bash
tail -20 trade_history/closed_trades.csv
```

**Look for patterns:**
- Are stocks with `high_rsi` flags closing negative?
- Are stocks with `subpar_volume` flags hitting stops?
- Are stocks with NO flags performing better?

---

## Weekly Analysis (Every Friday)

### Week 1 Analysis (Jan 17, 2026)

Run this analysis script:
```bash
cd /root/paper_trading_lab
python3 analyze_risk_flags.py
```

**Questions to answer:**

1. **Entry Rate:**
   - How many stocks entered with risk flags? (Target: 50-80%)
   - How many Tier 1 opportunities entered? (Target: 3-8 per day)

2. **Risk Flag Frequency:**
   - Which flags appear most often?
   - Do all flagged stocks still have catalyst quality?

3. **Performance by Flag:**
   - Win rate with high_rsi flag: ___%
   - Win rate with subpar_volume flag: ___%
   - Win rate with extended flag: ___%
   - Win rate with NO flags: ___%

4. **Comparison to Previous Week:**
   - Positions entered: v5.5 = 0, v5.6 = ___
   - If v5.6 still = 0, investigate why

### Week 2 Analysis (Jan 24, 2026)

Same analysis as Week 1, plus:

**Outcome Decision:**

| Scenario | Win Rate | Action |
|----------|----------|--------|
| Flagged stocks >60% win rate | Success | Keep soft flags, continue monitoring |
| Flagged stocks 40-60% win rate | Mixed | Keep soft flags, adjust thresholds |
| Flagged stocks <40% win rate | Failed | Selectively re-enable hard blocks |

**If re-enabling hard blocks, prioritize by impact:**
1. If `high_rsi` flag has <30% win rate → Re-enable RSI >75 as hard block
2. If `subpar_volume` flag has <30% win rate → Re-enable volume <1.2x as hard block
3. If `extended` flag has <30% win rate → Re-enable extension >15% as hard block

---

## Red Flags (Immediate Action Required)

### 🚨 STOP TEST IF:

1. **Portfolio Wipeout**: 5+ consecutive losses with average loss >5%
   - **Action**: Restore from `agent_v5.5_backup_jan11.py`

2. **Systemic Failure**: All entries hitting stops within 1-2 days
   - **Action**: Emergency halt, review catalyst quality

3. **Still Zero Entries**: After 3 days, still 0 positions entered
   - **Action**: Check if catastrophic blocks (VIX, macro) are triggering

### ⚠️ INVESTIGATE IF:

1. **Low Entry Rate**: <2 positions entered per day
   - Possible cause: Tier 3 block still rejecting
   - Check: `grep "Tier 3 catalyst" logs/go.log`

2. **High Risk Flag Rate**: >80% of entries have 3+ flags
   - Possible cause: Thresholds too sensitive
   - Action: Review threshold settings (RSI 70 → 75, volume 1.5x → 1.3x)

3. **Divergent Performance**: Flagged stocks perform BETTER than clean stocks
   - Possible cause: Flags identify momentum leaders
   - Action: Consider inverting logic (prioritize flagged stocks)

---

## Data Collection Points

### Daily Metrics to Track:
- Number of GO recommendations
- Number of risk flags logged
- Number of positions entered
- Number of positions with 0 flags
- Number of positions with 1+ flags
- Number of positions with 3+ flags

### Weekly Metrics to Track:
- Win rate (all positions)
- Win rate (0 flags)
- Win rate (1-2 flags)
- Win rate (3+ flags)
- Average return (all positions)
- Average return by flag type
- Most common flag combinations

### End of Test Metrics (Jan 25):
- Total positions entered: v5.5 = 0, v5.6 = ___
- Overall win rate: ___%
- Performance vs SPY: ___%
- Flag correlation analysis complete: Yes/No
- Recommendation: Keep soft flags / Re-enable selective hard blocks / Revert to v5.5

---

## Rollback Procedure (If Needed)

**If test fails, restore previous version:**

```bash
ssh root@174.138.67.26
cd /root/paper_trading_lab

# Backup failed version for analysis
cp agent_v5.5.py agent_v5.6_failed_jan11.py

# Restore previous version
cp agent_v5.5_backup_jan11.py agent_v5.5.py

# Verify restoration
head -3 agent_v5.5.py | grep "v5.6"  # Should show nothing
head -3 agent_v5.5.py | grep "TECHNICAL INDICATORS ENABLED"  # Should show this

# Test will run with v5.5 logic on next GO command
```

---

## Success Criteria

**After 2 weeks, v5.6 is considered SUCCESSFUL if:**

1. ✅ Positions entered: >20 total positions (avg 2+ per day)
2. ✅ Win rate: >50% overall
3. ✅ Risk flag correlation: Documented and understood
4. ✅ System functioning: No catastrophic failures

**If successful:**
- Keep v5.6 soft guard rails
- Use risk flag data to refine thresholds
- Implement position sizing modifiers (Phase 2)

**If unsuccessful:**
- Analyze which flags predicted failures
- Re-enable specific hard blocks selectively
- Consider hybrid approach (soft flags for Tier 1, hard blocks for Tier 2)

---

## Questions for End of Test Review

1. Did soft guard rails solve the zero-entry problem? **Yes / No**
2. Do risk flags correlate with worse outcomes? **Yes / No / Mixed**
3. Should we keep soft flags as-is? **Yes / Modify / Revert**
4. Which flags (if any) should become hard blocks again? **List**
5. What threshold adjustments are needed? **List**
6. Is Claude's judgment on Tier 1 catalysts sound? **Yes / No / Needs refinement**
7. Ready to implement position sizing modifiers based on flags? **Yes / Not yet**

---

## Contact During Test

**If urgent issues arise:**
- Check dashboard: https://164.92.75.167/dashboard
- Review logs: `ssh root@174.138.67.26 "tail -100 /root/paper_trading_lab/logs/go.log"`
- Document issue in `/root/paper_trading_lab/test_issues_v5.6.txt`

**Test concludes**: January 25, 2026
**Final analysis due**: January 26, 2026
