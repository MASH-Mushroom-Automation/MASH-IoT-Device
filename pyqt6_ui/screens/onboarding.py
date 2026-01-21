"""
Onboarding Screen - Important information and core functions
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QFrame, QScrollArea, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from config import COLORS, FONTS


class OnboardingScreen(QWidget):
    """Onboarding screen showing important information"""
    
    next_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Content area (top 60% for keyboard space)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        
        # Header
        header = QLabel("Welcome to MASH")
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['heading'] + 4}px;
            font-weight: 700;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(header)
        
        # Subtitle
        subtitle = QLabel("Mushroom Automation Smart Hub")
        subtitle.setStyleSheet(f"""
            color: {COLORS['primary']};
            font-size: {FONTS['subheading']}px;
            font-weight: 600;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(subtitle)
        
        # Spacer
        content_layout.addSpacing(20)
        
        # Scrollable content area for information
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {COLORS['surface']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['primary']};
                border-radius: 5px;
            }}
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(16)
        
        # Information cards
        info_items = [
            ("🌱 Automated Climate Control", 
             "Maintain optimal temperature, humidity, and CO\u2082 levels automatically"),
            ("📊 Real-time Monitoring", 
             "Track your grow chamber conditions 24/7 from anywhere"),
            ("🔔 Smart Alerts", 
             "Receive instant notifications when conditions need attention"),
            ("🤖 AI-Powered Insights", 
             "Get recommendations to optimize your mushroom yields"),
            ("📱 Mobile App Integration", 
             "Control and monitor your chamber from your phone"),
        ]
        
        for title, description in info_items:
            card = self.create_info_card(title, description)
            scroll_layout.addWidget(card)
        
        scroll_area.setWidget(scroll_content)
        content_layout.addWidget(scroll_area, 1)
        
        main_layout.addWidget(content_widget, 1)
        
        # Bottom spacer for keyboard (40% of screen)
        main_layout.addSpacerItem(QSpacerItem(20, 150, 
                                              QSizePolicy.Policy.Minimum, 
                                              QSizePolicy.Policy.Expanding))
        
        # Continue button at bottom
        btn_continue = QPushButton("Continue to Setup")
        btn_continue.setMinimumHeight(50)
        btn_continue.setStyleSheet(f"""
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
        btn_continue.clicked.connect(self.next_clicked.emit)
        main_layout.addWidget(btn_continue)
    
    def create_info_card(self, title: str, description: str) -> QFrame:
        """Create an information card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['body']}px;
            font-weight: 600;
        """)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['body_small']}px;
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        return card
