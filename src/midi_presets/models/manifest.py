from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional
from datetime import datetime
import re
from .base import ValidationStatus
from ..utils.logging import get_logger

logger = get_logger('models.manifest')

class FileChecksumModel(BaseModel):
    sha256: str = Field(..., pattern=r'^[a-f0-9]{64}$')
    size_bytes: int = Field(..., ge=0)
    last_modified: datetime
    schema_version: str
    file_revision: int = Field(..., ge=1)
    preset_count: int = Field(..., ge=0)
    validation_status: ValidationStatus
    contributor: Optional[str] = None

    def __init__(self, **data):
        logger.debug(
            "Initializing FileChecksumModel",
            extra={
                'sha256': data.get('sha256', '')[:16] + '...',
                'size_bytes': data.get('size_bytes'),
                'schema_version': data.get('schema_version'),
                'file_revision': data.get('file_revision'),
                'preset_count': data.get('preset_count'),
                'validation_status': data.get('validation_status')
            }
        )
        super().__init__(**data)

class RepositoryManifestModel(BaseModel):
    _repository_metadata: Dict[str, Any]
    file_checksums: Dict[str, FileChecksumModel]
    folder_checksums: Dict[str, str]
    repository_checksum: str = Field(..., pattern=r'^[a-f0-9]{64}$')
    statistics: Dict[str, Any]

    def __init__(self, **data):
        logger.info(
            "Initializing RepositoryManifestModel",
            extra={
                'file_count': len(data.get('file_checksums', {})),
                'folder_count': len(data.get('folder_checksums', {})),
                'repository_checksum': data.get('repository_checksum', '')[:16] + '...'
            }
        )

        super().__init__(**data)

        # Log repository statistics
        stats = self.statistics
        repo_meta = self._repository_metadata

        logger.info(
            "Repository manifest loaded successfully",
            extra={
                'manifest_version': repo_meta.get('manifest_version'),
                'repository_revision': repo_meta.get('repository_revision'),
                'total_devices': repo_meta.get('total_devices'),
                'total_presets': repo_meta.get('total_presets'),
                'file_checksums_count': len(self.file_checksums),
                'folder_checksums_count': len(self.folder_checksums),
                'repository_checksum': self.repository_checksum[:16] + '...',
                'validation_summary': stats.get('validation_summary', {}),
                'schema_distribution': stats.get('schema_version_distribution', {})
            }
        )

    @validator('folder_checksums')
    def validate_folder_checksums(cls, v):
        logger.debug(f"Validating {len(v)} folder checksums")

        sha256_pattern = r'^[a-f0-9]{64}$'
        invalid_checksums = []

        for folder, checksum in v.items():
            if not re.match(sha256_pattern, checksum):
                invalid_checksums.append((folder, checksum))
                logger.error(
                    f"Invalid checksum format for folder",
                    extra={'folder': folder, 'checksum': checksum[:16] + '...'}
                )

        if invalid_checksums:
            raise ValueError(f'Invalid checksum formats found for folders: {[f[0] for f in invalid_checksums]}')

        logger.info(f"All {len(v)} folder checksums validated successfully")
        return v

    @validator('repository_checksum')
    def validate_repository_checksum(cls, v):
        logger.debug(f"Validating repository checksum: {v[:16]}...")
        return v

    def get_file_by_checksum(self, checksum: str) -> Optional[str]:
        """Find file by its checksum"""
        logger.debug(f"Searching for file with checksum: {checksum[:16]}...")

        for file_path, file_info in self.file_checksums.items():
            if file_info.sha256 == checksum:
                logger.info(f"Found file: {file_path}")
                return file_path

        logger.warning(f"No file found with checksum: {checksum[:16]}...")
        return None

    def get_validation_summary(self) -> Dict[str, int]:
        """Get validation status summary"""
        summary = self.statistics.get('validation_summary', {})
        logger.debug(f"Validation summary: {summary}")
        return summary
