"""
Chamber Configuration Screen - Set up chamber details
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFrame,
                            QHBoxLayout, QLineEdit, QSpinBox, QComboBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from config import COLORS, FONTS


class ChamberConfigScreen(QWidget):
    """Chamber configuration screen"""
    
    chamber_configured = pyqtSignal(dict)  # Signal with chamber config data
    skip_setup = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        # Scrollable content
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Configure Chamber")
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['heading']}px;
            font-weight: 700;
        """)
        header.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Set up your mushroom growing chamber parameters")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['body_small']}px;
            margin-bottom: 10px;
        """)
        desc.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(desc)
        
        # Chamber Name
        layout.addWidget(self._create_section_label("Chamber Name"))
        self.chamber_name_input = self._create_text_input("e.g., Main Growing Chamber")
        layout.addWidget(self.chamber_name_input)
        
        # Mushroom Type
        layout.addWidget(self._create_section_label("Mushroom Type"))
        self.mushroom_type_combo = QComboBox()
        self.mushroom_type_combo.addItems([
            "Oyster Mushroom",
            "Shiitake",
            "Lion's Mane",
            "Button Mushroom",
            "Reishi",
            "King Oyster",
            "Other"
        ])
        self.mushroom_type_combo.setFixedHeight(44)
        self.mushroom_type_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                font-size: {FONTS['body']}px;
            }}
            QComboBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS['text_secondary']};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 4px;
            }}
        """)
        layout.addWidget(self.mushroom_type_combo)
        
        # Growth Stage
        layout.addWidget(self._create_section_label("Growth Stage"))
        self.growth_stage_combo = QComboBox()
        self.growth_stage_combo.addItems([
            "Inoculation",
            "Colonization",
            "Pinning",
            "Fruiting",
            "Harvesting"
        ])
        self.growth_stage_combo.setFixedHeight(44)
        self.growth_stage_combo.setStyleSheet(self.mushroom_type_combo.styleSheet())
        layout.addWidget(self.growth_stage_combo)
        
        # Chamber Size
        layout.addWidget(self._create_section_label("Chamber Size"))
        
        size_card = QFrame()
        size_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        size_layout = QVBoxLayout(size_card)
        size_layout.setSpacing(12)
        
        # Width
        width_row = QHBoxLayout()
        width_label = QLabel("Width (cm):")
        width_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: {FONTS['body_small']}px;")
        width_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.width_spin = self._create_spinbox(50, 500, 100)
        width_row.addWidget(width_label)
        width_row.addWidget(self.width_spin, 1)
        size_layout.addLayout(width_row)
        
        # Height
        height_row = QHBoxLayout()
        height_label = QLabel("Height (cm):")
        height_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: {FONTS['body_small']}px;")
        height_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.height_spin = self._create_spinbox(50, 500, 120)
        height_row.addWidget(height_label)
        height_row.addWidget(self.height_spin, 1)
        size_layout.addLayout(height_row)
        
        # Depth
        depth_row = QHBoxLayout()
        depth_label = QLabel("Depth (cm):")
        depth_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: {FONTS['body_small']}px;")
        depth_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.depth_spin = self._create_spinbox(50, 500, 80)
        depth_row.addWidget(depth_label)
        depth_row.addWidget(self.depth_spin, 1)
        size_layout.addLayout(depth_row)
        
        layout.addWidget(size_card)
        
        # Target Parameters
        layout.addWidget(self._create_section_label("Target Environmental Parameters"))
        
        params_card = QFrame()
        params_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        params_layout = QVBoxLayout(params_card)
        params_layout.setSpacing(12)
        
        # Temperature
        temp_row = QHBoxLayout()
        temp_label = QLabel("Temperature (°C):")
        temp_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: {FONTS['body_small']}px;")
        temp_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.temp_spin = self._create_spinbox(15, 30, 18, suffix="°C")
        temp_row.addWidget(temp_label)
        temp_row.addWidget(self.temp_spin, 1)
        params_layout.addLayout(temp_row)
        
        # Humidity
        humidity_row = QHBoxLayout()
        humidity_label = QLabel("Humidity (%):")
        humidity_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: {FONTS['body_small']}px;")
        humidity_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.humidity_spin = self._create_spinbox(70, 100, 85, suffix="%")
        humidity_row.addWidget(humidity_label)
        humidity_row.addWidget(self.humidity_spin, 1)
        params_layout.addLayout(humidity_row)
        
        # CO2
        co2_row = QHBoxLayout()
        co2_label = QLabel("CO2 (ppm):")
        co2_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: {FONTS['body_small']}px;")
        co2_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.co2_spin = self._create_spinbox(500, 2000, 1200, suffix=" ppm", step=50)
        co2_row.addWidget(co2_label)
        co2_row.addWidget(self.co2_spin, 1)
        params_layout.addLayout(co2_row)
        
        layout.addWidget(params_card)
        
        # Add spacer
        layout.addStretch()
        
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
        
        btn_continue = QPushButton("Continue")
        btn_continue.setFixedHeight(48)
        btn_continue.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_continue.setStyleSheet(f"""
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
        """)
        btn_continue.clicked.connect(self.on_continue)
        buttons_layout.addWidget(btn_continue, 1)
        
        layout.addLayout(buttons_layout)
        
        scroll.setWidget(content)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _create_section_label(self, text: str) -> QLabel:
        """Create a section label"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['body']}px;
            font-weight: 600;
            margin-top: 4px;
        """)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        return label
    
    def _create_text_input(self, placeholder: str) -> QLineEdit:
        """Create a text input field"""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedHeight(44)
        input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['card_bg']};
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
        return input_field
    
    def _create_spinbox(self, min_val: int, max_val: int, default: int, 
                       suffix: str = "", step: int = 1) -> QSpinBox:
        """Create a spinbox widget"""
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default)
        spinbox.setSingleStep(step)
        if suffix:
            spinbox.setSuffix(suffix)
        spinbox.setFixedHeight(44)
        spinbox.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 8px;
                font-size: {FONTS['body']}px;
            }}
            QSpinBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: transparent;
                border: none;
                width: 20px;
            }}
            QSpinBox::up-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid {COLORS['text_secondary']};
            }}
            QSpinBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {COLORS['text_secondary']};
            }}
        """)
        return spinbox
    
    def on_continue(self):
        """Collect config and emit signal"""
        config = {
            'chamber_name': self.chamber_name_input.text() or 'Main Chamber',
            'mushroom_type': self.mushroom_type_combo.currentText(),
            'growth_stage': self.growth_stage_combo.currentText(),
            'dimensions': {
                'width_cm': self.width_spin.value(),
                'height_cm': self.height_spin.value(),
                'depth_cm': self.depth_spin.value()
            },
            'target_params': {
                'temperature_c': self.temp_spin.value(),
                'humidity_percent': self.humidity_spin.value(),
                'co2_ppm': self.co2_spin.value()
            }
        }
        self.chamber_configured.emit(config)
