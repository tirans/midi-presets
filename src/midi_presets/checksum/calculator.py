import hashlib
import json
from pathlib import Path
from typing import Dict, List
import time

from ..utils.logging import get_logger

class ChecksumCalculator:
    def __init__(self):
        self.chunk_size = 4096
        self.logger = get_logger('checksum.calculator')
        
        self.logger.info(
            f"ChecksumCalculator initialized",
            extra={'chunk_size': self.chunk_size}
        )
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a single file"""
        start_time = time.time()
        
        self.logger.debug(
            f"Calculating file hash",
            extra={'file_path': str(file_path)}
        )
        
        sha256_hash = hashlib.sha256()
        bytes_processed = 0
        
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(self.chunk_size), b""):
                    sha256_hash.update(chunk)
                    bytes_processed += len(chunk)
            
            file_hash = sha256_hash.hexdigest()
            duration = (time.time() - start_time) * 1000
            
            self.logger.info(
                f"File hash calculated",
                extra={
                    'file_path': str(file_path),
                    'file_hash': file_hash[:16] + '...',
                    'bytes_processed': bytes_processed,
                    'duration_ms': duration
                }
            )
            
            return file_hash
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.logger.error(
                f"Error calculating file hash: {e}",
                extra={
                    'file_path': str(file_path),
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'duration_ms': duration
                }
            )
            raise ValueError(f"Error calculating hash for {file_path}: {e}")
    
    def calculate_folder_hash(self, folder_path: Path, exclude_patterns: List[str] = None) -> str:
        """Calculate SHA256 hash of folder contents"""
        start_time = time.time()
        
        if exclude_patterns is None:
            exclude_patterns = ["_manifest.json"]
        
        self.logger.info(
            f"Calculating folder hash",
            extra={
                'folder_path': str(folder_path),
                'exclude_patterns': exclude_patterns
            }
        )
        
        sha256_hash = hashlib.sha256()
        files_processed = 0
        total_bytes = 0
        
        # Get all JSON files sorted for consistent hashing
        json_files = sorted([
            f for f in folder_path.rglob("*.json")
            if not any(pattern in f.name for pattern in exclude_patterns)
        ])
        
        self.logger.debug(
            f"Found {len(json_files)} JSON files to process",
            extra={
                'folder_path': str(folder_path),
                'file_count': len(json_files),
                'files': [str(f.relative_to(folder_path)) for f in json_files[:10]]  # Log first 10
            }
        )
        
        for file_path in json_files:
            try:
                # Add relative path and file hash to folder hash
                relative_path = file_path.relative_to(folder_path)
                sha256_hash.update(str(relative_path).encode())
                
                file_hash = self.calculate_file_hash(file_path)
                sha256_hash.update(file_hash.encode())
                
                files_processed += 1
                total_bytes += file_path.stat().st_size
                
                self.logger.debug(
                    f"Processed file {files_processed}/{len(json_files)}",
                    extra={
                        'file_path': str(relative_path),
                        'file_hash': file_hash[:16] + '...'
                    }
                )
                
            except Exception as e:
                self.logger.error(
                    f"Error processing file in folder hash: {e}",
                    extra={
                        'file_path': str(file_path),
                        'error': str(e)
                    }
                )
                raise
        
        folder_hash = sha256_hash.hexdigest()
        duration = (time.time() - start_time) * 1000
        
        self.logger.info(
            f"Folder hash calculated successfully",
            extra={
                'folder_path': str(folder_path),
                'folder_hash': folder_hash[:16] + '...',
                'files_processed': files_processed,
                'total_bytes': total_bytes,
                'duration_ms': duration
            }
        )
        
        return folder_hash
    
    def calculate_repository_hash(self, devices_folder: Path) -> str:
        """Calculate hash of entire repository content"""
        start_time = time.time()
        
        self.logger.info(
            f"Calculating repository hash",
            extra={'devices_folder': str(devices_folder)}
        )
        
        sha256_hash = hashlib.sha256()
        folders_processed = 0
        
        # Get all device folders
        device_folders = sorted([
            f for f in devices_folder.iterdir()
            if f.is_dir() and any(f.rglob("*.json"))
        ])
        
        self.logger.debug(
            f"Found {len(device_folders)} device folders",
            extra={
                'devices_folder': str(devices_folder),
                'folder_count': len(device_folders),
                'folders': [f.name for f in device_folders]
            }
        )
        
        for folder in device_folders:
            try:
                folder_hash = self.calculate_folder_hash(folder)
                relative_path = folder.relative_to(devices_folder)
                sha256_hash.update(f"{relative_path}:{folder_hash}".encode())
                
                folders_processed += 1
                
                self.logger.debug(
                    f"Processed folder {folders_processed}/{len(device_folders)}",
                    extra={
                        'folder_name': folder.name,
                        'folder_hash': folder_hash[:16] + '...'
                    }
                )
                
            except Exception as e:
                self.logger.error(
                    f"Error processing folder in repository hash: {e}",
                    extra={
                        'folder_path': str(folder),
                        'error': str(e)
                    }
                )
                raise
        
        repo_hash = sha256_hash.hexdigest()
        duration = (time.time() - start_time) * 1000
        
        self.logger.info(
            f"Repository hash calculated successfully",
            extra={
                'devices_folder': str(devices_folder),
                'repository_hash': repo_hash[:16] + '...',
                'folders_processed': folders_processed,
                'duration_ms': duration
            }
        )
        
        return repo_hash
    
    def verify_file_hash(self, file_path: Path, expected_hash: str) -> bool:
        """Verify a file's hash matches expected value"""
        self.logger.debug(
            f"Verifying file hash",
            extra={
                'file_path': str(file_path),
                'expected_hash': expected_hash[:16] + '...'
            }
        )
        
        try:
            actual_hash = self.calculate_file_hash(file_path)
            matches = actual_hash == expected_hash
            
            self.logger.info(
                f"File hash verification {'passed' if matches else 'failed'}",
                extra={
                    'file_path': str(file_path),
                    'expected_hash': expected_hash[:16] + '...',
                    'actual_hash': actual_hash[:16] + '...',
                    'matches': matches
                }
            )
            
            return matches
            
        except Exception as e:
            self.logger.error(
                f"Error verifying file hash: {e}",
                extra={
                    'file_path': str(file_path),
                    'error': str(e)
                }
            )
            return False
