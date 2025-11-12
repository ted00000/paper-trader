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
        """Calculate comprehensive monthly statistics (PHASE 5 ENHANCED)"""

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

        # PHASE 5: Track new dimensions
        tier_stats = defaultdict(lambda: {'total': 0, 'winners': 0, 'returns': []})
        conviction_stats = defaultdict(lambda: {'total': 0, 'winners': 0, 'returns': []})
        vix_regime_stats = defaultdict(lambda: {'total': 0, 'winners': 0, 'returns': []})
        news_stats = {
            'high_score': {'total': 0, 'winners': 0, 'returns': []},
            'low_score': {'total': 0, 'winners': 0, 'returns': []},
            'exits_triggered': 0
        }
        rs_stats = {
            'strong_rs': {'total': 0, 'winners': 0, 'returns': []},
            'weak_rs': {'total': 0, 'winners': 0, 'returns': []}
        }

        # PHASE 5.6: Technical indicator tracking
        technical_stats = {
            'adx_high': {'total': 0, 'winners': 0, 'returns': []},  # ADX >25
            'adx_moderate': {'total': 0, 'winners': 0, 'returns': []},  # ADX 20-25
            'volume_high': {'total': 0, 'winners': 0, 'returns': []},  # Volume >2x
            'volume_moderate': {'total': 0, 'winners': 0, 'returns': []},  # Volume 1.5-2x
        }

        for trade in recent_trades:
            return_pct = float(trade.get('Return_Percent', 0))
            is_winner = return_pct > 0

            # Tier tracking
            tier = trade.get('Catalyst_Tier', 'Unknown')
            tier_stats[tier]['total'] += 1
            tier_stats[tier]['returns'].append(return_pct)
            if is_winner:
                tier_stats[tier]['winners'] += 1

            # Conviction tracking
            conviction = trade.get('Conviction_Level', 'MEDIUM')
            conviction_stats[conviction]['total'] += 1
            conviction_stats[conviction]['returns'].append(return_pct)
            if is_winner:
                conviction_stats[conviction]['winners'] += 1

            # VIX regime tracking
            vix_regime = trade.get('Market_Regime', 'UNKNOWN')
            vix_regime_stats[vix_regime]['total'] += 1
            vix_regime_stats[vix_regime]['returns'].append(return_pct)
            if is_winner:
                vix_regime_stats[vix_regime]['winners'] += 1

            # News validation tracking
            news_score = float(trade.get('News_Validation_Score', 0))
            if news_score >= 10:
                news_stats['high_score']['total'] += 1
                news_stats['high_score']['returns'].append(return_pct)
                if is_winner:
                    news_stats['high_score']['winners'] += 1
            else:
                news_stats['low_score']['total'] += 1
                news_stats['low_score']['returns'].append(return_pct)
                if is_winner:
                    news_stats['low_score']['winners'] += 1

            if trade.get('News_Exit_Triggered', '').lower() in ['true', '1', 'yes']:
                news_stats['exits_triggered'] += 1

            # Relative strength tracking
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

            # Technical indicator tracking (Phase 5.6)
            try:
                adx_value = float(trade.get('Technical_ADX', 0))
                volume_ratio = float(trade.get('Technical_Volume_Ratio', 0))

                # ADX performance
                if adx_value > 25:
                    technical_stats['adx_high']['total'] += 1
                    technical_stats['adx_high']['returns'].append(return_pct)
                    if is_winner:
                        technical_stats['adx_high']['winners'] += 1
                elif adx_value >= 20:
                    technical_stats['adx_moderate']['total'] += 1
                    technical_stats['adx_moderate']['returns'].append(return_pct)
                    if is_winner:
                        technical_stats['adx_moderate']['winners'] += 1

                # Volume performance
                if volume_ratio > 2.0:
                    technical_stats['volume_high']['total'] += 1
                    technical_stats['volume_high']['returns'].append(return_pct)
                    if is_winner:
                        technical_stats['volume_high']['winners'] += 1
                elif volume_ratio >= 1.5:
                    technical_stats['volume_moderate']['total'] += 1
                    technical_stats['volume_moderate']['returns'].append(return_pct)
                    if is_winner:
                        technical_stats['volume_moderate']['winners'] += 1
            except:
                pass  # Skip if technical data missing (pre-v5.6 trades)

        # Build phase metrics
        phase_metrics = {
            'tier_performance': {},
            'conviction_performance': {},
            'vix_regime_performance': {},
            'news_validation_performance': {},
            'relative_strength_performance': {},
            'technical_indicator_performance': {}  # Phase 5.6
        }

        # Tier performance
        for tier, stats in tier_stats.items():
            if stats['total'] > 0:
                phase_metrics['tier_performance'][tier] = {
                    'win_rate': (stats['winners'] / stats['total'] * 100),
                    'avg_return': statistics.mean(stats['returns']),
                    'count': stats['total']
                }

        # Conviction performance
        for conv, stats in conviction_stats.items():
            if stats['total'] > 0:
                phase_metrics['conviction_performance'][conv] = {
                    'win_rate': (stats['winners'] / stats['total'] * 100),
                    'avg_return': statistics.mean(stats['returns']),
                    'count': stats['total']
                }

        # VIX regime performance
        for regime, stats in vix_regime_stats.items():
            if stats['total'] > 0:
                phase_metrics['vix_regime_performance'][regime] = {
                    'win_rate': (stats['winners'] / stats['total'] * 100),
                    'avg_return': statistics.mean(stats['returns']),
                    'count': stats['total']
                }

        # News validation performance
        if news_stats['high_score']['total'] > 0:
            phase_metrics['news_validation_performance']['high_score'] = {
                'win_rate': (news_stats['high_score']['winners'] / news_stats['high_score']['total'] * 100),
                'avg_return': statistics.mean(news_stats['high_score']['returns']),
                'count': news_stats['high_score']['total']
            }
        if news_stats['low_score']['total'] > 0:
            phase_metrics['news_validation_performance']['low_score'] = {
                'win_rate': (news_stats['low_score']['winners'] / news_stats['low_score']['total'] * 100),
                'avg_return': statistics.mean(news_stats['low_score']['returns']),
                'count': news_stats['low_score']['total']
            }
        phase_metrics['news_validation_performance']['exit_rate'] = (
            (news_stats['exits_triggered'] / total_trades * 100) if total_trades > 0 else 0
        )

        # Relative strength performance
        if rs_stats['strong_rs']['total'] > 0:
            phase_metrics['relative_strength_performance']['strong_rs'] = {
                'win_rate': (rs_stats['strong_rs']['winners'] / rs_stats['strong_rs']['total'] * 100),
                'avg_return': statistics.mean(rs_stats['strong_rs']['returns']),
                'count': rs_stats['strong_rs']['total']
            }
        if rs_stats['weak_rs']['total'] > 0:
            phase_metrics['relative_strength_performance']['weak_rs'] = {
                'win_rate': (rs_stats['weak_rs']['winners'] / rs_stats['weak_rs']['total'] * 100),
                'avg_return': statistics.mean(rs_stats['weak_rs']['returns']),
                'count': rs_stats['weak_rs']['total']
            }

        # Technical indicator performance (Phase 5.6)
        if technical_stats['adx_high']['total'] > 0:
            phase_metrics['technical_indicator_performance']['adx_high'] = {
                'win_rate': (technical_stats['adx_high']['winners'] / technical_stats['adx_high']['total'] * 100),
                'avg_return': statistics.mean(technical_stats['adx_high']['returns']),
                'count': technical_stats['adx_high']['total']
            }
        if technical_stats['adx_moderate']['total'] > 0:
            phase_metrics['technical_indicator_performance']['adx_moderate'] = {
                'win_rate': (technical_stats['adx_moderate']['winners'] / technical_stats['adx_moderate']['total'] * 100),
                'avg_return': statistics.mean(technical_stats['adx_moderate']['returns']),
                'count': technical_stats['adx_moderate']['total']
            }
        if technical_stats['volume_high']['total'] > 0:
            phase_metrics['technical_indicator_performance']['volume_high'] = {
                'win_rate': (technical_stats['volume_high']['winners'] / technical_stats['volume_high']['total'] * 100),
                'avg_return': statistics.mean(technical_stats['volume_high']['returns']),
                'count': technical_stats['volume_high']['total']
            }
        if technical_stats['volume_moderate']['total'] > 0:
            phase_metrics['technical_indicator_performance']['volume_moderate'] = {
                'win_rate': (technical_stats['volume_moderate']['winners'] / technical_stats['volume_moderate']['total'] * 100),
                'avg_return': statistics.mean(technical_stats['volume_moderate']['returns']),
                'count': technical_stats['volume_moderate']['total']
            }

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
            'period': 'Last 30 days' if len(recent_trades) < len(trades) else 'All time',
            '_phase_metrics': phase_metrics
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
        """Generate comprehensive monthly report (PHASE 5 ENHANCED)"""

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

        # PHASE 5: Add new performance dimensions
        if monthly_stats and '_phase_metrics' in monthly_stats:
            phase_metrics = monthly_stats['_phase_metrics']

            report.append("\n## 📈 PHASE 1-4 PERFORMANCE (Last 30 Days)\n\n")

            # Tier performance
            if phase_metrics['tier_performance']:
                report.append("**Catalyst Tier Performance:**\n")
                for tier, stats in sorted(phase_metrics['tier_performance'].items()):
                    report.append(
                        f"- {tier}: {stats['win_rate']:.1f}% win rate, "
                        f"{stats['avg_return']:.2f}% avg ({stats['count']} trades)\n"
                    )
                report.append("\n")

            # Conviction performance
            if phase_metrics['conviction_performance']:
                report.append("**Conviction Performance:**\n")
                for conv, stats in sorted(phase_metrics['conviction_performance'].items(), reverse=True):
                    report.append(
                        f"- {conv}: {stats['win_rate']:.1f}% win rate, "
                        f"{stats['avg_return']:.2f}% avg ({stats['count']} trades)\n"
                    )
                report.append("\n")

            # VIX regime performance
            if phase_metrics['vix_regime_performance']:
                report.append("**VIX Regime Performance:**\n")
                for regime_type, stats in sorted(phase_metrics['vix_regime_performance'].items()):
                    report.append(
                        f"- {regime_type}: {stats['win_rate']:.1f}% win rate, "
                        f"{stats['avg_return']:.2f}% avg ({stats['count']} trades)\n"
                    )
                report.append("\n")

            # News validation performance
            if phase_metrics['news_validation_performance']:
                report.append("**News Validation Performance:**\n")
                news_perf = phase_metrics['news_validation_performance']
                if 'high_score' in news_perf:
                    report.append(
                        f"- High Score (≥10): {news_perf['high_score']['win_rate']:.1f}% win rate, "
                        f"{news_perf['high_score']['avg_return']:.2f}% avg ({news_perf['high_score']['count']} trades)\n"
                    )
                if 'low_score' in news_perf:
                    report.append(
                        f"- Low Score (<10): {news_perf['low_score']['win_rate']:.1f}% win rate, "
                        f"{news_perf['low_score']['avg_return']:.2f}% avg ({news_perf['low_score']['count']} trades)\n"
                    )
                report.append(f"- News Exit Rate: {news_perf['exit_rate']:.1f}%\n\n")

            # Relative strength performance
            if phase_metrics['relative_strength_performance']:
                report.append("**Relative Strength Performance:**\n")
                rs_perf = phase_metrics['relative_strength_performance']
                if 'strong_rs' in rs_perf:
                    report.append(
                        f"- Strong RS (≥3%): {rs_perf['strong_rs']['win_rate']:.1f}% win rate, "
                        f"{rs_perf['strong_rs']['avg_return']:.2f}% avg ({rs_perf['strong_rs']['count']} trades)\n"
                    )
                if 'weak_rs' in rs_perf:
                    report.append(
                        f"- Weak RS (<3%): {rs_perf['weak_rs']['win_rate']:.1f}% win rate, "
                        f"{rs_perf['weak_rs']['avg_return']:.2f}% avg ({rs_perf['weak_rs']['count']} trades)\n"
                    )
                report.append("\n")

        # Strategy Effectiveness
        report.append("## 🎯 STRATEGY EFFECTIVENESS\n\n")
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

        report.append(f"\n*Auto-generated by Monthly Learning Engine (Phase 5 Enhanced)*\n")

        return ''.join(report)
    
    def append_to_lessons_learned(self, report):
        """Append monthly report to lessons_learned.md"""

        with open(self.lessons_file, 'a') as f:
            f.write(report)

        print(f"   ✓ Appended monthly report to lessons_learned.md")

    def generate_parameter_recommendations(self, trades):
        """Analyze parameter effectiveness and generate recommendations for dashboard"""

        if len(trades) < 30:
            return []  # Need sufficient data

        recommendations = []

        # Analyze VIX threshold effectiveness
        vix_high_trades = [t for t in trades if float(t.get('VIX_at_Entry', 25)) > 25]
        if len(vix_high_trades) >= 15:
            win_rate = (sum(1 for t in vix_high_trades if float(t['Return_Percent']) > 0) / len(vix_high_trades)) * 100

            if win_rate < 40:
                recommendations.append({
                    'id': f"param_vix_{datetime.now().strftime('%Y%m%d')}",
                    'type': 'PARAMETER_ADJUSTMENT',
                    'parameter': 'VIX_THRESHOLD',
                    'current_value': 25,
                    'suggested_value': 22,
                    'reasoning': f'VIX >25 showing {win_rate:.1f}% win rate over {len(vix_high_trades)} trades. Lower threshold to avoid extreme volatility.',
                    'confidence': 'HIGH' if len(vix_high_trades) >= 25 else 'MEDIUM',
                    'sample_size': len(vix_high_trades),
                    'created': datetime.now().isoformat(),
                    'status': 'PENDING_REVIEW'
                })

        # Analyze RS threshold effectiveness
        rs_weak_trades = [t for t in trades if 0 < float(t.get('Relative_Strength', 5)) < 5]
        rs_strong_trades = [t for t in trades if float(t.get('Relative_Strength', 0)) >= 5]

        if len(rs_weak_trades) >= 10 and len(rs_strong_trades) >= 10:
            weak_wr = (sum(1 for t in rs_weak_trades if float(t['Return_Percent']) > 0) / len(rs_weak_trades)) * 100
            strong_wr = (sum(1 for t in rs_strong_trades if float(t['Return_Percent']) > 0) / len(rs_strong_trades)) * 100

            if strong_wr > weak_wr + 15:  # Strong RS significantly better
                recommendations.append({
                    'id': f"param_rs_{datetime.now().strftime('%Y%m%d')}",
                    'type': 'PARAMETER_ADJUSTMENT',
                    'parameter': 'RS_THRESHOLD',
                    'current_value': 3.0,
                    'suggested_value': 5.0,
                    'reasoning': f'RS ≥5%: {strong_wr:.1f}% win rate vs RS 3-5%: {weak_wr:.1f}% win rate. Raise threshold for better sector leaders.',
                    'confidence': 'HIGH',
                    'sample_size': len(rs_weak_trades) + len(rs_strong_trades),
                    'created': datetime.now().isoformat(),
                    'status': 'PENDING_REVIEW'
                })

        return recommendations

    def save_recommendations_to_dashboard(self, recommendations):
        """Save parameter recommendations for admin dashboard review"""

        dashboard_data_dir = PROJECT_DIR / 'dashboard_data'
        dashboard_data_dir.mkdir(exist_ok=True)

        actions_file = dashboard_data_dir / 'pending_actions.json'

        # Load existing actions
        existing_actions = []
        if actions_file.exists():
            try:
                with open(actions_file) as f:
                    existing_actions = json.load(f)
            except:
                existing_actions = []

        # Add new recommendations (avoid duplicates)
        existing_ids = {a['id'] for a in existing_actions}
        for rec in recommendations:
            if rec['id'] not in existing_ids:
                existing_actions.append(rec)

        # Save
        with open(actions_file, 'w') as f:
            json.dump(existing_actions, f, indent=2)

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

        # Generate parameter recommendations for dashboard
        print("7. Analyzing parameter effectiveness...")
        param_recommendations = self.generate_parameter_recommendations(trades)
        self.save_recommendations_to_dashboard(param_recommendations)
        print(f"   ✓ Generated {len(param_recommendations)} parameter recommendations")
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