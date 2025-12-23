#!/usr/bin/env python3
"""
MARKET SCREENER - S&P 1500 Universe Scanner
============================================

Scans the S&P 1500 daily to find stocks with:
- Relative Strength calculation (used as scoring factor, not filter)
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
from zoneinfo import ZoneInfo

# Configuration
ET = ZoneInfo('America/New_York')  # Eastern Time for trading operations
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
# DEEP RESEARCH ALIGNMENT: RS is a SCORING factor, not a HARD FILTER
# Hard filters: Price >$10, Liquidity >$50M, Catalyst presence
# Scoring factors: RS, technical setup, catalyst quality (0-100 point scorecard)
MIN_RS_PCT = None  # REMOVED - RS now used for scoring only, not filtering
MIN_PRICE = 10.0   # Minimum stock price (Deep Research: >$10)
MIN_MARKET_CAP = 1_000_000_000  # $1B minimum
MIN_DAILY_VOLUME_USD = 50_000_000  # $50M minimum (Deep Research: >$50M)
TOP_N_CANDIDATES = 150  # Number to output (wide screening, AI filters hard)


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
        self.today = datetime.now(ET).strftime('%Y-%m-%d')
        self.scan_results = []

        # Cache for Finnhub data (reduce API calls)
        self.earnings_calendar_cache = None
        self.analyst_ratings_cache = {}
        self.price_target_cache = {}  # PHASE 1.1: Analyst price target changes
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
            end_date = datetime.now(ET)
            start_date = end_date - timedelta(days=90)

            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_str}/{end_str}?apiKey={self.api_key}'
            response = requests.get(url, timeout=15)
            response.raise_for_status()
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
        PHASE 3.1: Calculate stock's RS vs MARKET (SPY) + IBD-style percentile rank

        Professional methodology (IBD/Minervini): Compare to market index, not sector.
        Prevents filtering out sector leaders when their sectors are strong.

        Returns: Dict with RS metrics including percentile rank (0-100)

        Note: Percentile rank is calculated after full scan in calculate_rs_percentiles()
        """
        sector_etf = SECTOR_ETF_MAP.get(sector, 'SPY')

        stock_return = self.get_3month_return(ticker)
        spy_return = self.get_3month_return('SPY')  # Compare to market, not sector
        sector_return = self.get_3month_return(sector_etf)  # Keep for informational purposes

        # Store stock return for later percentile calculation
        self.all_stock_returns[ticker] = stock_return

        # SCORING: Compare to market (SPY) for Entry Quality Scorecard
        # Deep Research: RS is a scoring factor (0-5 points), NOT a hard filter
        rs = stock_return - spy_return

        # Entry Quality Scorecard - Technical Setup - Relative Strength (0-5 points)
        # +1-3% sector outperformance: 2 points
        # +3-5%: 3 points
        # >5%: 5 points
        # Bonus: +2 if in top 3 sectors
        if rs > 5.0:
            rs_score_points = 5
        elif rs >= 3.0:
            rs_score_points = 3
        elif rs >= 1.0:
            rs_score_points = 2
        else:
            rs_score_points = 0

        return {
            'rs_pct': round(rs, 2),  # RS vs market (scoring factor)
            'stock_return_3m': stock_return,
            'sector_return_3m': sector_return,  # Informational only
            'spy_return_3m': spy_return,  # Informational - market baseline
            'sector_etf': sector_etf,
            'passed_filter': True,  # ALWAYS PASS - RS is scoring factor, not filter
            'score': min(rs / 15 * 100, 100) if rs > 0 else 0,  # Composite score (legacy)
            'rs_score_points': rs_score_points,  # Entry Quality Scorecard points (0-5)
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

    def detect_gap_up(self, ticker):
        """
        PHASE 2.5: Detect significant gap-ups with volume confirmation

        Gap-ups signal overnight institutional accumulation or news-driven buying pressure

        Catalyst Criteria:
        - Today's open >3% above yesterday's close
        - Today's volume >120% of 20-day average (confirms interest)
        - Price maintains above yesterday's close (gap not filled)

        Tier Classification: Tier 4 (technical catalyst, 1-3 day duration)

        Scoring:
        - Gap 3-5%: 8 points
        - Gap >5%: 12 points
        - Volume 150%+: +2 bonus points
        - Volume 200%+: +3 bonus points

        Returns: Dict with gap-up data and catalyst classification
        """
        try:
            end_date = datetime.now(ET)
            start_date = end_date - timedelta(days=30)  # 30 days for volume calc

            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_str}/{end_str}?apiKey={self.api_key}'
            response = requests.get(url, timeout=15)
            data = response.json()

            if data.get('status') not in ['OK', 'DELAYED'] or 'results' not in data or len(data['results']) < 21:
                return {'has_gap_up': False, 'score': 0, 'catalyst_type': None}

            results = data['results']

            # Calculate 20-day average volume
            recent_volumes = [r['v'] for r in results[-20:]]
            avg_volume_20d = sum(recent_volumes) / len(recent_volumes)

            # Check today's gap
            if len(results) < 2:
                return {'has_gap_up': False, 'score': 0, 'catalyst_type': None}

            yesterday = results[-2]
            today = results[-1]

            yesterday_close = yesterday['c']
            today_open = today['o']
            today_close = today['c']
            today_volume = today['v']

            # Calculate gap percentage
            gap_pct = ((today_open - yesterday_close) / yesterday_close) * 100

            # Check if gap-up (>3%) and maintained (close still above yesterday's close)
            if gap_pct < 3.0 or today_close < yesterday_close:
                return {'has_gap_up': False, 'score': 0, 'catalyst_type': None}

            # Check volume confirmation (>120% of average)
            volume_ratio = today_volume / avg_volume_20d
            if volume_ratio < 1.2:
                return {'has_gap_up': False, 'score': 0, 'catalyst_type': None}

            # Score based on gap magnitude
            score = 0
            catalyst_type = None

            if gap_pct >= 5.0:
                score = 12
                catalyst_type = 'gap_up_major'  # Tier 4 catalyst
            elif gap_pct >= 3.0:
                score = 8
                catalyst_type = 'gap_up'  # Tier 4 catalyst

            # Bonus for strong volume
            if volume_ratio >= 2.0:
                score += 3
            elif volume_ratio >= 1.5:
                score += 2

            result = {
                'has_gap_up': True,
                'score': score,
                'catalyst_type': catalyst_type,
                'gap_pct': round(gap_pct, 2),
                'volume_ratio': round(volume_ratio, 2),
                'yesterday_close': round(yesterday_close, 2),
                'today_open': round(today_open, 2),
                'today_close': round(today_close, 2)
            }

            return result

        except Exception as e:
            return {'has_gap_up': False, 'score': 0, 'catalyst_type': None}

    def check_sector_rotation_catalyst(self, ticker, sector):
        """
        PHASE 1.3: Check if stock is in a leading sector (sector rotation catalyst)

        Institutional Research: Sector rotation drives 20-30% of individual stock returns
        Stocks in leading sectors (>5% outperformance vs SPY) benefit from systematic buying

        Catalyst Criteria:
        - Stock's sector outperforming SPY by >5% (3-month basis)
        - Tier 3 catalyst (sector tailwind, not company-specific)

        Scoring:
        - Sector +5% to +10% vs SPY: 8 points (moderate rotation)
        - Sector >+10% vs SPY: 12 points (strong rotation)

        Returns: Dict with sector rotation catalyst data
        """
        try:
            if not sector or sector == 'Unknown':
                return {'has_rotation_catalyst': False, 'score': 0, 'catalyst_type': None}

            # Get sector ETF
            sector_etf = SECTOR_ETF_MAP.get(sector)
            if not sector_etf:
                return {'has_rotation_catalyst': False, 'score': 0, 'catalyst_type': None}

            # Calculate sector vs SPY performance
            spy_return = self.get_3month_return('SPY')
            sector_return = self.get_3month_return(sector_etf)
            vs_spy = sector_return - spy_return

            # Catalyst thresholds
            has_rotation_catalyst = False
            score = 0
            catalyst_type = None

            if vs_spy >= 10.0:
                has_rotation_catalyst = True
                score = 12
                catalyst_type = 'sector_rotation_strong'  # Tier 3 catalyst
            elif vs_spy >= 5.0:
                has_rotation_catalyst = True
                score = 8
                catalyst_type = 'sector_rotation_moderate'  # Tier 3 catalyst

            result = {
                'has_rotation_catalyst': has_rotation_catalyst,
                'score': score,
                'catalyst_type': catalyst_type,
                'sector': sector,
                'sector_etf': sector_etf,
                'sector_return_3m': round(sector_return, 2),
                'vs_spy': round(vs_spy, 2)
            }

            return result

        except Exception as e:
            return {'has_rotation_catalyst': False, 'score': 0, 'catalyst_type': None}

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
            end_date = datetime.now(ET)
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
            response.raise_for_status()
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
                # REMOVED 'upgrade': 5 - analyst upgrades are Tier 2, not Tier 1
            }

            # Tier 2 and momentum keywords
            tier2_keywords = {
                'upgrade': 5,          # MOVED from Tier 1 - analyst upgrades are Tier 2
                'analyst upgrade': 5,
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
                except Exception:
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
                            # AUDIT FIX: REQUIRE stock is TARGET (being acquired)
                            # Reject if: (1) stock is acquirer OR (2) no M&A context at all
                            if not is_target:
                                continue  # Skip - must be explicit target (being acquired)

                            # Additional validation: ticker must be in title for M&A
                            if ticker.upper() not in title.upper():
                                continue  # Skip - ticker not in headline (likely general M&A news)

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
                            # AUDIT FIX: Ticker must be in title for FDA approvals
                            if ticker.upper() not in title.upper():
                                continue  # Skip - ticker not in headline (likely general FDA news)

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
                except Exception:
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
            end_date = datetime.now(ET)
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
        Check proximity to 52-week high and calculate 50-day MA for market breadth

        Returns: Dict with technical metrics including above_50d_sma for breadth calculation
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

                # Calculate 50-day MA for market breadth (Phase 4.2 requirement)
                if len(results) >= 50:
                    ma_50 = sum(r['c'] for r in results[-50:]) / 50
                    above_50d_sma = current_price > ma_50
                else:
                    above_50d_sma = False

                return {
                    'distance_from_52w_high_pct': round(distance_pct, 2),
                    'is_near_high': is_near_high,
                    'high_52w': round(high_52w, 2),
                    'current_price': round(current_price, 2),
                    'above_50d_sma': above_50d_sma,  # Required for market breadth calculation
                    'score': max(100 - (distance_pct * 2), 0)  # Closer = higher score
                }

            return {'distance_from_52w_high_pct': 100, 'is_near_high': False, 'high_52w': 0, 'current_price': 0, 'above_50d_sma': False, 'score': 0}

        except Exception:
            return {'distance_from_52w_high_pct': 100, 'is_near_high': False, 'high_52w': 0, 'current_price': 0, 'above_50d_sma': False, 'score': 0}

    def detect_52week_high_breakout(self, ticker):
        """
        PHASE 1.2: Detect fresh 52-week high breakouts with volume confirmation

        Academic Research: 52-week high strategy delivers 72% win rate when combined
        with volume >150% average (O'Shaughnessy "What Works on Wall Street")

        Catalyst Criteria:
        - Stock hits new 52-week high within last 5 trading days
        - Volume on breakout day >=150% of 20-day average
        - Price maintains within 3% of 52-week high

        Tier Classification: Tier 4 (technical catalyst, variable duration)

        Scoring:
        - Fresh breakout (0-2 days): 10 points (Tier 4 catalyst)
        - Recent breakout (3-5 days): 7 points
        - Volume 150-200%: +2 bonus points
        - Volume >200%: +3 bonus points

        Returns: Dict with breakout data and catalyst classification
        """
        try:
            end_date = datetime.now(ET)
            start_date = end_date - timedelta(days=252)  # ~1 year

            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')

            url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_str}/{end_str}?apiKey={self.api_key}'
            response = requests.get(url, timeout=15)
            data = response.json()

            if data.get('status') not in ['OK', 'DELAYED'] or 'results' not in data or len(data['results']) < 21:
                return {'has_breakout': False, 'score': 0, 'catalyst_type': None}

            results = data['results']

            # Calculate 20-day average volume
            recent_volumes = [r['v'] for r in results[-20:]]
            avg_volume_20d = sum(recent_volumes) / len(recent_volumes)

            # Find 52-week high from PAST data (excluding last 5 days)
            historical_high = max(r['h'] for r in results[:-5]) if len(results) > 5 else 0

            # Check last 5 days for breakout
            has_breakout = False
            breakout_day_idx = None
            days_ago = None

            for i in range(max(len(results) - 5, 0), len(results)):
                day_high = results[i]['h']
                day_volume = results[i]['v']

                # Check if this day broke the 52-week high with volume confirmation
                if day_high > historical_high and day_volume >= (avg_volume_20d * 1.5):
                    has_breakout = True
                    breakout_day_idx = i
                    days_ago = len(results) - 1 - i  # Days ago from today
                    break  # Find earliest breakout in the 5-day window

            if not has_breakout:
                return {'has_breakout': False, 'score': 0, 'catalyst_type': None}

            # Get breakout details
            breakout_price = results[breakout_day_idx]['h']
            breakout_volume = results[breakout_day_idx]['v']
            volume_ratio = breakout_volume / avg_volume_20d
            current_price = results[-1]['c']

            # Check if price still within 3% of 52-week high (breakout maintained)
            current_high = max(r['h'] for r in results)
            distance_from_high = ((current_high - current_price) / current_high) * 100

            if distance_from_high > 3.0:
                # Breakout not maintained
                return {'has_breakout': False, 'score': 0, 'catalyst_type': None}

            # Score based on recency and volume
            score = 0
            catalyst_type = None

            if days_ago <= 2:
                score = 10
                catalyst_type = '52week_high_breakout_fresh'  # Tier 4 catalyst
            elif days_ago <= 5:
                score = 7
                catalyst_type = '52week_high_breakout_recent'

            # Bonus for strong volume
            if volume_ratio >= 2.0:
                score += 3
            elif volume_ratio >= 1.5:
                score += 2

            result = {
                'has_breakout': True,
                'score': score,
                'catalyst_type': catalyst_type,
                'breakout_price': round(breakout_price, 2),
                'days_ago': days_ago,
                'volume_ratio': round(volume_ratio, 2),
                'current_price': round(current_price, 2),
                'distance_from_high_pct': round(distance_from_high, 1)
            }

            return result

        except Exception as e:
            return {'has_breakout': False, 'score': 0, 'catalyst_type': None}

    def get_earnings_calendar(self):
        """
        Fetch recent + upcoming earnings from Finnhub calendar (cached for session)

        TIER 1 FOCUS: Past 5 days to catch fresh earnings beats with guidance raises

        Returns: Dict mapping ticker -> earnings data
        """
        if not self.finnhub_key:
            return {}

        # Use cache if already loaded
        if self.earnings_calendar_cache is not None:
            return self.earnings_calendar_cache

        try:
            # Get earnings from PAST 5 days + NEXT 30 days
            # This catches fresh earnings beats that are Tier 1 catalysts
            url = f'https://finnhub.io/api/v1/calendar/earnings'
            params = {
                'from': (datetime.now(ET) - timedelta(days=5)).strftime('%Y-%m-%d'),
                'to': (datetime.now(ET) + timedelta(days=30)).strftime('%Y-%m-%d'),
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
                    eps_actual = event.get('epsActual', None)
                    eps_estimate = event.get('epsEstimate', None)
                    revenue_actual = event.get('revenueActual', None)
                    revenue_estimate = event.get('revenueEstimate', None)

                    if ticker and date_str:
                        try:
                            earnings_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=ET)
                            now = datetime.now(ET)
                            days_diff = (earnings_date.date() - now.date()).days

                            # Calculate EPS beat percentage
                            eps_beat_pct = 0
                            if eps_actual is not None and eps_estimate is not None and eps_estimate != 0:
                                eps_beat_pct = ((eps_actual - eps_estimate) / abs(eps_estimate)) * 100

                            # Calculate revenue beat percentage
                            revenue_beat_pct = 0
                            if revenue_actual is not None and revenue_estimate is not None and revenue_estimate > 0:
                                revenue_beat_pct = ((revenue_actual - revenue_estimate) / revenue_estimate) * 100

                            # For reported earnings: set days_ago (0 if today, 1 if yesterday, etc.)
                            # For upcoming earnings: set days_until
                            if eps_actual is not None:  # Has reported
                                days_ago = abs(days_diff)  # 0 if today, 1 if yesterday, etc.
                                days_until = None
                            else:  # Not yet reported
                                days_ago = None
                                days_until = days_diff if days_diff >= 0 else None

                            earnings_map[ticker] = {
                                'date': date_str,
                                'days_until': days_until,
                                'days_ago': days_ago,
                                'eps_actual': eps_actual,
                                'eps_estimate': eps_estimate,
                                'eps_beat_pct': round(eps_beat_pct, 1) if eps_beat_pct != 0 else None,
                                'revenue_actual': revenue_actual,
                                'revenue_estimate': revenue_estimate,
                                'revenue_beat_pct': round(revenue_beat_pct, 1) if revenue_beat_pct != 0 else None,
                                'has_upcoming_earnings': days_diff >= 0 and eps_actual is None,
                                'has_reported': eps_actual is not None
                            }
                        except Exception:
                            pass

            # Cache results
            self.earnings_calendar_cache = earnings_map
            print(f"   📅 Loaded earnings calendar: {len(earnings_map)} stocks with earnings data")
            return earnings_map

        except Exception as e:
            print(f"   ⚠️ Error fetching earnings calendar: {e}")
            self.earnings_calendar_cache = {}
            return {}

    def detect_tier1_earnings_beat(self, ticker):
        """
        TIER 1 CATALYST: Detect earnings beats >10% from past 5 days

        TIER 1 CRITERIA:
        - EPS beat >10% vs estimate
        - Reported within last 5 days (fresh catalyst)
        - Optional: Revenue beat >5% (bonus points)

        This is the #1 most reliable Tier 1 catalyst for swing trading.

        Returns: Dict with Tier 1 earnings beat data
        """
        # Get earnings calendar (already cached)
        earnings_calendar = self.get_earnings_calendar()

        if ticker not in earnings_calendar:
            return {'has_tier1_beat': False, 'score': 0, 'catalyst_type': None}

        earnings = earnings_calendar[ticker]

        # Must have reported (not upcoming)
        if not earnings.get('has_reported', False):
            return {'has_tier1_beat': False, 'score': 0, 'catalyst_type': None}

        # Must be from past 5 days (fresh catalyst)
        days_ago = earnings.get('days_ago', None)
        if days_ago is None or days_ago > 5:
            return {'has_tier1_beat': False, 'score': 0, 'catalyst_type': None}

        # Get beat percentages
        eps_beat_pct = earnings.get('eps_beat_pct', 0) or 0
        revenue_beat_pct = earnings.get('revenue_beat_pct', 0) or 0

        # TIER 1 THRESHOLD: EPS beat >10%
        if eps_beat_pct < 10:
            return {'has_tier1_beat': False, 'score': 0, 'catalyst_type': None}

        # Calculate score (EPS beat is primary driver)
        # Base score: 60-100 points based on EPS beat magnitude
        base_score = min(50 + (eps_beat_pct * 3), 100)

        # Bonus: +20 points if revenue also beat >5%
        if revenue_beat_pct > 5:
            base_score = min(base_score + 20, 100)

        # Recency boost: fresher = better
        if days_ago == 0:
            recency_tier = 'TODAY'
            recency_boost = 1.2
        elif days_ago <= 2:
            recency_tier = 'FRESH'
            recency_boost = 1.1
        else:
            recency_tier = 'RECENT'
            recency_boost = 1.0

        final_score = min(base_score * recency_boost, 100)

        return {
            'has_tier1_beat': True,
            'eps_beat_pct': eps_beat_pct,
            'revenue_beat_pct': revenue_beat_pct if revenue_beat_pct > 0 else None,
            'days_ago': days_ago,
            'earnings_date': earnings.get('date'),
            'recency_tier': recency_tier,
            'score': round(final_score, 1),
            'catalyst_type': 'tier1_earnings_beat'
        }

    def detect_tier1_ma_deal(self, ticker, news_result, sec_8k_result):
        """
        TIER 1 CATALYST: Detect M&A deals with >15% premium

        TIER 1 CRITERIA:
        - M&A announcement (news or SEC 8-K Item 2.01)
        - Stock is TARGET (being acquired), not acquirer
        - Premium >15% (or any M&A if premium not disclosed)
        - Announced within last 2 days

        Returns: Dict with Tier 1 M&A data
        """
        # Check if M&A detected in news or SEC filings
        has_ma_news = news_result.get('catalyst_type_news') == 'M&A_news'
        has_ma_8k = sec_8k_result.get('catalyst_type_8k') == 'M&A_8k'

        if not has_ma_news and not has_ma_8k:
            return {'has_tier1_ma': False, 'score': 0, 'catalyst_type': None}

        # Check recency (must be within 2 days for Tier 1)
        news_age = news_result.get('catalyst_news_age_days', 999)
        if has_ma_news and news_age > 2:
            return {'has_tier1_ma': False, 'score': 0, 'catalyst_type': None}

        # Get M&A premium if available
        ma_premium = news_result.get('ma_premium', None)

        # AUDIT FIX: REQUIRE either premium >15% OR definitive agreement language
        # OLD: Defaulted to Tier 1 for ANY M&A (too permissive)
        # NEW: Require evidence of substantial deal

        if ma_premium is not None:
            # Premium explicitly stated - must be >15%
            if ma_premium < 15:
                return {'has_tier1_ma': False, 'score': 0, 'catalyst_type': None}
            is_tier1 = True
        else:
            # No premium disclosed - check for definitive agreement language
            # This catches deals announced without terms disclosed yet
            top_articles = news_result.get('top_articles', [])
            has_definitive_agreement = False

            for article in top_articles[:3]:  # Check top 3 articles
                text = f"{article.get('title', '')} {article.get('description', '')}".lower()
                if any(term in text for term in [
                    'definitive agreement', 'merger agreement', 'acquisition agreement',
                    'signed agreement', 'binding offer', 'to be acquired by'
                ]):
                    has_definitive_agreement = True
                    break

            if not has_definitive_agreement:
                # No premium AND no definitive agreement = likely rumor or speculation
                return {'has_tier1_ma': False, 'score': 0, 'catalyst_type': None}

            is_tier1 = True

        # Calculate score based on premium magnitude
        if ma_premium is not None:
            if ma_premium >= 40:
                base_score = 100  # Exceptional deal
            elif ma_premium >= 30:
                base_score = 90   # Strong premium
            elif ma_premium >= 20:
                base_score = 80   # Good premium
            else:
                base_score = 70   # Tier 1 minimum (15-20%)
        else:
            # No premium disclosed - use moderate score
            base_score = 75

        # Recency boost
        if news_age == 0:
            recency_tier = 'TODAY'
            recency_boost = 1.2
        elif news_age == 1:
            recency_tier = 'YESTERDAY'
            recency_boost = 1.1
        else:
            recency_tier = 'RECENT'
            recency_boost = 1.0

        final_score = min(base_score * recency_boost, 100)

        # Determine source
        if has_ma_8k:
            source = 'SEC_8K'
        else:
            source = 'NEWS'

        return {
            'has_tier1_ma': True,
            'ma_premium': ma_premium,
            'days_ago': news_age if has_ma_news else None,
            'source': source,
            'recency_tier': recency_tier,
            'score': round(final_score, 1),
            'catalyst_type': 'tier1_ma_deal'
        }

    def detect_tier1_fda_approval(self, ticker, news_result):
        """
        TIER 1 CATALYST: Detect FDA drug approvals

        TIER 1 CRITERIA:
        - FDA approval news detected
        - Announced within last 2 days
        - Approval type: BREAKTHROUGH > PRIORITY > STANDARD > EXPANDED

        Note: Without paid API, we rely on news keyword detection + classification

        Returns: Dict with Tier 1 FDA approval data
        """
        # Check if FDA news detected
        has_fda_news = news_result.get('catalyst_type_news') == 'FDA_news'

        if not has_fda_news:
            return {'has_tier1_fda': False, 'score': 0, 'catalyst_type': None}

        # Check recency (must be within 2 days for Tier 1)
        news_age = news_result.get('catalyst_news_age_days', 999)
        if news_age > 2:
            return {'has_tier1_fda': False, 'score': 0, 'catalyst_type': None}

        # Get FDA approval type
        fda_type = news_result.get('fda_approval_type', 'STANDARD')

        # Calculate score based on approval type
        type_scores = {
            'BREAKTHROUGH': 100,  # Game-changing designation
            'PRIORITY': 90,       # Fast-tracked approval
            'STANDARD': 80,       # Regular FDA approval
            'EXPANDED': 75,       # Additional indication
            'LIMITED': 60         # Restricted approval
        }

        base_score = type_scores.get(fda_type, 80)

        # Recency boost
        if news_age == 0:
            recency_tier = 'TODAY'
            recency_boost = 1.2
        elif news_age == 1:
            recency_tier = 'YESTERDAY'
            recency_boost = 1.1
        else:
            recency_tier = 'RECENT'
            recency_boost = 1.0

        final_score = min(base_score * recency_boost, 100)

        return {
            'has_tier1_fda': True,
            'fda_approval_type': fda_type,
            'days_ago': news_age,
            'recency_tier': recency_tier,
            'score': round(final_score, 1),
            'catalyst_type': 'tier1_fda_approval'
        }

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
                    days_ago = (datetime.now(ET) - earning_date).days

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

                except Exception:
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
                days_ago = (datetime.now(ET) - actual_dt).days
            except Exception:
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
                'from': (datetime.now(ET) - timedelta(days=90)).strftime('%Y-%m-%d'),
                'to': datetime.now(ET).strftime('%Y-%m-%d'),
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
                    days_ago = (datetime.now(ET) - filing_dt).days

                    # Only count buys from last 30 days
                    if days_ago <= 30 and days_ago >= 0:
                        # Positive change = buy
                        if change > 0:
                            recent_buys += 1
                            total_shares_bought += change
                            # PHASE 1.6: Calculate dollar value of purchase
                            if share_price > 0:
                                total_dollar_value += change * share_price
                except Exception:
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

    def get_dark_pool_activity(self, ticker):
        """
        PARKING LOT ITEM #3: Dark Pool Activity Tracking (FREE via Polygon)

        Detects institutional block trades by analyzing volume spikes.
        Dark pools = private exchanges where institutions execute large orders
        to avoid moving the market price.

        Detection method:
        - Compare recent volume to 30-day average volume
        - Spike >1.5x average = moderate institutional activity
        - Spike >2.0x average = heavy institutional accumulation

        Returns: Dict with dark pool activity metrics
        """
        try:
            # Get aggregated bars for last 30 days (daily bars)
            url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")}/{datetime.now().strftime("%Y-%m-%d")}'
            params = {'apiKey': self.api_key}

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if response.status_code != 200 or 'results' not in data:
                return {
                    'has_unusual_activity': False,
                    'volume_spike_ratio': 0,
                    'score': 0,
                    'signal_type': None
                }

            results = data.get('results', [])
            if len(results) < 5:
                # Not enough data
                return {
                    'has_unusual_activity': False,
                    'volume_spike_ratio': 0,
                    'score': 0,
                    'signal_type': None
                }

            # Calculate average volume (exclude most recent day)
            volumes = [bar['v'] for bar in results[:-1]]
            avg_volume = sum(volumes) / len(volumes)

            # Get most recent day's volume
            recent_volume = results[-1]['v']

            # Calculate spike ratio
            if avg_volume == 0:
                volume_spike_ratio = 0
            else:
                volume_spike_ratio = recent_volume / avg_volume

            # Detect unusual activity (volume spike >1.5x = institutional interest)
            has_unusual_activity = volume_spike_ratio >= 1.5

            # Score: 0-25 points based on volume spike
            # 1.5x = 15 pts, 2.0x = 20 pts, 2.5x+ = 25 pts
            if volume_spike_ratio >= 2.5:
                score = 25
                signal_type = 'heavy_accumulation'
            elif volume_spike_ratio >= 2.0:
                score = 20
                signal_type = 'strong_accumulation'
            elif volume_spike_ratio >= 1.5:
                score = 15
                signal_type = 'moderate_accumulation'
            else:
                score = 0
                signal_type = None

            return {
                'has_unusual_activity': has_unusual_activity,
                'volume_spike_ratio': round(volume_spike_ratio, 2),
                'recent_volume': recent_volume,
                'avg_volume': int(avg_volume),
                'score': score,
                'signal_type': signal_type
            }

        except Exception:
            # Silently fail (volume data not available for all stocks)
            return {
                'has_unusual_activity': False,
                'volume_spike_ratio': 0,
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

    def get_price_target_changes(self, ticker):
        """
        PHASE 1.1: Track analyst price target increases using Finnhub FREE tier

        Detects significant price target raises (often more impactful than rating upgrades)

        Uses: Finnhub /stock/price-target endpoint (FREE tier, 60 calls/min limit)

        Catalyst Scoring:
        - >20% target increase: Tier 2 catalyst (12 points)
        - 10-20% target increase: 8 points
        - 5-10% target increase: 5 points

        Example: Price target raised from $150 → $200 (+33%) drives strong buying pressure

        Returns: Dict with price target data and catalyst classification
        """
        # Check cache first
        if ticker in self.price_target_cache:
            return self.price_target_cache[ticker]

        try:
            if not self.finnhub_key:
                result = {'has_target_increase': False, 'score': 0, 'catalyst_type': None}
                self.price_target_cache[ticker] = result
                return result

            # Finnhub price target endpoint
            url = f'https://finnhub.io/api/v1/stock/price-target'
            params = {
                'symbol': ticker,
                'token': self.finnhub_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                result = {'has_target_increase': False, 'score': 0, 'catalyst_type': None}
                self.price_target_cache[ticker] = result
                time.sleep(0.1)  # Rate limit
                return result

            data = response.json()

            # Extract price targets
            target_high = data.get('targetHigh')
            target_low = data.get('targetLow')
            target_mean = data.get('targetMean')
            target_median = data.get('targetMedian')
            last_updated = data.get('lastUpdated')

            # Check if data exists and is recent (within 30 days)
            if not target_mean or not last_updated:
                result = {'has_target_increase': False, 'score': 0, 'catalyst_type': None}
                self.price_target_cache[ticker] = result
                time.sleep(0.1)  # Rate limit
                return result

            # Parse last updated date (Unix timestamp)
            update_date = datetime.fromtimestamp(last_updated, tz=ET)
            days_ago = (datetime.now(ET) - update_date).days

            # Only consider recent price targets (within 30 days)
            if days_ago > 30:
                result = {'has_target_increase': False, 'score': 0, 'catalyst_type': None}
                self.price_target_cache[ticker] = result
                time.sleep(0.1)  # Rate limit
                return result

            # Get current price to calculate upside
            current_price = self.get_current_price(ticker)

            if not current_price or current_price <= 0:
                result = {'has_target_increase': False, 'score': 0, 'catalyst_type': None}
                self.price_target_cache[ticker] = result
                time.sleep(0.1)  # Rate limit
                return result

            # Calculate upside percentage
            upside_pct = ((target_mean - current_price) / current_price) * 100

            # Score based on magnitude of upside
            has_target_increase = False
            score = 0
            catalyst_type = None

            if upside_pct >= 20:
                has_target_increase = True
                score = 12
                catalyst_type = 'price_target_raise_major'  # Tier 2 catalyst
            elif upside_pct >= 10:
                has_target_increase = True
                score = 8
                catalyst_type = 'price_target_raise'
            elif upside_pct >= 5:
                has_target_increase = True
                score = 5
                catalyst_type = 'price_target_raise_minor'

            result = {
                'has_target_increase': has_target_increase,
                'score': score,
                'catalyst_type': catalyst_type,
                'target_mean': target_mean,
                'target_high': target_high,
                'target_low': target_low,
                'current_price': current_price,
                'upside_pct': round(upside_pct, 1),
                'days_ago': days_ago
            }

            self.price_target_cache[ticker] = result
            time.sleep(0.1)  # Rate limit
            return result

        except Exception as e:
            result = {'has_target_increase': False, 'score': 0, 'catalyst_type': None}
            self.price_target_cache[ticker] = result
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
                        days_ago = (datetime.now(ET) - filing_dt).days

                        if days_ago <= 2:  # Filed in last 2 days
                            has_recent_8k = True
                            filing_date = most_recent

                            # Check for material agreement or M&A
                            if 'item 1.01' in content or 'material agreement' in content:
                                catalyst_type_8k = 'contract_8k'
                            elif 'item 2.01' in content or 'acquisition' in content or 'merger' in content:
                                catalyst_type_8k = 'M&A_8k'
                    except Exception:
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

        DEEP RESEARCH FLOW (Dec 15, 2025):
        1. Calculate RS (used as scoring factor 0-5 pts, NOT filter)
        2. Quick pre-check for FRESH M&A/FDA news (0-1 days old)
        3. Check for Tier 1 & Tier 2 catalysts
        4. Full technical analysis if passed
        5. Composite scoring (RS contributes to overall score)

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

        # DEEP RESEARCH ALIGNMENT: RS is scoring factor, not filter
        # No RS filtering here - all stocks proceed to catalyst evaluation

        # STEP 2: Check for Tier 1 & Tier 2 catalysts

        # TIER 1 CATALYSTS (highest priority - institutional-grade detection)
        tier1_earnings_result = self.detect_tier1_earnings_beat(ticker)  # Earnings beats >10%
        tier1_ma_result = self.detect_tier1_ma_deal(ticker, news_result, sec_8k_result)  # M&A deals >15% premium
        tier1_fda_result = self.detect_tier1_fda_approval(ticker, news_result)  # FDA approvals

        # TIER 2/3 CATALYSTS
        analyst_result = self.get_analyst_ratings(ticker)
        price_target_result = self.get_price_target_changes(ticker)  # PHASE 1.1: Price target increases
        insider_result = self.get_insider_transactions(ticker)
        earnings_surprise_result = self.get_earnings_surprises(ticker)
        revenue_surprise_result = self.get_revenue_surprise_fmp(ticker)  # PHASE 2.2
        breakout_52w_result = self.detect_52week_high_breakout(ticker)  # PHASE 1.2: 52-week high breakouts
        gap_up_result = self.detect_gap_up(ticker)  # PHASE 2.5: Gap-up detection
        sector_rotation_result = self.check_sector_rotation_catalyst(ticker, sector)  # PHASE 1.3: Sector rotation
        options_flow_result = self.get_options_flow(ticker)  # PARKING LOT #1: Options flow
        dark_pool_result = self.get_dark_pool_activity(ticker)  # PARKING LOT #3: Dark pool activity

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
            earnings_surprise_result.get('catalyst_type') == 'earnings_beat' or
            price_target_result.get('catalyst_type') in ['price_target_raise_major', 'price_target_raise']  # PHASE 1.1
        )

        has_tier3_catalyst_alt = (
            sector_rotation_result.get('catalyst_type') in ['sector_rotation_strong', 'sector_rotation_moderate']  # PHASE 1.3
        )

        has_tier4_catalyst = (
            breakout_52w_result.get('catalyst_type') in ['52week_high_breakout_fresh', '52week_high_breakout_recent'] or  # PHASE 1.2
            gap_up_result.get('catalyst_type') in ['gap_up_major', 'gap_up']  # PHASE 2.5
        )

        # DEEP RESEARCH CATALYST FILTER:
        # Hard filter: Catalyst presence required (any tier)
        # Deep Research Line 84: "rule-based filters for catalyst presence eliminate low-quality opportunities"

        has_any_catalyst = has_tier1_catalyst or has_tier2_catalyst or has_tier3_catalyst_alt or has_tier4_catalyst

        if not has_any_catalyst:
            return None  # REJECT: No catalyst detected (Deep Research hard filter)

        # STEP 3: Full technical analysis (only for catalyst stocks or strong momentum)
        time.sleep(0.1)  # Rate limit
        volume_result = self.get_volume_analysis(ticker)
        technical_result = self.get_technical_setup(ticker)

        # DEEP RESEARCH LIQUIDITY FILTER (Line 84: >$50M daily volume)
        # Hard filter prevents slippage on low-liquidity names
        avg_volume = volume_result.get('avg_volume_20d', 0)
        current_price = technical_result.get('current_price', 0)

        if avg_volume > 0 and current_price > 0:
            avg_dollar_volume = avg_volume * current_price

            if avg_dollar_volume < MIN_DAILY_VOLUME_USD:  # $50M minimum (Deep Research)
                # REJECT: Insufficient liquidity
                return None  # Skip low-liquidity stocks to avoid slippage

        # Calculate composite score with TIER-AWARE WEIGHTING (Enhancement 0.2)
        # Determine catalyst tier for intelligent weighting
        catalyst_tier = 'None'
        has_tier1_catalyst = False
        has_tier2_catalyst = False
        has_tier3_catalyst = False

        # Tier 1: INSTITUTIONAL-GRADE CATALYSTS (verified with hard data)
        if (tier1_earnings_result.get('has_tier1_beat') or  # Earnings >10% beat (Finnhub API)
            tier1_ma_result.get('has_tier1_ma') or           # M&A >15% premium (News + SEC 8-K)
            tier1_fda_result.get('has_tier1_fda') or         # FDA approval (News + Classification)
            earnings_surprise_result.get('catalyst_type') == 'earnings_beat'):  # Legacy earnings detection
            catalyst_tier = 'Tier 1'
            has_tier1_catalyst = True

        # Tier 2: Analyst Upgrades, Price Target Raises, Contracts
        elif (analyst_result.get('catalyst_type') in ['analyst_upgrade', 'analyst_upgrade_trend'] or
              price_target_result.get('catalyst_type') in ['price_target_raise_major', 'price_target_raise'] or  # PHASE 1.1
              news_result.get('catalyst_type_news') == 'contract_news' or
              sec_8k_result.get('catalyst_type_8k') == 'contract_8k'):
            catalyst_tier = 'Tier 2'
            has_tier2_catalyst = True

        # Tier 3: Insider Buying, Sector Rotation (leading indicators, not immediate catalysts)
        elif (insider_result.get('catalyst_type') == 'insider_buying' or
              sector_rotation_result.get('catalyst_type') in ['sector_rotation_strong', 'sector_rotation_moderate']):  # PHASE 1.3
            catalyst_tier = 'Tier 3'
            has_tier3_catalyst = True

        # Tier 4: Technical Catalysts (52-week high breakouts, gap-ups, etc.)  # PHASE 1.2, PHASE 2.5
        elif (breakout_52w_result.get('catalyst_type') in ['52week_high_breakout_fresh', '52week_high_breakout_recent'] or
              gap_up_result.get('catalyst_type') in ['gap_up_major', 'gap_up']):
            catalyst_tier = 'Tier 4'
            has_tier4_catalyst = True

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

        elif catalyst_tier == 'Tier 4':
            # PHASE 1.2: Tier 4 (Technical catalysts) - Heavy weight on momentum confirmation
            base_score = (
                rs_result['score'] * 0.35 +          # Strong RS confirms breakout
                news_result['scaled_score'] * 0.05 +
                volume_result['score'] * 0.15 +      # Volume critical for breakouts
                technical_result['score'] * 0.05
            )
            catalyst_weight_multiplier = 0.60  # 60% catalyst boost for technical catalysts

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

        # PHASE 1.1: Price target raises = 12-20 points based on magnitude
        if price_target_result.get('has_target_increase'):
            pt_score = price_target_result.get('score', 0)
            catalyst_score += pt_score * catalyst_weight_multiplier

        # Major contract news = 20 points
        if news_result.get('catalyst_type_news') == 'contract_news':
            catalyst_score += 20 * catalyst_weight_multiplier

        # SEC 8-K contract filing = 20 points
        elif sec_8k_result.get('catalyst_type_8k') == 'contract_8k':
            catalyst_score += 20 * catalyst_weight_multiplier

        # TIER 2.5: INSTITUTIONAL SIGNALS (PARKING LOT #1 & #3)
        # Options flow (heavy call buying) = 15-30 points
        # Dark pool activity (volume spikes) = 15-25 points
        # This sits between Tier 2 catalysts and Tier 3 (insider buying)
        # Call/put ratio >4.0 = strong institutional interest
        # Volume spike >2.0x = heavy accumulation
        if options_flow_result.get('has_unusual_activity'):
            catalyst_score += options_flow_result.get('score', 0) * catalyst_weight_multiplier
        if dark_pool_result.get('has_unusual_activity'):
            catalyst_score += dark_pool_result.get('score', 0) * catalyst_weight_multiplier

        # TIER 3 CATALYSTS (LEADING INDICATORS)
        # Insider buying = 15 points (but heavily discounted if Tier 3 only)
        if insider_result.get('catalyst_type') == 'insider_buying':
            catalyst_score += 15 * catalyst_weight_multiplier

        # PHASE 1.3: Sector rotation = 8-12 points (sector tailwind)
        if sector_rotation_result.get('has_rotation_catalyst'):
            rotation_score = sector_rotation_result.get('score', 0)
            catalyst_score += rotation_score * catalyst_weight_multiplier

        # Upcoming earnings = small boost
        if earnings_result.get('has_upcoming_earnings'):
            days_until = earnings_result.get('days_until', 999)
            if 3 <= days_until <= 7:
                catalyst_score += 5 * catalyst_weight_multiplier

        # ENHANCED TIER 3 PENALTIES (Prevent insider-only stocks from crowding out Tier 1)
        # Academic research: insider buying predicts 6-12 month returns, not 3-7 day swings
        if catalyst_tier == 'Tier 3':
            # Penalty 1: Weak news + weak RS (EXISTING)
            if news_result['scaled_score'] < 10 and rs_result['score'] < 60:
                catalyst_score -= 20

            # Penalty 2: No Tier 1/Tier 2 support (NEW - pure insider buying)
            if not has_tier1_catalyst and not has_tier2_catalyst:
                catalyst_score -= 15  # Pure insider buying = heavily penalized

            # Penalty 3: Multiple insiders but weak technicals (NEW - red flag)
            if (insider_result.get('buy_count', 0) >= 3 and
                technical_result['score'] < 50):
                catalyst_score -= 10  # Lots of insiders but bad setup = suspicious

        # TIER 4 CATALYSTS (TECHNICAL CATALYSTS)  # PHASE 1.2, PHASE 2.5
        # 52-week high breakout with volume = 10-13 points (72% win rate in research)
        if breakout_52w_result.get('has_breakout'):
            breakout_score = breakout_52w_result.get('score', 0)
            catalyst_score += breakout_score * catalyst_weight_multiplier

        # Gap-up with volume = 8-15 points (overnight institutional interest)
        if gap_up_result.get('has_gap_up'):
            gap_score = gap_up_result.get('score', 0)
            catalyst_score += gap_score * catalyst_weight_multiplier

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

        # TIER 1 CATALYSTS (INSTITUTIONAL-GRADE DETECTION)

        # Tier 1 Earnings Beats >10%
        if tier1_earnings_result.get('has_tier1_beat'):
            eps_beat = tier1_earnings_result.get('eps_beat_pct', 0)
            revenue_beat = tier1_earnings_result.get('revenue_beat_pct')
            days_ago = tier1_earnings_result.get('days_ago', 0)
            recency = tier1_earnings_result.get('recency_tier', '')

            if revenue_beat and revenue_beat > 5:
                catalyst_reasons.append(f"TIER 1 EARNINGS: EPS +{eps_beat:.0f}%, Rev +{revenue_beat:.0f}% ({recency}, {days_ago}d ago)")
            else:
                catalyst_reasons.append(f"TIER 1 EARNINGS: +{eps_beat:.0f}% EPS beat ({recency}, {days_ago}d ago)")

        # Tier 1 M&A Deals >15% premium
        if tier1_ma_result.get('has_tier1_ma'):
            ma_premium = tier1_ma_result.get('ma_premium')
            source = tier1_ma_result.get('source', 'NEWS')
            days_ago = tier1_ma_result.get('days_ago', 0)

            if ma_premium:
                catalyst_reasons.append(f"TIER 1 M&A: +{ma_premium:.0f}% premium ({source}, {days_ago}d ago)")
            else:
                catalyst_reasons.append(f"TIER 1 M&A: Acquisition announced ({source}, {days_ago}d ago)")

        # Tier 1 FDA Approvals
        if tier1_fda_result.get('has_tier1_fda'):
            fda_type = tier1_fda_result.get('fda_approval_type', 'STANDARD')
            days_ago = tier1_fda_result.get('days_ago', 0)
            catalyst_reasons.append(f"TIER 1 FDA: {fda_type} approval ({days_ago}d ago)")

        # SEC 8-K filings (direct from SEC)
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

        # AUDIT FIX: Add minimum composite score requirement for Tier 1
        # Prevents low-quality signals from being marked Tier 1
        if catalyst_tier == 'Tier 1' and composite_score < 60:
            catalyst_tier = 'Tier 2'
            catalyst_tier_display = 'Tier 2 - Unconfirmed Catalyst (low score)'

        # Add specific catalyst description
        if catalyst_tier == 'Tier 1':
            # PRIORITY 1: Tier 1 earnings beats >10%
            if tier1_earnings_result.get('has_tier1_beat'):
                eps_beat = tier1_earnings_result.get('eps_beat_pct', 0)
                revenue_beat = tier1_earnings_result.get('revenue_beat_pct')
                recency = tier1_earnings_result.get('recency_tier', '')

                if revenue_beat and revenue_beat > 5:
                    catalyst_tier_display = f'Tier 1 - Earnings Beat (EPS +{eps_beat:.0f}%, Rev +{revenue_beat:.0f}%) - {recency}'
                else:
                    catalyst_tier_display = f'Tier 1 - Earnings Beat (+{eps_beat:.0f}%) - {recency}'

            # PRIORITY 2: Tier 1 M&A deals >15% premium
            elif tier1_ma_result.get('has_tier1_ma'):
                ma_premium = tier1_ma_result.get('ma_premium')
                source = tier1_ma_result.get('source', 'NEWS')
                recency = tier1_ma_result.get('recency_tier', '')

                if ma_premium:
                    catalyst_tier_display = f'Tier 1 - M&A Deal (+{ma_premium:.0f}% premium) - {source} - {recency}'
                else:
                    catalyst_tier_display = f'Tier 1 - M&A Deal - {source} - {recency}'

            # PRIORITY 3: Tier 1 FDA approvals
            elif tier1_fda_result.get('has_tier1_fda'):
                fda_type = tier1_fda_result.get('fda_approval_type', 'STANDARD')
                recency = tier1_fda_result.get('recency_tier', '')
                catalyst_tier_display = f'Tier 1 - FDA Approval ({fda_type}) - {recency}'

            # LEGACY: Old detection methods (fallback)
            elif catalyst_type_8k == 'M&A_8k':
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
            if price_target_result.get('catalyst_type') in ['price_target_raise_major', 'price_target_raise']:
                # PHASE 1.1: Show price target upside percentage
                upside_pct = price_target_result.get('upside_pct', 0)
                catalyst_tier_display = f'Tier 2 - Price Target Raise (+{upside_pct}% upside)'
            elif analyst_result.get('catalyst_type') in ['analyst_upgrade', 'analyst_upgrade_trend']:
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
            # PHASE 1.3: Prioritize sector rotation over insider buying in display
            if sector_rotation_result.get('has_rotation_catalyst'):
                vs_spy = sector_rotation_result.get('vs_spy', 0)
                sector_name = sector_rotation_result.get('sector', 'Unknown')
                catalyst_tier_display = f'Tier 3 - Sector Rotation ({sector_name} +{vs_spy:.1f}% vs SPY)'
            elif insider_result.get('catalyst_type') == 'insider_buying':
                buy_count = insider_result.get('buy_count', 0)
                catalyst_tier_display = f'Tier 3 - Insider Buying ({buy_count}x)'
        elif catalyst_tier == 'Tier 4':
            # PHASE 1.2, PHASE 2.5: Technical catalysts
            if gap_up_result.get('catalyst_type') in ['gap_up_major', 'gap_up']:
                gap_pct = gap_up_result.get('gap_pct', 0)
                volume_ratio = gap_up_result.get('volume_ratio', 0)
                catalyst_tier_display = f'Tier 4 - Gap Up (+{gap_pct:.1f}%, {volume_ratio:.1f}x vol)'
            elif breakout_52w_result.get('catalyst_type') in ['52week_high_breakout_fresh', '52week_high_breakout_recent']:
                days_ago = breakout_52w_result.get('days_ago', 0)
                volume_ratio = breakout_52w_result.get('volume_ratio', 0)
                catalyst_tier_display = f'Tier 4 - 52W High Breakout ({days_ago}d ago, {volume_ratio:.1f}x vol)'
        else:
            catalyst_tier_display = 'No Catalyst'

        return {
            'ticker': ticker,
            'composite_score': round(composite_score, 2),
            'sector': sector,
            'price': technical_result['current_price'],
            'relative_strength': rs_result,
            'tier1_earnings': tier1_earnings_result,  # Tier 1 earnings beats >10%
            'tier1_ma': tier1_ma_result,              # Tier 1 M&A deals >15% premium
            'tier1_fda': tier1_fda_result,            # Tier 1 FDA approvals
            'catalyst_signals': news_result,
            'sec_8k_filings': sec_8k_result,  # SEC 8-K filing data
            'volume_analysis': volume_result,
            'technical_setup': technical_result,
            'analyst_ratings': analyst_result,
            'price_targets': price_target_result,  # PHASE 1.1: Analyst price target increases
            'insider_transactions': insider_result,
            'earnings_surprises': earnings_surprise_result,
            'earnings_data': earnings_result,
            'breakout_52w': breakout_52w_result,  # PHASE 1.2: 52-week high breakouts
            'gap_up': gap_up_result,  # PHASE 2.5: Gap-up detection
            'sector_rotation': sector_rotation_result,  # PHASE 1.3: Sector rotation catalyst
            'options_flow': options_flow_result,  # PARKING LOT #1: Options flow data
            'dark_pool': dark_pool_result,  # PARKING LOT #3: Dark pool activity
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
        print(f"Time: {datetime.now(ET).strftime('%H:%M:%S')} ET")
        print(f"Filters: Price ≥${MIN_PRICE}, MCap ≥${MIN_MARKET_CAP:,}")
        print(f"         (RS used for scoring, not filtering)\n")

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

        # v7.1.1: Save universe for version tracking (breadth stability)
        universe_file = Path(__file__).parent / 'universe_tickers.json'
        with open(universe_file, 'w') as f:
            json.dump({'tickers': sorted(tickers), 'fetched_at': self.today, 'count': len(tickers)}, f, indent=2)

        print(f"Scanning {universe_size} stocks...")
        print("(This will take 5-10 minutes due to API rate limits)\n")

        # Scan each stock
        candidates = []
        candidates_count = 0

        for i, ticker in enumerate(tickers, 1):
            if i % 50 == 0:
                print(f"   Progress: {i}/{universe_size} scanned ({candidates_count} candidates identified)")

            result = self.scan_stock(ticker)

            if result:
                candidates_count += 1
                candidates.append(result)

        print(f"\n   Scan complete: {candidates_count}/{universe_size} candidates identified\n")

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

        # TIER-BASED QUOTA SELECTION (Professional Best Practice)
        # Separate by tier to prevent Tier 3 from crowding out Tier 1
        tier1 = [c for c in candidates if c.get('catalyst_tier', '').startswith('Tier 1')]
        tier2 = [c for c in candidates if c.get('catalyst_tier', '').startswith('Tier 2')]
        tier3 = [c for c in candidates if c.get('catalyst_tier', '').startswith('Tier 3')]
        no_catalyst = [c for c in candidates if c.get('catalyst_tier', '') == 'No Catalyst']

        # Sort each tier by composite score (rank WITHIN tier, not across)
        tier1.sort(key=lambda x: x['composite_score'], reverse=True)
        tier2.sort(key=lambda x: x['composite_score'], reverse=True)
        tier3.sort(key=lambda x: x['composite_score'], reverse=True)
        no_catalyst.sort(key=lambda x: x['composite_score'], reverse=True)

        # Enforce quotas: Guarantee Tier 1 representation (IBD/Minervini approach)
        # Top 60 Tier 1, Top 50 Tier 2, Top 40 Tier 3 (prevents insider-only crowding)
        top_candidates = tier1[:60] + tier2[:50] + tier3[:40]

        # If we don't have enough candidates, backfill with remaining highest-scored
        if len(top_candidates) < TOP_N_CANDIDATES:
            remaining = [c for c in candidates if c not in top_candidates]
            remaining.sort(key=lambda x: x['composite_score'], reverse=True)
            top_candidates.extend(remaining[:TOP_N_CANDIDATES - len(top_candidates)])

        # Trim to exactly TOP_N_CANDIDATES if we have too many
        top_candidates = top_candidates[:TOP_N_CANDIDATES]

        # Add rank
        for rank, candidate in enumerate(top_candidates, 1):
            candidate['rank'] = rank

        # v7.0: Calculate market breadth at screener time (prevent lookahead bias)
        # Breadth = % of screened stocks above 50-day MA
        # This is calculated at 7:00 AM and used by GO command at 9:00 AM
        # Ensures we don't use end-of-day breadth data for intraday decisions
        total_stocks = len(top_candidates)
        above_50d_count = sum(1 for c in top_candidates if c.get('technical_setup', {}).get('above_50d_sma', False))
        breadth_pct = (above_50d_count / total_stocks * 100) if total_stocks > 0 else 0
        breadth_timestamp = datetime.now(ET).strftime('%Y-%m-%d %H:%M:%S ET')

        # Build output
        scan_output = {
            'scan_date': self.today,
            'scan_time': datetime.now(ET).strftime('%H:%M:%S ET'),
            'breadth_pct': round(breadth_pct, 1),  # v7.0: Pre-calculate breadth at screener time
            'breadth_timestamp': breadth_timestamp,  # v7.0: Timestamp when breadth was calculated
            'breadth_above_50d': above_50d_count,  # v7.0: Count for transparency
            'breadth_total': total_stocks,  # v7.0: Total for transparency
            'universe_size': universe_size,
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

        try:
            with open(output_file, 'w') as f:
                json.dump(scan_output, f, indent=2)

            # Verify file was actually written
            if output_file.exists():
                file_size = output_file.stat().st_size
                print(f"✓ Saved {scan_output['candidates_found']} candidates to screener_candidates.json ({file_size:,} bytes)")
            else:
                print(f"✗ ERROR: File not found after write: {output_file}")
        except Exception as e:
            print(f"✗ ERROR saving candidates file: {e}")
            import traceback
            traceback.print_exc()

        # Count Tier 1 catalysts (FIXED: was counting ALL tiers, now only Tier 1)
        tier1_count = sum(1 for c in scan_output['candidates']
                         if c.get('catalyst_tier', '').startswith('Tier 1'))

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
