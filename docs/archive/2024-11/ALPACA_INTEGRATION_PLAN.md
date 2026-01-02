# Alpaca Integration Plan
**Regulatory-Safe Trading Dashboard with Zero Licensing Requirements**

---

## Executive Summary

Transform your current paper trading system into a multi-user SaaS platform where users:
1. Connect their own Alpaca brokerage accounts
2. View AI-powered trade recommendations from Claude
3. Click to execute (or ignore) recommendations
4. Track performance on personalized dashboard

**You provide:** Software tool that analyzes markets and executes user-approved trades
**You DON'T provide:** Investment advice, custody of funds, or discretionary management

**Result:** No SEC registration, no Series 65, no RIA license needed.

---

## Phase 0: Current State (What You Have)

✅ Working paper trading system
✅ Claude AI making buy/sell decisions
✅ GO → EXECUTE → ANALYZE workflow
✅ Dashboard showing portfolio/performance
✅ Learning system tracking catalyst effectiveness

**Current Mode:** Single-user paper trading on your server

---

## Phase 1: Alpaca Paper Trading MVP (Week 1-2)

### Goal
Replace your current Polygon.io data + manual tracking with Alpaca Paper Trading API.

### What is Alpaca Paper Trading?
- Free simulated trading environment
- Real market data (15-min delayed)
- Executes fake orders instantly
- Tracks portfolio automatically
- Same API as live trading

### Setup Steps

**1. Create Alpaca Account (5 minutes)**
- Go to https://alpaca.markets
- Sign up (free)
- Verify email
- Get API keys (Paper Trading)

**2. Install Alpaca SDK**
```bash
cd /root/paper_trading_lab
source venv/bin/activate
pip install alpaca-trade-api
pip freeze > requirements.txt
```

**3. Add API Keys to Environment**
```bash
# Add to /root/.env
ALPACA_API_KEY=PKxxxxxxxxxxxxxxx
ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxx
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Paper trading URL
```

**4. Create Alpaca Adapter**

Create new file: `alpaca_broker.py`

```python
import alpaca_trade_api as tradeapi
import os

class AlpacaBroker:
    """
    Wrapper for Alpaca API - handles all brokerage operations
    Replaces manual portfolio tracking with real brokerage API
    """

    def __init__(self):
        self.api = tradeapi.REST(
            os.environ['ALPACA_API_KEY'],
            os.environ['ALPACA_SECRET_KEY'],
            os.environ['ALPACA_BASE_URL'],
            api_version='v2'
        )

    def get_account(self):
        """Get account info (buying power, equity, etc)"""
        return self.api.get_account()

    def get_positions(self):
        """Get all open positions"""
        return self.api.list_positions()

    def get_position(self, ticker):
        """Get specific position"""
        try:
            return self.api.get_position(ticker)
        except:
            return None

    def place_market_order(self, ticker, qty, side='buy'):
        """
        Place market order
        side: 'buy' or 'sell'
        """
        return self.api.submit_order(
            symbol=ticker,
            qty=qty,
            side=side,
            type='market',
            time_in_force='day'
        )

    def get_last_price(self, ticker):
        """Get latest price for ticker"""
        trade = self.api.get_latest_trade(ticker)
        return trade.price

    def get_bars(self, tickers, timeframe='1Day', limit=100):
        """Get historical price bars"""
        return self.api.get_bars(tickers, timeframe, limit=limit)

    def cancel_all_orders(self):
        """Cancel all pending orders"""
        return self.api.cancel_all_orders()
```

**5. Modify agent_v5.5.py to Use Alpaca**

