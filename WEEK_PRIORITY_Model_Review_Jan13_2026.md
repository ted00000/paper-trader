# Week Priority: Model Integrity Review & Portfolio Optimization
## January 13-17, 2026

---

## Current State Assessment

### What We Just Changed (v5.7 → v5.7.1)
**Architecture shift:** From "rules override AI" to "AI-first with full data"

**Removed:**
- Tier validation hard blocks
- Conviction counter hard blocks
- Sector/industry concentration limits
- Technical filter hard blocks (RSI, ADX, volume)

**Added:**
- Full technical indicators to Claude's view
- Threshold context as guidelines (not rules)
- Diversification guidance (not enforcement)
- Position sizing as risk dial (5-13%)
- Explicit decision types (ENTER/ENTER_SMALL/PASS)

**Result:** Claude now has full admission authority with only catastrophic checks remaining

---

## The Critical Question

**Have we devalued our model by removing validation rules?**

### What Our Model Originally Was:
A **swing trading system** focused on:
1. **Catalyst-driven entries** - Tier 1 events (FDA, M&A, earnings beats)
2. **Technical confirmation** - Stage 2 uptrends, momentum, volume
3. **Relative strength** - Outperforming sector/market
4. **Risk management** - 7% stops, position sizing, holding periods
5. **Portfolio construction** - Diversification, sector allocation
6. **Time horizon** - 3-7 day swings (not day trading)

### What We Need to Verify:
- Is Claude respecting the swing trading time horizon?
- Is Claude prioritizing catalyst quality over technical momentum?
- Is Claude maintaining disciplined risk management?
- Is Claude constructing portfolios or just picking stocks?

---

## Week Review Tasks

### Task 1: Audit Current Model Alignment

**Questions to answer:**

**Catalyst Quality:**
- Are Claude's picks truly catalyst-driven or momentum-chasing?
- Today's picks: ALGT (M&A), AVDL (M&A), AKAM (upgrade), AXGN (earnings), ARWR (clinical), APGE (clinical)
- ✓ All have identifiable catalysts (good start)
- ⚠️ Need to verify: Are these Tier 1 quality or did we lower standards?

**Technical Standards:**
- Are we entering technically sound setups or overheated momentum?
- Today: Several stocks skipped due to gaps (good - discipline present)
- Today: AXSM got 0% sizing from conviction (good - filter working)
- ⚠️ Need to verify: Are technical thresholds still meaningful?

**Time Horizon:**
- Is Claude building 3-7 day swing positions or same-day trades?
- GO prompt says: "Minimum hold 2 days, Maximum hold 21 days"
- ⚠️ Need to monitor: Does Claude respect swing trading rules?

**Portfolio Construction:**
- Is Claude thinking portfolio-level or stock-level?
- Today: 4 Healthcare (67% deployed), justified by FDA catalyst cluster
- ✓ Claude documented reasoning for concentration
- ⚠️ Need to verify: Is this concentration warranted or rationalized?

---

### Task 2: Define Model Guardrails vs Catastrophic Checks

**What Should Be Enforced (Catastrophic):**
These are existential risks that make trading impossible/dangerous:

