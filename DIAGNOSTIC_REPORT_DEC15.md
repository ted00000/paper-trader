# TEDBOT CRITICAL FAILURE - Diagnostic Report
**Date**: December 15, 2025
**Status**: System Non-Operational (Zero Trades in Weeks)
**Severity**: CRITICAL - Core Architecture Flaw

---

## Executive Summary

Tedbot has been running for weeks with **ZERO trades** despite claiming to follow best-in-class methodologies (IBD, Minervini, institutional quant strategies). The system is fundamentally broken due to a **screening architecture flaw** that violates every professional best practice researched.

**Root Cause**: The screener uses composite scoring to select top 50 candidates, allowing **Tier 3 signals (insider buying) to crowd out Tier 1 catalysts (earnings beats, M&A, FDA approvals)**. Professional systems use **tier-based prioritization with quotas**, not composite scoring.

**Impact**:
- 9 of 10 stocks Claude wanted to trade (NVDA, LLY, ORCL, MSFT, AVGO, COST, GS, XOM, ABBV) were **filtered out before reaching AI analysis**
- Screener output: 76% Tier 3 (38/50), 12% Tier 2 (6/50), 2% Tier 1 (1/50)
- Professional systems: 40-60% Tier 1, 20-40% Tier 2, 0-20% Tier 3

---

## What We Built vs. What We Should Have Built

### Our Stated Goals (from TEDBOT_OVERVIEW.md)

1. **"90-92% of best-in-class professional trader performance"**
2. **"Event-driven momentum trading (3-7 day holds)"**
3. **"High-conviction, concentrated positions (10 max) with strict risk management"**
4. **"Performance Target: 65-70% win rate, +12-15% avg gain on winners"**

### What Best-in-Class Actually Does

#### IBD (Investor's Business Daily) - The Model We Claim to Follow

**What IBD Does**:
- Catalyst is a **mandatory requirement**, not a scoring factor
- The "N" in CAN SLIM (New Products/Services) is a **GO/NO-GO filter**
- William O'Neil's research: **95% of winning stocks had a fundamental spark**
- IBD 50 list = Top 50 stocks **that already passed catalyst filter**
- Composite Rating is used **AFTER** catalyst filter, not before

**What We Do**:
- ❌ Catalyst is a **scoring component** weighted against technical factors
- ❌ Tier 3 signals (insider buying) compete with Tier 1 catalysts
- ❌ Composite score ranks **across all tiers**, not within tiers
- ❌ No catalyst quality filter - insider buying = 100 points, same as M&A

**Deviation**: We claim to follow IBD but **violate the core CAN SLIM principle** - catalyst must be present FIRST, then you rank by other factors.

---

#### Mark Minervini SEPA - The Funnel We Should Use

**What Minervini Does**:
- **6,000 stocks** → Fundamental screen → **1,000 stocks**
- **1,000 stocks** → Stage 2 filter → **200-300 stocks**
- **200-300 stocks** → Trend Template → **50-100 stocks**
- **50-100 stocks** → Manual review → **10-20 watchlist**
- **10-20 watchlist** → VCP pattern → **1-3 actual trades**

**What We Do**:
- ❌ **993 stocks** → RS filter → **253 stocks**
- ❌ **253 stocks** → Composite score → **50 candidates** (stop here!)
- ❌ **50 candidates** → AI analysis → **0 trades** (broken!)

**Deviation**: We stop the funnel at 50 candidates (should be 150-200), and we use **composite scoring** (should be **sequential filters**). Minervini would NEVER rank insider-buying stocks against earnings-beat stocks in one list.

---

#### Renaissance Technologies - The Quant Model We Should Emulate

**What Renaissance Does** (based on research):
- **Separate pipelines** for different signal types (catalyst vs. momentum vs. mean-reversion)
- **Hard constraints** on liquidity and catalyst quality (not scoring factors)
- **Statistical probabilities** analyzed per catalyst tier, not mixed
- **Multi-factor models** combine signals **within** strategy types, not across

**What We Do**:
- ❌ **One pipeline** mixes all signal types
- ❌ **Soft weighting** for catalyst quality (40% weight vs 30% technical)
- ❌ **No separation** between Tier 1 (immediate price impact) and Tier 3 (3-6 month signals)

**Deviation**: Renaissance would run **separate screens** for "M&A candidates" (Tier 1) vs. "insider accumulation plays" (Tier 3). We mix them and wonder why we get garbage.

---

## The Smoking Gun: Today's Screening Results

### What Claude Wanted to Trade (08:50 AM run - no screener data)

When the screener didn't finish in time, Claude did its own research and selected:

