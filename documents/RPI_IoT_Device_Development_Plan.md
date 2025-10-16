# M.A.S.H. IoT Device Implementation Plan

## Raspberry Pi 3 Model B Controller (2-Week Sprint)

### Timeline: October 16 - October XX, 2025

---

## Phase 1: Foundation & Development Environment (Days 1-3)

### Day 1: Project Setup & Cross-Development Environment

**Objective:** Set up development environment for Windows → RPi deployment

#### Windows Development Setup

- Install Python 3.9+ on Windows
- Set up VSCode with Python extensions
- Install mock GPIO libraries for Windows testing
- Create virtual environment and install dependencies
- Initialize Git repository structure

#### Raspberry Pi 3 Model B Setup

- Flash latest Raspberry Pi OS (Lite or Desktop)
- Enable SSH and I2C interface
- Configure WiFi/network connectivity
- Install Python 3.9+ and pip
- Set up remote development (SSH from Windows)

#### Project Structure

```
MASH-IoT-Device/
├── src/
│   ├── sensors/          # Sensor drivers and interfaces
│   ├── actuators/        # Actuator control (mocked initially)
│   ├── display/          # LCD display (mocked initially)
│   ├── mqtt/             # MQTT client and communication
│   ├── storage/          # SQLite database operations
│   └── utils/            # Helper functions and configs
├── tests/                # Unit and integration tests
├── config/               # Configuration files
├── data/                 # Local data storage (SQLite)
├── logs/                 # Application logs
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # Setup and deployment guide
```

**Deliverables:**

- ✅ Working development environment on Windows
- ✅ RPi 3 Model B accessible via SSH
- ✅ Git repository initialized
- ✅ Project structure created

---

### Day 2: SCD41 Sensor Integration (Real Hardware)

**Objective:** Get real sensor data from SCD41 (Temperature, Humidity, CO₂)

#### SCD41 Sensor Driver Implementation

- Install `adafruit-circuitpython-scd4x` library
- Create sensor interface class with error handling
- Implement continuous sensor reading with threading
- Add sensor calibration and validation
- Create fallback for Windows simulation

#### Key Features

```python
class SCD41Sensor:
    def read_sensor_data(self) -> SensorReading:
        """Read temperature, humidity, CO2 from SCD41"""
        
    def calibrate(self) -> bool:
        """Perform sensor calibration"""
        
    def validate_reading(self, reading) -> bool:
        """Validate sensor data quality"""
```

**Testing Strategy:**

- Test on Windows with simulated data
- Deploy to RPi and test with real SCD41
- Verify I2C communication
- Log sensor readings to console

**Deliverables:**

- ✅ SCD41 sensor driver working on RPi
- ✅ Real-time sensor data collection
- ✅ Simulation mode for Windows testing
- ✅ Data validation and error handling

---

### Day 3: SQLite Local Storage & Data Persistence (Backend-Aligned)

**Objective:** Store sensor readings locally with offline capability, fully aligned with PostgreSQL backend schema

#### Database Schema Design (Aligned with Backend PostgreSQL)

**Backend API:** https://mash-backend.onrender.com/api

**Database:** Neon PostgreSQL (referenced in backend .env)

