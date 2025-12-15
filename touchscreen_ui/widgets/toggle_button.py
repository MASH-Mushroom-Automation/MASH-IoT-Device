"""
MASH Touchscreen UI - Toggle Button Widget
Custom toggle button for actuator control
"""

from kivy.uix.button import Button
from kivy.properties import BooleanProperty, StringProperty, ListProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
import config


class ToggleButton(Button):
    """Custom toggle button for actuators"""
    
    # Properties
    is_on = BooleanProperty(False)
    actuator_name = StringProperty("Actuator")
    icon_on = StringProperty("[ON]")
    icon_off = StringProperty("[OFF]")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Button settings
        self.size_hint = (None, None)
        self.width = dp(160) * config.SCALE_FACTOR
        self.height = dp(60) * config.SCALE_FACTOR
        self.font_size = config.FONTS['size_body']
        self.bold = True
        
        # Remove default background
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        
        # Draw custom background
        with self.canvas.before:
            self.bg_color = Color(*config.COLORS['surface'])
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8) * config.SCALE_FACTOR]
            )
        
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(is_on=self._update_display)
        
        # Initial display
        self._update_display()
    
    def _update_rect(self, *args):
        """Update background rectangle"""
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def _update_display(self, *args):
        """Update button appearance based on state"""
        if self.is_on:
            self.bg_color.rgba = config.COLORS['success']
            self.text = f"{self.icon_on} {self.actuator_name} ON"
            self.color = config.COLORS['text_primary']
        else:
            self.bg_color.rgba = config.COLORS['surface']
            self.text = f"{self.icon_off} {self.actuator_name} OFF"
            self.color = config.COLORS['text_secondary']
    
    def toggle(self):
        """Toggle button state"""
        self.is_on = not self.is_on
        return self.is_on
    
    def set_state(self, state):
        """Set button state explicitly"""
        self.is_on = state
