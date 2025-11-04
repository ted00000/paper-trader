# Phase 4: Portfolio Rotation System
**Active Portfolio Management with Claude Decision-Making**

---

## Overview

Enable Claude to strategically rotate capital from weak/stalling positions into stronger opportunities when portfolio is at max capacity (10/10).

## Key Principles

1. **Claude makes all rotation decisions** with full context
2. **High bar for rotations** - avoid unnecessary churn
3. **Track everything** - measure rotation performance
4. **Learn from outcomes** - adjust criteria based on results
5. **Opportunity cost matters** - sometimes +2% → +8% is the right move

---

## Implementation

### 1. New Exit Reason: "Strategic_Rotation"

**Add to exit types:**
- `Stop_Loss` - Hit -7% stop
- `Target_Reached` - Hit +10% target
- `Time_Stop` - Held 21 days
- `News_Invalidation` - Thesis invalidated
- **`Strategic_Rotation`** - Exited to rotate into stronger opportunity ← NEW

### 2. Enhanced CSV Tracking

**New columns in completed_trades.csv:**
```
Exit_Type                  # e.g., "Strategic_Rotation"
Rotation_Into_Ticker       # Ticker rotated into (if applicable)
Rotation_Reason            # Why rotation was made
```

**Example rotation log:**
```csv
AMZN,2025-11-01,2025-11-05,229.25,235.00,4,2.5,5.75,Strategic_Rotation,Earnings_Beat,NVDA,Stalling momentum - rotating into fresh Tier 1 catalyst
```

### 3. GO Command Enhancement

**New logic after Claude returns decisions:**

```python
# After Step 5: Process decisions
hold_positions = decisions.get('hold', [])
exit_positions = decisions.get('exit', [])
buy_positions = decisions.get('buy', [])

# NEW: Check if we have strong opportunities but portfolio is full
if len(buy_positions) > 0 and (len(hold_positions) + len(exit_positions)) >= 10:
    print("\n5.5 Portfolio at capacity - evaluating rotation opportunities...")

    # Ask Claude to evaluate rotation potential
    rotation_decision = self.evaluate_portfolio_rotation(
        hold_positions=hold_positions,
        new_opportunities=buy_positions,
        premarket_data=premarket_data
    )

    if rotation_decision.get('rotations'):
        # Move rotated positions from HOLD to EXIT
        for rotation in rotation_decision['rotations']:
            # Add rotation metadata
            rotation['exit_reason'] = f"Strategic_Rotation: {rotation['reason']}"
            rotation['rotation_into'] = rotation['target_ticker']
            exit_positions.append(rotation)

            # Remove from holds
            hold_positions = [p for p in hold_positions if p['ticker'] != rotation['ticker']]
```

### 4. Claude Rotation Prompt

**Context for rotation decision:**
```
PORTFOLIO ROTATION EVALUATION

Current Holdings (10/10):
- NVDA: +2.91% (Day 5) - Tier 1 Earnings Beat
- XOM: -1.10% (Day 5) - Tier 2 Sector Momentum
- LLY: +9.32% (Day 5) - Tier 1 Binary Event
- ... [all 10 positions]

New Opportunities (3):
- MSFT: Tier 1 Earnings Beat (2 hours old, 95/100 news score)
- GOOGL: Tier 2 Analyst Upgrade (1 day old, 75/100 news score)
- META: Tier 1 Product Launch (4 hours old, 88/100 news score)

ROTATION CRITERIA:
- Weak position: Low momentum (<0.5%/day), stalling thesis, or underperforming
- Strong opportunity: Tier 1 catalyst, fresh (< 1 day), high news score (>80)
- Net expected value: New opportunity EV > Current position EV + exit cost

Should we rotate any positions? Consider:
1. Which current holdings are weakest (momentum, thesis, tier)?
2. Which new opportunities are strongest?
3. Is the expected value worth the rotation cost?

Return JSON:
{
  "rotations": [
    {
      "ticker": "XOM",
      "reason": "Stalling at -1.1% after 5 days, sector momentum fading",
      "target_ticker": "MSFT",
      "target_rationale": "Fresh Tier 1 earnings beat with 95/100 validation",
      "expected_net_gain": "+6-8% vs holding XOM to -7% stop",
      "confidence": "HIGH"
    }
  ],
  "no_rotation": [] // If keeping all positions
}
```

