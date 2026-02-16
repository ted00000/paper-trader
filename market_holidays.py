#!/usr/bin/env python3
"""
Market Holiday Checker for Tedbot

Prevents trading on US stock market holidays.
Called by cron wrapper scripts before executing commands.

Exit codes:
  0 = Market is OPEN (proceed with trading)
  1 = Market is CLOSED (skip trading)

Usage:
  python3 market_holidays.py && python3 agent_v5.5.py go
"""

from datetime import datetime, date
import sys

# US Stock Market Holidays for 2026
# Source: NYSE/NASDAQ holiday calendar
MARKET_HOLIDAYS_2026 = [
    date(2026, 1, 1),    # New Year's Day (Thu)
    date(2026, 1, 19),   # Martin Luther King Jr. Day (Mon)
    date(2026, 2, 16),   # Presidents Day (Mon)
    date(2026, 4, 3),    # Good Friday (Fri)
    date(2026, 5, 25),   # Memorial Day (Mon)
    date(2026, 7, 3),    # Independence Day (observed, Fri)
    date(2026, 9, 7),    # Labor Day (Mon)
    date(2026, 11, 26),  # Thanksgiving Day (Thu)
    date(2026, 12, 25),  # Christmas Day (Fri)
]

# Early close days (1:00 PM ET) - not blocking, just informational
EARLY_CLOSE_2026 = [
    date(2026, 11, 27),  # Day after Thanksgiving
    date(2026, 12, 24),  # Christmas Eve
]

def is_market_holiday(check_date=None):
    """
    Check if the given date is a US stock market holiday.

    Args:
        check_date: date object to check (defaults to today)

    Returns:
        True if market is closed, False if open
    """
    if check_date is None:
        check_date = date.today()

    # Weekend check
    if check_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return True

    # Holiday check
    if check_date in MARKET_HOLIDAYS_2026:
        return True

    return False

def get_holiday_name(check_date=None):
    """Get the name of the holiday if it's a holiday."""
    if check_date is None:
        check_date = date.today()

    holiday_names = {
        date(2026, 1, 1): "New Year's Day",
        date(2026, 1, 19): "Martin Luther King Jr. Day",
        date(2026, 2, 16): "Presidents Day",
        date(2026, 4, 3): "Good Friday",
        date(2026, 5, 25): "Memorial Day",
        date(2026, 7, 3): "Independence Day (observed)",
        date(2026, 9, 7): "Labor Day",
        date(2026, 11, 26): "Thanksgiving Day",
        date(2026, 12, 25): "Christmas Day",
    }

    if check_date.weekday() == 5:
        return "Saturday"
    elif check_date.weekday() == 6:
        return "Sunday"
    elif check_date in holiday_names:
        return holiday_names[check_date]

    return None

def main():
    """Main entry point for CLI usage."""
    today = date.today()

    if is_market_holiday(today):
        holiday_name = get_holiday_name(today)
        print(f"MARKET CLOSED: {holiday_name} ({today})")
        print("Skipping all trading commands.")
        sys.exit(1)  # Exit code 1 = market closed
    else:
        print(f"MARKET OPEN: {today} ({today.strftime('%A')})")
        sys.exit(0)  # Exit code 0 = market open

if __name__ == "__main__":
    main()
