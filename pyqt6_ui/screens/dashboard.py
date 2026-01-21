"""
MASH IoT Device - Dashboard Screen
Real-time sensor data with charts and status indicators
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon, QColor
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from datetime import datetime, timedelta

from config import (
    COLORS, ICONS_DIR, ICONS, THRESHOLDS, 
    SENSOR_UPDATE_INTERVAL, CHART_HISTORY_MINUTES
)
from api_client import APIClient
from icon_utils import load_svg_icon, create_icon


class SensorCard(QFrame):
    """Card displaying sensor value with icon and trend"""
    
    def __init__(self, name: str, icon_name: str, unit: str, color: str, parent=None):
        super().__init__(parent)
        self.name = name
        self.unit = unit
        self.color = color
        self.setup_ui(icon_name)
    
    def setup_ui(self, icon_name: str):
        """Setup card UI"""
        self.setProperty("class", "card")
        self.setMinimumHeight(160)
        self.setMinimumWidth(220)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        
        # Header with icon and name
        header = QHBoxLayout()
        header.setSpacing(10)
        
        # Icon
        icon_path = ICONS_DIR / icon_name
        if icon_path.exists():
            icon_label = QLabel()
            pixmap = load_svg_icon(icon_path, 32, self.color)
            icon_label.setPixmap(pixmap)
            header.addWidget(icon_label)
        
        # Name
        name_label = QLabel(self.name.replace('_', ' ').title())
        name_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        name_label.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 600;
            color: {COLORS['text_secondary']};
        """)
        header.addWidget(name_label)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Value
        self.value_label = QLabel("--")
        self.value_label.setProperty("class", "sensor-value")
        self.value_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.value_label.setStyleSheet(f"""
            font-size: 42px;
            font-weight: bold;
            color: {self.color};
        """)
        layout.addWidget(self.value_label)
        
        # Unit and status
        bottom = QHBoxLayout()
        
        self.unit_label = QLabel(self.unit)
        self.unit_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.unit_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 500;
            color: {COLORS['text_secondary']};
        """)
        bottom.addWidget(self.unit_label)
        bottom.addStretch()
        
        self.status_label = QLabel("Normal")
        self.status_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.status_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['success']};
            font-weight: 600;
        """)
        bottom.addWidget(self.status_label)
        
        layout.addLayout(bottom)
        
        self.setLayout(layout)
    
    def update_value(self, value: float, status: str = "Normal"):
        """Update sensor value and status"""
        self.value_label.setText(f"{value:.1f}")
        self.status_label.setText(status)
        
        # Update status color
        if status == "Normal" or status == "Optimal":
            color = COLORS['success']
        elif status == "Warning":
            color = COLORS['warning']
        else:
            color = COLORS['error']
        
        self.status_label.setStyleSheet(f"""
            font-size: 14px;
            color: {color};
            font-weight: 600;
        """)


