# Quick Start: Device Creation App

## Start the Server

```bash
# Navigate to project directory
cd /path/to/MASH-IoT-Device

# Start the device creation server
python3 src/api/device_creation_server.py
```

Server will start on `http://localhost:5001`

## Open Web Interface

Open your browser and go to:
```
http://localhost:5001/
```

## Create Your First Device

1. **Fill the form** with device details:
   - Brand: `MASH` (default)
   - Model: Select `Alpha Prototype Build [A]`
   - Version: `1`
   - Location: `CAL` (or your location code)
   - Year: `25` (current year)
   - Device Name: `Mushroom Chamber #1`
   - Device Location: `Lab Room A`

2. **Click** "🎲 GENERATE DEVICE ID"
   - A unique ID will be generated: `MASH-A1-CAL25-XXXXXX`
   - The last 6 characters are hexadecimal with Luhn checksum

3. **Click** "✅ REGISTER DEVICE"
   - Device will be registered in the backend
   - Appears in the "Device Management" panel

## View Devices

Use the tabs to filter devices:
- **All Devices**: Shows all registered devices
- **Active**: Shows only active devices
- **Inactive**: Shows only inactive/deleted devices

## Test via API

### Generate Device ID
```bash
curl -X POST http://localhost:5001/api/v1/device-id/generate \
  -H "Content-Type: application/json" \
  -d '{"brand":"MASH","model":"A","version":1,"location":"CAL","year":25}'
```

### List Devices
```bash
curl http://localhost:5001/api/v1/devices
```

## Configuration

Set backend URL (optional):
```bash
export BACKEND_URL=https://mash-backend-production.up.railway.app
```

## Troubleshooting

**Port already in use?**
```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill
```

**Backend not accessible?**
- Check your internet connection
- Verify backend URL is correct
- Check firewall settings

For more details, see [DEVICE_CREATION_APP.md](./DEVICE_CREATION_APP.md)
