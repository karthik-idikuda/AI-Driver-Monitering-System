#!/bin/bash

# Setup script for Driver Monitoring System on macOS/Linux

echo "Setting up Driver Monitoring System..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p data/logs
mkdir -p data/known_faces
mkdir -p data/screenshots
mkdir -p data/recordings
mkdir -p data/alerts
mkdir -p models

# Download models
echo "Downloading required models..."
python download_models.py

# Make main script executable
chmod +x main.py

echo ""
echo "Setup completed successfully!"
echo ""
echo "To run the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run GUI mode: python main.py --mode gui"
echo "3. Or run console mode: python main.py --mode console"
echo ""
echo "For help: python main.py --help"
