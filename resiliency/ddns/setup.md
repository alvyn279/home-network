# Dynamic DNS Setup - Cloudflare

## Prerequisites
- Domain name (any registrar)
- Cloudflare account (free)
- Python 3.6+ with pip

## Setup Steps

### 1. Domain Configuration
1. **Add domain to Cloudflare dashboard**
2. **Change nameservers** at registrar to Cloudflare's nameservers
3. **Wait for DNS propagation** (up to 48 hours, usually <1 hour)

### 2. Get Cloudflare Credentials

**API Token:**
1. Cloudflare Dashboard → My Profile → API Tokens → Create Token
2. Use "Edit zone DNS" template
3. Select your domain zone
4. Save the token securely

**Zone ID:**
1. Cloudflare Dashboard → Your Domain → Overview
2. Copy Zone ID from right sidebar

### 3. Install and Configure

```bash
# Clone repository
git clone <your-repo-url> /home/username/workplace/home-network

# Navigate to DDNS directory
cd /home/username/workplace/home-network/resiliency/ddns

# Setup virtual environment and dependencies
./install.sh

# Configure environment
cp .env.example .env
nano .env
```

**Edit `.env` file:**
```bash
# User configuration
USERNAME=pi
HOME_DIR=/home/pi

# Cloudflare API credentials
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token_here
CLOUDFLARE_ZONE_ID=your_cloudflare_zone_id_here

# DNS records to update
DDNS_RECORDS=home.example.com,api.example.com
```

### 4. Initialize DNS Records

```bash
# Activate virtual environment
source venv/bin/activate

# Create DNS records (first time only)
python ddns.py --init

# Test updates
python ddns.py

# Create one-time records
python ddns.py --add-record-once dashboard.example.com              # With proxy (default)
python ddns.py --add-record-once wireguard.example.com --non-proxy  # DNS only
python ddns.py --add-record-once test.example.com --ip 1.2.3.4 --non-proxy  # Custom IP, DNS only

# Deactivate environment
deactivate
```

### 5. Deploy Automatic Updates

```bash
# Deploy systemd service and timer
./update.sh

# Check service status
sudo systemctl status ddns.timer
sudo systemctl status ddns.service
```

## Verification

```bash
# Test DNS resolution
nslookup home.example.com

# Check service logs
sudo journalctl -u ddns.service -f

# Manual test
source venv/bin/activate
python ddns.py
```

## Updates

```bash
# Pull latest code and redeploy
git pull
./update.sh
```

The `.env` file is gitignored, so your local configuration won't be overwritten.

## Service Management

```bash
# Start/stop timer
sudo systemctl start ddns.timer
sudo systemctl stop ddns.timer

# View logs
sudo journalctl -u ddns.service -n 50

# Check timer schedule
sudo systemctl list-timers ddns.timer
```

## Troubleshooting

**Service won't start:**
```bash
# Check configuration
source venv/bin/activate
python ddns.py --init
deactivate

# Check logs
sudo journalctl -u ddns.service -n 20
```

**API errors:**
- Verify API token has "Zone:DNS:Edit" permissions
- Check Zone ID matches your domain
- Ensure records exist (run with `--init` flag)

**DNS not updating:**
- Check Cloudflare dashboard for recent API activity
- Verify your public IP: `curl ipv4.icanhazip.com`
- Test manual update: `python ddns.py`
