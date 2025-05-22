"""
Checksum calculation and manifest generation.

This package handles:
- File and folder hash calculation
- Repository manifest generation
- Checksum verification
"""

from .calculator import ChecksumCalculator
from .manifest import ManifestGenerator

__all__ = [
    "ChecksumCalculator",
    "ManifestGenerator"
]
