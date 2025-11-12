#!/usr/bin/env python3
"""
MASH IoT Device - Integrated Server
Combines sensor reading, actuator control, and HTTP API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import time
import threading
from datetime import datetime
from collections import deque
import logging
import os
import socket
from dotenv import load_dotenv
from rule_based_controller import RuleBasedController
from data_logger import DataLogger
from src.utils.bluetooth_manager import BluetoothManager
from src.utils.bluetooth_tethering import BluetoothTethering
from src.utils.bluetooth_setup import setup_bluetooth
from src.utils.config import Config
from src.backend_client import BackendClient
from src.firebase_client import FirebaseClient

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("WARNING: RPi.GPIO not available, running in simulation mode")


def get_ip_address():
    """Get the device's IP address"""
    try:
        # Create a socket connection to an external server
        # This doesn't actually establish a connection, but gets the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        logging.error(f"Error getting IP address: {e}")
        return "127.0.0.1"  # Return localhost as fallback


def get_mac_address():
    """Get the device's MAC address"""
    try:
        # Try to get the MAC address of the primary interface
        import uuid
        # Get the hex representation of the MAC address
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                        for elements in range(0, 8*6, 8)][::-1])
        return mac
    except Exception as e:
        logging.error(f"Error getting MAC address: {e}")
        return ""  # Return empty string as fallback

# ========== Load Environment Variables ==========
load_dotenv()

# ========== Load Configuration ==========
config = Config(config_file='config/device_config.yaml')

# Validate configuration
if not config.validate():
    print("ERROR: Invalid configuration. Please check config/device_config.yaml")
    exit(1)

# ========== Configuration Values ==========
# Device Identity
DEVICE_ID = config.get_nested('device', 'id', default='MASH-A1-CAL25-D5A91F')
DEVICE_NAME = config.get_nested('device', 'name', default='MASH Chamber #1')

# Serial Configuration (Arduino)
SERIAL_PORT = config.get_nested('sensors', 'serial', 'port', default='/dev/ttyUSB0')
SERIAL_BAUD = config.get_nested('sensors', 'serial', 'baud_rate', default=9600)

# GPIO Pin Configuration (BCM numbering)
gpio_config = config.get_gpio_config()
RELAY_BLOWER_FAN = gpio_config['relays']['blower_fan']
RELAY_EXHAUST_FAN = gpio_config['relays']['exhaust_fan']
RELAY_HUMIDIFIER = gpio_config['relays']['humidifier']
RELAY_LED_LIGHTS = gpio_config['relays']['led_lights']

# Data collection
WINDOW_SIZE = 30
READING_HISTORY = deque(maxlen=WINDOW_SIZE)

