from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from .base import BaseMetadataModel
from .collection import PresetCollectionModel
from ..utils.logging import get_logger

logger = get_logger('models.device')

class FileMetadataModel(BaseMetadataModel):
    schema_version: str = Field(..., pattern=r'^\d+\.\d+\.\d+$')
    file_revision: int = Field(..., ge=1)
    created_by: str = Field(..., min_length=1, max_length=100)
    modified_by: str = Field(..., min_length=1, max_length=100)
    migration_path: List[str] = Field(default_factory=list)
    compatibility: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        logger.debug(
            "Initializing FileMetadataModel",
            extra={
                'schema_version': data.get('schema_version'),
                'file_revision': data.get('file_revision'),
                'created_by': data.get('created_by'),
                'modified_by': data.get('modified_by')
            }
        )
        super().__init__(**data)

        if self.migration_path:
            logger.info(
                f"File has migration path with {len(self.migration_path)} versions",
                extra={
                    'migration_path': self.migration_path,
                    'current_version': self.schema_version
                }
            )

class DeviceInfoModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., min_length=1, max_length=20)
    manufacturer: str = Field(..., min_length=1, max_length=100)
    manufacturer_id: int = Field(..., ge=0, le=127)
    device_id: int = Field(..., ge=0, le=127)
    ports: List[str] = Field(default_factory=lambda: ["IN", "OUT"])
    midi_channels: Dict[str, int]
    midi_ports: Dict[str, str]

    def __init__(self, **data):
        logger.debug(
            "Initializing DeviceInfoModel",
            extra={
                'device_name': data.get('name'),
                'manufacturer': data.get('manufacturer'),
                'device_version': data.get('version'),
                'manufacturer_id': data.get('manufacturer_id'),
                'device_id': data.get('device_id')
            }
        )
        super().__init__(**data)

        logger.info(
            f"Created device info for {self.name} v{self.version} by {self.manufacturer}",
            extra={
                'device_name': self.name,
                'device_version': self.version,
                'manufacturer': self.manufacturer,
                'midi_ports': self.midi_ports,
                'midi_channels': self.midi_channels
            }
        )

    @validator('name')
    def validate_device_name(cls, v):
        logger.debug(f"Validating device name: {v}")
        invalid_chars = ['<', '>', '/', '\\', ':', '*', '?', '"', '|']
        if any(char in v for char in invalid_chars):
            logger.error(
                f"Device name contains invalid characters",
                extra={'device_name': v, 'invalid_chars': invalid_chars}
            )
            raise ValueError(f'Device name contains invalid characters: {invalid_chars}')
        return v

class DeviceModel(BaseModel):
    file_metadata: FileMetadataModel = Field(alias="_metadata")
    device_info: DeviceInfoModel
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    preset_collections: Dict[str, PresetCollectionModel] = Field(..., min_items=1)

    def __init__(self, **data):
        logger.info(
            "Initializing DeviceModel",
            extra={
                'device_name': data.get('device_info', {}).get('name', 'unknown'),
                'schema_version': data.get('_metadata', {}).get('schema_version', 'unknown'),
                'collections_count': len(data.get('preset_collections', {}))
            }
        )
        super().__init__(**data)

        # Log device summary
        total_presets = sum(
            len(collection.presets) 
            for collection in self.preset_collections.values()
        )

        logger.info(
            f"Device model created successfully",
            extra={
                'device_name': self.device_info.name,
                'manufacturer': self.device_info.manufacturer,
                'schema_version': self.file_metadata.schema_version,
                'file_revision': self.file_metadata.file_revision,
                'total_collections': len(self.preset_collections),
                'total_presets': total_presets,
                'collection_names': list(self.preset_collections.keys())
            }
        )

    @validator('preset_collections')
    def validate_preset_collections(cls, v):
        logger.debug(f"Validating {len(v)} preset collections")

        if not v:
            logger.error("No preset collections found")
            raise ValueError('At least one preset collection is required')

        for collection_name in v.keys():
            logger.debug(f"Validating collection name: {collection_name}")
            if not collection_name.replace('_', '').replace('-', '').isalnum():
                logger.error(
                    f"Invalid collection name",
                    extra={'collection_name': collection_name}
                )
                raise ValueError(f'Collection name "{collection_name}" contains invalid characters')

        logger.info(
            "All preset collections validated successfully",
            extra={'collection_names': list(v.keys())}
        )
        return v

    class Config:
        extra = "allow"
        validate_default = True
