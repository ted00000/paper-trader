function ConvictionDistribution({ convictionData }) {
  if (!convictionData || convictionData.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-tedbot-gray-500">No conviction data available</p>
      </div>
    )
  }

  // Map conviction levels to display data
  const convictionMap = {
    'HIGH': { label: 'HIGH Conviction', color: 'text-loss' },
    'MEDIUM': { label: 'MEDIUM Conviction', color: 'text-yellow-500' },
    'LOW': { label: 'LOW Conviction', color: 'text-tedbot-gray-500' },
    'SKIP': { label: 'SKIP (Learning)', color: 'text-tedbot-gray-600' }
  }

  // Get counts for each level
  const highCount = convictionData.find(c => c.name === 'HIGH')?.total_trades || 0
  const mediumCount = convictionData.find(c => c.name === 'MEDIUM')?.total_trades || 0
  const lowCount = convictionData.find(c => c.name === 'LOW')?.total_trades || 0
  const skipCount = convictionData.find(c => c.name === 'SKIP')?.total_trades || 0

  return (
    <div className="grid grid-cols-4 gap-4 text-center">
      <div>
        <div className={`text-4xl font-bold ${convictionMap['HIGH'].color} mb-2`}>
          {highCount}
        </div>
        <div className="text-sm text-tedbot-gray-400">
          {convictionMap['HIGH'].label}
        </div>
      </div>

      <div>
        <div className={`text-4xl font-bold ${convictionMap['MEDIUM'].color} mb-2`}>
          {mediumCount}
        </div>
        <div className="text-sm text-tedbot-gray-400">
          {convictionMap['MEDIUM'].label}
        </div>
      </div>

      <div>
        <div className={`text-4xl font-bold ${convictionMap['LOW'].color} mb-2`}>
          {lowCount}
        </div>
        <div className="text-sm text-tedbot-gray-400">
          {convictionMap['LOW'].label}
        </div>
      </div>

      <div>
        <div className={`text-4xl font-bold ${convictionMap['SKIP'].color} mb-2`}>
          {skipCount}
        </div>
        <div className="text-sm text-tedbot-gray-400">
          {convictionMap['SKIP'].label}
        </div>
      </div>
    </div>
  )
}

export default ConvictionDistribution
