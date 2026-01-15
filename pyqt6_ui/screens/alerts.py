"""
MASH IoT Device - Alerts Screen
System alerts with severity filtering and history
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton, QScrollArea, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon
from datetime import datetime

from config import COLORS, ICONS_DIR, ICONS, ALERT_CHECK_INTERVAL
from api_client import APIClient


class AlertItem(QFrame):
    """Individual alert item"""
    
    def __init__(self, alert_data: dict, parent=None):
        super().__init__(parent)
        self.alert_data = alert_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup alert UI"""
        severity = self.alert_data.get('severity', 'info')
        
        # Color coding by severity
        severity_colors = {
            'info': COLORS['info'],
            'warning': COLORS['warning'],
            'error': COLORS['error'],
            'critical': COLORS['error'],
        }
        border_color = severity_colors.get(severity, COLORS['info'])
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-left: 4px solid {border_color};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Header with severity icon and timestamp
        header = QHBoxLayout()
        header.setSpacing(10)
        
        # Severity icon
        icon_map = {
            'info': ICONS['info'],
            'warning': ICONS['warning'],
            'error': ICONS['error'],
            'critical': ICONS['error'],
        }
        icon_name = icon_map.get(severity, ICONS['info'])
        icon_path = ICONS_DIR / icon_name
        
        if icon_path.exists():
            icon_label = QLabel()
            pixmap = QPixmap(str(icon_path))
            icon_label.setPixmap(pixmap.scaled(
                24, 24,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            header.addWidget(icon_label)
        
        # Severity label
        severity_label = QLabel(severity.upper())
        severity_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {border_color};
        """)
        header.addWidget(severity_label)
        
        header.addStretch()
        
        # Timestamp
        timestamp = self.alert_data.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M:%S')
                date_str = dt.strftime('%Y-%m-%d')
                
                time_label = QLabel(f"{date_str} {time_str}")
                time_label.setStyleSheet(f"""
                    font-size: 11px;
                    color: {COLORS['text_secondary']};
                """)
                header.addWidget(time_label)
            except:
                pass
        
        layout.addLayout(header)
        
        # Message
        message = self.alert_data.get('message', 'No message')
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_primary']};
            line-height: 1.5;
        """)
        layout.addWidget(message_label)
        
        # Category (if present)
        category = self.alert_data.get('category', '')
        if category:
            category_label = QLabel(f"Category: {category}")
            category_label.setStyleSheet(f"""
                font-size: 11px;
                color: {COLORS['text_secondary']};
                font-style: italic;
            """)
            layout.addWidget(category_label)
        
        self.setLayout(layout)


class AlertsScreen(QWidget):
    """Alerts screen with filtering"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_client = APIClient()
        self.current_filter = 'all'
        self.setup_ui()
        self.setup_timers()
    
    def setup_ui(self):
        """Setup alerts UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("System Alerts")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        header.addWidget(title)
        header.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton()
        icon_path = ICONS_DIR / ICONS['refresh']
        if icon_path.exists():
            refresh_btn.setIcon(QIcon(str(icon_path)))
            refresh_btn.setIconSize(QSize(20, 20))
        refresh_btn.setText("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)
        
        layout.addLayout(header)
        
        # Filter buttons
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)
        
        self.filter_group = QButtonGroup()
        self.filter_group.setExclusive(True)
        
        filters = [
            ('all', 'All Alerts'),
            ('info', 'Info'),
            ('warning', 'Warnings'),
            ('error', 'Errors'),
        ]
        
        for filter_id, label in filters:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(filter_id == 'all')
            btn.clicked.connect(lambda checked, f=filter_id: self.set_filter(f))
            
            if filter_id == 'all':
                btn.setProperty("class", "primary")
            
            self.filter_group.addButton(btn)
            filter_layout.addWidget(btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Alert count
        self.count_label = QLabel("0 alerts")
        self.count_label.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_secondary']};
        """)
        layout.addWidget(self.count_label)
        
        # Alerts list in scroll area
        self.alerts_container = QWidget()
        self.alerts_layout = QVBoxLayout()
        self.alerts_layout.setSpacing(12)
        self.alerts_layout.addStretch()
        self.alerts_container.setLayout(self.alerts_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self.alerts_container)
        
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def setup_timers(self):
        """Setup update timers"""
        self.alert_timer = QTimer()
        self.alert_timer.timeout.connect(self.refresh)
        self.alert_timer.start(ALERT_CHECK_INTERVAL * 1000)
        
        # Initial load
        self.refresh()
    
    def refresh(self):
        """Refresh alerts from API"""
        try:
            alerts = self.api_client.get_alerts()
            self.display_alerts(alerts)
        except Exception as e:
            print(f"Error loading alerts: {e}")
            self.display_error()
    
    def display_alerts(self, alerts: list):
        """Display alerts in the list"""
        # Clear existing alerts
        while self.alerts_layout.count() > 1:
            item = self.alerts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Filter alerts
        if self.current_filter != 'all':
            alerts = [a for a in alerts if a.get('severity') == self.current_filter]
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Update count
        self.count_label.setText(f"{len(alerts)} alert{'s' if len(alerts) != 1 else ''}")
        
        # Display alerts
        if alerts:
            for alert in alerts:
                alert_item = AlertItem(alert)
                self.alerts_layout.insertWidget(
                    self.alerts_layout.count() - 1, 
                    alert_item
                )
        else:
            # No alerts message
            no_alerts = QLabel("No alerts to display")
            no_alerts.setStyleSheet(f"""
                font-size: 14px;
                color: {COLORS['text_secondary']};
                padding: 40px;
            """)
            no_alerts.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.alerts_layout.insertWidget(
                self.alerts_layout.count() - 1,
                no_alerts
            )
    
    def display_error(self):
        """Display error message"""
        while self.alerts_layout.count() > 1:
            item = self.alerts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        error_label = QLabel("Failed to load alerts")
        error_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['error']};
            padding: 40px;
        """)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.alerts_layout.insertWidget(
            self.alerts_layout.count() - 1,
            error_label
        )
    
    def set_filter(self, filter_id: str):
        """Set alert filter"""
        self.current_filter = filter_id
        self.refresh()