```sql
-- ================================================
-- LOCAL SQLITE SCHEMA FOR RASPBERRY PI IOT DEVICE
-- Aligned with Backend PostgreSQL Schema
-- ================================================

-- Device Info (Cached from backend after registration)
CREATE TABLE device_info (
    id TEXT PRIMARY KEY,                          -- UUID from backend
    user_id TEXT NOT NULL,                        -- Owner's UUID
    name TEXT NOT NULL,
    device_type TEXT DEFAULT 'MASH_CHAMBER',
    model TEXT DEFAULT 'RPi3-ModelB',
    serial_number TEXT,
    mac_address TEXT,
    firmware_version TEXT DEFAULT '1.0.0',
    hardware_version TEXT DEFAULT 'RPi3B',
    status TEXT DEFAULT 'offline',                -- online, offline, error, maintenance
    configuration TEXT,                            -- JSON string
    location TEXT,                                 -- JSON string
    timezone TEXT DEFAULT 'Asia/Manila',
    last_sync DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sensor Readings (Matches backend sensor_readings table)
CREATE TABLE sensor_readings (
    id TEXT PRIMARY KEY,                           -- Local UUID
    device_id TEXT NOT NULL,                       -- FK to device_info
    sensor_type TEXT NOT NULL,                     -- 'temperature', 'humidity', 'co2'
    value REAL NOT NULL,
    unit TEXT NOT NULL,                            -- 'celsius', 'percent', 'ppm'
    quality_indicator TEXT DEFAULT 'good',         -- 'good', 'uncertain', 'bad'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,                                 -- JSON string
    synced INTEGER DEFAULT 0,                      -- 0=pending, 1=synced
    backend_id TEXT,                               -- Backend UUID after sync
    sync_attempt_count INTEGER DEFAULT 0,
    last_sync_attempt DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES device_info(id)
);

CREATE INDEX idx_sensor_readings_device_timestamp 
    ON sensor_readings(device_id, timestamp DESC);
CREATE INDEX idx_sensor_readings_synced 
    ON sensor_readings(synced) WHERE synced = 0;

-- Device Commands (Matches backend device_commands table)
CREATE TABLE device_commands (
    id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL,
    user_id TEXT,
    command_type TEXT NOT NULL,
    command_data TEXT NOT NULL,                   -- JSON string
    status TEXT DEFAULT 'pending',
    sent_at DATETIME,
    acknowledged_at DATETIME,
    completed_at DATETIME,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 30,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES device_info(id)
);

-- Alerts (Matches backend alerts table)
CREATE TABLE alerts (
    id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,                       -- low, medium, high, critical
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    threshold_config TEXT,
    trigger_value REAL,
    current_value REAL,
    acknowledged INTEGER DEFAULT 0,
    acknowledged_by TEXT,
    acknowledged_at DATETIME,
    resolved INTEGER DEFAULT 0,
    resolved_by TEXT,
    resolved_at DATETIME,
    auto_resolve INTEGER DEFAULT 0,
    escalation_level INTEGER DEFAULT 1,
    metadata TEXT,
    synced INTEGER DEFAULT 0,
    backend_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES device_info(id)
);

-- Sync Queue (Manages upload queue)
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    priority INTEGER DEFAULT 1,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 5,
    last_attempt DATETIME,
    next_retry DATETIME,
    error_message TEXT,
    payload TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Configuration Cache (From backend + local settings)
CREATE TABLE config_cache (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    is_backend_config INTEGER DEFAULT 0,
    last_sync DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- System Logs
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,
    module TEXT NOT NULL,
    message TEXT NOT NULL,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Initial configuration (aligned with backend .env thresholds)
INSERT INTO config_cache (key, value, category) VALUES
    ('sensor_read_interval', '60', 'sensor'),
    ('temp_min', '25.0', 'control'),
    ('temp_max', '28.0', 'control'),
    ('temp_critical_high', '32.0', 'control'),
    ('humidity_min', '80.0', 'control'),
    ('humidity_max', '90.0', 'control'),
    ('co2_optimal_min', '10000', 'control'),
    ('co2_optimal_max', '15000', 'control'),
    ('co2_critical_high', '20000', 'control'),
    ('sync_interval', '300', 'sync'),
    ('batch_sync_size', '100', 'sync'),
    ('data_retention_days', '30', 'storage'),
    ('alert_cooldown_seconds', '900', 'alert');
```

#### Backend Integration

**API Endpoints (from backend):**

- Device Registration: `POST /api/devices`
- Sensor Sync: `POST /api/sensors/data`
- Alert Sync: `POST /api/alerts`
- Commands: `GET /api/devices/:id/commands`

**Environment Variables (from backend .env):**

```python
BACKEND_API_URL = "https://mash-backend.onrender.com/api"
MQTT_BROKER = os.getenv('MQTT_BROKER_URL', 'mqtt://localhost:1883')
JWT_SECRET = os.getenv('JWT_SECRET')  # For WebSocket auth
```

#### Storage Manager Implementation

- **UUID Generation:** Python uuid4 for PostgreSQL compatibility
- **DatabaseManager:** Connection pooling and transaction management
- **Batch Operations:** Bulk inserts (100 records/batch)
- **Sync Tracking:** Backend ID mapping after successful sync
- **Data Retention:** Auto-delete >30 day old synced records
- **Migrations:** Schema versioning for updates
- **Backup:** Pre-migration backups

