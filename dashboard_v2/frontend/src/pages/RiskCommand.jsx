import React from 'react'
import { Shield, AlertTriangle, Target, Lock } from 'lucide-react'

function RiskCommand() {
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
            <Shield className="text-profit" size={24} />
            <h3 className="text-sm font-semibold text-tedbot-gray-400">Portfolio Health</h3>
          </div>
          <p className="text-2xl font-bold text-profit">Excellent</p>
        </div>

        <div className="glass rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Target className="text-tedbot-accent" size={24} />
            <h3 className="text-sm font-semibold text-tedbot-gray-400">Max Drawdown</h3>
          </div>
          <p className="text-2xl font-bold">-12.4%</p>
        </div>

        <div className="glass rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="text-yellow-500" size={24} />
            <h3 className="text-sm font-semibold text-tedbot-gray-400">Risk Utilization</h3>
          </div>
          <p className="text-2xl font-bold">68%</p>
        </div>

        <div className="glass rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Lock className="text-tedbot-accent" size={24} />
            <h3 className="text-sm font-semibold text-tedbot-gray-400">Protected Capital</h3>
          </div>
          <p className="text-2xl font-bold">$32,000</p>
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
                <span className="text-sm font-bold">$5,000</span>
              </div>
              <div className="h-2 bg-tedbot-darker rounded-full overflow-hidden">
                <div className="h-full bg-profit" style={{ width: '60%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-tedbot-gray-400">Max Portfolio Heat</span>
                <span className="text-sm font-bold">80%</span>
              </div>
              <div className="h-2 bg-tedbot-darker rounded-full overflow-hidden">
                <div className="h-full bg-yellow-500" style={{ width: '68%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-tedbot-gray-400">Max Concurrent Positions</span>
                <span className="text-sm font-bold">10</span>
              </div>
              <div className="h-2 bg-tedbot-darker rounded-full overflow-hidden">
                <div className="h-full bg-profit" style={{ width: '40%' }}></div>
              </div>
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
            <div className="p-3 bg-profit/10 border border-profit/30 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <Shield size={16} className="text-profit" />
                <p className="text-sm font-semibold text-profit">All Systems Nominal</p>
              </div>
              <p className="text-xs text-tedbot-gray-500">No risk warnings detected</p>
            </div>
            <div className="p-3 bg-tedbot-darker rounded-lg opacity-50">
              <div className="flex items-center gap-2 mb-1">
                <AlertTriangle size={16} className="text-yellow-500" />
                <p className="text-sm font-semibold text-tedbot-gray-400">No Active Warnings</p>
              </div>
              <p className="text-xs text-tedbot-gray-600">Risk monitoring active</p>
            </div>
          </div>
        </div>
      </div>

      {/* Coming Soon */}
      <div className="glass rounded-lg p-8 text-center">
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
      </div>
    </div>
  )
}

export default RiskCommand
