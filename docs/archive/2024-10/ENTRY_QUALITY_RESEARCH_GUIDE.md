# Entry Quality Research Guide
**For Deep Research in Claude Pro**

## Purpose
This guide outlines key research areas for improving entry quality in the Tedbot 2.0 swing trading system. Our current edge is AI-driven catalyst identification. The goal is to systematically improve **which** stocks we enter and **when** we enter them.

## Current State (Baseline)
- **Strategy:** Swing trading (3-7 day holds)
- **Position sizing:** 10% per position, max 10 positions
- **Exit rules:** -7% stop, +10-15% target (full exits)
- **Entry method:** Tier 1 catalyst identification via AI
- **Price checks:** 2x daily (9:30 AM execute, 4:30 PM analyze)
- **Data:** Polygon.io Stocks Starter tier ($29/month)
  - Unlimited API calls
  - 15-min delayed prices
  - News endpoint (updated hourly)
  - 5 years historical data

## Key Constraint
Our advantage is NOT in execution speed or intraday timing. Our advantage is in **pattern recognition across catalysts and learning from historical trades**.

---

## 🔥 PRIORITY RESEARCH AREA: News-Based Catalyst Monitoring

**Status:** Available NOW (already have paid Polygon.io tier)
**Urgency:** HIGH - BA trade lost -4.4% due to undetected catalyst failure
**Implementation Effort:** Moderate (2-3 hours)
**Potential Impact:** Prevent 30-50% of catalyst-invalidation losses

### The BA Case Study (2025-10-30)

**What Happened:**
- Entered BA position (likely on bullish catalyst)
- Boeing reported Q3 earnings with **$4.9B charge on 777X delays**
- News broke 24 hours ago (Oct 29, ~2:00 PM)
- System held through negative catalyst event
- Current loss: -4.4% (approaching -7% stop loss)

**What SHOULD Have Happened (Per Strategy Rules):**
```
Strategy Rule: "Catalyst Invalidated - Exit same day regardless of P&L"
- 777X delays = Binary event catalyst invalidated
- Major earnings miss = Earnings catalyst invalidated
- Should have exited at 4:30 PM ANALYZE on Oct 29
```

**What Actually Happened:**
- ANALYZE command checked stops/targets only (mechanical rules)
- Did NOT check news or catalyst status
- Will not detect catalyst failure until next GO command (Oct 31, 8:45 AM)
- Loss compounds from -4.4% → potentially worse

**Cost of Delay:**
- If exited Oct 29 at 4:30 PM: ~-3% loss
- If exit Oct 31 at 9:30 AM: Potentially -5% to -8% loss
- Difference: 2-5% additional loss = $2-5 on $100 position

### Polygon.io News Endpoint

**Available on Stocks Starter Tier:** ✅ Yes
**Endpoint:** `GET /v2/reference/news`
**Rate Limit:** Unlimited (paid tier)
**Update Frequency:** Hourly
**Data Included:**
- Headlines, descriptions, full article URLs
- Publication timestamps
- Associated tickers
- Publisher information
- Sentiment insights (optional)

**Example API Call:**
```bash
GET https://api.polygon.io/v2/reference/news?ticker=BA&limit=10&apiKey=YOUR_KEY
```

**Example Response:**
```json
{
  "results": [
    {
      "title": "Boeing takes $4.9B charge on 777X delays",
      "description": "Company reports Q3 loss due to program issues...",
      "published_utc": "2025-10-29T14:30:00Z",
      "article_url": "https://...",
      "tickers": ["BA"],
      "keywords": ["earnings", "loss", "delay", "charge"]
    }
  ]
}
```

### Research Questions

#### 1. Catalyst Invalidation Detection

**Primary Question:** How do we programmatically detect when a catalyst has been invalidated?

**Sub-Questions:**
- **Keyword-Based Detection:**
  - What keywords indicate catalyst failure?
  - Negative: "miss", "loss", "charge", "delay", "downgrade", "cut guidance", "suspend", "investigation"
  - Positive (ignore): "beat", "upgrade", "raise guidance", "accelerate", "approval"
  - Context matters: "beat expectations despite loss" vs "miss on earnings"

- **Catalyst-Specific Rules:**
  - Earnings catalyst: "earnings miss", "revenue miss", "guidance lowered"
  - Analyst upgrade catalyst: "downgrade", "lower price target"
  - Binary event catalyst: "delay", "rejection", "suspend", "cancel"
  - Sector momentum: Check if multiple stocks in sector turning negative

