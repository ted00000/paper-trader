#!/usr/bin/env python3
"""
Daily Data Integrity Check
Validates all critical files and data consistency across the system.
Run daily via cron to catch data issues early.
"""

import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
import sys

class DataIntegrityChecker:
    def __init__(self, project_dir):
        self.project_dir = Path(project_dir)
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_total = 0

    def check(self, name, condition, error_msg=None, warning=False):
        """Track a check result"""
        self.checks_total += 1
        if condition:
            self.checks_passed += 1
            return True
        else:
            msg = error_msg or f"{name} failed"
            if warning:
                self.warnings.append(msg)
            else:
                self.errors.append(msg)
            return False

    def check_file_exists(self, path, required=True):
        """Check if a file exists"""
        full_path = self.project_dir / path
        exists = full_path.exists()
        self.check(
            f"File exists: {path}",
            exists,
            f"Missing required file: {path}" if required else None,
            warning=not required
        )
        return exists

    def check_json_valid(self, path):
        """Check if JSON file is valid and parseable"""
        try:
            with open(self.project_dir / path) as f:
                json.load(f)
            self.check(f"Valid JSON: {path}", True)
            return True
        except Exception as e:
            self.check(f"Valid JSON: {path}", False, f"Invalid JSON in {path}: {str(e)}")
            return False

    def check_portfolio_consistency(self):
        """Check portfolio data consistency"""
        portfolio_file = self.project_dir / "portfolio_data/current_portfolio.json"
        if not portfolio_file.exists():
            return

        try:
            with open(portfolio_file) as f:
                portfolio = json.load(f)

            positions = portfolio.get("positions", [])
            total_positions = portfolio.get("total_positions", 0)

            # Check position count matches
            self.check(
                "Portfolio position count",
                len(positions) == total_positions,
                f"Position count mismatch: {len(positions)} positions but total_positions={total_positions}"
            )

            # Check each position has required fields
            required_fields = ["ticker", "entry_date", "entry_price", "shares", "position_size"]
            for i, pos in enumerate(positions):
                for field in required_fields:
                    self.check(
                        f"Position {i+1} has {field}",
                        field in pos,
                        f"Position {i+1} missing required field: {field}"
                    )

        except Exception as e:
            self.check("Portfolio validation", False, f"Portfolio validation error: {str(e)}")

    def check_account_consistency(self):
        """Check account status consistency"""
        account_file = self.project_dir / "portfolio_data/account_status.json"
        if not account_file.exists():
            return

        try:
            with open(account_file) as f:
                account = json.load(f)

            account_value = account.get("account_value", 0)
            cash = account.get("cash_available", 0)
            positions_value = account.get("positions_value", 0)

            # Check account value = cash + positions
            calculated = cash + positions_value
            tolerance = 0.01  # Allow 1 cent rounding error
            self.check(
                "Account balance",
                abs(account_value - calculated) < tolerance,
                f"Account value mismatch: ${account_value:.2f} != ${cash:.2f} (cash) + ${positions_value:.2f} (positions)"
            )

            # Check required fields exist
            required = ["total_trades", "win_rate_percent", "realized_pl"]
            for field in required:
                self.check(
                    f"Account has {field}",
                    field in account,
                    f"Account missing field: {field}"
                )

        except Exception as e:
            self.check("Account validation", False, f"Account validation error: {str(e)}")

    def check_csv_integrity(self):
        """Check trade history CSV integrity"""
        csv_file = self.project_dir / "trade_history/completed_trades.csv"
        if not csv_file.exists():
            self.check("CSV exists", False, "Trade history CSV missing", warning=True)
            return

        try:
            with open(csv_file, newline='') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                rows = list(reader)

            # Check header exists
            self.check(
                "CSV has headers",
                fieldnames is not None and len(fieldnames) > 0,
                "CSV missing headers"
            )

            # Check all rows have same number of columns
            expected_cols = len(fieldnames)
            for i, row in enumerate(rows, 1):
                # Count non-None values (DictReader creates None keys for extra columns)
                actual_cols = sum(1 for k in row.keys() if k is not None)
                self.check(
                    f"CSV row {i} column count",
                    actual_cols == expected_cols,
                    f"CSV row {i} has {actual_cols} columns, expected {expected_cols}",
                    warning=True
                )

            # Check required fields in each row
            if rows:
                required = ["Ticker", "Entry_Date", "Exit_Date", "Return_Percent", "Exit_Reason"]
                for i, row in enumerate(rows, 1):
                    for field in required:
                        self.check(
                            f"CSV row {i} has {field}",
                            field in row and row[field],
                            f"CSV row {i} missing or empty: {field}"
                        )

        except Exception as e:
            self.check("CSV validation", False, f"CSV validation error: {str(e)}")

    def check_portfolio_csv_sync(self):
        """Check portfolio positions match trade history"""
        portfolio_file = self.project_dir / "portfolio_data/current_portfolio.json"
        account_file = self.project_dir / "portfolio_data/account_status.json"
        csv_file = self.project_dir / "trade_history/completed_trades.csv"

        if not all([portfolio_file.exists(), account_file.exists(), csv_file.exists()]):
            return

        try:
            # Get current position count
            with open(portfolio_file) as f:
                portfolio = json.load(f)
            current_positions = portfolio.get("total_positions", 0)

            # Get total trades from account
            with open(account_file) as f:
                account = json.load(f)
            total_trades = account.get("total_trades", 0)

            # Count trades in CSV
            with open(csv_file, newline='') as f:
                reader = csv.DictReader(f)
                csv_trades = sum(1 for _ in reader)

            # Check CSV trade count matches account
            self.check(
                "Trade count sync",
                csv_trades == total_trades,
                f"Trade count mismatch: CSV has {csv_trades} trades, account shows {total_trades}",
                warning=True
            )

        except Exception as e:
            self.check("Portfolio-CSV sync", False, f"Sync check error: {str(e)}", warning=True)

    def check_daily_activity_freshness(self):
        """Check if daily activity was updated today"""
        activity_file = self.project_dir / "portfolio_data/daily_activity.json"
        if not activity_file.exists():
            self.check("Daily activity exists", False, "Daily activity file missing", warning=True)
            return

        try:
            with open(activity_file) as f:
                activity = json.load(f)

            activity_date = activity.get("date")
            today = datetime.now().strftime("%Y-%m-%d")

            # Warning if not updated today (might be weekend/holiday)
            self.check(
                "Daily activity fresh",
                activity_date == today,
                f"Daily activity not updated today (last: {activity_date})",
                warning=True
            )

        except Exception as e:
            self.check("Daily activity check", False, f"Activity check error: {str(e)}", warning=True)

    def check_daily_picks_freshness(self):
        """Check if daily picks exist and are recent"""
        picks_file = self.project_dir / "dashboard_data/daily_picks.json"
        if not picks_file.exists():
            self.check("Daily picks exist", False, "Daily picks not generated yet", warning=True)
            return

        try:
            with open(picks_file) as f:
                picks = json.load(f)

            picks_date = picks.get("date")
            today = datetime.now().strftime("%Y-%m-%d")

            # Warning if not from today (might be weekend/holiday)
            self.check(
                "Daily picks fresh",
                picks_date == today,
                f"Daily picks not from today (last: {picks_date})",
                warning=True
            )

        except Exception as e:
            self.check("Daily picks check", False, f"Picks check error: {str(e)}", warning=True)

    def run_all_checks(self):
        """Run all integrity checks"""
        print("="*70)
        print("PAPER TRADING LAB - DAILY DATA INTEGRITY CHECK")
        print("="*70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 1. Check critical files exist
        print("1. Checking critical files...")
        self.check_file_exists("portfolio_data/current_portfolio.json")
        self.check_file_exists("portfolio_data/account_status.json")
        self.check_file_exists("portfolio_data/daily_activity.json")
        self.check_file_exists("trade_history/completed_trades.csv")
        self.check_file_exists("dashboard_data/daily_picks.json", required=False)
        print()

        # 2. Check JSON validity
        print("2. Validating JSON files...")
        if (self.project_dir / "portfolio_data/current_portfolio.json").exists():
            self.check_json_valid("portfolio_data/current_portfolio.json")
        if (self.project_dir / "portfolio_data/account_status.json").exists():
            self.check_json_valid("portfolio_data/account_status.json")
        if (self.project_dir / "portfolio_data/daily_activity.json").exists():
            self.check_json_valid("portfolio_data/daily_activity.json")
        if (self.project_dir / "dashboard_data/daily_picks.json").exists():
            self.check_json_valid("dashboard_data/daily_picks.json")
        print()

        # 3. Check data consistency
        print("3. Checking data consistency...")
        self.check_portfolio_consistency()
        self.check_account_consistency()
        self.check_csv_integrity()
        self.check_portfolio_csv_sync()
        print()

        # 4. Check freshness
        print("4. Checking data freshness...")
        self.check_daily_activity_freshness()
        self.check_daily_picks_freshness()
        print()

        # 5. Summary
        print("="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Checks passed: {self.checks_passed}/{self.checks_total}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ ALL CHECKS PASSED - System integrity verified")
            return 0
        elif not self.errors:
            print("\n⚠️  WARNINGS DETECTED - Review recommended")
            return 0
        else:
            print("\n❌ ERRORS DETECTED - Immediate action required!")
            return 1

if __name__ == "__main__":
    # Get project directory (default to current directory)
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    checker = DataIntegrityChecker(project_dir)
    exit_code = checker.run_all_checks()

    sys.exit(exit_code)
