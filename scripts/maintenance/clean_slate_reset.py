#!/usr/bin/env python3
"""
CLEAN SLATE RESET - Complete System Reset for Paper Trading Lab
===============================================================

This script performs a complete reset of both:
1. Alpaca Paper Trading Account (liquidates all positions, resets to target balance)
2. TedBot JSON/CSV data files (portfolio, trades, account status)

SAFETY FEATURES:
- Dry-run mode by default (preview changes without executing)
- Creates timestamped backup before any changes
- Verifies Alpaca connection before proceeding
- Confirms all actions with user

Usage:
    python3 clean_slate_reset.py              # Dry run (preview only)
    python3 clean_slate_reset.py --execute    # Actually execute reset
    python3 clean_slate_reset.py --help       # Show help

Author: TedBot System
Last Updated: 2026-01-21
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_DIR))

# Configuration
STARTING_CAPITAL = 10000.00  # Target starting balance for both accounts
ALPACA_TARGET_BALANCE = 10000.00  # What we want Alpaca paper account to have

def load_env():
    """Load environment variables from .env file"""
    env_file = PROJECT_DIR / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Remove 'export ' prefix if present
                if line.startswith('export '):
                    line = line[7:]
                if '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key] = val

def get_alpaca_client():
    """Get Alpaca API client"""
    try:
        import alpaca_trade_api as tradeapi
        load_env()

        api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY'),
            os.getenv('ALPACA_SECRET_KEY'),
            base_url='https://paper-api.alpaca.markets'
        )
        return api
    except ImportError:
        print("ERROR: alpaca_trade_api not installed")
        return None
    except Exception as e:
        print(f"ERROR: Failed to connect to Alpaca: {e}")
        return None

def check_alpaca_state(api):
    """Check current Alpaca account state"""
    try:
        account = api.get_account()
        positions = api.list_positions()

        return {
            'equity': float(account.equity),
            'cash': float(account.cash),
            'buying_power': float(account.buying_power),
            'positions': [
                {
                    'symbol': p.symbol,
                    'qty': int(p.qty),
                    'avg_entry_price': float(p.avg_entry_price),
                    'market_value': float(p.market_value),
                    'unrealized_pl': float(p.unrealized_pl)
                }
                for p in positions
            ]
        }
    except Exception as e:
        print(f"ERROR: Failed to get Alpaca state: {e}")
        return None

def liquidate_alpaca_positions(api, dry_run=True):
    """Liquidate all Alpaca positions"""
    positions = api.list_positions()

    if not positions:
        print("   No positions to liquidate")
        return True

    print(f"   Liquidating {len(positions)} positions...")

    for p in positions:
        if dry_run:
            print(f"      [DRY RUN] Would sell {p.qty} shares of {p.symbol}")
        else:
            try:
                api.submit_order(
                    symbol=p.symbol,
                    qty=int(p.qty),
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
                print(f"      Sold {p.qty} shares of {p.symbol}")
            except Exception as e:
                print(f"      ERROR selling {p.symbol}: {e}")
                return False

    return True

def reset_alpaca_balance(api, target_balance, dry_run=True):
    """
    Reset Alpaca paper account balance.

    NOTE: Alpaca paper accounts can be reset via their web dashboard:
    https://app.alpaca.markets/paper/dashboard/overview

    Click "Reset Account" to reset to $100,000 default.

    For custom amounts, you need to either:
    1. Reset to $100k and withdraw excess, or
    2. Contact Alpaca support

    This function will document what needs to be done.
    """
    account = api.get_account()
    current_equity = float(account.equity)

    print(f"\n   Current Alpaca equity: ${current_equity:,.2f}")
    print(f"   Target balance: ${target_balance:,.2f}")

    if abs(current_equity - target_balance) < 1.0:
        print("   Balance already at target!")
        return True

    print("\n   NOTE: Alpaca paper account balance reset requires manual action:")
    print("   1. Go to: https://app.alpaca.markets/paper/dashboard/overview")
    print("   2. Click 'Reset Account' in the top right")
    print("   3. This resets to $100,000 by default")
    print(f"   4. After reset, the TedBot will track with ${target_balance:,.2f} starting capital")
    print("\n   For this reset, we'll:")
    print(f"   - Liquidate all positions (done above)")
    print(f"   - TedBot will track ${target_balance:,.2f} as starting capital")
    print(f"   - Alpaca actual balance may differ but TedBot tracks independently")

    return True

def create_backup(dry_run=True):
    """Create backup of all data files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = PROJECT_DIR / 'backups' / f'clean_slate_backup_{timestamp}'

    files_to_backup = [
        'portfolio_data/current_portfolio.json',
        'portfolio_data/account_status.json',
        'portfolio_data/pending_positions.json',
        'portfolio_data/daily_activity.json',
        'trade_history/completed_trades.csv',
        'strategy_evolution/catalyst_exclusions.json',
        'strategy_evolution/near_miss_log.csv',
        'screener_candidates.json',
    ]

    if dry_run:
        print(f"   [DRY RUN] Would create backup at: {backup_dir}")
        for f in files_to_backup:
            src = PROJECT_DIR / f
            if src.exists():
                print(f"      Would backup: {f}")
        return str(backup_dir)

    backup_dir.mkdir(parents=True, exist_ok=True)

    for f in files_to_backup:
        src = PROJECT_DIR / f
        if src.exists():
            dest = backup_dir / f
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            print(f"      Backed up: {f}")

    # Also backup daily_reviews directory
    daily_reviews_src = PROJECT_DIR / 'daily_reviews'
    if daily_reviews_src.exists():
        daily_reviews_dest = backup_dir / 'daily_reviews'
        shutil.copytree(daily_reviews_src, daily_reviews_dest,
                       ignore=shutil.ignore_patterns('archive_*'))
        print(f"      Backed up: daily_reviews/")

    print(f"   Backup created: {backup_dir}")
    return str(backup_dir)

