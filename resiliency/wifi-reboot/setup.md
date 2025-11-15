# WiFi Reboot Setup Instructions

## Prerequisites

1. **Raspberry Pi 4** with Raspberry Pi OS installed
2. **TP-Link Kasa HS103** smart plug configured on network
3. **Secondary router** (TP-Link AX23) set up with WiFi network
4. **Static IP reservation** for smart plug (192.168.2.100)

## Installation Steps

### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
pip install python-kasa

# Verify installation
python -c "import kasa; print('python-kasa installed successfully')"
```

### 2. Deploy Files

```bash
# Copy Python script to Pi home directory
scp internet_monitor.py pi@192.168.2.50:/home/pi/

# Make script executable
chmod +x /home/pi/internet_monitor.py

# Test script manually
python3 /home/pi/internet_monitor.py
```

### 3. Install systemd Service

```bash
# Copy service file to systemd directory
sudo cp internet-monitor.service /etc/systemd/system/

# Reload systemd configuration
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable internet-monitor.service

# Start service now
sudo systemctl start internet-monitor.service
```

### 4. Verify Installation

```bash
# Check service status
sudo systemctl status internet-monitor.service

# View live logs
sudo journalctl -u internet-monitor.service -f

# Test smart plug connectivity
python3 -c "
import asyncio
from kasa import SmartPlug
async def test():
    plug = SmartPlug('192.168.2.100')
    await plug.update()
    print(f'Plug status: {plug.is_on}')
asyncio.run(test())
"
```

## Configuration

### Environment Variables (in service file)

- **PLUG_IP**: Smart plug IP address (default: 192.168.2.100)
- **CHECK_INTERVAL**: Seconds between internet checks (default: 60)
- **FAILURE_THRESHOLD**: Failed checks before restart (default: 3)
- **TEST_HOSTS**: Comma-separated ping targets (default: 8.8.8.8,1.1.1.1,9.9.9.9)
- **RESTART_DELAY**: Seconds to keep modem off (default: 10)
- **RECOVERY_WAIT**: Seconds to wait after restart (default: 120)

### Modify Configuration

```bash
# Edit service file
sudo nano /etc/systemd/system/internet-monitor.service

# Reload and restart after changes
sudo systemctl daemon-reload
sudo systemctl restart internet-monitor.service
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
python3 /home/pi/internet_monitor.py
```

**Can't find smart plug:**
```bash
# Discover Kasa devices
python3 -m kasa discover

# Check network connectivity
ping 192.168.2.100
```

**Permission errors:**
```bash
# Ensure correct ownership
sudo chown pi:pi /home/pi/internet_monitor.py
sudo chmod +x /home/pi/internet_monitor.py
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
python3 -c "
import asyncio
from kasa import SmartPlug
async def test():
    plug = SmartPlug('192.168.2.100')
    print('Turning OFF...')
    await plug.turn_off()
    await asyncio.sleep(2)
    print('Turning ON...')
    await plug.turn_on()
    print('Test complete')
asyncio.run(test())
"
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
