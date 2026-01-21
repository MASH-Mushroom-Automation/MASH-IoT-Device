"""
Setup Flow Window - Orchestrates the initial device setup process
"""
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget
from PyQt6.QtCore import pyqtSignal
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, MOCK_MODE
from screens.welcome import WelcomeScreen
from screens.onboarding import OnboardingScreen
from screens.wifi_setup import WiFiSetupScreen
from screens.qr_code_screen import QRCodeScreen
from screens.setup_complete import SetupCompleteScreen


class SetupFlowWindow(QMainWindow):
    """Main window for setup flow"""
    
    setup_complete = pyqtSignal()  # Emitted when setup is complete
    
    def __init__(self):
        super().__init__()
        
        # Initialize API client based on mode
        if MOCK_MODE:
            import sys
            from pathlib import Path
            # Add parent directory to path for touchscreen_ui import
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            from touchscreen_ui.mock_api_client import MockAPIClient
            self.api_client = MockAPIClient()
        else:
            # Import real API client
            import sys
            from pathlib import Path
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            from touchscreen_ui.api_client import APIClient
            self.api_client = APIClient()
        
        self.chamber_config = {}
        self.device_info = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle(f"{WINDOW_TITLE} - Setup")
        self.setMinimumSize(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.resize(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Create stacked widget for screens
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Create setup screens in order
        self.welcome_screen = WelcomeScreen()
        self.onboarding_screen = OnboardingScreen()
        self.wifi_screen = WiFiSetupScreen(self.api_client)
        self.qr_code_screen = QRCodeScreen()
        self.complete_screen = SetupCompleteScreen()
        
        # Add screens to stack
        self.stack.addWidget(self.welcome_screen)      # Index 0 - Title Page
        self.stack.addWidget(self.onboarding_screen)   # Index 1 - Onboarding
        self.stack.addWidget(self.wifi_screen)         # Index 2 - WiFi Setup
        self.stack.addWidget(self.qr_code_screen)      # Index 3 - QR Code
        self.stack.addWidget(self.complete_screen)     # Index 4 - Welcome to MASH
        
        # Connect signals for flow
        self.welcome_screen.start_setup.connect(self.show_onboarding)
        self.onboarding_screen.next_clicked.connect(self.show_wifi_setup)
        
        self.wifi_screen.wifi_configured.connect(self.show_qr_code)
        self.wifi_screen.skip_setup.connect(self.show_qr_code)
        
        self.qr_code_screen.next_clicked.connect(self.show_setup_complete)
        self.qr_code_screen.skip_clicked.connect(self.show_setup_complete)
        
        self.complete_screen.finish_setup.connect(self.setup_complete.emit)
        
        # Start with welcome screen
        self.stack.setCurrentIndex(0)
    
    def show_onboarding(self):
        """Show onboarding screen"""
        self.stack.setCurrentIndex(1)
    
    def show_wifi_setup(self):
        """Show WiFi setup screen"""
        self.stack.setCurrentIndex(2)
    
    def show_qr_code(self):
        """Show QR code screen"""
        self.stack.setCurrentIndex(3)
    
    def show_setup_complete(self):
        """Show setup complete screen"""
        self.stack.setCurrentIndex(4)
