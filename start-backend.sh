#!/bin/bash

echo "🚀 Starting Web Memory RAG Backend"
echo "=================================="

cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        echo "Please ensure Python 3.8+ is installed"
        exit 1
    fi
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Virtual environment not activated properly"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"

# Check if requirements are installed
if [ ! -f "venv/.installed" ]; then
    echo "📥 Installing dependencies (this may take a few minutes)..."
    echo "   Upgrading pip first..."
    pip install --upgrade pip
    
    echo "   Installing requirements..."
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        touch venv/.installed
        echo "✅ Dependencies installed!"
    else
        echo "❌ Failed to install dependencies"
        echo "Please check the error messages above"
        exit 1
    fi
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🎯 Starting FAISS backend server..."
echo "   URL: http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

python server.py
