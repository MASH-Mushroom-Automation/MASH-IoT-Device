# Backend & Firebase Setup Guide for MASH IoT Device

## Overview
This guide will help you configure the MASH IoT Device to connect to the Backend Server (Railway) and Firebase for real-time data synchronization and cloud messaging.

## Configuration Files

### 1. Environment Variables (`.env`)
Use the `.env.iot` file as a template and rename it to `.env`:

```bash
mv .env.iot .env
```

### 2. Device Configuration (`config/device_config.yaml`)
The YAML configuration is already set up with the correct values.

## Backend API Configuration

### Current Setup
✅ **Backend URL**: `https://mash-backend-api-production.up.railway.app/api/v1`
✅ **Device ID**: `MASH-A1-CAL25-D5A91F`
✅ **Device Name**: `MASH Chamber #1`

### Environment Variables
```bash
BACKEND_API_URL=https://mash-backend-api-production.up.railway.app/api/v1
BACKEND_API_KEY=
BACKEND_TIMEOUT=30
```

**Note:** `BACKEND_API_KEY` is currently empty. If the backend requires authentication, you'll need to add an API key.

## Firebase Configuration

### Current Setup
✅ **Project ID**: `mash-5b627`
✅ **Database URL**: `https://mash-5b627-default-rtdb.firebaseio.com`
✅ **Service Account**: `firebase-adminsdk-fbsvc@mash-5b627.iam.gserviceaccount.com`
✅ **Private Key**: Configured in `.env`

### Environment Variables
```bash
FIREBASE_PROJECT_ID=mash-5b627
FIREBASE_DATABASE_URL=https://mash-5b627-default-rtdb.firebaseio.com
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@mash-5b627.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
```

## Testing the Connection

### 1. Test Backend Connection
```bash
# From the IoT Device
curl https://mash-backend-api-production.up.railway.app/api/v1/health
```

Expected response:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-11-11T15:00:00.000Z"
  }
}
```

### 2. Test Device Registration
```bash
# Register device with backend
curl -X POST https://mash-backend-api-production.up.railway.app/api/v1/devices/register \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "MASH-A1-CAL25-D5A91F",
    "deviceName": "MASH Chamber #1",
    "deviceType": "MASH_CHAMBER",
    "model": "AlphaPrototype"
  }'
```

### 3. Test Firebase Connection
The IoT Device will automatically connect to Firebase when it starts. Check the logs:

```bash
python3 integrated_server.py
```

Look for:
```
INFO - Firebase initialized successfully
INFO - Connected to Firebase Realtime Database
```

## Integration Points

### 1. Sensor Data Sync
The IoT Device will automatically sync sensor data to both:
- **Backend API**: `/api/v1/devices/{deviceId}/sensor-data`
- **Firebase**: `/devices/{deviceId}/sensorData`

### 2. Real-time Updates
Firebase Realtime Database provides instant updates to:
- Mobile app
- Web dashboard
- Other connected clients

### 3. Command Execution
The device listens for commands from:
- **Backend API**: HTTP REST endpoints
- **Firebase**: Real-time database listeners

## Configuration Checklist

### ✅ Backend Configuration
- [x] Backend URL configured
- [x] Device ID set
- [x] Device name set
- [ ] API key configured (if required)
- [x] Timeout set (30 seconds)

### ✅ Firebase Configuration
- [x] Project ID configured
- [x] Database URL configured
- [x] Service account email configured
- [x] Private key configured

### ✅ Device Configuration
- [x] Device ID matches backend
- [x] Device name set
- [x] Device type set
- [x] Serial number set

## Troubleshooting

### Backend Connection Issues

**Problem**: Cannot connect to backend
```
ERROR: Failed to connect to backend: Connection refused
```

**Solutions**:
1. Check internet connection
2. Verify backend URL is correct
3. Test backend health endpoint
4. Check firewall settings

### Firebase Connection Issues

**Problem**: Firebase authentication failed
```
ERROR: Firebase authentication failed
```

**Solutions**:
1. Verify `FIREBASE_PRIVATE_KEY` is correctly formatted
2. Check service account permissions
3. Ensure project ID is correct
4. Verify database URL is accessible

### API Key Issues

**Problem**: Backend returns 401 Unauthorized
```
ERROR: Backend API returned 401: Unauthorized
```

**Solution**:
1. Add `BACKEND_API_KEY` to `.env`
2. Get API key from backend admin
3. Restart the IoT Device

## Monitoring

### Check Device Status
```bash
# Local API
curl http://localhost:5000/api/status

# Check if device is registered with backend
curl https://mash-backend-api-production.up.railway.app/api/v1/devices/MASH-A1-CAL25-D5A91F
```

### View Logs
```bash
# Real-time logs
tail -f logs/mash_device.log

# Filter for backend/Firebase logs
tail -f logs/mash_device.log | grep -E "Backend|Firebase"
```

## Security Best Practices

### 1. Protect Credentials
```bash
# Set proper file permissions
chmod 600 .env
chmod 600 config/device_config.yaml
```

### 2. Never Commit Secrets
```bash
# Ensure .env is in .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

### 3. Rotate Keys Regularly
- Change Firebase service account keys every 90 days
- Update backend API keys periodically
- Use different keys for production and development

## Next Steps

1. **Start the IoT Device**
   ```bash
   python3 integrated_server.py
   ```

2. **Verify Backend Connection**
   - Check device appears in backend dashboard
   - Verify sensor data is being received

3. **Verify Firebase Connection**
   - Check Firebase console for device data
   - Verify real-time updates are working

4. **Test Mobile App**
   - Connect mobile app to device
   - Verify sensor readings display correctly
   - Test actuator controls

## Support

If you encounter issues:
1. Check the logs: `logs/mash_device.log`
2. Verify configuration: `config/device_config.yaml`
3. Test connectivity: Backend health endpoint
4. Check Firebase console for errors

---

**Last Updated**: November 11, 2024
**Status**: Ready for Production
