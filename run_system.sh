#!/bin/bash

# Driver Monitoring System Launcher
# This script activates the virtual environment and runs the system

echo "🚗 Driver Monitoring System"
echo "=========================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if user wants GUI or console mode
if [ "$1" = "gui" ]; then
    echo "🖥️  Starting GUI mode..."
    python main.py --mode gui
elif [ "$1" = "console" ]; then
    echo "💻 Starting console mode..."
    python main.py --mode console
elif [ "$1" = "test" ]; then
    echo "🧪 Running system tests..."
    python test_system.py
else
    echo "📋 Usage:"
    echo "  ./run_system.sh gui      - Start with GUI"
    echo "  ./run_system.sh console  - Start in console mode"
    echo "  ./run_system.sh test     - Run system tests"
    echo ""
    echo "🔧 Available commands:"
    echo "  python main.py --mode gui     - GUI mode"
    echo "  python main.py --mode console - Console mode"
    echo "  python test_system.py         - Run tests"
fi
