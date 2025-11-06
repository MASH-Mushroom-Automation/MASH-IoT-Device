#!/usr/bin/env python3
"""
MASH IoT - Raspberry Pi Actuator Controller with ML Decision Engine
Receives sensor data from Arduino and controls actuators based on ML predictions
"""

import serial
import time
import logging
from datetime import datetime
from collections import deque
import json
import os

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("WARNING: RPi.GPIO not available, running in simulation mode")

# GPIO Pin Configuration (BCM numbering)
RELAY_EXHAUST_FAN = 27 
RELAY_INTAKE_FAN = 22
RELAY_HUMIDIFIER = 17 
RELAY_LED_LIGHTS = 18 

# Serial Configuration
SERIAL_PORT = '/dev/ttyACM0'  # Arduino Uno/Mega usually shows up as ttyACM0
SERIAL_BAUD = 9600

# Data collection settings
WINDOW_SIZE = 30  # Keep last 30 readings for trend analysis
READING_HISTORY = deque(maxlen=WINDOW_SIZE)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mash/MASH-IoT-Device/logs/actuator_control.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ActuatorController:
    """Controls relay-connected actuators"""
    
    def __init__(self, simulation_mode=False):
        self.simulation_mode = simulation_mode or not GPIO_AVAILABLE
        self.exhaust_fan_state = False
        self.intake_fan_state = False
        self.humidifier_state = False
        self.led_lights_state = False
        
        if not self.simulation_mode:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(RELAY_EXHAUST_FAN, GPIO.OUT)
            GPIO.setup(RELAY_INTAKE_FAN, GPIO.OUT)
            GPIO.setup(RELAY_HUMIDIFIER, GPIO.OUT)
            GPIO.setup(RELAY_LED_LIGHTS, GPIO.OUT)
            self._set_all_off()
            logger.info("GPIO initialized - actuators ready")
        else:
            logger.info("Running in SIMULATION mode - no GPIO control")
    
    def _set_all_off(self):
        """Turn off all actuators"""
        self.set_exhaust_fan(False)
        self.set_intake_fan(False)
        self.set_humidifier(False)
        self.set_led_lights(False)
    
    def set_exhaust_fan(self, state):
        """Control exhaust fan relay"""
        if self.exhaust_fan_state != state:
            self.exhaust_fan_state = state
            if not self.simulation_mode:
                GPIO.output(RELAY_EXHAUST_FAN, GPIO.HIGH if state else GPIO.LOW)
            logger.info(f"Exhaust Fan: {'ON' if state else 'OFF'}")
    
    def set_intake_fan(self, state):
        """Control intake fan relay"""
        if self.intake_fan_state != state:
            self.intake_fan_state = state
            if not self.simulation_mode:
                GPIO.output(RELAY_INTAKE_FAN, GPIO.HIGH if state else GPIO.LOW)
            logger.info(f"Intake Fan: {'ON' if state else 'OFF'}")
    
    def set_humidifier(self, state):
        """Control humidifier relay"""
        if self.humidifier_state != state:
            self.humidifier_state = state
            if not self.simulation_mode:
                GPIO.output(RELAY_HUMIDIFIER, GPIO.HIGH if state else GPIO.LOW)
            logger.info(f"Humidifier: {'ON' if state else 'OFF'}")
    
    def set_led_lights(self, state):
        """Control LED grow lights relay"""
        if self.led_lights_state != state:
            self.led_lights_state = state
            if not self.simulation_mode:
                GPIO.output(RELAY_LED_LIGHTS, GPIO.HIGH if state else GPIO.LOW)
            logger.info(f"LED Lights: {'ON' if state else 'OFF'}")
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if not self.simulation_mode:
            self._set_all_off()
            GPIO.cleanup()
            logger.info("GPIO cleanup complete")


