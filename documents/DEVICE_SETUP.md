# MASH IoT Device Setup Guide

## Overview
This guide explains how to set up the MASH IoT device using:
- **Raspberry Pi 3** (runs Python HTTP server)
- **Arduino Uno R3** (controls sensors and actuators)
- **Mobile App** (connects directly via same network)

## Architecture

```
Mobile App (Flutter) <--HTTP--> RPi3 <--Serial--> Arduino Uno R3 <--> Sensors/Relays
```

## Hardware Setup

### Arduino Uno R3 Connections

#### Sensors:
- **DHT22** (Temperature & Humidity)
  - VCC → 5V
  - GND → GND
  - DATA → Pin 2

- **MQ-135** (CO2 Sensor)
  - VCC → 5V
  - GND → GND
  - AOUT → A0

#### Relays (Active LOW):
- **Relay 1** (Humidifier) → Pin 7
- **Relay 2** (Exhaust Fan) → Pin 8
- **Relay 3** (Blower Fan) → Pin 9

### Raspberry Pi 3 Connections:
- **Arduino Uno R3** → USB port (Serial communication)
- **Network** → WiFi or Ethernet (same network as mobile app)

## Software Setup

### 1. Arduino Uno R3

1. Open `arduino_controller.ino` in Arduino IDE
2. Install required libraries:
   - DHT sensor library by Adafruit
3. Upload the sketch to Arduino Uno R3
4. Verify serial output at 9600 baud

### 2. Raspberry Pi 3

#### Install Dependencies:
```bash
cd /path/to/MASH-IoT-Device
pip3 install -r requirements.txt
```

#### Configure Device:
Edit `rpi_server.py` and set:
```python
DEVICE_ID = 'MASH-CHAMBER-001'  # Unique ID for this device
DEVICE_NAME = 'Mushroom Chamber 01'  # Human-readable name
SERIAL_PORT = '/dev/ttyACM0'  # Arduino serial port
```

#### Find Arduino Serial Port:
```bash
ls /dev/tty*
# Look for /dev/ttyACM0 or /dev/ttyUSB0
```

#### Run the Server:
```bash
python3 rpi_server.py
```

The server will start on port 5000.

#### Auto-start on Boot (Optional):
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
ExecStart=/usr/bin/python3 /home/pi/MASH-IoT-Device/rpi_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mash-device
sudo systemctl start mash-device
sudo systemctl status mash-device
```

### 3. Mobile App

The mobile app will connect to the RPi3 using its IP address on the same network.

#### Find RPi3 IP Address:
On RPi3:
```bash
hostname -I
```

Example: `192.168.1.100`

## API Endpoints

The RPi3 exposes the following REST API:

### GET /status
Get device status
```json
{
  "deviceId": "MASH-CHAMBER-001",
  "deviceName": "Mushroom Chamber 01",
  "status": "online",
  "timestamp": "2024-11-06T05:00:00"
}
```

### GET /data
Get current sensor data
```json
{
  "temperature": 25.5,
  "humidity": 85.2,
  "co2": 1200,
  "mode": "s",
  "actuators": {
    "humidifier": false,
    "exhaust_fan": false,
    "blower_fan": false
  },
  "timestamp": "2024-11-06T05:00:00"
}
```

### POST /mode
Set device mode
```json
{
  "mode": "s"  // "s" = Spawning, "f" = Fruiting
}
```

### POST /actuator
Control actuator
```json
{
  "actuator": "humidifier",  // or "exhaust_fan", "blower_fan"
  "state": true  // true = ON, false = OFF
}
```

### GET /health
Health check
```json
{
  "status": "healthy",
  "serial_connected": true,
  "timestamp": "2024-11-06T05:00:00"
}
```

## Serial Protocol (RPi ↔ Arduino)

### Arduino → RPi (Sensor Data):
Format: `T:25.5,H:85.2,C:1200`
- T = Temperature (°C)
- H = Humidity (%)
- C = CO2 (ppm)

### RPi → Arduino (Commands):

#### Mode Commands:
- `s` = Set Spawning mode
- `f` = Set Fruiting mode

#### Relay Commands:
- `R1:1` = Relay 1 ON (Humidifier)
- `R1:0` = Relay 1 OFF
- `R2:1` = Relay 2 ON (Exhaust Fan)
- `R2:0` = Relay 2 OFF
- `R3:1` = Relay 3 ON (Blower Fan)
- `R3:0` = Relay 3 OFF

## Testing

### Test Arduino:
1. Open Serial Monitor (9600 baud)
2. You should see sensor data: `T:25.5,H:85.2,C:1200`
3. Send commands: `s`, `f`, `R1:1`, `R1:0`

### Test RPi Server:
```bash
# Get status
curl http://localhost:5000/status

# Get sensor data
curl http://localhost:5000/data

# Set mode to Fruiting
curl -X POST http://localhost:5000/mode \
  -H "Content-Type: application/json" \
  -d '{"mode":"f"}'

# Turn on humidifier
curl -X POST http://localhost:5000/actuator \
  -H "Content-Type: application/json" \
  -d '{"actuator":"humidifier","state":true}'
```

### Test from Mobile App:
1. Ensure mobile device is on same network as RPi3
2. Use RPi3's IP address (e.g., `192.168.1.100`)
3. Connect to device in app
4. View sensor data and control actuators

## Troubleshooting

### Arduino not responding:
- Check USB connection
- Verify serial port: `ls /dev/tty*`
- Check baud rate (9600)
- Restart Arduino

### RPi server not starting:
- Check Python version: `python3 --version`
- Install dependencies: `pip3 install -r requirements.txt`
- Check port 5000 not in use: `sudo lsof -i :5000`

### Mobile app can't connect:
- Verify same network
- Check RPi3 IP: `hostname -I`
- Test with curl from another device
- Check firewall: `sudo ufw allow 5000`

### Sensors reading incorrect values:
- Check wiring
- Calibrate MQ-135 CO2 sensor
- Verify DHT22 is DHT22 (not DHT11)

## Network Configuration

Both RPi3 and mobile device must be on the same network:

### Option 1: Same WiFi Network
- Connect RPi3 to WiFi router
- Connect mobile device to same WiFi

### Option 2: Ethernet
- Connect RPi3 via Ethernet to router
- Connect mobile device to WiFi on same router

## Security Notes

- This setup is for local network only
- For production, add authentication
- Use HTTPS for secure communication
- Implement rate limiting

## Next Steps

1. **Register device in backend** - Add device to database
2. **Connect from mobile app** - Use device IP address
3. **Test data collection** - Verify sensor readings
4. **Test actuator control** - Control relays
5. **Implement automation** - Add AI/ML for automatic control
