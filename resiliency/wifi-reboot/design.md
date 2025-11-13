# WiFi Reboot Module - Automatic Modem Reset

## Problem
ISP modem occasionally loses internet connectivity despite showing green status light. Requires manual power cycling when away from home.

## Solution
Raspberry Pi monitors internet connectivity and automatically power cycles modem via smart plug when failures detected.

## Architecture

```
Internet → ISP Modem (via Smart Plug) → Main Router → Secondary Router → Pi
                ↑                                           ↓
                └─────── Power Control ←──────────────────────┘
```

## Hardware Requirements

- **Raspberry Pi 4** (2GB+ RAM) - ~$75 CAD
- **TP-Link Kasa HS103** smart plug - ~$25 CAD  
- **MicroSD Card** (32GB Class 10) - ~$15 CAD
- **Secondary Router** (TP-Link AX23) - ~$80 CAD

**Total: ~$195 CAD**

## Network Configuration

**IP Layout:**
- Main Network: 192.168.1.x (existing)
- Secondary Network: 192.168.2.x (monitoring)
- Pi: 192.168.2.50
- Smart Plug: 192.168.2.100

## Smart Plug Control (python-kasa)

### Installation
```bash
pip install python-kasa
```

### Basic Control
```python
import asyncio
from kasa import SmartPlug

async def restart_modem():
    plug = SmartPlug("192.168.2.100")  # HS103 IP
    
    # Power cycle modem
    await plug.turn_off()
    await asyncio.sleep(10)
    await plug.turn_on()
    
    print("Modem restarted")

# Usage
asyncio.run(restart_modem())
```

### Discovery
```bash
# Find Kasa devices on network
python -m kasa discover

# Or scan for port 9999
nmap -p 9999 192.168.2.0/24
```

## Monitoring Script Structure

```python
import asyncio
import subprocess
from kasa import SmartPlug
from datetime import datetime

class InternetMonitor:
    def __init__(self):
        self.plug_ip = "192.168.2.100"
        self.test_hosts = ["8.8.8.8", "1.1.1.1"]
        self.failure_threshold = 3
        self.check_interval = 60
        
    def ping_test(self, host):
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '3', host], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def check_internet(self):
        for host in self.test_hosts:
            if self.ping_test(host):
                return True
        return False
    
    async def restart_modem(self):
        plug = SmartPlug(self.plug_ip)
        await plug.turn_off()
        await asyncio.sleep(10)
        await plug.turn_on()
        print(f"{datetime.now()}: Modem restarted")
    
    async def monitor(self):
        failures = 0
        while True:
            if self.check_internet():
                failures = 0
            else:
                failures += 1
                print(f"Internet down ({failures}/{self.failure_threshold})")
                
                if failures >= self.failure_threshold:
                    await self.restart_modem()
                    failures = 0
                    await asyncio.sleep(120)  # Wait for modem boot
            
            await asyncio.sleep(self.check_interval)

if __name__ == "__main__":
    monitor = InternetMonitor()
    asyncio.run(monitor.monitor())
```

## Deployment Options

### Option 1: Systemd Service (Recommended)
```bash
# Create service file
sudo nano /etc/systemd/system/internet-monitor.service
```

```ini
[Unit]
Description=Internet Monitor
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/bin/python3 /home/pi/internet_monitor.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable internet-monitor.service
sudo systemctl start internet-monitor.service

# Check status
sudo systemctl status internet-monitor.service
```

### Option 2: Cron Job (Simple)
```bash
# Edit crontab
crontab -e

# Run every minute
* * * * * /usr/bin/python3 /home/pi/internet_monitor.py
```

## Setup Steps

1. **Install Raspberry Pi OS** on SD card
2. **Connect Pi to secondary router WiFi**
3. **Install dependencies:** `pip install python-kasa`
4. **Deploy monitoring script** to `/home/pi/internet_monitor.py`
5. **Set up systemd service** (recommended)
6. **Test with:** `sudo journalctl -u internet-monitor.service -f`

## Configuration

### Failure Detection
- **Test Hosts:** 8.8.8.8, 1.1.1.1 (Google, Cloudflare DNS)
- **Failure Threshold:** 3 consecutive failures
- **Check Interval:** 60 seconds
- **Restart Delay:** 10 seconds off, 120 seconds recovery wait

### Local Control Benefits
- Works during internet outages
- No cloud dependency
- Faster response (~1 second vs ~5 seconds)
- More reliable than cloud API

