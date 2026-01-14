"""
MASH Touchscreen UI - Setup Wizard
3-step onboarding process for first-time device setup
"""

import os
import json
import qrcode
from io import BytesIO
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image as KivyImage
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
import config


class SetupWizardScreen(Screen):
    """3-step setup wizard for first-time device configuration"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = 'setup_wizard'
        self.current_step = 1
        self.config_file = 'data/device_state.json'
        
        # Create container for wizard steps
        self.container = FloatLayout()
        
        # Background
        with self.container.canvas.before:
            Color(*self._hex_to_rgb('#121212'))
            self.bg_rect = Rectangle(size=self.container.size, pos=self.container.pos)
        
        self.container.bind(size=self._update_bg, pos=self._update_bg)
        
        # Initialize with step 1
        self._show_step_1()
        
        self.add_widget(self.container)
    
    def _show_step_1(self):
        """Step 1: Welcome / IoT Overview"""
        self.container.clear_widgets()
        self.current_step = 1
        
        # Main layout with 60/40 split
        layout = BoxLayout(orientation='vertical', padding=0, spacing=0)
        
        # Top 60% - Interactive content
        top_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.6),
            padding=dp(30) * config.SCALE_FACTOR,
            spacing=dp(20) * config.SCALE_FACTOR
        )
        
        # Welcome header
        header = Label(
            text='Welcome to M.A.S.H. Grow',
            font_size=dp(32) * config.SCALE_FACTOR,
            bold=True,
            color=config.COLORS['primary'],
            size_hint=(1, None),
            height=dp(50) * config.SCALE_FACTOR
        )
        top_section.add_widget(header)
        
        # Description
        description = Label(
            text='Your intelligent partner in sustainable\noyster mushroom cultivation.',
            font_size=config.FONTS['size_body'],
            color=config.COLORS['text_primary'],
            size_hint=(1, None),
            height=dp(80) * config.SCALE_FACTOR,
            halign='center'
        )
        description.bind(size=description.setter('text_size'))
        top_section.add_widget(description)
        
        # Features list
        features_text = (
            "• Automated climate control\n"
            "• Real-time monitoring\n"
            "• AI-driven optimization\n"
            "• Remote access via mobile app"
        )
        features = Label(
            text=features_text,
            font_size=config.FONTS['size_body'],
            color=config.COLORS['text_secondary'],
            size_hint=(1, 1),
            halign='left',
            valign='top'
        )
        features.bind(size=features.setter('text_size'))
        top_section.add_widget(features)
        
        layout.add_widget(top_section)
        
        # Bottom 40% - Logo and Next button (OSK safe zone)
        bottom_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.4),
            padding=dp(30) * config.SCALE_FACTOR,
            spacing=dp(20) * config.SCALE_FACTOR
        )
        
        # Spacer
        bottom_section.add_widget(BoxLayout(size_hint=(1, 0.5)))
        
        # Next button
        next_btn = Button(
            text='Get Started',
            size_hint=(None, None),
            size=(dp(200) * config.SCALE_FACTOR, dp(60) * config.SCALE_FACTOR),
            pos_hint={'center_x': 0.5},
            background_color=self._hex_to_rgb('#4CAF50') + (1,),
            color=(1, 1, 1, 1),
            font_size=config.FONTS['size_body'],
            bold=True
        )
        next_btn.bind(on_press=lambda x: self._show_step_2())
        bottom_section.add_widget(next_btn)
        
        layout.add_widget(bottom_section)
        
        self.container.add_widget(layout)
    
    def _show_step_2(self):
        """Step 2: WiFi Configuration"""
        self.container.clear_widgets()
        self.current_step = 2
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=0, spacing=0)
        
        # Top 60% - WiFi configuration
        top_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.6),
            padding=dp(20) * config.SCALE_FACTOR,
            spacing=dp(15) * config.SCALE_FACTOR
        )
        
        # Header
        header = Label(
            text='Connect to WiFi',
            font_size=dp(28) * config.SCALE_FACTOR,
            bold=True,
            color=config.COLORS['text_primary'],
            size_hint=(1, None),
            height=dp(40) * config.SCALE_FACTOR
        )
        top_section.add_widget(header)
        
        # Subtitle
        subtitle = Label(
            text='Select your 2.4GHz network',
            font_size=config.FONTS['size_body'],
            color=config.COLORS['text_secondary'],
            size_hint=(1, None),
            height=dp(30) * config.SCALE_FACTOR
        )
        top_section.add_widget(subtitle)
        
        # Note: In a full implementation, this would scan for WiFi networks
        # For now, provide a manual entry option
        
        # WiFi SSID input (positioned at top 20% for OSK clearance)
        self.ssid_input = TextInput(
            hint_text='Network Name (SSID)',
            multiline=False,
            size_hint=(1, None),
            height=dp(50) * config.SCALE_FACTOR,
            font_size=config.FONTS['size_body'],
            background_color=self._hex_to_rgb('#1E1E1E') + (1,),
            foreground_color=config.COLORS['text_primary'] + (1,),
            cursor_color=config.COLORS['primary'] + (1,),
            padding=[dp(15) * config.SCALE_FACTOR, dp(12) * config.SCALE_FACTOR]
        )
        top_section.add_widget(self.ssid_input)
        
        # WiFi password input
        self.password_input = TextInput(
            hint_text='Password',
            multiline=False,
            password=True,
            size_hint=(1, None),
            height=dp(50) * config.SCALE_FACTOR,
            font_size=config.FONTS['size_body'],
            background_color=self._hex_to_rgb('#1E1E1E') + (1,),
            foreground_color=config.COLORS['text_primary'] + (1,),
            cursor_color=config.COLORS['primary'] + (1,),
            padding=[dp(15) * config.SCALE_FACTOR, dp(12) * config.SCALE_FACTOR]
        )
        top_section.add_widget(self.password_input)
        
        # Status label
        self.wifi_status_label = Label(
            text='',
            font_size=config.FONTS['size_small'],
            color=config.COLORS['warning'] + (1,),
            size_hint=(1, None),
            height=dp(30) * config.SCALE_FACTOR
        )
        top_section.add_widget(self.wifi_status_label)
        
        # Spacer
        top_section.add_widget(BoxLayout(size_hint=(1, 1)))
        
        layout.add_widget(top_section)
        
        # Bottom 40% - Action buttons
        bottom_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.4),
            padding=dp(30) * config.SCALE_FACTOR,
            spacing=dp(15) * config.SCALE_FACTOR
        )
        
        # Button container
        button_box = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60) * config.SCALE_FACTOR,
            spacing=dp(15) * config.SCALE_FACTOR
        )
        
        # Skip button
        skip_btn = Button(
            text='Skip',
            size_hint=(0.4, 1),
            background_color=self._hex_to_rgb('#333333') + (1,),
            color=config.COLORS['text_secondary'],
            font_size=config.FONTS['size_body']
        )
        skip_btn.bind(on_press=lambda x: self._show_step_3())
        button_box.add_widget(skip_btn)
        
        # Connect button
        connect_btn = Button(
            text='Connect',
            size_hint=(0.6, 1),
            background_color=self._hex_to_rgb('#4CAF50') + (1,),
            color=(1, 1, 1, 1),
            font_size=config.FONTS['size_body'],
            bold=True
        )
        connect_btn.bind(on_press=self._connect_wifi)
        button_box.add_widget(connect_btn)
        
        bottom_section.add_widget(button_box)
        
        layout.add_widget(bottom_section)
        
        self.container.add_widget(layout)
    
    def _connect_wifi(self, instance):
        """Attempt to connect to WiFi"""
        ssid = self.ssid_input.text.strip()
        password = self.password_input.text.strip()
        
        if not ssid:
            self.wifi_status_label.text = '⚠ Please enter network name'
            return
        
        # Show connecting status
        self.wifi_status_label.text = 'Connecting...'
        self.wifi_status_label.color = config.COLORS['info'] + (1,)
        
        # Call API to connect
        try:
            result = self.app.api_client.connect_wifi(ssid, password)
            
            if result and result.get('success'):
                self.wifi_status_label.text = '✓ Connected successfully!'
                self.wifi_status_label.color = config.COLORS['success'] + (1,)
                
                # Update device state
                self._update_device_state({'wifiConfigured': True})
                
                # Move to next step after 1 second
                Clock.schedule_once(lambda dt: self._show_step_3(), 1.5)
            else:
                error_msg = result.get('message', 'Connection failed') if result else 'Connection failed'
                self.wifi_status_label.text = f'✗ {error_msg}'
                self.wifi_status_label.color = config.COLORS['error'] + (1,)
                
        except Exception as e:
            self.wifi_status_label.text = f'✗ Error: {str(e)}'
            self.wifi_status_label.color = config.COLORS['error'] + (1,)
    
    def _show_step_3(self):
        """Step 3: Mobile App Pairing"""
        self.container.clear_widgets()
        self.current_step = 3
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=0, spacing=0)
        
        # Top 60% - QR code and instructions
        top_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.6),
            padding=dp(20) * config.SCALE_FACTOR,
            spacing=dp(15) * config.SCALE_FACTOR
        )
        
        # Header
        header = Label(
            text='Sync with M.A.S.H. Grower',
            font_size=dp(28) * config.SCALE_FACTOR,
            bold=True,
            color=config.COLORS['text_primary'],
            size_hint=(1, None),
            height=dp(40) * config.SCALE_FACTOR
        )
        top_section.add_widget(header)
        
        # Instructions
        instructions = Label(
            text='Scan the QR code below to download\nthe mobile app and link your device.',
            font_size=config.FONTS['size_body'],
            color=config.COLORS['text_secondary'],
            size_hint=(1, None),
            height=dp(60) * config.SCALE_FACTOR,
            halign='center'
        )
        instructions.bind(size=instructions.setter('text_size'))
        top_section.add_widget(instructions)
        
        # QR Code
        qr_container = FloatLayout(size_hint=(1, 1))
        
        try:
            # Generate QR code with device ID and pairing URL
            device_id = self._get_device_id()
            pairing_url = f"https://mash-app.com/pair?device={device_id}"
            
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(pairing_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="white", back_color="black")
            
            # Convert PIL image to Kivy image
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            core_image = CoreImage(BytesIO(buffer.read()), ext='png')
            
            qr_image = KivyImage(
                texture=core_image.texture,
                size_hint=(None, None),
                size=(dp(200) * config.SCALE_FACTOR, dp(200) * config.SCALE_FACTOR),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            qr_container.add_widget(qr_image)
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            # Fallback to text
            qr_fallback = Label(
                text=f'Device ID:\n{self._get_device_id()}',
                font_size=config.FONTS['size_body'],
                color=config.COLORS['text_primary'],
                halign='center',
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            qr_container.add_widget(qr_fallback)
        
        top_section.add_widget(qr_container)
        
        layout.add_widget(top_section)
        
        # Bottom 40% - Complete button
        bottom_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.4),
            padding=dp(30) * config.SCALE_FACTOR,
            spacing=dp(20) * config.SCALE_FACTOR
        )
        
        # Note
        note = Label(
            text='You can also pair your device later\nfrom the Settings menu.',
            font_size=config.FONTS['size_small'],
            color=config.COLORS['text_secondary'],
            size_hint=(1, None),
            height=dp(40) * config.SCALE_FACTOR,
            halign='center'
        )
        note.bind(size=note.setter('text_size'))
        bottom_section.add_widget(note)
        
        # Complete button
        complete_btn = Button(
            text='Complete Setup',
            size_hint=(None, None),
            size=(dp(250) * config.SCALE_FACTOR, dp(60) * config.SCALE_FACTOR),
            pos_hint={'center_x': 0.5},
            background_color=self._hex_to_rgb('#4CAF50') + (1,),
            color=(1, 1, 1, 1),
            font_size=config.FONTS['size_body'],
            bold=True
        )
        complete_btn.bind(on_press=self._complete_setup)
        bottom_section.add_widget(complete_btn)
        
        layout.add_widget(bottom_section)
        
        self.container.add_widget(layout)
    
    def _complete_setup(self, instance):
        """Complete the setup wizard and go to dashboard"""
        # Update device state
        self._update_device_state({
            'isFirstTimeLogin': False,
            'deviceConfigured': True,
            'appPaired': True
        })
        
        print("✓ Setup wizard completed")
        
        # Navigate to dashboard
        self.app.screen_manager.current = 'dashboard'
    
    def _update_device_state(self, updates):
        """Update device state configuration
        
        Args:
            updates: Dictionary of state updates
        """
        try:
            # Load current state
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    state = json.load(f)
            else:
                state = {}
            
            # Apply updates
            state.update(updates)
            
            # Save
            with open(self.config_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            print(f"Error updating device state: {e}")
    
    def _get_device_id(self):
        """Get device ID from config or generate one"""
        try:
            # Try to get from API
            status = self.app.api_client.get_status()
            if status and 'deviceId' in status:
                return status['deviceId']
        except:
            pass
        
        # Fallback to default
        return 'MASH-DEVICE-001'
    
    def _update_bg(self, instance, value):
        """Update background rectangle"""
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
