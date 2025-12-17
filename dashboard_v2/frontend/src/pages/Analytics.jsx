import { useState, useEffect } from 'react'
import { TrendingUp, BarChart3, Calendar, RefreshCw } from 'lucide-react'
import axios from 'axios'
import CatalystPerformanceChart from '../components/CatalystPerformanceChart'
import MonthlyReturnsHeatmap from '../components/MonthlyReturnsHeatmap'

function Analytics() {
  const [catalystData, setCatalystData] = useState(null)
  const [monthlyData, setMonthlyData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState(null)

  const fetchAnalytics = async () => {
    setLoading(true)
    try {
      const [catalystRes, monthlyRes] = await Promise.all([
        axios.get('/api/v2/catalyst-performance'),
        axios.get('/api/v2/analytics/monthly-returns')
      ])

      setCatalystData(catalystRes.data.by_catalyst || [])
      setMonthlyData(monthlyRes.data.monthly_returns || {})
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalytics()
    const interval = setInterval(fetchAnalytics, 60000) // Update every minute
    return () => clearInterval(interval)
  }, [])

  if (loading && !catalystData && !monthlyData) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map(i => (
          <div key={i} className="glass rounded-lg p-8 shimmer h-96"></div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Analytics Deep Dive</h1>
          <p className="text-tedbot-gray-500">Advanced performance analytics and insights</p>
        </div>
        <div className="flex items-center gap-4">
          {lastUpdate && (
            <p className="text-xs text-tedbot-gray-600">
              Updated {lastUpdate.toLocaleTimeString()}
            </p>
          )}
          <button
            onClick={fetchAnalytics}
            disabled={loading}
            className="glass px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-tedbot-gray-900 transition-colors disabled:opacity-50"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Catalyst Performance Chart */}
      <div className="glass rounded-lg p-6">
        <div className="flex items-center gap-3 mb-6">
          <BarChart3 className="text-tedbot-accent" size={24} />
          <div>
            <h2 className="text-xl font-bold">Catalyst Performance Analysis</h2>
            <p className="text-sm text-tedbot-gray-500">Win rates by catalyst type</p>
          </div>
        </div>
        <CatalystPerformanceChart data={catalystData} />
      </div>

      {/* Monthly Returns Heatmap */}
      <div className="glass rounded-lg p-6">
        <div className="flex items-center gap-3 mb-6">
          <Calendar className="text-tedbot-accent" size={24} />
          <div>
            <h2 className="text-xl font-bold">Monthly Returns Calendar</h2>
            <p className="text-sm text-tedbot-gray-500">Performance heatmap by month and year</p>
          </div>
        </div>
        <MonthlyReturnsHeatmap data={monthlyData} />
      </div>

      {/* Additional Analytics Placeholders */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass rounded-lg p-8 text-center">
          <TrendingUp className="mx-auto mb-4 text-tedbot-accent" size={48} />
          <h3 className="text-xl font-bold mb-2">Hold Time Analysis</h3>
          <p className="text-tedbot-gray-500">Performance distribution by hold duration</p>
          <div className="mt-6 text-sm text-tedbot-gray-600">
            <p>• Histogram of returns by hold days</p>
            <p>• Optimal exit timing patterns</p>
            <p>• Win rate vs hold duration correlation</p>
          </div>
        </div>

        <div className="glass rounded-lg p-8 text-center">
          <BarChart3 className="mx-auto mb-4 text-tedbot-accent" size={48} />
          <h3 className="text-xl font-bold mb-2">Sector Allocation</h3>
          <p className="text-tedbot-gray-500">Distribution and performance across sectors</p>
          <div className="mt-6 text-sm text-tedbot-gray-600">
            <p>• Pie chart of sector allocation</p>
            <p>• Win rate by sector</p>
            <p>• Sector rotation patterns</p>
          </div>
        </div>

        <div className="glass rounded-lg p-8 text-center">
          <TrendingUp className="mx-auto mb-4 text-tedbot-accent" size={48} />
          <h3 className="text-xl font-bold mb-2">Conviction Analysis</h3>
          <p className="text-tedbot-gray-500">Performance by conviction level</p>
          <div className="mt-6 text-sm text-tedbot-gray-600">
            <p>• Win rate by conviction tier</p>
            <p>• Average returns by conviction</p>
            <p>• Conviction calibration accuracy</p>
          </div>
        </div>

        <div className="glass rounded-lg p-8 text-center">
          <BarChart3 className="mx-auto mb-4 text-tedbot-accent" size={48} />
          <h3 className="text-xl font-bold mb-2">Market Regime Performance</h3>
          <p className="text-tedbot-gray-500">Returns in different market conditions</p>
          <div className="mt-6 text-sm text-tedbot-gray-600">
            <p>• Performance in bull vs bear markets</p>
            <p>• High vs low volatility periods</p>
            <p>• Regime-specific win rates</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics
