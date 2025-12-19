# PAPER TRADING LAB - PROJECT INSTRUCTIONS v2.1 (Phase 1 + Gap-Ups Complete)

## 🎯 PROJECT OVERVIEW

**Project Name:** Paper Trading Lab - Tedbot
**Strategy:** Catalyst-Driven Swing Trading with Continuous Portfolio Optimization
**Start Date:** October 27, 2025
**Starting Capital:** $1,000 (paper money)
**Methodology:** Entry Quality Scorecard (100-point systematic evaluation)

---

## 🎭 STRATEGY PHILOSOPHY (IMPORTANT)

**This is a MULTI-TIER, REGIME-AWARE system, NOT a "Tier 1 only" system.**

### Tier Acceptance Policy:
**The system accepts Tier 1, 2, 3, and 4 catalysts** - but with **regime-dependent restrictions**:

- **Normal Markets (VIX <25):** All tiers acceptable (Tier 1, 2, 3, 4)
  - **Preference hierarchy:** Tier 1 > Tier 2 > Tier 4 > Tier 3
  - Tier 3/4 require stronger technical confirmation (RS ≥70 percentile, volume >150%)

- **Elevated Risk (VIX 25-30):** **Tier 1 or Tier 2 ONLY** (no Tier 3/4 technical catalysts)
  - System tightens to fundamental catalysts only

- **High Risk (VIX 30-35):** **Tier 1 ONLY** + News score ≥15/20 required
  - System restricts to highest-conviction fundamental catalysts

- **Shutdown (VIX ≥35):** **NO NEW POSITIONS** (existing positions held at stops)

### Why Multi-Tier Design:
**Code supports all tiers** because market conditions change dynamically:
- VIX regime determines acceptable catalyst tiers
- Profit targets are catalyst-specific (Tier 1 = +15%, Tier 2 = +12%, Tier 3 = +10%, Tier 4 = +8%)
- Post-earnings drift detection supports extended holds (Tier 1 earnings catalysts)
- Learning system tracks performance by catalyst tier for continuous improvement

**This is intentional flexibility, not design drift.** The system adapts catalyst acceptance based on risk regime.

---

## 📋 THE STRATEGY

### Core Concept:
Maintain an **actively optimized portfolio** targeting **8-10 high-quality positions** based on the Entry Quality Scorecard (0-100 points). Prioritize win rate over forced fills - only enter positions scoring ≥60 points. When portfolio is full (10 positions) and exceptional new opportunities (80+ points) emerge, rotate out the weakest performer to continuously optimize the portfolio.

### Position Sizing (Cluster-Based Conviction):
The system uses **conviction levels** derived from cluster-based factor scoring (Phase 4.1):

**Base Conviction Sizing:**
- **HIGH conviction** (7+ supporting factors): 13% base
- **MEDIUM-HIGH conviction** (5-6 factors): 11% base
- **MEDIUM conviction** (3-4 factors): 10% base
- **SKIP** (<3 factors): Do not enter

**Supporting Factors** (max 11 via clustering):
- **Momentum Cluster** (cap +3): RS percentile, sector strength, RS vs sector
- **Institutional Cluster** (cap +2): Options flow, dark pool activity
- **Catalyst Cluster** (no cap): Tier 1, multi-catalyst, revenue beat, news score >15
- **Market Conditions Cluster** (cap +2): VIX <20

**Market Breadth Adjustment:**
- **HEALTHY** (breadth ≥50%): 1.0x multiplier (no adjustment)
- **DEGRADED** (breadth 40-49%): 0.8x multiplier (reduce 20%)
- **UNHEALTHY** (breadth <40%): 0.6x multiplier (reduce 40%)

**Final Position Size** = Base Conviction × Market Breadth Adjustment

**Examples:**
- HIGH (13%) in HEALTHY market: 13% × 1.0 = 13% position
- HIGH (13%) in DEGRADED market: 13% × 0.8 = 10.4% position
- MEDIUM (10%) in UNHEALTHY market: 10% × 0.6 = 6% position

**Effective Range:** 6% (MEDIUM in UNHEALTHY) to 13% (HIGH in HEALTHY)

