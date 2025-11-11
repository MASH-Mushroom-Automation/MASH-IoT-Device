# MASH IoT - Data Logging System

## Overview
Comprehensive SQLite-based logging system that records all device activity including sensor readings, actuator states, AI decisions, and alerts.

---

## Database Schema

### **Tables:**

1. **sensor_readings**
   - Logs all sensor data (CO2, temperature, humidity)
   - Includes mode and timestamp
   - Indexed for fast queries

2. **actuator_states**
   - Logs every actuator state change
   - Tracks who triggered it (manual/AI)
   - Includes mode context

3. **ai_decisions**
   - Logs all AI automation decisions
   - Includes sensor data at decision time
   - Stores actions taken and reasoning

4. **alerts**
   - Logs all system alerts
   - Includes severity and threshold info
   - Tracks sensor values that triggered alerts

---

## API Endpoints

### **Get Sensor Logs**
```http
GET /api/logs/sensors?hours=24&limit=1000
```

**Response:**
```json
{
  "success": true,
  "data": {
    "readings": [
      {
        "id": 1,
        "timestamp": "2025-11-06T08:00:00",
        "co2": 586,
        "temperature": 28.7,
        "humidity": 88,
        "mode": "s"
      }
    ],
    "count": 1000
  }
}
```

### **Get Actuator History**
```http
GET /api/logs/actuators?hours=24&limit=500
```

**Response:**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "id": 1,
        "timestamp": "2025-11-06T08:00:00",
        "exhaust_fan": 0,
        "blower_fan": 1,
        "humidifier": 0,
        "led_lights": 0,
        "mode": "s",
        "triggered_by": "ai"
      }
    ],
    "count": 50
  }
}
```

### **Get AI Decision Logs**
```http
GET /api/logs/ai-decisions?hours=24&limit=100
```

**Response:**
```json
{
  "success": true,
  "data": {
    "decisions": [
      {
        "id": 1,
        "timestamp": "2025-11-06T08:00:00",
        "mode": "Spawning",
        "sensor_co2": 586,
        "sensor_temp": 28.7,
        "sensor_humidity": 88,
        "actions": {
          "blower_fan": true
        },
        "reasoning": [
          "Temperature high (28.7°C > 27°C) - cooling"
        ]
      }
    ],
    "count": 10
  }
}
```

### **Get Alert Logs**
```http
GET /api/logs/alerts?hours=24&limit=100
```

### **Get Statistics**
```http
GET /api/logs/statistics?hours=24
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sensor_readings": {
      "count": 8640,
      "co2": {"avg": 5000, "min": 400, "max": 12000},
      "temperature": {"avg": 24.5, "min": 21, "max": 28},
      "humidity": {"avg": 88, "min": 80, "max": 95}
    },
    "ai_decisions_count": 144,
    "alerts_by_severity": {
      "warning": 5,
      "critical": 1
    },
    "actuator_usage": {
      "exhaust_fan": 50,
      "blower_fan": 30,
      "humidifier": 80,
      "led_lights": 0
    }
  }
}
```

---

## What Gets Logged

### **Sensor Readings** (Every reading)
- CO2 level (ppm)
- Temperature (°C)
- Humidity (%)
- Current mode
- Timestamp

### **Actuator Changes** (Every state change)
- All 4 actuator states
- Who triggered it (manual/AI)
- Current mode
- Timestamp

### **AI Decisions** (Every 10 seconds when enabled)
- Sensor data at decision time
- Actions taken
- Reasoning for each action
- Mode
- Timestamp

### **Alerts** (When triggered)
- Alert type
- Severity level
- Message
- Sensor value
- Threshold value
- Timestamp

---

## Data Retention

**Default:** 30 days

**Cleanup:**
- Automatic cleanup can be scheduled
- Manual cleanup via `data_logger.cleanup_old_data(days=30)`
- Keeps database size manageable

---

## Database Location

**Path:** `/home/pi/mash_iot/data/device_logs.db`

**Size:** ~1-5MB per day (depends on activity)

**Backup:** Recommended weekly backups

---

## Usage Examples

### **Python (IoT Device)**
```python
from data_logger import DataLogger

logger = DataLogger()

# Log sensor reading
logger.log_sensor_reading({
    'co2': 5000,
    'temperature': 24.5,
    'humidity': 88,
    'mode': 's'
})

# Log actuator change
logger.log_actuator_change({
    'exhaust_fan': False,
    'blower_fan': True,
    'humidifier': True,
    'led_lights': False
}, mode='s', triggered_by='ai')

# Get statistics
stats = logger.get_statistics(hours=24)
```

### **Mobile App (API)**
```dart
// Get sensor logs
final response = await dio.get('/api/logs/sensors?hours=24');
final readings = response.data['data']['readings'];

// Get statistics
final statsResponse = await dio.get('/api/logs/statistics?hours=24');
final stats = statsResponse.data['data'];
```

---

## Benefits

✅ **Complete History** - Every action logged  
✅ **AI Transparency** - See why AI made decisions  
✅ **Troubleshooting** - Debug issues with logs  
✅ **Analytics** - Understand chamber behavior  
✅ **Compliance** - Audit trail for research  
✅ **Performance** - Indexed for fast queries  
✅ **Lightweight** - SQLite, no external DB needed  

---

## Next Steps for Mobile App

1. Create Analytics/Logs screen
2. Display sensor trends (charts)
3. Show AI decision history
4. Display statistics dashboard
5. Export logs functionality

---

## Maintenance

### **Check Database Size**
```bash
ls -lh /home/pi/mash_iot/data/device_logs.db
```

### **Manual Cleanup**
```python
from data_logger import DataLogger
logger = DataLogger()
deleted = logger.cleanup_old_data(days=30)
print(f"Deleted {deleted} old records")
```

### **Backup Database**
```bash
cp /home/pi/mash_iot/data/device_logs.db ~/backups/device_logs_$(date +%Y%m%d).db
```

---

## Summary

The MASH IoT device now has comprehensive data logging with:
- ✅ SQLite database
- ✅ 4 main tables (sensors, actuators, AI decisions, alerts)
- ✅ 5 API endpoints for data retrieval
- ✅ Automatic logging integrated
- ✅ Statistics and analytics
- ✅ Data retention management

Ready to build the mobile app Analytics/Logs page! 📊
