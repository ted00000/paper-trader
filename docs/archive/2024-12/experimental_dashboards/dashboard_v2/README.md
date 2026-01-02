# TEDBOT Dashboard v2.0 - Professional Trading Terminal

Modern, professional dashboard for the TEDBOT autonomous trading system. Built with React, Flask, and TailwindCSS.

## 🎯 Features

- **Command Center**: Real-time account overview with key metrics, equity curve, and position tracking
- **Analytics**: Deep dive into performance by catalyst, sector, and time period
- **Trade Explorer**: Search, filter, and analyze complete trade history
- **Learning Engine**: Visualization of autonomous learning system insights
- **Risk Command**: Real-time risk monitoring and position management
- **Live Feed**: Real-time trading activity stream (WebSocket)
- **Public View**: Clean, read-only showcase dashboard

## 🏗️ Architecture

### Backend (Flask API)
- **Read-only API** - Never writes to trading system files
- **Port 5001** - Separate from main trading logic
- **8 REST Endpoints** - Comprehensive data access
- **CORS Enabled** - For React frontend integration

### Frontend (React + Vite)
- **React 18** - Modern component-based UI
- **Vite** - Lightning-fast development and builds
- **TailwindCSS** - Utility-first styling with custom Tedbot theme
- **Recharts** - Professional financial charting
- **Framer Motion** - Smooth animations and transitions
- **Axios** - API communication

## 🚀 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd dashboard_v2/backend
pip install flask flask-cors
python api_enhanced.py
```

Backend will run on `http://localhost:5001`

### Frontend Setup

```bash
cd dashboard_v2/frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:3000`

## 📁 Project Structure

```
dashboard_v2/
├── backend/
│   └── api_enhanced.py          # Flask API with 8 endpoints
└── frontend/
    ├── index.html               # HTML entry point
    ├── package.json             # Dependencies
    ├── vite.config.js           # Vite configuration
    ├── tailwind.config.js       # TailwindCSS theme
    ├── postcss.config.js        # PostCSS setup
    └── src/
        ├── main.jsx             # React entry point
        ├── App.jsx              # Main app with routing
        ├── styles/
        │   └── index.css        # Custom theme and animations
        ├── components/
        │   ├── MetricCard.jsx
        │   ├── EquityCurveChart.jsx
        │   ├── RecentTradesTable.jsx
        │   ├── ActivePositionsGrid.jsx
        │   └── MarketRegimeIndicator.jsx
        └── pages/
            ├── CommandCenter.jsx    # Main dashboard
            ├── Analytics.jsx        # Performance analytics
            ├── TradeExplorer.jsx    # Trade search/filter
            ├── LearningEngine.jsx   # Learning insights
            ├── RiskCommand.jsx      # Risk monitoring
            ├── LiveFeed.jsx         # Real-time activity
            └── PublicView.jsx       # Public showcase
```

## 🎨 Design System

### Colors (Tedbot Theme)
- **Background**: `#0a0a0a` (tedbot-dark)
- **Panels**: `#050505` (tedbot-darker)
- **Accent**: `#00ff41` (tedbot-accent / profit)
- **Loss**: `#ff0033`
- **Gray Scale**: 50-900

### Key Visual Elements
- Glass morphism panels with backdrop blur
- Gradient text for branding
- Custom scrollbars
- Number flash animations (green/red)
- Responsive grid layouts
- Smooth transitions and hover effects

## 🔌 API Endpoints

1. **GET /api/v2/overview** - Command center metrics (account, performance, trades, positions)
2. **GET /api/v2/equity-curve** - Equity curve data with drawdown analysis
3. **GET /api/v2/catalyst-performance** - Performance by catalyst/tier/conviction
4. **GET /api/v2/trades** - Filtered trade history (params: limit, catalyst, outcome)
5. **GET /api/v2/risk/positions** - Current position risk metrics
6. **GET /api/v2/analytics/monthly-returns** - Monthly return heatmap data
7. **GET /api/v2/learning/insights** - Learning system metrics
8. **GET /api/v2/health** - System health check

## 🛠️ Development

### Run Both Servers

**Terminal 1 - Backend:**
```bash
cd dashboard_v2/backend
python api_enhanced.py
```

**Terminal 2 - Frontend:**
```bash
cd dashboard_v2/frontend
npm run dev
```

### Build for Production

```bash
cd dashboard_v2/frontend
npm run build
```

Optimized static files will be in `frontend/dist/`

## 📊 Components

### MetricCard
Reusable card for displaying key metrics with optional trend indicators and change percentages.

### EquityCurveChart
Professional Recharts area chart with gradient fills, custom tooltips, and drawdown shading.

### RecentTradesTable
Compact table showing recent trades with profit/loss indicators, catalyst info, and hold days.

### ActivePositionsGrid
Grid display of current positions with unrealized P&L, entry/current prices, and days held.

### MarketRegimeIndicator
Market regime status with VIX, trend, SPY performance, sector breadth, and risk signals.

## 🔄 Real-Time Updates (Planned)

The dashboard is designed for 30-second polling by default. WebSocket support for true real-time updates is planned:
- Live position P&L updates
- Trade execution notifications
- Market scan progress
- Learning loop completions

## 🎯 MVP vs Full Features

### ✅ MVP Complete (Current)
- Read-only Flask API
- React app structure with routing
- Command Center page with all components
- Professional Tedbot theme and styling
- Responsive design foundation
- All placeholder pages created

### 🚧 Coming Soon
- WebSocket real-time updates
- Advanced analytics charts (catalyst bar charts, monthly heatmaps)
- Interactive trade explorer with filtering
- Learning engine visualizations
- Risk command live monitoring
- Mobile app (PWA)

## 🔒 Security Notes

- **Read-Only API**: Backend only reads data files, never writes
- **No Trading Control**: Dashboard cannot execute trades or modify system
- **CORS Limited**: Configure allowed origins for production
- **No Auth (MVP)**: Add authentication for production deployment

## 🤝 Contributing

This dashboard is part of the TEDBOT autonomous trading system. Changes should:
- Never affect backend trading logic
- Maintain read-only data access
- Follow the established Tedbot design system
- Be responsive and accessible

## 📝 License

Part of the TEDBOT trading system. For internal use during validation period.

## 🎨 Brand

- **Name**: TEDBOT
- **Tagline**: Autonomous Trading System
- **Colors**: Dark theme with bright green (#00ff41) accents
- **Aesthetic**: Professional trader terminal, Bloomberg-inspired

---

Built with ❤️ for autonomous trading excellence.
