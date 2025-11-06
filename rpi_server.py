#!/usr/bin/env python3
"""
MASH IoT Device HTTP Server for Raspberry Pi 3
Communicates with Arduino Uno R3 via Serial
Exposes REST API for mobile app control
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import serial
import time
import json
import threading
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app

# Serial connection to Arduino Uno R3
SERIAL_PORT = '/dev/ttyACM0'  # Adjust if needed
BAUD_RATE = 9600
ser = None

# Device configuration
DEVICE_ID = 'MASH-A1-CAL25-AC2415'
DEVICE_NAME = 'Mushroom Prototype Chamber'

# Current sensor data
sensor_data = {
    'temperature': 0.0,
    'humidity': 0.0,
    'co2': 0.0,
    'mode': 's',  # 's' = Spawning, 'f' = Fruiting
    'actuators': {
        'humidifier': False,
        'exhaust_fan': False,
        'blower_fan': False,
    },
    'timestamp': datetime.now().isoformat()
}

# Lock for thread-safe access to sensor_data
data_lock = threading.Lock()


def init_serial():
    """Initialize serial connection to Arduino"""
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        print(f"✅ Serial connection established on {SERIAL_PORT}")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Arduino: {e}")
        return False


def read_sensor_data():
    """Continuously read sensor data from Arduino"""
    global sensor_data
    
    while True:
        try:
            if ser and ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                
                # Parse sensor data from Arduino
                # Expected format: "T:25.5,H:85.2,C:1200"
                if line.startswith('T:'):
                    parts = line.split(',')
                    
                    with data_lock:
                        for part in parts:
                            if ':' in part:
                                key, value = part.split(':')
                                if key == 'T':
                                    sensor_data['temperature'] = float(value)
                                elif key == 'H':
                                    sensor_data['humidity'] = float(value)
                                elif key == 'C':
                                    sensor_data['co2'] = float(value)
                        
                        sensor_data['timestamp'] = datetime.now().isoformat()
                    
                    print(f"📊 Sensor data: T={sensor_data['temperature']}°C, "
                          f"H={sensor_data['humidity']}%, CO2={sensor_data['co2']}ppm")
                
        except Exception as e:
            print(f"❌ Error reading sensor data: {e}")
        
        time.sleep(1)


def send_command_to_arduino(command):
    """Send command to Arduino via serial"""
    try:
        if ser:
            ser.write(f"{command}\n".encode('utf-8'))
            print(f"📤 Sent command to Arduino: {command}")
            return True
        return False
    except Exception as e:
        print(f"❌ Failed to send command: {e}")
        return False


# ========== API Endpoints ==========

@app.route('/status', methods=['GET'])
def get_status():
    """Get device status"""
    return jsonify({
        'deviceId': DEVICE_ID,
        'deviceName': DEVICE_NAME,
        'status': 'online',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/data', methods=['GET'])
def get_data():
    """Get current sensor data"""
    with data_lock:
        return jsonify(sensor_data)


@app.route('/mode', methods=['POST'])
def set_mode():
    """Set device mode (Spawning or Fruiting)"""
    try:
        data = request.get_json()
        mode = data.get('mode', '').lower()
        
        if mode not in ['s', 'f']:
            return jsonify({'error': 'Invalid mode. Use "s" or "f"'}), 400
        
        # Send mode command to Arduino
        if send_command_to_arduino(mode):
            with data_lock:
                sensor_data['mode'] = mode
            
            mode_name = 'Spawning' if mode == 's' else 'Fruiting'
            print(f"✅ Mode set to {mode_name}")
            
            return jsonify({
                'success': True,
                'mode': mode,
                'modeName': mode_name
            })
        
        return jsonify({'error': 'Failed to send command to Arduino'}), 500
        
    except Exception as e:
        print(f"❌ Error setting mode: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/actuator', methods=['POST'])
def control_actuator():
    """Control actuator (relay)"""
    try:
        data = request.get_json()
        actuator = data.get('actuator', '')
        state = data.get('state', False)
        
        # Map actuator names to relay numbers
        actuator_map = {
            'humidifier': '1',
            'exhaust_fan': '2',
            'blower_fan': '3',
        }
        
        if actuator not in actuator_map:
            return jsonify({'error': 'Invalid actuator'}), 400
        
        # Send relay command to Arduino
        # Format: "R1:1" (Relay 1 ON) or "R1:0" (Relay 1 OFF)
        relay_num = actuator_map[actuator]
        relay_state = '1' if state else '0'
        command = f"R{relay_num}:{relay_state}"
        
        if send_command_to_arduino(command):
            with data_lock:
                sensor_data['actuators'][actuator] = state
            
            print(f"✅ {actuator} turned {'ON' if state else 'OFF'}")
            
            return jsonify({
                'success': True,
                'actuator': actuator,
                'state': state
            })
        
        return jsonify({'error': 'Failed to send command to Arduino'}), 500
        
    except Exception as e:
        print(f"❌ Error controlling actuator: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'serial_connected': ser is not None and ser.is_open,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("🚀 Starting MASH IoT Device Server")
    print(f"📱 Device ID: {DEVICE_ID}")
    print(f"📱 Device Name: {DEVICE_NAME}")
    
    # Initialize serial connection
    if init_serial():
        # Start sensor data reading thread
        sensor_thread = threading.Thread(target=read_sensor_data, daemon=True)
        sensor_thread.start()
        print("📊 Sensor data reader started")
    else:
        print("⚠️ Running without Arduino connection")
    
    # Start Flask server
    print("🌐 Starting HTTP server on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
