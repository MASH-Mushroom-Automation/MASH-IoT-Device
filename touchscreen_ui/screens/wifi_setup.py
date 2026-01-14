"""
MASH Touchscreen UI - WiFi Setup Screen
Screen for WiFi network configuration
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
import config
from widgets.status_bar import StatusBar


class WiFiSetupScreen(Screen):
    """WiFi configuration screen"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = 'wifi_setup'
        self.available_networks = []
        
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
        
        # Title
        title = Label(
            text='WiFi Setup',
            font_size=config.FONTS['size_title'],
            size_hint=(1, None),
            height=dp(40) * config.SCALE_FACTOR,
            color=config.COLORS['text_primary'],
            bold=True
        )
        content.add_widget(title)
        
        # Current status
        self.status_label = Label(
            text='Checking WiFi status...',
            font_size=config.FONTS['size_body'],
            size_hint=(1, None),
            height=dp(30) * config.SCALE_FACTOR,
            color=config.COLORS['text_secondary']
        )
        content.add_widget(self.status_label)
        
        # Scan button
        scan_btn = Button(
            text='Scan for Networks',
            font_size=config.FONTS['size_body'],
            size_hint=(1, None),
            height=dp(50) * config.SCALE_FACTOR,
            background_color=config.COLORS['primary'],
            on_press=self.scan_networks
        )
        content.add_widget(scan_btn)
        
        # Networks list
        list_label = Label(
            text='Available Networks:',
            font_size=config.FONTS['size_subtitle'],
            size_hint=(1, None),
            height=dp(30) * config.SCALE_FACTOR,
            color=config.COLORS['text_primary'],
            bold=True,
            halign='left',
            valign='middle'
        )
        list_label.bind(size=list_label.setter('text_size'))
        content.add_widget(list_label)
        
        # Scrollable network list
        scroll = ScrollView(size_hint=(1, 0.4))
        self.network_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5) * config.SCALE_FACTOR
        )
        self.network_list.bind(minimum_height=self.network_list.setter('height'))
        scroll.add_widget(self.network_list)
        content.add_widget(scroll)
        
        # Connection form (top 50% for OSK compatibility)
        form_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.3),
            spacing=dp(10) * config.SCALE_FACTOR
        )
        
        form_label = Label(
            text='Connect to Network:',
            font_size=config.FONTS['size_subtitle'],
            size_hint=(1, None),
            height=dp(30) * config.SCALE_FACTOR,
            color=config.COLORS['text_primary'],
            bold=True,
            halign='left',
            valign='middle'
        )
        form_label.bind(size=form_label.setter('text_size'))
        form_container.add_widget(form_label)
        
        # SSID input
        self.ssid_input = TextInput(
            hint_text='Network SSID',
            font_size=config.FONTS['size_body'],
            size_hint=(1, None),
            height=dp(50) * config.SCALE_FACTOR,
            multiline=False,
            background_color=config.COLORS['surface'],
            foreground_color=config.COLORS['text_primary'],
            padding=[dp(15) * config.SCALE_FACTOR, dp(12) * config.SCALE_FACTOR]
        )
        form_container.add_widget(self.ssid_input)
        
        # Password input
        self.password_input = TextInput(
            hint_text='Password',
            font_size=config.FONTS['size_body'],
            size_hint=(1, None),
            height=dp(50) * config.SCALE_FACTOR,
            multiline=False,
            password=True,
            background_color=config.COLORS['surface'],
            foreground_color=config.COLORS['text_primary'],
            padding=[dp(15) * config.SCALE_FACTOR, dp(12) * config.SCALE_FACTOR]
        )
        form_container.add_widget(self.password_input)
        
        content.add_widget(form_container)
        
        # Button container
        button_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(150) * config.SCALE_FACTOR,
            spacing=dp(10) * config.SCALE_FACTOR
        )
        
        # Connect button
        connect_btn = Button(
            text='Connect',
            font_size=config.FONTS['size_body'],
            size_hint=(1, None),
            height=dp(50) * config.SCALE_FACTOR,
            background_color=config.COLORS['success'],
            on_press=self.connect_to_network
        )
        button_container.add_widget(connect_btn)
        
        # Status message
        self.message_label = Label(
            text='',
            font_size=config.FONTS['size_caption'],
            color=config.COLORS['text_secondary'],
            size_hint=(1, None),
            height=dp(30) * config.SCALE_FACTOR,
            halign='center',
            valign='middle'
        )
        self.message_label.bind(size=self.message_label.setter('text_size'))
        button_container.add_widget(self.message_label)
        
        # Back button
        back_btn = Button(
            text='<< Back to Settings',
            font_size=config.FONTS['size_body'],
            size_hint=(1, None),
            height=dp(50) * config.SCALE_FACTOR,
            background_color=config.COLORS['surface_light'],
            on_press=lambda x: self.go_back()
        )
        button_container.add_widget(back_btn)
        
        content.add_widget(button_container)
        
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
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.check_wifi_status()
        
        # Update status bar
        self.status_bar.backend_connected = self.app.api_client.health_check()
        self.status_bar.mqtt_connected = self.app.mqtt_client.connected if self.app.mqtt_client else False
        self.status_bar.automation_enabled = self.app.automation_enabled
    
    def check_wifi_status(self):
        """Check current WiFi connection status"""
        status = self.app.api_client.get_wifi_status()
        
        if status:
            if status.get('connected'):
                self.status_label.text = f"CONNECTED: {status.get('ssid', 'Unknown')}"
                self.status_label.color = config.COLORS['success']
            else:
                self.status_label.text = "NOT CONNECTED: WiFi disconnected"
                self.status_label.color = config.COLORS['warning']
        else:
            self.status_label.text = "ERROR: Unable to check WiFi status"
            self.status_label.color = config.COLORS['error']
    
    def scan_networks(self, instance):
        """Scan for available WiFi networks"""
        self.message_label.text = 'Scanning for networks...'
        self.message_label.color = config.COLORS['info']
        
        # Clear current list
        self.network_list.clear_widgets()
        
        # Get networks from API
        networks = self.app.api_client.scan_wifi()
        
        if networks:
            self.available_networks = networks
            self.message_label.text = f'Found {len(networks)} network(s)'
            self.message_label.color = config.COLORS['success']
            
            # Display networks
            for network in networks:
                network_btn = Button(
                    text=f"{network.get('ssid', 'Unknown')} ({network.get('signal', 0)}%)",
                    font_size=config.FONTS['size_caption'],
                    size_hint=(1, None),
                    height=dp(40) * config.SCALE_FACTOR,
                    background_color=config.COLORS['surface'],
                    on_press=lambda x, ssid=network.get('ssid'): self.select_network(ssid)
                )
                self.network_list.add_widget(network_btn)
        else:
            self.message_label.text = 'ERROR: No networks found or scan failed'
            self.message_label.color = config.COLORS['error']
    
    def select_network(self, ssid):
        """Select a network from the list"""
        self.ssid_input.text = ssid
        self.message_label.text = f'Selected: {ssid}'
        self.message_label.color = config.COLORS['info']
    
    def connect_to_network(self, instance):
        """Connect to WiFi network"""
        ssid = self.ssid_input.text.strip()
        password = self.password_input.text
        
        if not ssid:
            self.message_label.text = 'WARNING: Please enter network SSID'
            self.message_label.color = config.COLORS['warning']
            return
        
        self.message_label.text = f'Connecting to {ssid}...'
        self.message_label.color = config.COLORS['info']
        
        # Send connection request to API
        result = self.app.api_client.connect_wifi(ssid, password)
        
        if result and result.get('success'):
            self.message_label.text = f'SUCCESS: Connected to {ssid}!'
            self.message_label.color = config.COLORS['success']
            self.password_input.text = ''
            self.check_wifi_status()
        else:
            error_msg = result.get('message', 'Unknown error') if result else 'Connection failed'
            self.message_label.text = f'ERROR: {error_msg}'
            self.message_label.color = config.COLORS['error']
    
    def go_back(self):
        """Navigate back to settings"""
        self.manager.current = 'settings'
