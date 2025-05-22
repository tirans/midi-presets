import argparse
import json
import sys
from pathlib import Path
from typing import List

from ..checksum.manifest import ManifestGenerator
from ..utils.logging import LoggerSetup, get_logger

class ChecksumCLI:
    def __init__(self):
        self.logger = get_logger('cli.checksum')
    
    def generate_checksums(self, devices_folder: Path) -> bool:
        """Generate repository checksums"""
        try:
            self.logger.info(f"Generating checksums for {devices_folder}")
            
            generator = ManifestGenerator(devices_folder)
            manifest = generator.generate_manifest()
            
            manifest_path = devices_folder / "_manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
            
            self.logger.info(f"Manifest saved to {manifest_path}")
            print(f"✅ Repository manifest saved to {manifest_path}")
            print(f"📊 Repository checksum: {manifest['repository_checksum'][:16]}...")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating checksums: {e}")
            print(f"❌ Error generating checksums: {e}")
            return False
    
    def verify_checksums(self, devices_folder: Path) -> bool:
        """Verify existing checksums"""
        try:
            self.logger.info(f"Verifying checksums for {devices_folder}")
            
            manifest_path = devices_folder / "_manifest.json"
            if not manifest_path.exists():
                print(f"❌ No manifest file found at {manifest_path}")
                return False
            
            generator = ManifestGenerator(devices_folder)
            if generator.verify_manifest(manifest_path):
                print("✅ All checksums verified successfully")
                return True
            else:
                print("❌ Checksum verification failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying checksums: {e}")
            print(f"❌ Error verifying checksums: {e}")
            return False
    
    def run(self, args: List[str] = None) -> int:
        """Run checksum CLI"""
        parser = argparse.ArgumentParser(description='Generate and verify repository checksums')
        parser.add_argument('--verify', action='store_true', help='Verify existing checksums')
        parser.add_argument('--devices-folder', default='devices', help='Path to devices folder')
        parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        parser.add_argument('--log-file', type=Path, help='Log file path')
        parser.add_argument('--json-logs', action='store_true', help='Output logs in JSON format')
        
        parsed_args = parser.parse_args(args)
        
        # Setup logging
        LoggerSetup.setup_logging(
            level=parsed_args.log_level,
            log_file=parsed_args.log_file,
            json_format=parsed_args.json_logs
        )
        
        devices_folder = Path(parsed_args.devices_folder)
        if not devices_folder.exists():
            print(f"❌ Devices folder not found: {devices_folder}")
            return 1
        
        if parsed_args.verify:
            success = self.verify_checksums(devices_folder)
        else:
            success = self.generate_checksums(devices_folder)
        
        return 0 if success else 1
