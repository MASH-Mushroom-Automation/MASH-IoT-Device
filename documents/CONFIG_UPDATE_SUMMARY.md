# Configuration Update Summary

## Overview
Updated configuration files to be fully compatible with `integrated_server.py` and added comprehensive Bluetooth, GPIO, and API server configuration options.

## Files Updated

### 1. `config/device_config.yaml`
**New Sections Added:**

#### Serial Configuration
```yaml
sensors:
  serial:
    port: "/dev/ttyACM0"
    baud_rate: 9600
    timeout: 1
```

#### Bluetooth Configuration
```yaml
bluetooth:
  enabled: true
  discoverable_on_startup: true
  discoverable_timeout: 300  # 5 minutes
  device_name: "MASH-IoT-Device"
  pairing_required: true
  tethering:
    enabled: true
    auto_start: false
    interface: "bnep0"
```

#### GPIO Configuration
```yaml
gpio:
  mode: "BCM"  # BCM or BOARD
  relays:
    blower_fan: 22
    exhaust_fan: 27
    humidifier: 17
    led_lights: 18
  active_low: true  # Relays are active LOW
```

#### API Server Configuration
```yaml
api:
  host: "0.0.0.0"
  port: 5000
  debug: false
  cors_enabled: true
```

#### Development Configuration
```yaml
development:
  mock_mode: false
  debug_mode: false
  test_sensors: false
  simulation_mode: false  # Run without GPIO/Bluetooth
```

### 2. `src/utils/config.py`
**New Configuration Keys Added:**

#### Bluetooth Configuration
- `bluetooth_enabled` - Enable/disable Bluetooth (default: true)
- `bluetooth_discoverable_on_startup` - Auto-discoverable on startup (default: true)
- `bluetooth_discoverable_timeout` - Discoverable timeout in seconds (default: 300)
- `bluetooth_device_name` - Bluetooth device name (default: "MASH-IoT-Device")
- `bluetooth_pairing_required` - Require pairing (default: true)
- `bluetooth_tethering_enabled` - Enable tethering (default: true)
- `bluetooth_tethering_auto_start` - Auto-start tethering (default: false)
- `bluetooth_tethering_interface` - Tethering interface (default: "bnep0")

#### GPIO Configuration
- `gpio_mode` - GPIO mode: BCM or BOARD (default: "BCM")
- `gpio_relay_blower_fan` - Blower fan relay pin (default: 22)
- `gpio_relay_exhaust_fan` - Exhaust fan relay pin (default: 27)
- `gpio_relay_humidifier` - Humidifier relay pin (default: 17)
- `gpio_relay_led_lights` - LED lights relay pin (default: 18)
- `gpio_active_low` - Relays are active LOW (default: true)

#### API Server Configuration
- `api_host` - API server host (default: "0.0.0.0")
- `api_port` - API server port (default: 5000)
- `api_debug` - Enable Flask debug mode (default: false)
- `api_cors_enabled` - Enable CORS (default: true)

#### Development Configuration
- `simulation_mode` - Run without GPIO/Bluetooth (default: false)

**New Helper Methods:**

```python
# Get nested configuration values
config.get_nested('bluetooth', 'enabled')
config.get_nested('bluetooth.tethering.interface')

# Get Bluetooth configuration as dict
bt_config = config.get_bluetooth_config()
# Returns: {'enabled': True, 'discoverable_on_startup': True, ...}

# Get GPIO configuration as dict
gpio_config = config.get_gpio_config()
# Returns: {'mode': 'BCM', 'relays': {...}, 'active_low': True}

# Get API server configuration as dict
api_config = config.get_api_config()
# Returns: {'host': '0.0.0.0', 'port': 5000, ...}
```

## Usage in integrated_server.py

### Loading Configuration

```python
from src.utils.config import Config

# Load configuration from YAML file
config = Config(config_file='config/device_config.yaml')

# Validate configuration
if not config.validate():
    logger.error("Invalid configuration")
    exit(1)
```

### Using Configuration Values

```python
# Device configuration
DEVICE_ID = config.get('device_id', 'MASH-A1-CAL25-AC2415')
DEVICE_NAME = config.get('device_name', 'Mushroom Prototype Chamber')

# Serial configuration
SERIAL_PORT = config.get_nested('sensors', 'serial', 'port', default='/dev/ttyACM0')
SERIAL_BAUD = config.get_nested('sensors', 'serial', 'baud_rate', default=9600)

# GPIO configuration
gpio_config = config.get_gpio_config()
RELAY_BLOWER_FAN = gpio_config['relays']['blower_fan']
RELAY_EXHAUST_FAN = gpio_config['relays']['exhaust_fan']
RELAY_HUMIDIFIER = gpio_config['relays']['humidifier']
RELAY_LED_LIGHTS = gpio_config['relays']['led_lights']

# API server configuration
api_config = config.get_api_config()
API_HOST = api_config['host']
API_PORT = api_config['port']

# Bluetooth configuration
bt_config = config.get_bluetooth_config()
if bt_config['enabled']:
    bluetooth_manager = BluetoothManager()
    if bt_config['discoverable_on_startup']:
        bluetooth_manager.set_discoverable(True, timeout=bt_config['discoverable_timeout'])
```

### Starting the Server

