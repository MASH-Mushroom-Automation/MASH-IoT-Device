"""
MASH Touchscreen UI - Icon Helper
Utility functions for loading and managing Lucide icons
"""

import os
from kivy.uix.image import Image
from kivy.metrics import dp
import config

# Icon directory
ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons')

# Icon size presets
ICON_SIZES = {
    'small': 32,
    'medium': 48,
    'large': 60,
    'xlarge': 80
}

# Icon name mapping (for fallbacks)
ICON_NAMES = {
    # Navigation
    'home': 'home.png',
    'dashboard': 'home.png',
    'controls': 'sliders.png',
    'alerts': 'bell.png',
    'ai_insights': 'brain.png',
    'help': 'help-circle.png',
    'settings': 'settings.png',
    
    # Actuators
    'humidifier': 'droplet.png',
    'fan': 'wind.png',
    'fan_exhaust': 'wind.png',
    'fan_circulation': 'wind.png',
    'led_grow': 'lightbulb.png',
    'lights': 'lightbulb.png',
    
    # Sensors
    'co2': 'gauge.png',
    'temperature': 'thermometer.png',
    'humidity': 'droplet.png',
    
    # Status
    'success': 'check-circle.png',
    'warning': 'alert-triangle.png',
    'error': 'x-circle.png',
    'info': 'info.png',
    
    # System
    'wifi': 'wifi.png',
    'network': 'wifi.png',
    'activity': 'activity.png',
    'power': 'power.png',
    'refresh': 'refresh-cw.png',
    'arrow': 'chevron-right.png'
}


def get_icon_path(icon_name: str) -> str:
    """
    Get full path to icon file
    
    Args:
        icon_name: Icon name (e.g., 'home', 'settings')
        
    Returns:
        Full path to icon file
    """
    # Map icon name to filename
    filename = ICON_NAMES.get(icon_name, f'{icon_name}.png')
    
    # Construct full path
    icon_path = os.path.join(ICON_DIR, filename)
    
    # Check if file exists
    if not os.path.exists(icon_path):
        # Try direct filename
        icon_path = os.path.join(ICON_DIR, f'{icon_name}.png')
        
        # If still doesn't exist, return placeholder
        if not os.path.exists(icon_path):
            print(f"Warning: Icon '{icon_name}' not found at {icon_path}")
            # Return a default icon path or create a placeholder
            return os.path.join(ICON_DIR, 'placeholder.png')
    
    return icon_path


def get_icon(icon_name: str, size='large', color=None) -> Image:
    """
    Create an Image widget with the specified icon
    
    Args:
        icon_name: Icon name (e.g., 'home', 'settings')
        size: Size preset ('small', 'medium', 'large', 'xlarge') or int
        color: Optional color tint (not implemented for PNG)
        
    Returns:
        Kivy Image widget
    """
    # Get icon size
    if isinstance(size, str):
        icon_size = ICON_SIZES.get(size, 60)
    else:
        icon_size = size
    
    # Scale based on config
    scaled_size = dp(icon_size * config.SCALE_FACTOR)
    
    # Get icon path
    icon_path = get_icon_path(icon_name)
    
    # Create Image widget
    icon = Image(
        source=icon_path,
        size_hint=(None, None),
        size=(scaled_size, scaled_size),
        allow_stretch=True,
        keep_ratio=True
    )
    
    return icon


def create_placeholder_icon():
    """
    Create a placeholder icon if icons are missing
    
    This creates a simple colored square as a fallback
    """
    from kivy.uix.widget import Widget
    from kivy.graphics import Color, Rectangle
    
    placeholder = Widget(size_hint=(None, None), size=(dp(60), dp(60)))
    
    with placeholder.canvas:
        Color(0.3, 0.3, 0.3, 1)  # Gray
        Rectangle(pos=placeholder.pos, size=placeholder.size)
    
    placeholder.bind(pos=lambda i, v: setattr(placeholder.canvas.children[1], 'pos', v))
    placeholder.bind(size=lambda i, v: setattr(placeholder.canvas.children[1], 'size', v))
    
    return placeholder


# Ensure icon directory exists
os.makedirs(ICON_DIR, exist_ok=True)

# Create a simple placeholder if directory is empty
placeholder_path = os.path.join(ICON_DIR, 'placeholder.png')
if not os.path.exists(placeholder_path):
    try:
        from PIL import Image as PILImage, ImageDraw
        
        # Create 60x60 gray square
        img = PILImage.new('RGBA', (60, 60), (80, 80, 80, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple icon symbol
        draw.rectangle([15, 15, 45, 45], outline=(200, 200, 200, 255), width=3)
        
        # Save placeholder
        img.save(placeholder_path)
        print(f"Created placeholder icon at {placeholder_path}")
    except Exception as e:
        print(f"Could not create placeholder icon: {e}")