### Portfolio Targets:
- **Target:** 8-10 positions (goal, not enforced minimum)
- **Maximum:** 10 positions (**HARD LIMIT enforced** - rotation logic triggers at 10/10)
- **Actual Range:** 0-10 positions depending on quality setups available
  - Weak markets or high VIX: May hold 3-5 positions
  - Normal markets: Typically 6-10 positions
  - Strong opportunity flow: 10/10 positions (rotation mode active)
- **Quality Threshold:** Minimum 3 supporting factors required (MEDIUM conviction)
- **Cash Management:** Natural cash reserve results from quality-over-quantity approach
  - System does NOT enforce minimum cash reserve
  - Cash levels fluctuate based on available quality setups (3+ factors)
  - Typical cash: 0-30% depending on market opportunity set

**Note:** The Entry Quality Scorecard (0-100 points) is a DECISION FRAMEWORK for Claude to evaluate opportunities, not an automated threshold. The system enforces hard gates (technical filters, Stage 2, news score ≥5, Tier validation) and requires minimum 3 supporting factors for entry.

---

## 📊 ENTRY QUALITY SCORECARD (0-100 POINTS)

Every candidate is evaluated systematically across five components. This is the PRIMARY decision framework.

### Component 1: Catalyst Quality (0-30 points)

**Earnings Surprise Magnitude:**
- >25% beat: 12 points
- 15-25% beat: 9 points
- 10-15% beat: 6 points
- 5-10% beat: 3 points

**Revenue Performance:**
- EPS + Revenue beat: 8 points
- Revenue beat only: 4 points
- EPS beat only: 2 points

**Catalyst Freshness:**
- 0-2 days old: 5 points
- 3-5 days old: 3 points
- 6-10 days old: 1 point
- >10 days old: 0 points

**Secondary Catalysts** (bonus, max +5):
- Major analyst upgrade: +5 points
- Technical breakout: +4 points
- Sector momentum: +3 points
- Price target increase: +2 points

---

### Component 2: Technical Setup (0-25 points)

**Trend Alignment** (0-7 points):
- Price > 200-day SMA: +1
- Price > 50-day SMA: +2 (REQUIRED)
- 50 SMA > 200 SMA: +1
- 5 EMA > 20 EMA: +2 (REQUIRED)
- ADX >25: +1

**Relative Strength vs SPY** (0-5 points):
- >5% outperformance: 5 points
- 3-5% outperformance: 3 points
- 1-3% outperformance: 2 points
- <1%: 0 points
- Top 3 sector bonus: +2 points (capped at 5 total)

**Volume Confirmation** (0-5 points):
- >3x average volume: 5 points
- 2-3x average: 4 points
- 1.5-2x average: 2 points
- <1.5x average: 0 points
- OBV trending up: +1 bonus

**Price Action Setup** (0-5 points, select best):
- Clean breakout: 3 points
- Pullback holding support: 3 points
- Key retracement (38.2%, 50%, 61.8%): 2 points
- Confirming candlestick pattern: 1 point
- Gap with catalyst: 2 points

**Technical Structure** (0-3 points):
- Above recent swing highs: +1
- Clear stop-loss within 5-7%: +1
- Identifiable 3:1 risk-reward: +1

---

### Component 3: Sector and Market Context (0-20 points)

**Sector Strength** (0-6 points):
- Top 3 sectors: 4 points
- Ranks 4-6: 2 points
- Ranks 7-9: 0 points
- Bottom 2 sectors: -2 points
- Sector ETF above 50/200 MA: +2 bonus
- Positive 1-month momentum: +2 bonus

**Market Regime** (0-8 points):
- SPY above both 50/200 MA: 3 points
- VIX <25: +1 point
- Market breadth >50%: +1 point
- Positive new highs - new lows: +1 point
- SPY ADX >25 (trending): +1 point
- Max: 7 points

**Diversification** (0-4 points):
- 1st or 2nd position in sector: 2 points
- 3rd position in sector: 1 point
- 4th+ position in sector: -2 points (penalty)
- Portfolio concentration <40% any sector: +2 points

**Event Timing** (0-2 points, or penalties):
- No major events within 2 days: 2 points
- Minor events nearby: 0 points
- FOMC window: -3 points
- CPI/NFP window: -2 points
- Holding through earnings: -5 points

