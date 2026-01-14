"""
Quick Icon Integration Example
Replace text-based icons with Lucide PNG icons
"""

# Example 1: NavigationSidebar - Replace emoji icons
# Before:
nav_items = [
    ('🏠', 'dashboard', 'Home'),
    ('🔔', 'alerts', 'Alerts'),
]

# After (in navigation_sidebar.py):
from utils.icon_helper import get_icon

class NavigationButton(Button):
    def __init__(self, icon_name, screen_name, label_text, **kwargs):
        super().__init__(**kwargs)
        
        # Create layout
        layout = BoxLayout(orientation='vertical', spacing=dp(5))
        
        # Add icon
        icon = get_icon(icon_name, size='medium')
        layout.add_widget(icon)
        
        # Add label
        label = Label(text=label_text, font_size='12sp')
        layout.add_widget(label)


# Example 2: SensorCard - Add sensor type icon
# In sensor_card.py:
from utils.icon_helper import get_icon

class SensorCard(BoxLayout):
    def __init__(self, sensor_type, value, unit, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        
        # Icon on the left
        icon = get_icon(sensor_type, size='large')  # 'co2', 'temperature', or 'humidity'
        self.add_widget(icon)
        
        # Value and unit
        value_label = Label(text=f'{value} {unit}')
        self.add_widget(value_label)


# Example 3: ActuatorControl - Add actuator icon
# In toggle_button.py:
from utils.icon_helper import get_icon

class ToggleButton(Button):
    def __init__(self, actuator_name, **kwargs):
        super().__init__(**kwargs)
        
        # Determine icon based on actuator name
        icon_map = {
            'Humidifier': 'droplet',
            'Blower Fan': 'wind',
            'Exhaust Fan': 'wind',
            'LED Lights': 'lightbulb'
        }
        
        icon_name = icon_map.get(actuator_name, 'power')
        
        # Add icon to button
        icon = get_icon(icon_name, size='medium')
        # ... layout code


# Example 4: StatusBar - Add WiFi and connection icons
# In status_bar.py:
from utils.icon_helper import get_icon

def update_wifi_status(self, connected):
    if connected:
        icon = get_icon('wifi', size='small')
    else:
        icon = get_icon('wifi', size='small')  # Could use different color


# Download and placement checklist:
"""
1. Go to https://lucide.dev
2. Search for each icon name
3. Click "Copy SVG" or "Download PNG"
4. If downloading PNG:
   - Set size to 60x60px
   - Set color to #FFFFFF (white)
   - Set stroke width to 2px
5. Save in: touchscreen_ui/assets/icons/
6. Naming convention: lowercase-with-hyphens.png
   Example: help-circle.png, alert-triangle.png
"""
