# 🚀 Start Your TEDBOT Dashboard

## Quick Start (2 Commands)

The dashboard is currently **RUNNING** with both servers active!

- **Backend API**: http://localhost:5001 ✅
- **Frontend Dashboard**: http://localhost:3000 ✅

### 🌐 Open the Dashboard

Just open your browser to:
```
http://localhost:3000
```

You should see the TEDBOT Trading Terminal with all your trading data!

---

## Manual Startup (When Needed)

If you need to restart the servers later, open **TWO terminal windows**:

### Terminal 1 - Backend API
```bash
cd /Users/tednunes/Downloads/paper_trading_lab
python3 api_enhanced.py
```

Wait for this message:
```
✅ Running on http://127.0.0.1:5001
```

### Terminal 2 - Frontend Dev Server
```bash
cd /Users/tednunes/Downloads/paper_trading_lab/dashboard_v2/frontend
npm run dev
```

Wait for this message:
```
✅ Local: http://localhost:3000/
```

Then open: **http://localhost:3000**

---

## Stop the Servers

Press `Ctrl+C` in each terminal window to stop the servers.

---

## Current Status

Both servers are running in the background. You can:
1. Open http://localhost:3000 in your browser RIGHT NOW
2. Navigate between all 7 pages
3. See your real trading data
4. Enjoy the professional dashboard!

## Pages Available

1. **Command Center** (/) - Main dashboard with metrics, charts, positions
2. **Analytics** (/analytics) - Catalyst performance and monthly heatmap
3. **Trade Explorer** (/trades) - Search and filter trades
4. **Learning Engine** (/learning) - Learning system insights
5. **Risk Command** (/risk) - Risk monitoring dashboard
6. **Live Feed** (/live) - Activity stream
7. **Public View** (/public) - Showcase dashboard

## Troubleshooting

### Port 5001 already in use
```bash
lsof -ti:5001 | xargs kill -9
```

### Port 3000 already in use
```bash
lsof -ti:3000 | xargs kill -9
```

### Backend won't start - missing Flask
```bash
pip3 install flask flask-cors
```

### Frontend won't start - missing dependencies
```bash
cd dashboard_v2/frontend
npm install
```

---

**🎉 Your professional TEDBOT dashboard is ready to use!**

Open http://localhost:3000 and enjoy your trading terminal.
