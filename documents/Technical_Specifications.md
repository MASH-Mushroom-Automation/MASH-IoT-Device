# M.A.S.H. Technical Specifications

## System Architecture Overview

The M.A.S.H. system integrates hardware automation, IoT-enabled monitoring, AI-driven optimization, and e-commerce to holistically address challenges throughout the oyster mushroom cultivation cycle. The system is structured into three development phases, each progressively enhancing system capabilities and market integration.

## Hardware Components

### Core Controller
- **Raspberry Pi Zero 2W**
  - Processor: Quad-core ARM Cortex-A53 64-bit SoC @ 1GHz
  - RAM: 512MB LPDDR4
  - Storage: MicroSD card slot
  - Wireless: WiFi 802.11 b/g/n, Bluetooth 5.0
  - GPIO: 40-pin header for sensor integration
  - Power: 5V via micro USB

### Environmental Sensors
- **CO2L Unit with Temperature and Humidity Sensor (SCD41)**
  - Temperature Range: -10°C to +60°C (±0.5°C accuracy)
  - Humidity Range: 0-100% RH (±2% accuracy)
  - CO2 Range: 400-5000 ppm (±75 ppm accuracy)
  - Interface: I2C communication protocol
  - Power Consumption: < 75mW

### Display Module
- **I2C 20x4 LCD Display**
  - Display: 20 characters x 4 lines
  - Backlight: Blue/white LED
  - Interface: I2C (address 0x27)
  - Operating Voltage: 5V DC

### Environmental Control Actuators
- **Humidifier Module**
  - Type: Ultrasonic atomizer
  - Capacity: 4 spray nozzles
  - Power: 5V DC
  - Flow Rate: Adjustable

- **Exhaust Fan**
  - Size: 40mm
  - Voltage: 5V DC
  - Speed: Variable (PWM control)
  - Airflow: 4.5 CFM

- **Blower Fan (Air Intake)**
  - Size: 12 inches
  - Voltage: 220V AC
  - Power: 45W
  - Speed: Variable control

- **HEPA Filter System**
  - Filtration: 99.97% efficiency for 0.3μm particles
  - Compatible with Sharp FZ-F30HFE filter
  - Frame: Plastic housing

### Power Management
- **Smart Power Strip**
  - Voltage: 220V AC input
  - Outlets: 4 universal sockets
  - Features: Energy monitoring, surge protection
  - Connectivity: WiFi-enabled
  - Remote Control: Mobile app integration

- **Power MOSFET Module (F5305S)**
  - Voltage: 5V logic, 30V/14A switching
  - Applications: Motor speed control, lighting
  - Protection: Over-current, thermal shutdown

### Structural Components
- **Grow Tent**
  - Dimensions: 24" x 24" x 36" (61 x 61 x 91 cm)
  - Material: 600D reflective mylar
  - Features: Zippered access, light-proof, waterproof floor

## Software Stack

### Backend Framework
- **NestJS**
  - Language: TypeScript
  - Architecture: Modular, dependency injection
  - Features: RESTful APIs, authentication, validation
  - Database: Prisma ORM with PostgreSQL

### Frontend Frameworks
- **Flutter (Mobile Applications)**
  - Language: Dart
  - Platforms: iOS, Android
  - Features: Cross-platform, native performance
  - State Management: Provider/Bloc pattern

- **Next.js (Web Dashboard)**
  - Language: TypeScript/React
  - Features: Server-side rendering, API routes
  - UI Framework: Material-UI or Tailwind CSS

### Database Systems
- **Primary Database: PostgreSQL**
  - Type: Relational database
  - Features: ACID compliance, JSON support
  - ORM: Prisma
  - Hosting: Local or cloud (Supabase/AWS RDS)

- **Real-time Database: Firebase**
  - Features: Real-time synchronization
  - Offline Support: SQLite local storage
  - Authentication: Firebase Auth (JWT)

- **Cache/Queue: Redis**
  - Features: In-memory data structure store
  - Queue Management: BullMQ for job processing
  - Session Storage: User sessions and caching

