"""
MASH Touchscreen UI - Dashboard Screen
Main screen showing sensor readings and system status
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
import config
import json
import os
from widgets.sensor_card import SensorCard
from widgets.status_bar import StatusBar
from widgets.navigation_sidebar import NavigationSidebar
from widgets.tutorial_overlay import TutorialOverlay


class DashboardScreen(Screen):
    """Dashboard screen with sensor monitoring"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = 'dashboard'
        
        # Root layout with sidebar
        root_layout = BoxLayout(orientation='horizontal', spacing=0)
        
        # Navigation sidebar
        self.sidebar = NavigationSidebar(app_instance=app_instance)
        root_layout.add_widget(self.sidebar)
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        # Status bar
        self.status_bar = StatusBar()
        main_layout.add_widget(self.status_bar)
        
        # Content area
        content = BoxLayout(
            orientation='vertical',
            padding=dp(20) * config.SCALE_FACTOR,
            spacing=dp(15) * config.SCALE_FACTOR
        )
        
        root_layout.add_widget(main_layout)
        
        # Title
        title = Label(
            text='Live Monitoring',
            font_size=config.FONTS['size_title'],
            size_hint=(1, None),
            height=dp(40) * config.SCALE_FACTOR,
            color=config.COLORS['text_primary'],
            bold=True
        )
        content.add_widget(title)
        
        # Sensor cards grid
        sensor_grid = GridLayout(
            cols=2 if config.CURRENT_SCREEN == '7' else 1,
            spacing=dp(20) * config.SCALE_FACTOR,
            size_hint=(1, None),
            height=dp(300) * config.SCALE_FACTOR,
            padding=[dp(5) * config.SCALE_FACTOR, 0]
        )
        
        # CO2 sensor card
        self.co2_card = SensorCard(
            sensor_name="CO₂",
            sensor_value="--",
            sensor_unit="ppm",
            sensor_icon="CO2",
            status_color=config.COLORS['co2']
        )
        sensor_grid.add_widget(self.co2_card)
        
        # Temperature sensor card
        self.temp_card = SensorCard(
            sensor_name="Temperature",
            sensor_value="--",
            sensor_unit="°C",
            sensor_icon="TEMP",
            status_color=config.COLORS['temperature']
        )
        sensor_grid.add_widget(self.temp_card)
        
        # Humidity sensor card
        self.humidity_card = SensorCard(
            sensor_name="Humidity",
            sensor_value="--",
            sensor_unit="%",
            sensor_icon="H2O",
            status_color=config.COLORS['humidity']
        )
        sensor_grid.add_widget(self.humidity_card)
        
        # Mode indicator card
        self.mode_card = SensorCard(
            sensor_name="Chamber Mode",
            sensor_value="Spawning",
            sensor_unit="",
            sensor_icon="MODE",
            status_color=config.COLORS['primary']
        )
        sensor_grid.add_widget(self.mode_card)
        
        content.add_widget(sensor_grid)
        
        # Alert area
        self.alert_box = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(60) * config.SCALE_FACTOR,
            padding=dp(10) * config.SCALE_FACTOR
        )
        
        with self.alert_box.canvas.before:
            self.alert_color = Color(0, 0, 0, 0)
            self.alert_rect = Rectangle(pos=self.alert_box.pos, size=self.alert_box.size)
        
        self.alert_box.bind(
            pos=lambda *x: setattr(self.alert_rect, 'pos', self.alert_box.pos),
            size=lambda *x: setattr(self.alert_rect, 'size', self.alert_box.size)
        )
        
        self.alert_label = Label(
            text='',
            font_size=config.FONTS['size_body'],
            color=config.COLORS['text_primary'],
            bold=True
        )
        self.alert_box.add_widget(self.alert_label)
        content.add_widget(self.alert_box)
        
        # Navigation buttons
        nav_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60) * config.SCALE_FACTOR,
            spacing=dp(10) * config.SCALE_FACTOR
        )
        
        controls_btn = Button(
            text='Controls',
            font_size=config.FONTS['size_body'],
            background_color=config.COLORS['primary'],
            on_press=lambda x: self.go_to_controls()
        )
        nav_layout.add_widget(controls_btn)
        
        settings_btn = Button(
            text='Settings',
            font_size=config.FONTS['size_body'],
            background_color=config.COLORS['surface_light'],
            on_press=lambda x: self.go_to_settings()
        )
        nav_layout.add_widget(settings_btn)
        
        content.add_widget(nav_layout)
        
        # Add content to main layout
        main_layout.add_widget(content)
        
        # Set background
        with main_layout.canvas.before:
            Color(*config.COLORS['background'])
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        main_layout.bind(
            pos=lambda *x: setattr(self.bg_rect, 'pos', main_layout.pos),
            size=lambda *x: setattr(self.bg_rect, 'size', main_layout.size)
        )
        
        self.add_widget(root_layout)
        
        # Tutorial overlay (shown on first run)
        self.tutorial_overlay = None
        self.config_file = 'data/device_state.json'
    
    def on_enter(self):
        """Called when screen is displayed"""
        # Set sidebar active state
        if hasattr(self, 'sidebar'):
            self.sidebar.set_active_screen('dashboard')
        
        # Check if tutorial should be shown
        self._check_show_tutorial()
        
        # Update immediately
        self.update_display()
        
        # Schedule periodic updates
        self.update_event = Clock.schedule_interval(lambda dt: self.update_display(), 2)
    
    def _check_show_tutorial(self):
        """Check if tutorial should be shown"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    state = json.load(f)
                
                # Show tutorial if not done yet
                if not state.get('isTutorialDone', False):
                    # Delay showing tutorial by 1 second to let screen load
                    Clock.schedule_once(lambda dt: self._show_tutorial(), 1.0)
        except Exception as e:
            print(f"Error checking tutorial state: {e}")
    
    def _show_tutorial(self):
        """Show tutorial overlay"""
        if not self.tutorial_overlay:
            self.tutorial_overlay = TutorialOverlay(dashboard_screen=self)
            self.add_widget(self.tutorial_overlay)
    
    def on_leave(self):
        """Called when leaving screen"""
        if hasattr(self, 'update_event'):
            self.update_event.cancel()
    
    def update_display(self):
        """Update sensor values and status"""
        # Update sensor cards
        sensor_data = self.app.sensor_data
        
        if sensor_data:
            # CO2
            co2 = sensor_data.get('co2', 0)
            self.co2_card.update_value(
                co2,
                'error' if co2 > 20000 else 'warning' if co2 > 15000 else 'normal'
            )
            
            # Temperature
            temp = sensor_data.get('temperature', 0.0)
            self.temp_card.update_value(
                f"{temp:.1f}",
                'error' if temp > 32 else 'warning' if temp > 28 else 'normal'
            )
            
            # Humidity
            humidity = sensor_data.get('humidity', 0.0)
            self.humidity_card.update_value(
                f"{humidity:.1f}",
                'warning' if humidity < 80 or humidity > 95 else 'normal'
            )
            
            # Mode
            mode = sensor_data.get('mode', 's')
            self.mode_card.sensor_value = "Spawning" if mode == 's' else "Fruiting"
            
            # Alert
            if sensor_data.get('alert', False):
                self.show_alert("WARNING: Environmental conditions need attention!")
            else:
                self.hide_alert()
        
        # Update status bar
        self.status_bar.backend_connected = self.app.api_client.health_check()
        self.status_bar.mqtt_connected = self.app.mqtt_client.connected if self.app.mqtt_client else False
        self.status_bar.automation_enabled = self.app.automation_enabled
    
    def show_alert(self, message):
        """Show alert message"""
        self.alert_label.text = message
        self.alert_color.rgba = config.COLORS['warning']
    
    def hide_alert(self):
        """Hide alert message"""
        self.alert_label.text = ''
        self.alert_color.rgba = (0, 0, 0, 0)
    
    def go_to_controls(self):
        """Navigate to controls screen"""
        self.manager.current = 'controls'
    
    def go_to_settings(self):
        """Navigate to settings screen"""
        self.manager.current = 'settings'
