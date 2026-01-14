"""
MASH Touchscreen UI - Alerts Screen
Display system alerts and logs with color-coded severity
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
import config
from widgets.status_bar import StatusBar
from widgets.navigation_sidebar import NavigationSidebar
from datetime import datetime


class AlertCard(BoxLayout):
    """Individual alert card with severity color coding"""
    
    def __init__(self, alert_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.height = dp(80) * config.SCALE_FACTOR
        self.padding = dp(15) * config.SCALE_FACTOR
        self.spacing = dp(10) * config.SCALE_FACTOR
        
        # Determine severity color
        severity = alert_data.get('severity', 'info').lower()
        if severity in ['critical', 'error']:
            bg_color = self._hex_to_rgb('#F44336')  # Red
        elif severity == 'warning':
            bg_color = self._hex_to_rgb('#FFC107')  # Amber
        else:  # info, success
            bg_color = self._hex_to_rgb('#4CAF50')  # Green
        
        # Background
        with self.canvas.before:
            Color(*bg_color, 0.2)  # 20% opacity
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        # Left border indicator
        border_box = BoxLayout(
            size_hint=(None, 1),
            width=dp(5) * config.SCALE_FACTOR
        )
        with border_box.canvas.before:
            Color(*bg_color, 1)
            self.border_rect = Rectangle(size=border_box.size, pos=border_box.pos)
        
        border_box.bind(size=self._update_border, pos=self._update_border)
        self.add_widget(border_box)
        
        # Content
        content_layout = BoxLayout(orientation='vertical', spacing=dp(5) * config.SCALE_FACTOR)
        
        # Alert message
        message = Label(
            text=alert_data.get('message', 'No message'),
            font_size=config.FONTS['size_body'],
            color=config.COLORS['text_primary'],
            halign='left',
            valign='top',
            text_size=(None, None)
        )
        message.bind(size=message.setter('text_size'))
        content_layout.add_widget(message)
        
        # Timestamp
        timestamp_str = alert_data.get('timestamp', datetime.now().isoformat())
        try:
            # Parse ISO format timestamp
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            time_label_text = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_label_text = timestamp_str
        
        timestamp = Label(
            text=time_label_text,
            font_size=config.FONTS['size_small'],
            color=config.COLORS['text_secondary'],
            halign='left',
            valign='bottom',
            size_hint=(1, None),
            height=dp(20) * config.SCALE_FACTOR
        )
        timestamp.bind(size=timestamp.setter('text_size'))
        content_layout.add_widget(timestamp)
        
        self.add_widget(content_layout)
    
    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    def _update_border(self, instance, value):
        self.border_rect.size = instance.size
        self.border_rect.pos = instance.pos
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))


class AlertsScreen(Screen):
    """Alerts screen showing system notifications and logs"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = 'alerts'
        
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
        
        root_layout.add_widget(main_layout)
        
        # Content area
        content = BoxLayout(
            orientation='vertical',
            padding=dp(20) * config.SCALE_FACTOR,
            spacing=dp(15) * config.SCALE_FACTOR
        )
        
        # Header with clear button
        header_box = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(50) * config.SCALE_FACTOR,
            spacing=dp(10) * config.SCALE_FACTOR
        )
        
        # Title
        title = Label(
            text='Alerts & Notifications',
            font_size=config.FONTS['size_title'],
            color=config.COLORS['text_primary'],
            bold=True,
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header_box.add_widget(title)
        
        # Clear logs button
        clear_btn = Button(
            text='Clear Logs',
            size_hint=(None, 1),
            width=dp(120) * config.SCALE_FACTOR,
            background_color=self._hex_to_rgb('#333333') + (1,),
            color=config.COLORS['text_secondary'],
            font_size=config.FONTS['size_small']
        )
        clear_btn.bind(on_press=self._clear_logs)
        header_box.add_widget(clear_btn)
        
        content.add_widget(header_box)
        
        # Alerts scroll view
        scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        # Alerts container
        self.alerts_container = GridLayout(
            cols=1,
            spacing=dp(10) * config.SCALE_FACTOR,
            size_hint_y=None,
            padding=[0, dp(10) * config.SCALE_FACTOR]
        )
        self.alerts_container.bind(minimum_height=self.alerts_container.setter('height'))
        
        scroll_view.add_widget(self.alerts_container)
        content.add_widget(scroll_view)
        
        main_layout.add_widget(content)
        
        # Background
        with main_layout.canvas.before:
            Color(*self._hex_to_rgb('#121212'))
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        main_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        self.add_widget(root_layout)
        
        # Schedule periodic updates
        self.update_event = None
    
    def on_enter(self):
        """Called when screen is displayed"""
        # Set sidebar active state
        if hasattr(self, 'sidebar'):
            self.sidebar.set_active_screen('alerts')
        # Load alerts immediately
        self._load_alerts()
        
        # Schedule periodic updates (every 5 seconds)
        self.update_event = Clock.schedule_interval(
            lambda dt: self._load_alerts(),
            5.0
        )
    
    def on_leave(self):
        """Called when leaving screen"""
        # Cancel periodic updates
        if self.update_event:
            self.update_event.cancel()
    
    def _load_alerts(self):
        """Load alerts from API"""
        try:
            # Get alerts from API (last 24 hours, max 50)
            alerts_data = self.app.api_client.get_alert_logs(hours=24, limit=50)
            
            if alerts_data:
                self._display_alerts(alerts_data)
            else:
                # Show "no alerts" message
                self._display_no_alerts()
                
        except Exception as e:
            print(f"Error loading alerts: {e}")
            self._display_error()
    
    def _display_alerts(self, alerts):
        """Display list of alerts
        
        Args:
            alerts: List of alert dictionaries
        """
        # Clear existing alerts
        self.alerts_container.clear_widgets()
        
        if not alerts or len(alerts) == 0:
            self._display_no_alerts()
            return
        
        # Add alert cards (newest first)
        for alert in reversed(alerts) if isinstance(alerts, list) else []:
            alert_card = AlertCard(alert_data=alert)
            self.alerts_container.add_widget(alert_card)
    
    def _display_no_alerts(self):
        """Display 'no alerts' message"""
        self.alerts_container.clear_widgets()
        
        no_alerts_label = Label(
            text='No alerts or notifications',
            font_size=config.FONTS['size_body'],
            color=config.COLORS['text_secondary'],
            size_hint=(1, None),
            height=dp(60) * config.SCALE_FACTOR
        )
        self.alerts_container.add_widget(no_alerts_label)
    
    def _display_error(self):
        """Display error message"""
        self.alerts_container.clear_widgets()
        
        error_label = Label(
            text='⚠ Unable to load alerts\nCheck API connection',
            font_size=config.FONTS['size_body'],
            color=config.COLORS['error'] + (1,),
            size_hint=(1, None),
            height=dp(80) * config.SCALE_FACTOR,
            halign='center'
        )
        error_label.bind(size=error_label.setter('text_size'))
        self.alerts_container.add_widget(error_label)
    
    def _clear_logs(self, instance):
        """Clear all alerts (would need backend API support)"""
        # For now, just refresh the view
        # In production, this would call an API endpoint to clear logs
        print("Clear logs requested")
        self.alerts_container.clear_widgets()
        self._display_no_alerts()
    
    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