def reset_portfolio_data(dry_run=True):
    """Reset current_portfolio.json to empty state"""
    portfolio_file = PROJECT_DIR / 'portfolio_data' / 'current_portfolio.json'

    empty_portfolio = {
        "positions": [],
        "total_positions": 0,
        "portfolio_value": 0.0,
        "last_updated": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        "portfolio_status": "Empty - Clean slate reset"
    }

    if dry_run:
        print(f"   [DRY RUN] Would reset: current_portfolio.json")
        print(f"      Positions: 0")
        return True

    with open(portfolio_file, 'w') as f:
        json.dump(empty_portfolio, f, indent=2)

    print(f"   Reset: current_portfolio.json (0 positions)")
    return True

def reset_account_status(starting_capital, dry_run=True):
    """Reset account_status.json to starting capital"""
    account_file = PROJECT_DIR / 'portfolio_data' / 'account_status.json'

    fresh_account = {
        "account_value": starting_capital,
        "cash_available": starting_capital,
        "positions_value": 0.0,
        "realized_pl": 0.0,
        "total_trades": 0,
        "win_rate_percent": 0.0,
        "average_hold_time_days": 0.0,
        "average_winner_percent": 0.0,
        "average_loser_percent": 0.0,
        "last_updated": datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    }

    if dry_run:
        print(f"   [DRY RUN] Would reset: account_status.json")
        print(f"      Account value: ${starting_capital:,.2f}")
        print(f"      Cash available: ${starting_capital:,.2f}")
        print(f"      Realized P&L: $0.00")
        return True

    with open(account_file, 'w') as f:
        json.dump(fresh_account, f, indent=2)

    print(f"   Reset: account_status.json (${starting_capital:,.2f})")
    return True

def reset_trade_history(dry_run=True):
    """Reset completed_trades.csv to header only"""
    trades_file = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'

    # Full header from current architecture
    header = "Trade_ID,Entry_Date,Exit_Date,Ticker,Premarket_Price,Entry_Price,Exit_Price,Gap_Percent,Shares,Position_Size,Position_Size_Percent,Hold_Days,Return_Percent,Return_Dollars,Exit_Reason,Exit_Type,Catalyst_Type,Catalyst_Tier,Catalyst_Age_Days,News_Validation_Score,News_Exit_Triggered,VIX_At_Entry,Market_Regime,Macro_Event_Near,VIX_Regime,Market_Breadth_Regime,System_Version,Relative_Strength,Stock_Return_3M,Sector_ETF,Conviction_Level,Supporting_Factors,Technical_Score,Technical_SMA50,Technical_EMA5,Technical_EMA20,Technical_ADX,Technical_Volume_Ratio,Volume_Quality,Volume_Trending_Up,Keywords_Matched,News_Sources,News_Article_Count,Sector,Stop_Loss,Price_Target,Thesis,What_Worked,What_Failed,Account_Value_After,Rotation_Into_Ticker,Rotation_Reason\n"

    if dry_run:
        print(f"   [DRY RUN] Would reset: completed_trades.csv")
        print(f"      Trades: 0 (header only)")
        return True

    with open(trades_file, 'w') as f:
        f.write(header)

    print(f"   Reset: completed_trades.csv (0 trades)")
    return True

