# Tedbot 2.0 Implementation Plan
**Prioritized by ROI, Simplicity, and Learning Systems**

## Philosophy: Big Wins Only

**Your Constraints:**
1. Focus on **massive impact** improvements only (10%+ win rate improvement potential)
2. Every feature needs **learning loops** (daily/weekly/monthly feedback)
3. Avoid over-complexity (no 5000 lines for 0.005% gains)
4. Not just about BA - building best-in-class system

**My Analysis:**
The research is excellent but contains 7 modules. We'll implement **3 high-impact modules** that together could improve from baseline ~55% to target 70%+ win rate, with full learning systems.

---

## ✅ PHASE 1: News-Based Catalyst Monitoring (IMPLEMENT)

### Why This Is a Big Win
- **Prevented Loss:** BA -4.4% would have been caught
- **Impact:** Prevents 30-50% of catalyst-invalidation losses
- **Research validates:** 95+ severity score for "$4.9B charge" news
- **Simple:** 300-400 lines of code max
- **Clear ROI:** Every prevented -7% stop loss = immediate value

### Implementation Scope
```python
class CatalystMonitor:
    def check_news_for_position(self, ticker, catalyst_type):
        """
        Fetch last 5 news items from Polygon
        Score using weighted keywords
        Return: (score 0-100, should_exit bool, top_headline)
        """

    # Keyword dictionary (60 terms, weighted)
    NEGATIVE_KEYWORDS = {
        'severe': ['charge', 'writedown', 'loss', 'investigation'],  # 40-50 pts each
        'catalyst_fail': ['miss', 'delay', 'downgrade', 'cut guidance'],  # 30-40 pts
        'concern': ['concern', 'risk', 'weak', 'disappointing']  # 15-25 pts
    }

    # Threshold: 85+ = auto-exit
```