---

### Component 4: Historical Pattern Match (0-15 points)

**Catalyst Quality:**
- Tier 1 (earnings+guidance, M&A, FDA, major contracts): 4 points
- Tier 2 (analyst upgrades, strong beats, contracts): 3 points
- Tier 3 (product launches, sector news): 2 points
- Tier 4 (minor news): 1 point
- No catalyst: 0 points

**Sector Positioning** (0-2 points):
- Tech/Healthcare in bull market with strong RS: 2 points
- Cyclicals in neutral market: 1 point
- Defensives in bull market: 0 points

**Gap/Technical Setup** (0-3 points):
- 2-5% gap on >2x volume + breakout: 3 points
- 1-4% gap with volume: 2 points
- Minimal gap, average volume: 1 point
- No gap or low volume: 0 points
- >5% gap without volume: -1 point

**Timing Factors** (0-2 points):
- Monday close or Tuesday entry: 2 points
- Tuesday/Wednesday: 1 point
- Thursday/Friday: 0 points

**Seasonality** (0-2 points):
- Earnings season/year-end/turn-of-month: 2 points
- Neutral periods: 1 point
- Summer doldrums: 0 points

**Volume Confirmation** (0-2 points):
- >2x sustained volume: 2 points
- 1.5-2x volume: 1 point
- Below average: 0 points
- Declining volume: -1 point

---

### Component 5: Conviction and Risk (0-10 points)

**Entry Conviction** (0-6 points):
- Technical alignment: 0-3 points
- Catalyst quality: 0-3 points

**Risk Adjustment** (0-4 points):
- Low ATR (<1.0x average): +2 points
- Normal ATR: 0 points
- High ATR (>1.5x average): -2 points
- Beta <0.8: +1 point
- Beta >1.5: -1 point
- Risk-reward ≥3:1: +2 points
- Risk-reward 2-3:1: +1 point
- Risk-reward <2:1: 0 points

---

### SCORE THRESHOLDS

**Total Score Interpretation:**
- **80-100 points:** Exceptional setup
  - Target win rate: 70-75%
  - Position size: Full conviction (8-10%)
  - Action: Always accept, consider rotation if portfolio full

- **60-79 points:** Good setup
  - Target win rate: 60-70%
  - Position size: Standard (6-8%)
  - Action: Accept to fill portfolio slots

- **50-59 points:** Decent setup
  - Target win rate: 50-60%
  - Position size: Reduced (5-6%)
  - Action: Consider only if portfolio <8 positions

- **40-49 points:** Marginal setup
  - Target win rate: 45-55%
  - Position size: Minimal (4-5%)
  - Action: Reject (insufficient quality)

- **<40 points:** Poor setup
  - Target win rate: <45%
  - Action: Always reject

**Market Regime Multipliers:**
- VIX <20: Score × 1.1
- VIX 20-30: Score × 1.0
- VIX 30-40: Score × 0.7
- VIX >40: Score × 0.3 or system pause

---

## 🎯 CATALYST ACCEPTANCE CRITERIA

### Tier 1 Catalysts (High Probability)
**Always evaluate, accept if scorecard ≥60:**
- Earnings beats >10% with raised guidance
- M&A announcements (news + SEC 8-K Item 2.01)
- FDA approvals
- Major contract wins (news + SEC 8-K Item 1.01)
- Revenue beats >10% combined with EPS beat

### Tier 2 Catalysts (Medium Probability)
**Evaluate, accept if scorecard ≥60:**
- Analyst upgrades from major firms (Goldman, Morgan Stanley, JPM)
- Analyst upgrade trends (multiple upgrades)
- **Price target raises >20% (NEW - PHASE 1.1):** Analyst price targets raised significantly above current price
- SEC 8-K contract filings (Item 1.01)
- Contract news from reliable sources
- Strong earnings beats without guidance (>15%)

### Tier 3 Catalysts (Leading Indicators)
**Accept with strong RS/technical confirmation (3+ supporting factors required):**
- **Sector rotation (NEW - PHASE 1.3):** Stock in sector outperforming SPY by >5% (3-month basis)
- Insider buying clusters (3+ transactions within 30 days)
- Product launches without immediate revenue impact
- Conference presentations with strong momentum