**Deliverables:**

- ✅ SQLite schema aligned with PostgreSQL backend
- ✅ UUID-based primary keys
- ✅ Backend ID tracking for synced data
- ✅ Sync queue with retry logic
- ✅ Configuration matching backend thresholds
- ✅ Data transformation layer for API compatibility

---

## Phase 2: Hardware Abstraction & Simulation (Days 4-6)

### Day 4: Mock LCD Display System

**Objective:** Create LCD abstraction layer with console simulation

#### LCD Interface Design

```python
class LCDDisplay:
    """20x4 LCD Display abstraction (I2C)"""
    
    def __init__(self, mock_mode=True):
        """Initialize LCD or console mock"""
        
    def display_status(self, data: dict):
        """Show device status on LCD"""
        # Line 1: Temperature
        # Line 2: Humidity
        # Line 3: CO2 Level
        # Line 4: Device Status/Alerts
        
    def display_alert(self, alert: str):
        """Display critical alert"""
        
    def clear(self):
        """Clear display"""
```

#### Console Mock Implementation

- Create terminal-based LCD simulation with rich library
- Display real-time sensor data in formatted table
- Color-coded status indicators (green/yellow/red)
- Update display every 5 seconds

**Deliverables:**

- ✅ LCD abstraction layer
- ✅ Console-based mock for testing
- ✅ Real I2C LCD support (conditional, when available)
- ✅ Beautiful terminal UI for development

---

### Day 5: Mock Actuator Control System

**Objective:** Create actuator abstraction with simulation

#### Actuator Interface Design

```python
class ActuatorController:
    """Control fans, humidifiers, etc."""
    
    def __init__(self, mock_mode=True):
        """Initialize GPIO or mock actuators"""
        
    def control_humidifier(self, state: bool):
        """Turn humidifier ON/OFF"""
        
    def control_exhaust_fan(self, speed: int):
        """Control fan speed (0-100%)"""
        
    def control_blower_fan(self, state: bool):
        """Turn blower fan ON/OFF"""
        
    def get_actuator_status(self) -> dict:
        """Get current actuator states"""
```

#### Simulation Features

- Log all actuator commands to database
- Simulate actuator delays and transitions
- Create virtual device state machine
- Generate realistic power consumption metrics

**Deliverables:**

- ✅ Actuator abstraction layer
- ✅ Mock actuators with logging
- ✅ Ready for real GPIO integration
- ✅ State machine for device control

---

### Day 6: Environmental Control Logic

**Objective:** Implement automated environmental control algorithm

#### Control Algorithm Features

- **Temperature Control:** Target 25-28°C
- **Humidity Control:** Target 80-90% RH
- **CO₂ Management:** Monitor 10,000-15,000 ppm
- **Hysteresis Logic:** Prevent rapid on/off cycling
- **Safety Limits:** Emergency shutdown on extremes

#### Control Loop Implementation

```python
class EnvironmentalController:
    def process_sensor_data(self, reading: SensorReading):
        """Make control decisions based on sensor data"""
        
    def apply_control_strategy(self):
        """Execute control commands to actuators"""
        
    def check_safety_limits(self):
        """Emergency shutdown if needed"""
        
    def optimize_energy(self):
        """Minimize power consumption"""
```

**Deliverables:**

- ✅ Automated environmental control
- ✅ Safety limit enforcement
- ✅ Hysteresis-based control logic
- ✅ Logging of all control decisions

---

## Phase 3: MQTT & Backend Integration (Days 7-9)

### Day 7: MQTT Client Implementation

**Objective:** Connect to backend via MQTT for cloud communication

#### MQTT Configuration

```python
MQTT_BROKER = "mqtt://backend-mqtt-broker"
MQTT_PORT = 1883
MQTT_TOPICS = {
    'sensor_data': 'mash/device/{device_id}/sensors',
    'status': 'mash/device/{device_id}/status',
    'commands': 'mash/device/{device_id}/commands',
    'alerts': 'mash/device/{device_id}/alerts'
}
```

#### MQTT Client Features

