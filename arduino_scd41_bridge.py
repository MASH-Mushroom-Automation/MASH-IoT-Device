#!/usr/bin/env python3
"""
Arduino SCD41 Bridge for Raspberry Pi
Reads sensor data from Arduino and integrates with MASH IoT Device
"""

import serial
import time
import re
import threading
import logging
import json
import os
import sys
from datetime import datetime, timedelta
import argparse

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import MASH IoT Device modules
from sensors.sensor_reading import SensorReading

# Serial port configuration (change as needed)
DEFAULT_SERIAL_PORT = '/dev/ttyACM0'  # Common Arduino port on Raspberry Pi
DEFAULT_BAUD_RATE = 9600

# Regex to parse legacy serial output (pre-CSV format)
PATTERN = r"CO2: (\d+) ppm\tTemperature: ([0-9.]+) °C\tHumidity: ([0-9.]+) %"
ALT_PATTERN = r"CO2:\s*(\d+)\s*ppm.*Temperature:\s*([0-9.]+)\s*°C.*Humidity:\s*([0-9.]+)\s*%"

# Mushroom growing modes
MUSHROOM_MODES = {
    'SPAWNING': {'min_co2': 10000, 'max_co2': None},
    'FRUITING': {'min_co2': 500, 'max_co2': 800}
}

