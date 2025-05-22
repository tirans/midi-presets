from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from .base import BaseMetadataModel, ValidationStatus
from ..utils.logging import get_logger

logger = get_logger('models.preset')

class PresetMetadataModel(BaseMetadataModel):
    version: str = Field(..., pattern=r'^\d+\.\d+$')
    validation_status: ValidationStatus
    source: str = Field(..., min_length=1, max_length=50)
    derived_from: Optional[str] = None
    midi_learn_source: Optional[str] = None

    def __init__(self, **data):
        logger.debug(
            "Initializing PresetMetadataModel",
            extra={
                'version': data.get('version'),
                'validation_status': data.get('validation_status'),
                'source': data.get('source'),
                'derived_from': data.get('derived_from')
            }
        )
        super().__init__(**data)

class PresetModel(BaseModel):
    preset_id: str = Field(..., min_length=1, max_length=100)
    cc_0: Optional[int] = Field(None, ge=0, le=127)
    pgm: int = Field(..., ge=0, le=127)
    category: str = Field(..., min_length=1, max_length=50)
    preset_name: str = Field(..., min_length=1, max_length=100)
    sendmidi_command: str = Field(..., min_length=1)
    characters: List[str] = Field(default_factory=list)
    performance_notes: Optional[str] = Field("", max_length=500)
    user_ratings: Dict[str, Any] = Field(default_factory=dict)
    usage_stats: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        logger.debug(
            "Initializing PresetModel",
            extra={
                'preset_id': data.get('preset_id'),
                'preset_name': data.get('preset_name'),
                'category': data.get('category'),
                'pgm': data.get('pgm'),
                'cc_0': data.get('cc_0')
            }
        )
        super().__init__(**data)

        logger.info(
            f"Created preset: {self.preset_name}",
            extra={
                'preset_id': self.preset_id,
                'preset_name': self.preset_name,
                'category': self.category,
                'pgm': self.pgm,
                'cc_0': self.cc_0,
                'characters_count': len(self.characters),
                'has_performance_notes': bool(self.performance_notes.strip()),
                'has_user_ratings': bool(self.user_ratings),
                'has_usage_stats': bool(self.usage_stats)
            }
        )

    @validator('preset_name')
    def validate_preset_name(cls, v):
        logger.debug(f"Validating preset name: {v}")
        invalid_chars = ['<', '>', '{', '}', '\\', '/', ';', '"', "'"]
        if any(char in v for char in invalid_chars):
            logger.error(
                f"Preset name contains invalid characters",
                extra={'preset_name': v, 'invalid_chars': invalid_chars}
            )
            raise ValueError(f'Preset name contains invalid characters: {invalid_chars}')
        return v

    @validator('sendmidi_command')
    def validate_sendmidi_command(cls, v):
        logger.debug(f"Validating sendmidi command: {v[:50]}...")
        if not v.startswith('sendmidi'):
            logger.error(
                f"Invalid sendmidi command format",
                extra={'command_start': v[:20]}
            )
            raise ValueError('Command must start with "sendmidi"')
        return v

    @validator('preset_id')
    def validate_preset_id(cls, v):
        logger.debug(f"Validating preset ID: {v}")
        if not v.replace('_', '').replace('-', '').isalnum():
            logger.error(
                f"Invalid preset ID format",
                extra={'preset_id': v}
            )
            raise ValueError('Preset ID must be alphanumeric with underscores/hyphens only')
        return v

    @validator('pgm')
    def validate_program_number(cls, v):
        logger.debug(f"Validating program number: {v}")
        if not (0 <= v <= 127):
            logger.warning(
                f"Program number outside MIDI range",
                extra={'pgm': v}
            )
        return v

    @validator('cc_0')
    def validate_control_change(cls, v):
        if v is not None:
            logger.debug(f"Validating CC_0: {v}")
            if not (0 <= v <= 127):
                logger.warning(
                    f"CC_0 value outside MIDI range",
                    extra={'cc_0': v}
                )
        return v
