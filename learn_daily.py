#!/usr/bin/env python3
"""
Daily Learning Engine - Tactical Pattern Detection
Runs every trading day at 5:00 PM to identify and remove losing patterns quickly
"""

import os
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

PROJECT_DIR = Path(__file__).parent

class DailyLearning:
    """Fast tactical learning - identifies obvious losers quickly"""
    
    def __init__(self):
        self.trades_file = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'
        self.catalyst_file = PROJECT_DIR / 'strategy_evolution' / 'catalyst_performance.csv'
        self.exclusions_file = PROJECT_DIR / 'strategy_evolution' / 'catalyst_exclusions.json'
        self.strategy_file = PROJECT_DIR / 'strategy_evolution' / 'strategy_rules.md'
        self.lessons_file = PROJECT_DIR / 'strategy_evolution' / 'lessons_learned.md'
        
    def load_completed_trades(self):
        """Load all completed trades"""
        trades = []
        
        if not self.trades_file.exists():
            return trades
        
        with open(self.trades_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Trade_ID'):
                    trades.append(row)
        
        return trades
    
    def analyze_recent_performance(self, trades, days=7):
        """Analyze last N days of trades for quick pattern detection (PHASE 5 ENHANCED)"""

        if not trades:
            return {}

        # Filter to recent trades
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_trades = []

        for trade in trades:
            try:
                exit_date = datetime.strptime(trade.get('Exit_Date', ''), '%Y-%m-%d')
                if exit_date >= cutoff_date:
                    recent_trades.append(trade)
            except:
                continue

        # Analyze by catalyst
        catalyst_stats = defaultdict(lambda: {
            'total': 0,
            'winners': 0,
            'losers': 0,
            'returns': []
        })

        # PHASE 5: Track new metrics
        tier_stats = defaultdict(lambda: {'total': 0, 'winners': 0, 'returns': []})
        conviction_stats = defaultdict(lambda: {'total': 0, 'winners': 0, 'returns': []})
        news_exits = {'count': 0, 'total_trades': len(recent_trades)}

        for trade in recent_trades:
            catalyst = trade.get('Catalyst_Type', 'Unknown')
            return_pct = float(trade.get('Return_Percent', 0))

            stats = catalyst_stats[catalyst]
            stats['total'] += 1
            stats['returns'].append(return_pct)

            if return_pct > 0:
                stats['winners'] += 1
            else:
                stats['losers'] += 1

            # PHASE 2: Track tier performance
            tier = trade.get('Catalyst_Tier', 'Unknown')
            tier_stats[tier]['total'] += 1
            tier_stats[tier]['returns'].append(return_pct)
            if return_pct > 0:
                tier_stats[tier]['winners'] += 1

            # PHASE 4: Track conviction performance
            conviction = trade.get('Conviction_Level', 'MEDIUM')
            conviction_stats[conviction]['total'] += 1
            conviction_stats[conviction]['returns'].append(return_pct)
            if return_pct > 0:
                conviction_stats[conviction]['winners'] += 1

            # PHASE 1: Track news exit triggers
            if trade.get('News_Exit_Triggered', '').lower() in ['true', '1', 'yes']:
                news_exits['count'] += 1

        # Calculate win rates
        results = {}
        for catalyst, stats in catalyst_stats.items():
            win_rate = (stats['winners'] / stats['total']) * 100 if stats['total'] > 0 else 0
            avg_return = sum(stats['returns']) / len(stats['returns']) if stats['returns'] else 0

            results[catalyst] = {
                'total_trades': stats['total'],
                'winners': stats['winners'],
                'losers': stats['losers'],
                'win_rate': win_rate,
                'avg_return': avg_return,
                'last_7_days': True
            }

        # PHASE 5: Add new dimensions to results
        results['_phase_metrics'] = {
            'tier_performance': {tier: {'win_rate': (s['winners']/s['total']*100) if s['total'] > 0 else 0,
                                        'avg_return': sum(s['returns'])/len(s['returns']) if s['returns'] else 0,
                                        'count': s['total']}
                                for tier, s in tier_stats.items()},
            'conviction_performance': {conv: {'win_rate': (s['winners']/s['total']*100) if s['total'] > 0 else 0,
                                              'avg_return': sum(s['returns'])/len(s['returns']) if s['returns'] else 0,
                                              'count': s['total']}
                                      for conv, s in conviction_stats.items()},
            'news_exit_rate': (news_exits['count'] / news_exits['total_trades'] * 100) if news_exits['total_trades'] > 0 else 0
        }

        return results
    
    def analyze_all_time_performance(self, trades):
        """Analyze all trades for statistical significance"""
        
        catalyst_stats = defaultdict(lambda: {
            'total': 0,
            'winners': 0,
            'losers': 0,
            'returns': []
        })
        
        for trade in trades:
            catalyst = trade.get('Catalyst_Type', 'Unknown')
            return_pct = float(trade.get('Return_Percent', 0))
            
            stats = catalyst_stats[catalyst]
            stats['total'] += 1
            stats['returns'].append(return_pct)
            
            if return_pct > 0:
                stats['winners'] += 1
            else:
                stats['losers'] += 1
        
        results = {}
        for catalyst, stats in catalyst_stats.items():
            win_rate = (stats['winners'] / stats['total']) * 100 if stats['total'] > 0 else 0
            avg_return = sum(stats['returns']) / len(stats['returns']) if stats['returns'] else 0
            
            # Confidence based on sample size
            if stats['total'] < 10:
                confidence = 'Low'
            elif stats['total'] < 25:
                confidence = 'Medium'
            else:
                confidence = 'High'
            
            results[catalyst] = {
                'total_trades': stats['total'],
                'winners': stats['winners'],
                'losers': stats['losers'],
                'win_rate': win_rate,
                'avg_return': avg_return,
                'confidence': confidence
            }
        
        return results
    
    def identify_catalysts_to_exclude(self, all_time_stats):
        """Identify catalysts that should be excluded from strategy"""
        
        exclusions = []
        
        for catalyst, stats in all_time_stats.items():
            # Exclude if: Medium/High confidence AND <35% win rate
            if stats['confidence'] in ['Medium', 'High'] and stats['win_rate'] < 35:
                exclusions.append({
                    'catalyst': catalyst,
                    'win_rate': stats['win_rate'],
                    'total_trades': stats['total_trades'],
                    'confidence': stats['confidence'],
                    'avg_return': stats['avg_return'],
                    'excluded_date': datetime.now().strftime('%Y-%m-%d'),
                    'reason': 'Consistently poor performance'
                })
        
        return exclusions
    
    def identify_warning_catalysts(self, recent_stats, all_time_stats):
        """Identify catalysts showing concerning recent trends"""
        
        warnings = []
        
        for catalyst, recent in recent_stats.items():
            # Warning if: Recently performed poorly (last 7 days)
            if recent['total_trades'] >= 3 and recent['win_rate'] < 30:
                all_time = all_time_stats.get(catalyst, {})
                
                warnings.append({
                    'catalyst': catalyst,
                    'recent_win_rate': recent['win_rate'],
                    'recent_trades': recent['total_trades'],
                    'all_time_win_rate': all_time.get('win_rate', 0),
                    'all_time_trades': all_time.get('total_trades', 0),
                    'status': 'Watch closely - recent underperformance'
                })
        
        return warnings
    
    def update_exclusions_file(self, exclusions):
        """Update the catalyst exclusions JSON file"""
        
        self.exclusions_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing exclusions
        existing = []
        if self.exclusions_file.exists():
            try:
                with open(self.exclusions_file, 'r') as f:
                    data = json.load(f)
                    existing = data.get('excluded_catalysts', [])
            except:
                pass
        
        # Merge with new exclusions (avoid duplicates)
        excluded_names = {e['catalyst'] for e in existing}
        
        for ex in exclusions:
            if ex['catalyst'] not in excluded_names:
                existing.append(ex)
        
        # Save updated exclusions
        with open(self.exclusions_file, 'w') as f:
            json.dump({
                'excluded_catalysts': existing,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'note': 'These catalysts have been automatically excluded by the learning engine'
            }, f, indent=2)
        
        print(f"   ✓ Updated exclusions file: {len(existing)} catalysts excluded")
    
    def update_strategy_rules(self, exclusions):
        """Auto-update strategy_rules.md to reflect exclusions"""
        
        if not self.strategy_file.exists():
            print("   ⚠ strategy_rules.md not found, skipping update")
            return
        
        with open(self.strategy_file, 'r') as f:
            strategy = f.read()
        
        # Add exclusions section if it doesn't exist
        exclusion_section = "\n\n---\n\n## 🚫 AUTO-EXCLUDED CATALYSTS (LEARNED)\n\n"
        exclusion_section += "*The following catalysts have been automatically excluded by the learning engine due to poor performance:*\n\n"
        
        if exclusions:
            for ex in exclusions:
                exclusion_section += f"- **{ex['catalyst']}**: {ex['win_rate']:.1f}% win rate over {ex['total_trades']} trades ({ex['confidence']} confidence)\n"
        else:
            exclusion_section += "- None yet (need more data)\n"
        
        exclusion_section += "\n**These catalysts will be automatically filtered out by the agent.**\n"
        
        # Remove old exclusion section if exists
        if "## 🚫 AUTO-EXCLUDED CATALYSTS" in strategy:
            parts = strategy.split("## 🚫 AUTO-EXCLUDED CATALYSTS")
            strategy = parts[0] + exclusion_section
        else:
            strategy += exclusion_section
        
        # Write updated strategy
        with open(self.strategy_file, 'w') as f:
            f.write(strategy)
        
        print(f"   ✓ Updated strategy_rules.md with {len(exclusions)} exclusions")
    
    def append_learning_insights(self, all_time_stats, exclusions, warnings, recent_stats=None):
        """Append insights to lessons_learned.md (PHASE 5 ENHANCED)"""

        insights = []
        insights.append(f"\n\n{'='*80}\n")
        insights.append(f"# DAILY LEARNING UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        if exclusions:
            insights.append("## 🚫 NEW EXCLUSIONS\n\n")
            for ex in exclusions:
                insights.append(f"- **{ex['catalyst']}** excluded: {ex['win_rate']:.1f}% win rate over {ex['total_trades']} trades\n")

        if warnings:
            insights.append("\n## ⚠️ PERFORMANCE WARNINGS\n\n")
            for w in warnings:
                insights.append(f"- **{w['catalyst']}**: Recent {w['recent_win_rate']:.1f}% win rate (last 7 days) vs {w['all_time_win_rate']:.1f}% all-time\n")

        # PHASE 5: Add new metrics if available
        if recent_stats and '_phase_metrics' in recent_stats:
            phase_metrics = recent_stats['_phase_metrics']

            insights.append("\n## 📈 PHASE 1-4 PERFORMANCE (Last 7 Days)\n\n")

            # Tier performance
            if phase_metrics['tier_performance']:
                insights.append("**Catalyst Tier Performance:**\n")
                for tier, stats in sorted(phase_metrics['tier_performance'].items()):
                    insights.append(f"- {tier}: {stats['win_rate']:.1f}% win rate, {stats['avg_return']:.2f}% avg ({stats['count']} trades)\n")
                insights.append("\n")

            # Conviction performance
            if phase_metrics['conviction_performance']:
                insights.append("**Conviction Performance:**\n")
                for conv, stats in sorted(phase_metrics['conviction_performance'].items(), reverse=True):
                    insights.append(f"- {conv}: {stats['win_rate']:.1f}% win rate, {stats['avg_return']:.2f}% avg ({stats['count']} trades)\n")
                insights.append("\n")

            # News exits
            insights.append(f"**News Exit Rate:** {phase_metrics['news_exit_rate']:.1f}% (Phase 1 invalidation system)\n\n")

        if all_time_stats:
            insights.append("\n## 📊 CURRENT PERFORMANCE BY CATALYST\n\n")
            sorted_catalysts = sorted(all_time_stats.items(), key=lambda x: x[1]['win_rate'], reverse=True)

            for catalyst, stats in sorted_catalysts:
                insights.append(f"- **{catalyst}**: {stats['win_rate']:.1f}% ({stats['winners']}/{stats['total_trades']} wins) - {stats['confidence']} confidence\n")

        insights.append(f"\n*Auto-generated by Daily Learning Engine (Phase 5 Enhanced)*\n")

        # Append to lessons_learned.md
        with open(self.lessons_file, 'a') as f:
            f.write(''.join(insights))

        print(f"   ✓ Appended insights to lessons_learned.md")
    
    def run_learning_cycle(self):
        """Execute daily learning cycle"""
        
        print("\n" + "="*60)
        print("DAILY LEARNING ENGINE - TACTICAL ANALYSIS")
        print("="*60 + "\n")
        
        # Load trades
        print("1. Loading completed trades...")
        trades = self.load_completed_trades()
        
        if len(trades) < 5:
            print(f"   ⚠ Only {len(trades)} trades completed")
            print("   Need at least 5 trades for daily learning")
            print("   Skipping learning cycle\n")
            return
        
        print(f"   ✓ Loaded {len(trades)} completed trades\n")
        
        # Analyze recent performance (last 7 days)
        print("2. Analyzing recent performance (last 7 days)...")
        recent_stats = self.analyze_recent_performance(trades, days=7)
        print(f"   ✓ Analyzed {len(recent_stats)} catalyst types\n")
        
        # Analyze all-time performance
        print("3. Analyzing all-time performance...")
        all_time_stats = self.analyze_all_time_performance(trades)
        print(f"   ✓ Statistical analysis complete\n")
        
        # Identify exclusions
        print("4. Identifying catalysts to exclude...")
        exclusions = self.identify_catalysts_to_exclude(all_time_stats)
        
        if exclusions:
            print(f"   ⚠ Found {len(exclusions)} catalysts to exclude:")
            for ex in exclusions:
                print(f"      - {ex['catalyst']}: {ex['win_rate']:.1f}% win rate")
        else:
            print("   ✓ No exclusions needed yet")
        print()
        
        # Identify warnings
        print("5. Checking for performance warnings...")
        warnings = self.identify_warning_catalysts(recent_stats, all_time_stats)
        
        if warnings:
            print(f"   ⚠ {len(warnings)} catalysts showing concerning trends")
        else:
            print("   ✓ No immediate concerns")
        print()
        
        # Update files
        print("6. Updating strategy files...")
        self.update_exclusions_file(exclusions)
        self.update_strategy_rules(exclusions)
        print()
        
        # Append insights (PHASE 5: pass recent_stats)
        print("7. Documenting learning insights...")
        self.append_learning_insights(all_time_stats, exclusions, warnings, recent_stats)
        print()
        
        # Summary
        print("="*60)
        print("DAILY LEARNING COMPLETE")
        print("="*60)
        print(f"\nTotal trades analyzed: {len(trades)}")
        print(f"Catalysts excluded: {len(exclusions)}")
        print(f"Performance warnings: {len(warnings)}")
        
        if exclusions:
            print("\n⚠️ STRATEGY UPDATED: The following catalysts are now excluded:")
            for ex in exclusions:
                print(f"   - {ex['catalyst']}")
        
        print("\n" + "="*60 + "\n")

def main():
    """Main execution"""
    engine = DailyLearning()
    engine.run_learning_cycle()

if __name__ == '__main__':
    main()