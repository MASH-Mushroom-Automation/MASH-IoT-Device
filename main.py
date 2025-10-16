#!/usr/bin/env python3
"""
MASH IoT Device - Main Application
Raspberry Pi controller for mushroom cultivation automation
"""

import os
import sys
import time
import signal
import logging
import argparse
from datetime import datetime
from typing import Optional

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sensors import SensorManager, SensorReading
from storage import DatabaseManager
from utils.config import Config
from utils.logger import setup_logging


class MASHDevice:
    """Main MASH IoT Device application"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MASH device
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.running = False
        
        # Load configuration
        self.config = Config(config_path)
        
        # Initialize components
        self.database = None
        self.sensor_manager = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def initialize(self) -> bool:
        """
        Initialize all device components
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing MASH IoT Device...")
            
            # Initialize database
            self.database = DatabaseManager(
                db_path=self.config.get('database_path', './data/mash_device.db'),
                timeout=self.config.get('sqlite_timeout', 30)
            )
            
            # Initialize sensor manager
            self.sensor_manager = SensorManager(
                read_interval=self.config.get('sensor_read_interval', 60),
                mock_mode=self.config.get('mock_mode', False),
                calibration_offsets={
                    'temp': self.config.get('sensor_calibration_offset_temp', 0.0),
                    'humidity': self.config.get('sensor_calibration_offset_humidity', 0.0)
                },
                data_callback=self._on_sensor_reading
            )
            
            self.logger.info("Device initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Device initialization failed: {e}")
            return False
    
    def start(self) -> bool:
        """
        Start the device operation
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            self.logger.info("Starting MASH IoT Device...")
            
            # Start sensor manager
            if not self.sensor_manager.start():
                self.logger.error("Failed to start sensor manager")
                return False
            
            self.running = True
            self.logger.info("MASH IoT Device started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start device: {e}")
            return False
    
    def run(self):
        """Main application loop"""
        try:
            while self.running:
                # Main application logic here
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the device and cleanup resources"""
        if not self.running:
            return
        
        self.logger.info("Stopping MASH IoT Device...")
        self.running = False
        
        # Stop sensor manager
        if self.sensor_manager:
            self.sensor_manager.stop()
        
        self.logger.info("MASH IoT Device stopped")
    
    def _on_sensor_reading(self, reading: SensorReading):
        """
        Callback for new sensor readings
        
        Args:
            reading: New sensor reading
        """
        try:
            # Store reading in database
            reading_data = reading.to_dict()
            reading_data['device_id'] = self.config.get('device_id', 'default_device')
            reading_data['sensor_type'] = 'temperature'  # Default sensor type
            reading_data['unit'] = 'celsius'  # Default unit
            
            if self.database.store_sensor_reading(reading_data):
                self.logger.debug(f"Stored sensor reading: {reading}")
            else:
                self.logger.error(f"Failed to store sensor reading: {reading}")
            
        except Exception as e:
            self.logger.error(f"Error processing sensor reading: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def get_status(self) -> dict:
        """Get device status"""
        status = {
            'running': self.running,
            'timestamp': datetime.now().isoformat(),
            'config': {
                'device_id': self.config.get('device_id'),
                'mock_mode': self.config.get('mock_mode', False),
                'sensor_interval': self.config.get('sensor_read_interval', 60)
            }
        }
        
        if self.sensor_manager:
            status['sensor_manager'] = self.sensor_manager.get_statistics()
        
        if self.database:
            status['database'] = self.database.get_database_stats()
        
        return status


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='MASH IoT Device')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--mock', action='store_true', help='Run in mock mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--status', action='store_true', help='Show device status and exit')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(level=log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("MASH IoT Device starting...")
    
    try:
        # Create device instance
        device = MASHDevice(config_path=args.config)
        
        # Override mock mode if specified
        if args.mock:
            device.config.set('mock_mode', True)
        
        # Initialize device
        if not device.initialize():
            logger.error("Device initialization failed")
            sys.exit(1)
        
        # Show status and exit if requested
        if args.status:
            status = device.get_status()
            print(f"Device Status: {status}")
            sys.exit(0)
        
        # Start device
        if not device.start():
            logger.error("Failed to start device")
            sys.exit(1)
        
        # Run main loop
        device.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
