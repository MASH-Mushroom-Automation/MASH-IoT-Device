# M.A.S.H. Software Project Plan
## Mushroom Automation with Smart Hydro-environment using IoT and AI for Sustainable Harvest

### Project Information
- **Project Name**: M.A.S.H. (Mushroom Automation with Smart Hydro-environment using IoT and AI for Sustainable Harvest)
- **Version**: 1.0
- **Date**: October 1, 2025
- **Project Manager**: Kevin A. Llanes
- **Total Budget**: ₱20,000.00
- **Development Team**: 7 Members (BSCS-4B)

### Project Overview
This comprehensive software project plan outlines the development of the M.A.S.H. system, an integrated IoT and AI-driven platform for automated oyster mushroom cultivation with integrated e-commerce capabilities. The system addresses critical challenges in Philippine mushroom farming including environmental control, contamination prevention, and market access, with a target of 20% yield increase and 85% reduction in contamination incidents.

The system consists of four main components: Flutter mobile application for growers, IoT device integration with Raspberry Pi 3 Model B with LCD display, dual-portal e-commerce web platform, and comprehensive administrative dashboard.

---

## 1. Executive Summary

The M.A.S.H. system is an integrated IoT and AI-driven platform for automated oyster mushroom cultivation with integrated e-commerce capabilities. This comprehensive project plan outlines the development of four core components:

1. **Flutter Mobile Application** - Real-time sensor monitoring and cultivation management for growers
2. **IoT Device System** - Raspberry Pi 3 Model B with environmental sensors and LCD display
3. **E-commerce Web Platform** - Dual-portal website for consumers and sellers
4. **Admin Dashboard** - Comprehensive management system for users, devices, and content

The system addresses critical challenges in Philippine mushroom farming including environmental control, contamination prevention, and market access, with a target of 20% yield increase and 85% reduction in contamination incidents.

---

## 2. Project Goals & Objectives

### Primary Goal
Empower small-scale mushroom growers with technology-driven solutions to optimize cultivation processes and streamline market access through an integrated IoT and e-commerce ecosystem.

### Specific Objectives

| Objective ID | Objective Description | Key Performance Indicator (KPI) | Success Criteria |
|--------------|----------------------|----------------------------------|------------------|
| **OBJ-01** | Develop Flutter mobile app for real-time environmental monitoring | App displays sensor data with <2s latency | 100% of sensor data reflected in real-time |
| **OBJ-02** | Implement Raspberry Pi 3B IoT system with LCD display | Continuous 72-hour operation with accurate data logging | 99.5% uptime with <1% data loss |
| **OBJ-03** | Create dual-portal e-commerce website (buyer/seller) | Complete user journey implementation | 100% of e-commerce user stories pass UAT |
| **OBJ-04** | Build comprehensive admin dashboard | Full ecosystem management capabilities | Admins can manage users, devices, and content |
| **OBJ-05** | Ensure seamless system integration | Real-time data synchronization across platforms | <5s data propagation from IoT to all interfaces |
| **OBJ-06** | Achieve target agricultural improvements | 20% yield increase, 85% contamination reduction | Validated through field testing with stakeholders |

---

## 3. Project Scope

### 3.1 In Scope

#### Flutter Mobile Application (Grower-Focused)
- **Authentication System**
  - User registration and login
  - Profile management
  - Password recovery
  - Biometric authentication (fingerprint/face ID)

- **Real-Time Dashboard**
  - Environmental data display (Temperature, Humidity, CO₂)
  - Device status monitoring
  - Alert notifications (push notifications)
  - Historical data visualization with charts

- **Cultivation Management**
  - Growth cycle tracking
  - Cultivation log entries
  - Photo documentation
  - Harvest planning and scheduling
  - Maintenance reminders

- **Device Control**
  - Remote actuator control (fans, humidifiers)
  - Environmental parameter adjustment
  - Device registration and pairing
  - Offline data synchronization

#### IoT Device (Raspberry Pi 3 Model B)
- **Hardware Integration**
  - Sensor data collection (DHT22, MH-Z19B, SCD41)
  - GPIO control for actuators
  - LCD display interface (20x4 characters)
  - Camera module integration (future AI features)

- **Software Components**
  - Python-based sensor data collection
  - MQTT protocol implementation
  - Local SQLite database for offline storage
  - Automatic data synchronization
  - Real-time LCD status display

