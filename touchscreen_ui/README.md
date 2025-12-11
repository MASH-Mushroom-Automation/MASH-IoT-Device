# MASH Touchscreen UI

Local touchscreen interface for Raspberry Pi 3 with 7" display (800x480).

## Overview

This is a lightweight Kivy-based UI that runs directly on the IoT device, providing local control and monitoring capabilities. It complements the Flutter mobile app (primary interface for remote control).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Raspberry Pi 3 (IoT Device)                                │
│                                                             │
│  ┌────────────────┐            ┌────────────────┐          │
│  │  Touchscreen   │ Localhost  │  Flask API     │          │
│  │  UI (Kivy)     │◄──────────►│  (integrated_  │          │
│  │                │ 127.0.0.1  │   server.py)   │          │
│  │ - Dashboard    │            │                │          │
│  │ - Controls     │            │  - Sensors     │          │
│  │ - WiFi Setup   │            │  - Actuators   │          │
│  │ - Settings     │            │  - Automation  │          │
│  └────────────────┘            └────────────────┘          │
│         ▲                               │                   │
│         │                               │                   │
│    7" Touchscreen                Serial/GPIO                │
│    (800x480)                            │                   │
│                                         ▼                   │
│                              ┌────────────────┐             │
│                              │  Arduino +     │             │
│                              │  Sensors       │             │
│                              └────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

- **Responsive Design**: Supports both 3.5" (480x320) and 7" (800x480) screens with auto-detection
- **Offline Operation**: Works without internet connectivity
- **Real-time Monitoring**: Live sensor data display via HTTP and MQTT
- **Direct Control**: Toggle actuators (fans, humidifier, lights)
- **WiFi Configuration**: Set up network connection on first boot
- **Firebase Sync**: Cloud data synchronization (optional)
- **MQTT Messaging**: Real-time pub/sub communication (optional)
- **Lightweight**: ~300MB RAM usage, 60 FPS performance
- **Auto-start**: Boots directly into UI on device power-on

## Technology Stack

- **UI Framework**: Kivy 2.3.0 (responsive layouts)
- **Backend API**: Flask (integrated_server.py - existing)
- **Communication**: HTTP REST + WebSocket + MQTT
- **Cloud Sync**: Firebase Realtime Database (optional)
- **Messaging**: MQTT (Mosquitto broker)
- **Display**: 3.5" (480x320) or 7" (800x480) @ 60Hz touchscreen

## Directory Structure

```
touchscreen_ui/
├── main.py                 # Entry point - Kivy app
├── requirements.txt        # Python dependencies
├── config.py              # UI configuration
├── api_client.py          # Flask API client
├── screens/               # UI screens
│   ├── __init__.py
│   ├── dashboard.py       # Main dashboard
│   ├── controls.py        # Actuator controls
│   ├── wifi_setup.py      # WiFi configuration
│   └── settings.py        # System settings
├── widgets/               # Reusable UI components
│   ├── __init__.py
│   ├── sensor_card.py     # Sensor data display
│   ├── toggle_button.py   # Actuator toggle
│   └── status_bar.py      # Top status bar
├── assets/                # Images, fonts, icons
│   ├── fonts/
│   ├── icons/
│   └── images/
└── kv/                    # Kivy layout files
    ├── dashboard.kv
    ├── controls.kv
    ├── wifi_setup.kv
    └── settings.kv
```

## Relationship to Existing Code

This UI is a **supplement** to the existing system, not a replacement:

### Reuses Existing Backend
- Uses `integrated_server.py` Flask API (no modifications needed)
- Communicates via HTTP to `http://127.0.0.1:5000/api/*`
- Shares same data logger, automation controller, actuator controller

### Parallel to Mobile App
- Mobile app: Primary interface (90% usage - remote control)
- Touchscreen UI: Secondary interface (10% usage - local access)
- Both apps use the same Flask API endpoints

### Non-Invasive Installation
- Installed in separate `touchscreen_ui/` folder
- Does not modify existing Python files
- Can be disabled/removed without affecting CLI operation
- Existing system remains functional as backup

## Development Status

**Current Phase**: Foundation Complete (Responsive + Services)

- [x] Project structure created
- [x] Responsive design system (3.5" and 7" screens)
- [x] Main application skeleton
- [x] API client integration
- [x] MQTT client integration
- [x] Firebase configuration support
- [ ] Dashboard screen (in progress)
- [ ] Controls screen
- [ ] WiFi setup screen
- [ ] Settings screen
- [ ] WebSocket real-time updates
- [ ] Testing on RPi3 hardware

## Quick Start (Development)

```bash
# Navigate to touchscreen UI folder
cd /home/pi/MASH-IoT-Device/touchscreen_ui

# Install dependencies
pip3 install -r requirements.txt

# Run in development mode
python3 main.py
```

## Deployment

See `DEPLOYMENT_GUIDE.md` for complete instructions on:
- Installing Raspbian Desktop
- Configuring auto-boot
- Setting up touchscreen calibration
- System service configuration
- Network setup

## Related Documentation

- `../integrated_server.py` - Flask backend API
- `../documents/API_SPECIFICATION.md` - API endpoints reference
- `DEPLOYMENT_GUIDE.md` - RPi3 deployment instructions (from scratch)
- `RESPONSIVE_AND_SERVICES.md` - Responsive design & Firebase/MQTT setup
- `ROADMAP.md` - Development phases and timeline
- `../../Plans/Grower-IoT-Integration/` - Architecture decision docs

## Design Specifications

**Responsive Design** (adapts to screen size):

### 3.5" Screen (480x320)
- Resolution: 480x320 pixels
- Scale Factor: 0.6x
- Touch targets: Minimum 36x36 pixels
- Layout: 2-column grid
- Font sizes: 60% of base size

### 7" Screen (800x480)
- Resolution: 800x480 pixels
- Scale Factor: 1.0x (default)
- Touch targets: Minimum 60x60 pixels
- Layout: 3-column grid
- Font sizes: Base size

**Common Specs**:
- Color Scheme: Dark theme (easy on eyes in grow room)
- Font Family: Roboto (clear, readable)
- Frame rate: 60 FPS target
- Auto-detection: Based on actual screen resolution
