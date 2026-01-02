import React from 'react'
import { AlertCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react'

function MarketRegimeIndicator({ regime }) {
  if (!regime) {
    return (
      <div className="glass rounded-lg p-6 text-center">
        <AlertCircle className="mx-auto mb-2 text-tedbot-gray-500" size={32} />
        <p className="text-tedbot-gray-500">Market regime data unavailable</p>
      </div>
    )
  }

  const getRegimeColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'bullish':
      case 'bull':
        return 'text-profit'
      case 'bearish':
      case 'bear':
        return 'text-loss'
      case 'neutral':
      case 'mixed':
        return 'text-tedbot-gray-400'
      default:
        return 'text-tedbot-gray-400'
    }
  }

  const getRegimeIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'bullish':
      case 'bull':
        return <TrendingUp size={24} className="text-profit" />
      case 'bearish':
      case 'bear':
        return <TrendingDown size={24} className="text-loss" />
      default:
        return <Minus size={24} className="text-tedbot-gray-400" />
    }
  }

  const getRegimeBackground = (status) => {
    switch (status?.toLowerCase()) {
      case 'bullish':
      case 'bull':
        return 'bg-profit/10'
      case 'bearish':
      case 'bear':
        return 'bg-loss/10'
      default:
        return 'bg-tedbot-gray-800/30'
    }
  }

  return (
    <div className="glass rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-tedbot-gray-300">Market Regime</h3>
        <div className={`p-2 rounded-lg ${getRegimeBackground(regime.status)}`}>
          {getRegimeIcon(regime.status)}
        </div>
      </div>

      <div className="space-y-4">
        {/* Main Regime Status */}
        <div>
          <p className="text-xs text-tedbot-gray-500 mb-1">Current Regime</p>
          <p className={`text-2xl font-bold ${getRegimeColor(regime.status)}`}>
            {regime.status || 'Unknown'}
          </p>
        </div>

        {/* Market Indicators Grid */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-tedbot-gray-800">
          {/* VIX */}
          {regime.vix && (
            <div>
              <p className="text-xs text-tedbot-gray-500 mb-1">VIX</p>
              <p className={`text-lg font-bold ${
                regime.vix > 20 ? 'text-loss' :
                regime.vix > 15 ? 'text-tedbot-gray-300' :
                'text-profit'
              }`}>
                {regime.vix.toFixed(2)}
              </p>
            </div>
          )}

          {/* Market Trend */}
          {regime.trend && (
            <div>
              <p className="text-xs text-tedbot-gray-500 mb-1">Trend</p>
              <p className={`text-lg font-bold ${getRegimeColor(regime.trend)}`}>
                {regime.trend}
              </p>
            </div>
          )}

          {/* SPY Performance */}
          {regime.spy_change !== undefined && (
            <div>
              <p className="text-xs text-tedbot-gray-500 mb-1">SPY (1D)</p>
              <p className={`text-lg font-bold ${
                regime.spy_change >= 0 ? 'text-profit' : 'text-loss'
              }`}>
                {regime.spy_change >= 0 ? '+' : ''}{regime.spy_change.toFixed(2)}%
              </p>
            </div>
          )}

          {/* Sector Breadth */}
          {regime.sector_breadth !== undefined && (
            <div>
              <p className="text-xs text-tedbot-gray-500 mb-1">Sector Breadth</p>
              <p className={`text-lg font-bold ${
                regime.sector_breadth >= 0.7 ? 'text-profit' :
                regime.sector_breadth >= 0.5 ? 'text-tedbot-gray-300' :
                'text-loss'
              }`}>
                {(regime.sector_breadth * 100).toFixed(0)}%
              </p>
            </div>
          )}
        </div>

        {/* Risk Signal */}
        {regime.risk_signal && (
          <div className="pt-4 border-t border-tedbot-gray-800">
            <p className="text-xs text-tedbot-gray-500 mb-2">Risk Signal</p>
            <div className={`px-3 py-2 rounded-lg ${
              regime.risk_signal === 'Risk-On' ? 'bg-profit/10 text-profit' :
              regime.risk_signal === 'Risk-Off' ? 'bg-loss/10 text-loss' :
              'bg-tedbot-gray-800/30 text-tedbot-gray-400'
            }`}>
              <p className="text-sm font-semibold">{regime.risk_signal}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MarketRegimeIndicator