## Monitoring

### Logs
```bash
# Service logs
sudo journalctl -u internet-monitor.service -f

# System logs
tail -f /var/log/syslog | grep internet-monitor
```

### Status Check
```bash
# Service status
sudo systemctl status internet-monitor.service

# Test smart plug manually
python -c "import asyncio; from kasa import SmartPlug; asyncio.run(SmartPlug('192.168.2.100').update())"
```

## Security Considerations

- Pi runs on isolated secondary network
- Smart plug uses local API (no cloud dependency)
- No port forwarding required
- Automatic updates via `unattended-upgrades`

## Future Enhancements

- **Notifications:** SMS/email alerts on failures
- **Web Dashboard:** Status monitoring interface  
- **Multiple ISPs:** Failover between connections
- **Logging:** Detailed outage tracking and analysis

#### Phase 2: Remote Access
1. Configure VPN on secondary router
2. Set up mobile notifications
3. Create web dashboard for status
4. Add manual override controls

#### Phase 3: Advanced Monitoring
1. Add cellular backup connectivity
2. Implement cloud logging
3. Create predictive failure detection
4. Integrate with home automation platform

### Hardware Requirements

#### Secondary Router
- **Budget**: TP-Link Archer A7 (~$50)
- **Mid-range**: ASUS AX1800 (~$100)
- **Advanced**: Ubiquiti Dream Machine SE (~$400)

#### Smart Power Control
- **Simple**: TP-Link Kasa HS110 (~$25)
- **Advanced**: Shelly 1PM (~$20)
- **DIY**: Sonoff + Tasmota (~$15)

#### Monitoring Device
- **Raspberry Pi 4** (~$75) - Full Linux environment
- **ESP32** (~$10) - Minimal embedded solution
- **Existing computer** - Repurpose available hardware

### Software Stack Options

#### Lightweight Approach
- Python script with cron scheduling
- Simple HTTP API for smart plug control
- Basic logging to local files

#### Home Automation Integration
- Home Assistant for centralized control
- Node-RED for visual flow programming
- Grafana for monitoring dashboards

#### Cloud-Native Approach
- AWS IoT Core for device management
- Lambda functions for logic processing
- CloudWatch for monitoring and alerts

### Security Considerations

1. **Network Isolation**: Keep secondary network separate
2. **Access Control**: Strong passwords and key-based auth
3. **Firmware Updates**: Regular security patches
4. **VPN Security**: WireGuard or OpenVPN with certificates
5. **API Security**: Authentication tokens for smart devices

### Monitoring & Alerting

#### Local Monitoring
- Device status dashboard
- Connection quality metrics
- Power cycle event logs
- Network performance tracking

#### Remote Notifications
- SMS alerts for outages
- Email reports for extended downtime
- Push notifications via mobile app
- Slack/Discord integration for tech updates

### Future Expansion Opportunities

#### Home Automation Platform
- Smart lighting control
- HVAC monitoring and control
- Security camera management
- Environmental sensors

#### Network Services
- Local file server (NAS)
- Media streaming server
- Home DNS server
- Network-attached backup

#### IoT Device Management
- Device provisioning system
- Firmware update management
- Security monitoring
- Performance optimization

### Cost Estimate

#### Minimal Setup (~$100)
- Secondary router: $50
- Smart plug: $25
- Raspberry Pi Zero: $25

#### Complete Setup (~$300)
- Quality router: $150
- Advanced smart switch: $50
- Raspberry Pi 4 kit: $100

#### Enterprise-grade (~$600)
- Ubiquiti equipment: $400
- Professional monitoring: $200

### Success Metrics

1. **Reliability**: 99%+ internet uptime
2. **Response Time**: <5min outage detection
3. **Recovery Time**: <3min modem restart
4. **Remote Access**: 100% availability via secondary network
5. **False Positives**: <1% incorrect resets

### Risk Mitigation

1. **Power Failure**: UPS for secondary network
2. **Hardware Failure**: Redundant monitoring devices
3. **Network Loops**: Proper VLAN configuration
4. **ISP Issues**: Cellular backup for critical alerts
5. **Smart Plug Failure**: Manual bypass switch

## Next Steps

1. Research and purchase secondary router
2. Select appropriate smart power control device
3. Plan network IP addressing scheme
4. Design monitoring script architecture
5. Create testing plan for failure scenarios
