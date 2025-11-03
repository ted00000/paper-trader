# Learning System & Admin Dashboard Summary
**Added:** 2025-11-02
**Quick Reference Guide**

---

## Overview

Your trading system now has **autonomous learning** with **human oversight** for critical decisions.

### Two-Track System

```
┌──────────────────────────────────────────────────────────┐
│  CATALYST EXCLUSIONS          │  PARAMETER OPTIMIZATION  │
│  ─────────────────────        │  ──────────────────────  │
│  ✓ Fully Automated            │  ⚠ Requires Approval     │
│  ✓ Claude Can Override        │  ⚠ Human Decision        │
│  ✓ 7-Day Fast Loop            │  ⚠ 30-Day Slow Loop      │
└──────────────────────────────────────────────────────────┘
```

---

## 1. Catalyst Exclusions (Automated)

### What It Does
- Identifies bad catalysts (e.g., "stock_split", "activist_investor")
- Automatically excludes them from future trades
- Claude can override with strong reasoning

### How It Works
```
learn_daily.py (Daily 5:00 PM)
  ↓
Analyzes last 7 days
  ↓
Finds catalysts with <35% win rate (10+ trades)
  ↓
Updates catalyst_exclusions.json
  ↓
agent_v5.5.py enforces exclusions
  ↓
Claude can override with reasoning
  ↓
Override logged to exclusion_overrides.log
  ↓
Dashboard shows override results
```

### Example Exclusion
```json
{
  "catalyst": "stock_split",
  "win_rate": 28.5,
  "total_trades": 14,
  "added_date": "2025-11-01",
  "reasoning": "Poor momentum, high false signals"
}
```

### Claude Override
When Claude sees an excluded catalyst, it can still trade if it provides strong reasoning:

```json
{
  "action": "BUY",
  "ticker": "NVDA",
  "catalyst": "stock_split",
  "override_exclusion": true,
  "override_reasoning": "This is a 10:1 split for NVDA with strong institutional support and positive market sentiment. Unlike previous split failures in low-volume stocks, this has $500B+ market cap backing."
}
```

### Files Modified
- `agent_v5.5.py` (lines 2726-2754): Enforcement + override logic
- `agent_v5.5.py` (lines 2044-2061): Override logging
- `agent_v5.5.py` (lines 1924-1930): Claude prompt instructions

---

## 2. Parameter Optimization (Human Approval)

### What It Does
- Analyzes 30+ days of trades monthly
- Recommends changes to numerical parameters
- **Waits for your approval** before applying

### Parameters Monitored
| Parameter | Current | What It Does |
|-----------|---------|--------------|
| VIX_THRESHOLD | 25 | Skip trades when VIX > 25 (high volatility) |
| RS_THRESHOLD | 1.1 | Require 10%+ relative strength vs. SPY |
| NEWS_SCORE_MIN | 15 | Minimum news quality score (0-20 scale) |
| STOP_LOSS_PCT | -7% | Auto-exit when position drops 7% |

### How It Works
```
learn_monthly.py (Last Sunday 6:00 PM)
  ↓
Analyzes 30+ days of trades
  ↓
Identifies underperforming parameters
  ↓
Generates recommendations with reasoning
  ↓
Saves to dashboard_data/pending_actions.json
  ↓
YOU review at tedbot.ai/admin
  ↓
YOU approve or reject
  ↓
If approved, YOU manually edit agent_v5.5.py
```

### Example Recommendation
```json
{
  "type": "PARAMETER_ADJUSTMENT",
  "parameter": "VIX_THRESHOLD",
  "current_value": 25,
  "suggested_value": 22,
  "sample_size": 28,
  "reasoning": "VIX >25 showing 38.2% win rate over 28 trades. Lowering to 22 would have avoided 8 losing trades while only filtering 2 winners. Net improvement: +$187.",
  "confidence": "HIGH"
}
```

### Files Modified
- `learn_monthly.py` (lines 488-537): Recommendation generation
- `learn_monthly.py` (lines 539-564): Save to dashboard

---

## 3. Admin Dashboard

### Access
**URL:** https://tedbot.ai/admin
**Login:** Use credentials from `~/.env`

### What You See

#### System Status
- Account value: $XXX.XX
- Active positions: X/10
- Win rate (30d): XX.X%
- Last updated: timestamp

#### Actions Required
- Pending parameter recommendations
- Approve/Reject buttons
- Sample size and confidence levels
- Detailed reasoning

#### Recent Trades
- Last 5 completed trades
- Entry/Exit prices, Hold days, P&L
- Exit reasons

#### Exclusion Overrides
- Claude's override decisions
- Override reasoning
- Results (WIN/LOSS)

### Security Features
- Password protected (bcrypt hashing)
- Rate limiting (5 attempts, 15-min lockout)
- Session timeout (2 hours)
- Audit logging
- HTTPS encryption

