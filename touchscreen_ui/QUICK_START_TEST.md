# 🚀 Quick Start - Test Touchscreen UI NOW

**Goal**: Get the touchscreen UI running on your Windows desktop in 5 minutes.

---

## ⚡ Super Quick Commands

### Terminal 1: Backend Server (integrated_server.py)
```powershell
cd C:\Users\Ryzen\Desktop\ThesisDev\MASH-IoT-Device
python integrated_server.py
```

**Wait for**: `Running on http://127.0.0.1:5000`

---

### Terminal 2: Touchscreen UI
```powershell
cd C:\Users\Ryzen\Desktop\ThesisDev\MASH-IoT-Device\touchscreen_ui

# First time only - create virtual environment:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install kivy[base]==2.3.0
pip install -r requirements.txt

# Every time - run the app:
.\venv\Scripts\Activate.ps1
python main.py
```

---

## ✅ Expected Result

1. **800x480 window opens** (7" screen simulation)
2. **Welcome screen shows**:
   - "MASH Touchscreen UI" title
   - "✅ Backend Connected" status
   - Device and screen information
3. **Console logs show**:
   - Backend connection established
   - Periodic sensor/actuator updates every 5 seconds

---

## ⚠️ Current Limitations

The UI is **working but incomplete**:
- ✅ Main app structure
- ✅ Backend API connection
- ✅ Configuration system
- ⚠️ **Missing**: Dashboard screen (will show sensor readings)
- ⚠️ **Missing**: Controls screen (will toggle actuators)
- ⚠️ **Missing**: WiFi setup screen
- ⚠️ **Missing**: Settings screen

**The app shows a welcome/placeholder screen confirming everything works.**

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Python not found | Install Python 3.9+ from python.org |
| Execution policy error | Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Backend not connected | Make sure Terminal 1 is running integrated_server.py |
| Kivy not found | Reinstall: `pip install kivy[base]==2.3.0` |
| Import errors | Activate venv: `.\venv\Scripts\Activate.ps1` |

---

## 📝 What to Check

After running both terminals:

1. **Terminal 1 (integrated_server.py)** shows:
   ```
   Starting HTTP server on 0.0.0.0:5000
   * Running on http://127.0.0.1:5000
   ```

2. **Terminal 2 (main.py)** shows:
   ```
   MASH Touchscreen UI
   [INFO] Building MASH Touchscreen UI
   [INFO] ✅ Backend connection established
   ```

3. **UI Window** displays welcome screen with green checkmark

4. **Terminal 1 logs API requests** every 5 seconds:
   ```
   127.0.0.1 - - "GET /api/sensor/current HTTP/1.1" 200 -
   ```

---

## 🎯 Next Steps

Once this basic test works:

1. ✅ Confirm backend connection
2. ✅ No errors in console
3. ✅ Window displays correctly
4. 🚀 **Ready to implement full UI screens**

Tell me when you're ready and I'll implement:
- Dashboard with live sensor readings
- Controls for actuator toggles
- Full navigation system
- Complete UI widgets

---

## 📚 Full Documentation

- **`DESKTOP_TESTING_GUIDE.md`** - Complete testing guide
- **`DEPLOYMENT_GUIDE.md`** - Raspberry Pi deployment steps
- **`README.md`** - Project overview

---

Let's test! 🚀
