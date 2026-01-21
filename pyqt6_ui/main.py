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
from setup_flow import SetupFlowWindow


def is_first_time_setup() -> bool:
    """Check if this is the first time the device is being set up"""
    setup_file = parent_dir / "pyqt6_ui" / ".setup_complete"
    return not setup_file.exists()


def mark_setup_complete():
    """Mark setup as complete"""
    setup_file = parent_dir / "pyqt6_ui" / ".setup_complete"
    # Ensure parent directory exists
    setup_file.parent.mkdir(parents=True, exist_ok=True)
    setup_file.touch()


def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(WINDOW_TITLE)
    
    # Enable touch events globally
    app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeTouchForUnhandledMouseEvents, True)
    
    # Apply stylesheet
    app.setStyleSheet(get_stylesheet())
    
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
    
    # Check if first-time setup is needed
    if is_first_time_setup():
        # Show setup flow
        window = SetupFlowWindow()
        window.setup_complete.connect(lambda: (
            mark_setup_complete(),
            window.close(),
            show_main_window()
        ))
    else:
        # Show main window directly
        window = MainWindow()
    
    window.show()
    
    # Run application event loop
    sys.exit(app.exec())


def show_main_window():
    """Show the main application window after setup"""
    window = MainWindow()
    window.show()


if __name__ == '__main__':
    main()
