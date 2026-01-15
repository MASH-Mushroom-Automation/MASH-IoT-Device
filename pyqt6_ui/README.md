# MASH IoT Device - PyQt6 UI

Modern touchscreen interface for the MASH IoT mushroom growing automation system, built with PyQt6.

## Features

✨ **Modern UI Design**
- Dark theme optimized for grow room environments
- Lucide icon integration
- Responsive 800x480 touchscreen layout
- Smooth animations and transitions

📊 **Real-Time Dashboard**
- Live sensor data (CO2, Temperature, Humidity)
- 30-minute trend charts with PyQt6 Charts
- Status indicators with color-coded thresholds
- Auto-refresh every 5 seconds

🎮 **Manual Controls**
- Toggle actuators (Humidifier, Fans, Grow Lights)
- Automation enable/disable switch
- Real-time state synchronization
- Visual feedback for all actions

🔔 **Alerts System**
- Color-coded severity levels (Info, Warning, Error)
- Filter by severity
- Timestamp and categorization
- Auto-refresh monitoring

🧠 **AI Insights**
- View automation decision history
- Detailed reasoning for each action
- Sensor data context
- Chronological timeline

⚙️ **Settings**
- System information display
- Network configuration
- Sensor threshold display
- Data export functionality

## Requirements

### Software
- Python 3.13+ (or Python 3.8+ on other systems)
- PyQt6 6.6.0+
- PyQt6-Charts 6.6.0+

### Hardware
- Raspberry Pi 3/4/5 (recommended)
- 7" touchscreen display (800x480)
- Or any desktop with 800x480+ resolution

## Installation

### On Raspberry Pi (Debian/Ubuntu)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pyqt6 python3-pyqt6.qtcharts python3-pip

# Clone repository (if not already done)
cd ~/MASH-IoT-Device

# Install Python dependencies
cd pyqt6_ui
pip3 install -r requirements.txt
```

### On Windows

```bash
# Navigate to pyqt6_ui directory
cd pyqt6_ui

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### On macOS

```bash
cd pyqt6_ui

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Demo Mode (Mock Data)

Perfect for testing without hardware or backend:

1. **Set environment variable:**
   ```bash
   # Windows PowerShell
   $env:MOCK_MODE="true"
   
   # Linux/macOS
   export MOCK_MODE=true
   ```

2. **Or create `.env` file** in `touchscreen_ui` directory:
   ```
   MOCK_MODE=true
   DEBUG=true
   ```

3. **Run the application:**
   ```bash
   # Windows
   run.bat
   # or
   run.ps1
   
   # Linux/Raspberry Pi
   ./run.sh
   # or
   python main.py
   ```

### Production Mode

With real backend and hardware:

1. **Ensure Flask backend is running:**
   ```bash
   cd ~/MASH-IoT-Device
   python integrated_server.py
   ```

2. **Set MOCK_MODE to false** (or remove from .env)

3. **Run the UI:**
   ```bash
   cd pyqt6_ui
   python main.py
   ```

## Configuration

Edit [config.py](config.py) to customize:

```python
# Display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# API Endpoints
API_BASE_URL = 'http://127.0.0.1:5000/api'

# Update Intervals
SENSOR_UPDATE_INTERVAL = 5  # seconds
CHART_UPDATE_INTERVAL = 60

# Theme Colors
COLORS = {
    'primary': '#43D178',  # MASH green
    'background': '#17171C',
    # ... more colors
}
```

## Project Structure

```
pyqt6_ui/
├── main.py                 # Application entry point
├── main_window.py          # Main window with navigation
├── config.py               # Configuration and theme
├── api_client.py           # API communication layer
├── requirements.txt        # Python dependencies
├── screens/
│   ├── dashboard.py        # Dashboard with charts
│   ├── controls.py         # Actuator controls
│   ├── alerts.py           # Alerts display
│   ├── ai_insights.py      # AI decision history
│   └── settings.py         # Settings and info
└── run.bat / run.ps1 / run.sh  # Launcher scripts
```

## Raspberry Pi Deployment

### Auto-start on Boot

1. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/mash-ui.service
   ```

