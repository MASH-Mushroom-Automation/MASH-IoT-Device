# MASH IoT Device - Quick Start Guide

## 🚀 Quick Deployment (For Presentation)

### Prerequisites
- Raspberry Pi 3 Model B with Raspberry Pi OS Lite
- Arduino Uno connected via USB with sensor code uploaded
- 4-Channel Relay Module connected to GPIO
- Internet-capable WiFi router nearby

---

## ⚡ Fast Installation (5 Minutes)

### 1. Flash & Setup Pi
```bash
# SSH into your Pi
ssh pi@raspberrypi.local

# Clone repository
cd /home/pi
git clone <your-repo-url> mash-iot
cd mash-iot

# Run installation
chmod +x install.sh
./install.sh

# Reboot
sudo reboot
```

### 2. First Boot Behavior

After reboot, the device will automatically:
1. ✅ Start the MASH service
2. ❌ Detect no WiFi connection
3. 📡 **Create hotspot:** `MASH-Chamber-XXXXXX`
4. 🌐 **Listen on:** `192.168.4.1:5000`

Check logs:
```bash
sudo journalctl -u mash-device -f
```

Expected output:
```
[INFO] MASH IoT Device starting...
[INFO] ⚠️  Device not connected to WiFi
[INFO] 🔄 Starting provisioning mode (hotspot)
[INFO] ✓ Provisioning hotspot active
[INFO] 📱 Connect to WiFi: MASH-Chamber-D5A91F
[INFO] 🌐 Access setup at: http://192.168.4.1:5000
```

---

## 📱 Mobile App Setup (Presentation Demo)

### Step 1: Connect to Device Hotspot

**From Mobile App:**
1. Go to WiFi settings
2. Connect to: `MASH-Chamber-XXXXXX`
3. Open MASH Grower Mobile app
4. Navigate to **"Add Device"** screen

### Step 2: Scan for Device

The app should discover the device via mDNS or direct IP:
- **Device ID:** `MASH-Chamber-XXXXXX`
- **Status:** Provisioning Mode
- **IP:** `192.168.4.1`

### Step 3: Configure WiFi

**API Call (what the app does):**
```http
POST http://192.168.4.1:5000/api/v1/wifi/config
{
  "ssid": "YourRouterName",
  "password": "YourWiFiPassword"
}
```

**What happens:**
1. 🔄 Device stops hotspot
2. 🌐 Connects to your WiFi router
3. ✅ Registers with backend
4. 🎉 Ready for normal operation!

### Step 4: Control Device

**From the same network (local):**
```http
POST http://{device-local-ip}:5000/api/v1/commands/actuator_control
{
  "action": "set",
  "led_lights": true
}
```

**From anywhere (cloud via backend):**
```
Mobile App → Backend API → Device
```

---

## 🔧 Testing Without Mobile App (CLI Testing)

### Connect to Hotspot
```bash
# From laptop/phone, connect to MASH-Chamber-XXXXXX
```

### Test WiFi Scan
```bash
curl http://192.168.4.1:5000/api/v1/wifi/scan
```

### Configure WiFi
```bash
curl -X POST http://192.168.4.1:5000/api/v1/wifi/config \
  -H "Content-Type: application/json" \
  -d '{"ssid":"YourWiFi","password":"YourPassword"}'
```

### Check Device Status
```bash
# After device connects to WiFi, get its new IP from router
curl http://192.168.1.XXX:5000/api/v1/status
```

### Control Actuators
```bash
# Turn on LED lights
curl -X POST http://192.168.1.XXX:5000/api/v1/commands/actuator_control \
  -H "Content-Type: application/json" \
  -d '{"action":"set","led_lights":true}'

# Turn off all
curl -X POST http://192.168.1.XXX:5000/api/v1/commands/actuator_control \
  -H "Content-Type: application/json" \
  -d '{"action":"all_off"}'

# Get current state
curl -X POST http://192.168.1.XXX:5000/api/v1/commands/actuator_control \
  -H "Content-Type: application/json" \
  -d '{"action":"get_state"}'
```

---

## 🎯 Presentation Demo Flow

### Scenario 1: Initial Setup (Bare Minimum)

**Goal:** Show device provisioning and WiFi connection

1. **Power on Pi** → Show logs starting
2. **Hotspot appears** → Show on phone WiFi list
3. **Connect from phone** → Show connection
4. **Send WiFi config** → Show API call (curl or Postman)
5. **Device connects** → Show success logs
6. **Show device status** → Confirm online

**Time:** ~3 minutes

### Scenario 2: Actuator Control (Main Feature)

