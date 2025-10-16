"""
Database Schema Definition
Defines the SQLite schema aligned with backend PostgreSQL
"""

import sqlite3
import logging
from typing import List, Dict, Any


class DatabaseSchema:
    """Manages database schema creation and migrations"""
    
    def __init__(self, db_path: str):
        """
        Initialize schema manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def create_schema(self) -> bool:
        """
        Create the complete database schema
        
        Returns:
            True if schema created successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create all tables
                self._create_device_info_table(cursor)
                self._create_sensor_readings_table(cursor)
                self._create_device_commands_table(cursor)
                self._create_alerts_table(cursor)
                self._create_actuator_states_table(cursor)
                self._create_sync_queue_table(cursor)
                self._create_config_cache_table(cursor)
                self._create_system_logs_table(cursor)
                
                # Create indexes
                self._create_indexes(cursor)
                
                # Insert initial configuration
                self._insert_initial_config(cursor)
                
                conn.commit()
                self.logger.info("Database schema created successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create database schema: {e}")
            return False
    
    def _create_device_info_table(self, cursor):
        """Create device_info table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_info (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                device_type TEXT DEFAULT 'MASH_CHAMBER',
                model TEXT DEFAULT 'RPi3-ModelB',
                serial_number TEXT,
                mac_address TEXT,
                firmware_version TEXT DEFAULT '1.0.0',
                hardware_version TEXT DEFAULT 'RPi3B',
                status TEXT DEFAULT 'offline',
                configuration TEXT,
                location TEXT,
                timezone TEXT DEFAULT 'Asia/Manila',
                last_sync DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _create_sensor_readings_table(self, cursor):
        """Create sensor_readings table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                quality_indicator TEXT DEFAULT 'good',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                synced INTEGER DEFAULT 0,
                backend_id TEXT,
                sync_attempt_count INTEGER DEFAULT 0,
                last_sync_attempt DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES device_info(id)
            )
        """)
    
    def _create_device_commands_table(self, cursor):
        """Create device_commands table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_commands (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                user_id TEXT,
                command_type TEXT NOT NULL,
                command_data TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                sent_at DATETIME,
                acknowledged_at DATETIME,
                completed_at DATETIME,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                timeout_seconds INTEGER DEFAULT 30,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES device_info(id)
            )
        """)
    
    def _create_alerts_table(self, cursor):
        """Create alerts table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                threshold_config TEXT,
                trigger_value REAL,
                current_value REAL,
                acknowledged INTEGER DEFAULT 0,
                acknowledged_by TEXT,
                acknowledged_at DATETIME,
                resolved INTEGER DEFAULT 0,
                resolved_by TEXT,
                resolved_at DATETIME,
                auto_resolve INTEGER DEFAULT 0,
                escalation_level INTEGER DEFAULT 1,
                metadata TEXT,
                synced INTEGER DEFAULT 0,
                backend_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES device_info(id)
            )
        """)
    
    def _create_actuator_states_table(self, cursor):
        """Create actuator_states table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actuator_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                actuator_type TEXT NOT NULL,
                state TEXT NOT NULL,
                value REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                synced INTEGER DEFAULT 0,
                FOREIGN KEY (device_id) REFERENCES device_info(id)
            )
        """)
    
    def _create_sync_queue_table(self, cursor):
        """Create sync_queue table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                priority INTEGER DEFAULT 1,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 5,
                last_attempt DATETIME,
                next_retry DATETIME,
                error_message TEXT,
                payload TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _create_config_cache_table(self, cursor):
        """Create config_cache table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config_cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                is_backend_config INTEGER DEFAULT 0,
                last_sync DATETIME,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _create_system_logs_table(self, cursor):
        """Create system_logs table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                module TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _create_indexes(self, cursor):
        """Create database indexes for performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_timestamp ON sensor_readings(device_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_sensor_readings_synced ON sensor_readings(synced) WHERE synced = 0",
            "CREATE INDEX IF NOT EXISTS idx_commands_status ON device_commands(status) WHERE status IN ('pending', 'sent')",
            "CREATE INDEX IF NOT EXISTS idx_alerts_device_severity ON alerts(device_id, severity)",
            "CREATE INDEX IF NOT EXISTS idx_alerts_synced ON alerts(synced) WHERE synced = 0",
            "CREATE INDEX IF NOT EXISTS idx_sync_queue_priority ON sync_queue(priority DESC, created_at ASC)",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def _insert_initial_config(self, cursor):
        """Insert initial configuration values"""
        initial_config = [
            ('sensor_read_interval', '60', 'sensor'),
            ('temp_min', '25.0', 'control'),
            ('temp_max', '28.0', 'control'),
            ('temp_critical_high', '32.0', 'control'),
            ('humidity_min', '80.0', 'control'),
            ('humidity_max', '90.0', 'control'),
            ('co2_optimal_min', '10000', 'control'),
            ('co2_optimal_max', '15000', 'control'),
            ('co2_critical_high', '20000', 'control'),
            ('sync_interval', '300', 'sync'),
            ('batch_sync_size', '100', 'sync'),
            ('data_retention_days', '30', 'storage'),
            ('alert_cooldown_seconds', '900', 'alert')
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO config_cache (key, value, category) 
            VALUES (?, ?, ?)
        """, initial_config)
    
    def get_schema_version(self) -> int:
        """Get current schema version"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA user_version")
                return cursor.fetchone()[0]
        except Exception as e:
            self.logger.error(f"Failed to get schema version: {e}")
            return 0
    
    def set_schema_version(self, version: int) -> bool:
        """Set schema version"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA user_version = {version}")
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to set schema version: {e}")
            return False
    
    def validate_schema(self) -> bool:
        """Validate that all required tables exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                required_tables = [
                    'device_info', 'sensor_readings', 'device_commands',
                    'alerts', 'actuator_states', 'sync_queue',
                    'config_cache', 'system_logs'
                ]
                
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ({})
                """.format(','.join(['?' for _ in required_tables])), required_tables)
                
                existing_tables = [row[0] for row in cursor.fetchall()]
                missing_tables = set(required_tables) - set(existing_tables)
                
                if missing_tables:
                    self.logger.error(f"Missing tables: {missing_tables}")
                    return False
                
                return True
                
        except Exception as e:
            self.logger.error(f"Schema validation failed: {e}")
            return False
