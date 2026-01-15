# MASH Device Creation Web Application

A standalone web application for generating unique device IDs and managing IoT devices for the MASH Mushroom Automation project.

## Overview

This application provides a simple web interface for:
- Generating unique device IDs using the Luhn Modulo N algorithm
- Viewing and managing registered devices
- Filtering devices by status (Active/Inactive)
- Integrating with the MASH Backend API

## Features

### 1. Device ID Generation
- **Unique ID Format**: `MASH-A1-CAL25-D5A91F`
  - Brand: MASH
  - Model: A (Alpha), B (Beta), or R (Release)
  - Version: Numeric version (e.g., 1)
  - Location: 3-letter location code (e.g., CAL)
  - Year: 2-digit year (e.g., 25)
  - HEX Code: 6-character hexadecimal with Luhn checksum

### 2. Luhn Modulo N Algorithm
The application uses the Luhn Modulo N algorithm to generate a checksum for the hexadecimal portion of the device ID, ensuring:
- Uniqueness of each generated ID
- Validation capability for device IDs
- Error detection in case of manual entry mistakes

### 3. Model Types
- **Alpha Prototype Build [A]**: Early prototype devices
- **Beta Prototype Build [B]**: Testing phase devices
- **Release Build [R]**: Production-ready devices

### 4. Device Management
- List all registered devices
- Filter devices by status (All, Active, Inactive)
- View device details
- Soft delete devices
- Real-time updates

## Architecture

### Components

1. **Device ID Generator** (`src/utils/device_id_generator.py`)
   - Implements Luhn Modulo N algorithm
   - Generates unique hexadecimal codes with checksum
   - Validates device IDs
   - Parses device ID components

2. **Flask Web Server** (`src/api/device_creation_server.py`)
   - Serves the web interface
   - Proxies API requests to MASH Backend
   - Handles device ID generation
   - Manages device CRUD operations

3. **Web Interface** (`templates/device_creation.html`)
   - Responsive single-page application
   - Form-based device creation
   - Tabbed device management interface
   - Real-time updates

### Backend Integration

The application communicates with the MASH Backend API at:
```
https://mash-backend-production.up.railway.app/api/v1
```

All device operations (create, read, update, delete) are proxied to the backend, which stores data in a Neon PostgreSQL database.

## Installation

### Prerequisites
- Python 3.9+
- pip

### Install Dependencies
```bash
pip install flask flask-cors requests python-dotenv
```

### Environment Variables
Create a `.env` file or set environment variables:
```bash
# Backend API URL (optional, defaults to production URL)
BACKEND_URL=https://mash-backend-production.up.railway.app
```

## Usage

### Starting the Server
```bash
cd /path/to/MASH-IoT-Device
python3 src/api/device_creation_server.py
```

The server will start on `http://localhost:5001`

### Accessing the Web Interface
Open your browser and navigate to:
```
http://localhost:5001/
```

### Creating a Device

1. **Fill in Device Details**:
   - Brand: Default is "MASH" (can be customized)
   - Model Type: Select from Alpha [A], Beta [B], or Release [R]
   - Version: Enter version number (default: 1)
   - Location Code: Enter 3-letter location code (e.g., CAL, NYC, LAB)
   - Year: Enter 2-digit year (e.g., 25 for 2025)
   - Device Name: Enter a descriptive name (e.g., "Mushroom Chamber #1")
   - Device Location: Enter physical location (e.g., "Lab Room A")

2. **Generate Device ID**:
   - Click "🎲 GENERATE DEVICE ID" button
   - A unique ID will be generated with Luhn checksum
   - View the generated ID and its components

3. **Register Device**:
   - Click "✅ REGISTER DEVICE" button
   - Device will be registered in the backend database
   - Device appears in the "Device Management" panel

### Managing Devices

- **All Devices**: View all registered devices
- **Active**: View only active devices
- **Inactive**: View only inactive/deleted devices

Each device card shows:
- Device ID
- Device name
- Type and location
- Status (Online/Offline)
- Action buttons (View Details, Delete)

## API Endpoints

### Device ID Generation
```
POST /api/v1/device-id/generate
Content-Type: application/json

{
  "brand": "MASH",
  "model": "A",
  "version": 1,
  "location": "CAL",
  "year": 25
}

Response:
{
  "success": true,
  "device_id": "MASH-A1-CAL25-D5A91F",
  "components": {
    "brand": "MASH",
    "model": "A",
    "model_name": "Alpha Prototype Build",
    "version": "1",
    "location": "CAL",
    "year": "25",
    "hex_code": "D5A91F"
  },
  "timestamp": "2026-01-15T03:49:39.483310"
}
```

### Device ID Validation
```
POST /api/v1/device-id/validate
Content-Type: application/json

{
  "device_id": "MASH-A1-CAL25-D5A91F"
}

Response:
{
  "success": true,
  "valid": true,
  "parsed": {
    "device_id": "MASH-A1-CAL25-D5A91F",
    "brand": "MASH",
    "model": "A",
    "model_name": "Alpha Prototype Build",
    "version": "1",
    "location": "CAL",
    "year": "25",
    "hex_code": "D5A91F",
    "valid_checksum": true
  }
}
```

### List Devices
```
GET /api/v1/devices?page=1&perPage=30

Response:
{
  "success": true,
  "data": {
    "devices": [...],
    "pagination": {
      "page": 1,
      "perPage": 30,
      "total": 5,
      "totalPages": 1
    }
  }
}
```

### Create Device
```
POST /api/v1/devices
Content-Type: application/json

{
  "id": "MASH-A1-CAL25-D5A91F",
  "serialNumber": "MASH-A1-CAL25-D5A91F",
  "name": "Mushroom Chamber #1",
  "type": "MUSHROOM_CHAMBER",
  "location": "Lab Room A",
  "description": "Alpha Prototype Build - Version 1",
  "isActive": true
}
```