- **Communication Layer**
  - WiFi connectivity management
  - MQTT broker communication
  - Error handling and reconnection logic
  - Data encryption and security

#### E-commerce Website (Next.js)
- **Consumer Portal**
  - Product browsing and search
  - User registration and authentication
  - Shopping cart functionality
  - Secure checkout process
  - Order tracking and history
  - Product reviews and ratings

- **Seller Portal**
  - Product management (add/edit/remove)
  - Inventory tracking and management
  - Order fulfillment dashboard
  - Sales analytics and reporting
  - Seller profile management
  - Commission and payment tracking

- **Payment Integration**
  - Multiple payment gateways (PayPal, Stripe, GCash)
  - Secure transaction processing
  - Invoice generation
  - Refund management

#### Admin Dashboard (Next.js)
- **User Management**
  - View all registered users
  - User role assignment and permissions
  - Account activation/deactivation
  - User activity monitoring

- **Device Management**
  - IoT device registration and status
  - Device configuration management
  - Performance monitoring
  - Maintenance scheduling

- **Content Management System (CMS)**
  - Website content management
  - Product category management
  - Blog and news management
  - FAQ and help content

- **Analytics and Reporting**
  - Platform-wide usage statistics
  - Sales performance reports
  - Device performance analytics
  - User engagement metrics

#### Backend Infrastructure (NestJS)
- **API Development**
  - RESTful API endpoints
  - GraphQL integration (optional)
  - Real-time WebSocket communication
  - API documentation with Swagger

- **Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (RBAC)
  - OAuth integration
  - Session management

- **Database Management**
  - Prisma ORM integration
  - Database migrations
  - Data validation and sanitization
  - Backup and recovery procedures

### 3.2 Out of Scope (Future Phases)
- Advanced AI/ML algorithms for predictive analysis
- Multi-currency support and international shipping
- Third-party farm management software integration
- Solar panel power management software
- Advanced supply chain management features
- White-label solutions for other agricultural sectors

---

## 4. Technology Stack

### 4.1 Core Technologies
Based on the established M.A.S.H. technology stack:

#### Backend Framework
- **NestJS** (TypeScript)
  - Modular architecture
  - Prisma ORM integration
  - JWT authentication
  - WebSocket support

#### Frontend Frameworks
- **Flutter** (Dart) - Mobile applications
- **Next.js** (TypeScript/React) - Web applications

#### Database Systems
- **PostgreSQL** - Primary relational database
- **SQLite** - IoT offline storage
- **Firebase Realtime Database** - Real-time synchronization

#### IoT Platform
- **Raspberry Pi 3 Model B** - Main controller
- **Python** - IoT software development
- **MQTT** - Device communication protocol

#### Development & Deployment
- **Git/GitHub** - Version control
- **Docker** - Containerization
- **Vercel/Netlify** - Web hosting
- **AWS/GCP** - Backend hosting

### 4.2 Hardware Components
- Raspberry Pi 3 Model B (₱1,600)
- CO2L Unit with Temperature/Humidity Sensor (₱3,090)
- 20x4 LCD Display Module (₱280)
- Environmental control actuators (₱2,500)
- **Total Hardware Budget**: ₱16,028

---

## 5. Project Timeline & Phases

### Project Schedule
- **Start Date**: October 6, 2025
- **Target Launch**: April 6, 2026
- **Total Duration**: 26 weeks

### Phase Breakdown

| Phase | Duration | Start Date | End Date | Key Deliverables |
|-------|----------|------------|----------|------------------|
| **Phase 1: Planning & Design** | 4 weeks | Oct 6, 2025 | Nov 3, 2025 | Project plan, UI/UX designs, system architecture |
| **Phase 2: Backend Development** | 6 weeks | Nov 4, 2025 | Dec 15, 2025 | Core API, database schema, authentication |
| **Phase 3: IoT Development** | 6 weeks | Nov 4, 2025 | Dec 15, 2025 | Raspberry Pi software, sensor integration, LCD display |
| **Phase 4: Frontend Development** | 10 weeks | Dec 16, 2025 | Feb 23, 2026 | Flutter app, e-commerce website, admin dashboard |
| **Phase 5: Integration & Testing** | 4 weeks | Feb 24, 2026 | Mar 23, 2026 | System integration, UAT, bug fixes |
| **Phase 6: Deployment** | 2 weeks | Mar 24, 2026 | Apr 6, 2026 | Production deployment, app store submission |
| **Phase 7: Post-Launch Support** | Ongoing | Apr 7, 2026 | - | Monitoring, support, maintenance |

