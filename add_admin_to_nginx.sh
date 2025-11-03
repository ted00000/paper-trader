#!/bin/bash
# Script to add /admin location block to your nginx config
# Run this on your DigitalOcean server

cat << 'EOF'

Add these location blocks to /etc/nginx/sites-available/trading-dashboard
inside your HTTPS server block (the one with ssl and port 443):

    # ====================================================
    # ADMIN DASHBOARD
    # ====================================================

    location /admin {
        # Remove /admin prefix when proxying
        rewrite ^/admin/(.*) /$1 break;
        rewrite ^/admin$ / break;

        # Proxy to Flask on port 5000
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;

        # Forward headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /admin/api {
        rewrite ^/admin/api/(.*) /api/$1 break;
        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/logout {
        rewrite ^/admin/logout /logout break;
        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/login {
        rewrite ^/admin/login /login break;
        proxy_pass http://127.0.0.1:5000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

EOF

echo ""
echo "To edit the file, run:"
echo "  nano /etc/nginx/sites-available/trading-dashboard"
echo ""
echo "After editing:"
echo "  sudo nginx -t"
echo "  sudo systemctl reload nginx"
