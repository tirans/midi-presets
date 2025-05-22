# MIDI Device Presets Repository

A comprehensive system for managing, validating, and sharing MIDI device presets with version control and community collaboration.

## 🎵 Features

- **Comprehensive Validation**: Multi-layer validation including content, security, business rules, and structure
- **Version Control**: Full versioning support for presets and collections
- **Community Sharing**: GitHub-based preset sharing with automated validation
- **Checksum Integrity**: SHA256 checksums for data integrity verification
- **Rate Limited**: Prevents abuse with concurrent and hourly rate limits
- **Structured Logging**: Comprehensive logging for monitoring and debugging
- **CLI Tools**: Command-line tools for validation and checksum generation

## 📁 Repository Structure

```
midi-device-presets/
├── src/midi_presets/          # Main Python package
├── devices/                   # Device preset files (max 4 folder levels)
├── tests/                     # Unit tests
├── scripts/                   # Standalone scripts
├── .github/workflows/         # GitHub Actions
└── docs/                      # Documentation
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/tirans/midi-device-presets.git
cd midi-device-presets

# Install dependencies
pip install -e .

# Install development dependencies
pip install -e .[dev]
```

### Usage

```bash
# Validate preset files
validate-presets devices/expressivee/factory.json

# Generate repository checksums
generate-checksums --devices-folder devices

# Run tests
pytest

# Run with coverage
pytest --cov=src/midi_presets
```

## 📝 Device File Format

Device files follow a structured JSON format with metadata, device info, and preset collections:

```json
{
  "_metadata": {
    "schema_version": "3.1.0",
    "file_revision": 1,
    "created_date": "2024-01-01T00:00:00Z",
    "modified_date": "2024-01-01T00:00:00Z"
  },
  "device_info": {
    "name": "Device Name",
    "manufacturer": "Manufacturer Name"
  },
  "preset_collections": {
    "collection_name": {
      "metadata": { /* collection metadata */ },
      "presets": [ /* array of presets */ ],
      "preset_metadata": { /* preset metadata by ID */ }
    }
  }
}
```

## 🔒 Validation Rules

- **File Size**: Maximum 3MB per file
- **Folder Depth**: Maximum 4 levels below `devices/`
- **Path Restriction**: Public users can only modify files under the `devices/` directory
- **Security**: Scans for malicious content patterns
- **MIDI Ranges**: Validates MIDI values (0-127)
- **Uniqueness**: Ensures preset IDs are unique
- **Schema**: Validates against Pydantic models

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Add your preset files to appropriate device folders
   - Files must be placed under the `devices/` directory
   - Maximum 4 directory levels under `devices/`
   - Maximum file size is 3MB
4. Ensure all validation passes
5. Submit a pull request

Valid submissions are automatically merged if they pass all checks. GitHub Actions will automatically validate your changes when you push to your branch or create a pull request.

## 📊 Rate Limits

- Maximum 2 concurrent validations
- Maximum 10 validations per hour
- Prevents repository abuse

## 🔧 Configuration

The system supports configuration via:
- Environment variables
- JSON configuration files
- Command-line arguments

See configuration examples in the documentation.

## 🔄 GitHub Integration

The repository uses GitHub Actions to automatically validate preset files:

- **Validate MIDI Presets**: Runs on push and pull request events that modify JSON files in the devices directory
  - Validates JSON syntax and schema
  - Checks file size (max 3MB)
  - Verifies directory depth (max 4 levels under devices/)
  - Ensures files are properly structured

- **Restrict Changes**: Runs on pull request events
  - Ensures public users can only modify files under the devices/ directory
  - Allows repository maintainers to modify files outside devices/
  - Prevents unauthorized changes to repository infrastructure

## 🐛 Issues

Report issues on the [GitHub Issues](https://github.com/tirans/midi-device-presets/issues) page.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

- [ ] Web interface for preset management
- [ ] Real-time collaboration features
- [ ] Advanced search and filtering
- [ ] Preset recommendation system
- [ ] Multi-device support

---

Built with ❤️ for the MIDI community
