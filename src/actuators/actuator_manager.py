"""
Actuator Manager for MASH IoT Device
Manages relay-controlled actuators (fans, humidifier, lights)
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import threading

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


@dataclass
class ActuatorState:
    """State of all actuators"""
    exhaust_fan: bool = False
    intake_fan: bool = False
    humidifier: bool = False
    led_lights: bool = False
    last_update: Optional[str] = None
    mode: str = 'MANUAL'  # MANUAL or AUTO
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class ActuatorManager:
    """Manages all actuators for the MASH chamber"""
    
    # GPIO Pin Configuration (BCM numbering)
    PIN_EXHAUST_FAN = 27  # GPIO 27
    PIN_INTAKE_FAN = 22   # GPIO 22
    PIN_HUMIDIFIER = 17   # GPIO 17
    PIN_LED_LIGHTS = 18   # GPIO 18
    
    def __init__(self, mock_mode: bool = False):
        """
        Initialize Actuator Manager
        
        Args:
            mock_mode: Run in simulation mode without GPIO
        """
        self.logger = logging.getLogger(__name__)
        self.mock_mode = mock_mode or not GPIO_AVAILABLE
        
        # Current state
        self.state = ActuatorState()
        
        # Thread lock for state changes
        self.lock = threading.Lock()
        
        # Initialize GPIO if available
        if not self.mock_mode:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                
                # Setup GPIO pins as outputs
                GPIO.setup(self.PIN_EXHAUST_FAN, GPIO.OUT, initial=GPIO.LOW)
                GPIO.setup(self.PIN_INTAKE_FAN, GPIO.OUT, initial=GPIO.LOW)
                GPIO.setup(self.PIN_HUMIDIFIER, GPIO.OUT, initial=GPIO.LOW)
                GPIO.setup(self.PIN_LED_LIGHTS, GPIO.OUT, initial=GPIO.LOW)
                
                self.logger.info("GPIO initialized for actuator control")
            except Exception as e:
                self.logger.error(f"Failed to initialize GPIO: {e}")
                self.mock_mode = True
        
        if self.mock_mode:
            self.logger.info("Actuator Manager running in MOCK mode (no GPIO)")
    
    def set_exhaust_fan(self, state: bool) -> bool:
        """
        Control exhaust fan
        
        Args:
            state: True to turn ON, False to turn OFF
            
        Returns:
            True if successful
        """
        with self.lock:
            try:
                if self.state.exhaust_fan != state:
                    if not self.mock_mode:
                        GPIO.output(self.PIN_EXHAUST_FAN, GPIO.HIGH if state else GPIO.LOW)
                    
                    self.state.exhaust_fan = state
                    self.state.last_update = datetime.now().isoformat()
                    self.logger.info(f"Exhaust Fan: {'ON' if state else 'OFF'}")
                
                return True
            except Exception as e:
                self.logger.error(f"Error controlling exhaust fan: {e}")
                return False
    
    def set_intake_fan(self, state: bool) -> bool:
        """
        Control intake fan
        
        Args:
            state: True to turn ON, False to turn OFF
            
        Returns:
            True if successful
        """
        with self.lock:
            try:
                if self.state.intake_fan != state:
                    if not self.mock_mode:
                        GPIO.output(self.PIN_INTAKE_FAN, GPIO.HIGH if state else GPIO.LOW)
                    
                    self.state.intake_fan = state
                    self.state.last_update = datetime.now().isoformat()
                    self.logger.info(f"Intake Fan: {'ON' if state else 'OFF'}")
                
                return True
            except Exception as e:
                self.logger.error(f"Error controlling intake fan: {e}")
                return False
    
    def set_humidifier(self, state: bool) -> bool:
        """
        Control humidifier
        
        Args:
            state: True to turn ON, False to turn OFF
            
        Returns:
            True if successful
        """
        with self.lock:
            try:
                if self.state.humidifier != state:
                    if not self.mock_mode:
                        GPIO.output(self.PIN_HUMIDIFIER, GPIO.HIGH if state else GPIO.LOW)
                    
                    self.state.humidifier = state
                    self.state.last_update = datetime.now().isoformat()
                    self.logger.info(f"Humidifier: {'ON' if state else 'OFF'}")
                
                return True
            except Exception as e:
                self.logger.error(f"Error controlling humidifier: {e}")
                return False
    
    def set_led_lights(self, state: bool) -> bool:
        """
        Control LED grow lights
        
        Args:
            state: True to turn ON, False to turn OFF
            
        Returns:
            True if successful
        """
        with self.lock:
            try:
                if self.state.led_lights != state:
                    if not self.mock_mode:
                        GPIO.output(self.PIN_LED_LIGHTS, GPIO.HIGH if state else GPIO.LOW)
                    
                    self.state.led_lights = state
                    self.state.last_update = datetime.now().isoformat()
                    self.logger.info(f"LED Lights: {'ON' if state else 'OFF'}")
                
                return True
            except Exception as e:
                self.logger.error(f"Error controlling LED lights: {e}")
                return False
    
    def set_all(self, 
                exhaust_fan: Optional[bool] = None,
                intake_fan: Optional[bool] = None,
                humidifier: Optional[bool] = None,
                led_lights: Optional[bool] = None) -> bool:
        """
        Set multiple actuators at once
        
        Args:
            exhaust_fan: Exhaust fan state (None to skip)
            intake_fan: Intake fan state (None to skip)
            humidifier: Humidifier state (None to skip)
            led_lights: LED lights state (None to skip)
            
        Returns:
            True if all requested changes successful
        """
        success = True
        
        if exhaust_fan is not None:
            success = success and self.set_exhaust_fan(exhaust_fan)
        
        if intake_fan is not None:
            success = success and self.set_intake_fan(intake_fan)
        
        if humidifier is not None:
            success = success and self.set_humidifier(humidifier)
        
        if led_lights is not None:
            success = success and self.set_led_lights(led_lights)
        
        return success
    
    def turn_all_off(self) -> bool:
        """
        Turn off all actuators
        
        Returns:
            True if successful
        """
        self.logger.info("Turning off all actuators")
        return self.set_all(
            exhaust_fan=False,
            intake_fan=False,
            humidifier=False,
            led_lights=False
        )
    
    def get_state(self) -> ActuatorState:
        """
        Get current state of all actuators
        
        Returns:
            ActuatorState object
        """
        with self.lock:
            return ActuatorState(
                exhaust_fan=self.state.exhaust_fan,
                intake_fan=self.state.intake_fan,
                humidifier=self.state.humidifier,
                led_lights=self.state.led_lights,
                last_update=self.state.last_update,
                mode=self.state.mode
            )
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get state as dictionary"""
        return self.get_state().to_dict()
    
    def set_mode(self, mode: str) -> bool:
        """
        Set control mode
        
        Args:
            mode: Control mode (MANUAL or AUTO)
            
        Returns:
            True if successful
        """
        if mode not in ['MANUAL', 'AUTO']:
            self.logger.error(f"Invalid mode: {mode}")
            return False
        
        with self.lock:
            self.state.mode = mode
            self.logger.info(f"Control mode set to: {mode}")
        
        return True
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if not self.mock_mode:
            try:
                self.turn_all_off()
                GPIO.cleanup()
                self.logger.info("GPIO cleanup complete")
            except Exception as e:
                self.logger.error(f"Error during GPIO cleanup: {e}")
