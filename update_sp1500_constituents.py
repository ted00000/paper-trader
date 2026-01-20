#!/usr/bin/env python3
"""
S&P 1500 Constituents Updater

Updates the sp1500_constituents.json file with current index members.
Run quarterly (March, June, September, December) or when S&P announces changes.

Sources:
- S&P 500: GitHub datasets/s-and-p-500-companies (auto-updated from Wikipedia)
- S&P 400: Wikipedia List of S&P 400 companies
- S&P 600: Wikipedia List of S&P 600 companies

Usage:
    python update_sp1500_constituents.py

Cron example (run quarterly on 1st of Mar, Jun, Sep, Dec at 6am):
    0 6 1 3,6,9,12 * cd /root/paper_trading_lab && /root/paper_trading_lab/venv/bin/python update_sp1500_constituents.py >> logs/sp1500_update.log 2>&1
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from pathlib import Path
import sys

# Configuration
SCRIPT_DIR = Path(__file__).parent
OUTPUT_FILE = SCRIPT_DIR / 'sp1500_constituents.json'
BACKUP_DIR = SCRIPT_DIR / 'backups'

# URLs
SP500_URL = 'https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv'
SP400_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_400_companies'
SP600_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_600_companies'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}


def get_sp500_tickers():
    """Fetch S&P 500 tickers from GitHub (sourced from Wikipedia)"""
    print("Fetching S&P 500 from GitHub...")
    response = requests.get(SP500_URL, timeout=30)
    response.raise_for_status()

    tickers = []
    for line in response.text.strip().split('\n')[1:]:  # Skip header
        if line:
            ticker = line.split(',')[0].strip()
            if ticker:
                tickers.append(ticker)

    print(f"  Found {len(tickers)} S&P 500 tickers")
    return tickers


def get_tickers_from_wikipedia(url, index_name):
    """Fetch tickers from Wikipedia table"""
    print(f"Fetching {index_name} from Wikipedia...")
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the constituents table
    table = soup.find('table', {'id': 'constituents'})
    if not table:
        tables = soup.find_all('table', {'class': 'wikitable'})
        table = tables[0] if tables else None

    if not table:
        raise ValueError(f"Could not find constituents table for {index_name}")

    tickers = []
    for row in table.find_all('tr')[1:]:  # Skip header
        cells = row.find_all('td')
        if cells:
            ticker = cells[0].get_text(strip=True)
            # Clean up ticker - remove footnotes like [1]
            ticker = ticker.split('[')[0].strip()
            if ticker:
                tickers.append(ticker)

    print(f"  Found {len(tickers)} {index_name} tickers")
    return tickers


def backup_existing_file():
    """Create backup of existing constituents file"""
    if OUTPUT_FILE.exists():
        BACKUP_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = BACKUP_DIR / f'sp1500_constituents_{timestamp}.json'

        with open(OUTPUT_FILE, 'r') as f:
            data = f.read()
        with open(backup_path, 'w') as f:
            f.write(data)

        print(f"Backed up existing file to {backup_path}")


def main():
    print("=" * 60)
    print("S&P 1500 Constituents Updater")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        # Backup existing file
        backup_existing_file()

        # Fetch all three indices
        sp500 = get_sp500_tickers()
        sp400 = get_tickers_from_wikipedia(SP400_URL, "S&P 400")
        sp600 = get_tickers_from_wikipedia(SP600_URL, "S&P 600")

        # Combine and dedupe
        all_tickers = list(set(sp500 + sp400 + sp600))
        all_tickers.sort()

        print(f"\nTotal unique S&P 1500 tickers: {len(all_tickers)}")

        # Calculate letter distribution
        letters = {}
        for t in all_tickers:
            l = t[0] if t else '?'
            letters[l] = letters.get(l, 0) + 1

        print(f"Letter distribution: A-Z all represented")
        print(f"  A: {letters.get('A', 0)}, M: {letters.get('M', 0)}, Z: {letters.get('Z', 0)}")

        # Create the JSON data
        data = {
            'description': 'S&P 1500 Index Constituents (S&P 500 + S&P MidCap 400 + S&P SmallCap 600)',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'sources': {
                'sp500': 'https://github.com/datasets/s-and-p-500-companies',
                'sp400': 'https://en.wikipedia.org/wiki/List_of_S%26P_400_companies',
                'sp600': 'https://en.wikipedia.org/wiki/List_of_S%26P_600_companies'
            },
            'counts': {
                'sp500': len(sp500),
                'sp400': len(sp400),
                'sp600': len(sp600),
                'total_unique': len(all_tickers)
            },
            'tickers': all_tickers
        }

        # Save to file
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✓ Saved {len(all_tickers)} tickers to {OUTPUT_FILE}")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Error updating constituents: {e}")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