Key changes:
```python
from alpaca_broker import AlpacaBroker

class TradingAgent:
    def __init__(self):
        # ... existing code ...
        self.broker = AlpacaBroker()

    def fetch_current_prices(self, tickers):
        """Use Alpaca instead of Polygon for prices"""
        prices = {}
        for ticker in tickers:
            try:
                prices[ticker] = self.broker.get_last_price(ticker)
            except:
                print(f"⚠️ Failed to fetch {ticker}")
        return prices

    def load_current_portfolio(self):
        """Load from Alpaca positions instead of JSON file"""
        positions = self.broker.get_positions()

        portfolio_positions = []
        for pos in positions:
            portfolio_positions.append({
                'ticker': pos.symbol,
                'shares': float(pos.qty),
                'entry_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price),
                'position_size': float(pos.market_value),
                'unrealized_gain_pct': float(pos.unrealized_plpc) * 100,
                'unrealized_gain_dollars': float(pos.unrealized_pl),
                # ... map other fields ...
            })

        return {'positions': portfolio_positions}

    def execute_execute_command(self):
        """Modified to use Alpaca orders instead of manual tracking"""

        # EXITS: Place sell orders
        for exit_decision in exit_decisions:
            ticker = exit_decision['ticker']
            position = self.broker.get_position(ticker)
            if position:
                # Sell entire position
                order = self.broker.place_market_order(
                    ticker=ticker,
                    qty=position.qty,
                    side='sell'
                )
                print(f"✓ SOLD {ticker}: {position.qty} shares")

        # BUYS: Place buy orders
        for buy_pos in buy_positions:
            ticker = buy_pos['ticker']

            # Calculate shares from dollar amount
            price = self.broker.get_last_price(ticker)
            position_size_dollars = buy_pos['position_size_dollars']
            shares = int(position_size_dollars / price)

            if shares > 0:
                order = self.broker.place_market_order(
                    ticker=ticker,
                    qty=shares,
                    side='buy'
                )
                print(f"✓ BOUGHT {ticker}: {shares} shares @ ${price}")
```

**6. Test with Paper Account**
```bash
cd /root/paper_trading_lab
source venv/bin/activate
source /root/.env

# Test connection
python3 -c "from alpaca_broker import AlpacaBroker; broker = AlpacaBroker(); print(broker.get_account())"

# Run GO command (will use Alpaca data)
python3 agent_v5.5.py go

# Run EXECUTE (will place paper orders)
python3 agent_v5.5.py execute

# Check positions
python3 -c "from alpaca_broker import AlpacaBroker; broker = AlpacaBroker(); print(broker.get_positions())"
```

### Benefits After Phase 1
✅ Real brokerage API integration (not manual tracking)
✅ Automatic position updates
✅ Order execution handling
✅ Foundation for multi-user system
✅ Still completely free (paper trading)

---

## Phase 2: Multi-User Architecture (Week 3-4)

### Goal
Allow multiple users to connect their own Alpaca paper accounts.

### Database Schema

```sql
-- users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    subscription_tier VARCHAR(50) DEFAULT 'free'
);

-- alpaca_connections table
CREATE TABLE alpaca_connections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    alpaca_api_key VARCHAR(255) ENCRYPTED,
    alpaca_secret_key VARCHAR(255) ENCRYPTED,
    account_type VARCHAR(20), -- 'paper' or 'live'
    connected_at TIMESTAMP DEFAULT NOW()
);

-- user_trades table (for tracking/learning)
CREATE TABLE user_trades (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    trade_id VARCHAR(50),
    ticker VARCHAR(10),
    entry_date TIMESTAMP,
    exit_date TIMESTAMP,
    entry_price DECIMAL(10,2),
    exit_price DECIMAL(10,2),
    shares DECIMAL(10,4),
    return_percent DECIMAL(10,2),
    return_dollars DECIMAL(10,2),
    exit_reason VARCHAR(255),
    catalyst_type VARCHAR(50)
    -- ... all your existing CSV columns ...
);
```

### User Authentication

**Option A: Simple (Flask-Login)**
```python
from flask_login import LoginManager, login_user, logout_user

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    # Verify credentials
    # Create session
    return redirect('/dashboard')
```

**Option B: Modern (Clerk.dev - Recommended)**
- Drop-in auth solution ($25/month for 1000 users)
- Email/password + social login
- User management dashboard
- No security code to write
- 1-day integration

### Multi-User Trading Flow

```
8:45 AM - Cron runs GO command for ALL users:

FOR EACH user:
    1. Load user's Alpaca API keys from database
    2. Create AlpacaBroker instance with user's keys
    3. Run GO analysis for their portfolio
    4. Save recommendations to database
    5. Send email/notification: "3 new trade recommendations"

User logs in to dashboard:
    - Sees pending recommendations
    - Clicks "Execute" or "Ignore" for each
    - If Execute: Place order via their Alpaca account
    - Track decision in database for learning

4:30 PM - Cron runs ANALYZE for ALL users:
    - Update portfolios from Alpaca
    - Check stop loss / profit targets
    - Execute exits automatically (if enabled)
    - Update user dashboards
```

### Code Structure

```
/paper_trading_lab/
├── agent_v5.5.py              # Core trading logic (unchanged)
├── alpaca_broker.py            # Alpaca API wrapper
├── multi_user_runner.py        # NEW: Run GO/ANALYZE for all users
├── web_app.py                  # NEW: Flask app for user dashboard
├── /templates/
│   ├── login.html
│   ├── dashboard.html          # User's personalized dashboard
│   ├── connect_alpaca.html     # Alpaca connection flow
│   └── recommendations.html    # Pending trade recommendations
├── /database/
│   └── schema.sql
└── requirements.txt
```

