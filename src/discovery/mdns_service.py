"""
mDNS Service for MASH IoT Device
Provides local network discovery using mDNS/Zeroconf
"""

import socket
import logging
import threading
from typing import Optional, Dict, Any

try:
    from zeroconf import ServiceInfo, Zeroconf
    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False
    # Mock Zeroconf for development
    class ServiceInfo:
        def __init__(self, *args, **kwargs):
            pass
    
    class Zeroconf:
        def __init__(self, *args, **kwargs):
            pass
        
        def register_service(self, *args, **kwargs):
            pass
        
        def unregister_service(self, *args, **kwargs):
            pass
        
        def close(self):
            pass


class MDNSService:
    """mDNS Service for MASH IoT Device"""
    
    def __init__(self, 
                 device_id: str,
                 service_name: str = 'MASH IoT Device',
                 service_type: str = '_mash-iot._tcp.local.',
                 port: int = 5000,
                 mock_mode: bool = False):
        """
        Initialize mDNS service
        
        Args:
            device_id: Device ID
            service_name: Service name
            service_type: Service type
            port: Service port
            mock_mode: Use mock mDNS service
        """
        self.logger = logging.getLogger(__name__)
        self.device_id = device_id
        self.service_name = service_name
        self.service_type = service_type
        self.port = port
        self.mock_mode = mock_mode or not ZEROCONF_AVAILABLE
        
        # State variables
        self.zeroconf = None
        self.service_info = None
        self.running = False
        
        # Get local IP address
        self.local_ip = self._get_local_ip()
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Create a socket to determine the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            # Fallback to localhost
            return '127.0.0.1'
    
    def start(self) -> bool:
        """
        Start mDNS service
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            self.logger.warning("mDNS service already running")
            return True
        
        if self.mock_mode:
            self.logger.info("Mock mDNS service started")
            self.running = True
            return True
        
        try:
            # Create service info
            self.service_info = ServiceInfo(
                self.service_type,
                f"{self.device_id}.{self.service_type}",
                addresses=[socket.inet_aton(self.local_ip)],
                port=self.port,
                properties={
                    'device_id': self.device_id,
                    'name': self.service_name,
                    'type': 'mash-iot-device',
                    'api_version': 'v1'
                }
            )
            
            # Register service
            self.zeroconf = Zeroconf()
            self.zeroconf.register_service(self.service_info)
            
            self.running = True
            self.logger.info(f"mDNS service started: {self.device_id} at {self.local_ip}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start mDNS service: {e}")
            return False
    
    def stop(self):
        """Stop mDNS service"""
        self.running = False
        
        if self.mock_mode:
            self.logger.info("Mock mDNS service stopped")
            return
        
        try:
            if self.zeroconf and self.service_info:
                self.zeroconf.unregister_service(self.service_info)
                self.zeroconf.close()
                self.logger.info("mDNS service stopped")
        except Exception as e:
            self.logger.error(f"Error stopping mDNS service: {e}")
    
    def update_properties(self, properties: Dict[str, Any]) -> bool:
        """
        Update service properties
        
        Args:
            properties: Properties to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        if self.mock_mode:
            self.logger.debug(f"Mock mDNS update properties: {properties}")
            return True
        
        try:
            if not self.running:
                self.logger.warning("Cannot update properties: service not running")
                return False
            
            # Update service info
            # Note: Zeroconf doesn't support updating properties directly
            # We need to unregister and re-register the service
            
            # Unregister current service
            self.zeroconf.unregister_service(self.service_info)
            
            # Create new service info with updated properties
            all_properties = self.service_info.properties.copy()
            all_properties.update(properties)
            
            self.service_info = ServiceInfo(
                self.service_type,
                f"{self.device_id}.{self.service_type}",
                addresses=[socket.inet_aton(self.local_ip)],
                port=self.port,
                properties=all_properties
            )
            
            # Register updated service
            self.zeroconf.register_service(self.service_info)
            
            self.logger.debug(f"Updated mDNS properties: {properties}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update mDNS properties: {e}")
            return False
