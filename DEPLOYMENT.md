# DEPLOYMENT INSTRUCTIONS - Digital Ocean Setup

## 🚀 Quick Start Guide

This guide will help you deploy the Paper Trading Lab agent and dashboard to a Digital Ocean droplet.

---

## 📋 Prerequisites

- Digital Ocean account
- Claude API key (from console.anthropic.com)
- Domain name (optional, can use droplet IP)

---

## 1️⃣ CREATE DIGITAL OCEAN DROPLET

### Option A: Via Web Interface
1. Go to https://cloud.digitalocean.com/droplets/new
2. Choose:
   - **Image:** Ubuntu 24.04 LTS
   - **Plan:** Basic ($6/month)
   - **CPU:** Regular - 1GB RAM / 1 vCPU
   - **Datacenter:** Choose closest to you
   - **Authentication:** SSH key (recommended) or password
   - **Hostname:** paper-trading-lab

3. Click "Create Droplet"
4. Wait 60 seconds for droplet to be ready
5. Note the IP address (e.g., 123.45.67.89)

---

## 2️⃣ CONNECT TO YOUR DROPLET

```bash
# Replace with your droplet IP
ssh root@YOUR_DROPLET_IP
```

---

## 3️⃣ INSTALL DEPENDENCIES

```bash
# Update system
apt update && apt upgrade -y

# Install Python and required packages
apt install -y python3 python3-pip python3-venv nginx

# Install system cron
apt install -y cron
systemctl enable cron
systemctl start cron
```

---

## 4️⃣ UPLOAD PROJECT FILES

### Option A: Using SCP (from your local machine)

```bash
# Upload the entire project directory
scp -r paper_trading_lab root@YOUR_DROPLET_IP:/root/
```

### Option B: Using Git (if you have a repo)

```bash
# On the droplet
cd /root
git clone YOUR_REPO_URL paper_trading_lab
```

### Option C: Manual Upload
1. Download the paper_trading_lab.zip file
2. Use FileZilla or similar to upload to `/root/`
3. Unzip: `unzip paper_trading_lab.zip`

---

## 5️⃣ SETUP PYTHON ENVIRONMENT

```bash
cd /root/paper_trading_lab

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install required packages
pip install requests anthropic
```

---

## 6️⃣ CONFIGURE API KEY

```bash
# Create environment file
nano /root/.env

# Add this line (replace with your actual API key):
export CLAUDE_API_KEY="sk-ant-api03-your-actual-key-here"

# Save and exit (Ctrl+X, then Y, then Enter)

# Load environment variables
echo "source /root/.env" >> /root/.bashrc
source /root/.env
```

---

## 7️⃣ TEST THE AGENT

```bash
# Activate virtual environment
cd /root/paper_trading_lab
source venv/bin/activate

# Test the "go" command
python3 agent.py go

# If successful, you should see output saved to daily_reviews/

# Test the "analyze" command
python3 agent.py analyze
```

---

## 8️⃣ SETUP AUTOMATED SCHEDULING

### Create cron jobs for automatic execution:

```bash
# Edit crontab
crontab -e

# Add these lines (adjust timezone if needed - this assumes ET):
# Run "go" command at 8:45 AM ET every weekday
45 8 * * 1-5 cd /root/paper_trading_lab && source venv/bin/activate && source /root/.env && python3 agent.py go >> /var/log/trading_go.log 2>&1

# Run "analyze" command at 4:30 PM ET every weekday
30 16 * * 1-5 cd /root/paper_trading_lab && source venv/bin/activate && source /root/.env && python3 agent.py analyze >> /var/log/trading_analyze.log 2>&1

# Save and exit
```

**Note:** Digital Ocean droplets use UTC by default. To use ET times:
```bash
# Set timezone to Eastern
timedatectl set-timezone America/New_York
```

---

## 9️⃣ SETUP WEB DASHBOARD

### Configure Nginx to serve the dashboard:

```bash
# Create nginx config
nano /etc/nginx/sites-available/trading-dashboard

# Paste this configuration:
```

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;
    
    root /root/paper_trading_lab;
    index dashboard.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    location /paper_trading_lab/ {
        alias /root/paper_trading_lab/;
        autoindex off;
    }
    
    # Enable CORS for JSON files
    location ~* \.(json)$ {
        add_header Access-Control-Allow-Origin *;
    }
}
```

```bash
# Enable the site
ln -s /etc/nginx/sites-available/trading-dashboard /etc/nginx/sites-enabled/

