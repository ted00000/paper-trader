#!/usr/bin/env python3
"""
Edge Attribution Report - v7.1.1
Analyzes where the trading edge comes from across multiple dimensions

Third-party requirement (Dec 16, 2025):
"Create edge attribution report showing expectancy by:
- Catalyst tier/type
- RS bucket (Elite 90+ vs Good 70-89 vs Weak <70)
- Volume quality (EXCELLENT vs STRONG vs GOOD)
- Market regime (VIX + breadth)
- Conviction level (HIGH vs MEDIUM-HIGH vs MEDIUM)"

Usage:
    python reports/edge_attribution_report.py

Output:
    - Console report with key statistics
    - JSON file: reports/edge_attribution_analysis.json
"""

import csv
import json
from pathlib import Path
from collections import defaultdict
import statistics

PROJECT_DIR = Path(__file__).parent.parent
TRADES_CSV = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'
OUTPUT_JSON = PROJECT_DIR / 'reports' / 'edge_attribution_analysis.json'


def load_trades():
    """Load completed trades from CSV"""
    trades = []

    if not TRADES_CSV.exists():
        print(f"❌ Trades CSV not found: {TRADES_CSV}")
        return trades

    with open(TRADES_CSV, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            trades.append(row)

    return trades


def calculate_expectancy(returns):
    """
    Calculate expectancy (expected value per trade)
    Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)
    """
    if not returns:
        return {
            'count': 0,
            'win_rate': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'expectancy': 0,
            'total_return': 0
        }

    wins = [r for r in returns if r > 0]
    losses = [r for r in returns if r < 0]

    win_rate = len(wins) / len(returns) * 100 if returns else 0
    loss_rate = len(losses) / len(returns) * 100 if returns else 0

    avg_win = statistics.mean(wins) if wins else 0
    avg_loss = abs(statistics.mean(losses)) if losses else 0

    expectancy = (win_rate/100 * avg_win) - (loss_rate/100 * avg_loss)
    total_return = sum(returns)

    return {
        'count': len(returns),
        'win_rate': round(win_rate, 1),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'expectancy': round(expectancy, 2),
        'total_return': round(total_return, 2),
        'avg_return': round(statistics.mean(returns), 2) if returns else 0
    }


def analyze_by_catalyst(trades):
    """Analyze edge by catalyst tier and type"""
    by_tier = defaultdict(list)
    by_type = defaultdict(list)

    for trade in trades:
        try:
            return_pct = float(trade.get('Return_Percent', 0))
            tier = trade.get('Catalyst_Tier', 'Unknown')
            cat_type = trade.get('Catalyst_Type', 'Unknown')

            by_tier[tier].append(return_pct)
            by_type[cat_type].append(return_pct)
        except (ValueError, TypeError):
            continue

    return {
        'by_tier': {tier: calculate_expectancy(returns)
                   for tier, returns in by_tier.items()},
        'by_type': {cat_type: calculate_expectancy(returns)
                   for cat_type, returns in by_type.items() if len(returns) >= 3}  # Min 3 trades
    }


def analyze_by_rs_rating(trades):
    """Analyze edge by RS rating buckets"""
    elite = []  # RS 90+
    good = []   # RS 70-89
    weak = []   # RS <70

    for trade in trades:
        try:
            return_pct = float(trade.get('Return_Percent', 0))
            # Try to parse RS rating from various possible column names
            rs_rating = float(trade.get('Relative_Strength', 0))

            if rs_rating >= 90:
                elite.append(return_pct)
            elif rs_rating >= 70:
                good.append(return_pct)
            else:
                weak.append(return_pct)
        except (ValueError, TypeError):
            continue

    return {
        'elite_90_plus': calculate_expectancy(elite),
        'good_70_89': calculate_expectancy(good),
        'weak_below_70': calculate_expectancy(weak)
    }


def analyze_by_volume_quality(trades):
    """Analyze edge by volume quality"""
    by_volume = defaultdict(list)

    for trade in trades:
        try:
            return_pct = float(trade.get('Return_Percent', 0))
            vol_quality = trade.get('Volume_Quality', 'Unknown').upper()

            by_volume[vol_quality].append(return_pct)
        except (ValueError, TypeError):
            continue

    return {quality: calculate_expectancy(returns)
            for quality, returns in by_volume.items() if returns}


def analyze_by_conviction(trades):
    """Analyze edge by conviction level"""
    by_conviction = defaultdict(list)

    for trade in trades:
        try:
            return_pct = float(trade.get('Return_Percent', 0))
            conviction = trade.get('Conviction_Level', 'MEDIUM').upper()

            by_conviction[conviction].append(return_pct)
        except (ValueError, TypeError):
            continue

    return {level: calculate_expectancy(returns)
            for level, returns in by_conviction.items() if returns}


def analyze_by_vix_regime(trades):
    """Analyze edge by VIX regime"""
    by_vix = defaultdict(list)

    for trade in trades:
        try:
            return_pct = float(trade.get('Return_Percent', 0))
            vix_regime = trade.get('VIX_Regime', 'UNKNOWN')

            by_vix[vix_regime].append(return_pct)
        except (ValueError, TypeError):
            continue

    return {regime: calculate_expectancy(returns)
            for regime, returns in by_vix.items() if returns}


def analyze_by_market_breadth(trades):
    """Analyze edge by market breadth regime"""
    by_breadth = defaultdict(list)

    for trade in trades:
        try:
            return_pct = float(trade.get('Return_Percent', 0))
            breadth = trade.get('Market_Breadth_Regime', 'UNKNOWN')

            by_breadth[breadth].append(return_pct)
        except (ValueError, TypeError):
            continue

    return {regime: calculate_expectancy(returns)
            for regime, returns in by_breadth.items() if returns}


def analyze_by_supporting_factors(trades):
    """Analyze edge by number of supporting factors (conviction scoring)"""
    by_factors = defaultdict(list)

    for trade in trades:
        try:
            return_pct = float(trade.get('Return_Percent', 0))
            factors = int(trade.get('Supporting_Factors', 0))

            # Bucket: 7+ (HIGH), 5-6 (MEDIUM-HIGH), 3-4 (MEDIUM), <3 (LOW)
            if factors >= 7:
                bucket = '7+ (HIGH)'
            elif factors >= 5:
                bucket = '5-6 (MEDIUM-HIGH)'
            elif factors >= 3:
                bucket = '3-4 (MEDIUM)'
            else:
                bucket = '<3 (LOW)'

            by_factors[bucket].append(return_pct)
        except (ValueError, TypeError):
            continue

    return {bucket: calculate_expectancy(returns)
            for bucket, returns in by_factors.items() if returns}


def generate_report(trades):
    """Generate complete edge attribution report"""
    if not trades:
        return {
            'error': 'No completed trades found',
            'trades_analyzed': 0
        }

    # Calculate overall expectancy
    all_returns = []
    for trade in trades:
        try:
            return_pct = float(trade.get('Return_Percent', 0))
            all_returns.append(return_pct)
        except (ValueError, TypeError):
            continue

    report = {
        'report_version': 'v7.1.1',
        'generated_at': '2025-12-16',
        'trades_analyzed': len(trades),
        'overall_expectancy': calculate_expectancy(all_returns),
        'edge_by_catalyst': analyze_by_catalyst(trades),
        'edge_by_rs_rating': analyze_by_rs_rating(trades),
        'edge_by_volume_quality': analyze_by_volume_quality(trades),
        'edge_by_conviction': analyze_by_conviction(trades),
        'edge_by_vix_regime': analyze_by_vix_regime(trades),
        'edge_by_market_breadth': analyze_by_market_breadth(trades),
        'edge_by_supporting_factors': analyze_by_supporting_factors(trades),
        'interpretation': {
            'expectancy': 'Expected profit per trade (positive = edge)',
            'target_win_rate': '65-70% after enhancements',
            'positive_expectancy': 'Win Rate × Avg Win > Loss Rate × Avg Loss',
            'best_edge': 'Identify which factors drive highest expectancy'
        }
    }

    return report


def print_report(report):
    """Print formatted report to console"""
    print("\n" + "="*80)
    print("EDGE ATTRIBUTION REPORT - v7.1.1")
    print("="*80)

    if report.get('error'):
        print(f"\n❌ {report['error']}")
        return

    print(f"\n📊 Trades Analyzed: {report['trades_analyzed']}")

    # Overall expectancy
    overall = report['overall_expectancy']
    print(f"\n🎯 OVERALL PERFORMANCE:")
    print(f"   Win Rate:    {overall['win_rate']:.1f}%")
    print(f"   Avg Win:     +{overall['avg_win']:.2f}%")
    print(f"   Avg Loss:    -{overall['avg_loss']:.2f}%")
    print(f"   Expectancy:  {overall['expectancy']:+.2f}% per trade")
    print(f"   Total Return: {overall['total_return']:+.2f}%")

    # By catalyst tier
    print(f"\n📋 EDGE BY CATALYST TIER:")
    for tier in ['Tier 1', 'Tier 2', 'Tier 3', 'Unknown']:
        if tier in report['edge_by_catalyst']['by_tier']:
            stats = report['edge_by_catalyst']['by_tier'][tier]
            print(f"   {tier:10s} n={stats['count']:3d}  WR: {stats['win_rate']:5.1f}%  "
                  f"Expectancy: {stats['expectancy']:+6.2f}%  Total: {stats['total_return']:+7.2f}%")

    # By catalyst type (top 10 by count)
    print(f"\n🎪 EDGE BY CATALYST TYPE (Top 10):")
    catalyst_types = sorted(report['edge_by_catalyst']['by_type'].items(),
                           key=lambda x: x[1]['count'], reverse=True)[:10]
    for cat_type, stats in catalyst_types:
        print(f"   {cat_type[:30]:30s} n={stats['count']:3d}  WR: {stats['win_rate']:5.1f}%  "
              f"Exp: {stats['expectancy']:+6.2f}%")

    # By RS rating
    print(f"\n📈 EDGE BY RS RATING:")
    for bucket in ['elite_90_plus', 'good_70_89', 'weak_below_70']:
        if report['edge_by_rs_rating'][bucket]['count'] > 0:
            stats = report['edge_by_rs_rating'][bucket]
            label = bucket.replace('_', ' ').title()
            print(f"   {label:20s} n={stats['count']:3d}  WR: {stats['win_rate']:5.1f}%  "
                  f"Expectancy: {stats['expectancy']:+6.2f}%")

    # By volume quality
    print(f"\n🔊 EDGE BY VOLUME QUALITY:")
    for quality in ['EXCELLENT', 'STRONG', 'GOOD', 'Unknown']:
        if quality in report['edge_by_volume_quality']:
            stats = report['edge_by_volume_quality'][quality]
            print(f"   {quality:15s} n={stats['count']:3d}  WR: {stats['win_rate']:5.1f}%  "
                  f"Expectancy: {stats['expectancy']:+6.2f}%")

    # By conviction level
    print(f"\n💪 EDGE BY CONVICTION LEVEL:")
    for level in ['HIGH', 'MEDIUM-HIGH', 'MEDIUM', 'LOW']:
        if level in report['edge_by_conviction']:
            stats = report['edge_by_conviction'][level]
            print(f"   {level:15s} n={stats['count']:3d}  WR: {stats['win_rate']:5.1f}%  "
                  f"Expectancy: {stats['expectancy']:+6.2f}%")

    # By supporting factors
    print(f"\n🔢 EDGE BY SUPPORTING FACTORS:")
    for bucket in ['7+ (HIGH)', '5-6 (MEDIUM-HIGH)', '3-4 (MEDIUM)', '<3 (LOW)']:
        if bucket in report['edge_by_supporting_factors']:
            stats = report['edge_by_supporting_factors'][bucket]
            print(f"   {bucket:20s} n={stats['count']:3d}  WR: {stats['win_rate']:5.1f}%  "
                  f"Expectancy: {stats['expectancy']:+6.2f}%")

    # By VIX regime
    print(f"\n📉 EDGE BY VIX REGIME:")
    for regime in ['VERY_LOW', 'LOW', 'ELEVATED', 'HIGH', 'EXTREME']:
        if regime in report['edge_by_vix_regime']:
            stats = report['edge_by_vix_regime'][regime]
            print(f"   {regime:15s} n={stats['count']:3d}  WR: {stats['win_rate']:5.1f}%  "
                  f"Expectancy: {stats['expectancy']:+6.2f}%")

    # By market breadth
    print(f"\n🌊 EDGE BY MARKET BREADTH:")
    for regime in ['HEALTHY', 'DEGRADED', 'UNHEALTHY']:
        if regime in report['edge_by_market_breadth']:
            stats = report['edge_by_market_breadth'][regime]
            print(f"   {regime:15s} n={stats['count']:3d}  WR: {stats['win_rate']:5.1f}%  "
                  f"Expectancy: {stats['expectancy']:+6.2f}%")

    # Interpretation
    print(f"\n✅ KEY INSIGHTS:")
    print(f"   Expectancy >0: Trading edge exists (profitable over time)")
    print(f"   Target win rate: 65-70% (current: {overall['win_rate']:.1f}%)")
    print(f"   Best edge: Highest expectancy categories drive performance")

    print("\n" + "="*80)


def main():
    """Main execution"""
    print("Loading trades from CSV...")
    trades = load_trades()

    print(f"Found {len(trades)} completed trades")

    print("Generating edge attribution report...")
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
