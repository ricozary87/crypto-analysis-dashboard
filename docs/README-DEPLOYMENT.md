# 🚀 Crypto Trading AI Platform - Deployment Guide

## Overview

This is a comprehensive cryptocurrency trading analysis platform with AI-powered insights, real-time market data, and advanced technical analysis capabilities.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **PostgreSQL**: 16.x or higher
- **Redis**: 7.x or higher (optional, for caching)
- **Memory**: Minimum 4GB RAM
- **Storage**: Minimum 10GB free space

### Required API Keys
- **OKX Exchange API**: API Key, Secret, Passphrase
- **OpenAI API**: GPT-4 access key
- **Sentry DSN**: (optional, for error monitoring)

## 🔧 Quick Start

### 1. Clone and Setup Environment
```bash
git clone <your-repository>
cd crypto-trading-ai
cp .env.example .env
# Edit .env with your actual API keys and database credentials
```

### 2. Setup Database
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE trading_db;
CREATE USER trading_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE trading_db TO trading_user;
\q
```

### 3. Deploy with Script
```bash
# Development deployment
./deploy.sh development

# Production deployment
./deploy.sh production

# Docker deployment
./deploy.sh docker
```

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker Engine 20.x+
- Docker Compose v2.x+

### Steps
```bash
# 1. Configure environment
cp .env.example .env
# Edit .env file with your values

# 2. Start all services
docker-compose up -d

# 3. Check status
docker-compose ps
docker-compose logs trading-app
```

### Services Included
- **trading-app**: Main Flask application
- **postgres**: PostgreSQL database
- **redis**: Redis cache
- **nginx**: Reverse proxy (optional)

## 🏭 Manual Production Deployment

### 1. System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip nodejs npm postgresql redis-server nginx

# CentOS/RHEL
sudo yum install python3.11 python3-pip nodejs npm postgresql-server redis nginx
```

### 2. Application Setup
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-prod.txt

# Build frontend
npm ci --only=production
npm run build
cp -r dist/* static/react-build/

# Setup database
python -c "
from app import app, db
with app.app_context():
    db.create_all()
"
```

### 3. Configure Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/trading-ai.service
```

```ini
[Unit]
Description=Crypto Trading AI Platform
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/app/venv/bin
ExecStart=/path/to/your/app/venv/bin/gunicorn --config gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-ai
sudo systemctl start trading-ai
sudo systemctl status trading-ai
```

## 🔧 VPS Deployment Guide

### DigitalOcean / Linode / Vultr

1. **Create VPS Instance**
   - Minimum: 2 CPU, 4GB RAM, 25GB SSD
   - OS: Ubuntu 22.04 LTS

2. **Initial Server Setup**
```bash
# Connect to VPS
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Create application user
adduser trading
usermod -aG sudo trading
su - trading
```

3. **Install Dependencies**
```bash
# Install system packages
sudo apt install python3.11 python3.11-venv python3-pip nodejs npm postgresql postgresql-contrib nginx redis-server git

# Start services
sudo systemctl enable postgresql redis-server nginx
sudo systemctl start postgresql redis-server nginx
```

4. **Deploy Application**
```bash
# Clone repository
git clone <your-repo-url> /home/trading/crypto-trading-ai
cd /home/trading/crypto-trading-ai

# Run deployment script
./deploy.sh production
```

5. **Configure Nginx**
```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/trading-ai
sudo ln -s /etc/nginx/sites-available/trading-ai /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 Security Considerations

### 1. SSL/TLS Certificate
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Firewall Configuration
```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 3. Environment Security
- Use strong passwords for database
- Rotate API keys regularly
- Enable fail2ban for SSH protection
- Regular security updates

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Application health
curl http://localhost:5000/health

# Database connection
curl http://localhost:5000/api/health

# Metrics
curl http://localhost:5000/metrics
```

### Log Management
```bash
# Application logs
tail -f logs/error.log
tail -f logs/access.log

# System logs
sudo journalctl -u trading-ai -f
```

### Backup Strategy
```bash
# Database backup
pg_dump -U trading_user trading_db > backup_$(date +%Y%m%d).sql

# Application backup
tar -czf app_backup_$(date +%Y%m%d).tar.gz /home/trading/crypto-trading-ai
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql
# Check connection
psql -U trading_user -d trading_db -h localhost
```

2. **Permission Errors**
```bash
# Fix ownership
sudo chown -R trading:trading /home/trading/crypto-trading-ai
sudo chmod +x deploy.sh
```

3. **Port Already in Use**
```bash
# Check what's using port 5000
sudo lsof -i :5000
sudo kill -9 <PID>
```

4. **API Keys Not Working**
```bash
# Verify environment variables
source .env
echo $OPENAI_API_KEY
echo $OKX_API_KEY
```

## 📞 Support

### Application Access
- **Main Dashboard**: `http://your-domain.com`
- **API Documentation**: `http://your-domain.com/api/health`
- **Monitoring**: `http://your-domain.com/metrics`

### Performance Monitoring
- Check CPU/Memory usage: `htop`
- Database performance: `sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"`
- Application logs: `tail -f logs/error.log`

### Scaling Considerations
- Increase Gunicorn workers based on CPU cores
- Use Redis for session storage and caching
- Consider load balancer for multiple instances
- Monitor database performance and optimize queries

---

## 📝 Files Overview

### Production Files Created:
- `wsgi.py` - WSGI entry point for production
- `gunicorn.conf.py` - Gunicorn configuration
- `requirements-prod.txt` - Production dependencies
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-service deployment
- `.env.example` - Environment variables template
- `nginx.conf` - Reverse proxy configuration
- `deploy.sh` - Automated deployment script

### Removed Replit-specific Files:
- `.replit` - Replit configuration (not needed for VPS)
- `replit.nix` - Nix packages (not needed for VPS)

This setup provides a production-ready, scalable deployment suitable for any VPS or cloud provider.