**Reject - Insufficient catalyst:**
- Insider buying only (single transaction, no other catalyst)
- General sector momentum without strong outperformance

### Tier 4 Catalysts (Technical Catalysts)
**NEW - Accept with strong volume + RS confirmation:**
- **52-week high breakouts (PHASE 1.2):** Fresh breakout (last 5 days) with volume >150% average, price maintained within 3% of high
- **Gap-ups (PHASE 2.5):** Opening gap >3% above previous close with volume >120% average, gap maintained through close
- Consolidation breakouts with volume (4+ weeks tight range, volume spike on breakout)

**Note on Tier 4:** Technical catalysts require stronger RS and momentum confirmation than fundamental catalysts. System weights volume and RS heavily (35-40% weight) for Tier 4 positions.

---

## 📐 RISK MANAGEMENT RULES

### Entry Requirements:
- **Entry Quality Score:** Minimum 3 supporting factors (REQUIRED for entry)
- **Catalyst Tier (Regime-Dependent):**
  - **Normal Markets (VIX <25):** Tier 1, Tier 2, Tier 3, or Tier 4 acceptable (with 3+ supporting factors)
  - **Elevated Risk (VIX 25-30):** Tier 1 or Tier 2 ONLY (no Tier 3/4)
  - **High Risk (VIX 30-35):** Tier 1 ONLY + News ≥15/20
  - **Shutdown (VIX ≥35):** NO NEW POSITIONS (existing positions held at stops)
  - **Tier 3/4 Requirement:** Must have strong RS (≥70 percentile) AND volume confirmation
  - **Always Rejected:** Single insider transaction without other catalyst, weak sector momentum (<5% vs SPY)
- **Catalyst Age:** <5 days for earnings, <2 days for upgrades
- **Technical Filters:** ALL must pass:
  1. Price > 50-day SMA (trend filter)
  2. 5 EMA > 20 EMA (momentum filter)
  3. ADX >20 (trend strength filter)
  4. Volume >1.5x average (institutional confirmation)
- **Stage 2 Alignment:** 5/5 Minervini checks (REQUIRED)
- **News Validation:** Score ≥5/20 points (REQUIRED)
- **Liquidity:** Min $50M average daily dollar volume
- **Price:** Min $10/share
- **Market Cap:** Min $1B

### Exit Rules (STRICTLY ENFORCED):

**Automatic Exits:**
1. **Stop Loss Hit (-7%):** Exit immediately, no exceptions
2. **Price Target Hit (+10-15%):** Exit 50%, trail remaining 50%
3. **Catalyst Invalidated:** Exit same day if news score ≥70/100 (negative)
4. **Time Stop (21 days):** Exit if no progress after 3 weeks
5. **Technical Breakdown:** Exit if breaks below 50-day SMA with volume

**Portfolio Rotation:**
6. **Better Opportunity (Full Portfolio):**
   - Triggered when portfolio has 10/10 positions
   - New opportunity scores ≥80 points (exceptional)
   - Existing position scores ≥50 on exit scoring (weak momentum, stalling, underwater, low-tier catalyst)
   - Net rotation score positive (entry score - (100 - exit score) > 0)
   - Exit weakest performer, enter new exceptional setup

**Never:**
- Hold through stop loss hoping for recovery
- Sell winners early out of fear
- Average down on losing positions
- Make emotional decisions
- Force fills to reach 10 positions

---

## 🔄 DAILY WORKFLOW

### Pre-Market Screening (7:00 AM) - Automated

**Market Screener Runs:**
1. Scan S&P 1500 universe (~993 stocks currently tracked)
2. Apply hard filters:
   - Price ≥$10
   - Market cap ≥$1B
   - Average daily dollar volume ≥$50M
   - **Catalyst presence (Tier 1/2/3 required)**
   - **RS calculated for SCORING only (0-5 points), NOT filtered**
3. Calculate composite score with tier-aware weighting:
   - **Tier 1:** Catalyst 40%, RS 20%, News 20%, Volume 10%, Technical 10%
   - **Tier 2:** Catalyst 35%, RS 25%, News 20%, Volume 10%, Technical 10%
   - **Tier 3:** Catalyst 30%, RS 40%, News 10%, Volume 10%, Technical 10%