### Detailed Phase Plans

#### Phase 1: Planning & Design (4 weeks)
**Week 1-2: Project Foundation**
- [ ] Finalize project requirements and scope
- [ ] Set up development environment and tools
- [ ] Create detailed user stories and acceptance criteria
- [ ] Establish coding standards and guidelines

**Week 3-4: Design & Architecture**
- [ ] Complete UI/UX wireframes for all applications
- [ ] Design system architecture and data flow diagrams
- [ ] Create database schema design
- [ ] Define API specifications and endpoints

**Deliverables:**
- Project requirements document
- UI/UX designs and wireframes
- System architecture diagram
- Database schema
- API specification document

#### Phase 2: Backend Development (6 weeks)
**Week 1-2: Core Infrastructure**
- [ ] Set up NestJS project structure
- [ ] Configure Prisma ORM with PostgreSQL
- [ ] Implement basic authentication system
- [ ] Set up CI/CD pipelines

**Week 3-4: API Development**
- [ ] Develop user management APIs
- [ ] Implement device management endpoints
- [ ] Create sensor data collection endpoints
- [ ] Set up real-time WebSocket connections

**Week 5-6: Advanced Features**
- [ ] Implement e-commerce APIs (products, orders, payments)
- [ ] Develop admin dashboard APIs
- [ ] Set up MQTT broker and IoT communication
- [ ] Implement data validation and error handling

**Deliverables:**
- Complete backend API
- Database with all required tables
- Authentication and authorization system
- API documentation

#### Phase 3: IoT Development (6 weeks)
**Week 1-2: Hardware Setup**
- [ ] Configure Raspberry Pi 3 Model B
- [ ] Set up Python development environment
- [ ] Integrate sensor modules (temperature, humidity, CO₂)
- [ ] Configure LCD display interface

**Week 3-4: Software Development**
- [ ] Develop sensor data collection scripts
- [ ] Implement MQTT communication client
- [ ] Create local SQLite database for offline storage
- [ ] Develop LCD display interface

**Week 5-6: Integration & Testing**
- [ ] Implement data synchronization logic
- [ ] Add error handling and recovery mechanisms
- [ ] Test sensor accuracy and calibration
- [ ] Conduct continuous operation testing

**Deliverables:**
- Functional IoT device with all sensors
- LCD display showing real-time data
- MQTT communication established
- Local data logging system

#### Phase 4: Frontend Development (10 weeks)
**Week 1-3: Flutter Mobile App**
- [ ] Set up Flutter project structure
- [ ] Implement authentication screens
- [ ] Develop sensor data dashboard
- [ ] Create historical data visualization
- [ ] Implement push notifications

**Week 4-6: E-commerce Website**
- [ ] Set up Next.js project for e-commerce
- [ ] Develop consumer portal (product browsing, cart, checkout)
- [ ] Create seller portal (product management, analytics)
- [ ] Integrate payment gateways

**Week 7-9: Admin Dashboard**
- [ ] Set up Next.js project for admin dashboard
- [ ] Develop user management interface
- [ ] Create device management dashboard
- [ ] Implement CMS functionality

**Week 10: Integration & Polish**
- [ ] Connect all frontends to backend APIs
- [ ] Implement responsive design
- [ ] Conduct cross-browser testing
- [ ] Performance optimization

**Deliverables:**
- Complete Flutter mobile application
- E-commerce website with dual portals
- Admin dashboard with full functionality
- Integrated frontend applications

#### Phase 5: Integration & Testing (4 weeks)
**Week 1: System Integration**
- [ ] Connect IoT device to backend
- [ ] Test real-time data flow across all platforms
- [ ] Implement end-to-end functionality
- [ ] Performance testing and optimization

**Week 2-3: Testing**
- [ ] Conduct comprehensive system testing
- [ ] Perform user acceptance testing with stakeholders
- [ ] Security audit and penetration testing
- [ ] Bug fixes and performance improvements

**Week 4: Final Preparations**
- [ ] Production environment setup
- [ ] Data migration and seeding
- [ ] Documentation completion
- [ ] Training materials preparation

**Deliverables:**
- Fully integrated system
- Test reports and bug fixes
- Production-ready deployment
- User documentation

#### Phase 6: Deployment (2 weeks)
**Week 1: Production Deployment**
- [ ] Deploy backend to cloud infrastructure
- [ ] Set up production databases
- [ ] Configure monitoring and logging
- [ ] Deploy web applications