```python
if __name__ == '__main__':
    # Load configuration
    config = Config(config_file='config/device_config.yaml')
    
    # Get API configuration
    api_config = config.get_api_config()
    
    # Start Flask server
    app.run(
        host=api_config['host'],
        port=api_config['port'],
        debug=api_config['debug']
    )
```

## Environment Variables

All configuration values can be overridden using environment variables:

### Bluetooth
```bash
export BLUETOOTH_ENABLED=true
export BLUETOOTH_DISCOVERABLE_ON_STARTUP=true
export BLUETOOTH_DISCOVERABLE_TIMEOUT=300
export BLUETOOTH_DEVICE_NAME="MASH-IoT-Device"
export BLUETOOTH_PAIRING_REQUIRED=true
export BLUETOOTH_TETHERING_ENABLED=true
export BLUETOOTH_TETHERING_AUTO_START=false
export BLUETOOTH_TETHERING_INTERFACE="bnep0"
```

### GPIO
```bash
export GPIO_MODE=BCM
export GPIO_RELAY_BLOWER_FAN=22
export GPIO_RELAY_EXHAUST_FAN=27
export GPIO_RELAY_HUMIDIFIER=17
export GPIO_RELAY_LED_LIGHTS=18
export GPIO_ACTIVE_LOW=true
```

### API Server
```bash
export API_HOST=0.0.0.0
export API_PORT=5000
export API_DEBUG=false
export API_CORS_ENABLED=true
```

### Development
```bash
export SIMULATION_MODE=false
export MOCK_MODE=false
export DEBUG_MODE=false
```

## Configuration Priority

Configuration values are loaded in the following priority (highest to lowest):

1. **Environment Variables** - Highest priority
2. **YAML Configuration File** - Medium priority
3. **Default Values** - Lowest priority

Example:
```python
# If BLUETOOTH_ENABLED env var is set, it overrides YAML value
# If not set, uses value from device_config.yaml
# If not in YAML, uses default value (true)
bluetooth_enabled = config.get('bluetooth_enabled')
```

## Compatibility with integrated_server.py

The updated configuration is fully compatible with `integrated_server.py`:

### ✅ Device Configuration
- Device ID, name, type, model

### ✅ Serial Communication
- Arduino serial port and baud rate

### ✅ GPIO Control
- Relay pin assignments
- Active LOW configuration

### ✅ Bluetooth
- Bluetooth manager initialization
- Discoverable mode settings
- Tethering configuration

### ✅ API Server
- Flask server host and port
- CORS and debug settings

### ✅ Sensors
- SCD41 sensor configuration
- Serial communication settings

### ✅ Control Thresholds
- Temperature, humidity, CO2 thresholds

### ✅ Logging
- Log level, file, rotation

## Migration Guide

### From Old Configuration

**Old Way:**
```python
# Hard-coded values in integrated_server.py
DEVICE_ID = 'MASH-A1-CAL25-AC2415'
SERIAL_PORT = '/dev/ttyACM0'
RELAY_BLOWER_FAN = 22
```

**New Way:**
```python
# Load from configuration
config = Config(config_file='config/device_config.yaml')
DEVICE_ID = config.get('device_id')
SERIAL_PORT = config.get_nested('sensors', 'serial', 'port')
gpio_config = config.get_gpio_config()
RELAY_BLOWER_FAN = gpio_config['relays']['blower_fan']
```

### Benefits

1. **Centralized Configuration** - All settings in one place
2. **Environment Override** - Easy deployment configuration
3. **Type Safety** - Automatic type conversion
4. **Validation** - Built-in configuration validation
5. **Flexibility** - Easy to add new configuration options
6. **Documentation** - Self-documenting YAML file

## Example: Complete Integration

```python
#!/usr/bin/env python3
"""
MASH IoT Device - Integrated Server with Configuration
"""

from flask import Flask
from src.utils.config import Config
from src.utils.bluetooth_manager import BluetoothManager
from src.utils.bluetooth_tethering import BluetoothTethering
import logging

# Load configuration
config = Config(config_file='config/device_config.yaml')

# Validate configuration
if not config.validate():
    print("ERROR: Invalid configuration")
    exit(1)

# Setup logging
logging.basicConfig(
    level=config.get('log_level', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Get configurations
device_id = config.get('device_id')
device_name = config.get('device_name')
bt_config = config.get_bluetooth_config()
gpio_config = config.get_gpio_config()
api_config = config.get_api_config()

# Initialize Bluetooth if enabled
if bt_config['enabled']:
    bluetooth_manager = BluetoothManager()
    bluetooth_tethering = BluetoothTethering()
    
    if bt_config['discoverable_on_startup']:
        bluetooth_manager.set_discoverable(
            True, 
            timeout=bt_config['discoverable_timeout']
        )

# Start server
if __name__ == '__main__':
    logger.info(f"Starting {device_name} ({device_id})")
    app.run(
        host=api_config['host'],
        port=api_config['port'],
        debug=api_config['debug']
    )
```

## Testing

### Test Configuration Loading
```bash
python3 -c "
from src.utils.config import Config
config = Config(config_file='config/device_config.yaml')
print('Bluetooth enabled:', config.get('bluetooth_enabled'))
print('API port:', config.get('api_port'))
print('GPIO config:', config.get_gpio_config())
"
```

### Test Environment Override
```bash
export BLUETOOTH_ENABLED=false
export API_PORT=8080
python3 integrated_server.py
```

---

**Updated:** November 11, 2024
**Version:** 2.0.0
**Status:** Production Ready
