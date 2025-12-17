#!/usr/bin/env python3
"""
Weekly Learning Engine - Strategic Analysis
Runs every Sunday at 6:00 PM for deeper pattern analysis and parameter optimization
"""

import os
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import statistics

PROJECT_DIR = Path(__file__).parent

class WeeklyLearning:
    """Strategic learning - deeper analysis and optimization"""
    
    def __init__(self):
        self.trades_file = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'
        self.catalyst_file = PROJECT_DIR / 'strategy_evolution' / 'catalyst_performance.csv'
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
    
    def analyze_catalyst_performance(self, trades):
        """Deep analysis by catalyst type (PHASE 5 ENHANCED)"""

        catalyst_stats = defaultdict(lambda: {
            'total': 0,
            'winners': 0,
            'losers': 0,
            'returns': [],
            'hold_times': [],
            'winner_hold_times': [],
            'loser_hold_times': []
        })

        # PHASE 5: Track new dimensions
        tier_stats = defaultdict(lambda: {
            'total': 0, 'winners': 0, 'returns': [], 'hold_times': []
        })
        conviction_stats = defaultdict(lambda: {
            'total': 0, 'winners': 0, 'returns': [], 'hold_times': []
        })
        vix_regime_stats = defaultdict(lambda: {
            'total': 0, 'winners': 0, 'returns': []
        })
        news_validation_stats = {
            'high_score': {'total': 0, 'winners': 0, 'returns': []},  # >=10
            'low_score': {'total': 0, 'winners': 0, 'returns': []},   # <10
            'exits_triggered': 0,
            'total_trades': 0
        }
        rs_stats = {
            'strong_rs': {'total': 0, 'winners': 0, 'returns': []},  # >=3%
            'weak_rs': {'total': 0, 'winners': 0, 'returns': []}     # <3%
        }

        for trade in trades:
            catalyst = trade.get('Catalyst_Type', 'Unknown')
            return_pct = float(trade.get('Return_Percent', 0))
            hold_days = int(trade.get('Hold_Days', 0))

            stats = catalyst_stats[catalyst]
            stats['total'] += 1
            stats['returns'].append(return_pct)
            stats['hold_times'].append(hold_days)

            is_winner = return_pct > 0

            if is_winner:
                stats['winners'] += 1
                stats['winner_hold_times'].append(hold_days)
            else:
                stats['losers'] += 1
                stats['loser_hold_times'].append(hold_days)

            # PHASE 5: Track tier performance
            tier = trade.get('Catalyst_Tier', 'Unknown')
            tier_stats[tier]['total'] += 1
            tier_stats[tier]['returns'].append(return_pct)
            tier_stats[tier]['hold_times'].append(hold_days)
            if is_winner:
                tier_stats[tier]['winners'] += 1

            # PHASE 5: Track conviction performance
            conviction = trade.get('Conviction_Level', 'MEDIUM')
            conviction_stats[conviction]['total'] += 1
            conviction_stats[conviction]['returns'].append(return_pct)
            conviction_stats[conviction]['hold_times'].append(hold_days)
            if is_winner:
                conviction_stats[conviction]['winners'] += 1

            # PHASE 5: Track VIX regime performance
            vix_regime = trade.get('Market_Regime', 'UNKNOWN')
            vix_regime_stats[vix_regime]['total'] += 1
            vix_regime_stats[vix_regime]['returns'].append(return_pct)
            if is_winner:
                vix_regime_stats[vix_regime]['winners'] += 1

            # PHASE 5: Track news validation effectiveness
            news_validation_stats['total_trades'] += 1
            news_score = float(trade.get('News_Validation_Score', 0))
            if news_score >= 10:
                news_validation_stats['high_score']['total'] += 1
                news_validation_stats['high_score']['returns'].append(return_pct)
                if is_winner:
                    news_validation_stats['high_score']['winners'] += 1
            else:
                news_validation_stats['low_score']['total'] += 1
                news_validation_stats['low_score']['returns'].append(return_pct)
                if is_winner:
                    news_validation_stats['low_score']['winners'] += 1

            if trade.get('News_Exit_Triggered', '').lower() in ['true', '1', 'yes']:
                news_validation_stats['exits_triggered'] += 1

            # PHASE 5: Track relative strength effectiveness
            rs_value = float(trade.get('Relative_Strength', 0))
            if rs_value >= 3.0:
                rs_stats['strong_rs']['total'] += 1
                rs_stats['strong_rs']['returns'].append(return_pct)
                if is_winner:
                    rs_stats['strong_rs']['winners'] += 1
            else:
                rs_stats['weak_rs']['total'] += 1
                rs_stats['weak_rs']['returns'].append(return_pct)
                if is_winner:
                    rs_stats['weak_rs']['winners'] += 1
        
        # Calculate metrics
        results = {}
        for catalyst, stats in catalyst_stats.items():
            if stats['total'] == 0:
                continue

            win_rate = (stats['winners'] / stats['total']) * 100
            avg_return = statistics.mean(stats['returns'])
            median_return = statistics.median(stats['returns'])
            avg_hold = statistics.mean(stats['hold_times']) if stats['hold_times'] else 0

            avg_winner_hold = statistics.mean(stats['winner_hold_times']) if stats['winner_hold_times'] else 0
            avg_loser_hold = statistics.mean(stats['loser_hold_times']) if stats['loser_hold_times'] else 0

            # Best and worst trades
            best_trade = max(stats['returns']) if stats['returns'] else 0
            worst_trade = min(stats['returns']) if stats['returns'] else 0

            results[catalyst] = {
                'total_trades': stats['total'],
                'winners': stats['winners'],
                'losers': stats['losers'],
                'win_rate': win_rate,
                'avg_return': avg_return,
                'median_return': median_return,
                'best_trade': best_trade,
                'worst_trade': worst_trade,
                'avg_hold_days': avg_hold,
                'avg_winner_hold': avg_winner_hold,
                'avg_loser_hold': avg_loser_hold,
                'optimal_exit_day': round(avg_winner_hold) if avg_winner_hold > 0 else 0
            }

        # PHASE 5: Add new dimensions to results
        results['_phase_metrics'] = {
            'tier_performance': {},
            'conviction_performance': {},
            'vix_regime_performance': {},
            'news_validation_performance': {},
            'relative_strength_performance': {}
        }

        # Tier performance
        for tier, stats in tier_stats.items():
            if stats['total'] > 0:
                results['_phase_metrics']['tier_performance'][tier] = {
                    'win_rate': (stats['winners'] / stats['total'] * 100),
                    'avg_return': statistics.mean(stats['returns']),
                    'avg_hold': statistics.mean(stats['hold_times']) if stats['hold_times'] else 0,
                    'count': stats['total']
                }

        # Conviction performance
        for conv, stats in conviction_stats.items():
            if stats['total'] > 0:
                results['_phase_metrics']['conviction_performance'][conv] = {
                    'win_rate': (stats['winners'] / stats['total'] * 100),
                    'avg_return': statistics.mean(stats['returns']),
                    'avg_hold': statistics.mean(stats['hold_times']) if stats['hold_times'] else 0,
                    'count': stats['total']
                }

        # VIX regime performance
        for regime, stats in vix_regime_stats.items():
            if stats['total'] > 0:
                results['_phase_metrics']['vix_regime_performance'][regime] = {
                    'win_rate': (stats['winners'] / stats['total'] * 100),
                    'avg_return': statistics.mean(stats['returns']),
                    'count': stats['total']
                }

        # News validation performance
        if news_validation_stats['high_score']['total'] > 0:
            results['_phase_metrics']['news_validation_performance']['high_score'] = {
                'win_rate': (news_validation_stats['high_score']['winners'] / news_validation_stats['high_score']['total'] * 100),
                'avg_return': statistics.mean(news_validation_stats['high_score']['returns']),
                'count': news_validation_stats['high_score']['total']
            }
        if news_validation_stats['low_score']['total'] > 0:
            results['_phase_metrics']['news_validation_performance']['low_score'] = {
                'win_rate': (news_validation_stats['low_score']['winners'] / news_validation_stats['low_score']['total'] * 100),
                'avg_return': statistics.mean(news_validation_stats['low_score']['returns']),
                'count': news_validation_stats['low_score']['total']
            }
        results['_phase_metrics']['news_validation_performance']['exit_rate'] = (
            (news_validation_stats['exits_triggered'] / news_validation_stats['total_trades'] * 100)
            if news_validation_stats['total_trades'] > 0 else 0
        )

        # Relative strength performance
        if rs_stats['strong_rs']['total'] > 0:
            results['_phase_metrics']['relative_strength_performance']['strong_rs'] = {
                'win_rate': (rs_stats['strong_rs']['winners'] / rs_stats['strong_rs']['total'] * 100),
                'avg_return': statistics.mean(rs_stats['strong_rs']['returns']),
                'count': rs_stats['strong_rs']['total']
            }
        if rs_stats['weak_rs']['total'] > 0:
            results['_phase_metrics']['relative_strength_performance']['weak_rs'] = {
                'win_rate': (rs_stats['weak_rs']['winners'] / rs_stats['weak_rs']['total'] * 100),
                'avg_return': statistics.mean(rs_stats['weak_rs']['returns']),
                'count': rs_stats['weak_rs']['total']
            }

        return results
    
    def calculate_optimal_parameters(self, trades):
        """Calculate optimal stop loss and profit targets"""
        
        if not trades:
            return None
        
        returns = [float(t.get('Return_Percent', 0)) for t in trades if t.get('Return_Percent')]
        
        if not returns:
            return None
        
        winners = [r for r in returns if r > 0]
        losers = [r for r in returns if r < 0]
        
        if not winners or not losers:
            return None
        
        # Calculate averages
        avg_winner = statistics.mean(winners)
        median_winner = statistics.median(winners)
        avg_loser = statistics.mean(losers)
        median_loser = statistics.median(losers)
        
        # Calculate standard deviations
        std_winner = statistics.stdev(winners) if len(winners) > 1 else 0
        std_loser = statistics.stdev(losers) if len(losers) > 1 else 0
        
        # Optimal stop: median loser + 1 std (more conservative)
        optimal_stop = abs(median_loser) + (std_loser * 0.5)
        
        # Optimal target: median winner (realistic expectation)
        optimal_target = median_winner
        
        # Risk/reward ratio
        risk_reward = optimal_target / optimal_stop if optimal_stop > 0 else 0
        
        return {
            'optimal_stop_loss': round(min(optimal_stop, 10), 1),  # Cap at -10%
            'optimal_profit_target': round(optimal_target, 1),
            'avg_winner': round(avg_winner, 1),
            'median_winner': round(median_winner, 1),
            'avg_loser': round(avg_loser, 1),
            'median_loser': round(median_loser, 1),
            'risk_reward_ratio': round(risk_reward, 2),
            'recommendation': 'Adjust stops/targets based on data' if len(trades) > 20 else 'Need more data'
        }
    
    def analyze_entry_timing(self, trades):
        """Analyze if entry timing affects outcomes"""
        
        # This is a placeholder for more sophisticated timing analysis
        # Could analyze: day of week, time of day, days after catalyst, etc.
        
        day_performance = defaultdict(lambda: {'total': 0, 'winners': 0})
        
        for trade in trades:
            try:
                entry_date = datetime.strptime(trade.get('Entry_Date', ''), '%Y-%m-%d')
                day_of_week = entry_date.strftime('%A')
                return_pct = float(trade.get('Return_Percent', 0))
                
                day_performance[day_of_week]['total'] += 1
                if return_pct > 0:
                    day_performance[day_of_week]['winners'] += 1
            except:
                continue
        
        # Calculate win rates by day
        day_results = {}
        for day, stats in day_performance.items():
            if stats['total'] > 0:
                day_results[day] = {
                    'win_rate': (stats['winners'] / stats['total']) * 100,
                    'total_trades': stats['total']
                }
        
        return day_results
    
    def update_catalyst_performance_csv(self, catalyst_performance):
        """Update catalyst_performance.csv with latest data"""
        
        with open(self.catalyst_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Catalyst_Type', 'Total_Trades', 'Winners', 'Losers',
                'Win_Rate_Percent', 'Avg_Return_Winners_Percent',
                'Avg_Return_Losers_Percent', 'Net_Avg_Return_Percent',
                'Best_Trade_Percent', 'Worst_Trade_Percent',
                'Avg_Hold_Days', 'Optimal_Exit_Day', 'Sample_Size_Confidence'
            ])
            
            for catalyst, stats in catalyst_performance.items():
                confidence = 'High' if stats['total_trades'] >= 25 else 'Medium' if stats['total_trades'] >= 10 else 'Low'
                
                writer.writerow([
                    catalyst,
                    stats['total_trades'],
                    stats['winners'],
                    stats['losers'],
                    round(stats['win_rate'], 2),
                    round(stats['avg_return'], 2),
                    round(stats['avg_return'], 2),  # Simplified
                    round(stats['avg_return'], 2),
                    round(stats['best_trade'], 2),
                    round(stats['worst_trade'], 2),
                    round(stats['avg_hold_days'], 1),
                    stats['optimal_exit_day'],
                    confidence
                ])
        
        print(f"   ✓ Updated catalyst_performance.csv")
    
    def generate_weekly_insights(self, catalyst_perf, optimal_params, day_analysis):
        """Generate comprehensive weekly insights (PHASE 5 ENHANCED)"""

        insights = []
        insights.append(f"\n\n{'='*80}\n")
        insights.append(f"# WEEKLY LEARNING UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        # Top performers
        insights.append("## 🏆 TOP PERFORMING CATALYSTS\n\n")
        sorted_catalysts = sorted(
            [(k, v) for k, v in catalyst_perf.items() if k != '_phase_metrics'],
            key=lambda x: x[1]['win_rate'],
            reverse=True
        )

        for catalyst, stats in sorted_catalysts[:3]:
            if stats['total_trades'] >= 5:
                insights.append(f"- **{catalyst}**: {stats['win_rate']:.1f}% win rate over {stats['total_trades']} trades\n")
                insights.append(f"  - Avg hold: {stats['avg_hold_days']:.1f} days (optimal exit: day {stats['optimal_exit_day']})\n")
                insights.append(f"  - Best trade: +{stats['best_trade']:.1f}%, Worst: {stats['worst_trade']:.1f}%\n")

        # Worst performers
        insights.append("\n## ⚠️ UNDERPERFORMING CATALYSTS\n\n")
        for catalyst, stats in reversed(sorted_catalysts[-3:]):
            if stats['total_trades'] >= 5:
                insights.append(f"- **{catalyst}**: {stats['win_rate']:.1f}% win rate over {stats['total_trades']} trades\n")

        # PHASE 5: Add new performance dimensions
        if '_phase_metrics' in catalyst_perf:
            phase_metrics = catalyst_perf['_phase_metrics']

            insights.append("\n## 📈 PHASE 1-4 PERFORMANCE (All-Time)\n\n")

            # Tier performance
            if phase_metrics['tier_performance']:
                insights.append("**Catalyst Tier Performance:**\n")
                for tier, stats in sorted(phase_metrics['tier_performance'].items()):
                    insights.append(
                        f"- {tier}: {stats['win_rate']:.1f}% win rate, "
                        f"{stats['avg_return']:.2f}% avg, "
                        f"{stats['avg_hold']:.1f} day hold "
                        f"({stats['count']} trades)\n"
                    )
                insights.append("\n")

            # Conviction performance
            if phase_metrics['conviction_performance']:
                insights.append("**Conviction Performance:**\n")
                for conv, stats in sorted(phase_metrics['conviction_performance'].items(), reverse=True):
                    insights.append(
                        f"- {conv}: {stats['win_rate']:.1f}% win rate, "
                        f"{stats['avg_return']:.2f}% avg, "
                        f"{stats['avg_hold']:.1f} day hold "
                        f"({stats['count']} trades)\n"
                    )
                insights.append("\n")

            # VIX regime performance
            if phase_metrics['vix_regime_performance']:
                insights.append("**VIX Regime Performance:**\n")
                for regime, stats in sorted(phase_metrics['vix_regime_performance'].items()):
                    insights.append(
                        f"- {regime}: {stats['win_rate']:.1f}% win rate, "
                        f"{stats['avg_return']:.2f}% avg ({stats['count']} trades)\n"
                    )
                insights.append("\n")

            # News validation performance
            if phase_metrics['news_validation_performance']:
                insights.append("**News Validation Performance:**\n")
                news_perf = phase_metrics['news_validation_performance']
                if 'high_score' in news_perf:
                    insights.append(
                        f"- High Score (≥10): {news_perf['high_score']['win_rate']:.1f}% win rate, "
                        f"{news_perf['high_score']['avg_return']:.2f}% avg ({news_perf['high_score']['count']} trades)\n"
                    )
                if 'low_score' in news_perf:
                    insights.append(
                        f"- Low Score (<10): {news_perf['low_score']['win_rate']:.1f}% win rate, "
                        f"{news_perf['low_score']['avg_return']:.2f}% avg ({news_perf['low_score']['count']} trades)\n"
                    )
                insights.append(f"- News Exit Rate: {news_perf['exit_rate']:.1f}%\n\n")

            # Relative strength performance
            if phase_metrics['relative_strength_performance']:
                insights.append("**Relative Strength Performance:**\n")
                rs_perf = phase_metrics['relative_strength_performance']
                if 'strong_rs' in rs_perf:
                    insights.append(
                        f"- Higher RS (≥3%): {rs_perf['strong_rs']['win_rate']:.1f}% win rate, "
                        f"{rs_perf['strong_rs']['avg_return']:.2f}% avg ({rs_perf['strong_rs']['count']} trades)\n"
                    )
                if 'weak_rs' in rs_perf:
                    insights.append(
                        f"- Lower RS (<3%): {rs_perf['weak_rs']['win_rate']:.1f}% win rate, "
                        f"{rs_perf['weak_rs']['avg_return']:.2f}% avg ({rs_perf['weak_rs']['count']} trades)\n"
                    )
                insights.append("\n")

        # Optimal parameters
        if optimal_params:
            insights.append("## 📊 OPTIMAL PARAMETERS (DATA-DRIVEN)\n\n")
            insights.append(f"- **Optimal Stop Loss**: -{optimal_params['optimal_stop_loss']:.1f}%\n")
            insights.append(f"- **Optimal Profit Target**: +{optimal_params['optimal_profit_target']:.1f}%\n")
            insights.append(f"- **Risk/Reward Ratio**: {optimal_params['risk_reward_ratio']:.2f}:1\n")
            insights.append(f"- **Median Winner**: +{optimal_params['median_winner']:.1f}%\n")
            insights.append(f"- **Median Loser**: {optimal_params['median_loser']:.1f}%\n")
            insights.append(f"- **Recommendation**: {optimal_params['recommendation']}\n")

        # Entry timing
        if day_analysis:
            insights.append("\n## 📅 ENTRY TIMING ANALYSIS\n\n")
            sorted_days = sorted(day_analysis.items(), key=lambda x: x[1]['win_rate'], reverse=True)
            for day, stats in sorted_days:
                if stats['total_trades'] >= 3:
                    insights.append(f"- **{day}**: {stats['win_rate']:.1f}% win rate ({stats['total_trades']} trades)\n")

        insights.append(f"\n*Auto-generated by Weekly Learning Engine (Phase 5 Enhanced)*\n")

        return ''.join(insights)
    
    def append_to_lessons_learned(self, insights):
        """Append insights to lessons_learned.md"""
        
        with open(self.lessons_file, 'a') as f:
            f.write(insights)
        
        print(f"   ✓ Appended weekly insights to lessons_learned.md")
    
    def run_learning_cycle(self):
        """Execute weekly learning cycle"""
        
        print("\n" + "="*60)
        print("WEEKLY LEARNING ENGINE - STRATEGIC ANALYSIS")
        print("="*60 + "\n")
        
        # Load trades
        print("1. Loading completed trades...")
        trades = self.load_completed_trades()
        
        if len(trades) < 10:
            print(f"   ⚠ Only {len(trades)} trades completed")
            print("   Need at least 10 trades for weekly learning")
            print("   Skipping learning cycle\n")
            return
        
        print(f"   ✓ Loaded {len(trades)} completed trades\n")
        
        # Deep catalyst analysis
        print("2. Performing deep catalyst analysis...")
        catalyst_perf = self.analyze_catalyst_performance(trades)
        print(f"   ✓ Analyzed {len(catalyst_perf)} catalyst types\n")
        
        # Calculate optimal parameters
        print("3. Calculating optimal stop/target parameters...")
        optimal_params = self.calculate_optimal_parameters(trades)
        if optimal_params:
            print(f"   ✓ Optimal stop: -{optimal_params['optimal_stop_loss']:.1f}%, Target: +{optimal_params['optimal_profit_target']:.1f}%\n")
        else:
            print("   ⚠ Not enough data for parameter optimization\n")
        
        # Analyze entry timing
        print("4. Analyzing entry timing patterns...")
        day_analysis = self.analyze_entry_timing(trades)
        print(f"   ✓ Analyzed performance by day of week\n")
        
        # Update CSV
        print("5. Updating catalyst_performance.csv...")
        self.update_catalyst_performance_csv(catalyst_perf)
        print()
        
        # Generate insights
        print("6. Generating weekly insights...")
        insights = self.generate_weekly_insights(catalyst_perf, optimal_params, day_analysis)
        self.append_to_lessons_learned(insights)
        print()
        
        # Summary
        print("="*60)
        print("WEEKLY LEARNING COMPLETE")
        print("="*60)
        print(f"\nTotal trades analyzed: {len(trades)}")
        print(f"Catalyst types tracked: {len(catalyst_perf)}")
        
        # Show top performer
        if catalyst_perf:
            top = max(catalyst_perf.items(), key=lambda x: x[1]['win_rate'])
            print(f"\n🏆 Best catalyst: {top[0]} ({top[1]['win_rate']:.1f}% win rate)")
        
        print("\n" + "="*60 + "\n")

def main():
    """Main execution"""
    engine = WeeklyLearning()
    engine.run_learning_cycle()

if __name__ == '__main__':
    main()