### Learning System (CRITICAL)
**Daily:** Log every position + news score + whether exited
**Weekly:** Calculate:
- False positive rate (exited on news, stock went up anyway)
- False negative rate (didn't exit, should have)
- Avg loss prevented vs holding
- Keyword effectiveness (which terms predicted actual failures)

**Monthly:**
- Tune keyword weights based on accuracy
- Add new terms that appeared in failures
- Remove low-signal terms
- Adjust threshold (maybe 80 or 90 instead of 85)

**CSV Log Format:**
```
Date, Ticker, News_Score, Exited, Reason, Next_Day_Change, Prevented_Loss
2025-10-30, BA, 95, Yes, "$4.9B charge", -2.3%, +2.3%
```

**Success Metric:** Prevent 80%+ of catalyst failures within 24 hours

---

## ✅ PHASE 2: Entry Quality Scorecard (SIMPLIFIED VERSION)

### Why This Is a Big Win
- **Impact:** Transforms subjective decisions into repeatable edge
- **Research validates:** 80+ score = 70-75% win rate, 40-59 score = 50-60% win rate
- **Focus:** Catalyst quality (30pts) + Technical (25pts) = 55 points (enough signal)
- **Learning:** Track predicted score vs actual outcome

### Implementation Scope (SIMPLIFIED)
**We're implementing 2 of 5 components** (55 points total, not 100):

```python
class EntryQualityScorer:
    def score_opportunity(self, ticker, catalyst_data, price_data):
        """Returns score 0-55 and breakdown"""

        catalyst_score = self._score_catalyst(catalyst_data)  # 0-30
        technical_score = self._score_technical(price_data)   # 0-25

        return {
            'total': catalyst_score + technical_score,
            'catalyst': catalyst_score,
            'technical': technical_score,
            'rating': self._get_rating(total)  # High/Medium/Low
        }

    def _score_catalyst(self, data):
        # Earnings surprise: 0-12 pts (5% beat=3, 10%=6, 15%=9, 25%=12)
        # Revenue beat: 0-8 pts (both EPS+Rev = 8, single = 4)
        # Freshness: 0-5 pts (0-2 days=5, 3-5=3, 6-10=1, >10=0)
        # Multi-catalyst bonus: 0-5 pts
        pass

    def _score_technical(self, data):
        # Trend alignment: 0-7 pts (above 50MA=2, 5EMA>20EMA=2, ADX>25=1, etc)
        # Relative strength: 0-5 pts (vs sector)
        # Volume: 0-5 pts (2x avg=4, 3x=5)
        # Gap quality: 0-5 pts (2-5% gap on volume = 3 pts)
        # Risk/reward: 0-3 pts (3:1 = 2pts)
        pass
```

**Simplified Thresholds:**
- 45-55 pts = High Quality (full 10% position)
- 30-44 pts = Medium Quality (7% position)
- 15-29 pts = Low Quality (5% position or pass)
- <15 pts = Reject

### Learning System (CRITICAL)
**Daily:** Log every entry decision
```
Date, Ticker, Catalyst_Score, Tech_Score, Total, Position_Size, Entry_Price
2025-10-30, NVDA, 28, 22, 50, 10%, $207.04
```

**At Exit:** Add outcome
```
Exit_Date, Exit_Price, Hold_Days, Return, Hit_Target, Hit_Stop, Catalyst_Failed
2025-11-03, $223.50, 4, +7.9%, Yes, No, No
```

**Weekly Analysis:**
- Win rate by score bucket (45-55, 30-44, 15-29)
- Avg return by score bucket
- Which component (catalyst vs technical) predicted better?
- Calibration: If 45-55 bucket has <65% win rate, raise threshold to 48

**Monthly Tuning:**
- Adjust point allocations based on predictive power
- If relative strength doesn't matter, reduce its weight
- If freshness <2 days predicts 80% wins, increase its weight

**Success Metric:** 45-55 score entries achieve 65-70% win rate

---

## ✅ PHASE 3: Conviction-Based Position Sizing (IMPLEMENT)

### Why This Is a Big Win
- **Impact:** 2x more capital to winners, 0.5x to losers
- **Simple:** 50 lines of code
- **Research validates:** Half-Kelly + volatility adjust improves Sharpe 20-30%
- **Automatic:** Flows from Entry Quality Score

### Implementation Scope
```python
class PositionSizer:
    def calculate_size(self, entry_score, atr_data, market_vix):
        """
        Base: 10%
        Conviction adjust: (score / 55) multiplier
        Volatility adjust: Reduce if ATR elevated
        VIX adjust: Reduce if VIX > 25
        """

        base = 0.10  # 10%

        # Conviction (score 45-55 = ~0.9-1.0x, score 30 = ~0.55x)
        conviction_mult = entry_score / 55.0

        # Volatility (if ATR > 1.5x average, reduce to 0.7x)
        vol_mult = 0.7 if atr_ratio > 1.5 else 1.0

        # VIX (if 25-30 = 0.9x, if >30 = 0.7x)
        vix_mult = 1.0 if vix < 25 else (0.9 if vix < 30 else 0.7)

        final_size = base * conviction_mult * vol_mult * vix_mult
        return round(final_size, 3)  # e.g., 0.082 = 8.2%
```

**Example Calculations:**
- High conviction (score 50), normal vol, VIX 20: 10% × 0.91 × 1.0 × 1.0 = **9.1%**
- Medium conviction (score 35), high vol, VIX 28: 10% × 0.64 × 0.7 × 0.9 = **4.0%**
- Low conviction (score 20), normal vol, VIX 35: 10% × 0.36 × 1.0 × 0.7 = **2.5%**

### Learning System (CRITICAL)
**Track Every Position:**
```
Ticker, Entry_Score, Position_Size, Return, Optimal_Size_Retroactive
NVDA, 50, 9.1%, +12%, [10% would have been fine]
WEAK, 20, 2.5%, -6%, [good - limited damage]
```

**Weekly:**
- Compare actual returns by position size bucket
- Did 9-10% positions outperform 2-5% positions?
- Was volatility adjustment effective? (high ATR stocks = worse returns?)
- Was VIX adjustment effective? (VIX>30 entries = worse returns?)

**Monthly:**
- Calculate portfolio Sharpe ratio
- Compare to baseline fixed 10% sizing
- Tune multipliers if needed

**Success Metric:** Sharpe ratio improves 15-20% vs fixed sizing

---

## ❌ PHASE N: What We're NOT Implementing (And Why)

### Sector Rotation Module - SKIP
**Why skip:**
- Complexity: 200+ lines, 11 sector ETFs, daily tracking
- Marginal gain: Research shows 12.63% alpha but that's for pure sector rotation strategy
- We already filter by sector via news/catalyst
- **Diminishing returns:** Our edge is stock selection, not sector timing

**Compromise:** Simple rule instead:
- Max 3 positions per sector (already in strategy rules)
- Max 40% in any sector
- 2 lines of code in GO command check

### AI Decision Engine - SKIP FOR NOW
**Why skip:**
- We already use Claude for GO decisions
- Adding "structured 100-point scoring to Claude" = complexity without clear gain
- Claude already does implicit scoring

**Compromise:**
- Continue using Claude for decisions
- Add Entry Quality Score calculation AFTER Claude picks
- Use score for position sizing only
- Later: Can feed scores back to Claude as context

### Historical Pattern Matching Database - SKIP FOR NOW
**Why skip:**
- Requires 100+ trades to have meaningful data
- We have 1 trade currently (CAT)
- Premature optimization

**Compromise:**
- Let it build naturally in CSV
- After 50 trades, run analysis
- THEN build pattern matching if signals emerge

### Technical Indicators Beyond Basics - SKIP
**Why skip:**
- Research mentions ADX, RSI, OBV, VWAP, etc.
- Each adds complexity
- We're swing traders (3-7 days), not day traders

**Compromise:**
- Use only: Price vs 50MA, 5EMA vs 20EMA, volume vs 20-day avg
- That's enough signal for 3-7 day holds
- Can add ADX later if needed

---

## Implementation Timeline

### Week 1: News Monitoring
- **Days 1-2:** Build CatalystMonitor class (300 lines)
- **Day 3:** Add to ANALYZE command (check news at 4:30 PM)
- **Day 4:** Test with BA historical case + current portfolio
- **Day 5:** Deploy, start logging
- **Deliverable:** `news_monitor.py` + CSV logging

### Week 2: Entry Quality Scorecard (Simplified)
- **Days 1-2:** Build EntryQualityScorer class (catalyst + technical only)
- **Day 3:** Add to GO command (score each opportunity Claude suggests)
- **Day 4:** Test scoring on historical trades if data available
- **Day 5:** Deploy, start logging scores with outcomes
- **Deliverable:** `entry_scorer.py` + enhanced CSV logs

### Week 3: Conviction-Based Sizing
- **Day 1:** Build PositionSizer class (50 lines)
- **Day 2:** Integrate with Entry Quality Scores
- **Day 3:** Update EXECUTE command to use variable sizing
- **Day 4:** Backtest: "What if we'd sized CAT at 9% instead of 10%?"
- **Day 5:** Deploy, start using dynamic sizing
- **Deliverable:** `position_sizer.py` + sizing logs

### Week 4: Learning Systems
- **Day 1:** Build weekly analysis script (`analyze_weekly.py`)
- **Day 2:** Build monthly tuning script (`tune_monthly.py`)
- **Day 3:** Create dashboard visualizations for learning metrics
- **Day 4:** Document tuning procedures
- **Day 5:** First weekly review meeting
- **Deliverable:** Learning automation + reports

---

## Success Metrics (3-Month Goals)

**News Monitoring:**
- ✅ Detect 80%+ of catalyst failures within 24 hours
- ✅ False positive rate <20% (don't exit unnecessarily)
- ✅ Prevent average -3% loss per caught failure

**Entry Quality Scoring:**
- ✅ Scores 45-55: Win rate 65-70%
- ✅ Scores 30-44: Win rate 55-65%
- ✅ Scores <30: Win rate <50% (validates we should skip these)
- ✅ Correlation >0.6 between score and actual return

**Position Sizing:**
- ✅ Sharpe ratio improves 15-20% vs fixed sizing
- ✅ High-conviction positions (9-10%) outperform low-conviction (2-5%)
- ✅ Drawdowns reduced during high VIX periods

**Overall System:**
- ✅ Win rate: 55% baseline → 65-70% target
- ✅ Avg winner: +12-15% (same or better)
- ✅ Avg loser: -5% (better than -7% baseline due to news exits)
- ✅ Sharpe ratio: >1.5

---

## Why This Plan Works

**1. Focused on 3 Big Wins**
- News monitoring: Prevents catastrophic losses (BA-type)
- Entry scoring: Improves decision quality systematically
- Dynamic sizing: 2x allocation to best ideas, 0.5x to marginal

**2. Every Feature Has Learning**
- News: Weekly false positive/negative analysis → keyword tuning
- Scoring: Calibration by score bucket → point reallocation
- Sizing: Sharpe tracking → multiplier adjustment

**3. Builds On What Exists**
- GO/EXECUTE/ANALYZE structure stays the same
- Claude still makes decisions
- We add scoring + monitoring layers
- Incremental, not revolutionary

**4. Avoids Over-Complexity**
- Total new code: ~800 lines across 3 modules
- No AI training required (rule-based + Claude API)
- No new data subscriptions needed (Polygon has everything)
- Simple enough to understand and debug

**5. Research-Backed**
- News monitoring: Validated by Loughran-McDonald, gap-fill studies
- Entry scoring: PEAD research, momentum studies, 40+ years academia
- Dynamic sizing: Kelly criterion, Moreira & Muir volatility management

---

## Next Steps

1. **Review & Approve** this simplified plan
2. **Week 1 Start:** Begin news monitoring implementation
3. **Daily standups:** 15-min review of progress/blockers
4. **Weekly demos:** Show working features, get feedback
5. **Month 1 retrospective:** Adjust based on early results

**Question for you:** Does this focus on 3 modules (news, scoring, sizing) with full learning systems align with your vision? Or would you prefer different prioritization?
