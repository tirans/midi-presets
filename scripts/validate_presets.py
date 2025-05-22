#!/usr/bin/env python3
"""
Standalone validation script.

This script provides a command-line interface for validating 
MIDI device preset JSON files.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from midi_presets.cli.validate import ValidationCLI

if __name__ == "__main__":
    cli = ValidationCLI()
    sys.exit(cli.run())
