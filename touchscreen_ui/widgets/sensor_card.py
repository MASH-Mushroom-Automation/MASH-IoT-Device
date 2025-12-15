"""
MASH Touchscreen UI - Sensor Card Widget
Displays sensor data with icon, value, and status
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
import config


class SensorCard(BoxLayout):
    """Widget to display sensor data"""
    
    # Properties
    sensor_name = StringProperty("Sensor")
    sensor_value = StringProperty("--")
    sensor_unit = StringProperty("")
    sensor_icon = StringProperty("📊")
    status_color = ListProperty(config.COLORS['primary'])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout settings
        self.orientation = 'vertical'
        self.padding = dp(15) * config.SCALE_FACTOR
        self.spacing = dp(10) * config.SCALE_FACTOR
        self.size_hint = (None, None)
        self.width = dp(220) * config.SCALE_FACTOR
        self.height = dp(140) * config.SCALE_FACTOR
        
        # Draw background
        with self.canvas.before:
            Color(*config.COLORS['surface'])
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12) * config.SCALE_FACTOR]
            )
        
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Icon
        self.icon_label = Label(
            text=self.sensor_icon,
            font_size=config.FONTS['size_icon'],
            size_hint=(1, 0.3),
            color=self.status_color
        )
        self.add_widget(self.icon_label)
        
        # Value
        self.value_label = Label(
            text=self.sensor_value,
            font_size=config.FONTS['size_display'],
            size_hint=(1, 0.4),
            bold=True,
            color=config.COLORS['text_primary']
        )
        self.add_widget(self.value_label)
        
        # Name and unit
        self.name_label = Label(
            text=f"{self.sensor_name} {self.sensor_unit}",
            font_size=config.FONTS['size_caption'],
            size_hint=(1, 0.3),
            color=config.COLORS['text_secondary']
        )
        self.add_widget(self.name_label)
        
        # Bind properties to update display
        self.bind(
            sensor_name=self._update_labels,
            sensor_value=self._update_labels,
            sensor_unit=self._update_labels,
            sensor_icon=self._update_labels,
            status_color=self._update_labels
        )
    
    def _update_rect(self, *args):
        """Update background rectangle"""
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def _update_labels(self, *args):
        """Update label text and colors"""
        self.icon_label.text = self.sensor_icon
        self.icon_label.color = self.status_color
        self.value_label.text = self.sensor_value
        self.name_label.text = f"{self.sensor_name} {self.sensor_unit}"
    
    def update_value(self, value, status='normal'):
        """
        Update sensor value and status
        
        Args:
            value: Sensor reading value
            status: 'normal', 'warning', or 'error'
        """
        self.sensor_value = str(value)
        
        # Update color based on status
        if status == 'warning':
            self.status_color = config.COLORS['warning']
        elif status == 'error':
            self.status_color = config.COLORS['error']
        else:
            self.status_color = config.COLORS['primary']
