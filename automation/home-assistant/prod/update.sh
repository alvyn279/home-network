#!/bin/bash
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Error: .env file not found. Copy .env.example to .env first."
    exit 1
fi

echo "Updating Home Assistant..."

# Pull latest image
docker compose pull

# Recreate container with new image
docker compose up -d

# Show status
echo ""
echo "Home Assistant updated!"
echo ""
docker compose ps
