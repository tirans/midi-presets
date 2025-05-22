import argparse
import sys
from typing import List

from .validate import ValidationCLI
from .checksum import ChecksumCLI
from ..utils.logging import LoggerSetup

def main(args: List[str] = None) -> int:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='MIDI Device Presets Management CLI',
        prog='midi-presets'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate subcommand
    validate_parser = subparsers.add_parser('validate', help='Validate preset files')
    validate_parser.add_argument('files', nargs='+', help='JSON files to validate')
    validate_parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    validate_parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    validate_parser.add_argument('--log-file', help='Log file path')
    validate_parser.add_argument('--json-logs', action='store_true', help='Output logs in JSON format')
    
    # Checksum subcommand
    checksum_parser = subparsers.add_parser('checksum', help='Generate or verify checksums')
    checksum_parser.add_argument('--verify', action='store_true', help='Verify existing checksums')
    checksum_parser.add_argument('--devices-folder', default='devices', help='Path to devices folder')
    checksum_parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    checksum_parser.add_argument('--log-file', help='Log file path')
    checksum_parser.add_argument('--json-logs', action='store_true', help='Output logs in JSON format')
    
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    # Setup basic logging first
    LoggerSetup.setup_logging(level='INFO')
    
    if parsed_args.command == 'validate':
        cli = ValidationCLI()
        return cli.run([
            '--log-level', parsed_args.log_level,
            *((['--log-file', parsed_args.log_file] if parsed_args.log_file else [])),
            *((['--json-logs'] if parsed_args.json_logs else [])),
            *((['--strict'] if parsed_args.strict else [])),
            *parsed_args.files
        ])
    
    elif parsed_args.command == 'checksum':
        cli = ChecksumCLI()
        return cli.run([
            '--devices-folder', parsed_args.devices_folder,
            '--log-level', parsed_args.log_level,
            *((['--log-file', parsed_args.log_file] if parsed_args.log_file else [])),
            *((['--json-logs'] if parsed_args.json_logs else [])),
            *((['--verify'] if parsed_args.verify else []))
        ])
    
    return 1

if __name__ == '__main__':
    sys.exit(main())
