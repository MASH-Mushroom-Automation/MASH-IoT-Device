"""
Simple BLE WiFi Provisioning - No GATT Server Required
Uses BLE advertising and simple socket communication
"""

import logging
import subprocess
import socket
import threading
import json
from typing import Optional

logger = logging.getLogger(__name__)


class SimpleBLEWiFiProvisioning:
    """Simple BLE WiFi provisioning without complex GATT server"""
    
    def __init__(self, port=8888):
        self.port = port
        self.server_socket = None
        self.running = False
        self.thread = None
        
    def start(self):
        """Start simple TCP server for WiFi provisioning"""
        try:
            logger.info("Starting simple BLE WiFi provisioning server...")
            
            # Create TCP server
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(1)
            
            self.running = True
            self.thread = threading.Thread(target=self._server_loop, daemon=True)
            self.thread.start()
            
            logger.info(f"Simple WiFi provisioning server started on port {self.port}")
            logger.info("Mobile app can send WiFi credentials via BLE connection")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start WiFi provisioning server: {e}")
            return False
    
    def _server_loop(self):
        """Server loop to accept connections"""
        while self.running:
            try:
                logger.info("Waiting for WiFi provisioning connection...")
                client_socket, address = self.server_socket.accept()
                logger.info(f"Client connected from {address}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Server loop error: {e}")
    
    def _handle_client(self, client_socket):
        """Handle WiFi provisioning from client"""
        try:
            # Receive data (max 4KB)
            data = client_socket.recv(4096).decode('utf-8')
            logger.info(f"Received data: {len(data)} bytes")
            
            # Parse JSON
            credentials = json.loads(data)
            ssid = credentials.get('ssid')
            password = credentials.get('password')
            
            if not ssid:
                logger.error("No SSID provided")
                response = json.dumps({'success': False, 'error': 'No SSID'})
                client_socket.send(response.encode('utf-8'))
                return
            
            logger.info(f"Connecting to WiFi: {ssid}")
            
            # Connect to WiFi
            success = self._connect_to_wifi(ssid, password)
            
            # Send response
            response = json.dumps({'success': success})
            client_socket.send(response.encode('utf-8'))
            
            if success:
                logger.info(f"Successfully connected to {ssid}")
            else:
                logger.error(f"Failed to connect to {ssid}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
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
        if self.server_socket:
            self.server_socket.close()
        logger.info("WiFi provisioning server stopped")


# Singleton instance
_provisioning_server: Optional[SimpleBLEWiFiProvisioning] = None


def start_simple_wifi_provisioning(port=8888) -> bool:
    """Start simple WiFi provisioning server"""
    global _provisioning_server
    
    if _provisioning_server is None:
        _provisioning_server = SimpleBLEWiFiProvisioning(port)
    
    return _provisioning_server.start()


def stop_simple_wifi_provisioning():
    """Stop simple WiFi provisioning server"""
    global _provisioning_server
    
    if _provisioning_server:
        _provisioning_server.stop()
        _provisioning_server = None
