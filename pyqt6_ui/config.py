"""
MASH IoT Device - PyQt6 UI Configuration
Modern, responsive configuration for touchscreen interface
"""

import os
from pathlib import Path

# ========== Demo/Mock Mode ==========
MOCK_MODE = os.getenv('MOCK_MODE', 'true').lower() == 'true'

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
    'text_primary': '#FFFFFF',    # Pure white for maximum contrast
    'text_secondary': '#D0D0D8',  # Brighter gray for better visibility
    'text_tertiary': '#A0A0A8',   # Tertiary text
    'text_disabled': '#8B8B95',   # Slightly brighter dark gray
    
    # Additional UI colors
    'bg': '#17171C',              # Main background
    'card_bg': '#2D2D35',         # Card background
    'hover_bg': '#35353D',        # Hover background
    'border': '#3A3A42',          # Border color
    'border_light': '#45454D',    # Light border
    'primary_hover': '#52E88C',   # Primary hover
    'primary_pressed': '#34A65E', # Primary pressed
    
    # Sensor colors
    'co2': '#2196F3',             # Blue
    'co2_color': '#2196F3',       # Blue
    'temperature': '#FF6B35',     # Orange-red
    'temperature_color': '#FF6B35', # Orange-red
    'humidity': '#4ECDC4',        # Cyan
    'humidity_color': '#4ECDC4',  # Cyan
}

# ========== Typography ==========
FONTS = {
    'heading': 22,
    'subheading': 16,
    'body': 14,
    'body_small': 12,
    'caption': 11,
    'button': 14,
    'label': 13,
    'value': 32,
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
    'home': 'house.svg',
    'dashboard': 'house.svg',
    'controls': 'sliders-vertical.svg',
    'alerts': 'bell.svg',
    'ai_insights': 'brain.svg',
    'automation': 'brain.svg',
    'settings': 'settings.svg',
    'help': 'circle-question-mark.svg',
    
    # Sensors
    'sensor': 'thermometer.svg',
    'co2': 'wind.svg',
    'temperature': 'thermometer.svg',
    'humidity': 'droplet.svg',
    
    # Actuators
    'humidifier': 'droplets.svg',
    'fan_exhaust': 'air-vent.svg',
    'fan_circulation': 'fan.svg',
    'led_grow': 'lightbulb.svg',
    
    # Status
    'success': 'circle-check-big.svg',
    'warning': 'triangle-alert.svg',
    'error': 'circle-alert.svg',
    'info': 'info.svg',
    
    # Actions
    'refresh': 'refresh-cw.svg',
    'download': 'download.svg',
    'power': 'power.svg',
    'play': 'play.svg',
    'pause': 'pause.svg',
    'hand': 'hand.svg',
    'zap': 'zap.svg',
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
        font-size: 14px;
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
        padding: 12px 20px;
        font-size: 15px;
        font-weight: 600;
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
        padding: 12px;
    }}
    
    /* Scroll Area */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    
    QScrollBar:vertical {{
        background-color: {COLORS['surface']};
        width: 10px;
        border-radius: 5px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['border_light']};
        border-radius: 5px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['primary']};
    }}
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: none;
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
        font-size: 38px;
        font-weight: bold;
        color: {COLORS['text_primary']};
    }}
    
    QLabel.sensor-unit {{
        font-size: 16px;
        font-weight: 500;
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
