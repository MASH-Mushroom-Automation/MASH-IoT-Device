# MASH Grow: App-Device Connection Brainstorm

This document outlines the connection, data, and control flow between the MASH Grower Mobile App (Flutter) and the MASH Chamber IoT Device (Raspberry Pi).

## Key Components (Actors)

- **User**: The grower interacting with the mobile app.
- **MASH Grower App (Mobile)**: The Flutter application. Manages user account, device pairing, and data visualization.
- **MASH Chamber (RPi)**: The IoT device. Runs Python (main.py), collects sensor data, stores it locally (SQLite), and syncs to the backend.
- **MASH Backend (Cloud)**: The central server. Manages user authentication, stores all synced device data, and relays commands.
- **User's Home Wi-Fi**: The local network router.

## Phase 1: First-Time Setup & Provisioning (User Flow)

This is the "out-of-the-box" experience for a new user.

**Goal**: Securely get the MASH Chamber (RPi) onto the user's home Wi-Fi network and pair it with their MASH account.

| Step | User Action (in App) | App (Mobile) Flow | RPi (Device) Flow |
|------|---------------------|-------------------|-------------------|
| 1 | Powers on the MASH Chamber. | - | **Device Boots Up (main.py)**:<br/>1. Checks if NetworkManager has a valid, active connection (e.g., `nmcli connection show --active`).<br/>2. No config found: Enters "Provisioning Mode".<br/>3. Takes control of wlan0: Disables NetworkManager on wlan0 and starts a Soft Access Point (SoftAP) (e.g., using hostapd) with SSID `MASH-Chamber-a1b2`.<br/>4. Starts a local web server (e.g., Flask/FastAPI) on a static IP (e.g., 192.168.4.1). |
| 2 | Opens App > "Add New Device". | Shows DeviceConnectionScreen.<br/>Prompts user to look for the device's Wi-Fi network. | Broadcasting `MASH-Chamber-a1b2` Wi-Fi network. |
| 3 | Goes to phone's Wi-Fi settings and connects to `MASH-Chamber-a1b2`. | - | - |
| 4 | Returns to the MASH app. | App detects it's connected to the SoftAP.<br/>Navigates to WifiDeviceConnectionScreen. | Serves the local web server. |
| 5 | Sees a list of nearby Wi-Fi networks (scanned by the app). Selects "MyHomeWiFi" and enters the password. | 1. App scans for local Wi-Fi networks.<br/>2. User selects their home network (SSID) and inputs the password. | - |
| 6 | Taps "Connect". | 1. App HTTP POSTs the credentials (`{"ssid": "MyHomeWiFi", "psk": "password123"}`) to the RPi's local server (e.g., `http://192.168.4.1/api/v1/config_wifi`).<br/>2. Shows a "Connecting..." loading screen.<br/>3. App disconnects from SoftAP and reconnects to "MyHomeWiFi". | 1. Receives credentials at its `/api/v1/config_wifi` endpoint.<br/>2. Uses nmcli (via Python subprocess) to connect. (e.g., `nmcli dev wifi connect "MyHomeWiFi" password "password123"`). This is much more reliable than editing wpa_supplicant.conf.<br/>3. Shuts down the SoftAP.<br/>4. Re-enables NetworkManager to manage wlan0. |
| 7 | Waits... | App polls the MASH Backend: `GET /api/v1/devices/pair_status?device_id=UNIQUE_ID` (Unique ID could be sent from RPi in Step 6, or app could listen for mDNS). | 1. Connects to "MyHomeWiFi" via NetworkManager.<br/>2. Gets a new local IP (e.g., 192.168.1.100).<br/>3. "Phones Home": Registers with the MASH Backend, sending its unique ID (MAC address) and local IP. `POST /api/v1/devices/register` |
| 8 | Sees "Success! Device Connected." | Backend returns `{"status": "paired"}`.<br/>App navigates to the device dashboard. | Enters "Normal Operation" mode. Starts SensorManager and SyncManager. |

## Phase 2: Normal Operation (Development Flow)

Device is online and paired.

### A. Data Flow: RPi (Device) to Cloud & App

1. **Sensor Reading (RPi)**: SensorManager runs in a loop, collecting data (CO2, temp, humidity) from scd41_sensor.

2. **Local Storage (RPi)**: DatabaseManager writes every new reading to the local SQLite database. This is critical for offline capability.

3. **Cloud Sync (RPi)**: SyncManager (in a separate thread) checks the local DB for unsynced readings.

4. **Data Upload (RPi)**: SyncManager batches unsynced readings and POSTs them to the MASH Backend (e.g., `POST /api/v1/sensor-readings`).

5. **App Data Fetch (Remote)**: When the user is on 4G/5G, the App fetches all historical and "live" data from the MASH Backend.

6. **App Data Fetch (Local)**:
   - **Discovery**: When the App is on the same Wi-Fi as the RPi, it can discover the RPi's local IP (e.g., 192.168.1.100) via mDNS/Bonjour or by asking the backend.
   - **Direct Connection**: The App can then make requests directly to the RPi's local API (e.g., `GET http://192.168.1.100/api/v1/sensors/latest`). This provides true real-time data and is very low latency.

### B. Control Flow: App to RPi (Device)

#### Scenario 1: App is Remote (4G/5G)

1. **User Action**: User toggles a "Light ON" switch in the App.

2. **App to Cloud**: App sends command to MASH Backend: `POST /api/v1/devices/{device_id}/command` with payload `{"actuator": "light", "value": "on"}`.

3. **Cloud to RPi**: The MASH Backend needs to send this command to the RPi.
   - **Preferred Method (Real-time)**: The RPi maintains a persistent WebSocket (or MQTT) connection to the Backend. The Backend pushes the command `{...}` down this connection instantly.
   - **Fallback Method (Polling)**: The RPi periodically polls the Backend for new commands: `GET /api/v1/devices/{device_id}/commands/queue`.

4. **RPi Action**: The RPi receives the command and triggers the corresponding hardware (e.g., toggles a GPIO pin).

#### Scenario 2: App is Local (Same Wi-Fi)

1. **User Action**: User toggles a "Light ON" switch.

2. **App to RPi (Direct)**: The App bypasses the cloud and sends the command directly to the RPi's local API: `POST http://192.168.1.100/api/v1/actuators/light` with payload `{"value": "on"}`.

3. **RPi Action**: RPi receives the command instantly and triggers the hardware. This is faster and works even if the internet is down.

## Phase 3: Offline Capabilities

### Scenario 1: RPi loses Internet (but Local Wi-Fi is ON)

**RPi:**
- SyncManager fails to reach the MASH Backend. It simply retries later.
- DatabaseManager continues to save all sensor readings to the local SQLite DB. No data is lost.

**App (on same Wi-Fi):**
- The App can still discover and connect to the RPi's local API.
- User retains full local control (lights, fans) and can see live sensor data.
- The app would show a "Cloud Disconnected" or "Syncing..." icon. Historical data (before the internet drop) would be loaded from the backend (or app cache).

### Scenario 2: RPi is fully offline (Power Outage)

**RPi**: Device is off. No data collection.

**App:**
- Cannot connect to the RPi (locally) or the Backend (which reports the device as "offline").
- App shows the device as "Offline".
- User can only view historical data cached in the app or fetched from the backend (up to the last sync point). All controls are disabled.

### Scenario 3: App is Offline (no Wi-Fi/4G)

**App:**
- Cannot reach the Backend or the local RPi.
- App should load historical data from its own local cache (DatabaseHelper in the mobile code).
- All live data and controls are disabled. App shows "Offline".