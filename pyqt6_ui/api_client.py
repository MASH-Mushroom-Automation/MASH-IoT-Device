"""
MASH IoT Device - PyQt6 API Client
Handles communication with Flask backend or mock data
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for importing mock client
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / "touchscreen_ui"))

from config import MOCK_MODE, API_BASE_URL, API_TIMEOUT

if MOCK_MODE:
    from mock_api_client import MockAPIClient as APIClient
else:
    import requests
    from typing import Dict, List, Optional, Any
    
    class APIClient:
        """Real API client for Flask backend communication"""
        
        def __init__(self):
            self.base_url = API_BASE_URL
            self.timeout = API_TIMEOUT
        
        def _get(self, endpoint: str) -> Dict:
            """Make GET request"""
            try:
                response = requests.get(
                    f"{self.base_url}/{endpoint}",
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"API GET error: {e}")
                return {}
        
        def _post(self, endpoint: str, data: Dict) -> Dict:
            """Make POST request"""
            try:
                response = requests.post(
                    f"{self.base_url}/{endpoint}",
                    json=data,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"API POST error: {e}")
                return {}
        
        def get_sensor_data(self) -> Dict:
            """Get current sensor readings"""
            return self._get("sensor/current")
        
        def get_current_sensor_data(self) -> Dict:
            """Alias for get_sensor_data"""
            return self.get_sensor_data()
        
        def get_sensor_history(self, hours: int = 1) -> List[Dict]:
            """Get historical sensor data"""
            result = self._get(f"sensor/history?hours={hours}")
            return result.get('history', [])
        
        def get_actuator_states(self) -> Dict:
            """Get current actuator states"""
            return self._get("actuator/states")
        
        def set_actuator(self, actuator: str, state: bool) -> Dict:
            """Set actuator state"""
            return self._post("actuator/set", {
                'actuator': actuator,
                'state': state
            })
        
        def get_automation_status(self) -> Dict:
            """Get automation system status"""
            return self._get("automation/status")
        
        def set_automation_mode(self, enabled: bool) -> Dict:
            """Enable/disable automation"""
            return self._post("automation/mode", {
                'enabled': enabled
            })
        
        def get_alerts(self) -> List[Dict]:
            """Get system alerts"""
            result = self._get("alerts")
            return result.get('alerts', [])
        
        def get_alert_logs(self) -> List[Dict]:
            """Alias for get_alerts"""
            return self.get_alerts()
        
        def get_automation_history(self) -> List[Dict]:
            """Get AI decision history"""
            result = self._get("automation/history")
            return result.get('history', [])
        
        def get_system_info(self) -> Dict:
            """Get system information"""
            return self._get("system/info")
        
        def get_device_config(self) -> Dict:
            """Get device configuration"""
            return self._get("device/config")
        
        def update_device_config(self, config: Dict) -> Dict:
            """Update device configuration"""
            return self._post("device/config", config)
