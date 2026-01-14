# Lucide Icons Integration Guide

## Icon Assets Structure

Place downloaded PNG icons from [lucide.dev](https://lucide.dev) in:
```
touchscreen_ui/assets/icons/
├── home.png           # Dashboard/Home
├── sliders.png        # Controls/Settings
├── bell.png           # Alerts/Notifications
├── brain.png          # AI Insights
├── help-circle.png    # Help/Support
├── settings.png       # Settings
├── wifi.png           # WiFi/Network
├── droplet.png        # Humidity/Humidifier
├── wind.png           # Fan/Ventilation
├── lightbulb.png      # LED Lights
├── thermometer.png    # Temperature
├── gauge.png          # CO2 Sensor
├── activity.png       # System Activity
├── power.png          # Power/Enable
├── refresh-cw.png     # Refresh/Reload
├── check-circle.png   # Success
├── alert-triangle.png # Warning
├── x-circle.png       # Error
├── info.png           # Information
└── chevron-right.png  # Navigation Arrow
```

## Icon Download Instructions

1. Visit [lucide.dev](https://lucide.dev)
2. Search for each icon name
3. Download as PNG (60x60px for standard icons, 32x32px for small icons)
4. Recommended settings:
   - **Size**: 60x60 pixels (standard), 32x32 pixels (small)
   - **Color**: White (#FFFFFF) for dark theme
   - **Stroke Width**: 2px
   - **Format**: PNG with transparency

## Required Icons List

### Navigation Icons
- `home.png` - Dashboard navigation
- `sliders.png` - Controls navigation
- `bell.png` - Alerts navigation
- `brain.png` - AI Insights navigation
- `help-circle.png` - Help navigation
- `settings.png` - Settings navigation

### Actuator Icons
- `droplet.png` - Humidifier control
- `wind.png` - Fan controls (circulation & exhaust)
- `lightbulb.png` - LED grow lights

### Sensor Icons
- `gauge.png` - CO2 measurement
- `thermometer.png` - Temperature
- `droplet.png` - Humidity

### Status Icons
- `check-circle.png` - Success state
- `alert-triangle.png` - Warning state
- `x-circle.png` - Error state
- `info.png` - Information state

### System Icons
- `wifi.png` - WiFi connectivity
- `activity.png` - System activity
- `power.png` - Power/Enable toggle
- `refresh-cw.png` - Refresh data
- `chevron-right.png` - Navigation arrow

## Usage in Code

### Method 1: Direct Image Widget
```python
from kivy.uix.image import Image
from kivy.metrics import dp

icon = Image(
    source='assets/icons/home.png',
    size_hint=(None, None),
    size=(dp(60), dp(60))
)
```

### Method 2: Icon Helper (Recommended)
```python
from utils.icon_helper import get_icon

# Standard icon (60x60)
icon = get_icon('home')

# Small icon (32x32)
icon = get_icon('bell', size='small')

# Custom size
icon = get_icon('settings', size=40)
```

## Icon Helper Implementation

The icon helper is already created at `touchscreen_ui/utils/icon_helper.py`
