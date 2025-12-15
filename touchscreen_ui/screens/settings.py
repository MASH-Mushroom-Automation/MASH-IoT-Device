"""
MASH Touchscreen UI - Settings Screen
System settings and information
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
import config
from widgets.status_bar import StatusBar


class SettingsScreen(Screen):
    """Settings and system information screen"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = 'settings'
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        # Status bar
        self.status_bar = StatusBar()
        main_layout.add_widget(self.status_bar)
        
        # Scrollable content
        scroll = ScrollView(size_hint=(1, 1))
        
        content = BoxLayout(
            orientation='vertical',
            padding=dp(20) * config.SCALE_FACTOR,
            spacing=dp(15) * config.SCALE_FACTOR,
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Title
        title = Label(
            text='System Settings',
            font_size=config.FONTS['size_title'],
            size_hint=(1, None),
            height=dp(40) * config.SCALE_FACTOR,
            color=config.COLORS['text_primary'],
            bold=True
        )
        content.add_widget(title)
        
        # Device Information Section
        content.add_widget(self._create_section_title("Device Information"))
        content.add_widget(self._create_info_row("Device ID", config.DEVICE_ID))
        content.add_widget(self._create_info_row("Device Name", config.DEVICE_NAME))
        
        # Display Configuration Section
        content.add_widget(self._create_section_title("Display Configuration"))
        screen_info = config.SCREEN_CONFIGS[config.CURRENT_SCREEN]
        content.add_widget(self._create_info_row("Screen Type", screen_info['name']))
        content.add_widget(self._create_info_row("Resolution", f"{screen_info['width']}x{screen_info['height']}"))
        content.add_widget(self._create_info_row("Scale Factor", f"{screen_info['scale_factor']}x"))
        
        # Backend Configuration Section
        content.add_widget(self._create_section_title("Backend Configuration"))
        content.add_widget(self._create_info_row("API URL", config.API_BASE_URL))
        content.add_widget(self._create_info_row("WebSocket", config.WEBSOCKET_URL))
        
        # Feature Status Section
        content.add_widget(self._create_section_title("Feature Status"))
        content.add_widget(self._create_info_row(
            "MQTT",
            "Enabled" if config.MQTT_ENABLED else "Disabled",
            config.COLORS['success'] if config.MQTT_ENABLED else config.COLORS['text_secondary']
        ))
        content.add_widget(self._create_info_row(
            "Firebase",
            "Enabled" if config.FIREBASE_ENABLED else "Disabled",
            config.COLORS['success'] if config.FIREBASE_ENABLED else config.COLORS['text_secondary']
        ))
        content.add_widget(self._create_info_row(
            "Debug Mode",
            "Enabled" if config.DEBUG else "Disabled",
            config.COLORS['warning'] if config.DEBUG else config.COLORS['text_secondary']
        ))
        
        # System Actions Section
        content.add_widget(self._create_section_title("System Actions"))
        
        actions_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(140) * config.SCALE_FACTOR,
            spacing=dp(10) * config.SCALE_FACTOR
        )
        
        refresh_btn = Button(
            text='Refresh Connection',
            font_size=config.FONTS['size_body'],
            size_hint=(1, None),
            height=dp(50) * config.SCALE_FACTOR,
            background_color=config.COLORS['primary'],
            on_press=self.refresh_connection
        )
        actions_layout.add_widget(refresh_btn)
        
        wifi_btn = Button(
            text='WiFi Setup',
            font_size=config.FONTS['size_body'],
            size_hint=(1, None),
            height=dp(50) * config.SCALE_FACTOR,
            background_color=config.COLORS['info'],
            on_press=lambda x: self.go_to_wifi_setup()
        )
        actions_layout.add_widget(wifi_btn)
        
        content.add_widget(actions_layout)
        
        # Status message
        self.status_message = Label(
            text='',
            font_size=config.FONTS['size_caption'],
            color=config.COLORS['text_secondary'],
            size_hint=(1, None),
            height=dp(30) * config.SCALE_FACTOR
        )
        content.add_widget(self.status_message)
        
        # Navigation buttons
        nav_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60) * config.SCALE_FACTOR,
            spacing=dp(10) * config.SCALE_FACTOR
        )
        
        dashboard_btn = Button(
            text='<< Dashboard',
            font_size=config.FONTS['size_body'],
            background_color=config.COLORS['surface_light'],
            on_press=lambda x: self.go_to_dashboard()
        )
        nav_layout.add_widget(dashboard_btn)
        
        controls_btn = Button(
            text='Controls',
            font_size=config.FONTS['size_body'],
            background_color=config.COLORS['surface_light'],
            on_press=lambda x: self.go_to_controls()
        )
        nav_layout.add_widget(controls_btn)
        
        content.add_widget(nav_layout)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        # Set background
        with main_layout.canvas.before:
            Color(*config.COLORS['background'])
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        main_layout.bind(
            pos=lambda *x: setattr(self.bg_rect, 'pos', main_layout.pos),
            size=lambda *x: setattr(self.bg_rect, 'size', main_layout.size)
        )
        
        self.add_widget(main_layout)
    
    def _create_section_title(self, text):
        """Create a section title label"""
        label = Label(
            text=text,
            font_size=config.FONTS['size_subtitle'],
            size_hint=(1, None),
            height=dp(35) * config.SCALE_FACTOR,
            color=config.COLORS['primary'],
            bold=True,
            halign='left',
            valign='middle'
        )
        label.bind(size=label.setter('text_size'))
        return label
    
    def _create_info_row(self, label_text, value_text, value_color=None):
        """Create an information row"""
        if value_color is None:
            value_color = config.COLORS['text_primary']
        
        row = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(30) * config.SCALE_FACTOR,
            spacing=dp(10) * config.SCALE_FACTOR
        )
        
        label = Label(
            text=f"{label_text}:",
            font_size=config.FONTS['size_caption'],
            color=config.COLORS['text_secondary'],
            size_hint=(0.4, 1),
            halign='left',
            valign='middle'
        )
        label.bind(size=label.setter('text_size'))
        row.add_widget(label)
        
        value = Label(
            text=value_text,
            font_size=config.FONTS['size_caption'],
            color=value_color,
            size_hint=(0.6, 1),
            halign='right',
            valign='middle'
        )
        value.bind(size=value.setter('text_size'))
        row.add_widget(value)
        
        return row
    
    def on_enter(self):
        """Called when screen is displayed"""
        # Update status bar
        self.status_bar.backend_connected = self.app.api_client.health_check()
        self.status_bar.mqtt_connected = self.app.mqtt_client.connected if self.app.mqtt_client else False
        self.status_bar.automation_enabled = self.app.automation_enabled
    
    def refresh_connection(self, instance):
        """Refresh backend connection"""
        self.status_message.text = 'Refreshing connection...'
        
        if self.app.api_client.health_check():
            self.status_message.text = 'SUCCESS: Connection refreshed successfully'
            self.status_bar.backend_connected = True
        else:
            self.status_message.text = 'ERROR: Failed to connect to backend'
            self.status_bar.backend_connected = False
    
    def go_to_wifi_setup(self):
        """Navigate to WiFi setup screen"""
        self.manager.current = 'wifi_setup'
    
    def go_to_dashboard(self):
        """Navigate to dashboard screen"""
        self.manager.current = 'dashboard'
    
    def go_to_controls(self):
        """Navigate to controls screen"""
        self.manager.current = 'controls'
