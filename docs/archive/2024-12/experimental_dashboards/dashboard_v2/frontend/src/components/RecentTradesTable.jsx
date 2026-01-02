import React from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { format, parseISO } from 'date-fns'

function RecentTradesTable({ trades }) {
  if (!trades || trades.length === 0) {
    return (
      <div className="text-center py-8 text-tedbot-gray-500">
        No recent trades
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {trades.slice(0, 5).map((trade, index) => {
        const isWin = trade.return_pct > 0
        return (
          <div
            key={index}
            className="flex items-center justify-between p-3 rounded-lg bg-tedbot-gray-900/50 hover:bg-tedbot-gray-900 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${isWin ? 'bg-profit/10' : 'bg-loss/10'}`}>
                {isWin ? (
                  <TrendingUp className="text-profit" size={16} />
                ) : (
                  <TrendingDown className="text-loss" size={16} />
                )}
              </div>
              <div>
                <p className="font-bold">{trade.ticker}</p>
                <p className="text-xs text-tedbot-gray-500">
                  {trade.catalyst || 'Unknown'} · {trade.hold_days}d
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className={`font-bold ${isWin ? 'text-profit' : 'text-loss'}`}>
                {isWin ? '+' : ''}{trade.return_pct.toFixed(2)}%
              </p>
              <p className="text-xs text-tedbot-gray-500">
                {format(parseISO(trade.exit_date), 'MMM dd')}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default RecentTradesTable