- Automatic reconnection with exponential backoff
- Quality of Service (QoS) level 1 for reliability
- Batch sensor data transmission (every 60 seconds)
- Command subscription and handling
- Last Will and Testament (LWT) for connection monitoring

**Testing with Backend:**

- Use backend API at `https://mash-backend.onrender.com`
- Verify device registration endpoint
- Test sensor data ingestion
- Validate command reception

**Deliverables:**

- ✅ MQTT client with auto-reconnect
- ✅ Sensor data publishing to backend
- ✅ Command subscription working
- ✅ Connection monitoring

---

### Day 8: Offline-First Architecture & Data Sync

**Objective:** Ensure device works without internet, syncs when online

#### Sync Manager Implementation

```python
class SyncManager:
    def queue_sensor_data(self, data: list):
        """Queue data for upload when online"""
        
    def sync_to_backend(self):
        """Upload queued data to backend API"""
        
    def handle_failed_sync(self):
        """Retry with exponential backoff"""
        
    def cleanup_synced_data(self):
        """Remove successfully synced records"""
```

#### Features

- Store-and-forward pattern for sensor data
- Automatic sync when internet available
- Conflict resolution for device state
- Compression for batch uploads
- Bandwidth-aware sync throttling

**Deliverables:**

- ✅ Offline-first data collection
- ✅ Automatic sync when online
- ✅ Retry logic with backoff
- ✅ Optimized bandwidth usage

---

### Day 9: Alert System & Notifications

**Objective:** Generate and send alerts for critical conditions

#### Alert Engine

```python
class AlertEngine:
    def check_thresholds(self, reading: SensorReading):
        """Check if readings exceed thresholds"""
        
    def generate_alert(self, alert_type: str, severity: str):
        """Create alert record"""
        
    def send_to_backend(self, alert: Alert):
        """Publish alert via MQTT"""
        
    def local_notification(self, alert: Alert):
        """Display on LCD and log"""
```

#### Alert Types

- **Critical:** CO₂ > 20,000 ppm, Temp > 32°C
- **High:** Humidity < 70% or > 95%
- **Medium:** Approaching threshold limits
- **Low:** Minor deviations from optimal

**Deliverables:**

- ✅ Alert generation engine
- ✅ Multi-level alert severity
- ✅ Backend notification via MQTT
- ✅ Local LCD/console alerts

---

## Phase 4: Testing, Optimization & Deployment (Days 10-14)

### Day 10: Integration Testing

**Objective:** Test all components working together

#### Test Scenarios

- ✅ Sensor reading → Storage → Display loop
- ✅ Environmental control automation
- ✅ MQTT connectivity and failover
- ✅ Offline mode → Online sync
- ✅ Alert generation and transmission
- ✅ Command reception and execution

#### Performance Testing

- Monitor CPU and memory usage
- Test for memory leaks (24-hour run)
- Verify database performance
- Check MQTT message throughput

**Deliverables:**

- ✅ All integration tests passing
- ✅ 24-hour stability test completed
- ✅ Performance benchmarks recorded
- ✅ Bug fixes implemented

---

### Day 11: Error Handling & Recovery

**Objective:** Make system resilient to failures

#### Robustness Features

- Sensor read failure recovery
- I2C bus error handling
- Network disconnection handling
- Database corruption recovery
- Graceful degradation
- Automatic service restart on crash

#### Logging & Monitoring

```python
# Structured logging
logger.info("Sensor reading", extra={
    "temperature": 26.5,
    "humidity": 85.2,
    "co2": 1200
})

# Performance metrics
metrics.record("sensor_read_duration_ms", duration)
```

**Deliverables:**

- ✅ Comprehensive error handling
- ✅ Automatic recovery mechanisms
- ✅ Structured logging system
- ✅ System health monitoring

---

### Day 12: Configuration & Deployment Scripts

**Objective:** Easy deployment and configuration

#### Configuration Management

```python
# config.yml
device:
  id: "device_001"
  name: "Mushroom Chamber #1"
  location: "Greenhouse A"

sensors:
  scd41:
    read_interval: 60  # seconds
    calibration_offset:
      temperature: 0.0
      humidity: 0.0

mqtt:
  broker: "mqtt.mash-backend.com"
  port: 1883
  username: "device_001"
  use_tls: true

storage:
  retention_days: 30
  sync_interval: 300  # seconds
  batch_size: 100
```