### Files Created
- `dashboard_server.py` - Flask application
- `dashboard/templates/login.html` - Login page
- `dashboard/templates/dashboard.html` - Main interface
- `start_dashboard.sh` - Startup script
- `generate_dashboard_credentials.py` - Credential setup
- `DASHBOARD_SETUP.md` - Deployment guide
- `trading-dashboard.nginx.conf` - Nginx configuration

---

## Usage Guide

### Daily (Automated)
- System runs `learn_daily.py` at 5:00 PM
- Updates catalyst exclusions automatically
- No action required from you

### Weekly (Automated)
- System runs `learn_weekly.py` on Fridays at 5:30 PM
- Generates performance reports
- No action required from you

### Monthly (Requires Action)
1. System runs `learn_monthly.py` on last Sunday at 6:00 PM
2. Generates parameter recommendations
3. **YOU login to tedbot.ai/admin**
4. **YOU review recommendations**
5. **YOU approve or reject**
6. **If approved, YOU edit agent_v5.5.py manually**

### Monitoring
```bash
# View security events
tail -f logs/dashboard/audit.log

# View Claude overrides
tail -f logs/exclusion_overrides.log

# Check dashboard status
screen -r dashboard
```

---

## Why This Design?

### Catalyst Exclusions = Automated
- **Data is clear**: 28% win rate = bad catalyst
- **Fast feedback**: 7 days is enough signal
- **Override available**: Claude can use judgment
- **High accountability**: Overrides are tracked

### Parameter Changes = Human Approval
- **Context matters**: Market regimes change
- **Slow feedback**: 30 days prevents overreaction
- **Strategic impact**: Affects entire system
- **Prevents overfitting**: Human judgment adds friction

### Best of Both Worlds
- **Autonomous where appropriate**: Bad catalysts get cut fast
- **Human where needed**: Strategic parameters require context
- **Accountability**: All decisions logged
- **Flexibility**: System can adapt while you maintain control

---

## Quick Commands

### Start Dashboard
```bash
# On server
screen -S dashboard
./start_dashboard.sh
# Ctrl+A then D to detach
```

### View Logs
```bash
# Security events
tail -f logs/dashboard/audit.log

# Claude overrides
tail -f logs/exclusion_overrides.log
```

### Check Dashboard
```bash
# Reattach to see status
screen -r dashboard
```

### Access Dashboard
```
https://tedbot.ai/admin
```

---

## Troubleshooting

### Dashboard Not Loading
```bash
# Check if running
screen -r dashboard

# If not running, start it
./start_dashboard.sh
```

### Can't Login
```bash
# Check credentials
cat ~/.env | grep ADMIN

# Regenerate if needed
python3 generate_dashboard_credentials.py
```

### Parameter Changes Not Applying
- You must manually edit `agent_v5.5.py`
- Dashboard only shows recommendations
- You own the final decision

---

## Key Files Reference

### Learning System
- `learn_daily.py` - Catalyst exclusion analysis
- `learn_weekly.py` - Performance reports
- `learn_monthly.py` - Parameter recommendations

### Data Files
- `catalyst_exclusions.json` - Excluded catalysts
- `dashboard_data/pending_actions.json` - Parameter recommendations
- `logs/exclusion_overrides.log` - Claude override tracking
- `logs/dashboard/audit.log` - Security events

### Dashboard
- `dashboard_server.py` - Flask app
- `start_dashboard.sh` - Startup script
- `~/.env` - Credentials (NEVER commit!)
- `/etc/nginx/sites-available/trading-dashboard` - Nginx config

### Documentation
- `MASTER_STRATEGY_BLUEPRINT.md` - Complete strategy (see Appendix)
- `DASHBOARD_SETUP.md` - Deployment guide
- `LEARNING_SYSTEM_SUMMARY.md` - This file

---

## Summary

**You now have:**
1. ✅ Automated catalyst exclusion with Claude self-validation
2. ✅ Monthly parameter recommendations (requires your approval)
3. ✅ Secure admin dashboard at tedbot.ai/admin
4. ✅ Full audit trail of all decisions
5. ✅ Human-in-the-loop for strategic changes

**Your role:**
- Monitor dashboard daily (optional, but recommended)
- Review monthly parameter recommendations
- Approve/reject changes based on market context
- Apply approved changes to agent_v5.5.py

**System's role:**
- Learn from every trade
- Exclude bad catalysts automatically
- Generate data-driven recommendations
- Track Claude's override decisions
- Maintain audit logs

**The result:**
- System learns and adapts continuously
- You maintain control over strategic decisions
- Full accountability and transparency
- Best of automation + human judgment

---

**Questions?** Check MASTER_STRATEGY_BLUEPRINT.md (Appendix) for full details.
