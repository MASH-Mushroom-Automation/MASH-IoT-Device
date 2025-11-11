# Integrated Server Configuration Update

## Summary
Updated `integrated_server.py` to use the Config class instead of hard-coded values. The server now loads all configuration from `config/device_config.yaml` with environment variable override support.

## Changes Made

### 1. Added Config Import
```python
from src.utils.config import Config
```

### 2. Load Configuration on Startup
```python
# Load configuration
config = Config(config_file='config/device_config.yaml')

# Validate configuration
if not config.validate():
    print("ERROR: Invalid configuration. Please check config/device_config.yaml")
    exit(1)
```

### 3. Replaced Hard-Coded Values

#### Before (Hard-Coded):
```python
DEVICE_ID = 'MASH-A1-CAL25-AC2415'
DEVICE_NAME = 'Mushroom Prototype Chamber'
SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUD = 9600
RELAY_BLOWER_FAN = 22
RELAY_EXHAUST_FAN = 27
RELAY_HUMIDIFIER = 17
RELAY_LED_LIGHTS = 18
```

#### After (Config-Based):
```python
# Device Identity
DEVICE_ID = config.get('device_id', 'MASH-A1-CAL25-AC2415')
DEVICE_NAME = config.get('device_name', 'Mushroom Prototype Chamber')

# Serial Configuration
SERIAL_PORT = config.get_nested('sensors', 'serial', 'port', default='/dev/ttyACM0')
SERIAL_BAUD = config.get_nested('sensors', 'serial', 'baud_rate', default=9600)

# GPIO Configuration
gpio_config = config.get_gpio_config()
RELAY_BLOWER_FAN = gpio_config['relays']['blower_fan']
RELAY_EXHAUST_FAN = gpio_config['relays']['exhaust_fan']
RELAY_HUMIDIFIER = gpio_config['relays']['humidifier']
RELAY_LED_LIGHTS = gpio_config['relays']['led_lights']
```

### 4. Updated Logging Configuration
```python
# Use log level from config
log_level = config.get('log_level', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### 5. Updated Bluetooth Initialization
```python
# Get Bluetooth configuration
bt_config = config.get_bluetooth_config()

if bt_config['enabled']:
    if bluetooth_manager.is_available():
        # Make device discoverable if configured
        if bt_config['discoverable_on_startup']:
            timeout = bt_config['discoverable_timeout']
            bluetooth_manager.set_discoverable(True, timeout=timeout)
        
        # Auto-start tethering if configured
        if bt_config['tethering']['auto_start']:
            bluetooth_tethering.start_tethering()
else:
    logger.info("Bluetooth is disabled in configuration")
```

### 6. Updated Flask Server Startup
```python
# Get API configuration
api_config = config.get_api_config()

# Start server with configured settings
app.run(
    host=api_config['host'],
    port=api_config['port'],
    debug=api_config['debug']
)
```

## Benefits

### ✅ Centralized Configuration
All settings in one YAML file instead of scattered throughout code

### ✅ Easy Deployment
Change configuration without modifying code:
```yaml
# config/device_config.yaml
api:
  host: "0.0.0.0"
  port: 8080  # Change port here
  
bluetooth:
  enabled: false  # Disable Bluetooth here
```

### ✅ Environment Override
Override any setting with environment variables:
```bash
export API_PORT=8080
export BLUETOOTH_ENABLED=false
python3 integrated_server.py
```

### ✅ Validation
Configuration is validated on startup:
```
ERROR: Invalid configuration. Please check config/device_config.yaml
```

### ✅ Logging
Configuration loading is logged:
```
INFO - Starting MASH IoT Device Server
INFO - Device ID: MASH-A1-CAL25-AC2415
INFO - Device Name: Mushroom Prototype Chamber
INFO - Configuration loaded from: config/device_config.yaml
INFO - Bluetooth is available
INFO - Bluetooth set to discoverable mode (300 seconds)
```

## Configuration Options Now Available

### Device Configuration
- Device ID, name, type, model
- Loaded from `device_config.yaml`

### Serial Configuration
- Arduino serial port and baud rate
- Configurable per deployment

### GPIO Configuration
- All relay pin assignments
- Active LOW/HIGH configuration
- Easy to change for different hardware

### Bluetooth Configuration
- Enable/disable Bluetooth
- Auto-discoverable on startup
- Discoverable timeout
- Auto-start tethering
- All configurable without code changes

### API Server Configuration
- Host and port
- Debug mode
- CORS settings
- Easy to change for different environments

### Logging Configuration
- Log level (DEBUG, INFO, WARNING, ERROR)
- Configurable without code changes

## Usage Examples

### Run with Default Configuration
```bash
python3 integrated_server.py
```

### Run with Custom Port
```bash
export API_PORT=8080
python3 integrated_server.py
```

### Run with Bluetooth Disabled
```bash
export BLUETOOTH_ENABLED=false
python3 integrated_server.py
```

### Run with Debug Logging
```bash
export LOG_LEVEL=DEBUG
python3 integrated_server.py
```

### Run with Custom Config File
```python
# In code
config = Config(config_file='config/production.yaml')
```

## Testing

### Test Configuration Loading
```bash
python3 integrated_server.py
```

Expected output:
```
INFO - Starting MASH IoT Device Server
INFO - Device ID: MASH-A1-CAL25-AC2415
INFO - Device Name: MASH Chamber #1
INFO - Configuration loaded from: config/device_config.yaml
INFO - Bluetooth is available
INFO - Bluetooth set to discoverable mode (300 seconds)
INFO - Sensor data reader started
INFO - Rule-based automation thread started
INFO - Starting HTTP server on 0.0.0.0:5000
```

### Test Configuration Override
```bash
export API_PORT=8080
export BLUETOOTH_ENABLED=false
python3 integrated_server.py
```

Expected output:
```
INFO - Starting MASH IoT Device Server
INFO - Configuration loaded from: config/device_config.yaml
INFO - Bluetooth is disabled in configuration
INFO - Starting HTTP server on 0.0.0.0:8080
```

## Migration Complete

The `integrated_server.py` now:
- ✅ Loads configuration from YAML file
- ✅ Validates configuration on startup
- ✅ Supports environment variable overrides
- ✅ Uses Config helper methods for easy access
- ✅ Logs configuration loading
- ✅ Respects Bluetooth enable/disable setting
- ✅ Uses configured API host and port
- ✅ Uses configured log level
- ✅ Fully compatible with `device_config.yaml`

## Next Steps

1. **Test on Raspberry Pi** - Verify configuration loading works
2. **Test Environment Overrides** - Verify env vars work correctly
3. **Test Bluetooth Settings** - Verify Bluetooth config is respected
4. **Test API Settings** - Verify port and host changes work
5. **Deploy** - Use configuration for different environments

---

**Updated:** November 11, 2024
**Status:** Complete and Ready for Testing
