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
import json
import csv
import os

# Project setup
PROJECT_DIR = Path(__file__).parent.parent.parent
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

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
            'total_return_percent': 0.00
        }

    with open(ACCOUNT_JSON, 'r') as f:
        return json.load(f)

def load_screener_candidates():
    """Load latest screener candidates"""
    if not SCREENER_JSON.exists():
        return {'candidates': [], 'scan_date': None}

    with open(SCREENER_JSON, 'r') as f:
        return json.load(f)

# =====================================================================
# ROOT & DOCUMENTATION
# =====================================================================

@app.route('/', methods=['GET'])
def root():
    """API Documentation - Root endpoint"""
    return jsonify({
        'name': 'TEDBOT Enhanced Dashboard API',
        'version': '2.0',
        'description': 'Read-only API for TEDBOT trading dashboard',
        'frontend': 'http://localhost:3000',
        'endpoints': {
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

    # Calculate Sharpe ratio (simplified)
    import numpy as np
    if len(returns) > 1:
        sharpe = (np.mean(returns) / np.std(returns)) * (252 ** 0.5) if np.std(returns) > 0 else 0
    else:
        sharpe = 0

    # Max drawdown
    equity_curve = []
    cumulative = 1000.00
    for t in reversed(trades):  # Chronological order
        cumulative += float(t.get('Return_Dollars', 0))
        equity_curve.append(cumulative)

    peak = cumulative
    max_dd = 0
    for value in equity_curve:
        if value > peak:
            peak = value
        dd = ((peak - value) / peak) * 100
        if dd > max_dd:
            max_dd = dd

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
            'sharpe_ratio': round(sharpe, 2),
            'max_drawdown': round(max_dd, 2)
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
            peak = cumulative

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
        today = datetime.now().strftime('%Y%m%d')

        for operation in ['go', 'execute', 'analyze']:
            pattern = f"{operation}_{today}_*.json"
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
    """
    valid_operations = ['go', 'execute', 'analyze']
    operation = operation.lower()

    if operation not in valid_operations:
        return jsonify({'error': 'Invalid operation'}), 400

    daily_reviews_dir = PROJECT_DIR / 'daily_reviews'
    if not daily_reviews_dir.exists():
        return jsonify({'error': 'No daily reviews directory found'}), 404

    today = datetime.now().strftime('%Y%m%d')
    pattern = f"{operation}_{today}_*.json"
    files = sorted(daily_reviews_dir.glob(pattern), reverse=True)

    if not files:
        return jsonify({
            'error': 'No logs found for today',
            'operation': operation,
            'content': f'No {operation.upper()} command has been run today.'
        }), 404

    latest_file = files[0]

    try:
        with open(latest_file) as f:
            data = json.load(f)

        # Extract text content from Claude response
        content = data.get('content', [{}])[0].get('text', '')

        # Extract timestamp from filename
        filename = latest_file.name
        timestamp_str = filename.split('_')[2].replace('.json', '')
        timestamp = f"{timestamp_str[:2]}:{timestamp_str[2:4]}:{timestamp_str[4:]}"

        return jsonify({
            'operation': operation.upper(),
            'log_file': str(latest_file),
            'timestamp': timestamp,
            'content': content
        })

    except Exception as e:
        return jsonify({
            'error': f'Error reading log: {str(e)}',
            'operation': operation
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
