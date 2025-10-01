#!/bin/bash

# Amazon Monitor Start Script
echo "🔍 Starting Amazon Monitor..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Start the monitor
echo "🚀 Starting Amazon product monitoring..."
python run_monitor.py


