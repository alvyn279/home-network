# Dynamic DNS Setup

## Quick Start

1. **Setup virtual environment:**
   ```bash
   ./install.sh
   ```

2. **Configure:**
   ```bash
   cp config.json.example config.json
   # Edit config.json with your Cloudflare credentials
   ```

3. **Test:**
   ```bash
   source venv/bin/activate
   python ddns.py
   ```

4. **Deploy (systemd):**
   ```bash
   sudo cp ddns.service ddns.timer /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now ddns.timer
   ```

## Configuration

### Option 1: Config file (recommended)
Edit `config.json`:
```json
{
  "api_token": "your_token",
  "zone_id": "your_zone_id", 
  "records": ["home.alvynle.me", "api.alvynle.me"]
}
```

### Option 2: Environment variables
```bash
export CLOUDFLARE_API_TOKEN="your_token"
export CLOUDFLARE_ZONE_ID="your_zone_id"
export DDNS_RECORDS="home.alvynle.me,api.alvynle.me"
```

## Getting Cloudflare Credentials

1. **API Token:** Cloudflare Dashboard → My Profile → API Tokens → Create Token
   - Template: "Edit zone DNS"
   - Zone: alvynle.me
   
2. **Zone ID:** Cloudflare Dashboard → alvynle.me → Overview → Zone ID (right sidebar)

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
