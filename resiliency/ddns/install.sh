#!/bin/bash

set -e

if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping creation..."
else
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/updating dependencies..."
pip install -r requirements.txt

echo "Installation complete!"
echo "To activate the environment, run: source venv/bin/activate"
