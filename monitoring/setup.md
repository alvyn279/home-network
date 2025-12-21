# Monitoring Stack Setup

## Development (Mac)

```bash
# Test configuration locally
cd monitoring/
docker-compose up -d

# Access services
open http://localhost:3000  # Grafana
open http://localhost:9090  # Prometheus
```

## Production Deployment (HP EliteDesk)

### 1. Install Docker

```bash
# On HP EliteDesk
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit ports if needed (optional)
nano .env
```

### 3. Deploy Stack

```bash
# Copy files to HP EliteDesk
scp -r monitoring/ user@192.168.0.68:/home/user/

# SSH and deploy
ssh user@192.168.0.68
cd monitoring/
./deploy.sh
```

### 3. Access Services

- **Grafana**: http://192.168.0.68:3000
- **Prometheus**: http://192.168.0.68:9090

## Workflow

1. **Develop** - Test configs on Mac
2. **Commit** - Git push changes  
3. **Deploy** - Git pull on HP EliteDesk, redeploy

## Next Steps

- Add metrics to Internet Monitor (:8000/metrics)
- Create Grafana dashboards for internet uptime
- Add Node Exporter for system metrics