**Week 2: App Store Submission**
- [ ] Prepare Flutter app for store submission
- [ ] Submit to Google Play Store and Apple App Store
- [ ] Final system testing in production
- [ ] Launch preparations

**Deliverables:**
- Live production system
- Mobile app submissions
- Monitoring and alerting setup
- Launch-ready platform
- [ ] Product browsing and search
- [ ] Shopping cart functionality
- [ ] Order placement and tracking
- [ ] Payment integration
- [ ] Seller interface for product management

#### 4.6 Advanced Features
- [ ] Push notifications
- [ ] Dark mode support
- [ ] Offline synchronization
- [ ] Data export functionality
- [ ] AI-powered recommendations

**Deliverables**:
- Complete Flutter mobile application
- iOS and Android builds
- App store deployment packages
- User documentation

---

### Phase 5: Web Platform Development (Weeks 9-16)
**Duration**: 8 weeks
**Team**: Frontend Developers, UI/UX Designer

#### 5.1 Next.js Setup & Architecture
- [ ] Next.js project initialization
- [ ] TypeScript configuration
- [ ] Responsive design system
- [ ] Authentication integration
- [ ] API integration layer

#### 5.2 E-commerce User Website
- [ ] Product catalog with search and filters
- [ ] Product detail pages with images
- [ ] Shopping cart and checkout process
- [ ] User account dashboard
- [ ] Order history and tracking
- [ ] Reviews and ratings system

#### 5.3 Seller Dashboard
- [ ] Seller registration and verification
- [ ] Product management interface
- [ ] Inventory tracking system
- [ ] Order management dashboard
- [ ] Sales analytics and reports
- [ ] Commission and payment tracking

#### 5.4 Public Pages
- [ ] Landing page with company information
- [ ] About M.A.S.H. technology
- [ ] Blog/knowledge base
- [ ] Contact and support pages
- [ ] Terms of service and privacy policy

**Deliverables**:
- Complete e-commerce website
- Seller dashboard
- Responsive design for all devices
- SEO optimization

---

### Phase 6: Admin Dashboard Development (Weeks 11-18)
**Duration**: 8 weeks
**Team**: Frontend Developers, Backend Developers

#### 6.1 Dashboard Architecture
- [ ] Admin authentication system
- [ ] Role-based access control
- [ ] Dashboard layout and navigation
- [ ] Real-time data integration
- [ ] Responsive admin interface

#### 6.2 User Management
- [ ] User list with search and filters
- [ ] User profile management
- [ ] Role assignment interface
- [ ] Account suspension/activation
- [ ] User analytics and reports

#### 6.3 Device Management
- [ ] IoT device registration system
- [ ] Device status monitoring
- [ ] Remote device configuration
- [ ] Firmware update management
- [ ] Device performance analytics

#### 6.4 Content Management System
- [ ] Product approval workflow
- [ ] Blog post management
- [ ] Image and media library
- [ ] SEO management tools
- [ ] Content scheduling

#### 6.5 System Monitoring
- [ ] Real-time system health dashboard
- [ ] Error logging and monitoring
- [ ] Performance metrics
- [ ] Database query optimization tools
- [ ] Backup and recovery management

#### 6.6 Analytics & Reporting
- [ ] Sales analytics dashboard
- [ ] User engagement metrics
- [ ] IoT device performance reports
- [ ] Revenue tracking and forecasting
- [ ] Custom report builder

**Deliverables**:
- Complete admin dashboard
- User and device management systems
- CMS functionality
- Analytics and reporting tools

---

### Phase 7: Integration & Testing (Weeks 15-20)
**Duration**: 6 weeks
**Team**: Full Development Team, QA Engineers

#### 7.1 System Integration
- [ ] End-to-end API testing
- [ ] Mobile app to backend integration
- [ ] IoT device to backend communication
- [ ] Real-time data flow testing
- [ ] Payment gateway integration testing

#### 7.2 Performance Testing
- [ ] Load testing for concurrent users
- [ ] Database performance optimization
- [ ] API response time optimization
- [ ] Mobile app performance testing
- [ ] IoT device stress testing

#### 7.3 Security Testing
- [ ] Authentication and authorization testing
- [ ] Data encryption verification
- [ ] API security testing
- [ ] SQL injection prevention
- [ ] Cross-site scripting (XSS) prevention

