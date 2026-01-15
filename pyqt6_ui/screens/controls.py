"""
MASH IoT Device - Controls Screen
Manual actuator control with automation override
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon

from config import COLORS, ICONS_DIR, ICONS, SENSOR_UPDATE_INTERVAL
from api_client import APIClient


class ActuatorControl(QFrame):
    """Card for controlling individual actuator"""
    
    def __init__(self, name: str, display_name: str, icon_name: str, parent=None):
        super().__init__(parent)
        self.actuator_name = name
        self.display_name = display_name
        self.icon_name = icon_name
        self.state = False
        self.setup_ui()
    
    def setup_ui(self):
        """Setup control UI"""
        self.setProperty("class", "card")
        self.setMinimumHeight(140)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header with icon and name
        header = QHBoxLayout()
        header.setSpacing(12)
        
        # Icon
        icon_path = ICONS_DIR / self.icon_name
        if icon_path.exists():
            icon_label = QLabel()
            pixmap = QPixmap(str(icon_path))
            icon_label.setPixmap(pixmap.scaled(
                40, 40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            header.addWidget(icon_label)
        
        # Name
        name_label = QLabel(self.display_name)
        name_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        header.addWidget(name_label)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Status
        self.status_label = QLabel("OFF")
        self.status_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_disabled']};
            font-weight: 500;
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Toggle switch
        toggle_layout = QHBoxLayout()
        
        toggle_label = QLabel("Power:")
        toggle_label.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_secondary']};
        """)
        toggle_layout.addWidget(toggle_label)
        toggle_layout.addStretch()
        
        self.toggle = QCheckBox()
        self.toggle.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 56px;
                height: 28px;
                border-radius: 14px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {COLORS['surface_light']};
                border: 2px solid {COLORS['border']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                border: none;
            }}
        """)
        self.toggle.toggled.connect(self.on_toggle)
        toggle_layout.addWidget(self.toggle)
        
        layout.addLayout(toggle_layout)
        
        self.setLayout(layout)
    
    def on_toggle(self, checked: bool):
        """Handle toggle change"""
        self.state = checked
        self.update_status()
    
    def update_status(self):
        """Update status label"""
        if self.state:
            self.status_label.setText("ON")
            self.status_label.setStyleSheet(f"""
                font-size: 14px;
                color: {COLORS['success']};
                font-weight: 600;
            """)
        else:
            self.status_label.setText("OFF")
            self.status_label.setStyleSheet(f"""
                font-size: 14px;
                color: {COLORS['text_disabled']};
                font-weight: 500;
            """)
    
    def set_state(self, state: bool, block_signals: bool = True):
        """Set actuator state"""
        if block_signals:
            self.toggle.blockSignals(True)
        self.toggle.setChecked(state)
        if block_signals:
            self.toggle.blockSignals(False)
        
        self.state = state
        self.update_status()


class ControlsScreen(QWidget):
    """Actuator controls screen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_client = APIClient()
        self.setup_ui()
        self.setup_timers()
    
    def setup_ui(self):
        """Setup controls UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("Manual Controls")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        header.addWidget(title)
        header.addStretch()
        
        # Automation toggle
        self.auto_checkbox = QCheckBox("Automation Enabled")
        self.auto_checkbox.setStyleSheet(f"""
            QCheckBox {{
                font-size: 14px;
                font-weight: 500;
                color: {COLORS['text_primary']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {COLORS['surface_light']};
                border: 2px solid {COLORS['border']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                border: none;
            }}
        """)
        self.auto_checkbox.setChecked(True)
        self.auto_checkbox.toggled.connect(self.on_automation_toggle)
        header.addWidget(self.auto_checkbox)
        
        layout.addLayout(header)
        
        # Info banner
        self.info_banner = QFrame()
        self.info_banner.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface_light']};
                border-left: 4px solid {COLORS['info']};
                border-radius: 8px;
                padding: 12px 16px;
            }}
        """)
        
        banner_layout = QHBoxLayout()
        banner_layout.setSpacing(12)
        
        info_icon_path = ICONS_DIR / ICONS['info']
        if info_icon_path.exists():
            info_icon = QLabel()
            pixmap = QPixmap(str(info_icon_path))
            info_icon.setPixmap(pixmap.scaled(
                20, 20,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            banner_layout.addWidget(info_icon)
        
        self.info_label = QLabel("Automation is active. System is managing actuators automatically.")
        self.info_label.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_secondary']};
        """)
        self.info_label.setWordWrap(True)
        banner_layout.addWidget(self.info_label)
        
        self.info_banner.setLayout(banner_layout)
        layout.addWidget(self.info_banner)
        
        # Actuator controls grid
        controls_grid = QGridLayout()
        controls_grid.setSpacing(16)
        
        self.actuator_controls = {
            'humidifier': ActuatorControl('humidifier', 'Humidifier', ICONS['humidifier']),
            'fan_exhaust': ActuatorControl('fan_exhaust', 'Exhaust Fan', ICONS['fan_exhaust']),
            'fan_circulation': ActuatorControl('fan_circulation', 'Circulation Fan', ICONS['fan_circulation']),
            'led_grow': ActuatorControl('led_grow', 'Grow Lights', ICONS['led_grow']),
        }
        
        controls_grid.addWidget(self.actuator_controls['humidifier'], 0, 0)
        controls_grid.addWidget(self.actuator_controls['fan_exhaust'], 0, 1)
        controls_grid.addWidget(self.actuator_controls['fan_circulation'], 1, 0)
        controls_grid.addWidget(self.actuator_controls['led_grow'], 1, 1)
        
        # Connect actuator toggles
        for name, control in self.actuator_controls.items():
            control.toggle.toggled.connect(
                lambda checked, n=name: self.on_actuator_change(n, checked)
            )
        
        layout.addLayout(controls_grid)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def setup_timers(self):
        """Setup update timers"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_states)
        self.update_timer.start(SENSOR_UPDATE_INTERVAL * 1000)
        
        # Initial update
        self.update_states()
    
    def update_states(self):
        """Update actuator states from API"""
        try:
            # Get automation status
            auto_status = self.api_client.get_automation_status()
            if auto_status:
                enabled = auto_status.get('automation_enabled', True)
                self.auto_checkbox.blockSignals(True)
                self.auto_checkbox.setChecked(enabled)
                self.auto_checkbox.blockSignals(False)
                self.update_info_banner(enabled)
            
            # Get actuator states
            states = self.api_client.get_actuator_states()
            if states:
                for name, control in self.actuator_controls.items():
                    if name in states:
                        control.set_state(states[name], block_signals=True)
        
        except Exception as e:
            print(f"Error updating controls: {e}")
    
    def on_automation_toggle(self, checked: bool):
        """Handle automation toggle"""
        try:
            self.api_client.set_automation_mode(checked)
            self.update_info_banner(checked)
            
            # Enable/disable manual controls
            for control in self.actuator_controls.values():
                control.setEnabled(not checked)
        
        except Exception as e:
            print(f"Error toggling automation: {e}")
    
    def on_actuator_change(self, actuator: str, state: bool):
        """Handle actuator state change"""
        try:
            # Only send if automation is disabled
            if not self.auto_checkbox.isChecked():
                self.api_client.set_actuator(actuator, state)
        
        except Exception as e:
            print(f"Error changing actuator: {e}")
    
    def update_info_banner(self, automation_enabled: bool):
        """Update info banner based on automation state"""
        if automation_enabled:
            self.info_banner.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['surface_light']};
                    border-left: 4px solid {COLORS['info']};
                    border-radius: 8px;
                    padding: 12px 16px;
                }}
            """)
            self.info_label.setText("Automation is active. System is managing actuators automatically.")
            
            # Disable manual controls
            for control in self.actuator_controls.values():
                control.setEnabled(False)
        else:
            self.info_banner.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['surface_light']};
                    border-left: 4px solid {COLORS['warning']};
                    border-radius: 8px;
                    padding: 12px 16px;
                }}
            """)
            self.info_label.setText("Manual mode active. You have full control of actuators.")
            
            # Enable manual controls
            for control in self.actuator_controls.values():
                control.setEnabled(True)
    
    def refresh(self):
        """Refresh controls data"""
        self.update_states()
