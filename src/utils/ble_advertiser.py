"""
BLE (Bluetooth Low Energy) Advertiser
Makes the Raspberry Pi discoverable via BLE scan (not just Classic Bluetooth)
"""

import subprocess
import logging
import time
import os

logger = logging.getLogger(__name__)


class BLEAdvertiser:
    """Handles BLE advertising to make device discoverable by BLE scans"""
    
    def __init__(self, device_name: str = "MASH-IoT-Device"):
        self.device_name = device_name
        self.advertising = False
        
    def start_advertising(self) -> bool:
        """
        Start BLE advertising
        This makes the device discoverable by BLE scans (like Flutter Blue Plus)
        """
        try:
            logger.info(f"Starting BLE advertising as: {self.device_name}")
            
            # Method 1: Using hciconfig and hcitool (older method)
            self._start_advertising_hci()
            
            # Method 2: Using bluetoothctl (newer method)
            self._start_advertising_bluetoothctl()
            
            self.advertising = True
            logger.info("BLE advertising started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start BLE advertising: {e}")
            return False
    
    def _start_advertising_hci(self):
        """Start BLE advertising using hciconfig and hcitool"""
        try:
            # Enable BLE advertising
            logger.info("Enabling BLE advertising via hcitool...")
            
            # Set advertising parameters
            # This makes the device discoverable via BLE scan
            subprocess.run([
                'sudo', 'hcitool', '-i', 'hci0', 'cmd',
                '0x08', '0x0008',  # LE Set Advertising Data
                '1e',  # Length
                '02', '01', '06',  # Flags
                '03', '03', 'aa', 'fe',  # Complete list of 16-bit UUIDs
                f'{len(self.device_name) + 1:02x}', '09',  # Complete local name
                *[f'{ord(c):02x}' for c in self.device_name]
            ], check=False, capture_output=True)
            
            # Enable advertising
            subprocess.run([
                'sudo', 'hcitool', '-i', 'hci0', 'cmd',
                '0x08', '0x000a',  # LE Set Advertise Enable
                '01'  # Enable
            ], check=False, capture_output=True)
            
            logger.info("HCI BLE advertising enabled")
            
        except Exception as e:
            logger.warning(f"HCI advertising failed (this is OK if bluetoothctl works): {e}")
    
    def _start_advertising_bluetoothctl(self):
        """Start BLE advertising using bluetoothctl"""
        try:
            logger.info("Configuring BLE via bluetoothctl...")
            
            # Use bluetoothctl to set up advertising
            commands = [
                "power on",
                "discoverable on",
                "pairable on",
                f"system-alias {self.device_name}",
                "advertise on",  # This enables BLE advertising!
                "exit"
            ]
            
            process = subprocess.Popen(
                ['bluetoothctl'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input="\n".join(commands), timeout=10)
            
            logger.info("Bluetoothctl BLE advertising configured")
            logger.debug(f"Output: {stdout}")
            
        except Exception as e:
            logger.warning(f"Bluetoothctl advertising failed: {e}")
    
    def stop_advertising(self):
        """Stop BLE advertising"""
        try:
            logger.info("Stopping BLE advertising...")
            
            # Disable advertising via hcitool
            subprocess.run([
                'sudo', 'hcitool', '-i', 'hci0', 'cmd',
                '0x08', '0x000a',  # LE Set Advertise Enable
                '00'  # Disable
            ], check=False, capture_output=True)
            
            # Disable via bluetoothctl
            process = subprocess.Popen(
                ['bluetoothctl'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            process.communicate(input="advertise off\nexit\n", timeout=5)
            
            self.advertising = False
            logger.info("BLE advertising stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop BLE advertising: {e}")
    
    def is_advertising(self) -> bool:
        """Check if currently advertising"""
        return self.advertising


def start_ble_advertising(device_name: str = "MASH-IoT-Device") -> BLEAdvertiser:
    """
    Start BLE advertising
    
    Args:
        device_name: Name to advertise
        
    Returns:
        BLEAdvertiser instance
    """
    advertiser = BLEAdvertiser(device_name)
    advertiser.start_advertising()
    return advertiser


if __name__ == "__main__":
    # Test BLE advertising
    logging.basicConfig(level=logging.INFO)
    
    print("Starting BLE advertising test...")
    advertiser = start_ble_advertising("MASH-IoT-Device")
    
    print("BLE advertising active. Device should be visible in BLE scans.")
    print("Test with: sudo hcitool lescan")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping BLE advertising...")
        advertiser.stop_advertising()
        print("Done.")
