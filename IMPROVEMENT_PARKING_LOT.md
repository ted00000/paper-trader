# Tedbot Improvement Parking Lot

**Purpose**: Track deferred/skipped improvements for future consideration

**Last Updated**: November 29, 2024

---

## High-Priority Deferred Items (Revisit Soon)

### 1. Industry Group Strength Analysis (Phase 3.4)
**Status**: Skipped during Phase 3 implementation
**Reason**: Added complexity without proportional value given Phase 3.1-3.3 already implemented
**What it would do**:
- Drill down from sector (11 categories) to industry group (~100+ groups)
- Example: Technology → Software, Semiconductors, Hardware, etc.
- Identify strongest industry groups within leading sectors
- Target stocks from top-performing industry groups

**Implementation approach**:
- Use Polygon SIC codes to map stocks to industry groups
- Track industry group performance (average stock returns)
- Add industry_group field to candidate output
- Display top 3 performing industry groups in scan summary

**Effort**: 4-6 hours
**Cost**: $0 (uses existing Polygon data)
**Expected impact**: +5-10% better stock selection (focus on hot industries)

**When to revisit**: After 2-3 months of Phase 3 data to validate value

---

## Revenue & Earnings Enhancements

### 2. Revenue Surprise Data (Complete for Top Stocks)
**Status**: Partially implemented (FMP free tier, 250 calls/day limit)
**Current limitation**: Can only check revenue for ~125 stocks per day (2 API calls each)
**Gap**: Large universe scans (1000+ stocks) hit API limit

**Paid upgrade option**:
- FMP Professional: $29/month, 10,000 calls/day
- Would cover all 1500 stocks (3,000 calls total)

**Alternative**: Selective revenue checking
- Only check revenue for stocks that already passed other filters
- Check top 200 candidates by composite score
- Keeps within 250 call limit

**When to revisit**: If revenue beats become critical missing factor

### 3. Whisper Numbers (Beat Consensus but Miss Whisper)
**Status**: Not implemented
**What it solves**: Stocks that "beat estimates" but disappoint because they missed whisper numbers
**Data sources**:
- WhisperNumber.com (paid, ~$50-100/month)
- Estimize (paid, ~$100-200/month)

**Effort**: 2-3 hours integration
**Cost**: $50-200/month
**Expected impact**: Avoid 5-10% of "false positive" earnings beats

**When to revisit**: If we see pattern of earnings beat trades failing

### 4. Pre-Earnings Entry Strategy
**Status**: Deferred
**What it does**: Position 2-5 days before known earnings dates
**Current capability**: Have earnings calendar API (get_earnings_calendar()), not using it for entries

**Strategy**:
- Identify stocks with earnings in 2-5 days
- Check if strong technical setup (Stage 2, RS 80+, volume)
- Enter small position (4% vs 8% normal size)
- Exit immediately after earnings (win or lose)

**Risk**: High volatility, potential gaps down
**Effort**: 6-8 hours (strategy logic + risk management)
**Cost**: $0 (already have earnings calendar)
**Expected impact**: +3-5 extra trades per month, higher volatility

**When to revisit**: Once base trading strategy is proven profitable

---

## News & Catalyst Improvements

### 5. Real-Time News Feed (vs 7-Day Lookback)
**Status**: Deferred (costly)
**Current approach**: Polygon news API with 7-day lookback
**Gap**: Miss same-hour catalyst announcements

**Paid options**:
- Benzinga News API: $99/month (real-time news feed)
- NewsAPI Premium: $449/month (multiple sources)

**What it enables**:
- Detect catalysts within minutes of announcement
- Enter positions same-day before price runs
- Higher win rate on news-driven trades

**Effort**: 4-6 hours (streaming integration)
**Cost**: $99-449/month
**Expected impact**: +10-15% earlier entries on catalyst trades

**When to revisit**: If missing obvious catalyst opportunities due to delay

### 6. PDUFA Calendar Tracking (FDA Decision Dates)
**Status**: Deferred (manual effort)
**What it does**: Track known FDA decision dates (PDUFA dates) for biotech stocks
**Current approach**: Detect FDA approvals after-the-fact via news

**Manual implementation**:
- Subscribe to BiopharmCatalyst.com (free calendar)
- Manually input upcoming PDUFA dates into system
- Flag biotech stocks with PDUFA in next 30 days

**Automated option**:
- BiopharmCatalyst API (paid, custom pricing)

**Effort**: 2-3 hours/month (manual updates) OR 8-10 hours (API integration)
**Cost**: $0 (manual) OR $200+/month (API)
**Expected impact**: +2-4 biotech trades per month

**When to revisit**: If biotech sector becomes hot (leading sector)

