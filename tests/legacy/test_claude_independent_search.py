#!/usr/bin/env python3
"""
Test: Can Claude find Tier 1 stocks independently without the screener?
This is a diagnostic test to compare Claude's independent search vs screener output.
"""

import requests
import json
import os
from datetime import datetime

# Load API key
api_key = os.environ.get("CLAUDE_API_KEY")
if not api_key:
    print("ERROR: CLAUDE_API_KEY not found in environment")
    exit(1)

prompt = """You are an expert swing trader looking for high-conviction Tier 1 catalyst opportunities.

**TODAY IS DECEMBER 19, 2025**

**YOUR TASK:** Find 5-10 stocks RIGHT NOW that have TRUE Tier 1 catalysts for swing trading (3-30 day holds).

**TIER 1 CATALYSTS (Your Target):**
- Earnings beats >10% with raised guidance (reported in last 5 days)
- FDA approvals or major regulatory wins (announced recently)
- M&A announcements with significant premiums
- Major contract wins with revenue impact >10%
- Multiple strong catalysts converging (e.g., earnings + upgrade + insider buying)

**MARKET CONTEXT:**
- VIX: ~17 (normal market, all tiers acceptable)
- S&P 500 breadth: 70.6% (healthy bullish environment)
- Sector rotation: Healthcare showing unusual strength

**WHAT TO SEARCH FOR:**
1. Recent earnings calendar (Dec 16-19) - who beat and raised guidance?
2. FDA calendar - any recent approvals this week?
3. M&A news - any deals announced in last 48 hours?
4. Major contract announcements (defense, tech, pharma)
5. Stocks with unusual volume + news convergence

**OUTPUT FORMAT:**
For each stock you find:
- Ticker
- Specific Tier 1 catalyst (with dates/numbers)
- Why this qualifies as Tier 1
- Entry thesis (technical + fundamental)

**CRITICAL:** Only provide stocks where you can clearly articulate a SPECIFIC, VERIFIABLE Tier 1 catalyst. If you cannot find any true Tier 1 opportunities, say so honestly.

Begin your search now."""

print("=" * 80)
print("CLAUDE INDEPENDENT STOCK SEARCH TEST")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
print("=" * 80)
print()

headers = {
    'x-api-key': api_key,
    'anthropic-version': '2023-06-01',
    'content-type': 'application/json'
}

payload = {
    'model': 'claude-sonnet-4-5-20250929',
    'max_tokens': 4000,
    'messages': [
        {'role': 'user', 'content': prompt}
    ]
}

response = requests.post(
    'https://api.anthropic.com/v1/messages',
    headers=headers,
    json=payload,
    timeout=120
)

if response.status_code == 200:
    result = response.json()
    print(result['content'][0]['text'])
else:
    print(f"ERROR: API call failed with status {response.status_code}")
    print(response.text)

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