#### 7.4 User Acceptance Testing
- [ ] Stakeholder testing sessions
- [ ] User feedback collection
- [ ] Bug fixing and improvements
- [ ] Documentation updates
- [ ] Training material preparation

**Deliverables**:
- Fully integrated system
- Performance optimization reports
- Security audit results
- UAT sign-off documentation

---

### Phase 8: Deployment & Launch (Weeks 19-22)
**Duration**: 4 weeks
**Team**: DevOps Engineer, Full Development Team

#### 8.1 Production Deployment
- [ ] Production server setup
- [ ] Database migration to production
- [ ] SSL certificate installation
- [ ] CDN configuration
- [ ] Monitoring and logging setup

#### 8.2 Mobile App Deployment
- [ ] App Store submission (iOS)
- [ ] Google Play Store submission (Android)
- [ ] App store optimization (ASO)
- [ ] Beta testing program
- [ ] Production release

#### 8.3 IoT Device Preparation
- [ ] Production firmware preparation
- [ ] Device provisioning process
- [ ] Quality assurance testing
- [ ] Packaging and documentation
- [ ] Installation guides

#### 8.4 Launch Activities
- [ ] Soft launch with limited users
- [ ] Marketing website launch
- [ ] User onboarding flow testing
- [ ] Customer support setup
- [ ] Public launch announcement

**Deliverables**:
- Live production system
- Published mobile applications
- Ready-to-ship IoT devices
- Launch marketing materials

---

## 3. Technical Specifications

### 3.1 API Endpoints Structure
```
Authentication:
- POST /auth/login
- POST /auth/register
- POST /auth/refresh
- POST /auth/logout

Users:
- GET /users/profile
- PUT /users/profile
- GET /users/devices
- POST /users/devices

Devices:
- GET /devices
- POST /devices/register
- PUT /devices/:id/config
- GET /devices/:id/data
- POST /devices/:id/commands

Sensors:
- GET /sensors/data
- GET /sensors/history
- POST /sensors/alerts
- GET /sensors/analytics

E-commerce:
- GET /products
- POST /products
- GET /orders
- POST /orders
- PUT /orders/:id/status

Admin:
- GET /admin/users
- GET /admin/devices
- GET /admin/analytics
- POST /admin/cms
```

### 3.2 Database Schema Overview
```sql
-- Core Tables
Users (id, email, password, role, created_at, updated_at)
Devices (id, user_id, name, type, status, config, created_at)
SensorData (id, device_id, sensor_type, value, timestamp)
Products (id, seller_id, name, description, price, stock)
Orders (id, user_id, total, status, created_at)
OrderItems (id, order_id, product_id, quantity, price)

-- IoT Specific
DeviceCommands (id, device_id, command, status, timestamp)
Alerts (id, device_id, type, message, severity, resolved)
GrowthCycles (id, device_id, start_date, end_date, notes)
```

### 3.3 MQTT Topic Structure
```
mash/{device_id}/sensors/temperature
mash/{device_id}/sensors/humidity
mash/{device_id}/sensors/co2
mash/{device_id}/status
mash/{device_id}/commands
mash/{device_id}/alerts
```

---

## 4. Team Structure & Responsibilities

### 4.1 Core Team (8-10 people)
- **Project Manager** (1) - Overall project coordination
- **Backend Developers** (2) - NestJS API development
- **Frontend Developers** (2) - Next.js web development
- **Mobile Developer** (1) - Flutter app development
- **IoT Developer** (1) - Raspberry Pi programming
- **UI/UX Designer** (1) - Interface design
- **DevOps Engineer** (1) - Infrastructure and deployment
- **QA Engineer** (1) - Testing and quality assurance

### 4.2 Additional Resources
- **Hardware Engineer** (Part-time) - IoT device assembly
- **Technical Writer** (Part-time) - Documentation
- **Marketing Specialist** (Part-time) - Launch preparation

---

## 5. Project Timeline

### 5.1 High-Level Schedule
- **Weeks 1-4**: Foundation & Setup
- **Weeks 3-8**: IoT Development (Parallel)
- **Weeks 5-10**: Backend Development
- **Weeks 7-14**: Mobile App Development
- **Weeks 9-16**: Web Platform Development
- **Weeks 11-18**: Admin Dashboard Development
- **Weeks 15-20**: Integration & Testing
- **Weeks 19-22**: Deployment & Launch

