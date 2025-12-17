# Tedbot Improvement Parking Lot

**Purpose**: Track deferred/skipped improvements for future consideration

**Last Updated**: December 2, 2024

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
- ✅ Public model portfolio display (Enhancement 4.8) - Dashboard performance metrics & regime analysis

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

### ✅ COMPLETED: Public Model Portfolio Display (Enhancement 4.8)
**Status**: ✅ IMPLEMENTED (Dec 1, 2024)
**Reviewer concern**: "Without 6-12 months live results, can't claim 'best-in-class'" + operational transparency
**What it is**: Public-facing portfolio performance metrics on admin dashboard

**Implementation**:
1. **Admin Dashboard - System Health Integration** (completed):
   - Real-time health status display (pulls from health_check.py)
   - Last command execution times (GO/EXECUTE/ANALYZE)
   - API status indicators (Polygon, Anthropic)
   - Data freshness indicators
   - Active positions count + P&L
   - Disk space usage
   - Recent Claude API failures (if any)
   - Dashboard alerts replace Discord webhook approach

2. **Public Model Portfolio Tab** (completed):
   - YTD/MTD returns with color-coded display (green=profit, red=loss)
   - Total trades, win rate percentage
   - Average gain/loss per trade
   - Max drawdown calculation
   - Sharpe ratio (annualized, assuming ~50 trades/year)
   - Conviction distribution (HIGH/MEDIUM/LOW trade counts)
   - Auto-refresh every 5 minutes

3. **Performance by Market Regime** (completed):
   - VIX regime performance (5 levels: VERY_LOW, LOW, ELEVATED, HIGH, EXTREME)
   - Market breadth regime analysis (HEALTHY/DEGRADED/UNHEALTHY)
   - Top 5 sector performance attribution
   - Trade count, avg return %, win rate per regime
   - Color-coded cards for visual clarity

4. **Backend API Endpoints** (completed):
   - `/api/portfolio/performance` - Main performance metrics
   - `/api/portfolio/regime-performance` - Regime & sector analysis
   - Uses numpy for statistical calculations
   - Real-time CSV parsing from completed_trades.csv

**Effort**: 5 hours (actual)
**Cost**: $0
**Impact**: Complete transparency, enables 6-12 month track record building
**Result**: Dashboard now shows comprehensive performance metrics, ready for public demonstration

**Next Step**: Out-of-Sample Results Collection (ongoing - 6-12 months)
- Run system without code tweaking
- Document regime changes (bull, bear, chop)
- Prove consistency across market conditions
- Build credible track record for subscription product

---

### Priority 1: Out-of-Sample Results Collection (CRITICAL FOR MARKETING)
**Status**: ✅ CODE FROZEN AT v6.0 - Results collection started Dec 2, 2024
**Reviewer concern**: "Without 6-12 months live results, can't claim 'best-in-class'"

**Requirements**:
- Run system for 6-12 months without tweaking code
- Document all market regime changes encountered
- Prove consistency across different market conditions
- Maintain detailed trade logs with regime data

**Timeline**: Dec 2, 2024 - Jun/Dec 2025 (6-12 months minimum)
**Effort**: Ongoing monitoring, no code changes

---

## Priority 1 (v7.0): Post-v6.0 Validation & Simplification

**Status**: DEFERRED until v6.0 results collection completes (50+ trades minimum)
**Source**: Third-party analysis (Dec 2, 2024) - See [THIRD_PARTY_ANALYSIS_v6.0.md](THIRD_PARTY_ANALYSIS_v6.0.md)
**Key Finding**: Complexity (26 enhancements) is highest risk factor (8/10 overfitting risk)
**Goal**: Validate which features drive edge, simplify by 30-50% if possible

