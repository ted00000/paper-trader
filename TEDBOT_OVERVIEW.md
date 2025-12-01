# Tedbot Trading System - Complete Overview

## What is Tedbot?

Tedbot is an AI-powered catalyst-driven swing trading system that uses Claude (Anthropic's AI) to identify, analyze, and trade stocks experiencing significant catalysts. The system operates autonomously with a $1,000 paper trading account, making data-driven decisions based on news events, technical analysis, and market conditions.

**Performance Target**: 90-92% of best-in-class professional trader performance
**Strategy**: Event-driven momentum trading (3-7 day holds, occasionally 30-60 days for post-earnings drift)
**Approach**: High-conviction, concentrated positions (10 max) with strict risk management

---

## The Complete Trading Workflow

### Phase 1: Stock Identification (Market Screener)

**Tool**: `market_screener.py`
**Schedule**: Runs continuously, scanning 3,000+ stocks multiple times per day
**Data Sources**: Polygon.io (price data), Finnhub (news)

#### What the Screener Looks For:

1. **Catalyst Detection** (Tier 1-3 priority)
   - **Tier 1** (Highest Priority):
     - M&A announcements
     - FDA approvals
     - Major contract wins
     - Earnings beats (>15% surprise)
     - Analyst upgrades (from top-tier firms)

   - **Tier 2** (Medium Priority):
     - Product launches
     - Partnership announcements
     - Earnings beats (10-15% surprise)
     - Analyst upgrades (mid-tier firms)

   - **Tier 3** (Lower Priority):
     - Insider buying (cluster of 3+ executives)
     - Share buyback announcements

2. **Technical Filters** (All Must Pass)
   - **Price above 50-day SMA**: Confirms uptrend
   - **5 EMA > 20 EMA**: Bullish momentum crossover
   - **ADX > 20**: Strong trend (not choppy)
   - **Volume > 1.5x average**: Institutional participation

3. **Volume Analysis** (Enhancement 2.2)
   - **EXCELLENT** (3x+ average): Institutional surge
   - **STRONG** (2x+ average): High conviction
   - **GOOD** (1.5x+ average): Acceptable minimum
   - **Volume trending up**: Recent 5-day avg > prior 20-day by 20%+

4. **Relative Strength Analysis** (Phase 3.1 - IBD-Style)
   - **3-Month Performance**: Stock vs sector ETF
   - **RS Percentile Rank** (0-100, market-wide comparison):
     - 95+: Elite (top 5% of all stocks)
     - 90-94: Excellent (top 10%)
     - 80-89: Strong (top 20%)
     - 70-79: Above Average
     - <70: Filter out (only trade market leaders)
   - **Traditional RS %**: Stock outperformance vs sector
     - 95: Elite (RS ≥15%)
     - 85: Strong (RS 10-15%)
     - 75: Very Good (RS 7-10%)
     - 65: Good (RS 5-7%)
     - 55: Acceptable (RS 3-5%)

5. **Stage 2 Alignment** (Minervini Criteria)
   - Stock above 150-day and 200-day MAs
   - 150-day MA > 200-day MA
   - 200-day MA trending up
   - Stock within 25% of 52-week high
   - 50-day MA > 150-day and 200-day MAs

6. **Sector Rotation Detection** (Phase 3.2)
   - Tracks 11 sector ETFs vs SPY benchmark
   - **Leading Sectors**: >2% outperformance vs SPY (3-month)
   - **Lagging Sectors**: <-2% underperformance vs SPY
   - Prioritizes stocks from leading sectors in GO command

7. **Institutional Activity Signals** (Phase 3.3)
   - **Options Flow**: Unusual call buying (call/put ratio >2.0)
   - **Dark Pool Activity**: Volume spikes >1.5x average (institutional accumulation)
   - Adds conviction when institutions are buying

8. **Liquidity Filter** (Phase 4.4)
   - **Minimum $20M average daily dollar volume**
   - Prevents execution slippage on low-liquidity stocks
   - Filters at screener level before GO command sees candidates
   - Typical slippage on sub-$20M names: 1-3% per trade

**Output**: List of catalyst-driven candidates saved to `screener_candidates.json` with enhanced metadata

---

### Phase 2: Morning Analysis (GO Command)

**Tool**: `agent_v5.5.py go`
**Schedule**: 9:00 AM ET daily (15 minutes before market open)
**Purpose**: Claude reviews screener candidates and selects best opportunities

#### Claude's Analysis Process:

1. **News Validation** (0-20 points)
   - Analyzes 3-5 most recent news articles
   - Scores catalyst strength, credibility, recency
   - Validates the story isn't already "played out"
   - Checks for negative sentiment or red flags

2. **VIX/Market Regime Check**
   - **VIX < 20**: GREEN (normal trading)
   - **VIX 20-25**: YELLOW (caution, reduce position sizing)
   - **VIX 25-30**: ORANGE (elevated risk, Tier 1 only)
   - **VIX > 30**: RED (SHUTDOWN - no new trades)

3. **Macro Event Check**
   - Scans for Fed meetings, CPI reports, FOMC within 48 hours
   - Adjusts position sizing or skips trades during high-impact events

4. **Market Breadth & Trend Filter** (Phase 4.2)
   - **SPY Trend Check**: Price above 50-day and 200-day MAs
   - **Market Breadth**: % of stocks above 50-day MA (from screener data)
   - **Three Regimes**:
     - **HEALTHY** (SPY uptrend + breadth ≥50%): 100% position sizing
     - **DEGRADED** (SPY above 50d + breadth ≥40%): 80% position sizing
     - **UNHEALTHY** (otherwise): 60% position sizing
   - Prevents trading during rotational/choppy markets
   - Applied as multiplier to base conviction sizing

5. **Conviction Scoring** (Phase 4.1 - Cluster-Based)
   - **Prevents double-counting correlated signals via clustering**
   - **Momentum Cluster** (cap +3):
     - RS ≥90th percentile: +2 factors (DOUBLE WEIGHT)
     - RS 80-89th percentile: +1 factor
     - RS >7% sector outperformance: +1 factor
     - Leading sector (+2% vs SPY): +1 factor
   - **Institutional Cluster** (cap +2):
     - Unusual options flow: +1 factor
     - Dark pool accumulation: +1 factor
   - **Catalyst Cluster** (no cap - independent signals):
     - Tier 1 catalyst: +1 factor
     - Multi-catalyst: +1 factor
     - Revenue beat (EPS + Revenue): +1 factor
     - News score >15/20: +1 factor
   - **Market Conditions Cluster** (cap +2):
     - VIX <20: +1 factor
   - **Maximum possible score**: 11 factors (down from 14+ in Phase 3)

   - **Conviction Levels** (base sizing, before market breadth adjustment):
     - **HIGH** (7+ factors): 13% position size
     - **MEDIUM-HIGH** (5-6 factors): 11% position size
     - **MEDIUM** (3-4 factors): 10% position size
     - **SKIP** (<3 factors): Pass on trade
   - **Final Position Size** = Base Size × Market Breadth Adjustment
   - **Example**: HIGH conviction (13%) in DEGRADED market = 13% × 0.8 = 10.4% actual position

6. **Dynamic Profit Targets** (Enhancement 1.2)
   - **M&A targets**: +15% (stretch +20%)
   - **FDA approvals**: +15% (stretch +25%)
   - **Big earnings beats** (>20%): +12% (stretch +15%)
   - **Standard earnings beats**: +10%
   - **Tier 2 catalysts**: +8%
   - **Tier 3 (insider buying)**: +10% (longer hold: 10-20 days)

6. **Entry Timing Refinement** (Enhancement 1.6)
   - **Avoids** extended moves:
     - >5% above 20-day MA (wait for pullback)
     - 3x+ volume (climax, reversal risk)
     - Up >10% in 3 days (overheated)
     - RSI >70 (overbought)
   - **Entry Quality**:
     - GOOD: No timing issues
     - CAUTION: 1-2 issues
     - POOR: 3+ issues (skip or wait)

7. **Post-Earnings Drift Detection** (Enhancement 1.4)
   - **Strong PED** (Earnings +20%, Revenue +10%, Guidance raised):
     - Target: +12%, Hold: 30-60 days
   - **Medium PED** (Earnings +15%):
     - Target: +10%, Hold: 20-40 days

**Output**:
- BUY recommendations with conviction levels, position sizes, profit targets
- Detailed thesis for each position
- Saved to `daily_reviews/go_YYYYMMDD_HHMMSS.json`

---

### Phase 3: Trade Execution (EXECUTE Command)

**Tool**: `agent_v5.5.py execute`
**Schedule**: 9:45 AM ET daily (15 minutes after market open)
**Purpose**: Execute BUY orders and manage existing positions

#### Execution Logic:

1. **Position Capacity Check**
   - Max 10 positions at a time
   - If portfolio full → Skip to Portfolio Rotation evaluation

2. **Pre-Execution Validation**
   - Fetch current market price
   - Verify stock hasn't gapped >8% (gap-awareness)
   - Check if still in Stage 2 uptrend
   - Confirm volume and technical filters still valid

3. **Gap-Aware Entry** (Enhancement 0.1)
   - **Gap <3%**: Normal entry at market price
   - **Gap 3-5%**: Entry with caution (potential pullback)
   - **Gap 5-8%**: Wait for 1-day consolidation
   - **Gap >8%**: Skip (too extended, high reversal risk)

4. **Position Sizing** (Enhanced Phase 4)
   - **Base Conviction Sizing**:
     - HIGH (7+ factors): 13% base
     - MEDIUM-HIGH (5-6 factors): 11% base
     - MEDIUM (3-4 factors): 10% base
   - **Market Breadth Adjustment** (Phase 4.2):
     - HEALTHY market: 1.0x (no adjustment)
     - DEGRADED market: 0.8x (reduce by 20%)
     - UNHEALTHY market: 0.6x (reduce by 40%)
   - **Final Position Size** = Base × Breadth Adjustment
   - **Effective Range**: 6% (MEDIUM in UNHEALTHY) to 13% (HIGH in HEALTHY)
   - **Example**: HIGH conviction (13%) + DEGRADED market → 13% × 0.8 = 10.4% actual

5. **Stop Loss Calculation**
   - **Standard**: -7% from entry
   - **Gap entries**: Tighter stops (-5%) to account for volatility

6. **Price Target Calculation**
   - Based on catalyst type (see Dynamic Profit Targets above)
   - Trailing stop activates when target is hit

7. **Position Metadata Stored**
   ```
   - Entry date/time
   - Entry price
   - Position size (shares)
   - Stop loss price
   - Price target
   - Catalyst details
   - Conviction level
   - Supporting factors count
   - Technical indicators (50-day MA, 5/20 EMA, ADX, Volume ratio)
   - RS rating (0-100)
   - Volume quality (EXCELLENT/STRONG/GOOD)
   - Volume trending (True/False)
   ```

**Output**:
- Executed trades logged to `trade_history/completed_trades.csv`
- Current positions saved to `active_positions.json`
- Execution results saved to `daily_reviews/execute_YYYYMMDD_HHMMSS.json`

---

### Phase 4: Portfolio Rotation (When Portfolio Full)

**Triggered**: When portfolio has 10/10 positions AND new strong opportunities exist
**Purpose**: Swap underperforming positions for better opportunities

#### Quantitative Rotation Scoring (Enhancement 2.3):

**Exit Candidate Scoring** (0-100, higher = better to exit):
- Weak momentum (<0.3%/day): +30 points
- Stalling (>5 days, <+3% gain): +25 points
- Underwater (<-2%): +40 points
- Low-tier catalyst (Tier 2/3): +15 points
- **Threshold**: Must score ≥50 to be rotation candidate

**Entry Opportunity Scoring** (0-100, higher = better):
- Tier 1 catalyst: +40 points
- Fresh news (<24 hours): +30 points
- High news validation (>80/100): +20 points
- Strong RS rating (>75): +10 points
- **Threshold**: Must score ≥60 to be worth rotating into

**Rotation Decision**:
- Only recommends if exit score ≥50 AND entry score ≥60
- Calculates net score (entry score - (100 - exit score))
- Positive net score = favorable swap
- Claude provides final review and approval

**Output**:
- Exits underperformer
- Enters new opportunity
- Rotation metadata tracked in CSV

---

### Phase 5: Evening Analysis (ANALYZE Command)

**Tool**: `agent_v5.5.py analyze`
**Schedule**: 4:30 PM ET daily (30 minutes after market close)
**Purpose**: Review positions, check for exit conditions

#### Exit Decision Process:

1. **Fetch End-of-Day Prices**
   - Gets 4:00 PM market close prices
   - Calculates current P&L for all positions

2. **Exit Condition Checks**

   **AUTOMATIC EXITS** (Rule-Based):
   - **Stop Loss Hit**: Price ≤ stop loss (-7% or -5% for gap entries)
   - **Target Hit with Trailing Stop**:
     - If price ≥ target, activate trailing stop
     - Lock in minimum +8% gain
     - Trail by 2% from peak
     - Exit when price falls 2% below peak
   - **Time-Based**:
     - Standard positions: 7 days max
     - PED positions: 60 days max
     - Stalling positions (>5 days, <+3%): Consider exit

3. **Gap-Aware Trailing Stop** (Enhancement 1.1)
   - If large gap (>5%) to target:
     - Wait 2 days for consolidation before activating trail
     - Prevents getting shaken out by gap volatility

4. **News Invalidation Check**
   - Claude analyzes recent news (since entry)
   - **Invalidation scenarios** (0-100 points):
     - Deal fell through (M&A): 100 pts → EXIT
     - FDA rejection: 100 pts → EXIT
     - Earnings restatement: 80 pts → EXIT
     - Guidance lowered: 60 pts → Consider exit
     - Negative analyst comments: 40 pts → Monitor
   - **Threshold**: >50 points = Recommend exit

5. **Claude Final Review**
   - Reviews all positions
   - Considers news, price action, market conditions
   - Can override rules for strategic holds
   - Provides exit reasoning for each sale

**Trailing Stop Example**:
```
Entry: $100
Target: $110 (+10%)
Day 1: $105 → Hold (below target)
Day 2: $110 → Trailing stop ACTIVATED at $108 (locks +8%)
Day 3: $112 → NEW PEAK, trailing stop → $109.76 (2% below $112)
Day 4: $115 → NEW PEAK, trailing stop → $112.70 (2% below $115)
Day 5: $113 → Hold (above $112.70 trail)
Day 6: $112.70 → TRAILING STOP HIT, EXIT at $112.70 (+12.7%)
```

**Output**:
- Exit decisions executed
- Trade results logged to CSV with:
  - Exit date/time
  - Exit price
  - Return %
  - Hold days
  - Exit reason (Target Hit, Stop Loss, News Invalidation, Time-Based, etc.)
  - What worked (thesis validation)
  - What failed (if applicable)
- Saved to `daily_reviews/analyze_YYYYMMDD_HHMMSS.json`

---

## Key Enhancements Summary

### Phase 0: Foundation (4 Enhancements)
1. **Gap-Aware Entry/Exit** (Enhancement 0.1)
2. **News Validation Scoring** (Enhancement 0.2)
3. **Sector Concentration Limits** (Enhancement 0.3)
4. **Market Regime Filter** (Enhancement 0.4)

### Phase 1: Core Trading Logic (6 Enhancements)
1. **Trailing Stops** (Enhancement 1.1) - Let winners run
2. **Dynamic Profit Targets** (Enhancement 1.2) - Catalyst-specific targets
3. **Conviction Scoring** (Enhancement 1.3) - Position sizing by strength
4. **Post-Earnings Drift** (Enhancement 1.4) - 30-60 day holds for big beats
5. **Stage 2 Alignment** (Enhancement 1.5) - Minervini trend filter
6. **Entry Timing Refinement** (Enhancement 1.6) - Avoid chasing

### Phase 2: Optimization (4 Enhancements)
1. **RS Rank Percentile** (Enhancement 2.1) - 0-100 RS ratings
2. **Volume Confirmation** (Enhancement 2.2) - Quality + trend scoring
3. **Portfolio Rebalancing** (Enhancement 2.3) - Quantitative rotation
4. **Performance Attribution** (Enhancement 2.4) - Track what works

### Phase 3: RS & Sector Intelligence (4 Enhancements) ✅ COMPLETED
1. **IBD-Style RS Percentile Ranking** (Enhancement 3.1) - Market-wide 0-100 ranking vs all stocks
2. **Sector Rotation Detection** (Enhancement 3.2) - Track 11 sectors vs SPY, prioritize leading sectors
3. **Institutional Activity Signals** (Enhancement 3.3) - Options flow + dark pool tracking
4. **GO Command Integration** (Enhancement 3.4) - Enhanced conviction scoring with Phase 3 data

### Phase 4: Risk Optimization & Anti-Overlap (4 Enhancements) ✅ COMPLETED
1. **Cluster-Based Conviction Scoring** (Enhancement 4.1) - Prevent double-counting correlated signals
   - Groups factors into 4 clusters: Momentum (cap +3), Institutional (cap +2), Catalyst (no cap), Market (cap +2)
   - Reduces max score from 14+ → 11 factors
2. **Market Breadth & Trend Filter** (Enhancement 4.2) - Regime-based position sizing
   - SPY trend + market breadth analysis
   - Three regimes: HEALTHY (1.0x), DEGRADED (0.8x), UNHEALTHY (0.6x)
   - Prevents overtrading in rotational/choppy markets
3. **Sector Concentration Reduction** (Enhancement 4.3) - Reduce correlated drawdown risk
   - Max 2 positions per sector (down from 3)
   - Exception: Allow 3 in top 2 leading sectors (+2% vs SPY)
4. **Liquidity Filter** (Enhancement 4.4) - Prevent execution slippage
   - Minimum $20M average daily dollar volume
   - Filters low-liquidity stocks at screener level

---

## Performance Tracking & Learning

### Learning Command (python agent_v5.5.py learn)
Analyzes past performance across multiple dimensions:

1. **Conviction Accuracy**
   - Do HIGH conviction trades outperform MEDIUM?
   - Validates position sizing strategy

2. **Catalyst Tier Performance**
   - Which catalyst types deliver best returns?
   - Tier 1 vs Tier 2 vs Tier 3 comparison

3. **VIX Regime Performance**
   - How do different market conditions affect returns?
   - Validates risk-off thresholds

4. **News Score Effectiveness**
   - Does higher news validation = better returns?
   - Validates news filtering

5. **Relative Strength Impact**
   - RS positive (≥3%) vs RS negative (<3%)
   - Validates sector rotation strategy

6. **Enhancement Tracking** (NEW in Phase 2)
   - **RS Rating**: Elite (85+) vs Good (65-85) vs Weak (<65)
   - **Volume Quality**: EXCELLENT (3x) vs STRONG (2x) vs GOOD (1.5x)
   - **Volume Trending**: Trending Up vs Flat/Declining

**Output**: JSON reports saved to `learning_data/` for continuous improvement

---

## Data Storage & Audit Trail

### Files Created:

1. **`active_positions.json`** - Current portfolio (updated 3x daily)
2. **`trade_history/completed_trades.csv`** - Complete trade log with 50+ metrics
3. **`daily_reviews/go_*.json`** - Morning analysis (BUY recommendations)
4. **`daily_reviews/execute_*.json`** - Trade execution results
5. **`daily_reviews/analyze_*.json`** - Evening analysis (EXIT decisions)
6. **`screener_candidates.json`** - Latest screener results
7. **`learning_data/*.json`** - Performance attribution reports
8. **`daily_picks.json`** - Dashboard display (accepted + rejected picks)

### CSV Trade History Columns (50+ fields):
- Basic: Ticker, Entry/Exit Date, Entry/Exit Price, Return %, Hold Days
- Position: Shares, Position Size $, Account Value Before/After
- Catalyst: Type, Tier, News Score, Catalyst Details
- Risk: Stop Loss, Price Target, Max Drawdown
- Technical: 50-day MA, 5/20 EMA, ADX, Volume Ratio, Volume Quality, RS Rating
- Conviction: Level, Supporting Factors Count
- Market: VIX at Entry, Market Regime, Macro Events
- Exit: Reason, What Worked, What Failed
- Rotation: Rotation Into Ticker, Rotation Reason (if applicable)

---

## Execution Schedule (Automated via Cron)

```
8:00 AM - Market Screener starts scanning
9:00 AM - GO command (Claude analyzes opportunities)
9:45 AM - EXECUTE command (Place BUY orders)
4:30 PM - ANALYZE command (Review positions, place SELL orders)
```

---

## Risk Management Framework

### Position-Level Risk:
- **Position sizing** (Phase 4):
  - Base: 10-13% (MEDIUM to HIGH conviction)
  - Market breadth adjustment: 0.6x-1.0x multiplier
  - **Effective range**: 6% (MEDIUM in UNHEALTHY) to 13% (HIGH in HEALTHY)
  - **Typical max**: ~10-11% in normal/degraded markets
- **Stop loss**: -7% standard, -5% for gap entries
- **Max hold time**: 7 days standard, 60 days for PED

### Portfolio-Level Risk:
- **Max positions**: 10 (diversification)
- **Sector concentration** (Phase 4.3): Max 2 positions per sector (3 allowed in top 2 leading sectors)
- **Sector rotation aware**: Prioritize leading sectors (+2% vs SPY)
- **Market breadth filter** (Phase 4.2): Reduces exposure in rotational/choppy markets
- **Liquidity floor** (Phase 4.4): Min $20M daily dollar volume (prevents slippage)
- **Market regime**: SHUTDOWN at VIX >30
- **Macro events**: Reduce sizing during Fed/CPI

### Trade-Level Risk:
- **No revenge trading**: Each trade is independent
- **No averaging down**: Only one entry per position
- **No holding losers**: -7% stop is absolute

---

## Technology Stack

- **Language**: Python 3
- **AI Engine**: Claude Sonnet 4.5 (Anthropic)
- **Data Sources**:
  - Polygon.io (price/volume data)
  - Finnhub (news articles)
- **Infrastructure**:
  - DigitalOcean VPS (Ubuntu)
  - Automated via cron
- **Dashboard**: Flask web app for monitoring

---

## What Makes Tedbot Different?

1. **AI-Powered Analysis**: Claude reads and understands news like a human analyst
2. **Catalyst-Driven**: Trades on events, not just technicals
3. **Market-Wide RS Ranking**: IBD-style percentile scoring (only trades top 20% of stocks)
4. **Sector Rotation Awareness**: Prioritizes stocks from leading sectors (+2% vs SPY)
5. **Institutional Signal Detection**: Tracks options flow and dark pool activity (FREE via Polygon)
6. **Cluster-Based Conviction**: Prevents double-counting correlated signals (max 11 factors, down from 14+)
7. **Market Breadth Filter**: Regime-based position sizing (HEALTHY/DEGRADED/UNHEALTHY)
8. **Adaptive Position Sizing**: 6-13% sizing based on conviction + market conditions
9. **Liquidity-Aware**: $20M minimum volume filter prevents execution slippage
10. **Let Winners Run**: Trailing stops capture extended moves
11. **Quantitative + Qualitative**: Combines technical filters with AI reasoning
12. **Full Transparency**: Every decision logged and traceable
13. **Continuous Learning**: Performance attribution guides optimization

---

## Example Trade Lifecycle

**Stock: NVDA**

**1. Identification (Screener):**
- Catalyst: Earnings beat +25%, revenue beat +15%, guidance raised
- Technical: Above 50-day MA, 5 EMA > 20 EMA, ADX 28, Volume 3.2x (EXCELLENT)
- RS: +12% vs SMH (sector), RS Rating: 85 (STRONG)
- Stage 2: All 5 checks pass ✓

**2. Analysis (GO - 9:00 AM):**
- News Score: 18/20 (5 articles, all positive, fresh <12hrs)
- VIX: 18 (GREEN - normal trading)
- Sector: Technology (Leading sector, +3.4% vs SPY)
- RS Percentile: 92 (top 8% of all stocks)
- Institutional Signals: Dark pool accumulation detected (2.1x volume)
- Conviction: HIGH (9 supporting factors)
  - Tier 1 catalyst ✓
  - RS >7% ✓
  - **RS 92nd percentile (top 10%)** ✓✓ (double weight)
  - **Leading sector (+3.4% vs SPY)** ✓
  - Fresh news (<12hrs) ✓
  - Volume >2x ✓
  - News >15/20 ✓
  - ADX >25 ✓
  - **Dark pool accumulation** ✓
  - **Revenue beat (EPS + Revenue)** ✓
- Position Size: 13% ($130)
- Target: +12% (Strong PED detected)
- Hold: 30-60 days (earnings drift)

**3. Execution (EXECUTE - 9:45 AM):**
- Entry Price: $140.00
- Gap: +2.5% (normal entry)
- Shares: 0.93 shares ($130 position - HIGH conviction 13%)
- Stop Loss: $130.20 (-7%)
- Price Target: $156.80 (+12%)

**4. Position Monitoring (ANALYZE - Daily 4:30 PM):**
- Day 1: $142 (+1.4%) → HOLD
- Day 2: $145 (+3.6%) → HOLD
- Day 3: $150 (+7.1%) → HOLD
- Day 10: $156.80 (+12%) → TRAILING STOP ACTIVATED at $145.60 (+8% locked)
- Day 15: $162 (+15.7%) → NEW PEAK, trail → $158.76
- Day 20: $165 (+17.9%) → NEW PEAK, trail → $161.70
- Day 22: $163 (+16.4%) → HOLD (above trail)
- Day 23: $161.70 (+15.5%) → **TRAILING STOP HIT - EXIT**

**5. Trade Result:**
- Entry: $140.00
- Exit: $161.70
- Return: **+15.5%**
- Hold: 23 days
- Profit: $20.16 (from $130 position vs $12.37 from old $80 position)
- Exit Reason: "Trailing stop hit (peak was +17.9%)"
- What Worked: "Strong earnings catalyst, post-earnings drift as expected, excellent volume confirmation, market-leading RS percentile (92), leading sector (Technology), institutional accumulation"

---

## Common Questions

**Q: How much does it trade?**
A: Typically 2-5 new positions per week, depending on catalyst flow. Max 10 positions at once.

**Q: What's the win rate target?**
A: 65-70% after Phase 1 enhancements (was 55% baseline).

**Q: Average return per trade?**
A: Target +12-15% on winners (up from +8% baseline), -4% on losers.

**Q: How long are positions held?**
A: Average 3-7 days. Post-earnings drift positions: 30-60 days.

**Q: What sectors does it trade?**
A: Any sector, but limits to max 2 positions per sector to avoid concentration risk (3 allowed in top 2 leading sectors).

**Q: Can it trade options?**
A: No, stock-only for now. Options require different risk management.

**Q: Does it handle earnings announcements?**
A: Yes! It specifically looks for earnings beats and uses post-earnings drift strategy for strong beats (>15% surprise).

**Q: What happens in a market crash?**
A: SHUTDOWN mode activates at VIX >30. All positions exit at stops, no new trades until VIX <25.

---

**Last Updated**: December 1, 2024
**Version**: v5.6 (Phase 0-4 Complete: 22 Enhancements)
**Status**: Live in production paper trading

**Latest Updates (Phase 4 - Risk Optimization)**:
- ✅ Phase 4.1: Cluster-based conviction scoring (prevents double-counting correlated signals)
- ✅ Phase 4.2: Market breadth & trend filter (regime-based position sizing)
- ✅ Phase 4.3: Sector concentration reduction (max 2 per sector, 3 in leading sectors)
- ✅ Phase 4.4: Liquidity filter (min $20M daily volume prevents slippage)

**Previous Updates**:
- ✅ Phase 3: IBD-style RS percentile ranking, sector rotation detection, institutional signals
- ✅ Phase 2: RS rank percentile, volume confirmation, portfolio rebalancing, performance attribution
- ✅ Phase 1: Trailing stops, dynamic targets, conviction scoring, post-earnings drift, Stage 2 alignment
- ✅ Phase 0: Gap-aware entry/exit, news validation, sector concentration, market regime filter
