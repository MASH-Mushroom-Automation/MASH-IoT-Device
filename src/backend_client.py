"""
Backend Client for MASH IoT Device
Handles communication with MASH backend API
"""

import os
import requests
import logging
import time
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import threading


class BackendClient:
    """Manages communication with MASH backend"""
    
    def __init__(self,
                 api_url: str,
                 device_id: str,
                 api_key: Optional[str] = None,
                 timeout: int = 30,
                 mock_mode: bool = False):
        """
        Initialize Backend Client
        
        Args:
            api_url: Backend API base URL
            device_id: Unique device identifier
            api_key: API key for authentication
            timeout: Request timeout in seconds
            mock_mode: Run in simulation mode
        """
        self.logger = logging.getLogger(__name__)
        self.api_url = api_url.rstrip('/')
        self.device_id = device_id
        self.api_key = api_key
        self.timeout = timeout
        self.mock_mode = mock_mode
        
        # State
        self.is_registered = False
        self.registration_data = None
        self.last_sync_time = None
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'MASH-IoT-Device/{device_id}'
        })
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def register_device(self, 
                       user_id: str,
                       device_info: Dict[str, Any]) -> bool:
        """
        Register device with backend
        
        Args:
            user_id: User ID who owns the device
            device_info: Device information dictionary
            
        Returns:
            True if registration successful
        """
        if self.mock_mode:
            self.logger.info(f"Mock: Device registered with user {user_id}")
            self.is_registered = True
            return True
        
        try:
            self.logger.info(f"Registering device with backend: {self.device_id}")
            
            payload = {
                'userId': user_id,
                'serialNumber': self.device_id,
                'name': device_info.get('name', f'MASH Chamber {self.device_id[-6:]}'),
                'type': device_info.get('type', 'MUSHROOM_CHAMBER'),
                'location': device_info.get('location', 'Unknown'),
                'firmware': device_info.get('firmware', '1.0.0'),
                'ipAddress': device_info.get('ip_address'),
                'macAddress': device_info.get('mac_address'),
                'status': 'ONLINE',
                'isActive': True
            }
            
            response = self.session.post(
                f'{self.api_url}/devices',
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.is_registered = True
                self.registration_data = data
                self.logger.info("Device registered successfully")
                return True
            elif response.status_code == 409:
                # Device already registered
                self.logger.info("Device already registered, updating...")
                return self.update_device_status('ONLINE', device_info)
            else:
                self.logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error during registration: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error registering device: {e}")
            return False
    
    def update_device_status(self, 
                            status: str,
                            device_info: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update device status on backend
        
        Args:
            status: Device status (ONLINE, OFFLINE, MAINTENANCE, ERROR)
            device_info: Additional device information
            
        Returns:
            True if update successful
        """
        if self.mock_mode:
            self.logger.debug(f"Mock: Device status updated to {status}")
            return True
        
        try:
            payload = {
                'status': status,
                'lastSeen': datetime.now().isoformat()
            }
            
            if device_info:
                if 'ip_address' in device_info:
                    payload['ipAddress'] = device_info['ip_address']
                if 'firmware' in device_info:
                    payload['firmware'] = device_info['firmware']
            
            response = self.session.patch(
                f'{self.api_url}/devices/serial/{self.device_id}',
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Device status updated to {status}")
                return True
            else:
                self.logger.warning(f"Failed to update status: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating device status: {e}")
            return False
    
    def send_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """
        Send sensor data to backend
        
        Args:
            sensor_data: Sensor reading data
            
        Returns:
            True if data sent successfully
        """
        if self.mock_mode:
            return True
        
        try:
            # Get device ID from backend (if registered)
            if not self.registration_data:
                self.logger.warning("Device not registered, cannot send sensor data")
                return False
            
            backend_device_id = self.registration_data.get('id')
            
            payload = {
                'deviceId': backend_device_id,
                'sensorId': sensor_data.get('sensor_id'),
                'userId': self.registration_data.get('userId'),
                'type': sensor_data.get('type', 'environment'),
                'value': sensor_data.get('value', 0),
                'unit': sensor_data.get('unit', 'mixed'),
                'quality': sensor_data.get('quality'),
                'timestamp': sensor_data.get('timestamp', datetime.now().isoformat())
            }
            
            response = self.session.post(
                f'{self.api_url}/sensor-data',
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                self.logger.warning(f"Failed to send sensor data: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending sensor data: {e}")
            return False
    
    def send_sensor_data_batch(self, sensor_data_list: List[Dict[str, Any]]) -> bool:
        """
        Send batch of sensor data to backend
        
        Args:
            sensor_data_list: List of sensor readings
            
        Returns:
            True if batch sent successfully
        """
        if self.mock_mode:
            return True
        
        try:
            if not self.registration_data:
                return False
            
            backend_device_id = self.registration_data.get('id')
            user_id = self.registration_data.get('userId')
            
            payload = {
                'readings': [
                    {
                        'deviceId': backend_device_id,
                        'userId': user_id,
                        'type': reading.get('type', 'environment'),
                        'value': reading.get('value', 0),
                        'unit': reading.get('unit', 'mixed'),
                        'timestamp': reading.get('timestamp', datetime.now().isoformat())
                    }
                    for reading in sensor_data_list
                ]
            }
            
            response = self.session.post(
                f'{self.api_url}/sensor-data/batch',
                json=payload,
                timeout=self.timeout
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            self.logger.error(f"Error sending batch sensor data: {e}")
            return False
    
    def get_device_commands(self) -> List[Dict[str, Any]]:
        """
        Fetch pending commands from backend
        
        Returns:
            List of pending commands
        """
        if self.mock_mode:
            return []
        
        try:
            if not self.registration_data:
                return []
            
            backend_device_id = self.registration_data.get('id')
            
            response = self.session.get(
                f'{self.api_url}/device-commands/device/{backend_device_id}/pending',
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error fetching commands: {e}")
            return []
    
    def acknowledge_command(self, command_id: str, response_data: Any) -> bool:
        """
        Acknowledge command execution
        
        Args:
            command_id: Command ID to acknowledge
            response_data: Command response data
            
        Returns:
            True if acknowledgment successful
        """
        if self.mock_mode:
            return True
        
        try:
            payload = {
                'status': 'completed',
                'response': response_data,
                'acknowledgedAt': datetime.now().isoformat()
            }
            
            response = self.session.patch(
                f'{self.api_url}/device-commands/{command_id}',
                json=payload,
                timeout=self.timeout
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Error acknowledging command: {e}")
            return False
    
    def send_health_data(self, health_data: Dict[str, Any]) -> bool:
        """
        Send device health metrics to backend
        
        Args:
            health_data: Health metrics dictionary
            
        Returns:
            True if data sent successfully
        """
        if self.mock_mode:
            return True
        
        try:
            if not self.registration_data:
                return False
            
            backend_device_id = self.registration_data.get('id')
            
            payload = {
                'deviceId': backend_device_id,
                'status': health_data.get('status', 'HEALTHY'),
                'cpuUsage': health_data.get('cpu_usage'),
                'memoryUsage': health_data.get('memory_usage'),
                'diskUsage': health_data.get('disk_usage'),
                'temperature': health_data.get('temperature'),
                'networkLatency': health_data.get('network_latency'),
                'uptime': health_data.get('uptime'),
                'errorCount': health_data.get('error_count', 0),
                'metadata': health_data.get('metadata'),
                'timestamp': datetime.now().isoformat()
            }
            
            response = self.session.post(
                f'{self.api_url}/device-health',
                json=payload,
                timeout=self.timeout
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            self.logger.error(f"Error sending health data: {e}")
            return False
    
    def check_connection(self) -> bool:
        """
        Check if backend is reachable
        
        Returns:
            True if backend is reachable
        """
        if self.mock_mode:
            return True
        
        try:
            response = self.session.get(
                f'{self.api_url}/health',
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def close(self):
        """Close HTTP session"""
        if self.session:
            self.session.close()
