"""
Sync Manager
Handles synchronization of local data with backend services
"""

import time
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from queue import Queue, Empty
import threading

from .database_manager import DatabaseManager


class SyncManager:
    """Manages synchronization of local data with backend"""
    
    def __init__(self, 
                 database_manager: DatabaseManager,
                 backend_api_url: str,
                 api_key: Optional[str] = None,
                 sync_interval: int = 300,
                 batch_size: int = 100,
                 max_retries: int = 3):
        """
        Initialize sync manager
        
        Args:
            database_manager: Database manager instance
            backend_api_url: Backend API base URL
            api_key: API key for authentication
            sync_interval: Sync interval in seconds
            batch_size: Number of records to sync per batch
            max_retries: Maximum retry attempts for failed syncs
        """
        self.logger = logging.getLogger(__name__)
        self.db = database_manager
        self.backend_api_url = backend_api_url.rstrip('/')
        self.api_key = api_key
        self.sync_interval = sync_interval
        self.batch_size = batch_size
        self.max_retries = max_retries
        
        # Sync control
        self._running = False
        self._thread = None
        self._stop_event = threading.Event()
        
        # Statistics
        self.sync_count = 0
        self.error_count = 0
        self.last_sync_time = None
        
        # Request session for connection pooling
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def start(self) -> bool:
        """
        Start automatic synchronization
        
        Returns:
            True if started successfully, False otherwise
        """
        if self._running:
            self.logger.warning("Sync manager already running")
            return True
        
        try:
            self._running = True
            self._stop_event.clear()
            
            # Start sync thread
            self._thread = threading.Thread(target=self._sync_loop, daemon=True)
            self._thread.start()
            
            self.logger.info(f"Sync manager started (interval: {self.sync_interval}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start sync manager: {e}")
            self._running = False
            return False
    
    def stop(self):
        """Stop automatic synchronization"""
        if not self._running:
            return
        
        self.logger.info("Stopping sync manager...")
        self._running = False
        self._stop_event.set()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        
        self.logger.info("Sync manager stopped")
    
    def _sync_loop(self):
        """Main synchronization loop (runs in separate thread)"""
        self.logger.info("Sync loop started")
        
        while self._running and not self._stop_event.is_set():
            try:
                # Perform sync
                self.sync_all_data()
                
                # Wait for next sync
                if self._stop_event.wait(self.sync_interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in sync loop: {e}")
                self.error_count += 1
                time.sleep(10)  # Brief pause before retry
        
        self.logger.info("Sync loop ended")
    
    def sync_all_data(self) -> bool:
        """
        Synchronize all pending data
        
        Returns:
            True if sync successful, False otherwise
        """
        try:
            self.logger.debug("Starting data synchronization...")
            
            # Sync sensor readings
            sensor_synced = self.sync_sensor_readings()
            
            # Sync alerts
            alerts_synced = self.sync_alerts()
            
            # Sync actuator states
            actuators_synced = self.sync_actuator_states()
            
            # Update sync timestamp
            if sensor_synced or alerts_synced or actuators_synced:
                self.last_sync_time = datetime.now()
                self.sync_count += 1
                self.logger.info(f"Sync completed: readings={sensor_synced}, alerts={alerts_synced}, actuators={actuators_synced}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            self.error_count += 1
            return False
    
    def sync_sensor_readings(self) -> bool:
        """
        Synchronize sensor readings with backend
        
        Returns:
            True if sync successful, False otherwise
        """
        try:
            # Get unsynced readings
            readings = self.db.get_unsynced_sensor_readings(limit=self.batch_size)
            if not readings:
                return True  # Nothing to sync
            
            self.logger.debug(f"Syncing {len(readings)} sensor readings...")
            
            # Prepare data for backend
            sync_data = []
            reading_ids = []
            
            for reading in readings:
                sync_data.append({
                    'device_id': reading['device_id'],
                    'sensor_type': reading['sensor_type'],
                    'value': reading['value'],
                    'unit': reading['unit'],
                    'quality_indicator': reading['quality_indicator'],
                    'timestamp': reading['timestamp'],
                    'metadata': reading.get('metadata', {})
                })
                reading_ids.append(reading['id'])
            
            # Send to backend
            response = self.session.post(
                f"{self.backend_api_url}/sensors/data",
                json={'readings': sync_data},
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse response to get backend IDs
                result = response.json()
                backend_ids = result.get('reading_ids', [])
                
                # Mark as synced
                if len(backend_ids) == len(reading_ids):
                    self.db.mark_sensor_readings_synced(reading_ids, backend_ids)
                    self.logger.info(f"Synced {len(readings)} sensor readings")
                    return True
                else:
                    self.logger.warning(f"Backend returned {len(backend_ids)} IDs for {len(reading_ids)} readings")
                    return False
            else:
                self.logger.error(f"Backend sync failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Sensor readings sync failed: {e}")
            return False
    
    def sync_alerts(self) -> bool:
        """
        Synchronize alerts with backend
        
        Returns:
            True if sync successful, False otherwise
        """
        try:
            # Get unsynced alerts
            alerts = self.db.get_unsynced_alerts(limit=self.batch_size)
            if not alerts:
                return True  # Nothing to sync
            
            self.logger.debug(f"Syncing {len(alerts)} alerts...")
            
            # Prepare data for backend
            sync_data = []
            alert_ids = []
            
            for alert in alerts:
                sync_data.append({
                    'device_id': alert['device_id'],
                    'alert_type': alert['alert_type'],
                    'severity': alert['severity'],
                    'title': alert['title'],
                    'message': alert['message'],
                    'threshold_config': alert.get('threshold_config', {}),
                    'trigger_value': alert.get('trigger_value'),
                    'current_value': alert.get('current_value'),
                    'metadata': alert.get('metadata', {})
                })
                alert_ids.append(alert['id'])
            
            # Send to backend
            response = self.session.post(
                f"{self.backend_api_url}/alerts",
                json={'alerts': sync_data},
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse response to get backend IDs
                result = response.json()
                backend_ids = result.get('alert_ids', [])
                
                # Mark as synced
                if len(backend_ids) == len(alert_ids):
                    # Update alerts with backend IDs
                    for local_id, backend_id in zip(alert_ids, backend_ids):
                        # This would need to be implemented in DatabaseManager
                        pass
                    
                    self.logger.info(f"Synced {len(alerts)} alerts")
                    return True
                else:
                    self.logger.warning(f"Backend returned {len(backend_ids)} IDs for {len(alert_ids)} alerts")
                    return False
            else:
                self.logger.error(f"Backend alerts sync failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Alerts sync failed: {e}")
            return False
    
    def sync_actuator_states(self) -> bool:
        """
        Synchronize actuator states with backend
        
        Returns:
            True if sync successful, False otherwise
        """
        # This would be implemented when actuator control is added
        return True
    
    def get_pending_commands(self, device_id: str) -> List[Dict[str, Any]]:
        """
        Get pending commands from backend
        
        Args:
            device_id: Device ID to get commands for
            
        Returns:
            List of pending commands
        """
        try:
            response = self.session.get(
                f"{self.backend_api_url}/devices/{device_id}/commands",
                timeout=30
            )
            
            if response.status_code == 200:
                commands = response.json().get('commands', [])
                self.logger.debug(f"Retrieved {len(commands)} pending commands")
                return commands
            else:
                self.logger.error(f"Failed to get commands: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to get pending commands: {e}")
            return []
    
    def send_command_acknowledgment(self, command_id: str, status: str, 
                                  error_message: Optional[str] = None) -> bool:
        """
        Send command acknowledgment to backend
        
        Args:
            command_id: Command ID to acknowledge
            status: Command status
            error_message: Error message if failed
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            data = {
                'command_id': command_id,
                'status': status,
                'timestamp': datetime.now().isoformat()
            }
            
            if error_message:
                data['error_message'] = error_message
            
            response = self.session.post(
                f"{self.backend_api_url}/commands/acknowledge",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Command {command_id} acknowledged with status {status}")
                return True
            else:
                self.logger.error(f"Failed to acknowledge command: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send command acknowledgment: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get sync manager statistics"""
        return {
            'running': self._running,
            'sync_interval': self.sync_interval,
            'batch_size': self.batch_size,
            'sync_count': self.sync_count,
            'error_count': self.error_count,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'backend_api_url': self.backend_api_url
        }
    
    def is_running(self) -> bool:
        """Check if sync manager is running"""
        return self._running
    
    def force_sync(self) -> bool:
        """
        Force immediate synchronization
        
        Returns:
            True if sync successful, False otherwise
        """
        self.logger.info("Forcing immediate synchronization...")
        return self.sync_all_data()
    
    def close(self):
        """Close sync manager and cleanup resources"""
        self.stop()
        self.session.close()
        self.logger.info("Sync manager closed")
