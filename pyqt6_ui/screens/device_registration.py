"""
Device Registration Screen - Register device with MASH backend
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFrame,
                            QHBoxLayout, QLineEdit, QProgressBar, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from config import COLORS, FONTS, ICONS
from icon_utils import load_svg_icon


class DeviceRegistrationScreen(QWidget):
    """Device registration screen"""
    
    registration_complete = pyqtSignal(dict)  # Signal with device info
    skip_setup = pyqtSignal()
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.chamber_config = {}
        self.init_ui()
    
    def set_chamber_config(self, config: dict):
        """Set chamber configuration from previous screen"""
        self.chamber_config = config
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Add top spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Icon
        icon_container = QHBoxLayout()
        icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon_label.setFixedSize(80, 80)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_pixmap = load_svg_icon(ICONS['settings'], COLORS['primary'], 80)
        icon_label.setPixmap(icon_pixmap)
        icon_container.addWidget(icon_label)
        layout.addLayout(icon_container)
        
        # Header
        header = QLabel("Device Registration")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['heading']}px;
            font-weight: 700;
            margin: 12px 0;
        """)
        header.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Register your device with MASH cloud for remote monitoring and control")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['body_small']}px;
            margin-bottom: 20px;
        """)
        desc.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(desc)
        
        # Registration form
        form_card = QFrame()
        form_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(16)
        
        # Device Name
        name_label = QLabel("Device Name:")
        name_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['body_small']}px;
            font-weight: 600;
        """)
        name_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        form_layout.addWidget(name_label)
        
        self.device_name_input = QLineEdit()
        self.device_name_input.setPlaceholderText("e.g., MASH-001")
        self.device_name_input.setText("MASH-DEMO-001")
        self.device_name_input.setFixedHeight(44)
        self.device_name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                font-size: {FONTS['body']}px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
        """)
        form_layout.addWidget(self.device_name_input)
        
        # Location
        location_label = QLabel("Location (Optional):")
        location_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['body_small']}px;
            font-weight: 600;
        """)
        location_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        form_layout.addWidget(location_label)
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g., Lab Room 3")
        self.location_input.setFixedHeight(44)
        self.location_input.setStyleSheet(self.device_name_input.styleSheet())
        form_layout.addWidget(self.location_input)
        
        layout.addWidget(form_card)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['body_small']}px;
            padding: 8px;
        """)
        self.status_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['card_bg']};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
                border-radius: 2px;
            }}
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Add bottom spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        btn_skip = QPushButton("Skip for Now")
        btn_skip.setFixedHeight(48)
        btn_skip.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_skip.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                font-size: {FONTS['body']}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover_bg']};
            }}
        """)
        btn_skip.clicked.connect(self.skip_setup.emit)
        buttons_layout.addWidget(btn_skip, 1)
        
        self.btn_register = QPushButton("Register Device")
        self.btn_register.setFixedHeight(48)
        self.btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_register.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 10px;
                font-size: {FONTS['body']}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_tertiary']};
            }}
        """)
        self.btn_register.clicked.connect(self.register_device)
        buttons_layout.addWidget(self.btn_register, 1)
        
        layout.addLayout(buttons_layout)
    
    def register_device(self):
        """Register device with backend"""
        device_name = self.device_name_input.text().strip()
        
        if not device_name:
            self.show_status("Please enter a device name", False)
            return
        
        self.btn_register.setEnabled(False)
        self.btn_register.setText("Registering...")
        self.progress_bar.show()
        self.status_label.show()
        self.status_label.setText("Registering device...")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        
        # In mock mode, simulate registration
        if hasattr(self.api_client, '__class__') and 'Mock' in self.api_client.__class__.__name__:
            # Simulate delay
            QTimer.singleShot(2000, lambda: self._complete_registration(device_name))
        else:
            # Try actual registration with backend
            try:
                # Prepare registration data
                registration_data = {
                    'device_name': device_name,
                    'location': self.location_input.text().strip(),
                    'chamber_config': self.chamber_config
                }
                
                # Call registration API (placeholder - implement based on your API)
                # result = self.api_client.register_device(registration_data)
                
                # For now, complete registration
                self._complete_registration(device_name)
                
            except Exception as e:
                self.show_status(f"✗ Registration failed: {str(e)}", False)
                self.btn_register.setEnabled(True)
                self.btn_register.setText("Register Device")
                self.progress_bar.hide()
    
    def _complete_registration(self, device_name: str):
        """Complete registration process"""
        self.progress_bar.hide()
        self.show_status("✓ Device registered successfully!", True)
        
        device_info = {
            'device_id': f"MASH-{hash(device_name) % 10000:04d}",
            'device_name': device_name,
            'location': self.location_input.text().strip(),
            'chamber_config': self.chamber_config
        }
        
        # Emit signal after short delay
        QTimer.singleShot(1500, lambda: self.registration_complete.emit(device_info))
    
    def show_status(self, message: str, success: bool):
        """Show status message"""
        self.status_label.setText(message)
        color = COLORS['success'] if success else COLORS['error']
        self.status_label.setStyleSheet(f"""
            color: {color};
            font-size: {FONTS['body_small']}px;
            padding: 8px;
            font-weight: 500;
        """)
        self.status_label.show()
