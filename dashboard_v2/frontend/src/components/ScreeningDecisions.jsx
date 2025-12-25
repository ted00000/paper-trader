import { useState, useEffect } from 'react'
import { Search, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react'

function ScreeningDecisions() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDecisions()
  }, [])

  const fetchDecisions = async () => {
    try {
      const response = await fetch('/api/v2/screening-decisions')
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error('Failed to fetch screening decisions:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="glass rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Search className="text-tedbot-accent" size={24} />
          <h2 className="text-xl font-bold">Today's Screening Decisions</h2>
        </div>
        <div className="text-center py-8 text-tedbot-gray-500">
          Loading screening decisions...
        </div>
      </div>
    )
  }

  if (!data || data.decisions.length === 0) {
    return (
      <div className="glass rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Search className="text-tedbot-accent" size={24} />
          <h2 className="text-xl font-bold">Today's Screening Decisions</h2>
        </div>
        <div className="text-center py-8">
          <AlertCircle className="mx-auto mb-3 text-tedbot-gray-500" size={40} />
          <p className="text-tedbot-gray-500">{data?.summary || 'No screening data available'}</p>
          {!data?.is_today && (
            <p className="text-xs text-tedbot-gray-600 mt-2">
              Last screening: {data?.timestamp}
            </p>
          )}
        </div>
      </div>
    )
  }

  const getDecisionIcon = (decision) => {
    switch (decision) {
      case 'Selected':
        return <CheckCircle size={18} className="text-profit" />
      case 'On Hold':
        return <Clock size={18} className="text-yellow-500" />
      case 'Passed':
      default:
        return <XCircle size={18} className="text-tedbot-gray-500" />
    }
  }

  const getDecisionColor = (decision) => {
    switch (decision) {
      case 'Selected':
        return 'bg-profit/10 border-profit/30 text-profit'
      case 'On Hold':
        return 'bg-yellow-500/10 border-yellow-500/30 text-yellow-500'
      case 'Passed':
      default:
        return 'bg-tedbot-gray-800/30 border-tedbot-gray-800 text-tedbot-gray-400'
    }
  }

  return (
    <div className="glass rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Search className="text-tedbot-accent" size={24} />
          <div>
            <h2 className="text-xl font-bold">Today's Screening Decisions</h2>
            <p className="text-sm text-tedbot-gray-500">{data.summary}</p>
          </div>
        </div>
        {!data.is_today && (
          <span className="text-xs text-tedbot-gray-600">
            Last screening: {data.timestamp}
          </span>
        )}
      </div>

      <div className="space-y-3">
        {data.decisions.map((item, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg border ${getDecisionColor(item.decision)}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className="mt-1">{getDecisionIcon(item.decision)}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-lg">{item.ticker}</span>
                    <span className="text-xs px-2 py-1 bg-tedbot-darker rounded">
                      Score: {item.score?.toFixed(1)}
                    </span>
                  </div>
                  <p className="text-sm opacity-90">{item.reason}</p>
                </div>
              </div>
              <div className="ml-4">
                <span className={`text-xs font-semibold px-2 py-1 rounded ${
                  item.decision === 'Selected' ? 'bg-profit/20' :
                  item.decision === 'On Hold' ? 'bg-yellow-500/20' :
                  'bg-tedbot-gray-700'
                }`}>
                  {item.decision}
                </span>
              </div>
            </div>
          </div>
        ))}

        {data.total_reviewed > data.decisions.length && (
          <p className="text-center text-xs text-tedbot-gray-600 pt-2">
            Showing top {data.decisions.length} of {data.total_reviewed} stocks reviewed
          </p>
        )}
      </div>
    </div>
  )
}

export default ScreeningDecisions