**multi_user_runner.py:**
```python
"""
Run trading operations for all users
Called by cron at 8:45 AM and 4:30 PM
"""
import psycopg2
from alpaca_broker import AlpacaBroker
from agent_v5 import TradingAgent

def run_go_for_all_users():
    """Generate recommendations for all users"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT id, email FROM users WHERE subscription_tier != 'cancelled'")
    users = cursor.fetchall()

    for user_id, email in users:
        print(f"Running GO for user {email}...")

        # Get user's Alpaca keys
        cursor.execute(
            "SELECT alpaca_api_key, alpaca_secret_key FROM alpaca_connections WHERE user_id = %s",
            (user_id,)
        )
        keys = cursor.fetchone()

        if not keys:
            print(f"⚠️ User {email} has no Alpaca connection")
            continue

        # Create broker with user's keys
        broker = AlpacaBroker(api_key=keys[0], secret_key=keys[1])

        # Run GO command for this user
        agent = TradingAgent(broker=broker, user_id=user_id)
        recommendations = agent.execute_go_command()

        # Save recommendations to database
        save_recommendations(user_id, recommendations)

        # Send notification
        send_email(email, f"You have {len(recommendations['buy'])} new trade recommendations")

if __name__ == '__main__':
    run_go_for_all_users()
```

### Deployment Changes

**Crontab (still on your server, but for all users):**
```bash
# Run GO for all users
45 8 * * 1-5 cd /root/paper_trading_lab && source venv/bin/activate && python3 multi_user_runner.py go

# Run ANALYZE for all users
30 16 * * 1-5 cd /root/paper_trading_lab && source venv/bin/activate && python3 multi_user_runner.py analyze
```

**Web App (Flask on same server):**
```bash
# Start web app (separate from cron jobs)
gunicorn -w 4 -b 0.0.0.0:5001 web_app:app

# Nginx reverse proxy
location / {
    proxy_pass http://127.0.0.1:5001;
}
```

---

## Phase 3: Monetization (Month 2)

### Pricing Tiers

**Free Tier** (Paper Trading)
- Connect Alpaca paper account
- Get AI recommendations
- Track performance
- Limited to $10k paper capital
- 30-day trial

**Premium Tier** ($49/month)
- Connect Alpaca LIVE account
- Unlimited capital
- Full Claude AI analysis
- Email notifications
- Priority support

**Pro Tier** ($99/month)
- Everything in Premium
- Advanced analytics
- Custom risk parameters
- API access
- Phone support

### Payment Integration

**Stripe Setup (2-3 hours):**
```python
import stripe

stripe.api_key = os.environ['STRIPE_SECRET_KEY']

@app.route('/subscribe', methods=['POST'])
def subscribe():
    user_id = current_user.id
    tier = request.form['tier']  # 'premium' or 'pro'

    # Create Stripe subscription
    subscription = stripe.Subscription.create(
        customer=user.stripe_customer_id,
        items=[{'price': PRICE_IDS[tier]}]
    )

    # Update user tier in database
    update_user_tier(user_id, tier)

    return redirect('/dashboard')
```

### Webhooks for Subscription Management
```python
@app.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle subscription events"""
    event = stripe.Webhook.construct_event(
        request.data,
        request.headers['Stripe-Signature'],
        STRIPE_WEBHOOK_SECRET
    )

    if event['type'] == 'customer.subscription.deleted':
        # User cancelled - disable trading
        user = get_user_by_stripe_id(event['data']['object']['customer'])
        update_user_tier(user.id, 'cancelled')

    return '', 200
```

---

## Phase 4: Alpaca Live Trading (Month 3)

### Legal Protection

**Terms of Service (Required):**
```
TedBot Trading Dashboard - Terms of Service

1. SERVICE DESCRIPTION
   TedBot is a SOFTWARE TOOL that analyzes stock market data and provides
   trade recommendations. Users retain complete control over all trading
   decisions.

2. NOT INVESTMENT ADVICE
   TedBot does not provide investment advice. All recommendations are
   educational and for informational purposes only. Users are solely
   responsible for their trading decisions.

3. NO DISCRETIONARY MANAGEMENT
   TedBot never manages user funds. All money remains in the user's
   brokerage account. TedBot only executes trades that the user explicitly
   approves through the dashboard.

4. DISCLAIMER OF LIABILITY
   Past performance does not guarantee future results. Trading stocks
   involves risk of loss. User accepts all trading risks.

5. USER RESPONSIBILITIES
   User must:
   - Maintain their own Alpaca brokerage account
   - Review all recommendations before execution
   - Monitor their account regularly
   - Comply with all securities laws
```

