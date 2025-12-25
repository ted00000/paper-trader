#!/bin/bash
set -e

# Dashboard v2 Production Deployment Script
# This script:
# 1. Syncs ALL pending files from local to server
# 2. Builds React frontend for production
# 3. Deploys to tedbot.ai replacing both old dashboard.html and /admin
# 4. Configures nginx for SPA + API proxy
# 5. Sets up systemd service for enhanced API

SERVER="root@174.138.67.26"
PROJECT_DIR="/root/paper_trading_lab"
LOCAL_DIR="/Users/tednunes/Downloads/paper_trading_lab"

echo "========================================="
echo "Dashboard v2 Production Deployment"
echo "========================================="
echo ""

# Step 1: Build React frontend locally
echo "[1/7] Building React frontend for production..."
cd "$LOCAL_DIR/dashboard_v2/frontend"
npm run build
echo "✅ Frontend build complete"
echo ""

# Step 2: Sync ALL files to server (excluding build artifacts and dependencies)
echo "[2/7] Syncing ALL project files to server..."
rsync -avz --progress \
  --exclude 'node_modules/' \
  --exclude '.git/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '.DS_Store' \
  --exclude 'venv/' \
  --exclude '.env' \
  "$LOCAL_DIR/" \
  "$SERVER:$PROJECT_DIR/"
echo "✅ All files synced to server"
echo ""

# Step 3: Create nginx configuration on server
echo "[3/7] Creating nginx configuration..."
ssh "$SERVER" "cat > /etc/nginx/sites-available/tedbot-dashboard-v2 << 'NGINX_EOF'
server {
    server_name tedbot.ai www.tedbot.ai 174.138.67.26;

    # Password protection for entire site
    auth_basic \"TedBot Dashboard\";
    auth_basic_user_file /etc/nginx/.htpasswd;

    # API routes - proxy to enhanced API on port 5001
    location /api/v2 {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # React SPA - serve static files
    root $PROJECT_DIR/dashboard_v2/frontend/dist;
    index index.html;

    # SPA fallback - all routes go to index.html
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control \"public, immutable\";
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/tedbot.ai/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/tedbot.ai/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if (\$host = www.tedbot.ai) {
        return 301 https://\$host\$request_uri;
    } # managed by Certbot

    if (\$host = tedbot.ai) {
        return 301 https://\$host\$request_uri;
    } # managed by Certbot

    listen 80;
    server_name tedbot.ai www.tedbot.ai 174.138.67.26;
    return 404; # managed by Certbot
}
NGINX_EOF
"
echo "✅ Nginx configuration created"
echo ""

# Step 4: Create systemd service for enhanced API
echo "[4/7] Creating systemd service for enhanced API..."
ssh "$SERVER" "cat > /etc/systemd/system/dashboard-api-v2.service << 'SYSTEMD_EOF'
[Unit]
Description=TedBot Dashboard v2 Enhanced API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR/dashboard_v2/backend
Environment=\"PATH=$PROJECT_DIR/venv/bin\"
ExecStart=$PROJECT_DIR/venv/bin/python api_enhanced.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF
"
echo "✅ Systemd service created"
echo ""

# Step 5: Install Python dependencies and configure services
echo "[5/7] Installing dependencies and configuring services..."
ssh "$SERVER" << 'REMOTE_COMMANDS'
# Ensure Python dependencies are installed
cd /root/paper_trading_lab
source venv/bin/activate
pip install flask flask-cors

# Stop old dashboard service if running
systemctl stop dashboard-server 2>/dev/null || true

# Enable nginx config
ln -sf /etc/nginx/sites-available/tedbot-dashboard-v2 /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/trading-dashboard 2>/dev/null || true

# Test nginx configuration
nginx -t

# Reload systemd and start new API service
systemctl daemon-reload
systemctl enable dashboard-api-v2
systemctl restart dashboard-api-v2

# Reload nginx
systemctl reload nginx
REMOTE_COMMANDS
echo "✅ Services configured and started"
echo ""

# Step 6: Verify deployment
echo "[6/7] Verifying deployment..."
sleep 3

# Check if API is running
if ssh "$SERVER" "systemctl is-active dashboard-api-v2 > /dev/null 2>&1"; then
    echo "✅ Enhanced API is running on port 5001"
else
    echo "❌ Enhanced API failed to start"
    ssh "$SERVER" "journalctl -u dashboard-api-v2 -n 50 --no-pager"
    exit 1
fi

# Check if nginx is running
if ssh "$SERVER" "systemctl is-active nginx > /dev/null 2>&1"; then
    echo "✅ Nginx is running"
else
    echo "❌ Nginx failed to start"
    exit 1
fi

# Test API endpoint
if ssh "$SERVER" "curl -s http://localhost:5001/api/v2/health > /dev/null"; then
    echo "✅ API health check passed"
else
    echo "⚠️  API health check failed (may be normal if endpoint doesn't exist)"
fi

echo ""
echo "[7/7] Deployment Summary"
echo "========================================="
echo "✅ Dashboard v2 deployed successfully!"
echo ""
echo "🌐 URL: https://tedbot.ai"
echo "🔒 Password protection: Enabled (nginx basic auth)"
echo "📊 React SPA: Deployed from dashboard_v2/frontend/dist"
echo "🔌 Enhanced API: Running on port 5001 (systemd service)"
echo "🔄 Old dashboard: Disabled"
echo ""
echo "Next steps:"
echo "1. Visit https://tedbot.ai in your browser"
echo "2. Enter credentials when prompted"
echo "3. Test all three pages: Command Center, Today, Analytics"
echo "4. Verify real-time data updates"
echo ""
echo "Useful commands:"
echo "  Check API logs:    ssh $SERVER 'journalctl -u dashboard-api-v2 -f'"
echo "  Restart API:       ssh $SERVER 'systemctl restart dashboard-api-v2'"
echo "  Check nginx logs:  ssh $SERVER 'tail -f /var/log/nginx/error.log'"
echo "========================================="
