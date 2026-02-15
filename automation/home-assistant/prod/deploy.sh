#!/bin/bash
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Error: .env file not found. Copy .env.example to .env first."
    exit 1
fi

echo "Deploying Home Assistant production instance..."

# Configure firewall
echo "Configuring UFW for port 8123..."
sudo ufw allow 8123/tcp

# Start container
docker compose up -d

# Show status
echo ""
echo "Home Assistant production instance deployed!"
echo "Access at: http://192.168.0.68:8123"
echo ""
docker compose ps
