#!/usr/bin/env python3
"""
Admin Dashboard Server - Secure Web Interface
Provides authenticated access to trading system monitoring and approvals
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, abort
from werkzeug.security import check_password_hash
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
import json
import os
import csv
from time import time
import numpy as np

# Project setup
PROJECT_DIR = Path(__file__).parent
app = Flask(__name__,
    template_folder=PROJECT_DIR / 'dashboard' / 'templates',
    static_folder=PROJECT_DIR / 'dashboard' / 'static')

# Security configuration
app.secret_key = os.environ.get('DASHBOARD_SECRET_KEY')
if not app.secret_key:
    raise RuntimeError("DASHBOARD_SECRET_KEY not set in environment")

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True when using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Load admin credentials from environment
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')

if not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH:
    raise RuntimeError("Admin credentials not set. Run generate_dashboard_credentials.py first")

# Rate limiting
login_attempts = defaultdict(list)
MAX_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes

# File paths
AUDIT_LOG = PROJECT_DIR / 'logs' / 'dashboard' / 'audit.log'
AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

# =====================================================================
# SECURITY FUNCTIONS
# =====================================================================

def log_audit_event(event_type, username, ip, details=None):
    """Log security-relevant events"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'event': event_type,
        'username': username,
        'ip': ip,
        'details': details or {}
    }

    with open(AUDIT_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def is_rate_limited(ip):
    """Check if IP is rate limited"""
    now = time()
    # Clean old attempts
    login_attempts[ip] = [t for t in login_attempts[ip] if now - t < LOCKOUT_DURATION]

    if len(login_attempts[ip]) >= MAX_ATTEMPTS:
        return True
    return False

def record_attempt(ip):
    """Record login attempt"""
    login_attempts[ip].append(time())

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))

        # Check session timeout
        login_time = session.get('login_time', 0)
        if time() - login_time > 7200:  # 2 hours
            session.clear()
            return redirect(url_for('login'))

        return f(*args, **kwargs)

    return decorated_function

# =====================================================================
# DATA LOADING FUNCTIONS
# =====================================================================

