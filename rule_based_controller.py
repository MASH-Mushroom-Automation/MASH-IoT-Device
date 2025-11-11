#!/usr/bin/env python3
"""
MASH IoT - Rule-Based Automation Controller
Mathematical threshold-based decision engine for autonomous actuator control
Memory footprint: ~5-10MB (suitable for RPi3)
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RuleBasedController:
    """
    Rule-based automation controller for mushroom chamber management
    Uses mathematical thresholds and decision logic based on mushroom cultivation science
    
    Control Strategy:
    - Spawning Phase: High CO2 (10,000-20,000 ppm), Temp 21-27C, Humidity 85-95%
    - Fruiting Phase: Low CO2 (300-1,000 ppm), Temp 18-24C, Humidity 85-95%
    - Hysteresis prevents rapid oscillation of actuators
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the rule-based controller
        
        Args:
            config_path: Optional path to custom threshold configuration JSON
        """
        self.config_path = config_path
        self.enabled = False
        self.thresholds = self._load_default_thresholds()
        self.decision_history = []
        self.max_history = 50  # Keep last 50 decisions
        
        # Load custom configuration if available
        if config_path:
            self._load_custom_config()
        
        logger.info("Rule-Based Controller initialized with mathematical thresholds")
    
    def _load_default_thresholds(self) -> Dict:
        """
        Default thresholds based on mushroom growing science and best practices
        
        References:
        - Spawning phase requires high CO2 for mycelial growth
        - Fruiting phase requires fresh air exchange for primordia formation
        - Oyster mushroom optimal conditions (can be adjusted for other species)
        """
        return {
            # Spawning Phase Thresholds (CO2 accumulation phase)
            'spawning_co2_min': 10000,      # 10,000 ppm minimum
            'spawning_co2_optimal': 12500,  # 12,500 ppm optimal
            'spawning_co2_max': 20000,      # 20,000 ppm maximum (safety limit)
            'spawning_temp_min': 21.0,      # 21C minimum
            'spawning_temp_max': 27.0,      # 27C maximum
            'spawning_humidity_min': 85.0,  # 85% minimum
            'spawning_humidity_max': 95.0,  # 95% maximum
            
            # Fruiting Phase Thresholds (Fresh air exchange phase)
            'fruiting_co2_min': 300,        # 300 ppm minimum (ambient air level)
            'fruiting_co2_optimal': 600,    # 600 ppm optimal
            'fruiting_co2_max': 1000,       # 1,000 ppm maximum
            'fruiting_temp_min': 18.0,      # 18C minimum
            'fruiting_temp_max': 24.0,      # 24C maximum
            'fruiting_humidity_min': 85.0,  # 85% minimum
            'fruiting_humidity_max': 95.0,  # 95% maximum
            
            # Hysteresis buffers (prevent rapid on/off cycling)
            'co2_hysteresis': 500,          # 500 ppm buffer
            'temp_hysteresis': 1.0,         # 1C buffer
            'humidity_hysteresis': 3.0,     # 3% buffer
        }
    
    def _load_custom_config(self):
        """Load custom threshold configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Update thresholds with custom values
            if 'thresholds' in config:
                self.thresholds.update(config['thresholds'])
                logger.info(f"Loaded custom configuration from {self.config_path}")
                logger.info(f"   Configuration version: {config.get('version', 'unknown')}")
                logger.info(f"   Last updated: {config.get('updated_date', 'unknown')}")
            
        except FileNotFoundError:
            logger.info(f"No custom configuration found at {self.config_path}")
            logger.info("   Using default thresholds")
        except Exception as e:
            logger.error(f"Error loading custom configuration: {e}")
            logger.info("   Using default thresholds")
    
    def enable(self):
        """Enable automated control"""
        self.enabled = True
        logger.info("Rule-Based Automation ENABLED")
    
    def disable(self):
        """Disable automated control"""
        self.enabled = False
        logger.info("Rule-Based Automation DISABLED")
    
    def is_enabled(self) -> bool:
        """Check if automation is enabled"""
        return self.enabled
    
    def analyze_and_decide(self, sensor_data: Dict, actuator_states: Dict) -> Dict:
        """
        Analyze sensor data and decide actuator actions using mathematical rules
        
        Decision Logic:
        1. Determine current growth phase (spawning vs fruiting)
        2. Apply phase-specific threshold comparisons
        3. Calculate required actuator states
        4. Apply hysteresis to prevent oscillation
        
        Args:
            sensor_data: Current sensor readings {co2, temperature, humidity, mode}
            actuator_states: Current actuator states {exhaust_fan, blower_fan, humidifier, etc.}
            
        Returns:
            Dict with recommended actions and mathematical reasoning
        """
        if not self.enabled:
            return {'enabled': False, 'actions': {}}
        
        # Extract sensor values
        mode = sensor_data.get('mode', 's')
        co2 = sensor_data.get('co2', 0)
        temp = sensor_data.get('temperature', 0.0)
        humidity = sensor_data.get('humidity', 0.0)
        
        # Initialize decision structure
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
        
        # Apply mode-specific control logic
        if mode == 's':
            self._apply_spawning_rules(co2, temp, humidity, actuator_states, decision)
        else:
            self._apply_fruiting_rules(co2, temp, humidity, actuator_states, decision)
        
        # Store decision in history
        self.decision_history.append(decision)
        if len(self.decision_history) > self.max_history:
            self.decision_history.pop(0)
        
        return decision
    
    def _apply_spawning_rules(self, co2: int, temp: float, humidity: float, 
                              current_states: Dict, decision: Dict):
        """
        Apply mathematical rules for spawning phase
        
        Spawning Strategy:
        - Maintain high CO2 levels (10,000-20,000 ppm) for mycelial growth
        - Keep exhaust fan OFF to accumulate CO2 from mushroom respiration
        - Only ventilate if CO2 exceeds safety threshold (20,000 ppm)
        """
        actions = {}
        reasoning = []
        
        # CO2 Control Logic for Spawning
        if co2 < self.thresholds['spawning_co2_min']:
            # CO2 below minimum - ensure no ventilation
            if current_states.get('exhaust_fan', False):
                actions['exhaust_fan'] = False
                reasoning.append(
                    f"CO2 too low ({co2} ppm < {self.thresholds['spawning_co2_min']} ppm) - "
                    f"stopping exhaust to accumulate CO2"
                )
        
        elif co2 > self.thresholds['spawning_co2_max']:
            # CO2 above safety maximum - ventilate
            if not current_states.get('exhaust_fan', False):
                actions['exhaust_fan'] = True
                reasoning.append(
                    f"CO2 critical high ({co2} ppm > {self.thresholds['spawning_co2_max']} ppm) - "
                    f"activating exhaust for safety"
                )
        
        else:
            # CO2 in acceptable range - maintain accumulation
            if current_states.get('exhaust_fan', False):
                actions['exhaust_fan'] = False
                reasoning.append(
                    f"CO2 optimal ({co2} ppm) - maintaining accumulation mode"
                )
        
        # Temperature Control Logic
        if temp > self.thresholds['spawning_temp_max']:
            # Temperature too high - activate cooling
            if not current_states.get('blower_fan', False):
                actions['blower_fan'] = True
                reasoning.append(
                    f"Temperature high ({temp}C > {self.thresholds['spawning_temp_max']}C) - "
                    f"activating cooling fan"
                )
        
        elif temp < self.thresholds['spawning_temp_min']:
            # Temperature too low - stop cooling
            if current_states.get('blower_fan', False):
                actions['blower_fan'] = False
                reasoning.append(
                    f"Temperature low ({temp}C < {self.thresholds['spawning_temp_min']}C) - "
                    f"deactivating cooling fan"
                )
        
        # Humidity Control Logic
        if humidity < self.thresholds['spawning_humidity_min']:
            # Humidity too low - activate humidifier
            if not current_states.get('humidifier', False):
                actions['humidifier'] = True
                reasoning.append(
                    f"Humidity low ({humidity}% < {self.thresholds['spawning_humidity_min']}%) - "
                    f"activating humidifier"
                )
        
        elif humidity > self.thresholds['spawning_humidity_max']:
            # Humidity too high - deactivate humidifier
            if current_states.get('humidifier', False):
                actions['humidifier'] = False
                reasoning.append(
                    f"Humidity high ({humidity}% > {self.thresholds['spawning_humidity_max']}%) - "
                    f"deactivating humidifier"
                )
        
        decision['actions'] = actions
        decision['reasoning'] = reasoning
    
    def _apply_fruiting_rules(self, co2: int, temp: float, humidity: float,
                              current_states: Dict, decision: Dict):
        """
        Apply mathematical rules for fruiting phase
        
        Fruiting Strategy:
        - Maintain low CO2 levels (300-1,000 ppm) for primordia formation
        - Active fresh air exchange via exhaust fan
        - Higher ventilation promotes pinning and fruiting body development
        """
        actions = {}
        reasoning = []
        
        # CO2 Control Logic for Fruiting
        if co2 > self.thresholds['fruiting_co2_max']:
            # CO2 above maximum - activate ventilation
            if not current_states.get('exhaust_fan', False):
                actions['exhaust_fan'] = True
                reasoning.append(
                    f"CO2 high ({co2} ppm > {self.thresholds['fruiting_co2_max']} ppm) - "
                    f"activating fresh air exchange"
                )
        
        elif co2 < self.thresholds['fruiting_co2_min']:
            # CO2 below minimum - reduce ventilation
            if current_states.get('exhaust_fan', False):
                actions['exhaust_fan'] = False
                reasoning.append(
                    f"CO2 low ({co2} ppm < {self.thresholds['fruiting_co2_min']} ppm) - "
                    f"reducing ventilation"
                )
        
        else:
            # CO2 in range - apply hysteresis
            optimal_high = self.thresholds['fruiting_co2_optimal'] + self.thresholds['co2_hysteresis']
            if co2 > optimal_high and not current_states.get('exhaust_fan', False):
                actions['exhaust_fan'] = True
                reasoning.append(
                    f"CO2 above optimal ({co2} ppm) - initiating ventilation cycle"
                )
        
        # Temperature Control Logic
        if temp > self.thresholds['fruiting_temp_max']:
            # Temperature too high - activate cooling
            if not current_states.get('blower_fan', False):
                actions['blower_fan'] = True
                reasoning.append(
                    f"Temperature high ({temp}C > {self.thresholds['fruiting_temp_max']}C) - "
                    f"activating cooling fan"
                )
        
        elif temp < self.thresholds['fruiting_temp_min']:
            # Temperature too low - stop cooling
            if current_states.get('blower_fan', False):
                actions['blower_fan'] = False
                reasoning.append(
                    f"Temperature low ({temp}C < {self.thresholds['fruiting_temp_min']}C) - "
                    f"deactivating cooling fan"
                )
        
        # Humidity Control Logic (critical for fruiting)
        if humidity < self.thresholds['fruiting_humidity_min']:
            # Humidity too low - activate humidifier
            if not current_states.get('humidifier', False):
                actions['humidifier'] = True
                reasoning.append(
                    f"Humidity low ({humidity}% < {self.thresholds['fruiting_humidity_min']}%) - "
                    f"activating humidifier"
                )
        
        elif humidity > self.thresholds['fruiting_humidity_max']:
            # Humidity too high - deactivate humidifier
            if current_states.get('humidifier', False):
                actions['humidifier'] = False
                reasoning.append(
                    f"Humidity high ({humidity}% > {self.thresholds['fruiting_humidity_max']}%) - "
                    f"deactivating humidifier"
                )
        
        decision['actions'] = actions
        decision['reasoning'] = reasoning
    
    def get_decision_history(self, limit: int = 10) -> list:
        """Get recent decision history"""
        return self.decision_history[-limit:]
    
    def get_status(self) -> Dict:
        """Get controller status and configuration"""
        return {
            'enabled': self.enabled,
            'controller_type': 'rule_based_mathematical',
            'config_loaded': self.config_path if self.config_path else 'default',
            'thresholds': self.thresholds,
            'decisions_made': len(self.decision_history),
            'last_decision': self.decision_history[-1] if self.decision_history else None
        }
    
    def update_threshold(self, key: str, value: float):
        """
        Update a specific threshold value dynamically
        
        Args:
            key: Threshold parameter name
            value: New threshold value
        """
        if key in self.thresholds:
            old_value = self.thresholds[key]
            self.thresholds[key] = value
            logger.info(f"Updated threshold {key}: {old_value} -> {value}")
        else:
            logger.warning(f"Unknown threshold key: {key}")
    
    def save_config(self, output_path: str):
        """Save current threshold configuration to JSON file"""
        config = {
            'version': '1.0',
            'updated_date': datetime.now().isoformat(),
            'controller_type': 'rule_based_mathematical',
            'thresholds': self.thresholds
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Configuration saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")


# Maintain backward compatibility
AIAutomationEngine = RuleBasedController