### IoT Communication
- **MQTT Protocol**
  - Lightweight messaging for IoT devices
  - Quality of Service (QoS) levels: 0, 1, 2
  - Topics: sensor/data, actuator/control

- **WebSocket**
  - Real-time bidirectional communication
  - Fallback: HTTP polling for compatibility

## AI and Machine Learning Components

### Environmental Optimization Algorithm
- **Input Parameters**
  - Temperature, humidity, CO2 levels
  - Historical growth data
  - Target environmental ranges

- **Output Actions**
  - Actuator control signals
  - Predictive adjustments
  - Alert generation

### Contamination Detection
- **Image Processing**: Computer vision for visual inspection
- **Pattern Recognition**: Anomaly detection in sensor data
- **Machine Learning**: Classification models for contamination types

## System Specifications

### Environmental Control Ranges
- **Temperature**: 25-28°C (optimal for Pleurotus florida)
- **Humidity**: 80-90% RH
- **CO2 Levels**: 10,000-15,000 ppm (fruiting phase)
- **Light**: Complete darkness (12 hours/day recommended)

### Power Requirements
- **Controller**: 5V DC, 1A (Raspberry Pi Zero 2W)
- **Sensors**: 3.3V-5V DC, <100mA total
- **Actuators**: 5V-220V AC/DC, variable current
- **Total System Power**: <200W peak consumption

### Network Requirements
- **WiFi**: 802.11 b/g/n (2.4GHz)
- **Data Usage**: <50MB/day (sensor data transmission)
- **Offline Capability**: SQLite synchronization
- **Backup Connectivity**: GSM module (optional)

### Performance Metrics
- **Sensor Sampling Rate**: 1 reading per minute
- **Data Transmission**: Real-time or batched (5-minute intervals)
- **Response Time**: <2 seconds for actuator commands
- **Uptime Target**: 99.5% system availability

## Security Specifications

### Data Protection
- **Encryption**: AES-256 for data at rest
- **Transport Security**: TLS 1.3 for API communications
- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)

### IoT Security
- **Device Authentication**: Certificate-based authentication
- **Network Security**: WPA3 WiFi encryption
- **Firmware Updates**: Secure over-the-air updates
- **Physical Security**: Tamper-evident enclosures

## Testing and Quality Assurance

### Hardware Testing
- **Environmental Testing**: Temperature/humidity chambers
- **Durability Testing**: Continuous operation cycles
- **Calibration**: Sensor accuracy verification
- **Power Testing**: Voltage fluctuation tolerance

### Software Testing
- **Unit Testing**: Jest for backend, Flutter test for mobile
- **Integration Testing**: API endpoint validation
- **Performance Testing**: Load testing with Artillery
- **User Acceptance Testing**: Grower feedback sessions

## Deployment and Maintenance

### Installation Process
1. Hardware assembly and calibration
2. Software installation and configuration
3. Network setup and security configuration
4. User training and handover

### Maintenance Schedule
- **Daily**: Visual inspection, water level checks
- **Weekly**: Sensor calibration, software updates
- **Monthly**: Deep cleaning, performance audits
- **Quarterly**: Hardware component replacement

### Troubleshooting Procedures
- **Sensor Failures**: Automatic failover to backup sensors
- **Network Issues**: Offline mode activation
- **Power Outages**: Battery backup systems
- **Software Errors**: Automatic restart and logging

## Compliance and Standards

### Safety Standards
- **Electrical Safety**: IEC 60335 household appliance standards
- **Agricultural Equipment**: FAO guidelines for farming equipment
- **Environmental Standards**: RoHS compliance for electronic components

### Data Standards
- **IoT Protocols**: MQTT 5.0 compliance
- **API Standards**: RESTful API design principles
- **Data Formats**: JSON for API responses, ISO 8601 for timestamps

This technical specification document serves as the comprehensive blueprint for the M.A.S.H. system implementation, ensuring all components work together seamlessly to achieve the project's objectives of automated, sustainable oyster mushroom cultivation.