- **Magnitude/Severity:**
  - Small negative news: "slight miss" → Monitor, don't exit
  - Major negative news: "$4.9B charge" → Exit immediately
  - How to quantify severity? Dollar amounts? Analyst reactions?

#### 2. Confidence Thresholds

**Primary Question:** When should we auto-exit vs just flag for manual review?

**Scenarios:**
- **High Confidence Exit (auto-execute):**
  - Multiple negative keywords in headline
  - Large dollar loss mentioned ($1B+)
  - Explicit downgrade from analyst
  - Regulatory rejection/delay

- **Medium Confidence (flag for review):**
  - Mixed news (good revenue, bad guidance)
  - Single negative keyword
  - Unconfirmed reports

- **Low Confidence (monitor only):**
  - Opinion pieces without new data
  - Analyst commentary (not rating change)
  - Industry news (not company-specific)

**Implementation Options:**
1. **Conservative:** Only exit on explicit, unambiguous catalyst failures
2. **Aggressive:** Exit on any significant negative news
3. **Hybrid:** Use keyword scoring system (3+ negative keywords = exit)

#### 3. Timing & Frequency

**Primary Question:** When should we check news?

**Options:**
- **Current: 4:30 PM only** (1x per day during ANALYZE)
  - Pros: Simple, catches end-of-day news
  - Cons: Misses morning news until next ANALYZE

- **Enhanced: 4:30 PM + morning check** (2x per day)
  - 8:45 AM during GO: Check overnight news
  - 4:30 PM during ANALYZE: Check intraday news
  - Catches 99% of relevant news

- **Aggressive: Hourly checks** (10 AM, 12 PM, 2 PM, 4 PM)
  - Pros: Fastest response to breaking news
  - Cons: More complexity, may overreact

**Recommendation:** Start with 4:30 PM only, evaluate if morning check needed

#### 4. False Positives vs False Negatives

**Trade-offs:**

