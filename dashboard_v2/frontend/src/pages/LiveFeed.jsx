/*
  HIDDEN FOR MVP: Live Feed Page - Operations Status Moved to Command Center

  NOTE: This page is hidden from navigation but preserved for future development.

  The System Operations Status section (SCREENER, GO, EXECUTE, ANALYZE monitoring)
  has been extracted into a reusable component (OperationsStatus.jsx) and moved to
  the top of the Command Center page for better visibility and accessibility.

  FUTURE ENHANCEMENT: Real-Time Activity Stream

  This page was originally intended to provide a live feed of system events and
  decision-making processes. Future implementation would include:

  1. WebSocket Integration:
     - Real-time event streaming from trading system
     - Instant position updates and P&L changes
     - Live market scan progress and discoveries
     - Trade execution notifications with reasoning
     - Stop loss adjustments and risk management events
     - Learning loop completions and insights

  2. Activity Stream Features:
     - Chronological event timeline
     - Filterable by event type (scans, trades, learning, risk)
     - Expandable event details
     - Historical playback capability

  3. Implementation Requirements:
     - WebSocket server endpoint in Flask backend
     - Socket.io or native WebSocket connection in React
     - Event emission from screener, go, execute, analyze, learn processes
     - Persistent event storage for historical viewing
     - Reconnection logic and error handling

  To re-enable this page:
  1. Uncomment navigation entry in App.jsx
  2. Implement WebSocket infrastructure
  3. Remove placeholder activity items below
  4. Connect to real event stream
*/

import { useState, useEffect } from 'react'
import { Activity, Zap, CheckCircle2, XCircle, AlertCircle, Eye, RefreshCw } from 'lucide-react'
import axios from 'axios'

