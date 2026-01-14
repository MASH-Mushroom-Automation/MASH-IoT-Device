"""
MASH Touchscreen UI - Mock API Client
Returns mock data for demo/testing without backend/hardware
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class MockAPIClient:
    """Mock API client that returns simulated data for demo purposes"""
    
    def __init__(self, *args, **kwargs):
        """Initialize mock client"""
        self.start_time = time.time()
        self.manual_mode = False
        self.automation_enabled = True
        
        # Simulated sensor data with realistic variations
        self.base_co2 = 1200
        self.base_temp = 18.5
        self.base_humidity = 85.0
        
        # Simulated actuator states
        self.actuator_states = {
            'humidifier': False,
            'fan_exhaust': False,
            'fan_circulation': True,
            'led_grow': True
        }
        
        # Mock alerts history
        self.alerts = [
            {
                'id': 1,
                'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                'severity': 'info',
                'message': 'System started successfully',
                'category': 'system'
            },
            {
                'id': 2,
                'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
                'severity': 'warning',
                'message': 'CO2 level approaching upper threshold (1450 ppm)',
                'category': 'sensor'
            },
            {
                'id': 3,
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'severity': 'info',
                'message': 'Automation enabled',
                'category': 'automation'
            },
            {
                'id': 4,
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'severity': 'warning',
                'message': 'Humidity dropped below threshold (82%)',
                'category': 'sensor'
            },
            {
                'id': 5,
                'timestamp': (datetime.now() - timedelta(hours=3)).isoformat(),
                'severity': 'info',
                'message': 'Humidifier activated by automation',
                'category': 'automation'
            }
        ]
        
        # Mock AI insights history
        self.ai_insights = [
            {
                'timestamp': (datetime.now() - timedelta(minutes=2)).isoformat(),
                'sensor_data': {
                    'co2': 1380,
                    'temperature': 18.8,
                    'humidity': 86.2
                },
                'mode': 'auto',
                'reasoning': [
                    'CO2 level within optimal range',
                    'Temperature stable',
                    'Humidity slightly above target - monitoring'
                ],
                'actions': {
                    'humidifier': False,
                    'fan_exhaust': False,
                    'fan_circulation': True,
                    'led_grow': True
                }
            },
            {
                'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                'sensor_data': {
                    'co2': 1420,
                    'temperature': 19.1,
                    'humidity': 88.5
                },
                'mode': 'auto',
                'reasoning': [
                    'CO2 approaching upper threshold',
                    'Temperature rising - initiating cooling',
                    'Humidity high - exhaust fan activated'
                ],
                'actions': {
                    'humidifier': False,
                    'fan_exhaust': True,
                    'fan_circulation': True,
                    'led_grow': True
                }
            },
            {
                'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
                'sensor_data': {
                    'co2': 1250,
                    'temperature': 18.3,
                    'humidity': 83.0
                },
                'mode': 'auto',
                'reasoning': [
                    'All parameters optimal',
                    'Humidity below target - humidifier enabled',
                    'Maintaining circulation'
                ],
                'actions': {
                    'humidifier': True,
                    'fan_exhaust': False,
                    'fan_circulation': True,
                    'led_grow': True
                }
            }
        ]
        
        print("[MOCK MODE] Using mock API client - no backend required")
    
    def _get_simulated_sensor_data(self) -> Dict:
        """Generate realistic sensor data with variations"""
        # Add random variations to simulate real sensors
        co2 = self.base_co2 + random.uniform(-50, 50)
        temp = self.base_temp + random.uniform(-0.5, 0.5)
        humidity = self.base_humidity + random.uniform(-2, 2)
        
        # Clamp to realistic ranges
        co2 = max(800, min(2000, co2))
        temp = max(15, min(25, temp))
        humidity = max(70, min(95, humidity))
        
        return {
            'co2': round(co2, 1),
            'temperature': round(temp, 1),
            'humidity': round(humidity, 1),
            'timestamp': datetime.now().isoformat()
        }
    
    # ========== Status Endpoints ==========
    
    def get_status(self) -> Dict:
        """Get device status"""
        uptime = int(time.time() - self.start_time)
        return {
            'device_id': 'MASH-DEMO-001',
            'status': 'running',
            'mode': 'manual' if self.manual_mode else 'auto',
            'automation_enabled': self.automation_enabled,
            'uptime': uptime
        }
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        return True
    
    # ========== Sensor Data Endpoints ==========
    
    def get_sensor_current(self) -> Dict:
        """Get current sensor readings"""
        return {
            'success': True,
            'data': self._get_simulated_sensor_data()
        }
    
    def get_current_sensor_data(self) -> Dict:
        """Alias for get_sensor_current (backward compatibility)"""
        result = self.get_sensor_current()
        return result.get('data') if result and result.get('success') else None
    
    def get_sensor_history(self, hours: int = 1) -> Dict:
        """Get sensor reading history"""
        # Generate mock historical data
        now = datetime.now()
        history = []
        
        # Generate readings every 2 minutes for the requested hours
        num_readings = (hours * 60) // 2
        for i in range(num_readings, 0, -1):
            timestamp = now - timedelta(minutes=i * 2)
            history.append({
                'timestamp': timestamp.isoformat(),
                **self._get_simulated_sensor_data()
            })
        
        return {
            'success': True,
            'data': history,
            'count': len(history)
        }
    
    # ========== Actuator Control Endpoints ==========
    
    def get_actuators(self) -> Dict:
        """Get all actuator states"""
        return {
            'success': True,
            'actuators': self.actuator_states
        }
    
    def get_actuator_states(self) -> Dict:
        """Alias for get_actuators (backward compatibility)"""
        result = self.get_actuators()
        return result.get('actuators') if result and result.get('success') else None
    
    def set_actuator(self, actuator_id: str, state: bool) -> Dict:
        """Set actuator state"""
        if actuator_id in self.actuator_states:
            self.actuator_states[actuator_id] = state
            print(f"[MOCK] Set {actuator_id} = {state}")
            return {
                'success': True,
                'actuator': actuator_id,
                'state': state
            }
        return {
            'success': False,
            'error': f'Unknown actuator: {actuator_id}'
        }
    
    def get_actuator(self, actuator_id: str) -> Dict:
        """Get single actuator state"""
        if actuator_id in self.actuator_states:
            return {
                'success': True,
                'actuator': actuator_id,
                'state': self.actuator_states[actuator_id]
            }
        return {
            'success': False,
            'error': f'Unknown actuator: {actuator_id}'
        }
    
    # ========== Automation Endpoints ==========
    
    def get_automation_status(self) -> Dict:
        """Get automation status"""
        return {
            'enabled': self.automation_enabled,
            'mode': 'manual' if self.manual_mode else 'auto',
            'last_decision': datetime.now().isoformat()
        }
    
    def enable_automation(self) -> Dict:
        """Enable automation"""
        self.automation_enabled = True
        self.manual_mode = False
        print("[MOCK] Automation enabled")
        return {
            'success': True,
            'enabled': True
        }
    
    def disable_automation(self) -> Dict:
        """Disable automation"""
        self.automation_enabled = False
        self.manual_mode = True
        print("[MOCK] Automation disabled - manual mode")
        return {
            'success': True,
            'enabled': False
        }
    
    def get_automation_history(self, limit: int = 10) -> Dict:
        """Get automation decision history"""
        return {
            'success': True,
            'history': self.ai_insights[:limit]
        }
    
    # ========== Alerts/Logs Endpoints ==========
    
    def get_alerts(self, severity: str = None, limit: int = 50) -> Dict:
        """Get system alerts"""
        alerts = self.alerts
        
        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]
        
        return {
            'success': True,
            'alerts': alerts[:limit],
            'count': len(alerts)
        }
    
    def get_alert_logs(self, severity: str = None, limit: int = 50) -> Dict:
        """Alias for get_alerts (backward compatibility)"""
        return self.get_alerts(severity, limit)
    
    def clear_alerts(self) -> Dict:
        """Clear all alerts"""
        self.alerts = []
        print("[MOCK] Alerts cleared")
        return {
            'success': True,
            'message': 'Alerts cleared'
        }
    
    # ========== WiFi Endpoints ==========
    
    def scan_wifi(self) -> Dict:
        """Scan for WiFi networks"""
        return {
            'success': True,
            'networks': [
                {'ssid': 'MASH_Demo_Network', 'signal': -45, 'secured': True},
                {'ssid': 'GrowRoom_WiFi', 'signal': -62, 'secured': True},
                {'ssid': 'Office_Network', 'signal': -75, 'secured': True},
            ]
        }
    
    def connect_wifi(self, ssid: str, password: str = None) -> Dict:
        """Connect to WiFi network"""
        print(f"[MOCK] Connecting to WiFi: {ssid}")
        time.sleep(1)  # Simulate connection delay
        return {
            'success': True,
            'ssid': ssid,
            'connected': True
        }
    
    def get_wifi_status(self) -> Dict:
        """Get WiFi connection status"""
        return {
            'connected': True,
            'ssid': 'MASH_Demo_Network',
            'ip': '192.168.1.100',
            'signal': -45
        }
    
    # ========== Device Config Endpoints ==========
    
    def get_config(self) -> Dict:
        """Get device configuration"""
        return {
            'success': True,
            'config': {
                'device_id': 'MASH-DEMO-001',
                'device_name': 'MASH Demo Chamber',
                'thresholds': {
                    'co2': {'min': 1000, 'max': 1500, 'optimal': 1200},
                    'temperature': {'min': 16, 'max': 20, 'optimal': 18},
                    'humidity': {'min': 80, 'max': 90, 'optimal': 85}
                }
            }
        }
    
    def update_config(self, config: Dict) -> Dict:
        """Update device configuration"""
        print(f"[MOCK] Config updated: {config}")
        return {
            'success': True,
            'message': 'Configuration updated'
        }
    
    # ========== System Info Endpoints ==========
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        uptime = int(time.time() - self.start_time)
        return {
            'device_id': 'MASH-DEMO-001',
            'hostname': 'mash-demo',
            'uptime': uptime,
            'cpu_usage': random.uniform(10, 30),
            'memory_usage': random.uniform(40, 60),
            'disk_usage': random.uniform(20, 40),
            'temperature': random.uniform(45, 55)
        }
