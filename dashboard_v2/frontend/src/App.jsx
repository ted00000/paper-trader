import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  TrendingUp,
  // Search, // Hidden for MVP - Trade Explorer not ready
  // Brain, // Hidden for MVP - Learning Engine not ready
  Shield,
  // Activity, // Hidden for MVP - Live Feed moved to Command Center
  // Globe // Hidden for MVP - Public View not needed (password-protected dashboard)
} from 'lucide-react'

// Pages
import CommandCenter from './pages/CommandCenter'
import Analytics from './pages/Analytics'
import TradeExplorer from './pages/TradeExplorer'
import LearningEngine from './pages/LearningEngine'
import RiskCommand from './pages/RiskCommand'
import LiveFeed from './pages/LiveFeed'
import PublicView from './pages/PublicView'

function App() {
  const navigation = [
    { name: 'Command Center', href: '/', icon: LayoutDashboard },
    { name: 'Analytics', href: '/analytics', icon: TrendingUp },

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

    { name: 'Risk Command', href: '/risk', icon: Shield },

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
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <img
                  src="/tedbot-logo.png"
                  alt="Tedbot Logo"
                  className="w-12 h-12 rounded-lg"
                />
                <div>
                  <h1 className="text-3xl font-bold gradient-text">Tedbot</h1>
                  <p className="text-sm text-tedbot-gray-500">Autonomous Trading Terminal</p>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-right">
                  <div className="text-sm text-tedbot-gray-500">Account Value</div>
                  <div className="text-2xl font-bold text-tedbot-accent">$1,234.56</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-tedbot-gray-500">Total Return</div>
                  <div className="text-2xl font-bold text-profit">+23.4%</div>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex gap-1 px-6 overflow-x-auto">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                      isActive
                        ? 'border-tedbot-accent text-tedbot-accent'
                        : 'border-transparent text-tedbot-gray-500 hover:text-white hover:border-tedbot-gray-700'
                    }`
                  }
                >
                  <Icon size={16} />
                  {item.name}
                </NavLink>
              )
            })}
          </nav>
        </header>

        {/* Main Content */}
        <main className="p-6">
          <Routes>
            <Route path="/" element={<CommandCenter />} />
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
