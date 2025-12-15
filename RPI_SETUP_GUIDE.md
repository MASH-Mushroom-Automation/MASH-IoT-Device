# MASH IoT Device - Raspberry Pi Setup Guide

## Method 1: Using Remote Shell (Manual - Most Reliable)

Since you have direct shell access via Raspberry Pi Connect, this is the easiest method.

### Step 1: Create Project Directory on RPi

In your remote shell:
```bash
mkdir -p ~/MASH-IoT-Device
cd ~/MASH-IoT-Device
```

### Step 2: Transfer Files Manually

You have several options:

#### Option A: Copy-Paste Small Files
For configuration files, you can copy-paste content directly:

```bash
# Create integrated_server.py
nano integrated_server.py
# Paste content, Ctrl+O to save, Ctrl+X to exit

# Create requirements.txt
nano requirements.txt
# Paste content
```

#### Option B: Use Git with Personal Access Token (PAT)

1. **Generate a GitHub PAT:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control)
   - Copy the token (save it somewhere safe)

2. **Clone on RPi:**
```bash
cd ~
git clone https://<YOUR_GITHUB_USERNAME>:<YOUR_PAT>@github.com/MASH-Mushroom-Automation/MASH-IoT-Device.git
cd MASH-IoT-Device
```

#### Option C: Download as ZIP (if you can access via browser on RPi)

```bash
# If you have browser access on RPi
# 1. Navigate to GitHub repo
# 2. Click Code > Download ZIP
# 3. Extract to ~/MASH-IoT-Device
```

### Step 3: Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt install -y pkg-config libgl1-mesa-dev libgles2-mesa-dev
sudo apt install -y python3-setuptools libgstreamer1.0-dev git-core
sudo apt install -y gstreamer1.0-plugins-{bad,base,good,ugly}
sudo apt install -y gstreamer1.0-{omx,alsa} python3-dev libmtdev-dev
sudo apt install -y xclip xsel libjpeg-dev
```

### Step 4: Create Virtual Environment

```bash
cd ~/MASH-IoT-Device
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Python Dependencies

```bash
# Backend dependencies
pip install --upgrade pip
pip install -r requirements.txt

# UI dependencies
cd touchscreen_ui
pip install -r requirements.txt
cd ..
```

### Step 6: Configure for Production

```bash
cd touchscreen_ui
cat > .env << 'EOF'
# MASH IoT Device - Production Configuration
DEBUG=false
SCREEN_SIZE=7
DEVICE_ID=MASH-A1-CAL25-012704

# API Configuration
API_BASE_URL=http://127.0.0.1:5000/api
API_TIMEOUT=5

# MQTT Configuration (optional)
MQTT_ENABLED=false
MQTT_BROKER=127.0.0.1
MQTT_PORT=1883

# Display Settings
FULLSCREEN=true
AUTO_START=true
EOF
```

### Step 7: Test Run

```bash
# Terminal 1: Start backend
cd ~/MASH-IoT-Device
source venv/bin/activate
python integrated_server.py

# Terminal 2: Start UI (open new SSH session)
cd ~/MASH-IoT-Device/touchscreen_ui
source ../venv/bin/activate
python main.py
```

## Method 2: Using SCP from Windows (if SSH enabled)

If your RPi has SSH enabled on the network:

1. **From Windows PowerShell:**
```powershell
# Navigate to project
cd C:\Users\Ryzen\Desktop\ThesisDev\MASH-IoT-Device

# Run deployment script
.\deploy_to_rpi.ps1
```

## Method 3: Manual File-by-File Transfer

### Core Files Needed:

1. **Backend:**
   - `integrated_server.py`
   - `requirements.txt`

2. **Touchscreen UI:**
   - `touchscreen_ui/main.py`
   - `touchscreen_ui/config.py`
   - `touchscreen_ui/api_client.py`
   - `touchscreen_ui/mqtt_client.py`
   - `touchscreen_ui/requirements.txt`
   - `touchscreen_ui/.env`

