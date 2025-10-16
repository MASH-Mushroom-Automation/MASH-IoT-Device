"""
Sensor Reading Data Model
Represents a single sensor reading with metadata
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


@dataclass
class SensorReading:
    """Represents a single sensor reading"""
    
    # Core reading data
    temperature: float
    humidity: float
    co2_ppm: int
    
    # Metadata
    timestamp: datetime
    quality_indicator: str = 'good'  # 'good', 'uncertain', 'bad'
    device_id: Optional[str] = None
    reading_id: Optional[str] = None
    
    # Calibration offsets
    temp_offset: float = 0.0
    humidity_offset: float = 0.0
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation"""
        if self.reading_id is None:
            self.reading_id = str(uuid.uuid4())
        
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'id': self.reading_id,
            'device_id': self.device_id,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'co2_ppm': self.co2_ppm,
            'timestamp': self.timestamp.isoformat(),
            'quality_indicator': self.quality_indicator,
            'temp_offset': self.temp_offset,
            'humidity_offset': self.humidity_offset,
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SensorReading':
        """Create from dictionary (database retrieval)"""
        return cls(
            temperature=data['temperature'],
            humidity=data['humidity'],
            co2_ppm=data['co2_ppm'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            quality_indicator=data.get('quality_indicator', 'good'),
            device_id=data.get('device_id'),
            reading_id=data.get('id'),
            temp_offset=data.get('temp_offset', 0.0),
            humidity_offset=data.get('humidity_offset', 0.0),
            metadata=data.get('metadata', {})
        )
    
    def is_valid(self) -> bool:
        """Check if reading is within reasonable ranges"""
        return (
            -40 <= self.temperature <= 85 and
            0 <= self.humidity <= 100 and
            0 <= self.co2_ppm <= 100000
        )
    
    def apply_calibration(self) -> 'SensorReading':
        """Apply calibration offsets to readings"""
        return SensorReading(
            temperature=self.temperature + self.temp_offset,
            humidity=self.humidity + self.humidity_offset,
            co2_ppm=self.co2_ppm,
            timestamp=self.timestamp,
            quality_indicator=self.quality_indicator,
            device_id=self.device_id,
            reading_id=self.reading_id,
            temp_offset=self.temp_offset,
            humidity_offset=self.humidity_offset,
            metadata=self.metadata
        )
    
    def __str__(self) -> str:
        """String representation for logging"""
        return (f"SensorReading(t={self.temperature:.1f}°C, "
                f"h={self.humidity:.1f}%, co2={self.co2_ppm}ppm, "
                f"quality={self.quality_indicator})")
