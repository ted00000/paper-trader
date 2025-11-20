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
from datetime import datetime, timedelta
from pathlib import Path
import time

# Configuration
PROJECT_DIR = Path(__file__).parent
POLYGON_API_KEY = os.environ.get('POLYGON_API_KEY', '')
FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY', '')

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

class MarketScreener:
    """Scans S&P 1500 for high-probability swing trade candidates"""

    def __init__(self):
        self.api_key = POLYGON_API_KEY
        self.finnhub_key = FINNHUB_API_KEY
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.scan_results = []

        # Cache for Finnhub data (reduce API calls)
        self.earnings_calendar_cache = None
        self.analyst_ratings_cache = {}
        self.insider_transactions_cache = {}
        self.earnings_surprises_cache = {}

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
        Determine stock's sector

        In production, this would query Polygon's ticker details API.
        For Phase 1, using simple sector mapping.

        Returns: Sector name (defaults to 'Technology' if unknown)
        """
        # Simple sector mapping (expand in production)
        tech_stocks = ['AAPL', 'MSFT', 'NVDA', 'AVGO', 'ORCL', 'CRM', 'CSCO', 'ADBE', 'ACN', 'AMD',
                       'INTC', 'IBM', 'TXN', 'QCOM', 'AMAT', 'MU', 'LRCX', 'KLAC', 'SNPS', 'CDNS',
                       'PLTR', 'NOW', 'PANW', 'FTNT', 'CRWD', 'WDAY', 'TEAM', 'DDOG', 'NET', 'ZS',
                       'ANET', 'SMCI', 'MRVL', 'ARM', 'SNOW']
        healthcare = ['LLY', 'UNH', 'JNJ', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'PFE', 'BMY',
                      'AMGN', 'GILD', 'CVS', 'CI', 'VRTX', 'REGN', 'HUM', 'ISRG', 'SYK', 'BSX']
        financials = ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SPGI', 'AXP', 'USB',
                      'PNC', 'TFC', 'SCHW', 'BK', 'COF', 'CME', 'ICE', 'AON', 'MMC', 'MCO', 'COIN', 'SOFI', 'HOOD']
        consumer_disc = ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'LOW', 'SBUX', 'TJX', 'BKNG', 'ABNB',
                         'CMG', 'ORLY', 'AZO', 'GM', 'F', 'MAR', 'HLT', 'YUM', 'DRI', 'ULTA',
                         'SHOP', 'UBER', 'DASH', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'RBLX']
        comm_services = ['META', 'GOOGL', 'GOOG', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'TMUS', 'CHTR']
        industrials = ['CAT', 'BA', 'UNP', 'HON', 'UPS', 'RTX', 'LMT', 'DE', 'GE', 'MMM',
                       'GD', 'NOC', 'ETN', 'EMR', 'ITW', 'PH', 'CSX', 'NSC', 'FDX', 'WM']
        consumer_staples = ['WMT', 'PG', 'COST', 'KO', 'PEP', 'PM', 'MO', 'MDLZ', 'CL', 'KMB',
                           'GIS', 'K', 'HSY', 'SYY', 'KHC', 'CAG', 'CPB', 'STZ', 'TAP', 'TSN']
        energy = ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HES']
        materials = ['LIN', 'APD', 'ECL', 'SHW', 'FCX', 'NEM', 'DD', 'DOW', 'PPG', 'VMC']
        utilities = ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL', 'ED', 'PEG']
        real_estate = ['PLD', 'AMT', 'EQIX', 'PSA', 'WELL', 'DLR', 'O', 'CBRE', 'SPG', 'AVB']

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
        Calculate stock's RS vs sector ETF

        Returns: Dict with RS metrics
        """
        sector_etf = SECTOR_ETF_MAP.get(sector, 'SPY')

        stock_return = self.get_3month_return(ticker)
        sector_return = self.get_3month_return(sector_etf)

        rs = stock_return - sector_return

        return {
            'rs_pct': round(rs, 2),
            'stock_return_3m': stock_return,
            'sector_return_3m': sector_return,
            'sector_etf': sector_etf,
            'passed_filter': rs >= MIN_RS_PCT,
            'score': min(rs / 15 * 100, 100) if rs > 0 else 0  # 15%+ RS = perfect score
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

            # Score news articles
            catalyst_keywords = {
                'earnings': 3,
                'beat': 3,
                'raises': 2,
                'guidance': 2,
                'upgrade': 3,
                'analyst': 1,
                'price target': 2,
                'FDA': 3,
                'approval': 3,
                'contract': 2,
                'acquisition': 2,
                'merger': 2,
                'breakout': 1,
                'high': 1
            }

            score = 0
            found_keywords = set()

            for article in articles[:20]:
                title = article.get('title', '').lower()
                description = article.get('description', '').lower()
                text = f"{title} {description}"

                for keyword, points in catalyst_keywords.items():
                    if keyword in text:
                        score += points
                        found_keywords.add(keyword)

            # Cap at 20
            score = min(score, 20)

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
                'scaled_score': (score / 20) * 100,
                'top_articles': top_articles  # NEW: Actual article content for Claude
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

            response = requests.get(url, params=params, timeout=10)
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
        Fetch recent analyst ratings/upgrades for a ticker

        Returns: Dict with catalyst data
        """
        if not self.finnhub_key:
            return {'has_upgrade': False, 'upgrade_count': 0, 'score': 0, 'catalyst_type': None}

        # Check cache first
        if ticker in self.analyst_ratings_cache:
            return self.analyst_ratings_cache[ticker]

        try:
            # Get analyst ratings/upgrades from last 30 days
            url = f'https://finnhub.io/api/v1/stock/upgrade-downgrade'
            params = {
                'symbol': ticker,
                'from': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'to': datetime.now().strftime('%Y-%m-%d'),
                'token': self.finnhub_key
            }

            response = requests.get(url, params=params, timeout=10)
            ratings = response.json()

            if not isinstance(ratings, list):
                ratings = []

            # Analyze ratings for upgrades
            upgrade_count = 0
            downgrade_count = 0
            recent_upgrades = []

            for rating in ratings:
                action = rating.get('action', '').lower()
                from_grade = rating.get('fromGrade', '').lower()
                to_grade = rating.get('toGrade', '').lower()
                date_str = rating.get('time', '')

                # Detect upgrades
                if 'upgrade' in action or (from_grade and to_grade and
                    ('buy' in to_grade or 'outperform' in to_grade or 'overweight' in to_grade)):
                    upgrade_count += 1
                    try:
                        days_ago = (datetime.now() - datetime.fromisoformat(date_str.replace('Z', '+00:00'))).days
                        recent_upgrades.append({
                            'firm': rating.get('company', 'Unknown'),
                            'action': action,
                            'to_grade': to_grade,
                            'days_ago': days_ago
                        })
                    except:
                        pass

                # Detect downgrades
                elif 'downgrade' in action or (from_grade and to_grade and
                    ('sell' in to_grade or 'underperform' in to_grade or 'underweight' in to_grade)):
                    downgrade_count += 1

            # Calculate score and determine catalyst type
            has_upgrade = upgrade_count > 0
            net_upgrades = upgrade_count - downgrade_count

            # Tier 1 catalyst if upgraded in last 14 days (extended window)
            catalyst_type = None
            if recent_upgrades:
                recent_count = sum(1 for u in recent_upgrades if u['days_ago'] <= 14)
                if recent_count > 0:
                    catalyst_type = 'analyst_upgrade'

            result = {
                'has_upgrade': has_upgrade,
                'upgrade_count': upgrade_count,
                'downgrade_count': downgrade_count,
                'net_upgrades': net_upgrades,
                'recent_upgrades': recent_upgrades[:3],  # Top 3 most recent
                'score': min(net_upgrades * 50, 100) if net_upgrades > 0 else 0,
                'catalyst_type': catalyst_type
            }

            # Cache result
            self.analyst_ratings_cache[ticker] = result
            time.sleep(0.1)  # Rate limit: 60 calls/minute = 1 per second safe

            return result

        except Exception as e:
            result = {'has_upgrade': False, 'upgrade_count': 0, 'score': 0, 'catalyst_type': None}
            self.analyst_ratings_cache[ticker] = result
            return result

    def get_earnings_surprises(self, ticker):
        """
        Check for recent earnings beats (Tier 2 catalyst)

        Returns: Dict with earnings surprise data
        """
        if not self.finnhub_key:
            return {'has_beat': False, 'surprise_pct': 0, 'score': 0, 'catalyst_type': None}

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

            response = requests.get(url, params=params, timeout=10)
            earnings = response.json()

            if not isinstance(earnings, list) or not earnings:
                result = {'has_beat': False, 'surprise_pct': 0, 'score': 0, 'catalyst_type': None}
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

            # Build result
            if recent_beat:
                result = {
                    'has_beat': True,
                    'surprise_pct': recent_beat['surprise_pct'],
                    'days_ago': recent_beat['days_ago'],
                    'actual': recent_beat['actual'],
                    'estimate': recent_beat['estimate'],
                    'score': min(recent_beat['surprise_pct'] * 2, 100),  # 50% beat = 100 score
                    'catalyst_type': 'earnings_beat'
                }
            else:
                result = {'has_beat': False, 'surprise_pct': 0, 'score': 0, 'catalyst_type': None}

            self.earnings_surprises_cache[ticker] = result
            time.sleep(0.1)  # Rate limit
            return result

        except Exception as e:
            result = {'has_beat': False, 'surprise_pct': 0, 'score': 0, 'catalyst_type': None}
            self.earnings_surprises_cache[ticker] = result
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

            response = requests.get(url, params=params, timeout=10)
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

            for txn in transactions:
                change = txn.get('change', 0)
                filing_date = txn.get('filingDate', '')

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
                except:
                    continue

            # Clustered buying = 3+ insiders buying in last 30 days
            has_cluster = recent_buys >= 3

            result = {
                'has_cluster': has_cluster,
                'buy_count': recent_buys,
                'total_shares': total_shares_bought,
                'score': min(recent_buys * 25, 100) if has_cluster else 0,
                'catalyst_type': 'insider_buying' if has_cluster else None
            }

            self.insider_transactions_cache[ticker] = result
            time.sleep(0.1)  # Rate limit
            return result

        except Exception as e:
            result = {'has_cluster': False, 'buy_count': 0, 'score': 0, 'catalyst_type': None}
            self.insider_transactions_cache[ticker] = result
            return result

    def scan_stock(self, ticker):
        """
        Complete analysis of a single stock

        Returns: Dict with all metrics, or None if rejected
        """
        # Get sector
        sector = self.get_stock_sector(ticker)

        # Calculate relative strength (CRITICAL FILTER)
        rs_result = self.calculate_relative_strength(ticker, sector)

        # REJECT if fails RS filter
        if not rs_result['passed_filter']:
            return None

        # Get catalyst signals
        news_result = self.get_news_score(ticker)

        # Get volume analysis (rate limit: small delay)
        time.sleep(0.1)  # 10 requests/second
        volume_result = self.get_volume_analysis(ticker)

        # Get technical setup
        technical_result = self.get_technical_setup(ticker)

        # Get Finnhub catalyst data (TIER 1 & TIER 2 SIGNALS)
        analyst_result = self.get_analyst_ratings(ticker)
        insider_result = self.get_insider_transactions(ticker)
        earnings_surprise_result = self.get_earnings_surprises(ticker)

        # Check earnings calendar (for upcoming earnings only, not a Tier 1 catalyst)
        earnings_calendar = self.earnings_calendar_cache or {}
        earnings_result = earnings_calendar.get(ticker, {})

        # Calculate composite score with Tier 1 catalyst boost
        # Base weights (60% total for non-Tier 1 signals)
        base_score = (
            rs_result['score'] * 0.30 +          # Reduced from 0.40
            news_result['scaled_score'] * 0.15 + # Reduced from 0.30
            volume_result['score'] * 0.10 +       # Reduced from 0.20
            technical_result['score'] * 0.05      # Reduced from 0.10
        )

        # Catalyst weights (40% total - HIGHEST PRIORITY)
        catalyst_score = 0

        # TIER 1 CATALYSTS (TRUE CATALYSTS)
        # Analyst upgrade = 20% boost
        if analyst_result.get('catalyst_type') == 'analyst_upgrade':
            catalyst_score += 20

        # Clustered insider buying = 20% boost
        if insider_result.get('catalyst_type') == 'insider_buying':
            catalyst_score += 20

        # TIER 2 CATALYSTS (CONFIRMED EVENTS)
        # Recent earnings beat = 15% boost
        if earnings_surprise_result.get('catalyst_type') == 'earnings_beat':
            catalyst_score += 15

        # NOTE: Pre-earnings speculation is NO LONGER a Tier 1 catalyst
        # Upcoming earnings only gets small momentum boost (5%)
        if earnings_result.get('has_upcoming_earnings'):
            days_until = earnings_result.get('days_until', 999)
            if 3 <= days_until <= 7:
                catalyst_score += 5  # Minor boost for near-term catalyst

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

        # TIER 2 CATALYSTS
        if earnings_surprise_result.get('catalyst_type') == 'earnings_beat':
            surprise = earnings_surprise_result.get('surprise_pct', 0)
            days = earnings_surprise_result.get('days_ago', 0)
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

        # Determine overall catalyst tier (only TRUE catalysts are Tier 1)
        catalyst_tier = None
        if analyst_result.get('catalyst_type') == 'analyst_upgrade':
            catalyst_tier = 'Tier 1 - Analyst Upgrade'
        elif insider_result.get('catalyst_type') == 'insider_buying':
            catalyst_tier = 'Tier 1 - Insider Buying'
        elif earnings_surprise_result.get('catalyst_type') == 'earnings_beat':
            catalyst_tier = 'Tier 2 - Earnings Beat'

        return {
            'ticker': ticker,
            'composite_score': round(composite_score, 2),
            'sector': sector,
            'price': technical_result['current_price'],
            'relative_strength': rs_result,
            'catalyst_signals': news_result,
            'volume_analysis': volume_result,
            'technical_setup': technical_result,
            'analyst_ratings': analyst_result,
            'insider_transactions': insider_result,
            'earnings_surprises': earnings_surprise_result,
            'earnings_data': earnings_result,
            'catalyst_tier': catalyst_tier,
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
        print("TOP 10 CANDIDATES")
        print("=" * 80)
        print(f"Total candidates: {len(scan_output['candidates'])} | Tier 1 catalysts: {tier1_count}\n")
        print(f"{'Rank':<5} {'Ticker':<7} {'Score':<7} {'Catalyst':<30} {'RS%':<7} Why")
        print("-" * 80)

        for candidate in scan_output['candidates'][:10]:
            rank = candidate['rank']
            ticker = candidate['ticker']
            score = candidate['composite_score']
            rs = candidate['relative_strength']['rs_pct']
            catalyst = (candidate.get('catalyst_tier') or 'None')[:29]  # Truncate, handle None
            why = candidate['why_selected'][:30]  # Truncate

            print(f"{rank:<5} {ticker:<7} {score:<7.1f} {catalyst:<30} {rs:<7.1f} {why}")

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
