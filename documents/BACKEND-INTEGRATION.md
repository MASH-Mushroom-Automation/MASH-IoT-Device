# MASH IoT Device - Backend Integration Fix

## 🚨 **Critical Issue: CSRF Protection Blocking IoT Device Registration**

### **Problem Summary**
The MASH IoT Device is receiving a **403 CSRF token missing** error when attempting to register with the backend API. This prevents the device from syncing sensor data and receiving commands from the cloud.

**Error Details:**
```json
{
  "success": false,
  "statusCode": 403,
  "timestamp": "2025-11-11T09:57:26.943Z",
  "path": "/api/v1/devices",
  "method": "POST",
  "error": {
    "type": "ForbiddenException",
    "code": "INTERNAL_SERVER_ERROR", 
    "message": "CSRF token missing"
  }
}
```

**Root Cause:** CSRF middleware is blocking legitimate IoT device API calls because IoT devices cannot obtain/send CSRF tokens like web browsers.

---

## 🎯 **Recommended Solution: IoT API Key Authentication System**

### **Why This Approach?**
- ✅ **Security**: Proper authentication without disabling CSRF for web clients
- ✅ **Scalability**: Supports multiple IoT devices with individual keys
- ✅ **Maintainability**: Clean separation between web and IoT authentication
- ✅ **Auditability**: Track all IoT device API calls
- ✅ **Future-proof**: Easy to extend for device management features

---

## 🔧 **Implementation Guide**

### **Step 1: Create IoT API Key Database Schema**

```sql
-- Add to your database migration
CREATE TABLE iot_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(255) UNIQUE NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    device_name VARCHAR(255),
    device_type VARCHAR(100) DEFAULT 'MASH_CHAMBER',
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    permissions JSONB DEFAULT '["device:register", "sensor:write", "status:update"]'::jsonb,
    
    INDEX idx_iot_api_keys_device_id (device_id),
    INDEX idx_iot_api_keys_api_key (api_key),
    INDEX idx_iot_api_keys_active (is_active)
);
```

### **Step 2: Create IoT Authentication Middleware**

```typescript
// src/common/middleware/iot-auth.middleware.ts
import { Injectable, NestMiddleware, UnauthorizedException } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { IoTApiKey } from '../entities/iot-api-key.entity';

@Injectable()
export class IoTAuthMiddleware implements NestMiddleware {
  constructor(
    @InjectRepository(IoTApiKey)
    private readonly iotApiKeyRepository: Repository<IoTApiKey>,
  ) {}

  async use(req: Request, res: Response, next: NextFunction) {
    const apiKey = this.extractApiKey(req);
    
    if (!apiKey) {
      return next(); // Let other auth methods handle it
    }

    try {
      const iotKey = await this.iotApiKeyRepository.findOne({
        where: { api_key: apiKey, is_active: true },
        relations: ['user']
      });

      if (!iotKey) {
        throw new UnauthorizedException('Invalid IoT API Key');
      }

      // Update last used timestamp
      await this.iotApiKeyRepository.update(iotKey.id, {
        last_used: new Date()
      });

      // Attach IoT device info to request
      req['isIoTDevice'] = true;
      req['deviceId'] = iotKey.device_id;
      req['deviceName'] = iotKey.device_name;
      req['userId'] = iotKey.user_id;
      req['iotPermissions'] = iotKey.permissions;

      next();
    } catch (error) {
      throw new UnauthorizedException('IoT Authentication Failed');
    }
  }

  private extractApiKey(req: Request): string | null {
    // Check multiple header formats
    const authHeader = req.headers.authorization;
    const apiKeyHeader = req.headers['x-api-key'];
    
    if (authHeader?.startsWith('Bearer iot_')) {
      return authHeader.replace('Bearer ', '');
    }
    
    if (typeof apiKeyHeader === 'string' && apiKeyHeader.startsWith('iot_')) {
      return apiKeyHeader;
    }
    
    return null;
  }
}
```

### **Step 3: Update CSRF Protection Middleware**

```typescript
// src/common/middleware/csrf-protection.middleware.ts
import { Injectable, NestMiddleware, ForbiddenException } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class CsrfProtectionMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    // Skip CSRF protection for IoT device requests
    if (this.isIoTRequest(req)) {
      return next();
    }

    // Apply CSRF protection for web requests
    if (!this.validateCsrfToken(req)) {
      throw new ForbiddenException('CSRF token missing or invalid');
    }

    next();
  }

  private isIoTRequest(req: Request): boolean {
    // Check if request is from authenticated IoT device
    if (req['isIoTDevice']) {
      return true;
    }

    // Check for IoT device indicators
    const userAgent = req.headers['user-agent'];
    const apiKey = req.headers['x-api-key'] || req.headers.authorization;
    
    return (
      userAgent?.includes('MASH-IoT-Device') ||
      apiKey?.includes('iot_') ||
      req.headers['x-requested-with'] === 'XMLHttpRequest'
    );
  }

  private validateCsrfToken(req: Request): boolean {
    // Your existing CSRF validation logic
    const token = req.headers['x-csrf-token'] || req.body._token;
    return this.isValidCsrfToken(token);
  }
}
```

