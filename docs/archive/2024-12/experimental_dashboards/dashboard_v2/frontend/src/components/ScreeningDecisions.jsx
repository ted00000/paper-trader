import { useState, useEffect } from 'react'
import { Search, CheckCircle, XCircle, AlertCircle, PauseCircle } from 'lucide-react'

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

  const getDecisionIcon = (status) => {
    if (status === 'ACCEPTED') {
      return <CheckCircle size={18} className="text-profit" />
    } else if (status === 'SKIPPED') {
      return <PauseCircle size={18} className="text-yellow-500" />
    } else if (status === 'OWNED') {
      return <CheckCircle size={18} className="text-owned" />
    }
    return <XCircle size={18} className="text-loss" />
  }

  const getDecisionColor = (status) => {
    if (status === 'ACCEPTED') {
      return 'bg-profit/10 border-profit/30'
    } else if (status === 'SKIPPED') {
      return 'bg-yellow-500/10 border-yellow-500/30'
    } else if (status === 'OWNED') {
      return 'bg-owned/10 border-owned/30'
    }
    return 'bg-loss/5 border-loss/20'
  }

  const getStatusLabel = (status, decision) => {
    if (status === 'ACCEPTED') {
      return decision
    } else if (status === 'SKIPPED') {
      return 'Skipped'
    } else if (status === 'OWNED') {
      return 'Already Owned'
    }
    return 'Rejected'
  }

  const getStatusStyle = (status) => {
    if (status === 'ACCEPTED') {
      return 'bg-profit/20 text-profit'
    } else if (status === 'SKIPPED') {
      return 'bg-yellow-500/20 text-yellow-500'
    } else if (status === 'OWNED') {
      return 'bg-owned/20 text-owned'
    }
    return 'bg-loss/10 text-loss'
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

      <div className="space-y-2">
        {data.decisions.map((item, index) => (
          <div
            key={index}
            className={`p-3 rounded-lg border ${getDecisionColor(item.status)}`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {getDecisionIcon(item.status)}
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-base">{item.ticker}</span>
                    <span className="text-xs px-2 py-0.5 bg-tedbot-darker rounded">
                      Score: {item.score?.toFixed(1)}
                    </span>
                    {item.tier && item.tier !== 'N/A' && (
                      <span className="text-xs px-2 py-0.5 bg-tedbot-accent/20 text-tedbot-accent rounded">
                        {item.tier}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-tedbot-gray-400 mt-1">{item.reason}</p>
                </div>
              </div>
              <div className="ml-4 flex-shrink-0">
                <span className={`text-xs font-semibold px-2 py-1 rounded ${getStatusStyle(item.status)}`}>
                  {getStatusLabel(item.status, item.decision)}
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