**False Positive (exit when shouldn't):**
- Exit on negative-sounding news that doesn't actually invalidate thesis
- Example: "Company faces challenges" → Vague, not actionable
- Cost: Exit good position prematurely, miss potential gains

**False Negative (hold when should exit):**
- Miss catalyst invalidation, hold losing position
- Example: BA 777X news → Clear catalyst failure, didn't exit
- Cost: Larger losses as position deteriorates

**Risk Assessment:**
- In swing trading with -7% stops, false negatives are MORE dangerous
- Better to exit early (false positive) than hold through catalyst failure
- Can always re-enter if news was overblown

**Recommendation:** Err on side of false positives (exit on suspicious news)

#### 5. Integration with AI Decision-Making

**Primary Question:** Should news checking be automated or AI-assisted?

**Option A: Fully Automated (Rule-Based)**
```python
def check_catalyst_invalidation(ticker, news_items):
    negative_keywords = ["miss", "loss", "charge", "delay", "downgrade", "cut"]
    score = sum(1 for item in news_items for keyword in negative_keywords if keyword in item['title'].lower())
    return score >= 3  # Exit if 3+ negative signals
```
- Pros: Fast, consistent, no API costs
- Cons: Misses nuance, may trigger false positives

**Option B: AI-Assisted (Claude Reviews)**
```python
# Fetch news, send to Claude with prompt:
"Review this news for {ticker}. Does it invalidate our {catalyst} thesis? Recommend EXIT or HOLD."
```
- Pros: Understands context, nuance, thesis-specific
- Cons: Slower, costs $0.01-0.05 per review, needs API call

**Option C: Hybrid (Rules + AI Confirmation)**
```python
# Step 1: Rule-based filter (score >= 2)
# Step 2: If triggered, ask Claude to confirm
# Step 3: Execute Claude's recommendation
```
- Pros: Balance of speed and accuracy
- Cons: More complex implementation

**Recommendation:** Start with Option A (rules), upgrade to Option C after testing

#### 6. Entry Quality Enhancement

**Primary Question:** Can news also IMPROVE entry quality?

**Use Cases:**

**During GO Command (8:45 AM):**
- Verify catalyst is recent (<3 days old via news timestamps)
- Check if positive news is accelerating (multiple articles)
- Detect if "stale" catalyst is re-confirmed by new news
- Avoid entries on old catalysts with no recent confirmation

**Example:**
```
Claude suggests: "Buy NVDA on earnings beat catalyst"
News check shows:
- Earnings report: 3 days ago
- Follow-up articles: 1 day ago still bullish ("momentum continuing")
- Analyst upgrades: Multiple today
→ CONFIRMED: Fresh, accelerating catalyst ✅

vs

Claude suggests: "Buy STOCK on earnings beat catalyst"
News check shows:
- Earnings report: 7 days ago
- No recent follow-up coverage
- Sector turning negative (recent articles about sector headwinds)
→ REJECTED: Stale catalyst, momentum fading ❌
```

**Actionable Rules:**
1. Require catalyst confirmation via news within last 3 days
2. Check for "momentum continuing" signals (analyst upgrades, follow-up coverage)
3. Scan for contradicting sector/macro news

### Actionable Output

After research, deliver:

1. **Keyword Dictionary** for catalyst invalidation detection
   ```python
   CATALYST_INVALIDATION_KEYWORDS = {
       'earnings': ['miss', 'below', 'disappointing', 'cut guidance', 'lowered'],
       'analyst': ['downgrade', 'lower target', 'cut rating', 'reduce'],
       'binary_event': ['delay', 'reject', 'suspend', 'cancel', 'postpone'],
       'sector': ['selloff', 'downturn', 'weakness', 'concerns'],
       'severe': ['charge', 'loss', 'writedown', 'impairment', 'investigation']
   }
   ```

2. **Scoring Framework** for exit decisions
   ```
   Severity Score (0-10):
   - 0-2: Minor news, monitor only
   - 3-5: Significant news, flag for review
   - 6-8: Major news, consider exit
   - 9-10: Critical news, auto-exit

   Calculated from:
   - Number of negative keywords
   - Dollar amounts mentioned
   - Source credibility (Bloomberg > random blog)
   - Recency (breaking news > 24hrs old)
   ```

3. **Implementation Spec** for ANALYZE command enhancement
   ```python
   def analyze_with_news():
       for position in portfolio:
           # Existing: Check stops/targets
           should_exit_mechanical = check_stops_targets(position)

           # NEW: Check news for catalyst failure
           news = fetch_polygon_news(position.ticker, limit=5)
           should_exit_catalyst = check_catalyst_invalidation(news, position.catalyst_type)

           if should_exit_mechanical or should_exit_catalyst:
               exit_position(position)
   ```

4. **Testing Plan** with BA case study
   - Backtest: Would news check have caught BA on Oct 29?
   - Simulate: Run news check on current portfolio daily for 1 week
   - Measure: False positive rate, false negative rate
   - Tune: Adjust keyword weights based on results

5. **Monitoring Dashboard** (optional)
   - Show recent news headlines for each position
   - Display catalyst invalidation score
   - Flag positions with suspicious news

### Implementation Priority

**Phase 1 (Immediate):** News monitoring in ANALYZE
- Add Polygon news API fetch
- Simple keyword-based detection
- Auto-exit on high-confidence invalidations
- **Estimated time:** 2-3 hours
- **Impact:** Prevent 30-50% of catalyst-invalidation losses

**Phase 2 (After testing):** Entry quality enhancement
- Add news verification to GO command
- Confirm catalyst freshness
- Detect momentum acceleration/deceleration
- **Estimated time:** 1-2 hours
- **Impact:** Improve entry win rate by 5-10%

**Phase 3 (Future):** AI-assisted review
- Claude reviews ambiguous news
- Context-aware catalyst validation
- Sector correlation analysis
- **Estimated time:** 3-4 hours
- **Impact:** Reduce false positives, improve precision

### Success Metrics

We'll know news monitoring is working when:
- **Catalyst failures detected:** Catch 80%+ of invalidated catalysts within 24 hours
- **Loss reduction:** Average loss on catalyst failures decreases from -6% to -3%
- **False positive rate:** <20% (exit on news, position continues up)
- **Avoided losses:** Save $5-10 per month in prevented drawdowns

The goal: **Never hold through another BA-style catalyst failure.**

---

## Research Area 1: Catalyst Tier System Refinement

### Current Implementation
- Tier 1 catalysts: Earnings beats, sector momentum, technical breakouts, analyst upgrades, binary events
- Simple include/exclude based on historical win rates
- File: `strategy_evolution/catalyst_exclusions.json`

### Research Questions
1. **Catalyst Effectiveness by Market Regime**
   - Do earnings beats perform differently in bull vs bear markets?
   - Should sector momentum be weighted higher during rotation periods?
   - How do binary events (FDA approvals, contract wins) perform across different volatility environments?

2. **Catalyst Age/Freshness**
   - What is optimal entry timing after catalyst announcement?
   - Day 0 (same day)? Day 1? Day 2-3 (after initial spike)?
   - Does "post-earnings drift" exist in our backtested trades?
   - Should we avoid "stale" catalysts (>5 days old)?

3. **Catalyst Strength Scoring**
   - Can we quantify catalyst quality? (e.g., earnings beat by 5% vs 50%)
   - Should analyst upgrades from Goldman carry more weight than smaller firms?
   - How do we measure sector momentum strength? (RSI? Volume? Multiple stocks moving?)

4. **Multi-Catalyst Synergy**
   - Are stocks with 2+ simultaneous catalysts higher probability? (e.g., earnings beat + sector momentum)
   - Should we prioritize these over single-catalyst plays?

### Actionable Output
- Refined catalyst tier definitions (Tier 1, Tier 2, Avoid)
- Optimal entry timing windows by catalyst type
- Catalyst strength scoring rubric for AI to use

---

## Research Area 2: Sector & Market Context

### Current Implementation
- Basic sector tracking in position data
- Max 30% concentration per sector (not enforced in code)
- No market regime awareness

### Research Questions
1. **Sector Rotation Detection**
   - Can we identify sector rotation cycles programmatically?
   - Which sectors lead in early bull markets? Late bull markets?
   - Should we avoid defensive sectors during risk-on periods?

2. **Market Regime Classification**
   - Bull market (trending up): Favor momentum, growth
   - Bear market (trending down): Favor value, quality
   - Choppy/ranging: Favor mean reversion, catalysts with clear thesis
   - How do we detect regime changes? (VIX? SPY trend? Breadth indicators?)

3. **Correlation & Diversification**
   - Are we accidentally holding 5 tech stocks that all move together?
   - Should we measure portfolio beta and aim for lower correlation?
   - Can we use sector ETF correlations to avoid redundant positions?

4. **Macro Events**
   - FOMC meetings, CPI prints, earnings season timing
   - Should we avoid entries 1 day before major macro events?
   - Should we increase cash during high-uncertainty periods?

### Actionable Output
- Sector rotation framework for AI to reference
- Market regime detection rules (simple heuristics)
- Diversification scoring to avoid correlated bets

---

## Research Area 3: Technical Entry Timing

### Current Implementation
- Entry at 9:30 AM market open (GO → EXECUTE workflow)
- Uses 15-min delayed premarket prices for gap analysis
- No technical indicator analysis

### Research Questions
1. **Gap Analysis Optimization**
   - Premarket gap up >3%: Chase or wait for pullback?
   - Premarket gap down on good catalyst: Opportunity or red flag?
   - Does gap size correlate with eventual 3-7 day returns?

2. **Price Action Patterns**
   - Should we wait for confirmation? (e.g., higher high, higher low)
   - Are breakouts above resistance more reliable than "buy the dip"?
   - Do volume spikes on catalyst day predict follow-through?

3. **Support/Resistance Levels**
   - Should we prefer entries near support (lower risk) vs chasing breakouts?
   - Can we use 20/50/200 day moving averages as simple filters?
   - Do entries above all major MAs have higher win rates?

4. **Relative Strength**
   - Should we compare stock performance to sector ETF?
   - If stock is up 5% but sector is up 8%, is that relative weakness?
   - Should we prioritize stocks outperforming their sector?

### Important Note
We check prices 2x/day, so complex intraday patterns are NOT useful. Focus on **simple heuristics** that can be evaluated at 8:45 AM premarket review.

### Actionable Output
- Gap trading rules (when to enter vs wait)
- Simple technical filters (above/below key MAs)
- Relative strength vs sector benchmark

---

## Research Area 4: Position Sizing & Conviction

### Current Implementation
- Fixed 10% position size for all entries
- No differentiation by conviction level

### Research Questions
1. **Conviction-Based Sizing**
   - Should high-conviction setups (multiple catalysts, strong technicals) be 12-15%?
   - Should low-conviction opportunistic plays be 5-7%?
   - How do we quantify conviction programmatically?

2. **Risk-Based Sizing**
   - Should volatile stocks (high beta) get smaller positions?
   - Should we size based on distance to stop loss? (wider stop = smaller size)
   - Can we use ATR (Average True Range) for position sizing?

3. **Account Drawdown Management**
   - After losing streak, should we reduce position sizes temporarily?
   - After winning streak, should we increase sizes or stay disciplined?
   - Should we scale back to 8 positions (vs 10) during high volatility?

4. **Partial Portfolio vs Fully Invested**
   - Is there value in holding 20-30% cash during uncertain periods?
   - Or does staying fully invested maximize compound returns?
   - Can we backtest "selective patience" vs "always in the market"?

### Actionable Output
- Conviction scoring framework (High/Medium/Low)
- Position sizing rules based on conviction + volatility
- Cash allocation strategy for different market regimes

---

## Research Area 5: Learning from Historical Trades

### Current Implementation
- CSV log of all completed trades: `trade_history/completed_trades.csv`
- Manual monthly learning via `learn_monthly.py`
- Catalyst exclusions based on win rate: `catalyst_exclusions.json`

### Research Questions
1. **Win Rate Analysis by Attribute**
   - Which catalysts have highest win rate? Highest avg return?
   - Which sectors consistently outperform?
   - Does hold time (3 days vs 7 days) correlate with better returns?

2. **Loss Analysis**
   - What do our losers have in common?
   - Entered too early? Too late? Wrong catalyst type?
   - Did we ignore technical warnings (e.g., broken support)?

3. **Winner Analysis**
   - What do our big winners (>15% gain) have in common?
   - Multiple catalysts? Strong sector momentum? Specific entry timing?
   - Can we create a "blueprint" for high-probability setups?

4. **Time-Based Patterns**
   - Do certain days of week have better entry success? (Monday vs Friday)
   - Does earnings season (concentrated catalyst flow) improve or hurt returns?
   - Seasonal patterns? (November-January vs May-August)

5. **Gap Performance**
   - Do gap-up entries (+3% premarket) outperform flat opens?
   - Do gap-downs on good news create better risk/reward?
   - Should we avoid large gaps (>5%) entirely?

### Actionable Output
- "High Probability Setup" checklist derived from winners
- "Avoid These Patterns" checklist derived from losers
- Updated catalyst exclusions with specific reasoning

---

## Research Area 6: AI Prompt Engineering for Entry Selection

### Current Implementation
- Claude API called at 8:45 AM with portfolio review + context
- Receives premarket data, strategy rules, exclusions
- Returns HOLD/EXIT/BUY decisions in JSON format

### Research Questions
1. **Context Optimization**
   - What information does Claude need to make better entry decisions?
   - Should we provide SPY trend, VIX level, sector ETF performance?
   - Should we show "recent misses" (stocks we didn't enter that ran)?

2. **Decision Framework**
   - Should we ask Claude to score each opportunity 1-10?
   - Should we force Claude to rank opportunities (best to worst)?
   - Should we limit BUY decisions to top 3 opportunities even if 5 exist?

3. **Reasoning Transparency**
   - Should we require Claude to explain WHY it chose each entry?
   - Can we use that reasoning to build a scoring rubric over time?
   - Should Claude provide confidence levels (High/Medium/Low)?

4. **Backtesting Prompts**
   - Can we simulate past GO decisions with historical data?
   - Can we test different prompt variations and measure win rate impact?
   - Should we A/B test conservative vs aggressive prompts?

### Actionable Output
- Optimized prompt template with essential context
- Structured output format (scores, rankings, reasoning)
- Prompt testing methodology for continuous improvement

---

## Research Area 7: Data & Information Sources

### Current Implementation
- Polygon.io: 15-min delayed prices (free tier)
- No news feeds or sentiment analysis
- No earnings surprise data or analyst rating changes

### Research Questions
1. **Price Data Enhancement**
   - Is 15-min delay sufficient for 3-7 day swing trades? (Yes, likely)
   - Should we upgrade to real-time for better premarket gap analysis?
   - Do we need historical IV (implied volatility) for options-active stocks?

2. **Fundamental Data**
   - Earnings surprise %: Beat by 5% vs 50% - does magnitude matter?
   - Revenue vs EPS beats: Which is more predictive of price continuation?
   - Guidance changes: Can we detect raised/lowered guidance programmatically?

3. **News & Sentiment**
   - Can we scrape headlines for catalyst confirmation?
   - Is social media sentiment (Twitter/Reddit) useful or noise?
   - Do analyst notes (from Bloomberg/Reuters) improve entry quality?

4. **Alternative Data**
   - Unusual options activity: Large call buying = bullish signal?
   - Insider buying/selling: Does it correlate with our catalyst trades?
   - Short interest: High short interest + catalyst = short squeeze potential?

### Actionable Output
- List of high-value data sources worth paying for
- List of low-value data sources to ignore (avoid noise)
- API integration priorities (what to build next)

---

## Research Area 8: Psychological & Behavioral Factors

### Current Implementation
- Fully automated execution (no human discretion)
- Rules-based system (reduces emotion)

### Research Questions
1. **Overtrading Prevention**
   - Are we entering positions just because we have cash available?
   - Should we enforce "minimum catalyst quality" threshold?
   - Is there value in saying "no good setups today, stay patient"?

2. **Recency Bias**
   - After a big winner, do we chase similar setups (overconfidence)?
   - After a big loser, do we avoid good setups (fear)?
   - How do we stay disciplined and rules-based?

3. **Anchoring**
   - Do we avoid re-entering stocks we previously lost on?
   - Should we track "stocks we said no to" and learn from misses?

4. **Confirmation Bias**
   - Does Claude find reasons to justify trades we want to make?
   - Should we add a "devil's advocate" step to challenge each entry?

### Actionable Output
- Behavioral checklist for AI to follow
- Rules to prevent emotional/biased entries
- "Pause and review" triggers (e.g., after 3 losses in a row)

---

## Synthesis: Building the Entry Quality Framework

### Final Deliverable (After Research)
A comprehensive **Entry Quality Scorecard** that Claude uses to evaluate every potential entry:

```
Entry Quality Score (0-100):
├── Catalyst Quality (0-30 points)
│   ├── Tier 1 catalyst confirmed (+15)
│   ├── Fresh catalyst (<3 days) (+5)
│   ├── Catalyst strength high (+5)
│   └── Multiple catalysts present (+5)
│
├── Technical Setup (0-25 points)
│   ├── Above key moving averages (+10)
│   ├── Healthy gap/entry price (+5)
│   ├── Relative strength vs sector (+5)
│   └── Support level nearby (low risk) (+5)
│
├── Sector/Market Context (0-20 points)
│   ├── Favorable market regime (+10)
│   ├── Sector in rotation/leadership (+5)
│   └── Low correlation with existing holdings (+5)
│
├── Historical Pattern Match (0-15 points)
│   ├── Similar past trades were winners (+10)
│   └── No red flags from loss analysis (+5)
│
└── Conviction/Risk (0-10 points)
    ├── High conviction setup (+5)
    └── Risk/reward favorable (+5)

Score 80-100: High Priority Entry (12-15% position size)
Score 60-79:  Standard Entry (10% position size)
Score 40-59:  Low Conviction Entry (5-7% position size)
Score 0-39:   Pass (do not enter)
```

---

## Methodology for Claude Pro Research

### Recommended Approach
1. **Start with Research Area 5 (Historical Trades)**
   - Analyze existing trade data first
   - Let real results guide which areas to prioritize

2. **Tackle Areas 1-3 in Parallel**
   - Catalyst system, sector context, technical timing
   - These are interconnected and inform each other

3. **Address Areas 4, 6-8 After Core Framework**
   - Position sizing, prompts, data sources, psychology
   - These optimize the foundation built in Areas 1-3

4. **Synthesize into Scorecard**
   - Create weighted scoring system
   - Backtest scorecard against historical trades
   - Iterate until 70%+ win rate is achieved

### Expected Outcome
- Clear, quantifiable entry rules
- Scoring framework implementable in code
- Improved from "AI intuition" to "AI + systematic rules"
- Target: 65-75% win rate (vs current baseline)

---

## Implementation Notes

After research is complete, implementation will involve:
1. Updating `strategy_evolution/strategy_rules.md` with new entry framework
2. Enhancing `agent_v5.0.py` GO command prompts with scoring context
3. Adding data fetches for any new required inputs (sector ETFs, technical indicators)
4. Building entry quality scoring module (new Python module)
5. Backtesting framework to validate improvements

---

## Success Metrics

We will know entry quality has improved when:
- **Win rate increases:** From baseline to 70%+
- **Average winner increases:** Larger gains on winning trades
- **Average loser decreases:** Smaller losses on losing trades
- **Sharpe ratio improves:** Better risk-adjusted returns
- **Drawdown reduces:** Fewer consecutive losses

The goal is **not** more trades. The goal is **better** trades.

---

**Document Version:** 1.0
**Date:** 2025-10-30
**Author:** Tedbot 2.0 Research Initiative
**Next Step:** Deep research in Claude Pro, then implementation planning
