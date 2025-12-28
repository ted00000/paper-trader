import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import {
  LayoutDashboard,
  Calendar,
  TrendingUp,
  LogOut,
  // Search, // Hidden for MVP - Trade Explorer not ready
  // Brain, // Hidden for MVP - Learning Engine not ready
  // Shield, // Hidden for MVP - Risk Command contains proprietary strategy info
  // Activity, // Hidden for MVP - Live Feed moved to Command Center
  // Globe // Hidden for MVP - Public View not needed (password-protected dashboard)
} from 'lucide-react'

// Pages
import Login from './pages/Login'
import CommandCenter from './pages/CommandCenter'
import Today from './pages/Today'
import Analytics from './pages/Analytics'
import TradeExplorer from './pages/TradeExplorer'
import LearningEngine from './pages/LearningEngine'
import RiskCommand from './pages/RiskCommand'
import LiveFeed from './pages/LiveFeed'
import PublicView from './pages/PublicView'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isSuperUser, setIsSuperUser] = useState(false)
  const [loading, setLoading] = useState(true)
  const [headerData, setHeaderData] = useState({ value: 0, return: 0 })

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('tedbot_session')
      if (token) {
        try {
          const response = await fetch('/api/v2/auth/verify', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          if (response.ok) {
            const data = await response.json()
            setIsAuthenticated(true)
            setIsSuperUser(data.is_super_user || false)
          } else {
            localStorage.removeItem('tedbot_session')
          }
        } catch (error) {
          console.error('Auth check failed:', error)
          localStorage.removeItem('tedbot_session')
        }
      }
      setLoading(false)
    }
    checkAuth()
  }, [])

  const handleLogin = (token, is_super_user) => {
    setIsAuthenticated(true)
    setIsSuperUser(is_super_user || false)
  }

  const handleLogout = () => {
    localStorage.removeItem('tedbot_session')
    setIsAuthenticated(false)
  }

  // Fetch header data when authenticated
  useEffect(() => {
    if (!isAuthenticated) return

    const fetchHeaderData = async () => {
      try {
        const response = await fetch('/api/v2/overview')
        const data = await response.json()
        setHeaderData({
          value: data.account?.value || 0,
          return: data.account?.total_return_pct || 0
        })
      } catch (error) {
        console.error('Failed to fetch header data:', error)
      }
    }

    fetchHeaderData()
    const interval = setInterval(fetchHeaderData, 30000) // Update every 30s
    return () => clearInterval(interval)
  }, [isAuthenticated])

  if (loading) {
    return (
      <div className="min-h-screen bg-tedbot-dark flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-tedbot-accent border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-tedbot-gray-500">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />
  }

  const navigation = [
    { name: 'Command Center', href: '/', icon: LayoutDashboard },
    { name: 'Today', href: '/today', icon: Calendar },
    { name: 'Analytics', href: '/analytics', icon: TrendingUp },

    // HIDDEN FOR MVP: Risk Command - Contains proprietary strategy information
    // { name: 'Risk Command', href: '/risk', icon: Shield },
    // TODO: Review for future use - contains sensitive data:
    //   - Max position size (10% rule)
    //   - Max portfolio heat (80% limit)
    //   - Max concurrent positions (10 positions)
    //   - Stop loss strategy details
    //   - Diversification rules
    // Consider: Keep metrics (Portfolio Health, Max Drawdown, Risk Utilization)
    // Remove: Position Limits, Stop Loss Protection, Diversification sections

    // HIDDEN FOR MVP: Trade Explorer - Not ready for public launch
    // { name: 'Trade Explorer', href: '/trades', icon: Search },
    // TODO: Re-enable when trade explorer is functional:
    //   - Connect to /api/v2/trades endpoint
    //   - Build interactive sortable table
    //   - Implement search and filter functionality
    //   - Add detailed trade card view
    //   - Enable CSV export
    //   Note: Command Center already shows recent trades (sufficient for MVP)

    // HIDDEN FOR MVP: Learning Engine - Not ready for public launch
    // { name: 'Learning Engine', href: '/learning', icon: Brain },
    // TODO: Re-enable when learning system data is available:
    //   - Connect to real learning metrics API
    //   - Remove hardcoded placeholder values
    //   - Build actual visualization charts
    //   - Implement daily/weekly/monthly learning loops display

    // HIDDEN FOR MVP: Live Feed - Operations monitoring moved to Command Center
    // { name: 'Live Feed', href: '/live', icon: Activity },
    // TODO: Re-enable when real-time activity stream is implemented:
    //   - Build WebSocket server endpoint for live event streaming
    //   - Implement real-time activity event tracking from trading system
    //   - Connect to position updates, scan progress, execution events
    //   - Add reconnection logic and error handling
    //   Note: System Operations Status now displayed at top of Command Center

    // HIDDEN FOR MVP: Public View - Not needed since entire dashboard will be password protected
    // { name: 'Public View', href: '/public', icon: Globe },
    // TODO: Re-enable if public sharing becomes a requirement:
    //   - Consider use case: sharing performance with investors/friends/family
    //   - May need different data permissions (hide sensitive operations data)
    //   - Could be useful for marketing/portfolio showcase
    //   - Alternative: Screenshot/PDF export of key metrics instead
    //   Note: Current plan is single password-protected dashboard for MVP
  ]

  return (
    <Router>
      <div className="min-h-screen bg-tedbot-dark">
        {/* Header */}
        <header className="bg-tedbot-darker border-b-2 border-tedbot-accent">
          <div className="px-4 sm:px-6 py-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="flex items-center gap-3 sm:gap-4">
                <img
                  src="/tedbot-logo.png"
                  alt="Tedbot Logo"
                  className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg"
                />
                <div>
                  <h1 className="text-2xl sm:text-3xl font-bold gradient-text">Tedbot</h1>
                  <p className="text-xs sm:text-sm text-tedbot-gray-500">Autonomous Trading Terminal</p>
                </div>
              </div>

              <div className="flex items-center justify-between sm:justify-end gap-3 sm:gap-6">
                <div className="text-left sm:text-right">
                  <div className="text-xs sm:text-sm text-tedbot-gray-500">Account Value</div>
                  <div className="text-lg sm:text-2xl font-bold text-tedbot-accent">
                    ${headerData.value.toFixed(2)}
                  </div>
                </div>
                <div className="text-left sm:text-right">
                  <div className="text-xs sm:text-sm text-tedbot-gray-500">Total Return</div>
                  <div className={`text-lg sm:text-2xl font-bold ${headerData.return >= 0 ? 'text-profit' : 'text-loss'}`}>
                    {headerData.return >= 0 ? '+' : ''}{headerData.return.toFixed(2)}%
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-3 sm:px-4 py-2 bg-tedbot-darker border border-tedbot-gray-800 rounded-lg hover:border-loss hover:text-loss transition-colors whitespace-nowrap"
                  title="Sign out"
                >
                  <LogOut size={16} className="sm:w-[18px] sm:h-[18px]" />
                  <span className="text-xs sm:text-sm">Logout</span>
                </button>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex gap-1 px-4 sm:px-6 overflow-x-auto scrollbar-hide">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-3 sm:px-4 py-3 text-xs sm:text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                      isActive
                        ? 'border-tedbot-accent text-tedbot-accent'
                        : 'border-transparent text-tedbot-gray-500 hover:text-white hover:border-tedbot-gray-700'
                    }`
                  }
                >
                  <Icon size={14} className="sm:w-4 sm:h-4" />
                  {item.name}
                </NavLink>
              )
            })}
          </nav>
        </header>

        {/* Main Content */}
        <main className="p-6">
          <Routes>
            <Route path="/" element={<CommandCenter isSuperUser={isSuperUser} />} />
            <Route path="/today" element={<Today />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/trades" element={<TradeExplorer />} />
            <Route path="/learning" element={<LearningEngine />} />
            <Route path="/risk" element={<RiskCommand />} />
            <Route path="/live" element={<LiveFeed />} />
            <Route path="/public" element={<PublicView />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
