import argparse
import sys
from pathlib import Path
from typing import List

from ..validation.content import ContentValidator
from ..validation.security import SecurityValidator
from ..validation.business import BusinessRulesValidator
from ..validation.structure import StructureValidator
from ..utils.config import ValidationConfig
from ..utils.logging import LoggerSetup, get_logger

class ValidationCLI:
    def __init__(self, config: ValidationConfig = None):
        self.config = config or ValidationConfig()
        self.logger = get_logger('cli.validate')
        
        self.validators = [
            StructureValidator(),
            ContentValidator(self.config.max_file_size_mb),
            SecurityValidator(),
            BusinessRulesValidator()
        ]
    
    def validate_files(self, file_paths: List[Path]) -> bool:
        """Validate multiple files"""
        self.logger.info(f"Starting validation of {len(file_paths)} files")
        
        all_valid = True
        total_errors = 0
        total_warnings = 0
        
        for file_path in file_paths:
            self.logger.info(f"Validating {file_path}")
            print(f"Validating {file_path}...")
            
            file_valid = True
            file_errors = 0
            file_warnings = 0
            
            for validator in self.validators:
                validator.clear_errors()
                
                if not validator.validate(file_path):
                    file_valid = False
                
                # Count and print errors
                errors = validator.get_errors()
                warnings = validator.get_warnings()
                
                file_errors += len(errors)
                file_warnings += len(warnings)
                
                for error in errors:
                    print(f"  {error}")
                    self.logger.error(str(error), extra={'file_path': file_path})
                
                for warning in warnings:
                    print(f"  {warning}")
                    self.logger.warning(str(warning), extra={'file_path': file_path})
            
            total_errors += file_errors
            total_warnings += file_warnings
            
            if file_valid:
                print(f"  ✅ {file_path.name} is valid")
                self.logger.info(f"File validation passed", extra={'file_path': file_path})
            else:
                all_valid = False
                self.logger.error(
                    f"File validation failed",
                    extra={
                        'file_path': file_path,
                        'error_count': file_errors,
                        'warning_count': file_warnings
                    }
                )
        
        # Log summary
        self.logger.info(
            f"Validation completed",
            extra={
                'total_files': len(file_paths),
                'total_errors': total_errors,
                'total_warnings': total_warnings,
                'all_valid': all_valid
            }
        )
        
        return all_valid
    
    def run(self, args: List[str] = None) -> int:
        """Run validation CLI"""
        parser = argparse.ArgumentParser(description='Validate device preset JSON files')
        parser.add_argument('files', nargs='+', help='JSON files to validate')
        parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
        parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        parser.add_argument('--log-file', type=Path, help='Log file path')
        parser.add_argument('--json-logs', action='store_true', help='Output logs in JSON format')
        
        parsed_args = parser.parse_args(args)
        
        # Setup logging
        LoggerSetup.setup_logging(
            level=parsed_args.log_level,
            log_file=parsed_args.log_file,
            json_format=parsed_args.json_logs
        )
        
        if parsed_args.strict:
            self.config.strict_mode = True
        
        file_paths = [Path(f) for f in parsed_args.files]
        
        if self.validate_files(file_paths):
            print("\n✅ All validations passed!")
            return 0
        else:
            print("\n❌ Validation failed!")
            return 1
