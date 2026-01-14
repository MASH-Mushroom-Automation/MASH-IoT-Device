# MASH IoT Device Development Tasks

## Repository Analysis Summary

### Current Implementation Status

**Working Features:**
1. Backend device lookup and registration (device ID, IP, MAC, status updates)
2. Mobile app communication (real-time sensor data and actuator status)
3. Local database logging (SQLite-based data storage)

**In Progress / Not Yet Working:**
- Firebase Realtime Database integration (implemented but not working)
- MQTT messaging system (implemented but not yet tested/working)
- Touchscreen UI (implemented but not yet tested on actual hardware)

**Core Files in Use:**
- `integrated_server.py` - Main server orchestrating all components
- `src/backend_client.py` - Backend API communication
- `data_logger.py` - Local SQLite logging
- `rule_based_controller.py` - Mathematical threshold automation
- `src/utils/config.py` - Configuration management
- `src/utils/bluetooth_*.py` - Bluetooth provisioning modules
- `src/discovery/mdns_service.py` - Local network discovery

**Core Files Implemented (Not Yet Tested):**
- `src/firebase_client.py` - Real-time Firebase sync (needs testing)
- `touchscreen_ui/main.py` - Kivy-based local touchscreen interface (needs hardware testing)
- `touchscreen_ui/screens/*.py` - Dashboard, controls, WiFi setup, settings screens (needs testing)
- `touchscreen_ui/api_client.py` - Local API client for integrated_server (needs testing)
- `touchscreen_ui/mqtt_client.py` - MQTT client for real-time messaging (needs testing)

---

# [IOT-001] Complete IoT Device System Integration and Enhancement #1

## Epic Overview

Enhance and complete the MASH IoT device system to provide reliable mushroom chamber monitoring, control, and connectivity across local networks and cloud infrastructure. Address current integration gaps, improve stability, and implement missing features for production deployment.

### Business Objectives

- Ensure reliable real-time sensor monitoring and actuator control
- Enable seamless device provisioning via WiFi and Bluetooth
- Provide robust offline-first operation with cloud synchronization
- Implement comprehensive error handling and recovery mechanisms
- Support mobile app integration with real-time updates
- Enable secure and authenticated device-to-backend communication
- Provide local touchscreen interface for manual configuration and offline operation

### Epic Scope

This epic encompasses the complete IoT device experience from initial setup through ongoing operations:

1. Core System Integration and Stability - Issues #2-#6
2. Sensor and Data Management - Issues #7-#11
3. Actuator Control System - Issues #12-#16
4. Network and Connectivity - Issues #17-#21
5. Backend and Cloud Sync - Issues #22-#26
6. Mobile App Integration - Issues #27-#31
7. Touchscreen UI and Local Control - Issues #32-#36
8. Monitoring and Diagnostics - Issues #37-#41

### Success Metrics

- Device uptime greater than 99.5%
- Sensor reading accuracy within ±2% tolerance
- Backend sync latency under 5 seconds
- Mobile app connection success rate above 95%
- Average device provisioning time under 3 minutes
- Zero data loss during network interruptions
- Touchscreen UI responsiveness at 60 FPS with <100ms latency

### Timeline

Start Date: December 18, 2025
Target Completion: January 15, 2026
Total Tasks: 40 child issues

### Dependencies

- MASH Backend API (in progress)
- MASH Mobile App (parallel development)
- Firebase Realtime Database (configured)
- Arduino sensor firmware (completed)
- Raspberry Pi 3 hardware setup (completed)
- 7" Touchscreen display (480x320 or 800x480) (configured)

---

## Issue Categories and Tasks

### 1. Core System Integration and Stability

#### [IOT-002] Application Lifecycle and Error Handling #2
**Task Description**

Implement comprehensive application lifecycle management including graceful startup, shutdown, error recovery, and health monitoring for the integrated server.

**Acceptance Criteria**

- Graceful startup sequence with dependency initialization
- Clean shutdown handling (SIGTERM, SIGINT)
- Automatic recovery from component failures
- Health check endpoint with component status
- Watchdog timer for critical components
- Systemd service integration improvements
- Startup error logging and diagnostics

**Deliverables**

