# Paper Trading Lab - Master Strategy Blueprint
## Best-in-Class Swing Trading System

**Version:** 2.0 (Pareto-Optimized)
**Based On:** Deep Research + v5.0 Implementation
**Last Updated:** 2025-10-30
**Target Win Rate:** 70%+

---

## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Entry Strategy](#entry-strategy)
4. [Exit Strategy](#exit-strategy)
5. [Position Sizing](#position-sizing)
6. [Learning Strategy](#learning-strategy)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Optional Future Enhancements](#optional-future-enhancements)

---

## EXECUTIVE SUMMARY

### What Makes This System Best-in-Class

This is a **data-driven swing trading system** that combines:
- **AI-powered catalyst identification** (Claude Sonnet 4.5)
- **Systematic risk management** (-7% stops, +10-15% targets, 3-7 day holds)
- **Bidirectional news intelligence** (validates entries, invalidates exits)
- **Three-tier learning loops** (daily tactical, weekly optimization, monthly strategic)
- **Pareto-optimized simplicity** (20% of features drive 80% of results)

### Core Trading Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Portfolio Size** | 10 positions | Diversification without dilution |
| **Position Sizing** | 8-15% (conviction-based) | Simple, no complex formulas |
| **Stop Loss** | -7% from entry | Protects capital, allows breathing room |
| **Profit Target** | +10-15% | Realistic for 3-7 day swing trades |
| **Hold Time Target** | 3-7 days | Optimal swing trading window |
| **Maximum Hold** | 21 days | Time stop safety valve |
| **Minimum Hold** | 2 days | Prevents daily churning |

### Expected Performance

| Metric | Target | Current (v5.0) |
|--------|--------|----------------|
| **Win Rate** | 70%+ | TBD (no trades yet) |
| **Avg Winner** | +12% | TBD |
| **Avg Loser** | -5% | TBD |
| **Risk/Reward** | 2.4:1 | 2:1 minimum |
| **Monthly Return** | +5-12% | TBD |
| **Max Drawdown** | <15% | TBD |

---

## SYSTEM ARCHITECTURE

### Daily Workflow (Automated via Cron)

```
8:45 AM  - GO COMMAND
           ├─ Load current 10 positions
           ├─ Fetch premarket prices (15-min delayed)
           ├─ NEWS VALIDATION: Check catalyst freshness
           ├─ Claude AI reviews each position: HOLD/EXIT/BUY
           ├─ For exits: Identify replacements
           └─ Save decisions to pending_positions.json

9:45 AM  - EXECUTE COMMAND
           ├─ Load pending decisions
           ├─ Execute EXITS (close positions)
           ├─ Execute BUYS (enter new positions)
           ├─ Update portfolio with market prices
           └─ Log all trades to CSV

4:50 PM  - ANALYZE COMMAND
           ├─ Fetch closing prices for all positions
           ├─ Update P&L metrics
           ├─ Check exit conditions (stop/target/time)
           ├─ NEWS INVALIDATION: Check for catalyst failure
           ├─ Close any triggered exits
           ├─ Claude AI evening analysis
           └─ Create daily activity summary

5:00 PM  - DAILY LEARNING
           ├─ Analyze last 7 days of trades
           ├─ Identify failing catalysts (<35% win rate)
           ├─ Update catalyst_exclusions.json
           └─ Append insights to lessons_learned.md

Friday   - WEEKLY LEARNING
5:30 PM  ├─ Deep catalyst performance analysis
         ├─ Calculate optimal stop/target from data
         ├─ Analyze hold times and entry timing
         └─ Generate weekly performance report

Last     - MONTHLY LEARNING
Sunday   ├─ Market regime detection (Bull/Bear/Choppy)
6:00 PM  ├─ Comprehensive performance metrics
         ├─ Strategy effectiveness evaluation
         └─ Major strategic adjustments
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MARKET DATA (Polygon.io)                  │
│         15-min delayed prices + news + fundamentals          │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐         ┌──────▼──────┐
    │   GO     │         │   ANALYZE   │
    │ 8:45 AM  │         │   4:50 PM   │
    │          │         │             │
    │ News     │         │ News        │
    │ Validator│         │ Invalidator │
    └────┬─────┘         └──────┬──────┘
         │                      │
         │    ┌─────────────┐   │
         └────► EXECUTE     ◄───┘
              │  9:45 AM    │
              └──────┬──────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐         ┌──────▼──────┐
    │ Portfolio│         │ Trade       │
    │   Data   │         │  History    │
    └────┬─────┘         └──────┬──────┘
         │                      │
         └───────────┬──────────┘
                     │
              ┌──────▼──────┐
              │  Learning   │
              │   Systems   │
              │ Daily/Wkly/ │
              │   Monthly   │
              └─────────────┘
```

---

## ENTRY STRATEGY

### Overview

Entry quality determines success. We use a **multi-layered validation system**:
1. **Catalyst Tier System** - Only Tier 1 catalysts qualify
2. **News Validation** - Confirms catalyst is fresh and accelerating
3. **VIX Filter** - Ensures market regime is favorable
4. **Supporting Factors** - Minimum 3 confirming indicators
5. **Conviction Assessment** - Determines position sizing

### Catalyst Tier System

#### **TIER 1: High Conviction (ENTER)**

**A. Earnings Beat + Guidance Raise**
- EPS beat ≥10% above consensus
- Revenue beat (not just EPS accounting)
- **Forward guidance raised** (critical confirmation)
- Ideal entry: Within 3 days of report
- Expected hold: 3-5 days
- Target: +12-15%
- Position size: 12-15% (High conviction)

**B. Multi-Catalyst Synergy**
- Earnings beat + Analyst upgrade
- Technical breakout + Sector momentum
- FDA approval + Contract win
- 2+ catalysts present simultaneously
- Research shows: +15-25% win rate improvement
- Expected hold: 3-7 days
- Target: +12-15%
- Position size: 12-15% (High conviction)

**C. Major Analyst Upgrade**
- Top-tier firms: Goldman Sachs, Morgan Stanley, JPM
- Significant price target increase (≥15%)
- Detailed thesis in report (not just rating change)
- Ideal entry: Day of or day after upgrade
- Expected hold: 2-4 days
- Target: +8-12%
- Position size: 10-12% (Medium-High conviction)

**D. Strong Sector Momentum**
- Clear macro catalyst (policy, commodity spike, innovation)
- **3+ stocks in sector moving together** (not isolated)
- Volume confirmation (sector ETF >2x average)
- Ideal entry: First 1-3 days of rotation
- Expected hold: 5-10 days
- Target: +10-12%
- Position size: 10% (Medium conviction)

**E. Confirmed Technical Breakout**
- New 52-week high OR key resistance break
- **Volume ≥2x average** (institutional buying)
- Accompanied by positive fundamental catalyst
- Ideal entry: On breakout day with volume
- Expected hold: 2-5 days
- Target: +8-12%
- Position size: 8-10% (Medium conviction)

#### **TIER 2: Medium Conviction (CONDITIONAL)**

**Only enter if:**
- Portfolio has <8 positions (capital available)
- No Tier 1 opportunities available
- High news validation score

**Examples:**
- Earnings beat 5-10% (smaller beat)
- Analyst upgrade from smaller firm
- Technical breakout with <2x volume
- Sector momentum without clear catalyst

**Position size:** 8% (reduced conviction)

#### **TIER 3: Skip (DO NOT ENTER)**

**Auto-exclude if:**
- Earnings beat <5%
- Stale catalysts (>5 days old for earnings, >2 days for upgrades)
- Generic sector news without company-specific catalyst
- Meme stocks without fundamentals
- Pre-market gaps >15% (proven to fade)
- Any catalyst in `catalyst_exclusions.json`

### News Validation System (GO Command - Entry)

**Purpose:** Confirm catalyst quality BEFORE entering position

#### **Validation Checks**

**1. Catalyst Freshness Score (0-5 points)**
```
Earnings Catalysts:
- 0-2 days old: 5 points (FRESH - optimal entry window)
- 3-5 days old: 3 points (MODERATE - acceptable)
- 6-10 days old: 1 point (STALE - caution)
- >10 days old: 0 points (REJECT - momentum faded)

Analyst Upgrades:
- 0-1 days old: 5 points (FRESH)
- 2-3 days old: 2 points (MODERATE)
- >3 days old: 0 points (REJECT)

Binary Events (FDA, M&A, Contracts):
- 0-1 days old: 5 points (FRESH)
- >1 day old: 0 points (REJECT - news fully priced in)
```

**2. Momentum Acceleration Score (0-5 points)**
```
Follow-up Article Count (last 24 hours):
- 5+ articles: 5 points (STRONG momentum continuation)
- 3-4 articles: 3 points (MODERATE momentum)
- 1-2 articles: 1 point (WEAK momentum)
- 0 articles: 0 points (FADING momentum - caution)

Analyst Pile-On:
- 3+ upgrades in 48 hours: +5 points (STRONG confirmation)
- 2 upgrades: +3 points
- 1 upgrade: +1 point
```

**3. Multi-Catalyst Detection (0-10 points)**
```
Additional Positive Catalysts Detected:
- Earnings beat + Analyst upgrade: +5 points → UPGRADE to Tier 1
- Earnings beat + Contract win: +5 points → UPGRADE to Tier 1
- Technical breakout + Sector momentum: +3 points
- Any 2+ simultaneous catalysts: +5 points minimum
```

**4. Contradicting News Check (Penalty)**
```
Negative Keywords Detected:
- "concerns", "weakness", "downgrade", "cut": -3 points each
- "investigation", "lawsuit", "miss": -5 points each
- If total penalty >10 points: REJECT entry
```

#### **Validation Decision Matrix**

| Total Score | Decision | Action |
|-------------|----------|--------|
| **15-20 pts** | VALIDATED - High conviction | Enter at Tier 1 sizing (12-15%) |
| **10-14 pts** | VALIDATED - Medium conviction | Enter at Tier 1 sizing (10-12%) |
| **5-9 pts** | VALIDATED - Low confidence | Enter at Tier 2 sizing (8%) |
| **0-4 pts** | REJECTED - Stale/weak | PASS - Do not enter |
| **Negative** | REJECTED - Contradicting news | PASS - Catalyst invalidated |

**UPGRADE Logic:**
- If multi-catalyst score ≥5 points: Upgrade Tier 2 → Tier 1
- Increase position size by 20%
- Document multi-catalyst synergy in thesis

**Example:**
```
Stock: NVDA
Original catalyst: Analyst upgrade (Tier 2)
News check finds: Earnings beat announced this morning
Multi-catalyst score: +5 points
Decision: UPGRADE to Tier 1, increase size from 8% → 12%
```

### VIX Filter (Market Regime Check)

**Checked at:** 8:45 AM GO command

#### **VIX Thresholds**

| VIX Level | Market Regime | Action | Rationale |
|-----------|---------------|--------|-----------|
| **<20** | Normal/Low volatility | Full operations | Catalyst effectiveness high |
| **20-30** | Elevated volatility | Normal operations | Acceptable conditions |
| **30-35** | High volatility | HIGHEST CONVICTION ONLY | 50% catalyst effectiveness (research validated) |
| **35-40** | Extreme volatility | SYSTEM SHUTDOWN | Crisis mode - capital preservation |
| **>40** | Crisis mode | SYSTEM SHUTDOWN | Extended crisis - no operations |

**Implementation:**
```python
vix = fetch_vix_level()

if vix > 35:
    return "SYSTEM SHUTDOWN - Crisis volatility, no new entries"
elif vix > 30:
    return "HIGHEST CONVICTION ONLY - High volatility regime (50% effectiveness)"
elif vix > 20:
    return "NORMAL OPERATIONS - Elevated but acceptable"
else:
    return "NORMAL OPERATIONS - Favorable regime"
```

**Research Validation:**
- VIX >30 reduces catalyst effectiveness by 50% (research: Claude_Deep_Research.md line 25)
- VIX >40 appears only during major crises (2008, 2020 COVID)
- VIX-based filtering improves Sharpe ratio by 20-30%
- **CRITICAL:** System pauses at VIX 30 per research (not 35), implementing conservative threshold

### Supporting Factors Requirement

**Minimum 3 of the following must be present:**

1. **Catalyst** (Tier 1 - required baseline)
2. **Technical Confirmation**
   - Price above 50-day moving average
   - Volume >1.5x average
   - Clear support level nearby
3. **Sector Strength**
   - Sector ETF outperforming SPY (last 1 month)
   - Sector in top 3 momentum rankings
4. **Relative Strength** ⭐ **REQUIRED - Research Validated**
   - Stock outperforming its sector by **≥3%** over last 3 months
   - Research shows: 20.1% annualized for leaders vs 11.0% for sector average
   - Filters genuine leaders from sector coattail riders
5. **Market Regime**
   - SPY above 50-day and 200-day MA (bull market)
   - VIX <30 (normal volatility)
6. **News Validation**
   - Freshness score ≥3 points
   - Momentum acceleration score ≥3 points

**IMPORTANT:** Relative Strength (≥3% sector outperformance) is REQUIRED, not optional. Research demonstrates this single filter adds substantial alpha.

**Example - Valid Entry:**
```
Stock: GOOGL
✓ Catalyst: Earnings beat 18%, guidance raised (Tier 1)
✓ Technical: Above 50-day MA, volume 2.5x average
✓ Sector: Technology sector leading (rank #1)
✓ Relative Strength: GOOGL +5.2% vs XLK +2.1% (outperforming)
✓ Market Regime: SPY bullish, VIX 18
✓ News Validation: Report 1 day old, 4 follow-up articles

Total: 6 supporting factors → STRONG ENTRY
Conviction: HIGH (12-15% position)
```

### Entry Prohibitions (Never Enter)

| Prohibition | Rationale | Exception |
|-------------|-----------|-----------|
| **Pre-market gap >15%** | 80%+ fade probability | None |
| **Meme stocks** | Sentiment-driven, no edge | Only if Tier 1 catalyst present |
| **Penny stocks (<$5)** | Low liquidity, manipulation risk | None |
| **Market cap <$1B** | Illiquid, volatile | None |
| **No Tier 1 catalyst** | Core requirement | None |
| **Unclear thesis** | Can't articulate in 2 sentences | None |
| **VIX >30** | 50% catalyst effectiveness reduction | Highest conviction Tier 1 only |
| **Excluded catalyst** | Proven loser (<35% win rate) | None |
| **Stale catalyst** | >5 days old (earnings) | None |
| **FOMC window** | 2 days before through 1 day after | None |
| **CPI/NFP release** | Day before and day of | None |
| **Relative strength <3%** | Sector coattail rider, not leader | None |

### Macro Event Calendar (Risk Management)

**Purpose:** Avoid unpredictable volatility during major macro events

#### **Blackout Windows (No New Entries)**

**FOMC Meetings:**
- 2 days before meeting → 1 day after decision
- Rationale: 100-200% volatility spike on FOMC days (Fleming & Remolona 1999)
- Example: If FOMC is Wed 2:00 PM, blackout Mon-Thu

**CPI Releases:**
- Day before release → Day of release
- Rationale: 50-150% volatility spike on CPI days
- Example: If CPI is Thu 8:30 AM, blackout Wed-Thu

**NFP (Non-Farm Payroll) Releases:**
- Day before release → Day of release
- Rationale: Major market-moving data
- Example: If NFP is Fri 8:30 AM, blackout Thu-Fri

**Existing Positions During Blackouts:**
- Continue holding (don't exit solely due to calendar)
- Monitor more closely for news invalidation
- May exit if stop/target/news trigger hit

**Implementation:**
```python
def check_macro_blackout(date):
    """
    Check if date falls within macro event blackout window
    Returns: (is_blackout, event_name) tuple
    """
    # Fetch FOMC calendar (Fed website or API)
    # Fetch economic calendar (CPI, NFP dates)
    # Check if date within blackout windows

    if in_fomc_window(date):
        return (True, "FOMC blackout window")
    elif in_cpi_window(date):
        return (True, "CPI blackout window")
    elif in_nfp_window(date):
        return (True, "NFP blackout window")
    else:
        return (False, None)
```

### AI Decision Guardrails (Safety Limits)

**Purpose:** Prevent catastrophic losses from AI decision errors

#### **Position Limits**
- Maximum 15% per position (even high conviction)
- Maximum 10 positions total
- Maximum 3 positions per sector
- Maximum 40% allocation per sector

#### **Loss Limits (Auto-Pause Triggers)**

**Daily Loss Limit:** -2% of account value
- If daily losses exceed -2%, pause new entries for 24 hours
- Review all positions, check for systemic issues
- Example: $1,000 account → -$20 in one day = pause

**Monthly Loss Limit:** -8% of account value
- If monthly losses exceed -8%, pause system for strategic review
- Conduct comprehensive analysis of what's not working
- Example: $1,000 account → -$80 in one month = full pause

**Consecutive Loss Protocol:**
- After 3 consecutive losses: Mandatory review of strategy assumptions
- After 5 consecutive losses: Reduce position sizes by 50% until next winner
- Not automated initially, but tracked in learning system

#### **Override Authority**
- Human (you) has final override authority on all decisions
- Can manually exit positions flagged by AI
- Can reject AI entry recommendations
- Can pause system at any time

**Weekly Calibration:**
```python
def calibrate_ai_accuracy():
    """
    Track AI prediction accuracy vs actual outcomes
    """
    for trade in last_week_trades:
        ai_confidence = trade.confidence_level
        actual_outcome = trade.return_percent > 0

        # Compare AI confidence to win rate
        if ai_confidence == "HIGH" and win_rate < 65%:
            print("⚠️ AI overconfident on HIGH conviction trades")
        elif ai_confidence == "MEDIUM" and win_rate > 75%:
            print("⚠️ AI underconfident on MEDIUM conviction trades")
```

### Conviction Assessment & Sizing

**Determined by combining:**
1. Catalyst tier (Tier 1 vs Tier 2)
2. News validation score
3. Number of supporting factors
4. VIX regime
5. Relative strength (≥3% sector outperformance)
6. Macro event calendar (not in blackout window)

#### **Conviction Matrix**

| Scenario | Conviction | Position Size |
|----------|------------|---------------|
| Tier 1 + News ≥15 pts + 5+ factors + VIX <20 | **HIGH** | **12-15%** |
| Tier 1 + News 10-14 pts + 4 factors + VIX <30 | **MEDIUM-HIGH** | **10-12%** |
| Tier 1 + News 5-9 pts + 3 factors + VIX <30 | **MEDIUM** | **8-10%** |
| Tier 2 + News ≥10 pts + 4+ factors + VIX <25 | **MEDIUM** | **8%** |
| Any other combination | **LOW** | **SKIP** |

**Simplicity Rule:** If in doubt, default to 10% (standard position)

---

## EXIT STRATEGY

### Overview

Exit discipline determines long-term survival. We use **five exit triggers** checked twice daily:
1. Stop loss hit (-7%)
2. Profit target reached (+10-15%)
3. Time stop (21 days)
4. Catalyst invalidated (news-based)
5. Better opportunity (portfolio full)

### Exit Trigger 1: Stop Loss (-7%)

**Checked:** 4:50 PM ANALYZE command

**Trigger Condition:**
```python
if current_price <= entry_price * 0.93:
    exit_position(reason="Stop loss (-X.X%)")
```

**Parameters:**
- **Stop level:** Entry price × 0.93 (exactly -7%)
- **Execution:** Full 100% exit immediately
- **No exceptions:** Absolute discipline, no "giving it more room"
- **Adjustment:** May tighten to breakeven after +5% gain (optional)

**Research Validation:**
- Median loser from historical data: -5% to -7%
- -7% allows breathing room without catastrophic losses
- Protects capital for redeployment to better opportunities

**Exit Reason Format:**
```
"Stop loss (-7.2%)"
"Stop loss (-6.8%)"
```

### Exit Trigger 2: Profit Target (+10-15%)

**Checked:** 4:50 PM ANALYZE command

**Trigger Condition:**
```python
# Standard target for most catalysts
if current_price >= entry_price * 1.10:
    exit_position(reason="Target reached (+X.X%)")

# Extended target for strong catalysts
if catalyst == "Earnings_Beat_with_Guidance" and current_price >= entry_price * 1.15:
    exit_position(reason="Target reached (+X.X%)")
```

**Parameters:**
- **Standard target:** +10% (entry × 1.10)
- **Extended target:** +12-15% for:
  - Earnings beats >15% with guidance raise
  - Multi-catalyst synergy
  - Strong sector momentum with confirmation
- **Execution:** Full 100% exit (no partials)
- **Rationale:** Lock in profits, redeploy capital

**Why Full Exits:**
- Simplicity over complexity
- Capital redeployment to new opportunities
- Prevents "greed creep" (holding too long)
- Data will validate optimal target over time

**Exit Reason Format:**
```
"Target reached (+11.6%)"
"Target reached (+14.2%)"
```

### Exit Trigger 3: Time Stop (21 Days)

**Checked:** 4:50 PM ANALYZE command

**Trigger Condition:**
```python
if days_held >= 21:
    if unrealized_gain_pct < 3:
        exit_position(reason="Time stop (21 days)")
```

**Parameters:**
- **Maximum hold:** 21 calendar days
- **Trigger:** Only if position hasn't reached target
- **Rationale:** Capital tied up in stalled position
- **Action:** Exit and redeploy to better opportunity

**Why 21 Days:**
- **Optimal window is 3-7 days** for swing trades
- 21 days is safety valve for positions that stall
- Research shows catalyst momentum fades significantly after 10-14 days
- Better to redeploy capital than hope for recovery

**Exception:**
- If position is +8-9% (near target), may hold a few more days
- Document extended hold reason in notes

**Exit Reason Format:**
```
"Time stop (21 days)"
```

### Exit Trigger 4: Catalyst Invalidated (News-Based)

**Checked:** 4:50 PM ANALYZE command

**Purpose:** Detect when thesis is broken, exit BEFORE stop loss hit

#### **News Invalidation System**

**1. Negative Keyword Scoring**

```python
NEGATIVE_KEYWORDS = {
    'critical': ['charge', 'writedown', 'impairment', 'investigation'],  # 50 pts each
    'severe': ['delay', 'downgrade', 'cut guidance', 'miss', 'suspend'],  # 40 pts each
    'moderate': ['concerns', 'weakness', 'below', 'disappointing'],       # 25 pts each
    'mild': ['challenges', 'headwinds', 'competitive']                    # 10 pts each
}
```

**2. Context Amplifiers**

```python
AMPLIFIERS = {
    'quantified_dollar': 15,     # "$4.9B charge" → +15 pts
    'quantified_percent': 10,    # "Revenue miss -12%" → +10 pts
    'strong_negative': 5,        # "significantly below" → +5 pts
    'multiple_keywords': 10      # 3+ negative keywords in single article → +10 pts
}
```

**3. Source Credibility Multiplier**

```python
SOURCE_WEIGHTS = {
    'bloomberg': 1.0,      # Tier 1 sources
    'reuters': 1.0,
    'wsj': 1.0,
    'marketwatch': 0.75,   # Tier 2 sources
    'cnbc': 0.75,
    'seeking_alpha': 0.5,  # Tier 3 sources
    'retail_blogs': 0.25
}

final_score = base_score * source_weight
```

**4. Recency Bonus**

```python
if article_age_hours < 1:
    score += 10  # Breaking news
elif article_age_hours < 4:
    score += 5   # Recent news
```

#### **Invalidation Decision Matrix (Fully Automated)**

| Severity Score | Decision | Action |
|----------------|----------|--------|
| **85-100** | CRITICAL - Auto-exit | Exit immediately at market close (4:50 PM ANALYZE) |
| **70-84** | STRONG invalidation - Auto-exit | Exit immediately at market close (4:50 PM ANALYZE) |
| **50-69** | MODERATE concern | Continue holding, re-check next ANALYZE (24 hours) |
| **30-49** | MILD concern | Note in position log, continue monitoring |
| **<30** | Normal noise | Ignore |

**Example - Boeing Case:**
```
Article: "Boeing reports $4.9B charge on 777X delays"
Keywords found:
- "charge" (critical): 50 pts
- "delay" (severe): 40 pts
- "$4.9B" (quantified): +15 pts
- Source: Bloomberg: ×1.0
- Recency: <1 hour: +10 pts

Total Score: (50 + 40 + 15 + 10) × 1.0 = 115 points → CRITICAL

Decision: Auto-exit immediately
Reason: "Catalyst invalidated - $4.9B charge announced"
```

**Exit Reason Format:**
```
"Catalyst invalidated - earnings guidance lowered"
"Catalyst invalidated - sector reversal"
"Catalyst invalidated - major negative news"
```

#### **Catalyst-Specific Invalidation Rules**

**Earnings Beat Catalyst:**
- Guidance lowered within 7 days of entry → Exit
- Earnings restatement → Exit
- Major negative development (investigation, etc.) → Exit

**Analyst Upgrade Catalyst:**
- Downgrade from same or higher-tier firm → Exit
- Price target lowered significantly → Exit
- Thesis contradicted by news → Exit

**Sector Momentum Catalyst:**
- Macro driver reverses (oil crashes, policy change) → Exit
- 3+ stocks in sector breaking down → Exit
- Sector ETF breaks below 50-day MA → Monitor closely

**Technical Breakout Catalyst:**
- Volume dries up (<1x average for 2 days) → Exit
- Breaks back below breakout level → Exit
- Fails to make higher high within 3 days → Monitor

**FDA Approval / Biotech Catalyst:**
- Inverted-J pattern: Peak effectiveness Day 0-1, then 29% average decline over 86 days
- Entry timing critical: Must enter within 24 hours of approval
- Catalyst age >1 day: Reject entry (peak momentum passed)
- Monitor for safety issues, trial failures, or regulatory reversals

### Exit Trigger 5: Better Opportunity (Portfolio Full)

**Checked:** 8:45 AM GO command

**Trigger Condition:**
```python
if portfolio_count == 10 and new_tier1_opportunity_found:
    # Identify weakest current position
    weakest = find_lowest_conviction_position()
    if new_opportunity_conviction > weakest.conviction:
        exit_position(weakest, reason="Better opportunity identified")
        enter_position(new_opportunity)
```

**Parameters:**
- Portfolio must be full (10 positions)
- New opportunity must be Tier 1
- New opportunity conviction > weakest current position
- Weakest position must have been held ≥2 days (minimum hold)

**Weakest Position Criteria:**
1. Lowest conviction level
2. Stale catalyst (>5 days old)
3. Fading momentum (low volume, news score declining)
4. Smallest unrealized gain (if multiple at same conviction)

**Exit Reason Format:**
```
"Replaced with higher conviction opportunity (TICKER)"
```

### Exit Prohibitions (Never Do)

| Prohibition | Consequence | Exception |
|-------------|-------------|-----------|
| **Hold through -7% stop** | Account destruction | None |
| **Average down on losers** | Compounds mistakes | None |
| **Sell winners early** | Kills profitability | Only if target hit |
| **Exit without reason** | No learning loop | None |
| **Panic sell on noise** | Whipsaw losses | Only if invalidation score >85 |

### Position Age & Exit Timing

| Days Held | Action | Rationale |
|-----------|--------|-----------|
| **0-1** | Cannot exit (except stop/target) | Minimum 2-day hold enforcement |
| **2-4** | Optimal exit window | 60-70% of trades close here |
| **5-7** | Standard exit window | Target hit or momentum fading |
| **8-14** | Extended hold | Thesis still valid, approaching target |
| **15-20** | Late stage | Watch closely, prepare to exit |
| **21+** | Time stop triggered | Exit and redeploy |

### Exit Execution Flow

**At 4:50 PM ANALYZE command:**
```
For each of 10 positions:
1. Fetch current closing price
2. Calculate unrealized P&L
3. Check exit triggers in order:
   a. Stop loss hit? → Exit
   b. Target reached? → Exit
   c. News invalidation score >85? → Exit
   d. Days held ≥21? → Exit
4. If any trigger hit:
   - Calculate exact return % and $
   - Standardize exit reason
   - Log to completed_trades.csv
   - Update account status
5. Else:
   - Update position metrics
   - Increment days_held counter
   - Continue holding
```

**At 8:45 AM GO command:**
```
Review portfolio:
1. Overnight news check (catalyst validation)
2. Premarket gap analysis
3. Identify positions to exit for better opportunities
4. If exits needed:
   - Save to pending_positions.json
   - Execute at 9:45 AM EXECUTE command
```

---

## POSITION SIZING

### Overview

**Position sizing determines risk-adjusted returns.** We use a **simple conviction-based system** without complex formulas:

- **High conviction:** 12-15% of account
- **Medium conviction:** 8-10% of account
- **Low conviction:** Skip (do not enter)

**No ATR, Beta, Kelly Criterion, or drawdown protocols** - Keep it simple.

### Conviction Levels

#### **HIGH Conviction (12-15% Position)**

**Criteria (ALL must be met):**
- Tier 1 catalyst
- News validation score ≥15 points
- 5+ supporting factors present
- VIX <25
- Multi-catalyst synergy OR earnings beat >15% with guidance

**Examples:**
- NVDA: Earnings beat 18%, guidance raised, 3 analyst upgrades in 24 hours
- GOOGL: Earnings beat + contract win announced same day
- Any stock with 2+ simultaneous Tier 1 catalysts

**Position Size:** 12-15% of account
**Expected Win Rate:** 70-85%
**Target:** +12-15%

#### **MEDIUM Conviction (8-10% Position)**

**Criteria:**
- Tier 1 catalyst
- News validation score 5-14 points
- 3-4 supporting factors
- VIX <30
- Standard single catalyst

**Examples:**
- XOM: Earnings beat 12%, guidance unchanged
- PLTR: Major analyst upgrade from Goldman Sachs
- LLY: Strong sector momentum in Healthcare

**Position Size:** 8-10% of account (default to 10% if unsure)
**Expected Win Rate:** 55-70%
**Target:** +10-12%

#### **LOW Conviction (SKIP)**

**Criteria:**
- Tier 2 catalyst OR
- News validation score <5 points OR
- <3 supporting factors OR
- VIX >30

**Examples:**
- Earnings beat only 6%
- Analyst upgrade from small firm
- Stale catalyst (>5 days old)
- Contradicting news detected

**Position Size:** 0% (do not enter)
**Rationale:** Capital preservation, wait for better setups

### Position Sizing Formula (Simple)

```python
def calculate_position_size(account_value, conviction_level):
    """
    Simple conviction-based sizing
    No complex formulas, no volatility adjustments
    """
    if conviction_level == "HIGH":
        size_percent = 0.13  # 13% (midpoint of 12-15%)
    elif conviction_level == "MEDIUM":
        size_percent = 0.10  # 10% (standard)
    elif conviction_level == "MEDIUM-HIGH":
        size_percent = 0.11  # 11%
    else:
        size_percent = 0.00  # Skip

    position_size = account_value * size_percent
    return position_size
```

**Example:**
```
Account value: $1,000
Conviction: HIGH

Position size = $1,000 × 0.13 = $130 (13%)
```

### Portfolio Constraints

**Maximum Positions:** 10
**Maximum Sector Concentration:** 3 positions per sector
**Maximum Sector Allocation:** 40% of portfolio in any sector

**Why 10 Positions:**
- Diversification without dilution
- Manageable for daily review
- 10% average = simple mental math
- Research shows 8-12 positions optimal for risk-adjusted returns

**Sector Limits:**
```python
def check_sector_limits(portfolio, new_position):
    """
    Enforce sector concentration limits
    """
    sector = new_position.sector

    # Count existing positions in sector
    sector_count = sum(1 for p in portfolio if p.sector == sector)

    if sector_count >= 3:
        return False, "Maximum 3 positions per sector"

    # Calculate sector allocation
    sector_value = sum(p.position_size for p in portfolio if p.sector == sector)
    sector_percent = sector_value / account_value

    if sector_percent >= 0.40:
        return False, "Maximum 40% allocation per sector"

    return True, "Sector limits OK"
```

### Cash Management

**Target:** 0% cash (fully invested)
**Rationale:**
- Maximizes compound returns
- 10 positions × 10% average = 100% deployed
- Conviction-based sizing naturally creates 0-20% cash when opportunities are scarce

**When to Hold Cash:**
- VIX >35 (system pause)
- <10 Tier 1 opportunities available
- After major losses (optional, not automated)

**Cash Tracking:**
```python
cash_available = starting_capital - sum(position.position_size for position in portfolio) + realized_pl
```

### No Complex Adjustments (For Now)

**What we DON'T use initially (to keep it simple):**

❌ **Kelly Criterion** (Revisit after 100+ trades)
- Requires extensive historical data (100+ trades)
- Suggests 28% positions with 55% win rate (too aggressive)
- Half-Kelly (14%) better but still complex
- **Review after:** 100 completed trades with stable win rate

❌ **ATR (Average True Range) Volatility Sizing** (Revisit after 50+ trades)
- Requires 14-day ATR calculation
- Position size = (Account Risk / ATR × Multiplier) × Share Price
- Research shows: 20-30% Sharpe improvement with volatility management
- **Review after:** 50 trades to assess if complexity justified

❌ **Beta Adjustments** (Revisit after 50+ trades)
- High-beta stocks (β>1.5) get -20-40% size reduction
- Requires fetching beta data
- Most momentum stocks are high-beta anyway
- **Review after:** 50 trades, if high-volatility trades underperform

❌ **Drawdown Protocols** (Revisit after 50+ trades)
- After 2 losses: Reduce size 25%
- After 3 losses: Reduce size 50%
- After 5 losses: Pause system
- Sounds good but adds psychological complexity
- **Review after:** 50 trades, if losing streaks >3 occur

❌ **VIX-Based Cash Allocation** (Current approach is VIX filter instead)
- VIX <15: 100% invested
- VIX 15-20: 80% invested
- VIX 20-30: 60% invested
- We use VIX as entry filter instead (simpler)

**Why Skip These Initially:**
- Add 5-10% edge at most
- Increase system complexity significantly
- Harder to track, learn, and optimize
- Violates Pareto principle (80/20 rule)
- **BUT:** Can add after validating core system (50-100 trades)

**Review Triggers:**
- **After 50 trades:** Consider ATR/Beta adjustments if volatility causing issues
- **After 100 trades:** Consider Kelly Criterion baseline with stable win rate data
- **If max drawdown >15%:** Implement drawdown protocols
- **If Sharpe ratio <1.0:** Reevaluate volatility management

### Position Sizing Learning Loop

**Track in Weekly Learning:**
```python
def analyze_sizing_effectiveness():
    """
    Did conviction-based sizing improve returns?
    """
    high_conviction_trades = [t for t in trades if t.conviction == "HIGH"]
    medium_conviction_trades = [t for t in trades if t.conviction == "MEDIUM"]

    high_win_rate = calculate_win_rate(high_conviction_trades)
    medium_win_rate = calculate_win_rate(medium_conviction_trades)

    high_avg_return = calculate_avg_return(high_conviction_trades)
    medium_avg_return = calculate_avg_return(medium_conviction_trades)

    print(f"High conviction: {high_win_rate:.1f}% win rate, {high_avg_return:.2f}% avg return")
    print(f"Medium conviction: {medium_win_rate:.1f}% win rate, {medium_avg_return:.2f}% avg return")

    # Validate hypothesis
    if high_win_rate > medium_win_rate + 10:
        print("✓ Conviction-based sizing working as expected")
    else:
        print("⚠ Conviction assessment may need calibration")
```

**Track in Trade CSV:**
- Add column: `Conviction_Level` (High, Medium-High, Medium)
- Add column: `Position_Size_Percent` (actual % allocated)
- Compare conviction vs actual outcomes

---

## LEARNING STRATEGY

### Overview

The learning system is **already implemented** in v5.0. We enhance it to track new metrics from our Pareto improvements:
- News validation/invalidation effectiveness
- Catalyst tier performance
- VIX regime performance
- Conviction-based sizing accuracy

### Three-Tier Learning Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DAILY LEARNING                        │
│                  (Every day, 5:00 PM)                    │
│                                                          │
│  Purpose: Fast tactical pattern detection               │
│  - Analyze last 7 days of trades                        │
│  - Identify failing catalysts (<35% win rate)           │
│  - Auto-exclude poor performers                         │
│  - Track news monitoring effectiveness                  │
│                                                          │
│  Output: catalyst_exclusions.json (immediate effect)    │
└────────────────┬────────────────────────────────────────┘
                 │
    ┌────────────▼─────────────┐
    │   WEEKLY LEARNING        │
    │  (Fridays, 5:30 PM)      │
    │                          │
    │  Purpose: Optimization   │
    │  - Deep catalyst stats   │
    │  - Optimal hold times    │
    │  - Tier performance      │
    │  - Conviction accuracy   │
    │                          │
    │  Output: Reports         │
    └────────────┬─────────────┘
                 │
       ┌─────────▼──────────┐
       │  MONTHLY LEARNING  │
       │ (Last Sun, 6:00 PM)│
       │                    │
       │  Purpose: Strategic│
       │  - Regime detection│
       │  - Major shifts    │
       │  - VIX analysis    │
       │  - Strategy tuning │
       │                    │
       │  Output: Evolution │
       └────────────────────┘
```

### Daily Learning (Tactical - 5:00 PM)

**File:** `learn_daily.py` (already exists)

**Current Functionality:**
- Analyzes last 7 days of completed trades
- Groups by catalyst type
- Calculates win rate per catalyst
- Auto-excludes catalysts with <35% win rate (over 10+ trades)
- Updates `catalyst_exclusions.json`
- Appends insights to `lessons_learned.md`

**Enhancements Needed:**

#### **1. News Monitoring Effectiveness**

**Track:**
```python
def analyze_news_effectiveness(trades):
    """
    Did news validation/invalidation work?
    """
    # Validation effectiveness (at entry)
    validated_entries = [t for t in trades if t.news_validated == True]
    rejected_entries = [...]  # Log of opportunities we passed on

    validated_win_rate = calculate_win_rate(validated_entries)

    # Did we miss good opportunities by rejecting stale catalysts?
    # (Track separately if possible)

    # Invalidation effectiveness (at exit)
    news_exits = [t for t in trades if "invalidated" in t.exit_reason]

    for trade in news_exits:
        # Calculate: What would P&L be if held to -7% stop?
        avoided_loss = compare_news_exit_vs_stop_loss(trade)

    total_saved = sum(avoided_loss for trade in news_exits)

    # False positives
    false_positives = [t for t in news_exits if stock_recovered_after_exit(t)]
    false_positive_rate = len(false_positives) / len(news_exits)

    print(f"News exits: {len(news_exits)}")
    print(f"Total loss prevented: ${total_saved:.2f}")
    print(f"False positive rate: {false_positive_rate:.1%}")
```

**Output:**
```
News Monitoring Report (Last 7 Days):
- Validated entries: 5 (win rate: 80%)
- Rejected entries: 3 (stale catalysts)
- News-triggered exits: 2
- Loss prevented: $18.50
- False positive rate: 0% (0/2)
✓ News monitoring working effectively
```

#### **2. Catalyst Tier Performance**

**Track:**
```python
def analyze_tier_performance(trades):
    """
    Are Tier 1 catalysts outperforming Tier 2?
    """
    tier1 = [t for t in trades if t.catalyst_tier == "Tier1"]
    tier2 = [t for t in trades if t.catalyst_tier == "Tier2"]

    tier1_win_rate = calculate_win_rate(tier1)
    tier2_win_rate = calculate_win_rate(tier2)

    tier1_avg_return = calculate_avg_return(tier1)
    tier2_avg_return = calculate_avg_return(tier2)

    print(f"Tier 1: {tier1_win_rate:.1f}% win rate, {tier1_avg_return:+.2f}% avg")
    print(f"Tier 2: {tier2_win_rate:.1f}% win rate, {tier2_avg_return:+.2f}% avg")

    # Validation
    if tier1_win_rate > tier2_win_rate + 15:
        print("✓ Tier system working as designed")
    else:
        print("⚠ Tier 2 performing unexpectedly well - investigate")
```

**Required CSV Fields (add):**
- `Catalyst_Tier`: "Tier1" or "Tier2"
- `Catalyst_Age_Days`: Days between catalyst event and entry
- `News_Validation_Score`: 0-20 points from entry validation
- `Multi_Catalyst`: Boolean (True if 2+ catalysts)

### Weekly Learning (Optimization - Fridays 5:30 PM)

**File:** `learn_weekly.py` (already exists)

**Current Functionality:**
- Deep catalyst performance analysis (win rate, avg return, median, best/worst)
- Calculates optimal stop loss & profit targets from actual data
- Analyzes hold times (winners vs losers, optimal exit day)
- Entry timing analysis (day of week patterns)
- Updates `catalyst_performance.csv`
- Generates comprehensive weekly report

**Enhancements Needed:**

#### **1. VIX Regime Performance**

**Track:**
```python
def analyze_vix_regime_performance(trades):
    """
    Does win rate vary by VIX level at entry?
    """
    vix_buckets = {
        'low': [t for t in trades if t.vix_at_entry < 20],
        'medium': [t for t in trades if 20 <= t.vix_at_entry < 30],
        'high': [t for t in trades if 30 <= t.vix_at_entry < 35],
        'extreme': [t for t in trades if t.vix_at_entry >= 35]
    }

    for regime, bucket_trades in vix_buckets.items():
        if len(bucket_trades) >= 3:
            win_rate = calculate_win_rate(bucket_trades)
            avg_return = calculate_avg_return(bucket_trades)
            print(f"VIX {regime}: {win_rate:.1f}% win rate, {avg_return:+.2f}% avg ({len(bucket_trades)} trades)")

    # Recommendation
    if vix_buckets['high'] has low win rate:
        print("⚠ Consider lowering VIX threshold from 35 to 30")
```

**Required CSV Fields (add):**
- `VIX_At_Entry`: VIX level when position entered
- `Market_Regime`: "Bull", "Bear", "Choppy" (from SPY MA analysis)

#### **2. Conviction Accuracy**

**Track:**
```python
def analyze_conviction_accuracy(trades):
    """
    Are high conviction trades actually winning more?
    """
    by_conviction = {
        'HIGH': [t for t in trades if t.conviction == "HIGH"],
        'MEDIUM-HIGH': [t for t in trades if t.conviction == "MEDIUM-HIGH"],
        'MEDIUM': [t for t in trades if t.conviction == "MEDIUM"]
    }

    for level, trades_list in by_conviction.items():
        if len(trades_list) >= 3:
            win_rate = calculate_win_rate(trades_list)
            avg_return = calculate_avg_return(trades_list)
            avg_size = statistics.mean([t.position_size_percent for t in trades_list])

            print(f"{level}: {win_rate:.1f}% win rate, {avg_return:+.2f}% avg, {avg_size:.1f}% avg size")

    # Validation
    high_wr = by_conviction['HIGH'].win_rate
    medium_wr = by_conviction['MEDIUM'].win_rate

    if high_wr > medium_wr + 10:
        print("✓ Conviction assessment accurate")
    else:
        print("⚠ Conviction calibration needed - high not outperforming medium")
```

#### **3. Catalyst Age Analysis**

**Track:**
```python
def analyze_catalyst_freshness(trades):
    """
    Does catalyst age correlate with win rate?
    """
    age_buckets = {
        '0-2 days': [t for t in trades if t.catalyst_age_days <= 2],
        '3-5 days': [t for t in trades if 3 <= t.catalyst_age_days <= 5],
        '6-10 days': [t for t in trades if 6 <= t.catalyst_age_days <= 10],
        '10+ days': [t for t in trades if t.catalyst_age_days > 10]
    }

    for age_range, bucket_trades in age_buckets.items():
        if len(bucket_trades) >= 3:
            win_rate = calculate_win_rate(bucket_trades)
            print(f"Catalyst age {age_range}: {win_rate:.1f}% win rate")

    # Recommendation
    if age_buckets['6-10 days'].win_rate < 50:
        print("⚠ Catalysts >5 days old underperforming - tighten freshness requirement")
```

### Monthly Learning (Strategic - Last Sunday 6:00 PM)

**File:** `learn_monthly.py` (already exists)

**Current Functionality:**
- Market regime detection (Bull/Bear/Sideways)
- Comprehensive monthly statistics (win rate, Sharpe, max drawdown)
- Strategy effectiveness evaluation (improving vs declining)
- Identifies best practices from big winners (>10% returns)
- Rolling win rate analysis to detect trends
- Generates executive summary and action items

**Enhancements Needed:**

#### **1. News Monitoring ROI**

**Track:**
```python
def calculate_news_monitoring_roi(trades):
    """
    What's the financial impact of news monitoring?
    """
    # Losses prevented by news exits
    news_exits = [t for t in trades if "invalidated" in t.exit_reason]
    total_prevented = sum(estimate_prevented_loss(t) for t in news_exits)

    # Opportunities validated
    validated_entries = [t for t in trades if t.news_validated]
    validated_returns = sum(t.return_dollars for t in validated_entries)

    # False positives (opportunity cost)
    false_positives = [t for t in news_exits if stock_recovered(t)]
    opportunity_cost = sum(estimate_missed_gain(t) for t in false_positives)

    net_roi = total_prevented + validated_returns - opportunity_cost

    print(f"\nNews Monitoring ROI (Month):")
    print(f"  Losses prevented: +${total_prevented:.2f}")
    print(f"  Validated entry returns: +${validated_returns:.2f}")
    print(f"  False positive cost: -${opportunity_cost:.2f}")
    print(f"  NET ROI: ${net_roi:.2f}")
```

#### **2. Tier Definition Adjustments**

**Track:**
```python
def evaluate_tier_definitions(trades):
    """
    Should we promote/demote specific catalyst types between tiers?
    """
    # Break down Tier 1 by sub-type
    tier1_subtypes = {
        'Earnings_Beat_Guidance': [...],
        'Multi_Catalyst': [...],
        'Analyst_Upgrade_Major': [...],
        'Sector_Momentum': [...],
        'Technical_Breakout': [...]
    }

    for subtype, subtype_trades in tier1_subtypes.items():
        if len(subtype_trades) >= 10:
            win_rate = calculate_win_rate(subtype_trades)

            if win_rate < 55:
                print(f"⚠ {subtype} underperforming (Tier 1): {win_rate:.1f}%")
                print(f"   Recommendation: Demote to Tier 2 or exclude")
            elif win_rate > 75:
                print(f"✓ {subtype} excellent (Tier 1): {win_rate:.1f}%")
                print(f"   Recommendation: Prioritize this catalyst type")
```

#### **3. Strategy Evolution Tracking**

**Track:**
```python
def track_strategy_evolution(trades):
    """
    Is the strategy improving over time?
    """
    # Split trades into cohorts
    first_25 = trades[:25]
    second_25 = trades[25:50]
    recent_25 = trades[-25:]

    cohorts = {
        'First 25 trades': first_25,
        'Second 25 trades': second_25,
        'Recent 25 trades': recent_25
    }

    print("\nStrategy Evolution Analysis:")
    for period, cohort in cohorts.items():
        if len(cohort) >= 10:
            win_rate = calculate_win_rate(cohort)
            avg_return = calculate_avg_return(cohort)
            sharpe = calculate_sharpe(cohort)

            print(f"{period}: {win_rate:.1f}% WR, {avg_return:+.2f}% avg, {sharpe:.2f} Sharpe")

    # Trend analysis
    if recent_25.win_rate > first_25.win_rate + 10:
        print("✓ IMPROVING - Learning system working")
    elif recent_25.win_rate < first_25.win_rate - 10:
        print("⚠ DECLINING - Major strategy review needed")
```

### Learning Data Structure

**Enhanced completed_trades.csv:**

```csv
Trade_ID, Entry_Date, Exit_Date, Ticker,
Premarket_Price, Entry_Price, Exit_Price, Gap_Percent,
Shares, Position_Size, Position_Size_Percent,
Hold_Days, Return_Percent, Return_Dollars,
Exit_Reason, Catalyst_Type, Catalyst_Tier, Catalyst_Age_Days,
Multi_Catalyst, News_Validation_Score, News_Exit_Triggered,
Sector, Relative_Strength_Pct, Confidence_Level, Conviction_Level,
VIX_At_Entry, Market_Regime, Macro_Event_Near,
Stop_Loss, Price_Target,
Thesis, What_Worked, What_Failed,
Account_Value_After
```

**New Fields (Phase 1-4):**
- `Position_Size_Percent`: Actual % of account (8-15%)
- `Catalyst_Tier`: "Tier1" or "Tier2"
- `Catalyst_Age_Days`: Days between catalyst event and entry
- `Multi_Catalyst`: Boolean ("True" or "False")
- `News_Validation_Score`: 0-20 points from GO command validation
- `News_Exit_Triggered`: Boolean ("True" if exited due to news invalidation)
- `Relative_Strength_Pct`: Stock outperformance vs sector (e.g., 5.2%)
- `Conviction_Level`: "HIGH", "MEDIUM-HIGH", "MEDIUM"
- `VIX_At_Entry`: VIX level when entered
- `Market_Regime`: "Bull", "Bear", "Choppy"
- `Macro_Event_Near`: "FOMC", "CPI", "NFP", or "None"

**Fields to Add After 50+ Trades:**
- `ATR_At_Entry`: 14-day Average True Range
- `Beta`: Stock beta coefficient
- `Volatility_Adjustment`: Size adjustment factor (if implemented)

### New Learning Output Files

**1. `learning_data/news_monitoring_log.csv`**
```csv
Date, Ticker, Event_Type, Headline, Severity_Score, Decision, Entry_Price, Exit_Price, Outcome
2025-10-30, BA, INVALIDATION, "Boeing $4.9B charge", 95, EXIT, 165.00, 157.50, -4.5%
2025-10-31, NVDA, VALIDATION, "Strong earnings momentum", 18, ENTER, 207.00, 219.50, +6.0%
```

**2. `learning_data/tier_performance.json`**
```json
{
  "last_updated": "2025-10-30",
  "tier1": {
    "total_trades": 15,
    "win_rate": 73.3,
    "avg_return": 9.2,
    "status": "outperforming target (70%)"
  },
  "tier2": {
    "total_trades": 5,
    "win_rate": 60.0,
    "avg_return": 6.1,
    "status": "meeting expectations"
  }
}
```

**3. `learning_data/vix_regime_performance.json`**
```json
{
  "last_updated": "2025-10-30",
  "vix_low": {
    "range": "<20",
    "trades": 12,
    "win_rate": 75.0,
    "recommendation": "Favorable regime"
  },
  "vix_medium": {
    "range": "20-30",
    "trades": 8,
    "win_rate": 62.5,
    "recommendation": "Acceptable regime"
  },
  "vix_high": {
    "range": "30-35",
    "trades": 2,
    "win_rate": 50.0,
    "recommendation": "Monitor - small sample"
  }
}
```

### Learning Feedback Loop

```
┌────────────────────────────────────────────────┐
│           TRADING OPERATIONS                    │
│   GO → EXECUTE → ANALYZE → Log outcomes        │
└───────────────┬────────────────────────────────┘
                │
                ▼
      ┌─────────────────────┐
      │   DAILY LEARNING    │
      │  - News effectiveness│
      │  - Tier performance │
      │  - Quick exclusions │
      └─────────┬───────────┘
                │
                ▼
      ┌─────────────────────┐
      │  WEEKLY LEARNING    │
      │  - VIX regime stats │
      │  - Conviction accuracy│
      │  - Catalyst age     │
      └─────────┬───────────┘
                │
                ▼
      ┌─────────────────────┐
      │  MONTHLY LEARNING   │
      │  - Tier adjustments │
      │  - Strategy evolution│
      │  - ROI analysis     │
      └─────────┬───────────┘
                │
                ▼
      ┌─────────────────────┐
      │  STRATEGY UPDATES   │
      │  - catalyst_exclusions│
      │  - tier_definitions │
      │  - vix_thresholds   │
      └─────────┬───────────┘
                │
                └───────────► Next Week's Decisions
                              (Better informed)
```

### Success Metrics

**We'll know the system is working when:**

| Metric | Target | Measurement Frequency |
|--------|--------|----------------------|
| **Overall win rate** | 70%+ | Weekly |
| **Tier 1 win rate** | 70%+ | Weekly |
| **Tier 2 win rate** | 55%+ | Weekly |
| **High conviction win rate** | 75%+ | Monthly |
| **News exit effectiveness** | <20% false positive rate | Monthly |
| **VIX filter effectiveness** | Win rate 10%+ higher in VIX <30 | Monthly |
| **Catalyst age correlation** | 0-3 days > 60% WR | Monthly |
| **Strategy improvement** | Win rate increasing over time | Quarterly |

---

## IMPLEMENTATION ROADMAP

### Current State (v5.0 - Baseline)

**What's Working:**
✅ 10-position portfolio management
✅ GO/EXECUTE/ANALYZE workflow
✅ -7% stop loss, +10% target (mechanical)
✅ Catalyst-based entry system
✅ Daily/weekly/monthly learning loops
✅ Catalyst exclusion mechanism
✅ 15-minute delayed Polygon.io pricing
✅ Trade logging to CSV
✅ Claude AI decision-making integration

**What's Missing:**
❌ News-based catalyst validation/invalidation
❌ Catalyst tier system (Tier 1/2/3)
❌ VIX filter (market regime check)
❌ Conviction-based position sizing
❌ Enhanced learning metrics (tier/VIX/conviction tracking)

### Phase 1: News Monitoring (HIGHEST PRIORITY)

**Goal:** Prevent BA-type losses, validate entry quality

**Implementation Steps:**

**1.1 Create NewsMonitor Class** (2-3 hours)
```python
class NewsMonitor:
    def __init__(self):
        self.polygon_api_key = POLYGON_API_KEY

    def fetch_news(self, ticker, limit=10):
        """Fetch recent news from Polygon.io"""

    def validate_catalyst_entry(self, ticker, catalyst_type, catalyst_date):
        """GO command - validate catalyst freshness"""
        # Returns: validation_score (0-20), decision (VALIDATED/REJECTED/UPGRADED)

    def check_catalyst_invalidation(self, ticker):
        """ANALYZE command - detect catalyst failure"""
        # Returns: severity_score (0-100), decision (EXIT/MONITOR/HOLD)
```

**1.2 Integrate into GO Command** (1 hour)
- Before Claude AI analyzes opportunities, run news validation
- Add validation score to context
- Flag stale/weak catalysts

**1.3 Integrate into ANALYZE Command** (1 hour)
- After checking mechanical stops/targets, check news
- If severity score >85, trigger exit
- Log news exit to CSV with reason

**1.4 Create News Monitoring Log** (30 mins)
- CSV file: `learning_data/news_monitoring_log.csv`
- Track all validations and invalidations
- Feed into daily learning

**Validation:**
- Backtest on BA case: Would severity score >85? ✓
- Test on 5 historical earnings misses
- Verify false positive rate <20%

**Deliverables:**
- [ ] NewsMonitor class implemented
- [ ] GO command integration complete
- [ ] ANALYZE command integration complete
- [ ] news_monitoring_log.csv created
- [ ] Daily learning enhanced to track news effectiveness

**Expected Impact:** 30-50% reduction in catalyst invalidation losses

---

### Phase 2: Catalyst Tier System (HIGH PRIORITY)

**Goal:** Formalize entry quality standards

**Implementation Steps:**

**2.1 Create Tier Definitions File** (1 hour)
```json
// strategy_evolution/tier_definitions.json
{
  "tier1": {
    "catalysts": [
      {
        "type": "Earnings_Beat_Guidance",
        "criteria": {
          "eps_beat_percent": ">=10",
          "revenue_beat": true,
          "guidance_raised": true
        },
        "target_win_rate": 0.70,
        "position_size": 0.12-0.15
      },
      {
        "type": "Multi_Catalyst",
        "criteria": {
          "catalyst_count": ">=2"
        },
        "target_win_rate": 0.75,
        "position_size": 0.12-0.15
      }
    ]
  },
  "tier2": {
    "catalysts": [...]
  }
}
```

**2.2 Update GO Command Prompt** (30 mins)
- Include tier definitions in Claude context
- Request tier assignment in response
- Validate tier against definitions

**2.3 Enhance Trade Logging** (30 mins)
- Add `Catalyst_Tier` column to CSV
- Add `Catalyst_Age_Days` column
- Add `Multi_Catalyst` boolean column

**2.4 Enhance Weekly Learning** (1 hour)
- Add tier performance analysis
- Track win rate by tier
- Recommend tier adjustments

**Validation:**
- Review last 20 trades, assign tiers retroactively
- Calculate theoretical win rate improvement
- Verify Tier 1 > Tier 2 by ≥10%

**Deliverables:**
- [ ] tier_definitions.json created
- [ ] GO command enhanced with tier context
- [ ] CSV columns added
- [ ] Weekly learning tracks tier performance
- [ ] Monthly learning recommends tier adjustments

**Expected Impact:** 10-15% win rate improvement

---

### Phase 3: VIX Filter + Macro Calendar (HIGH PRIORITY)

**Goal:** Avoid trading in hostile market regimes and during volatile macro events

**Implementation Steps:**

**3.1 Create VIX Fetcher** (30 mins)
```python
def fetch_vix_level():
    """
    Fetch current VIX from Polygon or Yahoo Finance
    Returns: float (VIX level)
    """
    # Use Polygon.io or fallback to yfinance
```

**3.2 Integrate into GO Command** (30 mins)
- Fetch VIX at 8:45 AM
- Check thresholds: **UPDATED to 30 (not 35)**
- Adjust decision logic:
  - VIX >35: "SYSTEM SHUTDOWN"
  - VIX 30-35: "HIGHEST CONVICTION ONLY" (50% effectiveness)
  - VIX <30: "NORMAL OPERATIONS"

**3.3 Add Macro Event Calendar** (1 hour)
- Create economic calendar fetcher (FOMC, CPI, NFP dates)
- Check blackout windows before entries:
  - FOMC: 2 days before → 1 day after
  - CPI/NFP: Day before → Day of
- Flag prohibited entry dates

**3.4 Log VIX and Macro Events** (15 mins)
- Add `VIX_At_Entry` column to CSV
- Add `Market_Regime` column (Bull/Bear/Choppy)
- Add `Macro_Event_Near` column (FOMC/CPI/NFP/None)

**3.5 Enhance Monthly Learning** (1 hour)
- Add VIX regime performance analysis
- Track win rate by VIX bucket
- Track performance around macro events
- Recommend threshold adjustments

**Validation:**
- Verify VIX 30-35 triggers "highest conviction only" mode
- Confirm FOMC/CPI/NFP blackouts block entries
- Backtest: Would macro calendar have prevented any bad trades?

**Deliverables:**
- [ ] VIX fetcher implemented with 30 threshold (not 35)
- [ ] Macro event calendar integrated
- [ ] GO command checks both VIX and calendar
- [ ] CSV columns added
- [ ] Monthly learning tracks regime + event performance
- [ ] vix_regime_performance.json created

**Expected Impact:** 5-10% win rate improvement + volatility reduction

---

### Phase 4: Conviction-Based Sizing + Relative Strength (HIGH PRIORITY)

**Goal:** Allocate more capital to best opportunities and filter for sector leaders

**Implementation Steps:**

**4.1 Add Relative Strength Calculator** (1 hour)
```python
def calculate_relative_strength(ticker, sector_etf):
    """
    Calculate stock performance vs sector ETF over 3 months
    Returns: relative_strength_percent (positive = outperforming)
    """
    stock_return_3m = get_3month_return(ticker)
    sector_return_3m = get_3month_return(sector_etf)

    relative_strength = stock_return_3m - sector_return_3m
    return relative_strength

def check_relative_strength_filter(ticker, sector):
    """
    REQUIRED FILTER: Stock must outperform sector by ≥3%
    Returns: (passed, relative_strength)
    """
    sector_etf_map = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Financials': 'XLF',
        # ... etc for all 11 sectors
    }

    sector_etf = sector_etf_map.get(sector)
    rs = calculate_relative_strength(ticker, sector_etf)

    if rs >= 3.0:
        return (True, rs)
    else:
        return (False, rs)
```

**4.2 Create Conviction Scorer** (1 hour)
```python
def calculate_conviction_level(catalyst_tier, news_score, supporting_factors, vix, relative_strength):
    """
    Determine conviction level based on multiple factors
    Returns: "HIGH", "MEDIUM-HIGH", "MEDIUM", "SKIP"

    IMPORTANT: relative_strength ≥3% is REQUIRED
    """
    # First check: Relative strength filter
    if relative_strength < 3.0:
        return "SKIP"  # Fails required filter

    # Second check: Catalyst tier must be Tier 1
    if catalyst_tier != "Tier1":
        return "SKIP"

    # Third check: Conviction based on multiple factors
    if news_score >= 15 and supporting_factors >= 5 and vix < 25:
        return "HIGH"
    elif news_score >= 10 and supporting_factors >= 4 and vix < 30:
        return "MEDIUM-HIGH"
    elif news_score >= 5 and supporting_factors >= 3 and vix < 30:
        return "MEDIUM"
    else:
        return "SKIP"
```

**4.2 Update Position Sizing Logic** (30 mins)
```python
CONVICTION_SIZES = {
    "HIGH": 0.13,           # 13% (midpoint of 12-15%)
    "MEDIUM-HIGH": 0.11,    # 11%
    "MEDIUM": 0.10,         # 10% (standard)
    "SKIP": 0.00
}

def calculate_position_size(account_value, conviction):
    return account_value * CONVICTION_SIZES[conviction]
```

**4.3 Update EXECUTE Command** (30 mins)
- Read conviction level from pending_positions.json
- Apply conviction-based sizing
- Log actual size to CSV

**4.4 Enhance Weekly Learning** (30 mins)
- Add conviction accuracy analysis
- Compare conviction vs outcomes
- Recommend calibration adjustments

**Validation:**
- Simulate on last 25 trades
- Calculate return difference vs flat 10%
- Verify high conviction > medium conviction

**Deliverables:**
- [ ] Conviction scorer implemented
- [ ] Position sizing updated
- [ ] CSV columns added (Conviction_Level, Position_Size_Percent)
- [ ] Weekly learning tracks conviction accuracy

**Expected Impact:** 15-25% improvement in risk-adjusted returns (Sharpe ratio)

---

### Phase 5: Learning Enhancements (ONGOING)

**Goal:** Track new metrics from Phases 1-4

**Implementation Steps:**

**5.1 Enhanced Daily Learning** (1 hour)
- Add news monitoring effectiveness
- Add tier performance tracking
- Update lessons_learned.md format

**5.2 Enhanced Weekly Learning** (1 hour)
- Add VIX regime analysis
- Add conviction accuracy tracking
- Add catalyst age correlation

**5.3 Enhanced Monthly Learning** (1 hour)
- Add news monitoring ROI calculation
- Add tier definition adjustment recommendations
- Add strategy evolution tracking

**5.4 Create New Output Files** (30 mins)
- `learning_data/tier_performance.json`
- `learning_data/vix_regime_performance.json`
- `learning_data/conviction_accuracy.json`

**Deliverables:**
- [ ] All three learning scripts enhanced
- [ ] New output files created
- [ ] Weekly/monthly reports include new sections

**Expected Impact:** Continuous improvement via data-driven optimization

---

### Implementation Timeline (Updated with Quick Fixes)

| Phase | Priority | Effort | Timeline |
|-------|----------|--------|----------|
| **Phase 1: News Monitoring** | CRITICAL | 5-6 hours | Week 1 |
| **Phase 2: Catalyst Tiers** | HIGH | 3 hours | Week 1-2 |
| **Phase 3: VIX (30) + Macro Calendar** | HIGH | 3.5 hours | Week 2 |
| **Phase 4: Conviction + Rel Strength** | HIGH | 3.5 hours | Week 2-3 |
| **Phase 5: Learning Enhancements** | ONGOING | 3.5 hours | Week 3 |
| **TOTAL** | - | **19 hours** | **3 weeks** |

**Key Changes from Original Plan:**
- VIX threshold changed to 30 (research validated)
- Macro event calendar added (FOMC/CPI/NFP blackouts)
- Relative strength filter (≥3%) added as required
- FDA/biotech inverted-J decay pattern added
- AI guardrails added (daily -2%, monthly -8% loss limits)
- Total effort increased from 16 → 19 hours (+3 hours for enhancements)

### Validation Plan

**After Each Phase:**
1. Unit test new functionality
2. Backtest on historical trades (if data available)
3. Run for 1 week in production
4. Review outcomes in weekly learning
5. Adjust parameters if needed

**After All Phases Complete:**
1. Run for 25 trades
2. Compare metrics to baseline (v5.0)
3. Calculate actual win rate improvement
4. Document learnings in strategy_rules.md
5. Decide on optional enhancements

---

## OPTIONAL FUTURE ENHANCEMENTS

### These are documented but NOT implemented (for now)

**1. Technical Filters (Skip)**
- Rationale: We're catalyst-driven, not technical-driven
- Could add: 50-day MA requirement, ADX >25, relative strength
- Estimated impact: +5-10% win rate
- Complexity: Medium (requires fetching technical indicators)

**2. Sector Rotation Module (Skip)**
- Rationale: Catalyst identification already filters for sector strength
- Could add: Automated sector ranking, concentration tracking
- Estimated impact: +3-5% win rate
- Complexity: High (requires sector ETF data, ranking logic)

**3. Kelly Criterion Position Sizing (Skip)**
- Rationale: Requires 100+ trades for accuracy, too aggressive
- Could add: Half-Kelly sizing based on historical win rate
- Estimated impact: +10-15% Sharpe ratio
- Complexity: Medium (requires win rate, win/loss ratio calculation)

**4. ATR Volatility-Based Sizing (Skip)**
- Rationale: Adds complexity without proven edge for 3-7 day swings
- Could add: Position size = (Account Risk / ATR × 2.5) × Price
- Estimated impact: +5-10% Sharpe ratio
- Complexity: Medium (requires 14-day ATR calculation)

**5. Drawdown Protocols (Skip)**
- Rationale: Sounds good but adds psychological complexity
- Could add: After 3 losses, reduce size 50%; after 5, pause system
- Estimated impact: +5-10% max drawdown reduction
- Complexity: Low (simple logic)

**6. VIX-Based Cash Allocation (Skip)**
- Rationale: We use VIX as entry filter instead (simpler)
- Could add: Dynamic cash % based on VIX level
- Estimated impact: +5% Sharpe ratio
- Complexity: Low (simple formula)

**7. Multi-Timeframe Analysis (Skip)**
- Rationale: 15-min delayed data limits precision
- Could add: 4-hour chart patterns, daily trend alignment
- Estimated impact: +3-5% win rate
- Complexity: High (requires chart analysis, pattern recognition)

**8. Social Sentiment Analysis (Skip)**
- Rationale: Twitter/Reddit often noise for catalyst trades
- Could add: Sentiment scoring from social media
- Estimated impact: Unclear, possibly negative
- Complexity: Very high (requires API, NLP, filtering)

**9. Options Flow Analysis (Skip)**
- Rationale: 80-90% of options are hedging, not directional
- Could add: Unusual options activity detection
- Estimated impact: +2-5% win rate
- Complexity: Very high (requires options data subscription)

**10. Earnings Whisper Numbers (Skip for now)**
- Rationale: May improve earnings catalyst quality assessment
- Could add: Compare earnings to whisper vs consensus
- Estimated impact: +3-5% win rate on earnings plays
- Complexity: Medium (requires whisper number source)

### When to Revisit Optional Enhancements

**After 100+ trades:**
- Have enough data to validate Kelly Criterion
- Can backtest ATR sizing effectiveness
- Can measure actual vs expected performance

**If specific problems emerge:**
- Win rate stuck <65%: Consider technical filters
- Large drawdowns: Consider drawdown protocols
- Earnings trades underperforming: Consider whisper numbers

**If market regime changes:**
- Prolonged high VIX: Consider VIX-based cash allocation
- Choppy sideways market: Consider multi-timeframe analysis

---

## APPENDIX

### Key Metrics Glossary

**Win Rate:** % of trades that close with positive return
**Average Return:** Mean % return across all trades
**Sharpe Ratio:** Risk-adjusted return (avg return / volatility)
**Max Drawdown:** Largest peak-to-trough decline in account value
**Risk/Reward Ratio:** Avg winner % / Avg loser %
**Catalyst Effectiveness:** Win rate for specific catalyst type
**Hold Time:** Days between entry and exit
**Position Size:** % of account allocated to single position
**Conviction Level:** Qualitative assessment (High/Medium/Low)
**VIX:** CBOE Volatility Index (market fear gauge)

### File Structure Reference

```
/paper_trading_lab/
├── agent_v5.0.py                          # Main trading system
├── learn_daily.py                         # Daily learning (5 PM)
├── learn_weekly.py                        # Weekly learning (Fri 5:30 PM)
├── learn_monthly.py                       # Monthly learning (Last Sun 6 PM)
│
├── /portfolio_data/
│   ├── current_portfolio.json            # 10 active positions
│   ├── account_status.json               # Account metrics
│   ├── pending_positions.json            # GO command decisions
│   └── daily_activity.json               # Today's closed trades
│
├── /trade_history/
│   └── completed_trades.csv              # All historical trades
│
├── /strategy_evolution/
│   ├── strategy_rules.md                 # Current rules (this document)
│   ├── lessons_learned.md                # Learning insights
│   ├── catalyst_exclusions.json          # Excluded catalysts
│   ├── catalyst_performance.csv          # Win rates by catalyst
│   └── tier_definitions.json             # NEW: Tier 1/2/3 criteria
│
├── /learning_data/                        # NEW DIRECTORY
│   ├── news_monitoring_log.csv           # News validation/invalidation log
│   ├── tier_performance.json             # Tier 1 vs Tier 2 stats
│   ├── vix_regime_performance.json       # Win rate by VIX level
│   └── conviction_accuracy.json          # Conviction vs outcomes
│
└── /daily_reviews/
    ├── go_[timestamp].json               # GO responses
    └── analyze_[timestamp].json          # ANALYZE responses
```

### API & Data Sources

**Polygon.io (Stocks Starter Tier - $29/month)**
- Stock prices (15-min delayed)
- News feed (updated hourly)
- Fundamentals (earnings, financials)
- 10 years historical data
- Unlimited API calls

**Claude API (Sonnet 4.5)**
- Model: claude-sonnet-4-5-20250929
- Used for: GO, EXECUTE, ANALYZE decision-making
- Cost: ~$0.01-0.05 per command (context-dependent)

**VIX Source**
- Polygon.io or Yahoo Finance (yfinance library)
- Updated real-time during market hours

### Contact & Support

**GitHub Repository:** [Link when public]
**Documentation:** This file (MASTER_STRATEGY_BLUEPRINT.md)
**Version:** 2.0 (Pareto-Optimized)
**Last Updated:** 2025-10-30

---

**END OF MASTER STRATEGY BLUEPRINT**

*This is the definitive guide for the Paper Trading Lab system. All implementation, learning, and strategy decisions should reference this document.*
