#!/bin/bash
################################################################################
# Dashboard Startup Script
# Launches the secure admin dashboard with proper environment configuration
################################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Starting Trading Dashboard${NC}"
echo -e "${GREEN}=================================${NC}"

# Check if .env exists
if [ ! -f ~/.env ]; then
    echo -e "${RED}ERROR: ~/.env file not found${NC}"
    echo -e "${YELLOW}Run generate_dashboard_credentials.py first to create credentials${NC}"
    exit 1
fi

# Load environment variables
echo -e "${YELLOW}Loading environment variables...${NC}"
export $(cat ~/.env | grep -v '^#' | xargs)

# Verify required variables
if [ -z "$DASHBOARD_SECRET_KEY" ] || [ -z "$ADMIN_USERNAME" ] || [ -z "$ADMIN_PASSWORD_HASH" ]; then
    echo -e "${RED}ERROR: Missing required environment variables${NC}"
    echo -e "${YELLOW}Required: DASHBOARD_SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD_HASH${NC}"
    exit 1
fi

# Create required directories
echo -e "${YELLOW}Creating required directories...${NC}"
mkdir -p logs/dashboard
mkdir -p dashboard_data
mkdir -p dashboard/templates
mkdir -p dashboard/static

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade required packages
echo -e "${YELLOW}Checking dependencies...${NC}"
pip install -q --upgrade Flask werkzeug

# Check if port 5000 is already in use
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}ERROR: Port 5000 is already in use${NC}"
    echo -e "${YELLOW}Kill the process or choose a different port${NC}"
    exit 1
fi

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Dashboard Server Starting${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "${YELLOW}Access dashboard at:${NC}"
echo -e "  Local:   ${GREEN}http://localhost:5000${NC}"
echo -e "  Network: ${GREEN}http://$(hostname -I | awk '{print $1}'):5000${NC}"
echo ""
echo -e "${YELLOW}Security Notes:${NC}"
echo -e "  • Use SSH tunnel for remote access"
echo -e "  • Enable HTTPS in production"
echo -e "  • Monitor logs/dashboard/audit.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop server${NC}"
echo ""
echo -e "${GREEN}=================================${NC}"

# Start the dashboard server
python3 dashboard_server.py
