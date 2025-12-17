import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  Award,
  AlertTriangle
} from 'lucide-react'
import axios from 'axios'

// Components
import MetricCard from '../components/MetricCard'
import EquityCurveChart from '../components/EquityCurveChart'
import RecentTradesTable from '../components/RecentTradesTable'
import ActivePositionsGrid from '../components/ActivePositionsGrid'
import MarketRegimeIndicator from '../components/MarketRegimeIndicator'

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

  const { account, performance, recent_trades, positions } = overview

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

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Account Value"
          value={`$${account.value.toFixed(2)}`}
          change={account.total_return_pct}
          icon={DollarSign}
          trend={account.total_return_pct > 0 ? 'up' : 'down'}
        />
        <MetricCard
          title="Win Rate"
          value={`${performance.win_rate}%`}
          subtitle={`${performance.total_trades} trades`}
          icon={Target}
          trend={performance.win_rate >= 60 ? 'up' : performance.win_rate >= 50 ? 'neutral' : 'down'}
        />
        <MetricCard
          title="Sharpe Ratio"
          value={performance.sharpe_ratio.toFixed(2)}
          subtitle="Risk-adjusted return"
          icon={Award}
          trend={performance.sharpe_ratio > 1.5 ? 'up' : performance.sharpe_ratio > 1.0 ? 'neutral' : 'down'}
        />
        <MetricCard
          title="Max Drawdown"
          value={`${performance.max_drawdown.toFixed(1)}%`}
          subtitle="Peak to trough"
          icon={AlertTriangle}
          trend={performance.max_drawdown < 10 ? 'up' : performance.max_drawdown < 15 ? 'neutral' : 'down'}
          invertTrend
        />
      </div>

      {/* Cash & Positions Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="glass rounded-lg p-6">
          <h3 className="text-sm font-medium text-tedbot-gray-500 mb-2">Cash Available</h3>
          <p className="text-3xl font-bold text-profit">${account.cash.toFixed(2)}</p>
          <p className="text-xs text-tedbot-gray-600 mt-1">
            {((account.cash / account.value) * 100).toFixed(1)}% of account
          </p>
        </div>
        <div className="glass rounded-lg p-6">
          <h3 className="text-sm font-medium text-tedbot-gray-500 mb-2">Invested</h3>
          <p className="text-3xl font-bold text-tedbot-accent">${account.invested.toFixed(2)}</p>
          <p className="text-xs text-tedbot-gray-600 mt-1">
            {positions.length} active positions
          </p>
        </div>
        <div className="glass rounded-lg p-6">
          <h3 className="text-sm font-medium text-tedbot-gray-500 mb-2">Total P&L</h3>
          <p className={`text-3xl font-bold ${account.total_return_usd >= 0 ? 'text-profit' : 'text-loss'}`}>
            {account.total_return_usd >= 0 ? '+' : ''}${account.total_return_usd.toFixed(2)}
          </p>
          <p className="text-xs text-tedbot-gray-600 mt-1">
            {account.total_return_pct >= 0 ? '+' : ''}{account.total_return_pct.toFixed(2)}% all-time
          </p>
        </div>
      </div>

      {/* Equity Curve */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass rounded-lg p-6"
      >
        <h3 className="text-xl font-bold mb-4">Equity Curve</h3>
        <EquityCurveChart />
      </motion.div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Trades */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="glass rounded-lg p-6"
        >
          <h3 className="text-xl font-bold mb-4">Recent Trades</h3>
          <RecentTradesTable trades={recent_trades} />
        </motion.div>

        {/* Active Positions */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="glass rounded-lg p-6"
        >
          <h3 className="text-xl font-bold mb-4">Active Positions</h3>
          <ActivePositionsGrid positions={positions} />
        </motion.div>
      </div>

      {/* Market Regime Indicator */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <MarketRegimeIndicator />
      </motion.div>
    </div>
  )
}

export default CommandCenter
