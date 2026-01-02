# Tedbot v7.0 - Validation Requirements

## Critical Issues from Third-Party Re-Assessment (Dec 15, 2025)

### 1. Policy Drift Prevention ⚠️ HIGH PRIORITY

**Problem:** 
- `strategy_rules.md` is auto-updated by learning
- Learning outputs feed directly into Claude context
- Claiming "code frozen" while decision policy continuously mutates
- Makes clean v7.0 evaluation impossible
- Increases overfitting risk

**Solution:**
```python
RULESET_VERSION = hashlib.sha256(
    strategy_rules_content + 
    catalyst_exclusions_content + 
    prompt_template
).hexdigest()[:8]

# Log to CSV: "v7.0-a3f4b2c1"
```

**Implementation:**
- Add RULESET_VERSION to every trade in CSV
- Only allow strategy updates on monthly "releases"
- Track: v7.0-baseline, v7.0-month1, v7.0-month2, etc.
- Enables clean A/B testing: performance before/after rule changes

---

### 2. Execution Cost Modeling (Beyond Spread) ⚠️ HIGH PRIORITY

**Problem:**
- Spread check (0.5%) is necessary but NOT sufficient
- Real execution cost includes:
  - Fast tape / thin top-of-book
  - Gap continuation slippage
  - Market order impact
  - News volatility slippage

**Current:** 
```python
if spread_pct > 0.5%: skip  # Only checks quoted spread
```

**Better:**
```python
# At entry: log actual fill vs mid-price
slippage_bps = (fill_price - mid_price) / mid_price * 10000

# Track distribution:
# - p50 slippage: 8-12 bps (acceptable)
# - p90 slippage: 25-35 bps (marginal)
# - p99 slippage: 60+ bps (edge killer)
```

**Implementation Options:**
1. **Paper trading slippage model** (estimate 15 bps per trade)
2. **Limit-with-timeout** (place limit at mid+X bps, cancel if no fill in 30s)
3. **Track bid/ask at 9:45 + simulate fill price** based on urgency

---

### 3. Institutional Signals Validation ⚠️ MEDIUM PRIORITY

**Problem:**
- "FREE via Polygon" dark pool/options data is often weakly predictive
- Can become confidence amplifier in scoring (false precision)
- Not proven to add incremental edge

**Solution:**
Run ablation analysis on next 50 trades:
```
Group A: Full scoring (WITH institutional signals)
Group B: Scoring without options/dark pool factors

Compare:
- Win rate: A vs B
- Avg gain: A vs B  
- Edge contribution: Does institutional data add >1% to returns?
```

**Implementation:**
- Add `ablation_group` field to CSV
- Randomly assign 50% trades to "no_institutional" group
- Report after 50 trades whether to keep these factors

---

### 4. Exit Logic Consistency ⚠️ HIGH PRIORITY

**Problem:**
Documentation shows THREE different trailing stop policies:
- "50% profit (trail -5%), 100% (trail -3%)"
- "lock +8%, trail by 2%"
- "trail by 2% from peak"

**Which is actually implemented?**

**Solution:**
1. Define ONE canonical trailing stop policy
2. Log exact parameters per trade:
   - `trailing_stop_activated_at`: price
   - `trailing_stop_distance_pct`: 2.0%
   - `profit_locked_pct`: 8.0%
3. Track in CSV for analysis

---

### 5. ATR Stop Documentation Error ⚠️ CRITICAL

**Problem:**
- Doc says: "capped at -7% maximum"
- Example shows: "ATR=$5, entry=$100 → stop=$87.50 (-12.5%)"
- **These contradict each other**

**Actual Implementation:**
```python
atr_stop = entry_price - (2.5 * ATR)
max_stop = entry_price * 0.93  # -7% floor
final_stop = max(atr_stop, max_stop)  # Use tighter of two
```

**Truth:** -7% is a FLOOR (max loss), not a ceiling
- ATR suggests -12.5% → Use -7% floor (tighter)
- ATR suggests -5% → Use -5% (tighter than floor)

**Fix:** Remove confusing example, clarify that -7% is "maximum allowable loss"

---

## Minimum Validation Checklist (Before "90-92% Best-in-Class" Claim)

### Required Deliverables:

1. **Ablation Report**
   - Remove RS: performance without RS scoring
   - Remove institutional: without options/dark pool
   - Remove breadth gating: flat 10% sizing always
   - Shows which factors actually contribute edge

2. **Transaction Cost Accounting**
   - Spread cost per trade
   - Estimated slippage (model or actual)
   - Partial fill behavior
   - Total execution cost as % of P&L

3. **Versioned Policy**
   - RULESET_VERSION in CSV
   - "v7.0" means a specific frozen ruleset
   - Rule changes → v7.1, v7.2, etc.

4. **Regime Performance Table**
   - Rows: VIX regime (5 levels)
   - Cols: Breadth regime (3 levels)
   - Cells: Win rate, avg gain, Sharpe
   - Shows where system wins/loses

5. **Drawdown Control**
   - Max drawdown %
   - Time-to-recover (days)
   - Drawdown frequency
   - As important as win rate

---

## Next Steps

**Immediate (Dec 15-16):**
1. Fix ATR stop documentation
2. Add RULESET_VERSION to CSV logging
3. Define canonical exit policy
4. Model execution cost (15 bps baseline)

**Short-term (Dec 17-31):**
1. Collect 30-50 trades with full attribution
2. Run ablation analysis
3. Generate regime performance table
4. Validate institutional signals add edge

**Medium-term (Jan 2026):**
1. 90-day results with clean v7.0 ruleset
2. Quantitative validation report
3. Decision: keep learning updates or freeze further

---

## Quote from Assessment

> "If you paste (or upload) a slice of your completed_trades.csv (even 30–50 trades), I'll do a real quant-style evaluation:
> - expectancy,
> - win/loss distribution,
> - contribution by catalyst tier,
> - lift from RS/volume/sector strength,
> - and whether ATR stops improved tail losses."

**Action:** Generate completed_trades.csv sample when available for third-party quant analysis

---

**Status:** v7.0 is "legit upgrade" but needs validation rigor before claiming institutional-grade performance.
