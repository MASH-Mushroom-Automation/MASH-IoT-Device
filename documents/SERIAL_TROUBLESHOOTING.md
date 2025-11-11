# Serial Connection Troubleshooting Guide

## Problem: `serialConnected: false`

The server is running but can't connect to Arduino.

---

## Quick Fix Steps

### 1. Run Diagnostic Tool
```bash
cd /home/pi/MASH-IoT-Device
python3 check_serial.py
```

This will:
- List all available serial ports
- Test each port for Arduino data
- Show you the correct port to use

### 2. Check USB Connection
```bash
# List USB devices
lsusb

# Should show something like:
# Bus 001 Device 004: ID 2341:0043 Arduino SA Uno R3

# List serial ports
ls -l /dev/tty*

# Common Arduino ports:
# /dev/ttyACM0  - Arduino Uno/Mega
# /dev/ttyUSB0  - CH340 chip
# /dev/ttyACM1  - If multiple Arduinos
```

### 3. Check Permissions
```bash
# Add user to dialout group (for serial access)
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER

# Reboot for changes to take effect
sudo reboot

# Or logout and login again
```

### 4. Test Arduino Directly
```bash
# Install screen if not available
sudo apt-get install screen

# Connect to Arduino serial (9600 baud)
screen /dev/ttyACM0 9600

# You should see output like:
# SENSOR,12345,1200,22.5,92.3,SPAWNING,0

# Press Ctrl+A then K to exit screen
```

### 5. Update Serial Port in Code
If diagnostic tool finds Arduino on a different port:

Edit `integrated_server.py`:
```python
SERIAL_PORT = '/dev/ttyUSB0'  # Change to correct port
```

Then restart server:
```bash
sudo systemctl restart mash-device
# Or
python3 integrated_server.py
```

---

## Common Issues

### Issue 1: Port Not Found
**Symptoms:** No `/dev/ttyACM0` or `/dev/ttyUSB0`

**Solutions:**
```bash
# Check if Arduino is detected
dmesg | grep tty
dmesg | grep USB

# Reconnect Arduino USB cable
# Check cable is data cable (not charge-only)
```

### Issue 2: Permission Denied
**Symptoms:** `Permission denied: '/dev/ttyACM0'`

**Solutions:**
```bash
# Temporary fix
sudo chmod 666 /dev/ttyACM0

# Permanent fix
sudo usermod -a -G dialout pi
sudo reboot
```

### Issue 3: Port Busy
**Symptoms:** `Device or resource busy`

**Solutions:**
```bash
# Check what's using the port
sudo lsof /dev/ttyACM0

# Kill the process
sudo kill <PID>

# Or restart
sudo reboot
```

### Issue 4: Wrong Baud Rate
**Symptoms:** Garbage data or no data

**Solutions:**
- Verify Arduino code uses 9600 baud: `Serial.begin(9600);`
- Match baud rate in `integrated_server.py`: `SERIAL_BAUD = 9600`

### Issue 5: Arduino Not Sending Data
**Symptoms:** Port opens but no data received

**Solutions:**
```bash
# Upload Arduino code again
# Check Arduino Serial Monitor first
# Verify SCD41 sensor is connected
# Check I2C connections (SDA, SCL)
```

---

## Verification Steps

### 1. Arduino Side
```bash
# Open Arduino IDE Serial Monitor (9600 baud)
# You should see:
SENSOR,12345,1200,22.5,92.3,SPAWNING,0
SENSOR,17890,1205,22.6,92.1,SPAWNING,0
```

### 2. RPi Side
```bash
# Test with Python
python3 << EOF
import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

for i in range(10):
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        print(line)
    time.sleep(0.5)

ser.close()
EOF
```

### 3. Server Side
```bash
# Check server logs
sudo journalctl -u mash-device -f

# Should show:
# ✅ Serial connection established on /dev/ttyACM0
# 📊 CO2=1200ppm, T=22.5°C, H=92.3%
```

---

## Auto-Detection

The updated `integrated_server.py` now includes auto-detection:

1. Tries configured `SERIAL_PORT` first
2. If fails, scans for Arduino ports automatically
3. Tries detected port
4. Logs the correct port to use

**Example output:**
```
🔌 Attempting to connect to Arduino on /dev/ttyACM0...
⚠️  Failed to connect on /dev/ttyACM0: [Errno 2] No such file
🔍 Attempting to auto-detect Arduino port...
🔍 Found USB serial device: /dev/ttyUSB0 - USB Serial
🔌 Trying detected port: /dev/ttyUSB0...
✅ Serial connection established on /dev/ttyUSB0
💡 Update SERIAL_PORT in config to: /dev/ttyUSB0
```

---

## Still Not Working?

### Check Hardware:
- [ ] Arduino is powered (LED on)
- [ ] USB cable is data cable (not charge-only)
- [ ] USB cable is firmly connected
- [ ] SCD41 sensor is properly wired
- [ ] I2C connections are correct (SDA→A4, SCL→A5)

### Check Software:
- [ ] Arduino code is uploaded
- [ ] Arduino Serial Monitor shows data
- [ ] RPi can see USB device (`lsusb`)
- [ ] User has serial permissions
- [ ] No other program is using the port

### Get More Info:
```bash
# Full USB device info
lsusb -v | grep -A 10 Arduino

# Kernel messages
dmesg | tail -50

# Serial port details
udevadm info -a -n /dev/ttyACM0

# Check if port exists
ls -la /dev/tty* | grep -E 'ACM|USB'
```

---

## Quick Reference

| Port | Device | Notes |
|------|--------|-------|
| `/dev/ttyACM0` | Arduino Uno/Mega | Most common |
| `/dev/ttyUSB0` | CH340 chip | Clone Arduinos |
| `/dev/ttyAMA0` | RPi GPIO serial | Not for Arduino |
| `/dev/ttyS0` | Hardware UART | Not for Arduino |

---

**Need Help?**
Run the diagnostic tool first:
```bash
python3 check_serial.py
```

This will identify the issue and suggest fixes!