def load_system_status():
    """Load current system status"""
    status = {
        'trading_active': True,
        'account_value': 0,
        'active_positions': 0,
        'win_rate_30d': 0,
        'last_updated': None
    }

    # Load account status
    account_file = PROJECT_DIR / 'portfolio_data' / 'account_status.json'
    if account_file.exists():
        with open(account_file) as f:
            account = json.load(f)
            status['account_value'] = account.get('account_value', 0)

    # Load portfolio
    portfolio_file = PROJECT_DIR / 'portfolio_data' / 'current_portfolio.json'
    if portfolio_file.exists():
        with open(portfolio_file) as f:
            portfolio = json.load(f)
            status['active_positions'] = portfolio.get('total_positions', 0)
            status['last_updated'] = portfolio.get('last_updated', 'Never')

    # Calculate 30-day win rate
    trades_file = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'
    if trades_file.exists():
        recent_trades = []
        cutoff = datetime.now() - timedelta(days=30)

        with open(trades_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Exit_Date'):
                    exit_date = datetime.strptime(row['Exit_Date'], '%Y-%m-%d')
                    if exit_date >= cutoff:
                        recent_trades.append(row)

        if recent_trades:
            winners = sum(1 for t in recent_trades if float(t.get('Return_Percent', 0)) > 0)
            status['win_rate_30d'] = (winners / len(recent_trades)) * 100

    return status

def load_pending_actions():
    """Load pending actions requiring approval"""
    actions_file = PROJECT_DIR / 'dashboard_data' / 'pending_actions.json'

    if not actions_file.exists():
        return []

    with open(actions_file) as f:
        return json.load(f)

def load_recent_trades(limit=10):
    """Load recent completed trades"""
    trades_file = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'

    if not trades_file.exists():
        return []

    trades = []
    with open(trades_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Trade_ID'):
                trades.append(row)

    # Return most recent
    return sorted(trades, key=lambda x: x.get('Exit_Date', ''), reverse=True)[:limit]

def load_exclusion_overrides(days=30):
    """Load recent exclusion overrides"""
    overrides_file = PROJECT_DIR / 'logs' / 'exclusion_overrides.log'

    if not overrides_file.exists():
        return []

    overrides = []
    cutoff = datetime.now() - timedelta(days=days)

    with open(overrides_file) as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                entry_date = datetime.fromisoformat(entry['timestamp'])
                if entry_date >= cutoff:
                    overrides.append(entry)

    return sorted(overrides, key=lambda x: x['timestamp'], reverse=True)

# =====================================================================
# ROUTES
# =====================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        ip = request.remote_addr

        # Rate limiting check
        if is_rate_limited(ip):
            log_audit_event('LOGIN_RATE_LIMITED', 'unknown', ip)
            return render_template('login.html',
                error='Too many login attempts. Account locked for 15 minutes.'), 429

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Validate credentials
        if (username == ADMIN_USERNAME and
            check_password_hash(ADMIN_PASSWORD_HASH, password)):

            # Successful login
            session.permanent = True
            session['authenticated'] = True
            session['username'] = username
            session['login_time'] = time()

            log_audit_event('LOGIN_SUCCESS', username, ip)

            # Redirect to /admin for nginx reverse proxy setup
            return redirect('/admin')
        else:
            # Failed login
            record_attempt(ip)
            log_audit_event('LOGIN_FAILED', username or 'unknown', ip)

            return render_template('login.html',
                error='Invalid username or password'), 401

    # GET request - show login form
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    username = session.get('username', 'unknown')
    ip = request.remote_addr

    log_audit_event('LOGOUT', username, ip)

    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@require_auth
def dashboard():
    """Main dashboard"""
    username = session.get('username')

    # Load all dashboard data
    data = {
        'system_status': load_system_status(),
        'pending_actions': load_pending_actions(),
        'recent_trades': load_recent_trades(10),
        'exclusion_overrides': load_exclusion_overrides(30)
    }

    return render_template('dashboard.html',
        username=username,
        data=data
    )

@app.route('/api/actions/approve', methods=['POST'])
@require_auth
def approve_action():
    """Approve a pending action"""
    username = session.get('username')
    ip = request.remote_addr

    action_id = request.json.get('action_id')
    user_notes = request.json.get('notes', '')

    # Load pending actions
    actions_file = PROJECT_DIR / 'dashboard_data' / 'pending_actions.json'
    if not actions_file.exists():
        return {'error': 'No pending actions'}, 404

    with open(actions_file) as f:
        actions = json.load(f)

    # Find the action
    action = next((a for a in actions if a['id'] == action_id), None)
    if not action:
        return {'error': 'Action not found'}, 404

    # Update action status
    action['status'] = 'APPROVED'
    action['approved_by'] = username
    action['approved_date'] = datetime.now().isoformat()
    action['user_notes'] = user_notes

    # Generate code snippet if parameter adjustment
    if action['type'] == 'PARAMETER_ADJUSTMENT':
        action['code_to_apply'] = generate_code_snippet(action)

    # Save updated actions
    with open(actions_file, 'w') as f:
        json.dump(actions, f, indent=2)

    # Log approval
    log_audit_event('APPROVE_ACTION', username, ip, {
        'action_id': action_id,
        'action_type': action['type'],
        'notes': user_notes
    })

    return {'success': True, 'action': action}

@app.route('/api/actions/reject', methods=['POST'])
@require_auth
def reject_action():
    """Reject a pending action"""
    username = session.get('username')
    ip = request.remote_addr

    action_id = request.json.get('action_id')
    reason = request.json.get('reason', '')

    # Load and update actions
    actions_file = PROJECT_DIR / 'dashboard_data' / 'pending_actions.json'
    if not actions_file.exists():
        return {'error': 'No pending actions'}, 404

    with open(actions_file) as f:
        actions = json.load(f)

    action = next((a for a in actions if a['id'] == action_id), None)
    if not action:
        return {'error': 'Action not found'}, 404

    action['status'] = 'REJECTED'
    action['rejected_by'] = username
    action['rejected_date'] = datetime.now().isoformat()
    action['rejection_reason'] = reason

    with open(actions_file, 'w') as f:
        json.dump(actions, f, indent=2)

    log_audit_event('REJECT_ACTION', username, ip, {
        'action_id': action_id,
        'reason': reason
    })

    return {'success': True}

def generate_code_snippet(action):
    """Generate code snippet for parameter adjustment"""
    param = action['parameter']
    new_value = action['suggested_value']

    snippets = {
        'VIX_THRESHOLD': f"# In agent_v5.5.py, update VIX threshold\nVIX_THRESHOLD = {new_value}",
        'RS_THRESHOLD': f"# In agent_v5.5.py, update RS filter\nRS_THRESHOLD = {new_value}",
        'NEWS_SCORE_MIN': f"# In agent_v5.5.py, update news score requirement\nNEWS_SCORE_MIN = {new_value}",
        'STOP_LOSS_PCT': f"# In agent_v5.5.py, update stop loss\nSTOP_LOSS_PCT = {new_value}",
    }

    return snippets.get(param, f"# Update {param} to {new_value}")

@app.route('/api/operations/status')
@require_auth
def operations_status():
    """Get status of all system operations"""
    try:
        status_dir = PROJECT_DIR / 'dashboard_data' / 'operation_status'

        if not status_dir.exists():
            return jsonify({'operations': {}, 'health': 'UNKNOWN'})

        operations = {}
        overall_health = 'HEALTHY'

        for status_file in status_dir.glob('*_status.json'):
            try:
                with open(status_file) as f:
                    status = json.load(f)
                    op_name = status['operation']

                    # Calculate age
                    if status.get('last_run'):
                        last_run = datetime.fromisoformat(status['last_run'])
                        # Remove timezone info to compare with timezone-naive datetime.now()
                        if last_run.tzinfo is not None:
                            last_run = last_run.replace(tzinfo=None)
                        age_hours = (datetime.now() - last_run).total_seconds() / 3600
                    else:
                        age_hours = None

                    # Determine health
                    if status['status'] == 'FAILED':
                        health = 'FAILED'
                        overall_health = 'UNHEALTHY'
                    elif status['status'] == 'NEVER_RUN':
                        health = 'NEVER_RUN'
                    elif age_hours and age_hours > 48:
                        health = 'STALE'
                        if overall_health == 'HEALTHY':
                            overall_health = 'WARNING'
                    else:
                        health = 'HEALTHY'

                    operations[op_name] = {
                        'status': status['status'],
                        'health': health,
                        'last_run': status.get('last_run'),
                        'age_hours': age_hours,
                        'error': status.get('error'),
                        'log_file': status.get('log_file'),
                        'stats': status.get('stats')  # Include stats for operations like SCREENER
                    }
            except Exception as e:
                print(f"Error loading {status_file}: {e}")
                continue

        return jsonify({
            'operations': operations,
            'health': overall_health,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/daily-picks')
@require_auth
def daily_picks():
    """Get daily picks (all opportunities analyzed by Claude)"""
    try:
        daily_picks_file = PROJECT_DIR / 'dashboard_data' / 'daily_picks.json'

        if not daily_picks_file.exists():
            return jsonify({
                'available': False,
                'message': 'No daily picks data yet. Run GO command to generate.'
            })

        with open(daily_picks_file) as f:
            picks_data = json.load(f)

        return jsonify({
            'available': True,
            'data': picks_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system-health')
@require_auth
def data_integrity_health():
    """Run data integrity checks and return system health status"""
    try:
        # Import and run integrity checker
        import sys
        sys.path.insert(0, str(PROJECT_DIR))
        from data_integrity_check import DataIntegrityChecker

        checker = DataIntegrityChecker(PROJECT_DIR)
        health_status = checker.run_checks_silent()

        return jsonify(health_status)

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Health check failed: {str(e)}',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'checks_passed': 0,
            'checks_total': 0,
            'errors': [str(e)],
            'warnings': []
        }), 500

def extract_system_alerts(operation):
    """Extract important system alerts from terminal log files (macro blackouts, VIX, market regime)"""
    alerts = []

    try:
        log_file = PROJECT_DIR / 'logs' / f'{operation}.log'
        if not log_file.exists():
            return alerts

        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')

        # Read log and look for alert patterns
        with open(log_file) as f:
            lines = f.readlines()

        # Find today's section by looking for "Time: YYYY-MM-DD" timestamp
        section_start = -1
        for i in range(len(lines) - 1, -1, -1):
            if f'Time: {today}' in lines[i]:
                # Found today's timestamp, go back to find section start
                section_start = max(0, i - 5)
                break

        # If no section found, don't return any alerts (no run today)
        if section_start == -1:
            return alerts

        # Find the end of today's section (next timestamp or end of file)
        section_end = len(lines)
        for i in range(section_start + 10, len(lines)):
            if 'Time: 20' in lines[i] and today not in lines[i]:
                # Found next day's section
                section_end = i
                break

        # Extract alerts from today's section only
        seen_alerts = set()
        for line in lines[section_start:section_end]:
            alert_text = None

            # Extract macro blackout alerts
            if '🚨 MACRO BLACKOUT' in line:
                alert_text = line.strip()

            # Extract VIX warnings
            elif 'VIX' in line and ('SHUTDOWN' in line or '>30' in line):
                alert_text = line.strip()

            # Extract market regime messages (HEALTHY, DEGRADED, UNHEALTHY)
            # Note: Only keep the MOST RECENT regime message (not all historical ones)
            elif ('✓ Market HEALTHY' in line or '⚠️ Market DEGRADED' in line or
                  '⚠️ Market UNHEALTHY' in line):
                # Replace any previous market regime alert with the most recent one
                # Remove old market regime messages
                alerts = [a for a in alerts if not any(x in a for x in ['Market HEALTHY', 'Market DEGRADED', 'Market UNHEALTHY'])]
                alert_text = line.strip()

            # Extract blocking messages
            elif '✗ Blocking ALL' in line and 'BUY recommendations' in line:
                alert_text = line.strip()

            # Add only unique alerts
            if alert_text and alert_text not in seen_alerts:
                alerts.append(alert_text)
                seen_alerts.add(alert_text)

    except Exception as e:
        print(f"Error extracting system alerts: {e}")

    return alerts

@app.route('/api/operations/logs/<operation>')
@require_auth
def view_log(operation):
    """View log file for an operation - shows today's most recent run"""
    try:
        # Validate operation name
        valid_ops = ['go', 'execute', 'analyze', 'learn_daily', 'learn_weekly', 'learn_monthly', 'screener']
        if operation.lower() not in valid_ops:
            return jsonify({'error': 'Invalid operation'}), 400

        # For GO, EXECUTE, ANALYZE commands: Check daily_reviews for most recent JSON
        if operation.lower() in ['go', 'execute', 'analyze']:
            today = datetime.now().strftime('%Y%m%d')
            reviews_dir = PROJECT_DIR / 'daily_reviews'

            if reviews_dir.exists():
                # Find most recent review file for today
                pattern = f"{operation.lower()}_{today}_*.json"
                review_files = sorted(reviews_dir.glob(pattern), reverse=True)

                if review_files:
                    # Use most recent JSON file
                    latest_file = review_files[0]
                    with open(latest_file) as f:
                        data = json.load(f)

                    # Extract timestamp from filename (e.g., go_20251117_092728.json)
                    filename = latest_file.name
                    timestamp_str = filename.split('_')[2].replace('.json', '')
                    timestamp = f"{timestamp_str[:2]}:{timestamp_str[2:4]}:{timestamp_str[4:]}"

                    # Format the response text from JSON
                    response_text = data.get('content', [{}])[0].get('text', '')

                    # Remove JSON decision block (redundant - shown in Daily Picks section)
                    # Find and remove the ```json ... ``` block
                    lines = response_text.split('\n')
                    filtered_lines = []
                    in_json_block = False

                    for line in lines:
                        if line.strip().startswith('```json'):
                            in_json_block = True
                            continue
                        elif in_json_block and line.strip() == '```':
                            in_json_block = False
                            continue
                        elif not in_json_block:
                            filtered_lines.append(line)

                    cleaned_text = '\n'.join(filtered_lines)

                    # Extract system alerts from terminal log (macro blackouts, VIX warnings, etc.)
                    system_alerts = extract_system_alerts(operation.lower())
                    alerts_section = ""
                    if system_alerts:
                        alerts_section = "=== SYSTEM ALERTS ===\n" + "\n".join(system_alerts) + "\n\n" + "="*60 + "\n\n"

                    return jsonify({
                        'operation': operation,
                        'log_file': str(latest_file),
                        'lines_returned': len(cleaned_text.split('\n')),
                        'total_lines': len(cleaned_text.split('\n')),
                        'content': f"(Showing today's most recent run: {timestamp})\n\n{alerts_section}{cleaned_text}"
                    })

        # Fallback to log file for older behavior or if JSON not found
        log_file = PROJECT_DIR / 'logs' / f'{operation.lower()}.log'

        if not log_file.exists():
            return jsonify({'error': 'Log file not found', 'log': ''}), 404

        # Get today's date string in format used by logs
        today = datetime.now().strftime('%Y-%m-%d')
        today_short = datetime.now().strftime('%b %d')  # e.g., "Nov  3"

        # Read log and filter for today's entries
        with open(log_file) as f:
            all_lines = f.readlines()

            # Find complete sections for today
            today_lines = []
            in_todays_section = False
            current_section = []

            for i, line in enumerate(all_lines):
                # Check if this line starts a new section for today
                if (today in line or today_short in line) and ('Time:' in line or 'Starting:' in line or '====' in line):
                    # If we were in a section, save it
                    if current_section:
                        today_lines.extend(current_section)
                    # Start new section
                    in_todays_section = True
                    current_section = [line]
                elif in_todays_section:
                    current_section.append(line)
                    # Check if we've hit a section marker that indicates end of this run
                    if 'COMPLETED SUCCESSFULLY' in line or 'FAILED' in line:
                        # Look ahead - if next non-empty line is a different date, stop
                        if i + 1 < len(all_lines):
                            next_line = all_lines[i + 1].strip()
                            if next_line and today not in next_line and today_short not in next_line:
                                in_todays_section = False

            # Add any remaining section
            if current_section:
                today_lines.extend(current_section)

            # If no today's entries found, show last 100 lines as fallback
            if not today_lines:
                today_lines = all_lines[-100:] if len(all_lines) > 100 else all_lines
                content_note = "(No entries found for today - showing last 100 lines)\n\n"
            else:
                content_note = f"(Showing today's activity: {today})\n\n"

        return jsonify({
            'operation': operation,
            'log_file': str(log_file),
            'lines_returned': len(today_lines),
            'total_lines': len(all_lines),
            'content': content_note + ''.join(today_lines)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/health')
@require_auth
def system_health():
    """Get comprehensive system health check - runs health_check.py"""
    try:
        # Import and run health checker
        import sys
        sys.path.insert(0, str(PROJECT_DIR))
        from health_check import HealthChecker

        checker = HealthChecker()
        health_data = checker.run_silent()

        return jsonify(health_data)

    except Exception as e:
        return jsonify({
            'status': 'error',
            'status_color': 'red',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stats': {},
            'issues': [f'Health check failed: {str(e)}'],
            'warnings': [],
            'healthy': False
        }), 500

@app.route('/api/portfolio/performance')
def portfolio_performance():
    """Get public portfolio performance metrics (no auth required for transparency)"""
    try:
        trades_file = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'

        if not trades_file.exists():
            return jsonify({
                'ytd_return': 0,
                'mtd_return': 0,
                'total_trades': 0,
                'win_rate': 0,
                'avg_gain': 0,
                'avg_loss': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'total_conviction': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
                'last_updated': None
            })

        trades = []
        with open(trades_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Trade_ID') and row.get('Exit_Date'):
                    trades.append(row)

        if not trades:
            return jsonify({
                'ytd_return': 0,
                'mtd_return': 0,
                'total_trades': 0,
                'win_rate': 0,
                'avg_gain': 0,
                'avg_loss': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'total_conviction': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
                'last_updated': None
            })

        # Calculate metrics
        now = datetime.now()
        ytd_start = datetime(now.year, 1, 1)
        mtd_start = datetime(now.year, now.month, 1)

        ytd_trades = []
        mtd_trades = []
        returns = []
        conviction_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'SKIP': 0}

        for trade in trades:
            try:
                exit_date = datetime.strptime(trade['Exit_Date'], '%Y-%m-%d')
                return_pct = float(trade.get('Return_Percent', 0))
                returns.append(return_pct)

                # Conviction tracking
                conviction = trade.get('Conviction_Level', 'MEDIUM')
                if conviction in conviction_counts:
                    conviction_counts[conviction] += 1

                if exit_date >= ytd_start:
                    ytd_trades.append(return_pct)

                if exit_date >= mtd_start:
                    mtd_trades.append(return_pct)
            except (ValueError, KeyError):
                continue

        # Calculate performance metrics
        total_trades = len(returns)
        winners = [r for r in returns if r > 0]
        losers = [r for r in returns if r < 0]

        win_rate = (len(winners) / total_trades * 100) if total_trades > 0 else 0
        avg_gain = np.mean(winners) if winners else 0
        avg_loss = np.mean(losers) if losers else 0

        # YTD/MTD returns (cumulative)
        ytd_return = sum(ytd_trades)
        mtd_return = sum(mtd_trades)

        # Max drawdown calculation
        cumulative_returns = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = cumulative_returns - running_max
        max_drawdown = abs(np.min(drawdowns)) if len(drawdowns) > 0 else 0

        # Sharpe ratio (annualized, assuming ~50 trades/year)
        if len(returns) > 1:
            std_dev = np.std(returns)
            sharpe_ratio = (np.mean(returns) / std_dev) * np.sqrt(50) if std_dev > 0 else 0
        else:
            sharpe_ratio = 0

        return jsonify({
            'ytd_return': round(ytd_return, 2),
            'mtd_return': round(mtd_return, 2),
            'total_trades': total_trades,
            'win_rate': round(win_rate, 1),
            'avg_gain': round(avg_gain, 2),
            'avg_loss': round(avg_loss, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'total_conviction': conviction_counts,
            'last_updated': trades[-1]['Exit_Date'] if trades else None
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/regime-performance')
def regime_performance():
    """Get performance across different market regimes (no auth required for transparency)"""
    try:
        trades_file = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'

        if not trades_file.exists():
            return jsonify({
                'vix_regimes': {},
                'market_breadth_regimes': {},
                'sector_performance': {}
            })

        trades = []
        with open(trades_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Trade_ID') and row.get('Exit_Date'):
                    trades.append(row)

        # Group by VIX regime
        vix_regimes = {}
        breadth_regimes = {}
        sector_performance = {}

        for trade in trades:
            try:
                return_pct = float(trade.get('Return_Percent', 0))

                # VIX regime analysis
                vix = float(trade.get('VIX_At_Entry', 0))
                if vix > 0:
                    if vix < 15:
                        regime = 'VERY_LOW (<15)'
                    elif vix < 20:
                        regime = 'LOW (15-20)'
                    elif vix < 25:
                        regime = 'ELEVATED (20-25)'
                    elif vix < 30:
                        regime = 'HIGH (25-30)'
                    else:
                        regime = 'EXTREME (≥30)'

                    if regime not in vix_regimes:
                        vix_regimes[regime] = {'trades': 0, 'total_return': 0, 'wins': 0}

                    vix_regimes[regime]['trades'] += 1
                    vix_regimes[regime]['total_return'] += return_pct
                    if return_pct > 0:
                        vix_regimes[regime]['wins'] += 1

                # Market breadth regime (if available in newer trades)
                market_regime = trade.get('Market_Breadth_Regime', trade.get('Market_Regime', ''))
                if market_regime and market_regime != 'Unknown':
                    if market_regime not in breadth_regimes:
                        breadth_regimes[market_regime] = {'trades': 0, 'total_return': 0, 'wins': 0}

                    breadth_regimes[market_regime]['trades'] += 1
                    breadth_regimes[market_regime]['total_return'] += return_pct
                    if return_pct > 0:
                        breadth_regimes[market_regime]['wins'] += 1

                # Sector performance
                sector = trade.get('Sector', 'Unknown')
                if sector and sector != 'Unknown':
                    if sector not in sector_performance:
                        sector_performance[sector] = {'trades': 0, 'total_return': 0, 'wins': 0}

                    sector_performance[sector]['trades'] += 1
                    sector_performance[sector]['total_return'] += return_pct
                    if return_pct > 0:
                        sector_performance[sector]['wins'] += 1

            except (ValueError, KeyError):
                continue

        # Calculate averages and win rates
        for regime_dict in [vix_regimes, breadth_regimes, sector_performance]:
            for key in regime_dict:
                data = regime_dict[key]
                data['avg_return'] = round(data['total_return'] / data['trades'], 2) if data['trades'] > 0 else 0
                data['win_rate'] = round(data['wins'] / data['trades'] * 100, 1) if data['trades'] > 0 else 0

        return jsonify({
            'vix_regimes': vix_regimes,
            'market_breadth_regimes': breadth_regimes,
            'sector_performance': sector_performance
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/status')
def system_status():
    """Get public system status - minimal health info for public dashboard (no auth required)"""
    try:
        logs_dir = PROJECT_DIR / 'logs'

        def get_last_run_info(command):
            """Get last run timestamp for a command"""
            log_file = logs_dir / f'{command}.log'
            if not log_file.exists():
                return None

            mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            hours_ago = (datetime.now() - mod_time).total_seconds() / 3600

            # Convert to relative time string
            if hours_ago < 1:
                minutes_ago = int(hours_ago * 60)
                return f"{minutes_ago}m ago"
            elif hours_ago < 24:
                return f"{int(hours_ago)}h ago"
            else:
                days_ago = int(hours_ago / 24)
                return f"{days_ago}d ago"

        # Check screener data freshness
        screener_file = PROJECT_DIR / 'screener_candidates.json'
        screener_status = None
        if screener_file.exists():
            mod_time = datetime.fromtimestamp(screener_file.stat().st_mtime)
            hours_ago = (datetime.now() - mod_time).total_seconds() / 3600
            if hours_ago < 1:
                screener_status = f"{int(hours_ago * 60)}m ago"
            elif hours_ago < 24:
                screener_status = f"{int(hours_ago)}h ago"
            else:
                screener_status = f"{int(hours_ago / 24)}d ago"

        # Determine overall health
        go_info = get_last_run_info('go')
        execute_info = get_last_run_info('execute')
        exit_info = get_last_run_info('exit')
        analyze_info = get_last_run_info('analyze')

        # Simple health logic: if any command hasn't run in 48 hours, degraded
        all_times = []
        for cmd in ['go', 'execute', 'exit', 'analyze']:
            log_file = logs_dir / f'{cmd}.log'
            if log_file.exists():
                mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                hours_ago = (datetime.now() - mod_time).total_seconds() / 3600
                all_times.append(hours_ago)

        if not all_times:
            health_status = 'unknown'
            health_color = 'gray'
            health_text = 'Unknown'
        elif max(all_times) > 48:
            health_status = 'degraded'
            health_color = 'orange'
            health_text = 'Degraded'
        else:
            health_status = 'healthy'
            health_color = 'green'
            health_text = 'Healthy'

        # v7.0: Get system version from agent
        system_version = 'unknown'
        try:
            agent_file = PROJECT_DIR / 'agent_v5.5.py'
            if agent_file.exists():
                with open(agent_file) as f:
                    for line in f:
                        if line.strip().startswith('SYSTEM_VERSION ='):
                            system_version = line.split('=')[1].split('#')[0].strip().strip("'\"")
                            break
        except:
            pass

        return jsonify({
            'status': health_status,
            'status_color': health_color,
            'status_text': health_text,
            'system_version': system_version,  # v7.0: Include system version
            'processes': {
                'screener': screener_status or 'N/A',
                'go': go_info or 'N/A',
                'execute': execute_info or 'N/A',
                'exit': exit_info or 'N/A',
                'analyze': analyze_info or 'N/A'
            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'status_color': 'red',
            'status_text': 'Error',
            'processes': {
                'screener': 'N/A',
                'go': 'N/A',
                'execute': 'N/A',
                'exit': 'N/A',
                'analyze': 'N/A'
            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("ADMIN DASHBOARD SERVER")
    print("="*60)
    print(f"Starting server...")
    print(f"Access at: http://localhost:5000")
    print(f"Login with credentials from ~/.env")
    print(f"Press Ctrl+C to stop")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
