#!/bin/bash
# MASH IoT Device - PyQt6 UI Launcher (Raspberry Pi)

echo "╔══════════════════════════════════════════════╗"
echo "║     MASH IoT Device - PyQt6 UI Launcher     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo ""

# Launch application
echo "Starting PyQt6 UI..."
echo ""
python main.py
