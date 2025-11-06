# MASH IoT - Raspberry Pi ML Decision Engine

## Overview

This system receives sensor data from Arduino and uses ML-based trend analysis to control actuators (exhaust fan, intake fan, humidifier) for optimal mushroom growing conditions.

## Architecture

```
Arduino (Sensor Hub)
    ↓ Serial (USB)
Raspberry Pi (Decision Engine)
    ↓ GPIO
Relay Module → Actuators
```

## Hardware Setup

### GPIO Pin Assignments (BCM numbering)
- **GPIO 17**: Exhaust Fan Relay
- **GPIO 18**: Intake Fan Relay  
- **GPIO 27**: Humidifier Relay

### Wiring
1. Connect Arduino Mega to Raspberry Pi via USB
2. Connect relay module to Raspberry Pi GPIO pins
3. Connect actuators to relay module (separate power supply)

## Software Setup

### 1. Install Dependencies

```bash
sudo apt-get update
sudo apt-get install python3-pip python3-serial python3-rpi.gpio

pip3 install pandas numpy pyserial
```

### 2. Create Directory Structure

```bash
mkdir -p /home/pi/mash_iot/{logs,models,data}
```

### 3. Copy Files

```bash
# Copy Python scripts to Raspberry Pi
scp actuator_controller.py pi@raspberrypi:/home/pi/mash_iot/
scp train_decision_model.py pi@raspberrypi:/home/pi/mash_iot/
```

### 4. Set Permissions

```bash
chmod +x /home/pi/mash_iot/actuator_controller.py
chmod +x /home/pi/mash_iot/train_decision_model.py
```

## Usage

### Running the Controller

```bash
cd /home/pi/mash_iot
python3 actuator_controller.py
```

### Training the Model (Optional)

If you have historical data:

```bash
# Place your training data in /home/pi/mash_iot/data/training_data.csv
python3 train_decision_model.py
```

### Auto-start on Boot

Create systemd service:

```bash
sudo nano /etc/systemd/system/mash-iot.service
```

Add:

```ini
[Unit]
Description=MASH IoT Actuator Controller
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/mash_iot
ExecStart=/usr/bin/python3 /home/pi/mash_iot/actuator_controller.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable mash-iot.service
sudo systemctl start mash-iot.service
sudo systemctl status mash-iot.service
```

## Data Format

### Arduino → Raspberry Pi (Serial)

**Sensor Data:**
```
SENSOR,timestamp,co2,temperature,humidity,mode,alert
Example: SENSOR,12345,650,20.5,91.2,FRUITING,0
```

**Alert:**
```
ALERT,timestamp,mode,co2
Example: ALERT,12350,FRUITING,1200
```

**Mode Change:**
```
MODE,mode_name
Example: MODE,SPAWNING
```

## Decision Logic

The ML engine analyzes:
1. **Current values**: CO2, temperature, humidity
2. **Trends**: Rate of change over last 10 readings
3. **Mode**: SPAWNING vs FRUITING requirements

### Spawning Mode
- Target: CO2 > 10,000 ppm
- Actions: Minimize ventilation, maintain high CO2

### Fruiting Mode
- Target: CO2 500-800 ppm
- Actions: Active ventilation control based on trends

### Trend-Based Decisions
- **Rising CO2 + Above threshold** → Activate exhaust
- **Dropping humidity + Below minimum** → Activate humidifier
- **Gradual changes** → Minimal intervention (avoid false positives)

## Training Data Format

CSV format with columns:
- `timestamp`: Date and time
- `co2`: CO2 level (ppm)
- `temperature`: Temperature (°C)
- `humidity`: Humidity (%)
- `mode`: SPAWNING or FRUITING
- `exhaust_fan`: 0 or 1
- `intake_fan`: 0 or 1
- `humidifier`: 0 or 1
- `outcome`: success, failure, or warning
- `notes`: Optional observations

See `training_data_template.csv` for examples.

## Monitoring

### View Logs
```bash
tail -f /home/pi/mash_iot/logs/actuator_control.log
```

### Check Status
```bash
sudo systemctl status mash-iot.service
```

## Troubleshooting

### Arduino Not Detected
```bash
# Check USB devices
ls -l /dev/ttyACM*
ls -l /dev/ttyUSB*

# Add user to dialout group
sudo usermod -a -G dialout pi
```

### GPIO Permissions
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi
```

### Test Relays Manually
```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.HIGH)  # Turn on
GPIO.output(17, GPIO.LOW)   # Turn off
GPIO.cleanup()
```

## Memory Optimization (1GB RAM)

The system is optimized for Raspberry Pi 3 with 1GB RAM:
- Uses `deque` with fixed window size (30 readings)
- Simple statistical analysis instead of heavy ML libraries
- Rule-based logic with learned thresholds
- No TensorFlow/PyTorch (can add TFLite if needed)

## Future Enhancements

- [ ] Add TensorFlow Lite for more sophisticated predictions
- [ ] Web dashboard for monitoring
- [ ] MQTT integration for remote control
- [ ] Data logging to SQLite
- [ ] Automated model retraining

## License

MIT License - See main project README
