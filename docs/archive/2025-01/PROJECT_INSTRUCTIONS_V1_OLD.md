# PAPER TRADING LAB - PROJECT INSTRUCTIONS

## 🎯 PROJECT OVERVIEW

**Project Name:** Paper Trading Lab  
**Strategy:** Catalyst-Driven Swing Portfolio with Continuous Learning  
**Start Date:** October 27, 2025  
**Starting Capital:** $1,000 (paper money)

---

## 📋 THE STRATEGY

### Core Concept:
Maintain an active portfolio of exactly **10 stocks** at all times, holding positions for **3-7 days** (up to 3 weeks maximum) based on high-probability catalysts. The system learns from every trade and continuously refines its approach.

### Position Sizing:
- Each stock receives **10% of total account value**
- Account always fully invested (10 positions × 10% = 100%)
- Rebalance when replacing positions

---

## 🎯 STOCK SELECTION CRITERIA (TIER 1 CATALYSTS ONLY)

### ✅ We ONLY Buy Stocks With:

1. **Earnings Beats with Raised Guidance**
   - Beat consensus by 10%+
   - Raised forward guidance
   - Post-earnings drift is proven edge

2. **Strong Sector Momentum Plays**
   - Clear macro catalyst (oil spike, policy change, etc.)
   - Multiple stocks in sector moving together
   - Momentum typically lasts days/weeks

3. **Major Analyst Upgrades**
   - From top-tier firms (Goldman, Morgan Stanley, etc.)
   - Significant price target increase
   - Often creates 2-5 day follow-through

4. **Confirmed Technical Breakouts**
   - New 52-week high or key resistance break
   - MUST have 2x+ average volume
   - Institutional buying evident

5. **Binary Event Winners**
   - FDA approvals
   - Major contract wins
   - M&A announcements
   - Clear positive outcome

### ❌ We NEVER Buy:
- Pre-market pumps >15% (fade by noon)
- Meme stocks without fundamental catalyst
- Penny stocks (<$5/share)
- Stocks without clear 2-sentence thesis
- Market cap <$1B (liquidity issues)
- Anything without Tier 1 catalyst

---

## 🔬 PHASE 5.6: TECHNICAL VALIDATION (Added Nov 11, 2025)

Every stock must pass **ALL 4 technical filters** in addition to having a Tier 1 catalyst:

### Required Technical Indicators (ALL MUST PASS):

1. **50-Day Moving Average (SMA50):**
   - Stock price MUST be above 50-day SMA
   - Confirms uptrend / rejects downtrends
   - Data source: Polygon.io

2. **EMA Momentum (5/20 Cross):**
   - 5-day EMA MUST be above 20-day EMA
   - Confirms momentum acceleration
   - Rejects choppy or declining momentum

3. **ADX (Average Directional Index):**
   - ADX MUST be >20
   - Confirms strong trend (not sideways chop)
   - ADX <20 indicates weak/choppy market - reject

4. **Volume Confirmation:**
   - Current volume MUST be >1.5x 20-day average
   - Confirms institutional participation
   - Low volume = lack of conviction - reject

**Validation:** All 4 filters checked automatically during GO command. Stocks failing ANY filter are rejected regardless of catalyst quality.

---

## 📰 NEWS INTEGRATION & CATALYST VERIFICATION (Added Nov 14, 2025)

### How Catalyst Verification Works:

1. **Market Screener (8:30 AM):**
   - Scans S&P 1500 for stocks with RS ≥3%
   - Fetches top 5 news articles per stock from Polygon.io
   - Extracts: title, description, publish date, URL
   - Scores based on catalyst keywords

2. **GO Command (8:45 AM):**
   - Claude receives top 15 candidates with ACTUAL NEWS CONTENT
   - Reviews article titles and descriptions (not just keywords)
   - Verifies which stocks have genuine Tier 1 catalysts

3. **Catalyst Quality Assessment:**
   - **Tier 1 Verified:** Earnings beat >10% with guidance, FDA approval, M&A deal
   - **Tier 2/3 Rejected:** Analyst opinions, sector momentum without catalyst, stale news

