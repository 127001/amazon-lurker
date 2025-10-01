#!/bin/bash

# Amazon Monitor Setup Script
echo "🚀 Setting up Amazon Monitor..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env_example.txt .env
    echo "⚠️  Please edit .env file with your configuration before running the monitor."
else
    echo "✅ .env file already exists."
fi

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x start_monitor.sh
chmod +x run_monitor.py

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run ./start_monitor.sh to start monitoring"
echo ""
echo "For more information, see README.md"


