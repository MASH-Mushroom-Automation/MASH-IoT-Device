"""
Logging Configuration
Sets up structured logging for the MASH IoT Device
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        """Format log record with colors"""
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """Structured formatter for JSON-like log output"""
    
    def format(self, record):
        """Format log record as structured data"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return str(log_data)


def setup_logging(level: int = logging.INFO, 
                  log_file: Optional[str] = None,
                  max_size: int = 10 * 1024 * 1024,  # 10MB
                  backup_count: int = 5,
                  structured: bool = False):
    """
    Setup logging configuration
    
    Args:
        level: Logging level
        log_file: Path to log file (optional)
        max_size: Maximum log file size in bytes
        backup_count: Number of backup files to keep
        structured: Use structured logging format
    """
    # Create logs directory if needed
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if structured:
        console_formatter = StructuredFormatter()
    else:
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count
        )
        file_handler.setLevel(level)
        
        if structured:
            file_formatter = StructuredFormatter()
        else:
            file_formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-4d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('paho.mqtt').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return logging.getLogger(self.__class__.__name__)
    
    def log_with_data(self, level: int, message: str, **kwargs):
        """
        Log message with extra data
        
        Args:
            level: Logging level
            message: Log message
            **kwargs: Extra data to include in log
        """
        extra = {'extra_data': kwargs}
        self.logger.log(level, message, extra=extra)
    
    def log_debug(self, message: str, **kwargs):
        """Log debug message with data"""
        self.log_with_data(logging.DEBUG, message, **kwargs)
    
    def log_info(self, message: str, **kwargs):
        """Log info message with data"""
        self.log_with_data(logging.INFO, message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message with data"""
        self.log_with_data(logging.WARNING, message, **kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log error message with data"""
        self.log_with_data(logging.ERROR, message, **kwargs)
    
    def log_critical(self, message: str, **kwargs):
        """Log critical message with data"""
        self.log_with_data(logging.CRITICAL, message, **kwargs)
