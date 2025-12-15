"""
MASH Touchscreen UI - Status Bar Widget
Top bar showing connection status and system info
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import datetime
import config


class StatusBar(BoxLayout):
    """Top status bar widget"""
    
    # Properties
    device_name = StringProperty(config.DEVICE_NAME)
    backend_connected = BooleanProperty(False)
    mqtt_connected = BooleanProperty(False)
    automation_enabled = BooleanProperty(False)
    current_time = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout settings
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.height = dp(50) * config.SCALE_FACTOR
        self.padding = [dp(15) * config.SCALE_FACTOR, dp(5) * config.SCALE_FACTOR]
        self.spacing = dp(10) * config.SCALE_FACTOR
        
        # Draw background
        with self.canvas.before:
            Color(*config.COLORS['surface_light'])
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Left side - Device name
        self.device_label = Label(
            text=self.device_name,
            font_size=config.FONTS['size_body'],
            bold=True,
            color=config.COLORS['text_primary'],
            size_hint=(0.4, 1),
            halign='left',
            valign='middle'
        )
        self.device_label.bind(size=self.device_label.setter('text_size'))
        self.add_widget(self.device_label)
        
        # Center - Status indicators
        self.status_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.4, 1),
            spacing=dp(8) * config.SCALE_FACTOR
        )
        
        self.backend_indicator = Label(
            text="[-] API",
            font_size=config.FONTS['size_caption'],
            color=config.COLORS['text_secondary'],
            size_hint=(0.33, 1)
        )
        self.status_layout.add_widget(self.backend_indicator)
        
        self.mqtt_indicator = Label(
            text="[-] MQTT",
            font_size=config.FONTS['size_caption'],
            color=config.COLORS['text_secondary'],
            size_hint=(0.33, 1)
        )
        self.status_layout.add_widget(self.mqtt_indicator)
        
        self.auto_indicator = Label(
            text="[-] AUTO",
            font_size=config.FONTS['size_caption'],
            color=config.COLORS['text_secondary'],
            size_hint=(0.33, 1)
        )
        self.status_layout.add_widget(self.auto_indicator)
        
        self.add_widget(self.status_layout)
        
        # Right side - Time
        self.time_label = Label(
            text=self.current_time,
            font_size=config.FONTS['size_caption'],
            color=config.COLORS['text_secondary'],
            size_hint=(0.2, 1),
            halign='right',
            valign='middle'
        )
        self.time_label.bind(size=self.time_label.setter('text_size'))
        self.add_widget(self.time_label)
        
        # Bind properties
        self.bind(
            backend_connected=self._update_indicators,
            mqtt_connected=self._update_indicators,
            automation_enabled=self._update_indicators,
            device_name=self._update_device_name
        )
        
        # Update time every second
        Clock.schedule_interval(self._update_time, 1)
        self._update_time()
    
    def _update_rect(self, *args):
        """Update background rectangle"""
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def _update_indicators(self, *args):
        """Update status indicators"""
        # Backend indicator
        if self.backend_connected:
            self.backend_indicator.text = "[*] API"
            self.backend_indicator.color = config.COLORS['success']
        else:
            self.backend_indicator.text = "[X] API"
            self.backend_indicator.color = config.COLORS['error']
        
        # MQTT indicator
        if config.MQTT_ENABLED:
            if self.mqtt_connected:
                self.mqtt_indicator.text = "[*] MQTT"
                self.mqtt_indicator.color = config.COLORS['success']
            else:
                self.mqtt_indicator.text = "[X] MQTT"
                self.mqtt_indicator.color = config.COLORS['error']
        else:
            self.mqtt_indicator.text = "[-] MQTT"
            self.mqtt_indicator.color = config.COLORS['text_disabled']
        
        # Automation indicator
        if self.automation_enabled:
            self.auto_indicator.text = "[*] AUTO"
            self.auto_indicator.color = config.COLORS['success']
        else:
            self.auto_indicator.text = "[-] AUTO"
            self.auto_indicator.color = config.COLORS['text_secondary']
    
    def _update_device_name(self, *args):
        """Update device name label"""
        self.device_label.text = self.device_name
    
    def _update_time(self, *args):
        """Update current time"""
        self.current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.text = self.current_time
