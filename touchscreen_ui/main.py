#!/usr/bin/env python3
"""
MASH Touchscreen UI - Main Application
Local interface for Raspberry Pi 3 with 7" touchscreen
"""

import os
import sys
import logging

# ========== RPi3 GPU Optimization ==========
# Set environment variables BEFORE importing Kivy for optimal performance
if not os.getenv('KIVY_WINDOW'):
    # Check if running on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo:
                # Optimize for Broadcom GPU (RPi3)
                os.environ['KIVY_WINDOW'] = 'egl_rpi'
                os.environ['KIVY_BCM_DISPMANX_ID'] = '2'
                print("✓ RPi3 GPU optimization enabled")
    except:
        pass

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config as KivyConfig

# Import configuration
import config

# Configure Kivy before importing other Kivy modules
if not config.DEBUG:
    # Disable multitouch emulation (right-click) in production
    KivyConfig.set('input', 'mouse', 'mouse,multitouch_on_demand')

# Detect screen size and update config
if config.SCREEN_SIZE == 'auto':
    try:
        # Try to detect from environment first
        detected_size = config.detect_screen_size()
        config.CURRENT_SCREEN = detected_size
        
        # Update screen config
        screen_config = config.SCREEN_CONFIGS[detected_size]
        config.SCREEN_WIDTH = screen_config['width']
        config.SCREEN_HEIGHT = screen_config['height']
        config.SCALE_FACTOR = screen_config['scale_factor']
        
        logger = logging.getLogger(__name__)
        logger.info(f"Auto-detected screen: {screen_config['name']}")
    except:
        pass

