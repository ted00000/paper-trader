# Tedbot Improvement Parking Lot

**Purpose**: Track deferred/skipped improvements for future consideration

**Last Updated**: December 1, 2024

---

## 🎯 Institutional-Grade Roadmap (From Third-Party Review - Dec 2024)

**Context**: Third-party reviewer assessed Tedbot as "institutional-style" but not yet "institutional-grade" for serious capital deployment. Below are remaining gaps to cross that threshold.

**Current Status**: Phase 4 + Institutional Enhancements completed!
- ✅ Market breadth filter (4.2) - They wanted this, we built it
- ✅ Liquidity constraints (4.4) - They wanted this, we built it
- ✅ Cluster-based conviction (4.1) - They wanted this, we built it
- ✅ Sector concentration reduction (4.3) - Exceeds their ask
- ✅ VIX regime logging (Enhancement 4.5) - Tracks VIX regimes for learning & attribution
- ✅ AI robustness & failover (Enhancement 4.6) - Graceful degradation when Claude API fails
- ✅ Operational monitoring (Enhancement 4.7) - Health checks, alerting, version tracking

### ✅ COMPLETED: AI Robustness & Failover (Enhancement 4.6)
**Status**: ✅ IMPLEMENTED (Dec 1, 2024)
**Reviewer concern**: "What happens when the LLM goes sideways one day?"
**What it is**: Fallback logic when Claude API fails, times out, or returns unexpected output

**Implementation**:
1. **Degraded Mode - GO Command**:
   - If Claude API fails → HOLD all existing positions, skip all new entries
   - Clear console messaging about degraded mode
   - Logs failure to `logs/claude_api_failures.json`
   - Automatic retry on next GO command
2. **Degraded Mode - ANALYZE Command**:
   - If Claude API fails → Skip daily commentary, core operations already completed
   - All position exits/holds already processed before Claude call
   - Minimal impact: only missing performance analysis text
3. **Failure Logging**:
   - Timestamp, command, error type, error message
   - Action taken (skipped entries, held positions)
   - Enables monitoring and troubleshooting

**Effort**: 2.5 hours (actual)
**Cost**: $0
**Impact**: Institutional-grade robustness, no single point of failure
**Risk mitigation**: Prevents catastrophic trades if Anthropic has outage

**Result**: System can now operate safely even when Claude API is unavailable

---

### ✅ COMPLETED: Operational Monitoring & Health Checks (Enhancement 4.7)
**Status**: ✅ IMPLEMENTED (Dec 1, 2024)
**Reviewer concern**: "Institutions care about monitoring, alerting, change management"
**What it is**: Automated system monitoring with health checks, alerting, and version tracking

**Implementation**:
1. **Health Checks** (`health_check.py`):
   - Command execution monitoring (GO/EXECUTE/ANALYZE ran today?)
   - API connectivity tests (Polygon, Anthropic reachable?)
   - Data freshness validation (screener updated in 24 hours?)
   - Active positions monitoring (count, average P&L)
   - Claude API failure detection (from logs/claude_api_failures.json)
   - Disk space monitoring (alerts when low)
2. **Alerting System**:
   - Discord webhook integration (optional, configured via .env)
   - Color-coded alerts: Red (critical), Orange (warnings), Green (healthy)
   - Daily health report with system stats
   - Exit codes: 0 (healthy), 1 (issues detected)
3. **Version Tracking**:
   - Added SYSTEM_VERSION constant to agent_v5.5.py (v5.6)
   - System_Version column added to CSV exports
   - Every trade tagged with code version that generated it
   - Enables correlation of performance changes with code updates
4. **Deployment Tools**:
   - setup_monitoring.sh: Automated setup script
   - Configures cron jobs for daily 5pm ET health checks
   - Logs saved to logs/health_check.log

**Effort**: 4 hours (actual)
**Cost**: $0
**Impact**: Professional-grade operations, catch issues early
**Result**: Complete institutional-grade monitoring system with automated daily health checks

---

### Priority 1: Dashboard Health Monitoring & Performance Display (CRITICAL FOR MARKETING)
**Status**: Health checks running, need dashboard integration
**Reviewer concern**: "Without 6-12 months live results, can't claim 'best-in-class'" + operational transparency

**Implementation**:
1. **Admin Dashboard - System Health Tab** (3-4 hours):
   - Real-time health status display (pulls from health_check.py)
   - Last command execution times (GO/EXECUTE/ANALYZE)
   - API status indicators (Polygon, Anthropic)
   - Data freshness indicators
   - Active positions count + P&L
   - Disk space usage
   - Recent Claude API failures (if any)
   - Replace Discord webhook with dashboard alerts

2. **Public Model Portfolio Tab** (4-6 hours):
   - Dashboard card showing YTD/MTD performance
   - Win rate, avg gain/loss, max drawdown, Sharpe
   - Trade count, conviction distribution
   - Updated daily at 5pm ET

3. **Performance History** (2-3 hours):
   - Monthly snapshots saved to JSON
   - Performance across different regimes (VIX <20, 20-30, >30)
   - Sector attribution (which sectors performed best)

4. **Out-of-Sample Results** (ongoing):
   - Run system for 6-12 months without tweaking
   - Document all regime changes (bull, bear, chop)
   - Prove consistency across market conditions

**Effort**: 9-13 hours initial build, then ongoing data collection
**Cost**: $0
**Expected impact**: **REQUIRED** for subscription product credibility + operational transparency
**Timeline**: Dashboard updates NOW, then let it run for 6+ months

