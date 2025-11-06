#!/usr/bin/env python3
"""
Data Logger for MASH IoT Device
Logs sensor readings, actuator states, and AI decisions to SQLite database
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)


class DataLogger:
    """Logs all device data to SQLite database"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use current directory's data folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, 'data', 'device_logs.db')
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """Create database and tables if they don't exist"""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sensor readings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    co2 INTEGER,
                    temperature REAL,
                    humidity REAL,
                    mode TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Actuator states table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS actuator_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    exhaust_fan INTEGER,
                    blower_fan INTEGER,
                    humidifier INTEGER,
                    led_lights INTEGER,
                    mode TEXT,
                    triggered_by TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # AI decisions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    mode TEXT,
                    sensor_co2 INTEGER,
                    sensor_temp REAL,
                    sensor_humidity REAL,
                    actions TEXT,
                    reasoning TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT,
                    severity TEXT,
                    message TEXT,
                    sensor_value REAL,
                    threshold_value REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sensor_timestamp 
                ON sensor_readings(timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_actuator_timestamp 
                ON actuator_states(timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ai_timestamp 
                ON ai_decisions(timestamp DESC)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def log_sensor_reading(self, sensor_data: Dict) -> bool:
        """Log sensor reading"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sensor_readings (timestamp, co2, temperature, humidity, mode)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                sensor_data.get('co2'),
                sensor_data.get('temperature'),
                sensor_data.get('humidity'),
                sensor_data.get('mode')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to log sensor reading: {e}")
            return False
    
    def log_actuator_change(self, actuator_states: Dict, mode: str, triggered_by: str = 'manual') -> bool:
        """Log actuator state change"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO actuator_states 
                (timestamp, exhaust_fan, blower_fan, humidifier, led_lights, mode, triggered_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                1 if actuator_states.get('exhaust_fan') else 0,
                1 if actuator_states.get('blower_fan') else 0,
                1 if actuator_states.get('humidifier') else 0,
                1 if actuator_states.get('led_lights') else 0,
                mode,
                triggered_by
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to log actuator change: {e}")
            return False
    
    def log_ai_decision(self, decision: Dict) -> bool:
        """Log AI decision"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            sensor_data = decision.get('sensor_data', {})
            
            cursor.execute("""
                INSERT INTO ai_decisions 
                (timestamp, mode, sensor_co2, sensor_temp, sensor_humidity, actions, reasoning)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                decision.get('timestamp', datetime.now().isoformat()),
                decision.get('mode'),
                sensor_data.get('co2'),
                sensor_data.get('temperature'),
                sensor_data.get('humidity'),
                json.dumps(decision.get('actions', {})),
                json.dumps(decision.get('reasoning', []))
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to log AI decision: {e}")
            return False
    
    def log_alert(self, alert_type: str, severity: str, message: str, 
                  sensor_value: float = None, threshold_value: float = None) -> bool:
        """Log alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alerts 
                (timestamp, alert_type, severity, message, sensor_value, threshold_value)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                alert_type,
                severity,
                message,
                sensor_value,
                threshold_value
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
            return False
    
    def get_sensor_readings(self, hours: int = 24, limit: int = 1000) -> List[Dict]:
        """Get sensor readings from last N hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT * FROM sensor_readings 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (cutoff, limit))
            
            readings = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return readings
            
        except Exception as e:
            logger.error(f"Failed to get sensor readings: {e}")
            return []
    
    def get_actuator_history(self, hours: int = 24, limit: int = 500) -> List[Dict]:
        """Get actuator state history"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT * FROM actuator_states 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (cutoff, limit))
            
            states = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return states
            
        except Exception as e:
            logger.error(f"Failed to get actuator history: {e}")
            return []
    
    def get_ai_decisions(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get AI decision history"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT * FROM ai_decisions 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (cutoff, limit))
            
            decisions = []
            for row in cursor.fetchall():
                decision = dict(row)
                # Parse JSON fields
                if decision['actions']:
                    decision['actions'] = json.loads(decision['actions'])
                if decision['reasoning']:
                    decision['reasoning'] = json.loads(decision['reasoning'])
                decisions.append(decision)
            
            conn.close()
            return decisions
            
        except Exception as e:
            logger.error(f"Failed to get AI decisions: {e}")
            return []
    
    def get_alerts(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT * FROM alerts 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (cutoff, limit))
            
            alerts = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    def get_statistics(self, hours: int = 24) -> Dict:
        """Get statistics for the last N hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            stats = {}
            
            # Sensor reading stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    AVG(co2) as avg_co2,
                    MIN(co2) as min_co2,
                    MAX(co2) as max_co2,
                    AVG(temperature) as avg_temp,
                    MIN(temperature) as min_temp,
                    MAX(temperature) as max_temp,
                    AVG(humidity) as avg_humidity,
                    MIN(humidity) as min_humidity,
                    MAX(humidity) as max_humidity
                FROM sensor_readings
                WHERE timestamp >= ?
            """, (cutoff,))
            
            row = cursor.fetchone()
            if row:
                stats['sensor_readings'] = {
                    'count': row[0],
                    'co2': {'avg': row[1], 'min': row[2], 'max': row[3]},
                    'temperature': {'avg': row[4], 'min': row[5], 'max': row[6]},
                    'humidity': {'avg': row[7], 'min': row[8], 'max': row[9]}
                }
            
            # AI decision count
            cursor.execute("""
                SELECT COUNT(*) FROM ai_decisions WHERE timestamp >= ?
            """, (cutoff,))
            stats['ai_decisions_count'] = cursor.fetchone()[0]
            
            # Alert count by severity
            cursor.execute("""
                SELECT severity, COUNT(*) 
                FROM alerts 
                WHERE timestamp >= ?
                GROUP BY severity
            """, (cutoff,))
            stats['alerts_by_severity'] = dict(cursor.fetchall())
            
            # Actuator usage
            cursor.execute("""
                SELECT 
                    SUM(exhaust_fan) as exhaust_fan_count,
                    SUM(blower_fan) as blower_fan_count,
                    SUM(humidifier) as humidifier_count,
                    SUM(led_lights) as led_lights_count
                FROM actuator_states
                WHERE timestamp >= ?
            """, (cutoff,))
            row = cursor.fetchone()
            if row:
                stats['actuator_usage'] = {
                    'exhaust_fan': row[0] or 0,
                    'blower_fan': row[1] or 0,
                    'humidifier': row[2] or 0,
                    'led_lights': row[3] or 0
                }
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """Delete data older than N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Delete old sensor readings
            cursor.execute("DELETE FROM sensor_readings WHERE timestamp < ?", (cutoff,))
            deleted_readings = cursor.rowcount
            
            # Delete old actuator states
            cursor.execute("DELETE FROM actuator_states WHERE timestamp < ?", (cutoff,))
            deleted_states = cursor.rowcount
            
            # Delete old AI decisions
            cursor.execute("DELETE FROM ai_decisions WHERE timestamp < ?", (cutoff,))
            deleted_decisions = cursor.rowcount
            
            # Delete old alerts
            cursor.execute("DELETE FROM alerts WHERE timestamp < ?", (cutoff,))
            deleted_alerts = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            total = deleted_readings + deleted_states + deleted_decisions + deleted_alerts
            logger.info(f"Cleaned up {total} old records")
            return total
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0
