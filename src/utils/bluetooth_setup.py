"""
Bluetooth Setup Utility
Provides functions to configure system-level Bluetooth settings
"""

import os
import subprocess
import logging
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def check_bluetooth_service() -> bool:
    """Check if Bluetooth service is running"""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', 'bluetooth'],
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip() == 'active'
    except Exception as e:
        logger.error(f"Failed to check Bluetooth service: {e}")
        return False

def restart_bluetooth_service() -> bool:
    """Restart Bluetooth service"""
    try:
        logger.info("Restarting Bluetooth service...")
        subprocess.run(['sudo', 'systemctl', 'restart', 'bluetooth'], check=False)
        time.sleep(2)  # Give it time to restart
        return check_bluetooth_service()
    except Exception as e:
        logger.error(f"Failed to restart Bluetooth service: {e}")
        return False

def set_device_name(name: str) -> bool:
    """Set Bluetooth device name at system level"""
    try:
        # Update Bluetooth configuration file
        config_path = '/etc/bluetooth/main.conf'
        
        # Check if we can write to the file
        if not os.access(config_path, os.W_OK):
            logger.warning(f"No write access to {config_path}, trying with sudo")
            # Create a temporary file with our changes
            with open('/tmp/bluetooth_main.conf', 'w') as f:
                f.write(f"[General]\nName = {name}\nDiscoverableTimeout = 0\n")
            
            # Use sudo to copy it to the right place
            subprocess.run(['sudo', 'cp', '/tmp/bluetooth_main.conf', config_path], check=False)
        else:
            # We have write access, update directly
            with open(config_path, 'w') as f:
                f.write(f"[General]\nName = {name}\nDiscoverableTimeout = 0\n")
        
        # Restart Bluetooth service to apply changes
        return restart_bluetooth_service()
    except Exception as e:
        logger.error(f"Failed to set Bluetooth device name: {e}")
        return False

def make_always_discoverable() -> bool:
    """Make Bluetooth device always discoverable"""
    try:
        # Try using bluetoothctl
        process = subprocess.Popen(
            ['bluetoothctl'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        commands = [
            "power on",
            "discoverable on",
            "pairable on",
            "discoverable-timeout 0",  # 0 means always discoverable
            "exit"
        ]
        
        process.communicate(input="\n".join(commands))
        
        # Also try using hciconfig for older systems
        subprocess.run(['sudo', 'hciconfig', 'hci0', 'piscan'], check=False)
        
        logger.info("Bluetooth set to always discoverable")
        return True
    except Exception as e:
        logger.error(f"Failed to make Bluetooth always discoverable: {e}")
        return False

def setup_bluetooth(device_name: str) -> Dict[str, Any]:
    """
    Complete Bluetooth setup
    
    Args:
        device_name: Name for the Bluetooth device
        
    Returns:
        Status dictionary
    """
    status = {
        'service_running': False,
        'name_set': False,
        'discoverable': False,
        'success': False
    }
    
    # Check if Bluetooth service is running
    status['service_running'] = check_bluetooth_service()
    if not status['service_running']:
        logger.warning("Bluetooth service not running, attempting to restart")
        status['service_running'] = restart_bluetooth_service()
    
    if status['service_running']:
        # Set device name
        status['name_set'] = set_device_name(device_name)
        
        # Make always discoverable
        status['discoverable'] = make_always_discoverable()
        
        # Overall success
        status['success'] = status['name_set'] and status['discoverable']
    
    return status