### 1A. Ablation Testing Framework (CRITICAL - v7.0)
**Issue**: 26 enhancements across 5 phases = too many knobs, unclear which drive edge
**Risk**: 8/10 that system is more complex than realized edge justifies
**Proposed Solution**:
- Systematically remove feature families one at a time, measure performance degradation
- Test scenarios:
  - Remove momentum cluster (RS, sector strength) → measure impact
  - Remove institutional cluster (options flow, dark pool) → measure impact
  - Remove volume quality filters → measure impact
  - Remove timing filters (entry quality, gap-aware) → measure impact
  - Remove technical score → measure impact
- **Target**: Kill 30-50% of complexity if features don't significantly improve out-of-sample results
**Data Required**: 50+ trades minimum from v6.0 results collection
**Analyst's Words**: "Be willing to kill 30-50% of the complexity if it doesn't significantly improve out-of-sample results"
**Effort**: 3-5 days (after v6.0 completes)
**Impact**: Simplification = reduced overfitting risk + easier to explain edge

### 1B. LLM Contribution Analysis (CRITICAL - v7.0)
**Issue**: Heavy dependence on Claude for news validation, GO decisions, exit reviews
**Risk**: Can't isolate whether edge comes from rules vs LLM's behavior (7/10 risk)
**Concerns**:
- Model updates could alter behavior even if code is frozen
- Edge source unclear: rules vs LLM's evolving behavior?
- Single external cognitive dependency
**Proposed Solution**:
- Build simple baseline model (logistic regression or decision tree) on same features Claude sees
- Test: "Can it reproduce 80% of Claude's edge with 20% of complexity?"
- Run some days purely rules-based (no LLM news scoring) to quantify Claude's contribution
**Target**: Quantify LLM's marginal edge contribution in basis points
**Data Required**: 50+ trades with full feature snapshots from v6.0
**Analyst's Words**: "Store structured numeric feature snapshot to test if simple model reproduces edge. Gradually move LLM into overlay/exception handler."
**Effort**: 2-3 days (after v6.0 completes)
**Impact**: Understand if edge is rules-based (durable) vs LLM-based (fragile)

### 1C. Pre-Defined Success/Failure Metrics (CRITICAL - Define NOW)
**Issue**: Targets stated (65-70% win rate) but decision criteria unclear
**Risk**: Without pre-defined metrics, might rationalize bad results or change goal posts
**Proposed Solution**: Define NOW what metrics trigger keep/simplify/retire decisions

**DECISION CRITERIA** (defined Dec 2, 2024):
- **KEEP v6.0 AS-IS**:
  - Win rate ≥60%
  - Sharpe ratio ≥1.0
  - Max drawdown ≤-20%
  - Minimum 50 trades
  - **Conclusion**: System works, continue with v6.0 logic

- **SIMPLIFY TO v7.0**:
  - Win rate 50-60%
  - Sharpe ratio 0.5-1.0
  - Max drawdown -20% to -30%
  - Minimum 50 trades
  - **Conclusion**: Edge exists but complexity hurts, do ablation testing to find core 50%

- **RETIRE/REDESIGN**:
  - Win rate <50%
  - Sharpe ratio <0.5
  - Max drawdown >-30%
  - **Conclusion**: No edge detected, fundamental rethink required

**Action**: Document criteria NOW, apply after v6.0 results collection completes
**Analyst's Words**: "Pre-define what metrics would make you keep, simplify, or retire the system"
**Effort**: 0 hours (decision made)
**Impact**: Rigorous evaluation framework prevents rationalization

### 1D. Slippage Modeling (HIGH PRIORITY - v7.0)
**Issue**: Paper trading assumes perfect fills, real trading has spreads and market impact
**Risk**: Edge may disappear under realistic execution costs (7/10 risk)
**Current Assumption**: Entry at exact market price, exit at exact price (0% slippage)
**Realistic Assumption**: Entry at mid + 0.5-1% spread, exit at mid - 0.5-1% spread (1% round-trip drag)
**Proposed Solution**:
- Add estimated slippage to all v6.0 trades in post-analysis (assume 0.5% each side = 1% total)
- If edge survives -1% drag, confidence increases significantly
- Track VWAP vs actual fills when live trading starts
- Build market impact model (position size / ADV ratio)
**Target**: Validate edge exists after realistic execution costs
**Data Required**: v6.0 trade history with entry/exit prices
**Analyst's Words**: "Simulate realistic slippage & spread in analytics (e.g., entry at mid + 0.5-1 spread). If edge survives, confidence goes way up."
**Effort**: 1 day (post-analysis after v6.0)
**Impact**: Realistic performance expectations for live trading

