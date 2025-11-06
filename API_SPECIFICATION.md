# MASH IoT Device API Specification

## Overview
This document specifies the REST API endpoints that need to be implemented in the MASH Backend for IoT device management, sensor data collection, and actuator control.

**Version:** 1.0  
**Base URL:** `https://mash-backend-api-production.up.railway.app/api/v1`  
**Authentication:** Bearer Token (JWT)

---

## Table of Contents
1. [Device Management](#device-management)
2. [Sensor Data](#sensor-data)
3. [Actuator Control](#actuator-control)
4. [Device Status & Health](#device-status--health)
5. [Data Models](#data-models)
6. [Webhooks & Real-time](#webhooks--real-time)

---

## Device Management

### 1. Register Device
Register a new IoT device to a user's account.

**Endpoint:** `POST /devices`  
**Auth:** Required  
**Request Body:**
```json
{
  "deviceId": "MASH-A1-CAL25-AC2415",
  "name": "Mushroom Prototype Chamber",
  "type": "MUSHROOM_CHAMBER",
  "location": "Lab Room A",
  "ipAddress": "192.168.1.100",
  "port": 5000,
  "configuration": {
    "spawningTempMin": 20,
    "spawningTempMax": 25,
    "fruitingTempMin": 15,
    "fruitingTempMax": 20,
    "spawningHumidityMin": 90,
    "spawningHumidityMax": 95,
    "fruitingHumidityMin": 85,
    "fruitingHumidityMax": 90,
    "spawningCO2Min": 10000,
    "fruitingCO2Min": 500,
    "fruitingCO2Max": 800
  }
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "statusCode": 201,
  "data": {
    "id": "uuid-device-123",
    "deviceId": "MASH-A1-CAL25-AC2415",
    "name": "Mushroom Prototype Chamber",
    "type": "MUSHROOM_CHAMBER",
    "status": "OFFLINE",
    "userId": "uuid-user-456",
    "ipAddress": "192.168.1.100",
    "port": 5000,
    "lastSeen": null,
    "createdAt": "2024-11-06T06:00:00Z",
    "updatedAt": "2024-11-06T06:00:00Z"
  }
}
```

---

### 2. Get User's Devices
Retrieve all devices registered to the authenticated user.

**Endpoint:** `GET /devices`  
**Auth:** Required  
**Query Parameters:**
- `status` (optional): Filter by status (`ONLINE`, `OFFLINE`, `MAINTENANCE`)
- `type` (optional): Filter by device type
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)

**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "data": {
    "devices": [
      {
        "id": "uuid-device-123",
        "deviceId": "MASH-A1-CAL25-AC2415",
        "name": "Mushroom Prototype Chamber",
        "type": "MUSHROOM_CHAMBER",
        "status": "ONLINE",
        "ipAddress": "192.168.1.100",
        "port": 5000,
        "lastSeen": "2024-11-06T06:30:00Z",
        "currentMode": "SPAWNING",
        "createdAt": "2024-11-06T06:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 1,
      "totalPages": 1
    }
  }
}
```

---

### 3. Get Device Details
Get detailed information about a specific device.

**Endpoint:** `GET /devices/:deviceId`  
**Auth:** Required  
**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "data": {
    "id": "uuid-device-123",
    "deviceId": "MASH-A1-CAL25-AC2415",
    "name": "Mushroom Prototype Chamber",
    "type": "MUSHROOM_CHAMBER",
    "status": "ONLINE",
    "ipAddress": "192.168.1.100",
    "port": 5000,
    "currentMode": "SPAWNING",
    "lastSeen": "2024-11-06T06:30:00Z",
    "configuration": {
      "spawningTempMin": 20,
      "spawningTempMax": 25,
      "fruitingTempMin": 15,
      "fruitingTempMax": 20
    },
    "latestReading": {
      "temperature": 22.5,
      "humidity": 92.3,
      "co2": 12500,
      "timestamp": "2024-11-06T06:30:00Z"
    },
    "actuators": {
      "blower_fan": false,
      "exhaust_fan": false,
      "humidifier": true,
      "led_lights": false
    },
    "createdAt": "2024-11-06T06:00:00Z",
    "updatedAt": "2024-11-06T06:30:00Z"
  }
}
```

---

### 4. Update Device
Update device information.

**Endpoint:** `PATCH /devices/:deviceId`  
**Auth:** Required  
**Request Body:**
```json
{
  "name": "Updated Chamber Name",
  "location": "New Location",
  "ipAddress": "192.168.1.101",
  "configuration": {
    "spawningTempMin": 21
  }
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "data": {
    "id": "uuid-device-123",
    "deviceId": "MASH-A1-CAL25-AC2415",
    "name": "Updated Chamber Name",
    "updatedAt": "2024-11-06T06:35:00Z"
  }
}
```

---

### 5. Delete Device
Remove a device from user's account.

**Endpoint:** `DELETE /devices/:deviceId`  
**Auth:** Required  
**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "message": "Device deleted successfully"
}
```

---

## Sensor Data

### 6. Submit Sensor Reading
IoT device submits sensor data to backend (called by RPi).

**Endpoint:** `POST /devices/:deviceId/readings`  
**Auth:** Device API Key (in header: `X-Device-Key`)  
**Request Body:**
```json
{
  "temperature": 22.5,
  "humidity": 92.3,
  "co2": 12500,
  "mode": "SPAWNING",
  "alert": false,
  "timestamp": "2024-11-06T06:30:00Z"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "statusCode": 201,
  "data": {
    "id": "uuid-reading-789",
    "deviceId": "MASH-A1-CAL25-AC2415",
    "temperature": 22.5,
    "humidity": 92.3,
    "co2": 12500,
    "mode": "SPAWNING",
    "alert": false,
    "timestamp": "2024-11-06T06:30:00Z",
    "createdAt": "2024-11-06T06:30:05Z"
  }
}
```

---

### 7. Get Sensor History
Retrieve historical sensor data for a device.

**Endpoint:** `GET /devices/:deviceId/readings`  
**Auth:** Required  
**Query Parameters:**
- `startDate` (optional): ISO 8601 date
- `endDate` (optional): ISO 8601 date
- `limit` (optional): Number of readings (default: 100, max: 1000)
- `interval` (optional): Aggregation interval (`1m`, `5m`, `15m`, `1h`, `1d`)

**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "data": {
    "readings": [
      {
        "id": "uuid-reading-789",
        "temperature": 22.5,
        "humidity": 92.3,
        "co2": 12500,
        "mode": "SPAWNING",
        "alert": false,
        "timestamp": "2024-11-06T06:30:00Z"
      },
      {
        "id": "uuid-reading-790",
        "temperature": 22.3,
        "humidity": 91.8,
        "co2": 12300,
        "mode": "SPAWNING",
        "alert": false,
        "timestamp": "2024-11-06T06:25:00Z"
      }
    ],
    "count": 2,
    "startDate": "2024-11-06T06:00:00Z",
    "endDate": "2024-11-06T06:30:00Z"
  }
}
```

---

### 8. Get Latest Reading
Get the most recent sensor reading for a device.

**Endpoint:** `GET /devices/:deviceId/readings/latest`  
**Auth:** Required  
**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "data": {
    "id": "uuid-reading-789",
    "temperature": 22.5,
    "humidity": 92.3,
    "co2": 12500,
    "mode": "SPAWNING",
    "alert": false,
    "timestamp": "2024-11-06T06:30:00Z"
  }
}
```

---

### 9. Get Analytics
Get aggregated analytics for a device.

**Endpoint:** `GET /devices/:deviceId/analytics`  
**Auth:** Required  
**Query Parameters:**
- `period`: Time period (`24h`, `7d`, `30d`, `90d`)
- `metrics`: Comma-separated metrics (`temperature`, `humidity`, `co2`, `all`)

**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "data": {
    "period": "24h",
    "temperature": {
      "min": 20.5,
      "max": 24.2,
      "avg": 22.3,
      "current": 22.5
    },
    "humidity": {
      "min": 88.5,
      "max": 95.0,
      "avg": 92.1,
      "current": 92.3
    },
    "co2": {
      "min": 11000,
      "max": 13500,
      "avg": 12250,
      "current": 12500
    },
    "alerts": {
      "total": 3,
      "resolved": 3,
      "active": 0
    }
  }
}
```

---

## Actuator Control

### 10. Set Device Mode
Change device operating mode (Spawning/Fruiting).

**Endpoint:** `POST /devices/:deviceId/mode`  
**Auth:** Required  
**Request Body:**
```json
{
  "mode": "FRUITING"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "data": {
    "deviceId": "MASH-A1-CAL25-AC2415",
    "mode": "FRUITING",
    "previousMode": "SPAWNING",
    "changedAt": "2024-11-06T06:35:00Z"
  }
}
```

---

### 11. Control Actuator
Control a specific actuator (relay).

**Endpoint:** `POST /devices/:deviceId/actuators/:actuatorName`  
**Auth:** Required  
**Request Body:**
```json
{
  "state": true
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "data": {
    "deviceId": "MASH-A1-CAL25-AC2415",
    "actuator": "humidifier",
    "state": true,
    "timestamp": "2024-11-06T06:35:00Z"
  }
}
```

---

### 12. Get Actuator States
Get current state of all actuators.

**Endpoint:** `GET /devices/:deviceId/actuators`  
**Auth:** Required  
**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "data": {
    "blower_fan": false,
    "exhaust_fan": false,
    "humidifier": true,
    "led_lights": false,
    "lastUpdated": "2024-11-06T06:35:00Z"
  }
}
```

---

### 13. Submit Actuator State (from IoT)
IoT device reports actuator state changes.

**Endpoint:** `POST /devices/:deviceId/actuators/state`  
**Auth:** Device API Key  
**Request Body:**
```json
{
  "actuators": {
    "blower_fan": false,
    "exhaust_fan": false,
    "humidifier": true,
    "led_lights": false
  },
  "timestamp": "2024-11-06T06:35:00Z"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "message": "Actuator states updated"
}
```

---

## Device Status & Health

### 14. Update Device Status (Heartbeat)
IoT device sends periodic heartbeat to indicate it's online.

**Endpoint:** `POST /devices/:deviceId/heartbeat`  
**Auth:** Device API Key  
**Request Body:**
```json
{
  "status": "ONLINE",
  "ipAddress": "192.168.1.100",
  "uptime": 86400,
  "timestamp": "2024-11-06T06:35:00Z"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "message": "Heartbeat received"
}
```

---

### 15. Get Device Health
Get device health metrics.

**Endpoint:** `GET /devices/:deviceId/health`  
**Auth:** Required  
**Response:** `200 OK`
```json
{
  "success": true,
  "statusCode": 200,
  "data": {
    "status": "HEALTHY",
    "uptime": 86400,
    "lastSeen": "2024-11-06T06:35:00Z",
    "connectivity": {
      "serialConnected": true,
      "networkLatency": 25
    },
    "sensors": {
      "scd41": "OPERATIONAL",
      "lcd": "OPERATIONAL"
    },
    "actuators": {
      "blower_fan": "OPERATIONAL",
      "exhaust_fan": "OPERATIONAL",
      "humidifier": "OPERATIONAL",
      "led_lights": "OPERATIONAL"
    }
  }
}
```

---

## Data Models

### Device
```typescript
interface Device {
  id: string;
  deviceId: string;  // Unique hardware ID
  userId: string;
  name: string;
  type: DeviceType;
  status: DeviceStatus;
  ipAddress?: string;
  port?: number;
  currentMode?: GrowingMode;
  configuration?: DeviceConfiguration;
  lastSeen?: Date;
  createdAt: Date;
  updatedAt: Date;
}

enum DeviceType {
  MUSHROOM_CHAMBER = 'MUSHROOM_CHAMBER',
  ENVIRONMENTAL_SENSOR = 'ENVIRONMENTAL_SENSOR'
}

enum DeviceStatus {
  ONLINE = 'ONLINE',
  OFFLINE = 'OFFLINE',
  MAINTENANCE = 'MAINTENANCE',
  ERROR = 'ERROR'
}

enum GrowingMode {
  SPAWNING = 'SPAWNING',
  FRUITING = 'FRUITING'
}
```

### Sensor Reading
```typescript
interface SensorReading {
  id: string;
  deviceId: string;
  temperature: number;  // Celsius
  humidity: number;     // Percentage
  co2: number;          // PPM
  mode: GrowingMode;
  alert: boolean;
  timestamp: Date;
  createdAt: Date;
}
```

### Actuator State
```typescript
interface ActuatorState {
  deviceId: string;
  blower_fan: boolean;
  exhaust_fan: boolean;
  humidifier: boolean;
  led_lights: boolean;
  lastUpdated: Date;
}
```

---

## Webhooks & Real-time

### 16. WebSocket Connection
Real-time sensor data streaming.

**Endpoint:** `WS /devices/:deviceId/stream`  
**Auth:** Token in query param `?token=xxx`  
**Events:**
```json
{
  "event": "sensor_reading",
  "data": {
    "temperature": 22.5,
    "humidity": 92.3,
    "co2": 12500,
    "timestamp": "2024-11-06T06:35:00Z"
  }
}

{
  "event": "actuator_change",
  "data": {
    "actuator": "humidifier",
    "state": true,
    "timestamp": "2024-11-06T06:35:00Z"
  }
}

{
  "event": "alert",
  "data": {
    "type": "CO2_LOW",
    "message": "CO2 level below threshold",
    "value": 9500,
    "timestamp": "2024-11-06T06:35:00Z"
  }
}
```

---

## Authentication

### Device API Key
IoT devices use a unique API key for authentication.

**Header:** `X-Device-Key: device-api-key-here`

**Generate Device Key:**
```
POST /devices/:deviceId/api-key
```

**Response:**
```json
{
  "success": true,
  "data": {
    "apiKey": "mash_device_xxxxxxxxxxxxxxxx",
    "expiresAt": null
  }
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "statusCode": 400,
  "error": "Bad Request",
  "message": "Invalid device configuration",
  "timestamp": "2024-11-06T06:35:00Z"
}
```

**Common Status Codes:**
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict (e.g., device already registered)
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## Rate Limiting

- **User API:** 100 requests/minute
- **Device API:** 1000 requests/minute (for sensor data submission)
- **WebSocket:** 1 connection per device

---

## Notes for Backend Developer

1. **Database Schema:**
   - Create tables: `devices`, `sensor_readings`, `actuator_states`, `device_logs`
   - Index on: `deviceId`, `userId`, `timestamp`
   - Consider time-series database for sensor readings (e.g., TimescaleDB)

2. **Real-time:**
   - Implement WebSocket using Socket.io or native WS
   - Use Redis for pub/sub between API instances

3. **Data Retention:**
   - Raw sensor data: 90 days
   - Aggregated data (hourly): 1 year
   - Aggregated data (daily): Forever

4. **Security:**
   - Validate device ownership before allowing control
   - Rate limit actuator commands to prevent abuse
   - Log all actuator changes for audit trail

5. **Performance:**
   - Batch insert sensor readings
   - Cache latest reading per device
   - Use background jobs for analytics calculation

---

**End of API Specification**
