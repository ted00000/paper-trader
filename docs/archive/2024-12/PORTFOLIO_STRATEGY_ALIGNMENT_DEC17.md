# Portfolio Strategy Alignment - December 17, 2025

## Executive Summary

**STRATEGIC CLARIFICATION NEEDED**: User goal is "maintain a portfolio of 10 stocks, always looking to optimize the set." This differs from current implementation which targets 5-8 positions with quality-over-quantity approach.

**Decision Required**: Choose between two valid but different strategies.

---

## Current State Analysis

### What Deep Research Says (Best-in-Class Framework)

**Portfolio Sizing**:
- ✅ "Base allocation 10% standard" (Line 113)
- ✅ "Conviction multiplier: Entry Quality Score/100"
- ✅ "Max 15% per position" (Line 117 guardrails)
- ✅ "Max 3 positions per sector" (Line 47)
- ✅ "No more than 40% of portfolio in any single sector" (Line 47)
- ❌ **NO SPECIFICATION of exact position count** (10 vs 5-8)

**Key Insight** (Line 117):
> "max 3 new positions weekly, human override authority"

This suggests **quality over quantity** - accept 3-5 high-quality setups per week, not forced fills.

---

### What Current Code Implements

**agent_v5.5.py**:
- Max 10 positions (hard limit)
- Target: Fill when quality setups exist
- No minimum position requirement
- Sector concentration: Max 2 per sector (3 if leading)

**TEDBOT_OVERVIEW.md** (our documentation):
- "Max 10 positions at a time" (Line 359, 683)
- "Typically 2-5 new positions per week" (Line 795)
- "BUY: 0-10 positions (skips trades if market UNHEALTHY)" (Line 63)

**Interpretation**: Current system says "UP TO 10" not "MUST BE 10"

---

### What PROJECT_INSTRUCTIONS.md Says (Agent Prompt)

**Line 15**:
> "Maintain an active portfolio of exactly **10 stocks** at all times"

**Line 18**:
> "Each stock receives **10% of total account value**"
> "Account always fully invested (10 positions × 10% = 100%)"

**This creates FORCED FILLING behavior** - Claude thinks it MUST find 10 stocks.

---

## Two Valid Strategic Approaches

### Strategy A: "Always 10 Stocks" (Current Prompt)

**Philosophy**: Diversification reduces risk, full deployment maximizes returns

**Pros**:
- ✅ Maximum diversification (10 uncorrelated bets)
- ✅ Reduces single-stock risk
- ✅ Always fully invested (no cash drag)
- ✅ Systematic position sizing (easy to manage)
- ✅ Simple to execute (clear target)

**Cons**:
- ❌ Forces acceptance of marginal setups (40-59 point scores)
- ❌ May dilute conviction (spreading too thin)
- ❌ Accepts 50-60% win rate setups to fill slots
- ❌ Sector concentration harder to avoid (10 positions across 11 sectors)
- ❌ More positions = more monitoring = more work

**Requirements**:
- Must accept Tier 2 catalysts (analyst upgrades, contracts)
- Must accept 40-59 point scorecard scores
- Must size 40-point setup at ~5% (40/100 × 10% base)
- Need ~20-30 candidates scoring 40+ to choose 10

**Expected Weekly Flow**:
```
Screener: 300-500 Tier 1/2 candidates
    ↓
Agent: Evaluates using 100-point scorecard
    ↓
Accepts: 20-30 stocks scoring 40+ points
    ↓
Portfolio: Best 10 by conviction sizing
    ↓
Result: 10 positions, avg score 55-65 points
```

---

### Strategy B: "Quality Over Quantity" (Deep Research Aligned)

**Philosophy**: Only take exceptional setups, cash is a position

**Pros**:
- ✅ Higher conviction per position (only 60+ scores)
- ✅ Better risk-adjusted returns (target 60-70% win rate)
- ✅ Easier sector concentration management (fewer positions)
- ✅ Less monitoring required (5-8 vs 10)
- ✅ Can size best setups larger (80+ point setups get 12-15%)
- ✅ Aligns with "max 3 new positions weekly" (Deep Research Line 117)