3. **Screens:**
   - `touchscreen_ui/screens/__init__.py`
   - `touchscreen_ui/screens/dashboard.py`
   - `touchscreen_ui/screens/controls.py`
   - `touchscreen_ui/screens/settings.py`
   - `touchscreen_ui/screens/wifi_setup.py`

4. **Widgets:**
   - `touchscreen_ui/widgets/__init__.py`
   - `touchscreen_ui/widgets/sensor_card.py`
   - `touchscreen_ui/widgets/toggle_button.py`
   - `touchscreen_ui/widgets/status_bar.py`

### Transfer Process:

For each file:
```bash
# On RPi, create file
nano ~/MASH-IoT-Device/<path>/<filename>
# Paste content from Windows
# Save with Ctrl+O, exit with Ctrl+X
```

## Auto-Start Configuration (Optional)

### Option 1: systemd Service

Create backend service:
```bash
sudo nano /etc/systemd/system/mash-backend.service
```

Paste:
```ini
[Unit]
Description=MASH IoT Backend Server
After=network.target

[Service]
Type=simple
User=mash@mash
WorkingDirectory=/home/mash@mash/MASH-IoT-Device
ExecStart=/home/mash@mash/MASH-IoT-Device/venv/bin/python integrated_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create UI service:
```bash
sudo nano /etc/systemd/system/mash-ui.service
```

Paste:
```ini
[Unit]
Description=MASH IoT Touchscreen UI
After=mash-backend.service
Requires=mash-backend.service

[Service]
Type=simple
User=mash@mash
Environment=DISPLAY=:0
WorkingDirectory=/home/mash@mash/MASH-IoT-Device/touchscreen_ui
ExecStart=/home/mash@mash/MASH-IoT-Device/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
```

Enable services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mash-backend
sudo systemctl enable mash-ui
sudo systemctl start mash-backend
sudo systemctl start mash-ui
```

Check status:
```bash
sudo systemctl status mash-backend
sudo systemctl status mash-ui
```

### Option 2: Simple Autostart Script

```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/mash-iot.desktop
```

Paste:
```ini
[Desktop Entry]
Type=Application
Name=MASH IoT Device
Exec=/home/mash@mash/MASH-IoT-Device/start_mash.sh
Terminal=false
```

Create start script:
```bash
nano ~/MASH-IoT-Device/start_mash.sh
```

Paste:
```bash
#!/bin/bash
cd /home/mash@mash/MASH-IoT-Device
source venv/bin/activate

# Start backend in background
python integrated_server.py &

# Wait for backend to start
sleep 5

# Start UI
cd touchscreen_ui
python main.py
```

Make executable:
```bash
chmod +x ~/MASH-IoT-Device/start_mash.sh
```

## Troubleshooting

### UI doesn't display
```bash
# Check display
echo $DISPLAY
# Should show :0 or :0.0

# Test X server
xclock
# Should show a clock window
```

### Permission denied on GPIO
```bash
# Add user to GPIO group
sudo usermod -a -G gpio mash@mash
# Logout and login again
```

### Import errors
```bash
# Verify all packages installed
cd ~/MASH-IoT-Device
source venv/bin/activate
pip list
```

### Backend won't start
```bash
# Check logs
tail -f /var/log/syslog | grep mash
# Or if running manually:
python integrated_server.py
```

## Quick Reference Commands

```bash
# Start services manually
cd ~/MASH-IoT-Device
source venv/bin/activate
python integrated_server.py &
cd touchscreen_ui
python main.py

# Stop services
sudo systemctl stop mash-ui
sudo systemctl stop mash-backend

# View logs
sudo journalctl -u mash-backend -f
sudo journalctl -u mash-ui -f

# Restart services
sudo systemctl restart mash-backend
sudo systemctl restart mash-ui
```