# Set window size for development (comment out on actual RPi3 touchscreen)
if config.DEBUG:
    Window.size = (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import API client and MQTT client
from api_client import get_api_client
from mqtt_client import get_mqtt_client


class MASHApp(App):
    """Main Kivy application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_client = get_api_client()
        self.mqtt_client = get_mqtt_client()
        self.screen_manager = None
        
        # Application state
        self.sensor_data = {}
        self.actuator_states = {}
        self.device_status = {}
        self.automation_enabled = False
        
        # Update callbacks
        self.sensor_update_callback = None
        self.actuator_update_callback = None
        self.status_update_callback = None
        
        # Set up MQTT callbacks
        if self.mqtt_client.enabled:
            self.mqtt_client.set_on_sensor_data(self._on_mqtt_sensor_data)
            self.mqtt_client.set_on_actuator_update(self._on_mqtt_actuator_update)
            self.mqtt_client.set_on_status_update(self._on_mqtt_status_update)
    
    def build(self):
        """Build the application UI"""
        logger.info("Building MASH Touchscreen UI")
        
        # Create screen manager with FadeTransition for better performance
        from kivy.uix.screenmanager import FadeTransition
        self.screen_manager = ScreenManager(transition=FadeTransition(duration=0.2))
        
        # Import screen classes
        from screens.splash import SplashScreen
        from screens.setup_wizard import SetupWizardScreen
        from screens.dashboard import DashboardScreen
        from screens.controls import ControlsScreen
        from screens.alerts import AlertsScreen
        from screens.ai_insights import AIInsightsScreen
        from screens.help import HelpScreen
        from screens.settings import SettingsScreen
        from screens.wifi_setup import WiFiSetupScreen
        
        # Add all screens
        self.screen_manager.add_widget(SplashScreen(app_instance=self, name='splash'))
        self.screen_manager.add_widget(SetupWizardScreen(app_instance=self, name='setup_wizard'))
        self.screen_manager.add_widget(DashboardScreen(app_instance=self, name='dashboard'))
        self.screen_manager.add_widget(ControlsScreen(app_instance=self, name='controls'))
        self.screen_manager.add_widget(AlertsScreen(app_instance=self, name='alerts'))
        self.screen_manager.add_widget(AIInsightsScreen(app_instance=self, name='ai_insights'))
        self.screen_manager.add_widget(HelpScreen(app_instance=self, name='help'))
        self.screen_manager.add_widget(SettingsScreen(app_instance=self, name='settings'))
        self.screen_manager.add_widget(WiFiSetupScreen(app_instance=self, name='wifi_setup'))
        
        # Set splash screen as entry point
        self.screen_manager.current = 'splash'
        
        # Set background color
        Window.clearcolor = config.COLORS['background']
        
        # Schedule periodic updates
        self.sensor_update_callback = Clock.schedule_interval(
            self.update_sensor_data,
            config.SENSOR_UPDATE_INTERVAL
        )
        
        self.actuator_update_callback = Clock.schedule_interval(
            self.update_actuator_states,
            config.ACTUATOR_UPDATE_INTERVAL
        )
        
        self.status_update_callback = Clock.schedule_interval(
            self.update_device_status,
            config.STATUS_UPDATE_INTERVAL
        )
        
        logger.info("UI built successfully")
        return self.screen_manager
    
    def update_sensor_data(self, dt):
        """Periodically update sensor data from API"""
        data = self.api_client.get_current_sensor_data()
        if data:
            self.sensor_data = data
            logger.debug(f"Sensor data updated: CO2={data.get('co2')}, "
                        f"T={data.get('temperature')}°C, "
                        f"H={data.get('humidity')}%")
    
    def update_actuator_states(self, dt):
        """Periodically update actuator states from API"""
        states = self.api_client.get_actuator_states()
        if states:
            self.actuator_states = states
            logger.debug(f"Actuator states updated: {states}")
    
    def update_device_status(self, dt):
        """Periodically update device status from API"""
        status = self.api_client.get_status()
        if status:
            self.device_status = status
            self.automation_enabled = status.get('automation_enabled', False)
            logger.debug(f"Device status updated: Mode={status.get('mode')}, "
                        f"Auto={self.automation_enabled}")
    
    def _on_mqtt_sensor_data(self, data: dict):
        """Callback when sensor data received via MQTT"""
        logger.debug(f"MQTT sensor data: {data}")
        self.sensor_data = data
    
    def _on_mqtt_actuator_update(self, data: dict):
        """Callback when actuator state updated via MQTT"""
        logger.debug(f"MQTT actuator update: {data}")
        self.actuator_states.update(data)
    
    def _on_mqtt_status_update(self, data: dict):
        """Callback when device status updated via MQTT"""
        logger.debug(f"MQTT status update: {data}")
        self.device_status.update(data)
    
    def on_start(self):
        """Called when application starts"""
        screen_info = config.SCREEN_CONFIGS[config.CURRENT_SCREEN]
        logger.info("MASH Touchscreen UI started")
        logger.info(f"Display: {screen_info['name']} - {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}")
        logger.info(f"Scale Factor: {config.SCALE_FACTOR}x")
        logger.info(f"Backend API: {config.API_BASE_URL}")
        logger.info(f"MQTT: {'Enabled' if config.MQTT_ENABLED else 'Disabled'}")
        logger.info(f"Firebase: {'Enabled' if config.FIREBASE_ENABLED else 'Disabled'}")
    
    def on_stop(self):
        """Called when application stops"""
        logger.info("MASH Touchscreen UI stopping...")
        
        # Cancel scheduled updates
        if self.sensor_update_callback:
            self.sensor_update_callback.cancel()
        if self.actuator_update_callback:
            self.actuator_update_callback.cancel()
        if self.status_update_callback:
            self.status_update_callback.cancel()
        
        # Disconnect MQTT
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        
        logger.info("MASH Touchscreen UI stopped")


def main():
    """Entry point"""
    screen_info = config.SCREEN_CONFIGS[config.CURRENT_SCREEN]
    
    logger.info("="*60)
    logger.info("MASH Touchscreen UI")
    logger.info(f"Version: 0.1.0 (Development - Responsive)")
    logger.info(f"Device: {config.DEVICE_NAME} ({config.DEVICE_ID})")
    logger.info(f"Screen: {screen_info['name']} ({screen_info['width']}x{screen_info['height']})")
    logger.info(f"Backend: {config.API_BASE_URL}")
    logger.info(f"MQTT: {'Enabled' if config.MQTT_ENABLED else 'Disabled'}")
    logger.info(f"Firebase: {'Enabled' if config.FIREBASE_ENABLED else 'Disabled'}")
    logger.info("="*60)
    
    try:
        app = MASHApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
