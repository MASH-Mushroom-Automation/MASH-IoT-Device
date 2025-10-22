"""
MQTT Client for MASH IoT Device
Handles MQTT connection and message processing
"""

import json
import time
import logging
import threading
from typing import Optional, Dict, Any, Callable

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    # Mock MQTT for development
    class mqtt:
        Client = object
        MQTTv5 = 5
        MQTTv311 = 4


class MQTTClient:
    """MQTT Client for MASH IoT Device"""
    
    def __init__(self, 
                 broker_url: str,
                 client_id: str,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 keepalive: int = 60,
                 qos: int = 1,
                 mock_mode: bool = False):
        """
        Initialize MQTT client
        
        Args:
            broker_url: MQTT broker URL (e.g., mqtt://localhost:1883)
            client_id: MQTT client ID
            username: MQTT username
            password: MQTT password
            keepalive: MQTT keepalive interval in seconds
            qos: MQTT QoS level
            mock_mode: Use mock MQTT client
        """
        self.logger = logging.getLogger(__name__)
        self.broker_url = broker_url.replace('mqtt://', '')
        self.client_id = client_id
        self.username = username
        self.password = password
        self.keepalive = keepalive
        self.qos = qos
        self.mock_mode = mock_mode or not MQTT_AVAILABLE
        
        # State variables
        self.client = None
        self.connected = False
        self.reconnect_delay = 5
        self.max_reconnect_delay = 300
        self.running = False
        
        # Topics
        self.base_topic = f"mash/devices/{client_id}"
        self.command_topic = f"{self.base_topic}/commands"
        self.status_topic = f"{self.base_topic}/status"
        self.telemetry_topic = f"{self.base_topic}/telemetry"
        
        # Callbacks
        self.on_command_callbacks = {}
        
        # Initialize client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize MQTT client"""
        if self.mock_mode:
            self.logger.info("MQTT client running in mock mode")
            return
        
        try:
            # Create client
            self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv5)
            
            # Set credentials if provided
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            self.client.on_subscribe = self._on_subscribe
            
            self.logger.info("MQTT client initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MQTT client: {e}")
            self.mock_mode = True
    
    def connect(self) -> bool:
        """
        Connect to MQTT broker
        
        Returns:
            True if connected successfully, False otherwise
        """
        if self.mock_mode:
            self.logger.info("Mock MQTT client connected")
            self.connected = True
            return True
        
        try:
            # Parse broker URL
            if ':' in self.broker_url:
                host, port_str = self.broker_url.split(':')
                port = int(port_str)
            else:
                host = self.broker_url
                port = 1883
            
            # Connect to broker
            self.logger.info(f"Connecting to MQTT broker: {host}:{port}")
            self.client.connect_async(host, port, keepalive=self.keepalive)
            
            # Start network loop
            self.client.loop_start()
            
            # Wait for connection
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < 10:
                time.sleep(0.1)
            
            return self.connected
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.running = False
        
        if self.mock_mode:
            self.logger.info("Mock MQTT client disconnected")
            self.connected = False
            return
        
        try:
            if self.client and self.connected:
                self.client.disconnect()
                self.client.loop_stop()
                self.logger.info("MQTT client disconnected")
        except Exception as e:
            self.logger.error(f"Error disconnecting MQTT client: {e}")
    
    def publish_telemetry(self, data: Dict[str, Any]) -> bool:
        """
        Publish telemetry data
        
        Args:
            data: Telemetry data to publish
            
        Returns:
            True if published successfully, False otherwise
        """
        if self.mock_mode:
            self.logger.debug(f"Mock MQTT publish telemetry: {data}")
            return True
        
        try:
            if not self.connected:
                self.logger.warning("Cannot publish telemetry: not connected")
                return False
            
            payload = json.dumps(data)
            result = self.client.publish(self.telemetry_topic, payload, qos=self.qos)
            
            if result.rc == 0:
                self.logger.debug(f"Published telemetry: {data}")
                return True
            else:
                self.logger.error(f"Failed to publish telemetry: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error publishing telemetry: {e}")
            return False
    
    def publish_status(self, status: Dict[str, Any]) -> bool:
        """
        Publish device status
        
        Args:
            status: Status data to publish
            
        Returns:
            True if published successfully, False otherwise
        """
        if self.mock_mode:
            self.logger.debug(f"Mock MQTT publish status: {status}")
            return True
        
        try:
            if not self.connected:
                self.logger.warning("Cannot publish status: not connected")
                return False
            
            payload = json.dumps(status)
            result = self.client.publish(self.status_topic, payload, qos=self.qos, retain=True)
            
            if result.rc == 0:
                self.logger.debug(f"Published status: {status}")
                return True
            else:
                self.logger.error(f"Failed to publish status: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error publishing status: {e}")
            return False
    
    def register_command_handler(self, command_type: str, callback: Callable[[Dict[str, Any]], None]):
        """
        Register command handler
        
        Args:
            command_type: Command type to handle
            callback: Callback function to call when command is received
        """
        self.on_command_callbacks[command_type] = callback
        self.logger.debug(f"Registered command handler for: {command_type}")
    
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """MQTT on_connect callback"""
        if rc == 0:
            self.connected = True
            self.logger.info("Connected to MQTT broker")
            
            # Subscribe to command topic
            self.client.subscribe(f"{self.command_topic}/#", qos=self.qos)
            
            # Publish online status
            self.publish_status({"status": "online", "timestamp": time.time()})
        else:
            self.connected = False
            self.logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT on_disconnect callback"""
        self.connected = False
        self.logger.warning(f"Disconnected from MQTT broker: {rc}")
        
        # Implement reconnection if still running
        if self.running:
            threading.Thread(target=self._reconnect_thread).start()
    
    def _reconnect_thread(self):
        """Reconnect thread"""
        delay = self.reconnect_delay
        
        while self.running and not self.connected:
            self.logger.info(f"Attempting to reconnect in {delay} seconds...")
            time.sleep(delay)
            
            try:
                self.client.reconnect()
                self.logger.info("Reconnected to MQTT broker")
            except Exception as e:
                self.logger.error(f"Failed to reconnect: {e}")
                delay = min(delay * 2, self.max_reconnect_delay)
    
    def _on_message(self, client, userdata, msg):
        """MQTT on_message callback"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            self.logger.debug(f"Received message: {topic} = {payload}")
            
            # Process command messages
            if topic.startswith(self.command_topic):
                command_data = json.loads(payload)
                command_type = command_data.get('command_type')
                
                if command_type in self.on_command_callbacks:
                    self.logger.info(f"Processing command: {command_type}")
                    self.on_command_callbacks[command_type](command_data)
                else:
                    self.logger.warning(f"No handler for command type: {command_type}")
                    
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in message: {payload}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        """MQTT on_subscribe callback"""
        self.logger.debug(f"Subscribed to topics with QoS: {granted_qos}")
