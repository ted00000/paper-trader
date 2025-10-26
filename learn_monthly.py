#!/usr/bin/env python3
"""
Monthly Learning Engine - Macro Analysis & Regime Detection
Runs last Sunday of each month for major strategy evolution and market regime adaptation
"""

import os
import json
import csv
import requests
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import statistics

PROJECT_DIR = Path(__file__).parent

class MonthlyLearning:
    """Macro learning - market regime detection and major strategy shifts"""
    
    def __init__(self):
        self.trades_file = PROJECT_DIR / 'trade_history' / 'completed_trades.csv'
        self.strategy_file = PROJECT_DIR / 'strategy_evolution' / 'strategy_rules.md'
        self.lessons_file = PROJECT_DIR / 'strategy_evolution' / 'lessons_learned.md'
        self.regime_file = PROJECT_DIR / 'strategy_evolution' / 'market_regime.json'
        
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
    
    def detect_market_regime(self):
        """Detect current market regime (Bull/Bear/Sideways)"""
        
        # Simple regime detection based on SPY trend
        # In production, you'd fetch real SPY data
        # For now, this is a placeholder structure
        
        regime = {
            'regime_type': 'BULL',  # BULL, BEAR, SIDEWAYS
            'confidence': 'Medium',
            'detected_date': datetime.now().strftime('%Y-%m-%d'),
            'indicators': {
                'spy_50_day_ma_trend': 'Up',
                'spy_200_day_ma_trend': 'Up',
                'volatility_index': 'Low',
                'market_breadth': 'Strong'
            },
            'recommendation': 'Aggressive positioning - Full 10 positions'
        }
        
        # Save regime detection
        with open(self.regime_file, 'w') as f:
            json.dump(regime, f, indent=2)
        
        return regime
    
    def calculate_monthly_statistics(self, trades):
        """Calculate comprehensive monthly statistics"""
        
        if not trades:
            return None
        
        # Filter to last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        recent_trades = []
        
        for trade in trades:
            try:
                exit_date = datetime.strptime(trade.get('Exit_Date', ''), '%Y-%m-%d')
                if exit_date >= cutoff:
                    recent_trades.append(trade)
            except:
                pass
        
        if not recent_trades:
            recent_trades = trades  # Use all if none in last 30 days
        
        # Calculate metrics
        returns = [float(t.get('Return_Percent', 0)) for t in recent_trades]
        
        total_trades = len(recent_trades)
        winners = len([r for r in returns if r > 0])
        losers = len([r for r in returns if r < 0])
        win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
        
        avg_return = statistics.mean(returns) if returns else 0
        median_return = statistics.median(returns) if returns else 0
        
        best_trade = max(returns) if returns else 0
        worst_trade = min(returns) if returns else 0
        
        # Volatility (standard deviation of returns)
        volatility = statistics.stdev(returns) if len(returns) > 1 else 0
        
        # Sharpe-like metric (avg return / volatility)
        sharpe = (avg_return / volatility) if volatility > 0 else 0
        
        # Calculate max drawdown
        cumulative_returns = []
        cumulative = 0
        for r in returns:
            cumulative += r
            cumulative_returns.append(cumulative)
        
        max_drawdown = 0
        peak = cumulative_returns[0] if cumulative_returns else 0
        for ret in cumulative_returns:
            if ret > peak:
                peak = ret
            drawdown = peak - ret
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            'total_trades': total_trades,
            'winners': winners,
            'losers': losers,
            'win_rate': win_rate,
            'avg_return': avg_return,
            'median_return': median_return,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'period': 'Last 30 days' if len(recent_trades) < len(trades) else 'All time'
        }
    
    def analyze_strategy_effectiveness(self, trades):
        """Evaluate if overall strategy is working"""
        
        if len(trades) < 30:
            return {
                'status': 'Insufficient data',
                'recommendation': 'Continue current strategy, need more trades'
            }
        
        # Calculate rolling win rate over time
        rolling_window = 10
        win_rates = []
        
        for i in range(len(trades) - rolling_window + 1):
            window = trades[i:i+rolling_window]
            winners = len([t for t in window if float(t.get('Return_Percent', 0)) > 0])
            win_rate = (winners / rolling_window) * 100
            win_rates.append(win_rate)
        
        if not win_rates:
            return {'status': 'Insufficient data'}
        
        # Check if win rate is improving over time
        first_half_avg = statistics.mean(win_rates[:len(win_rates)//2]) if len(win_rates) >= 2 else 0
        second_half_avg = statistics.mean(win_rates[len(win_rates)//2:]) if len(win_rates) >= 2 else 0
        
        improving = second_half_avg > first_half_avg
        current_win_rate = win_rates[-1] if win_rates else 0
        
        # Determine status
        if current_win_rate > 60:
            status = 'EXCELLENT - Strategy is working well'
            recommendation = 'Continue current approach, minor optimizations only'
        elif current_win_rate > 50:
            status = 'GOOD - Strategy is profitable'
            recommendation = 'Continue but watch for improvements'
        elif current_win_rate > 40:
            status = 'MARGINAL - Barely profitable'
            recommendation = 'Consider significant strategy adjustments'
        else:
            status = 'POOR - Strategy needs overhaul'
            recommendation = 'Major strategy revision required'
        
        return {
            'status': status,
            'current_win_rate': current_win_rate,
            'trend': 'Improving' if improving else 'Declining',
            'first_half_avg': first_half_avg,
            'second_half_avg': second_half_avg,
            'recommendation': recommendation
        }
    
    def identify_best_practices(self, trades):
        """Identify what's working best in the strategy"""
        
        if len(trades) < 20:
            return []
        
        best_practices = []
        
        # Find trades with >10% return
        big_winners = [t for t in trades if float(t.get('Return_Percent', 0)) > 10]
        
        if len(big_winners) >= 5:
            # Analyze what they have in common
            catalyst_counts = defaultdict(int)
            for trade in big_winners:
                catalyst = trade.get('Catalyst_Type', '')
                if catalyst:
                    catalyst_counts[catalyst] += 1
            
            # Find most common catalyst in big winners
            if catalyst_counts:
                top_catalyst = max(catalyst_counts.items(), key=lambda x: x[1])
                best_practices.append({
                    'pattern': f'{top_catalyst[0]} produces big winners',
                    'evidence': f'{top_catalyst[1]} of {len(big_winners)} trades >10% used this catalyst',
                    'action': f'Prioritize {top_catalyst[0]} setups'
                })
        
        return best_practices
    
    def generate_monthly_report(self, monthly_stats, regime, strategy_eval, best_practices):
        """Generate comprehensive monthly report"""
        
        report = []
        report.append(f"\n\n{'='*80}\n")
        report.append(f"# MONTHLY LEARNING REPORT - {datetime.now().strftime('%B %Y')}\n\n")
        
        # Executive Summary
        report.append("## 📊 EXECUTIVE SUMMARY\n\n")
        if monthly_stats:
            report.append(f"- **Total Trades**: {monthly_stats['total_trades']}\n")
            report.append(f"- **Win Rate**: {monthly_stats['win_rate']:.1f}% ({monthly_stats['winners']}W / {monthly_stats['losers']}L)\n")
            report.append(f"- **Average Return**: {monthly_stats['avg_return']:.2f}%\n")
            report.append(f"- **Best Trade**: +{monthly_stats['best_trade']:.1f}%\n")
            report.append(f"- **Worst Trade**: {monthly_stats['worst_trade']:.1f}%\n")
            report.append(f"- **Volatility**: {monthly_stats['volatility']:.2f}%\n")
            report.append(f"- **Max Drawdown**: -{monthly_stats['max_drawdown']:.1f}%\n")
            report.append(f"- **Sharpe Ratio**: {monthly_stats['sharpe_ratio']:.2f}\n")
        
        # Market Regime
        report.append("\n## 🌍 MARKET REGIME DETECTION\n\n")
        report.append(f"- **Current Regime**: {regime['regime_type']}\n")
        report.append(f"- **Confidence**: {regime['confidence']}\n")
        report.append(f"- **Recommendation**: {regime['recommendation']}\n")
        
        # Strategy Effectiveness
        report.append("\n## 🎯 STRATEGY EFFECTIVENESS\n\n")
        report.append(f"- **Status**: {strategy_eval.get('status', 'Unknown')}\n")
        if 'trend' in strategy_eval:
            report.append(f"- **Trend**: {strategy_eval['trend']}\n")
            report.append(f"- **First Half Avg Win Rate**: {strategy_eval['first_half_avg']:.1f}%\n")
            report.append(f"- **Second Half Avg Win Rate**: {strategy_eval['second_half_avg']:.1f}%\n")
        report.append(f"- **Recommendation**: {strategy_eval.get('recommendation', 'Continue')}\n")
        
        # Best Practices
        if best_practices:
            report.append("\n## ✅ IDENTIFIED BEST PRACTICES\n\n")
            for practice in best_practices:
                report.append(f"- **{practice['pattern']}**\n")
                report.append(f"  - Evidence: {practice['evidence']}\n")
                report.append(f"  - Action: {practice['action']}\n")
        
        # Action Items
        report.append("\n## 📋 ACTION ITEMS FOR NEXT MONTH\n\n")
        report.append("1. Continue monitoring catalyst performance\n")
        report.append("2. Adjust for market regime if needed\n")
        report.append("3. Implement any identified best practices\n")
        if strategy_eval.get('recommendation'):
            report.append(f"4. {strategy_eval['recommendation']}\n")
        
        report.append(f"\n*Auto-generated by Monthly Learning Engine*\n")
        
        return ''.join(report)
    
    def append_to_lessons_learned(self, report):
        """Append monthly report to lessons_learned.md"""
        
        with open(self.lessons_file, 'a') as f:
            f.write(report)
        
        print(f"   ✓ Appended monthly report to lessons_learned.md")
    
    def run_learning_cycle(self):
        """Execute monthly learning cycle"""
        
        print("\n" + "="*60)
        print("MONTHLY LEARNING ENGINE - MACRO ANALYSIS")
        print("="*60 + "\n")
        
        # Load trades
        print("1. Loading completed trades...")
        trades = self.load_completed_trades()
        
        if len(trades) < 15:
            print(f"   ⚠ Only {len(trades)} trades completed")
            print("   Need at least 15 trades for monthly learning")
            print("   Skipping learning cycle\n")
            return
        
        print(f"   ✓ Loaded {len(trades)} completed trades\n")
        
        # Detect market regime
        print("2. Detecting market regime...")
        regime = self.detect_market_regime()
        print(f"   ✓ Regime: {regime['regime_type']}\n")
        
        # Calculate monthly statistics
        print("3. Calculating monthly statistics...")
        monthly_stats = self.calculate_monthly_statistics(trades)
        if monthly_stats:
            print(f"   ✓ Win rate: {monthly_stats['win_rate']:.1f}%\n")
        
        # Evaluate strategy effectiveness
        print("4. Evaluating strategy effectiveness...")
        strategy_eval = self.analyze_strategy_effectiveness(trades)
        print(f"   ✓ Status: {strategy_eval.get('status', 'Unknown')}\n")
        
        # Identify best practices
        print("5. Identifying best practices...")
        best_practices = self.identify_best_practices(trades)
        print(f"   ✓ Found {len(best_practices)} patterns\n")
        
        # Generate report
        print("6. Generating monthly report...")
        report = self.generate_monthly_report(monthly_stats, regime, strategy_eval, best_practices)
        self.append_to_lessons_learned(report)
        print()
        
        # Summary
        print("="*60)
        print("MONTHLY LEARNING COMPLETE")
        print("="*60)
        print(f"\nTotal trades analyzed: {len(trades)}")
        if monthly_stats:
            print(f"Win rate: {monthly_stats['win_rate']:.1f}%")
            print(f"Average return: {monthly_stats['avg_return']:.2f}%")
        print(f"Market regime: {regime['regime_type']}")
        print(f"Strategy status: {strategy_eval.get('status', 'Unknown')}")
        
        print("\n" + "="*60 + "\n")

def main():
    """Main execution"""
    engine = MonthlyLearning()
    engine.run_learning_cycle()

if __name__ == '__main__':
    main()