### **Step 4: Create IoT Device Controller**

```typescript
// src/modules/iot/controllers/iot-devices.controller.ts
import { Controller, Post, Put, Body, Param, UseGuards, Req } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiSecurity } from '@nestjs/swagger';
import { IoTAuthGuard } from '../guards/iot-auth.guard';
import { DevicesService } from '../../devices/devices.service';
import { SensorDataService } from '../../sensor-data/sensor-data.service';

@ApiTags('IoT Devices')
@ApiSecurity('IoT-API-Key')
@Controller('api/v1/iot')
@UseGuards(IoTAuthGuard)
export class IoTDevicesController {
  constructor(
    private readonly devicesService: DevicesService,
    private readonly sensorDataService: SensorDataService,
  ) {}

  @Post('devices/register')
  @ApiOperation({ summary: 'Register IoT device with backend' })
  async registerDevice(@Body() deviceData: RegisterDeviceDto, @Req() req) {
    const deviceId = req.deviceId || deviceData.serialNumber;
    
    return this.devicesService.registerOrUpdateDevice({
      ...deviceData,
      deviceId,
      userId: req.userId,
      registeredAt: new Date(),
      lastSeen: new Date(),
      status: 'ONLINE'
    });
  }

  @Post('devices/:deviceId/sensor-data')
  @ApiOperation({ summary: 'Receive sensor data from IoT device' })
  async receiveSensorData(
    @Param('deviceId') deviceId: string,
    @Body() sensorData: SensorDataDto,
    @Req() req
  ) {
    // Verify device ownership
    if (req.deviceId !== deviceId) {
      throw new ForbiddenException('Device ID mismatch');
    }

    return this.sensorDataService.storeSensorData({
      ...sensorData,
      deviceId,
      userId: req.userId,
      receivedAt: new Date()
    });
  }

  @Put('devices/:deviceId/status')
  @ApiOperation({ summary: 'Update device status and health' })
  async updateDeviceStatus(
    @Param('deviceId') deviceId: string,
    @Body() statusData: DeviceStatusDto,
    @Req() req
  ) {
    if (req.deviceId !== deviceId) {
      throw new ForbiddenException('Device ID mismatch');
    }

    return this.devicesService.updateDeviceStatus(deviceId, {
      ...statusData,
      lastSeen: new Date(),
      updatedBy: 'device'
    });
  }
}
```

### **Step 5: Create IoT API Key Management Service**

```typescript
// src/modules/iot/services/iot-api-key.service.ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { IoTApiKey } from '../entities/iot-api-key.entity';
import * as crypto from 'crypto';

@Injectable()
export class IoTApiKeyService {
  constructor(
    @InjectRepository(IoTApiKey)
    private readonly iotApiKeyRepository: Repository<IoTApiKey>,
  ) {}

  async generateApiKey(
    deviceId: string,
    deviceName: string,
    userId: string,
    deviceType: string = 'MASH_CHAMBER'
  ): Promise<string> {
    // Generate secure API key
    const randomBytes = crypto.randomBytes(32).toString('hex');
    const apiKey = `iot_${deviceId}_${randomBytes}`;

    // Store in database
    await this.iotApiKeyRepository.save({
      device_id: deviceId,
      device_name: deviceName,
      device_type: deviceType,
      user_id: userId,
      api_key: apiKey,
      is_active: true,
      permissions: ['device:register', 'sensor:write', 'status:update']
    });

    return apiKey;
  }

  async revokeApiKey(deviceId: string): Promise<void> {
    await this.iotApiKeyRepository.update(
      { device_id: deviceId },
      { is_active: false }
    );
  }

  async rotateApiKey(deviceId: string): Promise<string> {
    // Revoke old key
    await this.revokeApiKey(deviceId);
    
    // Generate new key
    const device = await this.iotApiKeyRepository.findOne({
      where: { device_id: deviceId }
    });
    
    return this.generateApiKey(
      deviceId,
      device.device_name,
      device.user_id,
      device.device_type
    );
  }
}
```

### **Step 6: Update Application Module**

