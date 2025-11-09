# Home Network Redundancy & Auto-Modem Reset Design

## Problem Statement
WiFi modem occasionally loses internet connectivity despite showing green status light. Requires manual power cycling when away from home, leaving smart home devices offline.

## Solution Architecture

### Core Components

#### 1. Secondary Private Network
- **Purpose**: Independent monitoring and control network
- **Hardware**: Dedicated router (TP-Link Archer, ASUS, or Ubiquiti)
- **Network Range**: 192.168.2.x (separate from main 192.168.1.x)
- **Power**: Different electrical circuit from main modem
- **Benefits**: 
  - Network redundancy
  - Independent monitoring capability
  - Foundation for home automation ecosystem

#### 2. Smart Power Control
- **Device Options**:
  - TP-Link Kasa HS110 (WiFi smart plug with energy monitoring)
  - Shelly 1PM (Advanced relay with API)
  - Sonoff S31 (Budget option with Tasmota firmware)
- **Connection**: Main modem plugged into smart switch
- **Control**: Connected to secondary network for reliability

#### 3. Internet Monitoring System
- **Monitoring Methods**:
  - Ping tests to multiple DNS servers (8.8.8.8, 1.1.1.1, 9.9.9.9)
  - HTTP requests to reliable endpoints
  - Speed test validation (optional)
- **Failure Detection**: 3+ consecutive failures before action
- **Reset Logic**: Power off 10s, power on, wait 2min for recovery

#### 4. Remote Access Options
- **VPN Server**: On secondary router for external access
- **Cellular Backup**: USB LTE modem on secondary network
- **Cloud Integration**: AWS IoT or similar for remote monitoring
- **Mobile App**: Direct control via smartphone

### Network Topology

```
Internet → Main Modem → Primary Router (192.168.1.x)
                    ↓
                Smart Plug ← Secondary Router (192.168.2.x)
                           ↓
                    Monitoring Device
```

### Implementation Phases

#### Phase 1: Basic Auto-Reset - Detailed Shopping List

**What You Need to Buy:**

1. **Secondary Router** ($40-60)
   - TP-Link Archer A6 or A7
   - Creates your "private home network"
   - Plugs into wall power outlet

2. **Smart Power Outlet** ($15-25)
   - TP-Link Kasa HS103 (basic) or HS110 (with energy monitoring)
   - Your main modem plugs INTO this
   - This plugs into wall outlet
   - Controlled via WiFi

3. **Raspberry Pi 4 Kit** ($75)
   - Small computer to run monitoring code
   - Connects to secondary router WiFi
   - Runs 24/7 monitoring script

4. **Ethernet Cable** ($5-10)
   - Cat6 cable, 3-6 feet
   - Connects secondary router to your main router

**Total Cost: ~$150**

**Physical Setup:**
```
Wall Outlet → Smart Plug → Your Main Modem
Wall Outlet → Secondary Router
Main Router ← Ethernet Cable → Secondary Router ← WiFi ← Raspberry Pi
```

**Network Configuration for Home Project:**

**Your Specific IP Layout:**
```
Main Network: 192.168.1.x
- Main Router: 192.168.1.1
- Your devices: 192.168.1.100+

Secondary Network: 192.168.2.x  
- Secondary Router: 192.168.2.1
- Raspberry Pi: 192.168.2.50
- Smart Plug: 192.168.2.100
```

**Physical Connections:**
```
Wall → Smart Plug → ISP Modem → Main Router (192.168.1.1)
                                      ↓ Ethernet
Wall → Secondary Router (192.168.2.1) ← WiFi ← Raspberry Pi
```

**How It Works:**
1. **Raspberry Pi** runs Python script that pings internet every minute
2. **When internet fails** → Pi sends WiFi command to smart plug
3. **Smart plug** physically cuts power to your ISP modem
4. **Smart plug** turns power back on after 10 seconds
5. **Pi waits** 2 minutes for modem to boot up
6. **Repeat** monitoring

**Traffic Flow for Internet Monitoring:**
- Pi pings 8.8.8.8 → Secondary Router → Main Router → Modem → Internet
- When internet fails: Pi → Smart Plug (local network only)

*See net_deep_dive.md for detailed networking concepts*

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
