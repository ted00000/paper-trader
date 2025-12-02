#!/usr/bin/env python3
"""
Tedbot Health Check System
Monitors critical components and sends alerts when issues detected
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import requests

# Load environment variables from .env file if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, use system environment variables
    pass

class HealthChecker:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.stats = {}

        # Discord webhook URL (optional - set in .env)
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL', '')

    def check_command_execution(self):
        """Check if GO, EXECUTE, ANALYZE ran today"""
        print("1. Checking command execution...")

        today = datetime.now().strftime('%Y%m%d')
        commands = ['go', 'execute', 'analyze']

        for cmd in commands:
            log_file = self.project_dir / 'logs' / f'{cmd}.log'

            if not log_file.exists():
                self.issues.append(f"❌ {cmd.upper()} log file missing: {log_file}")
                continue

            # Check if log was updated today
            mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            hours_ago = (datetime.now() - mod_time).total_seconds() / 3600

            if hours_ago > 24:
                self.issues.append(f"⚠️ {cmd.upper()} hasn't run in {hours_ago:.1f} hours (last: {mod_time.strftime('%Y-%m-%d %H:%M')})")
            else:
                print(f"   ✓ {cmd.upper()} ran {hours_ago:.1f} hours ago")

    def check_api_connectivity(self):
        """Test connections to critical APIs"""
        print("\n2. Checking API connectivity...")

        apis = {
            'Polygon': 'https://api.polygon.io/v2/aggs/ticker/SPY/prev?apiKey=' + os.getenv('POLYGON_API_KEY', ''),
            'Anthropic': 'https://api.anthropic.com/v1/messages',  # Will fail without auth, but tests connectivity
        }

        for api_name, url in apis.items():
            try:
                response = requests.get(url, timeout=10)
                # Polygon should return 200, Anthropic will return 401 (auth required) but connection works
                if response.status_code in [200, 401]:
                    print(f"   ✓ {api_name} API reachable")
                else:
                    self.warnings.append(f"⚠️ {api_name} API returned status {response.status_code}")
            except requests.exceptions.Timeout:
                self.issues.append(f"❌ {api_name} API timeout (>10 seconds)")
            except requests.exceptions.RequestException as e:
                self.issues.append(f"❌ {api_name} API connection failed: {str(e)}")

    def check_data_freshness(self):
        """Check if screener data is fresh"""
        print("\n3. Checking data freshness...")

        screener_file = self.project_dir / 'screener_candidates.json'

        if not screener_file.exists():
            self.issues.append(f"❌ Screener candidates file missing: {screener_file}")
            return

        mod_time = datetime.fromtimestamp(screener_file.stat().st_mtime)
        hours_ago = (datetime.now() - mod_time).total_seconds() / 3600

        if hours_ago > 24:
            self.issues.append(f"⚠️ Screener data is {hours_ago:.1f} hours old (last update: {mod_time.strftime('%Y-%m-%d %H:%M')})")
        else:
            print(f"   ✓ Screener data updated {hours_ago:.1f} hours ago")

            # Check if it has candidates
            try:
                with open(screener_file) as f:
                    candidates = json.load(f)
                    if isinstance(candidates, list):
                        print(f"   ✓ {len(candidates)} candidates in screener")
                        self.stats['screener_candidates'] = len(candidates)
            except Exception as e:
                self.warnings.append(f"⚠️ Error reading screener file: {str(e)}")

    def check_active_positions(self):
        """Check active positions status"""
        print("\n4. Checking active positions...")

        positions_file = self.project_dir / 'active_positions.json'

        if not positions_file.exists():
            print("   ✓ No active positions")
            self.stats['active_positions'] = 0
            return

        try:
            with open(positions_file) as f:
                positions = json.load(f)
                count = len(positions)
                print(f"   ✓ {count} active position(s)")
                self.stats['active_positions'] = count

                # Calculate total P&L
                total_pnl = 0
                for pos in positions:
                    if 'current_price' in pos and 'entry_price' in pos:
                        pnl_pct = ((pos['current_price'] - pos['entry_price']) / pos['entry_price']) * 100
                        total_pnl += pnl_pct

                if count > 0:
                    avg_pnl = total_pnl / count
                    print(f"   ✓ Average P&L: {avg_pnl:+.2f}%")
                    self.stats['avg_pnl'] = f"{avg_pnl:+.2f}%"
        except Exception as e:
            self.warnings.append(f"⚠️ Error reading positions: {str(e)}")

    def check_claude_api_failures(self):
        """Check for recent Claude API failures"""
        print("\n5. Checking Claude API failures...")

        failure_log = self.project_dir / 'logs' / 'claude_api_failures.json'

        if not failure_log.exists():
            print("   ✓ No Claude API failures logged")
            return

        try:
            with open(failure_log) as f:
                failures = json.load(f)

            if not failures:
                print("   ✓ No Claude API failures")
                return

            # Check for failures in last 24 hours
            recent_failures = []
            for failure in failures:
                failure_time = datetime.strptime(failure['timestamp'], '%Y-%m-%d %H:%M:%S')
                hours_ago = (datetime.now() - failure_time).total_seconds() / 3600
                if hours_ago < 24:
                    recent_failures.append(failure)

            if recent_failures:
                self.warnings.append(f"⚠️ {len(recent_failures)} Claude API failure(s) in last 24 hours")
                for failure in recent_failures[:3]:  # Show up to 3 most recent
                    print(f"     - {failure['timestamp']}: {failure['command']} - {failure['error_type']}")
            else:
                print(f"   ✓ No recent failures (last failure was {len(failures)} total)")
        except Exception as e:
            self.warnings.append(f"⚠️ Error reading failure log: {str(e)}")

    def check_disk_space(self):
        """Check available disk space"""
        print("\n6. Checking disk space...")

        try:
            import shutil
            total, used, free = shutil.disk_usage(self.project_dir)

            free_gb = free // (2**30)
            total_gb = total // (2**30)
            pct_used = (used / total) * 100

            print(f"   ✓ Disk: {free_gb}GB free of {total_gb}GB ({pct_used:.1f}% used)")

            if free_gb < 1:
                self.issues.append(f"❌ Low disk space: only {free_gb}GB remaining")
            elif pct_used > 90:
                self.warnings.append(f"⚠️ Disk {pct_used:.1f}% full")
        except Exception as e:
            self.warnings.append(f"⚠️ Could not check disk space: {str(e)}")

    def send_discord_alert(self, title, message, color=0xFF0000):
        """Send alert to Discord webhook"""
        if not self.discord_webhook:
            return

        try:
            payload = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": color,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "Tedbot Health Check"}
                }]
            }

            response = requests.post(self.discord_webhook, json=payload, timeout=10)
            if response.status_code == 204:
                print(f"\n✓ Discord alert sent: {title}")
            else:
                print(f"\n⚠️ Discord webhook failed: {response.status_code}")
        except Exception as e:
            print(f"\n⚠️ Discord webhook error: {str(e)}")

    def generate_report(self):
        """Generate and display health report"""
        print("\n" + "="*70)
        print("TEDBOT HEALTH CHECK REPORT")
        print("="*70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Summary stats
        if self.stats:
            print("📊 SYSTEM STATS:")
            for key, value in self.stats.items():
                print(f"   {key}: {value}")
            print()

        # Critical issues
        if self.issues:
            print("❌ CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"   {issue}")
            print()

        # Warnings
        if self.warnings:
            print("⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"   {warning}")
            print()

        # Overall status
        if self.issues:
            status = "❌ UNHEALTHY"
            color = 0xFF0000  # Red
        elif self.warnings:
            status = "⚠️ DEGRADED"
            color = 0xFFA500  # Orange
        else:
            status = "✅ HEALTHY"
            color = 0x00FF00  # Green

        print(f"OVERALL STATUS: {status}")
        print("="*70)

        # Send Discord alert if issues exist
        if self.discord_webhook and (self.issues or self.warnings):
            message_parts = []

            if self.stats:
                stats_text = "\n".join([f"**{k}**: {v}" for k, v in self.stats.items()])
                message_parts.append(f"**Stats:**\n{stats_text}")

            if self.issues:
                issues_text = "\n".join([f"• {issue}" for issue in self.issues])
                message_parts.append(f"\n**Critical Issues:**\n{issues_text}")

            if self.warnings:
                warnings_text = "\n".join([f"• {warning}" for warning in self.warnings])
                message_parts.append(f"\n**Warnings:**\n{warnings_text}")

            message = "\n".join(message_parts)
            self.send_discord_alert(f"Tedbot Health Check: {status}", message, color)

        return len(self.issues) == 0

    def run(self):
        """Run all health checks"""
        print("Starting Tedbot Health Check...\n")

        self.check_command_execution()
        self.check_api_connectivity()
        self.check_data_freshness()
        self.check_active_positions()
        self.check_claude_api_failures()
        self.check_disk_space()

        healthy = self.generate_report()

        # Exit with appropriate code
        sys.exit(0 if healthy else 1)

if __name__ == '__main__':
    checker = HealthChecker()
    checker.run()
