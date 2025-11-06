#!/usr/bin/env python3
"""
MASH IoT Device - Live Dashboard for Raspberry Pi OS Lite
Web-based dashboard for mushroom cultivation monitoring
"""

import serial
import time
import threading
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import argparse

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from flask import Flask, render_template, jsonify, request
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not available. Install with: pip install flask flask-socketio")

# Serial port configuration
DEFAULT_SERIAL_PORT = '/dev/ttyACM0'
DEFAULT_BAUD_RATE = 9600

# Mushroom growing modes
MUSHROOM_MODES = {
    'SPAWNING': {'min_co2': 10000, 'max_co2': None, 'color': 'red'},
    'FRUITING': {'min_co2': 500, 'max_co2': 800, 'color': 'green'}
}

class LiveDashboard:
    """Live dashboard for MASH IoT Device"""
    
    def __init__(self, serial_port=DEFAULT_SERIAL_PORT, baud_rate=DEFAULT_BAUD_RATE):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.ser = None
        self.running = False
        
        # Data storage
        self.times = []
        self.co2_values = []
        self.temp_values = []
        self.hum_values = []
        self.data_lock = threading.Lock()
        self.start_datetime = None
        self.max_data_points = 100
        
        # Current state
        self.current_mode = 'SPAWNING'
        self.alert_active = False
        self.notifications = []
        self.max_notifications = 10
        
        # Statistics
        self.stats = {
            'co2': {'min': 0, 'max': 0, 'avg': 0, 'current': 0},
            'temperature': {'min': 0, 'max': 0, 'avg': 0, 'current': 0},
            'humidity': {'min': 0, 'max': 0, 'avg': 0, 'current': 0}
        }
    
    def connect_arduino(self):
        """Connect to Arduino via serial"""
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            print(f"✅ Connected to Arduino on {self.serial_port}")
            self.start_datetime = datetime.now()
            print(f"📅 Session started at: {self.start_datetime.strftime('%Y-%m-%d %I:%M:%S %p')}")
            return True
        except serial.SerialException as e:
            print(f"❌ Failed to connect to Arduino: {e}")
            return False
    
    def start_reading(self):
        """Start reading from Arduino"""
        if not self.connect_arduino():
            return False
        
        self.running = True
        
        # Send initial mode to Arduino
        time.sleep(2)
        self.set_mode(self.current_mode)
        self.add_notification(f"System started in {self.current_mode} mode", "info")
        
        # Start reading thread
        self.reading_thread = threading.Thread(target=self._reading_loop, daemon=True)
        self.reading_thread.start()
        
        print("🚀 Live dashboard started")
        print("📊 Commands: 's' for Spawning mode, 'f' for Fruiting mode")
        return True
    
    def stop_reading(self):
        """Stop reading from Arduino"""
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        print("🛑 Live dashboard stopped")
    
    def _reading_loop(self):
        """Main reading loop"""
        start_time = time.time()
        
        while self.running:
            try:
                if not self.ser or not self.ser.is_open:
                    print("⚠️ Serial connection lost, attempting to reconnect...")
                    if not self.connect_arduino():
                        time.sleep(5)
                        continue
                
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    # Parse sensor data
                    if self._parse_sensor_data(line, start_time):
                        self._update_statistics()
                        self._check_alerts()
                
            except Exception as e:
                print(f"❌ Error reading from Arduino: {e}")
                time.sleep(1)
    
    def _parse_sensor_data(self, line: str, start_time: float) -> bool:
        """Parse sensor data from Arduino output"""
        import re
        
        # Try to match sensor data pattern
        pattern = r"CO2: (\d+) ppm\tTemperature: ([0-9.]+) °C\tHumidity: ([0-9.]+) %"
        match = re.match(pattern, line)
        
        if not match:
            # Try alternative pattern
            alt_pattern = r"CO2:\s*(\d+)\s*ppm.*Temperature:\s*([0-9.]+)\s*°C.*Humidity:\s*([0-9.]+)\s*%"
            match = re.match(alt_pattern, line)
        
        if match:
            co2 = int(match.group(1))
            temp = float(match.group(2))
            hum = float(match.group(3))
            current_time = time.time() - start_time
            
            with self.data_lock:
                self.times.append(current_time)
                self.co2_values.append(co2)
                self.temp_values.append(temp)
                self.hum_values.append(hum)
                
                # Limit data points
                if len(self.times) > self.max_data_points:
                    self.times.pop(0)
                    self.co2_values.pop(0)
                    self.temp_values.pop(0)
                    self.hum_values.pop(0)
            
            print(f"📊 Time: {current_time:.1f}s, CO2: {co2} ppm, Temp: {temp}°C, Hum: {hum}%")
            return True
        
        return False
    
    def _update_statistics(self):
        """Update statistics from current data"""
        with self.data_lock:
            if len(self.co2_values) > 0:
                self.stats['co2'] = {
                    'min': min(self.co2_values),
                    'max': max(self.co2_values),
                    'avg': sum(self.co2_values) / len(self.co2_values),
                    'current': self.co2_values[-1]
                }
                
                self.stats['temperature'] = {
                    'min': min(self.temp_values),
                    'max': max(self.temp_values),
                    'avg': sum(self.temp_values) / len(self.temp_values),
                    'current': self.temp_values[-1]
                }
                
                self.stats['humidity'] = {
                    'min': min(self.hum_values),
                    'max': max(self.hum_values),
                    'avg': sum(self.hum_values) / len(self.hum_values),
                    'current': self.hum_values[-1]
                }
    
    def _check_alerts(self):
        """Check for CO2 alerts based on current mode"""
        if len(self.co2_values) == 0:
            return
        
        current_co2 = self.co2_values[-1]
        mode_config = MUSHROOM_MODES[self.current_mode]
        should_alert = False
        alert_message = ""
        
        if self.current_mode == 'SPAWNING':
            if current_co2 < mode_config['min_co2']:
                should_alert = True
                alert_message = f"SPAWNING ALERT: CO2 too low! Need > {mode_config['min_co2']} ppm, current: {current_co2} ppm"
        elif self.current_mode == 'FRUITING':
            if current_co2 < mode_config['min_co2']:
                should_alert = True
                alert_message = f"FRUITING ALERT: CO2 too low! Need {mode_config['min_co2']}-{mode_config['max_co2']} ppm, current: {current_co2} ppm"
            elif current_co2 > mode_config['max_co2']:
                should_alert = True
                alert_message = f"FRUITING ALERT: CO2 too high! Need {mode_config['min_co2']}-{mode_config['max_co2']} ppm, current: {current_co2} ppm"
        
        # Add notification if alert status changed
        if should_alert and not self.alert_active:
            self.add_notification(alert_message, "alert")
        elif not should_alert and self.alert_active:
            self.add_notification(f"CO2 levels back to normal for {self.current_mode} mode", "success")
        
        self.alert_active = should_alert
    
    def set_mode(self, mode: str):
        """Set mushroom growing mode"""
        if mode not in MUSHROOM_MODES:
            print(f"❌ Invalid mode: {mode}")
            return False
        
        if self.ser and self.ser.is_open:
            try:
                if mode == 'SPAWNING':
                    self.ser.write(b's\n')
                elif mode == 'FRUITING':
                    self.ser.write(b'f\n')
                
                self.current_mode = mode
                print(f"🔄 Switched to {mode} mode")
                self.add_notification(f"Switched to {mode} mode", "info")
                return True
            except Exception as e:
                print(f"❌ Error sending command to Arduino: {e}")
                return False
        else:
            print("❌ Arduino not connected")
            return False
    
    def add_notification(self, message: str, notification_type: str = "info"):
        """Add a notification"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        notification = {
            'time': timestamp,
            'message': message,
            'type': notification_type
        }
        self.notifications.append(notification)
        
        # Keep only recent notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
    
    def get_data(self) -> Dict[str, Any]:
        """Get current data for web dashboard"""
        with self.data_lock:
            return {
                'times': self.times.copy(),
                'co2_values': self.co2_values.copy(),
                'temp_values': self.temp_values.copy(),
                'hum_values': self.hum_values.copy(),
                'stats': self.stats.copy(),
                'current_mode': self.current_mode,
                'alert_active': self.alert_active,
                'notifications': self.notifications[-5:],  # Last 5 notifications
                'uptime': (datetime.now() - self.start_datetime).total_seconds() if self.start_datetime else 0
            }

def create_web_app(dashboard: LiveDashboard):
    """Create Flask web application"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mash-iot-device-secret'
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    @app.route('/')
    def index():
        return render_template('dashboard.html')
    
    @app.route('/api/data')
    def get_data():
        return jsonify(dashboard.get_data())
    
    @app.route('/api/mode', methods=['POST'])
    def set_mode():
        data = request.get_json()
        mode = data.get('mode', '').upper()
        
        if mode in ['SPAWNING', 'FRUITING']:
            success = dashboard.set_mode(mode)
            return jsonify({'success': success, 'mode': mode})
        else:
            return jsonify({'success': False, 'error': 'Invalid mode'}), 400
    
    @socketio.on('connect')
    def handle_connect():
        print('📱 Client connected to dashboard')
        emit('data_update', dashboard.get_data())
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('📱 Client disconnected from dashboard')
    
    def send_data_update():
        """Send data updates to connected clients"""
        while dashboard.running:
            try:
                socketio.emit('data_update', dashboard.get_data())
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                print(f"❌ Error sending data update: {e}")
                break
    
    # Start data update thread
    update_thread = threading.Thread(target=send_data_update, daemon=True)
    update_thread.start()
    
    return app, socketio

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='MASH IoT Device Live Dashboard')
    parser.add_argument('--port', help='Arduino serial port', default=DEFAULT_SERIAL_PORT)
    parser.add_argument('--baud', type=int, help='Serial baud rate', default=DEFAULT_BAUD_RATE)
    parser.add_argument('--web-port', type=int, help='Web server port', default=8080)
    parser.add_argument('--host', help='Web server host', default='0.0.0.0')
    parser.add_argument('--no-web', action='store_true', help='Run without web interface')
    args = parser.parse_args()
    
    print("🍄 MASH IoT Device - Live Dashboard")
    print("=" * 50)
    
    # Create dashboard
    dashboard = LiveDashboard(args.port, args.baud)
    
    # Start reading from Arduino
    if not dashboard.start_reading():
        print("❌ Failed to start dashboard")
        return 1
    
    try:
        if not args.no_web and FLASK_AVAILABLE:
            print(f"🌐 Starting web dashboard on http://{args.host}:{args.web_port}")
            app, socketio = create_web_app(dashboard)
            socketio.run(app, host=args.host, port=args.web_port, debug=False)
        else:
            if args.no_web:
                print("🖥️ Running in console mode (no web interface)")
            else:
                print("⚠️ Flask not available, running in console mode")
                print("   Install Flask with: pip install flask flask-socketio")
            
            # Console mode
            print("📊 Dashboard running. Press Ctrl+C to stop.")
            print("Commands: 's' for Spawning mode, 'f' for Fruiting mode")
            
            while True:
                try:
                    # Simple keyboard input (non-blocking)
                    import select
                    if select.select([sys.stdin], [], [], 0)[0]:
                        line = sys.stdin.readline().strip().lower()
                        if line == 's':
                            dashboard.set_mode('SPAWNING')
                        elif line == 'f':
                            dashboard.set_mode('FRUITING')
                        elif line == 'q':
                            break
                    
                    time.sleep(1)
                except KeyboardInterrupt:
                    break
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping dashboard...")
    finally:
        dashboard.stop_reading()
    
    print("✅ Dashboard stopped")
    return 0

if __name__ == '__main__':
    sys.exit(main())
