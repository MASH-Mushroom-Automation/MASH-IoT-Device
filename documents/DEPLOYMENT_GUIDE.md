# MASH IoT Device - Deployment & Operation Guide

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Hardware Requirements](#hardware-requirements)
3. [Installation](#installation)
4. [Network Provisioning Flow](#network-provisioning-flow)
5. [API Endpoints](#api-endpoints)
6. [Actuator Control](#actuator-control)
7. [Backend Communication](#backend-communication)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

The MASH IoT Device is a Raspberry Pi 3 Model B-based mushroom cultivation automation system that:
- Reads sensor data from Arduino Uno (CO2, Temperature, Humidity)
- Controls actuators (fans, humidifier, LED lights) via GPIO relays
- Provides WiFi provisioning via hotspot for easy setup
- Connects to backend API for cloud control and monitoring
- Exposes local REST API for direct mobile app control

### Architecture

```
┌─────────────────┐
│  Arduino Uno    │ ◄─── SCD41 Sensor (CO2, Temp, Humidity)
│  (Sensor Bridge)│
└────────┬────────┘
         │ Serial (USB)
         ▼
┌─────────────────────────────────────┐
│   Raspberry Pi 3 Model B            │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Main Application (main.py)  │  │
│  │                              │  │
│  │  • Sensor Data Collection    │  │
│  │  • Actuator Control          │  │
│  │  • Network Management        │  │
│  │  • API Server (Port 5000)    │  │
│  │  • Backend Communication     │  │
│  └──────────────────────────────┘  │
│                                     │
│  GPIO Pins ──► Relay Module ──► Actuators
│                (4-Channel)       (Fans, Humidifier, Lights)
└─────────────────────────────────────┘
         │
         │ WiFi/Internet
         ▼
┌──────────────────┐       ┌────────────────┐
│  Mobile App      │       │  Backend API   │
│  (Direct/Local)  │       │  (Cloud)       │
└──────────────────┘       └────────────────┘
```

---

## 🛠️ Hardware Requirements

### Components
- **Raspberry Pi 3 Model B** (1GB RAM)
- **Arduino Uno** with USB cable
- **SCD41 Sensor** (CO2, Temperature, Humidity)
- **4-Channel Relay Module** (5V, active HIGH)
- **Actuators:**
  - Exhaust Fan (12V)
  - Intake Fan (12V)
  - Humidifier
  - LED Grow Lights
- **Power Supply:** 5V 3A for Raspberry Pi, 12V for actuators
- **MicroSD Card:** 16GB minimum

### GPIO Wiring (BCM Numbering)

| Actuator | GPIO Pin | Physical Pin | Relay Channel |
|----------|----------|--------------|---------------|
| Exhaust Fan | GPIO 27 | Pin 13 | CH1 |
| Intake Fan | GPIO 22 | Pin 15 | CH2 |
| Humidifier | GPIO 17 | Pin 11 | CH3 |
| LED Lights | GPIO 18 | Pin 12 | CH4 |

---

## 📦 Installation

### 1. Prepare Raspberry Pi

```bash
# Flash Raspberry Pi OS Lite (64-bit) to SD card
# Enable SSH before first boot (create empty 'ssh' file in boot partition)

# First boot - SSH into Pi
ssh pi@raspberrypi.local
# Default password: raspberry

# Change default password
passwd

# Update system
sudo apt-get update && sudo apt-get upgrade -y
```

### 2. Clone Repository

```bash
cd /home/pi
git clone https://github.com/your-org/mash-iot-device.git mash-iot
cd mash-iot
```

### 3. Run Installation Script

```bash
chmod +x install.sh
./install.sh
```

The installation script will:
- Install system dependencies (NetworkManager, Python, GPIO libraries)
- Create Python virtual environment
- Install Python packages
- Set up systemd service for auto-boot
- Configure network interfaces
- Generate unique device ID

### 4. Configure Environment

Edit `/home/pi/mash-iot/.env`:

```bash
# Device Configuration
DEVICE_ID=MASH-A1-CAL25-XXXXXX  # Auto-generated
DEVICE_NAME=MASH Chamber #1

# Backend Configuration
BACKEND_API_URL=https://mash-backend.onrender.com/api
BACKEND_API_KEY=your_api_key_here

# Sensor Configuration
SENSORS_SOURCE=arduino_bridge
SENSORS_SERIAL_PORT=/dev/ttyACM0
SENSORS_SERIAL_BAUD=9600

# Network Configuration
WIFI_INTERFACE=wlan0
HOTSPOT_SSID_PREFIX=MASH-Chamber

# Development
MOCK_MODE=false
DEBUG_MODE=false
```

### 5. Start Service

```bash
# Start service immediately
sudo systemctl start mash-device

# Check status
sudo systemctl status mash-device

# View logs
sudo journalctl -u mash-device -f

# The service will auto-start on boot
```

---

## 🌐 Network Provisioning Flow

### Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    POWER ON / BOOT                       │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  Check WiFi   │
                 │  Connection   │
                 └───────┬───────┘
                         │
            ┌────────────┴────────────┐
            │                         │
        ✓ Connected              ✗ Not Connected
            │                         │
            ▼                         ▼
    ┌───────────────┐         ┌──────────────────┐
    │ Register with │         │  Start Hotspot   │
    │    Backend    │         │  MASH-Chamber-XX │
    │               │         │  IP: 192.168.4.1 │
    └───────┬───────┘         └────────┬─────────┘
            │                          │
            │                          ▼
            │                 ┌──────────────────┐
            │                 │  Wait for Mobile │
            │                 │   App to Connect │
            │                 └────────┬─────────┘
            │                          │
            │                          ▼
            │                 ┌──────────────────┐
            │                 │ Mobile App Scans │
            │                 │  WiFi Networks   │
            │                 │ GET /api/v1/wifi/scan
            │                 └────────┬─────────┘
            │                          │
            │                          ▼
            │                 ┌──────────────────┐
            │                 │ User Selects WiFi│
            │                 │ Enters Password  │
            │                 │ POST /api/v1/wifi/config
            │                 └────────┬─────────┘
            │                          │
            │                          ▼
            │                 ┌──────────────────┐
            │                 │  Stop Hotspot    │
            │                 │  Connect to WiFi │
            │                 └────────┬─────────┘
            │                          │
            │                  ┌───────┴────────┐
            │                  │                │
            │              ✓ Success       ✗ Failed
            │                  │                │
            │                  │                ▼
            │                  │       ┌──────────────┐
            │                  │       │ Restart      │
            │                  │       │ Hotspot      │
            │                  │       │ Retry        │
            │                  │       └──────────────┘
            │                  │
            └──────────────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Register Device  │
            │  with Backend    │
            │ (User ID + Info) │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │  Start Normal    │
            │   Operations:    │
            │ • Sensor Reading │
            │ • Data Logging   │
            │ • AI Predictions │
            │ • Cloud Sync     │
            └──────────────────┘
```

### Detailed Steps

#### 1. Device Boot (Not Connected to WiFi)

When the device boots and has no WiFi connection:

```
[INFO] ⚠️  Device not connected to WiFi
[INFO] 🔄 Starting provisioning mode (hotspot)
[INFO] ✓ Provisioning hotspot active
[INFO] 📱 Connect to WiFi: MASH-Chamber-D5A91F
[INFO] 🌐 Access setup at: http://192.168.4.1:5000
```

#### 2. Mobile App Connection

The mobile app (Grower Mobile) connects to the hotspot:
- SSID: `MASH-Chamber-XXXXXX` (last 6 chars of device ID)
- Password: None (open network)
- Access: `http://192.168.4.1:5000`

#### 3. WiFi Configuration API

**Scan for Networks:**
```http
GET http://192.168.4.1:5000/api/v1/wifi/scan

Response:
{
  "success": true,
  "networks": [
    {
      "ssid": "Home WiFi",
      "signal": 85,
      "security": "WPA2",
      "frequency": "2.4 GHz"
    },
    ...
  ],
  "timestamp": "2025-11-06T01:00:00Z"
}
```

**Configure WiFi:**
```http
POST http://192.168.4.1:5000/api/v1/wifi/config
Content-Type: application/json

{
  "ssid": "Home WiFi",
  "password": "your_wifi_password"
}

Response:
{
  "success": true,
  "message": "Connecting to Home WiFi",
  "timestamp": "2025-11-06T01:00:05Z"
}
```

#### 4. Connection Process

The device will:
1. Stop the hotspot
2. Attempt to connect to the specified WiFi
3. If **successful**:
   - Connect to backend API
   - Register device with user
   - Start normal operations
4. If **failed**:
   - Restart hotspot
   - Wait for retry

#### 5. Backend Registration

Once connected to internet:

```
[INFO] Attempting to register with backend...
[INFO] ✓ Device registered with backend
```

The device sends registration data:
```json
{
  "userId": "user-id-from-mobile-app",
  "serialNumber": "MASH-A1-CAL25-D5A91F",
  "name": "MASH Chamber #1",
  "type": "MUSHROOM_CHAMBER",
  "location": "Greenhouse",
  "firmware": "1.0.0",
  "ipAddress": "192.168.1.100",
  "status": "ONLINE"
}
```

---

## 🔌 API Endpoints

### Provisioning Endpoints

#### GET `/api/v1/provisioning/info`
Get current provisioning status

**Response:**
```json
{
  "success": true,
  "data": {
    "active": true,
    "ssid": "MASH-Chamber-D5A91F",
    "ip_address": "192.168.4.1",
    "password_protected": false,
    "device_id": "MASH-A1-CAL25-D5A91F",
    "network_connected": false,
    "backend_registered": false
  }
}
```

#### GET `/api/v1/wifi/scan`
Scan for available WiFi networks

**Response:**
```json
{
  "success": true,
  "networks": [
    {
      "ssid": "Home WiFi",
      "signal": 85,
      "security": "WPA2",
      "frequency": "2.4 GHz"
    }
  ]
}
```

#### POST `/api/v1/wifi/config`
Configure WiFi connection

**Request:**
```json
{
  "ssid": "Home WiFi",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connecting to Home WiFi"
}
```

### Sensor Endpoints

#### GET `/api/v1/sensors/latest`
Get latest sensor readings

**Response:**
```json
{
  "co2": 1200,
  "temperature": 25.5,
  "humidity": 85.2,
  "timestamp": "2025-11-06T01:00:00Z",
  "source": "arduino_bridge"
}
```

### Actuator Control Endpoints

#### POST `/api/v1/commands/actuator_control`
Control actuators

**Request (Set specific actuators):**
```json
{
  "action": "set",
  "exhaust_fan": true,
  "intake_fan": true,
  "humidifier": false,
  "led_lights": true
}
```

**Request (Get state):**
```json
{
  "action": "get_state"
}
```

**Request (Turn all off):**
```json
{
  "action": "all_off"
}
```

**Request (Set mode):**
```json
{
  "action": "set_mode",
  "mode": "AUTO"
}
```

**Response:**
```json
{
  "success": true,
  "state": {
    "exhaust_fan": true,
    "intake_fan": true,
    "humidifier": false,
    "led_lights": true,
    "last_update": "2025-11-06T01:00:00Z",
    "mode": "MANUAL"
  }
}
```

### Device Status

#### GET `/api/v1/status`
Get complete device status

**Response:**
```json
{
  "running": true,
  "timestamp": "2025-11-06T01:00:00Z",
  "config": {
    "device_id": "MASH-A1-CAL25-D5A91F",
    "mock_mode": false,
    "sensor_interval": 60,
    "sensor_source": "arduino_bridge"
  },
  "arduino_bridge": {
    "connected": true,
    "readings_received": 1234
  },
  "network": {
    "connected": true,
    "connection": {
      "ssid": "Home WiFi",
      "ip_address": "192.168.1.100"
    }
  },
  "actuators": {
    "exhaust_fan": false,
    "intake_fan": false,
    "humidifier": true,
    "led_lights": false
  }
}
```

---

## 🎮 Actuator Control

### Local Control (Same Network)

When mobile app and device are on the same WiFi:

```http
POST http://192.168.1.100:5000/api/v1/commands/actuator_control
Content-Type: application/json

{
  "action": "set",
  "led_lights": true
}
```

### Cloud Control (Different Networks)

When mobile app and device are on different networks (both have internet):

```
Mobile App → Backend API → Device (via MQTT/WebSocket)
```

**Flow:**
1. Mobile app sends command to backend
2. Backend stores command in `device_commands` table
3. Device polls backend for pending commands
4. Device executes command and acknowledges

**Backend API Call (from Mobile):**
```http
POST https://mash-backend.onrender.com/api/device-commands
Content-Type: application/json
Authorization: Bearer user_token

{
  "deviceId": "device-db-id",
  "command": "actuator_control",
  "parameters": {
    "action": "set",
    "led_lights": true
  }
}
```

**Device Polling:**
```http
GET https://mash-backend.onrender.com/api/device-commands/device/{deviceId}/pending
Authorization: Bearer device_api_key
```

---

## 🌍 Backend Communication

### Device Registration

```python
# In main.py
def _try_backend_registration(self):
    device_info = {
        'name': 'MASH Chamber #1',
        'type': 'MUSHROOM_CHAMBER',
        'firmware': '1.0.0',
        'ip_address': '192.168.1.100'
    }
    
    success = self.backend_client.register_device(
        user_id='user-id',
        device_info=device_info
    )
```

### Sensor Data Sync

```python
# Automatic sync every 5 minutes
sensor_data = {
    'type': 'environment',
    'value': reading.co2,
    'unit': 'ppm',
    'timestamp': datetime.now().isoformat()
}

self.backend_client.send_sensor_data(sensor_data)
```

### Health Monitoring

```python
health_data = {
    'status': 'HEALTHY',
    'cpu_usage': 25.5,
    'memory_usage': 45.2,
    'uptime': 86400
}

self.backend_client.send_health_data(health_data)
```

---

## 🔧 Troubleshooting

### Hotspot Not Starting

**Issue:** Hotspot doesn't turn on after boot

**Solutions:**
1. Check NetworkManager is running:
   ```bash
   sudo systemctl status NetworkManager
   sudo systemctl start NetworkManager
   ```

2. Check for conflicting services:
   ```bash
   # Disable dhcpcd if active
   sudo systemctl disable dhcpcd
   sudo systemctl stop dhcpcd
   ```

3. Manual hotspot test:
   ```bash
   nmcli device wifi hotspot ifname wlan0 ssid TestHotspot
   ```

4. Check logs:
   ```bash
   sudo journalctl -u mash-device -n 100
   ```

### WiFi Connection Fails

**Issue:** Device can't connect to WiFi

**Solutions:**
1. Check WiFi credentials
2. Check signal strength (should be > 50%)
3. Verify router allows new connections
4. Check logs for error messages

### No Sensor Data

**Issue:** Not receiving data from Arduino

**Solutions:**
1. Check USB connection:
   ```bash
   ls -l /dev/ttyACM*
   ```

2. Check Arduino is running sensor code

3. Test serial connection:
   ```bash
   screen /dev/ttyACM0 9600
   ```

### Actuators Not Responding

**Issue:** Relays not switching

**Solutions:**
1. Check GPIO connections
2. Verify relay module power (5V)
3. Test GPIO manually:
   ```python
   import RPi.GPIO as GPIO
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(27, GPIO.OUT)
   GPIO.output(27, GPIO.HIGH)  # Should activate
   ```

4. Check permissions:
   ```bash
   groups pi
   # Should include: gpio
   ```

---

## 📝 Testing Checklist

- [ ] Device boots and shows log messages
- [ ] Hotspot starts when no WiFi configured
- [ ] Mobile can connect to hotspot
- [ ] WiFi scan returns networks
- [ ] WiFi configuration works
- [ ] Device connects to internet
- [ ] Backend registration succeeds
- [ ] Sensor data is received
- [ ] Actuators can be controlled via API
- [ ] Device auto-starts on boot
- [ ] Logs are written correctly

---

## 📚 Additional Resources

- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)
- [NetworkManager Guide](https://wiki.archlinux.org/title/NetworkManager)
- [GPIO Control](https://pinout.xyz/)
- [Backend API Documentation](https://mash-backend.onrender.com/api-docs)
