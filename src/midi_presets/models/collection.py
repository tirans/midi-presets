from pydantic import BaseModel, Field, validator
from typing import Dict, List
from .base import BaseMetadataModel, SyncStatus
from .preset import PresetModel, PresetMetadataModel
from ..utils.logging import get_logger

logger = get_logger('models.collection')

class CollectionMetadataModel(BaseMetadataModel):
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., pattern=r'^\d+\.\d+$')
    revision: int = Field(..., ge=1)
    author: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    readonly: bool = False
    preset_count: int = Field(..., ge=0)
    parent_collections: List[str] = Field(default_factory=list)
    sync_status: SyncStatus = SyncStatus.SYNCED

    def __init__(self, **data):
        logger.debug(
            "Initializing CollectionMetadataModel",
            extra={
                'collection_name': data.get('name'),
                'version': data.get('version'),
                'revision': data.get('revision'),
                'author': data.get('author'),
                'preset_count': data.get('preset_count'),
                'readonly': data.get('readonly', False)
            }
        )
        super().__init__(**data)

        logger.info(
            f"Collection metadata created: {self.name}",
            extra={
                'collection_name': self.name,
                'version': self.version,
                'revision': self.revision,
                'author': self.author,
                'preset_count': self.preset_count,
                'readonly': self.readonly,
                'sync_status': self.sync_status,
                'parent_collections': self.parent_collections
            }
        )

    @validator('author')
    def validate_author(cls, v):
        logger.debug(f"Validating author: {v}")
        invalid_chars = ['<', '>', '"', "'", ';', '&']
        if any(char in v for char in invalid_chars):
            logger.error(
                f"Author contains invalid characters",
                extra={'author': v, 'invalid_chars': invalid_chars}
            )
            raise ValueError(f'Author contains invalid characters: {invalid_chars}')
        return v

class PresetCollectionModel(BaseModel):
    metadata: CollectionMetadataModel
    presets: List[PresetModel] = Field(..., min_items=1, max_items=1000)
    preset_metadata: Dict[str, PresetMetadataModel]

    def __init__(self, **data):
        collection_name = data.get('metadata', {}).get('name', 'unknown')
        presets_count = len(data.get('presets', []))

        logger.info(
            f"Initializing PresetCollectionModel: {collection_name}",
            extra={
                'collection_name': collection_name,
                'presets_count': presets_count,
                'metadata_count': len(data.get('preset_metadata', {}))
            }
        )

        super().__init__(**data)

        # Log collection statistics
        categories = {}
        validation_statuses = {}
        sources = {}

        for preset in self.presets:
            # Count categories
            categories[preset.category] = categories.get(preset.category, 0) + 1

            # Get metadata for this preset
            preset_meta = self.preset_metadata.get(preset.preset_id)
            if preset_meta:
                # Count validation statuses
                status = preset_meta.validation_status
                validation_statuses[status] = validation_statuses.get(status, 0) + 1

                # Count sources
                source = preset_meta.source
                sources[source] = sources.get(source, 0) + 1

        logger.info(
            f"Collection {self.metadata.name} loaded successfully",
            extra={
                'collection_name': self.metadata.name,
                'total_presets': len(self.presets),
                'categories': categories,
                'validation_statuses': validation_statuses,
                'sources': sources,
                'readonly': self.metadata.readonly
            }
        )

    @validator('preset_metadata')
    def validate_preset_metadata_consistency(cls, v, values):
        logger.debug(f"Validating metadata consistency for {len(v)} presets")

        if 'presets' not in values:
            return v

        preset_ids = {preset.preset_id for preset in values['presets']}
        metadata_ids = set(v.keys())

        if preset_ids != metadata_ids:
            missing = preset_ids - metadata_ids
            extra = metadata_ids - preset_ids

            logger.error(
                "Preset metadata inconsistency detected",
                extra={
                    'missing_metadata': list(missing),
                    'extra_metadata': list(extra),
                    'preset_ids': list(preset_ids),
                    'metadata_ids': list(metadata_ids)
                }
            )

            errors = []
            if missing:
                errors.append(f"Missing metadata for presets: {missing}")
            if extra:
                errors.append(f"Extra metadata for non-existent presets: {extra}")

            raise ValueError("; ".join(errors))

        logger.info("Preset metadata consistency validation passed")
        return v

    @validator('metadata')
    def validate_preset_count(cls, v, values):
        logger.debug(f"Validating preset count: expected {v.preset_count}")

        if 'presets' not in values:
            return v

        actual_count = len(values['presets'])
        if v.preset_count != actual_count:
            logger.error(
                "Preset count mismatch",
                extra={
                    'expected_count': v.preset_count,
                    'actual_count': actual_count
                }
            )
            raise ValueError(f"Preset count mismatch: metadata={v.preset_count}, actual={actual_count}")

        logger.info(f"Preset count validation passed: {actual_count} presets")
        return v
