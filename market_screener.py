#!/usr/bin/env python3
"""
MARKET SCREENER - S&P 1500 Universe Scanner
============================================

Scans the S&P 1500 daily to find stocks with:
- Relative Strength ≥3% vs sector
- Recent catalysts (news, volume, technical)
- Composite scoring and ranking

Output: Top 50 candidates for Claude to select from

Author: Paper Trading Lab
Version: 1.0.0
Created: 2025-11-10
"""

import os
import sys
import json
import requests
import re
from datetime import datetime, timedelta
from pathlib import Path
import time

# Configuration
PROJECT_DIR = Path(__file__).parent
POLYGON_API_KEY = os.environ.get('POLYGON_API_KEY', '')
FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY', '')
FMP_API_KEY = os.environ.get('FMP_API_KEY', '')  # PHASE 2.2: Financial Modeling Prep (free tier)

# S&P 1500 Sector ETF Mapping (same as agent)
SECTOR_ETF_MAP = {
    'Technology': 'XLK',
    'Healthcare': 'XLV',
    'Financials': 'XLF',
    'Consumer Discretionary': 'XLY',
    'Industrials': 'XLI',
    'Consumer Staples': 'XLP',
    'Energy': 'XLE',
    'Utilities': 'XLU',
    'Real Estate': 'XLRE',
    'Materials': 'XLB',
    'Communication Services': 'XLC'
}

# Screening Parameters
MIN_RS_PCT = 3.0  # Minimum relative strength
MIN_PRICE = 5.0   # Minimum stock price
MIN_MARKET_CAP = 1_000_000_000  # $1B minimum
TOP_N_CANDIDATES = 50  # Number to output


# ============================================================================
# PHASE 1.3-1.4: NEWS PARSING HELPERS (Contract values, Guidance, M&A premiums)
# ============================================================================

