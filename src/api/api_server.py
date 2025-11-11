"""
API Server for MASH IoT Device
Provides a local REST API for direct device control
"""

import os
import json
import logging
import threading
from typing import Optional, Dict, Any, Callable
from datetime import datetime

try:
    from flask import Flask, request, jsonify
    from flask_restful import Api, Resource
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    # Mock Flask for development
    class Flask:
        def __init__(self, *args, **kwargs):
            pass
        
        def run(self, *args, **kwargs):
            pass
    
    class Api:
        def __init__(self, *args, **kwargs):
            pass
        
        def add_resource(self, *args, **kwargs):
            pass
    
    class Resource:
        pass
    
    def jsonify(*args, **kwargs):
        return {}
    
    request = type('obj', (object,), {
        'json': {},
        'args': {},
        'form': {}
    })


class APIServer:
    """API Server for MASH IoT Device"""
    
    def __init__(self, 
                 host: str = '0.0.0.0',
                 port: int = 5000,
                 debug: bool = False,
                 mock_mode: bool = False):
        """
        Initialize API server
        
        Args:
            host: Host to listen on
            port: Port to listen on
            debug: Enable debug mode
            mock_mode: Use mock API server
        """
        self.logger = logging.getLogger(__name__)
        self.host = host
        self.port = port
        self.debug = debug
        self.mock_mode = mock_mode or not API_AVAILABLE
        
        # State variables
        self.app = None
        self.api = None
        self.server_thread = None
        self.running = False
        
        # Callbacks
        self.sensor_data_callback = None
        self.device_status_callback = None
        self.command_callbacks = {}
        self.wifi_scan_callback = None
        self.wifi_connect_callback = None
        self.provisioning_info_callback = None
        self.bluetooth_status_callback = None
        self.bluetooth_start_tethering_callback = None
        self.bluetooth_stop_tethering_callback = None
        
        # Initialize server
        self._initialize_server()
    
    def _initialize_server(self):
        """Initialize API server"""
        if self.mock_mode:
            self.logger.info("API server running in mock mode")
            return
        
        try:
            # Create Flask app
            self.app = Flask(__name__)
            self.api = Api(self.app)
            
            # Register routes
            self._register_routes()
            
            self.logger.info("API server initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize API server: {e}")
            self.mock_mode = True
    
    def _register_routes(self):
        """Register API routes"""
        if self.mock_mode:
            return
        
        # Clear existing resources before re-registering
        resources_attr = getattr(self.api, 'resources', None)
        if isinstance(resources_attr, dict):
            resources_attr.clear()
        endpoints_to_remove = [
            'sensordataresource',
            'devicestatusresource',
            'commandresource',
            'wifiscanresource',
            'wificonfigresource',
            'provisioninginforesource'
        ]
        for endpoint in endpoints_to_remove:
            if self.app:
                self.app.view_functions.pop(endpoint, None)
            if hasattr(self.api, 'endpoints'):
                endpoints_attr = getattr(self.api, 'endpoints')
                if isinstance(endpoints_attr, dict):
                    endpoints_attr.pop(endpoint, None)
                elif isinstance(endpoints_attr, set):
                    endpoints_attr.discard(endpoint)

        # Define resource classes
        sensor_data_callback = self.sensor_data_callback
        device_status_callback = self.device_status_callback
        command_callbacks = self.command_callbacks
        logger = self.logger
        
        class SensorDataResource(Resource):
            def get(self):
                try:
                    if sensor_data_callback:
                        data = sensor_data_callback()
                        return jsonify(data)
                    return jsonify({"error": "Sensor data not available"}), 503
                except Exception as e:
                    logger.error(f"Error in sensor data endpoint: {e}")
                    return jsonify({"error": str(e)}), 500
        
        class DeviceStatusResource(Resource):
            def get(self):
                try:
                    if device_status_callback:
                        status = device_status_callback()
                        return jsonify(status)
                    return jsonify({"error": "Device status not available"}), 503
                except Exception as e:
                    logger.error(f"Error in device status endpoint: {e}")
                    return jsonify({"error": str(e)}), 500
        
        class CommandResource(Resource):
            def post(self, command_type):
                try:
                    # Parse command data
                    command_data = request.json or {}
                    command_data['command_type'] = command_type
                    
                    logger.info(f"Received command: {command_type}")
                    
                    # Execute command
                    if command_type in command_callbacks:
                        result = command_callbacks[command_type](command_data)
                        return jsonify({"success": True, "result": result})
                    else:
                        return jsonify({"error": f"Unknown command: {command_type}"}), 400
                except Exception as e:
                    logger.error(f"Error executing command: {e}")
                    return jsonify({"error": str(e)}), 500
        
        # Provisioning endpoints
        wifi_scan_callback = self.wifi_scan_callback
        wifi_connect_callback = self.wifi_connect_callback
        provisioning_info_callback = self.provisioning_info_callback
        
        class WiFiScanResource(Resource):
            def get(self):
                try:
                    if wifi_scan_callback:
                        networks = wifi_scan_callback()
                        return jsonify({
                            "success": True,
                            "networks": [
                                {
                                    "ssid": n.ssid,
                                    "signal": n.signal_strength,
                                    "security": n.security,
                                    "frequency": n.frequency
                                } for n in networks
                            ],
                            "timestamp": datetime.now().isoformat()
                        })
                    return jsonify({"error": "WiFi scan not available"}), 503
                except Exception as e:
                    logger.error(f"Error in WiFi scan endpoint: {e}")
                    return jsonify({"error": str(e)}), 500
        
        class WiFiConfigResource(Resource):
            def post(self):
                try:
                    data = request.json or {}
                    ssid = data.get('ssid')
                    password = data.get('password', '')
                    
                    if not ssid:
                        return jsonify({"error": "SSID is required"}), 400
                    
                    logger.info(f"WiFi configuration request for SSID: {ssid}")
                    
                    if wifi_connect_callback:
                        success = wifi_connect_callback(ssid, password)
                        if success:
                            return jsonify({
                                "success": True,
                                "message": f"Connecting to {ssid}",
                                "timestamp": datetime.now().isoformat()
                            })
                        else:
                            return jsonify({
                                "success": False,
                                "error": "Failed to connect to WiFi"
                            }), 500
                    
                    return jsonify({"error": "WiFi configuration not available"}), 503
                except Exception as e:
                    logger.error(f"Error in WiFi config endpoint: {e}")
                    return jsonify({"error": str(e)}), 500
        
        class ProvisioningInfoResource(Resource):
            def get(self):
                try:
                    if provisioning_info_callback:
                        info = provisioning_info_callback()
                        return jsonify({
                            "success": True,
                            "data": info,
                            "timestamp": datetime.now().isoformat()
                        })
                    return jsonify({"error": "Provisioning info not available"}), 503
                except Exception as e:
                    logger.error(f"Error in provisioning info endpoint: {e}")
                    return jsonify({"error": str(e)}), 500
        
        # Bluetooth endpoints
        bluetooth_status_callback = self.bluetooth_status_callback
        bluetooth_start_tethering_callback = self.bluetooth_start_tethering_callback
        bluetooth_stop_tethering_callback = self.bluetooth_stop_tethering_callback
        
        class BluetoothStatusResource(Resource):
            def get(self):
                try:
                    if bluetooth_status_callback:
                        status = bluetooth_status_callback()
                        return jsonify({
                            "success": True,
                            "data": status,
                            "timestamp": datetime.now().isoformat()
                        })
                    return jsonify({"error": "Bluetooth not available"}), 503
                except Exception as e:
                    logger.error(f"Error in Bluetooth status endpoint: {e}")
                    return jsonify({"error": str(e)}), 500
        
        class BluetoothTetheringResource(Resource):
            def post(self):
                try:
                    data = request.json or {}
                    action = data.get('action', 'start')
                    
                    if action == 'start':
                        if bluetooth_start_tethering_callback:
                            success = bluetooth_start_tethering_callback()
                            return jsonify({
                                "success": success,
                                "message": "Bluetooth tethering started" if success else "Failed to start",
                                "timestamp": datetime.now().isoformat()
                            })
                    elif action == 'stop':
                        if bluetooth_stop_tethering_callback:
                            success = bluetooth_stop_tethering_callback()
                            return jsonify({
                                "success": success,
                                "message": "Bluetooth tethering stopped" if success else "Failed to stop",
                                "timestamp": datetime.now().isoformat()
                            })
                    
                    return jsonify({"error": "Invalid action"}), 400
                except Exception as e:
                    logger.error(f"Error in Bluetooth tethering endpoint: {e}")
                    return jsonify({"error": str(e)}), 500
        
        # Register resources
        self.api.add_resource(SensorDataResource, '/api/v1/sensors/latest')
        self.api.add_resource(DeviceStatusResource, '/api/v1/status')
        self.api.add_resource(CommandResource, '/api/v1/commands/<string:command_type>')
        
        # Provisioning endpoints
        self.api.add_resource(WiFiScanResource, '/api/v1/wifi/scan')
        self.api.add_resource(WiFiConfigResource, '/api/v1/wifi/config')
        self.api.add_resource(ProvisioningInfoResource, '/api/v1/provisioning/info')
        
        # Bluetooth endpoints
        self.api.add_resource(BluetoothStatusResource, '/api/v1/bluetooth/status')
        self.api.add_resource(BluetoothTetheringResource, '/api/v1/bluetooth/tethering')
    
    
    def start(self) -> bool:
        """
        Start API server
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            self.logger.warning("API server already running")
            return True
        
        if self.mock_mode:
            self.logger.info("Mock API server started")
            self.running = True
            return True
        
        try:
            # Start server in a separate thread
            self.server_thread = threading.Thread(
                target=self.app.run,
                kwargs={
                    'host': self.host,
                    'port': self.port,
                    'debug': self.debug,
                    'use_reloader': False
                }
            )
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            self.logger.info(f"API server started on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start API server: {e}")
            return False
    
    def stop(self):
        """Stop API server"""
        self.running = False
        
        if self.mock_mode:
            self.logger.info("Mock API server stopped")
            return
        
        try:
            # Flask doesn't have a clean shutdown method
            # We'll rely on the daemon thread to exit when the main thread exits
            self.logger.info("API server stopped")
        except Exception as e:
            self.logger.error(f"Error stopping API server: {e}")
    
    def register_sensor_data_callback(self, callback: Callable[[], Dict[str, Any]]):
        """
        Register sensor data callback
        
        Args:
            callback: Callback function to provide sensor data
        """
        self.sensor_data_callback = callback
        self.logger.debug("Registered sensor data callback")
    
    def register_device_status_callback(self, callback: Callable[[], Dict[str, Any]]):
        """
        Register device status callback
        
        Args:
            callback: Callback function to provide device status
        """
        self.device_status_callback = callback
        self.logger.debug("Registered device status callback")
    
    def register_command_handler(self, command_type: str, callback: Callable[[Dict[str, Any]], Any]):
        """
        Register command handler
        
        Args:
            command_type: Command type to handle
            callback: Callback function to call when command is received
        """
        self.command_callbacks[command_type] = callback
        self.logger.debug(f"Registered command handler for: {command_type}")
        
        # Re-register routes if server is already initialized
        if self.api and not self.mock_mode:
            self._register_routes()
    
    def register_wifi_scan_callback(self, callback: Callable[[], list]):
        """
        Register WiFi scan callback
        
        Args:
            callback: Callback function to scan for WiFi networks
        """
        self.wifi_scan_callback = callback
        self.logger.debug("Registered WiFi scan callback")
    
    def register_wifi_connect_callback(self, callback: Callable[[str, str], bool]):
        """
        Register WiFi connect callback
        
        Args:
            callback: Callback function to connect to WiFi
        """
        self.wifi_connect_callback = callback
        self.logger.debug("Registered WiFi connect callback")
    
    def register_provisioning_info_callback(self, callback: Callable[[], Dict[str, Any]]):
        """
        Register provisioning info callback
        
        Args:
            callback: Callback function to get provisioning info
        """
        self.provisioning_info_callback = callback
        self.logger.debug("Registered provisioning info callback")
    
    def register_bluetooth_status_callback(self, callback: Callable[[], Dict[str, Any]]):
        """
        Register Bluetooth status callback
        
        Args:
            callback: Callback function to get Bluetooth status
        """
        self.bluetooth_status_callback = callback
        self.logger.debug("Registered Bluetooth status callback")
    
    def register_bluetooth_start_tethering_callback(self, callback: Callable[[], bool]):
        """
        Register Bluetooth start tethering callback
        
        Args:
            callback: Callback function to start Bluetooth tethering
        """
        self.bluetooth_start_tethering_callback = callback
        self.logger.debug("Registered Bluetooth start tethering callback")
    
    def register_bluetooth_stop_tethering_callback(self, callback: Callable[[], bool]):
        """
        Register Bluetooth stop tethering callback
        
        Args:
            callback: Callback function to stop Bluetooth tethering
        """
        self.bluetooth_stop_tethering_callback = callback
        self.logger.debug("Registered Bluetooth stop tethering callback")
