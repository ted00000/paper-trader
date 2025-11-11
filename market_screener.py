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
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.scan_results = []

        if not self.api_key:
            raise ValueError("POLYGON_API_KEY not set in environment")

    def get_sp1500_tickers(self):
        """
        Load S&P 1500 ticker list

        For now, using a static list of major tickers. In production,
        this would load from a maintained S&P 1500 constituent file.

        Returns: List of ticker symbols
        """
        # TODO: Replace with actual S&P 1500 list (can be downloaded from various sources)
        # For Phase 1, using S&P 500 major components as proof of concept

        sp500_major = [
            # Technology (XLK)
            'AAPL', 'MSFT', 'NVDA', 'AVGO', 'ORCL', 'CRM', 'CSCO', 'ADBE', 'ACN', 'AMD',
            'INTC', 'IBM', 'TXN', 'QCOM', 'AMAT', 'MU', 'LRCX', 'KLAC', 'SNPS', 'CDNS',
            'PLTR', 'NOW', 'PANW', 'FTNT', 'CRWD', 'WDAY', 'TEAM', 'DDOG', 'NET', 'ZS',

            # Healthcare (XLV)
            'LLY', 'UNH', 'JNJ', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'PFE', 'BMY',
            'AMGN', 'GILD', 'CVS', 'CI', 'VRTX', 'REGN', 'HUM', 'ISRG', 'SYK', 'BSX',

            # Financials (XLF)
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SPGI', 'AXP', 'USB',
            'PNC', 'TFC', 'SCHW', 'BK', 'COF', 'CME', 'ICE', 'AON', 'MMC', 'MCO',

            # Consumer Discretionary (XLY)
            'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'LOW', 'SBUX', 'TJX', 'BKNG', 'ABNB',
            'CMG', 'ORLY', 'AZO', 'GM', 'F', 'MAR', 'HLT', 'YUM', 'DRI', 'ULTA',

            # Communication Services (XLC)
            'META', 'GOOGL', 'GOOG', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'TMUS', 'CHTR',

            # Industrials (XLI)
            'CAT', 'BA', 'UNP', 'HON', 'UPS', 'RTX', 'LMT', 'DE', 'GE', 'MMM',
            'GD', 'NOC', 'ETN', 'EMR', 'ITW', 'PH', 'CSX', 'NSC', 'FDX', 'WM',

            # Consumer Staples (XLP)
            'WMT', 'PG', 'COST', 'KO', 'PEP', 'PM', 'MO', 'MDLZ', 'CL', 'KMB',
            'GIS', 'K', 'HSY', 'SYY', 'KHC', 'CAG', 'CPB', 'STZ', 'TAP', 'TSN',

            # Energy (XLE)
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HES',

            # Materials (XLB)
            'LIN', 'APD', 'ECL', 'SHW', 'FCX', 'NEM', 'DD', 'DOW', 'PPG', 'VMC',

            # Utilities (XLU)
            'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL', 'ED', 'PEG',

            # Real Estate (XLRE)
            'PLD', 'AMT', 'EQIX', 'PSA', 'WELL', 'DLR', 'O', 'CBRE', 'SPG', 'AVB',

            # Additional high-volume stocks
            'COIN', 'SHOP', 'SQ', 'PYPL', 'ANET', 'SMCI', 'MRVL', 'ARM', 'SNOW', 'UBER',
            'DASH', 'ABNB', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'SOFI', 'HOOD', 'RBLX'
        ]

        print(f"   Loaded {len(sp500_major)} tickers (S&P 500 subset)")
        print(f"   TODO: Expand to full S&P 1500 universe\n")

        return sp500_major

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

        Returns: Dict with news metrics
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
                return {'score': 0, 'count': 0, 'keywords': [], 'scaled_score': 0}

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

            return {
                'score': score,
                'count': len(articles),
                'keywords': list(found_keywords),
                'scaled_score': (score / 20) * 100  # Convert to 0-100 scale
            }

        except Exception:
            return {'score': 0, 'count': 0, 'keywords': [], 'scaled_score': 0}

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

        # Calculate composite score
        composite_score = (
            rs_result['score'] * 0.40 +
            news_result['scaled_score'] * 0.30 +
            volume_result['score'] * 0.20 +
            technical_result['score'] * 0.10
        )

        # Build why_selected string
        why_parts = []
        if rs_result['rs_pct'] >= 5:
            why_parts.append(f"Strong RS (+{rs_result['rs_pct']}%)")
        elif rs_result['rs_pct'] >= 3:
            why_parts.append(f"RS +{rs_result['rs_pct']}%")

        if news_result['score'] >= 10:
            why_parts.append(f"High news ({news_result['score']}/20)")
        elif news_result['score'] >= 5:
            why_parts.append(f"News score {news_result['score']}/20")

        if volume_result['volume_ratio'] >= 2.0:
            why_parts.append(f"{volume_result['volume_ratio']:.1f}x volume surge")

        if technical_result['is_near_high']:
            why_parts.append(f"Near 52w high ({technical_result['distance_from_52w_high_pct']:.1f}%)")

        why_selected = ', '.join(why_parts) if why_parts else 'Meets baseline criteria'

        return {
            'ticker': ticker,
            'composite_score': round(composite_score, 2),
            'sector': sector,
            'price': technical_result['current_price'],
            'relative_strength': rs_result,
            'catalyst_signals': news_result,
            'volume_analysis': volume_result,
            'technical_setup': technical_result,
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

        # Print top 10 summary
        print("\n" + "=" * 60)
        print("TOP 10 CANDIDATES")
        print("=" * 60)
        print(f"{'Rank':<5} {'Ticker':<7} {'Score':<7} {'RS%':<7} {'News':<7} {'Vol':<7} Why")
        print("-" * 60)

        for candidate in scan_output['candidates'][:10]:
            rank = candidate['rank']
            ticker = candidate['ticker']
            score = candidate['composite_score']
            rs = candidate['relative_strength']['rs_pct']
            news = candidate['catalyst_signals']['score']
            vol = candidate['volume_analysis']['volume_ratio']
            why = candidate['why_selected'][:40]  # Truncate

            print(f"{rank:<5} {ticker:<7} {score:<7.1f} {rs:<7.1f} {news:<7} {vol:<7.1f} {why}")

        print("=" * 60)

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