**Cons**:
- ❌ Cash drag during low-opportunity periods
- ❌ Less diversification (5-8 vs 10 names)
- ❌ More concentrated single-stock risk
- ❌ Portfolio may only have 2-3 positions in weak markets
- ❌ Underinvested during good markets

**Requirements**:
- Accept only 60+ point scorecard scores
- Tier 1 preferred, Tier 2 if exceptional (75+ points)
- Position sizing: 60-point = 6%, 80-point = 8%, 90-point = 12%
- Need ~10-15 candidates scoring 60+ to choose 5-8

**Expected Weekly Flow**:
```
Screener: 300-500 Tier 1/2 candidates
    ↓
Agent: Evaluates using 100-point scorecard
    ↓
Accepts: 10-15 stocks scoring 60+ points
    ↓
Portfolio: Best 5-8 by conviction sizing
    ↓
Result: 5-8 positions, avg score 70-75 points
```

---

## Academic Research Guidance

### Diversification Benefits (Line 47)

**From Banking Portfolio Research**:
- Correlation >0.5 requires risk limits
- Sector concentration >25-40% creates uncompensated risk
- **Optimal diversification: 8-12 stocks in different sectors**

**Implication**: 10 stocks provides good diversification IF across multiple sectors.

### Position Concentration (Line 113)

**From Conviction-Based Sizing Research**:
- Professional fund managers: 1% (low conviction) to 7-10% (high conviction)
- Half-Kelly suggests 14% max with 55% win rate
- **System uses: 6-13% based on conviction**

**Implication**: Variable sizing allows 5-8 concentrated positions OR 10 smaller positions.

### Win Rate Targets (Line 101)

**Entry Quality Scorecard Thresholds**:
- 80-100 points: 70-75% win rate (exceptional)
- 60-79 points: 60-70% win rate (good)
- 40-59 points: 50-60% win rate (acceptable)

**Implication**:
- Strategy A (10 stocks): Avg 50-60% win rate (includes 40-59 point setups)
- Strategy B (5-8 stocks): Avg 60-70% win rate (only 60+ point setups)

---

## Current System Performance (Dec 2025)

**Actual Results**:
- Screener outputs: 300-500 candidates
- Agent accepts: 1-2 stocks (0.4% acceptance)
- Portfolio: 1-2 positions (severely underinvested)

**Root Cause**: Agent prompt says "TIER 1 ONLY" but receives Tier 1/2 mix

**If We Fix Prompt to Accept Tier 1/2**:

**Strategy A Projection** (Always 10):
- Agent accepts: 20-30 stocks scoring 40+
- Portfolio: Best 10 (scores 45-75, avg ~55)
- Win rate: ~55% (mix of 40-79 point setups)
- Typical positions: 4-7% each (conviction adjusted)

**Strategy B Projection** (Quality 5-8):
- Agent accepts: 10-15 stocks scoring 60+
- Portfolio: Best 5-8 (scores 60-85, avg ~70)
- Win rate: ~65% (only good/exceptional setups)
- Typical positions: 8-12% each (higher conviction)

---

## Recommendation Matrix

### IF User Goal = "Always Have 10 Stocks"

**Update PROJECT_INSTRUCTIONS.md**:
```markdown
## Portfolio Management

**Target**: Maintain 8-10 active positions
- Minimum: 6 positions (quality setups exist)
- Maximum: 10 positions (hard limit)
- Accept Entry Quality Scorecard scores ≥40 points

**Position Sizing**:
- Base allocation: 10%
- Conviction multiplier: score/100
- Example: 40-point setup = 4%, 60-point = 6%, 80-point = 8%
- Sector limit: Max 2 per sector (3 if top-ranked)

**Acceptance Criteria**:
- Tier 1 catalysts: Always accept if score ≥40
- Tier 2 catalysts: Accept if score ≥50
- Fill portfolio to 8-10 positions when setups available
- Hold cash only during macro blackouts (VIX >30, FOMC windows)
```

