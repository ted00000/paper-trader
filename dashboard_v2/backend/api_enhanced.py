#!/usr/bin/env python3
"""
Enhanced Dashboard API - Read-Only Data Layer
Provides comprehensive analytics endpoints without touching trading logic

This API server runs INDEPENDENTLY from the trading agent.
All endpoints are READ-ONLY - they never modify trading data.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from functools import wraps
import json
import csv
import os
import secrets
import hashlib

# Project setup
PROJECT_DIR = Path(__file__).parent.parent.parent
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Authentication credentials (in production, move to environment variables)
VALID_USERNAME = os.getenv('DASHBOARD_USERNAME', 'tedbot')
VALID_PASSWORD_HASH = hashlib.sha256(os.getenv('DASHBOARD_PASSWORD', 'tedbot2025').encode()).hexdigest()

# Super user credentials (can view operation logs)
SUPER_USER_USERNAME = os.getenv('SUPER_USER_USERNAME', 'ted')
SUPER_USER_PASSWORD_HASH = hashlib.sha256(os.getenv('SUPER_USER_PASSWORD', 'SuperTed2025').encode()).hexdigest()

# Session storage (in-memory for MVP, use Redis for production)
active_sessions = {}

def generate_session_token():
    """Generate a secure random session token"""
    return secrets.token_urlsafe(32)

def verify_session(token):
    """Verify if session token is valid"""
    return token in active_sessions

# Data file paths (READ ONLY)
TRADES_CSV = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'
PORTFOLIO_JSON = PROJECT_DIR / 'portfolio_data' / 'current_portfolio.json'
ACCOUNT_JSON = PROJECT_DIR / 'portfolio_data' / 'account_status.json'
CATALYST_CSV = PROJECT_DIR / 'strategy_evolution' / 'catalyst_performance.csv'
LESSONS_MD = PROJECT_DIR / 'strategy_evolution' / 'lessons_learned.md'
EXCLUSIONS_JSON = PROJECT_DIR / 'strategy_evolution' / 'catalyst_exclusions.json'
SCREENER_JSON = PROJECT_DIR / 'screener_candidates.json'

# =====================================================================
# HELPER FUNCTIONS - Data Loading (Read-Only)
# =====================================================================

def load_trades(limit=None, filters=None):
    """Load trades from CSV with optional filtering"""
    trades = []

    if not TRADES_CSV.exists():
        return trades

    with open(TRADES_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Trade_ID'):
                # Apply filters if provided
                if filters:
                    if filters.get('catalyst_tier') and row.get('Catalyst_Tier') != filters['catalyst_tier']:
                        continue
                    if filters.get('min_return') and float(row.get('Return_Percent', 0)) < filters['min_return']:
                        continue
                    if filters.get('max_return') and float(row.get('Return_Percent', 0)) > filters['max_return']:
                        continue

                trades.append(row)

    # Sort by exit date descending
    trades.sort(key=lambda x: x.get('Exit_Date', ''), reverse=True)

    if limit:
        return trades[:limit]
    return trades

def load_portfolio():
    """Load current portfolio"""
    if not PORTFOLIO_JSON.exists():
        return {'positions': [], 'total_positions': 0}

    with open(PORTFOLIO_JSON, 'r') as f:
        return json.load(f)

def load_account():
    """Load account status"""
    if not ACCOUNT_JSON.exists():
        return {
            'account_value': 1000.00,
            'cash_balance': 1000.00,
            'total_return_percent': 0.00,
            'total_return_dollars': 0.00
        }

    with open(ACCOUNT_JSON, 'r') as f:
        data = json.load(f)
    
    # Calculate total return percent from account value vs starting capital
    starting_capital = 1000.00
    account_value = data.get('account_value', starting_capital)
    total_return_pct = ((account_value - starting_capital) / starting_capital) * 100
    # Calculate total return dollars
    total_return_usd = account_value - starting_capital
    data['total_return_percent'] = round(total_return_pct, 2)
    data['total_return_dollars'] = round(total_return_usd, 2)

    # Map cash_available to cash_balance for API compatibility
    if 'cash_available' in data and 'cash_balance' not in data:
        data['cash_balance'] = data['cash_available']
    
    return data

def load_screener_candidates():
    """Load latest screener candidates"""
    if not SCREENER_JSON.exists():
        return {'candidates': [], 'scan_date': None}

    with open(SCREENER_JSON, 'r') as f:
        return json.load(f)

# =====================================================================
# ROOT & DOCUMENTATION
# =====================================================================

# =====================================================================
# AUTHENTICATION ENDPOINTS
# =====================================================================

@app.route('/api/v2/auth/login', methods=['POST'])
def login():
    """Authenticate user and create session"""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    # Hash provided password and compare
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Check if super user
    is_super_user = (username == SUPER_USER_USERNAME and password_hash == SUPER_USER_PASSWORD_HASH)

    # Check if regular user or super user
    if (username == VALID_USERNAME and password_hash == VALID_PASSWORD_HASH) or is_super_user:
        # Generate session token
        token = generate_session_token()
        active_sessions[token] = {
            'username': username,
            'is_super_user': is_super_user,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'token': token,
            'username': username,
            'is_super_user': is_super_user
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Invalid username or password'
        }), 401

@app.route('/api/v2/auth/verify', methods=['GET'])
def verify():
    """Verify session token is valid"""
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return jsonify({'valid': False}), 401

    token = auth_header[7:]  # Remove 'Bearer ' prefix

    if verify_session(token):
        # Update last activity
        active_sessions[token]['last_activity'] = datetime.now().isoformat()
        return jsonify({
            'valid': True,
            'is_super_user': active_sessions[token].get('is_super_user', False)
        })
    else:
        return jsonify({'valid': False}), 401

@app.route('/api/v2/auth/logout', methods=['POST'])
def logout():
    """End session"""
    auth_header = request.headers.get('Authorization', '')

    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        if token in active_sessions:
            del active_sessions[token]

    return jsonify({'success': True})

@app.route('/', methods=['GET'])
def root():
    """API Documentation - Root endpoint"""
    return jsonify({
        'name': 'TEDBOT Enhanced Dashboard API',
        'version': '2.0',
        'description': 'Read-only API for TEDBOT trading dashboard',
        'frontend': 'http://localhost:3000',
        'endpoints': {
            'auth': {
                'login': '/api/v2/auth/login',
                'verify': '/api/v2/auth/verify',
                'logout': '/api/v2/auth/logout'
            },
            'health': '/api/v2/health',
            'overview': '/api/v2/overview',
            'equity_curve': '/api/v2/equity-curve',
            'catalyst_performance': '/api/v2/catalyst-performance',
            'trades': '/api/v2/trades',
            'risk_positions': '/api/v2/risk/positions',
            'monthly_returns': '/api/v2/analytics/monthly-returns',
            'learning_insights': '/api/v2/learning/insights'
        },
        'note': 'This is a READ-ONLY API. It never modifies trading data.',
        'docs': 'See README.md in dashboard_v2/ for full documentation'
    })

# =====================================================================
# ANALYTICS ENDPOINTS
# =====================================================================

@app.route('/api/v2/overview', methods=['GET'])
def get_overview():
    """
    Command Center Overview - All key metrics in one call

    Returns:
        - Account metrics
        - Performance stats
        - Recent trades
        - Current positions
        - Market regime
    """
    trades = load_trades(limit=100)
    portfolio = load_portfolio()
    account = load_account()

    # Calculate performance metrics
    total_trades = len(trades)
    winners = sum(1 for t in trades if float(t.get('Return_Percent', 0)) > 0)
    win_rate = (winners / total_trades * 100) if total_trades > 0 else 0

    # Calculate returns
    returns = [float(t.get('Return_Percent', 0)) for t in trades]
    avg_return = sum(returns) / len(returns) if returns else 0

    # Calculate avg gain and avg loss
    winning_returns = [r for r in returns if r > 0]
    losing_returns = [r for r in returns if r < 0]
    avg_gain = sum(winning_returns) / len(winning_returns) if winning_returns else 0
    avg_loss = sum(losing_returns) / len(losing_returns) if losing_returns else 0

    # Calculate YTD and MTD returns
    from datetime import datetime
    current_year = datetime.now().year
    current_month = datetime.now().month

    ytd_trades = [t for t in trades if t.get('Exit_Date', '').startswith(str(current_year))]
    ytd_returns = [float(t.get('Return_Percent', 0)) for t in ytd_trades]
    ytd_return = sum(ytd_returns) if ytd_returns else 0

    current_month_str = f"{current_year}-{current_month:02d}"
    mtd_trades = [t for t in trades if t.get('Exit_Date', '').startswith(current_month_str)]
    mtd_returns = [float(t.get('Return_Percent', 0)) for t in mtd_trades]
    mtd_return = sum(mtd_returns) if mtd_returns else 0

    # Calculate Sharpe ratio (simplified)
    import numpy as np
    if len(returns) > 1:
        sharpe = (np.mean(returns) / np.std(returns)) * (252 ** 0.5) if np.std(returns) > 0 else 0
    else:
        sharpe = 0

    # Max drawdown
    equity_curve = [1000.00]  # Start with initial capital
    cumulative = 1000.00
    for t in reversed(trades):  # Chronological order
        cumulative += float(t.get('Return_Dollars', 0))
        equity_curve.append(cumulative)

    peak = 1000.00  # Peak starts at initial capital
    max_dd = 0
    for value in equity_curve:
        if value > peak:
            peak = value
        dd = ((peak - value) / peak) * 100
        if dd > max_dd:
            max_dd = dd


    # Today's performance (from closed trades today)
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_trades = [t for t in trades if t.get('Exit_Date', '').startswith(today_str)]
    today_returns = [float(t.get('Return_Percent', 0)) for t in today_trades]
    today_pnl = sum(today_returns) if today_returns else 0
    today_wins = sum(1 for r in today_returns if r > 0)
    today_losses = sum(1 for r in today_returns if r < 0)
    return jsonify({
        'account': {
            'value': account.get('account_value', 1000.00),
            'cash': account.get('cash_balance', 1000.00),
            'invested': account.get('positions_value', 0.00),
            'total_return_pct': account.get('total_return_percent', 0.00),
            'total_return_usd': account.get('total_return_dollars', 0.00)
        },
        'performance': {
            'total_trades': total_trades,
            'win_rate': round(win_rate, 1),
            'avg_return': round(avg_return, 2),
            'avg_gain': round(avg_gain, 2),
            'avg_loss': round(avg_loss, 2),
            'ytd_return': round(ytd_return, 2),
            'mtd_return': round(mtd_return, 2),
            'sharpe_ratio': round(sharpe, 2),
            'max_drawdown': round(max_dd, 2)
        },
        'today': {
            'trades': len(today_trades),
            'wins': today_wins,
            'losses': today_losses,
            'pnl': round(today_pnl, 2)
        },
        'recent_trades': [
            {
                'ticker': t.get('Ticker'),
                'return_pct': float(t.get('Return_Percent', 0)),
                'hold_days': int(t.get('Hold_Days', 0)),
                'exit_date': t.get('Exit_Date'),
                'catalyst': t.get('Catalyst_Type'),
                'exit_reason': t.get('Exit_Reason')
            }
            for t in trades[:10]
        ],
        'positions': [
            {
                'ticker': p.get('ticker'),
                'entry_price': p.get('entry_price'),
                'current_price': p.get('current_price'),
                'unrealized_pnl_pct': p.get('unrealized_gain_pct', 0),
                'days_held': p.get('days_held', 0),
                'position_size': p.get('position_size', 0)
            }
            for p in portfolio.get('positions', [])
        ]
    })

@app.route('/api/v2/performance', methods=['GET'])
def get_performance():
    """
    Performance metrics endpoint (alias for overview performance data)
    Used by Today page for performance cards
    """
    trades = load_trades(limit=100)

    # Calculate performance metrics
    total_trades = len(trades)
    winners = sum(1 for t in trades if float(t.get('Return_Percent', 0)) > 0)
    losers = sum(1 for t in trades if float(t.get('Return_Percent', 0)) < 0)
    win_rate = (winners / total_trades * 100) if total_trades > 0 else 0

    # Calculate returns
    returns = [float(t.get('Return_Percent', 0)) for t in trades]
    avg_return = sum(returns) / len(returns) if returns else 0

    # Calculate avg gain and avg loss
    winning_returns = [r for r in returns if r > 0]
    losing_returns = [r for r in returns if r < 0]
    avg_gain = sum(winning_returns) / len(winning_returns) if winning_returns else 0
    avg_loss = sum(losing_returns) / len(losing_returns) if losing_returns else 0

    # Calculate YTD and MTD returns
    from datetime import datetime
    current_year = datetime.now().year
    current_month = datetime.now().month

    ytd_trades = [t for t in trades if t.get('Exit_Date', '').startswith(str(current_year))]
    ytd_returns = [float(t.get('Return_Percent', 0)) for t in ytd_trades]
    ytd_return = sum(ytd_returns) if ytd_returns else 0

    current_month_str = f"{current_year}-{current_month:02d}"
    mtd_trades = [t for t in trades if t.get('Exit_Date', '').startswith(current_month_str)]
    mtd_returns = [float(t.get('Return_Percent', 0)) for t in mtd_trades]
    mtd_return = sum(mtd_returns) if mtd_returns else 0

    # Calculate Sharpe ratio (simplified)
    import numpy as np
    if len(returns) > 1:
        sharpe_ratio = (np.mean(returns) / np.std(returns)) * (252 ** 0.5) if np.std(returns) > 0 else 0
    else:
        sharpe_ratio = 0

    # Max drawdown
    equity_curve = [1000.00]  # Start with initial capital
    cumulative = 1000.00
    for t in reversed(trades):  # Chronological order
        cumulative += float(t.get('Return_Dollars', 0))
        equity_curve.append(cumulative)

    peak = 1000.00  # Peak starts at initial capital
    max_drawdown = 0
    for value in equity_curve:
        if value > peak:
            peak = value
        dd = ((peak - value) / peak) * 100
        if dd > max_drawdown:
            max_drawdown = dd

    # Today's performance (from closed trades today)
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_trades = [t for t in trades if t.get('Exit_Date', '').startswith(today_str)]
    today_returns = [float(t.get('Return_Percent', 0)) for t in today_trades]
    today_pnl = sum(today_returns) if today_returns else 0
    today_wins = sum(1 for r in today_returns if r > 0)
    today_losses = sum(1 for r in today_returns if r < 0)

    return jsonify({
        'total_trades': total_trades,
        'win_rate': round(win_rate, 2),
        'avg_return': round(avg_return, 2),
        'avg_gain': round(avg_gain, 2),
        'avg_loss': round(avg_loss, 2),
        'ytd_return': round(ytd_return, 2),
        'mtd_return': round(mtd_return, 2),
        'max_drawdown': round(max_drawdown, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'today': {
            'trades': len(today_trades),
            'wins': today_wins,
            'losses': today_losses,
            'pnl': round(today_pnl, 2)
        }
    })

@app.route('/api/v2/equity-curve', methods=['GET'])
def get_equity_curve():
    """
    Equity curve data for charting

    Query params:
        - period: 30d, 90d, 1y, all (default: all)

    Returns:
        - Array of {date, value, drawdown_pct}
    """
    trades = load_trades()
    period = request.args.get('period', 'all')

    # Filter by period
    if period != 'all':
        days = {'30d': 30, '90d': 90, '1y': 365}.get(period, 999999)
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        trades = [t for t in trades if t.get('Exit_Date', '') >= cutoff]

    # Build equity curve
    equity_points = []
    cumulative = 1000.00
    peak = 1000.00

    # Sort chronologically
    trades.sort(key=lambda x: x.get('Exit_Date', ''))

    for trade in trades:
        cumulative += float(trade.get('Return_Dollars', 0))

        if cumulative > peak:
            peak = 1000.00  # Peak starts at initial capital

        drawdown_pct = ((peak - cumulative) / peak) * 100 if peak > 0 else 0

        equity_points.append({
            'date': trade.get('Exit_Date'),
            'value': round(cumulative, 2),
            'drawdown_pct': round(drawdown_pct, 2),
            'peak': round(peak, 2)
        })

    return jsonify({
        'equity_curve': equity_points,
        'starting_value': 1000.00,
        'current_value': round(cumulative, 2),
        'total_return_pct': round(((cumulative - 1000) / 1000) * 100, 2)
    })

@app.route('/api/v2/catalyst-performance', methods=['GET'])
def get_catalyst_performance():
    """
    Catalyst performance breakdown

    Returns:
        - Performance by catalyst type
        - Performance by tier
        - Performance by conviction level
    """
    trades = load_trades()

    # Group by catalyst type
    by_catalyst = defaultdict(lambda: {'trades': [], 'wins': 0, 'total': 0})
    by_tier = defaultdict(lambda: {'trades': [], 'wins': 0, 'total': 0})
    by_conviction = defaultdict(lambda: {'trades': [], 'wins': 0, 'total': 0})

    for trade in trades:
        catalyst = trade.get('Catalyst_Type', 'Unknown')
        tier = trade.get('Catalyst_Tier', 'Unknown')
        conviction = trade.get('Conviction_Level', 'MEDIUM')
        return_pct = float(trade.get('Return_Percent', 0))

        # By catalyst
        by_catalyst[catalyst]['trades'].append(return_pct)
        by_catalyst[catalyst]['total'] += 1
        if return_pct > 0:
            by_catalyst[catalyst]['wins'] += 1

        # By tier
        by_tier[tier]['trades'].append(return_pct)
        by_tier[tier]['total'] += 1
        if return_pct > 0:
            by_tier[tier]['wins'] += 1

        # By conviction
        by_conviction[conviction]['trades'].append(return_pct)
        by_conviction[conviction]['total'] += 1
        if return_pct > 0:
            by_conviction[conviction]['wins'] += 1

    # Format results
    def format_group(group_dict):
        return [
            {
                'name': name,
                'total_trades': stats['total'],
                'win_rate': round((stats['wins'] / stats['total']) * 100, 1) if stats['total'] > 0 else 0,
                'avg_return': round(sum(stats['trades']) / len(stats['trades']), 2) if stats['trades'] else 0,
                'total_return': round(sum(stats['trades']), 2)
            }
            for name, stats in group_dict.items()
        ]

    return jsonify({
        'by_catalyst': format_group(by_catalyst),
        'by_tier': format_group(by_tier),
        'by_conviction': format_group(by_conviction)
    })

@app.route('/api/v2/trades', methods=['GET'])
def get_trades():
    """
    Trade search/filter endpoint

    Query params:
        - limit: number of trades
        - catalyst_tier: filter by tier
        - min_return: minimum return %
        - max_return: maximum return %
        - search: search ticker/catalyst
    """
    limit = int(request.args.get('limit', 50))
    filters = {}

    if request.args.get('catalyst_tier'):
        filters['catalyst_tier'] = request.args.get('catalyst_tier')
    if request.args.get('min_return'):
        filters['min_return'] = float(request.args.get('min_return'))
    if request.args.get('max_return'):
        filters['max_return'] = float(request.args.get('max_return'))

    trades = load_trades(limit=limit, filters=filters)

    # Search filter
    search = request.args.get('search', '').lower()
    if search:
        trades = [
            t for t in trades
            if search in t.get('Ticker', '').lower() or
               search in t.get('Catalyst_Type', '').lower()
        ]

    return jsonify({
        'trades': trades,
        'total': len(trades)
    })

@app.route('/api/v2/risk/positions', methods=['GET'])
def get_risk_positions():
    """Current positions with risk metrics"""
    portfolio = load_portfolio()

    positions_with_risk = []
    for pos in portfolio.get('positions', []):
        entry_price = pos.get('entry_price', 0)
        current_price = pos.get('current_price', 0)
        stop_loss = pos.get('stop_loss', 0)
        price_target = pos.get('price_target', entry_price * 1.10)

        # Calculate distances to stop/target
        stop_distance_pct = ((current_price - stop_loss) / current_price * 100) if current_price > 0 else 0
        target_distance_pct = ((price_target - current_price) / current_price * 100) if current_price > 0 else 0

        positions_with_risk.append({
            'ticker': pos.get('ticker'),
            'entry_price': entry_price,
            'current_price': current_price,
            'stop_loss': stop_loss,
            'price_target': price_target,
            'unrealized_pnl_pct': pos.get('unrealized_gain_pct', 0),
            'position_size': pos.get('position_size', 0),
            'days_held': pos.get('days_held', 0),
            'stop_distance_pct': round(stop_distance_pct, 2),
            'target_distance_pct': round(target_distance_pct, 2),
            'risk_level': 'HIGH' if stop_distance_pct < 3 else 'MEDIUM' if stop_distance_pct < 5 else 'LOW'
        })

    return jsonify({
        'positions': positions_with_risk,
        'total_count': len(positions_with_risk)
    })

@app.route('/api/v2/analytics/monthly-returns', methods=['GET'])
def get_monthly_returns():
    """Monthly returns for calendar heatmap"""
    trades = load_trades()

    monthly_returns = defaultdict(float)

    for trade in trades:
        exit_date = trade.get('Exit_Date', '')
        if exit_date:
            try:
                # Extract year-month
                year_month = exit_date[:7]  # YYYY-MM
                return_dollars = float(trade.get('Return_Dollars', 0))
                monthly_returns[year_month] += return_dollars
            except:
                continue

    # Format for frontend
    result = [
        {
            'month': month,
            'return_usd': round(returns, 2),
            'return_pct': 0  # Would need starting capital per month
        }
        for month, returns in sorted(monthly_returns.items())
    ]

    return jsonify({
        'monthly_returns': result
    })

@app.route('/api/v2/learning/insights', methods=['GET'])
def get_learning_insights():
    """Learning system insights (placeholder)"""
    return jsonify({
        'daily_loops': 0,
        'weekly_loops': 0,
        'monthly_loops': 0,
        'total_patterns': 0,
        'recent_insights': []
    })

@app.route('/api/v2/operations/status', methods=['GET'])
def get_operations_status():
    """
    Get status of all system operations (SCREENER, GO, EXECUTE, ANALYZE, LEARN_*)

    Returns:
        - Operation name
        - Last run timestamp
        - Status (SUCCESS/FAILED/NEVER_RUN)
        - Stats (for screener: candidates, breadth, etc.)
    """
    operations = {}

    # Check daily_reviews for GO/EXECUTE/ANALYZE operations
    daily_reviews_dir = PROJECT_DIR / 'daily_reviews'
    if daily_reviews_dir.exists():
        for operation in ['go', 'execute', 'analyze']:
            pattern = f"{operation}_*.json"
            files = sorted(daily_reviews_dir.glob(pattern), reverse=True)

            if files:
                latest_file = files[0]
                # Extract timestamp from filename (e.g., go_20251218_153944.json)
                filename = latest_file.name
                parts = filename.replace('.json', '').split('_')
                if len(parts) >= 3:
                    timestamp_str = parts[2]
                    # Format: HHMMSS -> HH:MM:SS
                    timestamp = f"{parts[1][:4]}-{parts[1][4:6]}-{parts[1][6:8]} {timestamp_str[:2]}:{timestamp_str[2:4]}:{timestamp_str[4:]}"

                    try:
                        with open(latest_file) as f:
                            data = json.load(f)

                        operations[operation.upper()] = {
                            'status': 'SUCCESS',
                            'last_run': timestamp,
                            'health': 'HEALTHY',
                            'log_file': str(latest_file),
                            'summary': f"Latest {operation} command completed"
                        }
                    except Exception as e:
                        operations[operation.upper()] = {
                            'status': 'FAILED',
                            'last_run': timestamp,
                            'health': 'FAILED',
                            'error': str(e)
                        }
            else:
                operations[operation.upper()] = {
                    'status': 'NEVER_RUN',
                    'last_run': None,
                    'health': 'UNKNOWN'
                }

    # Check screener_candidates.json for SCREENER operation
    if SCREENER_JSON.exists():
        try:
            with open(SCREENER_JSON) as f:
                screener_data = json.load(f)

            # Get file modification time
            import os
            mod_time = datetime.fromtimestamp(os.path.getmtime(SCREENER_JSON))

            operations['SCREENER'] = {
                'status': 'SUCCESS',
                'last_run': mod_time.isoformat(),
                'health': 'HEALTHY',
                'stats': {
                    'candidates_found': len(screener_data.get('candidates', [])),
                    'scan_date': screener_data.get('scan_date', 'Unknown')
                }
            }
        except Exception as e:
            operations['SCREENER'] = {
                'status': 'FAILED',
                'last_run': None,
                'health': 'FAILED',
                'error': str(e)
            }
    else:
        operations['SCREENER'] = {
            'status': 'NEVER_RUN',
            'last_run': None,
            'health': 'UNKNOWN'
        }

    # Determine overall health
    overall_health = 'HEALTHY'
    for op_status in operations.values():
        if op_status.get('health') == 'FAILED':
            overall_health = 'UNHEALTHY'
            break
        elif op_status.get('health') == 'UNKNOWN':
            if overall_health == 'HEALTHY':
                overall_health = 'WARNING'

    return jsonify({
        'operations': operations,
        'health': overall_health,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/v2/operations/logs/<operation>', methods=['GET'])
def get_operation_log(operation):
    """
    Get log/output for a specific operation

    Returns the most recent daily_reviews JSON content for GO/EXECUTE/ANALYZE
    Returns screener_candidates.json for SCREENER
    Matches old dashboard behavior: shows today's log or falls back to most recent
    """
    valid_operations = ['go', 'execute', 'analyze', 'screener']
    operation = operation.lower()

    if operation not in valid_operations:
        return jsonify({'error': 'Invalid operation'}), 400

    # Handle SCREENER operation - show screener_candidates.json
    if operation == 'screener':
        screener_file = PROJECT_DIR / 'screener_candidates.json'
        if not screener_file.exists():
            return jsonify({
                'error': 'No screener output found',
                'operation': 'SCREENER',
                'content': 'Screener has not been run yet.'
            }), 404

        try:
            with open(screener_file) as f:
                data = json.load(f)

            # Format the screener output nicely with markdown styling
            output_lines = []
            output_lines.append("# 📊 SCREENER RESULTS")
            output_lines.append("")
            output_lines.append(f"**Scan Date:** {data.get('scan_date', 'Unknown')}")
            output_lines.append(f"**Scan Time:** {data.get('scan_time', 'Unknown')}")
            output_lines.append(f"**Universe Size:** {data.get('universe_size', 0):,}")
            output_lines.append(f"**Candidates Found:** {data.get('candidates_found', 0)}")
            output_lines.append("")
            output_lines.append("---")
            output_lines.append("")

            candidates = data.get('candidates', [])
            if candidates:
                output_lines.append(f"## ✅ CANDIDATES ({len(candidates)})")
                output_lines.append("")
                for i, candidate in enumerate(candidates, 1):
                    ticker = candidate.get('ticker', 'N/A')
                    score = candidate.get('composite_score', 0)
                    output_lines.append(f"### {i}. **{ticker}** <span style='color: #00ff41'>Score: {score:.2f}</span>")
                    output_lines.append(f"- **Sector:** {candidate.get('sector', 'Unknown')}")
                    output_lines.append(f"- **Price:** ${candidate.get('price', 0):.2f}")

                    # Catalyst info
                    catalyst = candidate.get('catalyst_signals', {})
                    if catalyst.get('count', 0) > 0:
                        keywords = ', '.join(catalyst.get('keywords', []))
                        output_lines.append(f"- **Catalysts:** <span style='color: #00ff41'>{catalyst.get('count')}</span> - {keywords}")

                    output_lines.append("")
            else:
                output_lines.append("No candidates found matching criteria.")

            content = "\n".join(output_lines)

            # Get file modification time
            import os
            mod_time = datetime.fromtimestamp(os.path.getmtime(screener_file))

            return jsonify({
                'operation': 'SCREENER',
                'log_file': str(screener_file),
                'timestamp': mod_time.strftime('%Y-%m-%d %H:%M:%S'),
                'is_today': mod_time.date() == datetime.now().date(),
                'content': content
            })

        except Exception as e:
            return jsonify({
                'error': f'Error reading screener output: {str(e)}',
                'operation': 'SCREENER'
            }), 500

    # Handle GO/EXECUTE/ANALYZE operations
    daily_reviews_dir = PROJECT_DIR / 'daily_reviews'
    if not daily_reviews_dir.exists():
        return jsonify({'error': 'No daily reviews directory found'}), 404

    # First try today's logs
    today = datetime.now().strftime('%Y%m%d')
    pattern_today = f"{operation}_{today}_*.json"
    files_today = sorted(daily_reviews_dir.glob(pattern_today), reverse=True)

    # If no logs today, find the most recent log from any date
    if not files_today:
        pattern_all = f"{operation}_*.json"
        files_all = sorted(daily_reviews_dir.glob(pattern_all), reverse=True)

        if not files_all:
            return jsonify({
                'error': 'No logs found',
                'operation': operation,
                'content': f'No {operation.upper()} command has ever been run.'
            }), 404

        latest_file = files_all[0]
        is_today = False
    else:
        latest_file = files_today[0]
        is_today = True

    try:
        with open(latest_file) as f:
            data = json.load(f)

        # Extract text content from Claude response OR format structured execute log
        content = data.get('content', [{}])[0].get('text', '')

        # If no content, check if this is a structured execute log
        if not content and operation == 'execute' and 'summary' in data:
            # Format execute log nicely
            summary = data.get('summary', {})
            closed_trades = data.get('closed_trades', [])
            new_entries = data.get('new_entries', [])
            timestamp = data.get('timestamp', 'Unknown')

            lines = []
            lines.append('# EXECUTE Results')
            lines.append('')
            lines.append(f'**Timestamp:** {timestamp}')
            lines.append('')
            lines.append('## Summary')
            lines.append('')
            lines.append(f'- **Holding:** {summary.get("holding", 0)} positions')
            lines.append(f'- **New Entries:** {summary.get("entered", 0)}')
            lines.append(f'- **Closed:** {summary.get("closed", 0)}')
            lines.append(f'- **Total Active:** {summary.get("total_active", 0)}')
            lines.append('')

            if new_entries:
                lines.append('## New Entries')
                lines.append('')
                for entry in new_entries:
                    ticker = entry.get('ticker', 'N/A')
                    price = entry.get('entry_price', 0)
                    lines.append(f'- **{ticker}** @ ${price:.2f}')
                lines.append('')

            if closed_trades:
                lines.append('## Closed Trades')
                lines.append('')
                for trade in closed_trades:
                    ticker = trade.get('ticker', 'N/A')
                    exit_price = trade.get('exit_price', 0)
                    pnl = trade.get('pnl_pct', 0)
                    reason = trade.get('reason', 'Unknown')
                    lines.append(f'- **{ticker}** @ ${exit_price:.2f} ({pnl:+.2f}%) - {reason}')
                lines.append('')

            if not new_entries and not closed_trades:
                lines.append('*No trades executed this session.*')

            content = '\n'.join(lines)

        # Extract date and timestamp from filename (e.g., go_20251218_153944.json)
        filename = latest_file.name
        parts = filename.replace('.json', '').split('_')
        date_str = parts[1]  # 20251218
        time_str = parts[2]  # 153944

        # Format date: 2025-12-18
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        # Format time: 15:39:44
        formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"

        # Clean up the content for better display
        import re

        # Remove JSON code blocks (```json ... ```)
        content = re.sub(r'```json\s*\n.*?\n```', '', content, flags=re.DOTALL)

        # Extract Portfolio Status and Reasoning before removing
        portfolio_status = None
        reasoning_text = None
        status_match = re.search(r'\*\*Portfolio Status:\*\* ([^\n]+)', content)
        reasoning_match = re.search(r'\*\*Reasoning:\*\* ([^\n]+)', content)

        if status_match:
            portfolio_status = status_match.group(1)
        if reasoning_match:
            reasoning_text = reasoning_match.group(1)

        # Remove orphaned Portfolio Status/Reasoning lines (that appeared after JSON)
        content = re.sub(r'\n*\*\*Portfolio Status:\*\*[^\n]*\n\*\*Reasoning:\*\*[^\n]*', '', content)

        # Style main title with green
        content = re.sub(
            r'^# ([^\n]+)$',
            r'# <span style="color: #00ff41">\1</span>',
            content,
            flags=re.MULTILINE,
            count=1
        )

        # Style critical sections
        content = re.sub(
            r'(ZERO TIER 1 CATALYSTS IDENTIFIED)',
            r'<span style="color: #ff0033; font-weight: bold;">\1</span>',
            content
        )

        # Style the override section
        content = re.sub(
            r'## 🚨 IF YOU WANT TO OVERRIDE',
            r'## 🚨 <span style="color: #00ff41">IF YOU WANT TO OVERRIDE</span>',
            content
        )

        # Style "Override Tier 1 requirement..." text with emphasis
        content = re.sub(
            r'"(Override Tier 1 requirement[^"]*)"',
            r'<span style="color: #00ff41; font-weight: bold;">"\1"</span>',
            content
        )

        # Style FINAL DECISION section
        content = re.sub(
            r'## ✅ FINAL DECISION',
            r'## <span style="color: #00ff41">✅ FINAL DECISION</span>',
            content
        )

        # Style recommendation text
        content = re.sub(
            r'(I recommend ZERO positions today\.)',
            r'<span style="color: #00ff41; font-weight: bold;">\1</span>',
            content
        )

        # Add formatted summary box at the end if we have the data
        if portfolio_status and reasoning_text:
            summary_box = '\n\n---\n\n'
            summary_box += '## 📋 <span style="color: #00ff41">SUMMARY</span>\n\n'
            summary_box += f'**Portfolio Status:** <span style="color: #00ff41">{portfolio_status}</span>\n\n'
            summary_box += f'**Reasoning:** {reasoning_text}\n'

            content = content + summary_box

        # Add note if not from today
        if not is_today:
            note = f"(No logs found for today - showing most recent run from {formatted_date})\n\n"
            content = note + content

        return jsonify({
            'operation': operation.upper(),
            'log_file': str(latest_file),
            'timestamp': f"{formatted_date} {formatted_time}",
            'is_today': is_today,
            'content': content
        })

    except Exception as e:
        return jsonify({
            'error': f'Error reading log: {str(e)}',
            'operation': operation
        }), 500

@app.route('/api/v2/screening-decisions', methods=['GET'])
def get_screening_decisions():
    """
    Get today screening decisions from GO log
    Returns all stocks analyzed (ENTER and REJECTED) with their details
    """
    import re

    # Find most recent GO log
    daily_reviews_dir = PROJECT_DIR / 'daily_reviews'
    go_files = sorted(daily_reviews_dir.glob('go_*.json'), reverse=True)

    if not go_files:
        return jsonify({
            'decisions': [],
            'summary': 'No screening data available - run GO command',
            'timestamp': None,
            'is_today': False,
            'total_reviewed': 0
        })

    latest_go = go_files[0]

    try:
        with open(latest_go) as f:
            data = json.load(f)

        content = data.get('content', [{}])[0].get('text', '')

        # Extract date from filename (go_YYYYMMDD_HHMMSS.json)
        filename = latest_go.name
        date_match = re.search(r'go_(\d{8})_(\d{6})', filename)
        if date_match:
            file_date = date_match.group(1)
            file_time = date_match.group(2)
            data_date = f'{file_date[:4]}-{file_date[4:6]}-{file_date[6:8]}'
            data_time = f'{file_time[:2]}:{file_time[2:4]}:{file_time[4:6]}'
            timestamp = f'{data_time} ET'
        else:
            data_date = ''
            timestamp = ''

        today = datetime.now().strftime('%Y-%m-%d')
        is_today = (data_date == today)

        decisions = []

        # Load screener data for scores (used as fallback for all stocks)
        screener_file = PROJECT_DIR / 'screener_candidates.json'
        screener_scores = {}
        if screener_file.exists():
            try:
                with open(screener_file) as f:
                    screener_data = json.load(f)
                for c in screener_data.get('candidates', []):
                    t = c.get('ticker')
                    screener_scores[t] = {
                        'score': c.get('composite_score', 0),
                        'rs': c.get('relative_strength', {}).get('rs_pct', 0),
                        'sector': c.get('sector', 'Unknown')
                    }
            except:
                pass

        # Parse BUY decisions from JSON block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                decisions_json = json.loads(json_match.group(1))
                for b in decisions_json.get('buy', []):
                    ticker = b.get('ticker', '')
                    catalyst = b.get('catalyst', 'Unknown')
                    confidence = b.get('confidence_level', 'MEDIUM')
                    size_pct = b.get('position_size_pct', 0)

                    # Determine display decision
                    if size_pct == 0:
                        decision = 'Accepted (Low Conviction - 0% size)'
                    else:
                        decision = f'Accepted ({confidence} conviction)'

                    # Extract score from content - look for "Score:** XX.X"
                    score_match = re.search(rf'\*\*{ticker}.*?Score:\*\*\s*([\d.]+)', content, re.DOTALL)
                    score = float(score_match.group(1)) if score_match else size_pct * 10

                    # Extract RS from content
                    rs_match = re.search(rf'{ticker}.*?\*\*RS:\*\*.*?([+-]?[\d.]+)%', content, re.DOTALL)
                    rs = float(rs_match.group(1)) if rs_match else 0

                    decisions.append({
                        'ticker': ticker,
                        'decision': decision,
                        'status': 'ACCEPTED',
                        'reason': f'Catalyst: {catalyst} | Tier: Tier1 | RS: {rs:.1f}%',
                        'score': score,
                        'conviction': confidence,
                        'size_pct': size_pct,
                        'tier': 'Tier1' if size_pct >= 8 else 'Tier2'
                    })
            except json.JSONDecodeError:
                pass

        # Parse PASS decisions with detailed analysis
        # Pattern: ### N. **TICKER (Sector) - PASS**
        pass_pattern = r'####? \*\*\d+\. ([A-Z]+) \(([^)]+)\) - Score [\d.]+ - PASS'
        for match in re.finditer(pass_pattern, content):
            ticker = match.group(1)
            sector = match.group(2)

            # Extract score - look for "Score:** XX.X" pattern
            score_match = re.search(rf'\*\*{ticker}.*?Score:\*\*\s*([\d.]+)', content, re.DOTALL)
            score = float(score_match.group(1)) if score_match else 0

            # Get RS from screener (more reliable than parsing Claude's text)
            screener_info = screener_scores.get(ticker, {})
            rs = screener_info.get('rs', 0)

            decisions.append({
                'ticker': ticker,
                'decision': 'Rejected',
                'status': 'REJECTED',
                'reason': f'Sector: {sector} | RS: {rs:.1f}%',
                'score': score,
                'conviction': 'SKIP',
                'size_pct': 0,
                'tier': 'N/A'
            })

        # Parse "Other Candidates" brief rejects - get scores from screener
        other_match = re.search(r'\*\*Other Candidates \(([^)]+)\).*?PASS', content)
        if other_match:
            other_tickers = [t.strip() for t in other_match.group(1).split(',')]
            for ticker in other_tickers:
                screener_info = screener_scores.get(ticker, {})
                score = screener_info.get('score', 0)
                rs = screener_info.get('rs', 0)
                sector = screener_info.get('sector', 'Unknown')

                decisions.append({
                    'ticker': ticker,
                    'decision': 'Rejected',
                    'status': 'REJECTED',
                    'reason': f'Sector: {sector} | RS: {rs:.1f}%',
                    'score': score,
                    'conviction': 'SKIP',
                    'size_pct': 0,
                    'tier': 'N/A'
                })

        # Sort: Accepted first, then by score descending
        decisions.sort(key=lambda x: (0 if x['status'] == 'ACCEPTED' else 1, -x['score']))

        # Build summary
        accepted = sum(1 for d in decisions if d['status'] == 'ACCEPTED')
        rejected = sum(1 for d in decisions if d['status'] == 'REJECTED')
        total = len(decisions)

        if total == 0:
            summary = 'No stocks analyzed yet'
        elif accepted == 0:
            summary = f'Analyzed {total} stocks - None met criteria'
        else:
            summary = f'Analyzed {total} stocks - {accepted} accepted, {rejected} rejected'

        return jsonify({
            'decisions': decisions,
            'summary': summary,
            'timestamp': timestamp,
            'is_today': is_today,
            'total_reviewed': total
        })

    except Exception as e:
        return jsonify({
            'error': f'Error loading screening decisions: {str(e)}',
            'decisions': [],
            'summary': 'Error loading data',
            'timestamp': None,
            'is_today': False,
            'total_reviewed': 0
        }), 500

@app.route('/api/v2/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0',
        'timestamp': datetime.now().isoformat()
    })

# =====================================================================
# START SERVER
# =====================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("TEDBOT ENHANCED DASHBOARD API v2.0")
    print("=" * 60)
    print(f"Data directory: {PROJECT_DIR}")
    print(f"Trades file: {TRADES_CSV.exists()}")
    print(f"Portfolio file: {PORTFOLIO_JSON.exists()}")
    print("\nStarting API server on http://localhost:5001")
    print("This is a READ-ONLY API - it never modifies trading data")
    print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5001, debug=True)