**Total Duration**: 22 weeks (approximately 5.5 months)

### 5.2 Milestones
- **Week 4**: Development environment ready
- **Week 8**: IoT device prototype functional
- **Week 10**: Backend APIs complete
- **Week 14**: Mobile app beta ready
- **Week 16**: Web platform beta ready
- **Week 18**: Admin dashboard complete
- **Week 20**: System integration complete
- **Week 22**: Production launch

---

## 6. Resource Requirements

### 6.1 Hardware Requirements
- **Development**: High-performance laptops for developers
- **IoT Testing**: Multiple Raspberry Pi 3 Model B units
- **Sensors**: Complete sensor kits for testing
- **Testing Devices**: Various mobile devices for app testing

### 6.2 Software & Services
- **Development Tools**: IDEs, version control, project management
- **Cloud Services**: AWS/Google Cloud for hosting
- **Third-party APIs**: Payment gateways, analytics
- **Testing Tools**: Automated testing frameworks

### 6.3 Budget Estimation
- **Personnel Costs**: $400,000 - $500,000 (22 weeks)
- **Infrastructure**: $10,000 - $15,000
- **Software Licenses**: $5,000 - $8,000
- **Hardware**: $15,000 - $20,000
- **Marketing**: $20,000 - $30,000

**Total Estimated Budget**: $450,000 - $573,000

---

## 7. Risk Management

### 7.1 Technical Risks
- **IoT Connectivity Issues**: Mitigation through offline functionality
- **Scalability Challenges**: Load testing and performance optimization
- **Integration Complexity**: Incremental integration approach
- **Hardware Failures**: Backup devices and testing protocols

### 7.2 Project Risks
- **Timeline Delays**: Buffer time and parallel development
- **Resource Availability**: Backup team members identification
- **Requirement Changes**: Agile methodology adoption
- **Budget Overruns**: Regular budget monitoring and control

### 7.3 Market Risks
- **Competition**: Unique value proposition focus
- **User Adoption**: Beta testing and user feedback
- **Technology Changes**: Regular technology assessment
- **Regulatory Compliance**: Legal review and compliance checks

---

## 8. Quality Assurance

### 8.1 Testing Strategy
- **Unit Testing**: 80% code coverage minimum
- **Integration Testing**: All API endpoints and integrations
- **End-to-End Testing**: Complete user workflows
- **Performance Testing**: Load and stress testing
- **Security Testing**: Vulnerability assessments

### 8.2 Code Quality Standards
- **Code Reviews**: Mandatory peer reviews
- **Documentation**: Comprehensive API and code documentation
- **Coding Standards**: Consistent coding conventions
- **Version Control**: Git workflow with protected branches

---

## 9. Deployment Strategy

### 9.1 Environment Setup
- **Development**: Local development environments
- **Staging**: Pre-production testing environment
- **Production**: Live system with high availability

### 9.2 Deployment Process
- **Automated Deployment**: CI/CD pipelines
- **Database Migrations**: Automated migration scripts
- **Rollback Strategy**: Quick rollback procedures
- **Monitoring**: Real-time system monitoring

---

## 10. Post-Launch Support

### 10.1 Maintenance Plan
- **Bug Fixes**: Regular bug fix releases
- **Feature Updates**: Quarterly feature releases
- **Security Updates**: Monthly security patches
- **Performance Optimization**: Ongoing optimization

### 10.2 User Support
- **Documentation**: User manuals and tutorials
- **Customer Support**: Help desk and ticketing system
- **Training**: User training programs
- **Community**: User forums and knowledge base

---

## Conclusion

This comprehensive software project plan provides a roadmap for developing the M.A.S.H. system, from initial setup through post-launch support. The plan emphasizes parallel development to optimize timeline, comprehensive testing to ensure quality, and proper risk management to handle potential challenges.

---

## 6. Team Structure & Responsibilities

### Core Team Members (7 people)

| Role | Team Member | Primary Responsibilities | Secondary Responsibilities |
|------|-------------|-------------------------|---------------------------|
| **Project Manager** | Kevin A. Llanes | Project oversight, timeline management, stakeholder communication | Quality assurance, documentation |
| **Backend Developer** | Jhon Keneth Ryan B. Namias | NestJS API development, database architecture, server deployment | DevOps, security implementation |
| **Frontend Developer** | Ma. Catherine H. Bae | Next.js development for e-commerce and admin portals | UI/UX implementation, responsive design |
| **Mobile Developer** | Irheil Mae S. Antang | Flutter app development, mobile UI/UX | Cross-platform optimization, app store management |
| **IoT Developer** | Jin Harold A. Failana | Raspberry Pi programming, sensor integration, hardware setup | MQTT implementation, device testing |
| **Full Stack Developer** | Ronan Renz T. Valencia | Database design, API integration, system architecture | Code review, technical documentation |
| **Database Administrator** | Emmanuel L. Pabua | Database management, data modeling, performance optimization | Backup strategies, migration scripts |

