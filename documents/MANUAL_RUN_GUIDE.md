# Manual Run Guide - MASH IoT Device

## Running the Device Manually (Without Service)

This guide shows how to run the IoT device manually for testing and development.

---

## Prerequisites

1. **SSH into Raspberry Pi**
   ```bash
   ssh mash@MASH-CHAMBER
   # or
   ssh mash@192.168.1.50
   ```

2. **Navigate to Project Directory**
   ```bash
   cd ~/MASH-IoT-Device
   ```

3. **Ensure Dependencies are Installed**
   ```bash
   # Check if virtual environment exists
   ls -la venv/
   
   # If not, run installation
   chmod +x install.sh
   ./install.sh
   ```

---

## Method 1: Run with Python Directly

### Basic Run (Production Mode)

```bash
cd ~/MASH-IoT-Device
python3 main.py
```

### Run in Mock Mode (No Hardware Required)

```bash
python3 main.py --mock
```

**Mock mode simulates:**
- Sensor readings (random CO2, temperature, humidity)
- GPIO actuators (logs instead of actual GPIO)
- Network operations (no actual hotspot/WiFi changes)

### Run with Debug Logging

```bash
python3 main.py --debug
```

### Run in Mock + Debug Mode

```bash
python3 main.py --mock --debug
```

---

## Method 2: Run with Virtual Environment

### Activate Virtual Environment

```bash
cd ~/MASH-IoT-Device
source venv/bin/activate
```

### Run Application

```bash
python main.py
# or
python main.py --mock --debug
```

### Deactivate When Done

```bash
deactivate
```

---

## Method 3: Run in Background (Manual)

### Start in Background

```bash
cd ~/MASH-IoT-Device
nohup python3 main.py > logs/manual-run.log 2>&1 &
```

### Check if Running

```bash
ps aux | grep main.py
```

### View Logs

```bash
tail -f logs/manual-run.log
```

### Stop Background Process

```bash
# Find process ID
ps aux | grep main.py

# Kill process (replace PID with actual process ID)
kill <PID>

# Or force kill
kill -9 <PID>
```

---

## Configuration for Manual Run

### 1. Create .env File (If Not Exists)

```bash
cd ~/MASH-IoT-Device
cp .env.example .env
nano .env
```

### 2. Update Configuration

```env
# Device Configuration
DEVICE_ID=MASH-A1-CAL25-XXXXXX
DEVICE_NAME=MASH Chamber #1
DEVICE_TYPE=MUSHROOM_CHAMBER

# Backend Configuration
BACKEND_API_URL=https://mash-backend-api-production.up.railway.app/api
BACKEND_API_KEY=
DEVICE_OWNER_USER_ID=

# Network Configuration
WIFI_INTERFACE=wlan0
HOTSPOT_SSID_PREFIX=MASH-Chamber
HOTSPOT_PASSWORD=

# Sensor Configuration
SENSORS_SOURCE=arduino_bridge
SENSORS_SERIAL_PORT=/dev/ttyACM0
SENSORS_SERIAL_BAUD=9600
SENSORS_READ_INTERVAL=60

# Development/Testing
MOCK_MODE=false
DEBUG_MODE=false
```

**For testing without hardware:**
```env
MOCK_MODE=true
DEBUG_MODE=true
```

---

## Testing Scenarios

### Scenario 1: Test Hotspot Creation

```bash
# Run in debug mode
python3 main.py --debug

# Expected output:
# [INFO] MASH IoT Device starting...
# [INFO] [WARN] Device not connected to WiFi
# [INFO] Starting provisioning mode (hotspot)
# [INFO] Hotspot started successfully: MASH-Chamber-XXXXXX
# [INFO] Connect to this network from mobile app
# [INFO] Access provisioning at http://192.168.4.1:5000
```

### Scenario 2: Test WiFi Configuration

```bash
# 1. Start device (creates hotspot)
python3 main.py --debug

# 2. From another terminal or mobile, configure WiFi
curl -X POST http://192.168.4.1:5000/api/v1/wifi/config \
  -H "Content-Type: application/json" \
  -d '{"ssid":"YourWiFi","password":"YourPassword"}'

# 3. Watch logs for connection attempt
```

### Scenario 3: Test Actuator Control

```bash
# 1. Start device
python3 main.py --mock --debug

# 2. Test actuator commands
curl -X POST http://localhost:5000/api/v1/commands/actuator_control \
  -H "Content-Type: application/json" \
  -d '{"action":"set","led_lights":true}'

# 3. Check logs for actuator state changes
```

### Scenario 4: Test Backend Registration

```bash
# 1. Ensure device is connected to WiFi
# 2. Set DEVICE_OWNER_USER_ID in .env
# 3. Run device
python3 main.py --debug

# Expected output:
# [INFO] Device connected to WiFi
# [INFO] Attempting to register with backend...
# [INFO] Device registered with backend
```

---

## Monitoring and Debugging

### View Live Logs

```bash
# If running in foreground, logs appear in terminal

# If running in background
tail -f logs/manual-run.log

# Or service logs if service is running
sudo journalctl -u mash-device -f
```

### Check Device Status

