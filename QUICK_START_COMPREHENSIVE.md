# PyQt6 UI & Device Creation - Quick Start Guide

## 🚀 Running PyQt6 UI

### Option 1: Quick Launch (Windows)

```powershell
cd pyqt6_ui
.\run.ps1
```

This will:
- Create virtual environment if needed
- Install dependencies
- Launch the UI in demo mode

### Option 2: Manual Launch (Windows)

```powershell
cd pyqt6_ui

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Set demo mode (optional)
$env:MOCK_MODE="true"

# Run application
python main.py
```

### Option 3: Raspberry Pi

```bash
cd pyqt6_ui

# Install system dependencies (one-time)
sudo apt-get install python3-pyqt6 python3-pyqt6.qtcharts

# Create virtual environment (one-time)
python3 -m venv venv

# Activate environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run application
export MOCK_MODE=true
python main.py
```

### Production Mode (With Backend)

```bash
# Start Flask backend first
cd ~/MASH-IoT-Device
python integrated_server.py

# In another terminal, start UI
cd pyqt6_ui
export MOCK_MODE=false
python main.py
```

## 🔐 JWT Authentication Setup

### 1. Configure Environment Variables

Create or edit `.env` file in project root:

```bash
# Backend API Configuration
BACKEND_API_URL=https://mash-backend-production.up.railway.app/api
BACKEND_API_KEY=your_api_key_here

# ============================================================================
# JWT - JSON Web Token Authentication
# ============================================================================
# CRITICAL: Change JWT_SECRET in production! Generate: openssl rand -hex 32

JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRATION=1d                       # Default token expiry: 1 day

# Session Configuration
SESSION_DURATION=7d                     # JWT access token expiry: 7 days
REFRESH_TOKEN_DURATION=30d              # Refresh token expiry: 30 days
MAX_SESSIONS_PER_USER=5                 # Max concurrent sessions per user
```

### 2. Generate Secure JWT Secret

**Windows (PowerShell):**
```powershell
# Generate random 64-character hex string
-join ((48..57) + (97..102) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

**Linux/macOS:**
```bash
openssl rand -hex 32
```

Copy the output and replace `JWT_SECRET` value in `.env`

### 3. Install Python Dependencies

```bash
# Ensure python-dotenv is installed
pip install python-dotenv PyYAML
```

## 🌐 Running Device Creation Server

### Start Server

```powershell
# Navigate to API directory
cd src/api

# Ensure environment is configured
# Copy .env.example to .env and update values

# Run server
python device_creation_server.py
```

Server will start on `http://localhost:5001`

### Access Web Interface

Open browser: `http://localhost:5001`

### Environment Variables for Device Creation

Create `.env` in project root with:

```bash
# Backend Configuration
BACKEND_URL=https://mash-backend-production.up.railway.app

# JWT Authentication (required for backend API)
JWT_SECRET=your-super-secret-jwt-key
BACKEND_API_KEY=your_api_key

# Optional: Override defaults
DEVICE_CREATION_PORT=5001
LOG_LEVEL=INFO
```

## 🧪 Testing

### Test PyQt6 UI (Demo Mode)

```powershell
cd pyqt6_ui
$env:MOCK_MODE="true"
python main.py
```

You should see:
- Main window with navigation sidebar
- Dashboard with sensor cards and charts
- All 5 screens functional
- No backend required

### Test Device Creation Server

```bash
# Generate Device ID
curl -X POST http://localhost:5001/api/v1/device-id/generate \
  -H "Content-Type: application/json" \
  -d '{"brand":"MASH","model":"A","version":1,"location":"CAL","year":25}'

# List Devices
curl http://localhost:5001/api/v1/devices

# Create Device
curl -X POST http://localhost:5001/api/v1/devices \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "id": "MASH-A1-CAL25-ABC123",
    "name": "Test Chamber",
    "type": "MUSHROOM_CHAMBER",
    "serialNumber": "SN123456"
  }'
```

## 📋 Project Structure

```
MASH-IoT-Device/
├── pyqt6_ui/              # PyQt6 touchscreen UI
│   ├── main.py            # Entry point
│   ├── main_window.py     # Main window
│   ├── config.py          # Configuration
│   ├── screens/           # UI screens
│   ├── run.ps1            # Launcher
│   └── requirements.txt   # Dependencies
│
├── src/
│   └── api/
│       └── device_creation_server.py  # Device creation API
│
├── .env                   # Environment variables (create this)
├── env.example            # Environment template
└── requirements.txt       # Main dependencies
```