### 7. Advanced SEC Filing Monitor (Beyond 8-K)
**Status**: Deferred
**Current approach**: Monitor 8-K filings for M&A and major contracts
**Gap**: Missing other filing types with catalysts

**Additional filings to monitor**:
- S-1 (IPO registration)
- 13D/13G (activist investor stakes >5%)
- Form 4 (insider cluster buying - already have)
- 10-Q amendments (restatements, accounting changes)

**Implementation**:
- Expand SEC EDGAR API queries
- Parse additional filing types
- Add catalyst detection rules

**Effort**: 12-16 hours
**Cost**: $0 (SEC EDGAR is free)
**Expected impact**: +5-8% more Tier 1 catalysts detected

**When to revisit**: After current catalyst detection is validated

---

## Technical & Timing Improvements

### 8. Options Flow Data (Institutional Sentiment)
**Status**: Deferred (expensive)
**What it provides**: Unusual options activity (large call/put sweeps)
**Use case**: Confirm institutional interest before entry

**Data sources**:
- Unusual Whales: $50/month (basic)
- FlowAlgo: $200/month (professional)
- Polygon Options API: Already included in free tier!

**Polygon approach** (FREE):
- Use Polygon /v3/snapshot/options/{ticker}
- Track call/put volume ratio
- Detect unusual volume spikes
- Flag bullish options activity

**Effort**: 6-8 hours (Polygon integration)
**Cost**: $0 (use existing Polygon free tier)
**Expected impact**: +10-15% conviction on entries

**When to revisit**: HIGH PRIORITY - This is free! Should implement next

### 9. Dark Pool Activity Tracking
**Status**: Deferred
**What it shows**: Large institutional block trades (>10,000 shares)
**Use case**: Detect accumulation by smart money

**Data sources**:
- QuoteMedia Dark Pool API: $300+/month
- Polygon Trades API: Already included! (can filter by exchange)

**Polygon approach** (FREE):
- Filter trades by exchange code 'D' (dark pools)
- Calculate dark pool volume ratio
- Flag stocks with >30% dark pool volume

**Effort**: 4-6 hours
**Cost**: $0 (use existing Polygon)
**Expected impact**: +5-10% better entries (follow smart money)

**When to revisit**: MEDIUM PRIORITY - Free data available

---

## Risk Management & Position Sizing

### 10. Volatility-Adjusted Position Sizing
**Status**: Deferred
**Current approach**: Fixed 8% position size for all trades
**Gap**: High-volatility stocks get same size as low-volatility

**What it does**:
- Calculate ATR (Average True Range) for each stock
- Reduce position size for high-volatility stocks
- Example: 8% for low-vol, 4% for high-vol

**Effort**: 2-3 hours
**Cost**: $0 (calculate from price data)
**Expected impact**: -10-15% portfolio volatility, smoother equity curve

**When to revisit**: After 20+ trades to assess volatility impact

### 11. Correlation-Based Position Limits
**Status**: Deferred
**What it prevents**: Overconcentration in correlated stocks
**Current gap**: Could hold 3 semiconductor stocks simultaneously (highly correlated)

**Implementation**:
- Calculate correlation matrix for current holdings
- Limit to 2 stocks with >0.7 correlation
- Diversify across sectors/industries

**Effort**: 6-8 hours
**Cost**: $0
**Expected impact**: -15-20% portfolio risk (better diversification)

**When to revisit**: After portfolio grows to 5+ positions

---

## Backtesting & Performance Tracking

### 12. Full Historical Backtesting Engine
**Status**: Deferred
**Current approach**: Paper trading (forward testing only)
**Gap**: Can't validate strategies on historical data

**What it requires**:
- Historical price data (Polygon has this, free)
- Historical news/catalyst data (expensive: $500+/month for Benzinga historical)
- Simulate entries/exits on past data
- Calculate historical win rate, Sharpe ratio, max drawdown

**Effort**: 40-60 hours (major project)
**Cost**: $0 (price only) OR $500+/month (with news history)
**Expected impact**: Validate strategies, optimize parameters

**When to revisit**: After 50+ paper trades to compare vs historical

### 13. Trade Attribution Analysis
**Status**: Deferred
**What it shows**: Which factors drive winning vs losing trades
**Questions to answer**:
- Do Tier 1 catalysts outperform Tier 2?
- Does RS 90+ beat RS 80-90?
- Do leading sector stocks win more often?

**Implementation**:
- Tag each trade with all factors (catalyst tier, RS percentile, sector, etc.)
- Calculate win rate by factor
- Identify which factors matter most

**Effort**: 8-10 hours
**Cost**: $0
**Expected impact**: Refine entry criteria, boost win rate by 5-10%

