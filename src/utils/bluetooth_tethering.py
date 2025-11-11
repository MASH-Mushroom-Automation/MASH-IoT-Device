"""
Bluetooth Tethering Service for MASH IoT Device
Provides internet sharing via Bluetooth PAN (Personal Area Network)
"""

import logging
import subprocess
import time
from typing import Optional, Callable
from .bluetooth_manager import BluetoothManager, BluetoothState


class BluetoothTethering:
    """Manages Bluetooth tethering for internet sharing"""
    
    def __init__(self, bluetooth_manager: BluetoothManager):
        self.logger = logging.getLogger(__name__)
        self.bt_manager = bluetooth_manager
        self.tethering_active = False
        self.connected_client_address: Optional[str] = None
    
    def start_tethering(self, on_client_connected: Optional[Callable] = None) -> bool:
        """
        Start Bluetooth tethering service
        
        Args:
            on_client_connected: Callback when client connects
            
        Returns:
            True if successful
        """
        try:
            self.logger.info("Starting Bluetooth tethering service...")
            
            # Enable Bluetooth
            if not self.bt_manager.enable():
                self.logger.error("Failed to enable Bluetooth")
                return False
            
            # Make device discoverable
            if not self.bt_manager.make_discoverable(timeout=300):
                self.logger.error("Failed to make device discoverable")
                return False
            
            # Setup network sharing
            self._setup_pan_server()
            
            self.tethering_active = True
            self.logger.info("Bluetooth tethering started - Device is discoverable")
            self.logger.info(f"Pair with device: {self.bt_manager.device_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start tethering: {e}")
            return False
    
    def stop_tethering(self) -> bool:
        """Stop Bluetooth tethering"""
        try:
            self.logger.info("Stopping Bluetooth tethering...")
            
            # Cleanup NAT rules
            self._cleanup_network_sharing()
            
            self.tethering_active = False
            self.connected_client_address = None
            
            self.logger.info("Bluetooth tethering stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping tethering: {e}")
            return False
    
    def _setup_pan_server(self) -> bool:
        """Setup Bluetooth PAN server"""
        try:
            # Enable IP forwarding
            subprocess.run(
                ['sysctl', '-w', 'net.ipv4.ip_forward=1'],
                capture_output=True,
                check=False
            )
            
            # Configure iptables for NAT
            # Forward from Bluetooth to WiFi
            subprocess.run([
                'iptables', '-t', 'nat', '-A', 'POSTROUTING',
                '-o', 'wlan0', '-j', 'MASQUERADE'
            ], capture_output=True, check=False)
            
            subprocess.run([
                'iptables', '-A', 'FORWARD', '-i', 'bnep0',
                '-o', 'wlan0', '-m', 'state',
                '--state', 'RELATED,ESTABLISHED', '-j', 'ACCEPT'
            ], capture_output=True, check=False)
            
            subprocess.run([
                'iptables', '-A', 'FORWARD', '-i', 'wlan0',
                '-o', 'bnep0', '-j', 'ACCEPT'
            ], capture_output=True, check=False)
            
            self.logger.info("PAN server configured")
            return True
            
        except Exception as e:
            self.logger.error(f"PAN setup error: {e}")
            return False
    
    def _cleanup_network_sharing(self) -> bool:
        """Cleanup network sharing rules"""
        try:
            # Remove iptables rules
            subprocess.run([
                'iptables', '-t', 'nat', '-D', 'POSTROUTING',
                '-o', 'wlan0', '-j', 'MASQUERADE'
            ], capture_output=True, check=False)
            
            subprocess.run([
                'iptables', '-D', 'FORWARD', '-i', 'bnep0',
                '-o', 'wlan0', '-m', 'state',
                '--state', 'RELATED,ESTABLISHED', '-j', 'ACCEPT'
            ], capture_output=True, check=False)
            
            subprocess.run([
                'iptables', '-D', 'FORWARD', '-i', 'wlan0',
                '-o', 'bnep0', '-j', 'ACCEPT'
            ], capture_output=True, check=False)
            
            return True
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            return False
    
    def accept_client_connection(self, client_address: str) -> bool:
        """
        Accept and connect to client device
        
        Args:
            client_address: Bluetooth MAC address of client
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Accepting connection from {client_address}...")
            
            # Pair with client
            if not self.bt_manager.pair_device(client_address):
                self.logger.error("Failed to pair with client")
                return False
            
            # Connect to client
            if not self.bt_manager.connect_device(client_address):
                self.logger.error("Failed to connect to client")
                return False
            
            # Setup network sharing for this client
            if not self.bt_manager.setup_network_sharing(client_address):
                self.logger.error("Failed to setup network sharing")
                return False
            
            self.connected_client_address = client_address
            self.logger.info(f"Client {client_address} connected with internet access")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error accepting client: {e}")
            return False
    
    def get_tethering_status(self) -> dict:
        """Get tethering status"""
        return {
            'active': self.tethering_active,
            'bluetooth_state': self.bt_manager.state.value,
            'device_name': self.bt_manager.device_name,
            'connected_client': self.connected_client_address,
            'discoverable': self.bt_manager.state == BluetoothState.DISCOVERABLE
        }
