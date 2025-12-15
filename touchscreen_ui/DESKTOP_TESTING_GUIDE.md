# MASH Touchscreen UI - Desktop Testing Guide

Complete guide to test the touchscreen UI on Windows before deploying to Raspberry Pi.

---

## 📋 Overview

This guide will help you:
1. ✅ Set up the development environment on Windows
2. ✅ Test the touchscreen UI on your desktop
3. ✅ Make necessary changes and improvements
4. ✅ Deploy the final version to Raspberry Pi

**Current Status**: The touchscreen UI has the basic framework but needs screen implementations to be fully functional.

---

## 🔍 Current Implementation Status

### ✅ Completed Components
- `main.py` - Main application structure
- `config.py` - Configuration system with responsive design support
- `api_client.py` - Flask backend API client
- `mqtt_client.py` - MQTT real-time messaging client
- `.env` - Environment configuration for testing

### ⚠️ Missing Components (Will be implemented)
- `screens/dashboard.py` - Main dashboard with sensor displays
- `screens/controls.py` - Actuator control screen
- `screens/wifi_setup.py` - WiFi configuration screen
- `screens/settings.py` - System settings screen
- `widgets/sensor_card.py` - Sensor data display widget
- `widgets/toggle_button.py` - Actuator toggle widget
- `widgets/status_bar.py` - Status bar widget
- `kv/*.kv` - Kivy layout files

**Note**: The current app will show a welcome screen that confirms backend connection and displays placeholder messages. We'll implement the full screens next.

---

## 🛠️ Part 1: Desktop Setup (Windows)

### Step 1: Install Python (if not already installed)

1. Download Python 3.9+ from https://www.python.org/downloads/
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```powershell
   python --version
   # Should show: Python 3.9.x or higher
   ```

### Step 2: Navigate to Project Directory

```powershell
cd C:\Users\Ryzen\Desktop\ThesisDev\MASH-IoT-Device\touchscreen_ui
```

### Step 3: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get an error about execution policy, run this first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Install Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install Kivy dependencies for Windows
pip install kivy[base]==2.3.0

# Install other dependencies
pip install -r requirements.txt
```

**Note**: Kivy installation on Windows might take a few minutes.

### Step 5: Verify Environment File

Check that `.env` file exists in `touchscreen_ui/` folder:

```env
DEVICE_ID=MASH-A1-CAL25-D5A91F
DEVICE_NAME=MASH Chamber Test
SCREEN_SIZE=7
API_BASE_URL=http://127.0.0.1:5000/api
DEBUG=true
```

---

## 🚀 Part 2: Start the Backend Server

The touchscreen UI needs the Flask backend (`integrated_server.py`) running to function properly.

### Option A: Test WITHOUT Raspberry Pi Hardware (Simulation Mode)

Open a **new PowerShell terminal** (keep the first one open):

```powershell
# Navigate to IoT Device root folder
cd C:\Users\Ryzen\Desktop\ThesisDev\MASH-IoT-Device

# Activate virtual environment (create one if needed)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run integrated_server.py in simulation mode
python integrated_server.py
```

**Expected Output**:
```
WARNING: RPi.GPIO not available, running in simulation mode
WARNING: Running in SIMULATION mode - no GPIO control
WARNING: Running without Arduino connection
Starting MASH IoT Device Server
Device ID: MASH-A1-CAL25-D5A91F
Starting HTTP server on 0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

### Option B: Test WITH Connected Raspberry Pi

If your Raspberry Pi is already running `integrated_server.py`, you can connect to it:

1. Find your Raspberry Pi's IP address from the screenshot: `connect.raspberrypi.com`
2. Update `.env` in `touchscreen_ui/`:
   ```env
   API_BASE_URL=http://<RPI_IP_ADDRESS>:5000/api
   ```

---

## 🖥️ Part 3: Run the Touchscreen UI

In the **first terminal** (with touchscreen_ui virtual environment active):

```powershell
# Make sure you're in the touchscreen_ui folder
cd C:\Users\Ryzen\Desktop\ThesisDev\MASH-IoT-Device\touchscreen_ui

# Activate venv if not already active
.\venv\Scripts\Activate.ps1

# Run the application
python main.py
```

### Expected Behavior:

