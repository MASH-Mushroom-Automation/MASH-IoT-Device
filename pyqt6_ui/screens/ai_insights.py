"""
MASH IoT Device - AI Insights Screen
Display automation decision history with reasoning
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon
from datetime import datetime

from config import COLORS, ICONS_DIR, ICONS, ALERT_CHECK_INTERVAL
from api_client import APIClient


class InsightCard(QFrame):
    """Card displaying single AI decision insight"""
    
    def __init__(self, insight_data: dict, parent=None):
        super().__init__(parent)
        self.insight_data = insight_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup insight card UI"""
        self.setProperty("class", "card")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        
        # Header with timestamp and action
        header = QHBoxLayout()
        header.setSpacing(10)
        
        # AI icon
        icon_path = ICONS_DIR / ICONS['ai_insights']
        if icon_path.exists():
            icon_label = QLabel()
            pixmap = QPixmap(str(icon_path))
            icon_label.setPixmap(pixmap.scaled(
                28, 28,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            header.addWidget(icon_label)
        
        # Action
        action = self.insight_data.get('action', 'System Action')
        action_label = QLabel(action)
        action_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        header.addWidget(action_label)
        
        header.addStretch()
        
        # Timestamp
        timestamp = self.insight_data.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M:%S')
                date_str = dt.strftime('%m/%d')
                
                time_label = QLabel(f"{date_str} {time_str}")
                time_label.setStyleSheet(f"""
                    font-size: 12px;
                    color: {COLORS['text_secondary']};
                """)
                header.addWidget(time_label)
            except:
                pass
        
        layout.addLayout(header)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {COLORS['border']};")
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        
        # Reasoning
        reasoning = self.insight_data.get('reasoning', 'No reasoning provided')
        
        reasoning_header = QLabel("AI Reasoning:")
        reasoning_header.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {COLORS['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(reasoning_header)
        
        reasoning_label = QLabel(reasoning)
        reasoning_label.setWordWrap(True)
        reasoning_label.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_primary']};
            line-height: 1.6;
        """)
        layout.addWidget(reasoning_label)
        
        # Sensor data (if present)
        sensor_data = self.insight_data.get('sensor_data', {})
        if sensor_data:
            layout.addSpacing(8)
            
            sensor_header = QLabel("Sensor Readings:")
            sensor_header.setStyleSheet(f"""
                font-size: 12px;
                font-weight: 600;
                color: {COLORS['text_secondary']};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            """)
            layout.addWidget(sensor_header)
            
            sensor_grid = QHBoxLayout()
            sensor_grid.setSpacing(20)
            
            # CO2
            if 'co2' in sensor_data:
                co2_widget = self.create_sensor_widget(
                    'CO2', 
                    sensor_data['co2'], 
                    'ppm',
                    COLORS['co2']
                )
                sensor_grid.addWidget(co2_widget)
            
            # Temperature
            if 'temperature' in sensor_data:
                temp_widget = self.create_sensor_widget(
                    'Temp', 
                    sensor_data['temperature'], 
                    '°C',
                    COLORS['temperature']
                )
                sensor_grid.addWidget(temp_widget)
            
            # Humidity
            if 'humidity' in sensor_data:
                hum_widget = self.create_sensor_widget(
                    'Humidity', 
                    sensor_data['humidity'], 
                    '%',
                    COLORS['humidity']
                )
                sensor_grid.addWidget(hum_widget)
            
            sensor_grid.addStretch()
            layout.addLayout(sensor_grid)
        
        self.setLayout(layout)
    
    def create_sensor_widget(self, name: str, value: float, unit: str, color: str) -> QWidget:
        """Create small sensor display widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            font-size: 11px;
            color: {COLORS['text_secondary']};
        """)
        layout.addWidget(name_label)
        
        value_label = QLabel(f"{value:.1f} {unit}")
        value_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {color};
        """)
        layout.addWidget(value_label)
        
        widget.setLayout(layout)
        return widget


class AIInsightsScreen(QWidget):
    """AI Insights screen showing automation decisions"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_client = APIClient()
        self.setup_ui()
        self.setup_timers()
    
    def setup_ui(self):
        """Setup insights UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("AI Insights")
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
        
        # Description
        desc = QLabel("View automation decisions and the reasoning behind each action.")
        desc.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_secondary']};
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Insights count
        self.count_label = QLabel("0 decisions")
        self.count_label.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_secondary']};
        """)
        layout.addWidget(self.count_label)
        
        # Insights list in scroll area
        self.insights_container = QWidget()
        self.insights_layout = QVBoxLayout()
        self.insights_layout.setSpacing(16)
        self.insights_layout.addStretch()
        self.insights_container.setLayout(self.insights_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self.insights_container)
        
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def setup_timers(self):
        """Setup update timers"""
        self.insights_timer = QTimer()
        self.insights_timer.timeout.connect(self.refresh)
        self.insights_timer.start(ALERT_CHECK_INTERVAL * 1000)
        
        # Initial load
        self.refresh()
    
    def refresh(self):
        """Refresh insights from API"""
        try:
            history = self.api_client.get_automation_history()
            self.display_insights(history)
        except Exception as e:
            print(f"Error loading AI insights: {e}")
            self.display_error()
    
    def display_insights(self, insights: list):
        """Display insights in the list"""
        # Clear existing insights
        while self.insights_layout.count() > 1:
            item = self.insights_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Sort by timestamp (newest first)
        insights.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Update count
        self.count_label.setText(f"{len(insights)} decision{'s' if len(insights) != 1 else ''}")
        
        # Display insights
        if insights:
            for insight in insights:
                insight_card = InsightCard(insight)
                self.insights_layout.insertWidget(
                    self.insights_layout.count() - 1,
                    insight_card
                )
        else:
            # No insights message
            no_insights = QLabel("No AI decisions recorded yet")
            no_insights.setStyleSheet(f"""
                font-size: 14px;
                color: {COLORS['text_secondary']};
                padding: 40px;
            """)
            no_insights.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.insights_layout.insertWidget(
                self.insights_layout.count() - 1,
                no_insights
            )
    
    def display_error(self):
        """Display error message"""
        while self.insights_layout.count() > 1:
            item = self.insights_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        error_label = QLabel("Failed to load AI insights")
        error_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['error']};
            padding: 40px;
        """)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.insights_layout.insertWidget(
            self.insights_layout.count() - 1,
            error_label
        )
