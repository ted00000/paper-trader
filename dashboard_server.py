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

                    return jsonify({
                        'operation': operation,
                        'log_file': str(latest_file),
                        'lines_returned': len(response_text.split('\n')),
                        'total_lines': len(response_text.split('\n')),
                        'content': f"(Showing today's most recent run: {timestamp})\n\n{response_text}"
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
    """Get comprehensive system health check"""
    try:
        health_file = PROJECT_DIR / 'dashboard_data' / 'system_health.json'

        if health_file.exists():
            with open(health_file) as f:
                health_data = json.load(f)
        else:
            health_data = {'status': 'unknown', 'message': 'Health check not run yet'}

        return jsonify(health_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
