#!/bin/bash

set -e

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "Loading configuration from .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found. Copy .env.example to .env and configure."
    exit 1
fi

echo "Updating internet-monitor service..."

# Update dependencies using existing install script
echo "Updating dependencies..."
./install.sh

# Generate systemd service file with environment variables
echo "Generating systemd service file..."
envsubst < config/internet-monitor.service.template > /tmp/internet-monitor.service

# Copy updated service file
echo "Installing systemd service file..."
sudo cp /tmp/internet-monitor.service /etc/systemd/system/

# Cleanup temp file
rm /tmp/internet-monitor.service

# Reload systemd and restart service
echo "Reloading systemd configuration..."
sudo systemctl daemon-reload

echo "Restarting service..."
sudo systemctl restart internet-monitor.service

# Check status
echo "Service status:"
sudo systemctl status internet-monitor.service --no-pager

echo "Update complete!"
