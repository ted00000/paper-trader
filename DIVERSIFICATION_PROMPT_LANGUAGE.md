# Diversification Guidance for GO Prompt

## Proposed Language to Add to GO Prompt

### Location: After "DECISION TYPES" section, before "POSITION SIZING"

```
**PORTFOLIO DIVERSIFICATION (Your Responsibility):**

You have full authority to construct the portfolio allocation based on current opportunities.
Diversification is important, but you should balance it against opportunity quality.

Guidelines:
- Avoid concentration risk: Generally aim for <40% in any single sector
- Consider temporary over-allocation: If a sector has exceptional catalysts (e.g., multiple FDA approvals, major policy shift), 40-50% allocation may be justified
- Explain your reasoning: If recommending sector concentration, articulate why the opportunity set warrants it
- Quality over arbitrary limits: Better to own 4 excellent Healthcare stocks (40%) than force 2 mediocre Tech stocks for "balance"
- Market regime matters: In sector rotation periods, concentration in leading sectors is appropriate

Current Portfolio Context:
[This section will show existing holdings by sector when reviewing portfolio]

Your Job:
- Analyze the opportunity set holistically
- Construct the best risk-adjusted portfolio given available catalysts
- Use sector allocation as a tool, not a constraint
- Document your allocation rationale in your analysis
```

## Example of How Claude Would Use This

**Scenario 1: Balanced Opportunities**
```
Sector Allocation Decision:
- Technology: 3 positions (30%) - Strong earnings season
- Healthcare: 2 positions (20%) - FDA approvals
- Industrials: 2 positions (20%) - Defense spending
- Materials: 2 positions (20%) - China policy
- Energy: 1 position (10%) - Oil breakout

Rationale: Diversified across 5 sectors, no single concentration >30%
```

**Scenario 2: Justified Concentration**
```
Sector Allocation Decision:
- Healthcare: 4 positions (40%) - Exceptional FDA catalyst week
  * 2 FDA approvals (AXSM, APGE)
  * 1 strong earnings with guidance (AXGN)
  * 1 clinical breakthrough (ARWR)
- Technology: 2 positions (20%) - Analyst upgrades
- Industrials: 1 position (10%) - M&A arb
- Materials: 1 position (10%) - Policy tailwind

Rationale: Healthcare concentration justified by rare cluster of Tier 1 FDA/clinical
catalysts. Risk mitigated by diverse sub-sectors (CNS, respiratory, devices, obesity).
Will rebalance next week as opportunities normalize.
```

**Scenario 3: Sector Rotation**
```
Sector Allocation Decision:
- Technology: 5 positions (50%) - Sector leading market, AI infrastructure theme
- Healthcare: 2 positions (20%) - Defensive quality
- Industrials: 2 positions (20%) - Earnings strength
- Energy: 1 position (10%) - Commodity hedge

Rationale: Technology sector in strong uptrend with broad participation.
Overweight justified by momentum regime. Healthcare provides defensive balance.
```

## What This Achieves

1. **Claude has the goal** - Diversification is important
2. **Claude has the context** - Current sector allocation shown
3. **Claude has the flexibility** - Can justify concentration when warranted
4. **Claude documents reasoning** - Explains allocation decisions
5. **We can measure** - Did concentration predict good/bad outcomes?

## What Gets Removed from Validation

Lines 959-983 in agent_v5.5.py:
```python
# REMOVED v5.7.1: Sector/industry concentration limits
# Claude is responsible for portfolio allocation decisions
# Non-catastrophic risk - allocation is optimization, not safety
#
# if sector_counts.get(sector, 0) >= max_allowed:
#     rejected_positions.append({...})
#     print(f"   ⚠️ REJECTED {ticker}: Sector limit reached...")
#     continue
#
# if industry_counts.get(industry, 0) >= MAX_PER_INDUSTRY:
#     rejected_positions.append({...})
#     print(f"   ⚠️ REJECTED {ticker}: Industry limit reached...")
#     continue
```

## Monitoring After Change

After 1 week, analyze:
- Did Claude maintain reasonable diversification?
- When he concentrated, was it justified by catalysts?
- Did concentrated sectors outperform or underperform?
- Any red flags (e.g., 80% in one sector with weak rationale)?

If Claude consistently over-concentrates without good reasoning, we tune the prompt language, not re-introduce hard blocks.