```bash
# While device is running
curl http://localhost:5000/api/v1/status | jq

# Or if on hotspot
curl http://192.168.4.1:5000/api/v1/status | jq
```

### Check Network Status

```bash
# Check WiFi connection
nmcli connection show --active

# Check hotspot status
nmcli connection show | grep hotspot

# Check device IP
hostname -I
```

### Check GPIO Status (If Using Real Hardware)

```bash
# Check GPIO pins
gpio readall

# Check user groups
groups mash
# Should include: gpio i2c spi dialout
```

### Check Serial Connection (Arduino)

```bash
# List USB devices
ls -l /dev/ttyACM* /dev/ttyUSB*

# Test serial connection
screen /dev/ttyACM0 9600
# Press Ctrl+A, K to exit
```

---

## Common Issues and Solutions

### Issue: Permission Denied (GPIO)

```bash
# Add user to gpio group
sudo usermod -a -G gpio mash

# Reboot required
sudo reboot
```

### Issue: Port 5000 Already in Use

```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill the process
kill <PID>

# Or change port in code (main.py)
```

### Issue: Hotspot Won't Start

```bash
# Check NetworkManager
sudo systemctl status NetworkManager

# Restart NetworkManager
sudo systemctl restart NetworkManager

# Check for conflicts
sudo systemctl status dhcpcd
# If active, disable it
sudo systemctl disable dhcpcd
sudo systemctl stop dhcpcd
```

### Issue: Arduino Not Detected

```bash
# Check USB connection
lsusb

# Check serial devices
ls -l /dev/ttyACM*

# Add user to dialout group
sudo usermod -a -G dialout mash

# Reboot
sudo reboot
```

### Issue: Backend Connection Failed

```bash
# Test backend connectivity
curl https://mash-backend-api-production.up.railway.app/api/health

# Check .env configuration
cat .env | grep BACKEND

# Run with debug to see detailed errors
python3 main.py --debug
```

---

## Stopping the Device

### If Running in Foreground

Press `Ctrl+C` in the terminal

### If Running in Background

```bash
# Find process
ps aux | grep main.py

# Kill process
kill <PID>

# Or use pkill
pkill -f main.py
```

### If Running as Service

```bash
sudo systemctl stop mash-device
```

---

## Quick Command Reference

| Task | Command |
|------|---------|
| Run normally | `python3 main.py` |
| Run in mock mode | `python3 main.py --mock` |
| Run with debug | `python3 main.py --debug` |
| Run mock + debug | `python3 main.py --mock --debug` |
| Run in background | `nohup python3 main.py > logs/manual-run.log 2>&1 &` |
| View logs | `tail -f logs/manual-run.log` |
| Check status | `curl http://localhost:5000/api/v1/status` |
| Stop background | `pkill -f main.py` |
| Check process | `ps aux \| grep main.py` |

---

## Development Workflow

### 1. Edit Code on Windows

Make changes to files in:
```
C:\Users\Ryzen\Desktop\ThesisDev\MASH-IoT-Device\
```

### 2. Transfer to Raspberry Pi

```powershell
# From Windows
scp -r C:\Users\Ryzen\Desktop\ThesisDev\MASH-IoT-Device mash@192.168.1.50:/home/mash/
```

### 3. Test on Raspberry Pi

```bash
# SSH into Pi
ssh mash@MASH-CHAMBER

# Navigate to directory
cd ~/MASH-IoT-Device

# Test in mock mode first
python3 main.py --mock --debug

# If OK, test with real hardware
python3 main.py --debug
```

### 4. Check Logs and Fix Issues

```bash
# View logs
tail -f logs/manual-run.log

# Or if errors occur
cat logs/service-error.log
```

### 5. Deploy as Service (When Ready)

```bash
# Copy service file
sudo cp config/mash-device.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable mash-device
sudo systemctl start mash-device

# Check status
sudo systemctl status mash-device
```

---

## Testing Checklist

Before running manually, ensure:

- [ ] SSH access to Raspberry Pi working
- [ ] Project files transferred to `/home/mash/MASH-IoT-Device`
- [ ] `.env` file created and configured
- [ ] Dependencies installed (`install.sh` run)
- [ ] User in correct groups (`gpio`, `i2c`, `spi`, `dialout`)
- [ ] Arduino connected (if using real sensors)
- [ ] Relay module connected (if using real actuators)

For mock mode testing:
- [ ] `MOCK_MODE=true` in `.env` or use `--mock` flag
- [ ] No hardware required

For production testing:
- [ ] All hardware connected and powered
- [ ] WiFi router available for testing
- [ ] Backend API accessible

---

## Next Steps

After successful manual testing:

1. **Deploy as Service**
   ```bash
   sudo systemctl enable mash-device
   sudo systemctl start mash-device
   ```

2. **Configure Auto-Start**
   - Service will start automatically on boot
   - Logs will be in `/home/mash/MASH-IoT-Device/logs/`

3. **Monitor in Production**
   ```bash
   sudo journalctl -u mash-device -f
   ```

4. **Update When Needed**
   - Transfer new files via SCP
   - Restart service: `sudo systemctl restart mash-device`
