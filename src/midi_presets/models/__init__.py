"""
Data models for MIDI device presets.

This package contains Pydantic models for:
- Device information and metadata
- Preset collections and individual presets  
- Repository manifests and checksums
- Base classes and enums
"""

from .base import ValidationStatus, SyncStatus, BaseMetadataModel
from .device import DeviceModel, DeviceInfoModel, FileMetadataModel
from .preset import PresetModel, PresetMetadataModel
from .collection import PresetCollectionModel, CollectionMetadataModel
from .manifest import RepositoryManifestModel, FileChecksumModel

__all__ = [
    "ValidationStatus",
    "SyncStatus", 
    "BaseMetadataModel",
    "DeviceModel",
    "DeviceInfoModel",
    "FileMetadataModel",
    "PresetModel",
    "PresetMetadataModel", 
    "PresetCollectionModel",
    "CollectionMetadataModel",
    "RepositoryManifestModel",
    "FileChecksumModel"
]