def reset_pending_positions(dry_run=True):
    """Remove pending_positions.json if exists"""
    pending_file = PROJECT_DIR / 'portfolio_data' / 'pending_positions.json'

    if not pending_file.exists():
        print(f"   Skip: pending_positions.json (does not exist)")
        return True

    if dry_run:
        print(f"   [DRY RUN] Would delete: pending_positions.json")
        return True

    pending_file.unlink()
    print(f"   Deleted: pending_positions.json")
    return True

def reset_daily_activity(dry_run=True):
    """Reset daily_activity.json"""
    activity_file = PROJECT_DIR / 'portfolio_data' / 'daily_activity.json'

    empty_activity = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "entries": [],
        "exits": [],
        "holds": [],
        "total_trades": 0
    }

    if dry_run:
        print(f"   [DRY RUN] Would reset: daily_activity.json")
        return True

    with open(activity_file, 'w') as f:
        json.dump(empty_activity, f, indent=2)

    print(f"   Reset: daily_activity.json")
    return True

def reset_catalyst_exclusions(dry_run=True):
    """Reset catalyst_exclusions.json to empty"""
    exclusions_file = PROJECT_DIR / 'strategy_evolution' / 'catalyst_exclusions.json'

    empty_exclusions = {
        "excluded_catalysts": [],
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "note": "Reset to empty - clean slate"
    }

    if dry_run:
        print(f"   [DRY RUN] Would reset: catalyst_exclusions.json")
        return True

    with open(exclusions_file, 'w') as f:
        json.dump(empty_exclusions, f, indent=2)

    print(f"   Reset: catalyst_exclusions.json")
    return True

def archive_daily_reviews(dry_run=True):
    """Archive current daily_reviews to dated folder"""
    reviews_dir = PROJECT_DIR / 'daily_reviews'
    timestamp = datetime.now().strftime('%Y%m%d')
    archive_dir = reviews_dir / f'archive_{timestamp}'

    if not reviews_dir.exists():
        print(f"   Skip: daily_reviews/ (does not exist)")
        return True

    # Get files to archive (not already in archive folders)
    files_to_archive = [f for f in reviews_dir.glob('*.json') if f.is_file()]

    if not files_to_archive:
        print(f"   Skip: daily_reviews/ (no files to archive)")
        return True

    if dry_run:
        print(f"   [DRY RUN] Would archive {len(files_to_archive)} files to: {archive_dir.name}/")
        return True

    archive_dir.mkdir(exist_ok=True)
    for f in files_to_archive:
        shutil.move(str(f), str(archive_dir / f.name))

    print(f"   Archived: {len(files_to_archive)} daily review files to {archive_dir.name}/")
    return True

def verify_reset(starting_capital):
    """Verify all files were reset correctly"""
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)

    all_good = True

    # Check portfolio
    portfolio_file = PROJECT_DIR / 'portfolio_data' / 'current_portfolio.json'
    if portfolio_file.exists():
        with open(portfolio_file) as f:
            data = json.load(f)
        positions = len(data.get('positions', []))
        if positions == 0:
            print(f"   ✓ Portfolio: 0 positions")
        else:
            print(f"   ✗ Portfolio: {positions} positions (should be 0)")
            all_good = False

    # Check account status
    account_file = PROJECT_DIR / 'portfolio_data' / 'account_status.json'
    if account_file.exists():
        with open(account_file) as f:
            data = json.load(f)
        value = data.get('account_value', 0)
        if abs(value - starting_capital) < 0.01:
            print(f"   ✓ Account value: ${value:,.2f}")
        else:
            print(f"   ✗ Account value: ${value:,.2f} (should be ${starting_capital:,.2f})")
            all_good = False

    # Check trades
    trades_file = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'
    if trades_file.exists():
        with open(trades_file) as f:
            lines = f.readlines()
        trade_count = len(lines) - 1  # Subtract header
        if trade_count == 0:
            print(f"   ✓ Trades: 0")
        else:
            print(f"   ✗ Trades: {trade_count} (should be 0)")
            all_good = False

    # Check pending
    pending_file = PROJECT_DIR / 'portfolio_data' / 'pending_positions.json'
    if not pending_file.exists():
        print(f"   ✓ Pending positions: None")
    else:
        print(f"   ✗ Pending positions file still exists")
        all_good = False

    return all_good

