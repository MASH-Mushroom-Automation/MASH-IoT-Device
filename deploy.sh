#!/bin/bash
# MASH IoT Device - Deployment Script
# Automated deployment script for Raspberry Pi

set -e  # Exit on any error

echo "MASH IoT Device - Deployment Script"
echo "===================================="

# Configuration
DEVICE_USER="pi"
DEVICE_HOST=""  # Set this to your RPi IP address
DEPLOY_DIR="/home/pi/MASH-IoT-Device"
SERVICE_NAME="mash-device"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on target device
check_target() {
    if [[ "$DEVICE_HOST" == "" ]]; then
        log_error "DEVICE_HOST not set. Please edit this script and set the RPi IP address."
        exit 1
    fi
    
    if [[ "$DEVICE_HOST" == "localhost" ]] || [[ "$DEVICE_HOST" == "127.0.0.1" ]]; then
        log_info "Deploying to local device"
        return 0
    fi
    
    log_info "Deploying to remote device: $DEVICE_HOST"
    return 1
}

# Install dependencies on target
install_dependencies() {
    log_info "Installing dependencies..."
    
    if check_target; then
        # Local installation
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv git
        sudo apt install -y i2c-tools python3-smbus  # For I2C support
    else
        # Remote installation
        ssh $DEVICE_USER@$DEVICE_HOST "sudo apt update && sudo apt install -y python3 python3-pip python3-venv git i2c-tools python3-smbus"
    fi
}

# Setup Python environment
setup_python_env() {
    log_info "Setting up Python environment..."
    
    if check_target; then
        # Local setup
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        # Remote setup
        ssh $DEVICE_USER@$DEVICE_HOST "cd $DEPLOY_DIR && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
    fi
}

# Deploy code
deploy_code() {
    log_info "Deploying code..."
    
    if check_target; then
        # Local deployment
        log_info "Code is already in place (local deployment)"
    else
        # Remote deployment
        log_info "Copying code to remote device..."
        
        # Create deployment directory
        ssh $DEVICE_USER@$DEVICE_HOST "mkdir -p $DEPLOY_DIR"
        
        # Copy files (excluding venv, __pycache__, etc.)
        rsync -av --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
              --exclude='.git' --exclude='data' --exclude='logs' \
              ./ $DEVICE_USER@$DEVICE_HOST:$DEPLOY_DIR/
    fi
}

# Setup systemd service
setup_service() {
    log_info "Setting up systemd service..."
    
    SERVICE_CONTENT="[Unit]
Description=MASH IoT Device
After=network.target

[Service]
Type=simple
User=$DEVICE_USER
WorkingDirectory=$DEPLOY_DIR
ExecStart=$DEPLOY_DIR/venv/bin/python $DEPLOY_DIR/main.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=$DEPLOY_DIR/src

[Install]
WantedBy=multi-user.target"

    if check_target; then
        # Local service setup
        echo "$SERVICE_CONTENT" | sudo tee $SERVICE_FILE > /dev/null
        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
    else
        # Remote service setup
        ssh $DEVICE_USER@$DEVICE_HOST "echo '$SERVICE_CONTENT' | sudo tee $SERVICE_FILE > /dev/null"
        ssh $DEVICE_USER@$DEVICE_HOST "sudo systemctl daemon-reload && sudo systemctl enable $SERVICE_NAME"
    fi
}

# Configure device
configure_device() {
    log_info "Configuring device..."
    
    # Create necessary directories
    if check_target; then
        mkdir -p data logs
    else
        ssh $DEVICE_USER@$DEVICE_HOST "mkdir -p $DEPLOY_DIR/data $DEPLOY_DIR/logs"
    fi
    
    # Copy environment file
    if check_target; then
        cp env.example .env
        log_warn "Please edit .env file with your configuration"
    else
        ssh $DEVICE_USER@$DEVICE_HOST "cd $DEPLOY_DIR && cp env.example .env"
        log_warn "Please edit .env file on remote device with your configuration"
    fi
}

# Enable I2C
enable_i2c() {
    log_info "Enabling I2C interface..."
    
    if check_target; then
        # Local I2C setup
        sudo raspi-config nonint do_i2c 0
        log_info "I2C enabled. Please reboot if this is the first time."
    else
        # Remote I2C setup
        ssh $DEVICE_USER@$DEVICE_HOST "sudo raspi-config nonint do_i2c 0"
        log_warn "I2C enabled on remote device. Reboot may be required."
    fi
}

# Test deployment
test_deployment() {
    log_info "Testing deployment..."
    
    if check_target; then
        # Local test
        source venv/bin/activate
        python test_device.py
    else
        # Remote test
        ssh $DEVICE_USER@$DEVICE_HOST "cd $DEPLOY_DIR && source venv/bin/activate && python test_device.py"
    fi
}

# Start service
start_service() {
    log_info "Starting MASH device service..."
    
    if check_target; then
        sudo systemctl start $SERVICE_NAME
        sudo systemctl status $SERVICE_NAME
    else
        ssh $DEVICE_USER@$DEVICE_HOST "sudo systemctl start $SERVICE_NAME && sudo systemctl status $SERVICE_NAME"
    fi
}

# Main deployment function
deploy() {
    log_info "Starting deployment process..."
    
    # Check prerequisites
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3."
        exit 1
    fi
    
    # Run deployment steps
    install_dependencies
    deploy_code
    setup_python_env
    configure_device
    enable_i2c
    setup_service
    
    log_info "Deployment completed successfully!"
    
    # Ask if user wants to test
    read -p "Do you want to run tests? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        test_deployment
    fi
    
    # Ask if user wants to start service
    read -p "Do you want to start the service now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_service
    fi
    
    log_info "Deployment complete! Use 'sudo systemctl status $SERVICE_NAME' to check service status."
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  deploy     Deploy the MASH IoT Device"
    echo "  test       Run tests only"
    echo "  start      Start the service"
    echo "  stop       Stop the service"
    echo "  status     Show service status"
    echo "  logs       Show service logs"
    echo "  help       Show this help message"
    echo ""
    echo "Before running, edit this script and set DEVICE_HOST to your RPi IP address."
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    test)
        test_deployment
        ;;
    start)
        start_service
        ;;
    stop)
        log_info "Stopping MASH device service..."
        if check_target; then
            sudo systemctl stop $SERVICE_NAME
        else
            ssh $DEVICE_USER@$DEVICE_HOST "sudo systemctl stop $SERVICE_NAME"
        fi
        ;;
    status)
        log_info "MASH device service status:"
        if check_target; then
            sudo systemctl status $SERVICE_NAME
        else
            ssh $DEVICE_USER@$DEVICE_HOST "sudo systemctl status $SERVICE_NAME"
        fi
        ;;
    logs)
        log_info "MASH device service logs:"
        if check_target; then
            sudo journalctl -u $SERVICE_NAME -f
        else
            ssh $DEVICE_USER@$DEVICE_HOST "sudo journalctl -u $SERVICE_NAME -f"
        fi
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        log_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac
