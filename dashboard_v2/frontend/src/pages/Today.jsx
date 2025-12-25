import React, { useState, useEffect } from 'react'
import { Calendar, TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react'
import ScreeningDecisions from '../components/ScreeningDecisions'

function Today() {
  const [todayData, setTodayData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTodayData()
  }, [])

  const fetchTodayData = async () => {
    try {
      // Fetch today's performance data
      const response = await fetch('/api/v2/performance')
      const data = await response.json()
      setTodayData(data)
    } catch (error) {
      console.error('Failed to fetch today data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-tedbot-gray-500">Loading today's data...</div>
      </div>
    )
  }

  // Calculate today's metrics (placeholder - will be replaced with real API)
  const todayPnL = 0 // TODO: Get from API
  const todayReturn = 0 // TODO: Get from API
  const todayTrades = 0 // TODO: Get from API
  const todayWins = 0 // TODO: Get from API
  const todayLosses = 0 // TODO: Get from API

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <Calendar className="text-tedbot-accent" size={32} />
          <div>
            <h1 className="text-3xl font-bold">Today's Activity</h1>
            <p className="text-tedbot-gray-500">
              {new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </p>
          </div>
        </div>
      </div>

      {/* Today's Performance Metrics */}
      <div>
        <h2 className="text-xl font-bold mb-4">Today's Performance</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {/* Today's P&L */}
          <div className="glass rounded-lg p-6">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign className={todayPnL >= 0 ? 'text-profit' : 'text-loss'} size={24} />
              <h3 className="text-sm font-semibold text-tedbot-gray-400">Today's P&L</h3>
            </div>
            <p className={`text-2xl font-bold ${todayPnL >= 0 ? 'text-profit' : 'text-loss'}`}>
              {todayPnL >= 0 ? '+' : ''}${Math.abs(todayPnL).toFixed(2)}
            </p>
          </div>

          {/* Today's Return % */}
          <div className="glass rounded-lg p-6">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className={todayReturn >= 0 ? 'text-profit' : 'text-loss'} size={24} />
              <h3 className="text-sm font-semibold text-tedbot-gray-400">Today's Return</h3>
            </div>
            <p className={`text-2xl font-bold ${todayReturn >= 0 ? 'text-profit' : 'text-loss'}`}>
              {todayReturn >= 0 ? '+' : ''}{todayReturn.toFixed(2)}%
            </p>
          </div>

          {/* Today's Trades */}
          <div className="glass rounded-lg p-6">
            <div className="flex items-center gap-3 mb-2">
              <Activity className="text-tedbot-accent" size={24} />
              <h3 className="text-sm font-semibold text-tedbot-gray-400">Trades Today</h3>
            </div>
            <p className="text-2xl font-bold">{todayTrades}</p>
          </div>

          {/* Today's Wins */}
          <div className="glass rounded-lg p-6">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="text-profit" size={24} />
              <h3 className="text-sm font-semibold text-tedbot-gray-400">Wins</h3>
            </div>
            <p className="text-2xl font-bold text-profit">{todayWins}</p>
          </div>

          {/* Today's Losses */}
          <div className="glass rounded-lg p-6">
            <div className="flex items-center gap-3 mb-2">
              <TrendingDown className="text-loss" size={24} />
              <h3 className="text-sm font-semibold text-tedbot-gray-400">Losses</h3>
            </div>
            <p className="text-2xl font-bold text-loss">{todayLosses}</p>
          </div>
        </div>
      </div>

      {/* Screening Decisions */}
      <ScreeningDecisions />

      {/* Today's Trades Table */}
      <div className="glass rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Today's Trades</h2>

        {todayTrades === 0 ? (
          <div className="text-center py-12 text-tedbot-gray-500">
            <Activity className="mx-auto mb-4 opacity-50" size={48} />
            <p>No trades executed today</p>
            <p className="text-sm mt-2">Waiting for system signals...</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-tedbot-gray-800">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-tedbot-gray-400">Time</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-tedbot-gray-400">Ticker</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-tedbot-gray-400">Action</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-tedbot-gray-400">Price</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-tedbot-gray-400">Shares</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-tedbot-gray-400">P&L</th>
                </tr>
              </thead>
              <tbody>
                {/* Table rows will be populated from API */}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <div className="glass rounded-lg p-6 border-l-4 border-yellow-500">
        <p className="text-sm text-tedbot-gray-500">
          <strong className="text-yellow-500">Disclaimer:</strong> This is an autonomous trading system
          in validation phase. Past performance does not guarantee future results. All trading involves
          risk of loss. This dashboard is for informational purposes only and does not constitute
          investment advice.
        </p>
      </div>
    </div>
  )
}

export default Today
