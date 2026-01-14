# Lucide Icons - Download List for MASH IoT Device

## Essential Icons (Priority 1)
Download from https://lucide.dev - Set size to 60x60px, color #FFFFFF, stroke 2px

### Navigation Icons (6 icons)
- [ ] home.png - Dashboard/Home screen
- [ ] sliders.png - Controls screen  
- [ ] bell.png - Alerts/Notifications screen
- [ ] brain.png - AI Insights screen
- [ ] help-circle.png - Help/Support screen
- [ ] settings.png - Settings screen

### Actuator Control Icons (4 icons)
- [ ] droplet.png - Humidifier control
- [ ] wind.png - Fan controls (both circulation & exhaust)
- [ ] lightbulb.png - LED grow lights
- [ ] power.png - Power/Enable toggle

### Sensor Icons (3 icons)
- [ ] gauge.png - CO2 measurement
- [ ] thermometer.png - Temperature sensor
- [ ] droplet.png - Humidity sensor (same as humidifier)

### Status Icons (4 icons)
- [ ] check-circle.png - Success status
- [ ] alert-triangle.png - Warning status
- [ ] x-circle.png - Error status
- [ ] info.png - Information status

## Additional Icons (Priority 2)

### System Icons (5 icons)
- [ ] wifi.png - WiFi connectivity
- [ ] activity.png - System activity/performance
- [ ] refresh-cw.png - Refresh/Reload data
- [ ] chevron-right.png - Navigation arrow
- [ ] menu.png - Hamburger menu (if needed)

### Action Icons (4 icons)
- [ ] play.png - Start automation
- [ ] pause.png - Pause automation
- [ ] skip-forward.png - Next step
- [ ] skip-back.png - Previous step

## Download Instructions

1. **Visit lucide.dev**
   - Go to https://lucide.dev

2. **Search for icon**
   - Use search bar to find icon by name (e.g., "home", "wifi")

3. **Download PNG** (Recommended)
   - Click on icon
   - Select "PNG" format
   - Configure:
     * Size: 60x60 pixels
     * Color: #FFFFFF (white)
     * Stroke width: 2px
   - Click "Download"

4. **Save to project**
   - Place file in: `touchscreen_ui/assets/icons/`
   - Keep lowercase-with-hyphens naming (e.g., `help-circle.png`)

## Alternative: Convert SVG to PNG

If downloading PNG directly doesn't work:

1. **Download SVG**
   - Click "Copy SVG" button
   - Save as .svg file

2. **Convert to PNG** (using online tool or Inkscape)
   - Upload SVG to https://convertio.co/svg-png/
   - Set output size to 60x60px
   - Download PNG

3. **Edit color** (if needed)
   - Open in image editor (Photoshop, GIMP, Photopea)
   - Change color to white (#FFFFFF)
   - Save with transparency

## Quick Check
After downloading, verify:
- [ ] All files are in `touchscreen_ui/assets/icons/` directory
- [ ] Files are named correctly (lowercase-with-hyphens.png)
- [ ] Icons are 60x60px
- [ ] Icons have transparent background
- [ ] Icons are white (#FFFFFF) for dark theme

## Usage in Code
```python
from utils.icon_helper import get_icon

# Standard usage
icon = get_icon('home')  # Returns 60x60 Image widget

# Different sizes
small_icon = get_icon('bell', size='small')    # 32x32
medium_icon = get_icon('wifi', size='medium')  # 48x48
large_icon = get_icon('settings', size='large') # 60x60

# Custom size
custom_icon = get_icon('power', size=40)  # 40x40
```
