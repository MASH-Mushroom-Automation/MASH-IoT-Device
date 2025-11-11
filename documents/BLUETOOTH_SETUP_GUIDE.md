# Bluetooth Setup Guide for MASH IoT Device

## Overview

This guide explains how to set up and use Bluetooth connectivity on your MASH IoT Device (Raspberry Pi 3). Bluetooth provides an alternative connection method when WiFi hotspot is unavailable, enabling:

- **Internet Tethering**: Share internet connection from mobile device to RPi
- **Offline Mode**: Direct device control without internet
- **Fallback Connectivity**: Automatic switch when WiFi fails

## Prerequisites

### Hardware Requirements
- Raspberry Pi 3 (built-in Bluetooth)
- Mobile device with Bluetooth support

### Software Requirements
- Raspbian OS (Bullseye or later)
- BlueZ Bluetooth stack
- Python 3.7+

## Installation

### 1. Install Required Packages

```bash
cd /home/pi/MASH-IoT-Device

# Install Bluetooth utilities
sudo apt-get update
sudo apt-get install -y bluetooth bluez bluez-tools

# Install Python dependencies (if not already installed)
pip3 install -r requirements.txt
```

### 2. Configure Bluetooth Service

```bash
# Enable Bluetooth service
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Check Bluetooth status
sudo systemctl status bluetooth
```

### 3. Configure PAN (Personal Area Network)

For internet sharing, configure NAT and IP forwarding:

```bash
# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# Make it persistent
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
```

## Usage

### Starting Bluetooth Tethering

The Bluetooth manager is integrated into the main application. To start tethering:

#### Method 1: Via API

```bash
# Start tethering via API
curl -X POST http://localhost:5000/api/v1/bluetooth/tethering \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'

# Check status
curl http://localhost:5000/api/v1/bluetooth/status
```

#### Method 2: Via Python

```python
from src.utils.bluetooth_manager import BluetoothManager
from src.utils.bluetooth_tethering import BluetoothTethering

# Initialize
bt_manager = BluetoothManager(device_name="MASH-IoT-Device")
bt_tethering = BluetoothTethering(bt_manager)

# Start tethering
if bt_tethering.start_tethering():
    print("Bluetooth tethering started")
    print(f"Device discoverable as: {bt_manager.device_name}")
```

### Pairing Process

1. **On Raspberry Pi**: Device becomes discoverable automatically when tethering starts

2. **On Mobile Device**:
   - Open Bluetooth settings
   - Scan for devices
   - Look for "MASH-IoT-Device"
   - Pair with device
   - Accept pairing on RPi if prompted

3. **Connection**: Once paired, mobile app can connect automatically

### Stopping Bluetooth Tethering

```bash
# Via API
curl -X POST http://localhost:5000/api/v1/bluetooth/tethering \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'
```

## Configuration

### Changing Device Name

Edit your `.env` file or set environment variable:

```bash
# .env
BLUETOOTH_DEVICE_NAME=MyMASH-Device
```

Or in code:

```python
bt_manager = BluetoothManager(device_name="MyCustomName")
```

### Discoverable Timeout

By default, device stays discoverable for 180 seconds (3 minutes). To change:

```python
bt_manager.make_discoverable(timeout=300)  # 5 minutes
bt_manager.make_discoverable(timeout=0)    # Infinite (not recommended)
```

## API Endpoints

### GET /api/v1/bluetooth/status

Get current Bluetooth status.

**Response:**
```json
{
  "success": true,
  "data": {
    "enabled": true,
    "state": "discoverable",
    "discoverable": true,
    "connected_devices": 1,
    "device_name": "MASH-IoT-Device"
  },
  "timestamp": "2024-11-11T13:28:00Z"
}
```

### POST /api/v1/bluetooth/tethering

Start or stop Bluetooth tethering.

**Request:**
```json
{
  "action": "start"  // or "stop"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Bluetooth tethering started",
  "timestamp": "2024-11-11T13:28:00Z"
}
```

## Troubleshooting

### Bluetooth Not Starting

```bash
# Check if Bluetooth is blocked
rfkill list

# Unblock if necessary
sudo rfkill unblock bluetooth

# Restart Bluetooth service
sudo systemctl restart bluetooth
```

### Cannot Pair Device

```bash
# Remove old pairings
bluetoothctl
> devices
> remove AA:BB:CC:DD:EE:FF
> exit

# Restart Bluetooth
sudo systemctl restart bluetooth
```

### Internet Sharing Not Working

```bash
# Check iptables rules
sudo iptables -t nat -L -n -v

# Verify IP forwarding
cat /proc/sys/net/ipv4/ip_forward  # Should show 1

# Check network interfaces
ifconfig
# Should see bnep0 interface when connected
```

### Connection Drops

```bash
# Check Bluetooth logs
journalctl -u bluetooth -f

# Increase connection timeout in code
bt_manager.connect_device(address, timeout=30)
```

## Security Considerations

1. **Pairing Security**: Always use secure pairing with PIN/passkey
2. **Network Access**: Bluetooth tethering provides full network access
3. **Discoverable Time**: Limit discoverable duration to prevent unauthorized pairing
4. **Trust Only Known Devices**: Only pair with trusted mobile devices

## Advanced Configuration

### Auto-start Bluetooth on Boot

Add to main.py or create systemd service:

```python
# In main.py initialization
if config.get('bluetooth.auto_start', False):
    bt_tethering.start_tethering()
```

### Bluetooth + WiFi Hotspot

Both can run simultaneously:

```python
# Start WiFi hotspot
hotspot_manager.start()

# Also start Bluetooth
bt_tethering.start_tethering()
```

## Performance Notes

- **Range**: Bluetooth ~10 meters (30 feet)
- **Speed**: ~1-3 Mbps practical throughput
- **Latency**: ~100-200ms typical
- **Battery**: Minimal impact on RPi, moderate on mobile

## Support

For issues or questions:
1. Check logs: `/var/log/mash-iot-device.log`
2. Enable debug mode: Set `LOG_LEVEL=DEBUG` in `.env`
3. Consult system logs: `journalctl -u mash-iot-device -f`
