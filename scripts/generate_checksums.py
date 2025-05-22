#!/usr/bin/env python3
"""
Standalone checksum generation script.

This script generates repository manifests with file and folder checksums.
"""

import sys
import json
import argparse
from pathlib import Path

# Add src to Python path  
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from midi_presets.checksum.manifest import ManifestGenerator

def main():
    parser = argparse.ArgumentParser(description='Generate and verify repository checksums')
    parser.add_argument('--verify', action='store_true', help='Verify existing checksums')
    parser.add_argument('--devices-folder', default='devices', help='Path to devices folder')
    
    args = parser.parse_args()
    
    devices_folder = Path(args.devices_folder)
    if not devices_folder.exists():
        print(f"❌ Devices folder not found: {devices_folder}")
        return 1
    
    generator = ManifestGenerator(devices_folder)
    manifest_path = devices_folder / "_manifest.json"
    
    if args.verify:
        if generator.verify_manifest(manifest_path):
            print("✅ All checksums verified successfully")
            return 0
        else:
            print("❌ Checksum verification failed")
            return 1
    else:
        manifest = generator.generate_manifest()
        
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Repository manifest saved to {manifest_path}")
        print(f"📊 Repository checksum: {manifest['repository_checksum'][:16]}...")
        return 0

if __name__ == "__main__":
    sys.exit(main())
