"""
Welcome/Splash Screen - First screen shown on initial setup
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from config import COLORS, FONTS, ICONS
from icon_utils import load_svg_icon
import os


class WelcomeScreen(QWidget):
    """Welcome screen for first-time setup"""
    
    start_setup = pyqtSignal()  # Signal when user clicks "Get Started"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Content area (top 60% for keyboard space)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(16)
        
        # Logo/Icon
        logo_container = QHBoxLayout()
        logo_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_label = QLabel()
        logo_label.setFixedSize(100, 100)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Try to load logo from assets
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.svg')
        if os.path.exists(logo_path):
            logo_pixmap = load_svg_icon(logo_path, 100)
            logo_label.setPixmap(logo_pixmap)
        else:
            # Fallback text
            logo_label.setText("🍄")
            logo_label.setStyleSheet(f"font-size: 64px;")
        
        logo_container.addWidget(logo_label)
        content_layout.addLayout(logo_container)
        
        # Title
        title = QLabel("Welcome to MASH")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['heading'] + 4}px;
            font-weight: 700;
            margin: 10px 0;
        """)
        content_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Mushroom Automation System Hub")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            color: {COLORS['primary']};
            font-size: {FONTS['subheading']}px;
            font-weight: 600;
        """)
        content_layout.addWidget(subtitle)
        
        # Description
        desc = QLabel("Intelligent climate control for optimal mushroom cultivation")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['body']}px;
            margin-top: 10px;
        """)
        content_layout.addWidget(desc)
        
        main_layout.addLayout(content_layout)
        
        # Bottom spacer for keyboard (40% of screen)
        main_layout.addSpacerItem(QSpacerItem(20, 150, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Get Started button at bottom
        btn_start = QPushButton("Get Started")
        btn_start.setMinimumHeight(50)
        btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['background']};
                border: none;
                border-radius: 8px;
                font-size: {FONTS['button']}px;
                font-weight: 600;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary_pressed']};
            }}
        """)
        btn_start.clicked.connect(self.start_setup.emit)
        main_layout.addWidget(btn_start)