### 5. Learning System Integration

**learn_monthly.py additions:**

```python
# Rotation Performance Analysis
def analyze_rotations(self, trades_df):
    """Analyze strategic rotation performance"""

    rotations = trades_df[trades_df['Exit_Type'] == 'Strategic_Rotation']

    if len(rotations) == 0:
        return {"message": "No rotations made this month"}

    # Get outcomes of rotation targets
    rotation_targets = {}
    for _, rot in rotations.iterrows():
        target_ticker = rot['Rotation_Into_Ticker']
        # Find the target's outcome
        target_trade = trades_df[trades_df['Ticker'] == target_ticker]
        if not target_trade.empty:
            rotation_targets[rot['Ticker']] = {
                'exit_pnl': rot['Return_Percent'],
                'target_pnl': target_trade.iloc[0]['Return_Percent'],
                'net_gain': target_trade.iloc[0]['Return_Percent'] - rot['Return_Percent']
            }

    # Calculate metrics
    avg_exit_pnl = rotations['Return_Percent'].mean()
    avg_target_pnl = # ... calculate from rotation_targets
    avg_net_gain = # ... calculate net benefit

    # Calculate "what if we held?" using time stop data
    # ...

    return {
        "rotations_made": len(rotations),
        "avg_exit_pnl": avg_exit_pnl,
        "avg_target_pnl": avg_target_pnl,
        "avg_net_gain": avg_net_gain,
        "win_rate_if_held": # % that would've hit target if held
        "recommendation": "Rotations adding +X% per trade" or "Too aggressive"
    }
```

### 6. Exit Reason Standardization

**Update `standardize_exit_reason()` to handle rotations:**

```python
def standardize_exit_reason(self, position, current_price, reason):
    """Standardize exit reasons for consistent logging"""

    # ... existing logic ...

    # Check for strategic rotation
    if 'rotation' in reason_lower or 'Strategic_Rotation' in reason:
        return f"Strategic rotation ({return_pct:+.1f}%)"

    # ... rest of logic ...
```

---

## Testing Plan

1. **Unit test rotation logic**
   - Mock portfolio at 10/10
   - Mock strong new opportunity
   - Verify Claude called with correct context
   - Verify rotation adds to exits

2. **Integration test**
   - Run GO command with full portfolio
   - Add strong opportunity to scan results
   - Verify rotation decision propagates to EXECUTE
   - Verify CSV logging correct

3. **Live test on paper account**
   - Monitor first rotation
   - Verify both legs execute correctly
   - Check CSV has rotation metadata

---

## Documentation Updates

### STRATEGY_DOC.md additions:

```markdown
## Phase 4: Portfolio Rotation (Active Management)

When portfolio is at max capacity (10/10) and strong opportunities appear, Claude may strategically rotate capital.

### Rotation Criteria
- **Exit weak positions:** Stalling momentum, lower conviction, or fading thesis
- **Enter strong opportunities:** Fresh Tier 1 catalysts with high validation scores
- **Net positive EV:** Expected gain from new position > current position + exit cost

### Example
Portfolio full with AMZN at +2% (Day 8, momentum stalling).
NVDA Tier 1 earnings beat appears (2 hours old, 95/100 score).
Claude decides: Exit AMZN (+2%) → Enter NVDA (expected +8-10%).
Result: Strategic rotation logged, both trades tracked for learning.

### Learning
Monthly analysis tracks:
- Rotation win rate
- Average net gain (target P&L - exit P&L)
- "What if held?" comparison
- Adjusts rotation criteria based on outcomes
```

---

## Success Metrics

After 30 days:
- **Rotation count:** 5-10 rotations (not excessive)
- **Avg net gain:** +3-5% per rotation
- **Target win rate:** 70%+ (new positions outperform)
- **Opportunity cost:** Rotations beat "held to stop/target" 60%+ of time

---

## Rollout Plan

1. Implement rotation logic (this PR)
2. Deploy to paper account
3. Monitor first 3 rotations manually
4. After 15 days, review learning metrics
5. Adjust criteria if needed
6. Full automation after 30 days validation

---

**Status:** Ready for implementation
**Estimated Time:** 3-4 hours
**Risk:** Low (paper trading, fully reversible)