- Enhanced `integrated_server.py` with lifecycle management
- Health monitoring module
- Error recovery mechanisms
- Updated systemd service configuration
- Startup diagnostics script

**Technical Notes**

- Use signal handlers for graceful shutdown
- Implement retry logic with exponential backoff
- Add component dependency checks
- Log all lifecycle events to local database

---

#### [IOT-003] Configuration Management Enhancements #3
**Task Description**

Enhance the configuration system to support runtime updates, validation, backup/restore, and multi-environment configurations.

**Acceptance Criteria**

- Runtime configuration reload without restart
- Configuration validation with detailed error messages
- Configuration backup and restore functionality
- Environment-specific configs (development, production)
- Secure credential management
- Configuration version tracking
- Default fallback values for all settings

**Deliverables**

- Enhanced `src/utils/config.py` module
- Configuration validation schemas
- Config backup/restore utilities
- Environment configuration templates
- Configuration migration guide

**Technical Notes**

- Use YAML for human-readable configs
- Implement configuration change listeners
- Validate on load and before applying changes
- Support hot-reload for non-critical settings

---

#### [IOT-004] Threading and Concurrency Improvements #4
**Task Description**

Improve thread management for sensor reading, automation control, and data synchronization to prevent race conditions and ensure reliable concurrent operations.

**Acceptance Criteria**

- Thread-safe access to shared state
- Proper lock management for sensor data
- Background task orchestration
- Thread pool for API requests
- Graceful thread shutdown
- Deadlock prevention mechanisms
- Thread monitoring and health checks

**Deliverables**

- Thread management utilities
- Improved data locking mechanisms
- Background task scheduler
- Thread health monitoring
- Concurrency test suite

**Technical Notes**

- Use threading.Lock for shared sensor_data
- Implement thread pool executor for sync tasks
- Add timeout protection for all locks
- Monitor thread health in diagnostics endpoint

---

#### [IOT-005] Logging System Enhancement #5
**Task Description**

Implement structured logging with rotation, remote log shipping, and query capabilities for debugging and monitoring.

**Acceptance Criteria**

- Structured JSON logging format
- Log rotation by size and time
- Log level control per module
- Remote log shipping to backend
- Log query API endpoint
- Error aggregation and alerting
- Performance metrics logging

**Deliverables**

- Enhanced logging configuration
- Log rotation utilities
- Remote log shipper
- Log query API endpoints
- Logging best practices guide

**Technical Notes**

- Use Python logging with JSON formatter
- Implement log rotation with max 10 files
- Ship logs to backend hourly
- Include context in all log entries

---

#### [IOT-006] Dependency Injection and Modularity #6
**Task Description**

Refactor integrated_server.py to use dependency injection for better testability, modularity, and maintainability.

**Acceptance Criteria**

- Dependency injection container
- Decoupled component initialization
- Interface-based component design
- Mock implementations for testing
- Component registry
- Lazy loading for heavy components
- Clear component dependencies

**Deliverables**

- Dependency injection framework
- Refactored integrated_server.py
- Component interfaces
- Test mock implementations
- Architecture documentation

**Technical Notes**

- Use factory pattern for component creation
- Implement service locator for global access
- Support both singleton and transient lifetimes
- Document all component dependencies

---

### 2. Sensor and Data Management

#### [IOT-007] Arduino Communication Reliability #7
**Task Description**

Improve serial communication with Arduino for reliable sensor data collection with error detection, recovery, and fallback mechanisms.

**Acceptance Criteria**

- Automatic Arduino port detection
- Serial connection recovery on failure
- Checksum validation for sensor data
- Timeout handling for serial reads
- Fallback to simulation mode
- Data validation and sanitization
- Connection status monitoring

**Deliverables**

- Enhanced serial communication module
- Arduino auto-discovery utility
- Data validation functions
- Connection health monitoring
- Serial troubleshooting guide

**Technical Notes**

- Implement serial port scanning
- Add CRC checksum to Arduino protocol
- Retry failed reads with exponential backoff
- Log all communication errors

---

#### [IOT-008] Sensor Data Validation and Filtering #8
**Task Description**

Implement robust sensor data validation, outlier detection, and filtering algorithms to ensure data quality.

**Acceptance Criteria**

