import React from 'react'
import { Activity, Radio, Zap } from 'lucide-react'

function LiveFeed() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Live Trading Feed</h1>
          <p className="text-tedbot-gray-500">Real-time system activity and decision stream</p>
        </div>
        <div className="flex items-center gap-2 glass px-4 py-2 rounded-lg">
          <div className="w-2 h-2 bg-profit rounded-full animate-pulse"></div>
          <span className="text-sm font-semibold text-profit">LIVE</span>
        </div>
      </div>

      {/* Connection Status */}
      <div className="glass rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Radio className="text-tedbot-accent" size={24} />
            <div>
              <p className="font-semibold">WebSocket Connection</p>
              <p className="text-sm text-tedbot-gray-500">Real-time updates disabled in MVP</p>
            </div>
          </div>
          <button className="px-4 py-2 bg-tedbot-darker rounded-lg border border-tedbot-gray-800 text-tedbot-gray-500 cursor-not-allowed">
            Connect
          </button>
        </div>
      </div>

      {/* Activity Feed Preview */}
      <div className="glass rounded-lg p-6">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Activity size={20} />
          Activity Stream Preview
        </h3>
        <div className="space-y-3">
          {/* Sample Activity Items */}
          <div className="flex items-start gap-3 p-3 bg-tedbot-darker rounded-lg border-l-4 border-profit">
            <Zap className="text-profit mt-1" size={18} />
            <div className="flex-1">
              <p className="text-sm font-semibold">Position Opened</p>
              <p className="text-xs text-tedbot-gray-500">AAPL - Entry at $182.45 - Earnings Catalyst (Tier 1)</p>
              <p className="text-xs text-tedbot-gray-600 mt-1">2 minutes ago</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-tedbot-darker rounded-lg border-l-4 border-tedbot-accent">
            <Activity className="text-tedbot-accent mt-1" size={18} />
            <div className="flex-1">
              <p className="text-sm font-semibold">Market Scan Complete</p>
              <p className="text-xs text-tedbot-gray-500">12 candidates identified from S&P 1500 universe</p>
              <p className="text-xs text-tedbot-gray-600 mt-1">15 minutes ago</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-tedbot-darker rounded-lg border-l-4 border-yellow-500">
            <Zap className="text-yellow-500 mt-1" size={18} />
            <div className="flex-1">
              <p className="text-sm font-semibold">Stop Loss Adjusted</p>
              <p className="text-xs text-tedbot-gray-500">NVDA - Trailing stop moved to $875.20 (+8.2%)</p>
              <p className="text-xs text-tedbot-gray-600 mt-1">32 minutes ago</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-tedbot-darker rounded-lg border-l-4 border-loss">
            <Zap className="text-loss mt-1" size={18} />
            <div className="flex-1">
              <p className="text-sm font-semibold">Position Closed</p>
              <p className="text-xs text-tedbot-gray-500">TSLA - Exit at $248.90 (+5.7%) - 3 day hold</p>
              <p className="text-xs text-tedbot-gray-600 mt-1">1 hour ago</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-tedbot-darker rounded-lg border-l-4 border-tedbot-accent">
            <Activity className="text-tedbot-accent mt-1" size={18} />
            <div className="flex-1">
              <p className="text-sm font-semibold">Daily Learning Loop</p>
              <p className="text-xs text-tedbot-gray-500">Pattern analysis complete - 7 trades processed</p>
              <p className="text-xs text-tedbot-gray-600 mt-1">2 hours ago</p>
            </div>
          </div>
        </div>
      </div>

      {/* Coming Soon */}
      <div className="glass rounded-lg p-8 text-center">
        <Radio className="mx-auto mb-4 text-tedbot-accent" size={64} />
        <h3 className="text-2xl font-bold mb-2">Real-Time WebSocket Feed</h3>
        <p className="text-tedbot-gray-500 mb-6">
          Live streaming of all system events and decision-making
        </p>
        <div className="space-y-2 text-sm text-tedbot-gray-600">
          <p>• Real-time position updates and P&L changes</p>
          <p>• Market scan progress and candidate discoveries</p>
          <p>• Trade execution notifications with reasoning</p>
          <p>• Stop loss adjustments and risk management events</p>
          <p>• Learning loop completions and insights</p>
          <p>• System health and performance metrics</p>
        </div>
      </div>
    </div>
  )
}

export default LiveFeed
