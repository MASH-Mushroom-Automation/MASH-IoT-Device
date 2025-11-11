# MASH IoT Device - Quick Start Guide

## System Overview

```
┌─────────────────┐      Serial      ┌──────────────────┐      HTTP/WS     ┌─────────────────┐
│  Arduino Uno R3 │ ←──────────────→ │  Raspberry Pi 3  │ ←──────────────→ │   Mobile App    │
│   (Sensors)     │                  │  (Controller)    │                  │   (Flutter)     │
└─────────────────┘                  └──────────────────┘                  └─────────────────┘
        │                                     │                                      │
        │                                     │                                      │
    SCD41 Sensor                         GPIO Relays                          User Interface
    (Temp/Hum/CO2)                       (Actuators)                          (Control/Monitor)
                                                │
                                                │
                                                ↓
                                         ┌──────────────────┐
                                         │  Backend API     │
                                         │  (NestJS)        │
                                         └──────────────────┘
                                         Data Storage & Analytics
```

## Hardware Setup

### Arduino Uno R3
- **SCD41 Sensor** (I2C):
  - VCC → 5V
  - GND → GND
  - SDA → A4
  - SCL → A5

- **LCD 2004 I2C** (Optional):
  - VCC → 5V
  - GND → GND
  - SDA → A4
  - SCL → A5

### Raspberry Pi 3
- **GPIO Pins** (BCM numbering):
  - GPIO 22 → Blower Fan Relay
  - GPIO 27 → Exhaust Fan Relay
  - GPIO 17 → Humidifier Relay
  - GPIO 18 → LED Lights Relay

- **USB Connection**:
  - Arduino Uno R3 → USB port (Serial: `/dev/ttyACM0`)

- **Network**:
  - Connect to same WiFi/network as mobile app

## Software Installation

### 1. Arduino Uno R3

#### Install Libraries (Arduino IDE):
```
Tools → Manage Libraries → Install:
- SensirionI2cScd4x
- LiquidCrystal_I2C
```

#### Upload Code:
1. Open `arduino-uno/test_scd41/test_scd41.ino`
2. Select Board: `Arduino Uno`
3. Select Port: `COM3` (Windows) or `/dev/ttyACM0` (Linux)
4. Click Upload

#### Verify:
Open Serial Monitor (9600 baud) - you should see sensor readings:
```
SENSOR,12345,1200,22.5,92.3,SPAWNING,0
```

### 2. Raspberry Pi 3

#### Install Dependencies:
```bash
cd /home/pi/MASH-IoT-Device
pip3 install -r requirements.txt
```

#### Configure Device ID:
Edit `integrated_server.py`:
```python
DEVICE_ID = 'MASH-A1-CAL25-AC2415'  # Your unique device ID
DEVICE_NAME = 'Mushroom Prototype Chamber'
```

#### Run Server:
```bash
python3 integrated_server.py
```

You should see:
```
🚀 Starting MASH IoT Device Server
📱 Device ID: MASH-A1-CAL25-AC2415
✅ Serial connection established on /dev/ttyACM0
📊 Sensor data reader started
🌐 Starting HTTP server on port 5000
```

#### Find RPi IP Address:
```bash
hostname -I
```
Example output: `192.168.1.100`

#### Test API:
```bash
# From another device on same network
curl http://192.168.1.100:5000/api/status

# Should return:
{
  "success": true,
  "data": {
    "deviceId": "MASH-A1-CAL25-AC2415",
    "status": "online"
  }
}
```

### 3. Auto-start on Boot (Optional)

Create systemd service:
```bash
sudo nano /etc/systemd/system/mash-device.service
```

Add:
```ini
[Unit]
Description=MASH IoT Device Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/MASH-IoT-Device
ExecStart=/usr/bin/python3 /home/pi/MASH-IoT-Device/integrated_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mash-device
sudo systemctl start mash-device
sudo systemctl status mash-device
```

View logs:
```bash
sudo journalctl -u mash-device -f
```

## API Endpoints

### Local Device API (RPi)

**Base URL:** `http://<RPI_IP>:5000/api`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Device status |
| `/sensor/current` | GET | Current sensor data |
| `/sensor/history` | GET | Sensor history (last 30 readings) |
| `/mode` | POST | Set mode (Spawning/Fruiting) |
| `/actuator` | POST | Control actuator |
| `/actuators` | GET | Get all actuator states |
| `/health` | GET | Health check |

### Examples

#### Get Current Sensor Data:
```bash
curl http://192.168.1.100:5000/api/sensor/current
```

