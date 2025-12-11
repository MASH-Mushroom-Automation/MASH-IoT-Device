#!/usr/bin/env python3
"""
Test script to send simulated sensor data to the integrated server
This simulates Arduino sending data via serial port
"""

import requests
import time
import random

# Server URL
BASE_URL = "http://localhost:5000/api"

def update_sensor_data_directly():
    """
    Directly update sensor data via API endpoint
    This is a workaround if Arduino is not connected
    """
    
    print("Simulating sensor data...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Generate random sensor data
            temperature = round(random.uniform(20.0, 28.0), 1)
            humidity = round(random.uniform(50.0, 90.0), 1)
            co2 = random.randint(300, 5000)
            mode = random.choice(['s', 'f'])
            
            # Print simulated data
            print(f"T:{temperature}°C, H:{humidity}%, CO2:{co2}ppm, Mode:{mode}")
            
            # Note: This would need an API endpoint to accept sensor data
            # For now, this is just a demonstration
            # The actual solution is to fix Arduino connection
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nStopped simulation")

def check_current_sensor_data():
    """Check what sensor data the server is currently returning"""
    try:
        response = requests.get(f"{BASE_URL}/sensor/current")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                sensor_data = data.get('data', {})
                print("\nCurrent sensor data from server:")
                print(f"  Temperature: {sensor_data.get('temperature', 0)}°C")
                print(f"  Humidity: {sensor_data.get('humidity', 0)}%")
                print(f"  CO2: {sensor_data.get('co2', 0)}ppm")
                print(f"  Mode: {sensor_data.get('mode', 'unknown')}")
                print(f"  Timestamp: {sensor_data.get('timestamp', 'N/A')}")
                
                if sensor_data.get('temperature', 0) == 0:
                    print("\n⚠️  WARNING: Sensor data is all zeros!")
                    print("   This means Arduino is not sending data.")
                    print("   Check:")
                    print("   1. Arduino is connected to /dev/ttyUSB0")
                    print("   2. Arduino code is running")
                    print("   3. Baud rate is 115200")
                    print("   4. Arduino is sending data in format: T:23.5,H:65.2,C:450.0,M:f")
                else:
                    print("\n✅ Sensor data looks good!")
            else:
                print("❌ Server returned success=false")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking sensor data: {e}")
        print("   Make sure integrated_server.py is running")

if __name__ == "__main__":
    print("=" * 60)
    print("MASH IoT Device - Sensor Data Test")
    print("=" * 60)
    
    # Check current sensor data
    check_current_sensor_data()
    
    print("\n" + "=" * 60)
    print("To fix sensor readings:")
    print("=" * 60)
    print("1. Connect Arduino to Raspberry Pi via USB")
    print("2. Upload Arduino code that sends data in format:")
    print("   T:23.5,H:65.2,C:450.0,M:f")
    print("3. Make sure Arduino sends data every 1-5 seconds")
    print("4. Check serial port: ls /dev/ttyUSB*")
    print("5. Test Arduino: python3 -c \"import serial; ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1); print(ser.readline())\"")
    print("6. Restart integrated_server.py")
    print("=" * 60)
