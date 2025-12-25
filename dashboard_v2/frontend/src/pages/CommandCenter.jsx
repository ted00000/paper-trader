import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  DollarSign,
  Target,
  Award,
  AlertTriangle,
  TrendingUp,
  Activity,
  Briefcase
} from 'lucide-react'
import axios from 'axios'

// Components
import OperationsStatus from '../components/OperationsStatus'
import EquityCurveChart from '../components/EquityCurveChart'
import ActivePositionsGrid from '../components/ActivePositionsGrid'
import PerformanceDonutChart from '../components/PerformanceDonutChart'

function CommandCenter() {
  const [overview, setOverview] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState(new Date())

  // Fetch overview data
  useEffect(() => {
    fetchOverview()
    const interval = setInterval(fetchOverview, 30000) // Update every 30s
    return () => clearInterval(interval)
  }, [])

  const fetchOverview = async () => {
    try {
      const response = await axios.get('/api/v2/overview')
      setOverview(response.data)
      setLastUpdate(new Date())
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch overview:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="shimmer w-32 h-32 rounded-full mx-auto mb-4"></div>
          <p className="text-tedbot-gray-500">Loading command center...</p>
        </div>
      </div>
    )
  }

  if (!overview) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="mx-auto text-warning" size={48} />
        <p className="mt-4 text-tedbot-gray-500">Failed to load dashboard data</p>
      </div>
    )
  }

  const { account, performance, positions } = overview

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Command Center</h2>
          <p className="text-tedbot-gray-500 mt-1">
            Real-time overview · Updated {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
        <button
          onClick={fetchOverview}
          className="px-4 py-2 bg-tedbot-gray-800 hover:bg-tedbot-gray-700 rounded-lg transition-colors"
        >
          Refresh Data
        </button>
      </div>

      {/* System Operations Status - Top Row */}
      <OperationsStatus />

      {/* Account Overview Hero */}
      <div className="glass rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Briefcase className="text-tedbot-accent" size={24} />
          <h2 className="text-xl font-bold">Account Overview</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h3 className="text-sm font-medium text-tedbot-gray-500 mb-2">Account Value</h3>
            <p className="text-3xl font-bold">${account.value.toFixed(2)}</p>
            <p className={`text-sm mt-1 ${account.total_return_pct >= 0 ? 'text-profit' : 'text-loss'}`}>
              {account.total_return_pct >= 0 ? '+' : ''}{account.total_return_pct.toFixed(2)}% ({account.total_return_usd >= 0 ? '+' : ''}${account.total_return_usd.toFixed(2)})
            </p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-tedbot-gray-500 mb-2">Active Positions</h3>
            <p className="text-3xl font-bold text-tedbot-accent">{positions.length}</p>
            <p className="text-sm text-tedbot-gray-600 mt-1">
              ${account.invested.toFixed(2)} deployed
            </p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-tedbot-gray-500 mb-2">Deployed Capital</h3>
            <p className="text-3xl font-bold text-profit">
              {((account.invested / account.value) * 100).toFixed(1)}%
            </p>
            <p className="text-sm text-tedbot-gray-600 mt-1">
              ${account.cash.toFixed(2)} cash available
            </p>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="glass rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <TrendingUp className="text-tedbot-accent" size={24} />
          <h2 className="text-xl font-bold">Performance Metrics</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <h3 className="text-sm font-semibold text-tedbot-gray-400 mb-2">YTD Return</h3>
            <p className={`text-2xl font-bold ${performance?.ytd_return >= 0 ? 'text-profit' : 'text-loss'}`}>
              {performance?.ytd_return >= 0 ? '+' : ''}{performance?.ytd_return?.toFixed(2) || '0.00'}%
            </p>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-tedbot-gray-400 mb-2">MTD Return</h3>
            <p className={`text-2xl font-bold ${performance?.mtd_return >= 0 ? 'text-profit' : 'text-loss'}`}>
              {performance?.mtd_return >= 0 ? '+' : ''}{performance?.mtd_return?.toFixed(2) || '0.00'}%
            </p>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-tedbot-gray-400 mb-2">Win Rate</h3>
            <p className={`text-2xl font-bold ${
              performance.win_rate >= 60 ? 'text-profit' :
              performance.win_rate >= 50 ? 'text-tedbot-accent' :
              'text-loss'
            }`}>
              {performance.win_rate}%
            </p>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-tedbot-gray-400 mb-2">Max Drawdown</h3>
            <p className={`text-2xl font-bold ${
              performance.max_drawdown < 10 ? 'text-profit' :
              performance.max_drawdown < 15 ? 'text-tedbot-accent' :
              'text-loss'
            }`}>
              {performance.max_drawdown.toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      {/* Performance Overview Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Donut Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-lg p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <Target className="text-tedbot-accent" size={24} />
            <h3 className="text-xl font-bold">Performance Breakdown</h3>
          </div>
          <PerformanceDonutChart performance={performance} />
        </motion.div>

        {/* Key Statistics */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-lg p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <Award className="text-tedbot-accent" size={24} />
            <h3 className="text-xl font-bold">Key Statistics</h3>
          </div>
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-medium text-tedbot-gray-500 mb-2">Sharpe Ratio</h4>
              <p className={`text-3xl font-bold ${
                performance.sharpe_ratio > 1.5 ? 'text-profit' :
                performance.sharpe_ratio > 1.0 ? 'text-tedbot-accent' :
                'text-tedbot-gray-400'
              }`}>
                {performance.sharpe_ratio.toFixed(2)}
              </p>
              <p className="text-xs text-tedbot-gray-600 mt-1">Risk-adjusted return</p>
            </div>
            <div>
              <h4 className="text-sm font-medium text-tedbot-gray-500 mb-2">Total Trades</h4>
              <p className="text-3xl font-bold text-tedbot-accent">
                {performance?.total_trades || 0}
              </p>
              <p className="text-xs text-tedbot-gray-600 mt-1">
                {performance.win_rate}% win rate
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Equity Curve - Full Width */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass rounded-lg p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <Activity className="text-tedbot-accent" size={24} />
          <h3 className="text-xl font-bold">Equity Curve</h3>
        </div>
        <EquityCurveChart />
      </motion.div>

      {/* Active Positions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass rounded-lg p-6"
      >
        <h3 className="text-xl font-bold mb-4">Active Positions</h3>
        <ActivePositionsGrid positions={positions} />
      </motion.div>

      {/* HIDDEN FOR MVP: Market Regime Indicator - Data not available */}
      {/* TODO: Re-enable when market regime detection is implemented:
        - Add VIX tracking
        - Implement trend detection (bull/bear/neutral)
        - Track SPY performance
        - Calculate sector breadth
        - Generate risk-on/risk-off signals
      */}
      {/* <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <MarketRegimeIndicator />
      </motion.div> */}

      {/* Disclaimer */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass rounded-lg p-6 border-l-4 border-yellow-500"
      >
        <p className="text-sm text-tedbot-gray-500">
          <strong className="text-yellow-500">Disclaimer:</strong> This is an autonomous trading system
          in validation phase. Past performance does not guarantee future results. All trading involves
          risk of loss. This dashboard is for informational purposes only and does not constitute
          investment advice.
        </p>
      </motion.div>
    </div>
  )
}

export default CommandCenter
