function CatalystBreakdown({ catalystData }) {
  if (!catalystData || catalystData.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-tedbot-gray-500">No catalyst data available</p>
      </div>
    )
  }

  // Map catalyst names to display-friendly names
  const catalystDisplayNames = {
    'earnings_beat': 'Earnings Beats',
    'sector_momentum': 'Sector Momentum',
    'technical_breakout': 'Technical Breakouts',
    'analyst_upgrade': 'Analyst Upgrades',
    'binary_event': 'Binary Events',
    'Earnings Beat': 'Earnings Beats',
    'Sector Momentum': 'Sector Momentum',
    'Technical Breakout': 'Technical Breakouts',
    'Analyst Upgrade': 'Analyst Upgrades',
    'Binary Event': 'Binary Events',
  }

  return (
    <div className="space-y-3">
      {catalystData.map((catalyst, index) => {
        const displayName = catalystDisplayNames[catalyst.name] || catalyst.name
        const count = catalyst.total_trades || 0

        return (
          <div
            key={index}
            className="flex items-center justify-between p-3 bg-tedbot-darker rounded-lg border border-tedbot-gray-800"
          >
            <span className="text-sm text-tedbot-gray-300">{displayName}</span>
            <span className="text-lg font-bold text-tedbot-accent">{count}</span>
          </div>
        )
      })}
    </div>
  )
}

export default CatalystBreakdown