- Range validation for all sensor types
- Outlier detection using statistical methods
- Moving average smoothing
- Spike detection and removal
- Data quality scoring
- Invalid data handling
- Calibration support

**Deliverables**

- Sensor data validation module
- Filtering algorithms
- Calibration utilities
- Data quality metrics
- Validation test suite

**Technical Notes**

- Use moving median for outlier detection
- Implement Kalman filter for smoothing
- Define sensor ranges in configuration
- Store raw and filtered values

---

#### [IOT-009] Historical Data Management #9
**Task Description**

Enhance local database storage for efficient historical data queries, aggregation, and retention policies.

**Acceptance Criteria**

- Time-series data optimization
- Efficient aggregation queries (hourly, daily)
- Data retention policies
- Database cleanup automation
- Export functionality (CSV, JSON)
- Data compression for old records
- Backup and restore capabilities

**Deliverables**

- Enhanced `data_logger.py` module
- Aggregation query functions
- Data retention scripts
- Export utilities
- Database maintenance guide

**Technical Notes**

- Use SQLite with time-series optimizations
- Implement automatic aggregation jobs
- Retain raw data for 30 days, aggregated for 1 year
- Create database indexes for performance

---

#### [IOT-010] Sensor Calibration System #10
**Task Description**

Implement sensor calibration workflow for CO₂, temperature, and humidity sensors with offset and scaling adjustments.

**Acceptance Criteria**

- Calibration API endpoints
- Offset and scaling factor storage
- Multi-point calibration support
- Calibration history tracking
- Calibration validation tests
- Factory reset functionality
- Calibration status indicators

**Deliverables**

- Calibration module
- Calibration API endpoints
- Calibration UI workflow (for mobile)
- Calibration test utilities
- Calibration guide

**Technical Notes**

- Store calibration values in config
- Apply corrections in real-time
- Support 2-point calibration minimum
- Track last calibration date

---

#### [IOT-011] Sensor Failure Detection and Alerts #11
**Task Description**

Implement automatic detection of sensor failures with alerting and fallback strategies.

**Acceptance Criteria**

- Sensor health monitoring
- Stuck sensor detection
- Communication failure detection
- Alert generation for failures
- Fallback to safe defaults
- Diagnostic information collection
- Recovery attempt mechanisms

**Deliverables**

- Sensor health monitor
- Alert generation system
- Diagnostic utilities
- Recovery mechanisms
- Health status API endpoint

**Technical Notes**

- Detect stuck values (no change for 10 readings)
- Monitor read error rates
- Generate alerts after 3 consecutive failures
- Enter safe mode on critical sensor failure

---

### 3. Actuator Control System

#### [IOT-012] Actuator State Management #12
**Task Description**

Implement comprehensive actuator state management with persistence, validation, and conflict resolution.

**Acceptance Criteria**

- Persistent actuator state storage
- State validation before changes
- Conflict resolution (manual vs auto)
- State transition logging
- Interlock prevention (safety rules)
- State synchronization with backend
- Emergency stop functionality

**Deliverables**

- Enhanced ActuatorController class
- State persistence module
- Safety interlock system
- Emergency stop endpoint
- State management tests

**Technical Notes**

- Store state in SQLite and config
- Validate state transitions
- Prevent conflicting actuator states
- Log all state changes with reasons

---

#### [IOT-013] GPIO Control Enhancement #13
**Task Description**

Improve GPIO control with error handling, monitoring, and simulation mode for development/testing.

**Acceptance Criteria**

- GPIO initialization with error handling
- Pin state monitoring
- Simulation mode for testing
- GPIO diagnostics
- Relay failure detection
- Power consumption tracking
- Safe mode on GPIO errors

**Deliverables**

- Enhanced GPIO control module
- Simulation mode implementation
- GPIO diagnostics tools
- Error recovery mechanisms
- GPIO testing utilities

**Technical Notes**

- Use RPi.GPIO with proper cleanup
- Implement software PWM for future use
- Mock GPIO in simulation mode
- Monitor GPIO state vs expected state

---

#### [IOT-014] Manual Control vs Automation Priority #14
**Task Description**

Implement clear priority system between manual control commands and automated decisions with override mechanisms.

**Acceptance Criteria**

