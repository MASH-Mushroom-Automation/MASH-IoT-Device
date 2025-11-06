# MASH IoT Device - Arduino Uno Presentation Version

This is a simplified version of the MASH IoT Device using Arduino Uno for presentation purposes. It provides real-time monitoring of CO2, temperature, and humidity using the SCD41 sensor.


python live_dashboard.py --port /dev/ttyACM0 --web-port 8080


## Quick Start

### 1. Hardware Setup
- **Arduino Uno R3**
- **SCD41 CO2/Temperature/Humidity Sensor**
- **2004 I2C LCD Display** (20x4 character LCD)
- **I2C Hub/Shield** for easy connections (optional - Base Shield V2 recommended)
- **Jumper wires**

**Wiring:**
```
Arduino Uno    SCD41 Sensor    2004 I2C LCD
5V            VCC             VCC
GND           GND             GND
A4 (SDA)      SDA             SDA
A5 (SCL)      SCL             SCL
```

**LCD I2C Addresses:**
- SCD41 Sensor: 0x62 (fixed)
- LCD Display: 0x27 or 0x3F (common addresses)

**Note:** Both the SCD41 sensor and LCD share the same I2C bus (A4/A5). The Arduino Uno's I2C implementation handles multiple devices on the same bus.

### 2. Software Setup
1. **Install Arduino Libraries:**
   - Open Arduino IDE > Tools > Manage Libraries
   - Search and install: "Sensirion I2C SCD4x"
   - Search and install: "LiquidCrystal I2C" (by Frank de Brabander)

2. **Upload Code:**
   - Open `test_scd41/test_scd41.ino`
   - Select board: Arduino Uno
   - Select correct COM port
   - Upload the code

3. **Python Visualization:**
   ```bash
   cd live_graph
   pip install -r requirements.txt
   # Update SERIAL_PORT in live_graph.py
   python live_graph.py
   ```

## Features

### Arduino Features
- ✅ **Real-time sensor readings** every 5 seconds
- ✅ **Enhanced serial output** with air quality indicators
- ✅ **Presentation mode** (type 'p' in serial monitor)
- ✅ **Error handling** with clear feedback
- ✅ **Serial communication** for data logging
- ✅ **2004 I2C LCD display** with cycling information pages
- ✅ **Visual alerts** with backlight flashing for CO2 warnings
- ✅ **Status indicators** for all environmental parameters

### LCD Display Features
The 2004 I2C LCD provides real-time visual feedback with three rotating information pages:

#### **Page 1: CO2 Monitoring**
- Current CO2 level and mode (Spawning/Fruiting)
- Status indicator (OK/LOW/HIGH/WAIT)
- Target CO2 range for current mode
- Alert status and system status

#### **Page 2: Temperature Monitoring**
- Current temperature with status (Good/Warm/Hot)
- CO2 reading for reference
- Current operating mode

#### **Page 3: Humidity Monitoring**
- Current humidity with status (Good/High/Very High)
- Temperature reading for reference
- Runtime counter and current mode

**Display Rotation:** Pages automatically cycle every 2 seconds
**Alert System:** LCD backlight flashes during CO2 alerts
**Error Display:** Shows clear error messages during sensor issues

### Python Visualization
- ✅ **Live graphs** for CO2, Temperature, and Humidity
- ✅ **Color-coded air quality zones**
- ✅ **Real-time statistics** and averages
- ✅ **Presentation mode** with enhanced visuals

## Presentation Commands

### Serial Monitor Commands
- Type `p` - Enter presentation mode (enhanced output with air quality indicators)
- Type `n` - Enter normal mode (simple data output)
- Type `s` - Switch to **Spawning Mode** (CO2 > 10,000 ppm required)
- Type `f` - Switch to **Fruiting Mode** (CO2 500-800 ppm required)

### Mushroom Growing Modes

#### **Spawning Mode** (Type 's')
- **CO2 Requirement**: > 10,000 ppm
- **Alert**: Triggers when CO2 drops below 10,000 ppm
- **Purpose**: Mycelium colonization phase

#### **Fruiting Mode** (Type 'f')
- **CO2 Requirement**: 500-800 ppm
- **Alert**: Triggers when CO2 < 500 ppm or > 800 ppm
- **Purpose**: Mushroom fruiting phase

### Air Quality Indicators
- **CO2**: Mode-specific thresholds with visual alerts
- **Temperature**: Green (18-24°C), Yellow (24-28°C), Orange (28-35°C)
- **Humidity**: Green (30-60%), Yellow (60-80%), Orange (80-100%)

## Troubleshooting

### Common Issues
1. **SCD41 Not Detected**: Check I2C connections (A4/A5), verify power
2. **Serial Issues**: Check COM port in Python code, verify baud rate (9600)
3. **Python Errors**: Install dependencies, check serial port permissions
4. **No Data**: Ensure Arduino is connected and sending data to serial monitor
5. **LCD Not Working**: Check LCD I2C address (try 0x27 or 0x3F), verify power and connections
6. **LCD Shows Garbled Text**: Check LCD initialization, try different I2C address
7. **LCD No Backlight**: Check power connections, LCD contrast potentiometer

### I2C Address Scanner
If unsure about I2C addresses, use the scanner code in `PRESENTATION_SETUP.md`

## Files Structure
```
arduino-uno/
├── test_scd41/
│   └── test_scd41.ino          # Main Arduino code with enhanced serial output
├── live_graph/
│   ├── live_graph.py           # Python visualization with presentation mode
│   └── requirements.txt        # Python dependencies
├── README.md                   # This file
└── PRESENTATION_SETUP.md       # Comprehensive setup guide
```

## Advantages of Arduino Version
- **Simpler Setup**: No complex I2C pin configuration issues
- **Reliable I2C**: Arduino's I2C implementation is more stable
- **Easy Debugging**: Serial monitor provides clear feedback
- **Cost Effective**: Lower cost for demonstration purposes
- **Educational**: Easier to understand and modify

## Next Steps
This Arduino version demonstrates the core functionality. The full RPi3 version includes WiFi, MQTT, database storage, and web APIs.

For detailed setup instructions, see `PRESENTATION_SETUP.md`