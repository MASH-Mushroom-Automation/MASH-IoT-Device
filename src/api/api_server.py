"""
API Server for MASH IoT Device
Provides a local REST API for direct device control
"""

import os
import json
import logging
import threading
from typing import Optional, Dict, Any, Callable

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
        
        # Register resources
        self.api.add_resource(SensorDataResource, '/api/v1/sensors/latest')
        self.api.add_resource(DeviceStatusResource, '/api/v1/status')
        self.api.add_resource(CommandResource, '/api/v1/commands/<string:command_type>')
    
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
