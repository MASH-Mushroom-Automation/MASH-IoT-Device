"""
MASH Touchscreen UI - API Client
Communicates with the Flask backend (integrated_server.py)
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class MASHApiClient:
    """Client for communicating with MASH Flask backend API"""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        """
        Initialize API client
        
        Args:
            base_url: Base URL for API (defaults to config.API_BASE_URL)
            timeout: Request timeout in seconds (defaults to config.API_TIMEOUT)
        """
        self.base_url = base_url or config.API_BASE_URL
        self.timeout = timeout or config.API_TIMEOUT
        self.session = requests.Session()
        
        logger.info(f"API Client initialized: {self.base_url}")
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/status')
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data or None on error
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {method} {url}")
            return None
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: {method} {url}")
            return None
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {method} {url} - {e}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error: {method} {url} - {e}")
            return None
    
    # ========== Status Endpoints ==========
    
    def get_status(self) -> Optional[Dict]:
        """
        Get device status
        
        Returns:
            {
                'device_id': str,
                'status': str,
                'mode': str,
                'automation_enabled': bool,
                'uptime': int
            }
        """
        return self._request('GET', '/status')
    
    def health_check(self) -> bool:
        """
        Check if API is healthy/reachable
        
        Returns:
            True if API is healthy, False otherwise
        """
        result = self._request('GET', '/health')
        return result is not None and result.get('status') == 'healthy'
    
    # ========== Sensor Data Endpoints ==========
    
    def get_current_sensor_data(self) -> Optional[Dict]:
        """
        Get current sensor readings
        
        Returns:
            {
                'co2': float,
                'temperature': float,
                'humidity': float,
                'mode': str,
                'alert': bool,
                'timestamp': str
            }
        """
        return self._request('GET', '/sensor/current')
    
    def get_sensor_history(self, hours: int = 1) -> Optional[List[Dict]]:
        """
        Get sensor data history
        
        Args:
            hours: Number of hours of history to retrieve
            
        Returns:
            List of sensor readings
        """
        return self._request('GET', f'/sensor/history?hours={hours}')
    
    # ========== Mode Control ==========
    
    def set_mode(self, mode: str) -> Optional[Dict]:
        """
        Set growth mode (spawning or fruiting)
        
        Args:
            mode: 's' for spawning, 'f' for fruiting
            
        Returns:
            Updated mode information
        """
        return self._request('POST', '/mode', json={'mode': mode})
    
    # ========== Actuator Control ==========
    
    def get_actuator_states(self) -> Optional[Dict]:
        """
        Get current actuator states
        
        Returns:
            {
                'blower_fan': bool,
                'exhaust_fan': bool,
                'humidifier': bool,
                'led_lights': bool
            }
        """
        return self._request('GET', '/actuators')
    
    def control_actuator(self, actuator: str, state: bool) -> Optional[Dict]:
        """
        Control a specific actuator
        
        Args:
            actuator: Actuator name (blower_fan, exhaust_fan, humidifier, led_lights)
            state: True to turn on, False to turn off
            
        Returns:
            Updated actuator state
        """
        return self._request('POST', '/actuator', json={
            'actuator': actuator,
            'state': state
        })
    
    # ========== Automation Control ==========
    
    def get_automation_status(self) -> Optional[Dict]:
        """
        Get automation system status
        
        Returns:
            {
                'enabled': bool,
                'current_mode': str,
                'rules_active': int,
                'last_action': str
            }
        """
        return self._request('GET', '/automation/status')
    
    def enable_automation(self) -> Optional[Dict]:
        """Enable rule-based automation"""
        return self._request('POST', '/automation/enable')
    
    def disable_automation(self) -> Optional[Dict]:
        """Disable rule-based automation"""
        return self._request('POST', '/automation/disable')
    
    def get_automation_history(self, hours: int = 24) -> Optional[List[Dict]]:
        """
        Get automation action history
        
        Args:
            hours: Number of hours of history
            
        Returns:
            List of automation actions
        """
        return self._request('GET', f'/automation/history?hours={hours}')
    
    # ========== WiFi Configuration ==========
    
    def wifi_scan(self) -> Optional[List[Dict]]:
        """
        Scan for available WiFi networks
        
        Returns:
            List of WiFi networks with SSID, signal strength, security
        """
        return self._request('GET', '/wifi/scan')
    
    def wifi_connect(self, ssid: str, password: str) -> Optional[Dict]:
        """
        Connect to WiFi network
        
        Args:
            ssid: Network SSID
            password: Network password
            
        Returns:
            Connection status
        """
        return self._request('POST', '/wifi/connect', json={
            'ssid': ssid,
            'password': password
        })
    
    def wifi_status(self) -> Optional[Dict]:
        """
        Get current WiFi connection status
        
        Returns:
            {
                'connected': bool,
                'ssid': str,
                'ip_address': str,
                'signal_strength': int
            }
        """
        return self._request('GET', '/wifi/status')
    
    def get_wifi_status(self) -> Optional[Dict]:
        """
        Get current WiFi connection status (alias for wifi_status)
        
        Returns:
            {
                'connected': bool,
                'ssid': str,
                'ip_address': str,
                'signal_strength': int
            }
        """
        return self.wifi_status()
    
    def scan_wifi(self) -> Optional[List[Dict]]:
        """
        Scan for available WiFi networks (alias for wifi_scan)
        
        Returns:
            List of WiFi networks with SSID, signal strength, security
        """
        return self.wifi_scan()
    
    def connect_wifi(self, ssid: str, password: str) -> Optional[Dict]:
        """
        Connect to WiFi network (alias for wifi_connect)
        
        Args:
            ssid: Network SSID
            password: Network password
            
        Returns:
            Connection status
        """
        return self.wifi_connect(ssid, password)
    
    # ========== Data Logs ==========
    
    def get_sensor_logs(self, hours: int = 24, limit: int = 100) -> Optional[List[Dict]]:
        """Get sensor data logs from database"""
        return self._request('GET', f'/logs/sensors?hours={hours}&limit={limit}')
    
    def get_actuator_logs(self, hours: int = 24, limit: int = 100) -> Optional[List[Dict]]:
        """Get actuator control logs from database"""
        return self._request('GET', f'/logs/actuators?hours={hours}&limit={limit}')
    
    def get_alert_logs(self, hours: int = 24, limit: int = 100) -> Optional[List[Dict]]:
        """Get alert logs from database"""
        return self._request('GET', f'/logs/alerts?hours={hours}&limit={limit}')
    
    def get_statistics(self, hours: int = 24) -> Optional[Dict]:
        """
        Get statistical summary of sensor data
        
        Returns:
            Statistics for CO2, temperature, humidity (min, max, avg, std)
        """
        return self._request('GET', f'/logs/statistics?hours={hours}')


# Singleton instance
_api_client = None

def get_api_client() -> MASHApiClient:
    """Get singleton API client instance"""
    global _api_client
    if _api_client is None:
        _api_client = MASHApiClient()
    return _api_client
