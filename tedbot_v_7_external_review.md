# Tedbot v7.x – Consolidated Technical Review & Bug Assessment

_Last updated: Dec 2025_

This document consolidates **all feedback to date** on the Tedbot system, including:
- Main agent (`agent_v5.5.py`) review
- Market screener (`market_screener.py` / `screener.txt`) review
- Bug / reliability assessment
- Architecture, logic, and data-pipeline risks

The intent is to provide **one authoritative review artifact** you can reference as Tedbot continues its 6–12 month validation run.

---

## 1. Executive Summary

**Overall assessment:**
Tedbot is a **research-grade autonomous trading platform**, not a hobby bot. The architecture, risk controls, and learning loop place it well above typical retail or experimental systems.

**Key conclusion:**
- ✅ No blocking syntax or runtime-crash bugs found in static review
- ⚠️ Several *silent-failure* and *edge-case reliability* risks exist (fixable)
- ⚠️ Some **spec drift / wording mismatches** between documentation and code
- ⚠️ A few **logic edge cases** in the screener and rotation logic are worth tightening

Nothing here invalidates your approach. These are **refinements**, not rewrites.

---

## 2. Main Agent (`agent_v5.5.py`) Review

### 2.1 What Is Strong

**GO / EXECUTE / ANALYZE separation**
- Correct institutional design
- Prevents decision–execution coupling
- Enables clean post-hoc learning

**Cluster-based conviction scoring**
- Momentum, Institutional, Market capped
- Catalyst uncapped (correct)
- Prevents correlated signal double-counting

**Risk system clarity**
- ATR-based stops with explicit -7% cap
- Canonical trailing stop policy
- Stop_Pct logging enables distribution analysis

**Fail-safe behavior**
- Claude failure → HOLD / skip new entries
- No undefined execution states

**Universe + ruleset hashing**
- Excellent research hygiene
- Prevents silent policy drift

---

### 2.2 Potential Bugs / Reliability Traps

These are **not failing today**, but are real-world failure risks.

#### 1. Requests without timeouts
Several `requests.get()` calls lack `timeout=`.
- Risk: hung cron jobs, stalled pipeline

**Fix:**
```python
requests.get(url, timeout=(3.05, 20))
```

---

#### 2. Bare `except:` blocks
At least two `except:` (no exception type) blocks exist.
- Risk: silent logic degradation

**Fix:**
```python
except Exception:
    logger.exception("Context")
```

---

#### 3. Naive datetime usage
Multiple `datetime.now()` calls without timezone.
- Risk: trading-day drift, file mislabeling

**Fix:** standardize to ET or UTC using `zoneinfo`.

---

#### 4. Inconsistent HTTP error handling
Some `.json()` calls occur without `raise_for_status()`.
- Risk: API error payloads treated as valid data

---

#### 5. Fail-open config loading
Catalyst exclusions and context files sometimes default to `{}` silently.
- Risk: unintended ruleset execution

**Recommendation:** log + surface a “context degraded” flag.

---

## 3. Market Screener Review (Composite Score + Top-N)

### 3.1 What the Screener Does Well

**Correct filter vs score separation**
- Hard filters: price, liquidity, catalyst presence
- RS correctly demoted to scoring factor

**RS percentile framework**
- IBD-style 0–100 normalization
- Much better than fixed RS thresholds

**News scoring realism**
- Tiered catalysts
- Recency rules
- Negative keyword filtering
- Law-firm spam suppression

**Volume quality classification**
- GOOD / STRONG / EXCELLENT
- Trending logic is practical and usable

---

### 3.2 Screener Logic Issues / Edge Cases

#### 1. Universe is not truly “S&P 1500”
`get_sp1500_tickers()` pulls US common stocks from Polygon and truncates alphabetically.
- Risk: universe drift, survivorship bias

**Recommendation:**
- Use a maintained S&P 1500 constituent list
- Treat Polygon as enrichment only

---

#### 2. RS wording vs implementation mismatch
Comments reference “sector outperformance” but code computes **market (SPY) outperformance**.

**Action:** update comments or rename variable for clarity.

---

#### 3. News score inflation risk
Tier 2 keywords can be counted repeatedly across multiple articles.
- Risk: artificial score inflation

**Fix options:**
- Cap per keyword per ticker
- Or apply decay for repeated hits

---

#### 4. Ticker filtering is stricter than documented
`isalpha()` and `len <= 5` excludes dotted tickers (BRK.B, BF.B, etc.).

This is fine — just **explicitly document it as intentional**.

---

### 3.3 Composite Score & Top-N Selection (Sanity Check)

Your pipeline:
1. Compute `base_score`
2. Add tier-aware `catalyst_score`
3. `composite_score = base_score + catalyst_score`
4. Split into Tier 1 / 2 / 3 buckets
5. Sort within each tier by `composite_score`
6. Apply tier quotas
7. Backfill to `TOP_N_CANDIDATES`
8. Assign rank

**Assessment:**
- Logic is internally consistent
- Tier-first sorting aligns with catalyst-driven philosophy

**Edge cases to guard:**
- Missing `composite_score`
- Tier label mismatches (string drift)
- Empty tiers causing silent underfill

---

### 3.4 High-ROI Screener Enhancements

These are not required, but would materially improve clarity and learning.

1. **“Why This Made the List” field**
   - Top 3 contributors (e.g., Tier 1 catalyst, EXCELLENT volume, RS 92nd pct)

2. **API call caching**
   - Cache SPY + sector ETF returns per run
   - Prevent call explosion

3. **Early market regime annotation**
   - You already compute breadth + SPY trend
   - Store regime in screener output

---

## 4. Cross-System Risks (Agent + Screener)

### 4.1 Context Dilution Risk (LLM)
Claude context includes:
- Rules
- Exclusions
- Lessons
- Portfolio
- Market regime

As this grows, reasoning quality can degrade.

**Recommendation:**
- Priority-rank context blocks
- Never truncate rules/exclusions
- Drop lowest-impact lessons first

---

### 4.2 Single Cognitive Decision Point
Claude selects trades.

**Mitigation (recommended):**
Add **quantitative veto gates**:
- Min Entry Quality Score
- RS floor unless Tier 1
- Volume quality size caps

This keeps Claude as *selector*, not *sole authority*.

---

### 4.3 Rotation Timing Risk
Rotation logic is snapshot-based.

**Risk:** rotating out before late catalyst resolution.

**Mitigation:**
- Add catalyst-age decay modifier

---

## 5. Bottom Line

- There are **no obvious breaking bugs** in the code as reviewed
- The issues identified are **production-hardening and edge-case risks**, not structural flaws
- The screener + agent alignment is coherent and internally consistent

**Recommendation:**
Run Tedbot **unchanged** for the validation window unless:
- Data proves a rule is negative expectancy
- A silent failure mode is observed in logs

If/when you want, the next logical steps are:
1. Spec-vs-code drift audit (rule-by-rule)
2. Expectancy attribution pruning
3. v8.0 design only after data justifies change

---

_End of consolidated review_