class ArduinoSCD41Bridge:
    """Bridge between Arduino SCD41 sensor and MASH IoT Device"""
    
    def __init__(self, serial_port=DEFAULT_SERIAL_PORT, baud_rate=DEFAULT_BAUD_RATE, 
                 data_callback=None, log_level=logging.INFO):
        """
        Initialize Arduino SCD41 Bridge
        
        Args:
            serial_port: Serial port for Arduino connection
            baud_rate: Serial baud rate
            data_callback: Callback function for new sensor readings
            log_level: Logging level
        """
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.data_callback = data_callback
        self.ser = None
        self.running = False
        self.current_mode = 'SPAWNING'  # Default mode
        
        # Data storage
        self.last_reading = None
        self.readings = []
        self.max_readings = 100  # Store last 100 readings
        self.start_time = None
        self.reading_count = 0
        self.error_count = 0
        self.last_alert = None
        
        # Threading
        self._thread = None
        self._lock = threading.Lock()
    
    def connect(self):
        """Connect to Arduino via serial port"""
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            self.logger.info(f"Connected to Arduino on {self.serial_port}")
            time.sleep(2)  # Wait for Arduino to reset
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to Arduino: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Arduino"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.logger.info("Disconnected from Arduino")
    
    def start(self):
        """Start reading from Arduino"""
        if self.running:
            self.logger.warning("Arduino bridge already running")
            return True
        
        if not self.ser:
            if not self.connect():
                return False
        
        self.running = True
        self.start_time = datetime.now()
        self.logger.info(f"Starting Arduino SCD41 bridge at {self.start_time}")
        
        # Send initial mode to Arduino
        self.set_mode(self.current_mode)
        
        # Start reading thread
        self._thread = threading.Thread(target=self._reading_loop, daemon=True)
        self._thread.start()
        
        return True
    
    def stop(self):
        """Stop reading from Arduino"""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        self.disconnect()
        self.logger.info("Arduino SCD41 bridge stopped")
    
    def set_mode(self, mode):
        """Set mushroom growing mode on Arduino"""
        if mode not in MUSHROOM_MODES:
            self.logger.error(f"Invalid mode: {mode}")
            return False
        
        if self.ser and self.ser.is_open:
            try:
                if mode == 'SPAWNING':
                    self.ser.write(b's\n')
                elif mode == 'FRUITING':
                    self.ser.write(b'f\n')
                self.current_mode = mode
                self.logger.info(f"Set Arduino to {mode} mode")
                return True
            except Exception as e:
                self.logger.error(f"Failed to set mode: {e}")
                return False
        else:
            self.logger.error("Cannot set mode: Arduino not connected")
            return False
    
    def _reading_loop(self):
        """Main reading loop (runs in separate thread)"""
        self.logger.info("Starting Arduino reading loop")
        
        while self.running:
            try:
                if not self.ser or not self.ser.is_open:
                    self.logger.error("Serial connection lost, attempting to reconnect")
                    self.connect()
                    time.sleep(2)
                    continue
                
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    handled = False

                    if line.startswith('SENSOR'):
                        try:
                            reading, mode, alert_active = self._parse_sensor_message(line)
                        except ValueError as exc:
                            self.logger.warning(f"Failed to parse SENSOR message '{line}': {exc}")
                        else:
                            with self._lock:
                                self.last_reading = reading
                                self.readings.append(reading)
                                if len(self.readings) > self.max_readings:
                                    self.readings.pop(0)
                                self.reading_count += 1
                                self.current_mode = mode
                                if alert_active:
                                    self.last_alert = {
                                        'mode': mode,
                                        'co2': reading.co2_ppm,
                                        'arduino_timestamp_ms': reading.metadata.get('arduino_timestamp_ms'),
                                        'received_at': datetime.now()
                                    }

                            self.logger.debug(f"New reading: {reading}")

                            if self.data_callback:
                                try:
                                    self.data_callback(reading)
                                except Exception as e:
                                    self.logger.error(f"Error in data callback: {e}")

                            handled = True

                    elif line.startswith('MODE'):
                        self._handle_mode_message(line)
                        handled = True

                    elif line.startswith('ALERT'):
                        self._handle_alert_message(line)
                        handled = True

                    if not handled:
                        # Try to parse legacy format for backward compatibility
                        match = re.match(PATTERN, line)
                        if not match:
                            match = re.match(ALT_PATTERN, line)

                        if match:
                            co2 = int(match.group(1))
                            temp = float(match.group(2))
                            hum = float(match.group(3))

                            reading = SensorReading(
                                temperature=temp,
                                humidity=hum,
                                co2_ppm=co2,
                                timestamp=datetime.now()
                            )

                            with self._lock:
                                self.last_reading = reading
                                self.readings.append(reading)
                                if len(self.readings) > self.max_readings:
                                    self.readings.pop(0)
                                self.reading_count += 1

                            self.logger.debug(f"New reading (legacy format): {reading}")

                            if self.data_callback:
                                try:
                                    self.data_callback(reading)
                                except Exception as e:
                                    self.logger.error(f"Error in data callback: {e}")
                        else:
                            if line and not line.startswith('=') and not line.startswith('Waiting'):
                                self.logger.debug(f"Arduino: {line}")
            
            except Exception as e:
                self.logger.error(f"Error reading from Arduino: {e}")
                self.error_count += 1
                time.sleep(1)
    
    def get_latest_reading(self):
        """Get latest sensor reading"""
        with self._lock:
            return self.last_reading
    
    def get_readings(self, count=None):
        """Get recent readings"""
        with self._lock:
            if count:
                return self.readings[-count:]
            return self.readings.copy()
    
    def get_statistics(self):
        """Get sensor statistics"""
        with self._lock:
            stats = {
                'reading_count': self.reading_count,
                'error_count': self.error_count,
                'uptime': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                'last_reading_time': self.last_reading.timestamp.isoformat() if self.last_reading else None,
                'mode': self.current_mode
            }
            
            # Add sensor statistics if available
            if self.readings:
                co2_values = [r.co2_ppm for r in self.readings]
                temp_values = [r.temperature for r in self.readings]
                hum_values = [r.humidity for r in self.readings]
                
                stats.update({
                    'co2': {
                        'min': min(co2_values),
                        'max': max(co2_values),
                        'avg': sum(co2_values) / len(co2_values),
                        'current': self.last_reading.co2_ppm if self.last_reading else None
                    },
                    'temperature': {
                        'min': min(temp_values),
                        'max': max(temp_values),
                        'avg': sum(temp_values) / len(temp_values),
                        'current': self.last_reading.temperature if self.last_reading else None
                    },
                    'humidity': {
                        'min': min(hum_values),
                        'max': max(hum_values),
                        'avg': sum(hum_values) / len(hum_values),
                        'current': self.last_reading.humidity if self.last_reading else None
                    }
                })
            
            if self.last_alert:
                stats['last_alert'] = {
                    'mode': self.last_alert['mode'],
                    'co2': self.last_alert['co2'],
                    'arduino_timestamp_ms': self.last_alert['arduino_timestamp_ms'],
                    'received_at': self.last_alert['received_at'].isoformat()
                }

            return stats

    def _parse_sensor_message(self, line):
        """Parse CSV sensor message from Arduino"""
        parts = [part.strip() for part in line.split(',')]
        if len(parts) < 7:
            raise ValueError('expected at least 7 comma-separated fields')

        _, arduino_ts, co2_str, temp_str, hum_str, mode, alert_str = parts[:7]

        co2 = int(co2_str)
        temperature = float(temp_str)
        humidity = float(hum_str)

        alert_active = alert_str in {'1', 'true', 'TRUE', 'True'}

        reading = SensorReading(
            temperature=temperature,
            humidity=humidity,
            co2_ppm=co2,
            timestamp=datetime.now(),
            metadata={
                'mode': mode,
                'alert_active': alert_active,
                'arduino_timestamp_ms': int(arduino_ts)
            }
        )

        return reading, mode, alert_active

    def _handle_mode_message(self, line):
        """Handle MODE message from Arduino"""
        parts = [part.strip() for part in line.split(',')]
        if len(parts) < 2:
            self.logger.warning(f"Malformed MODE message: '{line}'")
            return

        mode = parts[1].upper()
        if mode in MUSHROOM_MODES:
            self.current_mode = mode
            self.logger.info(f"Arduino mode changed to {mode}")
        else:
            self.logger.warning(f"Unknown mode reported by Arduino: '{parts[1]}'")

    def _handle_alert_message(self, line):
        """Handle ALERT message from Arduino"""
        parts = [part.strip() for part in line.split(',')]
        if len(parts) < 4:
            self.logger.warning(f"Malformed ALERT message: '{line}'")
            return

        try:
            alert = {
                'mode': parts[2],
                'co2': int(parts[3]),
                'arduino_timestamp_ms': int(parts[1]),
                'received_at': datetime.now()
            }
        except ValueError as exc:
            self.logger.warning(f"Failed to parse ALERT message '{line}': {exc}")
            return

        with self._lock:
            self.last_alert = alert

        self.current_mode = alert['mode'] if alert['mode'] in MUSHROOM_MODES else self.current_mode
        self.logger.warning(f"Alert received from Arduino: mode={alert['mode']}, co2={alert['co2']} ppm")

