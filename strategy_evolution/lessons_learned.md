# LESSONS LEARNED - STRATEGY EVOLUTION

**Last Updated:** January 22, 2026
**Status:** Clean slate - awaiting first trades to begin learning

---

## 🎯 PROVEN PATTERNS (70%+ Win Rate)

*Data will populate after 20+ trades per catalyst type*

### Tier 1 Catalysts Performance:
- **Earnings Beats:** Not enough data yet
- **Sector Momentum:** Not enough data yet
- **Analyst Upgrades:** Not enough data yet
- **Technical Breakouts:** Not enough data yet
- **Binary Events:** Not enough data yet

---

## ⚠️ MEDIOCRE PATTERNS (50-60% Win Rate)

*Setups that work sometimes but need refinement*

---

## ❌ FAILED PATTERNS (< 40% Win Rate - AVOID)

*Setups to stop making*

---

## 📊 OPTIMAL HOLDING PERIODS

*Average best exit day by catalyst type*

- **Earnings Beats:** TBD (need data)
- **Sector Plays:** TBD (need data)
- **Technical Breakouts:** TBD (need data)
- **Analyst Upgrades:** TBD (need data)

---

## 🎓 KEY INSIGHTS DISCOVERED

### Week 1 Learnings:
*To be populated after first 5 trading days*

### Week 2-4 Learnings:
*To be populated*

### Month 2+ Learnings:
*To be populated*

---

## 🔧 STRATEGY REFINEMENTS MADE

### Version 1.0 (October 27, 2025):
- Initial strategy: 10-position swing portfolio
- Entry: Tier 1 catalysts only
- Stop loss: -7%
- Target: +10-15% depending on catalyst
- Hold time: 3-7 days target, 3 weeks maximum

### Version 1.1 (TBD):
*Refinements based on first week of data*

### Version 2.0 (TBD):
*Major overhaul if needed based on accumulated evidence*

---

## 🧪 ACTIVE HYPOTHESES BEING TESTED

### Hypothesis 1: Earnings beats outperform other catalysts
- **Status:** Testing
- **Sample size needed:** 20+ earnings trades
- **Current sample:** 0

### Hypothesis 2: Waiting for pullback improves entry on large gaps
- **Status:** Testing
- **Sample size needed:** 15+ gap entries
- **Current sample:** 0

### Hypothesis 3: Sector plays require longer hold times than individual catalysts
- **Status:** Testing
- **Sample size needed:** 15+ sector trades
- **Current sample:** 0

---

## 📈 CONFIDENCE CALIBRATION

*Tracking if our confidence levels match reality*

**HIGH Confidence Picks (Should win 70-85%):**
- Current win rate: N/A (need data)
- Status: TBD

**MEDIUM Confidence Picks (Should win 55-70%):**
- Current win rate: N/A (need data)
- Status: TBD

**LOWER Confidence Picks (Should win 40-55%):**
- Current win rate: N/A (need data)
- Status: TBD

---

## 🚨 MISTAKES TO AVOID

*Learning from losses*

### Common Errors Identified:
*To be populated as we make mistakes*

### Rules Added to Prevent Repeats:
*To be populated*

---

## 💡 EDGE IDENTIFICATION

*What gives us an advantage*

### Confirmed Edges (Statistical Significance):
*Waiting for 30+ trades to confirm*

### Suspected Edges (Needs More Data):
*Initial observations to validate*

---

## 🔄 MARKET REGIME ADAPTATION

*How strategy changes based on market conditions*

### Bull Market (SPY Uptrend):
- Strategy adjustments: TBD based on data

### Bear Market (SPY Downtrend):
- Strategy adjustments: TBD based on data

### Choppy/Sideways Market:
- Strategy adjustments: TBD based on data

---

*This document evolves daily as we learn. It's the brain of the system.*

---

## 🚨 CRITICAL SYSTEM FAILURE - January 30, 2026

### STX Trailing Stop Execution Failure

**Trade Details:**
- Ticker: STX (Seagate Technology)
- Entry: .99 (Jan 23, 2026)
- Peak: ~ (+32%)
- Actual Exit: .48 (+18.3%)
- Lost Profit: ~ (14% of potential gains)

**What Happened:**
1. STX hit +10% target on ~Jan 27, triggering "trailing stop activation"
2. Stock continued to +32% - Claude correctly decided to HOLD with trailing stop
3. BUT: The trailing stop was ONLY tracked in JSON - there was NO MECHANISM to execute it
4. The JSON trailing stop was checked only at 9:45 AM and 4:30 PM (twice daily)
5. When EXECUTE ran the next morning, trailing stop data was LOST (Alpaca load bug)
6. By the time a real Alpaca trailing stop was placed, stock had dropped to ~

**Root Causes:**
1. **Paper Trailing Stops Are Useless**: Tracking a trailing stop in JSON without real-time execution is theater, not protection
2. **Check Frequency Too Low**: Checking exits only at 9:45 AM and 4:30 PM means 6+ hours of unprotected exposure
3. **Data Loss Bug**: Trailing stop fields weren't preserved when loading portfolio from Alpaca

**The Lesson:**
Claude's analysis was CORRECT - holding with trailing stop protection was the right call.
But the SYSTEM failed to provide the protection Claude was relying on.
**The gap between stated protection and actual protection cost 14% in lost gains.**

**Fixes Implemented (Jan 30, 2026):**
1. Added Alpaca native trailing stop orders - real-time execution by broker
2. Fixed portfolio loading to preserve trailing stop fields
3. When position hits +10%, now places actual Alpaca order instead of just JSON flag

**Future Consideration:**
For Tier 1 earnings beats that can run 30%+, should we use a tighter trail (1.5%)?
Or wider trail (3%) to ride momentum? STX demonstrates that +10% flat targets
leave massive gains on the table for strong catalysts.

---
