"""
MASH Touchscreen UI - Navigation Sidebar
Global navigation bar with icon-based menu
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
import config


class NavigationButton(Button):
    """Navigation button with icon and active state"""
    
    def __init__(self, icon_text, screen_name, **kwargs):
        super().__init__(**kwargs)
        self.icon_text = icon_text
        self.screen_name = screen_name
        self.is_active = False
        
        self.size_hint = (1, None)
        self.height = dp(80) * config.SCALE_FACTOR
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)  # Transparent
        
        # Icon/text
        self.text = icon_text
        self.font_size = dp(20) * config.SCALE_FACTOR
        self.color = config.COLORS['text_secondary']
        self.bold = False
        
        # Active indicator
        with self.canvas.before:
            self.active_color = Color(0, 0, 0, 0)
            self.active_rect = Rectangle(size=(dp(4) * config.SCALE_FACTOR, 0), pos=self.pos)
        
        self.bind(size=self._update_active_rect, pos=self._update_active_rect)
    
    def set_active(self, active):
        """Set active state"""
        self.is_active = active
        if active:
            # Active state - primary color
            primary = config.COLORS['primary']
            self.color = primary
            self.bold = True
            self.active_color.rgba = primary
            self.active_rect.size = (dp(4) * config.SCALE_FACTOR, self.height)
        else:
            # Inactive state - secondary color
            self.color = config.COLORS['text_secondary']
            self.bold = False
            self.active_color.rgba = (0, 0, 0, 0)
            self.active_rect.size = (dp(4) * config.SCALE_FACTOR, 0)
    
    def _update_active_rect(self, *args):
        """Update active indicator position"""
        if self.is_active:
            self.active_rect.pos = self.pos
            self.active_rect.size = (dp(4) * config.SCALE_FACTOR, self.height)


class NavigationSidebar(BoxLayout):
    """Global navigation sidebar with icon buttons"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        
        self.orientation = 'vertical'
        self.size_hint = (None, 1)
        self.width = dp(80) * config.SCALE_FACTOR
        self.spacing = 0
        self.padding = 0
        
        # Background
        with self.canvas.before:
            Color(*self._hex_to_rgb('#1E1E1E'))
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        # Navigation buttons
        self.nav_buttons = {}
        
        # Define navigation items (icon, screen_name, label)
        nav_items = [
            ('🏠', 'dashboard', 'Home'),
            ('🔔', 'alerts', 'Alerts'),
            ('🧠', 'ai_insights', 'AI'),
            ('🎛️', 'controls', 'Controls'),
            ('❓', 'help', 'Help'),
            ('⚙️', 'settings', 'Settings')
        ]
        
        for icon, screen_name, label in nav_items:
            btn = NavigationButton(icon, screen_name)
            btn.bind(on_press=self._on_nav_button_press)
            self.add_widget(btn)
            self.nav_buttons[screen_name] = btn
        
        # Spacer at bottom
        self.add_widget(BoxLayout(size_hint=(1, 1)))
    
    def _on_nav_button_press(self, button):
        """Handle navigation button press"""
        # Navigate to screen
        if hasattr(self.app, 'screen_manager'):
            self.app.screen_manager.current = button.screen_name
            self.set_active_screen(button.screen_name)
    
    def set_active_screen(self, screen_name):
        """Set active screen indicator"""
        for name, btn in self.nav_buttons.items():
            btn.set_active(name == screen_name)
    
    def _update_bg(self, instance, value):
        """Update background rectangle"""
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
