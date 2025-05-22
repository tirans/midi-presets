from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from ..utils.logging import get_logger

logger = get_logger('models.base')

class ValidationStatus(str, Enum):
    VERIFIED = "verified"
    USER_VERIFIED = "user_verified"
    PENDING = "pending"
    FAILED = "failed"

class SyncStatus(str, Enum):
    SYNCED = "synced"
    MODIFIED = "modified"
    CONFLICT = "conflict"
    PENDING = "pending"

class BaseMetadataModel(BaseModel):
    """Base class for all metadata models"""
    created_date: datetime
    modified_date: datetime

    def __init__(self, **data):
        logger.debug(
            "Initializing BaseMetadataModel",
            extra={
                'created_date': data.get('created_date'),
                'modified_date': data.get('modified_date')
            }
        )
        super().__init__(**data)

        # Log validation of dates
        if self.created_date > self.modified_date:
            logger.warning(
                "Created date is after modified date",
                extra={
                    'created_date': self.created_date.isoformat(),
                    'modified_date': self.modified_date.isoformat()
                }
            )

    class Config:
        validate_default = True
        extra = "forbid"
