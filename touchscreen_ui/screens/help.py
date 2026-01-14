"""
MASH Touchscreen UI - Help & Maintenance Screen
Tutorials, maintenance protocols, and troubleshooting guides
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
import config
from widgets.status_bar import StatusBar
from widgets.navigation_sidebar import NavigationSidebar


class HelpScreen(Screen):
    """Help & Maintenance screen with tutorials and troubleshooting"""
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.name = 'help'
        
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
            text='Help & Maintenance',
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
        
        # Tabbed panel
        tab_panel = TabbedPanel(
            do_default_tab=False,
            tab_width=dp(140) * config.SCALE_FACTOR,
            tab_height=dp(50) * config.SCALE_FACTOR
        )
        
        # Tab colors
        tab_panel.background_color = self._hex_to_rgb('#1E1E1E') + (1,)
        
        # Tutorials tab
        tutorials_tab = TabbedPanelItem(text='Tutorials')
        tutorials_tab.add_widget(self._create_tutorials_content())
        tab_panel.add_widget(tutorials_tab)
        
        # Maintenance tab
        maintenance_tab = TabbedPanelItem(text='Maintenance')
        maintenance_tab.add_widget(self._create_maintenance_content())
        tab_panel.add_widget(maintenance_tab)
        
        # Support tab
        support_tab = TabbedPanelItem(text='Support')
        support_tab.add_widget(self._create_support_content())
        tab_panel.add_widget(support_tab)
        
        content.add_widget(tab_panel)
        main_layout.add_widget(content)
        
        # Background
        with main_layout.canvas.before:
            Color(*self._hex_to_rgb('#121212'))
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        main_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        self.add_widget(root_layout)
    
    def on_enter(self):
        """Called when screen is displayed"""
        # Set sidebar active state
        if hasattr(self, 'sidebar'):
            self.sidebar.set_active_screen('help')
    
    def _create_tutorials_content(self):
        """Create tutorials tab content"""
        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=True)
        
        content = GridLayout(
            cols=1,
            spacing=dp(20) * config.SCALE_FACTOR,
            size_hint_y=None,
            padding=dp(15) * config.SCALE_FACTOR
        )
        content.bind(minimum_height=content.setter('height'))
        
        tutorials = [
            {
                'title': '🍄 Starting a New Batch',
                'steps': [
                    '1. Fully harvest the previous batch and remove all spent substrate.',
                    '2. Clean the chamber walls and floor with 70% isopropyl alcohol.',
                    '3. Load new sterilized fruiting bags (ensure they are cool to the touch).',
                    '4. Reset the "Batch Start" date in your Mobile App or Device Settings to restart AI growth tracking.'
                ]
            },
            {
                'title': '🎛️ Calibrating Manual Controls',
                'steps': [
                    '• If the chamber feels too dry despite a 90% reading, manually pulse the Humidifier for 5 minutes.',
                    '• If the chamber smells "stuffy," run the Exhaust Fan for 2 minutes regardless of CO2 readings.',
                    '• Monitor sensor readings after manual adjustments to verify effectiveness.'
                ]
            },
            {
                'title': '📍 Device Relocation',
                'steps': [
                    '• Always shutdown via Settings before unplugging.',
                    '• Keep the device away from direct sunlight to prevent false high-temperature readings.',
                    '• Allow 10 minutes after relocation for sensors to stabilize.',
                    '• Recalibrate if readings seem inconsistent.'
                ]
            },
            {
                'title': '🔬 The Science: CO2 Threshold',
                'steps': [
                    '• During the "Pinning" stage, CO2 must stay below 800ppm.',
                    '• High CO2 at this stage results in "Long Stems" and "Small Caps."',
                    '• The automation system will actively manage CO2 during critical growth phases.',
                    '• Monitor AI Insights for CO2-related decisions.'
                ]
            },
            {
                'title': '❄️ Evaporative Cooling',
                'steps': [
                    '• If temperature is too high, pulse the humidifier while running the exhaust fan.',
                    '• This can help drop temperature by 1-2°C through evaporation.',
                    '• Monitor both temperature and humidity to avoid over-humidification.',
                    '• Works best in low-humidity environments.'
                ]
            },
            {
                'title': '🌑 Darkness Period',
                'steps': [
                    '• White Oyster mycelium colonizes faster in total darkness.',
                    '• Minimize opening the chamber during the first 7 days.',
                    '• The LED lights will automatically manage day/night cycles.',
                    '• Sudden light exposure can stress young mycelium.'
                ]
            }
        ]
        
        for tutorial in tutorials:
            content.add_widget(self._create_section(tutorial['title'], tutorial['steps']))
        
        scroll_view.add_widget(content)
        return scroll_view
    
    def _create_maintenance_content(self):
        """Create maintenance tab content"""
        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=True)
        
        content = GridLayout(
            cols=1,
            spacing=dp(20) * config.SCALE_FACTOR,
            size_hint_y=None,
            padding=dp(15) * config.SCALE_FACTOR
        )
        content.bind(minimum_height=content.setter('height'))
        
        protocols = [
            {
                'title': '💧 Humidifier System',
                'steps': [
                    '⚠️ Use ONLY distilled or purified water to prevent mineral buildup on the ultrasonic mist maker.',
                    '• Clean the water tank weekly with a mild vinegar solution to prevent bacterial slime.',
                    '• Check water level daily - low water can damage the ultrasonic disc.',
                    '• Replace the atomizer disc every 3-6 months depending on usage.',
                    '• If mist production is weak, check for mineral deposits on the disc.'
                ]
            },
            {
                'title': '🌀 Air Filtration & Fans',
                'steps': [
                    '• Inspect the Blower Fan intake daily for dust or stray mushroom spores.',
                    '• Vacuum or replace the intake filter every 30 days to ensure high-volume air exchange.',
                    '• Clean fan blades monthly to maintain airflow efficiency.',
                    '• Listen for unusual noises indicating bearing wear.',
                    '• Exhaust fan should have a slight negative pressure feel.'
                ]
            },
            {
                'title': '🔬 Sensor Hygiene (SCD41)',
                'steps': [
                    '⚠️ DO NOT use liquids on sensors!',
                    '• Use a camera blower or a very soft, dry brush to remove dust from the vents.',
                    '• Ensure the sensor module is positioned at center-height of the chamber for the most accurate average reading.',
                    '• Check sensor readings against known reference (outdoor air ~400ppm CO2).',
                    '• Recalibrate if readings drift over time.'
                ]
            },
            {
                'title': '💡 LED Light Maintenance',
                'steps': [
                    '• Check LED strip connections monthly for corrosion.',
                    '• Clean LED surface with dry cloth to maintain light output.',
                    '• Verify timer settings match growth stage requirements.',
                    '• Replace LED strips if brightness decreases significantly (typically after 3-5 years).'
                ]
            },
            {
                'title': '🔌 Electrical Safety',
                'steps': [
                    '• Inspect all cables for damage or wear monthly.',
                    '• Keep all electrical connections away from water sources.',
                    '• Use GFCI-protected outlets in high-humidity environments.',
                    '• Never modify relay wiring while system is powered on.',
                    '• Check relay switching sounds - clicking indicates normal operation.'
                ]
            }
        ]
        
        for protocol in protocols:
            content.add_widget(self._create_section(protocol['title'], protocol['steps']))
        
        scroll_view.add_widget(content)
        return scroll_view
    
    def _create_support_content(self):
        """Create support tab content"""
        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=True)
        
        content = GridLayout(
            cols=1,
            spacing=dp(20) * config.SCALE_FACTOR,
            size_hint_y=None,
            padding=dp(15) * config.SCALE_FACTOR
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Troubleshooting section
        troubleshooting = {
            'title': '⚠️ Troubleshooting & Error Codes',
            'steps': [
                'Code 404 (No Sensor): The Raspberry Pi cannot detect the I2C bus. Check the 4-pin connector on the M5Stack sensor unit.',
                'Code 503 (Cloud Offline): The device is connected to WiFi but cannot reach the backend server. Check your ISP or server status.',
                'Laggy Interface: If the screen becomes slow, clear the "Alerts" history in Settings to free up local SQLite memory.',
                'Unstable Humidity: Check if the Humidifier "wicks" or atomizing sheet is clogged. Replace the atomizer disc if mist production is weak.',
                'High CO2 Readings: Verify exhaust fan is working. Check for chamber leaks. Increase ventilation cycle frequency.',
                'Temperature Fluctuations: Check sensor placement. Avoid direct sunlight. Ensure adequate air circulation.',
                'WiFi Connection Loss: Check router settings. Verify 2.4GHz band is enabled. Re-run WiFi setup if needed.'
            ]
        }
        content.add_widget(self._create_section(troubleshooting['title'], troubleshooting['steps']))
        
        # Contact section
        contact_box = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            spacing=dp(10) * config.SCALE_FACTOR,
            padding=dp(15) * config.SCALE_FACTOR
        )
        
        # Set height based on content
        contact_box.height = dp(200) * config.SCALE_FACTOR
        
        # Background
        with contact_box.canvas.before:
            Color(*self._hex_to_rgb('#1E1E1E'))
            self.contact_rect = Rectangle(size=contact_box.size, pos=contact_box.pos)
        
        contact_box.bind(size=lambda i, v: setattr(self.contact_rect, 'size', i.size))
        contact_box.bind(pos=lambda i, v: setattr(self.contact_rect, 'pos', i.pos))
        
        contact_title = Label(
            text='📞 Support & Documentation',
            font_size=config.FONTS['size_body'],
            color=config.COLORS['primary'],
            size_hint=(1, None),
            height=dp(30) * config.SCALE_FACTOR,
            bold=True,
            halign='left'
        )
        contact_title.bind(size=contact_title.setter('text_size'))
        contact_box.add_widget(contact_title)
        
        contact_text = Label(
            text=(
                'Research Team: UCC Caloocan BSCS 4B - Project M.A.S.H.\n\n'
                'For technical support, firmware bug reports, or questions:\n'
                '• Check the GitHub repository documentation\n'
                '• Visit the project Discord/support channel\n'
                '• Scan QR code in Settings > About for full documentation'
            ),
            font_size=config.FONTS['size_small'],
            color=config.COLORS['text_secondary'],
            size_hint=(1, 1),
            halign='left',
            valign='top'
        )
        contact_text.bind(size=contact_text.setter('text_size'))
        contact_box.add_widget(contact_text)
        
        content.add_widget(contact_box)
        
        scroll_view.add_widget(content)
        return scroll_view
    
    def _create_section(self, title, steps):
        """Create a section with title and steps"""
        section = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            spacing=dp(10) * config.SCALE_FACTOR,
            padding=dp(15) * config.SCALE_FACTOR
        )
        
        # Background
        with section.canvas.before:
            Color(*self._hex_to_rgb('#1E1E1E'))
            section_rect = Rectangle(size=section.size, pos=section.pos)
        
        section.bind(size=lambda i, v: setattr(section_rect, 'size', i.size))
        section.bind(pos=lambda i, v: setattr(section_rect, 'pos', i.pos))
        
        # Title
        title_label = Label(
            text=title,
            font_size=config.FONTS['size_body'],
            color=config.COLORS['primary'],
            size_hint=(1, None),
            height=dp(30) * config.SCALE_FACTOR,
            bold=True,
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        section.add_widget(title_label)
        
        # Steps
        steps_text = '\n'.join(steps)
        steps_label = Label(
            text=steps_text,
            font_size=config.FONTS['size_small'],
            color=config.COLORS['text_secondary'],
            size_hint=(1, None),
            halign='left',
            valign='top'
        )
        steps_label.bind(
            width=lambda *x: steps_label.setter('text_size')(steps_label, (steps_label.width, None))
        )
        steps_label.bind(
            texture_size=steps_label.setter('size')
        )
        section.add_widget(steps_label)
        
        # Calculate total height
        section.height = sum(child.height for child in section.children) + \
                        section.padding[1] * 2 + \
                        section.spacing * (len(section.children) - 1)
        
        return section
    
    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