# ========== Logging Setup ==========
log_level = config.get('log_level', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== Flask App ==========
app = Flask(__name__)
CORS(app)

# ========== Global State ==========
ser = None
current_mode = 's'  # 's' = Spawning, 'f' = Fruiting

# Current sensor data
sensor_data = {
    'co2': 0,
    'temperature': 0.0,
    'humidity': 0.0,
    'mode': 's',
    'alert': False,
    'timestamp': datetime.now().isoformat()
}

# Actuator states
actuator_states = {
    'blower_fan': False,
    'exhaust_fan': False,
    'humidifier': False,
    'led_lights': False
}

# Lock for thread-safe access
data_lock = threading.Lock()


# ========== GPIO/Actuator Control ==========
class ActuatorController:
    """Controls relay-connected actuators"""
    
    def __init__(self):
        self.simulation_mode = not GPIO_AVAILABLE
        
        if not self.simulation_mode:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(RELAY_BLOWER_FAN, GPIO.OUT)
            GPIO.setup(RELAY_EXHAUST_FAN, GPIO.OUT)
            GPIO.setup(RELAY_HUMIDIFIER, GPIO.OUT)
            GPIO.setup(RELAY_LED_LIGHTS, GPIO.OUT)
            # Turn all off initially (relays are active LOW: HIGH = OFF)
            self._set_all_off()
            logger.info("GPIO initialized - actuators ready")
        else:
            logger.info("WARNING: Running in SIMULATION mode - no GPIO control")
    
    def _set_all_off(self):
        """Turn off all actuators (active LOW relays: HIGH = OFF)"""
        GPIO.output(RELAY_BLOWER_FAN, GPIO.HIGH)
        GPIO.output(RELAY_EXHAUST_FAN, GPIO.HIGH)
        GPIO.output(RELAY_HUMIDIFIER, GPIO.HIGH)
        GPIO.output(RELAY_LED_LIGHTS, GPIO.HIGH)
    
    def set_actuator(self, actuator_name, state):
        """Control a specific actuator"""
        pin_map = {
            'blower_fan': RELAY_BLOWER_FAN,
            'exhaust_fan': RELAY_EXHAUST_FAN,
            'humidifier': RELAY_HUMIDIFIER,
            'led_lights': RELAY_LED_LIGHTS
        }
        
        if actuator_name not in pin_map:
            logger.error(f"Unknown actuator: {actuator_name}")
            return False
        
        pin = pin_map[actuator_name]
        
        with data_lock:
            actuator_states[actuator_name] = state
        
        if not self.simulation_mode:
            # Active LOW relays: LOW = ON, HIGH = OFF
            GPIO.output(pin, GPIO.LOW if state else GPIO.HIGH)
        
        logger.info(f"Actuator {actuator_name}: {'ON' if state else 'OFF'}")
        return True
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        if not self.simulation_mode:
            self._set_all_off()
            GPIO.cleanup()
            logger.info("GPIO cleanup complete")


# Initialize actuator controller
actuator_controller = ActuatorController()

# Initialize rule-based automation controller
automation_controller = RuleBasedController()

# Initialize data logger
data_logger = DataLogger()

# Initialize Bluetooth manager and tethering
bt_config = config.get_bluetooth_config()
bluetooth_device_name = bt_config['device_name']
logger.info(f"Initializing Bluetooth with device name: {bluetooth_device_name}")
bluetooth_manager = BluetoothManager(device_name=bluetooth_device_name)
bluetooth_tethering = BluetoothTethering(bluetooth_manager)

# Initialize Backend Client
backend_client = None
try:
    # Get device ID from config file
    device_id = config.get_nested('device', 'id')
    if not device_id:
        device_id = os.getenv('DEVICE_ID', 'MASH-A1-CAL25-D5A91F')
    
    # Debug logging
    logger.info(f"Device ID from config: '{device_id}'")
    logger.info(f"DEVICE_ID variable: '{DEVICE_ID}'")
    
    backend_api_url = os.getenv('BACKEND_API_URL', config.get('backend_api_url', 'https://mash-backend-api-production.up.railway.app/api/v1'))
    backend_api_key = os.getenv('BACKEND_API_KEY', config.get('backend_api_key', ''))
    backend_timeout = int(os.getenv('BACKEND_TIMEOUT', config.get('backend_timeout', 30)))
    
    backend_client = BackendClient(
        api_url=backend_api_url,
        device_id=device_id,  # Use the device ID from config
        api_key=backend_api_key if backend_api_key else None,
        timeout=backend_timeout,
        mock_mode=not backend_api_url.startswith('http')
    )
    logger.info(f"✅ Backend client initialized: {backend_api_url}")
    logger.info(f"✅ Using device ID: {device_id}")
except Exception as e:
    logger.error(f"❌ Failed to initialize backend client: {e}")

# Initialize Firebase Client
firebase_client = None
try:
    firebase_project_id = os.getenv('FIREBASE_PROJECT_ID', config.get('firebase_project_id', ''))
    firebase_database_url = os.getenv('FIREBASE_DATABASE_URL', config.get('firebase_database_url', ''))
    firebase_client_email = os.getenv('FIREBASE_CLIENT_EMAIL', config.get('firebase_client_email', ''))
    firebase_private_key = os.getenv('FIREBASE_PRIVATE_KEY', config.get('firebase_private_key', ''))
    
    if firebase_project_id and firebase_database_url:
        firebase_client = FirebaseClient(
            project_id=firebase_project_id,
            database_url=firebase_database_url,
            service_account_email=firebase_client_email,
            private_key=firebase_private_key,
            device_id=DEVICE_ID,
            mock_mode=not firebase_database_url.startswith('http')
        )
        logger.info(f"✅ Firebase client initialized: {firebase_database_url}")
    else:
        logger.warning("⚠️ Firebase credentials not found, running without Firebase")
except Exception as e:
    logger.error(f"❌ Failed to initialize Firebase client: {e}")


# ========== Serial Communication ==========
def find_arduino_port():
    """Auto-detect Arduino serial port"""
    import serial.tools.list_ports
    
    ports = serial.tools.list_ports.comports()
    
    # Try common Arduino ports first
    common_ports = ['/dev/ttyACM0', '/dev/ttyUSB0', '/dev/ttyACM1', '/dev/ttyUSB1']
    
    for port_name in common_ports:
        for port in ports:
            if port.device == port_name:
                logger.info(f"Found potential Arduino port: {port.device} - {port.description}")
                return port.device
    
    # If not found in common ports, try any USB serial device
    for port in ports:
        if 'USB' in port.description or 'Arduino' in port.description:
            logger.info(f"Found USB serial device: {port.device} - {port.description}")
            return port.device
    
    return None


def init_serial():
    """Initialize serial connection to Arduino"""
    global ser
    
    # Try configured port first
    port_to_try = SERIAL_PORT
    
    try:
        logger.info(f"Attempting to connect to Arduino on {port_to_try}...")
        ser = serial.Serial(port_to_try, SERIAL_BAUD, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        logger.info(f"Serial connection established on {port_to_try}")
        return True
    except Exception as e:
        logger.warning(f"WARNING: Failed to connect on {port_to_try}: {e}")
        
        # Try auto-detection
        logger.info("Attempting to auto-detect Arduino port...")
        detected_port = find_arduino_port()
        
        if detected_port and detected_port != port_to_try:
            try:
                logger.info(f"Trying detected port: {detected_port}...")
                ser = serial.Serial(detected_port, SERIAL_BAUD, timeout=1)
                time.sleep(2)
                logger.info(f"Serial connection established on {detected_port}")
                logger.info(f"TIP: Update SERIAL_PORT in config to: {detected_port}")
                return True
            except Exception as e2:
                logger.error(f"ERROR: Failed to connect on detected port: {e2}")
        
        logger.error("ERROR: Could not establish serial connection to Arduino")
        logger.info("TIP: Run 'python3 check_serial.py' to diagnose serial port issues")
        return False


def parse_sensor_line(line):
    """Parse sensor data from Arduino
    Format: SENSOR,timestamp,co2,temperature,humidity,mode,alert
    """
    try:
        parts = line.split(',')
        if len(parts) >= 7 and parts[0] == 'SENSOR':
            return {
                'co2': int(parts[2]),
                'temperature': float(parts[3]),
                'humidity': float(parts[4]),
                'mode': 's' if parts[5] == 'SPAWNING' else 'f',
                'alert': parts[6] == '1',
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error parsing sensor data: {e}")
    return None


def read_sensor_data():
    """Continuously read sensor data from Arduino"""
    global sensor_data, current_mode
    
    logger.info("Starting sensor data reader...")
    
    while True:
        try:
            if ser and ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                
                # Parse sensor data
                if line.startswith('SENSOR,'):
                    data = parse_sensor_line(line)
                    if data:
                        with data_lock:
                            sensor_data.update(data)
                            current_mode = data['mode']
                        
                        # Add to history
                        READING_HISTORY.append(data)
                        
                        # Log to database
                        data_logger.log_sensor_reading(data)
                        
                        # Sync to Backend and Firebase
                        sync_sensor_data(data)
                        
                        logger.debug(f"Sensor data: CO2={data['co2']}ppm, T={data['temperature']}°C, H={data['humidity']}%")
                
                # Handle mode changes
                elif line.startswith('MODE,'):
                    mode_name = line.split(',')[1]
                    with data_lock:
                        current_mode = 's' if mode_name == 'SPAWNING' else 'f'
                        sensor_data['mode'] = current_mode
                    logger.info(f"Mode changed to {mode_name}")
                
                # Handle alerts
                elif line.startswith('ALERT,'):
                    logger.warning(f"ALERT: {line}")
                
        except Exception as e:
            logger.error(f"ERROR: Error reading sensor data: {e}")
        
        time.sleep(0.1)


# ========== Data Syncing Functions ==========
def sync_sensor_data(data):
    """Sync sensor data to Backend and Firebase"""
    try:
        # Sync to Backend
        if backend_client:
            threading.Thread(
                target=lambda: backend_client.send_sensor_data(data),
                daemon=True
            ).start()
        
        # Sync to Firebase
        if firebase_client:
            threading.Thread(
                target=lambda: firebase_client.send_sensor_data(data),
                daemon=True
            ).start()
            
    except Exception as e:
        logger.error(f"Error syncing sensor data: {e}")


def sync_device_status(status='ONLINE'):
    """Sync device status to Backend and Firebase
    
    Args:
        status: Device status to set (default: 'ONLINE')
    """
    try:
        # Only include fields that are supported by the Prisma schema
        # Format the timestamp in a way that's compatible with the backend
        # Use UTC time to avoid timezone issues
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        status_data = {
            'status': status,
            'lastSeen': current_time,
            'firmware': '1.0.0',
            'ipAddress': get_ip_address(),
            'macAddress': get_mac_address()
        }
        logger.info(f"Using timestamp: {current_time}")
        
        # Sync to Backend
        if backend_client:
            threading.Thread(
                target=lambda: backend_client.update_device_status(status, status_data),
                daemon=True
            ).start()
        
        # Sync to Firebase
        if firebase_client:
            threading.Thread(
                target=lambda: firebase_client.send_device_status(status_data),
                daemon=True
            ).start()
            
    except Exception as e:
        logger.error(f"Error syncing device status: {e}")


def mark_device_offline():
    """Mark device as offline in backend"""
    try:
        logger.info("Marking device as OFFLINE in backend")
        # Use a direct call instead of a thread to ensure it completes before shutdown
        if backend_client:
            current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            status_data = {
                'status': 'OFFLINE',
                'lastSeen': current_time,
                'ipAddress': get_ip_address(),
                'macAddress': get_mac_address()
            }
            backend_client.update_device_status('OFFLINE', status_data)
            logger.info("Device marked as OFFLINE successfully")
    except Exception as e:
        logger.error(f"Error marking device as offline: {e}")


def sync_actuator_states():
    """Sync actuator states to Backend and Firebase"""
    try:
        # Sync to Firebase
        if firebase_client:
            threading.Thread(
                target=lambda: firebase_client.send_actuator_states(actuator_states.copy()),
                daemon=True
            ).start()
            
    except Exception as e:
        logger.error(f"Error syncing actuator states: {e}")


def send_command_to_arduino(command):
    """Send command to Arduino via serial"""
    try:
        if ser:
            ser.write(f"{command}\n".encode('utf-8'))
            logger.info(f"Sent command to Arduino: {command}")
            return True
        return False
    except Exception as e:
        logger.error(f"ERROR: Failed to send command: {e}")
        return False


def automation_loop():
    """Rule-based automation loop - runs every 10 seconds"""
    logger.info("Starting rule-based automation loop...")
    
    while True:
        try:
            if automation_controller.is_enabled():
                with data_lock:
                    current_sensor_data = sensor_data.copy()
                    current_actuator_states = actuator_states.copy()
                
                # Get automation decision
                decision = automation_controller.analyze_and_decide(
                    current_sensor_data,
                    current_actuator_states
                )
                
                # Execute recommended actions
                if decision.get('actions'):
                    for actuator, state in decision['actions'].items():
                        if actuator in actuator_states:
                            actuator_controller.set_actuator(actuator, state)
                            logger.info(f"Automation Action: {actuator} -> {'ON' if state else 'OFF'}")
                    
                    # Log actuator changes
                    data_logger.log_actuator_change(actuator_states, current_sensor_data.get('mode', 's'), 'automation')
                    
                    # Sync actuator states
                    sync_actuator_states()
                    
                    # Log reasoning
                    if decision.get('reasoning'):
                        for reason in decision['reasoning']:
                            logger.info(f"   Reasoning: {reason}")
                
                # Log automation decision
                data_logger.log_automation_decision(decision)
            
        except Exception as e:
            logger.error(f"ERROR: Error in automation loop: {e}")
        
        time.sleep(10)  # Run every 10 seconds


# ========== API Endpoints ==========

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get device status"""
    return jsonify({
        'success': True,
        'data': {
            'deviceId': DEVICE_ID,
            'deviceName': DEVICE_NAME,
            'status': 'online',
            'serialConnected': ser is not None and ser.is_open if ser else False,
            'timestamp': datetime.now().isoformat()
        }
    })


@app.route('/api/sensor/current', methods=['GET'])
def get_current_sensor_data():
    """Get current sensor readings"""
    with data_lock:
        return jsonify({
            'success': True,
            'data': {
                **sensor_data,
                'actuators': actuator_states
            }
        })


@app.route('/api/sensor/history', methods=['GET'])
def get_sensor_history():
    """Get sensor reading history"""
    limit = request.args.get('limit', 30, type=int)
    history_list = list(READING_HISTORY)[-limit:]
    
    return jsonify({
        'success': True,
        'data': {
            'readings': history_list,
            'count': len(history_list)
        }
    })


@app.route('/api/mode', methods=['POST'])
def set_mode():
    """Set device mode (Spawning or Fruiting)"""
    try:
        data = request.get_json()
        mode = data.get('mode', '').lower()
        
        if mode not in ['s', 'f', 'spawning', 'fruiting']:
            return jsonify({
                'success': False,
                'error': 'Invalid mode. Use "s"/"spawning" or "f"/"fruiting"'
            }), 400
        
        # Normalize mode
        mode_char = 's' if mode in ['s', 'spawning'] else 'f'
        mode_name = 'Spawning' if mode_char == 's' else 'Fruiting'
        
        # Send mode command to Arduino
        if send_command_to_arduino(mode_char):
            with data_lock:
                sensor_data['mode'] = mode_char
            
            logger.info(f"Mode set to {mode_name}")
            
            return jsonify({
                'success': True,
                'data': {
                    'mode': mode_char,
                    'modeName': mode_name
                }
            })
        
        return jsonify({
            'success': False,
            'error': 'Failed to send command to Arduino'
        }), 500
        
    except Exception as e:
        logger.error(f"ERROR: Error setting mode: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/actuator', methods=['POST'])
def control_actuator():
    """Control actuator (relay)"""
    try:
        data = request.get_json()
        actuator = data.get('actuator', '')
        state = data.get('state', False)
        
        valid_actuators = ['blower_fan', 'exhaust_fan', 'humidifier', 'led_lights']
        
        if actuator not in valid_actuators:
            return jsonify({
                'success': False,
                'error': f'Invalid actuator. Valid options: {", ".join(valid_actuators)}'
            }), 400
        
        # Control the actuator
        if actuator_controller.set_actuator(actuator, state):
            return jsonify({
                'success': True,
                'data': {
                    'actuator': actuator,
                    'state': state
                }
            })
        
        return jsonify({
            'success': False,
            'error': 'Failed to control actuator'
        }), 500
        
    except Exception as e:
        logger.error(f"ERROR: Error controlling actuator: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/actuators', methods=['GET'])
def get_actuator_states():
    """Get all actuator states"""
    with data_lock:
        return jsonify({
            'success': True,
            'data': actuator_states
        })


@app.route('/api/automation/status', methods=['GET'])
def get_automation_status():
    """Get rule-based automation status"""
    try:
        status = automation_controller.get_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"ERROR: Error getting automation status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/automation/enable', methods=['POST'])
def enable_automation():
    """Enable rule-based automation"""
    try:
        automation_controller.enable()
        return jsonify({
            'success': True,
            'data': {
                'enabled': True,
                'message': 'Rule-based automation enabled'
            }
        })
    except Exception as e:
        logger.error(f"ERROR: Error enabling automation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/automation/disable', methods=['POST'])
def disable_automation():
    """Disable rule-based automation"""
    try:
        automation_controller.disable()
        return jsonify({
            'success': True,
            'data': {
                'enabled': False,
                'message': 'Rule-based automation disabled'
            }
        })
    except Exception as e:
        logger.error(f"ERROR: Error disabling automation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/automation/history', methods=['GET'])
def get_automation_history():
    """Get automation decision history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = automation_controller.get_decision_history(limit)
        return jsonify({
            'success': True,
            'data': {
                'history': history,
                'count': len(history)
            }
        })
    except Exception as e:
        logger.error(f"ERROR: Error getting automation history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/logs/sensors', methods=['GET'])
def get_sensor_logs():
    """Get sensor reading logs"""
    try:
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 1000, type=int)
        
        readings = data_logger.get_sensor_readings(hours=hours, limit=limit)
        
        return jsonify({
            'success': True,
            'data': {
                'readings': readings,
                'count': len(readings)
            }
        })
    except Exception as e:
        logger.error(f"ERROR: Error getting sensor logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/logs/actuators', methods=['GET'])
def get_actuator_logs():
    """Get actuator state history"""
    try:
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 500, type=int)
        
        history = data_logger.get_actuator_history(hours=hours, limit=limit)
        
        return jsonify({
            'success': True,
            'data': {
                'history': history,
                'count': len(history)
            }
        })
    except Exception as e:
        logger.error(f"ERROR: Error getting actuator logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/logs/ai-decisions', methods=['GET'])
def get_ai_decision_logs():
    """Get AI decision logs"""
    try:
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        decisions = data_logger.get_ai_decisions(hours=hours, limit=limit)
        
        return jsonify({
            'success': True,
            'data': {
                'decisions': decisions,
                'count': len(decisions)
            }
        })
    except Exception as e:
        logger.error(f"ERROR: Error getting AI decision logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/logs/alerts', methods=['GET'])
def get_alert_logs():
    """Get alert logs"""
    try:
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        alerts = data_logger.get_alerts(hours=hours, limit=limit)
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': alerts,
                'count': len(alerts)
            }
        })
    except Exception as e:
        logger.error(f"ERROR: Error getting alert logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/logs/statistics', methods=['GET'])
def get_statistics():
    """Get statistics"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        stats = data_logger.get_statistics(hours=hours)
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"ERROR: Error getting statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bluetooth/status', methods=['GET'])
def get_bluetooth_status():
    """Get Bluetooth status"""
    try:
        status = bluetooth_manager.get_status()
        tethering_status = bluetooth_tethering.get_tethering_status()
        
        return jsonify({
            'success': True,
            'data': {
                'bluetooth': status,
                'tethering': tethering_status
            }
        })
    except Exception as e:
        logger.error(f"Error getting Bluetooth status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bluetooth/diagnostics', methods=['GET'])
def bluetooth_diagnostics():
    """Run Bluetooth diagnostics"""
    try:
        # Get device name from config
        bt_config = config.get_bluetooth_config()
        device_name = bt_config['device_name']
        
        # Check system Bluetooth status
        from src.utils.bluetooth_setup import check_bluetooth_service
        service_running = check_bluetooth_service()
        
        # Run hciconfig to get adapter info
        hci_output = "Not available"
        try:
            result = subprocess.run(['hciconfig', '-a'], capture_output=True, text=True, check=False)
            hci_output = result.stdout
        except Exception as e:
            hci_output = f"Error: {e}"
        
        # Check if device is discoverable
        discoverable = False
        try:
            result = subprocess.run(['hciconfig', 'hci0', 'name'], capture_output=True, text=True, check=False)
            discoverable = 'piscan' in result.stdout.lower()
        except Exception:
            pass
        
        # Try to make it discoverable again
        try:
            subprocess.run(['sudo', 'hciconfig', 'hci0', 'piscan'], check=False)
            subprocess.run(['sudo', 'hciconfig', 'hci0', 'name', device_name], check=False)
        except Exception:
            pass
        
        # Get Bluetooth manager status
        manager_status = bluetooth_manager.get_status()
        
        # Attempt to fix any issues
        from src.utils.bluetooth_setup import setup_bluetooth
        fix_attempt = setup_bluetooth(device_name)
        
        return jsonify({
            'success': True,
            'data': {
                'service_running': service_running,
                'device_name': device_name,
                'discoverable': discoverable,
                'hciconfig_output': hci_output,
                'manager_status': manager_status,
                'fix_attempt': fix_attempt,
                'recommendations': [
                    "Restart the Bluetooth service with 'sudo systemctl restart bluetooth'",
                    "Make sure the device is discoverable with 'sudo hciconfig hci0 piscan'",
                    "Set the device name with 'sudo hciconfig hci0 name MASH-IoT-Device'",
                    "Check if other devices can see this device",
                    "Try restarting the IoT device"
                ]
            }
        })
    except Exception as e:
        logger.error(f"Error running Bluetooth diagnostics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bluetooth/tethering', methods=['POST'])
def control_bluetooth_tethering():
    """Start or stop Bluetooth tethering"""
    try:
        data = request.get_json()
        action = data.get('action', '').lower()
        
        if action == 'start':
            success = bluetooth_tethering.start_tethering()
            message = 'Bluetooth tethering started' if success else 'Failed to start tethering'
        elif action == 'stop':
            success = bluetooth_tethering.stop_tethering()
            message = 'Bluetooth tethering stopped' if success else 'Failed to stop tethering'
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid action. Use "start" or "stop"'
            }), 400
        
        return jsonify({
            'success': success,
            'data': {
                'action': action,
                'message': message,
                'status': bluetooth_tethering.get_status()
            }
        })
    except Exception as e:
        logger.error(f"ERROR: Error controlling Bluetooth tethering: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bluetooth/discoverable', methods=['POST'])
def set_bluetooth_discoverable():
    """Set Bluetooth discoverable mode"""
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        timeout = data.get('timeout', 180)
        
        # Use make_discoverable if enabled, otherwise we don't need to do anything
        # since there's no explicit method to disable discoverability
        success = bluetooth_manager.make_discoverable(timeout) if enabled else True
        message = f'Bluetooth discoverable {"enabled" if enabled else "disabled"}'
        
        return jsonify({
            'success': success,
            'data': {
                'discoverable': enabled,
                'timeout': timeout if enabled else 0,
                'message': message
            }
        })
    except Exception as e:
        logger.error(f"ERROR: Error setting Bluetooth discoverable: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'data': {
            'status': 'healthy',
            'serialConnected': ser is not None and ser.is_open if ser else False,
            'gpioAvailable': GPIO_AVAILABLE,
            'automationEnabled': automation_controller.is_enabled(),
            'bluetoothAvailable': bluetooth_manager.is_available(),
            'timestamp': datetime.now().isoformat()
        }
    })


# ========== Main ==========
if __name__ == '__main__':
    start_time = time.time()  # Track uptime
    
    logger.info("Starting MASH IoT Device Server")
    logger.info(f"Device ID: {DEVICE_ID}")
    logger.info(f"Device Name: {DEVICE_NAME}")
    logger.info(f"Configuration loaded from: config/device_config.yaml")
    
    # Connect to Backend and Firebase
    logger.info("Connecting to Backend and Firebase...")
    
    # Look up device in backend instead of registering
    if backend_client:
        try:
            logger.info("Looking up device in backend...")
            if backend_client.lookup_device():
                logger.info("Device found in backend successfully")
                
                # Check if device ID changed (backend returned a different device)
                if backend_client.device_id and backend_client.device_id != DEVICE_ID:
                    logger.warning(f"Using different device from backend: {backend_client.device_id} (original: {DEVICE_ID})")
                    DEVICE_ID = backend_client.device_id
                
                # Update device status to online
                # Format the timestamp in a way that's compatible with the backend
                # Use UTC time to avoid timezone issues
                current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                status_data = {
                    'status': 'ONLINE',
                    'lastSeen': current_time,
                    'firmware': '1.0.0',
                    'ipAddress': get_ip_address(),
                    'macAddress': get_mac_address()
                }
                logger.info(f"Using timestamp: {current_time}")
                
                try:
                    if backend_client.update_device_status('ONLINE', status_data):
                        logger.info("Device status updated to ONLINE")
                    else:
                        logger.warning("Failed to update device status")
                except Exception as e:
                    logger.error(f"Error updating device status: {e}")
            else:
                logger.error("ERROR: Device not registered in backend. Please register this device in the Admin Dashboard first.")
                logger.info("Continuing with limited functionality. Some features may not work properly.")
                # You could exit here if you want to prevent operation without backend registration
                # import sys
                # sys.exit(1)  # Uncomment to exit if device not registered
                
        except Exception as e:
            logger.error(f"Backend lookup error: {e}")
    
    # Connect to Firebase
    if firebase_client:
        try:
            if firebase_client.connect():
                logger.info("Connected to Firebase successfully")
                
                # Start listening for commands
                def handle_firebase_command(command_data):
                    logger.info(f"Firebase command received: {command_data}")
                    # Handle command based on type
                    command_type = command_data.get('type')
                    if command_type == 'set_mode':
                        mode = command_data.get('mode', 's')
                        send_command_to_arduino(mode)
                    elif command_type == 'set_actuator':
                        actuator = command_data.get('actuator')
                        state = command_data.get('state', False)
                        if actuator in actuator_states:
                            actuator_controller.set_actuator(actuator, state)
                            sync_actuator_states()
                
                firebase_client.listen_for_commands(handle_firebase_command)
                
                # Send initial device status
                sync_device_status()
                
            else:
                logger.warning("Failed to connect to Firebase")
                
        except Exception as e:
            logger.error(f"Firebase connection error: {e}")
    
    # Start periodic status sync (every 10 minutes)
    def periodic_status_sync():
        while True:
            try:
                sync_device_status()
                time.sleep(600)  # 10 minutes
            except Exception as e:
                logger.error(f"Error in periodic status sync: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    status_sync_thread = threading.Thread(target=periodic_status_sync, daemon=True)
    status_sync_thread.start()
    logger.info("Periodic status sync started (every 10 minutes)")
    
    # Initialize Bluetooth (if enabled in config)
    bt_config = config.get_bluetooth_config()
    if bt_config['enabled']:
        try:
            if bluetooth_manager.is_available():
                logger.info("Bluetooth is available")
                
                # Perform system-level Bluetooth setup
                logger.info(f"Setting up Bluetooth with device name: {bluetooth_device_name}")
                bt_setup_status = setup_bluetooth(bluetooth_device_name)
                
                if bt_setup_status['success']:
                    logger.info("System-level Bluetooth setup successful")
                else:
                    logger.warning(f"System-level Bluetooth setup issues: {bt_setup_status}")
                
                # Make device discoverable on startup if configured
                if bt_config['discoverable_on_startup']:
                    timeout = bt_config['discoverable_timeout']
                    bluetooth_manager.make_discoverable(timeout=timeout)
                    logger.info(f"Bluetooth set to discoverable mode ({timeout} seconds)")
                    
                    # For better visibility, also try to make it always discoverable at system level
                    logger.info("Setting Bluetooth to always discoverable at system level")
                    subprocess.run(['sudo', 'hciconfig', 'hci0', 'piscan'], check=False)
                
                # Auto-start tethering if configured
                if bt_config['tethering']['auto_start']:
                    logger.info("Auto-starting Bluetooth tethering...")
                    bluetooth_tethering.start_tethering()
            else:
                logger.warning("WARNING: Bluetooth not available on this system")
        except Exception as e:
            logger.error(f"ERROR: Failed to initialize Bluetooth: {e}")
    else:
        logger.info("Bluetooth is disabled in configuration")
    
    # Initialize serial connection
    if init_serial():
        # Start sensor data reading thread
        sensor_thread = threading.Thread(target=read_sensor_data, daemon=True)
        sensor_thread.start()
        logger.info("Sensor data reader started")
    else:
        logger.warning("WARNING: Running without Arduino connection")
    
    # Start rule-based automation thread
    automation_thread = threading.Thread(target=automation_loop, daemon=True)
    automation_thread.start()
    logger.info("Rule-based automation thread started")
    
    # Register signal handlers for graceful shutdown
    import signal
    
    def signal_handler(sig, frame):
        logger.info(f"\nReceived signal {sig}, shutting down...")
        mark_device_offline()
        actuator_controller.cleanup()
        if ser:
            ser.close()
        logger.info("Shutdown complete")
        import sys
        sys.exit(0)
    
    # Register handlers for SIGINT (Ctrl+C) and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start Flask server with configured settings
        api_config = config.get_api_config()
        logger.info(f"Starting HTTP server on {api_config['host']}:{api_config['port']}")
        app.run(
            host=api_config['host'],
            port=api_config['port'],
            debug=api_config['debug']
        )
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        mark_device_offline()
    finally:
        actuator_controller.cleanup()
        if ser:
            ser.close()
        logger.info("Shutdown complete")