4. Output 300-500 catalyst-driven candidates to `screener_candidates.json`
   - **Expected distribution:** ~30-40% Tier 1, ~30% Tier 2, ~30% Tier 3

**Output:** Pre-qualified list of 300-500 stocks with real catalysts

**Note:** RS (Relative Strength) is now a SCORING component (0-5 points), NOT a filter. Stocks with any RS value (including negative) pass through if they have catalysts.

---

### Morning Check-In (9:00 AM) - User Issues: "go"

**Claude Will:**

1. **Review Current Portfolio (HOLD/EXIT decisions)**
   - Check overnight news on each position
   - Calculate news invalidation scores (0-100)
   - Verify stop losses / targets not hit
   - Assess if theses still intact
   - Flag positions for exit if:
     - Stop loss hit (-7%)
     - Target hit (+10-15%)
     - News invalidation score ≥70
     - Catalyst invalidated
     - Time stop reached (21 days)
     - Technical breakdown

2. **Evaluate New Opportunities (BUY decisions)**
   - Load 300-500 candidates from screener
   - Apply Entry Quality Scorecard to each candidate
   - Accept candidates scoring ≥60 points
   - Prioritize by total score (80+ = exceptional)
   - Expected: 10-20 candidates score ≥60 points

3. **Portfolio Optimization (ROTATION if applicable)**
   - If portfolio has 10/10 positions AND new opportunity scores ≥80:
     - Score existing positions for exit candidacy (0-100)
     - Identify weakest performer (exit score ≥50)
     - Calculate net rotation score
     - If positive net score: recommend rotation
     - Exit weakest, enter exceptional new setup

4. **Position Sizing (Conviction-Based)**
   - Base: 10% per position
   - Multiply by conviction (score/100)
   - Adjust for volatility (ATR, beta)
   - Adjust for market regime (VIX)
   - Apply drawdown protocol if applicable
   - Ensure sector concentration limits (<40% any sector, max 2-3 per sector)

5. **Provide Clear Action Items**
   ```
   TODAY'S ACTIONS:

   EXITS (if any):
   - [TICKER]: Stop hit / Target reached / News invalidation / Time stop

   ENTRIES (prioritized by score):
   - [TICKER] (Score: 85/100): Tier 1 catalyst, exceptional setup, 8.5% position
   - [TICKER] (Score: 72/100): Tier 2 catalyst, good setup, 7.2% position

   ROTATIONS (if portfolio full):
   - EXIT [WEAK_TICKER] (Exit Score: 65): Stalling momentum
   - ENTER [STRONG_TICKER] (Entry Score: 88): Exceptional new catalyst

   HOLDS:
   - [X positions]: All theses intact, no action needed

   Portfolio Status: [X/10] positions, [Y%] cash
   Portfolio Value: $X,XXX.XX
   Unrealized P&L: +/-X.XX%
   ```

6. **Document in JSON for execution**
   - All decisions logged with scores
   - Reasoning captured for accountability
   - Portfolio updates prepared

---

## 🔬 TECHNICAL VALIDATION (ALL REQUIRED)

Every stock must pass **ALL 4 technical filters**:

1. **50-Day Moving Average (SMA50):**
   - Stock price MUST be above 50-day SMA
   - Confirms uptrend, rejects downtrends

2. **EMA Momentum (5/20 Cross):**
   - 5-day EMA MUST be above 20-day EMA
   - Confirms momentum acceleration

3. **ADX (Average Directional Index):**
   - ADX MUST be >20
   - Confirms trend strength (not choppy/sideways)

4. **Volume Confirmation:**
   - Current volume MUST be >1.5x 20-day average
   - Confirms institutional participation

**Plus:**

5. **Stage 2 Alignment (Minervini):**
   - All 5 checks must pass (REQUIRED)
   - Price > 50/150/200 MA
   - Moving averages in correct order
   - Within 25% of 52-week high

6. **Entry Timing:**
   - Not extended >5% from 20-day MA
   - RSI not overbought (>75)
   - No exhaustion signals