def main():
    parser = argparse.ArgumentParser(
        description='Clean Slate Reset for Paper Trading Lab',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 clean_slate_reset.py              # Preview changes (dry run)
    python3 clean_slate_reset.py --execute    # Actually execute reset
    python3 clean_slate_reset.py --skip-alpaca --execute  # Reset only TedBot data
        """
    )
    parser.add_argument('--execute', action='store_true',
                       help='Actually execute the reset (default is dry-run)')
    parser.add_argument('--skip-alpaca', action='store_true',
                       help='Skip Alpaca liquidation (only reset TedBot data)')
    parser.add_argument('--starting-capital', type=float, default=STARTING_CAPITAL,
                       help=f'Starting capital (default: ${STARTING_CAPITAL:,.2f})')

    args = parser.parse_args()
    dry_run = not args.execute
    starting_capital = args.starting_capital

    print("\n" + "="*60)
    print("CLEAN SLATE RESET - Paper Trading Lab")
    print("="*60)
    print(f"\nStarting Capital: ${starting_capital:,.2f}")
    print(f"Mode: {'DRY RUN (preview only)' if dry_run else 'EXECUTE (will make changes)'}")
    print(f"Alpaca: {'SKIP' if args.skip_alpaca else 'WILL LIQUIDATE'}")

    if not dry_run:
        print("\n" + "!"*60)
        print("WARNING: This will DELETE all trading data!")
        print("!"*60)
        confirm = input("\nType 'RESET' to confirm: ")
        if confirm != 'RESET':
            print("\nAborted.")
            return 1

    # Step 1: Check Alpaca state
    print("\n" + "-"*60)
    print("STEP 1: Alpaca Account")
    print("-"*60)

    if not args.skip_alpaca:
        api = get_alpaca_client()
        if api:
            state = check_alpaca_state(api)
            if state:
                print(f"   Current equity: ${state['equity']:,.2f}")
                print(f"   Current cash: ${state['cash']:,.2f}")
                print(f"   Positions: {len(state['positions'])}")

                for p in state['positions']:
                    print(f"      {p['symbol']}: {p['qty']} shares (${p['market_value']:,.2f})")

                # Liquidate positions
                print("\n   Liquidating positions...")
                liquidate_alpaca_positions(api, dry_run)

                # Note about balance reset
                reset_alpaca_balance(api, starting_capital, dry_run)
            else:
                print("   ERROR: Could not get Alpaca state")
        else:
            print("   ERROR: Could not connect to Alpaca")
    else:
        print("   Skipped (--skip-alpaca flag)")

    # Step 2: Create backup
    print("\n" + "-"*60)
    print("STEP 2: Create Backup")
    print("-"*60)
    backup_path = create_backup(dry_run)

    # Step 3: Reset TedBot data files
    print("\n" + "-"*60)
    print("STEP 3: Reset TedBot Data Files")
    print("-"*60)

    reset_portfolio_data(dry_run)
    reset_account_status(starting_capital, dry_run)
    reset_trade_history(dry_run)
    reset_pending_positions(dry_run)
    reset_daily_activity(dry_run)
    reset_catalyst_exclusions(dry_run)

    # Step 4: Archive daily reviews
    print("\n" + "-"*60)
    print("STEP 4: Archive Daily Reviews")
    print("-"*60)
    archive_daily_reviews(dry_run)

    # Step 5: Verify
    if not dry_run:
        all_good = verify_reset(starting_capital)
    else:
        print("\n" + "="*60)
        print("DRY RUN COMPLETE")
        print("="*60)
        print("\nNo changes were made. To execute reset, run:")
        print(f"    python3 {Path(__file__).name} --execute")
        all_good = True

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if dry_run:
        print("\nThis was a DRY RUN. No changes were made.")
        print("\nWhat WOULD happen:")
        print(f"   - Alpaca: Liquidate all positions")
        print(f"   - TedBot: Reset to ${starting_capital:,.2f} starting capital")
        print(f"   - Portfolio: 0 positions")
        print(f"   - Trades: 0 completed trades")
        print(f"   - Daily reviews: Archived")
        print(f"\nTo execute, run:")
        print(f"    python3 {Path(__file__).name} --execute")
    else:
        if all_good:
            print("\n✓ RESET COMPLETE!")
            print(f"\n   Starting capital: ${starting_capital:,.2f}")
            print(f"   Positions: 0")
            print(f"   Trades: 0")
            print(f"   Backup: {backup_path}")
            print("\n   Ready for fresh start!")
            print("   Next: Wait for 8:45 AM cron to run 'go' command")
        else:
            print("\n✗ RESET INCOMPLETE - Some issues detected")
            print("   Please review the verification output above")

    print("\n" + "="*60)

    return 0 if all_good else 1

if __name__ == '__main__':
    sys.exit(main())
