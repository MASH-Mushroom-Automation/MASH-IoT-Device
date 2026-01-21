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
        base_date = datetime(2026, 1, 13, 14, 30)  # January 13, 2026, 2:30 PM
        self.alerts = [
            {
                'id': 1,
                'timestamp': (base_date - timedelta(minutes=2)).isoformat(),
                'severity': 'info',
                'message': 'System operating normally - all parameters within optimal range',
                'category': 'system'
            },
            {
                'id': 2,
                'timestamp': (base_date - timedelta(minutes=8)).isoformat(),
                'severity': 'warning',
                'message': 'CO2 level approaching upper threshold (1450 ppm). Exhaust fan activated.',
                'category': 'sensor'
            },
            {
                'id': 3,
                'timestamp': (base_date - timedelta(minutes=15)).isoformat(),
                'severity': 'info',
                'message': 'Automation system successfully adjusted humidity levels',
                'category': 'automation'
            },
            {
                'id': 4,
                'timestamp': (base_date - timedelta(minutes=25)).isoformat(),
                'severity': 'error',
                'message': 'Temperature sensor reading anomaly detected - validating...',
                'category': 'sensor'
            },
            {
                'id': 5,
                'timestamp': (base_date - timedelta(minutes=32)).isoformat(),
                'severity': 'info',
                'message': 'Sensor validation complete - all systems nominal',
                'category': 'system'
            },
            {
                'id': 6,
                'timestamp': (base_date - timedelta(hours=1)).isoformat(),
                'severity': 'warning',
                'message': 'Humidity dropped below optimal threshold (78%). Humidifier enabled.',
                'category': 'sensor'
            },
            {
                'id': 7,
                'timestamp': (base_date - timedelta(hours=1, minutes=15)).isoformat(),
                'severity': 'info',
                'message': 'Grow lights cycle initiated - 18-hour photoperiod',
                'category': 'automation'
            },
            {
                'id': 8,
                'timestamp': (base_date - timedelta(hours=2)).isoformat(),
                'severity': 'warning',
                'message': 'CO2 level temporarily exceeded maximum (1520 ppm). Auto-corrected.',
                'category': 'sensor'
            },
            {
                'id': 9,
                'timestamp': (base_date - timedelta(hours=3)).isoformat(),
                'severity': 'info',
                'message': 'Daily maintenance check completed successfully',
                'category': 'system'
            },
            {
                'id': 10,
                'timestamp': (base_date - timedelta(hours=4)).isoformat(),
                'severity': 'error',
                'message': 'Network connectivity temporarily lost - operating in offline mode',
                'category': 'network'
            },
            {
                'id': 11,
                'timestamp': (base_date - timedelta(hours=4, minutes=5)).isoformat(),
                'severity': 'info',
                'message': 'Network connectivity restored - cloud sync complete',
                'category': 'network'
            },
            {
                'id': 12,
                'timestamp': (base_date - timedelta(hours=6)).isoformat(),
                'severity': 'warning',
                'message': 'Circulation fan running at reduced efficiency - maintenance recommended',
                'category': 'actuator'
            }
        ]
        
        # Mock AI insights history
        self.ai_insights = [
            {
                'timestamp': (base_date - timedelta(minutes=2)).isoformat(),
                'action': 'Optimal Conditions Maintained',
                'sensor_data': {
                    'co2': 1280,
                    'temperature': 18.5,
                    'humidity': 85.0
                },
                'reasoning': 'All environmental parameters are within optimal ranges for mushroom cultivation. CO2 at 1280 ppm provides excellent growth conditions. Temperature steady at 18.5°C supports proper fruiting body development. Humidity at 85% prevents drying while avoiding excess moisture. System maintaining current actuator configuration.',
                'mode': 'auto'
            },
            {
                'timestamp': (base_date - timedelta(minutes=8)).isoformat(),
                'action': 'CO2 Reduction Initiated',
                'sensor_data': {
                    'co2': 1450,
                    'temperature': 19.1,
                    'humidity': 87.5
                },
                'reasoning': 'CO2 level approaching upper threshold at 1450 ppm. Activated exhaust fan to reduce CO2 concentration and prevent growth inhibition. Temperature slightly elevated at 19.1°C - exhaust will also assist cooling. Humidity within acceptable range but monitoring for potential excess due to temperature rise.',
                'mode': 'auto'
            },
            {
                'timestamp': (base_date - timedelta(minutes=15)).isoformat(),
                'action': 'Humidity Adjustment',
                'sensor_data': {
                    'co2': 1180,
                    'temperature': 18.2,
                    'humidity': 79.0
                },
                'reasoning': 'Humidity dropped to 79% which is below optimal range for pinning stage. Enabled humidifier to increase moisture levels and prevent premature drying of substrate. CO2 slightly low at 1180 ppm but within acceptable range. Temperature stable and optimal for current growth phase.',
                'mode': 'auto'
            },
            {
                'timestamp': (base_date - timedelta(minutes=25)).isoformat(),
                'action': 'Environmental Stabilization',
                'sensor_data': {
                    'co2': 1320,
                    'temperature': 18.7,
                    'humidity': 86.0
                },
                'reasoning': 'System successfully stabilized after previous adjustments. All parameters now in optimal ranges. CO2 at ideal level for active mycelial growth. Temperature and humidity perfect for fruiting. Circulation fan maintains air movement without causing excessive drying. No actuator changes required.',
                'mode': 'auto'
            },
            {
                'timestamp': (base_date - timedelta(minutes=35)).isoformat(),
                'action': 'Temperature Control Activated',
                'sensor_data': {
                    'co2': 1390,
                    'temperature': 19.8,
                    'humidity': 88.5
                },
                'reasoning': 'Temperature rising above optimal threshold at 19.8°C, likely due to ambient conditions. Increased air circulation and activated exhaust fan to facilitate heat exchange. CO2 levels elevated but not critical. Monitoring humidity closely as exhaust may cause decrease.',
                'mode': 'auto'
            },
            {
                'timestamp': (base_date - timedelta(hours=1)).isoformat(),
                'action': 'Night Cycle Transition',
                'sensor_data': {
                    'co2': 1240,
                    'temperature': 17.9,
                    'humidity': 84.0
                },
                'reasoning': 'Transitioning to night cycle parameters. Reduced lighting intensity while maintaining environmental controls. Temperature naturally declining as expected. CO2 and humidity levels stable and appropriate for rest period. All systems functioning optimally.',
                'mode': 'auto'
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
    
    def get_sensor_data(self) -> Dict:
        """Get sensor data - another alias for compatibility"""
        return self._get_simulated_sensor_data()
    
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
            'automation_enabled': self.automation_enabled,
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
    
    def set_automation_mode(self, enabled: bool) -> Dict:
        """Set automation mode"""
        if enabled:
            return self.enable_automation()
        else:
            return self.disable_automation()
    
    def get_automation_history(self, limit: int = 10):
        """Get automation decision history"""
        # Return list directly for compatibility with screens
        return self.ai_insights[:limit]
    
    # ========== Alerts/Logs Endpoints ==========
    
    def get_alerts(self, severity: str = None, limit: int = 50):
        """Get system alerts"""
        alerts = self.alerts
        
        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]
        
        # Return list directly for compatibility with screens
        return alerts[:limit]
    
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
