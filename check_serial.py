#!/usr/bin/env python3
"""
Serial Port Diagnostic Tool
Helps identify the correct serial port for Arduino connection
"""

import serial
import serial.tools.list_ports
import time

def list_serial_ports():
    """List all available serial ports"""
    print("=" * 60)
    print("Available Serial Ports:")
    print("=" * 60)
    
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ No serial ports found!")
        return []
    
    port_list = []
    for i, port in enumerate(ports, 1):
        print(f"\n{i}. Port: {port.device}")
        print(f"   Description: {port.description}")
        print(f"   Hardware ID: {port.hwid}")
        
        # Check if it's likely an Arduino
        if 'Arduino' in port.description or 'USB' in port.description:
            print(f"   ✅ Likely Arduino!")
        
        port_list.append(port.device)
    
    print("\n" + "=" * 60)
    return port_list


def test_serial_port(port, baud=9600):
    """Test connection to a specific serial port"""
    print(f"\n🔍 Testing {port} at {baud} baud...")
    
    try:
        ser = serial.Serial(port, baud, timeout=2)
        time.sleep(2)  # Wait for Arduino to reset
        
        print(f"✅ Successfully opened {port}")
        print(f"📡 Listening for data (10 seconds)...\n")
        
        start_time = time.time()
        data_received = False
        
        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"📥 {line}")
                        data_received = True
                        
                        # Check if it's MASH sensor data
                        if line.startswith('SENSOR,'):
                            print("\n✅ This is the correct port! MASH sensor data detected!")
                            break
                except Exception as e:
                    print(f"⚠️  Error reading: {e}")
            
            time.sleep(0.1)
        
        ser.close()
        
        if not data_received:
            print("\n⚠️  No data received. Arduino might not be sending data.")
        
        return data_received
        
    except serial.SerialException as e:
        print(f"❌ Failed to open {port}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("MASH IoT Device - Serial Port Diagnostic Tool")
    print("=" * 60 + "\n")
    
    # List all ports
    ports = list_serial_ports()
    
    if not ports:
        print("\n❌ No serial ports found. Check if Arduino is connected.")
        return
    
    # Test each port
    print("\n" + "=" * 60)
    print("Testing Ports for Arduino Data:")
    print("=" * 60)
    
    for port in ports:
        test_serial_port(port)
        print("\n" + "-" * 60)
    
    print("\n" + "=" * 60)
    print("Diagnostic Complete!")
    print("=" * 60)
    print("\nTo use the correct port, update integrated_server.py:")
    print("SERIAL_PORT = '/dev/ttyACM0'  # or /dev/ttyUSB0, etc.")
    print("\nCommon Arduino ports:")
    print("  - /dev/ttyACM0 (Arduino Uno/Mega)")
    print("  - /dev/ttyUSB0 (CH340 chip)")
    print("  - /dev/ttyAMA0 (Raspberry Pi serial)")
    print("\n")


if __name__ == "__main__":
    main()