- Manual override mode
- Timed manual control with auto-resume
- Clear indication of control mode
- Smooth transition between modes
- Override history tracking
- Mobile app control priority
- Safety override for critical conditions

**Deliverables**

- Control priority manager
- Override API endpoints
- Mode transition logic
- Priority indicator in status
- Control mode documentation

**Technical Notes**

- Manual control overrides automation for 30 minutes
- Automation resumes after timeout
- Critical alerts override manual mode
- Store control mode in state

---

#### [IOT-015] Actuator Scheduling and Timers #15
**Task Description**

Implement scheduling functionality for actuators (e.g., LED light cycles, timed ventilation).

**Acceptance Criteria**

- Cron-like scheduling syntax
- Recurring schedules (daily, weekly)
- One-time scheduled actions
- Schedule conflict detection
- Schedule persistence
- Schedule enable/disable
- Timezone support

**Deliverables**

- Scheduler module
- Schedule CRUD API endpoints
- Schedule execution engine
- Schedule persistence layer
- Scheduling documentation

**Technical Notes**

- Use APScheduler for job scheduling
- Store schedules in SQLite
- Support cron expressions
- Validate schedule conflicts

---

#### [IOT-016] Actuator Performance Analytics #16
**Task Description**

Track actuator usage patterns, runtime statistics, and maintenance predictions.

**Acceptance Criteria**

- Runtime tracking per actuator
- Cycle count tracking
- Performance metrics
- Maintenance prediction
- Usage pattern analysis
- Cost estimation (power usage)
- Analytics API endpoints

**Deliverables**

- Analytics tracking module
- Usage statistics calculator
- Maintenance predictor
- Analytics API endpoints
- Analytics dashboard data

**Technical Notes**

- Track ON/OFF cycles and duration
- Calculate average runtime per day
- Predict maintenance at 10,000 cycles
- Store metrics in SQLite

---

### 4. Network and Connectivity

#### [IOT-017] WiFi Provisioning Enhancement #17
**Task Description**

Improve WiFi provisioning workflow via Bluetooth and hotspot with better error handling and user feedback.

**Acceptance Criteria**

- Reliable Bluetooth WiFi provisioning
- Hotspot fallback mode
- Network credential validation
- Connection status feedback
- Retry mechanisms
- Provisioning timeout handling
- Multi-network support

**Deliverables**

- Enhanced WiFi provisioning module
- Improved Bluetooth serial protocol
- Hotspot manager improvements
- Provisioning API enhancements
- Provisioning user guide

**Technical Notes**

- Test credentials before saving
- Provide real-time connection status
- Timeout provisioning after 5 minutes
- Support WPA2 and WPA3

---

#### [IOT-018] Network Connectivity Monitoring #18
**Task Description**

Implement continuous network connectivity monitoring with automatic recovery and reconnection.

**Acceptance Criteria**

- Internet connectivity monitoring
- Local network monitoring
- Automatic reconnection attempts
- Connection quality metrics
- Offline mode handling
- Network change detection
- Connectivity status API

**Deliverables**

- Network monitor module
- Reconnection logic
- Connectivity metrics
- Status API endpoint
- Network troubleshooting guide

**Technical Notes**

- Ping gateway every 30 seconds
- Attempt reconnection on failure
- Track connection uptime
- Detect network changes

---

#### [IOT-019] mDNS Service Discovery #19
**Task Description**

Enhance mDNS service for reliable device discovery on local networks by mobile apps.

**Acceptance Criteria**

- Reliable mDNS advertising
- Service metadata (device info)
- mDNS query response
- Port and protocol advertising
- Network interface handling
- mDNS troubleshooting tools
- Fallback discovery methods

**Deliverables**

- Enhanced mDNS service module
- Device metadata management
- Discovery test utilities
- Alternative discovery methods
- Discovery documentation

**Technical Notes**

- Use Avahi/Zeroconf for mDNS
- Advertise _mash._tcp service
- Include device ID in TXT records
- Support multiple network interfaces

---

#### [IOT-020] Bluetooth Connection Management #20
**Task Description**

Improve Bluetooth connectivity for mobile app pairing, data transfer, and WiFi provisioning.

**Acceptance Criteria**

