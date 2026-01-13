# Implementation Plan v5.7 - AI-First with Catastrophic Blocks Only
## Based on Third-Party Analysis - Jan 12, 2026

---

## Current State Assessment

**What's Working:**
- ✅ Screener finds quality candidates (40 stocks with catalysts)
- ✅ Claude makes informed recommendations (5 stocks today)
- ✅ Soft guard rails (v5.6) log technical warnings without blocking

**What's Broken:**
- ❌ **Decision blocker**: Tier + conviction hard vetoes override Claude
- ❌ **Execution blocker**: EXECUTE crashes + pending_positions.json gets cleared
- ❌ **Schema mismatch**: "Tier 1" vs "Tier1" causes false rejects
- ❌ **Strategy confusion**: Catalyst momentum system with pullback-entry rules

**Result:** 0 positions entered in 6 days despite valid recommendations

---

## The Core Problem (Third-Party Diagnosis)

> "You're straddling two strategies. You've encoded catalyst-momentum in the screener + GO prompt, but you still enforce a confirmation-based swing-entry (RS thresholds, factor minimums) as a hard veto."

**Three Silent Killers Still Active:**
1. **Tier validation hard-block** - Overrides screener's Claude classification
2. **Conviction factor counter** - Can veto Tier 1 catalyst if RS too low
3. **Tier 3 auto-reject** - Can conflict with screener/GO tiering

**Plus execution reliability issue:** BE validated but EXECUTE crashed

---

## Implementation Plan - 5 Steps

### **STEP 0: Make EXECUTE Unbreakable (DO THIS FIRST)**

**Problem:** `entry_mid_price` can be None, causing crash at line 6247

**Fix:**
```python
# Line 6202: When fetching mid_price from spread_check
entry_mid_price = spread_check.get('mid_price')

# Line 6247: Add fallback chain
if entry_mid_price is None or entry_mid_price <= 0:
    # Fallback 1: Use entry_price as mid
    entry_mid_price = entry_price
    print(f"   ℹ️  {ticker}: Mid-price unavailable, using entry price ${entry_price:.2f}")

if entry_mid_price is not None and entry_mid_price > 0:
    slippage_bps = ((entry_price - entry_mid_price) / entry_mid_price) * 10000
    # ... rest of slippage calculation
else:
    # Fallback 2: Set defaults if still None
    entry_mid_price = entry_price
    # ... set zero slippage
```

**Never clear pending_positions.json until orders confirmed:**
```python
# Line 6346: Don't delete on crash
# Wrap in try/finally or only delete after successful order placement
try:
    # ... order placement logic
    orders_placed = True
except Exception as e:
    print(f"⚠️  Order placement failed: {e}")
    print(f"   Pending positions preserved for retry")
    orders_placed = False

# Only delete if ALL orders processed (success or intentional skip)
if orders_placed or all_positions_processed:
    self.pending_file.unlink()
```

**Priority:** CRITICAL - Do this before changing decision logic

---

### **STEP 1: Establish ONE Trade Admission Authority**

**Decision: AI-First Admission (Recommended)**

**New logic:**
```
IF Claude says BUY with confidence HIGH or MEDIUM:
    ADMIT trade to pending_positions.json
    Subject to CATASTROPHIC blocks only

CATASTROPHIC blocks (hard reject):
    - VIX ≥35 (shutdown)
    - Macro blackout (FOMC, CPI)
    - Stock halted/delisted
    - Liquidity collapse (<$1M daily notional)
    - Data integrity failure (no price, no volume)

EVERYTHING else becomes soft flag for:
    - Position sizing
    - Entry style (full vs split)
    - Stop width
    - Risk monitoring
```

**Remove from hard blocks:**
- Conviction <3 factors → Becomes sizing modifier
- Tier recalculation mismatch → Use screener tier as authoritative
- Technical filters → Already soft (v5.6) ✓
- Entry timing → Already soft (v5.6) ✓

---

### **STEP 2: Fix Tier Handling (Bug + Design Flaw)**

**Immediate Bug Fix - Normalize Tier Strings:**

```python
# Add helper function at top of agent
def normalize_tier(tier_string):
    """Normalize tier format: 'Tier 1', 'Tier1', 'tier1' → 'TIER_1'"""
    if not tier_string:
        return None
    tier_clean = str(tier_string).upper().replace(' ', '_')
    # Ensure format: TIER_1, TIER_2, TIER_3
    if 'TIER' not in tier_clean:
        tier_clean = f'TIER_{tier_clean}'
    return tier_clean

# Use everywhere tiers are compared:
normalized_tier = normalize_tier(candidate.get('catalyst_tier'))
if normalized_tier == 'TIER_1':
    # ... Tier 1 logic
```

**Architectural Fix - Single Source of Truth:**