1. **NVDA** - Tier 1: AI chip earnings beat, guidance raised 3x, Blackwell launch
2. **AVGO** - Tier 1: AI chip earnings beat, guidance raised 40%
3. **LLY** - Tier 1: Zepbound drug sales exceeding forecasts, capacity expansion
4. **ORCL** - Tier 1: Cloud revenue beat, 50%+ growth acceleration
5. **COST** - Tier 1: Consistent earnings beats, membership fee increase
6. **GS** - Tier 1: Q3 trading revenue beat, M&A pipeline building
7. **XOM** - Tier 2: Energy sector rotation, OPEC+ production discipline
8. **MSFT** - Tier 1: Azure AI guidance raise, Copilot enterprise rollout
9. **ABBV** - Tier 1: Skyrizi/Rinvoq beating estimates, offsetting Humira
10. **AMD** - Tier 2: MI300 AI chip production ramp, $4B+ orders

**Claude's portfolio composition**:
- **Tier 1**: 8 stocks (80%)
- **Tier 2**: 2 stocks (20%)
- **Tier 3**: 0 stocks (0%)

---

### What the Screener Actually Provided (08:55 AM run - screener finished)

**Overlap Check**:
- ✗ NVDA - NOT IN SCREENER (filtered out!)
- ✗ AVGO - NOT IN SCREENER (filtered out!)
- ✗ LLY - NOT IN SCREENER (filtered out!)
- ✗ ORCL - NOT IN SCREENER (filtered out!)
- ✗ COST - NOT IN SCREENER (filtered out!)
- ✗ GS - NOT IN SCREENER (filtered out!)
- ✗ XOM - NOT IN SCREENER (filtered out!)
- ✗ MSFT - NOT IN SCREENER (filtered out!)
- ✗ ABBV - NOT IN SCREENER (filtered out!)
- ✓ AMD - IN SCREENER (only 1 of 10!)

**Screener's actual output** (50 candidates):
- **Tier 1**: 1 stock (2%) - ARQT with **fake FDA news** (promotional article, not approval)
- **Tier 2**: 6 stocks (12%) - AMD, plus 5 analyst upgrades
- **Tier 3**: 38 stocks (76%) - Insider buying ONLY, no fundamental catalyst
- **No catalyst**: 5 stocks (10%) - Pure momentum plays

**What Claude did with screener data**: Rejected ALL 50 candidates, made 0 trades

---

## Why the Screener Filters Out Winners

### The Composite Scoring Formula (Lines 1931-1970)

```python
# Tier 1: Catalyst is KING (40% weight)
base_score = (
    rs_result['score'] * 0.20 +          # RS: 20%
    technical_result['score'] * 0.10 +   # Technical: 10%
    news_result['scaled_score'] * 0.40 + # News/Catalyst: 40%
    volume_result['score'] * 0.30        # Volume: 30%
)
```

**Problem 1**: Insider buying gets 100 points in the "catalyst" bucket. M&A announcements get ~80 points. **They compete on equal footing.**

**Problem 2**: A stock with:
- Tier 3 (insider buying): 100 points × 0.40 = 40
- Great technicals: 90 points × 0.10 = 9
- High volume: 100 points × 0.30 = 30
- **Total: 79 points**

Beats a stock with:
- Tier 1 (earnings beat): 80 points × 0.40 = 32
- Weak technicals: 40 points × 0.10 = 4
- Normal volume: 50 points × 0.30 = 15
- **Total: 51 points**

**Result**: **Tier 3 with good technicals > Tier 1 with weak technicals**. This is BACKWARDS.

---

### The Selection Logic (Line 2315)

```python
# Take top N
top_candidates = candidates[:TOP_N_CANDIDATES]
```

This sorts ALL candidates by composite score and takes top 50. **No tier awareness.**

**What happens**:
1. 253 stocks pass RS filter
2. All 253 get composite scores (Tier 1, Tier 2, Tier 3 mixed together)
3. Sort by composite score
4. Take top 50

**Result**:
- 38 Tier 3 stocks with high technical scores beat out
- 9 Tier 1 stocks with weak technical scores

