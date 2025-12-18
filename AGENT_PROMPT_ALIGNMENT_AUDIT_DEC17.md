# Agent Prompt Alignment Audit - December 17, 2025

## Executive Summary

**CRITICAL MISALIGNMENT FOUND**: PROJECT_INSTRUCTIONS.md (the agent's system prompt) is **completely contradictory** to the Deep Research methodology and current code implementation.

**Status**: 🚨 **URGENT** - Agent prompt telling Claude opposite of what code does

---

## The Problem

### What the CODE Does (Correct - Deep Research Aligned)
✅ Screener outputs 300-500 candidates (all Tier 1/2/3 catalysts)
✅ RS used for SCORING only (0-5 points)
✅ Agent accepts Tier 1 and Tier 2 catalysts
✅ Agent uses 100-point Entry Quality Scorecard
✅ Position sizing based on conviction (scorecard/100)

### What the PROMPT Says (Wrong - OLD methodology)
❌ "Scans S&P 1500 for stocks with RS ≥3%" (Line 99, 155)
❌ "Save top 50 candidates" (Line 162)
❌ "TIER 1 CATALYSTS ONLY" (Line 24)
❌ "Tier 2/3 REJECTED" (Line 111)
❌ "10 stocks at all times" (Line 15)
❌ "Each stock receives 10% of total account value" (Line 18)

**Result**: Claude receives 300-500 Tier 1/2 candidates, but the prompt tells it to ONLY accept Tier 1 and to expect 50 candidates with RS≥3%.

---

## Detailed Contradictions

### 1. RS Filter Contradiction 🚨 CRITICAL

**PROJECT_INSTRUCTIONS.md Lines 99, 155**:
```
"Scans S&P 1500 for stocks with RS ≥3%"
"Filter for Relative Strength ≥3% vs sector"
```

**Actual Code** (market_screener.py:577-605):
```python
'passed_filter': True,  # ALWAYS PASS - RS for scoring only
'rs_score_points': 0-5  # Scoring factor, not filter
```

**Impact**: Claude thinks all candidates have RS≥3%, but code sends candidates with any RS (including negative).

---

### 2. Candidate Count Contradiction

**PROJECT_INSTRUCTIONS.md Line 162**:
```
"Save top 50 candidates to `screener_candidates.json`"
```

**Actual Code** (market_screener.py:2348-2367):
```python
# Tier-based quotas to prevent insider crowding
# Top 60 Tier 1, Top 50 Tier 2, Top 40 Tier 3
# Expected output: 300-500 candidates
```

**Impact**: Claude expects 50 highly-filtered candidates, gets 300-500 mixed-tier candidates.

---

### 3. Tier Acceptance Contradiction 🚨 CRITICAL

**PROJECT_INSTRUCTIONS.md Line 24**:
```
"## 🎯 STOCK SELECTION CRITERIA (TIER 1 CATALYSTS ONLY)"
```

**PROJECT_INSTRUCTIONS.md Line 111**:
```
"Tier 2/3 Rejected: Analyst opinions, sector momentum without catalyst, stale news"
```

**Actual Code** (agent_v5.5.py:5369-5372):
```python
# Auto-reject Tier 3 catalysts
if tier_result['tier'] == 'Tier3':
    validation_passed = False
# NOTE: Tier 2 is ACCEPTED (analyst upgrades, contracts, etc.)
```

**Impact**:
- Claude told to reject Tier 2/3
- Code rejects Tier 3 only
- **Tier 2 analyst upgrades are legitimate catalysts but prompt says reject them**

---

### 4. Position Count Contradiction

**PROJECT_INSTRUCTIONS.md Lines 15, 18**:
```
"Maintain an active portfolio of exactly 10 stocks at all times"
"Each stock receives 10% of total account value"
```

**Actual System**:
- Max 10 positions (not required to fill all 10)
- Position sizing: 6-13% based on conviction
- Market breadth adjustment: -40% in UNHEALTHY markets
- Sector concentration: Max 2 per sector (3 in leading)

**Impact**: Claude may feel pressure to fill 10 positions even when only 3-5 quality setups exist.

---

### 5. Composite Scoring Weights Contradiction

**PROJECT_INSTRUCTIONS.md Lines 157-161**:
```
"Score and rank candidates by composite score:
   - 40% Relative Strength
   - 30% News/Catalyst Strength
   - 20% Volume Surge
   - 10% Technical Setup"
```

**Actual Code** (market_screener.py:1953-1979):
```python
# Tier 1: Catalyst is KING (40% weight)
base_score = (
    rs_result['score'] * 0.20 +          # RS 20% not 40%
    news_result['scaled_score'] * 0.20 + # News 20% not 30%
    volume_result['score'] * 0.10 +      # Volume 10% not 20%
    technical_result['score'] * 0.10     # Technical 10% same
)
```

**Impact**: Claude thinks RS is 40% of score (most important), but code makes it 20% for Tier 1 stocks.

---

### 6. Entry Quality Scorecard Missing 🚨 CRITICAL

**PROJECT_INSTRUCTIONS.md**: No mention of 100-point Entry Quality Scorecard

**Deep Research Document** (Claude_Deep_Research.md:91-101):
```
Entry Quality Scorecard (0-100 points):
- Catalyst Quality: 0-30 pts
- Technical Setup: 0-25 pts (RS is 0-5 pts within this)
- Sector/Market: 0-20 pts
- Historical Patterns: 0-15 pts
- Conviction/Risk: 0-10 pts

Score Thresholds:
- 80-100: Exceptional (70-75% win rate)
- 60-79: Good (60-70% win rate)
- 40-59: Acceptable (50-60% win rate)
```

**Impact**: Claude has NO GUIDANCE on the 100-point scoring system it should be using.

---

### 7. Technical Filters Contradiction

**PROJECT_INSTRUCTIONS.md Lines 66-90**:
```
"Every stock must pass ALL 4 technical filters:
1. Stock price MUST be above 50-day SMA
2. 5-day EMA MUST be above 20-day EMA
3. ADX MUST be >20
4. Current volume MUST be >1.5x 20-day average"
```

**Actual Code**: These filters ARE implemented correctly

**Impact**: ✅ This section is CORRECT and should be kept

---

### 8. Conviction Sizing Missing

**PROJECT_INSTRUCTIONS.md**: Fixed 10% position sizes

**Actual Code** (agent_v5.5.py:3190-3260):
```python
def calculate_conviction_level():
    # Cluster-based scoring (max 11 factors)
    # Conviction multiplier = score/100
    # Base allocation 10%, adjusted by conviction
```

**Impact**: No guidance on conviction-based sizing methodology

---

## What Claude Actually Receives

When the GO command runs, Claude receives:

```
PROJECT INSTRUCTIONS:
[PROJECT_INSTRUCTIONS.md - 5000 chars]
    ↓
"TIER 1 CATALYSTS ONLY"
"RS ≥3% filter"
"Top 50 candidates"
"10% fixed sizing"

SCREENER CANDIDATES:
[screener_candidates.json - actual data]
    ↓
300-500 stocks
Mixed Tier 1/2/3
RS ranging from -10% to +50%
Varying catalyst quality

STRATEGY RULES:
[strategy_rules.md - 8000 chars]
    ↓
Learning-derived patterns
May contradict PROJECT_INSTRUCTIONS
```

**Cognitive Dissonance**: Claude sees 300 candidates but told to expect 50. Sees Tier 2 stocks but told to reject them. Sees negative RS stocks but told all have RS≥3%.

---

## Impact Analysis

### Why Agent Rejects So Many Candidates

**Current Reality** (Dec 2025):
- Screener outputs: 300-500 candidates
- Agent accepts: 1-2 stocks
- **Acceptance rate: 0.4%** 🚨

**Root Causes**:

1. **Tier Confusion**: Prompt says "TIER 1 ONLY" but code sends Tier 2
   - Claude rejects legitimate Tier 2 analyst upgrades
   - Rejects Tier 2 contract news

2. **RS Expectation Mismatch**: Prompt says "RS≥3%" but code sends all RS
   - Claude may mentally filter RS<3% stocks as "shouldn't be here"
   - Creates suspicion of data quality

3. **Volume Expectation**: Prompt emphasizes quantity ("top 50") but receives 300-500
   - Claude may think lower-ranked stocks are "noise"
   - Focuses only on top 10-20 instead of entire pool

4. **Missing Scorecard Guidance**: No 100-point framework in prompt
   - Claude doesn't know to evaluate on 0-100 scale
   - Defaults to binary accept/reject thinking

5. **Fixed Sizing Assumption**: Prompt says 10% fixed
   - No guidance on conviction multipliers
   - May skip marginal setups that would be 6-8% positions

---

## Deep Research Alignment Gaps

### What Deep Research Says (Best-in-Class)

**Line 84-85**:
> "AI implementation best practices recommend **hybrid approach with AI as decision assist rather than autonomous agent**: **rule-based filters for minimum liquidity (>$50M daily volume), price (>$10), and catalyst presence eliminate low-quality opportunities, then AI analyzes sentiment, evaluates catalyst magnitude, and ranks remaining candidates.**"

**Key Points**:
1. ✅ Hard filters at screener level (price, volume, catalyst)
2. ✅ AI evaluates QUALITY not QUANTITY
3. ✅ AI uses Entry Quality Scorecard (0-100 points)
4. ✅ Score-based ranking, not binary accept/reject

### What PROJECT_INSTRUCTIONS Says (OLD)

1. ❌ "TIER 1 ONLY" - Too restrictive
2. ❌ "RS ≥3% filter" - Contradicts code
3. ❌ "Top 50 candidates" - Incorrect volume
4. ❌ "10% fixed sizing" - No conviction multipliers
5. ❌ No Entry Quality Scorecard framework
6. ❌ Binary thinking ("We ONLY buy" vs "We NEVER buy")

---

## Recommended Fixes

### Priority 1: CRITICAL FIXES 🚨

**1. Remove RS≥3% Filter References**
```diff
- Scans S&P 1500 for stocks with RS ≥3%
+ Scans S&P 1500 for stocks with catalyst presence

- Filter for Relative Strength ≥3% vs sector
+ RS calculated for scoring (0-5 pts), not filtering
```

**2. Update Tier Acceptance Criteria**
```diff
- ## 🎯 STOCK SELECTION CRITERIA (TIER 1 CATALYSTS ONLY)
+ ## 🎯 STOCK SELECTION CRITERIA (TIER 1 & TIER 2 CATALYSTS)

- Tier 2/3 Rejected: Analyst opinions, sector momentum
+ Tier 2 Accepted: Analyst upgrades, major contracts, SEC 8-K filings
+ Tier 3 Rejected: Insider buying only (leading indicator, not immediate catalyst)
```

**3. Add Entry Quality Scorecard**
```markdown
## 📊 ENTRY QUALITY SCORECARD (0-100 POINTS)

You will evaluate each candidate using this systematic framework:

### Component Breakdown:
1. **Catalyst Quality** (0-30 pts)
   - Earnings surprise magnitude: 3-12 pts
   - Revenue performance: 2-8 pts
   - Catalyst freshness: 0-5 pts
   - Secondary catalysts: +5 pts bonus

2. **Technical Setup** (0-25 pts)
   - Trend alignment: 0-7 pts
   - Relative strength vs SPY: 0-5 pts
   - Volume confirmation: 0-5 pts
   - Price action setup: 0-5 pts
   - Technical structure: 0-3 pts

3. **Sector and Market Context** (0-20 pts)
   - Sector strength: -2 to +4 pts
   - Market regime: 0-5 pts
   - Diversification: -2 to +4 pts
   - Event timing: -5 to +2 pts

4. **Historical Pattern Match** (0-15 pts)
   - Similar past setups: 0-6 pts
   - Sector positioning: 0-3 pts
   - Technical patterns: 0-3 pts
   - Timing factors: 0-3 pts

5. **Conviction and Risk** (0-10 pts)
   - Entry conviction: 0-6 pts
   - Risk/reward ratio: 0-4 pts

### Score Thresholds:
- **80-100 points**: Exceptional setup (target 70-75% win rate)
  - Full position size (10% × conviction multiplier)
  - High confidence entry

- **60-79 points**: Good setup (target 60-70% win rate)
  - Standard position size (75-100% of base)
  - Solid risk/reward

- **40-59 points**: Acceptable setup (target 50-60% win rate)
  - Reduced position size (50% of base)
  - Monitor closely

- **Below 40**: Skip (insufficient quality)
```

**4. Update Candidate Volume Expectations**
```diff
- Save top 50 candidates to `screener_candidates.json`
+ Save 300-500 catalyst-driven candidates to `screener_candidates.json`
+ (Tier 1: ~30-40%, Tier 2: ~30%, Tier 3: ~30%)
```

**5. Update Position Sizing Guidance**
```diff
- Each stock receives 10% of total account value
- Account always fully invested (10 positions × 10% = 100%)
+ Base allocation: 10% per position
+ Conviction multiplier: scorecard_total / 100
+ Final size = base × conviction × volatility_adj × market_regime_adj
+ Target: 5-8 positions (not required to fill 10)
+ Sector concentration: Max 2 per sector (3 if leading sector)
```

### Priority 2: MODERATE FIXES 🟡

**6. Update Composite Scoring Weights**
```diff
- Score and rank candidates by composite score:
-    - 40% Relative Strength
-    - 30% News/Catalyst Strength
-    - 20% Volume Surge
-    - 10% Technical Setup
+ Tier-aware weighting (screener level):
+ Tier 1: Catalyst is KING (40% catalyst weight)
+    - 20% RS, 20% News, 10% Volume, 10% Technical
+ Tier 2: Balanced weighting
+    - 25% RS, 20% News, 10% Volume, 5% Technical
+ Tier 3: RS and Technical critical
+    - 40% RS, 10% News, 5% Volume, 5% Technical
```

**7. Clarify Portfolio Target**
```diff
- Maintain an active portfolio of exactly 10 stocks at all times
+ Target portfolio: 5-8 positions (max 10)
+ Only enter positions scoring 40+ points
+ Quality over quantity - don't force fills
```

### Priority 3: NICE-TO-HAVE 🟢

**8. Add Deep Research Methodology Reference**
```markdown
## 🎓 METHODOLOGY: DEEP RESEARCH ALIGNMENT

This system implements the "Entry Quality Scorecard" methodology from professional
swing trading research (Deep Research v7.0, Dec 2025).

Key Principles:
1. **Screener**: Applies hard filters (price, volume, catalyst presence)
2. **Agent (You)**: Evaluates quality using 100-point scorecard
3. **Ranking**: Score then rank (not filter then accept)
4. **Sizing**: Conviction-based (not fixed 10%)
5. **Acceptance**: Score ≥40 points (not binary Tier 1 only)

This approach aligns with institutional best practices and academic research on
post-earnings announcement drift (PEAD) and catalyst-driven momentum.
```

---

## Testing Impact

### Before Fix (Current State)
**Screener → Agent Flow**:
```
Screener: Sends 300-500 Tier 1/2 candidates
           ↓
Agent Prompt: "TIER 1 ONLY", "RS≥3%", "Top 50"
           ↓
Claude: Confusion, over-filtering
           ↓
Result: Accepts 1-2 stocks (0.4% acceptance)
```

### After Fix (Expected)
**Screener → Agent Flow**:
```
Screener: Sends 300-500 Tier 1/2 candidates
           ↓
Agent Prompt: "Tier 1 & 2 accepted", "RS for scoring", "300-500 expected"
           ↓
Claude: Uses 100-point scorecard, accepts 40+ scores
           ↓
Result: Accepts 10-20 stocks (3-6% acceptance)
           ↓
Final Portfolio: Best 5-8 by conviction sizing
```

**Expected Improvement**:
- Acceptance rate: 0.4% → 3-6% (7-15x increase)
- Daily positions: 1-2 → 5-8 (3-4x increase)
- Tier 2 inclusion: 0% → 30-40% (major diversification)
- RS range: Expects all positive → Accepts any (aligns with code)

---

## Conclusion

**The agent prompt (PROJECT_INSTRUCTIONS.md) is fundamentally misaligned with:**
1. ❌ Deep Research methodology
2. ❌ Current code implementation
3. ❌ Entry Quality Scorecard framework
4. ❌ Conviction-based sizing
5. ❌ Tier 1/2 acceptance strategy

**This explains the 0.4% acceptance rate.**

Claude receives mixed signals:
- **Prompt says**: "Tier 1 only, RS≥3%, top 50 stocks, 10% fixed"
- **Data shows**: "Tier 1/2/3, any RS, 300-500 stocks, varying quality"
- **Code does**: "Reject Tier 3, accept Tier 1/2, conviction sizing"

**Fix Priority**: 🚨 **URGENT** - Update PROJECT_INSTRUCTIONS.md before next trading session

**Expected Impact**: 7-15x improvement in acceptance rate, enabling 5-8 daily positions instead of 1-2.

---

**Status**: Critical misalignment identified, fixes specified
**Date**: December 17, 2025, 9:00 PM ET
**Priority**: Update before Dec 18 market open
