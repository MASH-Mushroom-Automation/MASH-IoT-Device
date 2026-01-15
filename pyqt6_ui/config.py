"""
MASH IoT Device - PyQt6 UI Configuration
Modern, responsive configuration for touchscreen interface
"""

import os
from pathlib import Path

# ========== Demo/Mock Mode ==========
MOCK_MODE = os.getenv('MOCK_MODE', 'false').lower() == 'true'

# ========== Flask Backend API Configuration ==========
API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:5000/api')
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL', 'ws://127.0.0.1:5000')
API_TIMEOUT = 5

# ========== Display Configuration ==========
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
WINDOW_TITLE = "MASH IoT Device"

# ========== Paths ==========
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = BASE_DIR.parent / "touchscreen_ui" / "assets" / "icons"

# ========== UI Theme - Modern Dark Theme ==========
COLORS = {
    # Background colors
    'background': '#17171C',      # Very dark gray
    'surface': '#1E1E26',         # Dark gray
    'surface_light': '#26262D',   # Lighter gray
    'card': '#2D2D35',            # Card background
    'hover': '#35353D',           # Hover state
    
    # Primary colors (MASH brand green)
    'primary': '#43D178',         # MASH green
    'primary_dark': '#34A65E',    # Dark green
    'primary_light': '#52E88C',   # Light green
    
    # Status colors
    'success': '#43D178',         # Green
    'warning': '#FFB52E',         # Orange
    'error': '#F54336',           # Red
    'info': '#2196F3',            # Blue
    
    # Text colors
    'text_primary': '#F2F2F7',    # Almost white
    'text_secondary': '#ADADB5',  # Gray
    'text_disabled': '#787880',   # Dark gray
    
    # Sensor colors
    'co2': '#2196F3',             # Blue
    'temperature': '#FF6B35',     # Orange-red
    'humidity': '#4ECDC4',        # Cyan
    
    # Borders
    'border': '#35353D',
    'border_light': '#45454D',
}

# ========== Typography ==========
FONTS = {
    'heading': {'family': 'Segoe UI', 'size': 18, 'weight': 'bold'},
    'subheading': {'family': 'Segoe UI', 'size': 14, 'weight': 'semibold'},
    'body': {'family': 'Segoe UI', 'size': 12, 'weight': 'normal'},
    'caption': {'family': 'Segoe UI', 'size': 10, 'weight': 'normal'},
    'value': {'family': 'Segoe UI', 'size': 28, 'weight': 'bold'},
}

# ========== Sensor Thresholds ==========
THRESHOLDS = {
    'co2': {'min': 800, 'max': 1500, 'optimal_min': 1000, 'optimal_max': 1400, 'unit': 'ppm'},
    'temperature': {'min': 15, 'max': 25, 'optimal_min': 18, 'optimal_max': 22, 'unit': '°C'},
    'humidity': {'min': 70, 'max': 95, 'optimal_min': 80, 'optimal_max': 90, 'unit': '%'},
}

# ========== Update Intervals (seconds) ==========
SENSOR_UPDATE_INTERVAL = 5
CHART_UPDATE_INTERVAL = 60
ALERT_CHECK_INTERVAL = 10

# ========== Chart Configuration ==========
CHART_HISTORY_MINUTES = 30
CHART_MAX_POINTS = 60

# ========== Icon Mapping ==========
ICONS = {
    # Navigation
    'home': 'house.png',
    'controls': 'sliders-vertical.png',
    'alerts': 'bell.png',
    'ai_insights': 'brain.png',
    'settings': 'settings.png',
    'help': 'circle-question-mark.png',
    
    # Sensors
    'co2': 'wind.png',
    'temperature': 'thermometer.png',
    'humidity': 'droplet.png',
    
    # Actuators
    'humidifier': 'droplets.png',
    'fan_exhaust': 'air-vent.png',
    'fan_circulation': 'fan.png',
    'led_grow': 'lightbulb(1).png',
    
    # Status
    'success': 'circle-check-big.png',
    'warning': 'triangle-alert.png',
    'error': 'circle-alert.png',
    'info': 'info.png',
    
    # Actions
    'refresh': 'refresh-cw.png',
    'download': 'download.png',
    'power': 'power.png',
    'play': 'play.png',
    'pause': 'pause.png',
    'hand': 'hand.png',
    'zap': 'zap.png',
}

# ========== Stylesheet ==========
def get_stylesheet():
    """Generate PyQt6 stylesheet with theme colors"""
    return f"""
    /* Main Window */
    QMainWindow {{
        background-color: {COLORS['background']};
    }}
    
    /* General Widget Styling */
    QWidget {{
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI';
        font-size: 12px;
    }}
    
    /* Labels */
    QLabel {{
        color: {COLORS['text_primary']};
        background: transparent;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {COLORS['surface']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 500;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['hover']};
        border-color: {COLORS['border_light']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['surface_light']};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['surface']};
        color: {COLORS['text_disabled']};
    }}
    
    /* Primary Button */
    QPushButton.primary {{
        background-color: {COLORS['primary']};
        color: {COLORS['background']};
        border: none;
        font-weight: 600;
    }}
    
    QPushButton.primary:hover {{
        background-color: {COLORS['primary_light']};
    }}
    
    QPushButton.primary:pressed {{
        background-color: {COLORS['primary_dark']};
    }}
    
    /* Navigation Buttons */
    QPushButton.nav-button {{
        background-color: transparent;
        border: none;
        border-radius: 12px;
        padding: 16px;
        text-align: left;
    }}
    
    QPushButton.nav-button:hover {{
        background-color: {COLORS['surface_light']};
    }}
    
    QPushButton.nav-button:checked {{
        background-color: {COLORS['primary']};
        color: {COLORS['background']};
    }}
    
    /* Cards */
    QFrame.card {{
        background-color: {COLORS['card']};
        border-radius: 12px;
        border: 1px solid {COLORS['border']};
        padding: 16px;
    }}
    
    /* Scroll Area */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    
    QScrollBar:vertical {{
        background-color: {COLORS['surface']};
        width: 8px;
        border-radius: 4px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['border_light']};
        border-radius: 4px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['primary']};
    }}
    
    /* Status Indicators */
    QLabel.status-active {{
        color: {COLORS['success']};
        font-weight: 600;
    }}
    
    QLabel.status-inactive {{
        color: {COLORS['text_disabled']};
    }}
    
    /* Sensor Values */
    QLabel.sensor-value {{
        font-size: 28px;
        font-weight: bold;
        color: {COLORS['text_primary']};
    }}
    
    QLabel.sensor-unit {{
        font-size: 14px;
        color: {COLORS['text_secondary']};
    }}
    
    /* Alert Severity */
    QLabel.alert-info {{
        color: {COLORS['info']};
    }}
    
    QLabel.alert-warning {{
        color: {COLORS['warning']};
    }}
    
    QLabel.alert-error {{
        color: {COLORS['error']};
    }}
    
    /* Toggle Switch (styled as checkbox) */
    QCheckBox {{
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 48px;
        height: 24px;
        border-radius: 12px;
    }}
    
    QCheckBox::indicator:unchecked {{
        background-color: {COLORS['surface_light']};
        border: 1px solid {COLORS['border']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['primary']};
        border: none;
    }}
    """
