import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import time

from .calculator import ChecksumCalculator
from ..utils.git import GitUtils
from ..utils.logging import get_logger

class ManifestGenerator:
    def __init__(self, devices_folder: Path):
        self.devices_folder = Path(devices_folder)
        self.calculator = ChecksumCalculator()
        self.git_utils = GitUtils()
        self.logger = get_logger('checksum.manifest')
        
        self.logger.info(
            f"ManifestGenerator initialized",
            extra={'devices_folder': str(self.devices_folder)}
        )
    
    def generate_manifest(self) -> Dict[str, Any]:
        """Generate complete repository manifest"""
        start_time = time.time()
        
        self.logger.info("Starting repository manifest generation")
        
        manifest = {
            "_repository_metadata": {
                "manifest_version": "1.0.0",
                "generated_date": datetime.utcnow().isoformat() + "Z",
                "repository_revision": self.git_utils.get_revision_count(),
                "total_devices": 0,
                "total_presets": 0,
                "generator": "tirans/midi-device-presets-validator@2.1.0"
            },
            "file_checksums": {},
            "folder_checksums": {},
            "repository_checksum": "",
            "statistics": {
                "devices_by_manufacturer": {},
                "schema_version_distribution": {},
                "total_community_contributions": 0,
                "validation_summary": {
                    "passed": 0,
                    "failed": 0,
                    "pending": 0
                }
            }
        }
        
        self.logger.debug(
            f"Initialized manifest structure",
            extra={'repository_revision': manifest["_repository_metadata"]["repository_revision"]}
        )
        
        # Process all JSON files
        total_devices = 0
        total_presets = 0
        processed_files = 0
        failed_files = 0
        
        json_files = list(self.devices_folder.rglob("*.json"))
        json_files = [f for f in json_files if f.name != "_manifest.json"]
        
        self.logger.info(
            f"Found {len(json_files)} JSON files to process",
            extra={'file_count': len(json_files)}
        )
        
        for json_file in json_files:
            try:
                self.logger.debug(f"Processing file: {json_file}")
                
                relative_path = str(json_file.relative_to(self.devices_folder))
                file_info = self._analyze_file(json_file)
                manifest["file_checksums"][relative_path] = file_info
                
                if file_info.get("validation_status") == "passed":
                    total_devices += 1
                    total_presets += file_info.get("preset_count", 0)
                    processed_files += 1
                else:
                    failed_files += 1
                
                # Update statistics
                self._update_statistics(manifest["statistics"], file_info, json_file)
                
                if processed_files % 10 == 0:  # Log progress every 10 files
                    self.logger.info(
                        f"Progress: {processed_files}/{len(json_files)} files processed",
                        extra={
                            'processed': processed_files,
                            'total': len(json_files),
                            'failed': failed_files
                        }
                    )
                
            except Exception as e:
                failed_files += 1
                self.logger.error(
                    f"Error processing file: {e}",
                    extra={
                        'file_path': str(json_file),
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
                )
        
        # Calculate folder checksums
        self.logger.info("Calculating folder checksums")
        self._calculate_folder_checksums(manifest)
        
        # Calculate repository checksum
        self.logger.info("Calculating repository checksum")
        manifest["repository_checksum"] = self.calculator.calculate_repository_hash(self.devices_folder)
        
        # Update metadata
        manifest["_repository_metadata"]["total_devices"] = total_devices
        manifest["_repository_metadata"]["total_presets"] = total_presets
        
        duration = (time.time() - start_time) * 1000
        
        self.logger.info(
            f"Repository manifest generation completed",
            extra={
                'total_devices': total_devices,
                'total_presets': total_presets,
                'processed_files': processed_files,
                'failed_files': failed_files,
                'repository_checksum': manifest["repository_checksum"][:16] + '...',
                'duration_ms': duration
            }
        )
        
        return manifest
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze individual JSON file"""
        self.logger.debug(f"Analyzing file: {file_path}")
        
        try:
            file_start_time = time.time()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get("_metadata", {})
            
            # Count presets
            preset_count = 0
            collections_info = {}
            
            for collection_name, collection_data in data.get("preset_collections", {}).items():
                collection_presets = len(collection_data.get("presets", []))
                preset_count += collection_presets
                collections_info[collection_name] = collection_presets
            
            # Calculate file hash
            file_hash = self.calculator.calculate_file_hash(file_path)
            
            file_analysis_duration = (time.time() - file_start_time) * 1000
            
            result = {
                "sha256": file_hash,
                "size_bytes": file_path.stat().st_size,
                "last_modified": metadata.get("modified_date"),
                "schema_version": metadata.get("schema_version", "unknown"),
                "file_revision": metadata.get("file_revision", 1),
                "preset_count": preset_count,
                "validation_status": "passed"
            }
            
            self.logger.debug(
                f"File analysis completed",
                extra={
                    'file_path': str(file_path),
                    'file_hash': file_hash[:16] + '...',
                    'preset_count': preset_count,
                    'collections': collections_info,
                    'schema_version': result["schema_version"],
                    'duration_ms': file_analysis_duration
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                f"Error analyzing file: {e}",
                extra={
                    'file_path': str(file_path),
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            )
            
            # Return basic info even on error
            try:
                file_hash = self.calculator.calculate_file_hash(file_path)
                file_size = file_path.stat().st_size
            except:
                file_hash = "error_calculating_hash"
                file_size = 0
            
            return {
                "sha256": file_hash,
                "size_bytes": file_size,
                "last_modified": None,
                "schema_version": "unknown",
                "file_revision": 0,
                "preset_count": 0,
                "validation_status": "failed",
                "error": str(e)
            }
    
    def _calculate_folder_checksums(self, manifest: Dict[str, Any]):
        """Calculate checksums for all folders"""
        self.logger.info("Starting folder checksum calculation")
        
        folders_processed = 0
        
        for folder in self.devices_folder.rglob("*"):
            if folder.is_dir() and any(folder.rglob("*.json")):
                try:
                    relative_path = str(folder.relative_to(self.devices_folder))
                    if relative_path == ".":
                        relative_path = "devices"
                    
                    folder_hash = self.calculator.calculate_folder_hash(folder)
                    manifest["folder_checksums"][relative_path] = folder_hash
                    folders_processed += 1
                    
                    self.logger.debug(
                        f"Folder checksum calculated",
                        extra={
                            'folder_path': relative_path,
                            'folder_hash': folder_hash[:16] + '...'
                        }
                    )
                    
                except Exception as e:
                    self.logger.error(
                        f"Error calculating folder checksum: {e}",
                        extra={
                            'folder_path': str(folder),
                            'error': str(e)
                        }
                    )
        
        self.logger.info(
            f"Folder checksum calculation completed",
            extra={'folders_processed': folders_processed}
        )
    
    def _update_statistics(self, stats: Dict[str, Any], file_info: Dict[str, Any], file_path: Path):
        """Update statistics with file information"""
        # Update validation summary
        status = file_info.get("validation_status", "pending")
        stats["validation_summary"][status] += 1
        
        # Update schema version distribution
        schema_version = file_info.get("schema_version", "unknown")
        if schema_version not in stats["schema_version_distribution"]:
            stats["schema_version_distribution"][schema_version] = 0
        stats["schema_version_distribution"][schema_version] += 1
        
        # Try to extract manufacturer info for statistics
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            manufacturer = data.get("device_info", {}).get("manufacturer", "unknown")
            if manufacturer not in stats["devices_by_manufacturer"]:
                stats["devices_by_manufacturer"][manufacturer] = 0
            stats["devices_by_manufacturer"][manufacturer] += 1
            
        except Exception as e:
            self.logger.debug(
                f"Could not extract manufacturer info: {e}",
                extra={'file_path': str(file_path)}
            )
    
    def verify_manifest(self, manifest_path: Path) -> bool:
        """Verify existing manifest against current repository state"""
        self.logger.info(f"Verifying manifest: {manifest_path}")
        
        if not manifest_path.exists():
            self.logger.error(f"Manifest file not found: {manifest_path}")
            return False
        
        try:
            with open(manifest_path, 'r') as f:
                stored_manifest = json.load(f)
            
            verification_results = {
                'files_verified': 0,
                'files_failed': 0,
                'missing_files': 0,
                'extra_files': 0
            }
            
            stored_checksums = stored_manifest.get("file_checksums", {})
            
            # Verify each file in stored manifest
            for file_path, stored_info in stored_checksums.items():
                full_path = self.devices_folder / file_path
                
                if not full_path.exists():
                    verification_results['missing_files'] += 1
                    self.logger.warning(
                        f"Missing file referenced in manifest",
                        extra={'file_path': file_path}
                    )
                    continue
                
                if self.calculator.verify_file_hash(full_path, stored_info.get("sha256", "")):
                    verification_results['files_verified'] += 1
                else:
                    verification_results['files_failed'] += 1
                    self.logger.error(
                        f"File hash verification failed",
                        extra={'file_path': file_path}
                    )
            
            # Check for extra files not in manifest
            current_files = set(
                str(f.relative_to(self.devices_folder))
                for f in self.devices_folder.rglob("*.json")
                if f.name != "_manifest.json"
            )
            manifest_files = set(stored_checksums.keys())
            extra_files = current_files - manifest_files
            verification_results['extra_files'] = len(extra_files)
            
            for extra_file in extra_files:
                self.logger.warning(
                    f"Extra file not in manifest",
                    extra={'file_path': extra_file}
                )
            
            all_verified = (
                verification_results['files_failed'] == 0 and
                verification_results['missing_files'] == 0 and
                verification_results['extra_files'] == 0
            )
            
            self.logger.info(
                f"Manifest verification {'passed' if all_verified else 'failed'}",
                extra=verification_results
            )
            
            return all_verified
            
        except Exception as e:
            self.logger.error(
                f"Error verifying manifest: {e}",
                extra={
                    'manifest_path': str(manifest_path),
                    'error': str(e)
                }
            )
            return False
