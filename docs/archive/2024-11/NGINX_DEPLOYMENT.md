# Deploy Admin Dashboard at tedbot.ai/admin

## Overview
This guide shows you how to configure nginx on your DigitalOcean server to serve the admin dashboard at `https://tedbot.ai/admin`.

---

## Step 1: SSH into Your DigitalOcean Server

```bash
ssh root@174.138.67.26
```

---

## Step 2: Ensure Dashboard is Running

Make sure your Flask dashboard is running on port 5000:

```bash
cd /Users/tednunes/Downloads/paper_trading_lab
source venv/bin/activate
./start_dashboard.sh
```

Keep this running (use `screen` or `tmux` to run in background):

```bash
# Option A: Using screen
screen -S dashboard
./start_dashboard.sh
# Press Ctrl+A then D to detach

# Option B: Using tmux
tmux new -s dashboard
./start_dashboard.sh
# Press Ctrl+B then D to detach
```

---

## Step 3: Find Your Nginx Config

Locate your tedbot.ai nginx configuration:

```bash
# Common locations:
ls /etc/nginx/sites-available/tedbot.ai
ls /etc/nginx/conf.d/tedbot.ai.conf
ls /etc/nginx/nginx.conf

# Or search for it:
grep -r "server_name.*tedbot.ai" /etc/nginx/
```

---

## Step 4: Add Admin Route to Nginx Config

Edit your tedbot.ai nginx server block and add this location block:

```nginx
server {
    listen 443 ssl http2;
    server_name tedbot.ai www.tedbot.ai;

    # Your existing SSL certificates
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Your existing root and locations
    # ...

    # ====================================================
    # ADMIN DASHBOARD - Add this section
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

    # ====================================================
}
```

---

## Step 5: Test Nginx Configuration

```bash
sudo nginx -t
```

If you see "syntax is ok" and "test is successful", proceed. Otherwise, fix any errors.

---

## Step 6: Reload Nginx

```bash
sudo systemctl reload nginx
# or
sudo nginx -s reload
```

---

## Step 7: Update Flask App Config (Optional - for HTTPS)

Since you'll be serving over HTTPS via nginx, update the session cookie security:

Edit `dashboard_server.py` and change line 30:
```python
app.config['SESSION_COOKIE_SECURE'] = True  # Enable since nginx handles HTTPS
```

Then restart the dashboard.

---

## Step 8: Test the Dashboard

Visit: **https://tedbot.ai/admin**

You should see the login page. Use your credentials from `~/.env`.

---

## Troubleshooting

### Issue: "502 Bad Gateway"
**Cause**: Flask dashboard not running on port 5000

**Fix**:
```bash
# Check if dashboard is running
ps aux | grep dashboard_server

# Check port 5000
netstat -tlnp | grep 5000

# Restart dashboard
cd /Users/tednunes/Downloads/paper_trading_lab
./start_dashboard.sh
```

### Issue: "404 Not Found"
**Cause**: Nginx rewrite rules not working

**Fix**: Check nginx error log:
```bash
sudo tail -f /var/log/nginx/error.log
```

### Issue: Login redirects to wrong URL
**Cause**: Flask using absolute URLs instead of relative

**Fix**: Check that all redirects in Flask use `url_for()` correctly (already done in dashboard_server.py)

### Issue: CSS/JS not loading
**Cause**: Static files path incorrect

**Fix**: Verify static folder exists:
```bash
ls -la /Users/tednunes/Downloads/paper_trading_lab/dashboard/static/
```

---

## Auto-Start Dashboard on Boot (Optional)

Create systemd service at `/etc/systemd/system/trading-dashboard.service`:

```ini
[Unit]
Description=Trading Admin Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/Users/tednunes/Downloads/paper_trading_lab
Environment="PATH=/Users/tednunes/Downloads/paper_trading_lab/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/Users/tednunes/Downloads/paper_trading_lab/venv/bin/python3 /Users/tednunes/Downloads/paper_trading_lab/dashboard_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-dashboard
sudo systemctl start trading-dashboard
sudo systemctl status trading-dashboard
```

---

## Security Checklist

- [ ] Dashboard runs on localhost only (not 0.0.0.0)
- [ ] HTTPS enabled via nginx
- [ ] Strong password set (12+ characters)
- [ ] `SESSION_COOKIE_SECURE = True` in production
- [ ] Audit log monitored regularly
- [ ] `.env` file secured (chmod 600)
- [ ] Rate limiting active (5 attempts, 15-min lockout)

---

## Access URLs After Setup

- **Login**: https://tedbot.ai/admin
- **Dashboard**: https://tedbot.ai/admin (after login)
- **Logout**: https://tedbot.ai/admin/logout
- **API**: https://tedbot.ai/admin/api/*

---

## Next Steps

1. Add link to admin dashboard on your main tedbot.ai site
2. Monitor `logs/dashboard/audit.log` for security events
3. Set up systemd service for auto-start
4. Consider adding IP whitelist if you have a static IP
