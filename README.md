# M.A.S.H. IoT Device

**Mushroom Automation with Smart Hydro-environment using IoT and AI for Sustainable Harvest**

A Raspberry Pi 3 Model B-based IoT controller for automated mushroom cultivation chamber management.

## Overview

This project implements the IoT device component of the M.A.S.H. thesis project, providing:

- **WiFi Provisioning via Hotspot** - Easy setup without keyboard/monitor
- **Real-time sensor monitoring** - CO₂, Temperature, Humidity via Arduino/SCD41
- **Automated actuator control** - Fans, Humidifier, LED Lights via GPIO relays
- **Local REST API** - Direct control from mobile app on same network
- **Cloud connectivity** - Remote control via backend when on internet
- **Offline-first data storage** - SQLite with backend synchronization
- **Auto-boot service** - Runs automatically on power-up
- **mDNS discovery** - Device findable on local network

## Documentation

- **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** - Step-by-step setup guide
- **[QUICKSTART.md](QUICKSTART.md)** - Fast 5-minute deployment for presentations
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete technical documentation
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was built and how
- **[SCHEMA_USAGE.md](SCHEMA_USAGE.md)** - Backend database integration details

## Directory Structure

```
/home/mash/MASH-IoT-Device/
├── main.py                     # Main application entry point
├── install.sh                  # One-command installation script
├── requirements.txt            # Python dependencies
├── .env                        # Configuration (create from .env.example)
├── config/
│   ├── device_config.yaml      # Default configuration
│   └── mash-device.service     # Systemd service for auto-boot
├── src/
│   ├── actuators/              # GPIO actuator control
│   ├── api/                    # REST API server (Flask)
│   ├── sensors/                # Sensor data collection
│   ├── storage/                # SQLite local database
│   ├── utils/                  # Network, hotspot, config
│   └── backend_client.py       # Cloud API communication
├── raspberry-pi/
│   └── actuator_controller.py  # Standalone actuator script
├── arduino-uno/                # Arduino sensor code
├── logs/                       # Auto-generated logs
├── data/                       # Local database files
└── documents/                  # Schema and documentation
```

## Hardware Requirements

- **Raspberry Pi 3 Model B** (or Zero 2W)
- **SCD41 CO₂, Temperature, and Humidity Sensor**
- **I2C LCD Display** (20x4 characters)
- **Actuators** (Fans, Humidifiers, etc.)
- **Power supply** and wiring components

## Software Requirements

- **Python 3.9+**
- **Raspberry Pi OS** (Lite or Desktop)
- **Required Python packages** (see requirements.txt)

## Quick Start

### On Raspberry Pi

```bash
# 1. SSH into your Raspberry Pi
ssh mash@MASH-CHAMBER

# 2. Navigate to project directory
cd ~/MASH-IoT-Device

# 3. Run installation script
chmod +x install.sh
./install.sh

# 4. Create environment file
cp .env.example .env
nano .env

# 5. Reboot to start service
sudo reboot
```

### After Reboot

The device will automatically:
1. Start the MASH service
2. Check for WiFi connection
3. Create hotspot `MASH-Chamber-XXXXXX` if not connected
4. Wait for mobile app to configure WiFi

### Test Manually

```bash
# Start service
sudo systemctl start mash-device

# Check status
sudo systemctl status mash-device

# View logs
sudo journalctl -u mash-device -f

# Test in mock mode (no hardware needed)
python3 main.py --mock
```

### API Endpoints

When hotspot is active:
- **Provisioning Info**: `http://192.168.4.1:5000/api/v1/provisioning/info`
- **WiFi Scan**: `http://192.168.4.1:5000/api/v1/wifi/scan`
- **WiFi Config**: `POST http://192.168.4.1:5000/api/v1/wifi/config`
- **Device Status**: `http://192.168.4.1:5000/api/v1/status`
- **Actuator Control**: `POST http://192.168.4.1:5000/api/v1/commands/actuator_control`

## Configuration

### Environment Variables

Key configuration variables:

```bash
# Device Identity
DEVICE_ID=mash_device_001
DEVICE_NAME="MASH Chamber #1"

# Backend API
BACKEND_API_URL=https://mash-backend.onrender.com/api
BACKEND_API_KEY=your_api_key

# MQTT Configuration
MQTT_BROKER_URL=mqtt://your_broker:1883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password

# Sensor Settings
SENSOR_READ_INTERVAL=60
MOCK_MODE=false
```

### Control Thresholds

```bash
# Temperature Control
TEMP_MIN=25.0
TEMP_MAX=28.0
TEMP_CRITICAL_HIGH=32.0

# Humidity Control
HUMIDITY_MIN=80.0
HUMIDITY_MAX=90.0

# CO₂ Management
CO2_OPTIMAL_MIN=10000
CO2_OPTIMAL_MAX=15000
CO2_CRITICAL_HIGH=20000
```

