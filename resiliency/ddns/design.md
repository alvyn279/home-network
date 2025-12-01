# Dynamic DNS - Cloudflare Integration

## Overview
Automatically updates DNS records when home public IP changes, ensuring WireGuard clients can always connect.

## Architecture
```
ISP changes IP → Script detects → Cloudflare API → DNS updated → WireGuard reconnects
```

## Components
- **IP Detection**: `curl ipv4.icanhazip.com`
- **DNS Update**: Cloudflare API v4
- **Automation**: Cron job every 5 minutes
- **Domain**: `home.yourdomain.com` → current public IP

## Benefits
- **Reliable remote access** despite dynamic IP
- **Professional domain** vs free DDNS services
- **Fast DNS resolution** via Cloudflare's global network
- **API-based updates** for automation

## Integration
WireGuard endpoint uses domain name instead of IP address, automatically resolving to current IP.
