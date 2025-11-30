# Remote Access - WireGuard VPN

## Overview
Secure remote access to home network via WireGuard server on TP-Link AX23 router.

## Architecture
```
Remote Device → Internet → ISP Router → Secondary Router (WireGuard) → Home Network
                           192.168.1.1    192.168.2.1:51820          192.168.2.x
```

## Setup

### Router Configuration
1. **Access router**: http://192.168.2.1 → Advanced → VPN Server → WireGuard
2. **Enable WireGuard**: Port 51820, generate keys, set client pool (10.0.0.0/24)
3. **Port forwarding**: ISP router forwards 51820 UDP to 192.168.2.1

### Client Setup
1. **Generate config** via router interface
2. **Install WireGuard app** on device
3. **Import config** and connect

## Configuration Examples

### Router Settings
```
Listen Port: 51820
Client IP Pool: 10.0.0.0/24
DNS Server: 192.168.2.1
```

### Client Config
```ini
[Interface]
PrivateKey = [Generated]
Address = 10.0.0.2/32
DNS = 192.168.2.1

[Peer]
PublicKey = [Router Public Key]
Endpoint = [Your Public IP]:51820
AllowedIPs = 192.168.2.0/24
```

## Usage
```bash
# Connect
wg-quick up client-config

# Access services
ssh username@192.168.2.50
curl http://192.168.2.50:3000  # Grafana
```

## Benefits
- **Fast**: Kernel-level implementation
- **Simple**: Key-based auth, no certificates
- **Secure**: Modern cryptography (ChaCha20, Curve25519)
- **Mobile-friendly**: Better battery life, handles network changes
