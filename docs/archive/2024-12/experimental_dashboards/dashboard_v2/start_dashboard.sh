#!/bin/bash

# TEDBOT Dashboard v2.0 Startup Script
# Starts both backend API and frontend dev server

echo "🤖 Starting TEDBOT Dashboard v2.0..."
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the dashboard_v2 directory"
    echo "   cd dashboard_v2"
    echo "   ./start_dashboard.sh"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check Node
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed. Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if backend dependencies are installed
echo "📦 Checking backend dependencies..."
python3 -c "import flask; import numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Backend dependencies missing. Installing..."
    pip3 install flask flask-cors numpy
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "✅ All dependencies ready"
echo ""
echo "🚀 Starting servers..."
echo ""

# Start backend in background
echo "▶️  Starting Backend API on port 5001..."
cd backend
python3 api_enhanced.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 2

# Check if backend started successfully
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend API running (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start. Check backend.log for details."
    exit 1
fi

# Start frontend
echo "▶️  Starting Frontend Dev Server on port 3000..."
echo ""
cd frontend
npm run dev

# If we get here, frontend was stopped (Ctrl+C)
echo ""
echo "🛑 Shutting down servers..."

# Kill backend
kill $BACKEND_PID 2>/dev/null
echo "✅ Backend stopped"

echo ""
echo "👋 TEDBOT Dashboard stopped"
