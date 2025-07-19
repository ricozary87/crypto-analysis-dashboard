# 🛠️ Systemd Service Setup Guide

## Overview

File systemd service untuk menjalankan Cryptocurrency Trading AI Platform sebagai service di Linux VPS.

## Files

1. **`crypto-trading-ai.service`** - File systemd service
2. **`install-systemd-service.sh`** - Script otomatis untuk instalasi

## 🚀 Quick Installation

### Step 1: Persiapan Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv postgresql nginx
```

### Step 2: Install Service
```bash
# Copy aplikasi ke server
# Masuk ke directory aplikasi

# Jalankan installer
sudo ./install-systemd-service.sh
```

### Step 3: Konfigurasi
```bash
# Edit file environment
sudo nano /opt/crypto-trading-ai/.env

# Contoh konfigurasi:
DATABASE_URL=postgresql://user:pass@localhost/trading_db
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret
OKX_PASSPHRASE=your_passphrase
OPENAI_API_KEY=your_openai_key
SESSION_SECRET=your-super-secret-key
```

### Step 4: Start Service
```bash
# Start service
sudo systemctl start crypto-trading-ai

# Check status
sudo systemctl status crypto-trading-ai

# Enable auto-start
sudo systemctl enable crypto-trading-ai
```

## 📊 Service Management

### Basic Commands
```bash
# Start service
sudo systemctl start crypto-trading-ai

# Stop service
sudo systemctl stop crypto-trading-ai

# Restart service
sudo systemctl restart crypto-trading-ai

# Check status
sudo systemctl status crypto-trading-ai

# Enable auto-start
sudo systemctl enable crypto-trading-ai

# Disable auto-start
sudo systemctl disable crypto-trading-ai
```

### Monitoring
```bash
# Real-time logs
sudo journalctl -fu crypto-trading-ai

# Last 100 lines
sudo journalctl -n 100 -u crypto-trading-ai

# Logs since today
sudo journalctl --since today -u crypto-trading-ai
```

## 🔧 Configuration Details

### Service Configuration
- **User**: ubuntu (atau user yang Anda tentukan)
- **Working Directory**: `/opt/crypto-trading-ai`
- **Python Environment**: Virtual environment di `/opt/crypto-trading-ai/venv`
- **Command**: Gunicorn dengan konfigurasi production

### Security Features
- ✅ Private temporary directory
- ✅ Protected system files
- ✅ No new privileges
- ✅ Resource limits (Memory: 2GB, CPU: 200%)
- ✅ File system restrictions

### Auto-restart
- Service akan restart otomatis jika crash
- Delay 10 detik sebelum restart
- Graceful shutdown dengan timeout 30 detik

## 📁 Directory Structure
```
/opt/crypto-trading-ai/
├── app.py                 # Main Flask app
├── main.py               # Entry point
├── wsgi.py               # WSGI production entry
├── gunicorn.conf.py      # Gunicorn config
├── requirements-prod.txt # Production dependencies
├── .env                  # Environment variables
├── venv/                # Python virtual environment
├── logs/                # Application logs
├── reports/             # Analysis reports
├── snapshots/           # Trading snapshots
└── instance/            # Runtime data
```

## 🌐 Nginx Configuration (Optional)

Untuk setup reverse proxy dengan Nginx:

```nginx
# /etc/nginx/sites-available/crypto-trading-ai
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/crypto-trading-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔍 Troubleshooting

### Service tidak start
```bash
# Check detailed logs
sudo journalctl -u crypto-trading-ai --no-pager

# Check configuration
sudo systemctl cat crypto-trading-ai

# Validate syntax
sudo systemd-analyze verify /etc/systemd/system/crypto-trading-ai.service
```

### Permission issues
```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /opt/crypto-trading-ai

# Fix permissions
sudo chmod -R 755 /opt/crypto-trading-ai
sudo chmod 600 /opt/crypto-trading-ai/.env
```

### Database connection issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test database connection
sudo -u postgres psql -c "SELECT version();"
```

## 🔄 Updates

Untuk update aplikasi:
```bash
# Stop service
sudo systemctl stop crypto-trading-ai

# Backup current version
sudo cp -r /opt/crypto-trading-ai /opt/crypto-trading-ai.backup

# Copy new files
sudo cp -r /path/to/new/files/* /opt/crypto-trading-ai/

# Update dependencies if needed
sudo -u ubuntu /opt/crypto-trading-ai/venv/bin/pip install -r /opt/crypto-trading-ai/requirements-prod.txt

# Fix permissions
sudo chown -R ubuntu:ubuntu /opt/crypto-trading-ai

# Start service
sudo systemctl start crypto-trading-ai
```

## ✅ Benefits

1. **Auto-start** - Service starts automatically on server boot
2. **Auto-restart** - Automatic restart on crashes
3. **Security** - Runs with limited privileges
4. **Monitoring** - Easy log monitoring with journalctl
5. **Resource control** - Memory and CPU limits
6. **Professional** - Standard Linux service management

---

**Crypto Trading AI sekarang dapat berjalan sebagai professional Linux service!**