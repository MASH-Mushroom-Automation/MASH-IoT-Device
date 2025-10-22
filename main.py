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
from typing import Optional, Dict, Any

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sensors import SensorManager, SensorReading
from storage import DatabaseManager
from utils.config import Config
from utils.logger import setup_logging
from mqtt import MQTTClient
from api import APIServer
from discovery import MDNSService


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
        self.mqtt_client = None
        self.api_server = None
        self.mdns_service = None
        
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
            
            # Create required directories
            self._ensure_directories()
            
            # Get device ID
            device_id = self.config.get('device.id', 'mash-device-001')
            mock_mode = self.config.get('development.mock_mode', False)
            
            # Initialize database
            self.database = DatabaseManager(
                db_path=self.config.get('database.path', './data/mash_device.db'),
                timeout=self.config.get('database.timeout', 30)
            )
            
            # Initialize sensor manager
            self.sensor_manager = SensorManager(
                read_interval=self.config.get('sensors.scd41.read_interval', 60),
                mock_mode=mock_mode,
                calibration_offsets={
                    'temp': self.config.get('sensors.scd41.calibration.temperature_offset', 0.0),
                    'humidity': self.config.get('sensors.scd41.calibration.humidity_offset', 0.0)
                },
                data_callback=self._on_sensor_reading
            )
            
            # Initialize MQTT client
            self.mqtt_client = MQTTClient(
                broker_url=self.config.get('mqtt.broker_url', 'mqtt://localhost:1883'),
                client_id=self.config.get('mqtt.client_id', device_id),
                username=self.config.get('mqtt.username', ''),
                password=self.config.get('mqtt.password', ''),
                keepalive=self.config.get('mqtt.keepalive', 60),
                qos=self.config.get('mqtt.qos', 1),
                mock_mode=mock_mode
            )
            
            # Register MQTT command handlers
            self.mqtt_client.register_command_handler('sensor_config', self._handle_sensor_config_command)
            self.mqtt_client.register_command_handler('device_reboot', self._handle_device_reboot_command)
            
            # Initialize API server
            self.api_server = APIServer(
                host='0.0.0.0',
                port=5000,
                debug=self.config.get('development.debug_mode', False),
                mock_mode=mock_mode
            )
            
            # Register API callbacks
            self.api_server.register_sensor_data_callback(self._get_latest_sensor_data)
            self.api_server.register_device_status_callback(self.get_status)
            self.api_server.register_command_handler('sensor_config', self._handle_sensor_config_command)
            
            # Initialize mDNS service
            self.mdns_service = MDNSService(
                device_id=device_id,
                service_name=self.config.get('device.name', 'MASH IoT Device'),
                port=5000,
                mock_mode=mock_mode
            )
            
            self.logger.info("Device initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Device initialization failed: {e}")
            return False
            
    def _ensure_directories(self):
        """Create required directories if they don't exist"""
        try:
            import os
            
            # Create data directory
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            self.logger.debug(f"Created/verified data directory: {data_dir}")
            
            # Create logs directory
            logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            self.logger.debug(f"Created/verified logs directory: {logs_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to create directories: {e}")
            raise
    
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
            
            # Start MQTT client
            if self.mqtt_client:
                if not self.mqtt_client.connect():
                    self.logger.warning("Failed to connect MQTT client, will retry later")
                    # Continue anyway - MQTT is not critical
            
            # Start API server
            if self.api_server:
                if not self.api_server.start():
                    self.logger.warning("Failed to start API server")
                    # Continue anyway - API is not critical
            
            # Start mDNS service
            if self.mdns_service:
                if not self.mdns_service.start():
                    self.logger.warning("Failed to start mDNS service")
                    # Continue anyway - mDNS is not critical
            
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
        
        # Stop MQTT client
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        
        # Stop API server
        if self.api_server:
            self.api_server.stop()
        
        # Stop mDNS service
        if self.mdns_service:
            self.mdns_service.stop()
        
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
            reading_data['device_id'] = self.config.get('device.id', 'default_device')
            reading_data['sensor_type'] = 'temperature'  # Default sensor type
            reading_data['unit'] = 'celsius'  # Default unit
            
            if self.database.store_sensor_reading(reading_data):
                self.logger.debug(f"Stored sensor reading: {reading}")
            else:
                self.logger.error(f"Failed to store sensor reading: {reading}")
            
            # Publish telemetry data via MQTT
            if self.mqtt_client and self.mqtt_client.connected:
                self.mqtt_client.publish_telemetry(reading_data)
            
        except Exception as e:
            self.logger.error(f"Error processing sensor reading: {e}")
    
    def _get_latest_sensor_data(self) -> Dict[str, Any]:
        """
        Get latest sensor data for API
        
        Returns:
            Dictionary with latest sensor readings
        """
        if self.sensor_manager:
            return self.sensor_manager.get_latest_readings()
        return {}
    
    def _handle_sensor_config_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle sensor configuration command
        
        Args:
            command_data: Command data
            
        Returns:
            Result of command execution
        """
        try:
            if 'read_interval' in command_data:
                new_interval = int(command_data['read_interval'])
                if self.sensor_manager:
                    self.sensor_manager.set_read_interval(new_interval)
                    self.logger.info(f"Updated sensor read interval to {new_interval} seconds")
                    return {"success": True, "new_interval": new_interval}
            
            return {"success": False, "error": "Invalid command data"}
        except Exception as e:
            self.logger.error(f"Error handling sensor config command: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_device_reboot_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle device reboot command
        
        Args:
            command_data: Command data
            
        Returns:
            Result of command execution
        """
        try:
            delay = int(command_data.get('delay', 5))
            self.logger.info(f"Received reboot command, will reboot in {delay} seconds")
            
            # Schedule reboot in a separate thread
            import threading
            threading.Thread(target=self._delayed_reboot, args=(delay,), daemon=True).start()
            
            return {"success": True, "reboot_in": delay}
        except Exception as e:
            self.logger.error(f"Error handling reboot command: {e}")
            return {"success": False, "error": str(e)}
    
    def _delayed_reboot(self, delay: int):
        """
        Perform delayed reboot
        
        Args:
            delay: Delay in seconds
        """
        try:
            time.sleep(delay)
            self.logger.info("Executing reboot command")
            
            # Stop all services
            self.stop()
            
            # Execute reboot command
            import subprocess
            subprocess.call(['sudo', 'reboot'])
        except Exception as e:
            self.logger.error(f"Failed to reboot: {e}")
    
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
                'device_id': self.config.get('device.id'),
                'mock_mode': self.config.get('development.mock_mode', False),
                'sensor_interval': self.config.get('sensors.scd41.read_interval', 60)
            }
        }
        
        if self.sensor_manager:
            status['sensor_manager'] = self.sensor_manager.get_statistics()
        
        if self.database:
            status['database'] = self.database.get_database_stats()
        
        if self.mqtt_client:
            status['mqtt'] = {'connected': getattr(self.mqtt_client, 'connected', False)}
        
        if self.api_server:
            status['api'] = {'running': getattr(self.api_server, 'running', False)}
        
        return status


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='MASH IoT Device')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--mock', action='store_true', help='Run in mock mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--status', action='store_true', help='Show device status and exit')
    parser.add_argument('--provision', action='store_true', help='Run in provisioning mode')
    
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
            device.config.set('development.mock_mode', True)
        
        # Set provisioning mode if specified
        if args.provision:
            device.config.set('provisioning_mode', True)
        
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