For quick module testing purposes.

## Dependencies
Install the required Arduino library:
- Open Arduino IDE > Tools > Manage Libraries
- Search for "Sensirion I2C SCD4x" and install it

## Setup
1. Connect the arduino to your computer
2. Open the arduino IDE
3. Select the correct board and port
4. Upload the code from `test_scd41/test_scd41.ino`
5. Open the serial monitor
6. Set the baud rate to 9600
7. You should see the data being printed

## Hardware Setup
- Arduino I2C Hub with multiple channels: I2C, A0, A1, A2, A3 (for multiplexer), UART, and digital pins D2-D8
- Connect SCD41 to the appropriate I2C channel (default I2C pins A4/SDA, A5/SCL if using main I2C bus)

# Modules to Test
1. CO2L SCD41: CO2, Temperature, Humidity (`test_scd41/test_scd41.ino`)
2. LCD 16x2: Display

## Live Graph Application
For real-time visualization of sensor data:
- Navigate to `live_graph/`
- Install dependencies: `pip install -r requirements.txt`
- Update `SERIAL_PORT` in `live_graph.py` to match your Arduino's COM port
- Run: `python live_graph.py`
- This will display live graphs for CO2, Temperature, and Humidity