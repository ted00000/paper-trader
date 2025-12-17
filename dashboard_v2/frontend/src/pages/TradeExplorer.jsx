import React from 'react'
import { Search, Filter, Download } from 'lucide-react'

function TradeExplorer() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Trade Explorer</h1>
          <p className="text-tedbot-gray-500">Search, filter, and analyze all trades</p>
        </div>
        <button className="glass px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-tedbot-gray-900 transition-colors">
          <Download size={18} />
          Export CSV
        </button>
      </div>

      {/* Search and Filters */}
      <div className="glass rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-tedbot-gray-500" size={18} />
            <input
              type="text"
              placeholder="Search by ticker..."
              className="w-full pl-10 pr-4 py-2 bg-tedbot-darker rounded-lg border border-tedbot-gray-800 focus:border-tedbot-accent focus:outline-none transition-colors"
            />
          </div>
          <select className="px-4 py-2 bg-tedbot-darker rounded-lg border border-tedbot-gray-800 focus:border-tedbot-accent focus:outline-none transition-colors">
            <option>All Catalysts</option>
            <option>Earnings</option>
            <option>Breakout</option>
            <option>Unusual Volume</option>
            <option>Sector Rotation</option>
          </select>
          <select className="px-4 py-2 bg-tedbot-darker rounded-lg border border-tedbot-gray-800 focus:border-tedbot-accent focus:outline-none transition-colors">
            <option>All Results</option>
            <option>Winners Only</option>
            <option>Losers Only</option>
          </select>
        </div>
      </div>

      {/* Coming Soon Placeholder */}
      <div className="glass rounded-lg p-12 text-center">
        <Filter className="mx-auto mb-4 text-tedbot-accent" size={64} />
        <h3 className="text-2xl font-bold mb-2">Advanced Trade Explorer</h3>
        <p className="text-tedbot-gray-500 mb-6">
          Interactive table with sorting, filtering, and detailed trade analytics
        </p>
        <div className="space-y-2 text-sm text-tedbot-gray-600">
          <p>• Full trade history with all 63 CSV columns</p>
          <p>• Multi-dimensional filtering (catalyst, sector, conviction, result)</p>
          <p>• Sortable columns with performance metrics</p>
          <p>• Detailed trade cards with entry/exit analysis</p>
          <p>• Export capabilities for further analysis</p>
        </div>
      </div>
    </div>
  )
}

export default TradeExplorer
