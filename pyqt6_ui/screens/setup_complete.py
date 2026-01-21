"""
Setup Complete Screen - Final screen in setup flow
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QSpacerItem, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from config import COLORS, FONTS, ICONS
from icon_utils import load_svg_icon


class SetupCompleteScreen(QWidget):
    """Setup completion screen"""
    
    finish_setup = pyqtSignal()  # Signal to complete setup and go to dashboard
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.device_info = {}
        self.init_ui()
    
    def set_device_info(self, info: dict):
        """Set device information"""
        self.device_info = info
        
        # Update device name label if it exists
        if hasattr(self, 'device_name_value'):
            self.device_name_value.setText(info.get('device_name', 'MASH Device'))
            self.device_id_value.setText(info.get('device_id', 'N/A'))
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Add top spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Success icon
        icon_container = QHBoxLayout()
        icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon_label.setFixedSize(100, 100)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Use checkmark or success icon
        icon_pixmap = load_svg_icon(ICONS.get('success', ICONS['dashboard']), COLORS['success'], 100)
        icon_label.setPixmap(icon_pixmap)
        icon_container.addWidget(icon_label)
        layout.addLayout(icon_container)
        
        # Title
        title = QLabel("Setup Complete!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['heading']}px;
            font-weight: 700;
            margin: 20px 0;
        """)
        title.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(title)
        
        # Message
        message = QLabel("Your MASH device is ready to grow mushrooms!")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['body']}px;
            margin-bottom: 20px;
        """)
        message.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(message)
        
        # Device info card
        info_card = QFrame()
        info_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(12)
        
        # Device Name
        name_row = self._create_info_row("Device Name:", "MASH Device")
        self.device_name_value = name_row[1]
        info_layout.addLayout(name_row[0])
        
        # Device ID
        id_row = self._create_info_row("Device ID:", "Pending...")
        self.device_id_value = id_row[1]
        info_layout.addLayout(id_row[0])
        
        # Status
        status_row = self._create_info_row("Status:", "✓ Ready")
        status_label = status_row[1]
        status_label.setStyleSheet(f"""
            color: {COLORS['success']};
            font-size: {FONTS['body']}px;
            font-weight: 600;
        """)
        info_layout.addLayout(status_row[0])
        
        layout.addWidget(info_card)
        
        # Next steps card
        steps_card = QFrame()
        steps_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        steps_layout = QVBoxLayout(steps_card)
        steps_layout.setSpacing(10)
        
        steps_title = QLabel("What's Next:")
        steps_title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['body']}px;
            font-weight: 600;
            margin-bottom: 4px;
        """)
        steps_title.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        steps_layout.addWidget(steps_title)
        
        steps = [
            "• Monitor your chamber conditions in real-time",
            "• Enable AI automation for optimal growth",
            "• Control actuators manually when needed",
            "• View alerts and insights on the dashboard"
        ]
        
        for step in steps:
            step_label = QLabel(step)
            step_label.setStyleSheet(f"""
                color: {COLORS['text_secondary']};
                font-size: {FONTS['body_small']}px;
                padding: 2px 0;
            """)
            step_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            steps_layout.addWidget(step_label)
        
        layout.addWidget(steps_card)
        
        # Add bottom spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Go to Dashboard button
        btn_finish = QPushButton("Go to Dashboard")
        btn_finish.setFixedHeight(56)
        btn_finish.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_finish.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 12px;
                font-size: {FONTS['body']}px;
                font-weight: 600;
                padding: 0 24px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary_pressed']};
            }}
        """)
        btn_finish.clicked.connect(self.finish_setup.emit)
        layout.addWidget(btn_finish)
    
    def _create_info_row(self, label_text: str, value_text: str) -> tuple:
        """Create an info row with label and value"""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(8)
        
        label = QLabel(label_text)
        label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['body_small']}px;
        """)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        row_layout.addWidget(label)
        
        value = QLabel(value_text)
        value.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['body_small']}px;
            font-weight: 600;
        """)
        value.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        row_layout.addWidget(value, 1)
        
        return (row_layout, value)
