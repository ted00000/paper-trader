import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts'

function PerformanceDonutChart({ performance }) {
  if (!performance) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-tedbot-gray-500">No performance data available</p>
      </div>
    )
  }

  const { total_trades, win_rate } = performance
  const winners = Math.round((win_rate / 100) * total_trades)
  const losers = total_trades - winners
  const openPositions = 0 // We'll get this from positions data if needed

  const data = [
    { name: 'Winners', value: winners, color: '#10b981' }, // green
    { name: 'Losers', value: losers, color: '#ef4444' },   // red
    { name: 'Open Positions', value: openPositions, color: '#6b7280' } // gray
  ].filter(item => item.value > 0) // Only show non-zero values

  const COLORS = data.map(item => item.color)

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={2}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index]} />
            ))}
          </Pie>
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value, entry) => (
              <span className="text-sm text-tedbot-gray-400">
                {value}: {entry.payload.value}
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PerformanceDonutChart