**When to implement**: Dashboard updates THIS WEEK, then let system build track record

---

### Priority 2: Retail Safety Wrapper (MEDIUM PRIORITY)
**Status**: Not implemented
**Reviewer concern**: "Average user could blow themselves up with wrong settings"

**Implementation**:
1. **Risk Modes** (3-4 hours):
   - **Conservative**: 0.6x position sizing multiplier, VIX <25 only
   - **Standard**: 1.0x (current behavior)
   - **Aggressive**: 1.2x, allows VIX 25-30 trades
2. **Portfolio-Level Stops** (2-3 hours):
   - Max daily loss: -3% portfolio → stop trading for the day
   - Max drawdown: -10% from peak → email alert, manual review required
3. **Capital Allocation Limits** (1 hour):
   - Default: System only trades 30% of account (protect capital)
   - User can adjust 20-50% range
   - Hard cap: Never exceed 50% account deployed

**Effort**: 6-8 hours
**Cost**: $0
**Expected impact**: Prevent user misconfigurations, reduce support burden
**When to implement**: Before public beta launch (3-6 months)

---

### Priority 3: Slippage Modeling & Cost Assumptions (LOW PRIORITY)
**Status**: Not explicitly modeled
**Reviewer concern**: "Model at least 0.2-0.5% slippage per trade in backtests"

**Current reality**:
- ✅ We filter for $20M+ daily volume (Phase 4.4)
- ✅ Typical slippage on liquid names: 0.1-0.3%
- ❌ Not explicitly modeled in P&L calculations

**Implementation**:
1. Add slippage assumption to trade logging (0.25% per trade)
2. Adjust reported returns by -0.5% per round trip (in/out)
3. Document assumptions in performance reports

**Effort**: 1-2 hours
**Cost**: $0
**Expected impact**: More conservative/realistic performance reporting
**When to implement**: Before publishing official track record (6+ months)

---

## Phase 4 Deferred Items (From Third-Party Review)

### 1. Forward Guidance Delta Tracking
**Status**: Deferred (requires paid API tier or manual parsing)
**What it solves**: AI can misinterpret guidance nuance (e.g., "guidance raised" vs "guidance maintained")
**Current solution**: We check "revenue beat" confirmation, but don't track guidance delta
**Full implementation**:
- Track guidance changes (raised/maintained/lowered)
- Add +1 conviction factor for "guidance raised"
- Requires either:
  - FMP Pro tier ($29/month) for detailed transcripts
  - Manual parsing of earnings transcripts (high maintenance)

**Partial implementation (DONE)**: We already check EPS surprise + revenue surprise, which catches most strong earnings
**Effort**: 2 hours (if using FMP Pro), 8+ hours (if manual parsing)
**Cost**: $29/month (FMP Pro) or $0 (manual)
**Expected impact**: +2-3% better earnings trade quality

**When to revisit**: If we see pattern of earnings beat trades failing due to guidance misses

---

### 2. Advanced Fundamental Filters
**Status**: Deferred (requires paid tier)
**What it would add**:
- Gross margin stability check
- EPS acceleration (YoY growth rate)
- Free cash flow trends

**Current reality**:
- ✅ We already check EPS surprise & revenue surprise (FMP free)
- ❌ Don't have margin, cash flow, or acceleration data

**Why deferred**:
- FMP free tier only provides surprise data
- Full fundamentals require Pro tier ($29/month)
- Our catalyst-driven strategy cares more about events than financials

**Effort**: 4 hours
**Cost**: $29/month (FMP Pro)
**Expected impact**: +3-5% trade quality (avoid value traps)

**When to revisit**: If we see pattern of trades failing on weak fundamentals despite catalyst

---

### 3. Position Sizing Aggressiveness Review
**Status**: MONITORING (no immediate action)
**Concern**: 13% position size = 0.91% portfolio loss per stop
**Current risk**: 3-5 correlated stops = -2.7% to -4.5% daily drawdown
**Mitigation already in place**:
- ✅ Sector concentration limited to 2 positions (Phase 4.3)
- ✅ Leading sector exception allows 3 only in top 2 sectors
- ✅ Market breadth filter reduces sizing in DEGRADED/UNHEALTHY markets
- ✅ Liquidity filter prevents slippage on low-volume names

**Action**: Monitor correlation of stops over next 30 days
**Trigger**: If >2 stops hit same day more than 2x per month, reduce HIGH conviction from 13% → 12%

**When to revisit**: After 30 days of Phase 4 data

---

### 4. Discord Webhook Integration (OPTIONAL)
**Status**: Infrastructure ready, deferred in favor of dashboard
**What it is**: Send health check alerts to Discord channel instead of dashboard

**Current approach**:
- health_check.py has Discord webhook support built-in
- Currently not configured (no DISCORD_WEBHOOK_URL in environment)
- Dashboard integration preferred for operational transparency

**If implemented**:
- Set DISCORD_WEBHOOK_URL in server environment
- Color-coded alerts: Red (critical), Orange (warnings), Green (healthy)
- Daily 5pm ET health reports sent to Discord channel

**Effort**: 5 minutes (just set environment variable)
**Cost**: $0 (Discord webhooks are free)
**Expected impact**: Mobile alerts for critical issues
**Priority**: LOW (dashboard is better for admin monitoring)

**When to revisit**: If user wants mobile push notifications for system issues

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
