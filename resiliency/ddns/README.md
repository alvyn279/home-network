# Dynamic DNS Setup

## Quick Start

1. **Setup virtual environment:**
   ```bash
   ./install.sh
   ```

2. **Configure:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Test:**
   ```bash
   source venv/bin/activate
   python ddns.py
   ```

4. **Deploy:**
   ```bash
   ./update.sh
   ```

## Configuration

Edit `.env` file:
```bash
# User configuration
USERNAME=pi
HOME_DIR=/home/pi

# Cloudflare API credentials
CLOUDFLARE_API_TOKEN=your_token
CLOUDFLARE_ZONE_ID=your_zone_id
DDNS_RECORDS=home.example.com,api.example.com,ssh.example.com
```

## Getting Cloudflare Credentials

1. **API Token:** Cloudflare Dashboard → My Profile → API Tokens → Create Token
   - Template: "Edit zone DNS"
   - Zone: example.com
   
2. **Zone ID:** Cloudflare Dashboard → example.com → Overview → Zone ID (right sidebar)

## Updates

```bash
# Pull latest code and update service
git pull
./update.sh
```

The `.env` file is gitignored, so your local config won't be overwritten.

## Monitoring

```bash
# Check timer status
sudo systemctl status ddns.timer

# View logs
sudo journalctl -u ddns.service -f

# Manual run
source venv/bin/activate
python ddns.py
```
