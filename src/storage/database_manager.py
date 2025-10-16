"""
Database Manager
Handles SQLite database operations with connection pooling and transaction management
"""

import sqlite3
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
import uuid

from .schema import DatabaseSchema


class DatabaseManager:
    """Manages SQLite database operations with connection pooling"""
    
    def __init__(self, db_path: str, timeout: int = 30):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
            timeout: Database connection timeout in seconds
        """
        self.db_path = db_path
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        
        # Initialize schema
        self.schema = DatabaseSchema(db_path)
        
        # Create database and schema if needed
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database and create schema if needed"""
        try:
            # Create database directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Create schema if database is new
            if not self.schema.validate_schema():
                self.logger.info("Creating database schema...")
                if not self.schema.create_schema():
                    raise Exception("Failed to create database schema")
            
            self.logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path, 
                timeout=self.timeout,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def store_sensor_reading(self, reading_data: Dict[str, Any]) -> bool:
        """
        Store sensor reading in database
        
        Args:
            reading_data: Dictionary containing sensor reading data
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Generate UUID if not provided
                if 'id' not in reading_data:
                    reading_data['id'] = str(uuid.uuid4())
                
                # Handle different sensor types from SCD41
                sensor_type = reading_data.get('sensor_type', 'temperature')
                if sensor_type == 'temperature':
                    value = reading_data.get('temperature', reading_data.get('value', 0))
                    unit = 'celsius'
                elif sensor_type == 'humidity':
                    value = reading_data.get('humidity', reading_data.get('value', 0))
                    unit = 'percent'
                elif sensor_type == 'co2':
                    value = reading_data.get('co2_ppm', reading_data.get('value', 0))
                    unit = 'ppm'
                else:
                    value = reading_data.get('value', 0)
                    unit = reading_data.get('unit', 'unknown')
                
                cursor.execute("""
                    INSERT INTO sensor_readings (
                        id, device_id, sensor_type, value, unit,
                        quality_indicator, timestamp, metadata, synced
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    reading_data['id'],
                    reading_data.get('device_id'),
                    sensor_type,
                    value,
                    unit,
                    reading_data.get('quality_indicator', 'good'),
                    reading_data.get('timestamp', datetime.now().isoformat()),
                    json.dumps(reading_data.get('metadata', {})),
                    0  # Not synced yet
                ))
                
                conn.commit()
                self.logger.debug(f"Stored sensor reading: {reading_data['id']}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store sensor reading: {e}")
            return False
    
    def get_unsynced_sensor_readings(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get unsynced sensor readings for upload
        
        Args:
            limit: Maximum number of readings to retrieve
            
        Returns:
            List of unsynced sensor readings
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM sensor_readings 
                    WHERE synced = 0 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                """, (limit,))
                
                readings = []
                for row in cursor.fetchall():
                    reading = dict(row)
                    # Parse JSON metadata
                    if reading['metadata']:
                        reading['metadata'] = json.loads(reading['metadata'])
                    readings.append(reading)
                
                return readings
                
        except Exception as e:
            self.logger.error(f"Failed to get unsynced readings: {e}")
            return []
    
    def mark_sensor_readings_synced(self, reading_ids: List[str], backend_ids: List[str]) -> bool:
        """
        Mark sensor readings as synced
        
        Args:
            reading_ids: List of local reading IDs
            backend_ids: List of corresponding backend IDs
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for local_id, backend_id in zip(reading_ids, backend_ids):
                    cursor.execute("""
                        UPDATE sensor_readings 
                        SET synced = 1, backend_id = ?, last_sync_attempt = ?
                        WHERE id = ?
                    """, (backend_id, datetime.now().isoformat(), local_id))
                
                conn.commit()
                self.logger.debug(f"Marked {len(reading_ids)} readings as synced")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to mark readings as synced: {e}")
            return False
    
    def store_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Store alert in database
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Generate UUID if not provided
                if 'id' not in alert_data:
                    alert_data['id'] = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO alerts (
                        id, device_id, alert_type, severity, title, message,
                        threshold_config, trigger_value, current_value,
                        metadata, synced
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert_data['id'],
                    alert_data.get('device_id'),
                    alert_data['alert_type'],
                    alert_data['severity'],
                    alert_data['title'],
                    alert_data['message'],
                    json.dumps(alert_data.get('threshold_config', {})),
                    alert_data.get('trigger_value'),
                    alert_data.get('current_value'),
                    json.dumps(alert_data.get('metadata', {})),
                    0  # Not synced yet
                ))
                
                conn.commit()
                self.logger.debug(f"Stored alert: {alert_data['id']}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store alert: {e}")
            return False
    
    def get_unsynced_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get unsynced alerts for upload
        
        Args:
            limit: Maximum number of alerts to retrieve
            
        Returns:
            List of unsynced alerts
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM alerts 
                    WHERE synced = 0 
                    ORDER BY created_at ASC 
                    LIMIT ?
                """, (limit,))
                
                alerts = []
                for row in cursor.fetchall():
                    alert = dict(row)
                    # Parse JSON fields
                    if alert['threshold_config']:
                        alert['threshold_config'] = json.loads(alert['threshold_config'])
                    if alert['metadata']:
                        alert['metadata'] = json.loads(alert['metadata'])
                    alerts.append(alert)
                
                return alerts
                
        except Exception as e:
            self.logger.error(f"Failed to get unsynced alerts: {e}")
            return []
    
    def store_device_command(self, command_data: Dict[str, Any]) -> bool:
        """
        Store device command
        
        Args:
            command_data: Dictionary containing command data
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Generate UUID if not provided
                if 'id' not in command_data:
                    command_data['id'] = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO device_commands (
                        id, device_id, user_id, command_type, command_data,
                        status, timeout_seconds
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    command_data['id'],
                    command_data.get('device_id'),
                    command_data.get('user_id'),
                    command_data['command_type'],
                    json.dumps(command_data.get('command_data', {})),
                    command_data.get('status', 'pending'),
                    command_data.get('timeout_seconds', 30)
                ))
                
                conn.commit()
                self.logger.debug(f"Stored device command: {command_data['id']}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store device command: {e}")
            return False
    
    def get_pending_commands(self, device_id: str) -> List[Dict[str, Any]]:
        """
        Get pending commands for device
        
        Args:
            device_id: Device ID to get commands for
            
        Returns:
            List of pending commands
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM device_commands 
                    WHERE device_id = ? AND status = 'pending'
                    ORDER BY created_at ASC
                """, (device_id,))
                
                commands = []
                for row in cursor.fetchall():
                    command = dict(row)
                    # Parse JSON command data
                    if command['command_data']:
                        command['command_data'] = json.loads(command['command_data'])
                    commands.append(command)
                
                return commands
                
        except Exception as e:
            self.logger.error(f"Failed to get pending commands: {e}")
            return []
    
    def update_command_status(self, command_id: str, status: str, 
                            error_message: Optional[str] = None) -> bool:
        """
        Update command status
        
        Args:
            command_id: Command ID to update
            status: New status
            error_message: Error message if status is 'failed'
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                update_fields = ['status = ?']
                params = [status]
                
                if status == 'sent':
                    update_fields.append('sent_at = ?')
                    params.append(datetime.now().isoformat())
                elif status == 'acknowledged':
                    update_fields.append('acknowledged_at = ?')
                    params.append(datetime.now().isoformat())
                elif status == 'completed':
                    update_fields.append('completed_at = ?')
                    params.append(datetime.now().isoformat())
                elif status == 'failed' and error_message:
                    update_fields.append('error_message = ?')
                    params.append(error_message)
                
                params.append(command_id)
                
                cursor.execute(f"""
                    UPDATE device_commands 
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """, params)
                
                conn.commit()
                self.logger.debug(f"Updated command {command_id} status to {status}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update command status: {e}")
            return False
    
    def cleanup_old_data(self, retention_days: int = 30) -> int:
        """
        Clean up old synced data
        
        Args:
            retention_days: Number of days to retain data
            
        Returns:
            Number of records deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete old synced sensor readings
                cursor.execute("""
                    DELETE FROM sensor_readings 
                    WHERE synced = 1 AND timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_readings = cursor.rowcount
                
                # Delete old synced alerts
                cursor.execute("""
                    DELETE FROM alerts 
                    WHERE synced = 1 AND created_at < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_alerts = cursor.rowcount
                
                conn.commit()
                
                total_deleted = deleted_readings + deleted_alerts
                self.logger.info(f"Cleaned up {total_deleted} old records")
                return total_deleted
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count records in each table
                tables = ['sensor_readings', 'alerts', 'device_commands', 'sync_queue']
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f'{table}_count'] = cursor.fetchone()[0]
                
                # Count unsynced records
                cursor.execute("SELECT COUNT(*) FROM sensor_readings WHERE synced = 0")
                stats['unsynced_readings'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM alerts WHERE synced = 0")
                stats['unsynced_alerts'] = cursor.fetchone()[0]
                
                # Database size
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                stats['database_size_bytes'] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {}
