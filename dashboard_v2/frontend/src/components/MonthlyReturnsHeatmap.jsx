import React from 'react'

function MonthlyReturnsHeatmap({ data }) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="text-center py-12 text-tedbot-gray-500">
        No monthly returns data available
      </div>
    )
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  // Get unique years from data
  const years = Object.keys(data).sort().reverse() // Most recent first

  // Get color based on return percentage
  const getColor = (returnPct) => {
    if (returnPct === null || returnPct === undefined) {
      return 'bg-tedbot-gray-800'
    }

    const value = parseFloat(returnPct)

    // Strong positive (>5%)
    if (value >= 5) return 'bg-profit glow-green'
    // Good positive (2-5%)
    if (value >= 2) return 'bg-profit/80'
    // Slight positive (0-2%)
    if (value >= 0) return 'bg-profit/50'
    // Slight negative (0 to -2%)
    if (value >= -2) return 'bg-loss/50'
    // Bad negative (-2 to -5%)
    if (value >= -5) return 'bg-loss/80'
    // Strong negative (<-5%)
    return 'bg-loss glow-red'
  }

  const getTextColor = (returnPct) => {
    if (returnPct === null || returnPct === undefined) {
      return 'text-tedbot-gray-600'
    }

    const value = parseFloat(returnPct)
    if (Math.abs(value) >= 2) return 'text-white font-bold'
    return 'text-tedbot-gray-300'
  }

  return (
    <div className="overflow-x-auto">
      <div className="inline-block min-w-full">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="p-2 text-left text-sm font-semibold text-tedbot-gray-400 sticky left-0 bg-tedbot-dark">
                Year
              </th>
              {months.map(month => (
                <th key={month} className="p-2 text-center text-sm font-semibold text-tedbot-gray-400">
                  {month}
                </th>
              ))}
              <th className="p-2 text-center text-sm font-semibold text-tedbot-gray-400 border-l-2 border-tedbot-gray-700">
                YTD
              </th>
            </tr>
          </thead>
          <tbody>
            {years.map(year => {
              const yearData = data[year] || {}
              const ytd = yearData.ytd

              return (
                <tr key={year} className="border-t border-tedbot-gray-800">
                  <td className="p-2 text-sm font-bold text-tedbot-gray-300 sticky left-0 bg-tedbot-dark">
                    {year}
                  </td>
                  {months.map((month, index) => {
                    const monthValue = yearData[index]
                    return (
                      <td key={month} className="p-1">
                        <div
                          className={`
                            rounded p-2 text-center text-xs transition-all hover:scale-105 cursor-default
                            ${getColor(monthValue)}
                            ${getTextColor(monthValue)}
                          `}
                          title={monthValue !== null && monthValue !== undefined
                            ? `${month} ${year}: ${monthValue >= 0 ? '+' : ''}${monthValue.toFixed(2)}%`
                            : `${month} ${year}: No data`
                          }
                        >
                          {monthValue !== null && monthValue !== undefined
                            ? `${monthValue >= 0 ? '+' : ''}${monthValue.toFixed(1)}%`
                            : '-'
                          }
                        </div>
                      </td>
                    )
                  })}
                  <td className="p-1 border-l-2 border-tedbot-gray-700">
                    <div
                      className={`
                        rounded p-2 text-center text-xs font-bold transition-all
                        ${getColor(ytd)}
                        ${ytd >= 0 ? 'text-white' : 'text-white'}
                      `}
                      title={ytd !== null && ytd !== undefined
                        ? `${year} YTD: ${ytd >= 0 ? '+' : ''}${ytd.toFixed(2)}%`
                        : `${year} YTD: No data`
                      }
                    >
                      {ytd !== null && ytd !== undefined
                        ? `${ytd >= 0 ? '+' : ''}${ytd.toFixed(1)}%`
                        : '-'
                      }
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="mt-6 flex items-center justify-center gap-6 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-profit glow-green"></div>
          <span className="text-tedbot-gray-400">Strong Gain (&gt;5%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-profit/50"></div>
          <span className="text-tedbot-gray-400">Positive (0-2%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-tedbot-gray-800"></div>
          <span className="text-tedbot-gray-400">No Data</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-loss/50"></div>
          <span className="text-tedbot-gray-400">Negative (0 to -2%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-loss glow-red"></div>
          <span className="text-tedbot-gray-400">Strong Loss (&lt;-5%)</span>
        </div>
      </div>
    </div>
  )
}

export default MonthlyReturnsHeatmap