```python
# Line 5692-5701: Use screener tier as authoritative
screener_tier = screener_candidate.get('catalyst_tier')

if screener_tier:
    # Screener's Claude already classified - trust it
    tier_result['tier'] = normalize_tier(screener_tier)
    tier_result['tier_name'] = f'Screener Validated - {screener_tier}'
    tier_result['reasoning'] = 'Tier assigned by screener Claude analysis'
    tier_result['confidence'] = 'high'  # Screener did the analysis
else:
    # Only recalculate if screener tier missing/invalid
    tier_result = self.classify_catalyst_tier(catalyst_type, catalyst_details)
    tier_result['tier'] = normalize_tier(tier_result['tier'])
    tier_result['confidence'] = 'medium'  # Had to infer from type
```

**Remove tier hard-block from conviction:**

```python
# Line 3367-3373: REMOVE THIS HARD BLOCK
# OLD (WRONG):
if catalyst_tier not in ['Tier1', 'Tier 1']:
    return {'conviction': 'SKIP', ...}

# NEW (CORRECT):
# Let non-Tier-1 through, but size appropriately
# Tier 1: Full size (10-13%)
# Tier 2: Reduced size (5-7%)
# Tier 3: Minimum size (3-5%) or watchlist
```

---

### **STEP 3: Convert Conviction Factor Counter to Sizing (Not Veto)**

**New Conviction Logic:**

```python
# Line 3384-3395: Change from VETO to SIZING
if supporting_factors >= 7 and news_score >= 15 and vix < 25:
    conviction = 'HIGH'
    position_size = 13.0
elif supporting_factors >= 5 and news_score >= 10 and vix < 30:
    conviction = 'MEDIUM-HIGH'
    position_size = 11.0
elif supporting_factors >= 3 and news_score >= 5 and vix < 30:
    conviction = 'MEDIUM'
    position_size = 10.0
elif supporting_factors >= 1:  # CHANGED: Was else → SKIP
    conviction = 'LOW'
    position_size = 6.0  # Starter position
else:
    conviction = 'SKIP'
    position_size = 0.0

# But SKIP only happens if truly insufficient (0 factors)
# Not because of factor counting on a Tier 1 catalyst
```

**Remove conviction hard-block from validation:**

```python
# Line 5744-5746: REMOVE THIS HARD BLOCK
# OLD (WRONG):
if conviction_result['conviction'] == 'SKIP':
    validation_passed = False
    rejection_reasons.append(f"Conviction: {conviction_result['reasoning']}")

# NEW (CORRECT):
# Log conviction as context, adjust position size, but don't block
if conviction_result['conviction'] == 'SKIP':
    print(f"   ⚠️  Conviction risk flag: {conviction_result['reasoning']}")
    if 'risk_flags' not in buy_pos:
        buy_pos['risk_flags'] = []
    buy_pos['risk_flags'].append(f"conviction_low: {conviction_result['reasoning']}")
    # Still allow entry with minimum size (starter position)
    buy_pos['position_size_pct'] = 5.0  # Override to starter size
elif conviction_result['conviction'] == 'LOW':
    print(f"   ⚠️  Low conviction: {conviction_result['reasoning']}")
    buy_pos['position_size_pct'] = conviction_result['position_size_pct']  # 6%
```

---

### **STEP 4: Tier-Aware Position Sizing**

**New sizing matrix (replaces hard blocks):**

```python
def calculate_tier_aware_sizing(tier, conviction, risk_flags):
    """
    Determine position size based on tier + conviction + risk flags

    Tier 1 with HIGH conviction, no flags: 13%
    Tier 1 with MEDIUM conviction: 10%
    Tier 1 with LOW conviction: 6%
    Tier 1 with risk flags: Reduce by 20-40%

    Tier 2 with HIGH conviction: 8%
    Tier 2 with MEDIUM conviction: 6%
    Tier 2 with LOW conviction: 4%

    Tier 3: 3-4% maximum (or watchlist)
    """

    # Base size from tier
    if tier == 'TIER_1':
        base_sizes = {'HIGH': 13.0, 'MEDIUM-HIGH': 11.0, 'MEDIUM': 10.0, 'LOW': 6.0}
    elif tier == 'TIER_2':
        base_sizes = {'HIGH': 8.0, 'MEDIUM-HIGH': 7.0, 'MEDIUM': 6.0, 'LOW': 4.0}
    else:  # TIER_3
        base_sizes = {'HIGH': 4.0, 'MEDIUM-HIGH': 3.5, 'MEDIUM': 3.0, 'LOW': 0.0}

    position_size = base_sizes.get(conviction, 0.0)

    # Apply risk flag adjustments
    if risk_flags:
        num_flags = len(risk_flags)
        if num_flags >= 3:
            position_size *= 0.6  # 40% reduction
        elif num_flags >= 2:
            position_size *= 0.7  # 30% reduction
        elif num_flags >= 1:
            position_size *= 0.8  # 20% reduction

    return max(position_size, 3.0) if position_size > 0 else 0.0
```

---

### **STEP 5: Create Explicit Strategy Modes**

**Add to GO prompt and validation:**

