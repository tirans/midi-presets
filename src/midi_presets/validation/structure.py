from pathlib import Path
from typing import List
import os

from .base import BaseValidator
from ..utils.logging import get_logger

class StructureValidator(BaseValidator):
    def __init__(self, max_depth: int = 4):
        super().__init__()
        self.max_depth = max_depth
        self.logger = get_logger('validation.structure')
    
    def validate(self, target_path: Path) -> bool:
        """Validate folder structure and hierarchy"""
        self.logger.info(
            f"Starting structure validation for {target_path}",
            extra={'file_path': target_path, 'validation_type': 'structure'}
        )
        
        if target_path.is_file():
            return self._validate_file_path(target_path)
        elif target_path.is_dir():
            return self._validate_folder_structure(target_path)
        else:
            self.add_error(f"Path does not exist: {target_path}", file_path=target_path)
            return False
    
    def _validate_file_path(self, file_path: Path) -> bool:
        """Validate file is in correct location with correct naming"""
        parts = file_path.parts
        
        # Must be in devices folder
        if len(parts) < 2 or parts[0] != 'devices':
            self.logger.error(
                f"File not in devices folder: {file_path}",
                extra={'file_path': file_path}
            )
            self.add_error("File must be in devices/ folder", file_path=file_path)
            return False
        
        # Check depth (devices/device_name/... max 4 levels below devices)
        depth = len(parts) - 2  # Subtract 'devices' and filename
        if depth > self.max_depth:
            self.logger.error(
                f"File exceeds maximum depth: {depth} > {self.max_depth}",
                extra={'file_path': file_path}
            )
            self.add_error(
                f"File exceeds maximum folder depth of {self.max_depth} levels",
                file_path=file_path
            )
            return False
        
        # Validate folder names in path
        for i, part in enumerate(parts[1:-1], 1):  # Skip 'devices' and filename
            if not self._is_valid_folder_name(part):
                self.logger.error(
                    f"Invalid folder name at level {i}: {part}",
                    extra={'file_path': file_path}
                )
                self.add_error(
                    f"Invalid folder name '{part}' (must be alphanumeric with underscore/hyphen)",
                    file_path=file_path
                )
                return False
        
        # File must be JSON
        if not file_path.suffix.lower() == '.json':
            self.logger.error(
                f"Invalid file extension: {file_path.suffix}",
                extra={'file_path': file_path}
            )
            self.add_error("Only .json files are allowed", file_path=file_path)
            return False
        
        self.logger.info(
            f"File path validation passed",
            extra={'file_path': file_path, 'depth': depth}
        )
        return True
    
    def _validate_folder_structure(self, folder_path: Path) -> bool:
        """Validate folder structure"""
        # Must be under devices
        try:
            relative_path = folder_path.relative_to(Path('devices'))
        except ValueError:
            self.add_error("Folder must be under devices/", file_path=folder_path)
            return False
        
        # Check depth
        depth = len(relative_path.parts)
        if depth > self.max_depth:
            self.logger.error(
                f"Folder exceeds maximum depth: {depth} > {self.max_depth}",
                extra={'file_path': folder_path}
            )
            self.add_error(
                f"Folder exceeds maximum depth of {self.max_depth} levels",
                file_path=folder_path
            )
            return False
        
        # Validate folder name
        if not self._is_valid_folder_name(folder_path.name):
            self.logger.error(
                f"Invalid folder name: {folder_path.name}",
                extra={'file_path': folder_path}
            )
            self.add_error(
                f"Invalid folder name '{folder_path.name}' (must be alphanumeric with underscore/hyphen)",
                file_path=folder_path
            )
            return False
        
        self.logger.info(
            f"Folder structure validation passed",
            extra={'file_path': folder_path, 'depth': depth}
        )
        return True
    
    def _is_valid_folder_name(self, name: str) -> bool:
        """Check if folder name is valid"""
        if not name:
            return False
        
        # Must be alphanumeric with underscore/hyphen
        return name.replace('_', '').replace('-', '').isalnum()
    
    def validate_all_changes(self, changed_paths: List[Path]) -> bool:
        """Validate all changed paths"""
        self.logger.info(f"Validating {len(changed_paths)} changed paths")
        
        all_valid = True
        for path in changed_paths:
            if not self.validate(path):
                all_valid = False
        
        return all_valid
