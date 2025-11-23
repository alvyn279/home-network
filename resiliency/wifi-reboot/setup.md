# WiFi Reboot Setup Instructions

## Prerequisites

1. **Raspberry Pi 4** with Raspberry Pi OS installed
2. **TP-Link Kasa HS103** smart plug configured on your network
3. **Secondary router** (TP-Link AX23) set up with WiFi network (optional for basic setup)
4. **Smart plug IP address** - Use discovery commands below to find it

### Find Your Smart Plug IP

```bash
# Method 1: Use python-kasa discovery
source ~/internet-monitor-env/bin/activate
python3 -m kasa discover
deactivate

# Method 2: Scan your network (replace 192.168.X with your network)
nmap -sn 192.168.X.0/24

# Method 3: Check router's DHCP client list
# Navigate to your router's web interface (usually 192.168.X.1)
```

**Note:** Replace `192.168.X.Z` in all configuration files with your actual smart plug IP address.

## Installation Steps

### 1. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python virtual environment tools
sudo apt install python3-venv python3-pip -y
```

### 2. Create Python Virtual Environment

```bash
# Run the install script
./install.sh
```

**Or manually:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Deactivate for now
deactivate
```

### 3. Deploy Files

```bash
# Copy Python script to Pi home directory
scp internet_monitor.py pi@192.168.2.50:/home/pi/

# Make script executable
chmod +x /home/pi/internet_monitor.py

# Test script with virtual environment
source ~/internet-monitor-env/bin/activate
python3 /home/pi/internet_monitor.py
deactivate
```

### 4. Install systemd Service

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

# Test script manually with virtual environment
source ~/internet-monitor-env/bin/activate
python3 /home/pi/internet_monitor.py
deactivate
```

**Can't find smart plug:**
```bash
# Discover Kasa devices (with virtual environment)
source ~/internet-monitor-env/bin/activate
python3 -m kasa discover

# Or target specific network (replace X with your network number)
python3 -c "
import asyncio
from kasa import Discover
async def find():
    devices = await Discover.discover(target='192.168.X.255')
    for ip, dev in devices.items():
        await dev.update()
        print(f'Found: {ip} - {dev.alias} ({dev.model})')
asyncio.run(find())
"
deactivate

# Check network connectivity (replace with your plug's actual IP)
ping 192.168.X.Z
```

**Missing dependencies:**
```bash
# Reinstall in virtual environment
source ~/internet-monitor-env/bin/activate
pip install --upgrade python-kasa
deactivate
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

# Test smart plug control (with virtual environment)
source ~/internet-monitor-env/bin/activate
python3 -c "
import asyncio
from kasa import Discover
async def test():
    device = await Discover.discover_single('192.168.X.Z')  # Replace with your plug's IP
    print('Turning OFF...')
    await device.turn_off()
    await asyncio.sleep(2)
    print('Turning ON...')
    await device.turn_on()
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
