#!/bin/bash

# Deployment Script for Crypto Trading AI Platform
# Usage: ./deploy.sh [development|production]

set -e  # Exit on any error

ENVIRONMENT=${1:-development}
echo "🚀 Deploying Crypto Trading AI Platform - Environment: $ENVIRONMENT"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required files exist
check_requirements() {
    print_status "Checking requirements..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.example .env
        print_error "Please edit .env file with your actual values before running again!"
        exit 1
    fi
    
    if [ ! -f "requirements-prod.txt" ]; then
        print_error "requirements-prod.txt not found!"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs tmp static/react-build
    chmod 755 logs tmp
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    if [ "$ENVIRONMENT" = "development" ]; then
        pip install -r requirements.txt
    else
        pip install -r requirements-prod.txt
    fi
}

# Install Node.js dependencies and build frontend
build_frontend() {
    print_status "Building React frontend..."
    
    if [ -f "package.json" ]; then
        npm ci --only=production
        npm run build
        
        if [ -d "dist" ]; then
            cp -r dist/* static/react-build/
            print_status "Frontend built successfully"
        else
            print_warning "Frontend build directory not found"
        fi
    else
        print_warning "package.json not found. Skipping frontend build."
    fi
}

# Set up database
setup_database() {
    print_status "Setting up database..."
    
    # Load environment variables
    source .env
    
    # Run database migrations
    python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
}

# Start services based on environment
start_services() {
    if [ "$ENVIRONMENT" = "development" ]; then
        print_status "Starting development server..."
        python wsgi.py
    elif [ "$ENVIRONMENT" = "production" ]; then
        print_status "Starting production server with Gunicorn..."
        gunicorn --config gunicorn.conf.py wsgi:application
    elif [ "$ENVIRONMENT" = "docker" ]; then
        print_status "Starting with Docker Compose..."
        docker-compose up -d
        print_status "Services started. Access the app at http://localhost:5000"
    fi
}

# Main deployment flow
main() {
    case $ENVIRONMENT in
        "development")
            print_status "🔧 Development deployment"
            check_requirements
            create_directories
            install_python_deps
            build_frontend
            setup_database
            start_services
            ;;
        "production")
            print_status "🏭 Production deployment"
            check_requirements
            create_directories
            install_python_deps
            build_frontend
            setup_database
            start_services
            ;;
        "docker")
            print_status "🐳 Docker deployment"
            check_requirements
            create_directories
            build_frontend
            start_services
            ;;
        *)
            print_error "Invalid environment. Use: development, production, or docker"
            exit 1
            ;;
    esac
    
    print_status "✅ Deployment completed successfully!"
    print_status "Access your application at:"
    print_status "  - Main app: http://localhost:5000"
    print_status "  - API docs: http://localhost:5000/api/health"
    print_status "  - Metrics: http://localhost:5000/metrics"
}

# Run main function
main