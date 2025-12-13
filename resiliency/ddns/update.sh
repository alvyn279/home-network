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

echo "Updating DDNS service..."

# Update dependencies using existing install script
echo "Updating dependencies..."
./install.sh

# Generate systemd service and timer files with environment variables
echo "Generating systemd service files..."
envsubst < ddns.service.template > /tmp/ddns.service
cp ddns.timer /tmp/ddns.timer

# Copy updated service files
echo "Installing systemd service files..."
sudo cp /tmp/ddns.service /tmp/ddns.timer /etc/systemd/system/

# Cleanup temp files
rm /tmp/ddns.service /tmp/ddns.timer

# Reload systemd and restart service
echo "Reloading systemd configuration..."
sudo systemctl daemon-reload

echo "Restarting timer..."
sudo systemctl restart ddns.timer

# Check status
echo "Timer status:"
sudo systemctl status ddns.timer --no-pager

echo "Update complete!"