class MLDecisionEngine:
    """
    Lightweight ML-based decision engine for actuator control
    Uses trend analysis and rule-based logic optimized for 1GB RAM
    """
    
    def __init__(self, model_path=None):
        self.model_path = model_path
        self.history = deque(maxlen=WINDOW_SIZE)
        
        # Thresholds (can be learned from data)
        self.spawning_co2_min = 10000
        self.fruiting_co2_min = 500
        self.fruiting_co2_max = 800
        self.temp_min = 18
        self.temp_max = 28
        self.humidity_min = 80
        self.humidity_max = 95
        
        # Load pre-trained model if available
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            logger.info("No pre-trained model found, using rule-based logic")
    
    def load_model(self, path):
        """Load pre-trained decision model (placeholder for future ML)"""
        try:
            with open(path, 'r') as f:
                config = json.load(f)
                # Update thresholds from trained model
                self.spawning_co2_min = config.get('spawning_co2_min', self.spawning_co2_min)
                self.fruiting_co2_min = config.get('fruiting_co2_min', self.fruiting_co2_min)
                self.fruiting_co2_max = config.get('fruiting_co2_max', self.fruiting_co2_max)
                logger.info(f"Model loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    def add_reading(self, reading):
        """Add sensor reading to history"""
        self.history.append(reading)
    
    def calculate_trend(self, key, window=10):
        """Calculate rate of change for a sensor value"""
        if len(self.history) < 2:
            return 0.0
        
        recent = list(self.history)[-window:]
        if len(recent) < 2:
            return 0.0
        
        values = [r[key] for r in recent if key in r]
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend (change per reading)
        return (values[-1] - values[0]) / len(values)
    
    def decide_actions(self, current_reading, mode):
        """
        Main decision logic: analyze trends and decide actuator states
        Returns dict with actuator commands
        """
        self.add_reading(current_reading)
        
        co2 = current_reading.get('co2', 0)
        temp = current_reading.get('temperature', 0)
        humidity = current_reading.get('humidity', 0)
        
        # Calculate trends
        co2_trend = self.calculate_trend('co2', window=10)
        temp_trend = self.calculate_trend('temperature', window=10)
        humidity_trend = self.calculate_trend('humidity', window=10)
        
        actions = {
            'exhaust_fan': False,
            'intake_fan': False,
            'humidifier': False,
            'led_lights': False,  # Default to OFF, controlled by mobile app
            'reason': []
        }
        
        # Decision logic based on mode
        if mode == 'SPAWNING':
            # Spawning: Need high CO2 (>10,000 ppm)
            if co2 < self.spawning_co2_min:
                # CO2 too low - turn off exhaust, turn on intake if dropping fast
                if co2_trend < -50:  # Dropping quickly
                    actions['intake_fan'] = True
                    actions['reason'].append('CO2 dropping rapidly in spawning mode')
            elif co2 > self.spawning_co2_min + 2000:
                # CO2 very high - maintain with minimal ventilation
                pass
        
        elif mode == 'FRUITING':
            # Fruiting: Need moderate CO2 (500-800 ppm)
            if co2 > self.fruiting_co2_max:
                # CO2 too high - exhaust needed
                if co2_trend > 20:  # Rising
                    actions['exhaust_fan'] = True
                    actions['intake_fan'] = True
                    actions['reason'].append('CO2 rising above fruiting range')
                elif co2 > self.fruiting_co2_max + 100:  # Significantly high
                    actions['exhaust_fan'] = True
                    actions['reason'].append('CO2 significantly above fruiting range')
            
            elif co2 < self.fruiting_co2_min:
                # CO2 too low - reduce ventilation
                actions['exhaust_fan'] = False
                actions['intake_fan'] = False
                actions['reason'].append('CO2 below fruiting range - reducing ventilation')
        
        # Temperature control (applies to both modes)
        if temp > self.temp_max:
            if temp_trend > 0.5:  # Rising
                actions['exhaust_fan'] = True
                actions['intake_fan'] = True
                actions['reason'].append('Temperature rising above threshold')
        
        # Humidity control
        if humidity < self.humidity_min:
            if humidity_trend < -1:  # Dropping
                actions['humidifier'] = True
                actions['reason'].append('Humidity dropping below minimum')
        elif humidity > self.humidity_max:
            actions['humidifier'] = False
            if not actions['exhaust_fan']:  # Don't override CO2 control
                actions['exhaust_fan'] = True
                actions['reason'].append('Humidity above maximum')
        
        # Log decision
        if actions['reason']:
            logger.info(f"Decision: {', '.join(actions['reason'])}")
            logger.info(f"  CO2: {co2} ppm (trend: {co2_trend:.1f})")
            logger.info(f"  Temp: {temp:.1f}°C (trend: {temp_trend:.2f})")
            logger.info(f"  Humidity: {humidity:.1f}% (trend: {humidity_trend:.2f})")
        
        return actions


class SerialReader:
    """Reads and parses data from Arduino"""
    
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud
        self.serial = None
        self.connect()
    
    def connect(self):
        """Establish serial connection"""
        try:
            self.serial = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2)  # Wait for Arduino reset
            logger.info(f"Connected to Arduino on {self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            raise
    
    def read_line(self):
        """Read and parse one line from Arduino"""
        try:
            if self.serial and self.serial.in_waiting:
                line = self.serial.readline().decode('utf-8').strip()
                return self.parse_line(line)
        except Exception as e:
            logger.error(f"Serial read error: {e}")
        return None
    
    def parse_line(self, line):
        """Parse Arduino data line"""
        if not line:
            return None
        
        parts = line.split(',')
        
        if parts[0] == 'SENSOR' and len(parts) >= 7:
            # Format: SENSOR,timestamp,co2,temp,humidity,mode,alert
            return {
                'type': 'SENSOR',
                'timestamp': int(parts[1]),
                'co2': int(parts[2]),
                'temperature': float(parts[3]),
                'humidity': float(parts[4]),
                'mode': parts[5],
                'alert': parts[6] == '1'
            }
        
        elif parts[0] == 'ALERT' and len(parts) >= 4:
            # Format: ALERT,timestamp,mode,co2
            return {
                'type': 'ALERT',
                'timestamp': int(parts[1]),
                'mode': parts[2],
                'co2': int(parts[3])
            }
        
        elif parts[0] == 'MODE' and len(parts) >= 2:
            # Format: MODE,mode_name
            return {
                'type': 'MODE',
                'mode': parts[1]
            }
        
        # Log other messages
        if not line.startswith('==='):
            logger.debug(f"Arduino: {line}")
        
        return None
    
    def close(self):
        """Close serial connection"""
        if self.serial:
            self.serial.close()
            logger.info("Serial connection closed")


def main():
    """Main control loop"""
    logger.info("=== MASH IoT Actuator Controller Starting ===")
    
    # Initialize components
    actuators = ActuatorController(simulation_mode=not GPIO_AVAILABLE)
    decision_engine = MLDecisionEngine(model_path='/home/mash/MASH-IoT-Device/models/decision_model.json')
    
    try:
        serial_reader = SerialReader(SERIAL_PORT, SERIAL_BAUD)
    except Exception as e:
        logger.error(f"Cannot start without Arduino connection: {e}")
        return
    
    current_mode = 'SPAWNING'
    last_decision_time = 0
    decision_interval = 5  # Make decisions every 5 seconds
    
    logger.info("Control loop started")
    
    try:
        while True:
            # Read from Arduino
            data = serial_reader.read_line()
            
            if data:
                if data['type'] == 'SENSOR':
                    # Process sensor reading
                    current_mode = data['mode']
                    
                    # Make decision at controlled intervals
                    current_time = time.time()
                    if current_time - last_decision_time >= decision_interval:
                        actions = decision_engine.decide_actions(data, current_mode)
                        
                        # Apply actuator commands
                        actuators.set_exhaust_fan(actions['exhaust_fan'])
                        actuators.set_intake_fan(actions['intake_fan'])
                        actuators.set_humidifier(actions['humidifier'])
                        # LED lights controlled separately by mobile app
                        
                        last_decision_time = current_time
                
                elif data['type'] == 'ALERT':
                    logger.warning(f"ALERT from Arduino: {data['mode']} mode, CO2={data['co2']} ppm")
                
                elif data['type'] == 'MODE':
                    current_mode = data['mode']
                    logger.info(f"Mode changed to: {current_mode}")
            
            time.sleep(0.1)  # Small delay to prevent CPU spinning
    
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        serial_reader.close()
        actuators.cleanup()
        logger.info("=== MASH IoT Actuator Controller Stopped ===")


if __name__ == '__main__':
    main()
