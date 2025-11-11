# WiFi Configuration Methods for RPi3

## Problem
How do we configure the RPi3's WiFi credentials without using hotspot mode?

---

## Solution Options

### Option 1: Initial Setup via Ethernet (Recommended for Thesis)

**Setup Process**:
1. Connect RPi3 to router via **Ethernet cable** (one-time setup)
2. RPi3 gets IP from router via DHCP
3. Mobile app discovers RPi3 on local network (mDNS)
4. Mobile app sends WiFi credentials to RPi3
5. RPi3 saves credentials and switches to WiFi
6. Disconnect Ethernet cable - RPi3 now uses WiFi

**Advantages**:
- Simple and reliable
- No hotspot needed
- Works for initial setup
- Professional approach

**Implementation**:
```python
# On RPi3: wifi_config_server.py
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/configure-wifi', methods=['POST'])
def configure_wifi():
    data = request.json
    ssid = data.get('ssid')
    password = data.get('password')
    
    # Write to wpa_supplicant
    config = f"""
network={{
    ssid="{ssid}"
    psk="{password}"
    key_mgmt=WPA-PSK
}}
"""
    
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as f:
        f.write(config)
    
    # Restart networking
    subprocess.run(['sudo', 'systemctl', 'restart', 'networking'])
    
    return jsonify({'success': True, 'message': 'WiFi configured'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

### Option 2: Bluetooth Configuration (Most User-Friendly)

**Setup Process**:
1. Mobile app scans for Bluetooth devices
2. User selects RPi3 from list
3. Mobile app sends WiFi credentials via Bluetooth
4. RPi3 configures WiFi and connects
5. Done!

**Advantages**:
- No cables needed
- Very user-friendly
- Works like smart home devices
- No network required for setup

**Implementation**:
```python
# On RPi3: bluetooth_wifi_config.py
import bluetooth
import subprocess

def configure_wifi_via_bluetooth():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)
    
    port = server_sock.getsockname()[1]
    
    bluetooth.advertise_service(
        server_sock,
        "MASH-Chamber-Setup",
        service_id="00001101-0000-1000-8000-00805F9B34FB",
        service_classes=["00001101-0000-1000-8000-00805F9B34FB"],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )
    
    print("Waiting for Bluetooth connection...")
    client_sock, client_info = server_sock.accept()
    print(f"Connected to {client_info}")
    
    try:
        data = client_sock.recv(1024).decode('utf-8')
        ssid, password = data.split('|')
        
        # Configure WiFi
        config_wifi(ssid, password)
        
        client_sock.send("SUCCESS".encode('utf-8'))
    finally:
        client_sock.close()
        server_sock.close()
```

**Flutter Implementation**:
```dart
// Add to pubspec.yaml: flutter_bluetooth_serial: ^0.4.0

Future<void> configureWiFiViaBluetooth(String ssid, String password) async {
  // Scan for devices
  List<BluetoothDevice> devices = await FlutterBluetoothSerial.instance.getBondedDevices();
  
  // Find MASH device
  BluetoothDevice? mashDevice = devices.firstWhere(
    (device) => device.name?.contains('MASH-Chamber') ?? false,
  );
  
  // Connect
  BluetoothConnection connection = await BluetoothConnection.toAddress(mashDevice.address);
  
  // Send credentials
  connection.output.add(utf8.encode('$ssid|$password'));
  await connection.output.allSent;
  
  // Wait for response
  connection.input?.listen((data) {
    String response = utf8.decode(data);
    if (response == 'SUCCESS') {
      print('WiFi configured successfully!');
    }
  });
}
```

---

### Option 3: SD Card Pre-Configuration (Simplest)

**Setup Process**:
1. Before first boot, edit `wpa_supplicant.conf` on SD card
2. Insert SD card into RPi3
3. Boot RPi3 - automatically connects to WiFi
4. Done!

**Advantages**:
- No app needed for initial setup
- Very simple
- Works for controlled environments (lab/farm)

**Implementation**:
Create `wpa_supplicant.conf` on SD card boot partition:
```conf
country=PH
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YourWiFiName"
    psk="YourWiFiPassword"
    key_mgmt=WPA-PSK
}
```

---

### Option 4: Web-Based Configuration Portal (Fallback Mode)

**Setup Process**:
1. If RPi3 can't connect to saved WiFi, it creates a temporary hotspot
2. User connects to hotspot temporarily
3. Opens browser to `http://192.168.4.1`
4. Enters WiFi credentials via web form
5. RPi3 saves credentials and reboots
6. RPi3 connects to configured WiFi

**Advantages**:
- Works as fallback
- No app needed for reconfiguration
- Industry standard (used by many IoT devices)

---

## Recommended Approach for Your Thesis

### Phase 1: Initial Setup (Choose One)
**Option A**: Ethernet cable + mobile app configuration  
**Option B**: Bluetooth configuration  
**Option C**: SD card pre-configuration  

### Phase 2: Normal Operation
- RPi3 uses saved WiFi credentials
- Connects to internet automatically on boot
- WebSocket connection to backend

### Phase 3: Reconfiguration (If Needed)
- Web-based portal as fallback
- Or Bluetooth reconfiguration

---

## My Recommendation

For your thesis, I recommend:

**Initial Setup**: **Bluetooth Configuration** (Option 2)
- Most user-friendly
- Professional
- No cables needed
- Works like commercial IoT devices

**Fallback**: **Web Portal** (Option 4)
- If WiFi fails, temporary hotspot
- User can reconfigure via browser

This gives you the best of both worlds!
