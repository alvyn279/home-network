# Dynamic DNS Setup - Cloudflare

## Prerequisites
- Domain name (any registrar)
- Cloudflare account (free)

## Setup Steps

### 1. Domain Configuration
```bash
# Add domain to Cloudflare dashboard
# Change nameservers at registrar to Cloudflare's
# Create A record: home.yourdomain.com → current IP (proxy OFF)
```

### 2. API Access
```bash
# Cloudflare dashboard → My Profile → API Tokens
# Create custom token with Zone:DNS:Edit permissions
# Save token securely
```

### 3. Get IDs
```bash
# Zone ID
curl -X GET "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq '.result[] | select(.name=="yourdomain.com") | .id'

# Record ID
curl -X GET "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq '.result[] | select(.name=="home.yourdomain.com") | .id'
```

### 4. Update Script
```bash
# Create /home/username/update-dns.sh
#!/bin/bash
ZONE_ID="your_zone_id"
RECORD_ID="your_record_id"
API_TOKEN="your_token"

CURRENT_IP=$(curl -s https://ipv4.icanhazip.com)
curl -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  --data "{\"type\":\"A\",\"name\":\"home\",\"content\":\"$CURRENT_IP\",\"ttl\":300}"

chmod +x /home/username/update-dns.sh
```

### 5. Automation
```bash
# Add to crontab
crontab -e
*/5 * * * * /home/username/update-dns.sh
```

### 6. WireGuard Integration
```ini
# Update WireGuard config
[Peer]
Endpoint = home.yourdomain.com:51820
```

## Verification
```bash
# Test DNS resolution
nslookup home.yourdomain.com

# Test script
./update-dns.sh
```
