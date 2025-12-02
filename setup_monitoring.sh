#!/bin/bash
#
# Tedbot Operational Monitoring Setup Script
# Sets up health checks and Discord alerting
#

echo "========================================="
echo "TEDBOT OPERATIONAL MONITORING SETUP"
echo "========================================="
echo

# Check if running on server or local
if [[ $(hostname) == *"digitalocean"* ]] || [[ $(hostname) == *"droplet"* ]]; then
    ON_SERVER=true
    echo "✓ Detected DigitalOcean server environment"
else
    ON_SERVER=false
    echo "ℹ️  Running on local machine"
fi

echo

# Step 1: Discord Webhook (Optional)
echo "Step 1: Discord Webhook Configuration (Optional)"
echo "-----------------------------------------------"
echo "Discord webhooks allow Tedbot to send alerts to your Discord server."
echo

if grep -q "DISCORD_WEBHOOK_URL=" .env 2>/dev/null; then
    echo "✓ Discord webhook already configured in .env"
else
    echo "To set up Discord alerts:"
    echo "  1. Open Discord and go to your server"
    echo "  2. Go to Server Settings → Integrations → Webhooks"
    echo "  3. Click 'New Webhook' and copy the webhook URL"
    echo "  4. Add to .env: DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/..."
    echo
    echo "Skip this step if you don't want Discord alerts (health checks will still work)"
fi

echo
echo "Step 2: Make health_check.py executable"
echo "----------------------------------------"
chmod +x health_check.py
echo "✓ health_check.py is now executable"

echo
echo "Step 3: Test Health Check"
echo "-------------------------"
read -p "Run health check test now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running health check..."
    python3 health_check.py
fi

echo
echo "Step 4: Cron Job Setup"
echo "----------------------"

if [ "$ON_SERVER" = true ]; then
    echo "Setting up automated health checks on DigitalOcean server..."

    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "health_check.py"; then
        echo "✓ Health check cron job already configured"
    else
        echo "Adding health check to crontab..."

        # Get current directory
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

        # Add cron job: Run health check daily at 5:00 PM ET
        (crontab -l 2>/dev/null; echo "# Tedbot Health Check - Daily at 5:00 PM ET") | crontab -
        (crontab -l 2>/dev/null; echo "0 17 * * * cd $SCRIPT_DIR && /usr/bin/python3 health_check.py >> logs/health_check.log 2>&1") | crontab -

        echo "✓ Added health check cron job (daily at 5:00 PM ET)"
        echo "  Logs will be written to: logs/health_check.log"
    fi

    echo
    echo "Current crontab:"
    crontab -l | grep -A1 "Tedbot"
else
    echo "On local machine - manual setup required for production server"
    echo
    echo "To set up on DigitalOcean server, run:"
    echo "  ssh root@YOUR_SERVER_IP"
    echo "  cd /root/paper_trading_lab"
    echo "  ./setup_monitoring.sh"
fi

echo
echo "========================================="
echo "SETUP COMPLETE!"
echo "========================================="
echo
echo "✅ Health Check Features:"
echo "  • Monitors GO/EXECUTE/ANALYZE command execution"
echo "  • Checks API connectivity (Polygon, Anthropic)"
echo "  • Validates data freshness (screener updates)"
echo "  • Tracks active positions and P&L"
echo "  • Detects Claude API failures"
echo "  • Monitors disk space"

if grep -q "DISCORD_WEBHOOK_URL=" .env 2>/dev/null; then
    echo
    echo "✅ Discord Alerts:"
    echo "  • Critical issues: Red alerts"
    echo "  • Warnings: Orange alerts"
    echo "  • Daily summary: Green status"
fi

echo
echo "📋 Next Steps:"
echo "  1. Test: python3 health_check.py"
echo "  2. View logs: tail -f logs/health_check.log"

if [ "$ON_SERVER" = true ]; then
    echo "  3. Health checks will run automatically at 5:00 PM ET daily"
else
    echo "  3. Deploy to production server for automated monitoring"
fi

echo
