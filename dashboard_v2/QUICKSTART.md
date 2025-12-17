# TEDBOT Dashboard v2.0 - Quick Start Guide

Get the professional trading terminal running in 5 minutes.

## 🚀 Quick Installation

### Step 1: Install Dependencies

**Backend (Flask):**
```bash
cd dashboard_v2/backend
pip install flask flask-cors
```

**Frontend (React):**
```bash
cd dashboard_v2/frontend
npm install
```

### Step 2: Start Both Servers

**Terminal 1 - Start Backend API:**
```bash
cd dashboard_v2/backend
python api_enhanced.py
```

You should see:
```
 * Running on http://127.0.0.1:5001
```

**Terminal 2 - Start Frontend Dev Server:**
```bash
cd dashboard_v2/frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

### Step 3: Open Dashboard

Navigate to: **http://localhost:3000**

## 🎯 What You'll See

### Command Center (Home Page)
- **Account Overview**: Total value, cash, invested, returns
- **Performance Metrics**: Trades, win rate, Sharpe ratio, max drawdown
- **Equity Curve**: Beautiful chart showing account growth
- **Recent Trades**: Last 5 completed trades with P&L
- **Active Positions**: Current holdings with unrealized P&L
- **Market Regime**: Current market conditions and signals

### Navigation Pages
- **Analytics**: Performance deep dive (placeholder)
- **Trade Explorer**: Search and filter trades (placeholder)
- **Learning Engine**: Autonomous learning insights (placeholder)
- **Risk Command**: Risk monitoring dashboard (placeholder)
- **Live Feed**: Real-time activity stream (placeholder)
- **Public View**: Clean showcase dashboard

## 🔧 Troubleshooting

### Backend Won't Start
**Error**: `ModuleNotFoundError: No module named 'flask'`
**Fix**: `pip install flask flask-cors`

**Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'portfolio_data/current_portfolio.json'`
**Fix**: Run from the `paper_trading_lab` root directory, not from `dashboard_v2/backend`

### Frontend Won't Start
**Error**: `command not found: npm`
**Fix**: Install Node.js from https://nodejs.org/

**Error**: `Cannot find module 'react'`
**Fix**: Run `npm install` in the `dashboard_v2/frontend` directory

### API Connection Issues
**Error**: Network errors or empty data
**Fix**:
1. Verify backend is running on port 5001
2. Check CORS is enabled in `api_enhanced.py`
3. Verify Vite proxy is configured in `vite.config.js`

### Port Already in Use
**Error**: `Address already in use`
**Fix**:
- Backend: Change port in `api_enhanced.py` (line with `app.run(port=5001)`)
- Frontend: Vite will auto-increment to 3001, 3002, etc.

## 📊 Sample Data

The dashboard reads from your existing Tedbot data files:
- `portfolio_data/current_portfolio.json` - Current positions
- `portfolio_data/account_info.json` - Account balance
- `trade_logs/*.csv` - Historical trades

Make sure you have trading data before starting the dashboard, or you'll see empty states.

## 🎨 Customization

### Change Theme Colors
Edit `dashboard_v2/frontend/tailwind.config.js`:
```javascript
colors: {
  'tedbot': {
    'accent': '#00ff41',  // Change this!
  }
}
```

### Change Refresh Rate
Edit `dashboard_v2/frontend/src/pages/CommandCenter.jsx`:
```javascript
const interval = setInterval(fetchOverview, 30000)  // 30 seconds
```

## 🚢 Production Deployment

### Build Optimized Frontend
```bash
cd dashboard_v2/frontend
npm run build
```

Static files will be in `dashboard_v2/frontend/dist/`

### Deploy Options
1. **Vercel/Netlify**: Deploy `dist/` folder for frontend
2. **Flask Production**: Use gunicorn or uwsgi for backend
3. **Single Server**: Serve React build from Flask static folder

## 📝 Next Steps

1. **Test the Dashboard**: Browse through all pages
2. **Check API Endpoints**: Visit http://localhost:5001/api/v2/health
3. **Customize Colors**: Match your branding preferences
4. **Add Real Data**: Run some trades to populate the dashboard
5. **Explore Components**: Check out the React component source code

## 🆘 Need Help?

- **API Documentation**: See [README.md](./README.md) for full API endpoint details
- **Component Docs**: Check individual `.jsx` files for component usage
- **React Docs**: https://react.dev
- **Vite Docs**: https://vitejs.dev

---

**Built with Claude Code** | Professional Trading Terminal for TEDBOT
