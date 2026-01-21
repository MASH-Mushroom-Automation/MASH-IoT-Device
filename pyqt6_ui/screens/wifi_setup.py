"""
WiFi Setup Screen - Configure network connectivity
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFrame,
                            QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
                            QProgressBar, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap
from config import COLORS, FONTS, ICONS
from icon_utils import load_svg_icon
import subprocess


class WiFiSetupScreen(QWidget):
    """WiFi configuration screen"""
    
    wifi_configured = pyqtSignal()  # Signal when WiFi is connected
    skip_setup = pyqtSignal()  # Signal to skip WiFi setup
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.selected_ssid = None
        self.available_networks = []
        self.init_ui()
        
        # Auto-scan on load
        QTimer.singleShot(500, self.scan_networks)
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Connect to WiFi")
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['heading']}px;
            font-weight: 700;
        """)
        header.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Connect your device to a WiFi network for online features")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['body_small']}px;
            margin-bottom: 10px;
        """)
        desc.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        layout.addWidget(desc)
        
        # Scan button and progress
        scan_container = QHBoxLayout()
        
        self.btn_scan = QPushButton("Scan Networks")
        self.btn_scan.setFixedHeight(44)
        self.btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_scan.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-size: {FONTS['body_small']}px;
                font-weight: 600;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover_bg']};
            }}
        """)
        self.btn_scan.clicked.connect(self.scan_networks)
        scan_container.addWidget(self.btn_scan)
        
        self.scan_progress = QProgressBar()
        self.scan_progress.setFixedHeight(4)
        self.scan_progress.setTextVisible(False)
        self.scan_progress.setRange(0, 0)  # Indeterminate
        self.scan_progress.setStyleSheet(f"""
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
        self.scan_progress.hide()
        
        scan_container.addWidget(self.scan_progress, 1)
        layout.addLayout(scan_container)
        
        # Networks list
        self.networks_list = QListWidget()
        self.networks_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px;
            }}
            QListWidget::item {{
                background-color: transparent;
                color: {COLORS['text_primary']};
                padding: 12px;
                margin: 4px 0;
                border-radius: 6px;
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['hover_bg']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
            }}
        """)
        self.networks_list.itemClicked.connect(self.on_network_selected)
        layout.addWidget(self.networks_list, 1)
        
        # Password input (hidden initially)
        self.password_container = QFrame()
        password_layout = QVBoxLayout(self.password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(8)
        
        pwd_label = QLabel("Password:")
        pwd_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['body_small']}px;
            font-weight: 600;
        """)
        pwd_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        password_layout.addWidget(pwd_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter WiFi password")
        self.password_input.setFixedHeight(44)
        self.password_input.setStyleSheet(f"""
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
        password_layout.addWidget(self.password_input)
        
        self.password_container.hide()
        layout.addWidget(self.password_container)
        
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
        
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.setFixedHeight(48)
        self.btn_connect.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_connect.setEnabled(False)
        self.btn_connect.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 10px;
                font-size: {FONTS['body']}px;
                font-weight: 600;
            }}
            QPushButton:hover:enabled {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_tertiary']};
            }}
        """)
        self.btn_connect.clicked.connect(self.connect_to_wifi)
        buttons_layout.addWidget(self.btn_connect, 1)
        
        layout.addLayout(buttons_layout)
    
    def scan_networks(self):
        """Scan for available WiFi networks"""
        self.btn_scan.hide()
        self.scan_progress.show()
        self.networks_list.clear()
        self.status_label.hide()
        
        try:
            # Try nmcli first (NetworkManager)
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                networks = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            ssid = parts[0]
                            signal = parts[1] if len(parts) > 1 else '0'
                            security = parts[2] if len(parts) > 2 else ''
                            
                            if ssid and ssid.strip():
                                networks.append({
                                    'ssid': ssid,
                                    'signal': int(signal) if signal.isdigit() else 0,
                                    'security': security
                                })
                
                # Sort by signal strength
                networks.sort(key=lambda x: x['signal'], reverse=True)
                self.available_networks = networks
                
                # Populate list
                for network in networks:
                    icon = "🔒" if network['security'] else "📶"
                    item_text = f"{icon} {network['ssid']} ({network['signal']}%)"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, network['ssid'])
                    self.networks_list.addItem(item)
                
                if not networks:
                    self.show_status("No networks found", False)
            else:
                self.show_status("Failed to scan networks", False)
                
        except Exception as e:
            print(f"WiFi scan error: {e}")
            self.show_status("WiFi scan failed", False)
        finally:
            self.scan_progress.hide()
            self.btn_scan.show()
    
    def on_network_selected(self, item):
        """Handle network selection"""
        self.selected_ssid = item.data(Qt.ItemDataRole.UserRole)
        
        # Find network security
        network = next((n for n in self.available_networks if n['ssid'] == self.selected_ssid), None)
        
        if network and network['security']:
            # Requires password
            self.password_container.show()
            self.password_input.setFocus()
            self.btn_connect.setEnabled(False)
            self.password_input.textChanged.connect(lambda: self.btn_connect.setEnabled(bool(self.password_input.text())))
        else:
            # Open network
            self.password_container.hide()
            self.btn_connect.setEnabled(True)
    
    def connect_to_wifi(self):
        """Connect to selected WiFi network"""
        if not self.selected_ssid:
            return
        
        self.btn_connect.setEnabled(False)
        self.btn_connect.setText("Connecting...")
        self.status_label.show()
        self.status_label.setText("Connecting to WiFi...")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        
        try:
            password = self.password_input.text()
            cmd = ['nmcli', 'dev', 'wifi', 'connect', self.selected_ssid]
            
            if password:
                cmd.extend(['password', password])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.show_status("✓ Connected successfully!", True)
                QTimer.singleShot(1500, self.wifi_configured.emit)
            else:
                self.show_status(f"✗ Connection failed: {result.stderr}", False)
                self.btn_connect.setEnabled(True)
                self.btn_connect.setText("Connect")
                
        except Exception as e:
            self.show_status(f"✗ Error: {str(e)}", False)
            self.btn_connect.setEnabled(True)
            self.btn_connect.setText("Connect")
    
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
