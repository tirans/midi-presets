import pytest
import tempfile
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_device_data():
    """Sample valid device data"""
    return {
        "_metadata": {
            "schema_version": "3.1.0",
            "file_revision": 1,
            "created_date": "2024-01-01T00:00:00Z",
            "modified_date": "2024-01-01T00:00:00Z",
            "created_by": "Test User",
            "modified_by": "Test User",
            "migration_path": [],
            "compatibility": {}
        },
        "device_info": {
            "name": "Test Device",
            "version": "1.0",
            "manufacturer": "Test Manufacturer",
            "manufacturer_id": 1,
            "device_id": 1,
            "ports": ["IN", "OUT"],
            "midi_channels": {"IN": 1, "OUT": 1},
            "midi_ports": {"IN": "Test IN", "OUT": "Test OUT"}
        },
        "capabilities": {},
        "preset_collections": {
            "default": {
                "metadata": {
                    "name": "Default Presets",
                    "version": "1.0",
                    "revision": 1,
                    "created_date": "2024-01-01T00:00:00Z",
                    "modified_date": "2024-01-01T00:00:00Z",
                    "author": "Test User",
                    "description": "Test presets",
                    "readonly": True,
                    "preset_count": 1,
                    "parent_collections": [],
                    "sync_status": "synced"
                },
                "presets": [
                    {
                        "preset_id": "test_preset_001",
                        "cc_0": 30,
                        "pgm": 1,
                        "category": "test",
                        "preset_name": "Test Preset",
                        "sendmidi_command": "sendmidi dev \"Test OUT\" cc 0 30 pc 1",
                        "characters": ["test"],
                        "performance_notes": "",
                        "user_ratings": {},
                        "usage_stats": {}
                    }
                ],
                "preset_metadata": {
                    "test_preset_001": {
                        "version": "1.0",
                        "created_date": "2024-01-01T00:00:00Z",
                        "modified_date": "2024-01-01T00:00:00Z",
                        "validation_status": "verified",
                        "source": "factory",
                        "derived_from": None,
                        "midi_learn_source": None
                    }
                }
            }
        }
    }

@pytest.fixture
def devices_folder(temp_dir, sample_device_data):
    """Create a test devices folder structure"""
    devices_dir = temp_dir / "devices"
    devices_dir.mkdir()

    # Create test device
    test_device_dir = devices_dir / "test_device"
    test_device_dir.mkdir()

    # Create factory.json
    factory_file = test_device_dir / "factory.json"
    with open(factory_file, 'w') as f:
        json.dump(sample_device_data, f, indent=2)

    return devices_dir