**Goal:** Show real-time device control

1. **Get current state** → Show all actuators OFF
2. **Turn on LED lights** → Physical lights turn on
3. **Turn on fans** → Physical fans start
4. **Turn on humidifier** → Humidifier activates
5. **Turn all off** → Everything stops

**Time:** ~2 minutes

### Scenario 3: Cloud Control (If Internet Available)

**Goal:** Show control from different network

1. **Device on WiFi A** (home router)
2. **Phone on WiFi B or 4G**
3. **Send command via backend**
4. **Device receives and executes**
5. **Show status update in mobile app**

**Time:** ~2 minutes

---

## 🐛 Troubleshooting Quick Fixes

### Hotspot Not Starting
```bash
# Check NetworkManager
sudo systemctl status NetworkManager

# Restart service
sudo systemctl restart mash-device

# Check logs
sudo journalctl -u mash-device -n 50
```

### WiFi Connection Failed
```bash
# Check available networks
nmcli device wifi list

# Test connection manually
nmcli device wifi connect "YourSSID" password "YourPassword"

# Restart hotspot if needed
# The system does this automatically!
```

### Actuators Not Working
```bash
# Check GPIO permissions
groups pi  # Should show 'gpio'

# Test GPIO manually
python3 << EOF
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.HIGH)
import time
time.sleep(2)
GPIO.output(27, GPIO.LOW)
GPIO.cleanup()
EOF
```

### Service Not Starting
```bash
# Check service status
sudo systemctl status mash-device

# Check for errors
sudo journalctl -u mash-device -n 100

# Restart service
sudo systemctl restart mash-device
```

---

## 📊 System Status Commands

```bash
# Service status
sudo systemctl status mash-device

# Live logs
sudo journalctl -u mash-device -f

# Last 100 lines
sudo journalctl -u mash-device -n 100

# Check network
nmcli connection show

# Check active hotspot
nmcli connection show --active | grep mash

# Check device IP
hostname -I

# Check GPIO
gpio readall
```

---

## 🔑 Key Files & Locations

```
/home/pi/mash-iot/
├── main.py                    # Main application
├── .env                       # Configuration (EDIT THIS!)
├── config/
│   └── mash-device.service   # Systemd service
├── logs/
│   ├── service.log           # Application logs
│   └── service-error.log     # Error logs
├── data/
│   └── mash_device.db        # Local database
└── src/
    ├── actuators/            # Actuator control
    ├── backend_client.py     # Backend API client
    └── utils/
        ├── hotspot_manager.py    # Hotspot management
        └── network_manager.py    # WiFi management
```

---

## ✅ Pre-Presentation Checklist

- [ ] Raspberry Pi has power and boots up
- [ ] Arduino is connected and running sensor code
- [ ] Relay module is connected to GPIO pins
- [ ] Actuators (fans, lights, humidifier) have power
- [ ] Service auto-starts on boot (`systemctl is-enabled mash-device`)
- [ ] Hotspot appears within 30 seconds of boot
- [ ] Can connect to hotspot from mobile
- [ ] WiFi router credentials are correct
- [ ] Backend API is accessible (test with curl)
- [ ] Mobile app has latest code deployed
- [ ] Test all actuators manually once

---

## 🎬 Presentation Script

**Opening (30 seconds):**
> "This is the MASH IoT Device - a Raspberry Pi-based mushroom cultivation system that monitors environment and controls actuators. Let me show you how easy it is to set up."

**Setup Demo (3 minutes):**
> "When powered on, the device creates a WiFi hotspot since it's not configured. From the mobile app, I connect to this hotspot, scan for available WiFi networks, select my router, enter the password, and... done! The device is now connected to the internet and registered with our backend."

**Control Demo (2 minutes):**
> "Now I can control the device. Let me turn on the LED grow lights... [lights turn on]. The exhaust fan... [fan starts]. I can do this from the mobile app on the same network, or from anywhere in the world via the cloud backend."

**Closing (30 seconds):**
> "The device continuously monitors CO2, temperature, and humidity from the Arduino sensor, and can automatically control actuators based on AI predictions. All data is synced to the cloud for remote monitoring and historical analysis."

---

## 📞 Support & Resources

- **Full Documentation:** See `DEPLOYMENT_GUIDE.md`
- **API Reference:** See `API_ENDPOINTS.md`
- **Troubleshooting:** See `DEPLOYMENT_GUIDE.md#troubleshooting`
- **Backend Schema:** See `documents/SCHEMA_REFERENCE.md`

---

**Ready to demo! 🎉**