- Reliable Bluetooth pairing
- BLE GATT server implementation
- Serial SPP profile support
- Connection state management
- Multiple client handling
- Bluetooth diagnostics
- Pairing security

**Deliverables**

- Enhanced Bluetooth manager
- BLE GATT server
- SPP server implementation
- Connection state machine
- Bluetooth test suite

**Technical Notes**

- Support both BLE and Classic Bluetooth
- Implement device pairing workflow
- Handle connection timeouts
- Secure pairing with PIN

---

#### [IOT-021] Hotspot Mode Enhancement #21
**Task Description**

Improve WiFi hotspot mode for initial device setup and troubleshooting with captive portal support.

**Acceptance Criteria**

- Automatic hotspot activation on boot (no WiFi)
- Captive portal for easy access
- Web-based setup interface
- Hotspot timeout (auto-disable)
- Manual hotspot activation API
- Hotspot status monitoring
- Security improvements

**Deliverables**

- Enhanced hotspot manager
- Captive portal implementation
- Web setup interface
- Hotspot API endpoints
- Hotspot configuration guide

**Technical Notes**

- Use hostapd and dnsmasq
- Redirect all traffic to setup page
- Auto-disable after 30 minutes
- WPA2 secured hotspot

---

### 5. Backend and Cloud Sync

#### [IOT-022] Backend API Client Enhancement #22
**Task Description**

Improve backend API client with better error handling, retry logic, and request queuing.

**Acceptance Criteria**

- Robust error handling
- Exponential backoff retry
- Request queuing for offline mode
- Circuit breaker pattern
- API versioning support
- Request timeout handling
- Authentication token management

**Deliverables**

- Enhanced backend_client.py
- Request queue module
- Circuit breaker implementation
- Retry logic with backoff
- API client tests

**Technical Notes**

- Queue failed requests in SQLite
- Retry with exponential backoff
- Open circuit after 5 failures
- Store auth tokens securely

---

#### [IOT-023] Real-time Data Synchronization #23
**Task Description**

Implement efficient real-time data sync between device, backend, and Firebase with conflict resolution.

**Acceptance Criteria**

- Real-time sensor data streaming
- Actuator state synchronization
- Conflict resolution strategies
- Sync status monitoring
- Offline data queuing
- Bandwidth optimization
- Sync retry mechanisms

**Deliverables**

- Sync manager module
- Conflict resolution logic
- Data queue implementation
- Sync status API
- Sync performance tests

**Technical Notes**

- Batch sensor data (every 30 seconds)
- Sync actuator changes immediately
- Use last-write-wins for conflicts
- Compress historical data

---

#### [IOT-024] Device Registration and Authentication #24
**Task Description**

Implement secure device registration and authentication flow with backend API.

**Acceptance Criteria**

- Automatic device registration
- JWT token authentication
- Token refresh mechanism
- Device identity verification
- Re-registration on token expiry
- Secure credential storage
- Authentication error handling

**Deliverables**

- Authentication module
- Registration workflow
- Token management
- Credential storage
- Auth troubleshooting guide

**Technical Notes**

- Register device on first boot
- Store JWT in encrypted config
- Refresh token before expiry
- Use device serial as identifier

---

#### [IOT-025] Firebase Integration Enhancement #25
**Task Description**

Improve Firebase Realtime Database integration for mobile app real-time updates with better error handling.

**Acceptance Criteria**

- Reliable Firebase connection
- Real-time data push to Firebase
- Firebase authentication
- Connection state monitoring
- Offline persistence
- Data structure optimization
- Error recovery

**Deliverables**

- Enhanced firebase_client.py
- Connection manager
- Data structure schemas
- Offline persistence
- Firebase integration tests

**Technical Notes**

- Use service account authentication
- Push sensor data every 10 seconds
- Cache data when offline
- Optimize Firebase data structure

---

#### [IOT-026] Command Execution from Backend #26
**Task Description**

Implement secure command execution system for remote control from backend/mobile app.

**Acceptance Criteria**

- Command queue from backend
- Command validation and sanitization
- Command execution with feedback
- Command history logging
- Rate limiting
- Command rollback on failure
- Security and authorization

**Deliverables**

- Command execution module
- Command queue processor
- Validation and security layer
- Command history tracking
- Command API documentation

**Technical Notes**

