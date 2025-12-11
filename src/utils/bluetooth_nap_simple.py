"""
Simple Bluetooth Network Access Point (NAP) Setup
Creates a network bridge so phone can access Pi's HTTP server via Bluetooth
"""

import logging
import subprocess
import os

logger = logging.getLogger(__name__)


def setup_bluetooth_nap():
    """
    Setup Bluetooth Network Access Point (NAP)
    This allows phones to connect and get network access to the Pi
    """
    try:
        logger.info("Setting up Bluetooth Network Access Point (NAP)...")
        
        # 1. Enable Bluetooth NAP in bluetoothd config
        logger.info("Configuring bluetoothd for NAP...")
        
        # Check if bt-network service exists
        result = subprocess.run(
            ['systemctl', 'list-unit-files', 'bt-network.service'],
            capture_output=True,
            text=True
        )
        
        if 'bt-network.service' in result.stdout:
            logger.info("bt-network service found, enabling...")
            
            # Enable and start bt-network service
            subprocess.run(['sudo', 'systemctl', 'enable', 'bt-network'], check=False)
            subprocess.run(['sudo', 'systemctl', 'start', 'bt-network'], check=False)
            
            logger.info("bt-network service started")
        else:
            logger.warning("bt-network service not found, using manual setup")
            
            # Manual NAP setup using bt-network command
            # This creates a network bridge on bnep0
            subprocess.run(
                ['sudo', 'bt-network', '-s', 'nap', 'bridge'],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # 2. Configure network bridge
        logger.info("Configuring network bridge...")
        
        # Create bridge interface
        subprocess.run(['sudo', 'brctl', 'addbr', 'pan0'], check=False)
        
        # Assign IP to bridge
        subprocess.run(['sudo', 'ifconfig', 'pan0', '192.168.44.1', 'netmask', '255.255.255.0'], check=False)
        subprocess.run(['sudo', 'ifconfig', 'pan0', 'up'], check=False)
        
        logger.info("Bluetooth NAP configured successfully")
        logger.info("Devices can connect via Bluetooth and access: http://192.168.44.1:5000")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup Bluetooth NAP: {e}")
        logger.info("Trying alternative simple approach...")
        
        # Alternative: Just assign IP to bnep0 when it appears
        try:
            # This will be applied when a device connects
            logger.info("Setting up bnep0 auto-configuration...")
            
            # Create a simple script to configure bnep0 when it appears
            script_content = """#!/bin/bash
# Auto-configure bnep0 when Bluetooth device connects

if [ "$1" = "bnep0" ] && [ "$2" = "up" ]; then
    ifconfig bnep0 192.168.44.1 netmask 255.255.255.0
    echo "bnep0 configured with IP 192.168.44.1"
fi
"""
            
            script_path = '/etc/network/if-up.d/bnep0-config'
            
            # Write script
            with open('/tmp/bnep0-config', 'w') as f:
                f.write(script_content)
            
            # Move to if-up.d and make executable
            subprocess.run(['sudo', 'mv', '/tmp/bnep0-config', script_path], check=False)
            subprocess.run(['sudo', 'chmod', '+x', script_path], check=False)
            
            logger.info("bnep0 auto-configuration script installed")
            logger.info("When phone connects via Bluetooth, bnep0 will get IP 192.168.44.1")
            
            return True
            
        except Exception as e2:
            logger.error(f"Alternative setup also failed: {e2}")
            return False


def check_bluetooth_nap_status():
    """Check if Bluetooth NAP is working"""
    try:
        # Check if pan0 or bnep0 exists
        result = subprocess.run(
            ['ifconfig'],
            capture_output=True,
            text=True
        )
        
        if 'pan0' in result.stdout or 'bnep0' in result.stdout:
            logger.info("Bluetooth NAP interface found")
            
            # Check IP
            if '192.168.44.1' in result.stdout:
                logger.info("Bluetooth NAP is active with IP 192.168.44.1")
                return True
            else:
                logger.warning("Bluetooth NAP interface exists but no IP assigned")
                return False
        else:
            logger.info("No Bluetooth NAP interface found (will be created when device connects)")
            return False
            
    except Exception as e:
        logger.error(f"Error checking Bluetooth NAP status: {e}")
        return False


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    setup_bluetooth_nap()
    check_bluetooth_nap_status()