class SensorChart(QFrame):
    """Chart widget for sensor history"""
    
    def __init__(self, title: str, color: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.color = color
        self.data_points = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup chart UI"""
        self.setProperty("class", "card")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        layout.addWidget(title_label)
        
        # Chart
        self.series = QLineSeries()
        self.series.setColor(QColor(self.color))
        
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        self.chart.setBackgroundBrush(QColor(COLORS['card']))
        self.chart.setPlotAreaBackgroundBrush(QColor(COLORS['surface']))
        self.chart.setPlotAreaBackgroundVisible(True)
        self.chart.legend().hide()
        
        # Axes
        self.axis_x = QValueAxis()
        self.axis_x.setLabelFormat("%d min")
        self.axis_x.setTitleText("Time")
        self.axis_x.setRange(0, CHART_HISTORY_MINUTES)
        
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Value")
        
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        
        # Chart view
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(chart_view.renderHints())
        chart_view.setMinimumHeight(200)
        
        layout.addWidget(chart_view)
        
        self.setLayout(layout)
    
    def add_data_point(self, value: float):
        """Add new data point to chart"""
        timestamp = datetime.now()
        self.data_points.append((timestamp, value))
        
        # Keep only last 30 minutes
        cutoff = timestamp - timedelta(minutes=CHART_HISTORY_MINUTES)
        self.data_points = [(t, v) for t, v in self.data_points if t > cutoff]
        
        # Update series
        self.series.clear()
        if self.data_points:
            start_time = self.data_points[0][0]
            for t, v in self.data_points:
                minutes_elapsed = (t - start_time).total_seconds() / 60
                self.series.append(minutes_elapsed, v)
            
            # Update Y axis range
            values = [v for _, v in self.data_points]
            if values:
                min_val = min(values)
                max_val = max(values)
                padding = (max_val - min_val) * 0.1
                self.axis_y.setRange(min_val - padding, max_val + padding)


class DashboardScreen(QWidget):
    """Main dashboard screen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_client = APIClient()
        self.setup_ui()
        self.setup_timers()
    
    def setup_ui(self):
        """Setup dashboard UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("Dashboard")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        header.addWidget(title)
        header.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton()
        icon_path = ICONS_DIR / ICONS['refresh']
        if icon_path.exists():
            refresh_btn.setIcon(create_icon(icon_path, 20, COLORS['text_primary']))
            refresh_btn.setIconSize(QSize(20, 20))
        refresh_btn.setText("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)
        
        layout.addLayout(header)
        
        # Sensor cards grid
        cards_grid = QGridLayout()
        cards_grid.setSpacing(16)
        
        self.sensor_cards = {
            'co2': SensorCard('CO2', ICONS['co2'], 'ppm', COLORS['co2_color']),
            'temperature': SensorCard('Temperature', ICONS['temperature'], '°C', COLORS['temperature_color']),
            'humidity': SensorCard('Humidity', ICONS['humidity'], '%', COLORS['humidity_color']),
        }
        
        cards_grid.addWidget(self.sensor_cards['co2'], 0, 0)
        cards_grid.addWidget(self.sensor_cards['temperature'], 0, 1)
        cards_grid.addWidget(self.sensor_cards['humidity'], 0, 2)
        
        layout.addLayout(cards_grid)
        
        # Charts
        charts_layout = QVBoxLayout()
        charts_layout.setSpacing(16)
        
        self.charts = {
            'co2': SensorChart('CO2 Trend (30 min)', COLORS['co2']),
            'temperature': SensorChart('Temperature Trend (30 min)', COLORS['temperature']),
            'humidity': SensorChart('Humidity Trend (30 min)', COLORS['humidity']),
        }
        
        for chart in self.charts.values():
            charts_layout.addWidget(chart)
        
        # Scroll area for charts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Enable kinetic scrolling for touch
        scroll.setProperty("kineticScrollingEnabled", True)
        scroll.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        
        chart_container = QWidget()
        chart_container.setLayout(charts_layout)
        scroll.setWidget(chart_container)
        
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def setup_timers(self):
        """Setup update timers"""
        # Sensor update timer
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.update_sensors)
        self.sensor_timer.start(SENSOR_UPDATE_INTERVAL * 1000)
        
        # Initial update
        self.update_sensors()
    
    def update_sensors(self):
        """Update sensor readings"""
        try:
            data = self.api_client.get_sensor_data()
            
            if data:
                # Update CO2
                if 'co2' in data:
                    co2 = data['co2']
                    status = self.get_sensor_status('co2', co2)
                    self.sensor_cards['co2'].update_value(co2, status)
                    self.charts['co2'].add_data_point(co2)
                
                # Update Temperature
                if 'temperature' in data:
                    temp = data['temperature']
                    status = self.get_sensor_status('temperature', temp)
                    self.sensor_cards['temperature'].update_value(temp, status)
                    self.charts['temperature'].add_data_point(temp)
                
                # Update Humidity
                if 'humidity' in data:
                    hum = data['humidity']
                    status = self.get_sensor_status('humidity', hum)
                    self.sensor_cards['humidity'].update_value(hum, status)
                    self.charts['humidity'].add_data_point(hum)
        
        except Exception as e:
            print(f"Error updating sensors: {e}")
    
    def get_sensor_status(self, sensor: str, value: float) -> str:
        """Determine sensor status based on thresholds"""
        if sensor not in THRESHOLDS:
            return "Normal"
        
        thresholds = THRESHOLDS[sensor]
        
        if thresholds['optimal_min'] <= value <= thresholds['optimal_max']:
            return "Optimal"
        elif thresholds['min'] <= value <= thresholds['max']:
            return "Normal"
        elif value < thresholds['min'] or value > thresholds['max']:
            return "Critical"
        else:
            return "Warning"
    
    def refresh(self):
        """Refresh dashboard data"""
        self.update_sensors()