**Expected Outcome**:
- 8-10 positions most weeks
- Win rate: 55-60%
- Avg position size: 5-8%
- More diversification, less conviction

---

### IF User Goal = "Quality Over Quantity"

**Update PROJECT_INSTRUCTIONS.md**:
```markdown
## Portfolio Management

**Target**: Maintain 5-8 high-conviction positions
- Minimum: 3 positions (during weak markets)
- Maximum: 10 positions (hard limit, rare)
- Accept Entry Quality Scorecard scores ≥60 points

**Position Sizing**:
- Base allocation: 10%
- Conviction multiplier: score/100
- Example: 60-point setup = 6%, 75-point = 7.5%, 90-point = 9%
- Sector limit: Max 2 per sector (easier with fewer positions)

**Acceptance Criteria**:
- Tier 1 catalysts: Accept if score ≥60
- Tier 2 catalysts: Accept only if score ≥70 (exceptional)
- Target 5-8 positions, hold 20-40% cash when setups scarce
- Max 3 new positions per week (Deep Research guideline)
```

**Expected Outcome**:
- 5-8 positions most weeks
- Win rate: 63-68%
- Avg position size: 7-10%
- Higher conviction, less diversification

---

## Key Decision Points

### Question 1: Mandatory Fill vs Optional Fill?

**Option A**: "MUST maintain 10 stocks at all times"
- Accept 40-point setups to fill slots
- Always fully invested
- Lower avg win rate (55%), higher diversification

**Option B**: "TARGET 5-8 stocks, max 10"
- Only accept 60+ point setups
- Hold cash when quality lacking
- Higher avg win rate (65%), lower diversification

### Question 2: Fixed Sizing vs Conviction Sizing?

**Current Prompt** (PROJECT_INSTRUCTIONS.md):
- "Each stock receives 10% of total account value"
- Fixed sizing, no conviction multiplier

**Deep Research Framework**:
- Base 10% × conviction multiplier (score/100)
- Variable sizing based on setup quality
- Aligns with professional practices

**These MUST align** - can't have fixed 10% if targeting variable conviction.

### Question 3: Tier 1 Only vs Tier 1/2?

**Current Prompt**: "TIER 1 CATALYSTS ONLY"
- Rejects analyst upgrades, contracts (Tier 2)
- Very restrictive, explains low acceptance rate

**Deep Research + Code**: Accept Tier 1 & 2
- Tier 2 analyst upgrades = 20 points in scorecard
- Tier 2 contracts = Tier 1 if SEC 8-K filing
- More flexibility, better pipeline

**Recommendation**: Accept Tier 1/2, reject only Tier 3

---

## Proposed Resolution

Based on Deep Research best practices, I recommend **Strategy B with flexibility**:

### Hybrid Approach: "Quality-First with Flex Fill"

```markdown
## Portfolio Management Strategy

**Primary Target**: 5-8 high-conviction positions (Entry Quality Score ≥60)
**Secondary Target**: Fill to 10 positions if additional setups score ≥50
**Maximum**: 10 positions (hard limit for diversification)

**Acceptance Thresholds**:
- Priority 1: Scores 80-100 (exceptional) - always accept, up to max position size
- Priority 2: Scores 60-79 (good) - accept to fill slots 1-8
- Priority 3: Scores 50-59 (decent) - accept ONLY to fill slots 9-10 if available
- Reject: Scores <50 (marginal/poor)

**Position Sizing**:
- 80-100 points: 8-12% (conviction 0.80-1.00)
- 60-79 points: 6-8% (conviction 0.60-0.79)
- 50-59 points: 5-6% (conviction 0.50-0.59)
- Sector limit: Max 2 per sector (3 if top-ranked)

**Cash Management**:
- Target 10-30% cash reserve (quality buffer)
- 0-10% cash if many 80+ point setups exist
- 30-50% cash if VIX >30 or macro blackout
```