```python
# Detect strategy mode based on catalyst + technical setup
def determine_strategy_mode(ticker, catalyst_type, timing_result):
    """
    Catalyst Breakout Mode: High RSI/extension is EXPECTED (catalyst driving momentum)
    Pullback Trend Mode: Entry near MAs is PREFERRED (technical swing trade)
    """

    catalyst_breakout_types = [
        'Contract_Win', 'FDA_Approval', 'Earnings_Beat',
        'M&A_Announcement', 'Product_Launch'
    ]

    if catalyst_type in catalyst_breakout_types:
        # Catalyst-driven: expect hot technicals
        mode = 'CATALYST_BREAKOUT'
        # RSI >70 and extended are NORMAL, not warning signs
        expected_characteristics = 'High RSI/extension acceptable'
    else:
        # Technical swing: prefer cooler entry
        mode = 'PULLBACK_TREND'
        expected_characteristics = 'Entry near support preferred'

    return {
        'mode': mode,
        'characteristics': expected_characteristics
    }

# Apply mode-appropriate rules:
if mode == 'CATALYST_BREAKOUT':
    # RSI/extension are informational only
    # Size based on conviction + tier
elif mode == 'PULLBACK_TREND':
    # RSI/extension can reduce size or delay entry
```

---

## What Gets Removed (Lines to Delete/Modify)

### **Delete These Hard Blocks:**

1. **Line 3367-3373** - Tier 1 requirement in conviction calculation
   ```python
   # DELETE THIS:
   if catalyst_tier not in ['Tier1', 'Tier 1']:
       return {'conviction': 'SKIP', ...}
   ```

2. **Line 5547-5549** - Tier 3 auto-reject
   ```python
   # DELETE THIS:
   if tier_result['tier'] == 'Tier3':
       validation_passed = False
       rejection_reasons.append(f"Tier 3 catalyst: {tier_result['reasoning']}")
   ```

3. **Line 5744-5746** - Conviction SKIP hard-block
   ```python
   # DELETE THIS:
   if conviction_result['conviction'] == 'SKIP':
       validation_passed = False
       rejection_reasons.append(f"Conviction: {conviction_result['reasoning']}")
   ```

### **Modify to Soft Flags:**

All three become logging + sizing adjustments, not rejections.

---

## 2-Day Test Protocol

**Run Jan 13-14 with changes:**

**Measure:**
1. **Entry rate**: Positions entered per day (expect 3-8 vs current 0)
2. **Risk flag frequency**: How many entries have 1+ risk flags
3. **1-day adverse excursion**: Worst drawdown on entry day
4. **5-day return distribution**: Win rate and avg return by day 5
5. **High RSI outcomes**: Do "extended + high RSI" entries win or lose?

**Success criteria:**
- Entries per day: 3-8 (vs 0 currently)
- Win rate: >45% (validate later if Claude's judgment is sound)
- No catastrophic failures (no halted stocks, no -15% days)

**If test fails:**
- Review which risk flags predicted losses
- Selectively re-enable specific hard blocks based on data
- But START with trusting Claude, then prove which overrides are needed

---

## Summary: What Changes

### **Before (Current v5.6):**
```
Screener (40 stocks)
  → Claude recommends (5 stocks)
    → Soft flags log warnings ✓
    → Tier hard-block rejects (2 stocks)
    → Conviction hard-block rejects (2 stocks)
    → Result: 1 stock to EXECUTE
      → EXECUTE crashes
      → 0 positions entered
```

### **After (Proposed v5.7):**
```
Screener (40 stocks)
  → Claude recommends (5 stocks)
    → Catastrophic blocks only (VIX, macro, halted)
    → Tier from screener = authoritative
    → Risk flags adjust sizing (not veto)
    → Conviction adjusts sizing (not veto)
    → Result: 3-5 stocks to EXECUTE
      → EXECUTE never crashes (fallback handling)
      → 3-5 positions entered
```

### **Key Philosophical Change:**

**OLD:** "AI recommends → Rules decide"
**NEW:** "AI decides → Rules modulate risk"

Claude is the admission authority. Factor counting is the risk modulator.

---

## Implementation Order (Priority)

1. **TODAY**: Fix EXECUTE crash (Step 0) - CRITICAL
2. **TODAY**: Fix tier normalization bug (Step 2) - HIGH
3. **TONIGHT**: Remove 3 hard blocks (Steps 1-3) - HIGH
4. **TOMORROW AM**: Deploy v5.7, test with real GO command
5. **2 DAYS**: Collect data, validate Claude's judgment
6. **JAN 15**: Review outcomes, decide if any overrides needed

---

## Questions for User Approval

1. **Do you approve removing conviction as a hard block?** (Make it sizing only)
2. **Do you approve using screener tier as authoritative?** (Stop recalculating)
3. **Do you approve AI-first admission?** (Claude decides, rules modulate)
4. **Should we implement all 5 steps or start with Step 0 (EXECUTE fix) only?**

---

**This plan aligns with third-party feedback: One clear decision authority (Claude), catastrophic blocks only, everything else as sizing/logging.**
