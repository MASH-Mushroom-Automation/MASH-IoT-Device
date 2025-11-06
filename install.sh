#!/bin/bash
###############################################################################
# MASH IoT Device Installation Script
# This script sets up the MASH IoT device on Raspberry Pi 3 Model B
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/home/mash/MASH-IoT-Device"
SERVICE_NAME="mash-device"
PYTHON_VERSION="3.9"

# Print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as mash user
if [ "$(whoami)" != "mash" ]; then
    print_error "This script must be run as user 'mash'"
    print_info "Please run: sudo -u mash bash install.sh"
    exit 1
fi

print_info "====================================="
print_info "MASH IoT Device Installation"
print_info "====================================="

# Update system
print_info "Updating system packages..."
sudo apt-get update

# Install system dependencies
print_info "Installing system dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    network-manager \
    dnsmasq \
    i2c-tools \
    libgpiod2 \
    python3-rpi.gpio \
    python3-smbus \
    avahi-daemon \
    avahi-utils

# Enable I2C
print_info "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Add mash user to necessary groups
print_info "Adding user to required groups..."
sudo usermod -a -G gpio,i2c,spi,dialout mash

# Create installation directory
print_info "Creating installation directory: $INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"
sudo chown -R mash:mash "$INSTALL_DIR"

# Copy files to installation directory if not already there
if [ "$PWD" != "$INSTALL_DIR" ]; then
    print_info "Copying files to $INSTALL_DIR..."
    cp -r . "$INSTALL_DIR/"
fi

cd "$INSTALL_DIR"

# Create virtual environment
print_info "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
print_info "Creating data and log directories..."
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/models"

# Set up environment file if it doesn't exist
if [ ! -f "$INSTALL_DIR/.env" ]; then
    print_info "Creating .env file from template..."
    if [ -f "$INSTALL_DIR/env.example" ]; then
        cp "$INSTALL_DIR/env.example" "$INSTALL_DIR/.env"
        
        # Generate unique device ID
        DEVICE_ID="MASH-$(cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2 | tail -c 9)"
        sed -i "s/DEVICE_ID=.*/DEVICE_ID=$DEVICE_ID/" "$INSTALL_DIR/.env"
        
        print_info "Generated device ID: $DEVICE_ID"
    else
        print_warning "env.example not found, skipping .env creation"
    fi
fi

# Install systemd service
print_info "Installing systemd service..."
sudo cp "$INSTALL_DIR/config/$SERVICE_NAME.service" "/etc/systemd/system/$SERVICE_NAME.service"
sudo systemctl daemon-reload

# Enable service for auto-start
print_info "Enabling service for auto-start..."
sudo systemctl enable "$SERVICE_NAME.service"

# Set up NetworkManager for hotspot support
print_info "Configuring NetworkManager..."
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager

# Disable dhcpcd if it conflicts with NetworkManager
if systemctl is-active --quiet dhcpcd; then
    print_warning "Disabling dhcpcd (conflicts with NetworkManager)"
    sudo systemctl disable dhcpcd
    sudo systemctl stop dhcpcd
fi

# Set up avahi for mDNS
print_info "Configuring Avahi (mDNS)..."
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon

# Set permissions
print_info "Setting file permissions..."
chmod +x "$INSTALL_DIR/main.py"
chmod +x "$INSTALL_DIR/deploy.sh"

print_info "====================================="
print_info "Installation Complete!"
print_info "====================================="
echo ""
print_info "Device ID: $(grep DEVICE_ID $INSTALL_DIR/.env | cut -d '=' -f2)"
echo ""
print_info "To start the service:"
print_info "  sudo systemctl start $SERVICE_NAME"
echo ""
print_info "To view service status:"
print_info "  sudo systemctl status $SERVICE_NAME"
echo ""
print_info "To view logs:"
print_info "  sudo journalctl -u $SERVICE_NAME -f"
echo ""
print_info "To start on next boot:"
print_info "  Already enabled!"
echo ""
print_warning "Please reboot the Raspberry Pi for all changes to take effect:"
print_warning "  sudo reboot"
echo ""
