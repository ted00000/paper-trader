import { useState, useEffect } from 'react'
import { Calendar, TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react'
import ScreeningDecisions from '../components/ScreeningDecisions'

function Today() {
  const [todayData, setTodayData] = useState(null)
  const [todaysTrades, setTodaysTrades] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTodayData()
  }, [])

  const fetchTodayData = async () => {
    try {
      // Fetch today's performance data
      const [perfResponse, screeningResponse] = await Promise.all([
        fetch('/api/v2/performance'),
        fetch('/api/v2/screening-decisions')
      ])
      const perfData = await perfResponse.json()
      const screeningData = await screeningResponse.json()

      setTodayData(perfData)
      setTodaysTrades(screeningData.todays_trades || [])
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

  // Get today's metrics from API response
  const todayPnL = todayData?.today?.pnl_dollars || 0  // Dollar P&L
  const todayReturn = todayData?.today?.pnl || 0  // Percent return
  const todayTrades = todayData?.today?.trades || 0
  const todayWins = todayData?.today?.wins || 0
  const todayLosses = todayData?.today?.losses || 0

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
              {todayPnL >= 0 ? '+' : '-'}${Math.abs(todayPnL).toFixed(2)}
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

        {todaysTrades.length === 0 ? (
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
                {todaysTrades.map((trade, index) => (
                  <tr key={index} className="border-b border-tedbot-gray-800/50 hover:bg-tedbot-darker/50">
                    <td className="py-3 px-4 text-sm">{trade.time}</td>
                    <td className="py-3 px-4 font-semibold">{trade.ticker}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        trade.action === 'BUY' ? 'bg-profit/20 text-profit' : 'bg-loss/20 text-loss'
                      }`}>
                        {trade.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">${trade.price?.toFixed(2)}</td>
                    <td className="py-3 px-4 text-right">{trade.shares}</td>
                    <td className={`py-3 px-4 text-right font-semibold ${trade.pnl >= 0 ? 'text-profit' : 'text-loss'}`}>
                      {trade.pnl >= 0 ? '+' : ''}${trade.pnl?.toFixed(2)}
                      <span className="text-xs ml-1">({trade.pnl_pct?.toFixed(2)}%)</span>
                    </td>
                  </tr>
                ))}
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