## Usage

### Basic Operation

```bash
# Start device
python main.py

# Run in mock mode (for testing)
python main.py --mock

# Enable debug logging
python main.py --debug

# Check device status
python main.py --status
```

### Development Mode

```bash
# Run with mock sensors and debug output
python main.py --mock --debug

# Test sensor reading
python -c "
from src.sensors import SensorManager
sm = SensorManager(mock_mode=True)
sm.start()
time.sleep(5)
print(sm.get_latest_reading())
sm.stop()
"
```

## Project Structure

```
MASH-IoT-Device/
├── src/
│   ├── sensors/          # Sensor drivers and interfaces
│   │   ├── __init__.py
│   │   ├── scd41_sensor.py
│   │   ├── sensor_reading.py
│   │   └── sensor_manager.py
│   ├── actuators/        # Actuator control (mocked initially)
│   ├── display/          # LCD display (mocked initially)
│   ├── mqtt/             # MQTT client and communication
│   ├── storage/          # SQLite database operations
│   │   ├── __init__.py
│   │   ├── database_manager.py
│   │   ├── schema.py
│   │   └── sync_manager.py
│   └── utils/            # Helper functions and configs
│       ├── __init__.py
│       ├── config.py
│       └── logger.py
├── tests/                # Unit and integration tests
├── config/                # Configuration files
├── data/                  # Local data storage (SQLite)
├── logs/                  # Application logs
├── main.py               # Main application entry point
├── requirements.txt      # Python dependencies
├── env.example          # Environment variables template
└── README.md            # This file
```

## Database Schema

The local SQLite database is aligned with the backend PostgreSQL schema:

- **device_info** - Device information and configuration
- **sensor_readings** - Sensor data with sync status
- **device_commands** - Commands from backend or local
- **alerts** - Generated alerts and notifications
- **actuator_states** - Current actuator states
- **sync_queue** - Data pending upload to backend
- **system_logs** - Application logs
- **config_cache** - Configuration values

## API Integration

### Backend Endpoints

- **Device Registration**: `POST /api/devices`
- **Sensor Data Sync**: `POST /api/sensors/data`
- **Alert Sync**: `POST /api/alerts`
- **Command Retrieval**: `GET /api/devices/:id/commands`

### MQTT Topics

- **Sensor Data**: `mash/device/{device_id}/sensors`
- **Device Status**: `mash/device/{device_id}/status`
- **Commands**: `mash/device/{device_id}/commands`
- **Alerts**: `mash/device/{device_id}/alerts`

## Development Workflow

### Cross-Development Setup

1. **Windows Development**:
   - Install Python 3.9+
   - Install VSCode with Python extensions
   - Use mock mode for testing

2. **Raspberry Pi Deployment**:
   - Enable SSH on RPi
   - Deploy code via Git or SCP
   - Test with real hardware

3. **Remote Development**:
   ```bash
   # SSH to Raspberry Pi
   ssh pi@<rpi-ip>
   
   # Clone and run
   git clone <repository>
   cd MASH-IoT-Device
   python main.py
   ```

## Testing

### Unit Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_sensors.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Integration Tests

```bash
# Test sensor reading
python -c "
from src.sensors import SensorManager
sm = SensorManager(mock_mode=True)
sm.start()
time.sleep(10)
print('Latest reading:', sm.get_latest_reading())
sm.stop()
"

# Test database operations
python -c "
from src.storage import DatabaseManager
db = DatabaseManager('./test.db')
print('Database stats:', db.get_database_stats())
"
```

## Troubleshooting

### Common Issues

1. **Sensor Not Detected**:
   - Check I2C is enabled: `sudo raspi-config`
   - Verify wiring connections
   - Use mock mode for testing

2. **Database Errors**:
   - Check file permissions
   - Ensure data directory exists
   - Verify SQLite installation

3. **MQTT Connection Failed**:
   - Check network connectivity
   - Verify broker credentials
   - Test with local broker first

### Debug Mode

```bash
# Enable debug logging
python main.py --debug

# Check logs
tail -f logs/mash_device.log

# Monitor system resources
htop
```

## Hardware Setup

### SCD41 Sensor Wiring

```
SCD41    →    Raspberry Pi
VCC      →    3.3V (Pin 1)
GND      →    GND (Pin 6)
SCL      →    GPIO 3 (Pin 5)
SDA      →    GPIO 2 (Pin 3)
```

### I2C LCD Display (Future)

```
LCD      →    Raspberry Pi
VCC      →    5V (Pin 2)
GND      →    GND (Pin 6)
SCL      →    GPIO 3 (Pin 5)
SDA      →    GPIO 2 (Pin 3)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of the M.A.S.H. thesis research project.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the logs in `logs/mash_device.log`
- Create an issue in the repository

---

**Version**: 1.0  
**Created**: October 2025  
**Target Completion**: October 31, 2025