def parse_contract_value(text):
    """
    Extract contract/deal value from news text.

    Examples:
    - "$500M contract" -> 500000000
    - "$1.2B deal" -> 1200000000
    - "contract worth $75 million" -> 75000000
    - "$10M order" -> 10000000

    Returns: float (dollar amount) or None if not found
    """
    # Patterns to match: $500M, $1.2B, $75 million, etc.
    patterns = [
        r'\$(\d+(?:\.\d+)?)\s*billion',
        r'\$(\d+(?:\.\d+)?)\s*B\b',
        r'\$(\d+(?:\.\d+)?)\s*million',
        r'\$(\d+(?:\.\d+)?)\s*M\b',
        r'(\d+(?:\.\d+)?)\s*billion\s*dollar',
        r'(\d+(?:\.\d+)?)\s*million\s*dollar',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            # Convert to dollars
            if 'billion' in pattern.lower() or r'\s*B\b' in pattern:
                return value * 1_000_000_000
            else:  # million
                return value * 1_000_000

    return None


def parse_guidance_magnitude(text):
    """
    Extract guidance raise/lower percentage from news text.

    Examples:
    - "raises guidance by 20%" -> 20.0
    - "guidance raised 15%" -> 15.0
    - "lowers outlook by 10%" -> -10.0
    - "cuts guidance 25%" -> -25.0

    Returns: float (percentage) or None if not found
    """
    # Patterns for guidance raises
    raise_patterns = [
        r'raises?\s+guidance\s+(?:by\s+)?(\d+(?:\.\d+)?)%',
        r'guidance\s+raised\s+(?:by\s+)?(\d+(?:\.\d+)?)%',
        r'increases?\s+guidance\s+(?:by\s+)?(\d+(?:\.\d+)?)%',
        r'lifts?\s+outlook\s+(?:by\s+)?(\d+(?:\.\d+)?)%',
    ]

    # Patterns for guidance cuts
    lower_patterns = [
        r'lowers?\s+guidance\s+(?:by\s+)?(\d+(?:\.\d+)?)%',
        r'guidance\s+lowered\s+(?:by\s+)?(\d+(?:\.\d+)?)%',
        r'cuts?\s+guidance\s+(?:by\s+)?(\d+(?:\.\d+)?)%',
        r'reduces?\s+outlook\s+(?:by\s+)?(\d+(?:\.\d+)?)%',
    ]

    # Check raises
    for pattern in raise_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

    # Check cuts (return negative)
    for pattern in lower_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return -float(match.group(1))

    return None


def parse_ma_premium(text):
    """
    Extract M&A deal premium percentage from news text.

    Examples:
    - "acquired for 25% premium" -> 25.0
    - "buyout at 30% premium to closing price" -> 30.0
    - "premium of 20%" -> 20.0

    Returns: float (percentage) or None if not found
    """
    patterns = [
        r'(\d+(?:\.\d+)?)%\s+premium',
        r'premium\s+of\s+(\d+(?:\.\d+)?)%',
        r'at\s+(?:a\s+)?(\d+(?:\.\d+)?)%\s+premium',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

    return None


def classify_fda_approval(text):
    """
    Classify FDA approval type from news text.

    Types (priority order):
    - BREAKTHROUGH: Breakthrough therapy designation (most valuable)
    - PRIORITY: Priority review or fast track
    - STANDARD: Standard FDA approval
    - EXPANDED: Expanded indication (additional use approved)
    - LIMITED: Limited indication or conditional approval

    Returns: str (approval type) or None if not found
    """
    # Breakthrough therapy (highest value)
    if any(keyword in text for keyword in ['breakthrough therapy', 'breakthrough designation', 'breakthrough status']):
        return 'BREAKTHROUGH'

    # Priority review / fast track
    if any(keyword in text for keyword in ['priority review', 'fast track', 'accelerated approval', 'expedited review']):
        return 'PRIORITY'

    # Expanded indication (additional use)
    if any(keyword in text for keyword in ['expanded indication', 'additional indication', 'new indication', 'label expansion']):
        return 'EXPANDED'

    # Limited/conditional
    if any(keyword in text for keyword in ['limited indication', 'conditional approval', 'restricted use']):
        return 'LIMITED'

    # Standard approval (generic FDA approval)
    if any(keyword in text for keyword in ['fda approv', 'fda clearance', 'approved by fda']):
        return 'STANDARD'

    return None


class MarketScreener:
    """Scans S&P 1500 for high-probability swing trade candidates"""

    def __init__(self):
        self.api_key = POLYGON_API_KEY
        self.finnhub_key = FINNHUB_API_KEY
        self.fmp_key = FMP_API_KEY  # PHASE 2.2
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.scan_results = []

        # Cache for Finnhub data (reduce API calls)
        self.earnings_calendar_cache = None
        self.analyst_ratings_cache = {}
        self.insider_transactions_cache = {}
        self.earnings_surprises_cache = {}
        self.revenue_surprises_cache = {}  # PHASE 2.2: FMP revenue data

        # PHASE 3.1: IBD-style RS percentile ranking
        # Store all stock returns during scan for percentile calculation
        self.all_stock_returns = {}  # {ticker: 3month_return}

        # PHASE 3.3: Real-time sector classification cache
        self.sector_cache = {}  # {ticker: sector_name}

        if not self.api_key:
            raise ValueError("POLYGON_API_KEY not set in environment")

        if not self.finnhub_key:
            print("   ⚠️ WARNING: FINNHUB_API_KEY not set - Tier 1 catalyst detection disabled")
            print("   Sign up at https://finnhub.io/register for free API key\n")

    def get_sp1500_tickers(self):
        """
        Load S&P 1500 ticker list from Polygon API

        Fetches all US stocks meeting our criteria:
        - Listed on major exchanges (NYSE, NASDAQ, AMEX)
        - Common stock type (CS)
        - Active and primary listings
        - Filters out ETFs, ADRs, preferred shares

        Returns: List of ticker symbols (~1500 stocks)
        """
        try:
            print("   Fetching S&P 1500 universe from Polygon API...")

            # Get all US stock tickers
            url = f'https://api.polygon.io/v3/reference/tickers'
            params = {
                'market': 'stocks',
                'active': 'true',
                'type': 'CS',  # Common stock only
                'limit': 1000,  # Max per page
                'apiKey': self.api_key
            }

            all_tickers = []
            next_url = url

            # Paginate through results (need ~2 calls for 1500+ stocks)
            for page in range(3):  # Max 3 pages = 3000 stocks
                if next_url == url:
                    response = requests.get(url, params=params, timeout=30)
                else:
                    response = requests.get(next_url, timeout=30)

                data = response.json()

                if data.get('status') in ['OK', 'DELAYED'] and 'results' in data:
                    for ticker_data in data['results']:
                        ticker = ticker_data.get('ticker', '')
                        ticker_type = ticker_data.get('type', '')
                        primary_exchange = ticker_data.get('primary_exchange', '')

                        # Filter criteria:
                        # 1. Must be on major exchange
                        # 2. Must be common stock (type = CS)
                        # 3. Clean ticker format
                        if ticker and ticker_type == 'CS':
                            # Exclude ETFs, ADRs, preferred shares, warrants, units
                            if (not any(x in ticker for x in ['.', '-', '^', '=', '/']) and
                                len(ticker) <= 5 and  # Most stocks are 1-5 characters
                                ticker.isalpha() and  # Only letters, no numbers
                                ticker.isupper()):  # All uppercase
                                all_tickers.append(ticker)

                    # Check for next page
                    next_url = data.get('next_url', None)

                    # Stop if we have enough or no more pages
                    if len(all_tickers) >= 1500 or not next_url:
                        break
                else:
                    break

                time.sleep(0.2)  # Rate limit protection

            # Limit to 1500 stocks
            all_tickers = all_tickers[:1500]

            # Sort alphabetically for consistency
            all_tickers.sort()

            print(f"   Loaded {len(all_tickers)} tickers from Polygon API")
            print(f"   (US common stocks, active on major exchanges)\n")

            # If we got fewer than 500, fall back to curated list
            if len(all_tickers) < 500:
                raise Exception(f"Only got {len(all_tickers)} tickers, using fallback")

            return all_tickers

        except Exception as e:
            print(f"   ⚠️ Error fetching tickers from Polygon: {e}")
            print(f"   Falling back to curated list of 500 major stocks\n")

            # Fallback: Return curated list of 500 major stocks
            fallback_list = [
                # Technology (XLK)
                'AAPL', 'MSFT', 'NVDA', 'AVGO', 'ORCL', 'CRM', 'CSCO', 'ADBE', 'ACN', 'AMD',
                'INTC', 'IBM', 'TXN', 'QCOM', 'AMAT', 'MU', 'LRCX', 'KLAC', 'SNPS', 'CDNS',
                'PLTR', 'NOW', 'PANW', 'FTNT', 'CRWD', 'WDAY', 'TEAM', 'DDOG', 'NET', 'ZS',
                'ANET', 'SMCI', 'MRVL', 'ARM', 'SNOW', 'SPLK', 'OKTA', 'ZM', 'DOCU', 'MDB',

                # Healthcare (XLV)
                'LLY', 'UNH', 'JNJ', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'PFE', 'BMY',
                'AMGN', 'GILD', 'CVS', 'CI', 'VRTX', 'REGN', 'HUM', 'ISRG', 'SYK', 'BSX',
                'MDLZ', 'MDT', 'BDX', 'ELV', 'ZTS', 'IDXX', 'EW', 'RMD', 'DXCM', 'ALGN',

                # Financials (XLF)
                'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SPGI', 'AXP', 'USB',
                'PNC', 'TFC', 'SCHW', 'BK', 'COF', 'CME', 'ICE', 'AON', 'MMC', 'MCO',
                'CB', 'PGR', 'TRV', 'ALL', 'AIG', 'MET', 'PRU', 'AFL', 'COIN', 'SOFI', 'HOOD',

                # Consumer Discretionary (XLY)
                'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'LOW', 'SBUX', 'TJX', 'BKNG', 'ABNB',
                'CMG', 'ORLY', 'AZO', 'GM', 'F', 'MAR', 'HLT', 'YUM', 'DRI', 'ULTA',
                'SHOP', 'UBER', 'DASH', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'RBLX', 'ETSY',

                # Communication Services (XLC)
                'META', 'GOOGL', 'GOOG', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'TMUS', 'CHTR',
                'EA', 'TTWO', 'ATVI', 'SNAP', 'PINS', 'MTCH', 'SPOT', 'ROKU',

                # Industrials (XLI)
                'CAT', 'BA', 'UNP', 'HON', 'UPS', 'RTX', 'LMT', 'DE', 'GE', 'MMM',
                'GD', 'NOC', 'ETN', 'EMR', 'ITW', 'PH', 'CSX', 'NSC', 'FDX', 'WM',
                'RSG', 'CARR', 'OTIS', 'PCAR', 'CMI', 'AME', 'FAST', 'PAYX', 'VRSK', 'IEX',

                # Consumer Staples (XLP)
                'WMT', 'PG', 'COST', 'KO', 'PEP', 'PM', 'MO', 'MDLZ', 'CL', 'KMB',
                'GIS', 'K', 'HSY', 'SYY', 'KHC', 'CAG', 'CPB', 'STZ', 'TAP', 'TSN',
                'CHD', 'CLX', 'MKC', 'SJM', 'HRL', 'LW', 'BG', 'ADM', 'MNST', 'KDP',

                # Energy (XLE)
                'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HES',
                'HAL', 'BKR', 'FANG', 'DVN', 'MRO', 'APA', 'CTRA', 'OVV', 'EQT', 'PR',

                # Materials (XLB)
                'LIN', 'APD', 'ECL', 'SHW', 'FCX', 'NEM', 'DD', 'DOW', 'PPG', 'VMC',
                'MLM', 'NUE', 'STLD', 'IP', 'PKG', 'BALL', 'AVY', 'ALB', 'CE', 'EMN',

                # Utilities (XLU)
                'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL', 'ED', 'PEG',
                'ES', 'AWK', 'DTE', 'PCG', 'EIX', 'WEC', 'PPL', 'CNP', 'AEE', 'CMS',

                # Real Estate (XLRE)
                'PLD', 'AMT', 'EQIX', 'PSA', 'WELL', 'DLR', 'O', 'CBRE', 'SPG', 'AVB',
                'EQR', 'VTR', 'BXP', 'ARE', 'ESS', 'MAA', 'UDR', 'HST', 'REG', 'KIM'
            ]

            # Add more mid/small caps to reach closer to 500
            # ... (would add more here but keeping it reasonable for fallback)

            return fallback_list[:500]

    def get_stock_sector(self, ticker):
        """
        PHASE 3.3: Get stock sector from Polygon API (real-time classification)

        Uses Polygon's ticker details API to get accurate GICS sector classification.
        Caches results to reduce API calls.

        Returns: Sector name (defaults to 'Technology' if API fails)
        """
        # Check cache first
        if ticker in self.sector_cache:
            return self.sector_cache[ticker]

        try:
            # Query Polygon ticker details API
            url = f'https://api.polygon.io/v3/reference/tickers/{ticker}'
            params = {'apiKey': self.api_key}

            response = requests.get(url, params=params, timeout=5)
            data = response.json()

            if response.status_code == 200 and 'results' in data:
                # Polygon provides SIC sector description
                sic_description = data['results'].get('sic_description', '')

                # Map SIC description to our sector ETFs
                sector = self._map_sic_to_sector(sic_description, ticker)

                # Cache the result
                self.sector_cache[ticker] = sector
                return sector
            else:
                # API failed, use fallback
                sector = self._fallback_sector_mapping(ticker)
                self.sector_cache[ticker] = sector
                return sector

        except Exception:
            # Network error or timeout, use fallback
            sector = self._fallback_sector_mapping(ticker)
            self.sector_cache[ticker] = sector
            return sector

    def _map_sic_to_sector(self, sic_description, ticker):
        """
        Map Polygon SIC description to our 11 sector categories

        Args:
            sic_description: SIC industry description from Polygon
            ticker: Stock ticker (for fallback mapping)

        Returns: Sector name matching SECTOR_ETF_MAP keys
        """
        if not sic_description:
            return self._fallback_sector_mapping(ticker)

        sic = sic_description.lower()

        # Technology
        if any(keyword in sic for keyword in ['software', 'computer', 'semiconductor', 'electronic', 'internet', 'technology', 'data processing']):
            return 'Technology'

        # Healthcare
        if any(keyword in sic for keyword in ['pharma', 'drug', 'medical', 'healthcare', 'hospital', 'biotech', 'health services']):
            return 'Healthcare'

        # Financials
        if any(keyword in sic for keyword in ['bank', 'financial', 'insurance', 'investment', 'securities', 'credit', 'mortgage']):
            return 'Financials'

        # Consumer Discretionary
        if any(keyword in sic for keyword in ['retail', 'restaurant', 'hotel', 'auto', 'apparel', 'entertainment', 'leisure', 'home improvement']):
            return 'Consumer Discretionary'

        # Communication Services
        if any(keyword in sic for keyword in ['telecom', 'communication', 'broadcasting', 'media', 'cable', 'wireless']):
            return 'Communication Services'

        # Industrials
        if any(keyword in sic for keyword in ['industrial', 'aerospace', 'defense', 'machinery', 'transportation', 'construction', 'engineering']):
            return 'Industrials'

        # Consumer Staples
        if any(keyword in sic for keyword in ['food', 'beverage', 'tobacco', 'household products', 'personal products']):
            return 'Consumer Staples'

        # Energy
        if any(keyword in sic for keyword in ['oil', 'gas', 'energy', 'petroleum', 'coal']):
            return 'Energy'

        # Materials
        if any(keyword in sic for keyword in ['chemicals', 'metals', 'mining', 'paper', 'packaging', 'materials']):
            return 'Materials'

        # Utilities
        if any(keyword in sic for keyword in ['electric', 'utility', 'water', 'natural gas']):
            return 'Utilities'

        # Real Estate
        if any(keyword in sic for keyword in ['real estate', 'reit', 'property']):
            return 'Real Estate'

        # Default fallback
        return self._fallback_sector_mapping(ticker)

    def _fallback_sector_mapping(self, ticker):
        """
        Fallback sector mapping for when Polygon API is unavailable

        Returns: Sector name (defaults to 'Technology')
        """
        # Simple hardcoded mapping for common stocks (reduced from full list)
        tech_stocks = {'AAPL', 'MSFT', 'NVDA', 'AVGO', 'ORCL', 'CRM', 'CSCO', 'ADBE', 'AMD', 'INTC'}
        healthcare = {'LLY', 'UNH', 'JNJ', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'PFE', 'BMY'}
        financials = {'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SPGI', 'AXP', 'USB'}
        consumer_disc = {'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'LOW', 'SBUX', 'TJX', 'BKNG'}
        comm_services = {'META', 'GOOGL', 'GOOG', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'TMUS'}
        industrials = {'CAT', 'BA', 'UNP', 'HON', 'UPS', 'RTX', 'LMT', 'DE', 'GE', 'MMM'}
        consumer_staples = {'WMT', 'PG', 'COST', 'KO', 'PEP', 'PM', 'MO', 'MDLZ', 'CL'}
        energy = {'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO'}
        materials = {'LIN', 'APD', 'ECL', 'SHW', 'FCX', 'NEM', 'DD', 'DOW'}
        utilities = {'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL'}
        real_estate = {'PLD', 'AMT', 'EQIX', 'PSA', 'WELL', 'DLR', 'O', 'CBRE'}

        if ticker in tech_stocks:
            return 'Technology'
        elif ticker in healthcare:
            return 'Healthcare'
        elif ticker in financials:
            return 'Financials'
        elif ticker in consumer_disc:
            return 'Consumer Discretionary'
        elif ticker in comm_services:
            return 'Communication Services'
        elif ticker in industrials:
            return 'Industrials'
        elif ticker in consumer_staples:
            return 'Consumer Staples'
        elif ticker in energy:
            return 'Energy'
        elif ticker in materials:
            return 'Materials'
        elif ticker in utilities:
            return 'Utilities'
        elif ticker in real_estate:
            return 'Real Estate'
        else:
            return 'Technology'  # Default

    def get_3month_return(self, ticker):
        """
        Calculate 3-month return using Polygon API

        Returns: Float (percentage, e.g., 15.5 = +15.5%)
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)

            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_str}/{end_str}?apiKey={self.api_key}'
            response = requests.get(url, timeout=15)
            data = response.json()

            # Accept both 'OK' and 'DELAYED' status
            if data.get('status') in ['OK', 'DELAYED'] and 'results' in data and len(data['results']) >= 2:
                results = data['results']
                first_close = results[0]['c']
                last_close = results[-1]['c']
                return_pct = ((last_close - first_close) / first_close) * 100
                return round(return_pct, 2)

            return 0.0

        except Exception as e:
            # Silently fail individual stocks to avoid halting entire scan
            return 0.0

    def calculate_relative_strength(self, ticker, sector):
        """
        PHASE 3.1: Calculate stock's RS vs sector ETF + IBD-style percentile rank

        Returns: Dict with RS metrics including percentile rank (0-100)

        Note: Percentile rank is calculated after full scan in calculate_rs_percentiles()
        """
        sector_etf = SECTOR_ETF_MAP.get(sector, 'SPY')

        stock_return = self.get_3month_return(ticker)
        sector_return = self.get_3month_return(sector_etf)

        # Store stock return for later percentile calculation
        self.all_stock_returns[ticker] = stock_return

        rs = stock_return - sector_return

        return {
            'rs_pct': round(rs, 2),
            'stock_return_3m': stock_return,
            'sector_return_3m': sector_return,
            'sector_etf': sector_etf,
            'passed_filter': rs >= MIN_RS_PCT,
            'score': min(rs / 15 * 100, 100) if rs > 0 else 0,  # 15%+ RS = perfect score
            'rs_percentile': None  # Will be calculated after full scan
        }

    def calculate_rs_percentiles(self, candidates):
        """
        PHASE 3.1: Calculate IBD-style RS percentile rank (0-100) for all candidates

        IBD methodology:
        - 99 = Top 1% of all stocks (market leaders)
        - 90 = Top 10% (strong relative strength)
        - 80 = Top 20% (above average)
        - 50 = Average
        - <50 = Below average (generally avoid)

        Args:
            candidates: List of candidate dicts with 'ticker' and 'relative_strength' keys

        Returns: None (modifies candidates in-place)
        """
        if not self.all_stock_returns:
            print("   ⚠️ No stock returns collected - skipping percentile calculation")
            return

        # Get all return values sorted ascending
        all_returns = sorted(self.all_stock_returns.values())
        total_stocks = len(all_returns)

        print(f"\n   Calculating RS percentiles across {total_stocks} stocks...")

        # Calculate percentile for each candidate
        for candidate in candidates:
            ticker = candidate['ticker']
            stock_return = candidate['relative_strength']['stock_return_3m']

            # Find how many stocks this stock beats
            stocks_beaten = sum(1 for r in all_returns if r < stock_return)

            # Calculate percentile (0-100)
            percentile = int((stocks_beaten / total_stocks) * 100)

            # Update candidate with percentile
            candidate['relative_strength']['rs_percentile'] = percentile

        print(f"   ✓ RS percentiles calculated")

        # Print distribution summary
        percentile_90plus = sum(1 for c in candidates if c['relative_strength']['rs_percentile'] >= 90)
        percentile_80to89 = sum(1 for c in candidates if 80 <= c['relative_strength']['rs_percentile'] < 90)
        percentile_70to79 = sum(1 for c in candidates if 70 <= c['relative_strength']['rs_percentile'] < 80)

        print(f"   RS 90+ (top 10%): {percentile_90plus} stocks")
        print(f"   RS 80-89 (top 20%): {percentile_80to89} stocks")
        print(f"   RS 70-79 (top 30%): {percentile_70to79} stocks")

    def detect_sector_rotation(self):
        """
        PHASE 3.2: Detect sector rotation by analyzing sector ETF performance

        Identifies:
        - Leading sectors (outperforming SPY)
        - Lagging sectors (underperforming SPY)
        - Sector rotation trends (which sectors are rotating in/out)

        Returns: Dict with sector rotation analysis
        """
        print(f"\n   Analyzing sector rotation...")

        # Get SPY (market) performance as baseline
        spy_return = self.get_3month_return('SPY')

        # Calculate performance for each sector ETF
        sector_performance = {}
        for sector_name, etf in SECTOR_ETF_MAP.items():
            etf_return = self.get_3month_return(etf)
            relative_to_spy = etf_return - spy_return

            sector_performance[sector_name] = {
                'etf': etf,
                '3m_return': round(etf_return, 2),
                'vs_spy': round(relative_to_spy, 2),
                'is_leading': relative_to_spy > 2.0,  # Leading if 2%+ above SPY
                'is_lagging': relative_to_spy < -2.0  # Lagging if 2%+ below SPY
            }

        # Sort sectors by performance
        sorted_sectors = sorted(sector_performance.items(), key=lambda x: x[1]['3m_return'], reverse=True)

        # Identify leading and lagging sectors
        leading_sectors = [name for name, data in sorted_sectors if data['is_leading']]
        lagging_sectors = [name for name, data in sorted_sectors if data['is_lagging']]

        print(f"   ✓ Sector rotation analyzed")
        print(f"   SPY (market) 3-month return: {spy_return:+.1f}%")
        print(f"   Leading sectors ({len(leading_sectors)}): {', '.join(leading_sectors) if leading_sectors else 'None'}")
        print(f"   Lagging sectors ({len(lagging_sectors)}): {', '.join(lagging_sectors) if lagging_sectors else 'None'}")

        return {
            'spy_return': spy_return,
            'sector_performance': sector_performance,
            'leading_sectors': leading_sectors,
            'lagging_sectors': lagging_sectors,
            'sorted_sectors': sorted_sectors
        }

    def get_news_score(self, ticker):
        """
        Fetch and score recent news (last 7 days)

        Returns: Dict with news metrics INCLUDING top articles
        """
        try:
            # Get news from last 7 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            params = {
                'ticker': ticker,
                'published_utc.gte': start_date.strftime('%Y-%m-%d'),
                'published_utc.lte': end_date.strftime('%Y-%m-%d'),
                'order': 'desc',
                'limit': 20,
                'apiKey': self.api_key
            }

            response = requests.get('https://api.polygon.io/v2/reference/news', params=params, timeout=10)
            articles = response.json().get('results', [])

            if not articles:
                return {'score': 0, 'count': 0, 'keywords': [], 'scaled_score': 0, 'top_articles': []}

            # Score news articles with TIER 1 catalyst detection + RECENCY FILTERING
            # Tier 1 catalysts get MUCH higher weight
            tier1_keywords = {
                'acquisition': 8,      # M&A = Tier 1
                'merger': 8,           # M&A = Tier 1
                'acquires': 8,         # M&A = Tier 1
                'to acquire': 8,       # M&A = Tier 1
                'FDA approval': 8,     # FDA approval = Tier 1
                'drug approval': 8,    # FDA approval = Tier 1
                'contract win': 6,     # Major contract = Tier 1
                'awarded contract': 6, # Major contract = Tier 1
                'signs contract': 6,   # Major contract = Tier 1
                'upgrade': 5,          # Analyst upgrade = Tier 1
            }

            # Tier 2 and momentum keywords
            tier2_keywords = {
                'earnings beat': 4,
                'beat estimates': 4,
                'beat expectations': 4,
                'raises guidance': 3,
                'guidance raised': 3,
                # Product launches (PHASE 1.1)
                'launches': 4,
                'product launch': 4,
                'new product': 3,
                'unveils': 3,
                'introduces': 3,
                # Partnerships (PHASE 1.2)
                'partnership': 4,
                'strategic partnership': 5,
                'collaboration': 3,
                'joint venture': 4,
                'alliance': 3,
                'partners with': 4,
                # Original keywords
                'analyst': 1,
                'price target': 2,
                'breakout': 1,
                'new high': 2
            }

            # NEGATIVE sentiment keywords (filter these out)
            negative_keywords = [
                'investigation',
                'lawsuit',
                'legal action',
                'sec filing',
                'dilutive offering',
                'public offering',
                'share offering',
                'secondary offering',
                'reduces stake',
                'sells shares',
                'cutting',
                'downgrade',
                'misses',
                'disappoints',
                'concern',
                'warning'
            ]

            # LAW FIRM SPAM FILTERS (V5 - filter out shareholder alerts)
            law_firm_spam_keywords = [
                'shareholder alert',
                'shareholder notice',
                'law firm',
                'class action',
                'investigating',
                'investigation continues',
                'monteverde',
                'halper sadeh',
                'rosen law',
                'bragar eagel',
                'levi & korsinsky',
                'contact the firm',
                'shareholders who',
                'encourages shareholders'
            ]

            # M&A ACQUIRER FILTERS (V5 - reject if stock is buying, not being bought)
            acquirer_keywords = [
                'to acquire',
                'acquires',
                'acquiring',
                'announces acquisition of',
                'completed acquisition of',
                'agreement to acquire',
                'will acquire',
                'has acquired'
            ]

            # M&A TARGET KEYWORDS (stock being bought - THESE ARE GOOD)
            target_keywords = [
                'to be acquired',
                'acquired by',
                'acquisition offer',
                'buyout offer',
                'takeover offer',
                'merger agreement',
                'received offer',
                'unsolicited proposal',
                'acquisition proposal'
            ]

            score = 0
            found_keywords = set()
            catalyst_type_news = None
            catalyst_news_age_days = None

            # PHASE 1.3-1.5: Track magnitude data for contracts, guidance, M&A, FDA
            contract_value = None
            guidance_magnitude = None
            ma_premium = None
            fda_approval_type = None

            # Check for Tier 1 catalysts in news first (with recency and sentiment filtering)
            for article in articles[:20]:
                title = article.get('title', '').lower()
                description = article.get('description', '').lower()
                text = f"{title} {description}"

                # Get article age
                published = article.get('published_utc', '')
                try:
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    days_ago = (datetime.now(pub_date.tzinfo) - pub_date).days
                except:
                    days_ago = 999  # Unknown date = reject

                # NEGATIVE SENTIMENT FILTER
                is_negative = any(neg_word in text for neg_word in negative_keywords)
                if is_negative:
                    continue  # Skip negative news entirely

                # V5: LAW FIRM SPAM FILTER
                is_law_firm_spam = any(spam_word in text for spam_word in law_firm_spam_keywords)
                if is_law_firm_spam:
                    continue  # Skip law firm investigation alerts entirely

                # V5: M&A DIRECTION DETECTION (only keep targets, reject acquirers)
                is_acquirer = any(acq_word in text for acq_word in acquirer_keywords)
                is_target = any(tgt_word in text for tgt_word in target_keywords)

                # Check Tier 1 keywords (M&A, FDA, contracts) with SAME-DAY RECENCY
                for keyword, points in tier1_keywords.items():
                    if keyword in text:
                        # CRITICAL: Only accept M&A/FDA/contract news from SAME DAY (0-1 days old)
                        if 'acquisition' in keyword or 'merger' in keyword or 'acquire' in keyword:
                            # V5: Only accept if stock is TARGET (being bought), not acquirer (buying)
                            if is_acquirer and not is_target:
                                continue  # Skip - stock is buying, not being bought

                            if days_ago <= 1:  # Same day or yesterday only
                                score += points
                                found_keywords.add(keyword)
                                if not catalyst_type_news:
                                    catalyst_type_news = 'M&A_news'
                                    catalyst_news_age_days = days_ago
                                # PHASE 1.3: Extract M&A premium percentage
                                if ma_premium is None:
                                    ma_premium = parse_ma_premium(text)
                        elif 'FDA' in keyword or 'drug' in keyword:
                            if days_ago <= 1:  # Same day or yesterday only
                                score += points
                                found_keywords.add(keyword)
                                if not catalyst_type_news:
                                    catalyst_type_news = 'FDA_news'
                                    catalyst_news_age_days = days_ago
                                # PHASE 1.5: Classify FDA approval type
                                if fda_approval_type is None:
                                    fda_approval_type = classify_fda_approval(text)
                        elif 'contract' in keyword:
                            if days_ago <= 2:  # Give contracts 2 days (sometimes delayed reporting)
                                score += points
                                found_keywords.add(keyword)
                                if not catalyst_type_news:
                                    catalyst_type_news = 'contract_news'
                                    catalyst_news_age_days = days_ago
                                # PHASE 1.3: Extract contract value
                                if contract_value is None:
                                    contract_value = parse_contract_value(text)
                        else:  # Other Tier 1 keywords (upgrades, etc.)
                            score += points
                            found_keywords.add(keyword)

                # PHASE 1.4: Check for guidance raises/cuts in Tier 2 keywords
                for keyword, points in tier2_keywords.items():
                    if keyword in text and 'guidance' in keyword:
                        # Extract guidance magnitude
                        if guidance_magnitude is None:
                            guidance_magnitude = parse_guidance_magnitude(text)

                # Check Tier 2 keywords (no strict recency requirement)
                for keyword, points in tier2_keywords.items():
                    if keyword in text:
                        score += points
                        found_keywords.add(keyword)

            # Cap at 30 (increased from 20 to account for higher Tier 1 weights)
            score = min(score, 30)

            # Extract top 5 most relevant articles for Claude to review
            top_articles = []
            for article in articles[:5]:
                # Parse published date
                published = article.get('published_utc', '')
                try:
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    date_str = pub_date.strftime('%b %d')
                except:
                    date_str = 'Recent'

                top_articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', '')[:200],  # Limit to 200 chars
                    'published': date_str,
                    'url': article.get('article_url', '')
                })

            return {
                'score': score,
                'count': len(articles),
                'keywords': list(found_keywords),
                'scaled_score': (score / 30) * 100,  # Updated denominator to 30
                'catalyst_type_news': catalyst_type_news,  # M&A, FDA, contracts detected in news
                'catalyst_news_age_days': catalyst_news_age_days,  # How fresh is the catalyst
                'top_articles': top_articles,  # Actual article content for Claude
                # PHASE 1.3-1.5: Magnitude data for better scoring
                'contract_value': contract_value,  # Dollar amount for contracts
                'guidance_magnitude': guidance_magnitude,  # % raise/cut for guidance
                'ma_premium': ma_premium,  # % premium for M&A deals
                'fda_approval_type': fda_approval_type  # FDA approval classification
            }

        except Exception:
            return {'score': 0, 'count': 0, 'keywords': [], 'scaled_score': 0, 'top_articles': []}

    def get_volume_analysis(self, ticker):
        """
        Check for volume surge (vs 20-day average)

        Returns: Dict with volume metrics
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_str}/{end_str}?apiKey={self.api_key}'
            response = requests.get(url, timeout=15)
            data = response.json()

            if data.get('status') in ['OK', 'DELAYED'] and 'results' in data and len(data['results']) >= 20:
                results = data['results']

                # Calculate 20-day average volume (excluding yesterday)
                avg_volume = sum(r['v'] for r in results[:-1][-20:]) / 20
                yesterday_volume = results[-1]['v']

                volume_ratio = yesterday_volume / avg_volume if avg_volume > 0 else 1.0

                return {
                    'volume_ratio': round(volume_ratio, 2),
                    'avg_volume_20d': int(avg_volume),
                    'yesterday_volume': int(yesterday_volume),
                    'score': min(volume_ratio / 3 * 100, 100)  # 3x+ volume = perfect score
                }

            return {'volume_ratio': 1.0, 'avg_volume_20d': 0, 'yesterday_volume': 0, 'score': 33.3}

        except Exception:
            return {'volume_ratio': 1.0, 'avg_volume_20d': 0, 'yesterday_volume': 0, 'score': 33.3}

    def get_technical_setup(self, ticker):
        """
        Check proximity to 52-week high

        Returns: Dict with technical metrics
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=252)  # ~1 year

            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_str}/{end_str}?apiKey={self.api_key}'
            response = requests.get(url, timeout=15)
            data = response.json()

            if data.get('status') in ['OK', 'DELAYED'] and 'results' in data and len(data['results']) >= 2:
                results = data['results']

                # Find 52-week high
                high_52w = max(r['h'] for r in results)
                current_price = results[-1]['c']

                distance_pct = ((high_52w - current_price) / high_52w) * 100
                is_near_high = distance_pct <= 5.0  # Within 5%

                return {
                    'distance_from_52w_high_pct': round(distance_pct, 2),
                    'is_near_high': is_near_high,
                    'high_52w': round(high_52w, 2),
                    'current_price': round(current_price, 2),
                    'score': max(100 - (distance_pct * 2), 0)  # Closer = higher score
                }

            return {'distance_from_52w_high_pct': 100, 'is_near_high': False, 'high_52w': 0, 'current_price': 0, 'score': 0}

        except Exception:
            return {'distance_from_52w_high_pct': 100, 'is_near_high': False, 'high_52w': 0, 'current_price': 0, 'score': 0}

    def get_earnings_calendar(self):
        """
        Fetch upcoming earnings calendar from Finnhub (cached for session)

        Returns: Dict mapping ticker -> earnings data
        """
        if not self.finnhub_key:
            return {}

        # Use cache if already loaded
        if self.earnings_calendar_cache is not None:
            return self.earnings_calendar_cache

        try:
            # Get earnings calendar for next 30 days
            url = f'https://finnhub.io/api/v1/calendar/earnings'
            params = {
                'from': datetime.now().strftime('%Y-%m-%d'),
                'to': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'token': self.finnhub_key
            }

            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            # Build ticker -> earnings data mapping
            earnings_map = {}

            if 'earningsCalendar' in data:
                for event in data['earningsCalendar']:
                    ticker = event.get('symbol', '')
                    date_str = event.get('date', '')
                    eps_estimate = event.get('epsEstimate', None)

                    if ticker and date_str:
                        try:
                            earnings_date = datetime.strptime(date_str, '%Y-%m-%d')
                            days_until = (earnings_date - datetime.now()).days

                            earnings_map[ticker] = {
                                'date': date_str,
                                'days_until': days_until,
                                'eps_estimate': eps_estimate,
                                'has_upcoming_earnings': True
                            }
                        except:
                            pass

            # Cache results
            self.earnings_calendar_cache = earnings_map
            return earnings_map

        except Exception as e:
            print(f"   ⚠️ Error fetching earnings calendar: {e}")
            self.earnings_calendar_cache = {}
            return {}

    def get_analyst_ratings(self, ticker):
        """
        PHASE 2.1: Fetch analyst consensus trends using FREE tier recommendation endpoint

        NOTE: Upgrade/downgrade endpoint is PAID ONLY (403 forbidden on free tier)
        Instead, use /stock/recommendation which shows monthly consensus trends (FREE)

        Strategy:
        1. Use recommendation trends to detect improving analyst sentiment
        2. Combine with news keyword detection ("upgrade") for best coverage

        Returns: Dict with catalyst data
        """
        # Use the new free tier function
        return self.get_analyst_recommendation_trends(ticker)

    def get_earnings_surprises(self, ticker):
        """
        Check for recent earnings beats (Tier 2 catalyst)

        PRIORITY: Same-day beats (0-3 days) >>> older beats (4-30 days)

        Returns: Dict with earnings surprise data
        """
        if not self.finnhub_key:
            return {'has_beat': False, 'surprise_pct': 0, 'score': 0, 'catalyst_type': None, 'recency_tier': None}

        # Check cache first
        if ticker in self.earnings_surprises_cache:
            return self.earnings_surprises_cache[ticker]

        try:
            # Get earnings surprises from last 30 days
            url = f'https://finnhub.io/api/v1/stock/earnings'
            params = {
                'symbol': ticker,
                'token': self.finnhub_key
            }

            response = requests.get(url, params=params, timeout=30)
            earnings = response.json()

            if not isinstance(earnings, list) or not earnings:
                result = {'has_beat': False, 'surprise_pct': 0, 'score': 0, 'catalyst_type': None, 'recency_tier': None}
                self.earnings_surprises_cache[ticker] = result
                return result

            # Look at most recent earnings (last 30 days)
            recent_beat = None
            for earning in earnings:
                period = earning.get('period', '')
                actual = earning.get('actual', None)
                estimate = earning.get('estimate', None)

                if not period or actual is None or estimate is None:
                    continue

                try:
                    # Parse date
                    earning_date = datetime.strptime(period, '%Y-%m-%d')
                    days_ago = (datetime.now() - earning_date).days

                    # Only look at earnings from last 30 days
                    if days_ago > 30 or days_ago < 0:
                        continue

                    # Calculate surprise percentage
                    if estimate != 0:
                        surprise_pct = ((actual - estimate) / abs(estimate)) * 100
                    else:
                        surprise_pct = 0

                    # Significant beat = >15% surprise
                    if surprise_pct >= 15:
                        recent_beat = {
                            'period': period,
                            'days_ago': days_ago,
                            'actual': actual,
                            'estimate': estimate,
                            'surprise_pct': round(surprise_pct, 1)
                        }
                        break  # Take most recent

                except:
                    continue

            # Build result with recency tiers
            if recent_beat:
                days = recent_beat['days_ago']

                # Determine recency tier
                if days <= 3:
                    recency_tier = 'FRESH'  # 0-3 days = caught it early!
                    recency_boost = 1.5  # 50% boost for fresh beats
                elif days <= 7:
                    recency_tier = 'RECENT'  # 4-7 days = still good
                    recency_boost = 1.2  # 20% boost
                else:
                    recency_tier = 'OLDER'  # 8-30 days = older news
                    recency_boost = 1.0  # No boost

                # Apply recency boost to score
                base_score = min(recent_beat['surprise_pct'] * 2, 100)
                boosted_score = min(base_score * recency_boost, 100)

                result = {
                    'has_beat': True,
                    'surprise_pct': recent_beat['surprise_pct'],
                    'days_ago': recent_beat['days_ago'],
                    'actual': recent_beat['actual'],
                    'estimate': recent_beat['estimate'],
                    'score': boosted_score,
                    'recency_tier': recency_tier,
                    'catalyst_type': 'earnings_beat'
                }
            else:
                result = {'has_beat': False, 'surprise_pct': 0, 'score': 0, 'catalyst_type': None, 'recency_tier': None}

            self.earnings_surprises_cache[ticker] = result
            time.sleep(0.1)  # Rate limit
            return result

        except Exception as e:
            result = {'has_beat': False, 'surprise_pct': 0, 'score': 0, 'catalyst_type': None}
            self.earnings_surprises_cache[ticker] = result
            return result

    def get_revenue_surprise_fmp(self, ticker):
        """
        PHASE 2.2: Get revenue surprise using FMP free tier (250 calls/day)

        Uses 2 API calls per stock:
        1. /analyst-estimates - Get estimated revenue
        2. /income-statement - Get actual revenue

        Returns: Dict with revenue surprise data
        """
        if not self.fmp_key:
            return {'has_revenue_beat': False, 'revenue_surprise_pct': 0, 'score': 0}

        # Check cache first
        if ticker in self.revenue_surprises_cache:
            return self.revenue_surprises_cache[ticker]

        try:
            # Call 1: Get analyst revenue estimates (most recent quarter)
            estimates_url = f"https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}"
            estimates_params = {'apikey': self.fmp_key, 'limit': 1}
            estimates_response = requests.get(estimates_url, params=estimates_params, timeout=30)
            estimates_data = estimates_response.json()

            if not isinstance(estimates_data, list) or not estimates_data:
                result = {'has_revenue_beat': False, 'revenue_surprise_pct': 0, 'score': 0}
                self.revenue_surprises_cache[ticker] = result
                return result

            estimated_revenue = estimates_data[0].get('estimatedRevenueAvg', 0)
            estimate_date = estimates_data[0].get('date', '')

            if not estimated_revenue or estimated_revenue <= 0:
                result = {'has_revenue_beat': False, 'revenue_surprise_pct': 0, 'score': 0}
                self.revenue_surprises_cache[ticker] = result
                return result

            # Call 2: Get actual revenue from income statement (most recent quarter)
            actuals_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}"
            actuals_params = {'apikey': self.fmp_key, 'period': 'quarter', 'limit': 1}
            actuals_response = requests.get(actuals_url, params=actuals_params, timeout=30)
            actuals_data = actuals_response.json()

            if not isinstance(actuals_data, list) or not actuals_data:
                result = {'has_revenue_beat': False, 'revenue_surprise_pct': 0, 'score': 0}
                self.revenue_surprises_cache[ticker] = result
                return result

            actual_revenue = actuals_data[0].get('revenue', 0)
            actual_date = actuals_data[0].get('date', '')

            if not actual_revenue or actual_revenue <= 0:
                result = {'has_revenue_beat': False, 'revenue_surprise_pct': 0, 'score': 0}
                self.revenue_surprises_cache[ticker] = result
                return result

            # Calculate revenue surprise percentage
            revenue_surprise_pct = ((actual_revenue - estimated_revenue) / estimated_revenue) * 100

            # Check if beat is recent (last 30 days)
            try:
                actual_dt = datetime.strptime(actual_date, '%Y-%m-%d')
                days_ago = (datetime.now() - actual_dt).days
            except:
                days_ago = 999  # Unknown date = too old

            # Only count as catalyst if recent AND beat
            has_revenue_beat = revenue_surprise_pct > 0 and days_ago <= 30

            # Score: 0-50 points based on beat magnitude (scales with earnings beat)
            if has_revenue_beat:
                if revenue_surprise_pct >= 20:
                    score = 50
                elif revenue_surprise_pct >= 15:
                    score = 40
                elif revenue_surprise_pct >= 10:
                    score = 30
                else:
                    score = 20
            else:
                score = 0

            result = {
                'has_revenue_beat': has_revenue_beat,
                'revenue_surprise_pct': revenue_surprise_pct,
                'actual_revenue': actual_revenue,
                'estimated_revenue': estimated_revenue,
                'days_ago': days_ago,
                'score': score
            }

            self.revenue_surprises_cache[ticker] = result
            time.sleep(0.15)  # Rate limit: 250 calls/day = ~17/min safe
            return result

        except Exception as e:
            result = {'has_revenue_beat': False, 'revenue_surprise_pct': 0, 'score': 0}
            self.revenue_surprises_cache[ticker] = result
            return result

    def get_insider_transactions(self, ticker):
        """
        Check for clustered insider buying (Tier 1 catalyst)

        Returns: Dict with insider trading data
        """
        if not self.finnhub_key:
            return {'has_cluster': False, 'buy_count': 0, 'score': 0, 'catalyst_type': None}

        # Check cache first
        if ticker in self.insider_transactions_cache:
            return self.insider_transactions_cache[ticker]

        try:
            # Get insider transactions from last 90 days
            url = f'https://finnhub.io/api/v1/stock/insider-transactions'
            params = {
                'symbol': ticker,
                'from': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
                'to': datetime.now().strftime('%Y-%m-%d'),
                'token': self.finnhub_key
            }

            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            # Handle response format
            if isinstance(data, dict) and 'data' in data:
                transactions = data['data']
            elif isinstance(data, list):
                transactions = data
            else:
                transactions = []

            if not transactions:
                result = {'has_cluster': False, 'buy_count': 0, 'score': 0, 'catalyst_type': None}
                self.insider_transactions_cache[ticker] = result
                return result

            # Analyze for clustered buying (last 30 days)
            recent_buys = 0
            total_shares_bought = 0
            total_dollar_value = 0  # PHASE 1.6: Track dollar amount

            for txn in transactions:
                change = txn.get('change', 0)
                filing_date = txn.get('filingDate', '')
                share_price = txn.get('share', 0)  # Price per share at time of transaction

                if not filing_date:
                    continue

                try:
                    filing_dt = datetime.strptime(filing_date, '%Y-%m-%d')
                    days_ago = (datetime.now() - filing_dt).days

                    # Only count buys from last 30 days
                    if days_ago <= 30 and days_ago >= 0:
                        # Positive change = buy
                        if change > 0:
                            recent_buys += 1
                            total_shares_bought += change
                            # PHASE 1.6: Calculate dollar value of purchase
                            if share_price > 0:
                                total_dollar_value += change * share_price
                except:
                    continue

            # Clustered buying = 3+ insiders buying in last 30 days
            has_cluster = recent_buys >= 3

            # PHASE 1.6: Weight score by dollar amount
            # Base score: 25 points per buy (up to 100)
            # Bonus: +25% if total value >$1M, +50% if >$5M, +75% if >$10M
            base_score = min(recent_buys * 25, 100) if has_cluster else 0
            dollar_multiplier = 1.0
            if total_dollar_value > 10_000_000:
                dollar_multiplier = 1.75
            elif total_dollar_value > 5_000_000:
                dollar_multiplier = 1.50
            elif total_dollar_value > 1_000_000:
                dollar_multiplier = 1.25

            weighted_score = int(base_score * dollar_multiplier)

            result = {
                'has_cluster': has_cluster,
                'buy_count': recent_buys,
                'total_shares': total_shares_bought,
                'total_dollar_value': total_dollar_value,  # PHASE 1.6
                'score': min(weighted_score, 100),  # PHASE 1.6: Cap at 100
                'catalyst_type': 'insider_buying' if has_cluster else None
            }

            self.insider_transactions_cache[ticker] = result
            time.sleep(0.1)  # Rate limit
            return result

        except Exception as e:
            result = {'has_cluster': False, 'buy_count': 0, 'score': 0, 'catalyst_type': None}
            self.insider_transactions_cache[ticker] = result
            return result

    def get_options_flow(self, ticker):
        """
        PARKING LOT ITEM #1: Options Flow Data (FREE via Polygon)

        Detects unusual options activity (bullish call buying by institutions).
        Uses Polygon /v2/snapshot/locale/us/markets/options/tickers/{ticker} endpoint.

        Signals:
        - High call volume vs put volume (call/put ratio >2.0 = bullish)
        - Unusual volume spikes (today vs 30-day average)
        - Large institutional sweeps (>$100K premium trades)

        Returns: Dict with options flow metrics
        """
        try:
            # Query Polygon options snapshot
            url = f'https://api.polygon.io/v2/snapshot/locale/us/markets/options/tickers/{ticker}'
            params = {'apiKey': self.api_key}

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if response.status_code != 200 or 'results' not in data:
                return {
                    'has_unusual_activity': False,
                    'call_put_ratio': 0,
                    'score': 0,
                    'signal_type': None
                }

            results = data.get('results', [])
            if not results:
                return {
                    'has_unusual_activity': False,
                    'call_put_ratio': 0,
                    'score': 0,
                    'signal_type': None
                }

            # Aggregate call vs put volume
            total_call_volume = 0
            total_put_volume = 0
            unusual_call_volume = 0

            for option in results:
                details = option.get('details', {})
                day_data = option.get('day', {})

                contract_type = details.get('contract_type', '')
                volume = day_data.get('volume', 0)
                vwap = day_data.get('vwap', 0)
                open_interest = day_data.get('open_interest', 1)

                # Skip if no volume
                if volume == 0:
                    continue

                # Categorize as call or put
                if contract_type == 'call':
                    total_call_volume += volume

                    # Detect unusual activity: volume >2x open interest (likely institutional sweep)
                    if volume > open_interest * 2:
                        unusual_call_volume += volume

                elif contract_type == 'put':
                    total_put_volume += volume

            # Avoid division by zero
            if total_put_volume == 0:
                call_put_ratio = total_call_volume if total_call_volume > 0 else 0
            else:
                call_put_ratio = total_call_volume / total_put_volume

            # Bullish signal: call/put ratio >2.0 AND some unusual activity
            has_unusual_activity = call_put_ratio > 2.0 and unusual_call_volume > 0

            # Score: 0-30 points based on call/put ratio
            # 2.0 = 20 pts, 3.0 = 25 pts, 4.0+ = 30 pts
            if call_put_ratio >= 4.0:
                score = 30
                signal_type = 'heavy_call_buying'
            elif call_put_ratio >= 3.0:
                score = 25
                signal_type = 'strong_call_buying'
            elif call_put_ratio >= 2.0:
                score = 20
                signal_type = 'moderate_call_buying'
            else:
                score = 0
                signal_type = None

            return {
                'has_unusual_activity': has_unusual_activity,
                'call_put_ratio': round(call_put_ratio, 2),
                'total_call_volume': total_call_volume,
                'total_put_volume': total_put_volume,
                'unusual_call_volume': unusual_call_volume,
                'score': score,
                'signal_type': signal_type
            }

        except Exception:
            # Silently fail (options data not available for all stocks)
            return {
                'has_unusual_activity': False,
                'call_put_ratio': 0,
                'score': 0,
                'signal_type': None
            }

    def get_analyst_recommendation_trends(self, ticker):
        """
        PHASE 2.1: Check for improving analyst consensus using Finnhub FREE tier

        Uses: /stock/recommendation endpoint (FREE)
        Returns monthly aggregate: strongBuy, buy, hold, sell, strongSell counts

        Detects upgrades by comparing current month vs 2-3 months ago:
        - Increasing strongBuy count = bullish catalyst
        - Decreasing sell/strongSell = improving sentiment

        Returns: Dict with recommendation trend data
        """
        if not self.finnhub_key:
            return {'has_improving_trend': False, 'score': 0, 'catalyst_type': None}

        # Check cache first
        if ticker in self.analyst_ratings_cache:
            return self.analyst_ratings_cache[ticker]

        try:
            url = f'https://finnhub.io/api/v1/stock/recommendation'
            params = {
                'symbol': ticker,
                'token': self.finnhub_key
            }

            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            # API returns list of monthly snapshots, newest first
            # Example: [{"period": "2025-11", "strongBuy": 15, "buy": 23, ...}, ...]
            if not isinstance(data, list) or len(data) < 2:
                result = {'has_improving_trend': False, 'score': 0, 'catalyst_type': None}
                self.analyst_ratings_cache[ticker] = result
                return result

            # Compare current month (index 0) to 2-3 months ago (index 2)
            current = data[0]
            baseline = data[2] if len(data) > 2 else data[1]

            # Extract counts
            current_strong_buy = current.get('strongBuy', 0)
            current_buy = current.get('buy', 0)
            current_sell = current.get('sell', 0)
            current_strong_sell = current.get('strongSell', 0)

            baseline_strong_buy = baseline.get('strongBuy', 0)
            baseline_buy = baseline.get('buy', 0)
            baseline_sell = baseline.get('sell', 0)
            baseline_strong_sell = baseline.get('strongSell', 0)

            # Calculate bullish score (higher strongBuy/buy, lower sell/strongSell)
            current_bullish = current_strong_buy * 2 + current_buy
            current_bearish = current_sell + current_strong_sell * 2

            baseline_bullish = baseline_strong_buy * 2 + baseline_buy
            baseline_bearish = baseline_sell + baseline_strong_sell * 2

            # Detect improving trend
            bullish_improvement = current_bullish - baseline_bullish
            bearish_reduction = baseline_bearish - current_bearish

            # Significant upgrade = +3 or more strongBuy/buy OR -2 or more sell/strongSell
            has_improving_trend = (bullish_improvement >= 3) or (bearish_reduction >= 2)

            # Score based on magnitude of improvement
            if has_improving_trend:
                # 10 points per net strongBuy increase, 5 points per buy increase
                # Cap at 50 points (Tier 2 catalyst level)
                strong_buy_delta = current_strong_buy - baseline_strong_buy
                buy_delta = current_buy - baseline_buy
                sell_delta = baseline_sell - current_sell

                score = min(
                    strong_buy_delta * 10 + buy_delta * 5 + sell_delta * 5,
                    50
                )
            else:
                score = 0

            result = {
                'has_improving_trend': has_improving_trend,
                'current_strong_buy': current_strong_buy,
                'baseline_strong_buy': baseline_strong_buy,
                'strong_buy_delta': current_strong_buy - baseline_strong_buy,
                'bullish_improvement': bullish_improvement,
                'bearish_reduction': bearish_reduction,
                'score': score,
                'catalyst_type': 'analyst_upgrade_trend' if has_improving_trend else None,
                'period': current.get('period', 'Unknown')
            }

            self.analyst_ratings_cache[ticker] = result
            time.sleep(0.1)  # Rate limit
            return result

        except Exception as e:
            result = {'has_improving_trend': False, 'score': 0, 'catalyst_type': None}
            self.analyst_ratings_cache[ticker] = result
            return result

    def get_sec_8k_filings(self, ticker):
        """
        Check for recent SEC 8-K filings indicating M&A or major contracts

        8-K filings are legally required immediate disclosures for material events:
        - Item 1.01: Material Agreement (major contracts)
        - Item 2.01: Completion of Acquisition or Disposition of Assets (M&A)

        Benefit: Catch M&A/contracts 1-2 hours earlier than news sources

        Returns: Dict with 8-K filing data
        """
        try:
            # SEC EDGAR API endpoint
            # Format: https://data.sec.gov/submissions/CIK##########.json

            # First, get the CIK (Central Index Key) for the ticker
            # Use SEC ticker lookup
            headers = {
                'User-Agent': 'Paper Trading Lab tednunes@example.com'  # SEC requires identification
            }

            # Get company CIK from ticker
            cik_url = f'https://www.sec.gov/cgi-bin/browse-edgar'
            params = {
                'action': 'getcompany',
                'ticker': ticker,
                'type': '8-K',
                'dateb': '',
                'owner': 'exclude',
                'count': 10,
                'output': 'atom'
            }

            response = requests.get(cik_url, params=params, headers=headers, timeout=10)

            # Parse for recent 8-K filings
            # Look for Item 1.01 (Material Agreement) or Item 2.01 (M&A completion)
            content = response.text.lower()

            # Check if any 8-K filed in last 2 days
            has_recent_8k = False
            catalyst_type_8k = None
            filing_date = None

            # Simple regex to detect filing dates and items
            import re

            # Look for dates in format YYYY-MM-DD
            date_pattern = r'(\d{4}-\d{2}-\d{2})'
            dates = re.findall(date_pattern, content)

            if dates:
                # Check most recent filing
                most_recent = dates[0] if dates else None
                if most_recent:
                    try:
                        filing_dt = datetime.strptime(most_recent, '%Y-%m-%d')
                        days_ago = (datetime.now() - filing_dt).days

                        if days_ago <= 2:  # Filed in last 2 days
                            has_recent_8k = True
                            filing_date = most_recent

                            # Check for material agreement or M&A
                            if 'item 1.01' in content or 'material agreement' in content:
                                catalyst_type_8k = 'contract_8k'
                            elif 'item 2.01' in content or 'acquisition' in content or 'merger' in content:
                                catalyst_type_8k = 'M&A_8k'
                    except:
                        pass

            return {
                'has_recent_8k': has_recent_8k,
                'catalyst_type_8k': catalyst_type_8k,
                'filing_date': filing_date,
                'score': 100 if has_recent_8k else 0
            }

        except Exception as e:
            # SEC API failures should not break the scan
            return {
                'has_recent_8k': False,
                'catalyst_type_8k': None,
                'filing_date': None,
                'score': 0
            }

    def scan_stock(self, ticker):
        """
        Complete analysis of a single stock

        V4 FLOW: Fresh catalyst bypass
        1. Calculate RS
        2. Quick pre-check for FRESH M&A/FDA news (0-1 days old)
        3. If fresh catalyst → Bypass RS filter
        4. Otherwise → Apply RS ≥3% filter
        5. Check for other Tier 1 & Tier 2 catalysts
        6. Full technical analysis if passed

        Returns: Dict with all metrics, or None if rejected
        """
        # Get sector
        sector = self.get_stock_sector(ticker)

        # STEP 1: Calculate relative strength
        rs_result = self.calculate_relative_strength(ticker, sector)

        # STEP 1.5: Quick pre-check for FRESH M&A/FDA news (0-1 days old) OR SEC 8-K filings
        # Do lightweight news check BEFORE applying RS filter
        news_result = self.get_news_score(ticker)
        sec_8k_result = self.get_sec_8k_filings(ticker)  # Check SEC filings

        has_fresh_tier1 = (
            (news_result.get('catalyst_type_news') in ['M&A_news', 'FDA_news'] and
             news_result.get('catalyst_news_age_days') is not None and
             news_result.get('catalyst_news_age_days') <= 1) or
            sec_8k_result.get('catalyst_type_8k') in ['M&A_8k', 'contract_8k']  # 8-K filings
        )

        # BYPASS RS filter if has TODAY's/yesterday's M&A/FDA news OR recent 8-K filing
        # Otherwise apply normal RS ≥3% filter
        if not rs_result['passed_filter'] and not has_fresh_tier1:
            return None  # Reject only if no fresh catalyst AND weak RS

        # STEP 2: Check for other Tier 1 & Tier 2 catalysts (now that RS check passed or was bypassed)
        analyst_result = self.get_analyst_ratings(ticker)
        insider_result = self.get_insider_transactions(ticker)
        earnings_surprise_result = self.get_earnings_surprises(ticker)
        revenue_surprise_result = self.get_revenue_surprise_fmp(ticker)  # PHASE 2.2
        options_flow_result = self.get_options_flow(ticker)  # PARKING LOT #1: Options flow

        # NOTE: news_result and sec_8k_result already fetched in STEP 1.5 for fresh catalyst check

        # Check earnings calendar (for upcoming earnings only, not a Tier 1 catalyst)
        earnings_calendar = self.earnings_calendar_cache or {}
        earnings_result = earnings_calendar.get(ticker, {})

        # Determine if stock has ANY catalyst (Tier 1 or Tier 2)
        has_tier1_catalyst = (
            analyst_result.get('catalyst_type') == 'analyst_upgrade' or
            insider_result.get('catalyst_type') == 'insider_buying' or
            news_result.get('catalyst_type_news') in ['M&A_news', 'FDA_news', 'contract_news'] or
            sec_8k_result.get('catalyst_type_8k') in ['M&A_8k', 'contract_8k']  # SEC 8-K filings
        )

        has_tier2_catalyst = (
            earnings_surprise_result.get('catalyst_type') == 'earnings_beat'
        )

        # CATALYST FILTER LOGIC:
        # - If has Tier 1 catalyst -> Continue to full analysis
        # - If has Tier 2 catalyst -> Continue to full analysis
        # - If strong RS (>7%) -> Continue (pure momentum play)
        # - Otherwise -> REJECT (no catalyst + weak momentum)

        has_any_catalyst = has_tier1_catalyst or has_tier2_catalyst
        strong_momentum = rs_result['rs_pct'] >= 7.0

        if not has_any_catalyst and not strong_momentum:
            return None  # REJECT: No catalyst and weak momentum

        # STEP 3: Full technical analysis (only for catalyst stocks or strong momentum)
        time.sleep(0.1)  # Rate limit
        volume_result = self.get_volume_analysis(ticker)
        technical_result = self.get_technical_setup(ticker)

        # Calculate composite score with TIER-AWARE WEIGHTING (Enhancement 0.2)
        # Determine catalyst tier for intelligent weighting
        catalyst_tier = 'None'
        has_tier1_catalyst = False
        has_tier2_catalyst = False
        has_tier3_catalyst = False

        # Tier 1: M&A, FDA, Earnings Beats, Major Contracts
        if (news_result.get('catalyst_type_news') in ['M&A_news', 'FDA_news'] or
            sec_8k_result.get('catalyst_type_8k') in ['M&A_8k'] or
            earnings_surprise_result.get('catalyst_type') == 'earnings_beat'):
            catalyst_tier = 'Tier 1'
            has_tier1_catalyst = True

        # Tier 2: Analyst Upgrades, Contracts
        elif (analyst_result.get('catalyst_type') in ['analyst_upgrade', 'analyst_upgrade_trend'] or
              news_result.get('catalyst_type_news') == 'contract_news' or
              sec_8k_result.get('catalyst_type_8k') == 'contract_8k'):
            catalyst_tier = 'Tier 2'
            has_tier2_catalyst = True

        # Tier 3: Insider Buying (leading indicator, not immediate catalyst)
        elif insider_result.get('catalyst_type') == 'insider_buying':
            catalyst_tier = 'Tier 3'
            has_tier3_catalyst = True

        # Tier-aware base score weighting
        if catalyst_tier == 'Tier 1':
            # Tier 1: Catalyst is KING (40% weight)
            base_score = (
                rs_result['score'] * 0.20 +          # RS important but secondary
                news_result['scaled_score'] * 0.20 + # News sentiment
                volume_result['score'] * 0.10 +      # Volume confirmation
                technical_result['score'] * 0.10     # Technical setup
            )
            catalyst_weight_multiplier = 1.0  # Full catalyst boost

        elif catalyst_tier == 'Tier 2':
            # Tier 2: Balanced weighting
            base_score = (
                rs_result['score'] * 0.25 +
                news_result['scaled_score'] * 0.20 +
                volume_result['score'] * 0.10 +
                technical_result['score'] * 0.05
            )
            catalyst_weight_multiplier = 0.75  # 75% of catalyst boost

        elif catalyst_tier == 'Tier 3':
            # Tier 3: RS and Technical become MORE important (prove momentum exists)
            base_score = (
                rs_result['score'] * 0.40 +          # RS critical for Tier 3
                news_result['scaled_score'] * 0.10 +
                volume_result['score'] * 0.05 +
                technical_result['score'] * 0.05
            )
            catalyst_weight_multiplier = 0.40  # Only 40% of catalyst boost

        else:
            # No catalyst: Pure technical/momentum play
            base_score = (
                rs_result['score'] * 0.45 +
                news_result['scaled_score'] * 0.10 +
                volume_result['score'] * 0.05 +
                technical_result['score'] * 0.00
            )
            catalyst_weight_multiplier = 0.0

        # Catalyst scoring with tier-aware multiplier
        catalyst_score = 0

        # TIER 1 CATALYSTS (TRUE CATALYSTS)
        # M&A news = 25 points
        if news_result.get('catalyst_type_news') == 'M&A_news':
            catalyst_score += 25 * catalyst_weight_multiplier

        # FDA approval news = 25 points
        elif news_result.get('catalyst_type_news') == 'FDA_news':
            catalyst_score += 25 * catalyst_weight_multiplier

        # SEC 8-K M&A filing = 25 points
        if sec_8k_result.get('catalyst_type_8k') == 'M&A_8k':
            catalyst_score += 25 * catalyst_weight_multiplier

        # Recent earnings beat with recency bonus
        if earnings_surprise_result.get('catalyst_type') == 'earnings_beat':
            recency = earnings_surprise_result.get('recency_tier', 'OLDER')
            if recency == 'FRESH':
                catalyst_score += 20 * catalyst_weight_multiplier  # Fresh beat (0-3 days)
            elif recency == 'RECENT':
                catalyst_score += 17 * catalyst_weight_multiplier  # Recent beat (4-7 days)
            else:
                catalyst_score += 15 * catalyst_weight_multiplier  # Older beat (8-30 days)

        # PHASE 2.2: Revenue surprise bonus (enhances earnings beat)
        if revenue_surprise_result.get('has_revenue_beat'):
            # Revenue beat adds 5-10 points on top of earnings beat
            rev_surprise_pct = revenue_surprise_result.get('revenue_surprise_pct', 0)
            if rev_surprise_pct >= 20:
                catalyst_score += 10 * catalyst_weight_multiplier  # Strong revenue beat
            elif rev_surprise_pct >= 10:
                catalyst_score += 7 * catalyst_weight_multiplier
            else:
                catalyst_score += 5 * catalyst_weight_multiplier

        # TIER 2 CATALYSTS
        # Analyst upgrade trend = 20 points (PHASE 2.1: FREE tier recommendation trends)
        if analyst_result.get('catalyst_type') in ['analyst_upgrade', 'analyst_upgrade_trend']:
            catalyst_score += 20 * catalyst_weight_multiplier

        # Major contract news = 20 points
        if news_result.get('catalyst_type_news') == 'contract_news':
            catalyst_score += 20 * catalyst_weight_multiplier

        # SEC 8-K contract filing = 20 points
        elif sec_8k_result.get('catalyst_type_8k') == 'contract_8k':
            catalyst_score += 20 * catalyst_weight_multiplier

        # TIER 2.5: INSTITUTIONAL SIGNALS (PARKING LOT #1)
        # Options flow (heavy call buying) = 15 points
        # This sits between Tier 2 catalysts and Tier 3 (insider buying)
        # Call/put ratio >4.0 = strong institutional interest
        if options_flow_result.get('has_unusual_activity'):
            catalyst_score += options_flow_result.get('score', 0) * catalyst_weight_multiplier

        # TIER 3 CATALYSTS (LEADING INDICATORS)
        # Insider buying = 15 points (but heavily discounted if Tier 3 only)
        if insider_result.get('catalyst_type') == 'insider_buying':
            catalyst_score += 15 * catalyst_weight_multiplier

        # Upcoming earnings = small boost
        if earnings_result.get('has_upcoming_earnings'):
            days_until = earnings_result.get('days_until', 999)
            if 3 <= days_until <= 7:
                catalyst_score += 5 * catalyst_weight_multiplier

        # PENALTY: Insider buying ONLY (no other catalyst + weak news)
        # This prevents AEO, A, BFLY from ranking high on insider alone
        if (catalyst_tier == 'Tier 3' and
            news_result['scaled_score'] < 10 and
            rs_result['score'] < 60):
            catalyst_score -= 20  # Heavy penalty for weak insider-only picks
            # print(f"   ⚠️ {ticker}: Insider-only penalty applied (weak news + weak RS)")

        # ============================================================================
        # PHASE 2.4: MAGNITUDE-BASED SCORING ADJUSTMENTS
        # ============================================================================
        magnitude_bonus = 0

        # M&A Premium Magnitude Bonus
        if news_result.get('catalyst_type_news') == 'M&A_news':
            ma_premium = news_result.get('ma_premium')
            if ma_premium:
                if ma_premium >= 30:
                    magnitude_bonus += 10  # Huge premium (30%+)
                elif ma_premium >= 20:
                    magnitude_bonus += 7   # Strong premium (20-30%)
                elif ma_premium >= 10:
                    magnitude_bonus += 4   # Decent premium (10-20%)
                # else: < 10% = no bonus (weak deal)

        # FDA Approval Type Magnitude Bonus
        if news_result.get('catalyst_type_news') == 'FDA_news':
            fda_type = news_result.get('fda_approval_type')
            if fda_type == 'BREAKTHROUGH':
                magnitude_bonus += 12  # Breakthrough = game changer
            elif fda_type == 'PRIORITY':
                magnitude_bonus += 8   # Priority review = strong
            elif fda_type == 'EXPANDED':
                magnitude_bonus += 5   # Expanded indication = good
            elif fda_type == 'LIMITED':
                magnitude_bonus -= 5   # Limited = weak (penalty)
            # STANDARD = 0 (no bonus)

        # Contract Value Magnitude Bonus
        if news_result.get('catalyst_type_news') == 'contract_news':
            contract_value = news_result.get('contract_value')
            if contract_value:
                if contract_value >= 1_000_000_000:  # $1B+
                    magnitude_bonus += 10
                elif contract_value >= 500_000_000:  # $500M+
                    magnitude_bonus += 7
                elif contract_value >= 100_000_000:  # $100M+
                    magnitude_bonus += 4
                # else: < $100M = no bonus

        # Guidance Magnitude Bonus/Penalty
        guidance_magnitude = news_result.get('guidance_magnitude')
        if guidance_magnitude is not None:
            if guidance_magnitude >= 20:
                magnitude_bonus += 8   # Massive raise (+20%+)
            elif guidance_magnitude >= 15:
                magnitude_bonus += 6   # Strong raise (+15-20%)
            elif guidance_magnitude >= 10:
                magnitude_bonus += 4   # Good raise (+10-15%)
            elif guidance_magnitude >= 5:
                magnitude_bonus += 2   # Modest raise (+5-10%)
            elif guidance_magnitude <= -10:
                magnitude_bonus -= 10  # Major cut (penalty)
            elif guidance_magnitude < 0:
                magnitude_bonus -= 5   # Any cut (penalty)

        # Insider Transaction Dollar Magnitude (already in insider_result score, but verify)
        # The get_insider_transactions() already applies dollar weighting via multiplier
        # So no additional bonus needed here

        # Apply magnitude bonus to catalyst score
        catalyst_score += magnitude_bonus

        composite_score = base_score + catalyst_score

        # Build why_selected string with catalysts first
        why_parts = []
        catalyst_reasons = []

        # TIER 1 CATALYSTS (show first)
        if analyst_result.get('catalyst_type') == 'analyst_upgrade':
            upgrades = analyst_result.get('recent_upgrades', [])
            if upgrades:
                firm = upgrades[0].get('firm', 'Analyst')
                days = upgrades[0].get('days_ago', 0)
                catalyst_reasons.append(f"UPGRADE: {firm} ({days}d ago)")

        if insider_result.get('catalyst_type') == 'insider_buying':
            buy_count = insider_result.get('buy_count', 0)
            catalyst_reasons.append(f"INSIDER BUY: {buy_count} transactions")

        # M&A, FDA, Contract news from Polygon (with age)
        catalyst_type_news = news_result.get('catalyst_type_news')
        news_age = news_result.get('catalyst_news_age_days')
        if catalyst_type_news == 'M&A_news':
            if news_age is not None:
                if news_age == 0:
                    catalyst_reasons.append(f"M&A NEWS: TODAY - Acquisition/merger")
                else:
                    catalyst_reasons.append(f"M&A NEWS: {news_age}d ago")
            else:
                catalyst_reasons.append(f"M&A NEWS: Acquisition/merger")
        elif catalyst_type_news == 'FDA_news':
            if news_age is not None and news_age == 0:
                catalyst_reasons.append(f"FDA NEWS: TODAY - Drug approval")
            else:
                catalyst_reasons.append(f"FDA NEWS: Drug approval")
        elif catalyst_type_news == 'contract_news':
            if news_age is not None and news_age <= 1:
                catalyst_reasons.append(f"CONTRACT NEWS: {news_age}d ago")
            else:
                catalyst_reasons.append(f"CONTRACT NEWS: Major win")

        # SEC 8-K filings (HIGHEST PRIORITY - direct from SEC)
        catalyst_type_8k = sec_8k_result.get('catalyst_type_8k')
        filing_date = sec_8k_result.get('filing_date')
        if catalyst_type_8k == 'M&A_8k':
            if filing_date:
                catalyst_reasons.append(f"SEC 8-K M&A: Filed {filing_date}")
            else:
                catalyst_reasons.append(f"SEC 8-K M&A: Recent filing")
        elif catalyst_type_8k == 'contract_8k':
            if filing_date:
                catalyst_reasons.append(f"SEC 8-K CONTRACT: Filed {filing_date}")
            else:
                catalyst_reasons.append(f"SEC 8-K CONTRACT: Recent filing")

        # TIER 2 CATALYSTS
        if earnings_surprise_result.get('catalyst_type') == 'earnings_beat':
            surprise = earnings_surprise_result.get('surprise_pct', 0)
            days = earnings_surprise_result.get('days_ago', 0)
            recency = earnings_surprise_result.get('recency_tier', '')
            if recency == 'FRESH':
                catalyst_reasons.append(f"FRESH BEAT: +{surprise}% ({days}d ago)")
            else:
                catalyst_reasons.append(f"BEAT: +{surprise}% ({days}d ago)")

        # Technical/momentum signals
        if rs_result['rs_pct'] >= 5:
            why_parts.append(f"Strong RS (+{rs_result['rs_pct']}%)")
        elif rs_result['rs_pct'] >= 3:
            why_parts.append(f"RS +{rs_result['rs_pct']}%")

        if volume_result['volume_ratio'] >= 2.0:
            why_parts.append(f"{volume_result['volume_ratio']:.1f}x volume")

        if technical_result['is_near_high']:
            why_parts.append(f"Near 52w high")

        # Combine: Catalysts first, then technical signals
        all_reasons = catalyst_reasons + why_parts
        why_selected = ', '.join(all_reasons) if all_reasons else 'Meets baseline criteria'

        # Update catalyst_tier_display to match new scoring logic (Enhancement 0.2)
        catalyst_tier_display = catalyst_tier  # Use the tier from scoring logic

        # Add specific catalyst description
        if catalyst_tier == 'Tier 1':
            if catalyst_type_8k == 'M&A_8k':
                catalyst_tier_display = 'Tier 1 - SEC 8-K M&A'
            elif catalyst_type_news == 'M&A_news':
                catalyst_tier_display = 'Tier 1 - M&A News'
            elif catalyst_type_news == 'FDA_news':
                catalyst_tier_display = 'Tier 1 - FDA News'
            elif earnings_surprise_result.get('catalyst_type') == 'earnings_beat':
                recency = earnings_surprise_result.get('recency_tier', '')
                if recency == 'FRESH':
                    catalyst_tier_display = 'Tier 1 - Fresh Earnings Beat (0-3d)'
                elif recency == 'RECENT':
                    catalyst_tier_display = 'Tier 1 - Recent Earnings Beat (4-7d)'
                else:
                    catalyst_tier_display = 'Tier 1 - Earnings Beat (8-30d)'
        elif catalyst_tier == 'Tier 2':
            if analyst_result.get('catalyst_type') in ['analyst_upgrade', 'analyst_upgrade_trend']:
                # PHASE 2.1: Show strongBuy delta if available
                strong_buy_delta = analyst_result.get('strong_buy_delta', 0)
                if strong_buy_delta > 0:
                    catalyst_tier_display = f'Tier 2 - Analyst Upgrade Trend (+{strong_buy_delta} StrongBuy)'
                else:
                    catalyst_tier_display = 'Tier 2 - Analyst Upgrade Trend'
            elif catalyst_type_news == 'contract_news':
                catalyst_tier_display = 'Tier 2 - Contract News'
            elif catalyst_type_8k == 'contract_8k':
                catalyst_tier_display = 'Tier 2 - SEC 8-K Contract'
        elif catalyst_tier == 'Tier 3':
            if insider_result.get('catalyst_type') == 'insider_buying':
                buy_count = insider_result.get('buy_count', 0)
                catalyst_tier_display = f'Tier 3 - Insider Buying ({buy_count}x)'
        else:
            catalyst_tier_display = 'No Catalyst'

        return {
            'ticker': ticker,
            'composite_score': round(composite_score, 2),
            'sector': sector,
            'price': technical_result['current_price'],
            'relative_strength': rs_result,
            'catalyst_signals': news_result,
            'sec_8k_filings': sec_8k_result,  # SEC 8-K filing data
            'volume_analysis': volume_result,
            'technical_setup': technical_result,
            'analyst_ratings': analyst_result,
            'insider_transactions': insider_result,
            'earnings_surprises': earnings_surprise_result,
            'earnings_data': earnings_result,
            'options_flow': options_flow_result,  # PARKING LOT #1: Options flow data
            'catalyst_tier': catalyst_tier_display,
            'why_selected': why_selected
        }

    def run_scan(self):
        """
        Execute full market scan

        Returns: Dict with scan results
        """
        print("=" * 60)
        print("MARKET SCREENER - S&P 1500 Scan")
        print("=" * 60)
        print(f"Date: {self.today}")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')} ET")
        print(f"Filters: RS ≥{MIN_RS_PCT}%, Price ≥${MIN_PRICE}, MCap ≥${MIN_MARKET_CAP:,}\n")

        # Load Finnhub earnings calendar (TIER 1 CATALYST DATA)
        if self.finnhub_key:
            print("Loading Finnhub earnings calendar...")
            earnings_cal = self.get_earnings_calendar()
            earnings_count = len(earnings_cal)
            print(f"   ✓ Loaded {earnings_count} upcoming earnings events (next 30 days)\n")
        else:
            print("   ⚠️ Finnhub disabled - Tier 1 catalyst detection limited\n")

        # Get universe
        tickers = self.get_sp1500_tickers()
        universe_size = len(tickers)

        print(f"Scanning {universe_size} stocks...")
        print("(This will take 5-10 minutes due to API rate limits)\n")

        # Scan each stock
        candidates = []
        rs_pass_count = 0

        for i, ticker in enumerate(tickers, 1):
            if i % 50 == 0:
                print(f"   Progress: {i}/{universe_size} scanned ({rs_pass_count} passed RS filter)")

            result = self.scan_stock(ticker)

            if result:
                rs_pass_count += 1
                candidates.append(result)

        print(f"\n   Scan complete: {rs_pass_count}/{universe_size} passed RS filter\n")

        # PHASE 3.1: Calculate IBD-style RS percentile rankings
        print("=" * 60)
        print("CALCULATING RS PERCENTILES")
        print("=" * 60)
        self.calculate_rs_percentiles(candidates)

        # PHASE 3.2: Detect sector rotation
        print("\n" + "=" * 60)
        print("SECTOR ROTATION ANALYSIS")
        print("=" * 60)
        sector_rotation = self.detect_sector_rotation()

        # Sort by composite score
        candidates.sort(key=lambda x: x['composite_score'], reverse=True)

        # Take top N
        top_candidates = candidates[:TOP_N_CANDIDATES]

        # Add rank
        for rank, candidate in enumerate(top_candidates, 1):
            candidate['rank'] = rank

        # Build output
        scan_output = {
            'scan_date': self.today,
            'scan_time': datetime.now().strftime('%H:%M:%S ET'),
            'universe_size': universe_size,
            'rs_pass_count': rs_pass_count,
            'candidates_found': len(top_candidates),
            'filters_applied': {
                'min_rs_pct': MIN_RS_PCT,
                'min_price': MIN_PRICE,
                'min_market_cap': MIN_MARKET_CAP
            },
            'sector_rotation': sector_rotation,  # PHASE 3.2: Sector rotation analysis
            'candidates': top_candidates
        }

        return scan_output

    def save_results(self, scan_output):
        """
        Save scan results to JSON file

        Args:
            scan_output: Dict with scan results
        """
        output_file = PROJECT_DIR / 'screener_candidates.json'

        with open(output_file, 'w') as f:
            json.dump(scan_output, f, indent=2)

        print(f"✓ Saved {scan_output['candidates_found']} candidates to screener_candidates.json")

        # Count Tier 1 catalysts
        tier1_count = sum(1 for c in scan_output['candidates'] if c.get('catalyst_tier'))

        # Print top 10 summary
        print("\n" + "=" * 80)
        print("TOP 10 CANDIDATES (PHASE 3.1: Now showing RS percentile rank)")
        print("=" * 80)
        print(f"Total candidates: {len(scan_output['candidates'])} | Tier 1 catalysts: {tier1_count}\n")
        print(f"{'Rank':<5} {'Ticker':<7} {'Score':<7} {'RS%':<7} {'RS-Pct':<7} {'Catalyst':<25} Why")
        print("-" * 80)

        for candidate in scan_output['candidates'][:10]:
            rank = candidate['rank']
            ticker = candidate['ticker']
            score = candidate['composite_score']
            rs = candidate['relative_strength']['rs_pct']
            rs_pct = candidate['relative_strength'].get('rs_percentile', 0)  # IBD-style percentile
            catalyst = (candidate.get('catalyst_tier') or 'None')[:24]  # Truncate, handle None
            why = candidate['why_selected'][:25]  # Truncate

            print(f"{rank:<5} {ticker:<7} {score:<7.1f} {rs:>+6.1f} {rs_pct:>6} {catalyst:<25} {why}")

        print("=" * 80)

def main():
    """Main execution"""
    try:
        screener = MarketScreener()
        scan_output = screener.run_scan()
        screener.save_results(scan_output)

        print("\n✓ Market screening completed successfully")
        return 0

    except Exception as e:
        print(f"\n✗ Error during screening: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
