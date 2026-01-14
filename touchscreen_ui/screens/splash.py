"""
MASH Touchscreen UI - Splash Screen
Boot screen with logo animation and initialization routing
"""

import os
import json
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
import config


class SplashScreen(Screen):
    """Splash screen shown during app initialization"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = 'splash'
        self.config_file = 'data/device_state.json'
        
        # Main layout
        layout = FloatLayout()
        
        # Background color (#121212)
        with layout.canvas.before:
            Color(*self._hex_to_rgb('#121212'))
            self.bg_rect = Rectangle(size=layout.size, pos=layout.pos)
        
        layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # M.A.S.H. Logo (centered)
        # First check for logo in assets folder, fallback to text
        logo_path = 'assets/images/mash_logo.png'
        
        if os.path.exists(logo_path):
            self.logo = Image(
                source=logo_path,
                size_hint=(None, None),
                size=(dp(200) * config.SCALE_FACTOR, dp(200) * config.SCALE_FACTOR),
                pos_hint={'center_x': 0.5, 'center_y': 0.55},
                opacity=0  # Start invisible for fade animation
            )
        else:
            # Fallback to text logo
            self.logo = Label(
                text='M.A.S.H.',
                font_size=dp(48) * config.SCALE_FACTOR,
                bold=True,
                color=(1, 1, 1, 0),  # White, start invisible
                size_hint=(None, None),
                size=(dp(300) * config.SCALE_FACTOR, dp(100) * config.SCALE_FACTOR),
                pos_hint={'center_x': 0.5, 'center_y': 0.55}
            )
        
        layout.add_widget(self.logo)
        
        # Subtitle
        self.subtitle = Label(
            text='Mushroom Automation System',
            font_size=config.FONTS['size_body'],
            color=(0.68, 0.68, 0.71, 0),  # Start invisible (RGBA)
            size_hint=(None, None),
            size=(dp(400) * config.SCALE_FACTOR, dp(30) * config.SCALE_FACTOR),
            pos_hint={'center_x': 0.5, 'center_y': 0.4}
        )
        layout.add_widget(self.subtitle)
        
        # Loading text (bottom center)
        self.loading_label = Label(
            text='Loading...',
            font_size=config.FONTS['size_small'],
            color=(0.68, 0.68, 0.71, 0),  # Start invisible (RGBA)
            size_hint=(None, None),
            size=(dp(200) * config.SCALE_FACTOR, dp(30) * config.SCALE_FACTOR),
            pos_hint={'center_x': 0.5, 'center_y': 0.15}
        )
        layout.add_widget(self.loading_label)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Called when screen is displayed"""
        # Start fade-in animation
        self._animate_logo()
        
        # Schedule initialization checks
        Clock.schedule_once(self._perform_initialization, 1.5)
    
    def _animate_logo(self):
        """Fade in logo and text"""
        # Fade in logo over 1 second
        if isinstance(self.logo, Image):
            anim_logo = Animation(opacity=1, duration=1.0)
        else:
            # For Label logo, animate color alpha
            anim_logo = Animation(color=(1, 1, 1, 1), duration=1.0)
        
        anim_logo.start(self.logo)
        
        # Fade in subtitle slightly after (0.5s delay)
        Clock.schedule_once(lambda dt: self._fade_in_text(self.subtitle), 0.5)
        
        # Fade in loading text (1.0s delay)
        Clock.schedule_once(lambda dt: self._fade_in_text(self.loading_label), 1.0)
    
    def _fade_in_text(self, widget):
        """Fade in text widget"""
        current_color = list(widget.color)
        current_color[3] = 1  # Set alpha to 1
        anim = Animation(color=tuple(current_color), duration=0.5)
        anim.start(widget)
    
    def _perform_initialization(self, dt):
        """Check system state and route to appropriate screen"""
        try:
            # Check if this is first time login
            is_first_time = self._check_first_time_login()
            
            # Check if API server is reachable
            self._check_api_connectivity()
            
            # Route to appropriate screen after 0.5s delay
            if is_first_time:
                Clock.schedule_once(lambda dt: self._go_to_setup_wizard(), 0.5)
            else:
                Clock.schedule_once(lambda dt: self._go_to_dashboard(), 0.5)
                
        except Exception as e:
            print(f"Initialization error: {e}")
            # Fallback to dashboard on error
            Clock.schedule_once(lambda dt: self._go_to_dashboard(), 0.5)
    
    def _check_first_time_login(self):
        """Check if this is the first time the device is being set up
        
        Returns:
            bool: True if first time login, False otherwise
        """
        try:
            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)
            
            # Check for config file
            if not os.path.exists(self.config_file):
                # First time - create config file
                self._create_device_state_config(is_first_time=True)
                return True
            
            # Load config file
            with open(self.config_file, 'r') as f:
                state = json.load(f)
            
            # Check isFirstTimeLogin flag
            return state.get('isFirstTimeLogin', True)
            
        except Exception as e:
            print(f"Error checking first time login: {e}")
            # Assume not first time if there's an error
            return False
    
    def _create_device_state_config(self, is_first_time=True):
        """Create device state configuration file
        
        Args:
            is_first_time: Whether this is first time setup
        """
        state = {
            'isFirstTimeLogin': is_first_time,
            'isTutorialDone': False,
            'deviceConfigured': not is_first_time,
            'lastBootTime': None
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _check_api_connectivity(self):
        """Check if Flask API server is reachable"""
        try:
            status = self.app.api_client.get_status()
            if status:
                print("✓ API server connected")
                return True
        except Exception as e:
            print(f"⚠ API server not reachable: {e}")
        
        return False
    
    def _go_to_setup_wizard(self):
        """Navigate to setup wizard"""
        print("→ Routing to Setup Wizard (First Time Setup)")
        # Check if setup wizard exists
        if self.app.screen_manager.has_screen('setup_wizard'):
            self.app.screen_manager.current = 'setup_wizard'
        else:
            # Fallback to WiFi setup if wizard not implemented yet
            print("⚠ Setup wizard not implemented, using WiFi setup")
            self.app.screen_manager.current = 'wifi_setup'
    
    def _go_to_dashboard(self):
        """Navigate to dashboard"""
        print("→ Routing to Dashboard")
        self.app.screen_manager.current = 'dashboard'
    
    def _update_bg(self, instance, value):
        """Update background rectangle size"""
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple
        
        Args:
            hex_color: Hex color string (e.g., '#121212')
            
        Returns:
            tuple: (r, g, b) values from 0-1
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
