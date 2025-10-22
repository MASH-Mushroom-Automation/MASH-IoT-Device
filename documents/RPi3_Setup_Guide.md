# Raspberry Pi 3 Model B Setup Guide for MASH-IoT-Device

## Table of Contents
- [Raspberry Pi 3 Model B Setup Guide for MASH-IoT-Device](#raspberry-pi-3-model-b-setup-guide-for-mash-iot-device)
  - [Table of Contents](#table-of-contents)
  - [Required Hardware Components](#required-hardware-components)
  - [Initial Setup with Raspberry Pi Imager](#initial-setup-with-raspberry-pi-imager)
  - [First Boot and Basic Configuration](#first-boot-and-basic-configuration)
  - [WiFi Configuration (NetworkManager Method)](#wifi-configuration-networkmanager-method)
  - [Enable Required Interfaces](#enable-required-interfaces)
  - [Hardware Setup](#hardware-setup)
    - [GPIO Pin Layout Reference](#gpio-pin-layout-reference)
    - [LED Indicators Setup](#led-indicators-setup)
    - [Reset Button Setup](#reset-button-setup)
    - [Buzzer Setup](#buzzer-setup)
    - [SCD41 Sensor Connection (I2C)](#scd41-sensor-connection-i2c)
  - [Software Installation](#software-installation)
  - [Testing Components](#testing-components)
    - [Test LEDs](#test-leds)
    - [Test Button](#test-button)
    - [Test Buzzer](#test-buzzer)
    - [Test SCD41 Sensor](#test-scd41-sensor)
  - [Running the MASH-IoT-Device Software](#running-the-mash-iot-device-software)
  - [Troubleshooting](#troubleshooting)
    - [WiFi Connection Issues](#wifi-connection-issues)
    - [I2C Connection Issues](#i2c-connection-issues)
    - [GPIO Issues](#gpio-issues)
    - [SCD41 Sensor Issues](#scd41-sensor-issues)
    - [Service Issues](#service-issues)
    - [LED Indicator Reference](#led-indicator-reference)
  - [Advanced Configuration](#advanced-configuration)
    - [Headless Setup (No Monitor)](#headless-setup-no-monitor)
    - [Remote Development](#remote-development)
    - [Backup and Restore](#backup-and-restore)

## Required Hardware Components

- Raspberry Pi 3 Model B
- MicroSD card (16GB+ recommended)
- Power supply (5V/2.5A)
- SCD41 CO2, Temperature, and Humidity sensor
- Breadboard
- LEDs: 1x Green, 1x Blue, 1x Red
- 3x 220Ω resistors (for LEDs)
- 1x Momentary push button
- 1x Buzzer
- Jumper wires (male-to-male, male-to-female)
- USB keyboard and mouse (for initial setup)
- HDMI monitor (for initial setup)
- Ethernet cable (optional)

## Initial Setup with Raspberry Pi Imager

1. **Download and Install Raspberry Pi Imager**
   - Go to [Raspberry Pi website](https://www.raspberrypi.com/software/)
   - Download and install Raspberry Pi Imager for Windows

2. **Prepare MicroSD Card**
   - Insert your microSD card into your computer
   - Launch Raspberry Pi Imager
   - Click "CHOOSE OS" and select "Raspberry Pi OS Lite (32-bit)" (recommended for IoT devices)
   - Click "CHOOSE STORAGE" and select your microSD card

3. **Configure Advanced Options (Important)**
   - Click the gear icon (⚙️) in the bottom right corner
   - Enable "Set hostname" and enter your device name (e.g., "mash-iot-device")
   - Enable "Enable SSH" and select "Use password authentication"
   - Enable "Set username and password"
     - Username: pi (or your preferred username)
     - Password: (create a strong password)
   - Enable "Configure wireless LAN"
     - SSID: Your WiFi network name
     - Password: Your WiFi password
     - Wireless LAN country: PH (Philippines)
   - Enable "Set locale settings"
     - Time zone: Asia/Manila
     - Keyboard layout: US (or your preferred layout)
   - Click "SAVE"

4. **Write to SD Card**
   - Click "WRITE"
   - Confirm and wait for the process to complete
   - When finished, safely eject the microSD card

## First Boot and Basic Configuration

1. **Insert SD Card and Connect Peripherals**
   - Insert the microSD card into your Raspberry Pi
   - Connect keyboard, mouse, and monitor (for initial setup only)
   - Connect power supply (do not connect power yet)

2. **Power On and First Boot**
   - Connect the power supply
   - Wait for the system to boot (first boot takes longer)
   - The system should automatically connect to WiFi based on your settings

3. **Verify Network Connection**
   - Login with your username and password
   - Run: `ping -c 4 google.com`
   - If successful, you have internet connectivity

4. **Update System**
   - Run: `sudo apt update`
   - Run: `sudo apt upgrade -y`
   - Run: `sudo reboot`

## WiFi Configuration (NetworkManager Method)

If your WiFi wasn't configured during imaging or if you need to change it:

1. **Check NetworkManager Status**
   - Run: `sudo systemctl status NetworkManager`
   - If not running, start it: `sudo systemctl start NetworkManager`
   - Enable it: `sudo systemctl enable NetworkManager`

2. **Connect to WiFi using NetworkManager**
   - List available networks: `nmcli device wifi list`
   - Connect to your network: `sudo nmcli device wifi connect "YOUR_WIFI_NAME" password "YOUR_WIFI_PASSWORD"`
   - Or use the interactive method: `sudo nmcli device wifi connect "YOUR_WIFI_NAME" --ask`

3. **Verify Connection**
   - Check connection status: `nmcli connection show --active`
   - Check IP address: `ip addr show wlan0`
   - Test internet: `ping -c 4 google.com`

4. **Troubleshooting WiFi**
   - Check WiFi status: `sudo rfkill list`
   - If blocked, unblock: `sudo rfkill unblock wifi`
   - Check NetworkManager logs: `sudo journalctl -u NetworkManager`
   - Restart NetworkManager: `sudo systemctl restart NetworkManager`
   - View available networks: `nmcli device wifi list`
   - Check connection details: `nmcli connection show "YOUR_WIFI_NAME"`

5. **Advanced NetworkManager Commands**
   - List all connections: `nmcli connection show`
   - Delete a connection: `nmcli connection delete "YOUR_WIFI_NAME"`
   - Modify connection settings: `nmcli connection modify "YOUR_WIFI_NAME" connection.autoconnect yes`
   - Set static IP: `nmcli connection modify "YOUR_WIFI_NAME" ipv4.addresses 192.168.1.100/24`
   - Set DNS: `nmcli connection modify "YOUR_WIFI_NAME" ipv4.dns "8.8.8.8,8.8.4.4"`

## Enable Required Interfaces

1. **Open Raspberry Pi Configuration**
   - Run: `sudo raspi-config`

2. **Enable I2C Interface**
   - Navigate to "Interface Options"
   - Select "I2C"
   - Select "Yes" to enable
   - Select "Ok"

3. **Enable GPIO Remote Access (Optional)**
   - Navigate to "Interface Options"
   - Select "Remote GPIO"
   - Select "Yes" to enable
   - Select "Ok"

4. **Finish and Reboot**
   - Select "Finish"
   - Select "Yes" to reboot

## Hardware Setup

### GPIO Pin Layout Reference

```
3.3V    [ 1] [ 2]  5V
GPIO2   [ 3] [ 4]  5V
GPIO3   [ 5] [ 6]  GND
GPIO4   [ 7] [ 8]  GPIO14
GND     [ 9] [10] GPIO15
GPIO17  [11] [12] GPIO18
GPIO27  [13] [14] GND
GPIO22  [15] [16] GPIO23
3.3V    [17] [18] GPIO24
GPIO10  [19] [20] GND
GPIO9   [21] [22] GPIO25
GPIO11  [23] [24] GPIO8
GND     [25] [26] GPIO7
GPIO0   [27] [28] GPIO1
GPIO5   [29] [30] GND
GPIO6   [31] [32] GPIO12
GPIO13  [33] [34] GND
GPIO19  [35] [36] GPIO16
GPIO26  [37] [38] GPIO20
GND     [39] [40] GPIO21
```

### LED Indicators Setup

1. **Connect LEDs to Breadboard**
   - Green LED (Running indicator):
     - Connect long leg (anode) to a 220Ω resistor
     - Connect resistor to GPIO17 (Pin 11)
     - Connect short leg (cathode) to GND (Pin 9)
   
   - Blue LED (Actuator status):
     - Connect long leg (anode) to a 220Ω resistor
     - Connect resistor to GPIO27 (Pin 13)
     - Connect short leg (cathode) to GND (Pin 14)
   
   - Red LED (Online/Offline status):
     - Connect long leg (anode) to a 220Ω resistor
     - Connect resistor to GPIO22 (Pin 15)
     - Connect short leg (cathode) to GND (Pin 14)

### Reset Button Setup

1. **Connect Button to Breadboard**
   - Connect one terminal to GPIO4 (Pin 7)
   - Connect other terminal to GND (Pin 6)
   - No resistor needed as we'll use internal pull-up

### Buzzer Setup

1. **Connect Buzzer to Breadboard**
   - Connect positive terminal to GPIO18 (Pin 12)
   - Connect negative terminal to GND (Pin 14)

### SCD41 Sensor Connection (I2C)

1. **Connect SCD41 to Raspberry Pi**
   - VCC to 3.3V (Pin 1)
   - GND to GND (Pin 9)
   - SCL to GPIO3/SCL (Pin 5)
   - SDA to GPIO2/SDA (Pin 3)

## Software Installation

1. **Install Required Packages**
   ```bash
   sudo apt install -y python3-pip python3-venv git i2c-tools
   ```

2. **Verify I2C Connection**
   ```bash
   sudo i2cdetect -y 1
   ```
   - You should see the SCD41 device address (typically 0x62)

3. **Set Up Project Files**

   **Option A: Transfer Files via SCP (Recommended)**
   ```bash
   # From your local machine, transfer the project files
   scp -r /path/to/your/MASH-IoT-Device MASH@192.168.1.50:~/MASH-IoT-Device/
   ```

   **Option B: Use Git with Authentication**
   ```bash
   # Set up Git credentials (one-time setup)
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   
   # Clone with authentication
   git clone https://github.com/yourusername/MASH-IoT-Device.git
   cd MASH-IoT-Device
   ```

   **Option C: Use SSH Key Authentication**
   ```bash
   # Generate SSH key (if you don't have one)
   ssh-keygen -t ed25519 -C "your.email@example.com"
   
   # Add the public key to your GitHub account
   cat ~/.ssh/id_ed25519.pub
   
   # Clone using SSH
   git clone git@github.com:yourusername/MASH-IoT-Device.git
   cd MASH-IoT-Device
   ```

   **Option D: Manual File Transfer**
   - Use VS Code Remote SSH to upload files
   - Or use SFTP/SCP to transfer individual files

4. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Install Adafruit CircuitPython SCD4X Library**
   ```bash
   pip install adafruit-circuitpython-scd4x
   ```

7. **Configure Device**
   ```bash
   cp config/device_config.yaml config/device_config.local.yaml
   nano config/device_config.local.yaml
   ```
   - Update device ID, name, and other settings as needed

## Testing Components

### Test LEDs
1. Create a test script:
   ```bash
   nano test_leds.py
   ```

2. Add the following code:
   ```python
   import RPi.GPIO as GPIO
   import time
   
   # Setup GPIO
   GPIO.setmode(GPIO.BCM)
   GPIO.setwarnings(False)
   
   # Define pins
   GREEN_LED = 17
   BLUE_LED = 27
   RED_LED = 22
   
   # Setup pins
   GPIO.setup(GREEN_LED, GPIO.OUT)
   GPIO.setup(BLUE_LED, GPIO.OUT)
   GPIO.setup(RED_LED, GPIO.OUT)
   
   # Test LEDs
   print("Testing Green LED (Running indicator)")
   GPIO.output(GREEN_LED, GPIO.HIGH)
   time.sleep(1)
   GPIO.output(GREEN_LED, GPIO.LOW)
   
   print("Testing Blue LED (Actuator status)")
   GPIO.output(BLUE_LED, GPIO.HIGH)
   time.sleep(1)
   GPIO.output(BLUE_LED, GPIO.LOW)
   
   print("Testing Red LED (Online/Offline status)")
   GPIO.output(RED_LED, GPIO.HIGH)
   time.sleep(1)
   GPIO.output(RED_LED, GPIO.LOW)
   
   # Blink pattern test
   print("Testing blink pattern")
   for _ in range(3):
       GPIO.output(GREEN_LED, GPIO.HIGH)
       time.sleep(0.2)
       GPIO.output(GREEN_LED, GPIO.LOW)
       time.sleep(0.2)
   
   # Cleanup
   GPIO.cleanup()
   print("LED test complete")
   ```

3. Run the test:
   ```bash
   python test_leds.py
   ```

### Test Button
1. Create a test script:
   ```bash
   nano test_button.py
   ```

2. Add the following code:
   ```python
   import RPi.GPIO as GPIO
   import time
   
   # Setup GPIO
   GPIO.setmode(GPIO.BCM)
   GPIO.setwarnings(False)
   
   # Define pins
   BUTTON_PIN = 4
   
   # Setup pins with pull-up resistor
   GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
   
   print("Press the button (Ctrl+C to exit)...")
   
   try:
       while True:
           # Button is pressed when input is LOW
           if GPIO.input(BUTTON_PIN) == GPIO.LOW:
               print("Button pressed!")
               time.sleep(0.3)  # Debounce
   except KeyboardInterrupt:
       print("Test ended")
       GPIO.cleanup()
   ```

3. Run the test:
   ```bash
   python test_button.py
   ```

### Test Buzzer
1. Create a test script:
   ```bash
   nano test_buzzer.py
   ```

2. Add the following code:
   ```python
   import RPi.GPIO as GPIO
   import time
   
   # Setup GPIO
   GPIO.setmode(GPIO.BCM)
   GPIO.setwarnings(False)
   
   # Define pins
   BUZZER_PIN = 18
   
   # Setup pins
   GPIO.setup(BUZZER_PIN, GPIO.OUT)
   
   # Create PWM object
   buzzer = GPIO.PWM(BUZZER_PIN, 440)  # 440Hz - A4 note
   
   # Test patterns
   print("Testing buzzer...")
   
   # Single beep
   print("Single beep")
   buzzer.start(50)  # 50% duty cycle
   time.sleep(0.5)
   buzzer.stop()
   time.sleep(0.5)
   
   # Double beep
   print("Double beep")
   buzzer.start(50)
   time.sleep(0.2)
   buzzer.stop()
   time.sleep(0.2)
   buzzer.start(50)
   time.sleep(0.2)
   buzzer.stop()
   time.sleep(0.5)
   
   # Alarm pattern
   print("Alarm pattern")
   for _ in range(3):
       buzzer.start(50)
       time.sleep(0.1)
       buzzer.stop()
       time.sleep(0.1)
   
   # Cleanup
   GPIO.cleanup()
   print("Buzzer test complete")
   ```

3. Run the test:
   ```bash
   python test_buzzer.py
   ```

### Test SCD41 Sensor
1. Create a test script:
   ```bash
   nano test_scd41.py
   ```

2. Add the following code:
   ```python
   import time
   import board
   import busio
   import adafruit_scd4x
   
   # Create I2C bus
   i2c = busio.I2C(board.SCL, board.SDA)
   
   # Create SCD41 sensor
   scd41 = adafruit_scd4x.SCD4X(i2c)
   
   # Start periodic measurements
   print("Starting SCD41 measurements...")
   scd41.start_periodic_measurement()
   
   # Wait for first measurement
   print("Waiting for first measurement (5 seconds)...")
   time.sleep(5)
   
   # Read data
   print("Reading sensor data...")
   
   try:
       for i in range(10):  # Read 10 measurements
           if scd41.data_ready:
               print(f"CO2: {scd41.CO2} ppm")
               print(f"Temperature: {scd41.temperature:.2f} °C")
               print(f"Humidity: {scd41.relative_humidity:.2f} %")
               print("-" * 30)
           else:
               print("Data not ready yet")
           
           time.sleep(5)
       
       print("Test complete")
   
   except KeyboardInterrupt:
       print("Test interrupted")
   
   except Exception as e:
       print(f"Error: {e}")
   ```

3. Run the test:
   ```bash
   python test_scd41.py
   ```

## Running the MASH-IoT-Device Software

1. **Run the Main Application**
   ```bash
   cd ~/MASH-IoT-Device
   source venv/bin/activate
   python main.py
   ```

2. **Set Up as System Service**
   ```bash
   sudo nano /etc/systemd/system/mash-iot.service
   ```

3. **Add Service Configuration**
   ```
   [Unit]
   Description=MASH IoT Device Service
   After=network.target
   
   [Service]
   User=pi
   WorkingDirectory=/home/pi/MASH-IoT-Device
   ExecStart=/home/pi/MASH-IoT-Device/venv/bin/python main.py
   Restart=always
   RestartSec=10
   StandardOutput=syslog
   StandardError=syslog
   SyslogIdentifier=mash-iot
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Enable and Start Service**
   ```bash
   sudo systemctl enable mash-iot.service
   sudo systemctl start mash-iot.service
   ```

5. **Check Service Status**
   ```bash
   sudo systemctl status mash-iot.service
   ```

## Troubleshooting

### WiFi Connection Issues

1. **Check WiFi Status**
   ```bash
   sudo iwconfig wlan0
   ```
   - Look for "ESSID" to confirm connection

2. **Check IP Address**
   ```bash
   ip addr show wlan0
   ```
   - Should show an IP address

3. **Test Internet Connection**
   ```bash
   ping -c 4 google.com
   ```

4. **Common Solutions**
   - Verify SSID and password in wpa_supplicant.conf
   - Check WiFi country code is set correctly
   - Try moving closer to router
   - Restart networking: `sudo systemctl restart networking`
   - Reboot: `sudo reboot`

### I2C Connection Issues

1. **Check I2C Devices**
   ```bash
   sudo i2cdetect -y 1
   ```
   - Should show device at address 0x62 (SCD41)

2. **Check I2C Interface Status**
   ```bash
   lsmod | grep i2c
   ```
   - Should show i2c_bcm2835 and i2c_dev

3. **Common Solutions**
   - Verify I2C is enabled in raspi-config
   - Check wiring connections
   - Try different I2C pins or cables
   - Restart I2C: `sudo rmmod i2c_bcm2835; sudo modprobe i2c_bcm2835`

### GPIO Issues

1. **Check GPIO Status**
   ```bash
   gpio readall
   ```
   - Shows status of all GPIO pins

2. **Common Solutions**
   - Verify GPIO pin numbers (BCM vs Physical)
   - Check for loose connections
   - Verify resistors are correctly placed
   - Test with simple GPIO script

### SCD41 Sensor Issues

1. **Check Library Installation**
   ```bash
   pip list | grep adafruit
   ```
   - Should show adafruit-circuitpython-scd4x

2. **Common Solutions**
   - Reinstall library: `pip install --force-reinstall adafruit-circuitpython-scd4x`
   - Check power supply (3.3V)
   - Verify I2C address with `i2cdetect`
   - Try slower I2C clock: `sudo nano /boot/config.txt` and add `dtparam=i2c_arm_baudrate=10000`

### Service Issues

1. **Check Service Status**
   ```bash
   sudo systemctl status mash-iot.service
   ```

2. **View Service Logs**
   ```bash
   sudo journalctl -u mash-iot.service
   ```

3. **Common Solutions**
   - Check Python path in service file
   - Verify permissions on project directory
   - Check for Python errors in logs
   - Restart service: `sudo systemctl restart mash-iot.service`

### LED Indicator Reference

- **Green LED (Running)**
  - Steady on: System running normally
  - Fast blinking: System starting up
  - Slow blinking: System in maintenance mode
  - Off: System stopped or power issue

- **Blue LED (Actuator)**
  - On: At least one actuator active
  - Off: All actuators inactive

- **Red LED (Online/Offline)**
  - On: Connected to backend/MQTT
  - Off: Offline mode

- **Error Patterns**
  - All LEDs flashing together: Critical system error
  - Green LED off, Red LED blinking: Cannot connect to backend
  - Green LED blinking, Red LED on: Sensor error

## Advanced Configuration

### Headless Setup (No Monitor)

1. **Find Raspberry Pi IP**
   - Use router admin page
   - Use network scanner like Angry IP Scanner
   - Use `ping raspberrypi.local` or your hostname

2. **Connect via SSH**
   ```bash
   ssh pi@raspberrypi.local
   ```
   - Enter your password

### Remote Development

1. **Install Visual Studio Code on your PC**

2. **Install Remote SSH Extension**
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Remote - SSH"
   - Install the extension

3. **Connect to Raspberry Pi**
   - Press F1 and type "Remote-SSH: Connect to Host"
   - Enter `pi@raspberrypi.local` or `pi@IP_ADDRESS`
   - Select platform (Linux)
   - Enter password

4. **Open Project Folder**
   - Click "Open Folder"
   - Navigate to `/home/pi/MASH-IoT-Device`

### Backup and Restore

1. **Backup SD Card**
   - Shut down Raspberry Pi: `sudo shutdown now`
   - Remove SD card and insert into computer
   - Use Win32DiskImager to create an image file

2. **Backup Configuration**
   ```bash
   scp pi@raspberrypi.local:/home/pi/MASH-IoT-Device/config/device_config.local.yaml ./backup/
   ```

3. **Backup Database**
   ```bash
   scp pi@raspberrypi.local:/home/pi/MASH-IoT-Device/data/mash_device.db ./backup/
   ```

---

**Last Updated**: October 22, 2025  
**Author**: Jin Harold A. Failana  
**Version**: 1.0.0
