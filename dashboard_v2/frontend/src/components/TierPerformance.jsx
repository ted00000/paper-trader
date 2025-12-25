import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

const COLORS = {
  'Tier 1': '#00f5ff',  // tedbot-accent
  'Tier 2': '#10b981',  // profit green
  'Tier 3': '#f59e0b',  // yellow
  'Unknown': '#6b7280'  // gray
}

function TierPerformance({ tierData }) {
  if (!tierData || tierData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-tedbot-gray-500">No tier data available</p>
      </div>
    )
  }

  // Format data for pie chart
  const chartData = tierData.map(item => ({
    name: item.name,
    value: item.total_trades,
    winRate: item.win_rate,
    avgReturn: item.avg_return
  }))

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="glass p-3 rounded-lg border border-tedbot-gray-800">
          <p className="font-bold text-tedbot-accent">{data.name}</p>
          <p className="text-sm text-tedbot-gray-400">Trades: {data.value}</p>
          <p className="text-sm text-tedbot-gray-400">Win Rate: {data.winRate}%</p>
          <p className={`text-sm ${data.avgReturn >= 0 ? 'text-profit' : 'text-loss'}`}>
            Avg Return: {data.avgReturn >= 0 ? '+' : ''}{data.avgReturn}%
          </p>
        </div>
      )
    }
    return null
  }

  const renderLegend = (props) => {
    const { payload } = props
    return (
      <div className="flex flex-col gap-2 mt-4">
        {payload.map((entry, index) => {
          const tierInfo = tierData.find(t => t.name === entry.value)
          return (
            <div key={`legend-${index}`} className="flex items-center justify-between p-2 bg-tedbot-darker rounded">
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-sm font-semibold">{entry.value}</span>
              </div>
              <div className="flex gap-4 text-xs text-tedbot-gray-400">
                <span>{tierInfo?.total_trades} trades</span>
                <span className={tierInfo?.win_rate >= 50 ? 'text-profit' : 'text-loss'}>
                  {tierInfo?.win_rate}% win
                </span>
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="40%"
          innerRadius={60}
          outerRadius={80}
          paddingAngle={2}
          dataKey="value"
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[entry.name] || COLORS['Unknown']} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend content={renderLegend} />
      </PieChart>
    </ResponsiveContainer>
  )
}

export default TierPerformance
