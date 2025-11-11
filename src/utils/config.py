"""
Configuration Manager
Handles application configuration from environment variables and config files
"""

import os
import yaml
import logging
from typing import Any, Optional, Dict
from dotenv import load_dotenv


class Config:
    """Application configuration manager"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to YAML configuration file
        """
        self.logger = logging.getLogger(__name__)
        self._config = {}
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration file if provided
        if config_file and os.path.exists(config_file):
            self._load_config_file(config_file)
        
        # Set default values
        self._set_defaults()
    
    def _load_config_file(self, config_file: str):
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                self._config = yaml.safe_load(f) or {}
            self.logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            self.logger.error(f"Failed to load config file {config_file}: {e}")
    
    def _set_defaults(self):
        """Set default configuration values"""
        defaults = {
            # Device Configuration
            'device_id': os.getenv('DEVICE_ID', 'mash_device_001'),
            'device_name': os.getenv('DEVICE_NAME', 'MASH Chamber #1'),
            'device_type': os.getenv('DEVICE_TYPE', 'MASH_CHAMBER'),
            'device_model': os.getenv('DEVICE_MODEL', 'RPi3-ModelB'),
            
            # Backend Configuration
            'backend_api_url': os.getenv('BACKEND_API_URL', 'https://mash-backend-api-production.up.railway.app'),
            'backend_api_key': os.getenv('BACKEND_API_KEY', ''),
            
            # MQTT Configuration
            'mqtt_broker_url': os.getenv('MQTT_BROKER_URL', 'mqtt://localhost:1883'),
            'mqtt_username': os.getenv('MQTT_USERNAME', ''),
            'mqtt_password': os.getenv('MQTT_PASSWORD', ''),
            'mqtt_client_id': os.getenv('MQTT_CLIENT_ID', 'mash_device_001'),
            
            # Database Configuration
            'database_path': os.getenv('DATABASE_PATH', './data/mash_device.db'),
            'sqlite_timeout': int(os.getenv('SQLITE_TIMEOUT', '30')),
            
            # Sensor Configuration
            'sensor_read_interval': int(os.getenv('SENSOR_READ_INTERVAL', '60')),
            'sensor_calibration_offset_temp': float(os.getenv('SENSOR_CALIBRATION_OFFSET_TEMP', '0.0')),
            'sensor_calibration_offset_humidity': float(os.getenv('SENSOR_CALIBRATION_OFFSET_HUMIDITY', '0.0')),
            'sensors.source': os.getenv('SENSOR_SOURCE', 'arduino_bridge'),
            'sensors.serial.port': os.getenv('SENSOR_SERIAL_PORT', '/dev/ttyACM0'),
            'sensors.serial.baud': int(os.getenv('SENSOR_SERIAL_BAUD', '9600')),
            
            # Control Thresholds
            'temp_min': float(os.getenv('TEMP_MIN', '25.0')),
            'temp_max': float(os.getenv('TEMP_MAX', '28.0')),
            'temp_critical_high': float(os.getenv('TEMP_CRITICAL_HIGH', '32.0')),
            'humidity_min': float(os.getenv('HUMIDITY_MIN', '80.0')),
            'humidity_max': float(os.getenv('HUMIDITY_MAX', '90.0')),
            'co2_optimal_min': int(os.getenv('CO2_OPTIMAL_MIN', '10000')),
            'co2_optimal_max': int(os.getenv('CO2_OPTIMAL_MAX', '15000')),
            'co2_critical_high': int(os.getenv('CO2_CRITICAL_HIGH', '20000')),
            
            # Sync Configuration
            'sync_interval': int(os.getenv('SYNC_INTERVAL', '300')),
            'batch_sync_size': int(os.getenv('BATCH_SYNC_SIZE', '100')),
            'data_retention_days': int(os.getenv('DATA_RETENTION_DAYS', '30')),
            'alert_cooldown_seconds': int(os.getenv('ALERT_COOLDOWN_SECONDS', '900')),
            
            # Logging Configuration
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_file': os.getenv('LOG_FILE', './logs/mash_device.log'),
            'log_max_size': int(os.getenv('LOG_MAX_SIZE', '10485760')),  # 10MB
            'log_backup_count': int(os.getenv('LOG_BACKUP_COUNT', '5')),
            
            # Bluetooth Configuration
            'bluetooth_enabled': os.getenv('BLUETOOTH_ENABLED', 'true').lower() == 'true',
            'bluetooth_discoverable_on_startup': os.getenv('BLUETOOTH_DISCOVERABLE_ON_STARTUP', 'true').lower() == 'true',
            'bluetooth_discoverable_timeout': int(os.getenv('BLUETOOTH_DISCOVERABLE_TIMEOUT', '300')),
            'bluetooth_device_name': os.getenv('BLUETOOTH_DEVICE_NAME', 'MASH-IoT-Device'),
            'bluetooth_pairing_required': os.getenv('BLUETOOTH_PAIRING_REQUIRED', 'true').lower() == 'true',
            'bluetooth_tethering_enabled': os.getenv('BLUETOOTH_TETHERING_ENABLED', 'true').lower() == 'true',
            'bluetooth_tethering_auto_start': os.getenv('BLUETOOTH_TETHERING_AUTO_START', 'false').lower() == 'true',
            'bluetooth_tethering_interface': os.getenv('BLUETOOTH_TETHERING_INTERFACE', 'bnep0'),
            
            # GPIO Configuration
            'gpio_mode': os.getenv('GPIO_MODE', 'BCM'),
            'gpio_relay_blower_fan': int(os.getenv('GPIO_RELAY_BLOWER_FAN', '22')),
            'gpio_relay_exhaust_fan': int(os.getenv('GPIO_RELAY_EXHAUST_FAN', '27')),
            'gpio_relay_humidifier': int(os.getenv('GPIO_RELAY_HUMIDIFIER', '17')),
            'gpio_relay_led_lights': int(os.getenv('GPIO_RELAY_LED_LIGHTS', '18')),
            'gpio_active_low': os.getenv('GPIO_ACTIVE_LOW', 'true').lower() == 'true',
            
            # API Server Configuration
            'api_host': os.getenv('API_HOST', '0.0.0.0'),
            'api_port': int(os.getenv('API_PORT', '5000')),
            'api_debug': os.getenv('API_DEBUG', 'false').lower() == 'true',
            'api_cors_enabled': os.getenv('API_CORS_ENABLED', 'true').lower() == 'true',
            
            # Development/Testing
            'mock_mode': os.getenv('MOCK_MODE', 'false').lower() == 'true',
            'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true',
            'simulation_mode': os.getenv('SIMULATION_MODE', 'false').lower() == 'true'
        }
        
        # Update config with defaults (only if not already set)
        for key, value in defaults.items():
            if key not in self._config:
                self._config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
        self.logger.debug(f"Set config {key} = {value}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()
    
    def update(self, updates: Dict[str, Any]):
        """
        Update multiple configuration values
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        self._config.update(updates)
        self.logger.debug(f"Updated config with {len(updates)} values")
    
    def save_to_file(self, file_path: str):
        """
        Save configuration to YAML file
        
        Args:
            file_path: Path to save configuration file
        """
        try:
            with open(file_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False, indent=2)
            self.logger.info(f"Configuration saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def get_nested(self, *keys, default: Any = None) -> Any:
        """
        Get nested configuration value using dot notation or multiple keys
        
        Args:
            *keys: Configuration keys (e.g., 'bluetooth', 'enabled' or 'bluetooth.enabled')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # Handle dot notation
        if len(keys) == 1 and '.' in keys[0]:
            keys = keys[0].split('.')
        
        value = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def get_bluetooth_config(self) -> Dict[str, Any]:
        """Get Bluetooth configuration"""
        return {
            'enabled': self.get('bluetooth_enabled', True),
            'discoverable_on_startup': self.get('bluetooth_discoverable_on_startup', True),
            'discoverable_timeout': self.get('bluetooth_discoverable_timeout', 300),
            'device_name': self.get('bluetooth_device_name', 'MASH-IoT-Device'),
            'pairing_required': self.get('bluetooth_pairing_required', True),
            'tethering': {
                'enabled': self.get('bluetooth_tethering_enabled', True),
                'auto_start': self.get('bluetooth_tethering_auto_start', False),
                'interface': self.get('bluetooth_tethering_interface', 'bnep0')
            }
        }
    
    def get_gpio_config(self) -> Dict[str, Any]:
        """Get GPIO configuration"""
        return {
            'mode': self.get('gpio_mode', 'BCM'),
            'relays': {
                'blower_fan': self.get('gpio_relay_blower_fan', 22),
                'exhaust_fan': self.get('gpio_relay_exhaust_fan', 27),
                'humidifier': self.get('gpio_relay_humidifier', 17),
                'led_lights': self.get('gpio_relay_led_lights', 18)
            },
            'active_low': self.get('gpio_active_low', True)
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API server configuration"""
        return {
            'host': self.get('api_host', '0.0.0.0'),
            'port': self.get('api_port', 5000),
            'debug': self.get('api_debug', False),
            'cors_enabled': self.get('api_cors_enabled', True)
        }
    
    def validate(self) -> bool:
        """
        Validate configuration values
        
        Returns:
            True if configuration is valid, False otherwise
        """
        required_keys = [
            'device_id', 'backend_api_url', 'database_path'
        ]
        
        missing_keys = []
        for key in required_keys:
            if not self.get(key):
                missing_keys.append(key)
        
        if missing_keys:
            self.logger.error(f"Missing required configuration: {missing_keys}")
            return False
        
        # Validate numeric values
        numeric_keys = [
            'sensor_read_interval', 'temp_min', 'temp_max',
            'humidity_min', 'humidity_max', 'co2_optimal_min',
            'co2_optimal_max', 'sync_interval', 'batch_sync_size'
        ]
        
        for key in numeric_keys:
            value = self.get(key)
            if value is not None and not isinstance(value, (int, float)):
                self.logger.error(f"Invalid numeric value for {key}: {value}")
                return False
        
        self.logger.info("Configuration validation passed")
        return True
