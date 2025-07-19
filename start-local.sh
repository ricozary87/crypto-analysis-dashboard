#!/bin/bash

# Local Development Startup Script
# Starts the application without database dependency for local testing

echo "🚀 Starting Crypto Trading AI Platform (Local Development)"

# Create necessary directories
mkdir -p logs tmp static/react-build

# Set environment variables for local development
export FLASK_ENV=development
export DATABASE_URL="sqlite:///trading_local.db"
export SESSION_SECRET="dev-secret-key"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Build frontend if package.json exists
if [ -f "package.json" ]; then
    echo "Building frontend..."
    npm install
    npm run build
    if [ -d "dist" ]; then
        cp -r dist/* static/react-build/
    fi
fi

# Start the application
echo "Starting Flask application..."
python wsgi.py