## 🔧 Troubleshooting

### PyQt6 UI Issues

**"ModuleNotFoundError: No module named 'PyQt6'"**
```bash
pip install PyQt6 PyQt6-Charts
```

**"No module named 'yaml'"**
```bash
pip install PyYAML
```

**Charts not displaying**
```bash
pip install PyQt6-Charts
```

### Device Creation Server Issues

**"ModuleNotFoundError: No module named 'dotenv'"**
```bash
pip install python-dotenv
```

**"Port 5001 already in use"**
```bash
# Windows
netstat -ano | findstr :5001
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:5001 | xargs kill
```

**"Cannot connect to backend"**
- Check internet connection
- Verify BACKEND_URL in .env
- Check backend is accessible: `curl https://mash-backend-production.up.railway.app/api/health`

### JWT Authentication Issues

**"Invalid JWT token"**
- Ensure JWT_SECRET matches between client and server
- Check token expiration (JWT_EXPIRATION)
- Verify token is included in Authorization header: `Bearer <token>`

**"API Key required"**
- Add X-API-Key header to requests
- Or configure BACKEND_API_KEY in .env

## 📝 Configuration Files

### PyQt6 UI (.env in touchscreen_ui/)

```bash
MOCK_MODE=true
API_BASE_URL=http://127.0.0.1:5000/api
WEBSOCKET_URL=ws://127.0.0.1:5000
DEBUG=true
```

### Device Creation (.env in project root)

```bash
BACKEND_URL=https://mash-backend-production.up.railway.app
BACKEND_API_KEY=your_api_key
JWT_SECRET=your_jwt_secret
JWT_EXPIRATION=1d
SESSION_DURATION=7d
REFRESH_TOKEN_DURATION=30d
MAX_SESSIONS_PER_USER=5
```

## 🎯 Quick Commands Reference

```bash
# PyQt6 UI
cd pyqt6_ui && .\run.ps1

# Device Creation Server
cd src/api && python device_creation_server.py

# Generate JWT Secret
openssl rand -hex 32

# Install All Dependencies
pip install -r requirements.txt

# Test UI (Demo)
cd pyqt6_ui && python main.py

# Test Backend API
curl http://localhost:5001/api/v1/devices
```

## ✅ Success Checklist

- [ ] `.env` file created with JWT_SECRET
- [ ] PyQt6 installed and UI launches
- [ ] Device creation server starts on port 5001
- [ ] Web interface accessible at localhost:5001
- [ ] Can generate device IDs
- [ ] Can create devices in backend
- [ ] JWT authentication working

## 🚀 Production Deployment

### PyQt6 UI on Raspberry Pi

1. Copy files to RPi:
   ```bash
   scp -r pyqt6_ui/ pi@raspberrypi:~/MASH-IoT-Device/
   ```

2. Install dependencies:
   ```bash
   ssh pi@raspberrypi
   cd ~/MASH-IoT-Device/pyqt6_ui
   sudo apt-get install python3-pyqt6 python3-pyqt6.qtcharts
   pip3 install -r requirements.txt
   ```

3. Configure auto-start:
   ```bash
   sudo cp config/mash-ui.service /etc/systemd/system/
   sudo systemctl enable mash-ui.service
   sudo systemctl start mash-ui.service
   ```

### Device Creation Server (Production)

1. Set production environment:
   ```bash
   export JWT_SECRET=$(openssl rand -hex 32)
   export BACKEND_URL=https://your-production-backend.com
   ```

2. Use production WSGI server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5001 device_creation_server:app
   ```

## 📚 Documentation

- [PyQt6 README](pyqt6_ui/README.md) - Complete UI documentation
- [Implementation Summary](pyqt6_ui/IMPLEMENTATION_SUMMARY.md) - Technical details
- [Device Creation Guide](DEVICE_CREATION_APP.md) - Full device creation docs
- [Backend Integration](documents/BACKEND-INTEGRATION.md) - API documentation

---

**Need Help?**
- Check logs: `tail -f logs/*.log`
- Enable debug: `LOG_LEVEL=DEBUG`
- Verify environment: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('JWT_SECRET'))"`
