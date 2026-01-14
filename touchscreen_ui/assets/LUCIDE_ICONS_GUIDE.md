# Lucide Icons Guide for MASH IoT Device

This document lists all Lucide icons needed for the MASH touchscreen UI.

## Required Icons

### Navigation Icons
1. **home** - Dashboard/Home screen
   - URL: https://lucide.dev/icons/home
   - Usage: Main navigation, dashboard button
   - Size: 60x60px

2. **bell** - Alerts/Notifications screen
   - URL: https://lucide.dev/icons/bell
   - Usage: Alerts center navigation
   - Size: 60x60px

3. **brain** - AI Insights screen
   - URL: https://lucide.dev/icons/brain
   - Usage: Automation insights navigation
   - Size: 60x60px

4. **sliders** - Controls screen
   - URL: https://lucide.dev/icons/sliders
   - Usage: Manual controls navigation
   - Size: 60x60px

5. **help-circle** - Help & Maintenance screen
   - URL: https://lucide.dev/icons/help-circle
   - Usage: Help/support navigation
   - Size: 60x60px

6. **settings** - Settings screen
   - URL: https://lucide.dev/icons/settings
   - Usage: Device settings navigation
   - Size: 60x60px

### Sensor Icons
7. **wind** - CO2 Sensor
   - URL: https://lucide.dev/icons/wind
   - Usage: CO2 level indicator
   - Size: 48x48px

8. **thermometer** - Temperature Sensor
   - URL: https://lucide.dev/icons/thermometer
   - Usage: Temperature indicator
   - Size: 48x48px

9. **droplets** - Humidity Sensor
   - URL: https://lucide.dev/icons/droplets
   - Usage: Humidity indicator
   - Size: 48x48px

### Actuator Icons
10. **fan** - Fan/Circulation
    - URL: https://lucide.dev/icons/fan
    - Usage: Fan controls
    - Size: 48x48px

11. **droplet** - Humidifier
    - URL: https://lucide.dev/icons/droplet
    - Usage: Humidifier control
    - Size: 48x48px

12. **lightbulb** - LED Grow Lights
    - URL: https://lucide.dev/icons/lightbulb
    - Usage: LED light control
    - Size: 48x48px

13. **air-vent** - Exhaust Fan
    - URL: https://lucide.dev/icons/air-vent
    - Usage: Exhaust ventilation control
    - Size: 48x48px

### Status & Alert Icons
14. **check-circle** - Success/OK status
    - URL: https://lucide.dev/icons/check-circle
    - Usage: Success messages, green alerts
    - Size: 32x32px

15. **alert-triangle** - Warning status
    - URL: https://lucide.dev/icons/alert-triangle
    - Usage: Warning messages, amber alerts
    - Size: 32x32px

16. **alert-circle** - Error/Critical status
    - URL: https://lucide.dev/icons/alert-circle
    - Usage: Error messages, red alerts
    - Size: 32x32px

17. **info** - Information status
    - URL: https://lucide.dev/icons/info
    - Usage: Info messages, blue alerts
    - Size: 32x32px

### WiFi & Network Icons
18. **wifi** - WiFi Connected
    - URL: https://lucide.dev/icons/wifi
    - Usage: WiFi status, network setup
    - Size: 32x32px

19. **wifi-off** - WiFi Disconnected
    - URL: https://lucide.dev/icons/wifi-off
    - Usage: No network indicator
    - Size: 32x32px

20. **signal** - Network Signal Strength
    - URL: https://lucide.dev/icons/signal
    - Usage: Signal indicator
    - Size: 24x24px

### Action Icons
21. **power** - Power On/Off
    - URL: https://lucide.dev/icons/power
    - Usage: Turn devices on/off
    - Size: 32x32px

22. **refresh-cw** - Refresh/Reload
    - URL: https://lucide.dev/icons/refresh-cw
    - Usage: Refresh data, rescan
    - Size: 32x32px

23. **download** - Download/Export
    - URL: https://lucide.dev/icons/download
    - Usage: Export data, download logs
    - Size: 32x32px

24. **play** - Start/Resume
    - URL: https://lucide.dev/icons/play
    - Usage: Start automation
    - Size: 32x32px

25. **pause** - Pause
    - URL: https://lucide.dev/icons/pause
    - Usage: Pause automation
    - Size: 32x32px

### Mode Icons
26. **zap** - Auto Mode
    - URL: https://lucide.dev/icons/zap
    - Usage: Automation enabled indicator
    - Size: 32x32px

27. **hand** - Manual Mode
    - URL: https://lucide.dev/icons/hand
    - Usage: Manual control indicator
    - Size: 32x32px

28. **trending-up** - Optimization
    - URL: https://lucide.dev/icons/trending-up
    - Usage: Performance/optimization indicators
    - Size: 32x32px

### Additional UI Icons
29. **chevron-right** - Navigation arrow
    - URL: https://lucide.dev/icons/chevron-right
    - Usage: Next, forward navigation
    - Size: 24x24px

