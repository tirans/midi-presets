import json
from pathlib import Path
from typing import List
import time

from .base import BaseValidator
from ..utils.logging import get_logger

class SecurityValidator(BaseValidator):
    def __init__(self):
        super().__init__()
        self.logger = get_logger('validation.security')
        self.suspicious_patterns = [
            'javascript:', '<script', 'eval(', 'function(', 'onclick=',
            '<iframe', 'document.', 'window.', 'alert(', 'confirm(',
            'prompt(', 'setTimeout', 'setInterval', '__import__',
            'exec(', 'compile(', 'globals(', 'locals(', 'vars(',
            'getattr(', 'setattr(', 'delattr(', 'hasattr('
        ]
        
        self.logger.info(
            f"SecurityValidator initialized with {len(self.suspicious_patterns)} patterns",
            extra={'pattern_count': len(self.suspicious_patterns)}
        )
    
    def validate(self, file_path: Path) -> bool:
        """Check for suspicious/malicious content"""
        start_time = time.time()
        
        self.logger.info(
            f"Starting security validation",
            extra={'file_path': str(file_path), 'validation_type': 'security'}
        )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_size = len(content)
            content_lower = content.lower()
            
            self.logger.debug(
                f"Scanning file content",
                extra={
                    'file_path': str(file_path),
                    'file_size_chars': file_size,
                    'patterns_to_check': len(self.suspicious_patterns)
                }
            )
            
            found_patterns = []
            pattern_locations = {}
            
            for pattern in self.suspicious_patterns:
                if pattern.lower() in content_lower:
                    found_patterns.append(pattern)
                    # Find first occurrence for logging
                    index = content_lower.find(pattern.lower())
                    pattern_locations[pattern] = index
                    
                    self.logger.warning(
                        f"Suspicious pattern detected: {pattern}",
                        extra={
                            'file_path': str(file_path),
                            'pattern': pattern,
                            'location_index': index,
                            'context': content[max(0, index-20):index+50]
                        }
                    )
            
            duration = (time.time() - start_time) * 1000
            
            if found_patterns:
                self.logger.error(
                    f"Security validation failed - {len(found_patterns)} suspicious patterns found",
                    extra={
                        'file_path': str(file_path),
                        'found_patterns': found_patterns,
                        'pattern_locations': pattern_locations,
                        'duration_ms': duration
                    }
                )
                
                self.add_error(
                    f"Contains suspicious patterns: {', '.join(found_patterns)}",
                    file_path=file_path
                )
                return False
            
            self.logger.info(
                f"Security validation passed",
                extra={
                    'file_path': str(file_path),
                    'patterns_checked': len(self.suspicious_patterns),
                    'file_size_chars': file_size,
                    'duration_ms': duration
                }
            )
            return True
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.logger.error(
                f"Security validation error: {e}",
                extra={
                    'file_path': str(file_path),
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'duration_ms': duration
                }
            )
            self.add_error(f"Error checking security: {e}", file_path=file_path)
            return False
