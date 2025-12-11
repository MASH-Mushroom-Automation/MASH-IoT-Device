#!/usr/bin/env python3
"""
Standalone Bluetooth Agent Test Script
Tests the persistent D-Bus Bluetooth agent for "Just Works" pairing

Run this script to verify the agent works before starting the full server.
Keep this running and try to pair from your phone/desktop.
"""

import logging
import time
import sys
import signal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import the agent
from src.utils.bluetooth_agent import start_bluetooth_agent, stop_bluetooth_agent, get_agent_manager

def main():
    """Test the Bluetooth agent"""
    
    device_name = "MASH-IoT-Device"
    
    logger.info("=" * 60)
    logger.info("Bluetooth Agent Test Script")
    logger.info("=" * 60)
    logger.info(f"Device Name: {device_name}")
    logger.info("Capability: NoInputNoOutput (Just Works)")
    logger.info("")
    logger.info("This test will:")
    logger.info("  1. Start a persistent Bluetooth agent")
    logger.info("  2. Make the device discoverable and pairable")
    logger.info("  3. Keep running until you press Ctrl+C")
    logger.info("")
    logger.info("Try pairing from your phone/desktop while this runs.")
    logger.info("=" * 60)
    logger.info("")
    
    # Signal handler for clean shutdown
    def signal_handler(sig, frame):
        logger.info("\n" + "=" * 60)
        logger.info("Shutting down Bluetooth agent...")
        logger.info("=" * 60)
        stop_bluetooth_agent()
        logger.info("Bluetooth agent stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the agent
    logger.info("Starting Bluetooth agent...")
    
    if start_bluetooth_agent(device_name):
        logger.info("✅ Bluetooth agent started successfully!")
        logger.info("")
        logger.info("=" * 60)
        logger.info("STATUS: READY FOR PAIRING")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Instructions:")
        logger.info("  1. On your phone/desktop, open Bluetooth settings")
        logger.info(f"  2. Look for device: {device_name}")
        logger.info("  3. Tap to pair - it should connect instantly")
        logger.info("  4. Watch this terminal for pairing events")
        logger.info("")
        logger.info("Press Ctrl+C to stop the agent")
        logger.info("=" * 60)
        logger.info("")
        
        # Get agent manager for status checks
        agent_mgr = get_agent_manager()
        
        # Keep running and show status
        try:
            while True:
                if agent_mgr.is_running():
                    logger.info("Agent Status: RUNNING (waiting for pairing requests...)")
                else:
                    logger.error("❌ Agent stopped unexpectedly!")
                    break
                
                time.sleep(30)  # Status update every 30 seconds
        
        except KeyboardInterrupt:
            logger.info("\nInterrupted by user")
        
    else:
        logger.error("❌ Failed to start Bluetooth agent")
        logger.error("")
        logger.error("Troubleshooting:")
        logger.error("  1. Make sure python3-dbus and python3-gi are installed:")
        logger.error("     sudo apt install python3-dbus python3-gi")
        logger.error("  2. Make sure Bluetooth service is running:")
        logger.error("     sudo systemctl status bluetooth")
        logger.error("  3. Check if hci0 adapter is available:")
        logger.error("     hciconfig")
        logger.error("  4. Try restarting Bluetooth:")
        logger.error("     sudo systemctl restart bluetooth")
        sys.exit(1)
    
    # Clean shutdown
    logger.info("\nStopping Bluetooth agent...")
    stop_bluetooth_agent()
    logger.info("Test complete")


if __name__ == '__main__':
    main()