### Team Communication Structure
- **Daily Standups**: 15-minute meetings at 8:00 AM
- **Weekly Sprint Reviews**: Every Friday at 2:00 PM
- **Monthly Stakeholder Updates**: First Monday of each month
- **Emergency Communications**: Slack/Discord for urgent issues

---

## 7. Risk Management

### Risk Assessment Matrix

| Risk ID | Risk Description | Probability | Impact | Risk Level | Mitigation Strategy |
|---------|------------------|-------------|---------|------------|-------------------|
| **R-01** | Hardware supply chain delays | Medium | High | **HIGH** | Order all components in Phase 1, identify alternative suppliers |
| **R-02** | Technology integration complexity | Medium | High | **HIGH** | Early proof-of-concept testing, standardized data formats |
| **R-03** | Scope creep from stakeholders | High | Medium | **MEDIUM** | Strict change control process, phase-based delivery |
| **R-04** | Internet connectivity issues at deployment sites | High | High | **HIGH** | Offline-first architecture with SQLite, robust sync logic |
| **R-05** | Security vulnerabilities | Medium | High | **HIGH** | Security audit, penetration testing, best practices implementation |
| **R-06** | Team member availability | Medium | Medium | **MEDIUM** | Cross-training, documentation, backup assignments |
| **R-07** | Budget overruns | Low | High | **MEDIUM** | Regular budget monitoring, contingency fund (₱3,972) |
| **R-08** | Sensor accuracy and calibration issues | Medium | Medium | **MEDIUM** | Multiple sensor validation, calibration procedures |

### Risk Monitoring and Response
- **Weekly Risk Reviews**: Assess risk status and mitigation effectiveness
- **Escalation Process**: High-risk issues escalated to project manager within 24 hours
- **Contingency Planning**: Alternative solutions prepared for high-impact risks
- **Risk Documentation**: All risks tracked in project management system

---

## 8. Quality Assurance Plan

### Testing Strategy

#### 8.1 Testing Phases
1. **Unit Testing** - Individual component testing
2. **Integration Testing** - Component interaction testing
3. **System Testing** - End-to-end functionality testing
4. **User Acceptance Testing** - Stakeholder validation
5. **Performance Testing** - Load and stress testing
6. **Security Testing** - Vulnerability assessment

#### 8.2 Testing Scope by Component

**Flutter Mobile App**
- [ ] UI/UX testing across different devices
- [ ] Real-time data display accuracy
- [ ] Offline functionality testing
- [ ] Push notification testing
- [ ] Performance on low-end devices

**IoT Device (Raspberry Pi)**
- [ ] Sensor accuracy and calibration
- [ ] Continuous operation testing (72+ hours)
- [ ] Network connectivity resilience
- [ ] Data synchronization testing
- [ ] LCD display functionality

**E-commerce Website**
- [ ] Cross-browser compatibility
- [ ] Payment gateway integration
- [ ] Order processing workflow
- [ ] Seller portal functionality
- [ ] Responsive design testing

**Admin Dashboard**
- [ ] User management operations
- [ ] Device monitoring accuracy
- [ ] CMS functionality
- [ ] Analytics and reporting
- [ ] Security access controls

**Backend API**
- [ ] API endpoint functionality
- [ ] Database operations
- [ ] Authentication and authorization
- [ ] Real-time communication
- [ ] Load testing

#### 8.3 Quality Standards
- **Code Coverage**: Minimum 80% for backend, 70% for frontend
- **Performance**: <2 second API response times
- **Uptime**: 99.5% system availability target
- **Security**: Zero critical vulnerabilities in production
- **Usability**: 90% user satisfaction in UAT

---

## 9. Budget Allocation

### Total Project Budget: ₱20,000.00

