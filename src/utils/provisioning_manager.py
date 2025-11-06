"""
Provisioning Manager for MASH IoT Device
Handles device provisioning mode (SoftAP) for WiFi setup
"""

import os
import subprocess
import logging
import time
import uuid
from typing import Optional, Dict, Any
from pathlib import Path


class ProvisioningManager:
    """Manages device provisioning mode (SoftAP)"""
    
    def __init__(self, 
                 device_id: str,
                 interface: str = 'wlan0',
                 ap_ssid_prefix: str = 'MASH-Chamber',
                 ap_password: Optional[str] = None,
                 ap_channel: int = 6,
                 ap_ip: str = '192.168.4.1',
                 mock_mode: bool = False):
        """
        Initialize Provisioning Manager
        
        Args:
            device_id: Device unique ID
            interface: WiFi interface name
            ap_ssid_prefix: Access point SSID prefix
            ap_password: Access point password (None for open network)
            ap_channel: WiFi channel to use
            ap_ip: IP address for the access point
            mock_mode: Run in mock mode for testing
        """
        self.logger = logging.getLogger(__name__)
        self.device_id = device_id
        self.interface = interface
        self.ap_ssid_prefix = ap_ssid_prefix
        self.ap_password = ap_password
        self.ap_channel = ap_channel
        self.ap_ip = ap_ip
        self.mock_mode = mock_mode
        
        # Generate unique SSID
        device_suffix = device_id.split('-')[-1] if '-' in device_id else device_id[:6]
        self.ap_ssid = f"{ap_ssid_prefix}-{device_suffix}"
        
        # State
        self.is_provisioning = False
        self.connection_name = f"mash-provisioning-{device_suffix}"
        
        # Check dependencies
        self.nmcli_available = self._check_dependency('nmcli')
        self.hostapd_available = self._check_dependency('hostapd')
        self.dnsmasq_available = self._check_dependency('dnsmasq')
    
    def _check_dependency(self, command: str) -> bool:
        """Check if a command is available"""
        if self.mock_mode:
            return True
        
        try:
            result = subprocess.run(
                ['which', command],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def start_provisioning_mode(self) -> bool:
        """
        Start provisioning mode (create SoftAP)
        
        Returns:
            True if successful, False otherwise
        """
        if self.is_provisioning:
            self.logger.warning("Already in provisioning mode")
            return True
        
        if self.mock_mode:
            self.logger.info(f"Mock: Started provisioning mode (SSID: {self.ap_ssid})")
            self.is_provisioning = True
            return True
        
        try:
            self.logger.info(f"Starting provisioning mode (SSID: {self.ap_ssid})")
            
            # Method 1: Using NetworkManager (nmcli) - Easier and more reliable
            if self.nmcli_available:
                return self._start_provisioning_nmcli()
            
            # Method 2: Using hostapd + dnsmasq (fallback)
            elif self.hostapd_available and self.dnsmasq_available:
                return self._start_provisioning_hostapd()
            
            else:
                self.logger.error("No suitable method available for provisioning mode")
                self.logger.error("Please install NetworkManager or hostapd+dnsmasq")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting provisioning mode: {e}")
            return False
    
    def _start_provisioning_nmcli(self) -> bool:
        """Start provisioning using nmcli (NetworkManager)"""
        try:
            # Delete existing connection if any
            subprocess.run(
                ['nmcli', 'connection', 'delete', self.connection_name],
                capture_output=True,
                timeout=5
            )
            
            # Create WiFi hotspot
            cmd = [
                'nmcli', 'device', 'wifi', 'hotspot',
                'ifname', self.interface,
                'con-name', self.connection_name,
                'ssid', self.ap_ssid,
                'band', 'bg',
                'channel', str(self.ap_channel)
            ]
            
            if self.ap_password:
                cmd.extend(['password', self.ap_password])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"Failed to create hotspot: {result.stderr}")
                return False
            
            # Wait for hotspot to start
            time.sleep(3)
            
            # Set static IP
            subprocess.run(
                [
                    'nmcli', 'connection', 'modify', self.connection_name,
                    'ipv4.addresses', f'{self.ap_ip}/24',
                    'ipv4.method', 'shared'
                ],
                capture_output=True,
                timeout=5
            )
            
            # Restart connection to apply changes
            subprocess.run(
                ['nmcli', 'connection', 'up', self.connection_name],
                capture_output=True,
                timeout=10
            )
            
            self.is_provisioning = True
            self.logger.info(f"Provisioning mode started: {self.ap_ssid} at {self.ap_ip}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in nmcli provisioning: {e}")
            return False
    
    def _start_provisioning_hostapd(self) -> bool:
        """Start provisioning using hostapd + dnsmasq (fallback method)"""
        # This is more complex and requires configuration files
        # For now, we'll keep this as a placeholder
        self.logger.warning("hostapd provisioning not fully implemented yet")
        self.logger.warning("Please use NetworkManager (nmcli) for provisioning")
        return False
    
    def stop_provisioning_mode(self) -> bool:
        """
        Stop provisioning mode
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_provisioning:
            self.logger.warning("Not in provisioning mode")
            return True
        
        if self.mock_mode:
            self.logger.info("Mock: Stopped provisioning mode")
            self.is_provisioning = False
            return True
        
        try:
            self.logger.info("Stopping provisioning mode")
            
            if self.nmcli_available:
                # Stop and delete hotspot connection
                subprocess.run(
                    ['nmcli', 'connection', 'down', self.connection_name],
                    capture_output=True,
                    timeout=10
                )
                
                subprocess.run(
                    ['nmcli', 'connection', 'delete', self.connection_name],
                    capture_output=True,
                    timeout=5
                )
                
                self.is_provisioning = False
                self.logger.info("Provisioning mode stopped")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error stopping provisioning mode: {e}")
            return False
    
    def get_provisioning_info(self) -> Dict[str, Any]:
        """
        Get provisioning mode information
        
        Returns:
            Dictionary with provisioning information
        """
        return {
            'active': self.is_provisioning,
            'ssid': self.ap_ssid,
            'ip_address': self.ap_ip,
            'password_protected': self.ap_password is not None,
            'channel': self.ap_channel,
            'interface': self.interface,
            'device_id': self.device_id,
            'mock_mode': self.mock_mode
        }
    
    def get_connected_clients(self) -> int:
        """
        Get number of connected clients
        
        Returns:
            Number of connected clients
        """
        if self.mock_mode:
            return 0
        
        if not self.is_provisioning:
            return 0
        
        try:
            # Get DHCP leases to count clients
            if os.path.exists('/var/lib/NetworkManager/dnsmasq-*.leases'):
                result = subprocess.run(
                    ['cat', '/var/lib/NetworkManager/dnsmasq-*.leases'],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return len(result.stdout.strip().split('\n'))
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error getting connected clients: {e}")
            return 0
