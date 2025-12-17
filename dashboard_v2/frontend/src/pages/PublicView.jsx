import { useState, useEffect } from 'react'
import { TrendingUp, Award, Target } from 'lucide-react'
import axios from 'axios'
import EquityCurveChart from '../components/EquityCurveChart'

function PublicView() {
  const [data, setData] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [overviewRes, equityRes] = await Promise.all([
          axios.get('/api/v2/overview'),
          axios.get('/api/v2/equity-curve')
        ])
        setData({
          overview: overviewRes.data,
          equity: equityRes.data
        })
      } catch (error) {
        console.error('Error fetching public view data:', error)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 60000) // Update every minute
    return () => clearInterval(interval)
  }, [])

  if (!data) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="shimmer w-full h-full rounded-lg"></div>
      </div>
    )
  }

  const account = data.overview.account
  const performance = data.overview.performance

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12">
        <div className="flex items-center justify-center gap-3 mb-4">
          <img
            src="/tedbot-logo.png"
            alt="Tedbot Logo"
            className="w-16 h-16 rounded-lg"
          />
          <h1 className="text-5xl font-bold gradient-text">Tedbot</h1>
        </div>
        <p className="text-xl text-tedbot-gray-400 mb-2">Autonomous Trading System</p>
        <p className="text-tedbot-gray-500">
          Machine learning driven catalyst-based momentum strategy
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass rounded-lg p-6 text-center glow-green">
          <TrendingUp className="mx-auto mb-3 text-profit" size={32} />
          <p className="text-sm text-tedbot-gray-400 mb-2">Total Return</p>
          <p className="text-3xl font-bold text-profit">
            +{account.total_return_pct.toFixed(2)}%
          </p>
        </div>

        <div className="glass rounded-lg p-6 text-center">
          <Award className="mx-auto mb-3 text-tedbot-accent" size={32} />
          <p className="text-sm text-tedbot-gray-400 mb-2">Win Rate</p>
          <p className="text-3xl font-bold">{performance.win_rate.toFixed(1)}%</p>
        </div>

        <div className="glass rounded-lg p-6 text-center">
          <Target className="mx-auto mb-3 text-tedbot-accent" size={32} />
          <p className="text-sm text-tedbot-gray-400 mb-2">Sharpe Ratio</p>
          <p className="text-3xl font-bold">{performance.sharpe_ratio.toFixed(2)}</p>
        </div>

        <div className="glass rounded-lg p-6 text-center">
          <TrendingUp className="mx-auto mb-3 text-tedbot-accent" size={32} />
          <p className="text-sm text-tedbot-gray-400 mb-2">Total Trades</p>
          <p className="text-3xl font-bold">{performance.total_trades}</p>
        </div>
      </div>

      {/* Equity Curve */}
      <div className="glass rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-6">Performance History</h2>
        <EquityCurveChart data={data.equity.equity_curve} />
      </div>

      {/* Strategy Overview */}
      <div className="glass rounded-lg p-8">
        <h2 className="text-2xl font-bold mb-6">Strategy Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold mb-3 text-tedbot-accent">Approach</h3>
            <ul className="space-y-2 text-tedbot-gray-400">
              <li>• Catalyst-driven momentum trading</li>
              <li>• S&P 1500 universe screening</li>
              <li>• Multi-tier catalyst validation</li>
              <li>• Relative strength analysis</li>
              <li>• Dynamic position sizing</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-3 text-tedbot-accent">Risk Management</h3>
            <ul className="space-y-2 text-tedbot-gray-400">
              <li>• Strict 8% initial stop loss</li>
              <li>• Dynamic trailing stops (2-4 ATR)</li>
              <li>• Max portfolio heat limits</li>
              <li>• Sector diversification rules</li>
              <li>• Daily drawdown protection</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-3 text-tedbot-accent">Learning System</h3>
            <ul className="space-y-2 text-tedbot-gray-400">
              <li>• Daily performance analysis</li>
              <li>• Weekly pattern identification</li>
              <li>• Monthly strategy review</li>
              <li>• 63-feature data capture</li>
              <li>• Continuous optimization</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-3 text-tedbot-accent">Catalysts</h3>
            <ul className="space-y-2 text-tedbot-gray-400">
              <li>• Earnings reports (Tier 1)</li>
              <li>• Breakout patterns</li>
              <li>• Unusual volume spikes</li>
              <li>• Sector rotation signals</li>
              <li>• Analyst upgrades</li>
            </ul>
          </div>
        </div>
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

export default PublicView
