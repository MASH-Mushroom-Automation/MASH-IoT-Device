"""
MASH Touchscreen UI - MQTT Client
Real-time communication with MQTT broker
"""

import logging
import json
from typing import Dict, Optional, Callable
import config

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logging.warning("paho-mqtt not installed, MQTT features disabled")

logger = logging.getLogger(__name__)


class MQTTClient:
    """MQTT client for real-time updates"""
    
    def __init__(self):
        self.enabled = config.MQTT_ENABLED and MQTT_AVAILABLE
        self.client = None
        self.connected = False
        
        # Callbacks
        self.on_sensor_data_callback = None
        self.on_actuator_update_callback = None
        self.on_status_update_callback = None
        
        if self.enabled:
            self._initialize()
        else:
            logger.info("MQTT client disabled or unavailable")
    
    def _initialize(self):
        """Initialize MQTT client"""
        try:
            # Parse broker URL
            broker_url = config.MQTT_BROKER_URL.replace('mqtt://', '')
            broker_parts = broker_url.split(':')
            broker_host = broker_parts[0]
            broker_port = int(broker_parts[1]) if len(broker_parts) > 1 else 1883
            
            # Create client
            self.client = mqtt.Client(client_id=config.MQTT_CLIENT_ID)
            
            # Set credentials if provided
            if config.MQTT_USERNAME and config.MQTT_PASSWORD:
                self.client.username_pw_set(
                    config.MQTT_USERNAME,
                    config.MQTT_PASSWORD
                )
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # Connect to broker
            logger.info(f"Connecting to MQTT broker: {broker_host}:{broker_port}")
            self.client.connect(broker_host, broker_port, keepalive=60)
            
            # Start network loop
            self.client.loop_start()
            
        except Exception as e:
            logger.error(f"Failed to initialize MQTT client: {e}")
            self.enabled = False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.connected = True
            logger.info("✅ Connected to MQTT broker")
            
            # Subscribe to topics
            topics = [
                (config.MQTT_TOPICS['sensor_data'], 0),
                (config.MQTT_TOPICS['actuator_control'], 0),
                (config.MQTT_TOPICS['device_status'], 0),
            ]
            
            for topic, qos in topics:
                self.client.subscribe(topic, qos)
                logger.info(f"Subscribed to: {topic}")
        else:
            logger.error(f"❌ Failed to connect to MQTT broker: rc={rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.connected = False
        if rc != 0:
            logger.warning(f"⚠️ Unexpected MQTT disconnection: rc={rc}")
        else:
            logger.info("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            logger.debug(f"MQTT message received: {topic}")
            
            # Route message to appropriate callback
            if topic == config.MQTT_TOPICS['sensor_data']:
                if self.on_sensor_data_callback:
                    self.on_sensor_data_callback(payload)
            
            elif topic == config.MQTT_TOPICS['actuator_control']:
                if self.on_actuator_update_callback:
                    self.on_actuator_update_callback(payload)
            
            elif topic == config.MQTT_TOPICS['device_status']:
                if self.on_status_update_callback:
                    self.on_status_update_callback(payload)
        
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def publish(self, topic: str, payload: Dict) -> bool:
        """
        Publish message to MQTT broker
        
        Args:
            topic: MQTT topic
            payload: Message payload (dict)
            
        Returns:
            True if published successfully
        """
        if not self.enabled or not self.connected:
            return False
        
        try:
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos=1)
            return result.rc == 0
        except Exception as e:
            logger.error(f"Failed to publish MQTT message: {e}")
            return False
    
    def publish_command(self, command: str, params: Dict = None) -> bool:
        """
        Publish command to device
        
        Args:
            command: Command name (e.g., 'set_actuator', 'set_mode')
            params: Command parameters
            
        Returns:
            True if published successfully
        """
        payload = {
            'command': command,
            'params': params or {},
            'source': 'touchscreen_ui'
        }
        return self.publish(config.MQTT_TOPICS['commands'], payload)
    
    def set_on_sensor_data(self, callback: Callable[[Dict], None]):
        """Set callback for sensor data updates"""
        self.on_sensor_data_callback = callback
    
    def set_on_actuator_update(self, callback: Callable[[Dict], None]):
        """Set callback for actuator state updates"""
        self.on_actuator_update_callback = callback
    
    def set_on_status_update(self, callback: Callable[[Dict], None]):
        """Set callback for device status updates"""
        self.on_status_update_callback = callback
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client and self.connected:
            logger.info("Disconnecting from MQTT broker...")
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False


# Singleton instance
_mqtt_client = None

def get_mqtt_client() -> MQTTClient:
    """Get singleton MQTT client instance"""
    global _mqtt_client
    if _mqtt_client is None:
        _mqtt_client = MQTTClient()
    return _mqtt_client
