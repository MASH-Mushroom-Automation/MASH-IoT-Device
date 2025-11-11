"""
Bluetooth Manager for MASH IoT Device
Handles Bluetooth connectivity and network sharing via PAN (Personal Area Network)
"""

import os
import subprocess
import logging
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class BluetoothState(Enum):
    """Bluetooth connection state"""
    OFF = "off"
    ON = "on"
    DISCOVERABLE = "discoverable"
    CONNECTED = "connected"


@dataclass
class BluetoothDevice:
    """Bluetooth device information"""
    address: str
    name: str
    paired: bool = False
    connected: bool = False


class BluetoothManager:
    """Manages Bluetooth connectivity for network sharing"""
    
    def __init__(self, device_name: str = "MASH-IoT-Device", mock_mode: bool = False):
        self.logger = logging.getLogger(__name__)
        self.device_name = device_name
        self.mock_mode = mock_mode
        self.state = BluetoothState.OFF
        self._connected_devices: List[BluetoothDevice] = []
        self.bluetooth_available = self._check_bluetooth()
    
    def _check_bluetooth(self) -> bool:
        """Check if Bluetooth is available"""
        if self.mock_mode:
            return True
        try:
            result = subprocess.run(['which', 'bluetoothctl'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception as e:
            self.logger.warning(f"Bluetooth not available: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if Bluetooth is available on this system"""
        return self.bluetooth_available
    
    def _run_bt_command(self, command: str, timeout: int = 10) -> Optional[str]:
        """Run bluetoothctl command"""
        if self.mock_mode:
            return "Mock output"
        
        try:
            process = subprocess.Popen(
                ['bluetoothctl'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output, _ = process.communicate(input=f"{command}\nexit\n", timeout=timeout)
            return output
        except Exception as e:
            self.logger.error(f"BT command error: {e}")
            return None
    
    def enable(self) -> bool:
        """Enable Bluetooth"""
        if self.mock_mode:
            self.state = BluetoothState.ON
            return True
        
        try:
            self._run_bt_command("power on")
            self._run_bt_command(f"system-alias {self.device_name}")
            self.state = BluetoothState.ON
            self.logger.info("Bluetooth enabled")
            return True
        except Exception as e:
            self.logger.error(f"Enable error: {e}")
            return False
    
    def make_discoverable(self, timeout: int = 180) -> bool:
        """Make device discoverable"""
        if self.mock_mode:
            self.state = BluetoothState.DISCOVERABLE
            return True
        
        try:
            if self.state != BluetoothState.ON:
                self.enable()
            
            self._run_bt_command("discoverable on")
            self._run_bt_command("pairable on")
            if timeout > 0:
                self._run_bt_command(f"discoverable-timeout {timeout}")
            
            self.state = BluetoothState.DISCOVERABLE
            self.logger.info("Device discoverable")
            return True
        except Exception as e:
            self.logger.error(f"Discoverable error: {e}")
            return False
    
    def pair_device(self, address: str) -> bool:
        """Pair with device"""
        if self.mock_mode:
            return True
        
        try:
            self._run_bt_command(f"trust {address}")
            output = self._run_bt_command(f"pair {address}", timeout=30)
            return output and "successful" in output.lower()
        except Exception as e:
            self.logger.error(f"Pair error: {e}")
            return False
    
    def connect_device(self, address: str) -> bool:
        """Connect to paired device"""
        if self.mock_mode:
            self.state = BluetoothState.CONNECTED
            return True
        
        try:
            output = self._run_bt_command(f"connect {address}", timeout=15)
            if output and "Connection successful" in output:
                self.state = BluetoothState.CONNECTED
                self.logger.info(f"Connected to {address}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Connect error: {e}")
            return False
    
    def setup_network_sharing(self, device_address: str) -> bool:
        """Setup Bluetooth PAN for internet sharing"""
        if self.mock_mode:
            self.logger.info("Mock: Network sharing setup")
            return True
        
        try:
            self.logger.info("Setting up Bluetooth network sharing...")
            
            # Enable IP forwarding
            subprocess.run(['sysctl', '-w', 'net.ipv4.ip_forward=1'], check=True)
            
            # Setup NAT for bnep0 interface
            subprocess.run([
                'iptables', '-t', 'nat', '-A', 'POSTROUTING',
                '-o', 'wlan0', '-j', 'MASQUERADE'
            ], check=False)
            
            subprocess.run([
                'iptables', '-A', 'FORWARD', '-i', 'bnep0',
                '-o', 'wlan0', '-j', 'ACCEPT'
            ], check=False)
            
            self.logger.info("Network sharing configured")
            return True
        except Exception as e:
            self.logger.error(f"Network sharing error: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get Bluetooth status"""
        return {
            'enabled': self.state != BluetoothState.OFF,
            'state': self.state.value,
            'discoverable': self.state == BluetoothState.DISCOVERABLE,
            'connected_devices': len(self._connected_devices),
            'device_name': self.device_name
        }
