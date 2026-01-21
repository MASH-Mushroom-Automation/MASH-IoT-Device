"""
QR Code Screen - Show QR code for MASH Grower Mobile App download
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from config import COLORS, FONTS
from pathlib import Path


class QRCodeScreen(QWidget):
    """QR Code screen for mobile app download"""
    
    next_clicked = pyqtSignal()
    skip_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Content area (top 60%)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        
        # Header
        header = QLabel("Download MASH Grower App")
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['heading']}px;
            font-weight: 700;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(header)
        
        # Description
        desc = QLabel("Scan this QR code with your phone to download the MASH Grower mobile app")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['body']}px;
            margin-bottom: 10px;
        """)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(desc)
        
        # QR Code
        qr_container = QHBoxLayout()
        qr_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Load QR code image
        qr_path = Path(__file__).parent.parent.parent / "touchscreen_ui" / "assets" / "images" / "qrcode200x200.png"
        if qr_path.exists():
            pixmap = QPixmap(str(qr_path))
            qr_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, 
                                            Qt.TransformationMode.SmoothTransformation))
        else:
            # Fallback text if image not found
            qr_label.setText("QR Code Image Not Found")
            qr_label.setStyleSheet(f"""
                color: {COLORS['text_secondary']};
                font-size: {FONTS['body']}px;
                padding: 40px;
                background: {COLORS['card_bg']};
                border-radius: 12px;
            """)
        
        qr_container.addWidget(qr_label)
        content_layout.addLayout(qr_container)
        
        # Info text
        info = QLabel("The mobile app allows you to monitor and control your grow chamber remotely")
        info.setWordWrap(True)
        info.setStyleSheet(f"""
            color: {COLORS['text_tertiary']};
            font-size: {FONTS['body_small']}px;
            margin-top: 10px;
        """)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(info)
        
        main_layout.addLayout(content_layout)
        
        # Bottom spacer for keyboard
        main_layout.addSpacerItem(QSpacerItem(20, 150, 
                                              QSizePolicy.Policy.Minimum, 
                                              QSizePolicy.Policy.Expanding))
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        btn_skip = QPushButton("Skip")
        btn_skip.setMinimumHeight(50)
        btn_skip.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-size: {FONTS['button']}px;
                font-weight: 600;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover_bg']};
            }}
        """)
        btn_skip.clicked.connect(self.skip_clicked.emit)
        buttons_layout.addWidget(btn_skip, 1)
        
        btn_continue = QPushButton("Continue")
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
        buttons_layout.addWidget(btn_continue, 2)
        
        main_layout.addLayout(buttons_layout)