**Disclaimer on Every Page:**
```
⚠️ NOT INVESTMENT ADVICE: TedBot is a software tool, not a financial advisor.
We do not provide investment advice. You are solely responsible for your
trading decisions. Past performance does not guarantee future results.
```

### Alpaca Live Account Connection

**User Flow:**
```
1. User clicks "Connect Live Trading"
2. Redirected to Alpaca OAuth flow
3. User authorizes TedBot to trade on their behalf
4. Alpaca returns OAuth token
5. TedBot stores encrypted token
6. System can now place real orders
```

**OAuth Implementation:**
```python
@app.route('/connect/alpaca/live')
def connect_alpaca_live():
    """Redirect to Alpaca OAuth"""
    oauth_url = (
        f"https://app.alpaca.markets/oauth/authorize?"
        f"response_type=code&"
        f"client_id={ALPACA_OAUTH_CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope=account:write trading"
    )
    return redirect(oauth_url)

@app.route('/connect/alpaca/callback')
def alpaca_callback():
    """Handle Alpaca OAuth callback"""
    code = request.args.get('code')

    # Exchange code for access token
    response = requests.post(
        'https://api.alpaca.markets/oauth/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': ALPACA_OAUTH_CLIENT_ID,
            'client_secret': ALPACA_OAUTH_SECRET,
            'redirect_uri': REDIRECT_URI
        }
    )

    token = response.json()['access_token']

    # Encrypt and store token
    save_alpaca_token(current_user.id, token, account_type='live')

    return redirect('/dashboard?connected=true')
```

### Safety Controls for Live Trading

**Required User Confirmations:**
```python
@app.route('/execute_trade', methods=['POST'])
def execute_trade():
    """User explicitly approves trade execution"""
    trade_id = request.form['trade_id']
    confirmation = request.form['confirm']

    if confirmation != 'I UNDERSTAND THE RISKS':
        return "Confirmation required", 400

    # Load trade recommendation
    trade = get_pending_trade(current_user.id, trade_id)

    # Place order via Alpaca
    broker = get_user_broker(current_user.id)
    order = broker.place_market_order(
        ticker=trade['ticker'],
        qty=trade['shares'],
        side='buy'
    )

    # Log decision
    log_user_trade(current_user.id, trade, order)

    return redirect('/dashboard')
```

**Account Limits (Safety Rails):**
```python
# In multi_user_runner.py
def validate_trade_safety(user_id, trade):
    """Prevent dangerous trades"""
    account = broker.get_account()

    # Max position size: 15% of account
    if trade['position_size'] > float(account.equity) * 0.15:
        return False, "Position size exceeds 15% limit"

    # Max 10 positions
    positions = broker.get_positions()
    if len(positions) >= 10:
        return False, "Portfolio at maximum 10 positions"

    # Min $1000 account size
    if float(account.equity) < 1000:
        return False, "Account below $1000 minimum"

    return True, "OK"
```

---

## Phase 5: Scale & Optimize (Month 4+)

### Performance Optimizations

**Background Job Queue (Celery):**
```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def run_go_for_user(user_id):
    """Run GO command in background"""
    # This prevents 8:45 AM cron from timing out with 100+ users
    agent = get_user_agent(user_id)
    agent.execute_go_command()

# In multi_user_runner.py
for user_id in active_users:
    run_go_for_user.delay(user_id)  # Queues task, returns immediately
```

**Caching (Redis):**
```python
import redis

cache = redis.Redis(host='localhost', port=6379)

def get_market_data(ticker):
    """Cache market data to reduce API calls"""
    cached = cache.get(f"price:{ticker}")
    if cached:
        return float(cached)

    price = broker.get_last_price(ticker)
    cache.setex(f"price:{ticker}", 60, price)  # Cache for 60 seconds
    return price
```

### Monitoring & Alerts

**Sentry for Error Tracking:**
```python
import sentry_sdk

sentry_sdk.init(dsn=SENTRY_DSN)

# Automatically captures all exceptions
# Shows errors in dashboard with full context
```