**Benefits**:
- ✅ Prioritizes quality (targets 5-8 at 60+ points)
- ✅ Allows opportunistic fill (can go to 10 if good setups)
- ✅ Maintains cash buffer for best opportunities
- ✅ Flexible with market conditions
- ✅ Aligns with Deep Research conviction framework

**Expected Results**:
- Typical portfolio: 6-8 positions
- Strong markets: 8-10 positions (more 60+ setups)
- Weak markets: 4-6 positions (fewer quality setups)
- Avg score: 65-70 points
- Win rate: 60-65%

---

## Implementation Impact

### Current Prompt Issues

**PROJECT_INSTRUCTIONS.md Line 15-18**:
```
"Maintain an active portfolio of exactly 10 stocks at all times"
"Each stock receives 10% of total account value"
```

**Problems**:
1. ❌ "Exactly 10" forces marginal fills
2. ❌ "10% fixed" contradicts conviction sizing
3. ❌ "Always" prevents cash management
4. ❌ Creates cognitive dissonance with scorecard framework

### After Fix

**Updated PROJECT_INSTRUCTIONS.md**:
```markdown
## Portfolio Management

**Target**: 5-8 high-conviction positions (scorecard ≥60 points)
**Maximum**: 10 positions (diversification limit)
**Fill Strategy**: Prioritize quality, accept 50+ point setups to optimize portfolio

**Position Sizing** (conviction-based):
- Base allocation: 10% per position
- Conviction multiplier: Entry Quality Score / 100
- Example: 60-point setup = 6%, 80-point = 8%, 90-point = 9%
- Sector concentration: Max 2 per sector (3 in top-ranked sectors)

**Acceptance Criteria**:
- **Tier 1 Catalysts** (earnings beats, M&A, FDA, major contracts):
  - Score ≥80: Always accept (exceptional setup)
  - Score 60-79: Accept to fill portfolio (good setup)
  - Score 50-59: Accept only if needed to optimize (decent setup)
  - Score <50: Reject (insufficient quality)

- **Tier 2 Catalysts** (analyst upgrades, contracts, SEC 8-K):
  - Score ≥70: Accept (strong Tier 2)
  - Score <70: Reject (insufficient quality for Tier 2)

- **Tier 3 Catalysts** (insider buying only):
  - Always reject (leading indicator, not immediate catalyst)

**Cash Management**:
- Target: 10-30% strategic cash reserve
- Allows deployment into best opportunities
- Increases to 30-50% during VIX >30 or macro blackouts
- Prevents forced fills into marginal setups
```

---

## User Decision Required

**Please confirm your strategic preference**:

### Option 1: "Always Maintain 10 Stocks"
- Accept 40+ point setups to fill all slots
- Always fully invested (0-10% cash)
- Target win rate: 55-60%
- More diversification, less conviction
- **Prompt Update**: Accept scores ≥40, target 10 positions

### Option 2: "Quality Over Quantity" (5-8 Target)
- Accept only 60+ point setups
- Hold 20-40% cash strategically
- Target win rate: 63-68%
- Less diversification, higher conviction
- **Prompt Update**: Accept scores ≥60, target 5-8 positions

### Option 3: "Hybrid Quality-First" (RECOMMENDED)
- Target 5-8 at 60+ points, flex to 10 if good setups at 50+
- Hold 10-30% cash normally
- Target win rate: 60-65%
- Balanced approach
- **Prompt Update**: Accept scores ≥50, prioritize 60+, target 5-10 positions

---

**Once you choose, I'll update PROJECT_INSTRUCTIONS.md to align with your goal and ensure the agent behavior matches your strategy.**

---

**Status**: Awaiting strategic direction
**Date**: December 17, 2025, 9:45 PM ET
**Decision Impact**: Agent acceptance rate, portfolio composition, win rate targets
