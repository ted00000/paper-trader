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
