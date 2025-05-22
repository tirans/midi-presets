"""
MIDI Device Presets Package

A comprehensive system for managing, validating, and sharing MIDI device presets.
"""

__version__ = "2.1.0"
__author__ = "tirans"

from .utils.logging import LoggerSetup, get_logger
from .utils.config import AppConfig, ValidationConfig
from .models.device import DeviceModel
from .validation.content import ContentValidator
from .validation.security import SecurityValidator
from .validation.business import BusinessRulesValidator
from .validation.structure import StructureValidator

__all__ = [
    "LoggerSetup",
    "get_logger", 
    "AppConfig",
    "ValidationConfig",
    "DeviceModel",
    "ContentValidator",
    "SecurityValidator", 
    "BusinessRulesValidator",
    "StructureValidator"
]
