"""
MASH Touchscreen UI - Configuration
"""

import os

# ========== Flask Backend API Configuration ==========
# The touchscreen UI communicates with the existing Flask server
API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:5000/api')
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL', 'ws://127.0.0.1:5000')

# API timeout (seconds)
API_TIMEOUT = 5

# ========== Display Configuration ==========
# Auto-detect screen size or use environment variable
SCREEN_SIZE = os.getenv('SCREEN_SIZE', 'auto')  # 'auto', '3.5', '7'

# Screen specifications for different display modules
SCREEN_CONFIGS = {
    '3.5': {
        'width': 480,
        'height': 320,
        'dpi': 128,
        'scale_factor': 0.6,  # UI elements scale
        'name': '3.5" Screen'
    },
    '7': {
        'width': 800,
        'height': 480,
        'dpi': 96,
        'scale_factor': 1.0,  # Default scale
        'name': '7" Screen'
    }
}

# Auto-detect screen size based on resolution
def detect_screen_size():
    """Detect screen size from Kivy window"""
    try:
        from kivy.core.window import Window
        width = Window.width
        height = Window.height
        
        # Match resolution to screen type
        if width <= 480 and height <= 320:
            return '3.5'
        elif width <= 800 and height <= 480:
            return '7'
        else:
            # Default to 7" for larger screens
            return '7'
    except:
        # If detection fails, default to 7"
        return '7'

# Determine screen configuration
if SCREEN_SIZE == 'auto':
    CURRENT_SCREEN = '7'  # Will be updated at runtime
else:
    CURRENT_SCREEN = SCREEN_SIZE if SCREEN_SIZE in SCREEN_CONFIGS else '7'

# Get current screen config
screen_config = SCREEN_CONFIGS[CURRENT_SCREEN]
SCREEN_WIDTH = screen_config['width']
SCREEN_HEIGHT = screen_config['height']
SCREEN_DPI = screen_config['dpi']
SCALE_FACTOR = screen_config['scale_factor']

# Target frame rate
TARGET_FPS = 60

# ========== UI Theme Configuration ==========
# Color palette (dark theme for grow room environment)
COLORS = {
    # Background colors
    'background': (0.09, 0.09, 0.11, 1),        # #17171C - Very dark gray
    'surface': (0.12, 0.12, 0.15, 1),           # #1E1E26 - Dark gray
    'surface_light': (0.15, 0.15, 0.18, 1),     # #26262D - Lighter gray
    
    # Primary colors (MASH brand - green)
    'primary': (0.26, 0.82, 0.47, 1),           # #43D178 - MASH green
    'primary_dark': (0.20, 0.65, 0.37, 1),      # #34A65E - Dark green
    'primary_light': (0.32, 0.91, 0.55, 1),     # #52E88C - Light green
    
    # Status colors
    'success': (0.26, 0.82, 0.47, 1),           # #43D178 - Green
    'warning': (1.0, 0.71, 0.18, 1),            # #FFB52E - Orange
    'error': (0.96, 0.26, 0.21, 1),             # #F54336 - Red
    'info': (0.13, 0.59, 0.95, 1),              # #2196F3 - Blue
    
    # Text colors
    'text_primary': (0.95, 0.95, 0.97, 1),      # #F2F2F7 - Almost white
    'text_secondary': (0.68, 0.68, 0.71, 1),    # #ADADB5 - Gray
    'text_disabled': (0.47, 0.47, 0.50, 1),     # #787880 - Dark gray
    
    # Sensor-specific colors
    'co2': (0.13, 0.59, 0.95, 1),               # Blue
    'temperature': (0.96, 0.26, 0.21, 1),       # Red
    'humidity': (0.13, 0.71, 0.95, 1),          # Light blue
}

# Font configuration (responsive based on screen size)
def get_font_sizes():
    """Get font sizes scaled for current screen"""
    base_sizes = {
        'size_display': 42,      # Large display numbers
        'size_title': 28,
        'size_subtitle': 22,
        'size_heading': 20,
        'size_body': 16,
        'size_caption': 14,
        'size_small': 12,
        'size_icon': 36,         # Icon/emoji size
    }
    
    # Scale fonts based on screen size
    scale = SCALE_FACTOR
    return {
        key: max(10, int(size * scale))  # Minimum 10px
        for key, size in base_sizes.items()
    }

FONTS = {
    'regular': 'Roboto-Regular',
    'bold': 'Roboto-Bold',
    'light': 'Roboto-Light',
    **get_font_sizes()  # Add scaled font sizes
}

