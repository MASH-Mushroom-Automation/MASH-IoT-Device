#!/usr/bin/env python3
"""
MASH IoT Device - Test Script
Simple test script to verify device functionality
"""

import sys
import os
import time
import logging

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sensors import SensorManager, SensorReading
from storage import DatabaseManager
from utils.config import Config
from utils.logger import setup_logging


def test_sensor_manager():
    """Test sensor manager functionality"""
    print("Testing Sensor Manager...")
    
    # Setup logging
    setup_logging(level=logging.INFO)
    
    # Create sensor manager in mock mode
    sensor_manager = SensorManager(
        read_interval=5,  # 5 seconds for testing
        mock_mode=True,
        data_callback=lambda reading: print(f"New reading: {reading}")
    )
    
    try:
        # Start sensor manager
        if not sensor_manager.start():
            print("[ERROR] Failed to start sensor manager")
            return False
        
        print("[OK] Sensor manager started")
        
        # Wait for a few readings
        print("Collecting sensor readings...")
        time.sleep(15)  # Wait for 3 readings
        
        # Get latest reading
        latest = sensor_manager.get_latest_reading()
        if latest:
            print(f"[OK] Latest reading: {latest}")
        else:
            print("[ERROR] No readings available")
            return False
        
        # Get statistics
        stats = sensor_manager.get_statistics()
        print(f"[OK] Statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Sensor manager test failed: {e}")
        return False
    finally:
        sensor_manager.stop()
        print("[OK] Sensor manager stopped")


def test_database_manager():
    """Test database manager functionality"""
    print("\nTesting Database Manager...")
    
    try:
        # Create database manager
        db_manager = DatabaseManager('./test_data.db')
        print("[OK] Database manager created")
        
        # Test storing sensor reading
        test_reading = {
            'id': 'test_001',
            'device_id': 'test_device',
            'sensor_type': 'temperature',
            'value': 25.5,
            'unit': 'celsius',
            'quality_indicator': 'good',
            'metadata': {'test': True}
        }
        
        if db_manager.store_sensor_reading(test_reading):
            print("[OK] Sensor reading stored")
        else:
            print("[ERROR] Failed to store sensor reading")
            return False
        
        # Test retrieving unsynced readings
        readings = db_manager.get_unsynced_sensor_readings(limit=10)
        if readings:
            print(f"[OK] Retrieved {len(readings)} unsynced readings")
        else:
            print("[ERROR] No unsynced readings found")
            return False
        
        # Test database stats
        stats = db_manager.get_database_stats()
        print(f"[OK] Database stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Database manager test failed: {e}")
        return False


def test_config_manager():
    """Test configuration manager"""
    print("\nTesting Configuration Manager...")
    
    try:
        # Create config manager
        config = Config()
        print("[OK] Configuration manager created")
        
        # Test getting values
        device_id = config.get('device_id', 'default')
        print(f"[OK] Device ID: {device_id}")
        
        # Test setting values
        config.set('test_key', 'test_value')
        if config.get('test_key') == 'test_value':
            print("[OK] Configuration set/get working")
        else:
            print("[ERROR] Configuration set/get failed")
            return False
        
        # Test validation
        if config.validate():
            print("[OK] Configuration validation passed")
        else:
            print("[ERROR] Configuration validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Configuration manager test failed: {e}")
        return False


def test_integration():
    """Test integrated functionality"""
    print("\nTesting Integration...")
    
    try:
        # Setup logging
        setup_logging(level=logging.INFO)
        
        # Create components
        config = Config()
        db_manager = DatabaseManager('./test_integration.db')
        sensor_manager = SensorManager(
            read_interval=3,
            mock_mode=True,
            data_callback=lambda reading: store_reading(reading, db_manager)
        )
        
        def store_reading(reading: SensorReading, db: DatabaseManager):
            """Store reading in database"""
            reading_data = reading.to_dict()
            reading_data['device_id'] = 'test_device'
            reading_data['sensor_type'] = 'temperature'  # Add sensor type
            reading_data['unit'] = 'celsius'  # Add unit
            db.store_sensor_reading(reading_data)
            print(f"Stored: {reading}")
        
        # Start sensor manager
        if not sensor_manager.start():
            print("[ERROR] Failed to start sensor manager")
            return False
        
        print("[OK] Integration test started")
        
        # Wait for readings
        time.sleep(10)
        
        # Check database
        readings = db_manager.get_unsynced_sensor_readings()
        if readings:
            print(f"[OK] Integration test successful: {len(readings)} readings stored")
        else:
            print("[ERROR] No readings found in database")
            return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Integration test failed: {e}")
        return False
    finally:
        if 'sensor_manager' in locals():
            sensor_manager.stop()


def main():
    """Run all tests"""
    print("MASH IoT Device - Test Suite")
    print("=" * 40)
    
    tests = [
        ("Sensor Manager", test_sensor_manager),
        ("Database Manager", test_database_manager),
        ("Configuration Manager", test_config_manager),
        ("Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"[OK] {test_name} PASSED")
        else:
            print(f"[ERROR] {test_name} FAILED")
    
    print(f"\n{'='*40}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! Device is ready for deployment.")
        return 0
    else:
        print("[WARNING]  Some tests failed. Please check the implementation.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