# Remove default site
rm /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t

# Restart nginx
systemctl restart nginx

# Fix permissions
chmod -R 755 /root/paper_trading_lab
```

---

## 🔟 ACCESS YOUR DASHBOARD

**Via IP Address:**
```
http://YOUR_DROPLET_IP
```

**Via Domain (if configured):**
```
http://trading.yourdomain.com
```

---

## 🔒 OPTIONAL: SETUP HTTPS (Recommended)

```bash
# Install certbot
apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
certbot --nginx -d trading.yourdomain.com

# Certbot will automatically configure HTTPS and auto-renewal
```

---

## 📊 MONITOR LOGS

```bash
# View "go" command logs
tail -f /var/log/trading_go.log

# View "analyze" command logs
tail -f /var/log/trading_analyze.log

# View nginx access logs
tail -f /var/log/nginx/access.log

# View nginx error logs
tail -f /var/log/nginx/error.log
```

---

## 🔧 TROUBLESHOOTING

### Agent not running?
```bash
# Check if cron is running
systemctl status cron

# View cron logs
grep CRON /var/log/syslog

# Manually test agent
cd /root/paper_trading_lab
source venv/bin/activate
source /root/.env
python3 agent.py go
```

### Dashboard not loading?
```bash
# Check nginx status
systemctl status nginx

# Check nginx error logs
tail -f /var/log/nginx/error.log

# Verify file permissions
ls -la /root/paper_trading_lab/
```

### API calls failing?
```bash
# Verify API key is set
echo $CLAUDE_API_KEY

# Test API manually
python3 -c "import os; print(os.environ.get('CLAUDE_API_KEY', 'NOT SET'))"
```

---

## 🔄 MANUAL EXECUTION (Anytime)

If you want to run commands manually instead of waiting for cron:

```bash
ssh root@YOUR_DROPLET_IP
cd /root/paper_trading_lab
source venv/bin/activate
source /root/.env

# Run go command
python3 agent.py go

# Run analyze command
python3 agent.py analyze
```

---

## 💰 COST BREAKDOWN

- **Droplet:** $6/month (1GB RAM)
- **Claude API:** ~$1-3/month (2 calls/day × 20 trading days)
- **Domain:** ~$12/year (optional)
- **SSL Certificate:** Free (Let's Encrypt)

**Total: ~$7-9/month**

---

## 📝 MAINTENANCE

### Update project files:
```bash
cd /root/paper_trading_lab
# Upload new files via SCP or git pull
systemctl restart nginx
```

### View all data:
```bash
cd /root/paper_trading_lab
cat portfolio_data/account_status.json
cat portfolio_data/current_portfolio.json
```

---

## 🎯 WHAT HAPPENS AUTOMATICALLY

1. **8:45 AM ET (Mon-Fri):** Agent runs "Go" command
   - Analyzes market and portfolio
   - Makes trading decisions
   - Updates JSON files
   - Dashboard auto-refreshes

2. **4:30 PM ET (Mon-Fri):** Agent runs "analyze" command
   - Updates positions with closing prices
   - Calculates P&L
   - Extracts learnings
   - Updates JSON files
   - Dashboard auto-refreshes

3. **Dashboard:** Auto-refreshes every 60 seconds to show latest data

---

## ✅ VERIFICATION CHECKLIST

After deployment, verify:
- [ ] Droplet is running
- [ ] Can SSH into droplet
- [ ] Python environment is setup
- [ ] API key is configured
- [ ] Agent can run manually
- [ ] Cron jobs are scheduled
- [ ] Nginx is running
- [ ] Dashboard is accessible via browser
- [ ] JSON files are being created/updated

---

## 🆘 NEED HELP?

Common issues and solutions are in the troubleshooting section above.

If you encounter other issues, check:
1. System logs: `journalctl -xe`
2. Cron logs: `grep CRON /var/log/syslog`
3. Application logs: `/var/log/trading_*.log`

---

**Deployment time: 15-30 minutes**  
**Maintenance time: <5 minutes/week**

---

*Last updated: October 24, 2025*