- Poll backend for commands every 30 seconds
- Validate all commands before execution
- Log command execution results
- Rate limit to 10 commands/minute

---

### 6. Mobile App Integration

#### [IOT-027] Mobile API Endpoints #27
**Task Description**

Implement comprehensive REST API endpoints for mobile app integration with proper documentation.

**Acceptance Criteria**

- Complete CRUD API for all features
- API versioning (v1, v2)
- Request/response validation
- Error response standardization
- API rate limiting
- CORS configuration
- OpenAPI/Swagger documentation

**Deliverables**

- Complete API endpoint set
- Input/output validation
- Error response handlers
- API documentation (Swagger)
- API testing suite

**Technical Notes**

- Use Flask-RESTful for endpoints
- Implement JSON schema validation
- Return consistent error formats
- Document all endpoints

---

#### [IOT-028] WebSocket Real-time Updates #28
**Task Description**

Implement WebSocket server for real-time sensor updates to mobile app.

**Acceptance Criteria**

- WebSocket server implementation
- Real-time sensor data streaming
- Actuator state updates
- Client connection management
- Reconnection handling
- Message queuing
- Authentication for WebSocket

**Deliverables**

- WebSocket server module
- Client connection manager
- Message serialization
- WebSocket test client
- WebSocket integration guide

**Technical Notes**

- Use Flask-SocketIO for WebSocket
- Push updates every 2 seconds
- Handle multiple clients
- Authenticate with JWT tokens

---

#### [IOT-029] Mobile App Device Discovery #29
**Task Description**

Implement multiple device discovery methods for mobile app (mDNS, Bluetooth, manual IP).

**Acceptance Criteria**

- mDNS-based discovery
- Bluetooth-based discovery
- Manual IP entry support
- QR code configuration
- Discovery metadata (device info)
- Discovery priority logic
- Fallback mechanisms

**Deliverables**

- Discovery service module
- Multi-method discovery logic
- QR code generator
- Discovery API endpoints
- Discovery troubleshooting guide

**Technical Notes**

- Prioritize mDNS for local network
- Use Bluetooth when WiFi unavailable
- Generate QR with device IP and ID
- Respond to discovery broadcasts

---

#### [IOT-030] Mobile Control Security #30
**Task Description**

Implement security measures for mobile app control including authentication and authorization.

**Acceptance Criteria**

- API key authentication
- Role-based access control
- Command authorization
- Secure communication (HTTPS)
- Request signing
- Rate limiting per client
- Security audit logging

**Deliverables**

- Authentication middleware
- Authorization framework
- HTTPS/TLS configuration
- Security test suite
- Security documentation

**Technical Notes**

- Require API key for all endpoints
- Implement RBAC (admin, user, viewer)
- Use self-signed cert for local HTTPS
- Log all security events

---

#### [IOT-031] Mobile App State Synchronization #31
**Task Description**

Ensure mobile app always has current device state with efficient sync mechanisms.

**Acceptance Criteria**

- Full state snapshot endpoint
- Incremental state updates
- State version tracking
- Conflict resolution
- Offline state handling
- State cache on device
- Sync status indicators

**Deliverables**

- State sync module
- State versioning system
- Conflict resolver
- State cache manager
- Sync documentation

**Technical Notes**

- Provide /api/state/full endpoint
- Use timestamps for conflict resolution
- Cache last state in memory
- Push updates via WebSocket

---

### 7. Touchscreen UI and Local Control

#### [IOT-032] Touchscreen UI Reliability and Auto-Start #32
**Task Description**

Ensure touchscreen UI (Kivy-based) reliably auto-starts on boot and handles errors gracefully for offline/manual device operation.

**Acceptance Criteria**

- Auto-start on Raspberry Pi boot (systemd service)
- Graceful fallback when integrated_server is unavailable
- Screen size auto-detection (3.5" vs 7")
- Error recovery and automatic reconnection
- Touchscreen calibration support
- Display orientation configuration
- Resource usage optimization (<300MB RAM)

**Deliverables**

- Enhanced touchscreen_ui/main.py with lifecycle management
- Systemd service configuration for UI
- Screen detection and calibration utilities
- Error handling and recovery mechanisms
- UI performance optimization

**Technical Notes**

