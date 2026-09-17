#!/bin/bash

echo "🔐 Secure Question Paper Management System"
echo "════════════════════════════════════════════"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📌 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Initialize database and demo users
echo "🗄️  Initializing database..."
python3 init_demo_users.py

# Run the application
echo ""
echo "🚀 Starting application..."
echo "📍 Access at: http://localhost:5000"
echo ""
python3 app.py
