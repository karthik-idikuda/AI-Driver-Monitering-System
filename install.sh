#!/bin/bash
# Driver Monitoring System Installer
# This script sets up the virtual environment and installs all dependencies

echo "🚗 Driver Monitoring System - Installer"
echo "========================================"

# Set working directory
cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or newer."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if camera is available
echo "📹 Checking camera availability..."
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera available:', cap.isOpened()); cap.release()"

# Download models if needed
if [ ! -f "models/shape_predictor_68_face_landmarks.dat" ] || [ ! -f "models/haarcascade_frontalface_default.xml" ]; then
    echo "🧠 Downloading required models..."
    python download_models.py
fi

# Create required directories
echo "📁 Creating data directories..."
mkdir -p data/logs
mkdir -p data/recordings
mkdir -p data/screenshots
mkdir -p data/history
mkdir -p data/driver_profiles

# Make run script executable
chmod +x run_system.sh

echo ""
echo "✅ Installation complete!"
echo ""
echo "To start the system:"
echo "  ./run_system.sh gui      - Start with GUI (recommended)"
echo "  ./run_system.sh console  - Start in console mode"
echo "  ./run_system.sh test     - Run system checks"
echo ""
