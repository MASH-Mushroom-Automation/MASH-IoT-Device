"""
MASH IoT Device - PyQt6 Main Application
Modern touchscreen interface for mushroom grow automation
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for .env loading
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Load environment variables
from dotenv import load_dotenv
env_path = parent_dir / "touchscreen_ui" / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded environment from: {env_path}")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from config import get_stylesheet, WINDOW_TITLE, SCREEN_WIDTH, SCREEN_HEIGHT, MOCK_MODE
from main_window import MainWindow


def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(WINDOW_TITLE)
    
    # Apply stylesheet
    app.setStyleSheet(get_stylesheet())
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Print startup info
    mode = "DEMO MODE (Mock Data)" if MOCK_MODE else "Production Mode"
    print(f"""
╔══════════════════════════════════════════════╗
║        MASH IoT Device - PyQt6 UI           ║
╚══════════════════════════════════════════════╝

Mode: {mode}
Resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}
Framework: PyQt6
Backend: Flask REST API

Ready! Access the touchscreen interface.
    """)
    
    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
