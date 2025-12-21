#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    source .env
fi

# Configure firewall rules
sudo ufw allow ${GRAFANA_PORT:-3000}  # Grafana
sudo ufw allow ${PROMETHEUS_PORT:-9090}  # Prometheus

# Start monitoring services
docker compose up -d
