# Touchscreen UI Testing Checklist

Use this checklist to track your testing progress.

---

## 📋 Pre-Testing Setup

- [ ] Python 3.9+ installed on Windows
- [ ] Can run `python --version` in PowerShell
- [ ] Fresh Raspberry Pi OS updated on your RPi
- [ ] RPi accessible via Raspberry Pi Connect
- [ ] Two PowerShell terminals ready

---

## 🖥️ Desktop Testing (Windows)

### Backend Server Setup
- [ ] Navigated to `MASH-IoT-Device` folder
- [ ] Created virtual environment (`python -m venv venv`)
- [ ] Activated venv (`.\venv\Scripts\Activate.ps1`)
- [ ] Installed requirements (`pip install -r requirements.txt`)
- [ ] Started `integrated_server.py`
- [ ] Server running on `http://127.0.0.1:5000`
- [ ] No critical errors in console

### Touchscreen UI Setup
- [ ] Navigated to `MASH-IoT-Device\touchscreen_ui` folder
- [ ] Created separate virtual environment
- [ ] Activated touchscreen UI venv
- [ ] Installed Kivy (`pip install kivy[base]==2.3.0`)
- [ ] Installed other requirements (`pip install -r requirements.txt`)
- [ ] `.env` file exists and configured
- [ ] Started `main.py`
- [ ] UI window opened (800x480 size)

### Basic Functionality Test
- [ ] UI shows "MASH Touchscreen UI" title
- [ ] Status shows "✅ Backend Connected"
- [ ] Device info displayed correctly
- [ ] Screen size shows "7" Screen (800x480)"
- [ ] No Python errors in console
- [ ] Console shows periodic updates every 5 seconds
- [ ] Backend terminal shows API requests

### Connection Test
- [ ] Backend `/api/health` endpoint responding
- [ ] Sensor data endpoint working
- [ ] Actuator states endpoint working
- [ ] Status endpoint working
- [ ] No timeout errors
- [ ] No connection refused errors

### 5-Minute Stability Test
- [ ] Let app run for 5 minutes
- [ ] No crashes or freezes
- [ ] Periodic updates still working
- [ ] Memory usage stable (~300MB or less)
- [ ] CPU usage reasonable (<30%)

---

## 🎨 UI Implementation (After Basic Test)

### Phase 1: Core Widgets
- [ ] Implement `widgets/sensor_card.py`
- [ ] Implement `widgets/toggle_button.py`
- [ ] Implement `widgets/status_bar.py`
- [ ] Test each widget independently

### Phase 2: Dashboard Screen
- [ ] Implement `screens/dashboard.py`
- [ ] Create `kv/dashboard.kv` layout
- [ ] Add sensor cards for CO2, Temperature, Humidity
- [ ] Test live data updates
- [ ] Verify responsive design

### Phase 3: Controls Screen
- [ ] Implement `screens/controls.py`
- [ ] Create `kv/controls.kv` layout
- [ ] Add toggle buttons for actuators
- [ ] Test actuator control via API
- [ ] Verify state synchronization

### Phase 4: Navigation
- [ ] Add screen navigation
- [ ] Test smooth transitions
- [ ] Add back button functionality
- [ ] Test navigation flow

### Phase 5: Additional Screens
- [ ] Implement WiFi setup screen (optional for desktop)
- [ ] Implement settings screen
- [ ] Add error handling screens
- [ ] Test all screens

---

## 🚀 Raspberry Pi Deployment

### File Transfer
- [ ] Connect to RPi via Raspberry Pi Connect or SSH
- [ ] Transfer `touchscreen_ui/` folder to RPi
- [ ] Transfer updated `integrated_server.py` if needed
- [ ] Verify all files transferred correctly

### RPi Environment Setup
- [ ] Update system (`sudo apt update && sudo apt upgrade -y`)
- [ ] Install Python dependencies
- [ ] Install Kivy for Raspberry Pi
- [ ] Install touchscreen drivers (if needed)
- [ ] Test touchscreen responsiveness

### Backend Server on RPi
- [ ] `integrated_server.py` running on RPi
- [ ] Server accessible at `http://127.0.0.1:5000`
- [ ] Serial connection to Arduino working
- [ ] GPIO actuators responding
- [ ] Sensor data streaming

### Touchscreen UI on RPi
- [ ] UI starts without errors
- [ ] Display shows on 7" touchscreen
- [ ] Touch input works correctly
- [ ] Backend connection established (localhost)
- [ ] Sensor data displaying live
- [ ] Actuator controls working
- [ ] Performance acceptable (30+ FPS)

### Auto-Start Configuration
- [ ] Create systemd service for UI
- [ ] Enable service at boot
- [ ] Test auto-start on reboot
- [ ] Verify UI launches on power-up
- [ ] Test graceful shutdown

### Final Testing on RPi
- [ ] Full system integration test
- [ ] All sensors reading correctly
- [ ] All actuators responding
- [ ] UI responsive and smooth
- [ ] No memory leaks over 30 minutes
- [ ] Error handling working
- [ ] Log files generating properly

---

## ✅ Sign-Off

### Desktop Testing Complete
- [ ] All basic tests passed
- [ ] UI implementation satisfactory
- [ ] Ready for RPi deployment
- **Date**: __________
- **Notes**: _________________________________

### RPi Deployment Complete
- [ ] UI running on touchscreen
- [ ] Full integration working
- [ ] Auto-start configured
- [ ] System stable and production-ready
- **Date**: __________
- **Notes**: _________________________________

---

## 📝 Issues Log

| Issue | Date | Status | Solution |
|-------|------|--------|----------|
| | | | |
| | | | |
| | | | |

---

## 🎯 Current Status

**Last Updated**: December 16, 2025

**Current Phase**: Desktop Testing Setup

**Next Step**: Run basic UI test on Windows

**Blockers**: None

---

Print this checklist and mark items as you complete them! ✓