---

## 📰 NEWS INTEGRATION

### Entry Validation (GO Command):
**News Validation Score (0-20 points):**
- Catalyst freshness: 0-5 pts
- Momentum acceleration: 0-5 pts
- Multi-catalyst detection: 0-10 pts
- Contradicting news: negative pts
- **Minimum required:** 5 points to proceed

### Exit Monitoring (Ongoing):
**News Invalidation Score (0-100 points):**
- Negative keywords (critical/severe/moderate/mild)
- Context amplifiers (dollar amounts, percentages)
- Source credibility (Bloomberg 1.0x, retail 0.25x)
- Recency bonus (breaking <1 hour: +10 pts)
- **Auto-exit threshold:** ≥70 points (before stop loss hit)

### Data Sources:
- Polygon.io News API (primary)
- SEC EDGAR 8-K filings (M&A, contracts - 1-2 hour early detection)
- Finnhub earnings/analyst data
- FMP revenue data

---

## 💡 KEY STRATEGIC PRINCIPLES

### Quality Over Quantity:
- **Target:** 8-10 positions scoring ≥60 points
- **Accept:** Good setups (60+), prioritize exceptional (80+)
- **Reject:** Marginal setups (<60) even if slots available
- **Cash:** Maintain 10-30% reserve for best opportunities

### Continuous Optimization:
- Portfolio is NEVER static
- Always looking to upgrade weakest position
- Rotation when exceptional opportunity emerges
- Quality improvement over time

### Conviction-Based Sizing:
- Higher scores = larger positions
- Variable sizing (5-12%) vs fixed 10%
- Risk-adjusted for volatility and beta
- Regime-adjusted for VIX

### Win Rate Priority:
- Target 60-70% win rate (vs 50-55% with forced fills)
- Only exceptional setups (80+) trigger rotations
- Never force fills to reach 10 positions
- Cash is a position (optionality + safety)

### Systematic Scoring:
- Entry Quality Scorecard eliminates bias
- Every decision quantified and traceable
- Repeatable process compounds edge
- Continuous calibration and improvement

---

## 🎓 METHODOLOGY SOURCE

This system implements the **Entry Quality Scorecard methodology** from Deep Research v7.0 (December 2025), which synthesizes:

- Post-Earnings Announcement Drift (Bernard & Thomas)
- Sector Momentum (Moskowitz & Grinblatt, Meb Faber)
- Volatility-Managed Portfolios (Moreira & Muir)
- Technical Analysis (Lo, Mamaysky, Wang - MIT Journal of Finance 2000)
- IBD/Minervini relative strength and Stage 2 methodology
- Professional fund manager conviction-based sizing practices

**Key Research Principles:**
1. Hard filters at screener level (price, volume, catalyst)
2. AI evaluates quality using 100-point scorecard
3. Score-based ranking (not binary accept/reject)
4. Conviction-based sizing (not fixed allocations)
5. Continuous optimization (rotation when beneficial)

---

## 📊 EXPECTED PERFORMANCE

### Portfolio Composition:
- **Typical state:** 8-10 positions
- **Strong markets:** 9-10 positions (more 60+ setups)
- **Weak markets:** 5-7 positions (fewer quality setups)
- **High VIX (>30):** 3-5 positions (highest conviction only)

### Quality Metrics:
- **Average score:** 65-75 points
- **Win rate:** 60-70% (vs 55% with forced fills)
- **Avg position size:** 6-9% (conviction-adjusted)
- **Monthly turnover:** 3-6 new positions/rotations

### Risk Metrics:
- **Max position:** 15% (exceptional setups with low volatility)
- **Sector concentration:** <40% any sector
- **Typical drawdown:** 8-12% (stop losses enforced)
- **Max drawdown target:** <15%

---

**Version:** 2.1 (Enhanced Catalyst Detection - Phase 1 + Gap-Ups)
**Last Updated:** December 18, 2025
**Methodology:** Entry Quality Scorecard (100-point systematic framework)
**Strategy:** Continuous Portfolio Optimization with Win Rate Priority
**New in v2.1:** Added Tier 2 (price targets), Tier 3 (sector rotation), Tier 4 (52W breakouts, gap-ups)
