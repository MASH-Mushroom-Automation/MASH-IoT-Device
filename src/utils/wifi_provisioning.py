"""
WiFi Provisioning Service for MASH IoT Device
Allows mobile app to configure WiFi credentials via Bluetooth
"""

import subprocess
import logging
import os
import time
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class WiFiProvisioning:
    """Handles WiFi configuration and connection"""
    
    def __init__(self):
        """Initialize WiFi provisioning service"""
        self.current_ssid = None
        self.connection_status = "disconnected"
        
    def scan_wifi_networks(self) -> List[Dict[str, str]]:
        """
        Scan for available WiFi networks
        
        Returns:
            List of dictionaries with network info (ssid, signal, security)
        """
        try:
            logger.info("Scanning for WiFi networks...")
            
            # Use nmcli to scan networks
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"WiFi scan failed: {result.stderr}")
                return []
            
            networks = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split(':')
                if len(parts) >= 3:
                    ssid = parts[0]
                    signal = parts[1]
                    security = parts[2]
                    
                    # Skip empty SSIDs (hidden networks)
                    if ssid:
                        networks.append({
                            'ssid': ssid,
                            'signal': int(signal) if signal.isdigit() else 0,
                            'security': security,
                            'secured': bool(security and security != '--')
                        })
            
            # Sort by signal strength
            networks.sort(key=lambda x: x['signal'], reverse=True)
            
            logger.info(f"Found {len(networks)} WiFi networks")
            return networks
            
        except subprocess.TimeoutExpired:
            logger.error("WiFi scan timed out")
            return []
        except Exception as e:
            logger.error(f"Error scanning WiFi networks: {e}")
            return []
    
    def connect_to_wifi(self, ssid: str, password: Optional[str] = None) -> bool:
        """
        Connect to a WiFi network
        
        Args:
            ssid: Network SSID
            password: Network password (None for open networks)
            
        Returns:
            True if connection successful
        """
        try:
            logger.info(f"Connecting to WiFi network: {ssid}")
            
            # Check if connection already exists
            existing_conn = self._get_connection_name(ssid)
            
            if existing_conn:
                # Connection exists, just activate it
                logger.info(f"Using existing connection: {existing_conn}")
                result = subprocess.run(
                    ['nmcli', 'connection', 'up', existing_conn],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                # Create new connection
                if password:
                    # Secured network
                    result = subprocess.run(
                        ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                else:
                    # Open network
                    result = subprocess.run(
                        ['nmcli', 'dev', 'wifi', 'connect', ssid],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully connected to {ssid}")
                self.current_ssid = ssid
                self.connection_status = "connected"
                
                # Wait a moment for IP assignment
                time.sleep(2)
                
                # Verify internet connectivity
                if self._check_internet():
                    logger.info("✅ Internet connectivity verified")
                    return True
                else:
                    logger.warning("⚠️  Connected to WiFi but no internet access")
                    return True  # Still return True as WiFi is connected
            else:
                logger.error(f"Failed to connect to {ssid}: {result.stderr}")
                self.connection_status = "failed"
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"WiFi connection to {ssid} timed out")
            self.connection_status = "timeout"
            return False
        except Exception as e:
            logger.error(f"Error connecting to WiFi: {e}")
            self.connection_status = "error"
            return False
    
    def disconnect_wifi(self) -> bool:
        """
        Disconnect from current WiFi network
        
        Returns:
            True if disconnection successful
        """
        try:
            logger.info("Disconnecting from WiFi...")
            
            result = subprocess.run(
                ['nmcli', 'device', 'disconnect', 'wlan0'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info("✅ Disconnected from WiFi")
                self.current_ssid = None
                self.connection_status = "disconnected"
                return True
            else:
                logger.error(f"Failed to disconnect: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error disconnecting from WiFi: {e}")
            return False
    
    def get_current_connection(self) -> Optional[Dict[str, str]]:
        """
        Get current WiFi connection info
        
        Returns:
            Dictionary with connection info or None if not connected
        """
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'ACTIVE,SSID,SIGNAL,RATE', 'dev', 'wifi'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            for line in result.stdout.strip().split('\n'):
                parts = line.split(':')
                if len(parts) >= 2 and parts[0] == 'yes':
                    return {
                        'ssid': parts[1],
                        'signal': parts[2] if len(parts) > 2 else '0',
                        'rate': parts[3] if len(parts) > 3 else 'Unknown',
                        'status': 'connected'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current connection: {e}")
            return None
    
    def get_ip_address(self) -> Optional[str]:
        """
        Get current IP address
        
        Returns:
            IP address string or None
        """
        try:
            result = subprocess.run(
                ['hostname', '-I'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                ip = result.stdout.strip().split()[0]
                return ip
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting IP address: {e}")
            return None
    
    def _get_connection_name(self, ssid: str) -> Optional[str]:
        """
        Get NetworkManager connection name for an SSID
        
        Args:
            ssid: Network SSID
            
        Returns:
            Connection name or None
        """
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            for line in result.stdout.strip().split('\n'):
                parts = line.split(':')
                if len(parts) >= 2:
                    name = parts[0]
                    conn_type = parts[1]
                    
                    # Check if this is a WiFi connection matching the SSID
                    if conn_type == '802-11-wireless' and ssid in name:
                        return name
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting connection name: {e}")
            return None
    
    def _check_internet(self) -> bool:
        """
        Check if internet is accessible
        
        Returns:
            True if internet is accessible
        """
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def save_credentials(self, ssid: str, password: str) -> bool:
        """
        Save WiFi credentials for auto-connect on boot
        
        Args:
            ssid: Network SSID
            password: Network password
            
        Returns:
            True if credentials saved successfully
        """
        try:
            # NetworkManager automatically saves credentials
            # Just ensure autoconnect is enabled
            conn_name = self._get_connection_name(ssid)
            
            if conn_name:
                result = subprocess.run(
                    ['nmcli', 'connection', 'modify', conn_name, 
                     'connection.autoconnect', 'yes'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ WiFi credentials saved for {ssid}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            return False
    
    def forget_network(self, ssid: str) -> bool:
        """
        Forget a saved WiFi network
        
        Args:
            ssid: Network SSID
            
        Returns:
            True if network forgotten successfully
        """
        try:
            conn_name = self._get_connection_name(ssid)
            
            if conn_name:
                result = subprocess.run(
                    ['nmcli', 'connection', 'delete', conn_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ Forgot network: {ssid}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error forgetting network: {e}")
            return False


# Singleton instance
_wifi_provisioning = None

def get_wifi_provisioning() -> WiFiProvisioning:
    """Get WiFi provisioning singleton instance"""
    global _wifi_provisioning
    if _wifi_provisioning is None:
        _wifi_provisioning = WiFiProvisioning()
    return _wifi_provisioning
