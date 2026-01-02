import React from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { motion } from 'framer-motion'

function MetricCard({ title, value, change, subtitle, icon: Icon, trend = 'neutral', invertTrend = false }) {
  // Determine trend color
  let trendColor = 'text-tedbot-gray-500'
  let TrendIcon = Minus

  if (trend === 'up') {
    trendColor = invertTrend ? 'text-loss' : 'text-profit'
    TrendIcon = TrendingUp
  } else if (trend === 'down') {
    trendColor = invertTrend ? 'text-profit' : 'text-loss'
    TrendIcon = TrendingDown
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className="glass rounded-lg p-6 transition-all hover:shadow-lg"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-tedbot-gray-500 mb-2">{title}</p>
          <p className="text-3xl font-bold mb-1">{value}</p>
          {change !== undefined && (
            <div className={`flex items-center gap-1 text-sm ${trendColor}`}>
              <TrendIcon size={16} />
              <span>{change >= 0 ? '+' : ''}{change}%</span>
            </div>
          )}
          {subtitle && !change && (
            <p className="text-xs text-tedbot-gray-600 mt-1">{subtitle}</p>
          )}
        </div>
        {Icon && (
          <div className={`p-3 rounded-lg ${trendColor === 'text-profit' ? 'bg-profit/10' : trendColor === 'text-loss' ? 'bg-loss/10' : 'bg-tedbot-gray-800'}`}>
            <Icon className={trendColor} size={24} />
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default MetricCard
