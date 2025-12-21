# WiFi Reboot Setup Instructions

## Prerequisites

1. **Ubuntu Desktop** system (HP EliteDesk 800 G1 DM or similar)
2. **TP-Link Kasa HS103** smart plug configured on your network
3. **Secondary router** (TP-Link AX23) set up with WiFi network (optional for basic setup)
4. **Smart plug IP address** - Use discovery commands below to find it

### Find Your Smart Plug IP

```bash
# Method 1: Use python-kasa discovery
source venv/bin/activate
python3 -m kasa discover
deactivate

# Method 2: Scan your network (replace 192.168.X with your network)
nmap -sn 192.168.X.0/24

# Method 3: Check router's DHCP client list
# Navigate to your router's web interface (usually 192.168.X.1)
```

## Installation Steps

### 1. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python virtual environment tools
sudo apt install python3-venv python3-pip -y
```

### 2. Setup Project

```bash
# Clone the repository
git clone <your-repo-url> /home/username/workplace/home-network

# Navigate to wifi-reboot directory
cd /home/username/workplace/home-network/resiliency/wifi-reboot

# Create virtual environment and install dependencies
./install.sh
```

### 3. Configure Service

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

Edit `.env` with your settings:
```bash
# User configuration
USERNAME=pi
HOME_DIR=/home/pi

# Internet monitor settings
PLUG_IP=192.168.2.100
CHECK_INTERVAL_IN_SECONDS=60
FAILURE_THRESHOLD=3
TEST_HOSTS=8.8.8.8,1.1.1.1,9.9.9.9
RESTART_DELAY_IN_SECONDS=10
RECOVERY_WAIT_IN_SECONDS=180
```

### 4. Test Configuration

```bash
# Test script manually
source venv/bin/activate
python3 internet_monitor.py

# Test with metrics enabled (default port 8000)
python3 internet_monitor.py --with-metrics
curl http://localhost:8000/metrics

# Test with custom metrics port
python3 internet_monitor.py --with-metrics --metrics-port 9000
curl http://localhost:9000/metrics

# Test mode with metrics
python3 internet_monitor.py --test --with-metrics

# Stop with Ctrl+C
deactivate
```

### 5. Deploy Service

```bash
# Deploy systemd service with your configuration
./update.sh
```

### 6. Verify Installation

```bash
# Check service status
sudo systemctl status internet-monitor.service

# View live logs
sudo journalctl -u internet-monitor.service -f
```

## Updates

```bash
# Pull latest code and update service
git pull
./update.sh
```

The `.env` file is gitignored, so your local config won't be overwritten.

## Configuration

### Environment Variables (in .env file)

- **USERNAME**: System username (e.g., pi)
- **HOME_DIR**: User home directory (e.g., /home/pi)
- **PLUG_IP**: Smart plug IP address (default: 192.168.2.100)
- **CHECK_INTERVAL_IN_SECONDS**: Seconds between internet checks (default: 60)
- **FAILURE_THRESHOLD**: Failed checks before restart (default: 3)
- **TEST_HOSTS**: Comma-separated ping targets (default: 8.8.8.8,1.1.1.1,9.9.9.9)
- **RESTART_DELAY_IN_SECONDS**: Seconds to keep modem off (default: 10)
- **RECOVERY_WAIT_IN_SECONDS**: Seconds to wait after restart (default: 180)

### Modify Configuration

```bash
# Edit .env file
nano .env

# Redeploy service
./update.sh
```

## Service Management

```bash
# Start service
sudo systemctl start internet-monitor.service

# Stop service
sudo systemctl stop internet-monitor.service

# Restart service
sudo systemctl restart internet-monitor.service

# Check status
sudo systemctl status internet-monitor.service

# View logs (last 50 lines)
sudo journalctl -u internet-monitor.service -n 50

# Follow logs in real-time
sudo journalctl -u internet-monitor.service -f

# Disable auto-start
sudo systemctl disable internet-monitor.service
```

## Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check for Python errors
sudo journalctl -u internet-monitor.service -n 20

# Test script manually
source venv/bin/activate
python3 internet_monitor.py
deactivate
```

**Can't find smart plug:**
```bash
# Discover Kasa devices
source venv/bin/activate
python3 -m kasa discover
deactivate

# Check network connectivity
ping 192.168.X.Z
```

**Missing dependencies:**
```bash
# Reinstall dependencies
./install.sh
```

**Permission errors:**
```bash
# Ensure correct ownership
sudo chown -R username:username /home/username/workplace/home-network/resiliency/wifi-reboot
chmod +x internet_monitor.py
```

### Log Analysis

```bash
# Show only errors
sudo journalctl -u internet-monitor.service -p err

# Show logs from last boot
sudo journalctl -u internet-monitor.service -b

# Export logs to file
sudo journalctl -u internet-monitor.service > monitor_logs.txt
```

## Testing

### Manual Testing

```bash
# Test internet connectivity check
python3 -c "
import subprocess
result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], capture_output=True)
print('Internet OK' if result.returncode == 0 else 'Internet DOWN')
"

# Test smart plug control
source venv/bin/activate
python3 -c "
import asyncio
from kasa import SmartPlug
async def test():
    plug = SmartPlug('192.168.2.100')  # Replace with your plug IP
    await plug.update()
    print(f'Plug status: {plug.is_on}')
    print('Turning OFF...')
    await plug.turn_off()
    await asyncio.sleep(2)
    print('Turning ON...')
    await plug.turn_on()
    print('Test complete')
asyncio.run(test())
"
deactivate
```

### Simulate Internet Outage

```bash
# Block internet temporarily (requires sudo)
sudo iptables -A OUTPUT -d 8.8.8.8 -j DROP
sudo iptables -A OUTPUT -d 1.1.1.1 -j DROP

# Watch logs to see restart trigger
sudo journalctl -u internet-monitor.service -f

# Restore internet
sudo iptables -F OUTPUT
```

## Prometheus Metrics

When deployed with `--with-metrics` flag, the service exposes metrics on port 8000:

### Available Metrics
- `ping_success_total{host}` - Successful ping counter per host
- `ping_failure_total{host}` - Failed ping counter per host  
- `internet_up_total` - Internet connectivity checks that passed
- `internet_down_total` - Internet connectivity checks that failed
- `modem_restart_total` - Number of modem restarts triggered

### Availability Calculations
```promql
# 1-minute availability
rate(internet_up_total[1m]) / (rate(internet_up_total[1m]) + rate(internet_down_total[1m])) * 100

# 5-minute availability  
rate(internet_up_total[5m]) / (rate(internet_up_total[5m]) + rate(internet_down_total[5m])) * 100
```

### Testing Metrics
```bash
# Check metrics endpoint (default port)
curl http://192.168.0.68:8000/metrics

# Check metrics endpoint (custom port)
curl http://192.168.0.68:9000/metrics

# Test locally with metrics
source venv/bin/activate
python internet_monitor.py --with-metrics
curl http://localhost:8000/metrics

# Test with custom port
python internet_monitor.py --with-metrics --metrics-port 9100
curl http://localhost:9100/metrics
```

### Command Line Options
```bash
# Show all available options
python internet_monitor.py --help

# Available flags:
--test                    # Run in test mode with test.env
--with-metrics           # Enable Prometheus metrics server
--metrics-port PORT      # Custom metrics port (default: 8000)
```
