#!/bin/bash

# 🚀 Script untuk menginstall Crypto Trading AI sebagai systemd service
# Usage: sudo ./install-systemd-service.sh

set -e

echo "🚀 Installing Cryptocurrency Trading AI as systemd service..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root (use sudo)"
  exit 1
fi

# Configuration variables
APP_NAME="crypto-trading-ai"
APP_USER="ubuntu"
APP_GROUP="ubuntu" 
INSTALL_DIR="/opt/${APP_NAME}"
SERVICE_FILE="${APP_NAME}.service"
CURRENT_DIR=$(pwd)

# Create application user if doesn't exist
if ! id "$APP_USER" &>/dev/null; then
    echo "👤 Creating user: $APP_USER"
    useradd --system --shell /bin/bash --home $INSTALL_DIR --create-home $APP_USER
fi

# Create installation directory
echo "📁 Creating installation directory: $INSTALL_DIR"
mkdir -p $INSTALL_DIR
mkdir -p $INSTALL_DIR/logs
mkdir -p $INSTALL_DIR/reports
mkdir -p $INSTALL_DIR/snapshots
mkdir -p $INSTALL_DIR/instance

# Copy application files
echo "📋 Copying application files..."
cp -r * $INSTALL_DIR/
chown -R $APP_USER:$APP_GROUP $INSTALL_DIR

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
sudo -u $APP_USER python3 -m venv $INSTALL_DIR/venv
sudo -u $APP_USER $INSTALL_DIR/venv/bin/pip install --upgrade pip
sudo -u $APP_USER $INSTALL_DIR/venv/bin/pip install -r $INSTALL_DIR/requirements-prod.txt

# Create .env file if not exists
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo "⚙️ Creating .env file from template..."
    sudo -u $APP_USER cp $INSTALL_DIR/.env.example $INSTALL_DIR/.env
    echo "📝 Please edit $INSTALL_DIR/.env with your configuration"
fi

# Install systemd service
echo "🔧 Installing systemd service..."
cp $CURRENT_DIR/$SERVICE_FILE /etc/systemd/system/

# Update service file paths if needed
sed -i "s|/opt/crypto-trading-ai|$INSTALL_DIR|g" /etc/systemd/system/$SERVICE_FILE
sed -i "s|User=ubuntu|User=$APP_USER|g" /etc/systemd/system/$SERVICE_FILE
sed -i "s|Group=ubuntu|Group=$APP_GROUP|g" /etc/systemd/system/$SERVICE_FILE

# Reload systemd and enable service
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

echo "✅ Enabling service to start on boot..."
systemctl enable $APP_NAME

echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit configuration: sudo nano $INSTALL_DIR/.env"
echo "2. Start service: sudo systemctl start $APP_NAME"
echo "3. Check status: sudo systemctl status $APP_NAME"
echo "4. View logs: sudo journalctl -fu $APP_NAME"
echo ""
echo "🌐 Service Commands:"
echo "  Start:   sudo systemctl start $APP_NAME"
echo "  Stop:    sudo systemctl stop $APP_NAME"
echo "  Restart: sudo systemctl restart $APP_NAME"
echo "  Status:  sudo systemctl status $APP_NAME"
echo "  Logs:    sudo journalctl -fu $APP_NAME"
echo ""
echo "🔧 Configuration file: $INSTALL_DIR/.env"
echo "📁 Application directory: $INSTALL_DIR"