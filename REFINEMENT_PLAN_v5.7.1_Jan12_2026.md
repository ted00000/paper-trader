# Refinement Plan v5.7.1 - Third-Party Feedback Implementation
## January 12, 2026

---

## Executive Summary

Third-party reviewer validated v5.7 architecture (85-90% agreement) but identified 5 refinements:
1. Make decision explicit (ENTER/ENTER_SMALL/PASS)
2. Narrow sizing for testing phase (6-10% vs 5-13%)
3. Add portfolio-level exposure warnings
4. Add risk flag severity levels
5. Watch for Claude optimism bias

**Priority:** Implement #1 and #2 before tomorrow's GO command (Jan 13, 8:45 AM)
**Timeline:** #3, #4, #5 can be monitoring/post-processing during 5-7 day test

---

## Feedback Analysis

### ✅ What We Got Right (No Changes Needed)

1. **AI-first admission authority** - "Correct architectural move"
2. **Exposing all technical data** - "Fixes hidden rules anti-pattern completely"
3. **Thresholds as guidelines** - "Exactly how real traders think"
4. **Position sizing as risk dial** - "Professional-grade portfolio thinking"

### ⚠️ Where to Refine (Action Items)

**Refinement #1: Make Confidence Explicit**
> "Claude must explicitly choose ENTER | ENTER_SMALL | PASS. Right now you infer intent from sizing + language. That works... until it doesn't."

**Why it matters:**
- Prevents "accidental trades" when Claude is unsure
- Gives Learning a clean signal: Claude wanted this or not
- Makes intent auditable

**Current state:**
```json
{
  "ticker": "BE",
  "position_size": 7.0,
  "confidence": "High",  // Free text
  "thesis": "..."
}
```

**Proposed state:**
```json
{
  "ticker": "BE",
  "decision": "ENTER",  // ENTER | ENTER_SMALL | PASS
  "confidence_level": "HIGH",  // HIGH | MEDIUM | LOW
  "position_size_pct": 7.0,
  "thesis": "..."
}
```

---

**Refinement #2: Narrow Sizing for Testing Phase**
> "The 5-13% range is fine long-term, but for first live validation, it's wider than I'd prefer. Testing decision correctness, not capital efficiency yet."

**Recommendation:** Cap at 6-10% for first 5-10 trading days

