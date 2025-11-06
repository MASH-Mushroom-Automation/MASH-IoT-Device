# MASH IoT Device - Arduino Uno Presentation Setup

## Overview
This is a simplified version of the MASH IoT Device using Arduino Uno for presentation purposes. It provides real-time monitoring of CO2, temperature, and humidity using the SCD41 sensor with enhanced serial output and Python visualization.

## Hardware Requirements

### Arduino Uno Components
- **Arduino Uno R3** (or compatible)
- **SCD41 CO2/Temperature/Humidity Sensor**
- **I2C Hub/Shield** (for easy connections, optional)
- **Jumper wires**
- **Breadboard** (optional, for prototyping)

### Wiring Diagram
```
Arduino Uno    SCD41 Sensor
5V            VCC
GND           GND
A4 (SDA)      SDA
A5 (SCL)      SCL
```

## Software Setup

### 1. Arduino IDE Setup
1. Install Arduino IDE (latest version)
2. Install required libraries:
   - **Sensirion I2C SCD4x**: Tools > Manage Libraries > Search "Sensirion I2C SCD4x"

### 2. Python Environment Setup
```bash
# Navigate to the live_graph directory
cd arduino-uno/live_graph

# Install dependencies
pip install -r requirements.txt
```

### 3. Arduino Code Upload
1. Open `test_scd41/test_scd41.ino` in Arduino IDE
2. Select correct board: Tools > Board > Arduino Uno
3. Select correct port: Tools > Port > [Your Arduino Port]
4. Upload the code

## Presentation Features

### Arduino Features
- **Real-time sensor readings** every 5 seconds
- **Enhanced serial output** with air quality indicators
- **Presentation mode** (type 'p' in serial monitor)
- **Normal mode** (type 'n' in serial monitor)
- **Error handling** with clear feedback

### Python Visualization Features
- **Live graphs** for CO2, Temperature, and Humidity
- **Color-coded zones** for air quality indicators
- **Real-time statistics** and averages
- **Presentation mode** with enhanced visuals
- **Data point limiting** for smooth performance

## Running the Presentation

### Step 1: Start Arduino
1. Connect Arduino to computer
2. Open Serial Monitor (9600 baud)
3. Wait for "SUCCESS: SCD41 sensor initialized!" message
4. Type 'p' to enter presentation mode

### Step 2: Start Python Visualization
1. Update `SERIAL_PORT` in `live_graph.py` to match your Arduino's COM port
2. Run the visualization:
   ```bash
   python live_graph.py
   ```

### Step 3: Presentation Tips
- **Serial Monitor**: Shows enhanced sensor data with air quality indicators
- **Python Graphs**: Display real-time data with color-coded zones
- **Presentation Mode**: Enhanced output with emojis and status indicators
- **Air Quality Zones**: 
  - CO2: Green (0-400), Yellow (400-1000), Orange (1000-5000), Red (5000+)
  - Temperature: Green (18-24°C), Yellow (24-28°C), Orange (28-35°C)
  - Humidity: Green (30-60%), Yellow (60-80%), Orange (80-100%)

## Troubleshooting

### Common Issues

#### 1. SCD41 Not Detected
- Check I2C connections (SDA to A4, SCL to A5)
- Verify sensor power (3.3V or 5V)
- Try different I2C address (0x62 is default)

#### 2. No Serial Output
- Check Arduino connection and COM port
- Verify baud rate is set to 9600
- Ensure code is uploaded successfully

#### 3. Serial Communication Issues
- Check COM port in Python code
- Verify baud rate (9600)
- Ensure Arduino is connected and recognized

#### 4. Python Visualization Not Starting
- Install all dependencies: `pip install -r requirements.txt`
- Check serial port permissions
- Verify Arduino is sending data in correct format

### I2C Address Scanner
If you're unsure about I2C addresses, upload this code to scan for devices:
```cpp
#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(9600);
  Serial.println("I2C Scanner");
}

void loop() {
  byte error, address;
  int nDevices = 0;
  
  for(address = 1; address < 127; address++ ) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
    
    if (error == 0) {
      Serial.print("I2C device found at address 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
      nDevices++;
    }
  }
  
  if (nDevices == 0) Serial.println("No I2C devices found");
  delay(5000);
}
```

## Presentation Script

### Introduction
"This is our MASH IoT Device demonstration using Arduino Uno. We're monitoring three key environmental parameters: CO2 levels, temperature, and humidity using the SCD41 sensor."

### Key Points to Highlight
1. **Real-time Monitoring**: Data updates every 5 seconds
2. **Enhanced Serial Output**: Clear data display with air quality indicators
3. **Python Visualization**: Detailed graphs with color-coded zones
4. **IoT Capabilities**: Serial communication enables data logging and analysis
5. **Scalability**: This is a simplified version of our full RPi3 system

### Demonstration Flow
1. Show serial monitor with enhanced sensor data
2. Open Python visualization to show detailed graphs
3. Explain the color-coded zones and their significance
4. Discuss how this data can be used for environmental monitoring
5. Compare with full system capabilities (RPi3 version)

## Advantages of Arduino Version
- **Simpler Setup**: No complex I2C pin configuration issues
- **Reliable I2C**: Arduino's I2C implementation is more stable
- **Easy Debugging**: Serial monitor provides clear feedback
- **Cost Effective**: Lower cost for demonstration purposes
- **Educational**: Easier to understand and modify

## Next Steps
This Arduino version demonstrates the core functionality of our MASH IoT Device. The full RPi3 version includes:
- WiFi connectivity
- MQTT communication
- Database storage
- Web API endpoints
- Advanced data processing

## Files Structure
```
arduino-uno/
├── test_scd41/
│   └── test_scd41.ino          # Main Arduino code
├── live_graph/
│   ├── live_graph.py           # Python visualization
│   └── requirements.txt        # Python dependencies
├── README.md                   # Basic setup instructions
└── PRESENTATION_SETUP.md       # This comprehensive guide
```

## Support
For issues or questions:
1. Check the troubleshooting section above
2. Verify all connections and power
3. Ensure all libraries are installed
4. Check serial communication settings
