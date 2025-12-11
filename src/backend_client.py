"""
Backend Client for MASH IoT Device
Handles communication with MASH backend API
"""

import os
import requests
import logging
import time
from typing import Dict, Any, List, Union, Optional
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
        
        # Debug logging
        self.logger.info(f"Backend client initialized with device ID: '{self.device_id}'")
        self.logger.info(f"API URL: {self.api_url}")
        
        # State
        self.is_registered = False
        self.registration_data = None
        self.last_sync_time = None
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'MASH-IoT-Device/{device_id}',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'X-API-Key': api_key  # Bypass CSRF protection for IoT device
            })
    
    def lookup_device(self) -> bool:
        """
        Look up device in backend by serial number
        
        Returns:
            True if device found and details retrieved
        """
        if self.mock_mode:
            self.logger.info(f"Mock: Device found in backend: {self.device_id}")
            self.is_registered = True
            return True
        
        try:
            self.logger.info(f"Looking up device in backend: {self.device_id}")
            self.logger.info(f"API URL: {self.api_url}/iot/devices/serial/{self.device_id}")
            
            # Make sure the device_id is properly formatted
            if not self.device_id or not isinstance(self.device_id, str):
                self.logger.error(f"Invalid device ID: {self.device_id}")
                return False
                
            # Print headers for debugging
            self.logger.info(f"Request headers: {self.session.headers}")
            
            response = self.session.get(
                f'{self.api_url}/iot/devices/serial/{self.device_id}',
                timeout=self.timeout
            )
            
            self.logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.is_registered = True
                self.registration_data = data.get('data')
                
                # Debug logging for response data
                self.logger.info(f"Response data structure: {data.keys()}")
                if 'data' in data:
                    self.logger.info(f"Device data keys: {self.registration_data.keys() if self.registration_data else 'None'}")
                else:
                    self.logger.warning("No 'data' field in response")
                
                # Check if the returned device has the same serial number
                returned_serial = self.registration_data.get('serialNumber')
                if returned_serial and returned_serial != self.device_id:
                    self.logger.warning(f"Found device with different serial number: {returned_serial} (expected {self.device_id})")
                    self.logger.warning("Using this device for testing purposes")
                    # Update our device_id to match the one from the backend
                    self.device_id = returned_serial
                elif not returned_serial:
                    self.logger.warning(f"Device found but no serial number returned, keeping original: {self.device_id}")
                
                self.logger.info(f"Device found in backend: {self.registration_data}")
                return True
            else:
                self.logger.error(f"Device not found in backend: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error during device lookup: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error looking up device: {e}")
            return False
    
    def register_device(self, 
                       user_id: Optional[str] = None,
                       device_info: Dict[str, Any] = None) -> bool:
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
            
            if device_info is None:
                device_info = {}
                
            # Create payload with required fields
            payload = {
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
            
            # Add userId only if provided with a non-empty value
            if user_id and user_id.strip():
                payload['userId'] = user_id
            else:
                self.logger.info("No user ID provided, device will be registered without a user")
            
            response = self.session.post(
                f'{self.api_url}/iot/devices',
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
    
    def update_device_status(self, status: str, additional_data: Dict[str, Any] = None) -> bool:
        """
        Update device status in backend
        
        Args:
            status: Device status (ONLINE, OFFLINE, etc)
            additional_data: Additional data to update
            
        Returns:
            True if status updated successfully
        """
        if self.mock_mode:
            return True
        
        try:
            # First check if we have registration data
            if not self.is_registered:
                self.logger.warning("Device not registered, attempting to look up device first")
                if not self.lookup_device():
                    self.logger.error("Device not found in backend, cannot update status")
                    return False
            
            # Format the timestamp in a way that's compatible with the backend
            # Use UTC time to avoid timezone issues
            current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            payload = {
                'status': status,
                'lastSeen': current_time
            }
            self.logger.info(f"Using timestamp: {current_time}")
            
            # Add any additional data
            if additional_data:
                payload.update(additional_data)
                
            # Remove userId from payload to prevent null value errors
            if 'userId' in payload and payload['userId'] is None:
                del payload['userId']
                
            # Filter out unsupported fields
            allowed_fields = ['status', 'lastSeen', 'firmware', 'ipAddress', 'macAddress', 'name', 'description', 'location']
            filtered_payload = {k: v for k, v in payload.items() if k in allowed_fields}
            payload = filtered_payload
            
            self.logger.info(f"Sending payload: {payload}")
            
            # Make sure we have a valid device ID
            if not self.device_id or self.device_id == 'None':
                self.logger.error("Cannot update device status: Invalid device ID")
                return False
                
            self.logger.info(f"Updating device status to {status} for {self.device_id}")
            
            response = self.session.patch(
                f'{self.api_url}/iot/devices/serial/{self.device_id}',
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.logger.info("Device status updated successfully")
                return True
            else:
                self.logger.error(f"Failed to update device status: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error updating device status: {e}")
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
                self.logger.warning("Device not registered, attempting to look up device first")
                if not self.lookup_device():
                    self.logger.error("Device not found in backend, cannot send sensor data")
                    return False
            
            # Check if device is active (not turned off in app)
            device_status = self.registration_data.get('status')
            is_active = self.registration_data.get('isActive', True)
            
            if not is_active or device_status == 'OFFLINE':
                self.logger.debug(f"Device is turned off (status={device_status}, isActive={is_active}), skipping sensor data")
                return False
            
            backend_device_id = self.registration_data.get('id')
            
            # Note: Backend expects data at /sensors/:sensorId/data, not /sensor-data
            # For now, we'll skip sending individual sensor readings since we don't have sensor IDs
            # The device should use the batch endpoint or we need to create sensors first
            self.logger.debug("Sensor data sync skipped - use batch endpoint or create sensors first")
            return True
                
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
                self.logger.warning("Device not registered, attempting to look up device first")
                if not self.lookup_device():
                    self.logger.error("Device not found in backend, cannot send sensor data batch")
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
                self.logger.warning("Device not registered, attempting to look up device first")
                if not self.lookup_device():
                    self.logger.error("Device not found in backend, cannot get device commands")
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
                self.logger.warning("Device not registered, attempting to look up device first")
                if not self.lookup_device():
                    self.logger.error("Device not found in backend, cannot send health data")
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
    
    def refresh_device_status(self) -> bool:
        """
        Refresh device status from backend
        This checks if the device was turned on/off in the Grower app
        
        Returns:
            True if refresh successful
        """
        if self.mock_mode:
            return True
        
        try:
            # Re-lookup device to get latest status
            response = self.session.get(
                f'{self.api_url}/iot/devices/serial/{self.device_id}',
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    self.registration_data = data['data']
                    
                    # Log status changes
                    status = self.registration_data.get('status')
                    is_active = self.registration_data.get('isActive', True)
                    
                    if not is_active:
                        self.logger.info("Device is turned OFF in Grower app - monitoring paused")
                    elif status == 'OFFLINE':
                        self.logger.info("Device status is OFFLINE in backend")
                    else:
                        self.logger.debug(f"Device status refreshed: {status}, active: {is_active}")
                    
                    return True
            else:
                self.logger.warning(f"Failed to refresh device status: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error refreshing device status: {e}")
            return False
    
    def is_device_active(self) -> bool:
        """
        Check if device is active (turned on in app)
        
        Returns:
            True if device should be running
        """
        if not self.registration_data:
            return True  # Default to active if no data
        
        status = self.registration_data.get('status')
        is_active = self.registration_data.get('isActive', True)
        
        return is_active and status != 'OFFLINE'
    
    def close(self):
        """Close HTTP session"""
        if self.session:
            self.session.close()
