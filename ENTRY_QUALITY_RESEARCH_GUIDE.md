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
- **Data:** Polygon.io 15-min delayed quotes (free tier)

## Key Constraint
Our advantage is NOT in execution speed or intraday timing. Our advantage is in **pattern recognition across catalysts and learning from historical trades**.

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