### 1E. Walk-Forward & Monte Carlo Analysis (HIGH PRIORITY - v7.0)
**Issue**: Single equity curve doesn't prove robustness
**Risk**: Lucky trade sequence could mask fragility (7/10 risk)
**Proposed Solution**:
- **Walk-Forward Analysis**: Divide v6.0 results into quarters, verify consistency
  - Q1 (trades 1-N/4): Calculate Sharpe, DD, win rate
  - Q2 (trades N/4 to N/2): Calculate same metrics
  - Q3, Q4: Same
  - Test: Are metrics consistent across quarters?
- **Monte Carlo Simulation**: Randomize trade order 10,000x to estimate drawdown distribution
  - Use actual v6.0 trade returns
  - Shuffle order randomly
  - Calculate max DD for each sequence
  - Result: 95th percentile expected DD (worst realistic case)
**Target**: Prove results aren't sequence-dependent
**Data Required**: 50+ trades from v6.0
**Analyst's Words**: "Walk-forward curves over multiple distinct time slices. Simulated drawdowns under randomized trade order."
**Effort**: 1-2 days (after v6.0)
**Impact**: Confidence in system robustness vs lucky sequence

### 1F. Sensitivity Analysis Framework (MEDIUM PRIORITY - v7.0)
**Issue**: Don't know which parameter changes break the system
**Proposed Solution**: Test edge sensitivity to parameter changes
- **Stop width variations**: -5%, -7%, -10% → measure impact on win rate, avg loss, Sharpe
- **Catalyst tier variations**: Tier 1 only vs Tier 1+2 → measure trade frequency, win rate, returns
- **Conviction threshold variations**: Skip <3 factors vs <2 factors vs <4 factors → measure impact
- **Market breadth sizing**: Current (1.0x / 0.8x / 0.6x) vs more aggressive (1.0x / 0.9x / 0.7x) → measure DD impact
**Target**: Identify fragile parameters vs robust parameters
**Data Required**: v6.0 trade history
**Analyst's Words**: "Sensitivity analysis: what if you widen/tighten stops, or trade only Tier 1 vs Tier 1+2 catalysts?"
**Effort**: 2-3 days (after v6.0)
**Impact**: Know which parameters are critical vs arbitrary

---

## Priority 2 (v7.0): Feature Enhancements - LOWER PRIORITY

**Status**: DEFERRED until after Priority 1 validation completes
**Rationale**: Third-party analysis recommends simplification before adding features

### 2A. ATR-Based Stops (MEDIUM PRIORITY - v7.0)
**Issue**: Fixed -7% stops don't account for volatility differences across stocks
**Risk**: False stops on volatile names (6/10 risk)
**Current**: Universal -7% stop (or -5% for gaps)
**Proposed**: Calculate stops as 2x ATR(14) instead of fixed percentage
**Benefits**:
- Per-trade risk more consistent in standard deviations
- Fewer false stops on volatile stocks
- More appropriate sizing on calm stocks
**Action During v6.0**: Track ATR(14) at entry in CSV for post-hoc analysis
**Analyst's Words**: "Move toward volatility-based position sizing & stops so per-trade risk is more consistent"
**Effort**: 1-2 days (v7.0)
**Impact**: Reduce unnecessary stop-outs, improve risk consistency