**Why:**
- Cleaner attribution (is Claude's directional judgment right?)
- Lower emotional drawdown during validation
- Better diagnostics without volatility masking signal
- Widen later once confidence earned

**Implementation:**
- Update GO prompt: "Testing phase - use 6-10% range"
- After 15-20 successful trades, widen to 5-13%

---

**Refinement #3: Add Portfolio-Level Exposure Warnings**
> "Claude could theoretically stack 8 names all at 10-13% all in same sector. Show advisory signals like 'Tech exposure now 42%'"

**Current:** No portfolio-level context shown to Claude
**Proposed:** Add to GO prompt before decisions

```
CURRENT PORTFOLIO EXPOSURE:
- Total positions: 7/10 (70% capital deployed)
- Sector concentration: Technology 35%, Healthcare 25%, Energy 10%
- Top 3 positions: 31% of capital (NVDA 12%, AAPL 11%, MSFT 8%)
- Risk level: MEDIUM (2 positions with 2+ risk flags)

ℹ️  Advisory (not blocking): Avoid >40% in single sector, >35% in top 3 positions
```

**Not a veto** - Claude can still decide, but has context

---

**Refinement #4: Add Risk Flag Severity Levels**
> "Right now all risk flags logged equally. Distinguish: structural risk vs technical heat vs execution risk."

**Current:**
```python
buy_pos['risk_flags'] = [
    "tier3: Minor catalyst",
    "high_rsi: RSI 80",
    "subpar_volume: 1.2x average"
]
```

**Proposed:**
```python
buy_pos['risk_flags'] = [
    {"flag": "tier3", "severity": "HIGH", "description": "Minor catalyst"},
    {"flag": "high_rsi", "severity": "MEDIUM", "description": "RSI 80"},
    {"flag": "subpar_volume", "severity": "LOW", "description": "1.2x average"}
]
```

**Severity levels:**
- **HIGH:** Structural risks (Tier 3, no catalyst, failed earnings)
- **MEDIUM:** Technical heat (RSI >75, extended >15%, parabolic move)
- **LOW:** Execution risks (volume 1.2-1.5x, wide spread <2%)

---

**Refinement #5: Watch for Optimism Bias**
> "When you give LLM freedom + sizing, it can rationalize marginal setups, over-trust narrative, underweight tail risk."

**Red flags to monitor:**
- 5-7 trades/day with few PASS decisions
- All positions sized 7-8% (no variance = not really deciding)
- "Everything is MEDIUM confidence"
- Vague thesis statements ("strong momentum", "good setup")

**Mitigation:**
- After 2 days, audit GO logs for decision distribution
- If <20% PASS rate, tighten confidence language in prompt
- Example: "PASS is expected on 30-40% of candidates - quality over quantity"

---

## Implementation Priority

### **Phase 1: Pre-Launch (Tonight - Jan 12)**
Implement before tomorrow's GO command:

**Task 1.1: Update GO Prompt - Add Explicit Decision Field**
```python
# Add to GO prompt JSON structure:
"buy": [
  {
    "ticker": "AAPL",
    "decision": "ENTER",  # NEW: ENTER | ENTER_SMALL | PASS (required)
    "confidence_level": "HIGH",  # NEW: HIGH | MEDIUM | LOW (required)
    "position_size_pct": 8.0,
    "catalyst": "Earnings_Beat",
    "sector": "Technology",
    "thesis": "One sentence thesis"
  }
]

# Add guidance:
**DECISION TYPES (Required):**
- ENTER: Standard entry with sizing 6-10% based on conviction + risk
- ENTER_SMALL: Reduced entry 5-6% for speculative/uncertain setups
- PASS: Do not enter (catalyst interesting but insufficient conviction or excessive risk)

Expect PASS on 30-40% of candidates - quality over quantity is critical.
```

**Task 1.2: Narrow Position Sizing Range for Testing**
```python
# Update GO prompt sizing guidance:
**POSITION SIZING = RISK DIAL (TESTING PHASE - TIGHTENED RANGE):**
For initial validation (first 5-10 days), use narrower band:
- 9-10%: High conviction - strong catalyst + aligned technicals
- 7-8%: Good opportunity - catalyst strong, some technical heat
- 6-7%: Starter position - solid catalyst, multiple risk flags
- 5-6%: ENTER_SMALL only - speculative setup

Once system validated (15-20 successful trades), range will widen to 5-13%.
```

**Task 1.3: Update JSON Parsing to Handle New Fields**
```python
# In validation logic, check for new fields:
decision = buy_pos.get('decision', 'ENTER')  # Default to ENTER for backward compatibility
confidence_level = buy_pos.get('confidence_level', 'MEDIUM')

# PASS decisions don't reach validation - Claude filtered them
# ENTER_SMALL caps position size:
if decision == 'ENTER_SMALL':
    buy_pos['position_size_pct'] = min(buy_pos.get('position_size_pct', 6.0), 6.0)
```

---

### **Phase 2: Day 1-2 (Jan 13-14) - Monitoring**

**Task 2.1: Audit Decision Distribution**
```bash
# After each GO command:
grep -E "decision.*ENTER|decision.*PASS" daily_reviews/go_*.json | wc -l

# Expected healthy distribution:
# ENTER: 50-60% of candidates
# ENTER_SMALL: 10-20% of candidates
# PASS: 30-40% of candidates (implied - not in buy array)
```

**Task 2.2: Monitor Position Sizing Variance**
```bash
# Check if Claude is actually varying sizes:
jq '.buy[].position_size_pct' portfolio_data/pending_positions.json

# Red flag: All positions 7-8% (no real risk modulation)
# Healthy: Mix of 6%, 7%, 8%, 9%, 10%
```

**Task 2.3: Watch for Optimism Bias Signals**
- Thesis statements becoming generic ("strong momentum", "good catalyst")
- Few risk flags logged despite technical heat visible
- Confidence always MEDIUM or HIGH, never LOW
- ENTER_SMALL never used

---

### **Phase 3: Day 3-7 (Jan 15-19) - Refinements**

**Task 3.1: Add Portfolio Exposure Warnings**
```python
# In GO command, before screener section:
def format_portfolio_exposure_summary(current_positions):
    """Calculate and format portfolio-level exposure warnings"""
    total_exposure = sum(p['position_size'] for p in current_positions)

    # Sector concentration
    sector_exposure = {}
    for pos in current_positions:
        sector = pos.get('sector', 'Unknown')
        sector_exposure[sector] = sector_exposure.get(sector, 0) + pos['position_size']

    # Top 3 positions
    sorted_positions = sorted(current_positions, key=lambda x: x['position_size'], reverse=True)
    top3_exposure = sum(p['position_size'] for p in sorted_positions[:3])

    # Risk flag summary
    high_risk_count = sum(1 for p in current_positions if len(p.get('risk_flags', [])) >= 2)

    output = "CURRENT PORTFOLIO EXPOSURE:\n"
    output += f"- Total positions: {len(current_positions)}/10 ({total_exposure/current_account_value*100:.0f}% capital)\n"
    output += f"- Sector concentration: {', '.join(f'{k} {v/current_account_value*100:.0f}%' for k,v in sector_exposure.items())}\n"
    output += f"- Top 3 positions: {top3_exposure/current_account_value*100:.0f}% of capital\n"
    output += f"- Risk level: {'HIGH' if high_risk_count >= 3 else 'MEDIUM' if high_risk_count >= 1 else 'LOW'}\n\n"
    output += "ℹ️  Advisory: Avoid >40% single sector, >35% top 3 positions (not blocking)\n\n"

    return output
```

**Task 3.2: Implement Risk Flag Severity Levels**
```python
def classify_risk_flag_severity(flag_type, value):
    """Classify risk flag severity: HIGH | MEDIUM | LOW"""

    severity_rules = {
        'tier3': 'HIGH',  # Structural risk
        'low_conviction': 'HIGH',  # Fundamental doubt
        'high_rsi': 'MEDIUM' if value < 85 else 'HIGH',  # Technical heat
        'extended': 'MEDIUM' if value < 25 else 'HIGH',  # Extension level
        'subpar_volume': 'LOW' if value > 1.2 else 'MEDIUM',  # Execution risk
        'weak_trend': 'LOW',  # ADX concern
    }

    return severity_rules.get(flag_type, 'MEDIUM')

# Update risk flag storage:
buy_pos['risk_flags'] = [
    {
        'flag': 'high_rsi',
        'severity': 'MEDIUM',
        'value': 80,
        'description': 'RSI 80 (overbought)'
    }
]
```

**Task 3.3: Add Optimism Bias Check**
```python
# After GO command completes:
def check_optimism_bias(decisions_json):
    """Detect if Claude is over-optimistic"""

    buy_count = len(decisions_json.get('buy', []))
    enter_small_count = sum(1 for b in decisions_json['buy'] if b.get('decision') == 'ENTER_SMALL')
    low_confidence_count = sum(1 for b in decisions_json['buy'] if b.get('confidence_level') == 'LOW')

    # Assuming 15 candidates total (from screener)
    candidates_total = 15
    pass_rate = (candidates_total - buy_count) / candidates_total if candidates_total > 0 else 0

    warnings = []

    if pass_rate < 0.20:
        warnings.append(f"⚠️  Low PASS rate ({pass_rate*100:.0f}%) - Claude may be over-optimistic")

    if enter_small_count == 0 and buy_count > 5:
        warnings.append(f"⚠️  No ENTER_SMALL decisions - Claude not using caution sizing")

    if low_confidence_count == 0 and buy_count > 5:
        warnings.append(f"⚠️  No LOW confidence entries - all decisions rated MEDIUM+ may indicate bias")

    # Check sizing variance
    sizes = [b.get('position_size_pct', 0) for b in decisions_json['buy']]
    if sizes and (max(sizes) - min(sizes)) < 2.0:
        warnings.append(f"⚠️  Low sizing variance ({min(sizes):.1f}-{max(sizes):.1f}%) - may not be risk-adjusting")

    return warnings
```

---

## Validation Framework (Updated)

### Day 1-2: "Does it trade at all?"
- ✅ Entry rate >2 per day
- ✅ EXECUTE runs without crashes
- ✅ Decision field properly populated

### Day 3-7: "Are we avoiding obvious disasters?"
- ✅ No halted stocks entered
- ✅ No -10% intraday moves on entry
- ✅ Decision distribution healthy (PASS rate 20-40%)
- ✅ Position sizing varies appropriately

### After 15-20 trades: "Is Claude adding edge?"
- Win rate >50%
- Average return >0% (better than random)
- Risk flags correlate with outcomes (validate or refute)
- Optimism bias not present

---

## GO Prompt Changes (Concrete)

### Addition #1: Decision Types Section
```
**DECISION TYPES (Required - Choose One Per Candidate):**

You must classify each recommendation as:
- ENTER: Standard entry, normal position sizing (6-10%)
- ENTER_SMALL: Reduced entry for speculative/uncertain setups (5-6% max)
- PASS: Do not enter - catalyst interesting but insufficient conviction or excessive risk

PASS is expected on 30-40% of candidates. Do not force trades on marginal setups.
Quality over quantity is critical for system success.

Examples:
- Strong FDA catalyst + RSI 72 + good volume = ENTER at 9%
- Contract win + RSI 85 + extended 18% = ENTER_SMALL at 6%
- Analyst upgrade + weak volume + Tier 3 = PASS (don't recommend)
```

### Addition #2: Testing Phase Sizing
```
**POSITION SIZING = RISK DIAL (TESTING PHASE):**

⚠️  TESTING MODE: Using tightened range (6-10%) for initial validation.
Range will widen to 5-13% after 15-20 successful trades.

For ENTER decisions:
- 9-10%: High conviction - Tier 1 catalyst + strong technicals + HIGH confidence
- 7-8%: Good opportunity - Strong catalyst, some technical heat + MEDIUM confidence
- 6-7%: Starter position - Solid catalyst, multiple risk flags + MEDIUM/LOW confidence

For ENTER_SMALL decisions:
- 5-6%: Speculative setup - catalyst intriguing but concerning risk indicators + LOW confidence

Use the full range - variance in sizing demonstrates risk discrimination.
```

### Addition #3: Updated JSON Structure
```json
**CRITICAL OUTPUT REQUIREMENT - JSON at end:**
```json
{
  "hold": ["TICKER1", "TICKER2"],
  "exit": [
    {"ticker": "TICKER3", "reason": "Specific reason following exit rules"}
  ],
  "buy": [
    {
      "ticker": "NVDA",
      "decision": "ENTER",
      "confidence_level": "HIGH",
      "position_size_pct": 9.0,
      "catalyst": "Earnings_Beat",
      "sector": "Technology",
      "thesis": "One sentence thesis"
    },
    {
      "ticker": "AXSM",
      "decision": "ENTER_SMALL",
      "confidence_level": "MEDIUM",
      "position_size_pct": 6.0,
      "catalyst": "FDA_Approval",
      "sector": "Healthcare",
      "thesis": "One sentence thesis"
    }
  ]
}
```

**NEW REQUIRED FIELDS:**
- decision: Must be "ENTER", "ENTER_SMALL", or omit from buy array (= PASS)
- confidence_level: Must be "HIGH", "MEDIUM", or "LOW"

Do not include tickers you are PASSing on in the buy array.
```

---

## Implementation Steps (Tonight)

1. **Update GO prompt in agent_v5.5.py** (lines ~4044-4149)
   - Add DECISION TYPES section
   - Update POSITION SIZING to testing phase range
   - Update JSON structure requirements

2. **Update JSON parsing** (lines ~5530-5560)
   - Handle new `decision` field
   - Handle new `confidence_level` field
   - Apply ENTER_SMALL cap

3. **Add monitoring script**
   - Create `check_optimism_bias.py` for daily analysis

4. **Test locally** - Verify JSON parsing with sample data

5. **Deploy v5.7.1** before tomorrow's GO command

---

## Rollback Criteria (Updated)

**Immediate rollback if:**
- EXECUTE breaks on new JSON fields
- Claude consistently ignores decision/confidence requirements
- >5 consecutive losses with avg >5%

**Investigate if (Day 3-7):**
- PASS rate <20% (over-optimism)
- All positions sized 7-8% (no risk discrimination)
- Confidence always MEDIUM+ (no uncertainty expressed)
- Thesis statements become generic

**Action:** Tighten prompt language, don't revert architecture

---

## Questions for User

1. **Timing:** Should we implement Phase 1 changes tonight for tomorrow's GO, or wait another day?

2. **Sizing range:** Comfortable with 6-10% for testing, or prefer different bounds?

3. **PASS threshold:** Should we suggest 30-40% PASS rate, or different target?

4. **Monitoring:** Want daily reports on decision distribution, or wait until Day 3?

---

## Summary

Third-party validated our architecture (AI-first, catastrophic checks only) but identified important refinements:
- Make decisions explicit (prevents accidental trades)
- Tighten sizing during testing (cleaner signal validation)
- Add portfolio context (inform, don't veto)
- Grade risk severity (better learning)
- Watch for optimism bias (LLMs over-trust narrative)

**All refinements preserve v5.7 architecture** - they add guardrails without re-introducing veto wars.

The reviewer's final verdict: "Legitimate best-in-class architecture shift. The system is finally allowed to express an opinion. That's the prerequisite for learning."
