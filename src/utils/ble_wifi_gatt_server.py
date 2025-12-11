"""
BLE GATT Server for WiFi Provisioning
Receives WiFi credentials via BLE and connects to network using nmcli
"""

import logging
import subprocess
import threading
from typing import Optional, Callable
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib


# Service and Characteristic UUIDs
WIFI_PROVISIONING_SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
SSID_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef1'
PASSWORD_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef2'
CONNECT_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef3'
STATUS_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef4'


class WiFiProvisioningCharacteristic(dbus.service.Object):
    """Base class for BLE GATT Characteristic"""
    
    def __init__(self, bus, index, uuid, flags, service):
        self.path = f"{service.path}/char{index:04d}"
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.value = []
        dbus.service.Object.__init__(self, bus, self.path)
    
    @dbus.service.method('org.bluez.GattCharacteristic1',
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        """Read characteristic value"""
        return self.value
    
    @dbus.service.method('org.bluez.GattCharacteristic1',
                        in_signature='aya{sv}')
    def WriteValue(self, value, options):
        """Write characteristic value"""
        self.value = value
        self.on_write(value)
    
    def on_write(self, value):
        """Override this in subclasses"""
        pass
    
    @dbus.service.method('org.bluez.GattCharacteristic1')
    def StartNotify(self):
        """Start notifications"""
        pass
    
    @dbus.service.method('org.bluez.GattCharacteristic1')
    def StopNotify(self):
        """Stop notifications"""
        pass
    
    @dbus.service.signal('org.freedesktop.DBus.Properties',
                        signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        """Properties changed signal"""
        pass


class SSIDCharacteristic(WiFiProvisioningCharacteristic):
    """SSID Characteristic - receives WiFi network name"""
    
    def __init__(self, bus, index, service, provisioning_service):
        self.provisioning_service = provisioning_service
        self.logger = logging.getLogger(__name__)
        self.buffer = bytearray()  # Buffer for chunked data
        super().__init__(
            bus, index,
            SSID_CHARACTERISTIC_UUID,
            ['write'],
            service
        )
    
    def on_write(self, value):
        """Called when SSID chunk is written"""
        try:
            # Accumulate chunks
            self.buffer.extend(value)
            self.logger.debug(f"Received SSID chunk: {len(value)} bytes, total: {len(self.buffer)} bytes")
            
            # Try to decode - if successful, we have complete data
            try:
                ssid = self.buffer.decode('utf-8')
                self.provisioning_service.set_ssid(ssid)
                self.logger.info(f"Received complete SSID via BLE: {ssid}")
                self.buffer = bytearray()  # Clear buffer
            except UnicodeDecodeError:
                # Incomplete data, wait for more chunks
                self.logger.debug("Waiting for more SSID chunks...")
        except Exception as e:
            self.logger.error(f"Error processing SSID: {e}")
            self.buffer = bytearray()  # Clear buffer on error


class PasswordCharacteristic(WiFiProvisioningCharacteristic):
    """Password Characteristic - receives WiFi password"""
    
    def __init__(self, bus, index, service, provisioning_service):
        self.provisioning_service = provisioning_service
        self.logger = logging.getLogger(__name__)
        self.buffer = bytearray()  # Buffer for chunked data
        super().__init__(
            bus, index,
            PASSWORD_CHARACTERISTIC_UUID,
            ['write'],
            service
        )
    
    def on_write(self, value):
        """Called when password chunk is written"""
        try:
            # Accumulate chunks
            self.buffer.extend(value)
            self.logger.debug(f"Received password chunk: {len(value)} bytes, total: {len(self.buffer)} bytes")
            
            # Try to decode - if successful, we have complete data
            try:
                password = self.buffer.decode('utf-8')
                self.provisioning_service.set_password(password)
                self.logger.info(f"Received complete password via BLE: {'*' * len(password)}")
                self.buffer = bytearray()  # Clear buffer
            except UnicodeDecodeError:
                # Incomplete data, wait for more chunks
                self.logger.debug("Waiting for more password chunks...")
        except Exception as e:
            self.logger.error(f"Error processing password: {e}")
            self.buffer = bytearray()  # Clear buffer on error


class ConnectCharacteristic(WiFiProvisioningCharacteristic):
    """Connect Characteristic - triggers WiFi connection"""
    
    def __init__(self, bus, index, service, provisioning_service):
        self.provisioning_service = provisioning_service
        self.logger = logging.getLogger(__name__)
        super().__init__(
            bus, index,
            CONNECT_CHARACTERISTIC_UUID,
            ['write'],
            service
        )
    
    def on_write(self, value):
        """Called when connect command is written"""
        try:
            if value and value[0] == 0x01:
                self.logger.info("Received connect command via BLE")
                self.provisioning_service.connect_to_wifi()
        except Exception as e:
            self.logger.error(f"Error processing connect command: {e}")


class StatusCharacteristic(WiFiProvisioningCharacteristic):
    """Status Characteristic - reports connection status"""
    
    def __init__(self, bus, index, service, provisioning_service):
        self.provisioning_service = provisioning_service
        self.logger = logging.getLogger(__name__)
        super().__init__(
            bus, index,
            STATUS_CHARACTERISTIC_UUID,
            ['read', 'notify'],
            service
        )
    
    def ReadValue(self, options):
        """Read current status"""
        status = self.provisioning_service.get_status()
        return [ord(c) for c in status]
    
    def update_status(self, status: str):
        """Update status and notify"""
        self.value = [ord(c) for c in status]
        self.PropertiesChanged(
            'org.bluez.GattCharacteristic1',
            {'Value': self.value},
            []
        )


class WiFiProvisioningService(dbus.service.Object):
    """BLE GATT Service for WiFi Provisioning"""
    
    PATH_BASE = '/org/bluez/mash/wifi'
    
    def __init__(self, bus, index):
        self.path = f"{self.PATH_BASE}/service{index:04d}"
        self.bus = bus
        self.logger = logging.getLogger(__name__)
        
        # WiFi credentials
        self.ssid: Optional[str] = None
        self.password: Optional[str] = None
        self.status = "idle"
        
        # Characteristics
        self.characteristics = []
        
        dbus.service.Object.__init__(self, bus, self.path)
        
        # Create characteristics
        self._create_characteristics()
    
    def _create_characteristics(self):
        """Create GATT characteristics"""
        self.ssid_char = SSIDCharacteristic(self.bus, 0, self, self)
        self.password_char = PasswordCharacteristic(self.bus, 1, self, self)
        self.connect_char = ConnectCharacteristic(self.bus, 2, self, self)
        self.status_char = StatusCharacteristic(self.bus, 3, self, self)
        
        self.characteristics = [
            self.ssid_char,
            self.password_char,
            self.connect_char,
            self.status_char
        ]
    
    def set_ssid(self, ssid: str):
        """Set WiFi SSID"""
        self.ssid = ssid
        self.logger.info(f"SSID set: {ssid}")
    
    def set_password(self, password: str):
        """Set WiFi password"""
        self.password = password
        self.logger.info("Password set")
    
    def get_status(self) -> str:
        """Get current status"""
        return self.status
    
    def connect_to_wifi(self):
        """Connect to WiFi network using nmcli"""
        if not self.ssid:
            self.logger.error("Cannot connect: SSID not set")
            self._update_status("error_no_ssid")
            return
        
        self.logger.info(f"Connecting to WiFi: {self.ssid}")
        self._update_status("connecting")
        
        # Run connection in background thread
        thread = threading.Thread(target=self._connect_thread)
        thread.daemon = True
        thread.start()
    
    def _connect_thread(self):
        """Background thread for WiFi connection"""
        try:
            # Build nmcli command - exactly as you use it manually
            cmd = [
                'sudo', 'nmcli', 'device', 'wifi', 'connect',
                self.ssid
            ]
            
            # Add password if provided
            if self.password:
                cmd.extend(['password', self.password])
            
            self.logger.info(f"Running command: {' '.join(cmd)}")
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully connected to {self.ssid}")
                self.logger.info(f"Output: {result.stdout}")
                self._update_status("connected")
            else:
                self.logger.error(f"Failed to connect to {self.ssid}")
                self.logger.error(f"Error: {result.stderr}")
                self._update_status("error_connection_failed")
        
        except subprocess.TimeoutExpired:
            self.logger.error("WiFi connection timed out")
            self._update_status("error_timeout")
        
        except Exception as e:
            self.logger.error(f"Error connecting to WiFi: {e}")
            self._update_status("error_exception")
    
    def _update_status(self, status: str):
        """Update status and notify"""
        self.status = status
        self.logger.info(f"Status updated: {status}")
        if hasattr(self, 'status_char'):
            self.status_char.update_status(status)
    
    @dbus.service.method('org.freedesktop.DBus.Properties',
                        in_signature='s',
                        out_signature='a{sv}')
    def GetAll(self, interface):
        """Get all properties"""
        if interface != 'org.bluez.GattService1':
            raise dbus.exceptions.DBusException(
                'org.freedesktop.DBus.Error.InvalidArgs',
                'Invalid interface'
            )
        
        return {
            'UUID': WIFI_PROVISIONING_SERVICE_UUID,
            'Primary': True,
            'Characteristics': dbus.Array(
                [char.path for char in self.characteristics],
                signature='o'
            )
        }


class BLEWiFiGATTServer:
    """BLE GATT Server for WiFi Provisioning"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bus = None
        self.service = None
        self.mainloop = None
        self.thread = None
    
    def start(self) -> bool:
        """Start BLE GATT server"""
        try:
            self.logger.info("Starting BLE WiFi GATT server...")
            
            # Initialize DBus mainloop
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            
            # Get system bus
            self.bus = dbus.SystemBus()
            
            # Create WiFi provisioning service
            self.service = WiFiProvisioningService(self.bus, 0)
            
            # Register service with BlueZ
            self._register_service()
            
            # Start GLib mainloop in background thread
            self.mainloop = GLib.MainLoop()
            self.thread = threading.Thread(target=self.mainloop.run)
            self.thread.daemon = True
            self.thread.start()
            
            self.logger.info("BLE WiFi GATT server started successfully")
            self.logger.info(f"Service UUID: {WIFI_PROVISIONING_SERVICE_UUID}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to start BLE GATT server: {e}")
            return False
    
    def _register_service(self):
        """Register GATT service with BlueZ"""
        try:
            # Get GATT Manager
            adapter_path = '/org/bluez/hci0'
            adapter = dbus.Interface(
                self.bus.get_object('org.bluez', adapter_path),
                'org.bluez.GattManager1'
            )
            
            # Register service
            adapter.RegisterApplication(
                self.service.path,
                {},
                reply_handler=self._register_success,
                error_handler=self._register_error
            )
        
        except Exception as e:
            self.logger.error(f"Failed to register GATT service: {e}")
            raise
    
    def _register_success(self):
        """Service registration successful"""
        self.logger.info("GATT service registered successfully")
    
    def _register_error(self, error):
        """Service registration failed"""
        self.logger.error(f"GATT service registration failed: {error}")
    
    def stop(self):
        """Stop BLE GATT server"""
        try:
            if self.mainloop:
                self.mainloop.quit()
            self.logger.info("BLE WiFi GATT server stopped")
        except Exception as e:
            self.logger.error(f"Error stopping BLE GATT server: {e}")


# Singleton instance
_gatt_server: Optional[BLEWiFiGATTServer] = None


def start_ble_wifi_gatt_server() -> bool:
    """Start BLE WiFi GATT server (singleton)"""
    global _gatt_server
    
    if _gatt_server is None:
        _gatt_server = BLEWiFiGATTServer()
    
    return _gatt_server.start()


def stop_ble_wifi_gatt_server():
    """Stop BLE WiFi GATT server"""
    global _gatt_server
    
    if _gatt_server:
        _gatt_server.stop()
        _gatt_server = None


def get_gatt_server() -> Optional[BLEWiFiGATTServer]:
    """Get GATT server instance"""
    return _gatt_server
