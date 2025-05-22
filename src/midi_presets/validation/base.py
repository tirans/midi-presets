from abc import ABC, abstractmethod
from typing import List, Any
from pathlib import Path

class ValidationError:
    def __init__(self, message: str, severity: str = "error", file_path: Path = None):
        self.message = message
        self.severity = severity  # "error", "warning", "info"
        self.file_path = file_path
    
    def __str__(self):
        prefix = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[self.severity]
        location = f" ({self.file_path})" if self.file_path else ""
        return f"{prefix} {self.message}{location}"

class BaseValidator(ABC):
    def __init__(self):
        self.errors: List[ValidationError] = []
    
    @abstractmethod
    def validate(self, target: Any) -> bool:
        """Validate target and return True if valid"""
        pass
    
    def add_error(self, message: str, severity: str = "error", file_path: Path = None):
        self.errors.append(ValidationError(message, severity, file_path))
    
    def has_errors(self) -> bool:
        return any(e.severity == "error" for e in self.errors)
    
    def has_warnings(self) -> bool:
        return any(e.severity == "warning" for e in self.errors)
    
    def get_errors(self) -> List[ValidationError]:
        return [e for e in self.errors if e.severity == "error"]
    
    def get_warnings(self) -> List[ValidationError]:
        return [e for e in self.errors if e.severity == "warning"]
    
    def clear_errors(self):
        self.errors.clear()
