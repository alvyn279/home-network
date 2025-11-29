# WiFi Reboot Setup Instructions

## Prerequisites

1. **Ubuntu Desktop** system (HP EliteDesk 800 G1 DM or similar)
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
# Clone the repository on remote server
git clone <your-repo-url> /home/username/workplace/home-network

# Navigate to wifi-reboot directory
cd /home/username/workplace/home-network/resiliency/wifi-reboot

# Run installation script
./install.sh

# Test script with virtual environment and test configuration
source venv/bin/activate
python3 internet_monitor.py --test
deactivate
```

### 4. Configure Service

```bash
# Edit service file to set your smart plug IP and other settings
nano /home/username/workplace/home-network/resiliency/wifi-reboot/config/internet-monitor.service

# Replace 192.168.X.Z with your actual smart plug IP address
# Adjust other environment variables as needed:
# - CHECK_INTERVAL_IN_SECONDS (default: 60)
# - FAILURE_THRESHOLD (default: 3)
# - RESTART_DELAY_IN_SECONDS (default: 10)
# - RECOVERY_WAIT_IN_SECONDS (default: 120)
```

### 5. Install systemd Service

```bash
# Copy service file to systemd directory
sudo cp /home/username/workplace/home-network/resiliency/wifi-reboot/config/internet-monitor.service /etc/systemd/system/

# Reload systemd configuration
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable internet-monitor.service

# Start service now
sudo systemctl start internet-monitor.service
```

### 6. Verify Installation

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
cd /home/username/workplace/home-network/resiliency/wifi-reboot
source venv/bin/activate
python3 internet_monitor.py
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
cd /home/username/workplace/home-network/resiliency/wifi-reboot
source venv/bin/activate
pip install --upgrade -r requirements.txt
deactivate
```

**Permission errors:**
```bash
# Ensure correct ownership
sudo chown -R username:username /home/username/workplace/home-network/resiliency/wifi-reboot
chmod +x /home/username/workplace/home-network/resiliency/wifi-reboot/internet_monitor.py
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

## Testing

### Manual Testing with Test Configuration

```bash
cd /home/username/workplace/home-network/resiliency/wifi-reboot
source venv/bin/activate

# Run script with test configuration
python3 internet_monitor.py --test

# Stop with Ctrl+C
deactivate
```

The `test.env` file provides faster intervals and lower thresholds for testing:
- Check interval: 10 seconds (vs 60 in production)
- Failure threshold: 2 (vs 3 in production)  
- Restart delay: 5 seconds (vs 10 in production)
- Recovery wait: 30 seconds (vs 120 in production)

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