**Example:**
- AMD (#1 score): "Investment in quantum company" → Rejected (not Tier 1)
- BIIB (#12 score): "UK approval for LEQEMBI maintenance dosing" → Selected (Tier 1 binary event)

**This ensures quality over quantity** - system will select lower-ranked stocks if they have superior catalysts.

---

## 📐 RISK MANAGEMENT RULES

### Entry Requirements:
- Must articulate thesis in 2 sentences
- Set entry price BEFORE buying
- Set stop loss at -7% from entry
- Set initial price target (+10-15% depending on catalyst)
- Require 3+ supporting factors (catalyst + technical + sector)
- **Pass ALL 4 technical filters (Phase 5.6)**
- **Verified Tier 1 catalyst from actual news content**

### Exit Rules (STRICTLY ENFORCED):

**Automatic Exits:**
1. **Stop Loss Hit (-7%):** Sell immediately, no exceptions
2. **Price Target Hit (+10-15%):** Sell 50%, trail remaining 50%
3. **Catalyst Invalidated:** Exit same day (news reversal, guidance cut)
4. **Time Stop (3 weeks):** Exit if no progress after 21 days
5. **Better Opportunity:** May exit weakest position if new Tier 1 emerges

**Never:**
- Hold through stop loss hoping for recovery
- Sell winners early out of fear  
- Average down on losing positions
- Make emotional decisions

---

## 🔄 DAILY WORKFLOW

### Pre-Market Screening (8:30 AM) - Automated

**Market Screener Runs:**
1. Scan S&P 1500 universe (~1,500 stocks)
2. Filter for Relative Strength ≥3% vs sector
3. Check for recent catalysts (news, volume surges, breakouts)
4. Score and rank candidates by composite score:
   - 40% Relative Strength
   - 30% News/Catalyst Strength
   - 20% Volume Surge
   - 10% Technical Setup
5. Save top 50 candidates to `screener_candidates.json`

**Output:** Pre-qualified list of 50 stocks with real catalysts

---

### Morning Check-In (8:45 AM) - User Issues: "Go"

**Claude Will:**
1. Review all 10 current portfolio positions
   - Check overnight news on each holding
   - Verify stop losses / targets not hit
   - Assess if theses still intact

2. Evaluate pre-screened candidates from Market Screener
   - Review top 50 candidates from 8:30 AM scan
   - Analyze composite scores and catalyst strength
   - Select best opportunities from real market data
   - Fallback to manual search if screener unavailable

3. Make trading decisions
   - Which positions to EXIT (if any)
   - Which new positions to ENTER (from screener candidates)
   - Update any stop losses or targets

4. Provide clear action items:
   ```
   TODAY'S ACTIONS:
   SELL: [TICKER] - Reason: [stop hit / target reached / catalyst failed]
   BUY: [TICKER] - Reason: [Tier 1 catalyst description]
   HOLD: [X positions] - All theses intact
   
   Portfolio Value: $X,XXX.XX
   Unrealized P&L: +/-X.XX%
   ```

5. Document in `/daily_reviews/YYYY-MM-DD_morning.md`

**Time Required from User:** 5-10 minutes to read and acknowledge

---

### Evening Update (3:45 PM - Optional) - User Issues: "analyze"

**Claude Will:**
1. Update all position prices and P&L
2. Check if any positions hit key levels during day
3. Document any completed trades
4. Extract learnings from today's action
5. Prepare tomorrow's watchlist
6. Update all tracking files

**Time Required from User:** 5-10 minutes

---

## 🧠 THE LEARNING SYSTEM (CRITICAL COMPONENT)

### What Makes This System Work:

Every single day, Claude will:

1. **Document Everything:**
   - Why each position was entered (thesis)
   - Why each position was exited (result)
   - What worked vs. what failed
   - Market conditions and context

2. **Track Performance by Catalyst Type:**
   - Earnings beats: Win rate, avg return, optimal hold time
   - Sector plays: Win rate, avg return, optimal hold time
   - Technical breakouts: Win rate, avg return, optimal hold time
   - Analyst upgrades: Win rate, avg return, optimal hold time

3. **Identify Patterns:**
   - Which setups have >70% win rate (do more of these)
   - Which setups have <40% win rate (stop doing these)
   - What's the optimal holding period per catalyst
   - How to improve entry/exit timing

4. **Refine Strategy:**
   - Drop low-performing catalyst types
   - Increase allocation to proven patterns
   - Adjust stop loss / target levels based on data
   - Adapt to market regime changes

5. **Build Statistical Confidence:**
   - After 20+ samples per catalyst: High confidence in what works
   - Track calibration: Are our predictions accurate?
   - Test hypotheses systematically

### The Learning Loop:
```
Trade → Document → Analyze → Learn → Refine → Apply Learnings → Better Trade
```

**This compounds over time. Week 1 decisions < Week 4 decisions < Week 12 decisions.**

---

## 📁 FILE STRUCTURE & PURPOSE

```
/paper_trading_lab/
├── PROJECT_INSTRUCTIONS.md          ← This file (the system blueprint)
│
├── /portfolio_data/
│   ├── current_portfolio.json       ← Live: 10 active positions with all details
│   └── account_status.json          ← Current account value, streaks, stats
│
├── /daily_reviews/
│   ├── 2025-10-27_morning.md        ← Daily: Morning analysis & actions
│   ├── 2025-10-27_evening.md        ← Daily: Evening update & learnings
│   └── ...
│
├── /trade_history/
│   ├── completed_trades.csv         ← Every closed position with full data
│   └── trade_journal.md             ← Detailed notes on key trades
│
├── /strategy_evolution/
│   ├── lessons_learned.md           ← Updated continuously: What works/doesn't
│   ├── catalyst_performance.csv     ← Stats by catalyst type
│   ├── hypothesis_testing.md        ← Active experiments being run
│   └── strategy_rules.md            ← Current ruleset (evolves over time)
│
└── /analysis_reports/
    ├── weekly_review_YYYY-WW.md     ← Weekly: Comprehensive analysis
    └── monthly_summary_YYYY-MM.md   ← Monthly: Big picture performance
```

---

## 🎯 SUCCESS METRICS

### Primary Goal:
**Learn to identify high-probability trading setups through systematic analysis**

### Secondary Goals:
- Achieve 55-65% win rate over 30+ trades
- Positive cumulative return over 3 months
- Build statistical confidence in proven patterns

### NOT the Goal:
- "Get rich quick"
- Beat professional traders
- Find a "perfect system"

---

## 📈 EXPECTED PROGRESSION

**Week 1 (Days 1-5):**
- Establish initial portfolio
- Test various Tier 1 catalysts
- Gather baseline data
- Expected: -5% to +5% (high variance)

**Weeks 2-4:**
- First pattern recognition
- Drop low-performing setups
- Focus on proven catalysts
- Expected: +2-5% (learning phase)

**Month 2:**
- Refined catalyst selection
- Optimized entry/exit timing
- Statistical confidence building
- Expected: +5-8% (improvement)

**Month 3+:**
- High-confidence system
- Consistent edge identified
- Repeatable process
- Expected: +8-12% (mature strategy)

---

## ⚠️ CRITICAL DISCLAIMERS

**MUST READ:**

- This is **PAPER TRADING ONLY** - no real money at risk
- Results are **SIMULATED** and don't reflect real trading conditions
- This is for **EDUCATIONAL PURPOSES ONLY**
- **NOT financial advice** or recommendation to buy/sell securities
- Real trading involves commissions, slippage, execution risk, and emotions
- Past performance does not guarantee future results
- The AI (Claude) is not a licensed financial professional
- Always consult a licensed financial advisor before real trading
- Never invest more than you can afford to lose

---

## 🚀 GETTING STARTED

**On Monday, October 27, 2025 at 8:45 AM:**

User types: **"Go"**

Claude will:
1. Execute comprehensive research (20+ searches)
2. Find 10 best Tier 1 catalyst opportunities
3. Build initial portfolio with detailed rationale
4. Document everything in daily_reviews/
5. Provide clear action summary

**Then each day:**
- Morning: "Go" command → Review + Trading decisions
- Evening (optional): "analyze" command → Update + Learning extraction

---

## 🎓 KEY PRINCIPLES

1. **Discipline > Emotion:** Follow stops religiously
2. **Data > Opinion:** Let results guide strategy
3. **Learning > Winning:** Process matters more than individual outcomes
4. **Patience > Action:** Not every day requires trades
5. **Quality > Quantity:** 10 great positions > 20 mediocre ones

---

## 🔧 SYSTEM MAINTENANCE

Claude will automatically:
- ✅ Read previous learnings before each decision
- ✅ Update all tracking files daily
- ✅ Identify emerging patterns
- ✅ Propose strategy refinements based on data
- ✅ Track statistical confidence in each catalyst type
- ✅ Adapt to changing market conditions

User needs to:
- ✅ Issue "Go" command each morning
- ✅ (Optional) Issue "analyze" command each evening
- ✅ Trust the process over 30+ days minimum

---

## 📊 WHAT MAKES THIS DIFFERENT

**Traditional approach:**
- Pick stocks randomly or based on hunches
- No systematic tracking
- No learning from mistakes
- Repeat same errors indefinitely

**Our approach:**
- Strict Tier 1 catalyst criteria
- Document every single decision
- Analyze what works/doesn't work
- Build statistical edge over time
- Continuously refine based on data
- System gets smarter every day

**This is how professional traders operate.**

---

**Version:** 1.0  
**Last Updated:** October 24, 2025  
**Next Review:** After Week 1 (November 1, 2025)

---

*Let's build something that actually works.* 🚀
