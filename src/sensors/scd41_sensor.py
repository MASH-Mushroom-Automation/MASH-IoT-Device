"""
SCD41 CO2, Temperature, and Humidity Sensor Driver
Handles I2C communication with SCD41 sensor
"""

import time
import logging
from typing import Optional, Tuple
from datetime import datetime

try:
    import board
    import busio
    from adafruit_scd4x import SCD4X
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    # Mock classes for Windows development
    class SCD4X:
        def __init__(self, *args, **kwargs):
            self.temperature = 25.0
            self.relative_humidity = 80.0
            self.co2 = 1000
        
        def start_periodic_measurement(self):
            pass
        
        def data_ready(self):
            return True
        
        def measure(self):
            pass

from .sensor_reading import SensorReading


class SCD41Sensor:
    """SCD41 CO2, Temperature, and Humidity Sensor Driver"""
    
    def __init__(self, mock_mode: bool = False, calibration_offsets: Optional[dict] = None):
        """
        Initialize SCD41 sensor
        
        Args:
            mock_mode: Use mock data instead of real hardware
            calibration_offsets: Dict with 'temp' and 'humidity' offset values
        """
        self.logger = logging.getLogger(__name__)
        self.mock_mode = mock_mode or not HARDWARE_AVAILABLE
        self.calibration_offsets = calibration_offsets or {}
        
        self.sensor = None
        self.is_initialized = False
        self.last_reading_time = None
        
        # Initialize sensor
        self._initialize_sensor()
    
    def _initialize_sensor(self) -> bool:
        """Initialize the SCD41 sensor hardware"""
        try:
            if self.mock_mode:
                self.logger.info("SCD41 sensor running in mock mode")
                self.sensor = SCD4X()  # Mock sensor
                self.is_initialized = True
                return True
            
            if not HARDWARE_AVAILABLE:
                self.logger.warning("Hardware libraries not available, falling back to mock mode")
                self.mock_mode = True
                self.sensor = SCD4X()
                self.is_initialized = True
                return True
            
            # Initialize I2C bus
            # For I2C1 bus (pins 27, 28) - use board.SCL1 and board.SDA1
            # For I2C0 bus (pins 3, 5) - use board.SCL and board.SDA
            try:
                # Try I2C1 first (pins 27, 28)
                i2c = busio.I2C(board.SCL1, board.SDA1)
                self.logger.info("Using I2C1 bus (pins 27, 28)")
            except AttributeError:
                # Fallback to I2C0 (pins 3, 5)
                i2c = busio.I2C(board.SCL, board.SDA)
                self.logger.info("Using I2C0 bus (pins 3, 5)")
            
            self.sensor = SCD4X(i2c)
            
            # Start periodic measurement
            self.sensor.start_periodic_measurement()
            self.logger.info("SCD41 sensor initialized successfully")
            self.is_initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize SCD41 sensor: {e}")
            self.logger.info("Falling back to mock mode")
            self.mock_mode = True
            self.sensor = SCD4X()
            self.is_initialized = True
            return False
    
    def read_sensor_data(self) -> Optional[SensorReading]:
        """
        Read temperature, humidity, and CO2 from SCD41 sensor
        
        Returns:
            SensorReading object or None if reading failed
        """
        if not self.is_initialized:
            self.logger.error("Sensor not initialized")
            return None
        
        try:
            if self.mock_mode:
                # Generate realistic mock data with some variation
                import random
                base_temp = 26.0 + random.uniform(-2, 2)
                base_humidity = 85.0 + random.uniform(-5, 5)
                base_co2 = 1200 + random.randint(-200, 200)
                
                reading = SensorReading(
                    temperature=base_temp,
                    humidity=base_humidity,
                    co2_ppm=base_co2,
                    timestamp=datetime.now(),
                    temp_offset=self.calibration_offsets.get('temp', 0.0),
                    humidity_offset=self.calibration_offsets.get('humidity', 0.0)
                )
            else:
                # Check if data is ready
                if not self.sensor.data_ready:
                    self.logger.debug("Sensor data not ready")
                    return None
                
                # Read sensor data
                self.sensor.measure()
                
                reading = SensorReading(
                    temperature=self.sensor.temperature,
                    humidity=self.sensor.relative_humidity,
                    co2_ppm=self.sensor.co2,
                    timestamp=datetime.now(),
                    temp_offset=self.calibration_offsets.get('temp', 0.0),
                    humidity_offset=self.calibration_offsets.get('humidity', 0.0)
                )
            
            # Apply calibration offsets
            reading = reading.apply_calibration()
            
            # Validate reading
            if not reading.is_valid():
                self.logger.warning(f"Invalid sensor reading: {reading}")
                reading.quality_indicator = 'bad'
            else:
                reading.quality_indicator = 'good'
            
            self.last_reading_time = datetime.now()
            self.logger.debug(f"Sensor reading: {reading}")
            return reading
            
        except Exception as e:
            self.logger.error(f"Failed to read sensor data: {e}")
            return None
    
    def calibrate(self) -> bool:
        """
        Perform sensor calibration
        
        Returns:
            True if calibration successful, False otherwise
        """
        if self.mock_mode:
            self.logger.info("Mock sensor calibration completed")
            return True
        
        try:
            # SCD41 doesn't require manual calibration
            # It performs automatic self-calibration
            self.logger.info("SCD41 sensor calibration completed")
            return True
        except Exception as e:
            self.logger.error(f"Sensor calibration failed: {e}")
            return False
    
    def validate_reading(self, reading: SensorReading) -> bool:
        """
        Validate sensor reading quality
        
        Args:
            reading: SensorReading to validate
            
        Returns:
            True if reading is valid, False otherwise
        """
        if not reading:
            return False
        
        # Check basic validity
        if not reading.is_valid():
            return False
        
        # Check for reasonable ranges for mushroom cultivation
        temp_ok = 15 <= reading.temperature <= 35
        humidity_ok = 50 <= reading.humidity <= 100
        co2_ok = 400 <= reading.co2_ppm <= 50000
        
        if not (temp_ok and humidity_ok and co2_ok):
            self.logger.warning(f"Reading outside expected ranges: {reading}")
            return False
        
        return True
    
    def get_sensor_info(self) -> dict:
        """Get sensor information and status"""
        return {
            'sensor_type': 'SCD41',
            'mock_mode': self.mock_mode,
            'initialized': self.is_initialized,
            'last_reading': self.last_reading_time.isoformat() if self.last_reading_time else None,
            'calibration_offsets': self.calibration_offsets
        }
    
    def close(self):
        """Close sensor connection"""
        if self.sensor and not self.mock_mode:
            try:
                # SCD41 doesn't have explicit close method
                pass
            except Exception as e:
                self.logger.error(f"Error closing sensor: {e}")
        
        self.is_initialized = False
        self.logger.info("SCD41 sensor closed")
