# MASH IoT Device - Setup Instructions

## Current Directory Structure

```
mash@MASH-CHAMBER:~ $ pwd
/home/mash

mash@MASH-CHAMBER:~ $ ls
MASH-IoT-Device/
```

**Working Directory:** `/home/mash/MASH-IoT-Device`

---

## Installation Steps

### 1. Transfer Files from Windows to Raspberry Pi

**Option A: Using SCP (Command Line)**

From Windows PowerShell or Command Prompt:

```powershell
# Replace 192.168.1.50 with your Raspberry Pi's IP address
scp -r C:\Users\Ryzen\Desktop\ThesisDev\MASH-IoT-Device mash@192.168.1.50:/home/mash/
```

**Option B: Using WinSCP (GUI)**

1. Download and install [WinSCP](https://winscp.net/)
2. Connect to your Raspberry Pi:
   - Host: `192.168.1.50` (or your Pi's IP)
   - User: `mash`
   - Password: (your password)
3. Drag and drop the `MASH-IoT-Device` folder to `/home/mash/`

**Option C: Using FileZilla**

1. Download and install [FileZilla](https://filezilla-project.org/)
2. Connect using SFTP:
   - Host: `sftp://192.168.1.50`
   - Username: `mash`
   - Password: (your password)
3. Transfer the folder

### 2. SSH into Raspberry Pi

```bash
ssh mash@MASH-CHAMBER
# or
ssh mash@192.168.1.50
```

### 3. Navigate to Project Directory

```bash
cd ~/MASH-IoT-Device
```

### 4. Run Installation Script

```bash
chmod +x install.sh
./install.sh
```

The script will:
- Install system dependencies (NetworkManager, Python, GPIO libraries)
- Create Python virtual environment
- Install Python packages
- Set up systemd service
- Configure permissions

### 5. Create Environment File

```bash
cp .env.example .env
nano .env
```

Update these values:
```env
DEVICE_ID=MASH-A1-CAL25-XXXXXX
DEVICE_NAME=MASH Chamber #1
BACKEND_API_URL=https://mash-backend-api-production.up.railway.app/api
DEVICE_OWNER_USER_ID=your_user_uuid
```

### 6. Create Required Directories

```bash
mkdir -p ~/MASH-IoT-Device/logs
mkdir -p ~/MASH-IoT-Device/data
mkdir -p ~/MASH-IoT-Device/models
```

### 7. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable mash-device
sudo systemctl start mash-device
```

### 8. Check Service Status

```bash
sudo systemctl status mash-device
```

Expected output:
```
● mash-device.service - MASH IoT Device Service
   Loaded: loaded (/etc/systemd/system/mash-device.service; enabled)
   Active: active (running) since ...
```

### 9. View Logs

**Live logs:**
```bash
sudo journalctl -u mash-device -f
```

**Application logs:**
```bash
tail -f ~/MASH-IoT-Device/logs/service.log
```

**Error logs:**
```bash
tail -f ~/MASH-IoT-Device/logs/service-error.log
```

---

## Verification

### Check Hotspot Created

After boot, verify hotspot is active:

```bash
# List active connections
nmcli connection show --active

# Should see something like:
# mash-hotspot-XXXXXX  wifi  wlan0  ...
```

### Check API Server

```bash
# From the Pi
curl http://192.168.4.1:5000/api/v1/status

# Or from mobile connected to hotspot
curl http://192.168.4.1:5000/api/v1/provisioning/info
```

### Test GPIO Access

```bash
# Check user groups
groups mash
# Should include: gpio i2c spi dialout

# Test GPIO permissions
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); print('GPIO OK')"
```

---

## File Locations

```
/home/mash/MASH-IoT-Device/
├── main.py                          # Main application
├── install.sh                       # Installation script
├── .env                            # Configuration (create from .env.example)
├── requirements.txt                # Python dependencies
│
├── config/
│   ├── device_config.yaml          # Default config
│   └── mash-device.service         # Systemd service
│
├── src/
│   ├── actuators/                  # Actuator control
│   ├── api/                        # REST API server
│   ├── sensors/                    # Sensor management
│   ├── storage/                    # Local database
│   ├── utils/                      # Network & utilities
│   └── backend_client.py           # Backend communication
│
├── logs/                           # Auto-generated logs
│   ├── service.log
│   └── service-error.log
│
├── data/                           # Local database
│   └── mash_device.db
│
└── models/                         # AI models
    └── decision_model.json
```

---

## Common Commands

### Service Management

```bash
# Start service
sudo systemctl start mash-device

# Stop service
sudo systemctl stop mash-device

# Restart service
sudo systemctl restart mash-device

# Check status
sudo systemctl status mash-device

# Enable auto-start on boot
sudo systemctl enable mash-device

# Disable auto-start
sudo systemctl disable mash-device
```

### Network Management

```bash
# List WiFi networks
nmcli device wifi list

# Connect to WiFi manually
nmcli device wifi connect "SSID" password "password"

# Check current connection
nmcli connection show --active

# Restart hotspot manually
nmcli connection down mash-hotspot-XXXXXX
nmcli connection up mash-hotspot-XXXXXX
```

### Testing

```bash
# Test in mock mode (no GPIO required)
cd ~/MASH-IoT-Device
python3 main.py --mock

# Test with status only
python3 main.py --status

# Run with debug logging
python3 main.py --debug
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check for errors
sudo journalctl -u mash-device -n 50

# Check if Python virtual environment exists
ls -la ~/MASH-IoT-Device/venv/

# Reinstall if needed
cd ~/MASH-IoT-Device
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Hotspot Issues

```bash
# Check NetworkManager is running
sudo systemctl status NetworkManager

# Restart NetworkManager
sudo systemctl restart NetworkManager

# Check for conflicting services
sudo systemctl status dhcpcd
# If active, disable it:
sudo systemctl disable dhcpcd
sudo systemctl stop dhcpcd
```

### GPIO Errors

```bash
# Add user to gpio group (requires reboot)
sudo usermod -a -G gpio mash
sudo reboot

# Check GPIO permissions
ls -l /dev/gpiomem
# Should show: crw-rw---- 1 root gpio ...
```

### Arduino Not Detected

```bash
# List USB devices
ls -l /dev/ttyACM* /dev/ttyUSB*

# Check permissions
sudo usermod -a -G dialout mash

# Test serial connection
screen /dev/ttyACM0 9600
# Ctrl+A, K to exit
```

---

## Quick Test Sequence

```bash
# 1. Check service is running
sudo systemctl status mash-device

# 2. Check hotspot is active (if no WiFi configured)
nmcli connection show --active | grep hotspot

# 3. Test API from Pi
curl http://192.168.4.1:5000/api/v1/status | jq

# 4. Test from mobile (connect to hotspot first)
# From mobile browser: http://192.168.4.1:5000/api/v1/provisioning/info

# 5. Configure WiFi
curl -X POST http://192.168.4.1:5000/api/v1/wifi/config \
  -H "Content-Type: application/json" \
  -d '{"ssid":"YourWiFi","password":"YourPassword"}'

# 6. After WiFi connects, check device status
curl http://$(hostname -I | awk '{print $1}'):5000/api/v1/status | jq
```

---

## Production Checklist

- [ ] Service auto-starts on boot: `sudo systemctl is-enabled mash-device`
- [ ] Hotspot creates on boot when no WiFi
- [ ] WiFi configuration works from mobile app
- [ ] Device registers with backend after WiFi connects
- [ ] Sensor data is being collected (check logs)
- [ ] Actuators respond to API commands
- [ ] Logs are being written to `/home/mash/MASH-IoT-Device/logs/`
- [ ] All permissions are correct (gpio, i2c, spi groups)

---

## Support

For issues or questions:
- Check logs: `sudo journalctl -u mash-device -f`
- Review documentation: `DEPLOYMENT_GUIDE.md`
- Test in mock mode: `python3 main.py --mock`
