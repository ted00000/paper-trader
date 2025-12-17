#!/usr/bin/env python3
"""
Execution Cost Report - v7.1.1
Analyzes slippage distribution by regime, spread, and other factors

Third-party requirement (Dec 16, 2025):
"Create execution cost report showing slippage distribution by regime/spread.
Need median, P90, P99 slippage. Identify if certain conditions have excessive slippage."

Usage:
    python reports/execution_cost_report.py

Output:
    - Console report with key statistics
    - JSON file: reports/execution_cost_analysis.json
"""

import csv
import json
from pathlib import Path
from collections import defaultdict
import statistics

PROJECT_DIR = Path(__file__).parent.parent
TRADES_CSV = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'
OUTPUT_JSON = PROJECT_DIR / 'reports' / 'execution_cost_analysis.json'


def load_trades():
    """Load completed trades from CSV"""
    trades = []

    if not TRADES_CSV.exists():
        print(f"❌ Trades CSV not found: {TRADES_CSV}")
        return trades

    with open(TRADES_CSV, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only include trades with v7.1+ data (has slippage_bps)
            if row.get('Slippage_Bps') and row['Slippage_Bps'] not in ['', '0', '0.0']:
                trades.append(row)

    return trades


def calculate_percentiles(values):
    """Calculate median, P90, P99 of a list of values"""
    if not values:
        return {'median': 0, 'p90': 0, 'p99': 0, 'count': 0}

    sorted_values = sorted(values)
    n = len(sorted_values)

    return {
        'median': statistics.median(sorted_values),
        'p90': sorted_values[int(n * 0.9)] if n > 0 else 0,
        'p99': sorted_values[int(n * 0.99)] if n >= 100 else sorted_values[-1] if n > 0 else 0,
        'min': sorted_values[0],
        'max': sorted_values[-1],
        'mean': statistics.mean(sorted_values),
        'count': n
    }


def analyze_slippage_by_regime(trades):
    """Analyze slippage by VIX regime"""
    by_vix_regime = defaultdict(list)
    by_breadth_regime = defaultdict(list)

    for trade in trades:
        slippage_bps = float(trade.get('Slippage_Bps', 0))
        vix_regime = trade.get('VIX_Regime', 'UNKNOWN')
        breadth_regime = trade.get('Market_Breadth_Regime', 'UNKNOWN')

        by_vix_regime[vix_regime].append(slippage_bps)
        by_breadth_regime[breadth_regime].append(slippage_bps)

    return {
        'by_vix_regime': {regime: calculate_percentiles(values)
                         for regime, values in by_vix_regime.items()},
        'by_breadth_regime': {regime: calculate_percentiles(values)
                             for regime, values in by_breadth_regime.items()}
    }


def analyze_slippage_by_spread(trades):
    """Analyze slippage by entry spread percentage"""
    # Bucket spreads: 0-0.1%, 0.1-0.2%, 0.2-0.3%, 0.3-0.4%, 0.4-0.5%
    spread_buckets = {
        '0-0.1%': [],
        '0.1-0.2%': [],
        '0.2-0.3%': [],
        '0.3-0.4%': [],
        '0.4-0.5%': []
    }

    for trade in trades:
        slippage_bps = float(trade.get('Slippage_Bps', 0))
        spread_pct = float(trade.get('Entry_Spread_Pct', 0))

        if spread_pct <= 0.1:
            spread_buckets['0-0.1%'].append(slippage_bps)
        elif spread_pct <= 0.2:
            spread_buckets['0.1-0.2%'].append(slippage_bps)
        elif spread_pct <= 0.3:
            spread_buckets['0.2-0.3%'].append(slippage_bps)
        elif spread_pct <= 0.4:
            spread_buckets['0.3-0.4%'].append(slippage_bps)
        elif spread_pct <= 0.5:
            spread_buckets['0.4-0.5%'].append(slippage_bps)

    return {bucket: calculate_percentiles(values)
            for bucket, values in spread_buckets.items() if values}


def analyze_slippage_by_catalyst(trades):
    """Analyze slippage by catalyst tier"""
    by_tier = defaultdict(list)

    for trade in trades:
        slippage_bps = float(trade.get('Slippage_Bps', 0))
        tier = trade.get('Catalyst_Tier', 'Unknown')

        by_tier[tier].append(slippage_bps)

    return {tier: calculate_percentiles(values)
            for tier, values in by_tier.items()}


def analyze_overall_slippage(trades):
    """Calculate overall slippage statistics"""
    all_slippage = [float(trade.get('Slippage_Bps', 0)) for trade in trades]

    # Count favorable vs adverse slippage
    favorable = [s for s in all_slippage if s < 0]
    adverse = [s for s in all_slippage if s > 0]
    neutral = [s for s in all_slippage if s == 0]

    return {
        'overall': calculate_percentiles(all_slippage),
        'favorable_count': len(favorable),
        'adverse_count': len(adverse),
        'neutral_count': len(neutral),
        'favorable_pct': round(len(favorable) / len(all_slippage) * 100, 1) if all_slippage else 0,
        'adverse_pct': round(len(adverse) / len(all_slippage) * 100, 1) if all_slippage else 0
    }


def generate_report(trades):
    """Generate complete execution cost report"""
    if not trades:
        return {
            'error': 'No trades with v7.1+ slippage data found',
            'trades_analyzed': 0
        }

    report = {
        'report_version': 'v7.1.1',
        'generated_at': '2025-12-16',
        'trades_analyzed': len(trades),
        'overall_slippage': analyze_overall_slippage(trades),
        'slippage_by_regime': analyze_slippage_by_regime(trades),
        'slippage_by_spread': analyze_slippage_by_spread(trades),
        'slippage_by_catalyst_tier': analyze_slippage_by_catalyst(trades),
        'interpretation': {
            'slippage_bps': 'Positive = paid more than mid (adverse), Negative = paid less than mid (favorable)',
            'target': 'Median <5 bps (good execution), P90 <20 bps (acceptable tail risk)',
            'spread_threshold': '0.5% spread check prevents trades with >20 bps expected slippage'
        }
    }

    return report


def print_report(report):
    """Print formatted report to console"""
    print("\n" + "="*80)
    print("EXECUTION COST REPORT - v7.1.1")
    print("="*80)

    if report.get('error'):
        print(f"\n❌ {report['error']}")
        return

    print(f"\n📊 Trades Analyzed: {report['trades_analyzed']}")

    # Overall slippage
    overall = report['overall_slippage']['overall']
    print(f"\n🎯 OVERALL SLIPPAGE:")
    print(f"   Median:  {overall['median']:+.1f} bps")
    print(f"   Mean:    {overall['mean']:+.1f} bps")
    print(f"   P90:     {overall['p90']:+.1f} bps")
    print(f"   P99:     {overall['p99']:+.1f} bps")
    print(f"   Range:   {overall['min']:+.1f} to {overall['max']:+.1f} bps")

    # Favorable vs adverse
    fav_pct = report['overall_slippage']['favorable_pct']
    adv_pct = report['overall_slippage']['adverse_pct']
    print(f"\n   Favorable: {report['overall_slippage']['favorable_count']} trades ({fav_pct}%)")
    print(f"   Adverse:   {report['overall_slippage']['adverse_count']} trades ({adv_pct}%)")

    # By VIX regime
    print(f"\n📈 SLIPPAGE BY VIX REGIME:")
    for regime, stats in report['slippage_by_regime']['by_vix_regime'].items():
        print(f"   {regime:15s} Median: {stats['median']:+6.1f} bps  P90: {stats['p90']:+6.1f} bps  (n={stats['count']})")

    # By market breadth
    print(f"\n🌊 SLIPPAGE BY MARKET BREADTH:")
    for regime, stats in report['slippage_by_regime']['by_breadth_regime'].items():
        print(f"   {regime:15s} Median: {stats['median']:+6.1f} bps  P90: {stats['p90']:+6.1f} bps  (n={stats['count']})")

    # By spread
    print(f"\n💰 SLIPPAGE BY ENTRY SPREAD:")
    for bucket, stats in report['slippage_by_spread'].items():
        print(f"   {bucket:10s} Median: {stats['median']:+6.1f} bps  P90: {stats['p90']:+6.1f} bps  (n={stats['count']})")

    # By catalyst tier
    print(f"\n🎪 SLIPPAGE BY CATALYST TIER:")
    for tier, stats in report['slippage_by_catalyst_tier'].items():
        print(f"   {tier:10s} Median: {stats['median']:+6.1f} bps  P90: {stats['p90']:+6.1f} bps  (n={stats['count']})")

    # Interpretation
    print(f"\n✅ TARGET BENCHMARKS:")
    print(f"   Good execution:  Median <5 bps")
    print(f"   Acceptable risk: P90 <20 bps")
    print(f"   Spread threshold validates if <0.5% prevents >20 bps slippage")

    # Warnings
    if overall['median'] > 10:
        print(f"\n⚠️  WARNING: Median slippage ({overall['median']:.1f} bps) exceeds 10 bps target")
    if overall['p90'] > 20:
        print(f"⚠️  WARNING: P90 slippage ({overall['p90']:.1f} bps) exceeds 20 bps acceptable risk")

    print("\n" + "="*80)


def main():
    """Main execution"""
    print("Loading trades from CSV...")
    trades = load_trades()

    print(f"Found {len(trades)} trades with v7.1+ slippage data")

    print("Generating execution cost report...")
    report = generate_report(trades)

    # Save JSON report
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✅ Report saved to: {OUTPUT_JSON}")

    # Print console report
    print_report(report)


if __name__ == '__main__':
    main()
