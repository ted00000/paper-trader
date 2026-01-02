import React, { useState, useEffect } from 'react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts'
import axios from 'axios'
import { format, parseISO } from 'date-fns'

function EquityCurveChart({ period = 'all' }) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    fetchEquityCurve()
  }, [period])

  const fetchEquityCurve = async () => {
    try {
      const response = await axios.get(`/api/v2/equity-curve?period=${period}`)
      setData(response.data.equity_curve)
      setStats({
        starting: response.data.starting_value,
        current: response.data.current_value,
        return_pct: response.data.total_return_pct
      })
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch equity curve:', error)
      setLoading(false)
    }
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-tedbot-darker border border-tedbot-gray-700 rounded-lg p-3 shadow-xl">
          <p className="text-sm text-tedbot-gray-400 mb-1">
            {format(parseISO(data.date), 'MMM dd, yyyy')}
          </p>
          <p className="text-lg font-bold text-tedbot-accent">
            ${data.value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          {data.drawdown_pct > 0 && (
            <p className="text-sm text-loss mt-1">
              Drawdown: -{data.drawdown_pct.toFixed(2)}%
            </p>
          )}
        </div>
      )
    }
    return null
  }

  if (loading) {
    return (
      <div className="h-80 flex items-center justify-center">
        <div className="shimmer w-full h-full rounded-lg"></div>
      </div>
    )
  }

  if (!data.length) {
    return (
      <div className="h-80 flex items-center justify-center">
        <p className="text-tedbot-gray-500">No equity data available</p>
      </div>
    )
  }

  return (
    <div>
      {/* Stats Bar */}
      {stats && (
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-tedbot-gray-800">
          <div>
            <p className="text-sm text-tedbot-gray-500">Starting Value</p>
            <p className="text-xl font-bold">${stats.starting.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-tedbot-gray-500">Current Value</p>
            <p className="text-xl font-bold text-tedbot-accent">${stats.current.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-tedbot-gray-500">Total Return</p>
            <p className={`text-xl font-bold ${stats.return_pct >= 0 ? 'text-profit' : 'text-loss'}`}>
              {stats.return_pct >= 0 ? '+' : ''}{stats.return_pct.toFixed(2)}%
            </p>
          </div>
        </div>
      )}

      {/* Chart */}
      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00ff41" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#00ff41" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ff0033" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#ff0033" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
          <XAxis
            dataKey="date"
            stroke="#525252"
            tickFormatter={(value) => format(parseISO(value), 'MMM dd')}
            tick={{ fill: '#737373' }}
          />
          <YAxis
            stroke="#525252"
            tickFormatter={(value) => `$${value.toLocaleString()}`}
            tick={{ fill: '#737373' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={1000} stroke="#404040" strokeDasharray="3 3" />

          {/* Drawdown area (below peak) */}
          <Area
            type="monotone"
            dataKey="peak"
            stroke="none"
            fill="url(#drawdownGradient)"
            fillOpacity={0.5}
          />

          {/* Equity line */}
          <Area
            type="monotone"
            dataKey="value"
            stroke="#00ff41"
            strokeWidth={3}
            fill="url(#equityGradient)"
            animationDuration={1500}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export default EquityCurveChart
