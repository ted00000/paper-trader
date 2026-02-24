#!/usr/bin/env python3
"""
Alpaca Sync Check - Hourly alignment verification

Runs via cron every hour to check if Alpaca positions match JSON portfolio.
Writes status to portfolio_data/alpaca_status.json for dashboard display.

Status levels:
- GREEN: Online and positions aligned
- YELLOW: Online but alignment issues detected (requires attention)
- RED: Connection failed

Usage:
    python alpaca_sync_check.py

Cron (hourly, market hours only):
    0 9-16 * * 1-5 cd /path/to/paper_trading_lab && python alpaca_sync_check.py
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project directory to path
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

def load_json_portfolio():
    """Load portfolio from JSON file"""
    portfolio_file = PROJECT_DIR / 'portfolio_data' / 'current_portfolio.json'

    if not portfolio_file.exists():
        return {}

    with open(portfolio_file, 'r') as f:
        data = json.load(f)

    # Return dict of {ticker: shares}
    positions = {}
    for pos in data.get('positions', []):
        ticker = pos.get('ticker')
        shares = pos.get('shares', 0)
        if ticker and shares > 0:
            positions[ticker] = shares

    return positions


def write_status(status: str, message: str, details: dict = None):
    """Write status to JSON file for dashboard"""
    status_file = PROJECT_DIR / 'portfolio_data' / 'alpaca_status.json'

    # Ensure directory exists
    status_file.parent.mkdir(parents=True, exist_ok=True)

    data = {
        'status': status,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'details': details
    }

    with open(status_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"[{status}] {message}")
    return data


def check_sync():
    """Main sync check function"""
    print(f"\n{'='*50}")
    print(f"ALPACA SYNC CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*50)

    # Check if Alpaca is configured
    api_key = os.environ.get('ALPACA_API_KEY')
    secret_key = os.environ.get('ALPACA_SECRET_KEY')

    if not api_key or not secret_key:
        return write_status(
            'RED',
            'Alpaca not configured (missing API keys)',
            {'error': 'ALPACA_API_KEY or ALPACA_SECRET_KEY not set'}
        )

    # Try to connect to Alpaca
    try:
        from alpaca_broker import AlpacaBroker
        broker = AlpacaBroker()
    except ImportError as e:
        return write_status(
            'RED',
            'Alpaca broker module not available',
            {'error': str(e)}
        )
    except Exception as e:
        return write_status(
            'RED',
            f'Alpaca connection failed: {str(e)}',
            {'error': str(e)}
        )

    # Get Alpaca data
    try:
        alpaca_account = broker.get_account()
        alpaca_positions = {p.symbol: float(p.qty) for p in broker.api.list_positions()}

        print(f"Alpaca: {len(alpaca_positions)} positions, ${float(alpaca_account.equity):,.2f} equity")
    except Exception as e:
        return write_status(
            'RED',
            f'Failed to fetch Alpaca data: {str(e)}',
            {'error': str(e)}
        )

    # Load JSON portfolio
    json_positions = load_json_portfolio()
    print(f"JSON: {len(json_positions)} positions")

    # Check alignment
    issues = []
    all_tickers = set(json_positions.keys()) | set(alpaca_positions.keys())

    for ticker in sorted(all_tickers):
        json_shares = json_positions.get(ticker, 0)
        alpaca_shares = alpaca_positions.get(ticker, 0)

        if json_shares > 0 and alpaca_shares == 0:
            issues.append(f'{ticker}: in JSON ({json_shares:.0f} shares) but not Alpaca')
        elif alpaca_shares > 0 and json_shares == 0:
            issues.append(f'{ticker}: in Alpaca ({alpaca_shares:.0f} shares) but not JSON')
        elif abs(json_shares - alpaca_shares) > 0.01:
            issues.append(f'{ticker}: share mismatch (JSON: {json_shares:.2f}, Alpaca: {alpaca_shares:.2f})')

    # Write status
    if issues:
        print(f"\nAlignment issues found:")
        for issue in issues:
            print(f"  - {issue}")

        return write_status(
            'YELLOW',
            f'{len(issues)} alignment issue(s) detected',
            {
                'issues': issues,
                'json_positions': len(json_positions),
                'alpaca_positions': len(alpaca_positions),
                'alpaca_equity': float(alpaca_account.equity),
                'alpaca_cash': float(alpaca_account.cash)
            }
        )
    else:
        return write_status(
            'GREEN',
            f'Online and aligned ({len(alpaca_positions)} positions)',
            {
                'positions': len(alpaca_positions),
                'alpaca_equity': float(alpaca_account.equity),
                'alpaca_cash': float(alpaca_account.cash)
            }
        )


if __name__ == '__main__':
    try:
        result = check_sync()
        print(f"\nStatus written to portfolio_data/alpaca_status.json")
        sys.exit(0 if result['status'] == 'GREEN' else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        write_status('RED', f'Sync check crashed: {str(e)}', {'error': str(e)})
        sys.exit(1)
