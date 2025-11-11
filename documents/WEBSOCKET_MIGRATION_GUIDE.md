# WebSocket Migration Guide for RPi3

## Overview

This guide explains how to migrate the RPi3 chamber controller from direct HTTP API to WebSocket connection.

---

## Why WebSocket?

### Problems with Current Setup:
1. **Hotspot Issues**: RPi3 hotspot prevents internet connection
2. **Network Isolation**: Mobile app can't access internet when connected to RPi3
3. **Manual Configuration**: User has to type IP address
4. **Limited Range**: Only works on same network

### WebSocket Benefits:
1. **No Hotspot Needed**: RPi3 connects to WiFi/Ethernet normally
2. **Internet Access**: Both RPi3 and mobile app have internet
3. **Auto-Discovery**: No IP address entry needed
4. **Remote Access**: Control from anywhere
5. **Real-Time**: Instant sensor updates and command execution

---

## Installation

### 1. Install Required Packages

```bash
pip install websockets asyncio python-dotenv
```

### 2. Update requirements.txt

```txt
websockets>=12.0
asyncio>=3.4.3
python-dotenv>=1.0.0
```

---

## Implementation

### 1. Create WebSocket Client (`websocket_client.py`)

```python
import asyncio
import websockets
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from sensor_reader import SensorReader
from actuator_controller import ActuatorController

load_dotenv()

class WebSocketClient:
    def __init__(self):
        self.ws_url = os.getenv('WS_SERVER_URL', 'ws://localhost:8080/ws/device')
        self.device_id = os.getenv('DEVICE_ID', 'chamber-001')
        self.device_token = os.getenv('DEVICE_TOKEN', 'your-device-token')
        
        self.websocket = None
        self.sensor_reader = SensorReader()
        self.actuator_controller = ActuatorController()
        self.is_connected = False
        
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            # Build connection URL with auth params
            url = f"{self.ws_url}?deviceId={self.device_id}&userId=device&token={self.device_token}"
            
            print(f"Connecting to {url}...")
            self.websocket = await websockets.connect(url)
            self.is_connected = True
            print("✅ Connected to WebSocket server")
            
            # Send initial status
            await self.send_device_status()
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.is_connected = False
            return False
    
    async def send_device_status(self):
        """Send current device status"""
        status = {
            'type': 'deviceStatus',
            'data': {
                'deviceId': self.device_id,
                'status': 'online',
                'mode': self.actuator_controller.get_mode(),
                'actuators': self.actuator_controller.get_all_states(),
                'timestamp': datetime.now().isoformat()
            }
        }
        await self.send_message(status)
    
    async def send_sensor_data(self):
        """Send sensor readings"""
        readings = self.sensor_reader.read_all()
        
        message = {
            'type': 'sensorData',
            'data': {
                'deviceId': self.device_id,
                'temperature': readings['temperature'],
                'humidity': readings['humidity'],
                'co2': readings['co2'],
                'timestamp': datetime.now().isoformat()
            }
        }
        await self.send_message(message)
    
    async def send_message(self, message):
        """Send message to server"""
        if self.websocket and self.is_connected:
            try:
                await self.websocket.send(json.dumps(message))
            except Exception as e:
                print(f"Failed to send message: {e}")
                self.is_connected = False
    
    async def handle_command(self, command, params):
        """Handle incoming command"""
        print(f"Received command: {command}")
        
        if command == 'setActuator':
            actuator = params.get('actuator')
            state = params.get('state')
            self.actuator_controller.set_actuator(actuator, state)
            
        elif command == 'setMode':
            mode = params.get('mode')
            self.actuator_controller.set_mode(mode)
            
        elif command == 'getStatus':
            await self.send_device_status()
            
        elif command == 'getSensorData':
            await self.send_sensor_data()
        
        # Send updated status after command
        await self.send_device_status()
    
    async def listen(self):
        """Listen for incoming messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'command':
                    command = data.get('command')
                    params = data.get('params', {})
                    await self.handle_command(command, params)
                
                elif msg_type == 'ping':
                    # Respond to heartbeat
                    await self.send_message({'type': 'pong'})
                    
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
            self.is_connected = False
        except Exception as e:
            print(f"Error in listen loop: {e}")
            self.is_connected = False
    
    async def sensor_loop(self):
        """Periodically send sensor data"""
        while self.is_connected:
            try:
                await self.send_sensor_data()
                await asyncio.sleep(5)  # Send every 5 seconds
            except Exception as e:
                print(f"Error in sensor loop: {e}")
                break
    
    async def run(self):
        """Main run loop with auto-reconnect"""
        while True:
            try:
                # Connect
                if not await self.connect():
                    print("Retrying in 5 seconds...")
                    await asyncio.sleep(5)
                    continue
                
                # Start tasks
                listen_task = asyncio.create_task(self.listen())
                sensor_task = asyncio.create_task(self.sensor_loop())
                
                # Wait for tasks
                await asyncio.gather(listen_task, sensor_task)
                
            except Exception as e:
                print(f"Error in main loop: {e}")
            
            finally:
                # Cleanup
                if self.websocket:
                    await self.websocket.close()
                self.is_connected = False
                
                # Wait before reconnecting
                print("Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

# Main entry point
if __name__ == "__main__":
    client = WebSocketClient()
    asyncio.run(client.run())
```