def on_sensor_reading(reading):
    """Example callback for new sensor readings"""
    print(f"New reading: CO2={reading.co2_ppm} ppm, Temp={reading.temperature}°C, Hum={reading.humidity}%")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Arduino SCD41 Bridge for Raspberry Pi')
    parser.add_argument('--port', help='Serial port for Arduino connection', default=DEFAULT_SERIAL_PORT)
    parser.add_argument('--baud', type=int, help='Serial baud rate', default=DEFAULT_BAUD_RATE)
    parser.add_argument('--mode', choices=['SPAWNING', 'FRUITING'], help='Mushroom growing mode', default='SPAWNING')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--stats', action='store_true', help='Print statistics periodically')
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Arduino SCD41 Bridge")
    
    try:
        # Create bridge
        bridge = ArduinoSCD41Bridge(
            serial_port=args.port,
            baud_rate=args.baud,
            data_callback=on_sensor_reading,
            log_level=log_level
        )
        
        # Set initial mode
        bridge.current_mode = args.mode
        
        # Start bridge
        if not bridge.start():
            logger.error("Failed to start Arduino bridge")
            return 1
        
        # Main loop
        try:
            while True:
                if args.stats:
                    stats = bridge.get_statistics()
                    print("\n" + "="*50)
                    print(f"Arduino SCD41 Bridge Statistics - Mode: {stats['mode']}")
                    print(f"Uptime: {timedelta(seconds=int(stats['uptime']))}")
                    print(f"Readings: {stats['reading_count']}, Errors: {stats['error_count']}")
                    
                    if 'co2' in stats:
                        print(f"CO2: Current={stats['co2']['current']} ppm, "
                              f"Avg={stats['co2']['avg']:.1f} ppm, "
                              f"Min={stats['co2']['min']} ppm, "
                              f"Max={stats['co2']['max']} ppm")
                        
                        print(f"Temperature: Current={stats['temperature']['current']:.1f}°C, "
                              f"Avg={stats['temperature']['avg']:.1f}°C, "
                              f"Min={stats['temperature']['min']:.1f}°C, "
                              f"Max={stats['temperature']['max']:.1f}°C")
                        
                        print(f"Humidity: Current={stats['humidity']['current']:.1f}%, "
                              f"Avg={stats['humidity']['avg']:.1f}%, "
                              f"Min={stats['humidity']['min']:.1f}%, "
                              f"Max={stats['humidity']['max']:.1f}%")
                    
                    print("="*50)
                
                time.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    finally:
        if 'bridge' in locals():
            bridge.stop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
