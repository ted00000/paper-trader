#!/usr/bin/env python3
"""
System Health Check & Status Reporter
Validates all file paths, operations, and system readiness
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

class SystemHealthCheck:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.passed = []

    def check_required_files(self):
        """Verify all required files exist"""
        required_files = {
            'agent_v5.5.py': 'Main trading agent',
            'learn_daily.py': 'Daily learning script',
            'learn_weekly.py': 'Weekly learning script',
            'learn_monthly.py': 'Monthly learning script',
            'dashboard_server.py': 'Admin dashboard server',
            'run_go.sh': 'GO wrapper script',
            'run_execute.sh': 'EXECUTE wrapper script',
            'run_analyze.sh': 'ANALYZE wrapper script',
        }

        for file, desc in required_files.items():
            path = self.base_dir / file
            if path.exists():
                # Check if wrapper scripts reference correct agent version
                if file.startswith('run_') and file.endswith('.sh'):
                    with open(path) as f:
                        content = f.read()
                        if 'agent_v5.5.py' in content:
                            self.passed.append(f"✓ {file}: {desc} (correct version)")
                        else:
                            self.issues.append(f"✗ {file}: References wrong agent version")
                else:
                    self.passed.append(f"✓ {file}: {desc}")
            else:
                self.issues.append(f"✗ MISSING: {file} ({desc})")

    def check_required_directories(self):
        """Verify all required directories exist"""
        required_dirs = {
            'portfolio_data': 'Portfolio state files',
            'trade_history': 'Completed trades history',
            'logs': 'Operation logs',
            'dashboard_data': 'Admin dashboard data',
            'strategy_evolution': 'Learning system data',
        }

        for dir_name, desc in required_dirs.items():
            path = self.base_dir / dir_name
            if path.exists() and path.is_dir():
                self.passed.append(f"✓ {dir_name}/: {desc}")
            else:
                self.issues.append(f"✗ MISSING DIRECTORY: {dir_name}/ ({desc})")
                # Create it
                path.mkdir(parents=True, exist_ok=True)
                self.warnings.append(f"⚠ Created missing directory: {dir_name}/")

    def check_operation_status(self):
        """Check status of recent operations"""
        operations = {
            'GO': {
                'log': 'logs/go.log',
                'output': 'portfolio_data/pending_positions.json',
                'schedule': '8:45 AM weekdays'
            },
            'EXECUTE': {
                'log': 'logs/execute.log',
                'output': 'portfolio_data/current_portfolio.json',
                'schedule': '9:45 AM weekdays'
            },
            'ANALYZE': {
                'log': 'logs/analyze.log',
                'output': 'portfolio_data/account_status.json',
                'schedule': '4:30 PM weekdays'
            },
            'LEARN_DAILY': {
                'log': 'logs/learn_daily.log',
                'output': 'catalyst_exclusions.json',
                'schedule': '5:00 PM weekdays'
            }
        }

        now = datetime.now()

        for op_name, details in operations.items():
            log_path = self.base_dir / details['log']
            output_path = self.base_dir / details['output']

            # Check log exists
            if not log_path.exists():
                self.issues.append(f"✗ {op_name}: Log file missing ({details['log']})")
                continue

            # Check log recency
            log_mtime = datetime.fromtimestamp(log_path.stat().st_mtime)
            age_hours = (now - log_mtime).total_seconds() / 3600

            if age_hours > 48:
                self.warnings.append(f"⚠ {op_name}: Log not updated in {age_hours:.1f} hours")
            else:
                self.passed.append(f"✓ {op_name}: Log updated {age_hours:.1f} hours ago")

            # Check for errors in log
            with open(log_path) as f:
                log_content = f.read()
                if 'agent_v5.0.py' in log_content:
                    self.issues.append(f"✗ {op_name}: Log shows calls to old agent_v5.0.py")
                elif 'COMPLETED SUCCESSFULLY' in log_content:
                    self.passed.append(f"✓ {op_name}: Last run successful")
                elif 'Error' in log_content or 'Traceback' in log_content:
                    self.warnings.append(f"⚠ {op_name}: Errors detected in log")

            # Check output file
            if output_path.exists():
                output_mtime = datetime.fromtimestamp(output_path.stat().st_mtime)
                output_age = (now - output_mtime).total_seconds() / 3600

                if output_age > 48:
                    self.warnings.append(f"⚠ {op_name}: Output not updated in {output_age:.1f} hours")
                else:
                    self.passed.append(f"✓ {op_name}: Output fresh ({output_age:.1f} hours old)")
            else:
                self.warnings.append(f"⚠ {op_name}: Output file not found ({details['output']})")

    def check_environment(self):
        """Check environment variables"""
        required_env_vars = [
            'ANTHROPIC_API_KEY',
            'POLYGON_API_KEY',
            'ADMIN_USERNAME',
            'ADMIN_PASSWORD_HASH',
            'SECRET_KEY'
        ]

        # Try to load from ~/.env
        env_path = Path.home() / '.env'
        if env_path.exists():
            self.passed.append(f"✓ Environment file exists: {env_path}")

            with open(env_path) as f:
                env_content = f.read()
                for var in required_env_vars:
                    if var in env_content:
                        self.passed.append(f"✓ Environment variable set: {var}")
                    else:
                        self.warnings.append(f"⚠ Environment variable missing: {var}")
        else:
            self.issues.append(f"✗ Environment file missing: {env_path}")

    def check_crontab(self):
        """Check cron schedule (server-side only)"""
        # This would need to run on the server
        self.warnings.append("⚠ Crontab check skipped (run on server with: crontab -l)")

    def generate_report(self):
        """Generate comprehensive health report"""
        print("=" * 70)
        print("PAPER TRADING LAB - SYSTEM HEALTH CHECK")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()

        if self.issues:
            print("🚨 CRITICAL ISSUES:")
            print("-" * 70)
            for issue in self.issues:
                print(f"  {issue}")
            print()

        if self.warnings:
            print("⚠️  WARNINGS:")
            print("-" * 70)
            for warning in self.warnings:
                print(f"  {warning}")
            print()

        if self.passed:
            print("✅ PASSED CHECKS:")
            print("-" * 70)
            for check in self.passed:
                print(f"  {check}")
            print()

        print("=" * 70)
        print(f"SUMMARY: {len(self.passed)} passed, {len(self.warnings)} warnings, {len(self.issues)} critical")
        print("=" * 70)

        # Return status
        return {
            'timestamp': datetime.now().isoformat(),
            'passed': len(self.passed),
            'warnings': len(self.warnings),
            'issues': len(self.issues),
            'details': {
                'passed': self.passed,
                'warnings': self.warnings,
                'issues': self.issues
            }
        }

    def run_all_checks(self):
        """Run all health checks"""
        print("Running system health checks...\n")

        self.check_required_files()
        self.check_required_directories()
        self.check_operation_status()
        self.check_environment()
        self.check_crontab()

        report = self.generate_report()

        # Save report
        report_path = self.base_dir / 'dashboard_data' / 'system_health.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {report_path}")

        return len(self.issues) == 0


if __name__ == '__main__':
    checker = SystemHealthCheck()
    success = checker.run_all_checks()

    exit(0 if success else 1)
