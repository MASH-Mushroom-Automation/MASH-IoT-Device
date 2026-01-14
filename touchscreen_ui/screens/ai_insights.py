"""
MASH Touchscreen UI - AI Insights Screen
Display automation reasoning and AI-driven suggestions
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
import config
from widgets.status_bar import StatusBar
from widgets.navigation_sidebar import NavigationSidebar
from datetime import datetime


class InsightCard(BoxLayout):
    """Individual AI insight card"""
    
    def __init__(self, insight_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, None)
        self.padding = dp(20) * config.SCALE_FACTOR
        self.spacing = dp(10) * config.SCALE_FACTOR
        
        # Background
        with self.canvas.before:
            Color(*self._hex_to_rgb('#1E1E1E'))
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_bg, pos=self._update_bg)
        
        # Timestamp
        timestamp_str = insight_data.get('timestamp', datetime.now().isoformat())
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_str = timestamp_str
        
        timestamp_label = Label(
            text=time_str,
            font_size=config.FONTS['size_small'],
            color=config.COLORS['text_secondary'],
            size_hint=(1, None),
            height=dp(20) * config.SCALE_FACTOR,
            halign='left',
            valign='top'
        )
        timestamp_label.bind(size=timestamp_label.setter('text_size'))
        self.add_widget(timestamp_label)
        
        # Mode indicator
        mode = insight_data.get('mode', 'Unknown')
        mode_label = Label(
            text=f'Mode: {mode}',
            font_size=config.FONTS['size_body'],
            color=config.COLORS['primary'],
            size_hint=(1, None),
            height=dp(25) * config.SCALE_FACTOR,
            halign='left',
            valign='top',
            bold=True
        )
        mode_label.bind(size=mode_label.setter('text_size'))
        self.add_widget(mode_label)
        
        # Sensor conditions
        sensor_data = insight_data.get('sensor_data', {})
        if sensor_data:
            conditions_text = (
                f"Conditions: CO₂ {sensor_data.get('co2', '--')} ppm, "
                f"Temp {sensor_data.get('temperature', '--')}°C, "
                f"Humidity {sensor_data.get('humidity', '--')}%"
            )
            conditions_label = Label(
                text=conditions_text,
                font_size=config.FONTS['size_small'],
                color=config.COLORS['text_secondary'],
                size_hint=(1, None),
                height=dp(25) * config.SCALE_FACTOR,
                halign='left',
                valign='top'
            )
            conditions_label.bind(size=conditions_label.setter('text_size'))
            self.add_widget(conditions_label)
        
        # AI Reasoning
        reasoning = insight_data.get('reasoning', [])
        if reasoning:
            reasoning_text = '\n'.join(f"• {r}" for r in reasoning if r)
            
            reasoning_label = Label(
                text=reasoning_text,
                font_size=dp(18) * config.SCALE_FACTOR,  # Larger for readability
                color=config.COLORS['text_primary'],
                size_hint=(1, None),
                halign='left',
                valign='top',
                markup=True
            )
            reasoning_label.bind(
                width=lambda *x: reasoning_label.setter('text_size')(reasoning_label, (reasoning_label.width, None))
            )
            reasoning_label.bind(
                texture_size=reasoning_label.setter('size')
            )
            self.add_widget(reasoning_label)
        
        # Actions taken
        actions = insight_data.get('actions', {})
        if actions:
            actions_text = "Actions: " + ", ".join(
                f"{k.replace('_', ' ').title()}: {'ON' if v else 'OFF'}"
                for k, v in actions.items()
                if k != 'timestamp'
            )
            
            actions_label = Label(
                text=actions_text,
                font_size=config.FONTS['size_small'],
                color=config.COLORS['success'] if any(actions.values()) else config.COLORS['text_secondary'],
                size_hint=(1, None),
                height=dp(25) * config.SCALE_FACTOR,
                halign='left',
                valign='top',
                bold=True
            )
            actions_label.bind(size=actions_label.setter('text_size'))
            self.add_widget(actions_label)
        
        # Calculate total height
        self.height = sum(child.height for child in self.children) + \
                     self.padding[1] * 2 + \
                     self.spacing * (len(self.children) - 1)
    
    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))


class AIInsightsScreen(Screen):
    """AI Insights screen showing automation reasoning and suggestions"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = 'ai_insights'
        
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
        
        # Title
        title = Label(
            text='AI Insights & Automation',
            font_size=config.FONTS['size_title'],
            color=config.COLORS['text_primary'],
            size_hint=(1, None),
            height=dp(40) * config.SCALE_FACTOR,
            bold=True,
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        content.add_widget(title)
        
        # Description
        description = Label(
            text='Real-time AI reasoning and automated control decisions',
            font_size=config.FONTS['size_body'],
            color=config.COLORS['text_secondary'],
            size_hint=(1, None),
            height=dp(30) * config.SCALE_FACTOR,
            halign='left',
            valign='middle'
        )
        description.bind(size=description.setter('text_size'))
        content.add_widget(description)
        
        # Insights scroll view
        scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        # Insights container
        self.insights_container = GridLayout(
            cols=1,
            spacing=dp(15) * config.SCALE_FACTOR,
            size_hint_y=None,
            padding=[0, dp(10) * config.SCALE_FACTOR]
        )
        self.insights_container.bind(minimum_height=self.insights_container.setter('height'))
        
        scroll_view.add_widget(self.insights_container)
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
            self.sidebar.set_active_screen('ai_insights')
        # Load insights immediately
        self._load_insights()
        
        # Schedule periodic updates (every 10 seconds)
        self.update_event = Clock.schedule_interval(
            lambda dt: self._load_insights(),
            10.0
        )
    
    def on_leave(self):
        """Called when leaving screen"""
        # Cancel periodic updates
        if self.update_event:
            self.update_event.cancel()
    
    def _load_insights(self):
        """Load AI insights from API"""
        try:
            # Get automation history from API (last 50 decisions)
            history_data = self.app.api_client.get_automation_history(limit=50)
            
            if history_data:
                self._display_insights(history_data)
            else:
                self._display_no_insights()
                
        except Exception as e:
            print(f"Error loading AI insights: {e}")
            self._display_error()
    
    def _display_insights(self, insights):
        """Display list of AI insights
        
        Args:
            insights: List of automation decision dictionaries
        """
        # Clear existing insights
        self.insights_container.clear_widgets()
        
        if not insights or len(insights) == 0:
            self._display_no_insights()
            return
        
        # Add insight cards (newest first - already reversed from API)
        for insight in insights[:20] if isinstance(insights, list) else []:  # Limit to 20 most recent
            insight_card = InsightCard(insight_data=insight)
            self.insights_container.add_widget(insight_card)
    
    def _display_no_insights(self):
        """Display 'no insights' message"""
        self.insights_container.clear_widgets()
        
        no_insights_label = Label(
            text='No AI insights available yet.\nAutomation will begin recording decisions shortly.',
            font_size=config.FONTS['size_body'],
            color=config.COLORS['text_secondary'],
            size_hint=(1, None),
            height=dp(80) * config.SCALE_FACTOR,
            halign='center'
        )
        no_insights_label.bind(size=no_insights_label.setter('text_size'))
        self.insights_container.add_widget(no_insights_label)
    
    def _display_error(self):
        """Display error message"""
        self.insights_container.clear_widgets()
        
        error_label = Label(
            text='⚠ Unable to load AI insights\nCheck API connection',
            font_size=config.FONTS['size_body'],
            color=config.COLORS['error'],
            size_hint=(1, None),
            height=dp(80) * config.SCALE_FACTOR,
            halign='center'
        )
        error_label.bind(size=error_label.setter('text_size'))
        self.insights_container.add_widget(error_label)
    
    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
