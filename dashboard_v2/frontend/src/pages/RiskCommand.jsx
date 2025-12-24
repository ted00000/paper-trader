import { useState, useEffect } from 'react'
import { Shield, AlertTriangle, Target, Lock } from 'lucide-react'

function RiskCommand() {
  const [overview, setOverview] = useState(null)
  const [positions, setPositions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRiskData()
  }, [])

  const fetchRiskData = async () => {
    try {
      const [overviewRes, positionsRes] = await Promise.all([
        fetch('/api/v2/overview'),
        fetch('/api/v2/risk/positions')
      ])

      const overviewData = await overviewRes.json()
      const positionsData = await positionsRes.json()

      setOverview(overviewData)
      setPositions(positionsData.positions || [])
    } catch (error) {
      console.error('Failed to fetch risk data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-tedbot-gray-500">Loading risk data...</div>
      </div>
    )
  }

  // Calculate portfolio health based on win rate and drawdown
  const winRate = overview?.performance?.win_rate || 0
  const maxDrawdown = overview?.performance?.max_drawdown || 0
  const getPortfolioHealth = () => {
    if (winRate >= 65 && maxDrawdown >= -15) return { label: 'Excellent', color: 'text-profit' }
    if (winRate >= 55 && maxDrawdown >= -20) return { label: 'Good', color: 'text-profit' }
    if (winRate >= 45 && maxDrawdown >= -25) return { label: 'Fair', color: 'text-yellow-500' }
    return { label: 'Weak', color: 'text-loss' }
  }
  const portfolioHealth = getPortfolioHealth()

  // Calculate risk utilization (portfolio value vs cash)
  const accountValue = overview?.account?.value || 0
  const cashBalance = overview?.account?.cash || 0
  const positionsValue = accountValue - cashBalance
  const riskUtilization = accountValue > 0 ? (positionsValue / accountValue * 100) : 0

  // Calculate max position size (10% of account)
  const maxPositionSize = accountValue * 0.10

  // Calculate portfolio heat (current positions vs max allowed)
  const maxPortfolioHeat = 80 // 80% max deployment
  const currentHeat = riskUtilization

  // Max concurrent positions
  const maxConcurrentPositions = 10
  const currentPositions = positions.length

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Risk Command Center</h1>
        <p className="text-tedbot-gray-500">Real-time risk monitoring and position management</p>
      </div>

      {/* Risk Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Shield className={portfolioHealth.color} size={24} />
            <h3 className="text-sm font-semibold text-tedbot-gray-400">Portfolio Health</h3>
          </div>
          <p className={`text-2xl font-bold ${portfolioHealth.color}`}>{portfolioHealth.label}</p>
        </div>

        <div className="glass rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Target className="text-tedbot-accent" size={24} />
            <h3 className="text-sm font-semibold text-tedbot-gray-400">Max Drawdown</h3>
          </div>
          <p className="text-2xl font-bold">{maxDrawdown.toFixed(1)}%</p>
        </div>

        <div className="glass rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className={riskUtilization > 80 ? 'text-loss' : riskUtilization > 60 ? 'text-yellow-500' : 'text-profit'} size={24} />
            <h3 className="text-sm font-semibold text-tedbot-gray-400">Risk Utilization</h3>
          </div>
          <p className="text-2xl font-bold">{riskUtilization.toFixed(0)}%</p>
        </div>

        <div className="glass rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Lock className="text-tedbot-accent" size={24} />
            <h3 className="text-sm font-semibold text-tedbot-gray-400">Protected Capital</h3>
          </div>
          <p className="text-2xl font-bold">${cashBalance.toFixed(0)}</p>
        </div>
      </div>

      {/* Risk Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass rounded-lg p-6">
          <h3 className="text-xl font-bold mb-4">Position Limits</h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-tedbot-gray-400">Max Position Size</span>
                <span className="text-sm font-bold">${maxPositionSize.toFixed(0)}</span>
              </div>
              <div className="h-2 bg-tedbot-darker rounded-full overflow-hidden">
                <div className="h-full bg-profit" style={{ width: '100%' }}></div>
              </div>
              <p className="text-xs text-tedbot-gray-600 mt-1">10% of account value</p>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-tedbot-gray-400">Max Portfolio Heat</span>
                <span className="text-sm font-bold">{maxPortfolioHeat}%</span>
              </div>
              <div className="h-2 bg-tedbot-darker rounded-full overflow-hidden">
                <div
                  className={`h-full ${currentHeat > 80 ? 'bg-loss' : currentHeat > 60 ? 'bg-yellow-500' : 'bg-profit'}`}
                  style={{ width: `${Math.min((currentHeat / maxPortfolioHeat) * 100, 100)}%` }}
                ></div>
              </div>
              <p className="text-xs text-tedbot-gray-600 mt-1">Currently {currentHeat.toFixed(0)}% deployed</p>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-tedbot-gray-400">Max Concurrent Positions</span>
                <span className="text-sm font-bold">{maxConcurrentPositions}</span>
              </div>
              <div className="h-2 bg-tedbot-darker rounded-full overflow-hidden">
                <div
                  className="h-full bg-profit"
                  style={{ width: `${(currentPositions / maxConcurrentPositions) * 100}%` }}
                ></div>
              </div>
              <p className="text-xs text-tedbot-gray-600 mt-1">Currently {currentPositions} position{currentPositions !== 1 ? 's' : ''}</p>
            </div>
          </div>
        </div>

        <div className="glass rounded-lg p-6">
          <h3 className="text-xl font-bold mb-4">Stop Loss Protection</h3>
          <div className="space-y-4">
            <div className="p-3 bg-tedbot-darker rounded-lg">
              <p className="text-sm text-tedbot-gray-400 mb-1">Initial Stop</p>
              <p className="text-lg font-bold">-8%</p>
            </div>
            <div className="p-3 bg-tedbot-darker rounded-lg">
              <p className="text-sm text-tedbot-gray-400 mb-1">Trailing Stop</p>
              <p className="text-lg font-bold">Dynamic (2-4 ATR)</p>
            </div>
            <div className="p-3 bg-tedbot-darker rounded-lg">
              <p className="text-sm text-tedbot-gray-400 mb-1">Max Daily Loss</p>
              <p className="text-lg font-bold">-2%</p>
            </div>
          </div>
        </div>

        <div className="glass rounded-lg p-6">
          <h3 className="text-xl font-bold mb-4">Diversification</h3>
          <div className="space-y-3">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-tedbot-gray-400">Sector Concentration</span>
                <span className="text-sm font-bold text-profit">Well Distributed</span>
              </div>
              <p className="text-xs text-tedbot-gray-600">Max 30% per sector</p>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-tedbot-gray-400">Correlation Risk</span>
                <span className="text-sm font-bold text-profit">Low</span>
              </div>
              <p className="text-xs text-tedbot-gray-600">Positions have low correlation</p>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-tedbot-gray-400">Catalyst Diversity</span>
                <span className="text-sm font-bold text-profit">High</span>
              </div>
              <p className="text-xs text-tedbot-gray-600">Multiple catalyst types active</p>
            </div>
          </div>
        </div>

        <div className="glass rounded-lg p-6">
          <h3 className="text-xl font-bold mb-4">Risk Alerts</h3>
          <div className="space-y-3">
            {/* Check for risk warnings */}
            {currentHeat > 80 && (
              <div className="p-3 bg-loss/10 border border-loss/30 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle size={16} className="text-loss" />
                  <p className="text-sm font-semibold text-loss">Portfolio Heat Critical</p>
                </div>
                <p className="text-xs text-tedbot-gray-500">Risk utilization at {currentHeat.toFixed(0)}% (max: {maxPortfolioHeat}%)</p>
              </div>
            )}
            {currentHeat > 60 && currentHeat <= 80 && (
              <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle size={16} className="text-yellow-500" />
                  <p className="text-sm font-semibold text-yellow-500">Portfolio Heat Elevated</p>
                </div>
                <p className="text-xs text-tedbot-gray-500">Risk utilization at {currentHeat.toFixed(0)}% (approaching limit)</p>
              </div>
            )}
            {winRate < 50 && overview?.performance?.total_trades > 10 && (
              <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle size={16} className="text-yellow-500" />
                  <p className="text-sm font-semibold text-yellow-500">Win Rate Below Target</p>
                </div>
                <p className="text-xs text-tedbot-gray-500">Current win rate: {winRate.toFixed(1)}% (target: 50%+)</p>
              </div>
            )}
            {maxDrawdown < -25 && (
              <div className="p-3 bg-loss/10 border border-loss/30 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle size={16} className="text-loss" />
                  <p className="text-sm font-semibold text-loss">High Drawdown Alert</p>
                </div>
                <p className="text-xs text-tedbot-gray-500">Max drawdown: {maxDrawdown.toFixed(1)}% (target: -20% or better)</p>
              </div>
            )}
            {currentHeat <= 60 && winRate >= 50 && maxDrawdown >= -25 && (
              <div className="p-3 bg-profit/10 border border-profit/30 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <Shield size={16} className="text-profit" />
                  <p className="text-sm font-semibold text-profit">All Systems Nominal</p>
                </div>
                <p className="text-xs text-tedbot-gray-500">No risk warnings detected</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Current Positions Risk Table */}
      <div className="glass rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Current Positions</h2>
        {positions.length === 0 ? (
          <div className="text-center py-12 text-tedbot-gray-500">
            <Shield className="mx-auto mb-4 opacity-50" size={48} />
            <p>No active positions</p>
            <p className="text-sm mt-2">Protected capital mode</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-tedbot-gray-800">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-tedbot-gray-400">Ticker</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-tedbot-gray-400">Entry</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-tedbot-gray-400">Current</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-tedbot-gray-400">P&L</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-tedbot-gray-400">Stop Loss</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-tedbot-gray-400">Distance to Stop</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-tedbot-gray-400">Risk Level</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos, idx) => (
                  <tr key={idx} className="border-b border-tedbot-gray-800 hover:bg-tedbot-darker/50">
                    <td className="py-3 px-4">
                      <span className="font-bold">{pos.ticker}</span>
                      <div className="text-xs text-tedbot-gray-500">{pos.days_held} days</div>
                    </td>
                    <td className="text-right py-3 px-4">${pos.entry_price?.toFixed(2)}</td>
                    <td className="text-right py-3 px-4">${pos.current_price?.toFixed(2)}</td>
                    <td className={`text-right py-3 px-4 font-bold ${pos.unrealized_pnl_pct >= 0 ? 'text-profit' : 'text-loss'}`}>
                      {pos.unrealized_pnl_pct >= 0 ? '+' : ''}{pos.unrealized_pnl_pct?.toFixed(2)}%
                    </td>
                    <td className="text-right py-3 px-4">${pos.stop_loss?.toFixed(2)}</td>
                    <td className={`text-right py-3 px-4 ${pos.stop_distance_pct < 3 ? 'text-loss' : pos.stop_distance_pct < 5 ? 'text-yellow-500' : 'text-profit'}`}>
                      {pos.stop_distance_pct?.toFixed(1)}%
                    </td>
                    <td className="text-right py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${
                        pos.risk_level === 'HIGH' ? 'bg-loss/20 text-loss' :
                        pos.risk_level === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-500' :
                        'bg-profit/20 text-profit'
                      }`}>
                        {pos.risk_level}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* HIDDEN FOR MVP: Advanced Risk Analytics - Future development */}
      {/* TODO: Re-enable when advanced analytics are implemented:
        - Live position heat maps by sector and conviction
        - Historical drawdown analysis and recovery times
        - Portfolio beta and market correlation tracking
        - Worst-case scenario stress testing
        - Risk-adjusted performance attribution
      */}
      {/* <div className="glass rounded-lg p-8 text-center">
        <Shield className="mx-auto mb-4 text-tedbot-accent" size={64} />
        <h3 className="text-2xl font-bold mb-2">Advanced Risk Analytics</h3>
        <p className="text-tedbot-gray-500 mb-6">
          Real-time risk monitoring with portfolio stress testing
        </p>
        <div className="space-y-2 text-sm text-tedbot-gray-600">
          <p>• Live position heat maps by sector and conviction</p>
          <p>• Historical drawdown analysis and recovery times</p>
          <p>• Portfolio beta and market correlation tracking</p>
          <p>• Worst-case scenario stress testing</p>
          <p>• Risk-adjusted performance attribution</p>
        </div>
      </div> */}
    </div>
  )
}

export default RiskCommand
