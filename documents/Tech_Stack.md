# M.A.S.H. Technology Stack

## Overview

The M.A.S.H. (Mushroom Automation with Smart Hydro-environment using IoT and AI for Sustainable Harvest) system utilizes a modern, scalable technology stack designed to support IoT-enabled mushroom cultivation, real-time monitoring, AI-driven optimization, and integrated e-commerce functionality. The stack is optimized for reliability, offline capability, and cross-platform compatibility.

## Core Technologies

### Backend Framework
- **NestJS** (TypeScript)
  - Modular, scalable Node.js framework for building efficient server-side applications
  - Integrated with Prisma ORM for database management
  - RESTful API design with JWT authentication
  - Real-time capabilities via WebSocket integration

### Frontend Frameworks
- **Flutter** (Dart)
  - Cross-platform mobile applications for iOS and Android
  - Single codebase for grower and consumer applications
  - Real-time data synchronization with Firebase
  - Offline-first architecture with SQLite integration

- **Next.js** (TypeScript/React)
  - Server-side rendered web applications
  - Administrative dashboard and public e-commerce platform
  - Responsive design for desktop and mobile access

### Database Systems

#### Primary Database
- **PostgreSQL**
  - Relational database for core business data
  - User management, product catalogs, orders, and analytics
  - Integrated with Prisma ORM in NestJS backend
  - ACID compliance for transactional integrity

#### Offline Database
- **SQLite**
  - Local storage for offline functionality
  - Sensor data recording during internet outages
  - Automatic synchronization when connectivity is restored
  - Lightweight, file-based database for IoT devices

#### Real-time Database
- **Firebase Realtime Database**
  - Real-time synchronization of IoT sensor data
  - Live environmental monitoring (temperature, humidity, CO₂)
  - Cross-platform data sharing between mobile apps and web dashboard
  - Push notifications and alerts

### IoT and Hardware Integration
- **Raspberry Pi Zero 2W** (Controller)
  - Python-based sensor data collection
  - MQTT protocol for device communication
  - GPIO control for actuators (fans, humidifiers)
  - Offline data logging to SQLite

### Development Tools
- **Postman**
  - API testing and documentation
  - Automated testing workflows
  - Collection management for backend endpoints

## System Architecture

### Data Flow Architecture
```
IoT Sensors → Raspberry Pi → MQTT → NestJS Backend → Multiple Databases
                                      ↓
Flutter Apps ← Firebase Realtime ← Web Dashboard (Next.js)
                                      ↓
SQLite (Offline) ← Automatic Sync ← PostgreSQL (Primary)
```

### Offline Capability
- **Internet-Independent Operation**: IoT device continues data collection and actuator control without internet connectivity
- **Local Storage**: SQLite database on Raspberry Pi stores sensor readings during outages
- **Automatic Synchronization**: Data uploads to Firebase/PostgreSQL when connection is restored
- **Graceful Degradation**: Core functionality maintained in offline mode

### Power Management
- **Solar Panel Integration**: Photovoltaic panels provide sustainable energy source
- **Battery Backup**: Lithium-ion battery system ensures continuous operation
- **Power Monitoring**: Real-time battery charge tracking via mobile app
- **Emergency Mode**: Reduced functionality during low-power conditions

## Application Ecosystem

### Mobile Application (Grower App)
Designed for mushroom cultivators, this application provides real-time access to environmental data, AI-driven alerts (e.g., contamination detection), and remote control over grow chamber parameters. It supports logging cultivation metrics, viewing growth progress, and receiving maintenance reminders. It is also supported by solar panels and battery for the IoT device so it still works even if there's an accident in the electricity.

### Mobile Application (E-commerce for Consumers)
A consumer-facing app facilitating mushroom product browsing, purchasing, and order tracking. It supports payment processing and provides product information with traceability, increasing buyer confidence and enabling direct sales from growers to end consumers.

### Web Dashboard (System Administrators)
An administrative portal for managing the entire ecosystem including multiple grow sites, user roles, IoT devices, and energy systems. The dashboard offers comprehensive analytics, farm status monitoring, and system configuration controls, designed for technical support and operational oversight.

### Website E-commerce Platform
A public-facing website that connects growers, middlemen, and consumers. It features product catalogs, order management, digital payment gateways, and logistics coordination tools to enhance market access and business scalability.

## IPO Diagram (Input – Process – Output)

### Input
- Real-time sensor data including temperature (±0.5°C), humidity (±2%), CO₂ levels, and sterilization status; battery charge; user sales and order data from e-commerce platform

### Process
- AI and machine learning algorithms analyze sensor inputs to optimize environmental parameters dynamically. E-commerce module processes sales orders, manages inventory, and coordinates logistics via integrated backend

### Output
- Automated environmental control adjustments (actuator commands for humidifiers, fans, sterilizers), contamination alerts issued to users, real-time performance dashboards, user notifications, order tracking updates, and sales analytics reports

## Security and Performance

### Data Security
- **Encryption**: AES-256 encryption for data at rest and in transit
- **Authentication**: JWT tokens with Firebase Auth integration
- **Access Control**: Role-based permissions across all applications
- **API Security**: Rate limiting and input validation

### Performance Metrics
- **Response Time**: <2 seconds for API calls
- **Uptime**: 99.5% system availability
- **Data Synchronization**: Real-time with <5-minute offline buffer
- **Mobile App Performance**: Smooth operation on devices with 2GB+ RAM

## Development and Deployment

### Development Environment
- **Version Control**: Git with GitHub repository
- **CI/CD**: Automated testing and deployment pipelines
- **Containerization**: Docker for consistent environments
- **Monitoring**: Application performance monitoring and logging

### Deployment Architecture
- **Backend**: NestJS deployed on cloud platforms (AWS/Vercel)
- **Databases**: PostgreSQL (AWS RDS), Firebase (managed), SQLite (local)
- **Mobile Apps**: Published on App Store and Google Play
- **Web Applications**: Hosted on Vercel/Netlify with CDN

This technology stack provides a robust, scalable foundation for the M.A.S.H. system, ensuring reliable operation in both online and offline conditions while supporting the complex requirements of IoT-enabled mushroom cultivation and e-commerce integration.