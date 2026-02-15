#!/bin/bash
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Error: .env file not found. Copy .env.example to .env first."
    exit 1
fi

echo "Starting Home Assistant test instance..."

# Configure firewall
echo "Configuring UFW for port 8124..."
sudo ufw allow 8124/tcp

# Start container
docker compose up -d

# Show status
echo ""
echo "Home Assistant test instance started!"
echo "Access at: http://192.168.0.68:8124"
echo ""
docker compose ps