#### Deployment Automation

```bash
# deploy.sh
#!/bin/bash
# Automated deployment script

# 1. Pull latest code from Git
# 2. Install/update dependencies
# 3. Run database migrations
# 4. Restart service
# 5. Verify health check
```

**Deliverables:**

- ✅ Configuration file system
- ✅ One-command deployment script
- ✅ Service installation (systemd)
- ✅ Automatic startup on boot

---

### Day 13: Documentation & User Guide

**Objective:** Complete documentation for setup and operation

#### Documentation Deliverables

1. **README.md** - Quick start guide
2. **SETUP.md** - Detailed hardware setup
3. **DEPLOYMENT.md** - Software deployment
4. **API.md** - MQTT message formats
5. **TROUBLESHOOTING.md** - Common issues

#### Hardware Setup Guide

- SCD41 sensor wiring diagram
- I2C LCD connection (for future)
- GPIO pin mapping for actuators
- Power supply requirements
- Safety precautions

**Deliverables:**

- ✅ Complete documentation set
- ✅ Hardware wiring diagrams
- ✅ Step-by-step setup guides
- ✅ Troubleshooting guide

---

### Day 14: Final Testing & Handover

**Objective:** Production-ready system

#### Final Checklist

- ✅ All features working as specified
- ✅ Runs continuously for 48 hours without issues
- ✅ Backend integration verified
- ✅ Documentation complete
- ✅ Code cleaned and commented
- ✅ Git repository organized
- ✅ Demo video/presentation ready

#### Production Deployment

- Deploy to RPi 3 Model B
- Configure as systemd service
- Set up automatic updates
- Enable remote monitoring
- Create backup/restore procedure

**Final Deliverables:**

- ✅ Production-ready IoT device software
- ✅ Complete documentation
- ✅ Deployment automation
- ✅ Handover presentation

---

## Technical Stack Summary

### Core Technologies

- **Python 3.9+** - Main programming language
- **Adafruit CircuitPython** - SCD41 sensor library
- **Paho MQTT** - MQTT client
- **SQLite3** - Local database
- **RPi.GPIO** - GPIO control (when actuators added)
- **Pillow/PIL** - LCD display rendering
- **Rich** - Terminal UI for simulation

### Development Tools

- **VSCode** - IDE with Remote SSH
- **Git** - Version control
- **pytest** - Testing framework
- **Black** - Code formatting
- **Pylint** - Code quality

### Backend Integration

- **API:** https://mash-backend.onrender.com/api
- **MQTT Broker:** Backend-provided
- **WebSocket:** For real-time updates (future)

---

## Risk Mitigation

### Hardware Risks

- **Missing hardware:** Use simulation mode
- **Sensor failure:** Graceful degradation
- **I2C issues:** Error recovery and logging

### Software Risks

- **Backend downtime:** Offline-first design
- **Network issues:** Store-and-forward
- **Bugs:** Comprehensive testing

### Timeline Risks

- **2-week deadline:** Focus on core features first
- **Scope creep:** Stick to simulation for missing hardware
- **Integration issues:** Early backend API testing

---

## Success Criteria

✅ **Must Have (MVP)**

1. Real SCD41 sensor data collection
2. Local SQLite storage
3. MQTT communication with backend
4. Offline capability with sync
5. Console-based monitoring
6. Automated environmental logic (simulation)

⭐ **Nice to Have**

1. I2C LCD integration (when hardware arrives)
2. Real actuator control (when hardware arrives)
3. Advanced analytics
4. Web dashboard on RPi

---

## Post-Implementation Plan

### When I2C LCD Arrives

- Replace console mock with real LCD driver
- Update display manager to use I2C
- Test LCD update frequency

### When Actuators Arrive

- Replace GPIO mocks with real GPIO control
- Calibrate actuator responses
- Implement safety interlocks
- Test control loop with real devices

### Future Enhancements

- Camera module integration (contamination detection)
- Power consumption monitoring
- Predictive maintenance alerts
- Multi-device coordination

---

**Plan Version:** 1.0

**Created:** October 16, 2025

**Target Completion:** October 31, 2025

**Lead Developer:** Hardware Programmer - Jin Harold A. Failana