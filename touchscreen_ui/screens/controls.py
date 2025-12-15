"""
MASH Touchscreen UI - Controls Screen
Screen for manual actuator control
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
from widgets.toggle_button import ToggleButton
from widgets.status_bar import StatusBar


class ControlsScreen(Screen):
    """Controls screen for actuator management"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = 'controls'
        
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
            text='Manual Control',
            font_size=config.FONTS['size_title'],
            size_hint=(1, None),
            height=dp(40) * config.SCALE_FACTOR,
            color=config.COLORS['text_primary'],
            bold=True
        )
        content.add_widget(title)
        
        # Automation toggle
        auto_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60) * config.SCALE_FACTOR,
            spacing=dp(10) * config.SCALE_FACTOR,
            padding=[0, dp(10) * config.SCALE_FACTOR]
        )
        
        auto_label = Label(
            text='Automation Mode:',
            font_size=config.FONTS['size_body'],
            color=config.COLORS['text_primary'],
            size_hint=(0.6, 1),
            halign='left',
            valign='middle'
        )
        auto_label.bind(size=auto_label.setter('text_size'))
        auto_layout.add_widget(auto_label)
        
        self.auto_button = Button(
            text='Disabled',
            font_size=config.FONTS['size_body'],
            size_hint=(0.4, 1),
            background_color=config.COLORS['surface'],
            on_press=self.toggle_automation
        )
        auto_layout.add_widget(self.auto_button)
        
        content.add_widget(auto_layout)
        
        # Actuator controls grid
        controls_grid = GridLayout(
            cols=2,
            spacing=dp(15) * config.SCALE_FACTOR,
            size_hint=(1, None),
            height=dp(280) * config.SCALE_FACTOR,
            padding=[0, dp(10) * config.SCALE_FACTOR]
        )
        
        # Blower Fan toggle
        self.blower_toggle = ToggleButton(
            actuator_name="Blower Fan",
            icon_on="[ON]",
            icon_off="[OFF]",
            on_press=lambda x: self.control_actuator('blower_fan', self.blower_toggle.toggle())
        )
        controls_grid.add_widget(self.blower_toggle)
        
        # Exhaust Fan toggle
        self.exhaust_toggle = ToggleButton(
            actuator_name="Exhaust Fan",
            icon_on="[ON]",
            icon_off="[OFF]",
            on_press=lambda x: self.control_actuator('exhaust_fan', self.exhaust_toggle.toggle())
        )
        controls_grid.add_widget(self.exhaust_toggle)
        
        # Humidifier toggle
        self.humidifier_toggle = ToggleButton(
            actuator_name="Humidifier",
            icon_on="[ON]",
            icon_off="[OFF]",
            on_press=lambda x: self.control_actuator('humidifier', self.humidifier_toggle.toggle())
        )
        controls_grid.add_widget(self.humidifier_toggle)
        
        # LED Lights toggle
        self.lights_toggle = ToggleButton(
            actuator_name="LED Lights",
            icon_on="[ON]",
            icon_off="[OFF]",
            on_press=lambda x: self.control_actuator('led_lights', self.lights_toggle.toggle())
        )
        controls_grid.add_widget(self.lights_toggle)
        
        content.add_widget(controls_grid)
        
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
        
        back_btn = Button(
            text='<< Dashboard',
            font_size=config.FONTS['size_body'],
            background_color=config.COLORS['surface_light'],
            on_press=lambda x: self.go_to_dashboard()
        )
        nav_layout.add_widget(back_btn)
        
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
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.update_display()
        self.update_event = Clock.schedule_interval(lambda dt: self.update_display(), 2)
    
    def on_leave(self):
        """Called when leaving screen"""
        if hasattr(self, 'update_event'):
            self.update_event.cancel()
    
    def update_display(self):
        """Update actuator states and automation status"""
        # Update actuator toggles from app state
        actuator_states = self.app.actuator_states
        
        if actuator_states:
            self.blower_toggle.set_state(actuator_states.get('blower_fan', False))
            self.exhaust_toggle.set_state(actuator_states.get('exhaust_fan', False))
            self.humidifier_toggle.set_state(actuator_states.get('humidifier', False))
            self.lights_toggle.set_state(actuator_states.get('led_lights', False))
        
        # Update automation button
        if self.app.automation_enabled:
            self.auto_button.text = 'ENABLED'
            self.auto_button.background_color = config.COLORS['success']
            self.status_message.text = 'Automation is controlling actuators'
            # Disable manual controls when automation is on
            self.blower_toggle.disabled = True
            self.exhaust_toggle.disabled = True
            self.humidifier_toggle.disabled = True
            self.lights_toggle.disabled = True
        else:
            self.auto_button.text = 'DISABLED'
            self.auto_button.background_color = config.COLORS['surface']
            self.status_message.text = 'Manual control enabled'
            # Enable manual controls when automation is off
            self.blower_toggle.disabled = False
            self.exhaust_toggle.disabled = False
            self.humidifier_toggle.disabled = False
            self.lights_toggle.disabled = False
        
        # Update status bar
        self.status_bar.backend_connected = self.app.api_client.health_check()
        self.status_bar.mqtt_connected = self.app.mqtt_client.connected if self.app.mqtt_client else False
        self.status_bar.automation_enabled = self.app.automation_enabled
    
    def toggle_automation(self, instance):
        """Toggle automation mode"""
        if self.app.automation_enabled:
            # Disable automation
            result = self.app.api_client.disable_automation()
            if result:
                self.app.automation_enabled = False
                self.status_message.text = 'SUCCESS: Automation disabled - manual control active'
        else:
            # Enable automation
            result = self.app.api_client.enable_automation()
            if result:
                self.app.automation_enabled = True
                self.status_message.text = 'SUCCESS: Automation enabled - system will auto-control'
        
        self.update_display()
    
    def control_actuator(self, actuator_name, state):
        """Control an actuator"""
        if self.app.automation_enabled:
            self.status_message.text = 'WARNING: Disable automation first to use manual control'
            return
        
        # Send control command to API
        result = self.app.api_client.control_actuator(actuator_name, state)
        
        if result:
            self.app.actuator_states[actuator_name] = state
            self.status_message.text = f'SUCCESS: {actuator_name.replace("_", " ").title()} {"ON" if state else "OFF"}'
        else:
            self.status_message.text = f'ERROR: Failed to control {actuator_name.replace("_", " ")}'
            # Revert toggle state
            if actuator_name == 'blower_fan':
                self.blower_toggle.set_state(not state)
            elif actuator_name == 'exhaust_fan':
                self.exhaust_toggle.set_state(not state)
            elif actuator_name == 'humidifier':
                self.humidifier_toggle.set_state(not state)
            elif actuator_name == 'led_lights':
                self.lights_toggle.set_state(not state)
    
    def go_to_dashboard(self):
        """Navigate to dashboard screen"""
        self.manager.current = 'dashboard'
    
    def go_to_settings(self):
        """Navigate to settings screen"""
        self.manager.current = 'settings'