# Touch interaction (responsive)
TOUCH_MIN_SIZE = int(60 * SCALE_FACTOR)  # Minimum touch target size (scaled)
TOUCH_RIPPLE_DURATION = 0.3  # Ripple effect duration (seconds)

# ========== Data Update Configuration ==========
# How often to poll API for sensor data (seconds)
SENSOR_UPDATE_INTERVAL = 2

# How often to update actuator states (seconds)
ACTUATOR_UPDATE_INTERVAL = 5

# How often to check system status (seconds)
STATUS_UPDATE_INTERVAL = 10

# WebSocket reconnection settings
WEBSOCKET_RECONNECT_DELAY = 5  # seconds
WEBSOCKET_MAX_RETRIES = 10

# ========== Chart Configuration ==========
# Number of data points to show in live charts (adjusted for screen size)
CHART_HISTORY_SIZE = 60 if CURRENT_SCREEN == '7' else 30  # Fewer points on small screen

# Chart colors (matching sensor colors)
CHART_COLORS = {
    'co2': COLORS['co2'],
    'temperature': COLORS['temperature'],
    'humidity': COLORS['humidity'],
}

# ========== Firebase Configuration ==========
# Firebase integration for cloud sync
FIREBASE_ENABLED = os.getenv('FIREBASE_ENABLED', 'False').lower() == 'true'
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL', '')
FIREBASE_CLIENT_EMAIL = os.getenv('FIREBASE_CLIENT_EMAIL', '')
FIREBASE_PRIVATE_KEY = os.getenv('FIREBASE_PRIVATE_KEY', '')

# ========== Device Information ==========
# These are read from the main device config or environment
DEVICE_ID = os.getenv('DEVICE_ID', 'MASH-A1-CAL25-D5A91F')
DEVICE_NAME = os.getenv('DEVICE_NAME', 'MASH Chamber #1')

# ========== MQTT Configuration ==========
# MQTT broker for real-time communication
MQTT_ENABLED = os.getenv('MQTT_ENABLED', 'False').lower() == 'true'
MQTT_BROKER_URL = os.getenv('MQTT_BROKER_URL', 'mqtt://localhost:1883')
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', f'mash_ui_{DEVICE_ID}')
MQTT_TOPICS = {
    'sensor_data': f'mash/{DEVICE_ID}/sensors',
    'actuator_control': f'mash/{DEVICE_ID}/actuators',
    'device_status': f'mash/{DEVICE_ID}/status',
    'commands': f'mash/{DEVICE_ID}/commands',
}

# ========== WiFi Configuration ==========
# WiFi scan timeout (seconds)
WIFI_SCAN_TIMEOUT = 10

# WiFi connection timeout (seconds)
WIFI_CONNECT_TIMEOUT = 30

# ========== Mode Configuration ==========
# Growth modes
MODES = {
    's': {
        'name': 'Spawning',
        'icon': '🌱',
        'description': 'Mycelium colonization phase',
        'color': COLORS['primary'],
    },
    'f': {
        'name': 'Fruiting',
        'icon': '🍄',
        'description': 'Mushroom fruiting phase',
        'color': COLORS['info'],
    }
}

# ========== System Configuration ==========
# Enable debug logging
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Enable performance monitoring
SHOW_FPS = DEBUG

# Enable touch visualization (for debugging touch issues)
SHOW_TOUCH = DEBUG

# ========== Paths ==========
# Base directory of touchscreen UI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Assets directory
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
ICONS_DIR = os.path.join(ASSETS_DIR, 'icons')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')

# Kivy files directory
KV_DIR = os.path.join(BASE_DIR, 'kv')

# ========== Responsive Layout Helpers ==========
def sp(pixels):
    """Scale pixels based on screen size (Scale Pixels)"""
    return int(pixels * SCALE_FACTOR)

def dp(density_pixels):
    """Convert density-independent pixels to actual pixels"""
    return int(density_pixels * (SCREEN_DPI / 96.0))

def get_layout_config():
    """Get layout configuration for current screen size"""
    if CURRENT_SCREEN == '3.5':
        return {
            'padding': sp(10),
            'spacing': sp(8),
            'card_height': sp(80),
            'button_height': sp(50),
            'icon_size': sp(32),
            'margin': sp(8),
            'columns': 2,  # 2-column layout for small screen
        }
    else:  # 7" screen
        return {
            'padding': sp(20),
            'spacing': sp(15),
            'card_height': sp(120),
            'button_height': sp(60),
            'icon_size': sp(48),
            'margin': sp(15),
            'columns': 3,  # 3-column layout for large screen
        }