- Create touchscreen-ui.service for systemd
- Start UI after integrated_server.service
- Implement retry logic for API connection
- Support both 480x320 and 800x480 displays
- Optimize Kivy rendering for RPi3 GPU

---

#### [IOT-033] Dashboard and Real-time Display #33
**Task Description**

Enhance the dashboard screen with real-time sensor monitoring, visual alerts, and status indicators for local device operation.

**Acceptance Criteria**

- Real-time sensor data display (CO₂, temp, humidity)
- Live charts for sensor trends
- Actuator status indicators
- Automation mode display
- Visual alerts for critical conditions
- Connection status (backend, WiFi, mobile)
- Auto-refresh every 2 seconds

**Deliverables**

- Enhanced touchscreen_ui/screens/dashboard.py
- Real-time chart widgets
- Alert notification system
- Status indicator components
- Dashboard layout optimization

**Technical Notes**

- Use Kivy Clock for periodic updates
- Poll integrated_server API every 2 seconds
- Implement circular buffer for chart data
- Use color coding for alert severity
- Cache last known state for offline display

---

#### [IOT-034] Manual Actuator Control Interface #34
**Task Description**

Implement comprehensive manual control interface for actuators with visual feedback and safety interlocks.

**Acceptance Criteria**

- Toggle controls for all actuators (fans, humidifier, lights)
- Manual override mode
- Safety interlock warnings
- Control confirmation dialogs
- State synchronization with backend
- Visual feedback for state changes
- Disabled state when automation is active

**Deliverables**

- Enhanced touchscreen_ui/screens/controls.py
- Toggle button widgets with state
- Confirmation dialog components
- Safety interlock validation
- Control feedback animations

**Technical Notes**

- Use POST /api/actuator endpoint
- Implement debouncing for touch inputs
- Show visual confirmation of state change
- Disable controls during automation mode
- Display last update timestamp

---

#### [IOT-035] WiFi Configuration and Network Setup #35
**Task Description**

Implement on-screen WiFi configuration interface for initial device setup and network changes without mobile app.

**Acceptance Criteria**

- WiFi network scanning and display
- Password input with on-screen keyboard
- Network connection testing
- Saved networks management
- Manual IP configuration option
- Network status monitoring
- Hotspot mode activation

**Deliverables**

- Enhanced touchscreen_ui/screens/wifi_setup.py
- Network scanner integration
- Virtual keyboard widget
- Network credentials storage
- Connection test utilities

**Technical Notes**

- Use /api/wifi/scan endpoint
- Implement secure password input
- Test connection before saving
- Store credentials encrypted
- Show connection strength indicators

---

#### [IOT-036] Settings and Device Configuration #36
**Task Description**

Implement settings screen for device configuration, system information, and maintenance operations accessible locally.

**Acceptance Criteria**

- Device information display (ID, IP, MAC, version)
- Automation enable/disable toggle
- Mode switching (spawning/fruiting)
- Sensor calibration interface
- System diagnostics access
- Log viewer
- Factory reset option

**Deliverables**

- Enhanced touchscreen_ui/screens/settings.py
- Device info display components
- Configuration management interface
- Diagnostic tools UI
- Log viewer widget

**Technical Notes**

- Display device ID, IP from /api/status
- Integrate with /api/automation endpoints
- Provide access to /api/diagnostics
- Implement scrollable log viewer
- Require confirmation for destructive actions

---

### 8. Monitoring and Diagnostics

#### [IOT-037] System Health Monitoring #37
**Task Description**

Implement comprehensive system health monitoring including CPU, memory, disk, and temperature.

**Acceptance Criteria**

- CPU usage monitoring
- Memory usage tracking
- Disk space monitoring
- System temperature monitoring
- Process monitoring
- Resource alerts
- Health history logging

**Deliverables**

- System monitor module
- Resource metrics collector
- Health API endpoint
- Resource alert system
- Monitoring dashboard data

**Technical Notes**

- Use psutil for system metrics
- Monitor every 60 seconds
- Alert when disk > 90% full
- Track Raspberry Pi temperature

---

#### [IOT-038] Diagnostic API and Tools #38
**Task Description**

Implement diagnostic endpoints and tools for troubleshooting device issues.

**Acceptance Criteria**

