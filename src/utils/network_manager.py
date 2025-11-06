"""
Network Manager for MASH IoT Device
Handles WiFi configuration and network connectivity
"""

import os
import subprocess
import logging
import time
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class WiFiNetwork:
    """WiFi network information"""
    ssid: str
    signal_strength: int
    security: str
    frequency: str
    in_use: bool = False


class NetworkManager:
    """Manages network connectivity and WiFi configuration"""
    
    def __init__(self, interface: str = 'wlan0', mock_mode: bool = False):
        """
        Initialize Network Manager
        
        Args:
            interface: WiFi interface name (default: wlan0)
            mock_mode: Run in mock mode for testing
        """
        self.logger = logging.getLogger(__name__)
        self.interface = interface
        self.mock_mode = mock_mode
        
        # Check if NetworkManager is available
        self.nmcli_available = self._check_nmcli()
    
    def _check_nmcli(self) -> bool:
        """Check if nmcli is available"""
        if self.mock_mode:
            return True
        
        try:
            result = subprocess.run(
                ['which', 'nmcli'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.warning(f"nmcli not available: {e}")
            return False
    
    def scan_wifi_networks(self) -> List[WiFiNetwork]:
        """
        Scan for available WiFi networks
        
        Returns:
            List of available WiFi networks
        """
        if self.mock_mode:
            return self._mock_scan_wifi()
        
        if not self.nmcli_available:
            self.logger.error("nmcli not available for scanning")
            return []
        
        try:
            # Trigger a new scan
            subprocess.run(
                ['nmcli', 'device', 'wifi', 'rescan'],
                capture_output=True,
                timeout=10
            )
            
            # Wait a bit for scan to complete
            time.sleep(2)
            
            # Get scan results
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY,FREQ,IN-USE', 'device', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.logger.error(f"WiFi scan failed: {result.stderr}")
                return []
            
            # Parse results
            networks = []
            seen_ssids = set()
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split(':')
                if len(parts) < 5:
                    continue
                
                ssid = parts[0].strip()
                if not ssid or ssid in seen_ssids:
                    continue
                
                seen_ssids.add(ssid)
                
                try:
                    signal = int(parts[1])
                    security = parts[2]
                    frequency = parts[3]
                    in_use = parts[4] == '*'
                    
                    networks.append(WiFiNetwork(
                        ssid=ssid,
                        signal_strength=signal,
                        security=security,
                        frequency=frequency,
                        in_use=in_use
                    ))
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"Failed to parse network info: {e}")
                    continue
            
            # Sort by signal strength
            networks.sort(key=lambda n: n.signal_strength, reverse=True)
            
            self.logger.info(f"Found {len(networks)} WiFi networks")
            return networks
            
        except subprocess.TimeoutExpired:
            self.logger.error("WiFi scan timeout")
            return []
        except Exception as e:
            self.logger.error(f"WiFi scan error: {e}")
            return []
    
    def _mock_scan_wifi(self) -> List[WiFiNetwork]:
        """Mock WiFi scan for testing"""
        return [
            WiFiNetwork(ssid='Home WiFi', signal_strength=85, security='WPA2', frequency='2.4 GHz'),
            WiFiNetwork(ssid='Office Network', signal_strength=70, security='WPA2', frequency='5 GHz'),
            WiFiNetwork(ssid='Guest WiFi', signal_strength=50, security='Open', frequency='2.4 GHz'),
        ]
    
    def connect_to_wifi(self, ssid: str, password: str = '') -> bool:
        """
        Connect to a WiFi network
        
        Args:
            ssid: Network SSID
            password: Network password (empty for open networks)
            
        Returns:
            True if connection successful, False otherwise
        """
        if self.mock_mode:
            self.logger.info(f"Mock: Connected to WiFi '{ssid}'")
            return True
        
        if not self.nmcli_available:
            self.logger.error("nmcli not available for connection")
            return False
        
        try:
            self.logger.info(f"Connecting to WiFi: {ssid}")
            
            # Build connection command
            cmd = ['nmcli', 'device', 'wifi', 'connect', ssid]
            
            if password:
                cmd.extend(['password', password])
            
            # Execute connection command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully connected to {ssid}")
                return True
            else:
                self.logger.error(f"Failed to connect to {ssid}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Connection to {ssid} timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error connecting to WiFi: {e}")
            return False
    
    def disconnect_wifi(self) -> bool:
        """
        Disconnect from current WiFi network
        
        Returns:
            True if disconnection successful, False otherwise
        """
        if self.mock_mode:
            self.logger.info("Mock: Disconnected from WiFi")
            return True
        
        if not self.nmcli_available:
            return False
        
        try:
            result = subprocess.run(
                ['nmcli', 'device', 'disconnect', self.interface],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error disconnecting WiFi: {e}")
            return False
    
    def get_current_connection(self) -> Optional[Dict[str, Any]]:
        """
        Get current WiFi connection info
        
        Returns:
            Connection info or None if not connected
        """
        if self.mock_mode:
            return {
                'ssid': 'Home WiFi',
                'ip_address': '192.168.1.100',
                'signal': 85,
                'connected': True
            }
        
        if not self.nmcli_available:
            return None
        
        try:
            # Get active connection
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'NAME,TYPE,DEVICE', 'connection', 'show', '--active'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            # Find WiFi connection
            for line in result.stdout.strip().split('\n'):
                parts = line.split(':')
                if len(parts) >= 3 and parts[1] == '802-11-wireless':
                    ssid = parts[0]
                    device = parts[2]
                    
                    # Get IP address
                    ip_result = subprocess.run(
                        ['nmcli', '-t', '-f', 'IP4.ADDRESS', 'device', 'show', device],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    ip_address = None
                    if ip_result.returncode == 0:
                        for ip_line in ip_result.stdout.strip().split('\n'):
                            if ip_line.startswith('IP4.ADDRESS'):
                                ip_address = ip_line.split(':')[1].split('/')[0]
                                break
                    
                    return {
                        'ssid': ssid,
                        'ip_address': ip_address,
                        'device': device,
                        'connected': True
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting current connection: {e}")
            return None
    
    def is_connected(self) -> bool:
        """
        Check if device is connected to WiFi
        
        Returns:
            True if connected, False otherwise
        """
        connection = self.get_current_connection()
        return connection is not None and connection.get('connected', False)
    
    def get_interface_ip(self) -> Optional[str]:
        """
        Get IP address of WiFi interface
        
        Returns:
            IP address or None
        """
        connection = self.get_current_connection()
        if connection:
            return connection.get('ip_address')
        return None
    
    def enable_interface(self) -> bool:
        """
        Enable WiFi interface
        
        Returns:
            True if successful, False otherwise
        """
        if self.mock_mode:
            return True
        
        try:
            result = subprocess.run(
                ['nmcli', 'radio', 'wifi', 'on'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error enabling WiFi interface: {e}")
            return False
    
    def disable_interface(self) -> bool:
        """
        Disable WiFi interface
        
        Returns:
            True if successful, False otherwise
        """
        if self.mock_mode:
            return True
        
        try:
            result = subprocess.run(
                ['nmcli', 'radio', 'wifi', 'off'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error disabling WiFi interface: {e}")
            return False
