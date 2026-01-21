"""
MASH IoT Device - Settings Screen
System configuration and information
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton, QScrollArea, QLineEdit
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon

from config import COLORS, ICONS_DIR, ICONS, MOCK_MODE
from api_client import APIClient
from icon_utils import create_icon


class SettingSection(QFrame):
    """Settings section container"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setup_ui(title)
    
    def setup_ui(self, title: str):
        """Setup section UI"""
        self.setProperty("class", "card")
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(14, 14, 14, 14)
        self.layout.setSpacing(12)
        
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        self.layout.addWidget(title_label)
        
        self.setLayout(self.layout)
    
    def add_item(self, label: str, value: str):
        """Add setting item"""
        item_layout = QHBoxLayout()
        item_layout.setSpacing(12)
        
        label_widget = QLabel(label)
        label_widget.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        label_widget.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 500;
            color: {COLORS['text_secondary']};
        """)
        item_layout.addWidget(label_widget)
        
        item_layout.addStretch()
        
        value_widget = QLabel(value)
        value_widget.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        value_widget.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        item_layout.addWidget(value_widget)
        
        self.layout.addLayout(item_layout)


class SettingsScreen(QWidget):
    """Settings and system information screen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_client = APIClient()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("Settings")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        header.addWidget(title)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Scroll area for settings sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Enable kinetic scrolling for touch
        scroll.setProperty("kineticScrollingEnabled", True)
        scroll.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(16)
        
        # System Information Section
        system_section = SettingSection("System Information")
        
        # Mode indicator
        mode = "Demo Mode (Mock Data)" if MOCK_MODE else "Production Mode"
        system_section.add_item("Operation Mode:", mode)
        
        try:
            info = self.api_client.get_system_info()
            if info:
                if 'device_name' in info:
                    system_section.add_item("Device Name:", info['device_name'])
                if 'version' in info:
                    system_section.add_item("Software Version:", info['version'])
                if 'uptime' in info:
                    system_section.add_item("Uptime:", info['uptime'])
        except:
            system_section.add_item("Status:", "Unable to fetch system info")
        
        scroll_layout.addWidget(system_section)
        
        # Network Section
        network_section = SettingSection("Network Configuration")
        network_section.add_item("API Endpoint:", "http://127.0.0.1:5000/api")
        network_section.add_item("Connection:", "Local")
        scroll_layout.addWidget(network_section)
        
        # Sensor Thresholds Section
        thresholds_section = SettingSection("Sensor Thresholds")
        thresholds_section.add_item("CO2 Range:", "800 - 1500 ppm")
        thresholds_section.add_item("CO2 Optimal:", "1000 - 1400 ppm")
        thresholds_section.add_item("Temperature Range:", "15 - 25 °C")
        thresholds_section.add_item("Temperature Optimal:", "18 - 22 °C")
        thresholds_section.add_item("Humidity Range:", "70 - 95 %")
        thresholds_section.add_item("Humidity Optimal:", "80 - 90 %")
        scroll_layout.addWidget(thresholds_section)
        
        # About Section
        about_section = SettingSection("About MASH IoT Device")
        about_section.add_item("Application:", "MASH IoT Device Control")
        about_section.add_item("UI Framework:", "PyQt6")
        about_section.add_item("Backend:", "Flask + Python")
        about_section.add_item("Purpose:", "Mushroom Growing Automation")
        scroll_layout.addWidget(about_section)
        
        # Actions Section
        actions_section = QFrame()
        actions_section.setProperty("class", "card")
        actions_layout = QVBoxLayout()
        actions_layout.setContentsMargins(20, 20, 20, 20)
        actions_layout.setSpacing(12)
        
        actions_title = QLabel("Actions")
        actions_title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        actions_layout.addWidget(actions_title)
        
        # Export data button
        export_btn = QPushButton()
        icon_path = ICONS_DIR / ICONS['download']
        if icon_path.exists():
            export_btn.setIcon(create_icon(icon_path, 20, COLORS['text_primary']))
            export_btn.setIconSize(QSize(20, 20))
        export_btn.setText("Export Sensor Data")
        export_btn.clicked.connect(self.export_data)
        actions_layout.addWidget(export_btn)
        
        # Refresh config button
        refresh_btn = QPushButton()
        icon_path = ICONS_DIR / ICONS['refresh']
        if icon_path.exists():
            refresh_btn.setIcon(create_icon(icon_path, 20, COLORS['text_primary']))
            refresh_btn.setIconSize(QSize(20, 20))
        refresh_btn.setText("Refresh Configuration")
        refresh_btn.clicked.connect(self.refresh)
        actions_layout.addWidget(refresh_btn)
        
        actions_section.setLayout(actions_layout)
        scroll_layout.addWidget(actions_section)
        
        scroll_layout.addStretch()
        
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def refresh(self):
        """Refresh settings"""
        # Rebuild UI to refresh data
        # Clear layout
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Rebuild
        self.setup_ui()
    
    def export_data(self):
        """Export sensor data"""
        # TODO: Implement data export functionality
        print("Export data functionality - to be implemented")
