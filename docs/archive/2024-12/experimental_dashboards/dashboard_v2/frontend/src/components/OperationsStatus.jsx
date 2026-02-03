import { useState, useEffect } from 'react'
import { Activity, CheckCircle2, XCircle, AlertCircle, Eye, RefreshCw } from 'lucide-react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import rehypeRaw from 'rehype-raw'

function OperationsStatus({ isSuperUser = false }) {
  const [operationsData, setOperationsData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedLog, setSelectedLog] = useState(null)
  const [logContent, setLogContent] = useState(null)
  const [logLoading, setLogLoading] = useState(false)

  // Format GO output for better readability
  const formatGoOutput = (content) => {
    if (!content) return content

    let formatted = content

    // Style ENTER decisions - pattern: **TICKER (Sector) - ENTER**
    formatted = formatted.replace(
      /\*\*([A-Z]+)\s*\(([^)]+)\)\s*-\s*ENTER\*\*/g,
      '<span class="ticker-name">$1</span> ($2) - <span class="decision-enter">ENTER</span>'
    )

    // Style PASS decisions - pattern: **TICKER (Sector) - PASS**
    formatted = formatted.replace(
      /\*\*([A-Z]+)\s*\(([^)]+)\)\s*-\s*PASS\*\*/g,
      '<span class="ticker-name">$1</span> ($2) - <span class="decision-pass">PASS</span>'
    )

    // Also handle PASS in "Other Candidates" section
    formatted = formatted.replace(
      /\*\*Other Candidates.*?PASS\*\*/g,
      (match) => match.replace('PASS', '<span class="decision-pass">PASS</span>')
    )

    return formatted
  }

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

  // Define operation order (RECHECK follows EXECUTE as it's the 10:15 AM gap re-check, EXIT at 3:45 PM before ANALYZE)
  const operationOrder = ['SCREENER', 'GO', 'EXECUTE', 'RECHECK', 'EXIT', 'ANALYZE']

  // Sort operations by defined order
  const sortedOperations = operationsData ?
    operationOrder
      .filter(op => operationsData.operations[op])
      .map(op => [op, operationsData.operations[op]])
    : []

  return (
    <>
      <div className="glass rounded-lg p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
          <h3 className="text-lg sm:text-xl font-bold flex items-center gap-2">
            <Activity size={20} />
            System Operations Status
          </h3>
          <div className="flex items-center gap-2 sm:gap-4">
            {operationsData && (
              <div className={`flex items-center gap-2 glass px-3 sm:px-4 py-2 rounded-lg border ${
                operationsData.health === 'HEALTHY' ? 'border-profit' :
                operationsData.health === 'WARNING' ? 'border-yellow-500' :
                'border-loss'
              }`}>
                <div className={`w-2 h-2 rounded-full animate-pulse ${
                  operationsData.health === 'HEALTHY' ? 'bg-profit' :
                  operationsData.health === 'WARNING' ? 'bg-yellow-500' :
                  'bg-loss'
                }`}></div>
                <span className={`text-xs sm:text-sm font-semibold ${
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
              className="flex items-center gap-2 px-3 sm:px-4 py-2 bg-tedbot-darker rounded-lg border border-tedbot-gray-800 hover:border-tedbot-accent transition-colors whitespace-nowrap"
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
              <span className="text-sm">Refresh</span>
            </button>
          </div>
        </div>

        {loading && !operationsData ? (
          <div className="text-center py-8">
            <div className="animate-pulse">
              <Activity className="mx-auto mb-4 text-tedbot-accent" size={48} />
              <p className="text-tedbot-gray-500">Loading operations status...</p>
            </div>
          </div>
        ) : operationsData ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            {sortedOperations.map(([name, op]) => (
              <div
                key={name}
                onClick={isSuperUser ? () => viewLog(name) : undefined}
                className={`bg-tedbot-darker rounded-lg p-4 border-l-4 ${getHealthColor(op.health)} transition-all ${isSuperUser ? 'cursor-pointer hover:shadow-lg hover:border-tedbot-accent' : ''}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    {getHealthIcon(op.health)}
                    <div>
                      <h4 className="font-bold text-sm">{name}</h4>
                      <p className="text-xs text-tedbot-gray-500">{op.status}</p>
                    </div>
                  </div>
                  {isSuperUser && <Eye size={16} className="text-tedbot-gray-500" />}
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
                <div className="bg-tedbot-darker rounded-lg p-6 prose prose-invert prose-sm max-w-none overflow-x-auto go-output">
                  <ReactMarkdown rehypePlugins={[rehypeRaw]}>
                    {selectedLog === 'GO' ? formatGoOutput(logContent.content) : logContent.content}
                  </ReactMarkdown>
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
    </>
  )
}

export default OperationsStatus