**When to revisit**: After 30+ trades

---

## Machine Learning & Advanced Analytics

### 14. Catalyst NLP Sentiment Analysis
**Status**: Deferred (advanced)
**Current approach**: Keyword matching for catalysts
**Gap**: Miss context, can't detect sentiment nuance

**What it would do**:
- Use NLP (Natural Language Processing) to analyze news sentiment
- Detect "strong buy" vs "cautious buy" tone
- Score conviction level (1-10) from article text

**Tools**:
- OpenAI GPT-4 API: $0.03 per 1K tokens (~$5-10/month for screening)
- Hugging Face FinBERT: Free sentiment model

**Effort**: 16-20 hours (ML integration)
**Cost**: $5-10/month (GPT-4) OR $0 (FinBERT)
**Expected impact**: +5-8% accuracy in catalyst detection

**When to revisit**: After validating keyword-based approach works

### 15. Predictive Win Rate Model
**Status**: Deferred (requires data)
**What it does**: Predict probability of +8% gain before entry
**Inputs**: All current factors (RS, catalyst, sector, volume, etc.)
**Output**: Win probability (0-100%)

**Approach**:
- Collect 100+ historical trades with outcomes
- Train ML model (logistic regression or random forest)
- Score new candidates by predicted win rate
- Only enter trades with >60% win probability

**Effort**: 20-30 hours
**Cost**: $0
**Expected impact**: +10-15% win rate improvement

**When to revisit**: After 100+ completed trades

---

## Infrastructure & Automation

### 16. Real-Time Alert System
**Status**: Deferred
**What it does**: Send notifications when new candidates appear
**Current gap**: Must manually run screener

**Implementation options**:
- Email alerts via SendGrid API (free tier: 100 emails/day)
- SMS alerts via Twilio ($0.0075 per SMS)
- Discord webhook (free)

**Triggers**:
- New Tier 1 catalyst detected
- Stock enters RS 95+ (top 5%)
- Leading sector rotation detected

**Effort**: 4-6 hours
**Cost**: $0-$5/month
**Expected impact**: Faster reaction time, don't miss opportunities

**When to revisit**: Once daily screening is stable

### 17. Auto-Execution (No Human Approval)
**Status**: Deferred (risky)
**Current approach**: Claude recommends → Human approves → Execute
**Proposed**: Claude auto-executes if criteria met

**Safety requirements**:
- Max position size limits (8% hard cap)
- Max daily trades (2 per day)
- Emergency stop if portfolio down >10%
- Human review weekly

**Effort**: 8-10 hours (safety logic)
**Cost**: $0
**Risk**: HIGH (bugs could cause losses)
**Expected impact**: Faster execution, remove emotional bias

**When to revisit**: After 100+ successful paper trades

---

## Summary by Priority

### 🔥 High Priority (Revisit in 1-3 months)
1. ✅ **Options Flow Data (Polygon)** - FREE, high impact - COMPLETED
2. Industry Group Strength Analysis - FREE, moderate impact
3. ✅ **Dark Pool Activity Tracking (Polygon)** - FREE, moderate impact - COMPLETED

### 🟡 Medium Priority (Revisit in 3-6 months)
4. Trade Attribution Analysis - Optimize existing strategy
5. Pre-Earnings Entry Strategy - Tactical enhancement
6. Volatility-Adjusted Position Sizing - Risk management

### 🔵 Low Priority (Revisit after 6+ months)
7. Revenue Surprise Upgrade (FMP Pro)
8. Real-Time News Feed (Benzinga)
9. Full Historical Backtesting Engine
10. PDUFA Calendar Tracking

### 💰 Expensive / Not Worth It (Unlikely to implement)
11. Whisper Numbers ($50-200/month) - Marginal value
12. NewsAPI Premium ($449/month) - Too expensive
13. Predictive ML Model - Requires 100+ trades first

---

## Decision Framework: When to Implement

**Ask these questions before implementing any parking lot item**:

1. **Is it free?** → Prioritize free improvements first
2. **What's the expected impact?** → Focus on >5% win rate or >10% better selection
3. **Do we have enough data?** → ML/backtesting requires 50-100+ trades
4. **What's the risk?** → Avoid auto-execution until proven safe
5. **Is it a bottleneck?** → Only fix pain points (e.g., missing catalysts)

**Current recommendation**: ~~Focus on **Options Flow Data** next (free, high impact, easy to implement)~~ **COMPLETED: Options Flow & Dark Pool Activity implemented!**

Next recommendation: Consider **Industry Group Strength Analysis** (Parking Lot #2) after validating Phase 3 results.

---

**Maintained by**: Tedbot Development Team
**Review Cadence**: Monthly
