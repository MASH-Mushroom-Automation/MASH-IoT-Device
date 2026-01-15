"""
MASH IoT Device - PyQt6 Main Window
Modern touchscreen interface with navigation sidebar
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap

from config import COLORS, ICONS_DIR, ICONS, SCREEN_WIDTH, SCREEN_HEIGHT
from screens.dashboard import DashboardScreen
from screens.controls import ControlsScreen
from screens.alerts import AlertsScreen
from screens.ai_insights import AIInsightsScreen
from screens.settings import SettingsScreen


class NavigationButton(QPushButton):
    """Custom navigation button with icon and label"""
    
    def __init__(self, icon_name: str, label: str, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setProperty("class", "nav-button")
        
        # Create layout
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Icon
        icon_path = ICONS_DIR / icon_name
        if icon_path.exists():
            icon_label = QLabel()
            pixmap = QPixmap(str(icon_path))
            icon_label.setPixmap(pixmap.scaled(
                24, 24, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            layout.addWidget(icon_label)
        
        # Label
        text_label = QLabel(label)
        text_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(text_label)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setMinimumHeight(56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class NavigationSidebar(QFrame):
    """Left sidebar with navigation buttons"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup sidebar UI"""
        self.setFixedWidth(220)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(8)
        
        # Logo/Title
        title = QLabel("MASH IoT")
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['primary']};
            padding: 12px 0;
        """)
        layout.addWidget(title)
        
        # Spacing
        layout.addSpacing(20)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ('home', 'Dashboard', ICONS['home']),
            ('controls', 'Controls', ICONS['controls']),
            ('alerts', 'Alerts', ICONS['alerts']),
            ('ai_insights', 'AI Insights', ICONS['ai_insights']),
            ('settings', 'Settings', ICONS['settings']),
        ]
        
        for key, label, icon in nav_items:
            btn = NavigationButton(icon, label)
            self.nav_buttons[key] = btn
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # System status at bottom
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface_light']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        status_layout = QVBoxLayout()
        status_layout.setSpacing(4)
        
        self.status_label = QLabel("System Online")
        self.status_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {COLORS['success']};
        """)
        
        self.uptime_label = QLabel("Uptime: --")
        self.uptime_label.setStyleSheet(f"""
            font-size: 10px;
            color: {COLORS['text_secondary']};
        """)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.uptime_label)
        status_frame.setLayout(status_layout)
        
        layout.addWidget(status_frame)
        
        self.setLayout(layout)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup main window UI"""
        self.setWindowTitle("MASH IoT Device")
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = NavigationSidebar()
        main_layout.addWidget(self.sidebar)
        
        # Content area with stacked widget
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {COLORS['background']};
            }}
        """)
        
        # Add screens
        self.screens = {
            'dashboard': DashboardScreen(),
            'controls': ControlsScreen(),
            'alerts': AlertsScreen(),
            'ai_insights': AIInsightsScreen(),
            'settings': SettingsScreen(),
        }
        
        for screen in self.screens.values():
            self.content_stack.addWidget(screen)
        
        main_layout.addWidget(self.content_stack)
        
        central_widget.setLayout(main_layout)
        
        # Set initial screen
        self.show_screen('dashboard')
    
    def setup_connections(self):
        """Connect navigation buttons to screens"""
        for key, button in self.sidebar.nav_buttons.items():
            button.clicked.connect(lambda checked, k=key: self.show_screen(k))
    
    def show_screen(self, screen_name: str):
        """Switch to specified screen"""
        if screen_name in self.screens:
            # Update navigation buttons
            for key, button in self.sidebar.nav_buttons.items():
                button.setChecked(key == screen_name)
            
            # Show screen
            self.content_stack.setCurrentWidget(self.screens[screen_name])
            
            # Refresh screen data
            if hasattr(self.screens[screen_name], 'refresh'):
                self.screens[screen_name].refresh()
