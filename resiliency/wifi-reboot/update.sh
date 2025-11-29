#!/bin/bash

set -e

echo "Updating internet-monitor service..."

# Navigate to project directory
cd /home/username/workplace/home-network/resiliency/wifi-reboot

# Pull latest changes
echo "Pulling latest code..."
git pull

# Update dependencies using existing install script
echo "Updating dependencies..."
./install.sh

# Copy updated service file
echo "Updating systemd service file..."
sudo cp config/internet-monitor.service /etc/systemd/system/

# Reload systemd and restart service
echo "Reloading systemd configuration..."
sudo systemctl daemon-reload

echo "Restarting service..."
sudo systemctl restart internet-monitor.service

# Check status
echo "Service status:"
sudo systemctl status internet-monitor.service --no-pager

echo "Update complete!"