```typescript
// src/app.module.ts
import { Module, MiddlewareConsumer, NestModule } from '@nestjs/common';
import { IoTAuthMiddleware } from './common/middleware/iot-auth.middleware';
import { CsrfProtectionMiddleware } from './common/middleware/csrf-protection.middleware';

@Module({
  // ... existing imports
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    // Apply IoT auth middleware first
    consumer
      .apply(IoTAuthMiddleware)
      .forRoutes('api/v1/iot/*');
    
    // Apply CSRF protection to all routes (will skip IoT routes)
    consumer
      .apply(CsrfProtectionMiddleware)
      .forRoutes('*');
  }
}
```

---

## 🔑 **API Key Generation**

### **Manual Generation (For Initial Setup)**

```sql
-- Generate API key for device MASH-A1-CAL25-D5A91F
INSERT INTO iot_api_keys (
    device_id,
    device_name,
    device_type,
    user_id,
    api_key,
    is_active
) VALUES (
    'MASH-A1-CAL25-D5A91F',
    'MASH Chamber #1',
    'MASH_CHAMBER',
    'your-user-uuid-here',
    'iot_MASH-A1-CAL25-D5A91F_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6',
    true
);
```

### **Programmatic Generation (Admin API)**

```typescript
// Add to admin controller
@Post('admin/iot/generate-key')
async generateIoTApiKey(@Body() data: { deviceId: string, deviceName: string, userId: string }) {
  const apiKey = await this.iotApiKeyService.generateApiKey(
    data.deviceId,
    data.deviceName,
    data.userId
  );
  
  return { apiKey, deviceId: data.deviceId };
}
```

---

## 🧪 **Testing the Implementation**

### **Test 1: Device Registration**
```bash
curl -X POST https://mash-backend-api-production.up.railway.app/api/v1/iot/devices/register \
  -H "Content-Type: application/json" \
  -H "X-API-Key: iot_MASH-A1-CAL25-D5A91F_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6" \
  -H "User-Agent: MASH-IoT-Device/MASH-A1-CAL25-D5A91F" \
  -d '{
    "serialNumber": "MASH-A1-CAL25-D5A91F",
    "name": "MASH Chamber #1",
    "type": "MASH_CHAMBER",
    "location": "Laboratory",
    "firmware": "1.0.0"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "id": "device-uuid",
    "deviceId": "MASH-A1-CAL25-D5A91F",
    "name": "MASH Chamber #1",
    "status": "ONLINE",
    "registeredAt": "2025-11-11T18:00:00Z"
  }
}
```

### **Test 2: Sensor Data Submission**
```bash
curl -X POST https://mash-backend-api-production.up.railway.app/api/v1/iot/devices/MASH-A1-CAL25-D5A91F/sensor-data \
  -H "Content-Type: application/json" \
  -H "X-API-Key: iot_MASH-A1-CAL25-D5A91F_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6" \
  -d '{
    "temperature": 22.5,
    "humidity": 85.2,
    "co2": 950,
    "mode": "f",
    "timestamp": "2025-11-11T18:00:00Z"
  }'
```

---

## 🔒 **Security Considerations**

### **API Key Security**
- ✅ **Unique per device**: Each device has its own API key
- ✅ **Scoped permissions**: Keys limited to device-specific operations
- ✅ **Rotation support**: Keys can be rotated without downtime
- ✅ **Audit trail**: All API calls logged with device identification

### **Rate Limiting**
```typescript
// Add rate limiting for IoT endpoints
@UseGuards(ThrottlerGuard)
@Throttle(100, 60) // 100 requests per minute per device
export class IoTDevicesController {
  // ... controller methods
}
```

### **IP Whitelisting (Optional)**
```typescript
// For high-security deployments
@UseGuards(IoTIPWhitelistGuard)
export class IoTDevicesController {
  // ... controller methods
}
```

---

## 📋 **Deployment Checklist**

### **Backend Changes**
- [ ] Create IoT API key database table
- [ ] Implement IoT authentication middleware
- [ ] Update CSRF middleware to skip IoT requests
- [ ] Create IoT device controller with new endpoints
- [ ] Add IoT API key management service
- [ ] Update application module middleware configuration
- [ ] Generate API key for device `MASH-A1-CAL25-D5A91F`

### **IoT Device Configuration**
- [ ] Update `.env` file with new API key
- [ ] Update backend client to use new endpoints
- [ ] Test device registration and sensor data sync

### **Environment Variables**
```bash
# Add to IoT device .env
BACKEND_API_URL=https://mash-backend-api-production.up.railway.app/api/v1/iot
BACKEND_API_KEY=iot_MASH-A1-CAL25-D5A91F_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

---

## 🎯 **Expected Results**

After implementation, the IoT device logs should show:
```
✅ Backend client initialized: https://mash-backend-api-production.up.railway.app/api/v1/iot
✅ Device registered with backend successfully
✅ Sensor data synced to backend
✅ Device status updated successfully
✅ No more CSRF errors
```