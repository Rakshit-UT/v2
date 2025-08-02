#!/bin/bash

# HackRx 6.0 Deployment Script
# This script sets up and runs the LLM Query Retrieval System

echo "🚀 HackRx 6.0 - LLM Query Retrieval System Deployment"
echo "================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Python version $python_version is too old. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python version $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if all required files exist
required_files=("main.py" "requirements.txt" "index.html")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file $file not found!"
        exit 1
    fi
done

echo "✅ All required files found"

# Start the application
echo "🎯 Starting the application..."
echo "📡 API will be available at: http://localhost:8000"
echo "🌐 Web interface will be available at: http://localhost:8000"
echo "📋 API documentation will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run with uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