- Comprehensive diagnostic endpoint
- Network diagnostics
- Sensor diagnostics
- Actuator diagnostics
- Component status checks
- Log export functionality
- Self-test suite

**Deliverables**

- Diagnostic API endpoints
- Self-test module
- Diagnostic utilities
- Log export tools
- Troubleshooting guide

**Technical Notes**

- Provide /api/diagnostics endpoint
- Test all components in sequence
- Export last 1000 log entries
- Include system information

---

#### [IOT-039] Alert and Notification System #39
**Task Description**

Implement alert system for critical conditions with notification delivery to mobile and backend.

**Acceptance Criteria**

- Alert rule engine
- Critical condition detection
- Alert priority levels
- Alert throttling
- Multi-channel notifications
- Alert history tracking
- Alert acknowledgment

**Deliverables**

- Alert engine module
- Notification dispatcher
- Alert rules configuration
- Alert API endpoints
- Alert documentation

**Technical Notes**

- Define alert rules in config
- Priority: Critical, Warning, Info
- Throttle duplicate alerts (5 min)
- Store alerts in database

---

#### [IOT-040] Performance Metrics and Analytics #40
**Task Description**

Implement performance tracking and analytics for system optimization.

**Acceptance Criteria**

- API response time tracking
- Sensor read latency
- Sync performance metrics
- Resource utilization trends
- Error rate tracking
- Performance dashboards
- Metrics export

**Deliverables**

- Metrics collection module
- Performance analyzer
- Metrics API endpoints
- Dashboard data preparation
- Performance report generator

**Technical Notes**

- Track all API response times
- Monitor sync latency
- Calculate error rates
- Store metrics in time-series format

---

#### [IOT-041] Remote Debugging and Logging #41
**Task Description**

Implement remote debugging capabilities for production troubleshooting without physical access.

**Acceptance Criteria**

- Remote log access API
- Live log streaming
- Debug mode toggle
- Remote command execution
- Configuration viewing
- Safe mode activation
- Audit logging

**Deliverables**

- Remote debugging API
- Log streaming endpoint
- Remote command module
- Safety mechanisms
- Remote debugging guide

**Technical Notes**

- Stream logs via WebSocket
- Require admin authentication
- Limit remote commands to safe operations
- Log all remote access

---

## Implementation Priority

### Phase 1: Critical Foundation (Weeks 1-2)
- IOT-002: Application Lifecycle
- IOT-003: Configuration Management
- IOT-007: Arduino Communication
- IOT-012: Actuator State Management
- IOT-022: Backend API Enhancement
- IOT-032: Touchscreen UI Auto-Start

### Phase 2: Core Functionality (Weeks 2-3)
- IOT-008: Sensor Data Validation
- IOT-013: GPIO Control
- IOT-017: WiFi Provisioning
- IOT-023: Real-time Sync
- IOT-027: Mobile API Endpoints
- IOT-033: Touchscreen Dashboard
- IOT-034: Manual Control Interface

### Phase 3: Advanced Features (Weeks 3-4)
- IOT-015: Actuator Scheduling
- IOT-020: Bluetooth Management
- IOT-028: WebSocket Updates
- IOT-035: WiFi Configuration UI
- IOT-036: Settings Interface
- IOT-037: System Health Monitoring
- IOT-039: Alert System

### Phase 4: Polish and Optimization (Week 4)
- IOT-004: Threading Improvements
- IOT-005: Logging Enhancement
- IOT-038: Diagnostic Tools
- IOT-040: Performance Metrics
- IOT-041: Remote Debugging

---

## Testing Strategy

Each task should include:
- Unit tests for individual functions
- Integration tests for component interaction
- Hardware tests on actual Raspberry Pi
- Touchscreen UI testing (both 3.5" and 7" displays)
- Network connectivity tests
- Mobile app integration tests
- Performance and load tests
- Security testing
- Offline operation testing

## Documentation Requirements

Each completed task must include:
- Code documentation (docstrings)
- API documentation (if applicable)
- User guide updates
- Architecture documentation
- Troubleshooting guide entries
- Touchscreen UI user manual (for local operation)

---

**Last Updated:** December 18, 2025
**Document Version:** 1.1
**Status:** Draft - Pending Review
