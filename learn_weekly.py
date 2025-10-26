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
        """Deep analysis by catalyst type"""
        
        catalyst_stats = defaultdict(lambda: {
            'total': 0,
            'winners': 0,
            'losers': 0,
            'returns': [],
            'hold_times': [],
            'winner_hold_times': [],
            'loser_hold_times': []
        })
        
        for trade in trades:
            catalyst = trade.get('Catalyst_Type', 'Unknown')
            return_pct = float(trade.get('Return_Percent', 0))
            hold_days = int(trade.get('Hold_Days', 0))
            
            stats = catalyst_stats[catalyst]
            stats['total'] += 1
            stats['returns'].append(return_pct)
            stats['hold_times'].append(hold_days)
            
            if return_pct > 0:
                stats['winners'] += 1
                stats['winner_hold_times'].append(hold_days)
            else:
                stats['losers'] += 1
                stats['loser_hold_times'].append(hold_days)
        
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
        """Generate comprehensive weekly insights"""
        
        insights = []
        insights.append(f"\n\n{'='*80}\n")
        insights.append(f"# WEEKLY LEARNING UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        # Top performers
        insights.append("## 🏆 TOP PERFORMING CATALYSTS\n\n")
        sorted_catalysts = sorted(catalyst_perf.items(), key=lambda x: x[1]['win_rate'], reverse=True)
        
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
        
        # Optimal parameters
        if optimal_params:
            insights.append("\n## 📊 OPTIMAL PARAMETERS (DATA-DRIVEN)\n\n")
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
        
        insights.append(f"\n*Auto-generated by Weekly Learning Engine*\n")
        
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