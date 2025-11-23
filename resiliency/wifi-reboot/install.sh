#!/bin/bash

set -e

echo "Creating Python virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installation complete!"
echo "To activate the environment, run: source venv/bin/activate"
