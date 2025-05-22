import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'file_path'):
            log_entry['file_path'] = str(record.file_path)
        if hasattr(record, 'validation_type'):
            log_entry['validation_type'] = record.validation_type
        if hasattr(record, 'duration'):
            log_entry['duration_ms'] = record.duration
        if hasattr(record, 'error_count'):
            log_entry['error_count'] = record.error_count
        
        return json.dumps(log_entry)

class LoggerSetup:
    @staticmethod
    def setup_logging(
        level: str = "INFO",
        log_file: Optional[Path] = None,
        json_format: bool = False
    ) -> logging.Logger:
        """Setup structured logging"""
        
        # Create main logger
        logger = logging.getLogger('midi_presets')
        logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        if json_format:
            console_handler.setFormatter(JSONFormatter())
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(JSONFormatter())
            logger.addHandler(file_handler)
        
        return logger

# Convenience function
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(f'midi_presets.{name}')