2. **Add configuration:**
   ```ini
   [Unit]
   Description=MASH IoT Device UI
   After=graphical.target
   
   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/MASH-IoT-Device/pyqt6_ui
   Environment="DISPLAY=:0"
   Environment="MOCK_MODE=false"
   ExecStart=/home/pi/MASH-IoT-Device/pyqt6_ui/venv/bin/python main.py
   Restart=on-failure
   
   [Install]
   WantedBy=graphical.target
   ```

3. **Enable service:**
   ```bash
   sudo systemctl enable mash-ui.service
   sudo systemctl start mash-ui.service
   ```

### Touchscreen Calibration

If touch input is inverted or offset:

```bash
# Install calibration tool
sudo apt-get install xinput-calibrator

# Run calibration
DISPLAY=:0 xinput_calibrator
```

## Troubleshooting

### Import Error: No module named 'PyQt6'

```bash
# Raspberry Pi
sudo apt-get install python3-pyqt6 python3-pyqt6.qtcharts

# Or via pip
pip install PyQt6 PyQt6-Charts
```

### Charts Not Displaying

Ensure PyQt6-Charts is installed:
```bash
pip install PyQt6-Charts
```

### API Connection Failed

1. Check Flask backend is running: `http://localhost:5000/api/sensor/current`
2. Verify API_BASE_URL in config.py
3. Try demo mode: `MOCK_MODE=true`

### Display Issues on Raspberry Pi

```bash
# Set Qt platform
export QT_QPA_PLATFORM=xcb

# Or use EGL for better performance
export QT_QPA_PLATFORM=eglfs
```

## Performance Notes

- **RAM Usage:** ~150MB (vs 300MB for Kivy)
- **CPU Usage:** 5-10% idle, 15-25% with animations
- **Startup Time:** 2-3 seconds on RPi3, <1s on RPi4+

## Development

### Adding New Screens

1. Create screen in `screens/new_screen.py`:
   ```python
   from PyQt6.QtWidgets import QWidget, QVBoxLayout
   
   class NewScreen(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.setup_ui()
       
       def setup_ui(self):
           # Build UI here
           pass
       
       def refresh(self):
           # Called when screen becomes visible
           pass
   ```

2. Add to [main_window.py](main_window.py):
   ```python
   from screens.new_screen import NewScreen
   
   self.screens['new_screen'] = NewScreen()
   ```

3. Add navigation button in [main_window.py](main_window.py):
   ```python
   ('new_screen', 'New Screen', ICONS['icon_name'])
   ```

### Customizing Icons

Icons are located in `../touchscreen_ui/assets/icons/`. To add new icons:

1. Download from [lucide.dev](https://lucide.dev)
2. Export as PNG (24x24 or 32x32)
3. Place in icons directory
4. Add to ICONS dict in [config.py](config.py)

## Migration from Kivy

Key advantages of PyQt6 over Kivy:

| Feature | PyQt6 | Kivy |
|---------|-------|------|
| Python 3.13 Support | ✅ Yes | ❌ No (requires 3.11) |
| Native Look | ✅ Yes | ⚠️ Custom only |
| Built-in Charts | ✅ Qt Charts | ❌ Manual/3rd party |
| RAM Usage | 150MB | 300MB |
| Documentation | Excellent | Good |
| Touch Support | ✅ Full | ✅ Full |

## License

MIT License - See [LICENSE](../LICENSE)

## Support

For issues or questions:
- GitHub Issues: [MASH-Mushroom-Automation/MASH-IoT-Device](https://github.com/MASH-Mushroom-Automation/MASH-IoT-Device)
- Documentation: See [documents/](../documents/) folder