### 2B. Regime-Conditional Learning Stats (MEDIUM PRIORITY - v7.0)
**Issue**: Learning loop can become pro-cyclical (exclude catalysts right before recovery)
**Risk**: Catalyst exclusions may whipsaw (6/10 risk)
**Current**: Single win rate threshold (40%) across all regimes
**Proposed**: Track catalyst performance by VIX regime and market breadth separately
- Example: "Tier 2 catalysts: 65% win rate in VIX <20, 35% win rate in VIX >25"
- Exclude only in specific regimes, not universally
**Benefits**:
- Avoid whipsaw (dropping catalyst right before favorable regime)
- More nuanced learning (what works when)
- Less pro-cyclical bias
**Action During v6.0**: Already tracking VIX regime and market breadth per trade
**Analyst's Words**: "Use regime-conditional stats. Consider shrinkage approach rather than hard exclusions."
**Effort**: 2-3 days (v7.0)
**Impact**: Smarter learning system that adapts to regime changes

### 2C. Feature Snapshot Storage for Every Decision (LOWER PRIORITY - v7.0)
**Issue**: Can't reconstruct exact features Claude saw at decision time
**Current**: 52-column CSV captures trade outcome, but not all raw features at decision point
**Proposed**: Store structured JSON snapshot with every GO decision:
- All screener features for each candidate (RS, volume, ADX, etc.)
- VIX regime, market breadth, macro events
- News validation scores
- Claude's output (conviction, reasoning)
**Benefits**: Enables post-hoc model training (logistic regression on exact features)
**Effort**: 1 day (v7.0)
**Impact**: Enables LLM contribution analysis (Priority 1B)

---

## Priority 3: Future Enhancements (v8.0+)

**Status**: LOWEST PRIORITY - Only consider after v6.0 + v7.0 validation proves edge

### 3A. Capacity Analysis & Scaling Model
**Issue**: Unknown capacity constraints as account size grows
**Proposed**: Model market impact as function of position size / ADV ratio
**Trigger**: When account >$10,000 or preparing for real capital deployment

### 3B. Multi-Model Ensemble (Advanced)
**Issue**: Single LLM dependency
**Proposed**: Ensemble of Claude + simple rules-based model + ML model
**Trigger**: After proving LLM adds measurable edge (Priority 1B complete)

### 3C. Sector Rotation with Macro Regime Awareness
**Issue**: Current sector rotation is pure momentum (3-month performance)
**Proposed**: Add macro regime awareness (Fed tightening = avoid growth, favor value)
**Trigger**: After simplification (Priority 1A) proves sector rotation adds edge

---

## Summary: Priority Order for v7.0+

1. **CRITICAL (Do First)**:
   - 1A: Ablation testing (find which 50% of features drive edge)
   - 1B: LLM contribution analysis (quantify Claude's edge)
   - 1C: Apply success/failure metrics (keep/simplify/retire decision)
   - 1D: Slippage modeling (validate edge survives execution costs)

2. **HIGH PRIORITY (Do Second)**:
   - 1E: Walk-forward & Monte Carlo (prove robustness)
   - 1F: Sensitivity analysis (identify fragile parameters)

3. **MEDIUM PRIORITY (Do Third)**:
   - 2A: ATR-based stops (if v6.0 shows stop-out issues)
   - 2B: Regime-conditional learning (if v6.0 shows pro-cyclical whipsaw)

4. **LOWER PRIORITY (Do Last)**:
   - 2C: Feature snapshot storage (nice to have for analysis)
   - Priority 3 items (only if v6.0+v7.0 prove edge exists)

**Guiding Principle**: "Treat v6.0 as an experiment to simplify and harden the system rather than keep piling on features" - Third-party analyst

**Current approach**:
- ✅ Code frozen at v6.0 (Dec 2, 2024)
- ✅ All 50+ CSV columns capturing complete trade data
- ✅ Learning system operational and tracking all Phase 4 enhancements
- ✅ Dashboard displaying real-time performance metrics
- ✅ Health monitoring and alerting active

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
- ✅ We filter for $50M+ daily volume (Deep Research v7.0)
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
