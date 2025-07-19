# MyApp Systemd Service

File systemd service untuk menjalankan aplikasi Python Flask/Django dengan Gunicorn di VPS Ubuntu.

## Files
- `myapp.service` - File systemd service
- `install-myapp-service.sh` - Script installer otomatis

## Manual Installation

### 1. Copy service file
```bash
sudo cp myapp.service /etc/systemd/system/
```

### 2. Reload systemd daemon
```bash
sudo systemctl daemon-reload
```

### 3. Enable service (auto-start on boot)
```bash
sudo systemctl enable myapp
```

### 4. Start service
```bash
sudo systemctl start myapp
```

## Automatic Installation

```bash
sudo ./install-myapp-service.sh
sudo systemctl start myapp
```

## Service Management

### Basic Commands
```bash
# Start service
sudo systemctl start myapp

# Stop service
sudo systemctl stop myapp

# Restart service
sudo systemctl restart myapp

# Check status
sudo systemctl status myapp

# Enable auto-start on boot
sudo systemctl enable myapp

# Disable auto-start
sudo systemctl disable myapp
```

### Monitoring
```bash
# View real-time logs
sudo journalctl -fu myapp

# View last 50 lines
sudo journalctl -n 50 -u myapp

# View logs since today
sudo journalctl --since today -u myapp
```

## Configuration Details

### Service Settings
- **User**: ubuntu
- **Working Directory**: /home/ubuntu/myapp
- **Virtual Environment**: /home/ubuntu/myapp/venv
- **Command**: gunicorn wsgi:application --bind 0.0.0.0:8000
- **Auto-restart**: Yes (10 second delay)
- **Logging**: systemd journal

### Security Features
- No new privileges
- Protected system directories
- Protected home directory
- Write access only to app directory

### Requirements
- Python virtual environment at `/home/ubuntu/myapp/venv`
- Application code at `/home/ubuntu/myapp`
- `wsgi.py` file with `application` object
- Gunicorn installed in virtual environment

## Troubleshooting

### Service fails to start
```bash
# Check detailed logs
sudo journalctl -u myapp --no-pager

# Verify paths exist
ls -la /home/ubuntu/myapp/venv/bin/gunicorn
ls -la /home/ubuntu/myapp/wsgi.py

# Test manually
sudo -u ubuntu /home/ubuntu/myapp/venv/bin/gunicorn wsgi:application --bind 0.0.0.0:8000
```

### Permission issues
```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /home/ubuntu/myapp

# Check service file permissions
ls -la /etc/systemd/system/myapp.service
```

### Port already in use
```bash
# Check what's using port 8000
sudo netstat -tulpn | grep :8000

# Kill process if needed
sudo fuser -k 8000/tcp
```

## Example Usage

After installation, your application will:
- Start automatically on server boot
- Restart automatically if it crashes
- Log to systemd journal
- Run as the ubuntu user
- Bind to all interfaces on port 8000

Access your application at: `http://your-server-ip:8000`