### 2. Create Environment File (`.env`)

```env
# WebSocket Server Configuration
WS_SERVER_URL=ws://your-backend.com/ws/device
# For local testing: ws://localhost:8080/ws/device

# Device Configuration
DEVICE_ID=chamber-001
DEVICE_TOKEN=your-device-token-here

# Optional: Device Info
DEVICE_NAME=Chamber 1
DEVICE_LOCATION=Lab A
```

### 3. Update Main Script

```python
# main.py
import asyncio
from websocket_client import WebSocketClient

def main():
    print("Starting MASH IoT Device with WebSocket...")
    client = WebSocketClient()
    
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()
```

---

## Testing

### 1. Local Testing (Without Backend)

Use a simple WebSocket echo server for testing:

```bash
pip install websockets
```

```python
# test_server.py
import asyncio
import websockets

async def echo(websocket):
    async for message in websocket:
        print(f"Received: {message}")
        await websocket.send(message)

async def main():
    async with websockets.serve(echo, "localhost", 8080):
        print("WebSocket server running on ws://localhost:8080")
        await asyncio.Future()

asyncio.run(main())
```

Run test server:
```bash
python test_server.py
```

### 2. Test RPi3 Client

```bash
python websocket_client.py
```

Expected output:
```
Starting MASH IoT Device with WebSocket...
Connecting to ws://localhost:8080/ws/device...
✅ Connected to WebSocket server
Received command: getStatus
```

---

## Deployment

### 1. Network Setup

**Option A: WiFi Connection (Recommended)**
```bash
sudo raspi-config
# Select: Network Options → Wi-Fi
# Enter SSID and password
```

**Option B: Ethernet Connection**
- Simply plug in Ethernet cable
- No configuration needed

### 2. Auto-Start on Boot

Create systemd service:

```bash
sudo nano /etc/systemd/system/mash-device.service
```

```ini
[Unit]
Description=MASH IoT Device WebSocket Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/MASH-IoT-Device
ExecStart=/usr/bin/python3 /home/pi/MASH-IoT-Device/websocket_client.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mash-device.service
sudo systemctl start mash-device.service
sudo systemctl status mash-device.service
```

### 3. Monitoring

View logs:
```bash
sudo journalctl -u mash-device.service -f
```

---

## Migration Checklist

- [ ] Install websockets package
- [ ] Create `.env` file with configuration
- [ ] Implement `websocket_client.py`
- [ ] Test with local WebSocket server
- [ ] Connect RPi3 to WiFi/Ethernet
- [ ] Update backend URL in `.env`
- [ ] Test connection to production backend
- [ ] Set up systemd service for auto-start
- [ ] Test reconnection after network interruption
- [ ] Update mobile app to use WebSocket connection screen
- [ ] Remove old direct IP connection code

---

## Troubleshooting

### Connection Fails

**Check network:**
```bash
ping google.com
```

**Check WebSocket server:**
```bash
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" http://your-backend.com/ws/device
```

### Auto-Reconnect Not Working

Check systemd service:
```bash
sudo systemctl status mash-device.service
```

Restart service:
```bash
sudo systemctl restart mash-device.service
```

### Sensor Data Not Updating

Check sensor connections:
```bash
python -c "from sensor_reader import SensorReader; print(SensorReader().read_all())"
```

---

## Next Steps

1. **Deploy Backend**: Set up WebSocket server (see `WEBSOCKET_ARCHITECTURE.md`)
2. **Test Connection**: Verify RPi3 can connect to backend
3. **Update Mobile App**: Use new WebSocket connection screen
4. **Field Testing**: Test in real environment
5. **Documentation**: Update thesis with new architecture

---

## Summary

WebSocket provides a **robust, scalable, and user-friendly** solution that eliminates the hotspot requirement and enables remote access. The RPi3 simply connects to the internet like any other device, and the mobile app can control it from anywhere.
