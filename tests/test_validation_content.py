import pytest
import json
import tempfile
from pathlib import Path

from midi_presets.validation.content import ContentValidator
from midi_presets.utils.logging import LoggerSetup

class TestContentValidator:
    @pytest.fixture(autouse=True)
    def setup_logging(self):
        LoggerSetup.setup_logging(level="DEBUG")
    
    def test_validate_valid_file(self, temp_dir, sample_device_data):
        """Test validation of a valid JSON file"""
        validator = ContentValidator()
        
        # Create valid file
        valid_file = temp_dir / "valid.json"
        with open(valid_file, 'w') as f:
            json.dump(sample_device_data, f)
        
        assert validator.validate(valid_file) == True
        assert len(validator.get_errors()) == 0
    
    def test_validate_file_too_large(self, temp_dir, sample_device_data):
        """Test validation fails for files that are too large"""
        validator = ContentValidator(max_file_size_mb=0.001)  # Very small limit
        
        # Create large file
        large_file = temp_dir / "large.json"
        large_data = sample_device_data.copy()
        large_data["large_field"] = "x" * 10000  # Make it large
        
        with open(large_file, 'w') as f:
            json.dump(large_data, f)
        
        assert validator.validate(large_file) == False
        errors = validator.get_errors()
        assert len(errors) > 0
        assert "exceeds" in errors[0].message.lower()
    
    def test_validate_invalid_json(self, temp_dir):
        """Test validation fails for invalid JSON"""
        validator = ContentValidator()
        
        # Create invalid JSON file
        invalid_file = temp_dir / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write('{"invalid": json}')  # Invalid JSON
        
        assert validator.validate(invalid_file) == False
        errors = validator.get_errors()
        assert len(errors) > 0
        assert "json" in errors[0].message.lower()
    
    def test_validate_invalid_schema(self, temp_dir):
        """Test validation fails for invalid schema"""
        validator = ContentValidator()
        
        # Create file with invalid schema
        invalid_file = temp_dir / "invalid_schema.json"
        invalid_data = {"invalid": "schema"}
        
        with open(invalid_file, 'w') as f:
            json.dump(invalid_data, f)
        
        assert validator.validate(invalid_file) == False
        errors = validator.get_errors()
        assert len(errors) > 0
        assert "schema" in errors[0].message.lower()
    
    def test_validate_missing_file(self, temp_dir):
        """Test validation fails for missing file"""
        validator = ContentValidator()
        
        missing_file = temp_dir / "missing.json"
        # Don't create the file
        
        assert validator.validate(missing_file) == False
        errors = validator.get_errors()
        assert len(errors) > 0
