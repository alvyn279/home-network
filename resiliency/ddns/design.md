# Dynamic DNS - Cloudflare Integration

## Overview
Automatically updates DNS records when home public IP changes, ensuring remote access to home services.

## Architecture
```
ISP changes IP → Script detects → Cloudflare API → DNS updated → Services accessible
```

## Multi-Subdomain Support
Updates multiple A records pointing to home network:
- `home.alvynle.me` → Home Assistant dashboard
- `api.alvynle.me` → API services
- `ssh.alvynle.me` → SSH access
- AWS records (alvynle.me, www, dev) remain unchanged

## Implementation
```python
import requests

class CloudflareDDNS:
    def __init__(self, api_token, zone_id):
        self.api_token = api_token
        self.zone_id = zone_id
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {"Authorization": f"Bearer {api_token}"}
        
    def get_public_ip(self):
        return requests.get("https://ipv4.icanhazip.com").text.strip()
    
    def update_record(self, record_name, ip):
        records = requests.get(
            f"{self.base_url}/zones/{self.zone_id}/dns_records",
            headers=self.headers,
            params={"name": record_name}
        ).json()["result"]
        
        if records:
            record_id = records[0]["id"]
            requests.put(
                f"{self.base_url}/zones/{self.zone_id}/dns_records/{record_id}",
                headers=self.headers,
                json={"type": "A", "name": record_name, "content": ip}
            )
    
    def update_all(self):
        ip = self.get_public_ip()
        for record in ["home.alvynle.me", "api.alvynle.me", "ssh.alvynle.me"]:
            self.update_record(record, ip)
```

## Deployment
**systemd timer** - runs every 5 minutes on HP EliteDesk

## DNS Provider Comparison

### Cloudflare (Recommended)
- **Cost**: Free
- **DDoS Protection**: Yes (hides home IP via proxy)
- **SSL/TLS**: Free certificates
- **CDN**: Included
- **WAF**: Basic rules free
- **Best for**: Publicly exposed home services

### Route53
- **Cost**: $0.50/month + $0.40/million queries
- **DDoS Protection**: DNS only (home IP still exposed)
- **SSL/TLS**: Bring your own (Let's Encrypt)
- **CDN**: Requires CloudFront (additional cost)
- **WAF**: Requires AWS WAF (additional cost)
- **Best for**: AWS-integrated infrastructure

## Key Difference
- **Route53**: DNS only - resolves names to your home IP (visible to attackers)
- **Cloudflare**: DNS + Proxy - hides home IP, filters traffic before forwarding

## Decision
Using Cloudflare for alvynle.me to leverage free proxy/DDoS protection for publicly exposed home services.
