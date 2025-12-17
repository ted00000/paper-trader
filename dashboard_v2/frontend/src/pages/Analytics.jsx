import React from 'react'
import { TrendingUp, BarChart3, PieChart, Calendar } from 'lucide-react'

function Analytics() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Analytics Deep Dive</h1>
        <p className="text-tedbot-gray-500">Advanced performance analytics and insights</p>
      </div>

      {/* Coming Soon Placeholder */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass rounded-lg p-8 text-center">
          <BarChart3 className="mx-auto mb-4 text-tedbot-accent" size={48} />
          <h3 className="text-xl font-bold mb-2">Catalyst Performance</h3>
          <p className="text-tedbot-gray-500">Performance breakdown by catalyst type and tier</p>
        </div>

        <div className="glass rounded-lg p-8 text-center">
          <Calendar className="mx-auto mb-4 text-tedbot-accent" size={48} />
          <h3 className="text-xl font-bold mb-2">Monthly Returns</h3>
          <p className="text-tedbot-gray-500">Calendar heatmap of monthly performance</p>
        </div>

        <div className="glass rounded-lg p-8 text-center">
          <PieChart className="mx-auto mb-4 text-tedbot-accent" size={48} />
          <h3 className="text-xl font-bold mb-2">Sector Allocation</h3>
          <p className="text-tedbot-gray-500">Distribution across sectors and industries</p>
        </div>

        <div className="glass rounded-lg p-8 text-center">
          <TrendingUp className="mx-auto mb-4 text-tedbot-accent" size={48} />
          <h3 className="text-xl font-bold mb-2">Hold Time Analysis</h3>
          <p className="text-tedbot-gray-500">Performance by hold duration</p>
        </div>
      </div>

      <div className="glass rounded-lg p-6 text-center">
        <p className="text-tedbot-gray-400">
          Advanced analytics visualizations coming soon...
        </p>
      </div>
    </div>
  )
}

export default Analytics