| Category | Allocated Amount | Percentage | Usage Details |
|----------|------------------|------------|---------------|
| **Hardware Components** | ₱16,028.00 | 80.14% | IoT sensors, Raspberry Pi, actuators, grow tent |
| **Software Development Tools** | ₱1,500.00 | 7.50% | Development licenses, cloud services, testing tools |
| **Testing & Prototyping** | ₱1,000.00 | 5.00% | Additional hardware for testing, prototyping materials |
| **Documentation & Training** | ₱500.00 | 2.50% | Printing, training materials, documentation tools |
| **Contingency Fund** | ₱972.00 | 4.86% | Unexpected expenses, component replacements |

### Budget Monitoring
- **Weekly Budget Reviews**: Track expenses against allocation
- **Approval Process**: Expenses >₱500 require project manager approval
- **Cost Control**: Monthly budget variance analysis
- **Contingency Usage**: Requires team consensus for allocation

---

## 10. Communication Plan

### Communication Channels

#### 10.1 Internal Team Communication
- **Primary Tool**: Discord/Slack for daily communication
- **Video Conferencing**: Google Meet for meetings
- **Project Management**: Jira/Trello for task tracking
- **Documentation**: Confluence/Notion for project documentation
- **Code Collaboration**: GitHub for version control and code reviews

#### 10.2 Stakeholder Communication
- **Weekly Reports**: Progress updates every Friday
- **Monthly Presentations**: Stakeholder demos on first Monday
- **Emergency Communication**: 24-hour response commitment
- **Documentation Sharing**: Google Drive for document access

#### 10.3 Communication Schedule
- **Daily Standups**: 8:00 AM - 8:15 AM (Mon-Fri)
- **Sprint Planning**: Every Monday 9:00 AM - 10:00 AM
- **Sprint Review**: Every Friday 2:00 PM - 3:00 PM
- **Stakeholder Updates**: First Monday of month 10:00 AM - 11:00 AM

---

## 11. Success Criteria & KPIs

### 11.1 Technical Success Metrics
- [ ] System uptime: >99.5%
- [ ] API response time: <2 seconds
- [ ] Data synchronization delay: <5 seconds
- [ ] Mobile app crash rate: <0.1%
- [ ] IoT device connectivity: >95%

### 11.2 Business Success Metrics
- [ ] User adoption: 50+ growers in first 3 months
- [ ] E-commerce transactions: 100+ orders in first quarter
- [ ] Yield improvement: 20% increase demonstrated
- [ ] Contamination reduction: 85% decrease in incidents
- [ ] User satisfaction: >4.5/5 rating

### 11.3 Project Success Criteria
- [ ] On-time delivery within 26-week timeline
- [ ] Budget adherence within ₱20,000 allocation
- [ ] All functional requirements delivered
- [ ] Stakeholder acceptance achieved
- [ ] System ready for production use

---

## 12. Post-Launch Support Plan

### 12.1 Support Structure
- **Level 1 Support**: Basic user inquiries and troubleshooting
- **Level 2 Support**: Technical issues and system configuration
- **Level 3 Support**: Complex system issues and development changes

### 12.2 Maintenance Schedule
- **Daily**: System monitoring and alert response
- **Weekly**: Performance optimization and minor updates
- **Monthly**: Security patches and feature enhancements
- **Quarterly**: Major system updates and hardware maintenance

### 12.3 Support Resources
- **Documentation**: User manuals and technical guides
- **Training**: On-site training for growers and administrators
- **Help Desk**: 24/7 support hotline and email
- **Community**: User forum and knowledge base

---

## 13. Conclusion

The M.A.S.H. software project plan provides a comprehensive roadmap for developing an integrated IoT and e-commerce platform for automated mushroom cultivation. With a dedicated team of 7 developers, a realistic 26-week timeline, and a well-allocated ₱20,000 budget, this project is positioned to revolutionize small-scale mushroom farming in the Philippines.

The success of this project depends on:
- **Strong team collaboration** and adherence to established processes
- **Effective risk management** and proactive issue resolution
- **Continuous stakeholder engagement** and feedback incorporation
- **Quality-focused development** with comprehensive testing
- **Realistic timeline management** with achievable milestones

By following this detailed project plan, the M.A.S.H. system will deliver significant value to mushroom growers through improved yields, reduced contamination, and enhanced market access, ultimately contributing to food security and sustainable agriculture in the Philippines.

---

**Document Version**: 1.0  
**Last Updated**: October 1, 2025  
**Next Review**: October 8, 2025  
**Approved By**: Kevin A. Llanes, Project Manager