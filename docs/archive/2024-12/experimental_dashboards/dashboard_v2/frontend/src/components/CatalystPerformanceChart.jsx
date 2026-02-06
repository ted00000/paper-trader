import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

function CatalystPerformanceChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-tedbot-gray-500">
        No catalyst performance data available
      </div>
    )
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="glass rounded-lg p-4 border border-tedbot-gray-800">
          <p className="font-bold mb-2">{data.catalyst}</p>
          <div className="space-y-1 text-sm">
            <p className="text-tedbot-gray-400">
              Win Rate: <span className="text-white font-semibold">{data.win_rate.toFixed(1)}%</span>
            </p>
            <p className="text-tedbot-gray-400">
              Avg Return: <span className={`font-semibold ${data.avg_return >= 0 ? 'text-profit' : 'text-loss'}`}>
                {data.avg_return >= 0 ? '+' : ''}{data.avg_return.toFixed(2)}%
              </span>
            </p>
            <p className="text-tedbot-gray-400">
              Trades: <span className="text-white font-semibold">{data.trade_count}</span>
            </p>
          </div>
        </div>
      )
    }
    return null
  }

  // Custom bar colors based on performance
  const getBarColor = (value, index) => {
    if (value >= 60) return '#00ff41'  // Excellent win rate - bright green
    if (value >= 50) return '#00cc33'  // Good win rate - green
    if (value >= 40) return '#cccc00'  // Average - yellow
    return '#ff0033'  // Poor - red
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart
        data={data}
        margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
        <XAxis
          dataKey="catalyst"
          angle={-45}
          textAnchor="end"
          height={100}
          stroke="#737373"
          tick={{ fill: '#a3a3a3', fontSize: 12 }}
        />
        <YAxis
          stroke="#737373"
          tick={{ fill: '#a3a3a3', fontSize: 12 }}
          label={{ value: 'Win Rate (%)', angle: -90, position: 'insideLeft', fill: '#a3a3a3' }}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(38, 38, 38, 0.5)' }} />
        <Bar
          dataKey="win_rate"
          name="Win Rate (%)"
          radius={[8, 8, 0, 0]}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={getBarColor(entry.win_rate, index)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

export default CatalystPerformanceChart