**NVDA example** (speculative reconstruction):
- Tier 1 catalyst: 85 points × 0.40 = 34
- But: Price far above 50d MA (overextended): 30 points × 0.10 = 3
- Volume normal (not 3x): 60 points × 0.30 = 18
- RS strong: 90 points × 0.20 = 18
- **Total: 73 points** (ranks ~#60, doesn't make top 50!)

**CGAU example** (actually in screener):
- Tier 3 (40x insider buys!): 100 points × 0.40 = 40
- Perfect Stage 2: 95 points × 0.10 = 9.5
- Volume good: 80 points × 0.30 = 24
- RS great: 95 points × 0.20 = 19
- **Total: 92.5 points** (ranks #4!)

---

## Why Our "Best Practices Alignment" Failed

### What We Did Right

1. ✅ **IBD-style RS percentile ranking** (Phase 3.1) - Top 20% filter works
2. ✅ **Sector rotation detection** (Phase 3.2) - Correctly identifies leading sectors
3. ✅ **Stage 2 alignment** (Minervini criteria) - Good technical filter
4. ✅ **Institutional signals** (options flow, dark pool) - Adds conviction
5. ✅ **Cluster-based conviction** (Phase 4.1) - Prevents double-counting in GO command
6. ✅ **VIX regime + breadth filter** (Phase 4.2/4.5) - Market regime awareness

**These are EXCELLENT enhancements... for the GO command.** They're wasted if the screener never sends Tier 1 stocks to the GO command!

---

### What We Did Wrong

1. ❌ **Composite scoring as primary filter** - Professional systems use **tier-based quotas**
2. ❌ **Insider buying = Tier 3 catalyst** - Research shows it's a **quality signal**, not a swing-trade catalyst
3. ❌ **50 candidate limit** - Minervini outputs 100-200 for manual review, we output 50 for AI
4. ❌ **No tier quotas** - Professional systems guarantee minimum Tier 1 representation
5. ❌ **One pipeline for all signals** - Institutions run separate pipelines for different opportunity types

---

### Where We Misunderstood "Best-in-Class"

#### Misconception 1: "Composite scoring is sophisticated"

**What we thought**: "Professional systems use multi-factor models, so composite scoring is advanced."

**Reality**: Professional systems use multi-factor models **AFTER tier-based filtering**. IBD's Composite Rating is applied to stocks that **already have catalysts**. We're using composite scoring to **SELECT which catalysts to analyze**, which is backwards.

---

#### Misconception 2: "Insider buying is a Tier 3 catalyst"

**What we thought**: "Tier 1 = M&A/FDA, Tier 2 = upgrades, Tier 3 = insider buying. All are catalysts, just different quality."

**Reality**: Academic research shows insider buying is **NOT a catalyst** - it's a **quality signal** that predicts 6-12 month outperformance, not 3-7 day swing trades. It should be a **tiebreaker** (enhances Tier 1/2 stocks), not a standalone catalyst competing with earnings beats.

The [Catalyst Insider Buying Fund (INSAX)](https://catalystmf.com/funds/catalyst-insider-buying-fund/) even says: "We combine insider buying WITH fundamental analysis and technical setups." They don't trade insider buying alone.

---

#### Misconception 3: "Tight screening improves quality"

**What we thought**: "Output only top 50 candidates → AI gets highest quality → Better trades."

**Reality**: Mark Minervini screens 1,000 → 300 → 100 → 20 → 3 trades. The screener's job is to **cast a wide net of QUALIFIED candidates** (all have catalysts, all in Stage 2). The trader's/AI's job is to **pick the best setups**.

By screening to only 50, we're forcing the screener to do BOTH jobs:
- Filter to qualified candidates (it does this via RS, Stage 2, liquidity)
- Pick the absolute best setups (this should be the AI's job!)

Result: We filter out NVDA because "it's overextended" - but that's a **SETUP decision** (AI's job), not a **QUALIFICATION decision** (screener's job).

---

#### Misconception 4: "More factors = better system"

**What we thought**: "We added RS percentile (Phase 3.1), sector rotation (3.2), institutional signals (3.3), cluster-based conviction (4.1), breadth filter (4.2)... we're building a sophisticated system!"

**Reality**: We added excellent **GO command enhancements** but broke the **screener → GO pipeline**. It's like building a Ferrari engine (GO command) but the gas tank (screener) is empty.

All those enhancements are useless if the screener never sends NVDA, LLY, ORCL to the GO command.

---

## The Evidence Trail: How We Got Here

### Phase 0-2: Foundation (Working)
- Basic screener with catalyst detection
- Composite scoring introduced
- No issues reported - system was making trades

### Phase 3: RS & Sector Intelligence (Started Breaking)
- Added RS percentile ranking (good!)
- Added sector rotation (good!)
- Added institutional signals (good!)
- **But**: Composite score now has MORE factors, making it HARDER for Tier 1 stocks to rank high
- **Result**: Screener starts filtering out good stocks

### Phase 4: Risk Optimization (Fully Broken)
- Added cluster-based conviction (good for GO command!)
- Added market breadth filter (good for GO command!)
- Added liquidity filter (good for screener!)
- **But**: We're so focused on the GO command, we don't notice the screener is broken
- **Result**: Zero trades for weeks, blamed on "low catalyst environment"

### December 15: The Revelation
- Screener runs at 8:50 AM with stale data → Claude does own research → Finds 10 Tier 1 stocks
- Screener finishes at 8:55 AM → Provides 50 candidates → Claude rejects all 50
- Investigation reveals: **Only 1 of Claude's 10 picks made it through screener**

---

## The "Low Catalyst Environment" Lie

We told ourselves: "There are no Tier 1 opportunities right now, the market is in a low-catalyst phase."

**The truth**:
- Claude found 10 Tier 1 opportunities when forced to do its own research
- The screener filtered out 9 of them
- Market breadth is 80% (HEALTHY)
- VIX is 15.7 (VERY_LOW)
- We're in a **HIGH opportunity environment**, our screener just can't see it

---

## Competitive Analysis: What We Should Have Built

### IBD Approach (What We Claim to Follow)

**Screening Workflow**:
1. Start with 8,000+ stocks
2. **Catalyst Filter** (GO/NO-GO): Must have NEW catalyst (earnings, product, M&A)
3. **EPS Filter**: 25%+ earnings growth
4. **Sales Filter**: 20%+ revenue growth
5. **Composite Rating**: Now rank the qualified stocks by 100-point scale
6. **Output**: IBD 50 list (top 50 stocks that PASSED catalyst filter)

**Key Insight**: Composite Rating is used **AFTER** catalyst filter, not instead of it.

**Our Deviation**: We use composite score to SELECT which stocks to analyze for catalysts. IBD would reject our approach immediately.

---

### Minervini SEPA (What We Should Emulate)

**Screening Workflow**:
1. **Fundamental Screen**: 6,000 → 1,000 stocks (earnings growth 25%+, sales 20%+)
2. **Stage 2 Filter**: 1,000 → 200-300 stocks (price above 150/200d MA, MAs aligned)
3. **Trend Template**: 200 → 50-100 stocks (specific MA alignment, volume)
4. **Manual Review**: 50-100 → 10-20 watchlist (VCP patterns, setup quality)
5. **Trade Execution**: 10-20 → 1-3 positions (final entry timing)

**Output at each stage**:
- 1,000 stocks have fundamentals
- 200-300 stocks have technical setup
- 50-100 stocks have ideal pattern
- 10-20 stocks ready to trade
- 1-3 actual positions

**Our Deviation**: We jump from 253 stocks → 50 candidates → 0 trades. We skip the "100-200 for deep review" stage entirely.

---

### Renaissance Technologies (Quant Model)

**Known Principles**:
- **Separate signal pipelines**: Mean-reversion, momentum, catalyst-driven are DIFFERENT strategies
- **Hard constraints**: Liquidity and catalyst quality are filters, not weights
- **Statistical probabilities**: Each signal type analyzed independently, then combined
- **Backtesting**: Every signal validated over 20+ years before deployment

**Our Deviation**:
- **One pipeline** for all signal types
- **Soft weighting** (40% catalyst, 30% volume, 20% RS, 10% technical)
- **No separation** between Tier 1 (immediate) and Tier 3 (lagging) signals

Renaissance would say: "You're mixing alpha signals (catalysts) with beta signals (momentum). These require different holding periods and risk models. Why are you ranking them together?"

---

## The Fix We Need (Summary)

### Immediate (Critical Path to Trades)

1. **Increase TOP_N_CANDIDATES**: 50 → 150
   - Minervini outputs 100-200 for review
   - We output 150 from 253 RS-passing stocks (60% pass rate)

2. **Implement tier-based quotas**:
   - Top 60 Tier 1 (guarantee all Tier 1 reach AI)
   - Top 50 Tier 2 (analyst upgrades, contracts)
   - Top 40 Tier 3 (insider buying enhancers)
   - Sort WITHIN tiers by composite score, not across tiers

3. **Strengthen Tier 3 penalties**:
   - Pure insider buying (no Tier 1/2 support): -15 points
   - Multiple insiders + weak technicals: -10 points
   - Prevents insider-only stocks from ranking high

### Medium-Term (System Improvement)

4. **Separate catalyst validation**:
   - ARQT "Tier 1 - FDA News" is fake (promotional article)
   - Need stricter FDA approval detection (press releases, SEC 8-Ks)
   - Tier 1 should be <5% false positives

5. **Redefine insider buying**:
   - Move from Tier 3 catalyst → Secondary filter (enhancer)
   - Used as tiebreaker between equal Tier 1/2 stocks
   - Not a standalone catalyst for screener output

6. **Sequential filters (like Minervini)**:
   - Stage 1: RS filter (currently doing this)
   - Stage 2: Catalyst tier filter (Tier 1/2 only? or include Tier 3?)
   - Stage 3: Technical filter (Stage 2 alignment)
   - Stage 4: Composite score (rank within tier)

### Long-Term (Architecture Redesign)

7. **Separate pipelines for signal types**:
   - Catalyst-driven pipeline (Tier 1/2): 3-7 day holds
   - Momentum pipeline (Tier 3 + technicals): 10-20 day holds
   - Don't mix signals with different time horizons

8. **Backtesting validation**:
   - Test: "Does Tier 3 insider buying produce 3-7 day swing gains?"
   - If no → Remove from swing trading system
   - If yes → Validate win rate and avg gain vs Tier 1

---

## Accountability: Why This Wasn't Caught Earlier

### Red Flags We Ignored

1. **Week 1**: "No trades today, probably low catalyst environment" ✗
2. **Week 2**: "Still no trades, market might be choppy" ✗
3. **Week 3**: "System is being disciplined, waiting for quality" ✗
4. **Week 4 (Dec 15)**: "Market HEALTHY (80% breadth), VIX LOW (15.7), still no trades... something is wrong" ✓

We blamed external factors (market conditions) instead of auditing the screener output.

### What We Should Have Done

**Week 1 diagnostic**:
- Check screener output: "Why are 76% Tier 3?"
- Spot check: "Where is NVDA? Where is MSFT? Where is LLY?"
- Compare to IBD 50: "Our list looks nothing like theirs"

**Lesson**: When a system produces ZERO output for weeks, the system is broken - not the market.

---

## Conclusion

We built a theoretically sophisticated system with excellent enhancements (RS percentile, sector rotation, cluster-based conviction, breadth filter) but **broke the fundamental architecture** by using composite scoring instead of tier-based prioritization.

**The irony**: We researched IBD, Minervini, and institutional approaches... then built the OPPOSITE of what they do.

- **IBD**: Catalyst is a required filter → We made it a weighted score
- **Minervini**: Sequential filters, wide → narrow funnel → We use one composite score
- **Renaissance**: Separate pipelines per signal type → We mix everything together

**The result**: A system that's been running for weeks with perfect market conditions (80% breadth, low VIX) but produces zero trades because the screener filters out every high-quality stock before the AI sees it.

**The fix**: Implement tier-based quotas (like professionals do) to guarantee Tier 1 stocks reach AI analysis, regardless of their composite score ranking.

---

## Appendix: Supporting Data

### Today's Screener Output (Full Breakdown)

**Tier 1 (1 stock - 2%)**:
1. ARQT - "Tier 1 - FDA News" (FALSE POSITIVE - promotional article, not approval)

**Tier 2 (6 stocks - 12%)**:
1. AMD - "Tier 2 - Analyst Upgrade Trend (+4 StrongBuy)"
2. [5 others]

**Tier 3 (38 stocks - 76%)**:
1. BCAX - "Tier 3 - Insider Buying (7x)"
2. ASTS - "Tier 3 - Insider Buying (9x)"
3. CGAU - "Tier 3 - Insider Buying (40x)"
4. [35 others - ALL insider buying only]

**No Catalyst (5 stocks - 10%)**:
- Pure momentum/technical plays

---

### Claude's Rejected Analysis (10:15 AM run)

Claude reviewed all 50 screener candidates and rejected them with these findings:

**ARQT** (Tier 1 - FDA News):
- ❌ News Review: "Biotech stock could cure portfolio pain" (promotional)
- ❌ No FDA approval TODAY, generic promotional content
- ❌ Catalyst Grade: Tier 3 (promotional article, not real catalyst)

**AMD** (Tier 2 - Analyst Upgrade):
- ❌ News Review: Articles about NVIDIA (competitor), general AI sector
- ❌ No AMD-specific catalyst, sector momentum alone = Tier 2
- ❌ Decision: REJECT (not Tier 1)

**All Tier 3 stocks**:
- ❌ Insider buying alone is NOT a Tier 1 catalyst
- ❌ Strong relative strength alone is NOT a Tier 1 catalyst
- ❌ Decision: REJECT ALL

**Claude's conclusion**: "ZERO TIER 1 CATALYSTS IDENTIFIED"

**The reality**: There ARE Tier 1 catalysts (NVDA, LLY, ORCL, MSFT) - they just didn't make it through the screener!

---

**End of Report**
