# Alpaca Integration Setup Instructions

## Step 1: Create Alpaca Paper Trading Account (5 minutes)

1. Go to https://alpaca.markets
2. Click "Sign Up" in the top right
3. Fill out registration form:
   - Email address
   - Password
   - Name
4. Verify your email address (check inbox for verification link)
5. Log in to your Alpaca account

## Step 2: Get API Keys for Paper Trading

1. Once logged in, click on your profile/account icon (top right)
2. Navigate to "API Keys" or "Paper Trading"
3. You should see TWO sets of API keys:
   - **Paper Trading Keys** (what we want - for testing)
   - **Live Trading Keys** (DO NOT use these for MVP)

4. Under "Paper Trading", click "Generate New Key" or "View" if keys already exist
5. You'll see:
   ```
   API Key ID: PKxxxxxxxxxxxxxxxxxx
   Secret Key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
6. **IMPORTANT**: Copy both keys somewhere safe
   - You can only see the Secret Key ONCE when it's created
   - If you lose it, you'll need to regenerate a new key pair

## Step 3: Add API Keys to Server Environment

You need to add these keys to the server's `.env` file:

```bash
# SSH into your server
ssh root@174.138.67.26

# Edit the .env file
cd /root/paper_trading_lab
nano .env

# Add these lines (replace with your actual keys):
ALPACA_API_KEY=PKxxxxxxxxxxxxxxxxxx
ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Save and exit (Ctrl+X, then Y, then Enter)

# Source the environment variables
source .env
```

## Step 4: Install Alpaca SDK on Server

```bash
# SSH into server (if not already)
ssh root@174.138.67.26

# Navigate to project directory
cd /root/paper_trading_lab

# Activate virtual environment
source venv/bin/activate

# Install alpaca-trade-api
pip install alpaca-trade-api==3.2.0

# Update requirements file
pip freeze > requirements.txt
```

## Step 5: Test Connection

```bash
# Still on server with venv activated
python3 alpaca_broker.py
```

You should see output like:
```
============================================================
ALPACA CONNECTION TEST
============================================================

✓ Connected to Alpaca (https://paper-api.alpaca.markets)
  Account Status: ACTIVE
  Buying Power: $100,000.00

Account Status: ACTIVE
Account Value: $100,000.00
Cash Available: $100,000.00
Buying Power: $100,000.00

Open Positions: 0

✓ Connection successful!
```

## Step 6: Verify Local Setup (Optional)

If you want to test locally on your Mac:

```bash
# On your local machine
cd /Users/tednunes/Downloads/paper_trading_lab

# Add to your local .env file
echo "ALPACA_API_KEY=PKxxxxxxxxxxxxxxxxxx" >> .env
echo "ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" >> .env
echo "ALPACA_BASE_URL=https://paper-api.alpaca.markets" >> .env

# Source environment
source .env

# Install SDK (if you have a local venv)
pip install alpaca-trade-api==3.2.0

# Test connection
python3 alpaca_broker.py
```

## Troubleshooting

### "alpaca-trade-api package not installed"
- Make sure you activated the virtual environment: `source venv/bin/activate`
- Run: `pip install alpaca-trade-api==3.2.0`

### "Alpaca API credentials not found"
- Make sure you added the keys to `.env`
- Make sure you sourced the environment: `source .env`
- Check spelling: `ALPACA_API_KEY` (not `ALPACA_KEY`)

### "Failed to connect to Alpaca"
- Verify your API keys are correct (try copying again from Alpaca dashboard)
- Make sure you're using **Paper Trading keys** (start with "PK")
- Check your internet connection

### "Invalid API key"
- You might be using Live keys instead of Paper keys
- Regenerate Paper Trading keys in Alpaca dashboard

## Next Steps

Once you've successfully run the connection test, come back to Claude Code and say:

**"Alpaca is connected. Continue with agent integration."**

I'll then modify agent_v5.5.py to use the AlpacaBroker for:
1. Loading portfolio from Alpaca positions (instead of JSON file)
2. Fetching prices from Alpaca (alongside Polygon.io as backup)
3. Executing orders via Alpaca API (instead of simulated tracking)

## Security Notes

- Never commit `.env` file to git (already in .gitignore)
- Never share your Secret Key publicly
- Paper trading keys have NO ACCESS to real money
- You can regenerate keys anytime in the Alpaca dashboard
- For MVP, we'll ONLY use paper trading (no live trading)
