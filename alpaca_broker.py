#!/usr/bin/env python3
"""
Alpaca Broker Wrapper for Tedbot v7.1.1
Paper Trading Integration Module

This module provides a clean abstraction layer for Alpaca's API, supporting:
- Paper trading account management
- Position tracking and portfolio queries
- Market order execution (buy/sell)
- Real-time price data
- Historical price bars

Environment Variables Required:
- ALPACA_API_KEY: Your Alpaca API key
- ALPACA_SECRET_KEY: Your Alpaca secret key
- ALPACA_BASE_URL: https://paper-api.alpaca.markets (paper trading)
                   https://api.alpaca.markets (live trading - NOT recommended for MVP)
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

try:
    import alpaca_trade_api as tradeapi
except ImportError:
    print("⚠️  WARNING: alpaca-trade-api not installed")
    print("   Install with: pip install alpaca-trade-api")
    tradeapi = None


class AlpacaBroker:
    """
    Wrapper for Alpaca API - handles all brokerage operations
    Replaces manual portfolio tracking with real brokerage API
    """

    def __init__(self, api_key=None, secret_key=None, base_url=None, paper=True):
        """
        Initialize Alpaca broker connection

        Args:
            api_key: Alpaca API key (defaults to ALPACA_API_KEY env var)
            secret_key: Alpaca secret key (defaults to ALPACA_SECRET_KEY env var)
            base_url: Alpaca base URL (defaults to ALPACA_BASE_URL env var)
            paper: If True, forces paper trading URL (safety check)
        """
        if tradeapi is None:
            raise ImportError("alpaca-trade-api package not installed")

        self.api_key = api_key or os.environ.get('ALPACA_API_KEY')
        self.secret_key = secret_key or os.environ.get('ALPACA_SECRET_KEY')
        self.base_url = base_url or os.environ.get('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials not found. Set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables.")

        # Safety check: Ensure we're using paper trading for MVP
        if paper and 'paper' not in self.base_url:
            logging.warning(f"⚠️  Paper trading requested but base_url is {self.base_url}")
            logging.warning("   Forcing paper trading URL for safety")
            self.base_url = 'https://paper-api.alpaca.markets'

        # Initialize Alpaca REST API
        self.api = tradeapi.REST(
            self.api_key,
            self.secret_key,
            self.base_url,
            api_version='v2'
        )

        # Test connection
        try:
            account = self.api.get_account()
            logging.info(f"✓ Connected to Alpaca ({self.base_url})")
            logging.info(f"  Account Status: {account.status}")
            logging.info(f"  Buying Power: ${float(account.buying_power):,.2f}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Alpaca: {e}")

    # =====================================================================
    # ACCOUNT MANAGEMENT
    # =====================================================================

    def get_account(self):
        """
        Get account info (buying power, equity, cash, etc)

        Returns:
            Account object with fields:
            - equity: Total account value
            - cash: Cash available
            - buying_power: Margin buying power
            - portfolio_value: Value of positions
            - status: Account status (ACTIVE, etc)
        """
        return self.api.get_account()

    def get_account_value(self) -> float:
        """Get total account equity as a float"""
        account = self.get_account()
        return float(account.equity)

    def get_cash_available(self) -> float:
        """Get available cash as a float"""
        account = self.get_account()
        return float(account.cash)

    def get_buying_power(self) -> float:
        """Get buying power as a float"""
        account = self.get_account()
        return float(account.buying_power)

    # =====================================================================
    # POSITION MANAGEMENT
    # =====================================================================

    def get_positions(self):
        """
        Get all open positions

        Returns:
            List of Position objects with fields:
            - symbol: Ticker symbol
            - qty: Number of shares
            - avg_entry_price: Average entry price
            - current_price: Current market price
            - market_value: Current position value
            - cost_basis: Total cost basis
            - unrealized_pl: Unrealized profit/loss (dollars)
            - unrealized_plpc: Unrealized P/L percent (0.05 = 5%)
            - side: 'long' or 'short'
        """
        return self.api.list_positions()

    def get_position(self, ticker: str):
        """
        Get specific position

        Args:
            ticker: Stock symbol (e.g., 'AAPL')

        Returns:
            Position object or None if no position exists
        """
        try:
            return self.api.get_position(ticker)
        except:
            return None

    def has_position(self, ticker: str) -> bool:
        """Check if we have an open position in this ticker"""
        return self.get_position(ticker) is not None

    # =====================================================================
    # ORDER EXECUTION
    # =====================================================================

    def place_market_order(self, ticker: str, qty: int, side: str = 'buy'):
        """
        Place market order (executes immediately at current market price)

        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            qty: Number of shares (integer)
            side: 'buy' or 'sell'

        Returns:
            Order object with fields:
            - id: Order ID
            - client_order_id: Client-side order ID
            - status: Order status (new, filled, canceled, etc)
            - filled_avg_price: Average fill price
            - filled_qty: Quantity filled
        """
        if qty <= 0:
            raise ValueError(f"Invalid quantity: {qty}. Must be > 0")

        if side.lower() not in ['buy', 'sell']:
            raise ValueError(f"Invalid side: {side}. Must be 'buy' or 'sell'")

        return self.api.submit_order(
            symbol=ticker,
            qty=qty,
            side=side.lower(),
            type='market',
            time_in_force='day'  # Cancel at end of day if not filled
        )

    def place_limit_order(self, ticker: str, qty: int, limit_price: float, side: str = 'buy'):
        """
        Place limit order (only executes at specified price or better)

        Args:
            ticker: Stock symbol
            qty: Number of shares
            limit_price: Max price for buy, min price for sell
            side: 'buy' or 'sell'

        Returns:
            Order object
        """
        if qty <= 0:
            raise ValueError(f"Invalid quantity: {qty}. Must be > 0")

        if limit_price <= 0:
            raise ValueError(f"Invalid limit price: {limit_price}. Must be > 0")

        return self.api.submit_order(
            symbol=ticker,
            qty=qty,
            side=side.lower(),
            type='limit',
            limit_price=limit_price,
            time_in_force='day'
        )

    def get_order(self, order_id: str):
        """Get order details by order ID"""
        return self.api.get_order(order_id)

    def get_orders(self, status: str = 'open'):
        """
        Get orders by status

        Args:
            status: 'open', 'closed', or 'all'

        Returns:
            List of Order objects
        """
        return self.api.list_orders(status=status)

    def cancel_order(self, order_id: str):
        """Cancel a specific order"""
        return self.api.cancel_order(order_id)

    def cancel_all_orders(self):
        """Cancel all open orders"""
        return self.api.cancel_all_orders()

    # =====================================================================
    # TRAILING STOP ORDERS (Real-time execution by Alpaca)
    # =====================================================================

    def place_trailing_stop_order(self, ticker: str, qty: int, trail_percent: float = 2.0) -> Tuple[bool, str, Optional[str]]:
        """
        Place trailing stop sell order - Alpaca monitors and executes in real-time

        When the position's price drops by trail_percent from its peak,
        Alpaca automatically executes a market sell order.

        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            qty: Number of shares to sell
            trail_percent: Percentage to trail below peak (e.g., 2.0 = 2%)

        Returns:
            Tuple of (success: bool, message: str, order_id: str or None)
        """
        if qty <= 0:
            return False, f"Invalid quantity: {qty}. Must be > 0", None

        if trail_percent <= 0 or trail_percent > 10:
            return False, f"Invalid trail_percent: {trail_percent}. Must be between 0 and 10", None

        try:
            # First cancel any existing open orders for this symbol
            # (avoid duplicate trailing stops)
            self.cancel_orders_for_symbol(ticker)

            # Place trailing stop order
            order = self.api.submit_order(
                symbol=ticker,
                qty=qty,
                side='sell',
                type='trailing_stop',
                trail_percent=str(trail_percent),  # Alpaca API expects string
                time_in_force='gtc'  # Good-til-canceled (persists across days)
            )

            return True, f"Trailing stop placed: {qty} shares, trail {trail_percent}%", order.id

        except Exception as e:
            return False, f"Failed to place trailing stop for {ticker}: {str(e)}", None

    def get_orders_for_symbol(self, ticker: str, status: str = 'open') -> List:
        """
        Get orders for a specific symbol

        Args:
            ticker: Stock symbol
            status: 'open', 'closed', or 'all'

        Returns:
            List of Order objects for this symbol
        """
        try:
            all_orders = self.api.list_orders(status=status)
            return [o for o in all_orders if o.symbol == ticker]
        except Exception as e:
            logging.warning(f"Failed to get orders for {ticker}: {e}")
            return []

    def cancel_orders_for_symbol(self, ticker: str) -> Tuple[int, List[str]]:
        """
        Cancel all open orders for a specific symbol

        Args:
            ticker: Stock symbol

        Returns:
            Tuple of (count_canceled: int, order_ids: List[str])
        """
        canceled = []
        try:
            orders = self.get_orders_for_symbol(ticker, status='open')
            for order in orders:
                try:
                    self.api.cancel_order(order.id)
                    canceled.append(order.id)
                except Exception as e:
                    logging.warning(f"Failed to cancel order {order.id}: {e}")
        except Exception as e:
            logging.warning(f"Failed to get orders for {ticker}: {e}")

        return len(canceled), canceled

    def has_trailing_stop_order(self, ticker: str) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Check if there's an existing trailing stop order for a symbol

        Args:
            ticker: Stock symbol

        Returns:
            Tuple of (has_order: bool, order_id: str or None, trail_percent: float or None)
        """
        try:
            orders = self.get_orders_for_symbol(ticker, status='open')
            for order in orders:
                if order.type == 'trailing_stop' and order.side == 'sell':
                    trail_pct = float(order.trail_percent) if hasattr(order, 'trail_percent') and order.trail_percent else None
                    return True, order.id, trail_pct
            return False, None, None
        except Exception as e:
            logging.warning(f"Failed to check trailing stop for {ticker}: {e}")
            return False, None, None

    def update_trailing_stop(self, ticker: str, qty: int, new_trail_percent: float) -> Tuple[bool, str, Optional[str]]:
        """
        Update an existing trailing stop order (cancel and replace)

        Args:
            ticker: Stock symbol
            qty: Number of shares
            new_trail_percent: New trail percentage

        Returns:
            Tuple of (success: bool, message: str, new_order_id: str or None)
        """
        # Cancel existing and place new
        return self.place_trailing_stop_order(ticker, qty, new_trail_percent)

    # =====================================================================
    # PRICE DATA
    # =====================================================================

    def get_last_price(self, ticker: str) -> float:
        """
        Get latest price for ticker

        Args:
            ticker: Stock symbol

        Returns:
            Most recent trade price as float
        """
        try:
            trade = self.api.get_latest_trade(ticker)
            return float(trade.price)
        except Exception as e:
            logging.warning(f"Failed to fetch price for {ticker}: {e}")
            return 0.0

    def get_last_prices(self, tickers: List[str]) -> Dict[str, float]:
        """
        Get latest prices for multiple tickers (batch operation)

        Args:
            tickers: List of stock symbols

        Returns:
            Dict of {ticker: price}
        """
        prices = {}
        for ticker in tickers:
            prices[ticker] = self.get_last_price(ticker)
        return prices

    def get_bars(self, ticker: str, timeframe: str = '1Day', limit: int = 100,
                 start: Optional[datetime] = None, end: Optional[datetime] = None):
        """
        Get historical price bars

        Args:
            ticker: Stock symbol
            timeframe: '1Min', '5Min', '15Min', '1Hour', '1Day'
            limit: Number of bars to retrieve (max 10000)
            start: Start date (optional, overrides limit)
            end: End date (optional, defaults to now)

        Returns:
            List of Bar objects with fields:
            - t: Timestamp
            - o: Open price
            - h: High price
            - l: Low price
            - c: Close price
            - v: Volume
        """
        if start and end:
            return self.api.get_bars(ticker, timeframe, start=start.isoformat(), end=end.isoformat()).df
        else:
            return self.api.get_bars(ticker, timeframe, limit=limit).df

    def get_snapshot(self, ticker: str):
        """
        Get current snapshot with latest trade, quote, and bar data

        Returns:
            Snapshot object with comprehensive market data
        """
        return self.api.get_snapshot(ticker)

    # =====================================================================
    # PORTFOLIO HELPERS (For Tedbot Integration)
    # =====================================================================

    def get_portfolio_summary(self) -> Dict:
        """
        Get portfolio summary in Tedbot-compatible format

        Returns:
            Dict with:
            - positions: List of position dicts
            - total_positions: Count
            - portfolio_value: Total value
            - cash: Available cash
            - total_return_pct: Total return percentage
            - last_updated: Timestamp
        """
        account = self.get_account()
        positions = self.get_positions()

        position_list = []
        for pos in positions:
            position_list.append({
                'ticker': pos.symbol,
                'shares': float(pos.qty),
                'entry_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price),
                'position_size': float(pos.market_value),
                'cost_basis': float(pos.cost_basis),
                'unrealized_gain_pct': float(pos.unrealized_plpc) * 100,  # Convert to percentage
                'unrealized_gain_dollars': float(pos.unrealized_pl),
                'side': pos.side
            })

        # Calculate total return vs starting capital
        # Note: This assumes starting capital tracking elsewhere
        # For now, just use portfolio value
        equity = float(account.equity)

        return {
            'positions': position_list,
            'total_positions': len(position_list),
            'portfolio_value': equity,
            'cash': float(account.cash),
            'buying_power': float(account.buying_power),
            'total_return_pct': 0.0,  # Need to calculate vs starting capital
            'last_updated': datetime.now().isoformat(),
            'portfolio_status': f"{len(position_list)} active positions" if position_list else "Empty - No active positions"
        }

    def close_position(self, ticker: str, qty: Optional[int] = None) -> Tuple[bool, str]:
        """
        Close a position (sell all or partial shares)

        Args:
            ticker: Stock symbol
            qty: Number of shares to sell (None = close entire position)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            position = self.get_position(ticker)
            if not position:
                return False, f"No position found for {ticker}"

            shares_to_sell = qty if qty else int(float(position.qty))

            order = self.place_market_order(ticker, shares_to_sell, side='sell')

            return True, f"Submitted sell order for {shares_to_sell} shares of {ticker} (Order ID: {order.id})"

        except Exception as e:
            return False, f"Failed to close {ticker}: {str(e)}"


# =====================================================================
# TESTING / VALIDATION
# =====================================================================

def test_connection():
    """Test Alpaca connection and print account info"""
    try:
        broker = AlpacaBroker()

        print("\n" + "="*60)
        print("ALPACA CONNECTION TEST")
        print("="*60 + "\n")

        # Account info
        account = broker.get_account()
        print(f"Account Status: {account.status}")
        print(f"Account Value: ${float(account.equity):,.2f}")
        print(f"Cash Available: ${float(account.cash):,.2f}")
        print(f"Buying Power: ${float(account.buying_power):,.2f}\n")

        # Positions
        positions = broker.get_positions()
        print(f"Open Positions: {len(positions)}")
        for pos in positions:
            print(f"  {pos.symbol}: {pos.qty} shares @ ${float(pos.avg_entry_price):.2f}")
            print(f"    Current: ${float(pos.current_price):.2f} | P/L: {float(pos.unrealized_plpc)*100:+.2f}%")

        print("\n✓ Connection successful!\n")
        return True

    except Exception as e:
        print(f"\n✗ Connection failed: {e}\n")
        return False


if __name__ == '__main__':
    # Run connection test when script is executed directly
    test_connection()
