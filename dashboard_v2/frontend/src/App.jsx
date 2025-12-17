import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  TrendingUp,
  Search,
  Brain,
  Shield,
  Activity,
  Globe
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
    { name: 'Trade Explorer', href: '/trades', icon: Search },
    { name: 'Learning Engine', href: '/learning', icon: Brain },
    { name: 'Risk Command', href: '/risk', icon: Shield },
    { name: 'Live Feed', href: '/live', icon: Activity },
    { name: 'Public View', href: '/public', icon: Globe },
  ]

  return (
    <Router>
      <div className="min-h-screen bg-tedbot-dark">
        {/* Header */}
        <header className="bg-tedbot-darker border-b-2 border-tedbot-accent">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-tedbot-accent rounded-lg flex items-center justify-center">
                  <span className="text-2xl">🤖</span>
                </div>
                <div>
                  <h1 className="text-3xl font-bold gradient-text">TEDBOT</h1>
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
