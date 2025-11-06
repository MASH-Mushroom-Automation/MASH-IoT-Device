#!/usr/bin/env python3
"""
MASH IoT Device - Integrated Server
Combines sensor reading, actuator control, and HTTP API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import serial
import time
import threading
from datetime import datetime
from collections import deque
import logging
from ai_automation import AIAutomationEngine
from data_logger import DataLogger

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("WARNING: RPi.GPIO not available, running in simulation mode")

# ========== Configuration ==========
# Device Identity
DEVICE_ID = 'MASH-A1-CAL25-AC2415'
DEVICE_NAME = 'Mushroom Prototype Chamber'

# Serial Configuration (Arduino)
SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUD = 9600

# GPIO Pin Configuration (BCM numbering)
RELAY_BLOWER_FAN = 22
RELAY_EXHAUST_FAN = 27
RELAY_HUMIDIFIER = 17
RELAY_LED_LIGHTS = 18

# Data collection
WINDOW_SIZE = 30
READING_HISTORY = deque(maxlen=WINDOW_SIZE)

# ========== Logging Setup ==========
logging.basicConfig(
    level=logging.INFO,
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

# Initialize AI automation engine
ai_engine = AIAutomationEngine()

# Initialize data logger
data_logger = DataLogger()


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


def ai_automation_loop():
    """AI automation loop - runs every 10 seconds"""
    logger.info("Starting AI automation loop...")
    
    while True:
        try:
            if ai_engine.is_enabled():
                with data_lock:
                    current_sensor_data = sensor_data.copy()
                    current_actuator_states = actuator_states.copy()
                
                # Get AI decision
                decision = ai_engine.analyze_and_decide(
                    current_sensor_data,
                    current_actuator_states
                )
                
                # Execute recommended actions
                if decision.get('actions'):
                    for actuator, state in decision['actions'].items():
                        if actuator in actuator_states:
                            actuator_controller.set_actuator(actuator, state)
                            logger.info(f"AI Action: {actuator} -> {'ON' if state else 'OFF'}")
                    
                    # Log actuator changes
                    data_logger.log_actuator_change(actuator_states, current_sensor_data.get('mode', 's'), 'ai')
                    
                    # Log reasoning
                    if decision.get('reasoning'):
                        for reason in decision['reasoning']:
                            logger.info(f"   Reasoning: {reason}")
                
                # Log AI decision
                data_logger.log_ai_decision(decision)
            
        except Exception as e:
            logger.error(f"ERROR: Error in AI automation loop: {e}")
        
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
    """Get AI automation status"""
    try:
        status = ai_engine.get_status()
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
    """Enable AI automation"""
    try:
        ai_engine.enable()
        return jsonify({
            'success': True,
            'data': {
                'enabled': True,
                'message': 'AI automation enabled'
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
    """Disable AI automation"""
    try:
        ai_engine.disable()
        return jsonify({
            'success': True,
            'data': {
                'enabled': False,
                'message': 'AI automation disabled'
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
    """Get AI decision history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = ai_engine.get_decision_history(limit)
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


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'data': {
            'status': 'healthy',
            'serialConnected': ser is not None and ser.is_open if ser else False,
            'gpioAvailable': GPIO_AVAILABLE,
            'aiAutomationEnabled': ai_engine.is_enabled(),
            'timestamp': datetime.now().isoformat()
        }
    })


# ========== Main ==========
if __name__ == '__main__':
    logger.info("Starting MASH IoT Device Server")
    logger.info(f"Device ID: {DEVICE_ID}")
    logger.info(f"Device Name: {DEVICE_NAME}")
    
    # Initialize serial connection
    if init_serial():
        # Start sensor data reading thread
        sensor_thread = threading.Thread(target=read_sensor_data, daemon=True)
        sensor_thread.start()
        logger.info("Sensor data reader started")
    else:
        logger.warning("WARNING: Running without Arduino connection")
    
    # Start AI automation thread
    ai_thread = threading.Thread(target=ai_automation_loop, daemon=True)
    ai_thread.start()
    logger.info("AI automation thread started")
    
    try:
        # Start Flask server
        logger.info("Starting HTTP server on port 5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    finally:
        actuator_controller.cleanup()
        if ser:
            ser.close()
        logger.info("Shutdown complete")