Response:
```json
{
  "success": true,
  "data": {
    "co2": 12500,
    "temperature": 22.5,
    "humidity": 92.3,
    "mode": "s",
    "alert": false,
    "timestamp": "2024-11-06T06:30:00",
    "actuators": {
      "blower_fan": false,
      "exhaust_fan": false,
      "humidifier": true,
      "led_lights": false
    }
  }
}
```

#### Set Mode to Fruiting:
```bash
curl -X POST http://192.168.1.100:5000/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode":"f"}'
```

#### Turn On Humidifier:
```bash
curl -X POST http://192.168.1.100:5000/api/actuator \
  -H "Content-Type: application/json" \
  -d '{"actuator":"humidifier","state":true}'
```

## Mobile App Connection

**IMPORTANT:** Both mobile device and RPi3 must be on the **same WiFi network**.

### 1. Ensure Same Network
- Connect RPi3 to your WiFi router
- Connect mobile device to the **same WiFi network**
- Verify connectivity: `ping 192.168.1.100` (from another device)

### 2. Connect to Device
In the mobile app:
1. Go to "Devices" tab
2. Tap "Add Device" or "Connect Device"
3. Enter device details:
   - **Device ID:** `MASH-A1-CAL25-AC2415`
   - **IP Address:** `192.168.1.100` (your RPi's IP)
   - **Port:** `5000`
4. Tap "Connect"

### 3. Monitor & Control
- View real-time sensor data (CO2, Temperature, Humidity)
- Switch between Spawning/Fruiting modes
- Control actuators (Blower Fan, Exhaust Fan, Humidifier, LED Lights)

**Note:** If connection fails, verify:
- Both devices on same WiFi
- RPi server is running: `sudo systemctl status mash-device`
- Firewall allows port 5000: `sudo ufw allow 5000`

## Troubleshooting

### Arduino Issues

**Problem:** No sensor data in Serial Monitor
```bash
# Check I2C connections
# Verify SCD41 address (should be 0x62)
# Ensure libraries are installed
```

**Problem:** "ERROR: SCD41 sensor not detected"
```bash
# Check wiring (SDA, SCL, VCC, GND)
# Try different I2C address (0x62 or 0x61)
# Test with I2C scanner sketch
```

### Raspberry Pi Issues

**Problem:** "Failed to connect to Arduino"
```bash
# Check USB connection
# Verify serial port
ls /dev/tty*

# Try different port
SERIAL_PORT = '/dev/ttyUSB0'  # or /dev/ttyACM1
```

**Problem:** GPIO not working
```bash
# Check if running as root or in gpio group
sudo usermod -a -G gpio pi

# Test GPIO
python3 raspberry-pi/relay-tester.py --targets 1
```

**Problem:** Can't access API from mobile
```bash
# Check firewall
sudo ufw allow 5000

# Verify same network
ping 192.168.1.100

# Check server is running
sudo systemctl status mash-device
```

### Mobile App Issues

**Problem:** Can't connect to device
```bash
# Verify same WiFi network
# Check RPi IP address (may have changed)
# Test API with curl first
curl http://192.168.1.100:5000/api/status
```

## Serial Protocol Reference

### Arduino → RPi (Sensor Data)
```
SENSOR,<timestamp>,<co2>,<temp>,<humidity>,<mode>,<alert>
Example: SENSOR,12345,1200,22.5,92.3,SPAWNING,0
```

### RPi → Arduino (Commands)
```
s         # Set Spawning mode
f         # Set Fruiting mode
```

### Arduino → RPi (Mode Change)
```
MODE,<mode_name>
Example: MODE,FRUITING
```

### Arduino → RPi (Alert)
```
ALERT,<timestamp>,<mode>,<co2>
Example: ALERT,12345,SPAWNING,9500
```

## Operating Modes

### Spawning Mode
- **Temperature:** 20-25°C
- **Humidity:** 90-95%
- **CO2:** >10,000 ppm (high)
- **Light:** OFF
- **Focus:** Mycelium growth

### Fruiting Mode
- **Temperature:** 15-20°C
- **Humidity:** 85-90%
- **CO2:** 500-800 ppm (low)
- **Light:** ON (12h/day)
- **Focus:** Mushroom production

## Next Steps

1. ✅ Hardware setup complete
2. ✅ Software installed and running
3. ✅ API tested and working
4. 🔄 Register device in backend
5. 🔄 Connect mobile app
6. 🔄 Collect baseline data
7. 🔄 Train ML model for automation
8. 🔄 Enable automatic control

## Support

For issues or questions:
- Check logs: `sudo journalctl -u mash-device -f`
- Review API docs: `API_SPECIFICATION.md`
- Test hardware: `python3 raspberry-pi/relay-tester.py`

---

**Device ID:** MASH-A1-CAL25-AC2415  
**Version:** 1.0  
**Last Updated:** 2025-11-06