**Custom Monitoring:**
```python
@celery.task
def monitor_system_health():
    """Run every 5 minutes"""

    # Check if GO ran today
    last_go = get_last_go_run()
    if (datetime.now() - last_go).hours > 24:
        send_alert("GO command hasn't run in 24 hours!")

    # Check Alpaca API status
    try:
        broker.get_account()
    except:
        send_alert("Alpaca API is down!")

    # Check database connection
    # Check disk space
    # Check memory usage
```

---

## Technology Stack Summary

**Current (Single User):**
- Python 3.11
- agent_v5.5.py (trading logic)
- Polygon.io (market data)
- Flask (dashboard)
- JSON files (portfolio tracking)

**Target (Multi-User SaaS):**
- Python 3.11
- agent_v5.5.py (trading logic - mostly unchanged)
- Alpaca API (market data + order execution)
- Flask (web app)
- PostgreSQL (user data, trades)
- Redis (caching, job queue)
- Celery (background jobs)
- Gunicorn (web server)
- Nginx (reverse proxy)
- Stripe (payments)
- Clerk.dev (authentication)

**Infrastructure:**
- DigitalOcean Droplet (current: $6/mo → upgrade to $24/mo for 4GB RAM)
- AWS RDS PostgreSQL ($15/mo for small instance)
- Redis Cloud (free tier, 30MB)
- Total: ~$40/mo for 100 users

---

## Revenue Model

**Assumptions:**
- 100 free users (paper trading)
- 15 convert to Premium ($49/mo) = $735/mo
- 5 convert to Pro ($99/mo) = $495/mo
- **Total MRR: $1,230**

**Costs:**
- Infrastructure: $40/mo
- Stripe fees (2.9%): $36/mo
- Clerk auth: $25/mo
- **Total Costs: $101/mo**

**Net Profit: $1,129/mo**

**At 1,000 users:**
- 150 Premium ($49) = $7,350
- 50 Pro ($99) = $4,950
- **Total MRR: $12,300**
- Costs: ~$200/mo
- **Net Profit: $12,100/mo**

---

## Timeline & Milestones

**Week 1-2: Alpaca Integration**
- [ ] Create Alpaca paper account
- [ ] Install SDK, create alpaca_broker.py
- [ ] Modify agent_v5.5.py to use Alpaca
- [ ] Test GO → EXECUTE → ANALYZE with Alpaca paper
- [ ] Validate orders execute correctly

**Week 3-4: Multi-User Architecture**
- [ ] Set up PostgreSQL database
- [ ] Create user tables + schema
- [ ] Build Flask web app (login, dashboard, connect Alpaca)
- [ ] Implement multi_user_runner.py
- [ ] Test with 2-3 test users

**Week 5-6: Polish & Beta**
- [ ] Add Stripe payment integration
- [ ] Write terms of service + disclaimers
- [ ] Set up monitoring/alerts
- [ ] Deploy to production
- [ ] Invite 10 beta users (free paper trading)

**Week 7-8: Public Launch**
- [ ] Gather feedback from beta
- [ ] Fix bugs, improve UX
- [ ] Marketing (Twitter, Reddit, landing page)
- [ ] Launch paid tiers ($49 Premium, $99 Pro)
- [ ] Goal: 20 paying users by end of month 2

**Month 3-4: Live Trading**
- [ ] Consult fintech attorney ($5k one-time)
- [ ] Implement Alpaca OAuth for live accounts
- [ ] Add safety controls (position limits, confirmations)
- [ ] Launch live trading tier
- [ ] Goal: 50 paying users, $3k MRR

**Month 5-6: Scale**
- [ ] Add advanced analytics
- [ ] Improve Claude's decision explanations
- [ ] Add mobile app (optional)
- [ ] Goal: 100 paying users, $6k MRR

---

## Next Steps (This Week)

**Priority 1: Alpaca POC (2-3 hours)**
1. Create Alpaca paper account
2. Install alpaca-trade-api
3. Write alpaca_broker.py (80 lines of code)
4. Modify fetch_current_prices() to use Alpaca
5. Test: Can you fetch prices via Alpaca?

**Priority 2: Place Test Order (1 hour)**
1. Modify execute_execute_command() to use broker.place_market_order()
2. Run GO → EXECUTE with 1 position
3. Verify order appears in Alpaca dashboard
4. Celebrate: You just integrated a real brokerage! 🎉

**Priority 3: Planning (1 hour)**
1. Decide: Do you want to build this as a SaaS?
2. If yes: Choose database (PostgreSQL vs SQLite)
3. If yes: Choose auth (Clerk vs custom)
4. Sketch out user dashboard design

Want me to help you start with the Alpaca POC right now?
