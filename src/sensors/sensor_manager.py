"""
Sensor Manager
Coordinates sensor operations and data collection
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, List
from queue import Queue, Empty

from .scd41_sensor import SCD41Sensor
from .sensor_reading import SensorReading


class SensorManager:
    """Manages sensor operations and continuous data collection"""
    
    def __init__(self, 
                 read_interval: int = 60,
                 mock_mode: bool = False,
                 calibration_offsets: Optional[dict] = None,
                 data_callback: Optional[Callable[[SensorReading], None]] = None):
        """
        Initialize sensor manager
        
        Args:
            read_interval: Seconds between sensor readings
            mock_mode: Use mock sensor data
            calibration_offsets: Temperature and humidity calibration offsets
            data_callback: Callback function for new sensor readings
        """
        self.logger = logging.getLogger(__name__)
        self.read_interval = read_interval
        self.data_callback = data_callback
        
        # Initialize sensor
        self.sensor = SCD41Sensor(mock_mode=mock_mode, calibration_offsets=calibration_offsets)
        
        # Threading control
        self._running = False
        self._thread = None
        self._stop_event = threading.Event()
        
        # Data queue for thread-safe communication
        self._data_queue = Queue()
        
        # Statistics
        self.reading_count = 0
        self.error_count = 0
        self.last_reading = None
        self.start_time = None
    
    def start(self) -> bool:
        """
        Start continuous sensor reading
        
        Returns:
            True if started successfully, False otherwise
        """
        if self._running:
            self.logger.warning("Sensor manager already running")
            return True
        
        try:
            self._running = True
            self._stop_event.clear()
            self.start_time = datetime.now()
            
            # Start reading thread
            self._thread = threading.Thread(target=self._reading_loop, daemon=True)
            self._thread.start()
            
            self.logger.info(f"Sensor manager started (interval: {self.read_interval}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start sensor manager: {e}")
            self._running = False
            return False
    
    def stop(self):
        """Stop continuous sensor reading"""
        if not self._running:
            return
        
        self.logger.info("Stopping sensor manager...")
        self._running = False
        self._stop_event.set()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        
        self.logger.info("Sensor manager stopped")
    
    def _reading_loop(self):
        """Main sensor reading loop (runs in separate thread)"""
        self.logger.info("Sensor reading loop started")
        
        while self._running and not self._stop_event.is_set():
            try:
                # Read sensor data
                reading = self.sensor.read_sensor_data()
                
                if reading:
                    # Validate reading
                    if self.sensor.validate_reading(reading):
                        self.reading_count += 1
                        self.last_reading = reading
                        
                        # Add to queue for processing
                        self._data_queue.put(reading)
                        
                        # Call callback if provided
                        if self.data_callback:
                            try:
                                self.data_callback(reading)
                            except Exception as e:
                                self.logger.error(f"Error in data callback: {e}")
                        
                        self.logger.debug(f"Reading #{self.reading_count}: {reading}")
                    else:
                        self.logger.warning(f"Invalid reading: {reading}")
                        self.error_count += 1
                else:
                    self.logger.warning("Failed to read sensor data")
                    self.error_count += 1
                
                # Wait for next reading
                if self._stop_event.wait(self.read_interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in reading loop: {e}")
                self.error_count += 1
                time.sleep(1)  # Brief pause before retry
        
        self.logger.info("Sensor reading loop ended")
    
    def get_latest_reading(self) -> Optional[SensorReading]:
        """
        Get the most recent sensor reading
        
        Returns:
            Latest SensorReading or None if no readings available
        """
        return self.last_reading
    
    def get_queued_readings(self, max_count: int = 10) -> List[SensorReading]:
        """
        Get queued sensor readings
        
        Args:
            max_count: Maximum number of readings to retrieve
            
        Returns:
            List of SensorReading objects
        """
        readings = []
        
        try:
            while len(readings) < max_count:
                reading = self._data_queue.get_nowait()
                readings.append(reading)
        except Empty:
            pass
        
        return readings
    
    def calibrate_sensor(self) -> bool:
        """
        Calibrate the sensor
        
        Returns:
            True if calibration successful, False otherwise
        """
        return self.sensor.calibrate()
    
    def get_statistics(self) -> dict:
        """Get sensor manager statistics"""
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'running': self._running,
            'read_interval': self.read_interval,
            'reading_count': self.reading_count,
            'error_count': self.error_count,
            'uptime_seconds': uptime,
            'queue_size': self._data_queue.qsize(),
            'last_reading': self.last_reading.to_dict() if self.last_reading else None,
            'sensor_info': self.sensor.get_sensor_info()
        }
    
    def is_running(self) -> bool:
        """Check if sensor manager is running"""
        return self._running
    
    def set_read_interval(self, interval: int):
        """
        Update sensor reading interval
        
        Args:
            interval: New interval in seconds
        """
        if interval < 1:
            raise ValueError("Read interval must be at least 1 second")
        
        self.read_interval = interval
        self.logger.info(f"Sensor read interval updated to {interval}s")
    
    def close(self):
        """Close sensor manager and cleanup resources"""
        self.stop()
        self.sensor.close()
        self.logger.info("Sensor manager closed")
