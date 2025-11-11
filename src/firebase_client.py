"""
Firebase Client for MASH IoT Device
Handles real-time data sync with Firebase Realtime Database
"""

import os
import json
import logging
import time
import threading
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import requests


class FirebaseClient:
    """Manages real-time communication with Firebase"""
    
    def __init__(self,
                 project_id: str,
                 database_url: str,
                 service_account_email: str,
                 private_key: str,
                 device_id: str,
                 mock_mode: bool = False):
        """
        Initialize Firebase Client
        
        Args:
            project_id: Firebase project ID
            database_url: Firebase Realtime Database URL
            service_account_email: Service account email
            private_key: Service account private key
            device_id: Unique device identifier
            mock_mode: Run in simulation mode
        """
        self.logger = logging.getLogger(__name__)
        self.project_id = project_id
        self.database_url = database_url.rstrip('/')
        self.service_account_email = service_account_email
        self.private_key = private_key
        self.device_id = device_id
        self.mock_mode = mock_mode
        
        # State
        self.is_connected = False
        self.access_token = None
        self.token_expires_at = 0
        
        # Callbacks
        self.command_callback = None
        self.connection_callback = None
        
        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        
        if not mock_mode:
            self._authenticate()
    
    def _authenticate(self) -> bool:
        """Authenticate with Firebase using service account"""
        try:
            if self.mock_mode:
                self.logger.info("Mock: Firebase authentication successful")
                self.is_connected = True
                return True
            
            # For simplicity, we'll use the REST API with the database secret
            # In production, you should use proper OAuth2 authentication
            self.logger.info("Authenticating with Firebase...")
            
            # Test connection to database
            test_url = f"{self.database_url}/.json"
            self.logger.debug(f"Testing Firebase connection to: {test_url}")
            response = self.session.get(
                test_url,
                timeout=10
            )
            
            if response.status_code == 200:
                self.is_connected = True
                self.logger.info("Firebase connection successful")
                return True
            else:
                self.logger.error(f"Firebase authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Firebase authentication error: {e}")
            return False
    
    def connect(self) -> bool:
        """Connect to Firebase"""
        if self.mock_mode:
            self.is_connected = True
            self.logger.info("Mock: Connected to Firebase")
            return True
        
        return self._authenticate()
    
    def disconnect(self):
        """Disconnect from Firebase"""
        self.is_connected = False
        self.logger.info("Disconnected from Firebase")
    
    def send_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """
        Send sensor data to Firebase
        
        Args:
            sensor_data: Dictionary containing sensor readings
            
        Returns:
            True if data sent successfully
        """
        if self.mock_mode:
            self.logger.debug(f"Mock: Sent sensor data to Firebase: {sensor_data}")
            return True
        
        if not self.is_connected:
            self.logger.warning("Not connected to Firebase")
            return False
        
        try:
            # Prepare data with timestamp
            timestamp = datetime.now().isoformat()
            data = {
                **sensor_data,
                'deviceId': self.device_id,
                'timestamp': timestamp
            }
            
            # Send to Firebase Realtime Database
            path = f"/devices/{self.device_id}/sensorData"
            response = self.session.put(
                f"{self.database_url}{path}.json",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Sensor data sent to Firebase: {data}")
                return True
            else:
                self.logger.error(f"Failed to send sensor data: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending sensor data to Firebase: {e}")
            return False
    
    def send_device_status(self, status_data: Dict[str, Any]) -> bool:
        """
        Send device status to Firebase
        
        Args:
            status_data: Dictionary containing device status
            
        Returns:
            True if status sent successfully
        """
        if self.mock_mode:
            self.logger.debug(f"Mock: Sent device status to Firebase: {status_data}")
            return True
        
        if not self.is_connected:
            self.logger.warning("Not connected to Firebase")
            return False
        
        try:
            # Prepare status data
            timestamp = datetime.now().isoformat()
            data = {
                **status_data,
                'deviceId': self.device_id,
                'timestamp': timestamp,
                'lastSeen': timestamp
            }
            
            # Send to Firebase
            path = f"/devices/{self.device_id}/status"
            response = self.session.put(
                f"{self.database_url}{path}.json",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Device status sent to Firebase: {data}")
                return True
            else:
                self.logger.error(f"Failed to send device status: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending device status to Firebase: {e}")
            return False
    
    def send_actuator_states(self, actuator_states: Dict[str, bool]) -> bool:
        """
        Send actuator states to Firebase
        
        Args:
            actuator_states: Dictionary of actuator states
            
        Returns:
            True if states sent successfully
        """
        if self.mock_mode:
            self.logger.debug(f"Mock: Sent actuator states to Firebase: {actuator_states}")
            return True
        
        if not self.is_connected:
            return False
        
        try:
            data = {
                'actuators': actuator_states,
                'deviceId': self.device_id,
                'timestamp': datetime.now().isoformat()
            }
            
            path = f"/devices/{self.device_id}/actuators"
            response = self.session.put(
                f"{self.database_url}{path}.json",
                json=data,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Error sending actuator states to Firebase: {e}")
            return False
    
    def listen_for_commands(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Listen for commands from Firebase (simplified polling implementation)
        
        Args:
            callback: Function to call when command received
        """
        self.command_callback = callback
        
        if self.mock_mode:
            self.logger.info("Mock: Listening for commands from Firebase")
            return
        
        def command_listener():
            while self.is_connected:
                try:
                    # Poll for commands
                    path = f"/devices/{self.device_id}/commands"
                    response = self.session.get(
                        f"{self.database_url}{path}.json",
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        commands = response.json()
                        if commands:
                            for command_id, command_data in commands.items():
                                if command_data and not command_data.get('processed', False):
                                    self.logger.info(f"Received command from Firebase: {command_data}")
                                    if self.command_callback:
                                        self.command_callback(command_data)
                                    
                                    # Mark command as processed
                                    self.session.patch(
                                        f"{self.database_url}{path}/{command_id}.json",
                                        json={'processed': True, 'processedAt': datetime.now().isoformat()}
                                    )
                    
                    time.sleep(5)  # Poll every 5 seconds
                    
                except Exception as e:
                    self.logger.error(f"Error listening for commands: {e}")
                    time.sleep(10)  # Wait longer on error
        
        # Start command listener thread
        listener_thread = threading.Thread(target=command_listener, daemon=True)
        listener_thread.start()
        self.logger.info("Started listening for Firebase commands")
    
    def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Send alert to Firebase
        
        Args:
            alert_data: Alert information
            
        Returns:
            True if alert sent successfully
        """
        if self.mock_mode:
            self.logger.info(f"Mock: Sent alert to Firebase: {alert_data}")
            return True
        
        if not self.is_connected:
            return False
        
        try:
            timestamp = datetime.now().isoformat()
            data = {
                **alert_data,
                'deviceId': self.device_id,
                'timestamp': timestamp,
                'id': f"{self.device_id}_{int(time.time())}"
            }
            
            path = f"/alerts/{data['id']}"
            response = self.session.put(
                f"{self.database_url}{path}.json",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Alert sent to Firebase: {alert_data['message']}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error sending alert to Firebase: {e}")
            return False
    
    def get_device_config(self) -> Optional[Dict[str, Any]]:
        """
        Get device configuration from Firebase
        
        Returns:
            Device configuration dictionary or None
        """
        if self.mock_mode:
            return {
                'thresholds': {
                    'temperature': {'min': 18, 'max': 26},
                    'humidity': {'min': 80, 'max': 95},
                    'co2': {'min': 800, 'max': 1200}
                }
            }
        
        if not self.is_connected:
            return None
        
        try:
            path = f"/devices/{self.device_id}/config"
            response = self.session.get(
                f"{self.database_url}{path}.json",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting device config from Firebase: {e}")
            return None
