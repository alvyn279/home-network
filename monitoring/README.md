# Monitoring Stack - Prometheus + Grafana

## Quick Start

```bash
# Start the monitoring stack
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Access

- **Grafana**: http://192.168.0.68:3000
- **Prometheus**: http://192.168.0.68:9090

## Configuration

### Prometheus
- **Config**: `core/prometheus.yml`
- **Retention**: 90 days
- **Scrape interval**: 15 seconds

### Grafana
- **Data source**: Auto-configured to use Prometheus
- **Provisioning**: `dashboards/provisioning/` auto-configured

## Targets

Current scrape targets:
- `prometheus:9090` - Prometheus self-monitoring
- `host.docker.internal:8000` - Internet Monitor (when implemented)
- `host.docker.internal:9100` - Node Exporter (future)

## Data Persistence

- **Prometheus data**: `prometheus_data` volume
- **Grafana data**: `grafana_data` volume

Data persists across container restarts.

## Management

```bash
# Stop services
docker-compose down

# Update images
docker-compose pull
docker-compose up -d

# Remove everything (including data)
docker-compose down -v
```
