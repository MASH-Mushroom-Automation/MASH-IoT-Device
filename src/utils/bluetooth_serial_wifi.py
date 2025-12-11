"""
Bluetooth Serial (RFCOMM) WiFi Provisioning
Simple and reliable - works without network layer!
"""

import logging
import subprocess
import threading
import json
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    logger.warning("PyBluez not available - Bluetooth Serial WiFi provisioning disabled")


class BluetoothSerialWiFiProvisioning:
    """Bluetooth Serial (RFCOMM) WiFi provisioning - no network needed!"""
    
    # Service UUID for WiFi provisioning
    SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
    SERVICE_NAME = "MASH-WiFi-Provisioning"
    
    def __init__(self):
        self.server_sock = None
        self.running = False
        self.thread = None
        
    def start(self):
        """Start Bluetooth Serial server for WiFi provisioning"""
        if not BLUETOOTH_AVAILABLE:
            logger.error("PyBluez not installed - cannot start Bluetooth Serial")
            logger.info("Install with: sudo pip3 install pybluez")
            return False
            
        try:
            logger.info("Starting Bluetooth Serial WiFi provisioning...")
            
            # Create Bluetooth RFCOMM socket
            self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_sock.bind(("", bluetooth.PORT_ANY))
            self.server_sock.listen(1)
            
            port = self.server_sock.getsockname()[1]
            logger.info(f"Bluetooth Serial listening on RFCOMM channel {port}")
            
            # Advertise service
            bluetooth.advertise_service(
                self.server_sock,
                self.SERVICE_NAME,
                service_id=self.SERVICE_UUID,
                service_classes=[self.SERVICE_UUID, bluetooth.SERIAL_PORT_CLASS],
                profiles=[bluetooth.SERIAL_PORT_PROFILE]
            )
            
            logger.info(f"Bluetooth Serial service advertised: {self.SERVICE_NAME}")
            logger.info(f"Service UUID: {self.SERVICE_UUID}")
            logger.info("Mobile app can now send WiFi credentials via Bluetooth Serial")
            
            # Start server thread
            self.running = True
            self.thread = threading.Thread(target=self._server_loop, daemon=True)
            self.thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Bluetooth Serial server: {e}")
            return False
    
    def _server_loop(self):
        """Server loop to accept connections"""
        while self.running:
            try:
                logger.info("Waiting for Bluetooth Serial connection...")
                client_sock, client_info = self.server_sock.accept()
                logger.info(f"Bluetooth Serial connection from {client_info}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_sock, client_info),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Server loop error: {e}")
    
    def _handle_client(self, client_sock, client_info):
        """Handle WiFi provisioning from client"""
        try:
            logger.info("Receiving WiFi credentials via Bluetooth Serial...")
            
            # Receive data (up to 4KB)
            data = client_sock.recv(4096)
            
            if not data:
                logger.warning("No data received")
                return
            
            # Decode data
            data_str = data.decode('utf-8').strip()
            logger.info(f"Received {len(data_str)} bytes")
            
            # Parse JSON
            try:
                credentials = json.loads(data_str)
                ssid = credentials.get('ssid')
                password = credentials.get('password')
            except json.JSONDecodeError:
                # Fallback: try pipe-separated format (SSID|PASSWORD)
                if '|' in data_str:
                    parts = data_str.split('|', 1)
                    ssid = parts[0]
                    password = parts[1] if len(parts) > 1 else None
                else:
                    logger.error("Invalid data format")
                    response = json.dumps({'success': False, 'error': 'Invalid format'})
                    client_sock.send(response.encode('utf-8'))
                    return
            
            if not ssid:
                logger.error("No SSID provided")
                response = json.dumps({'success': False, 'error': 'No SSID'})
                client_sock.send(response.encode('utf-8'))
                return
            
            logger.info(f"Connecting to WiFi: {ssid}")
            
            # Connect to WiFi
            success = self._connect_to_wifi(ssid, password)
            
            # Send response
            response = json.dumps({'success': success})
            client_sock.send(response.encode('utf-8'))
            
            if success:
                logger.info(f"Successfully connected to {ssid}")
            else:
                logger.error(f"Failed to connect to {ssid}")
                
        except Exception as e:
            logger.error(f"Error handling client: {e}")
            try:
                response = json.dumps({'success': False, 'error': str(e)})
                client_sock.send(response.encode('utf-8'))
            except:
                pass
        finally:
            try:
                client_sock.close()
            except:
                pass
    
    def _connect_to_wifi(self, ssid: str, password: Optional[str]) -> bool:
        """Connect to WiFi using nmcli"""
        try:
            # Build nmcli command
            cmd = ['sudo', 'nmcli', 'device', 'wifi', 'connect', ssid]
            
            if password:
                cmd.extend(['password', password])
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"nmcli output: {result.stdout}")
                return True
            else:
                logger.error(f"nmcli error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("WiFi connection timed out")
            return False
        except Exception as e:
            logger.error(f"Error connecting to WiFi: {e}")
            return False
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_sock:
            try:
                self.server_sock.close()
            except:
                pass
        logger.info("Bluetooth Serial WiFi provisioning stopped")


# Singleton instance
_bt_serial_provisioning: Optional[BluetoothSerialWiFiProvisioning] = None


def start_bluetooth_serial_wifi_provisioning() -> bool:
    """Start Bluetooth Serial WiFi provisioning"""
    global _bt_serial_provisioning
    
    if _bt_serial_provisioning is None:
        _bt_serial_provisioning = BluetoothSerialWiFiProvisioning()
    
    return _bt_serial_provisioning.start()


def stop_bluetooth_serial_wifi_provisioning():
    """Stop Bluetooth Serial WiFi provisioning"""
    global _bt_serial_provisioning
    
    if _bt_serial_provisioning:
        _bt_serial_provisioning.stop()
        _bt_serial_provisioning = None
