#!/usr/bin/env python3
"""
MASH IoT - AI Automation Engine
Lightweight decision engine for autonomous actuator control
Memory footprint: ~10-20MB (suitable for RPi3)
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AIAutomationEngine:
    """
    Lightweight AI automation engine for mushroom chamber control
    Uses pre-trained thresholds and rule-based decisions
    """
    
    def __init__(self, model_path: str = None):
        if model_path is None:
            # Use current directory's models folder
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, 'models', 'decision_model.json')
        self.model_path = model_path
        self.enabled = False
        self.thresholds = self._load_default_thresholds()
        self.decision_history = []
        self.max_history = 50  # Keep last 50 decisions
        
        # Load trained model if available
        self._load_model()
        
        logger.info("AI Automation Engine initialized")
    
    def _load_default_thresholds(self) -> Dict:
        """Default thresholds based on mushroom growing best practices"""
        return {
            # Spawning Phase (CO2 accumulation)
            'spawning_co2_min': 10000,  # 10,000 ppm minimum
            'spawning_co2_optimal': 12500,  # 12,500 ppm optimal
            'spawning_co2_max': 20000,  # 20,000 ppm maximum
            'spawning_temp_min': 21.0,
            'spawning_temp_max': 27.0,
            'spawning_humidity_min': 85.0,
            'spawning_humidity_max': 95.0,
            
            # Fruiting Phase (Fresh air exchange)
            'fruiting_co2_min': 300,
            'fruiting_co2_optimal': 600,
            'fruiting_co2_max': 1000,
            'fruiting_temp_min': 18.0,
            'fruiting_temp_max': 24.0,
            'fruiting_humidity_min': 85.0,
            'fruiting_humidity_max': 95.0,
            
            # Hysteresis to prevent oscillation
            'co2_hysteresis': 500,  # ppm
            'temp_hysteresis': 1.0,  # °C
            'humidity_hysteresis': 3.0,  # %
        }
    
    def _load_model(self):
        """Load pre-trained model from JSON"""
        try:
            with open(self.model_path, 'r') as f:
                model = json.load(f)
                
            # Update thresholds with trained values
            if 'thresholds' in model:
                self.thresholds.update(model['thresholds'])
                logger.info(f"Loaded trained model from {self.model_path}")
                logger.info(f"   Model version: {model.get('version', 'unknown')}")
                logger.info(f"   Trained date: {model.get('trained_date', 'unknown')}")
            
        except FileNotFoundError:
            logger.warning(f"WARNING: No trained model found at {self.model_path}")
            logger.info("   Using default thresholds")
        except Exception as e:
            logger.error(f"ERROR: Error loading model: {e}")
            logger.info("   Using default thresholds")
    
    def enable(self):
        """Enable AI automation"""
        self.enabled = True
        logger.info("AI Automation ENABLED")
    
    def disable(self):
        """Disable AI automation"""
        self.enabled = False
        logger.info("AI Automation DISABLED")
    
    def is_enabled(self) -> bool:
        """Check if automation is enabled"""
        return self.enabled
    
    def analyze_and_decide(self, sensor_data: Dict, actuator_states: Dict) -> Dict:
        """
        Analyze sensor data and decide actuator actions
        
        Args:
            sensor_data: Current sensor readings (co2, temperature, humidity, mode)
            actuator_states: Current actuator states
            
        Returns:
            Dict with recommended actions and reasoning
        """
        if not self.enabled:
            return {'enabled': False, 'actions': {}}
        
        mode = sensor_data.get('mode', 's')
        co2 = sensor_data.get('co2', 0)
        temp = sensor_data.get('temperature', 0.0)
        humidity = sensor_data.get('humidity', 0.0)
        
        # Initialize decision
        decision = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'Spawning' if mode == 's' else 'Fruiting',
            'sensor_data': {
                'co2': co2,
                'temperature': temp,
                'humidity': humidity
            },
            'actions': {},
            'reasoning': []
        }
        
        # Mode-specific decisions
        if mode == 's':
            self._decide_spawning_mode(co2, temp, humidity, actuator_states, decision)
        else:
            self._decide_fruiting_mode(co2, temp, humidity, actuator_states, decision)
        
        # Add to history
        self.decision_history.append(decision)
        if len(self.decision_history) > self.max_history:
            self.decision_history.pop(0)
        
        return decision
    
    def _decide_spawning_mode(self, co2: int, temp: float, humidity: float, 
                              current_states: Dict, decision: Dict):
        """Decision logic for spawning phase"""
        actions = {}
        reasoning = []
        
        # CO2 Management (want HIGH CO2 for spawning)
        if co2 < self.thresholds['spawning_co2_min']:
            # CO2 too low - turn OFF exhaust fan to accumulate
            if current_states.get('exhaust_fan', False):
                actions['exhaust_fan'] = False
                reasoning.append(f"CO2 too low ({co2}ppm < {self.thresholds['spawning_co2_min']}ppm) - stopping exhaust")
        
        elif co2 > self.thresholds['spawning_co2_max']:
            # CO2 dangerously high - brief ventilation
            if not current_states.get('exhaust_fan', False):
                actions['exhaust_fan'] = True
                reasoning.append(f"CO2 too high ({co2}ppm > {self.thresholds['spawning_co2_max']}ppm) - venting")
        
        else:
            # CO2 in acceptable range - keep exhaust OFF
            if current_states.get('exhaust_fan', False):
                actions['exhaust_fan'] = False
                reasoning.append(f"CO2 optimal ({co2}ppm) - maintaining accumulation")
        
        # Temperature Management
        if temp > self.thresholds['spawning_temp_max']:
            # Too hot - turn on blower fan for cooling
            if not current_states.get('blower_fan', False):
                actions['blower_fan'] = True
                reasoning.append(f"Temperature high ({temp}°C > {self.thresholds['spawning_temp_max']}°C) - cooling")
        
        elif temp < self.thresholds['spawning_temp_min']:
            # Too cold - turn off cooling
            if current_states.get('blower_fan', False):
                actions['blower_fan'] = False
                reasoning.append(f"Temperature low ({temp}°C < {self.thresholds['spawning_temp_min']}°C) - stop cooling")
        
        # Humidity Management
        if humidity < self.thresholds['spawning_humidity_min']:
            # Too dry - turn on humidifier
            if not current_states.get('humidifier', False):
                actions['humidifier'] = True
                reasoning.append(f"Humidity low ({humidity}% < {self.thresholds['spawning_humidity_min']}%) - humidifying")
        
        elif humidity > self.thresholds['spawning_humidity_max']:
            # Too humid - turn off humidifier
            if current_states.get('humidifier', False):
                actions['humidifier'] = False
                reasoning.append(f"Humidity high ({humidity}% > {self.thresholds['spawning_humidity_max']}%) - stop humidifying")
        
        decision['actions'] = actions
        decision['reasoning'] = reasoning
    
    def _decide_fruiting_mode(self, co2: int, temp: float, humidity: float,
                              current_states: Dict, decision: Dict):
        """Decision logic for fruiting phase"""
        actions = {}
        reasoning = []
        
        # CO2 Management (want LOW CO2 for fruiting)
        if co2 > self.thresholds['fruiting_co2_max']:
            # CO2 too high - turn ON exhaust fan
            if not current_states.get('exhaust_fan', False):
                actions['exhaust_fan'] = True
                reasoning.append(f"CO2 too high ({co2}ppm > {self.thresholds['fruiting_co2_max']}ppm) - venting")
        
        elif co2 < self.thresholds['fruiting_co2_min']:
            # CO2 too low - turn OFF exhaust fan
            if current_states.get('exhaust_fan', False):
                actions['exhaust_fan'] = False
                reasoning.append(f"CO2 too low ({co2}ppm < {self.thresholds['fruiting_co2_min']}ppm) - stop venting")
        
        else:
            # CO2 in optimal range
            if co2 > self.thresholds['fruiting_co2_optimal'] + self.thresholds['co2_hysteresis']:
                if not current_states.get('exhaust_fan', False):
                    actions['exhaust_fan'] = True
                    reasoning.append(f"CO2 above optimal ({co2}ppm) - gentle venting")
        
        # Temperature Management
        if temp > self.thresholds['fruiting_temp_max']:
            # Too hot - turn on blower fan
            if not current_states.get('blower_fan', False):
                actions['blower_fan'] = True
                reasoning.append(f"Temperature high ({temp}°C > {self.thresholds['fruiting_temp_max']}°C) - cooling")
        
        elif temp < self.thresholds['fruiting_temp_min']:
            # Too cold - turn off cooling
            if current_states.get('blower_fan', False):
                actions['blower_fan'] = False
                reasoning.append(f"Temperature low ({temp}°C < {self.thresholds['fruiting_temp_min']}°C) - stop cooling")
        
        # Humidity Management (critical for fruiting)
        if humidity < self.thresholds['fruiting_humidity_min']:
            # Too dry - turn on humidifier
            if not current_states.get('humidifier', False):
                actions['humidifier'] = True
                reasoning.append(f"Humidity low ({humidity}% < {self.thresholds['fruiting_humidity_min']}%) - humidifying")
        
        elif humidity > self.thresholds['fruiting_humidity_max']:
            # Too humid - turn off humidifier
            if current_states.get('humidifier', False):
                actions['humidifier'] = False
                reasoning.append(f"Humidity high ({humidity}% > {self.thresholds['fruiting_humidity_max']}%) - stop humidifying")
        
        decision['actions'] = actions
        decision['reasoning'] = reasoning
    
    def get_decision_history(self, limit: int = 10) -> list:
        """Get recent decision history"""
        return self.decision_history[-limit:]
    
    def get_status(self) -> Dict:
        """Get automation status"""
        return {
            'enabled': self.enabled,
            'model_loaded': self.model_path,
            'thresholds': self.thresholds,
            'decisions_made': len(self.decision_history),
            'last_decision': self.decision_history[-1] if self.decision_history else None
        }