1. **VIX ≥35** - Market shutdown condition (proven correlation with drawdowns)
2. **Macro blackout** - FOMC/CPI days (proven volatility spikes)
3. **Stock halted** - Cannot trade (execution impossible)
4. **Liquidity collapse** - <$1M notional (can't exit without slippage)
5. **Data integrity** - Missing price/volume (blind decision making)

**What Should Be Guidance (Model Principles):**
These are optimization goals Claude should understand and work toward:

1. **Catalyst quality** - Prefer Tier 1, justify if Tier 2
2. **Technical health** - Thresholds are guidelines for co-existent factors
3. **Diversification** - Aim <40% per sector, justify if concentrated
4. **Time horizon** - 3-7 day swings, not day trades
5. **Position sizing** - 5-13% based on conviction + risk
6. **Holding discipline** - Minimum 2 days unless stop/target hit

**Critical distinction:**
- Catastrophic = "You cannot do this" (blocks entry)
- Model principles = "You should aim for this" (guides decision, Claude can deviate with reasoning)

---

### Task 3: Measure Model Adherence

**Daily Checks (for 1 week):**

**Catalyst Quality Check:**
```bash
# Review each day's picks
jq '.buy[] | {ticker, catalyst, confidence}' pending_positions.json

Questions:
- Is catalyst specific and recent (last 5 days)?
- Is thesis quantitative (revenue beat %, contract $, approval timeline)?
- Or generic (momentum, sector strength, technical breakout)?
```

**Technical Discipline Check:**
```bash
# Check if risk flags are being considered
jq '.buy[] | {ticker, risk_flags: (.risk_flags | length)}' pending_positions.json

Questions:
- Are stocks with 3+ risk flags sized smaller?
- Or is Claude ignoring flags and sizing all 10%?
- Are ENTER_SMALL decisions being used?
```

**Portfolio Construction Check:**
```bash
# Review sector allocation reasoning in GO output
cat daily_reviews/go_*.json | jq -r '.content[0].text' | grep -A 20 "PORTFOLIO CONSTRUCTION"

Questions:
- Did Claude document sector allocation rationale?
- Is concentration justified by opportunity set?
- Or arbitrary (just happened to pick 4 Healthcare)?
```

**Time Horizon Check:**
```bash
# After 3 days, check if positions are being held
jq '.positions[] | {ticker, days_held, reason_for_entry}' current_portfolio.json

Questions:
- Are positions being churned daily (day trading)?
- Or held 3-7 days (swing trading)?
- Are exits justified (stop hit, target hit, catalyst invalid)?
```

---

### Task 4: Identify Gaps in Current Model

**What might be missing now:**

**1. Entry Timing Discipline:**
- Old validation: Blocked if extended >10% from 20-MA
- New approach: Claude sees "extended 12%" and decides
- **Question:** Will Claude chase or wait for pullbacks?
- **Test:** Track 1-day adverse excursion on entries with "extended" flag

**2. Conviction Floor:**
- Old validation: SKIP if <3 supporting factors
- New approach: Claude sets position size (can go 5%)
- **Question:** Will Claude enter weak setups at 5% or properly PASS?
- **Test:** Do 5-6% positions have worse outcomes than 10-13%?

**3. Tier Discipline:**
- Old validation: Hard block on Tier 2/3
- New approach: Claude told "prefer Tier 1, justify Tier 2"
- **Question:** Will Claude rationalize Tier 2 picks?
- **Test:** What % of picks are Tier 1 vs Tier 2? Do Tier 2 underperform?

**4. Sector Concentration Limits:**
- Old validation: Max 2 per sector (or 3 if leading)
- New approach: Claude told "<40% per sector, justify if 40-50%"
- **Question:** Will Claude respect 40% or always find justification?
- **Test:** Track concentration levels and correlation with drawdowns

**5. Holding Period Discipline:**
- Old validation: None (was in ANALYZE command logic)
- New approach: GO prompt says "minimum 2 days"
- **Question:** Will Claude respect swing trading time horizon?
- **Test:** Average holding period, churn rate, premature exits

---

### Task 5: Define Success Metrics

**Not just win rate and returns - measure MODEL ADHERENCE:**

| Metric | Model Standard | Measurement |
|--------|---------------|-------------|
| **Catalyst Quality** | 80%+ Tier 1 | % of picks with Tier 1 catalyst |
| **Technical Discipline** | <20% with 3+ risk flags | % high-risk entries |
| **Diversification** | <40% per sector | Max sector concentration |
| **Time Horizon** | 3-7 day avg hold | Median holding period |
| **Entry Timing** | <10% chase moves | % entries extended >15% |
| **Position Sizing** | Variance 5-13% | Std dev of position sizes |
| **PASS Rate** | 30-40% selectivity | % candidates rejected |

**If metrics drift:**
- 50% Tier 1 → Claude lowering standards
- 60% single sector → Claude rationalizing concentration
- 1.5 day avg hold → Claude day trading
- All 10% sizing → Claude not using risk dial
- 10% PASS rate → Claude forcing trades

**Then:** Tune prompt language, don't re-introduce hard blocks

---

## This Week's Focus

### Monday-Tuesday (Jan 13-14): Observe & Document
- Let Claude run with new architecture
- Document every decision and reasoning
- Track: catalyst quality, technical flags, sector allocation, position sizing

### Wednesday (Jan 15): First Review
- Analyze 2 days of decisions
- Check model adherence metrics
- Identify any immediate concerns (day trading, poor catalysts, etc.)

### Thursday-Friday (Jan 16-17): Tune or Affirm
- If model adherent: Affirm approach, continue monitoring
- If drifting: Tune prompt language to reinforce principles
- If broken: Discuss selective re-introduction of soft floors

---

## Portfolio Optimization Guidelines

**What Claude should be doing DAILY:**

### Portfolio Review (8:45 AM):
1. **Evaluate existing positions:**
   - Is catalyst still intact? (news, guidance, timeline)
   - Is technical setup still healthy? (above MA, momentum)
   - Is position profitable or at risk? (vs stop, vs target)

2. **Hold/Exit decision framework:**
   - HOLD if: Profitable, catalyst intact, technical healthy, <21 days
   - EXIT if: Stop approaching, target hit, catalyst invalidated, 21 days flat
   - DO NOT exit just because it's a new day

3. **New entry evaluation:**
   - Compare new opportunities to existing positions
   - Only replace if: New is significantly better AND old is flat/small loss AND >2 days held
   - Quality over quantity: Better 6 great positions than 10 mediocre

### What We Should See:
- **Low churn:** Most positions held 3-7 days (not daily turnover)
- **Selective exits:** Only when stop/target/catalyst triggers (not arbitrary)
- **Portfolio thinking:** "Should I hold ALGT or replace with BA?" not "Should I buy BA?"
- **Consistency:** Similar allocation themes across week (not random daily pivots)

### What Would Be Concerning:
- **Daily churn:** Exiting winners to chase new momentum
- **Arbitrary exits:** Selling profitable positions just to free slots
- **Stock-level thinking:** Filling 10 slots without portfolio consideration
- **Inconsistency:** Tech heavy Monday, Healthcare Tuesday, Energy Wednesday (no theme)

---

## Goal Alignment Check

**Your stated goal:** "High return with very high consistency"

**This means:**
- Consistency > peak returns (rather 15% with 5% drawdown than 40% with 20% drawdown)
- Swing trading > day trading (fewer trades, less churn, let swings work)
- Catalyst quality > momentum chasing (fundamentals drive multi-day moves)
- Risk management > opportunity capture (position size, stops, diversification)

**Questions to ask each day:**
1. Are we maintaining consistency (low drawdowns, steady gains)?
2. Are we respecting swing time horizon (not day trading)?
3. Are we being selective (PASS rate 30-40%)?
4. Are we sizing risk appropriately (variance in position sizes)?

**If NO to any:** The model is drifting, needs correction

---

## Deliverables This Week

### Daily (Jan 13-17):
- Document Claude's GO analysis and reasoning
- Track metrics: catalyst tier, risk flags, sector %, position sizes, PASS rate
- Note any concerning patterns

### Wednesday Review:
- Compile 2-day metrics
- Assess model adherence
- Flag any immediate concerns

### Friday Summary:
- Full week analysis
- Model adherence report card
- Recommendations: Continue / Tune / Selective Re-enforcement

---

## The Big Picture

**We didn't remove the model - we changed enforcement from rules to guidance.**

**Old model:**
- Rules enforce principles → AI tries to work around them → Blockers kill opportunities

**New model:**
- AI understands principles → AI applies them with context → Catastrophic checks only

**This week proves:** Can Claude be trusted to uphold model principles without hard blocks?

**Success looks like:**
- Claude selects Tier 1 catalysts without being forced
- Claude respects swing time horizon without being blocked
- Claude manages risk via sizing without being capped
- Claude diversifies thoughtfully without being limited

**Failure looks like:**
- Claude chases momentum (day trading behavior)
- Claude rationalizes weak catalysts (Tier 2/3 becoming norm)
- Claude ignores risk flags (all 10% sizing regardless)
- Claude concentrates arbitrarily (70% Healthcare "just because")

---

## Key Principle

**"Let Claude be Claude" does NOT mean "Let Claude do whatever"**

It means:
- Give Claude the model principles explicitly
- Give Claude the data to make informed decisions
- Trust Claude to apply principles with context
- Measure if Claude upholds principles
- Tune prompt if Claude drifts from principles
- Only re-introduce blocks if Claude proves untrustworthy of specific principle

**This week we find out:** Is Claude a disciplined swing trader or a momentum chaser?

The answer determines if v5.7 architecture succeeds or needs refinement.

---

**Prepared:** January 13, 2026
**Review Date:** January 17, 2026 (end of week)
**Status:** Week 1 of AI-first model validation
