"""
Enhanced Hotspot Manager for MASH IoT Device
Handles Access Point creation with improved reliability
"""

import os
import subprocess
import logging
import time
from typing import Optional, Dict, Any


class HotspotManager:
    """Manages WiFi hotspot/Access Point for device provisioning"""
    
    def __init__(self, 
                 device_id: str,
                 interface: str = 'wlan0',
                 ssid_prefix: str = 'MASH-Chamber',
                 password: Optional[str] = None,
                 channel: int = 6,
                 ap_ip: str = '192.168.4.1',
                 dhcp_range_start: str = '192.168.4.2',
                 dhcp_range_end: str = '192.168.4.20',
                 mock_mode: bool = False):
        """
        Initialize Hotspot Manager
        
        Args:
            device_id: Unique device identifier
            interface: WiFi interface name (default: wlan0)
            ssid_prefix: SSID prefix for the hotspot
            password: Hotspot password (None for open network)
            channel: WiFi channel (default: 6)
            ap_ip: IP address for the access point
            dhcp_range_start: DHCP range start
            dhcp_range_end: DHCP range end
            mock_mode: Run in simulation mode
        """
        self.logger = logging.getLogger(__name__)
        self.device_id = device_id
        self.interface = interface
        self.ssid_prefix = ssid_prefix
        self.password = password
        self.channel = channel
        self.ap_ip = ap_ip
        self.dhcp_range_start = dhcp_range_start
        self.dhcp_range_end = dhcp_range_end
        self.mock_mode = mock_mode
        
        # Generate unique SSID from device ID
        device_suffix = device_id.split('-')[-1] if '-' in device_id else device_id[-6:]
        self.ssid = f"{ssid_prefix}-{device_suffix}"
        
        # Connection name for NetworkManager
        self.connection_name = f"mash-hotspot-{device_suffix}"
        
        # State tracking
        self.is_active = False
        
        # Check system dependencies
        self._check_dependencies()
    
    def _check_dependencies(self) -> bool:
        """Check if required tools are installed"""
        if self.mock_mode:
            return True
        
        required_tools = ['nmcli', 'ip', 'iptables']
        missing_tools = []
        
        for tool in required_tools:
            try:
                result = subprocess.run(
                    ['which', tool],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode != 0:
                    missing_tools.append(tool)
            except Exception:
                missing_tools.append(tool)
        
        if missing_tools:
            self.logger.warning(f"Missing tools for hotspot: {', '.join(missing_tools)}")
            return False
        
        return True
    
    def start(self) -> bool:
        """
        Start WiFi hotspot
        
        Returns:
            True if successful, False otherwise
        """
        if self.is_active:
            self.logger.warning("Hotspot already active")
            return True
        
        if self.mock_mode:
            self.logger.info(f"Mock: Started hotspot '{self.ssid}'")
            self.is_active = True
            return True
        
        try:
            self.logger.info(f"Starting WiFi hotspot: {self.ssid}")
            
            # Method 1: Try NetworkManager first (most reliable on Raspberry Pi OS)
            if self._start_with_networkmanager():
                self.is_active = True
                self.logger.info(f"Hotspot started successfully: {self.ssid}")
                self.logger.info("Connect to this network from mobile app")
                self.logger.info(f"Access provisioning at http://{self.ap_ip}:5000")
                return True
            
            # Method 2: Fallback to manual configuration
            self.logger.warning("NetworkManager method failed, trying manual configuration")
            if self._start_manually():
                self.is_active = True
                self.logger.info(f"Hotspot started (manual mode): {self.ssid}")
                return True
            
            self.logger.error("All hotspot methods failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error starting hotspot: {e}", exc_info=True)
            return False
    
    def _start_with_networkmanager(self) -> bool:
        """Start hotspot using NetworkManager (nmcli)"""
        try:
            # Step 1: Clean up any existing hotspot connection
            self.logger.debug("Cleaning up existing connections...")
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
            
            time.sleep(1)
            
            # Step 2: Ensure WiFi radio is on
            self.logger.debug("Enabling WiFi radio...")
            subprocess.run(
                ['nmcli', 'radio', 'wifi', 'on'],
                capture_output=True,
                timeout=5
            )
            
            time.sleep(1)
            
            # Step 3: Create hotspot connection
            self.logger.debug(f"Creating hotspot connection: {self.connection_name}")
            
            # Build nmcli command
            cmd = [
                'nmcli', 'connection', 'add',
                'type', 'wifi',
                'ifname', self.interface,
                'con-name', self.connection_name,
                'autoconnect', 'no',
                'ssid', self.ssid
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.logger.error(f"Failed to create connection: {result.stderr}")
                return False
            
            # Step 4: Configure as access point
            self.logger.debug("Configuring as access point...")
            subprocess.run(
                [
                    'nmcli', 'connection', 'modify', self.connection_name,
                    'wifi.mode', 'ap',
                    'wifi.band', 'bg',
                    'wifi.channel', str(self.channel),
                    '802-11-wireless.hidden', 'no'
                ],
                capture_output=True,
                timeout=5
            )
            
            # Step 5: Configure IP address (important: shared mode for DHCP)
            self.logger.debug(f"Configuring IP address: {self.ap_ip}")
            subprocess.run(
                [
                    'nmcli', 'connection', 'modify', self.connection_name,
                    'ipv4.method', 'shared',
                    'ipv4.addresses', f'{self.ap_ip}/24'
                ],
                capture_output=True,
                timeout=5
            )
            
            # Step 6: Configure WiFi security if password provided
            if self.password:
                self.logger.debug("Configuring WPA2 security...")
                subprocess.run(
                    [
                        'nmcli', 'connection', 'modify', self.connection_name,
                        'wifi-sec.key-mgmt', 'wpa-psk',
                        'wifi-sec.psk', self.password
                    ],
                    capture_output=True,
                    timeout=5
                )
            else:
                self.logger.debug("Configuring as open network...")
                subprocess.run(
                    [
                        'nmcli', 'connection', 'modify', self.connection_name,
                        'wifi-sec.key-mgmt', 'none'
                    ],
                    capture_output=True,
                    timeout=5
                )
            
            # Step 7: Bring up the hotspot
            self.logger.debug("Activating hotspot connection...")
            result = subprocess.run(
                ['nmcli', 'connection', 'up', self.connection_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"Failed to activate hotspot: {result.stderr}")
                return False
            
            # Wait for interface to stabilize
            time.sleep(3)
            
            # Verify hotspot is running
            if self._verify_hotspot():
                return True
            else:
                self.logger.error("Hotspot activated but verification failed")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout while starting hotspot")
            return False
        except Exception as e:
            self.logger.error(f"Error in NetworkManager hotspot: {e}")
            return False
    
    def _start_manually(self) -> bool:
        """Start hotspot manually (fallback method)"""
        # This would require hostapd and dnsmasq
        # For now, return False as this is more complex
        self.logger.warning("Manual hotspot configuration not yet implemented")
        self.logger.info("Please install NetworkManager: sudo apt-get install network-manager")
        return False
    
    def _verify_hotspot(self) -> bool:
        """Verify that hotspot is actually running"""
        try:
            # Check if connection is active
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'NAME,DEVICE,STATE', 'connection', 'show', '--active'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    parts = line.split(':')
                    if len(parts) >= 3 and parts[0] == self.connection_name:
                        if parts[2] == 'activated':
                            self.logger.info(f"Hotspot verified active on {parts[1]}")
                            return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error verifying hotspot: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop WiFi hotspot
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_active:
            self.logger.debug("Hotspot not active")
            return True
        
        if self.mock_mode:
            self.logger.info("Mock: Stopped hotspot")
            self.is_active = False
            return True
        
        try:
            self.logger.info("Stopping WiFi hotspot...")
            
            # Bring down connection
            subprocess.run(
                ['nmcli', 'connection', 'down', self.connection_name],
                capture_output=True,
                timeout=10
            )
            
            # Delete connection
            subprocess.run(
                ['nmcli', 'connection', 'delete', self.connection_name],
                capture_output=True,
                timeout=5
            )
            
            self.is_active = False
            self.logger.info("Hotspot stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping hotspot: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get hotspot status information"""
        return {
            'active': self.is_active,
            'ssid': self.ssid,
            'ip_address': self.ap_ip,
            'interface': self.interface,
            'password_protected': self.password is not None,
            'channel': self.channel,
            'device_id': self.device_id,
            'connection_name': self.connection_name
        }
    
    def get_connected_clients(self) -> int:
        """Get number of connected clients"""
        if not self.is_active or self.mock_mode:
            return 0
        
        try:
            # Check DHCP leases
            lease_files = [
                '/var/lib/NetworkManager/dnsmasq-*.leases',
                '/var/lib/misc/dnsmasq.leases'
            ]
            
            for lease_pattern in lease_files:
                result = subprocess.run(
                    f'cat {lease_pattern} 2>/dev/null || echo ""',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.stdout.strip():
                    lines = [l for l in result.stdout.strip().split('\n') if l]
                    return len(lines)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error getting connected clients: {e}")
            return 0
