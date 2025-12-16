#!/usr/bin/env python3
"""
Exit Quality Report - v7.1.1
Analyzes trailing stop effectiveness and giveback distribution

Third-party requirement (Dec 16, 2025):
"Create exit quality report showing:
- Trailing stop activation frequency
- Average peak return after activation
- Giveback distribution (how much profit given back from peak to exit)"

Usage:
    python reports/exit_quality_report.py

Output:
    - Console report with key statistics
    - JSON file: reports/exit_quality_analysis.json
"""

import csv
import json
from pathlib import Path
from collections import defaultdict
import statistics

PROJECT_DIR = Path(__file__).parent.parent
TRADES_CSV = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'
OUTPUT_JSON = PROJECT_DIR / 'reports' / 'exit_quality_analysis.json'


def load_trades():
    """Load completed trades from CSV"""
    trades = []

    if not TRADES_CSV.exists():
        print(f"❌ Trades CSV not found: {TRADES_CSV}")
        return trades

    with open(TRADES_CSV, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Include all trades (v7.1 adds trailing stop fields, but older trades still have exits)
            trades.append(row)

    return trades


def calculate_percentiles(values):
    """Calculate median, P25, P75, P90 of a list of values"""
    if not values:
        return {'median': 0, 'p25': 0, 'p75': 0, 'p90': 0, 'count': 0}

    sorted_values = sorted(values)
    n = len(sorted_values)

    return {
        'median': statistics.median(sorted_values),
        'p25': sorted_values[int(n * 0.25)] if n > 0 else 0,
        'p75': sorted_values[int(n * 0.75)] if n > 0 else 0,
        'p90': sorted_values[int(n * 0.9)] if n > 0 else 0,
        'min': sorted_values[0],
        'max': sorted_values[-1],
        'mean': statistics.mean(sorted_values),
        'count': n
    }


def analyze_trailing_stops(trades):
    """Analyze trailing stop activation and performance"""
    # v7.1 trades with trailing stop data
    trailing_stop_trades = []
    no_trailing_stop_trades = []

    for trade in trades:
        activated = trade.get('Trailing_Stop_Activated', '')
        if activated in ['True', 'true', '1']:
            trailing_stop_trades.append(trade)
        else:
            no_trailing_stop_trades.append(trade)

    # Calculate giveback for trailing stop trades
    givebacks = []
    peak_returns = []
    exit_returns = []

    for trade in trailing_stop_trades:
        try:
            peak_pct = float(trade.get('Peak_Return_Pct', 0))
            exit_pct = float(trade.get('Return_Percent', 0))

            if peak_pct > 0 and exit_pct > 0:
                giveback = peak_pct - exit_pct  # How much profit given back
                givebacks.append(giveback)
                peak_returns.append(peak_pct)
                exit_returns.append(exit_pct)
        except (ValueError, TypeError):
            continue

    return {
        'total_trades': len(trades),
        'trailing_stop_activated_count': len(trailing_stop_trades),
        'trailing_stop_not_activated_count': len(no_trailing_stop_trades),
        'trailing_stop_activation_rate': round(len(trailing_stop_trades) / len(trades) * 100, 1) if trades else 0,
        'peak_returns': calculate_percentiles(peak_returns) if peak_returns else None,
        'exit_returns': calculate_percentiles(exit_returns) if exit_returns else None,
        'givebacks': calculate_percentiles(givebacks) if givebacks else None,
        'capture_rate': round(statistics.mean([e/p*100 for p, e in zip(peak_returns, exit_returns)
                                              if p > 0]), 1) if peak_returns else 0
    }


def analyze_exit_types(trades):
    """Analyze exit distribution by type"""
    exit_types = defaultdict(list)

    for trade in trades:
        exit_type = trade.get('Exit_Type', 'Unknown')
        try:
            return_pct = float(trade.get('Return_Percent', 0))
            exit_types[exit_type].append(return_pct)
        except (ValueError, TypeError):
            continue

    return {exit_type: {
        'count': len(returns),
        'win_rate': round(sum(1 for r in returns if r > 0) / len(returns) * 100, 1) if returns else 0,
        'avg_return': round(statistics.mean(returns), 2) if returns else 0,
        'median_return': round(statistics.median(returns), 2) if returns else 0
    } for exit_type, returns in exit_types.items()}


def analyze_stop_distance_effectiveness(trades):
    """Analyze if tighter stops (ATR-based) perform better"""
    # Group by stop distance
    tight_stops = []  # <-6%
    medium_stops = []  # -6% to -7%
    wide_stops = []  # Fallback -7%

    for trade in trades:
        try:
            stop_pct = float(trade.get('Stop_Pct', 0))
            return_pct = float(trade.get('Return_Percent', 0))

            if stop_pct == 0:
                continue  # No stop data

            if stop_pct > -6:
                tight_stops.append(return_pct)
            elif stop_pct > -6.9:
                medium_stops.append(return_pct)
            else:
                wide_stops.append(return_pct)
        except (ValueError, TypeError):
            continue

    return {
        'tight_stops': {
            'range': '>-6%',
            'count': len(tight_stops),
            'avg_return': round(statistics.mean(tight_stops), 2) if tight_stops else 0,
            'win_rate': round(sum(1 for r in tight_stops if r > 0) / len(tight_stops) * 100, 1) if tight_stops else 0
        },
        'medium_stops': {
            'range': '-6% to -7%',
            'count': len(medium_stops),
            'avg_return': round(statistics.mean(medium_stops), 2) if medium_stops else 0,
            'win_rate': round(sum(1 for r in medium_stops if r > 0) / len(medium_stops) * 100, 1) if medium_stops else 0
        },
        'wide_stops': {
            'range': '-7% (cap)',
            'count': len(wide_stops),
            'avg_return': round(statistics.mean(wide_stops), 2) if wide_stops else 0,
            'win_rate': round(sum(1 for r in wide_stops if r > 0) / len(wide_stops) * 100, 1) if wide_stops else 0
        }
    }


def generate_report(trades):
    """Generate complete exit quality report"""
    if not trades:
        return {
            'error': 'No completed trades found',
            'trades_analyzed': 0
        }

    report = {
        'report_version': 'v7.1.1',
        'generated_at': '2025-12-16',
        'trades_analyzed': len(trades),
        'trailing_stop_analysis': analyze_trailing_stops(trades),
        'exit_type_distribution': analyze_exit_types(trades),
        'stop_distance_effectiveness': analyze_stop_distance_effectiveness(trades),
        'interpretation': {
            'capture_rate': '% of peak profit captured at exit (target: 80%+)',
            'giveback': 'Peak - Exit return (lower is better, shows tight trailing)',
            'trailing_stop_policy': 'Lock +8%, trail -2% from peak (v7.1 canonical)',
            'stop_distance': 'ATR-based stops (tight) vs -7% cap (wide)'
        }
    }

    return report


def print_report(report):
    """Print formatted report to console"""
    print("\n" + "="*80)
    print("EXIT QUALITY REPORT - v7.1.1")
    print("="*80)

    if report.get('error'):
        print(f"\n❌ {report['error']}")
        return

    print(f"\n📊 Trades Analyzed: {report['trades_analyzed']}")

    # Trailing stop analysis
    ts = report['trailing_stop_analysis']
    print(f"\n🎯 TRAILING STOP ANALYSIS:")
    print(f"   Activation Rate: {ts['trailing_stop_activation_rate']}% ({ts['trailing_stop_activated_count']}/{ts['total_trades']} trades)")

    if ts.get('peak_returns'):
        print(f"\n   Peak Returns:")
        print(f"      Median: +{ts['peak_returns']['median']:.1f}%")
        print(f"      Mean:   +{ts['peak_returns']['mean']:.1f}%")
        print(f"      Range:  +{ts['peak_returns']['min']:.1f}% to +{ts['peak_returns']['max']:.1f}%")

    if ts.get('exit_returns'):
        print(f"\n   Exit Returns (after giveback):")
        print(f"      Median: +{ts['exit_returns']['median']:.1f}%")
        print(f"      Mean:   +{ts['exit_returns']['mean']:.1f}%")

    if ts.get('givebacks'):
        print(f"\n   Giveback (Peak - Exit):")
        print(f"      Median: {ts['givebacks']['median']:.1f}%")
        print(f"      P25:    {ts['givebacks']['p25']:.1f}%")
        print(f"      P75:    {ts['givebacks']['p75']:.1f}%")
        print(f"      P90:    {ts['givebacks']['p90']:.1f}%")

    if ts.get('capture_rate'):
        print(f"\n   Capture Rate: {ts['capture_rate']}% (target: 80%+)")

    # Exit type distribution
    print(f"\n📉 EXIT TYPE DISTRIBUTION:")
    for exit_type, stats in sorted(report['exit_type_distribution'].items()):
        print(f"   {exit_type:25s} n={stats['count']:3d}  Win Rate: {stats['win_rate']:5.1f}%  Avg: {stats['avg_return']:+6.2f}%")

    # Stop distance effectiveness
    print(f"\n🛑 STOP DISTANCE EFFECTIVENESS:")
    sde = report['stop_distance_effectiveness']
    for key in ['tight_stops', 'medium_stops', 'wide_stops']:
        if sde[key]['count'] > 0:
            stats = sde[key]
            print(f"   {stats['range']:15s} n={stats['count']:3d}  Win Rate: {stats['win_rate']:5.1f}%  Avg: {stats['avg_return']:+6.2f}%")

    # Interpretation
    print(f"\n✅ TARGET BENCHMARKS:")
    print(f"   Capture rate:  80%+ (good trailing stop effectiveness)")
    print(f"   Median giveback: <3% (tight trailing, minimal profit erosion)")
    print(f"   Activation rate: 40%+ (reaching targets frequently)")

    # Warnings
    if ts.get('capture_rate') and ts['capture_rate'] < 75:
        print(f"\n⚠️  WARNING: Capture rate ({ts['capture_rate']}%) below 75% - consider tighter trailing stop")
    if ts.get('givebacks') and ts['givebacks']['median'] > 5:
        print(f"⚠️  WARNING: Median giveback ({ts['givebacks']['median']:.1f}%) >5% - trailing stop may be too loose")

    print("\n" + "="*80)


def main():
    """Main execution"""
    print("Loading trades from CSV...")
    trades = load_trades()

    print(f"Found {len(trades)} completed trades")

    print("Generating exit quality report...")
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
