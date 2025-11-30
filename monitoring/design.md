# Monitoring Infrastructure Design

## Overview
Centralized monitoring system using Prometheus + Grafana for time-series metrics collection and visualization across all home cluster services.

## Architecture

**Data Flow:**
```
Services → Prometheus → Grafana → Web Dashboard
```

## Components

### Prometheus (Metrics Collection)
- **Purpose**: Scrapes metrics from all cluster services
- **Storage**: Time-series database with configurable retention
- **Port**: 9090 (web UI + API)
- **Config**: `/etc/prometheus/prometheus.yml`

### Grafana (Visualization)
- **Purpose**: Web dashboards for metrics visualization
- **Port**: 3000 (web UI)
- **Features**: Alerting, multi-service dashboards, historical analysis

### Service Integration
Services expose metrics via HTTP endpoints:
- **Internet Monitor**: `:8000/metrics` - ping success rates, response times
- **Future Services**: `:800X/metrics` - service-specific metrics
- **System Metrics**: Node Exporter on `:9100/metrics`

## Metrics Strategy

### Internet Monitor Metrics
- `ping_success_total{host}` - Successful ping counter per host
- `ping_failure_total{host}` - Failed ping counter per host  
- `ping_duration_seconds{host}` - Response time histogram
- `modem_restart_total` - Modem restart counter

### System Metrics (Node Exporter)
- CPU, memory, disk usage
- Network interface statistics
- System uptime and load

## Deployment
- **Docker Compose**: Single-file deployment for both services
- **Persistent Storage**: Volumes for Prometheus data and Grafana config
- **Network**: Bridge network for service communication

## Scalability
- **Service Discovery**: Auto-detect new services via file-based discovery
- **Modular Dashboards**: Separate dashboard per service module
- **Alerting Rules**: Configurable thresholds per service type

## Security
- **Internal Network**: Services communicate via Docker bridge
- **External Access**: Grafana web UI only, Prometheus internal-only
- **Authentication**: Grafana login for dashboard access
