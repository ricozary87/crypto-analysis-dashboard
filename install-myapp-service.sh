#!/bin/bash

# Script untuk menginstall myapp sebagai systemd service
# Usage: sudo ./install-myapp-service.sh

set -e

echo "Installing MyApp systemd service..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run as root (use sudo)"
  exit 1
fi

# Verify service file exists
if [ ! -f "myapp.service" ]; then
    echo "Error: myapp.service file not found in current directory"
    exit 1
fi

# Copy service file
echo "Copying service file to /etc/systemd/system/"
cp myapp.service /etc/systemd/system/

# Set proper permissions
chmod 644 /etc/systemd/system/myapp.service

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service to start on boot
echo "Enabling myapp service..."
systemctl enable myapp

echo "Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Start service:  sudo systemctl start myapp"
echo "2. Check status:   sudo systemctl status myapp"
echo "3. View logs:      sudo journalctl -fu myapp"
echo ""
echo "Service management commands:"
echo "  Start:   sudo systemctl start myapp"
echo "  Stop:    sudo systemctl stop myapp"
echo "  Restart: sudo systemctl restart myapp"
echo "  Status:  sudo systemctl status myapp"
echo "  Logs:    sudo journalctl -fu myapp"