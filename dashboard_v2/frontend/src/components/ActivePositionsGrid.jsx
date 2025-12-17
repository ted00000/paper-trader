import React from 'react'
import { Activity } from 'lucide-react'

function ActivePositionsGrid({ positions }) {
  if (!positions || positions.length === 0) {
    return (
      <div className="text-center py-8 text-tedbot-gray-500">
        <Activity className="mx-auto mb-2" size={32} />
        <p>No active positions</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-3">
      {positions.map((pos, index) => {
        const isProfit = pos.unrealized_pnl_pct >= 0
        return (
          <div
            key={index}
            className="p-4 rounded-lg bg-tedbot-gray-900/50 hover:bg-tedbot-gray-900 transition-colors border-l-4"
            style={{
              borderLeftColor: isProfit ? '#00ff41' : '#ff0033'
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="font-bold text-lg">{pos.ticker}</p>
                <p className="text-xs text-tedbot-gray-500">Day {pos.days_held}</p>
              </div>
              <div className="text-right">
                <p className={`text-xl font-bold ${isProfit ? 'text-profit' : 'text-loss'}`}>
                  {isProfit ? '+' : ''}{pos.unrealized_pnl_pct.toFixed(2)}%
                </p>
                <p className="text-xs text-tedbot-gray-500">${pos.position_size.toFixed(0)}</p>
              </div>
            </div>
            <div className="flex items-center justify-between text-xs text-tedbot-gray-600">
              <span>Entry: ${pos.entry_price.toFixed(2)}</span>
              <span>Current: ${pos.current_price.toFixed(2)}</span>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default ActivePositionsGrid
