#!/usr/bin/env python3
"""
Bluetooth Fix Utility
Helps diagnose and fix Bluetooth visibility issues
"""

import os
import sys
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_command(cmd, check=False):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Error running command {cmd}: {e}")
        return f"Error: {e}"

def restart_bluetooth():
    """Restart Bluetooth service"""
    logger.info("Restarting Bluetooth service...")
    run_command(['sudo', 'systemctl', 'restart', 'bluetooth'])
    time.sleep(2)
    status = run_command(['systemctl', 'is-active', 'bluetooth'])
    logger.info(f"Bluetooth service status: {status}")
    return status == "active"

def set_device_name(name):
    """Set Bluetooth device name"""
    logger.info(f"Setting Bluetooth device name to: {name}")
    run_command(['sudo', 'hciconfig', 'hci0', 'name', name])
    
    # Also update the main.conf file
    try:
        # Create a temporary config file with proper content
        config_content = f"[General]\nName = {name}\nDiscoverableTimeout = 0\n"
        
        # Use echo and sudo to write directly to the file
        echo_cmd = ['echo', '-e', config_content]
        echo_process = subprocess.Popen(echo_cmd, stdout=subprocess.PIPE)
        sudo_cmd = ['sudo', 'tee', '/etc/bluetooth/main.conf']
        sudo_process = subprocess.Popen(sudo_cmd, stdin=echo_process.stdout)
        sudo_process.communicate()
        
        logger.info("Updated Bluetooth config file")
    except Exception as e:
        logger.error(f"Error updating Bluetooth config: {e}")

def fix_raspberry_pi_bluetooth():
    """Fix common Raspberry Pi Bluetooth issues"""
    logger.info("Applying Raspberry Pi specific fixes...")
    
    # Fix for Raspberry Pi Bluetooth service
    try:
        # Check if we're on a Raspberry Pi
        if os.path.exists('/proc/device-tree/model'):
            with open('/proc/device-tree/model') as f:
                model = f.read()
                if 'Raspberry Pi' in model:
                    logger.info(f"Detected Raspberry Pi: {model}")
                    
                    # Fix for Bluetooth not starting properly
                    logger.info("Applying Raspberry Pi Bluetooth fixes...")
                    
                    # Restart bluetooth service
                    run_command(['sudo', 'systemctl', 'restart', 'bluetooth'])
                    time.sleep(2)
                    
                    # Make sure the hciuart service is running (for onboard Bluetooth)
                    run_command(['sudo', 'systemctl', 'restart', 'hciuart'])
                    time.sleep(2)
                    
                    # Check if dtoverlay=pi3-disable-bt is in config.txt
                    config_txt = run_command(['cat', '/boot/config.txt'])
                    if 'dtoverlay=pi3-disable-bt' in config_txt:
                        logger.warning("Bluetooth is disabled in /boot/config.txt!")
                        logger.warning("Remove 'dtoverlay=pi3-disable-bt' from /boot/config.txt and reboot")
                    
                    return True
    except Exception as e:
        logger.error(f"Error applying Raspberry Pi fixes: {e}")
    
    return False

def power_on_adapter():
    """Power on the Bluetooth adapter"""
    logger.info("Powering on Bluetooth adapter...")
    run_command(['sudo', 'hciconfig', 'hci0', 'up'])
    time.sleep(1)
    status = run_command(['hciconfig'])
    if 'DOWN' in status:
        logger.warning("Adapter still appears to be down, trying alternative methods")
        # Try rfkill
        run_command(['sudo', 'rfkill', 'unblock', 'bluetooth'])
        time.sleep(1)
        # Try bluetoothctl power on
        process = subprocess.Popen(
            ['bluetoothctl'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        process.communicate(input="power on\nexit\n")
        time.sleep(1)

def make_discoverable():
    """Make device discoverable"""
    logger.info("Making device discoverable...")
    # First make sure it's powered on
    power_on_adapter()
    # Then set discoverable mode
    run_command(['sudo', 'hciconfig', 'hci0', 'piscan'])
    run_command(['sudo', 'hciconfig', 'hci0', 'sspmode', '1'])
    
    # Also try bluetoothctl
    try:
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
            "discoverable-timeout 0",
            "exit"
        ]
        
        process.communicate(input="\n".join(commands))
    except Exception as e:
        logger.error(f"Error with bluetoothctl: {e}")

def check_adapter_present():
    """Check if Bluetooth adapter is physically present"""
    logger.info("Checking for Bluetooth adapter...")
    
    # Check with lsusb for USB Bluetooth adapters
    lsusb_output = run_command(['lsusb'])
    if 'Bluetooth' in lsusb_output:
        logger.info("USB Bluetooth adapter found")
        return True
    
    # Check with lspci for PCI Bluetooth adapters
    lspci_output = run_command(['lspci'])
    if 'Bluetooth' in lspci_output:
        logger.info("PCI Bluetooth adapter found")
        return True
    
    # Check if hci0 exists
    hci_output = run_command(['hciconfig'])
    if 'hci0' in hci_output:
        logger.info("Bluetooth adapter hci0 found")
        return True
    
    # Check dmesg for Bluetooth
    dmesg_output = run_command(['dmesg', '|', 'grep', '-i', 'bluetooth'])
    if dmesg_output and 'bluetooth' in dmesg_output.lower():
        logger.info("Bluetooth mentioned in dmesg logs")
        return True
    
    logger.warning("No Bluetooth adapter detected!")
    return False

def show_bluetooth_info():
    """Show Bluetooth information"""
    logger.info("Bluetooth adapter information:")
    print("\n" + "="*50)
    print(run_command(['hciconfig', '-a']))
    print("="*50 + "\n")
    
    # Show rfkill status
    print("\nRFKill status:")
    print("="*50)
    print(run_command(['rfkill', 'list', 'bluetooth']))
    print("="*50 + "\n")

def main():
    """Main function"""
    device_name = "MASH-IoT-Device"
    if len(sys.argv) > 1:
        device_name = sys.argv[1]
    
    logger.info(f"Starting Bluetooth fix utility for device: {device_name}")
    
    # Check if running as root
    if os.geteuid() != 0:
        logger.warning("This script should be run as root (sudo) for best results")
    
    # Check if Bluetooth adapter is present
    if not check_adapter_present():
        logger.error("No Bluetooth adapter detected! Please check your hardware.")
        logger.info("If you're using a Raspberry Pi, make sure Bluetooth is enabled in raspi-config.")
        logger.info("Try running: sudo raspi-config > Interface Options > Bluetooth > Enable")
        return False
    
    # Show current status
    show_bluetooth_info()
    
    # Apply Raspberry Pi specific fixes if applicable
    fix_raspberry_pi_bluetooth()
    
    # Restart Bluetooth
    if restart_bluetooth():
        logger.info("Bluetooth service restarted successfully")
    else:
        logger.error("Failed to restart Bluetooth service")
    
    # Explicitly power on the adapter
    power_on_adapter()
    
    # Set device name
    set_device_name(device_name)
    
    # Make discoverable
    make_discoverable()
    
    # Show updated status
    time.sleep(1)
    show_bluetooth_info()
    
    logger.info("Bluetooth fix completed. Your device should now be visible.")
    logger.info("If your phone still can't see the device, try restarting the Bluetooth on your phone.")

if __name__ == "__main__":
    main()
