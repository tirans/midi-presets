from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
import os
import json

from .logging import get_logger

logger = get_logger('utils.config')

@dataclass
class ValidationConfig:
    max_file_size_mb: float = 3.0
    max_presets_per_collection: int = 1000
    max_folder_depth: int = 4
    strict_mode: bool = False
    allowed_extensions: List[str] = field(default_factory=lambda: ['.json'])
    
    def __post_init__(self):
        logger.debug(
            "ValidationConfig initialized",
            extra={
                'max_file_size_mb': self.max_file_size_mb,
                'max_presets_per_collection': self.max_presets_per_collection,
                'max_folder_depth': self.max_folder_depth,
                'strict_mode': self.strict_mode,
                'allowed_extensions': self.allowed_extensions
            }
        )

@dataclass
class ChecksumConfig:
    exclude_patterns: List[str] = field(default_factory=lambda: ["_manifest.json"])
    chunk_size: int = 4096
    
    def __post_init__(self):
        logger.debug(
            "ChecksumConfig initialized",
            extra={
                'exclude_patterns': self.exclude_patterns,
                'chunk_size': self.chunk_size
            }
        )

@dataclass
class LoggingConfig:
    level: str = "INFO"
    json_format: bool = False
    log_file: Optional[Path] = None
    
    def __post_init__(self):
        logger.debug(
            "LoggingConfig initialized",
            extra={
                'level': self.level,
                'json_format': self.json_format,
                'log_file': str(self.log_file) if self.log_file else None
            }
        )

@dataclass
class AppConfig:
    devices_folder: Path
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    checksum: ChecksumConfig = field(default_factory=ChecksumConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    def __post_init__(self):
        # Ensure devices_folder is a Path object
        if isinstance(self.devices_folder, str):
            self.devices_folder = Path(self.devices_folder)
        
        logger.info(
            "AppConfig initialized",
            extra={
                'devices_folder': str(self.devices_folder),
                'devices_folder_exists': self.devices_folder.exists(),
                'validation_strict_mode': self.validation.strict_mode,
                'logging_level': self.logging.level
            }
        )
    
    @classmethod
    def from_file(cls, config_file: Path) -> 'AppConfig':
        """Load configuration from JSON file"""
        logger.info(f"Loading configuration from file: {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
            
            logger.debug(f"Configuration file loaded successfully")
            
            # Parse nested configurations
            validation_data = data.get('validation', {})
            checksum_data = data.get('checksum', {})
            logging_data = data.get('logging', {})
            
            config = cls(
                devices_folder=Path(data['devices_folder']),
                validation=ValidationConfig(**validation_data),
                checksum=ChecksumConfig(**checksum_data),
                logging=LoggingConfig(**logging_data)
            )
            
            logger.info(
                f"Configuration loaded from file",
                extra={'config_file': str(config_file)}
            )
            
            return config
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(
                f"Invalid JSON in configuration file: {e}",
                extra={'config_file': str(config_file), 'error': str(e)}
            )
            raise
        except Exception as e:
            logger.error(
                f"Error loading configuration: {e}",
                extra={'config_file': str(config_file), 'error': str(e)}
            )
            raise
    
    @classmethod
    def from_environment(cls) -> 'AppConfig':
        """Load configuration from environment variables"""
        logger.info("Loading configuration from environment variables")
        
        devices_folder = os.getenv('MIDI_DEVICES_FOLDER', 'devices')
        
        validation_config = ValidationConfig(
            max_file_size_mb=float(os.getenv('MIDI_MAX_FILE_SIZE_MB', '3.0')),
            max_presets_per_collection=int(os.getenv('MIDI_MAX_PRESETS_PER_COLLECTION', '1000')),
            max_folder_depth=int(os.getenv('MIDI_MAX_FOLDER_DEPTH', '4')),
            strict_mode=os.getenv('MIDI_STRICT_MODE', 'false').lower() == 'true'
        )
        
        logging_config = LoggingConfig(
            level=os.getenv('MIDI_LOG_LEVEL', 'INFO'),
            json_format=os.getenv('MIDI_JSON_LOGS', 'false').lower() == 'true',
            log_file=Path(log_file) if (log_file := os.getenv('MIDI_LOG_FILE')) else None
        )
        
        config = cls(
            devices_folder=Path(devices_folder),
            validation=validation_config,
            logging=logging_config
        )
        
        logger.info("Configuration loaded from environment variables")
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'devices_folder': str(self.devices_folder),
            'validation': {
                'max_file_size_mb': self.validation.max_file_size_mb,
                'max_presets_per_collection': self.validation.max_presets_per_collection,
                'max_folder_depth': self.validation.max_folder_depth,
                'strict_mode': self.validation.strict_mode,
                'allowed_extensions': self.validation.allowed_extensions
            },
            'checksum': {
                'exclude_patterns': self.checksum.exclude_patterns,
                'chunk_size': self.checksum.chunk_size
            },
            'logging': {
                'level': self.logging.level,
                'json_format': self.logging.json_format,
                'log_file': str(self.logging.log_file) if self.logging.log_file else None
            }
        }
    
    def save_to_file(self, config_file: Path):
        """Save configuration to JSON file"""
        logger.info(f"Saving configuration to file: {config_file}")
        
        try:
            config_dict = self.to_dict()
            
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved successfully")
            
        except Exception as e:
            logger.error(
                f"Error saving configuration: {e}",
                extra={'config_file': str(config_file), 'error': str(e)}
            )
            raise