function LiveFeed() {
  const [operationsData, setOperationsData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedLog, setSelectedLog] = useState(null)
  const [logContent, setLogContent] = useState(null)
  const [logLoading, setLogLoading] = useState(false)

  const fetchOperations = async () => {
    try {
      const response = await axios.get('/api/v2/operations/status')
      setOperationsData(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching operations:', error)
      setLoading(false)
    }
  }

  const viewLog = async (operation) => {
    setSelectedLog(operation)
    setLogLoading(true)
    setLogContent(null)

    try {
      const response = await axios.get(`/api/v2/operations/logs/${operation.toLowerCase()}`)
      setLogContent(response.data)
      setLogLoading(false)
    } catch (error) {
      console.error('Error fetching log:', error)
      setLogContent({ error: error.response?.data?.error || 'Failed to load log' })
      setLogLoading(false)
    }
  }

  const closeLogModal = () => {
    setSelectedLog(null)
    setLogContent(null)
  }

  useEffect(() => {
    fetchOperations()
    const interval = setInterval(fetchOperations, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const getHealthIcon = (health) => {
    switch (health) {
      case 'HEALTHY':
        return <CheckCircle2 className="text-profit" size={20} />
      case 'FAILED':
      case 'UNHEALTHY':
        return <XCircle className="text-loss" size={20} />
      case 'WARNING':
      case 'UNKNOWN':
        return <AlertCircle className="text-yellow-500" size={20} />
      default:
        return <AlertCircle className="text-tedbot-gray-500" size={20} />
    }
  }

  const getHealthColor = (health) => {
    switch (health) {
      case 'HEALTHY':
        return 'border-profit'
      case 'FAILED':
      case 'UNHEALTHY':
        return 'border-loss'
      case 'WARNING':
      case 'UNKNOWN':
        return 'border-yellow-500'
      default:
        return 'border-tedbot-gray-700'
    }
  }

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Never'

    try {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = Math.floor((now - date) / 1000) // seconds

      if (diff < 60) return 'Just now'
      if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
      if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
      return `${Math.floor(diff / 86400)}d ago`
    } catch {
      return timestamp
    }
  }

  // Define operation order
  const operationOrder = ['SCREENER', 'GO', 'EXECUTE', 'ANALYZE']

  // Sort operations by defined order
  const sortedOperations = operationsData ?
    operationOrder
      .filter(op => operationsData.operations[op])
      .map(op => [op, operationsData.operations[op]])
    : []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Live Trading Feed</h1>
          <p className="text-tedbot-gray-500">Real-time system activity and decision stream</p>
        </div>
        <div className="flex items-center gap-4">
          {operationsData && (
            <div className={`flex items-center gap-2 glass px-4 py-2 rounded-lg border ${
              operationsData.health === 'HEALTHY' ? 'border-profit' :
              operationsData.health === 'WARNING' ? 'border-yellow-500' :
              'border-loss'
            }`}>
              <div className={`w-2 h-2 rounded-full animate-pulse ${
                operationsData.health === 'HEALTHY' ? 'bg-profit' :
                operationsData.health === 'WARNING' ? 'bg-yellow-500' :
                'bg-loss'
              }`}></div>
              <span className={`text-sm font-semibold ${
                operationsData.health === 'HEALTHY' ? 'text-profit' :
                operationsData.health === 'WARNING' ? 'text-yellow-500' :
                'text-loss'
              }`}>
                {operationsData.health}
              </span>
            </div>
          )}
          <button
            onClick={fetchOperations}
            className="flex items-center gap-2 px-4 py-2 bg-tedbot-darker rounded-lg border border-tedbot-gray-800 hover:border-tedbot-accent transition-colors"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            <span className="text-sm">Refresh</span>
          </button>
        </div>
      </div>

      {/* Operations Status Grid */}
      <div className="glass rounded-lg p-6">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Activity size={20} />
          System Operations Status
        </h3>

        {loading && !operationsData ? (
          <div className="text-center py-8">
            <div className="animate-pulse">
              <Activity className="mx-auto mb-4 text-tedbot-accent" size={48} />
              <p className="text-tedbot-gray-500">Loading operations status...</p>
            </div>
          </div>
        ) : operationsData ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {sortedOperations.map(([name, op]) => (
              <div
                key={name}
                onClick={() => viewLog(name)}
                className={`bg-tedbot-darker rounded-lg p-4 border-l-4 ${getHealthColor(op.health)} transition-all cursor-pointer hover:shadow-lg hover:border-tedbot-accent`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    {getHealthIcon(op.health)}
                    <div>
                      <h4 className="font-bold text-sm">{name}</h4>
                      <p className="text-xs text-tedbot-gray-500">{op.status}</p>
                    </div>
                  </div>
                  <Eye size={16} className="text-tedbot-gray-500" />
                </div>

                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-tedbot-gray-500">Last Run:</span>
                    <span className="font-semibold">{formatTimestamp(op.last_run)}</span>
                  </div>

                  {op.stats && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-tedbot-gray-500">Candidates:</span>
                        <span className="font-semibold text-profit">{op.stats.candidates_found}</span>
                      </div>
                    </>
                  )}

                  {op.error && (
                    <div className="mt-2 p-2 bg-loss bg-opacity-10 border border-loss rounded text-xs text-loss">
                      {op.error}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <XCircle className="mx-auto mb-4 text-loss" size={48} />
            <p className="text-tedbot-gray-500">Failed to load operations status</p>
          </div>
        )}
      </div>

      {/* Activity Feed Preview */}
      <div className="glass rounded-lg p-6">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Activity size={20} />
          Recent Activity Stream
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

      {/*
        FUTURE ENHANCEMENT: Real-Time WebSocket Feed

        NOTE: This section is commented out but preserved for future development.

        WebSocket implementation would provide instant real-time updates instead of
        30-second polling, enabling:
        - Instant position updates and P&L changes
        - Real-time market scan progress
        - Live trade execution notifications with reasoning
        - Immediate stop loss adjustments and risk events
        - Learning loop completion alerts
        - Continuous system health metrics

        Implementation would require:
        1. WebSocket server endpoint in Flask backend
        2. Socket.io or native WebSocket connection in React
        3. Event streaming architecture from trading system
        4. Reconnection logic and error handling

        Uncomment the code below to restore the "Coming Soon" UI section:

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
      */}

      {/* Log Modal */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-80">
          <div className="glass rounded-lg max-w-5xl w-full max-h-[80vh] flex flex-col border-2 border-tedbot-accent">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-tedbot-gray-800">
              <h3 className="text-2xl font-bold text-tedbot-accent">
                {selectedLog} Output
                {logContent?.timestamp && (
                  <span className="ml-4 text-sm text-tedbot-gray-500">
                    {logContent.timestamp}
                  </span>
                )}
              </h3>
              <button
                onClick={closeLogModal}
                className="text-tedbot-gray-500 hover:text-white text-3xl font-bold leading-none"
              >
                ×
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6">
              {logLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin">
                    <RefreshCw size={48} className="text-tedbot-accent" />
                  </div>
                </div>
              ) : logContent?.error ? (
                <div className="p-4 bg-loss bg-opacity-10 border border-loss rounded">
                  <p className="text-loss">{logContent.error}</p>
                </div>
              ) : logContent?.content ? (
                <div className="bg-tedbot-darker rounded-lg p-4 font-mono text-sm text-tedbot-accent whitespace-pre-wrap overflow-x-auto">
                  {logContent.content}
                </div>
              ) : (
                <div className="text-center py-12 text-tedbot-gray-500">
                  No content available
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default LiveFeed