1. **Window Opens**: A window sized 800x480 (7" screen size) should appear
2. **Welcome Screen**: Shows:
   - Title: "MASH Touchscreen UI"
   - Status: "Initializing..." then either:
     - ✅ "Backend Connected" (if integrated_server.py is running)
     - ⚠️ "Backend Not Connected" (if not running)
   - Device info and screen details
3. **Console Output**: Check for logs showing connection status

### Console Output Example:

```
============================================================
MASH Touchscreen UI
Version: 0.1.0 (Development - Responsive)
Device: MASH Chamber Test (MASH-A1-CAL25-D5A91F)
Screen: 7" Screen (800x480)
Backend: http://127.0.0.1:5000/api
MQTT: Disabled
Firebase: Disabled
============================================================
[INFO] Building MASH Touchscreen UI
[INFO] UI built successfully
[INFO] MASH Touchscreen UI started
[INFO] Checking backend connection...
[INFO] ✅ Backend connection established
```

---

## 🧪 Part 4: Testing Checklist

### Test 1: Backend Connection
- [ ] UI shows "✅ Backend Connected"
- [ ] No connection errors in console
- [ ] API_BASE_URL is correct in `.env`

### Test 2: Window Display
- [ ] Window size is 800x480 pixels
- [ ] Window is responsive (can see all content)
- [ ] Background color is dark theme

### Test 3: Basic Interaction
- [ ] Can click/interact with the window
- [ ] No crashes or errors
- [ ] Console shows periodic updates (every 5 seconds for sensors)

### Test 4: API Communication
Check the `integrated_server.py` terminal for incoming requests:
```
127.0.0.1 - - [16/Dec/2025 15:30:00] "GET /api/health HTTP/1.1" 200 -
127.0.0.1 - - [16/Dec/2025 15:30:05] "GET /api/sensor/current HTTP/1.1" 200 -
127.0.0.1 - - [16/Dec/2025 15:30:05] "GET /api/actuators HTTP/1.1" 200 -
127.0.0.1 - - [16/Dec/2025 15:30:05] "GET /api/status HTTP/1.1" 200 -
```

---

## 🐛 Troubleshooting

### Issue: "Kivy not found" or import errors

**Solution**:
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall Kivy
pip uninstall kivy
pip install kivy[base]==2.3.0
```

### Issue: "Backend Not Connected"

**Solution**:
1. Check if `integrated_server.py` is running in another terminal
2. Verify the Flask server shows: `Running on http://127.0.0.1:5000`
3. Check `.env` has correct `API_BASE_URL=http://127.0.0.1:5000/api`
4. Test API manually:
   ```powershell
   curl http://127.0.0.1:5000/api/health
   ```

### Issue: Window too big/small

**Solution**: Adjust SCREEN_SIZE in `.env`:
```env
# For smaller test window
SCREEN_SIZE=3.5

# For 7" screen (800x480)
SCREEN_SIZE=7
```

### Issue: "Execution Policy" error when activating venv

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📝 Part 5: Next Steps - Implementing Full UI

Once basic testing is successful, we'll implement:

### Phase 1: Core Widgets
1. `widgets/sensor_card.py` - Display sensor readings with icons
2. `widgets/toggle_button.py` - Control actuators
3. `widgets/status_bar.py` - Top bar with connection status

### Phase 2: Main Screens
1. `screens/dashboard.py` - Real-time sensor monitoring
2. `screens/controls.py` - Manual actuator control
3. `kv/dashboard.kv` - Dashboard layout
4. `kv/controls.kv` - Controls layout

### Phase 3: Additional Features
1. `screens/wifi_setup.py` - WiFi configuration UI
2. `screens/settings.py` - System settings
3. Navigation between screens
4. Error handling and alerts

### Phase 4: Testing & Polish
1. Test all screens with real data
2. Optimize performance (60 FPS target)
3. Test touch interactions
4. Final UI polish

---

## 🚀 Part 6: Deployment to Raspberry Pi

After desktop testing is complete, we'll:

1. **Transfer Files**: Copy `touchscreen_ui/` to Raspberry Pi
2. **Install Dependencies**: Run setup on RPi
3. **Configure Auto-start**: Set up systemd service
4. **Test on Touchscreen**: Verify on actual 7" display
5. **Fine-tune**: Adjust for touch input and performance

See `DEPLOYMENT_GUIDE.md` for detailed RPi deployment steps.

---

## 📊 Performance Targets

- **RAM Usage**: < 300MB
- **CPU Usage**: < 15% (idle), < 30% (active)
- **Frame Rate**: 60 FPS
- **API Response**: < 100ms
- **Boot Time**: < 10 seconds to UI

---

## 🎯 Testing Summary

**Before proceeding to Raspberry Pi, ensure**:
- ✅ UI launches without errors on Windows
- ✅ Backend connection is established
- ✅ No crashes during 5-minute run test
- ✅ Console shows periodic API calls
- ✅ You're satisfied with the basic structure

**Once desktop testing is complete**, we can confidently deploy to the Raspberry Pi knowing the core functionality works.

---

## 💡 Tips for Development

1. **Keep integrated_server.py running** - The UI depends on it
2. **Check both terminals** - UI terminal for app logs, server terminal for API logs
3. **Use DEBUG=true** - Enables helpful debugging features
4. **Test incrementally** - Test each new screen/widget before adding more
5. **Hot reload** - Restart the app to see changes (Kivy doesn't auto-reload)

---

## 📞 Ready to Start?

Run these commands to begin testing:

```powershell
# Terminal 1: Start backend server
cd C:\Users\Ryzen\Desktop\ThesisDev\MASH-IoT-Device
python integrated_server.py

# Terminal 2: Start touchscreen UI
cd C:\Users\Ryzen\Desktop\ThesisDev\MASH-IoT-Device\touchscreen_ui
.\venv\Scripts\Activate.ps1
python main.py
```

Let me know when you're ready to implement the full UI screens! 🚀