### Get Device Details
```
GET /api/v1/devices/{device_id}
```

### Update Device
```
PUT /api/v1/devices/{device_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "location": "New Location"
}
```

### Delete Device (Soft Delete)
```
DELETE /api/v1/devices/{device_id}
```

### Activate/Deactivate Device
```
POST /api/v1/devices/{device_id}/activate
Content-Type: application/json

{
  "isActive": true
}
```

## Database Schema

The backend uses Neon PostgreSQL with the following schema:

```sql
CREATE TABLE device (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    serialNumber TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OFFLINE',
    userId TEXT,
    location TEXT,
    description TEXT,
    firmware TEXT,
    ipAddress TEXT,
    macAddress TEXT,
    lastSeen TIMESTAMP,
    isActive BOOLEAN NOT NULL DEFAULT true,
    createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP NOT NULL
);
```

## Luhn Modulo N Algorithm Details

The Luhn Modulo N algorithm is used to generate and validate the hexadecimal checksum:

1. **Character Set**: 0-9, A-F (hexadecimal)
2. **Algorithm**:
   - Generate 5 random hexadecimal characters
   - Calculate Luhn checksum digit
   - Append checksum to create 6-character code
3. **Validation**:
   - Parse the 6-character code
   - Recalculate checksum for first 5 characters
   - Compare with the 6th character (checksum digit)

### Example
```python
from src.utils.device_id_generator import DeviceIDGenerator

# Generate a device ID
device_id, components = DeviceIDGenerator.generate_device_id(
    brand="MASH",
    model="A",
    version=1,
    location="CAL",
    year=25
)
print(device_id)  # Output: MASH-A1-CAL25-D5A91F

# Validate a device ID
is_valid = DeviceIDGenerator.validate_device_id("MASH-A1-CAL25-D5A91F")
print(is_valid)  # Output: True

# Parse a device ID
parsed = DeviceIDGenerator.parse_device_id("MASH-A1-CAL25-D5A91F")
print(parsed)
# Output:
# {
#   'device_id': 'MASH-A1-CAL25-D5A91F',
#   'brand': 'MASH',
#   'model': 'A',
#   'model_name': 'Alpha Prototype Build',
#   'version': '1',
#   'location': 'CAL',
#   'year': '25',
#   'hex_code': 'D5A91F',
#   'valid_checksum': True
# }
```

## Screenshots

### Initial View
![Device Creation Page - Initial](https://github.com/user-attachments/assets/b313a041-4d35-4536-bdb7-6e1c5c77d795)

### After ID Generation
![Device Creation Page - ID Generated](https://github.com/user-attachments/assets/a93d5cc9-dd0c-4e28-a1e6-857a52187607)

## Development

### Project Structure
```
MASH-IoT-Device/
├── src/
│   ├── api/
│   │   └── device_creation_server.py  # Flask server
│   └── utils/
│       └── device_id_generator.py      # ID generation logic
├── templates/
│   └── device_creation.html            # Web interface
└── DEVICE_CREATION_APP.md              # This file
```

### Testing

#### Test Device ID Generation
```bash
curl -X POST http://localhost:5001/api/v1/device-id/generate \
  -H "Content-Type: application/json" \
  -d '{"brand":"MASH","model":"A","version":1,"location":"CAL","year":25}'
```

#### Test Device Creation
```bash
curl -X POST http://localhost:5001/api/v1/devices \
  -H "Content-Type: application/json" \
  -d '{
    "id": "MASH-A1-CAL25-TEST01",
    "serialNumber": "MASH-A1-CAL25-TEST01",
    "name": "Test Chamber",
    "type": "MUSHROOM_CHAMBER",
    "location": "Lab",
    "description": "Test device",
    "isActive": true
  }'
```

#### Test Device Listing
```bash
curl http://localhost:5001/api/v1/devices
```

## Deployment

### Production Deployment

1. **Configure Backend URL**:
   ```bash
   export BACKEND_URL=https://mash-backend-production.up.railway.app
   ```

2. **Use Production WSGI Server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5001 src.api.device_creation_server:app
   ```

3. **Add to Requirements**:
   ```txt
   flask>=2.0.0
   flask-cors>=3.0.10
   requests>=2.28.0
   python-dotenv>=0.19.0
   gunicorn>=20.1.0
   ```

## Security Considerations

1. **API Authentication**: In production, add authentication to the backend API
2. **Input Validation**: All inputs are validated before processing
3. **SQL Injection Prevention**: Backend uses parameterized queries
4. **CORS**: Configured to allow frontend-backend communication
5. **HTTPS**: Use HTTPS in production for secure communication

## Future Enhancements

- [ ] Add user authentication and authorization
- [ ] Implement bulk device registration
- [ ] Add device search and filtering capabilities
- [ ] Export device list to CSV/Excel
- [ ] QR code generation for device IDs
- [ ] Device firmware update interface
- [ ] Real-time device status monitoring via WebSockets
- [ ] Device configuration management UI

## Troubleshooting

### Server Won't Start
- Check if port 5001 is already in use: `lsof -i:5001`
- Try a different port: Edit `device_creation_server.py` and change the port number

### Cannot Connect to Backend
- Verify backend URL is correct
- Check network connectivity
- Ensure backend server is running
- Check firewall rules

### Device Not Appearing in List
- Check browser console for errors
- Verify backend API is responding
- Check device was successfully created (inspect network tab)
- Try refreshing the page

## License

This project is part of the M.A.S.H. (Mushroom Automation with Smart Hydro-environment) IoT Device system.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the main project README.md
- Create an issue in the repository