30. **chevron-left** - Back arrow
    - URL: https://lucide.dev/icons/chevron-left
    - Usage: Back, previous navigation
    - Size: 24x24px

31. **x** - Close/Cancel
    - URL: https://lucide.dev/icons/x
    - Usage: Close dialogs, cancel actions
    - Size: 24x24px

32. **check** - Confirm/Accept
    - URL: https://lucide.dev/icons/check
    - Usage: Confirm actions, checkmarks
    - Size: 24x24px

33. **qr-code** - QR Code
    - URL: https://lucide.dev/icons/qr-code
    - Usage: Mobile app pairing
    - Size: 48x48px

34. **clock** - Time/Schedule
    - URL: https://lucide.dev/icons/clock
    - Usage: Timers, schedules
    - Size: 32x32px

35. **calendar** - Date/Calendar
    - URL: https://lucide.dev/icons/calendar
    - Usage: Date indicators
    - Size: 32x32px

## Download Instructions

### Option 1: Individual SVG Download (Recommended)
1. Visit each icon URL above
2. Click "Copy SVG" button
3. Save as `{icon-name}.svg` in `touchscreen_ui/assets/icons/` directory
4. Or click "Download SVG" for direct download

### Option 2: NPM Package (For batch download)
```bash
npm install lucide-static
# Icons will be in node_modules/lucide-static/icons/
```

### Option 3: CDN (Not recommended for offline device)
```html
<script src="https://unpkg.com/lucide@latest"></script>
```

## Export Settings for Kivy

When exporting icons for use in Kivy:

1. **Format**: SVG (vector) or PNG (raster)
2. **Color**: Export as single color (white/black) for easy recoloring in Kivy
3. **Size**: 
   - Navigation icons: 60x60px @1x, 120x120px @2x
   - Sensor icons: 48x48px @1x, 96x96px @2x
   - Status icons: 32x32px @1x, 64x64px @2x
   - UI icons: 24x24px @1x, 48x48px @2x

## Converting SVG to PNG

Use ImageMagick or online converter:

```bash
# Using ImageMagick
magick convert -background none -density 300 input.svg -resize 60x60 output.png

# For batch conversion
for file in *.svg; do
  magick convert -background none -density 300 "$file" -resize 60x60 "${file%.svg}.png"
done
```

## Icon Atlas (Performance Optimization)

For better RPi3 performance, combine all icons into a single texture atlas:

```python
# Example atlas structure
icons_atlas = {
    'home': (0, 0, 60, 60),
    'bell': (60, 0, 60, 60),
    'brain': (120, 0, 60, 60),
    # ... etc
}
```

## Usage in Kivy

### Method 1: Image Widget
```python
from kivy.uix.image import Image
from kivy.graphics import Color

icon = Image(
    source='assets/icons/home.png',
    size_hint=(None, None),
    size=(60, 60),
    allow_stretch=True,
    keep_ratio=True
)
```

### Method 2: Label with Custom Font (Icon Font)
Convert Lucide to icon font using tools like IcoMoon:
```python
from kivy.uix.label import Label

icon = Label(
    text='\\ue900',  # Unicode character
    font_name='assets/fonts/lucide-icons.ttf',
    font_size='32sp',
    color=(1, 1, 1, 1)
)
```

### Method 3: SVG Rendering (kivy.garden.iconfonts)
```python
from kivy_garden.iconfonts import iconfonts

icon = iconfonts.Icon(
    icon='home',
    size=(60, 60),
    color=(1, 1, 1, 1)
)
```

## Color Customization

Lucide icons work best with Kivy's color system:

```python
# MASH color palette
COLORS = {
    'primary': (0.26, 0.82, 0.47, 1),      # Green - active state
    'text_secondary': (0.68, 0.68, 0.71, 1), # Gray - inactive state
    'warning': (1.0, 0.71, 0.18, 1),       # Amber - warnings
    'error': (0.96, 0.26, 0.21, 1),        # Red - errors
    'success': (0.26, 0.82, 0.47, 1),      # Green - success
}
```

## License

Lucide icons are released under the ISC License, which allows free use in commercial and personal projects.
- License: https://lucide.dev/license
- Attribution recommended but not required

## Quick Start Command

Download all icons at once:

```bash
# Create icons directory
mkdir -p touchscreen_ui/assets/icons

# Download navigation icons (bash script)
for icon in home bell brain sliders help-circle settings; do
  curl "https://api.lucide.dev/$icon.svg" -o "touchscreen_ui/assets/icons/$icon.svg"
done

# Download sensor icons
for icon in wind thermometer droplets; do
  curl "https://api.lucide.dev/$icon.svg" -o "touchscreen_ui/assets/icons/$icon.svg"
done

# Download actuator icons
for icon in fan droplet lightbulb air-vent; do
  curl "https://api.lucide.dev/$icon.svg" -o "touchscreen_ui/assets/icons/$icon.svg"
done
```

## Notes

- All icons are 24x24px base size but scale perfectly
- Stroke width: 2px (default)
- Use solid fills for better performance on RPi3
- Pre-render icons at exact display sizes for optimal performance
