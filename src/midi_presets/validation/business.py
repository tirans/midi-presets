import json
from pathlib import Path
from collections import defaultdict, Counter
import time

from .base import BaseValidator
from ..models.device import DeviceModel
from ..utils.logging import get_logger

class BusinessRulesValidator(BaseValidator):
    def __init__(self):
        super().__init__()
        self.logger = get_logger('validation.business_rules')

        self.logger.info("BusinessRulesValidator initialized")

    def validate(self, file_path: Path) -> bool:
        """Validate business logic rules"""
        start_time = time.time()

        self.logger.info(
            f"Starting business rules validation",
            extra={'file_path': str(file_path), 'validation_type': 'business_rules'}
        )

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            device = DeviceModel(**data)

            self.logger.debug(
                f"Device model created for business validation",
                extra={
                    'file_path': str(file_path),
                    'device_name': device.device_info.name,
                    'collections_count': len(device.preset_collections)
                }
            )

            valid = True
            validation_results = {}

            # Run all business rule validations
            validation_results['preset_id_uniqueness'] = self._validate_preset_id_uniqueness(device, file_path)
            validation_results['midi_ranges'] = self._validate_midi_ranges(device, file_path)
            validation_results['collection_consistency'] = self._validate_collection_consistency(device, file_path)
            validation_results['naming_conventions'] = self._validate_naming_conventions(device, file_path)
            validation_results['data_integrity'] = self._validate_data_integrity(device, file_path)

            # Overall result
            valid = all(validation_results.values())

            duration = (time.time() - start_time) * 1000

            self.logger.info(
                f"Business rules validation {'passed' if valid else 'failed'}",
                extra={
                    'file_path': str(file_path),
                    'validation_results': validation_results,
                    'duration_ms': duration,
                    'error_count': len(self.get_errors()),
                    'warning_count': len(self.get_warnings())
                }
            )

            return valid

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.logger.error(
                f"Business rules validation error: {e}",
                extra={
                    'file_path': str(file_path),
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'duration_ms': duration
                }
            )
            self.add_error(f"Error in business rules validation: {e}", file_path=file_path)
            return False

    def _validate_preset_id_uniqueness(self, device: DeviceModel, file_path: Path) -> bool:
        """Validate that all preset IDs are unique across collections"""
        self.logger.debug("Validating preset ID uniqueness")

        all_preset_ids = []
        collection_preset_counts = {}

        for collection_name, collection in device.preset_collections.items():
            collection_ids = [preset.preset_id for preset in collection.presets]
            all_preset_ids.extend(collection_ids)
            collection_preset_counts[collection_name] = len(collection_ids)

            self.logger.debug(
                f"Collection {collection_name} has {len(collection_ids)} presets",
                extra={
                    'collection_name': collection_name,
                    'preset_count': len(collection_ids),
                    'preset_ids': collection_ids[:5]  # Log first 5 IDs
                }
            )

        # Find duplicates
        id_counts = Counter(all_preset_ids)
        duplicates = [pid for pid, count in id_counts.items() if count > 1]

        if duplicates:
            self.logger.error(
                f"Found {len(duplicates)} duplicate preset IDs",
                extra={
                    'file_path': str(file_path),
                    'duplicate_ids': duplicates,
                    'total_presets': len(all_preset_ids),
                    'unique_presets': len(set(all_preset_ids))
                }
            )

            self.add_error(
                f"Duplicate preset IDs found: {', '.join(duplicates)}",
                file_path=file_path
            )
            return False

        self.logger.info(
            f"Preset ID uniqueness validation passed",
            extra={
                'total_presets': len(all_preset_ids),
                'collections': collection_preset_counts
            }
        )
        return True

    def _validate_midi_ranges(self, device: DeviceModel, file_path: Path) -> bool:
        """Validate MIDI values are within acceptable ranges"""
        self.logger.debug("Validating MIDI ranges")

        valid = True
        midi_stats = {
            'cc_0_out_of_range': 0,
            'pgm_out_of_range': 0,
            'total_presets': 0,
            'cc_0_distribution': defaultdict(int),
            'pgm_distribution': defaultdict(int)
        }

        for collection_name, collection in device.preset_collections.items():
            for preset in collection.presets:
                midi_stats['total_presets'] += 1

                # Validate CC_0
                if preset.cc_0 is not None:
                    midi_stats['cc_0_distribution'][preset.cc_0] += 1
                    if not (0 <= preset.cc_0 <= 127):
                        midi_stats['cc_0_out_of_range'] += 1
                        self.add_error(
                            f"CC_0 value {preset.cc_0} out of MIDI range for preset {preset.preset_id}",
                            severity="warning",
                            file_path=file_path
                        )
                        self.logger.warning(
                            f"CC_0 out of range",
                            extra={
                                'preset_id': preset.preset_id,
                                'cc_0': preset.cc_0,
                                'collection': collection_name
                            }
                        )

                # Validate Program Change
                midi_stats['pgm_distribution'][preset.pgm] += 1
                if not (0 <= preset.pgm <= 127):
                    midi_stats['pgm_out_of_range'] += 1
                    self.add_error(
                        f"Program value {preset.pgm} out of MIDI range for preset {preset.preset_id}",
                        severity="warning",
                        file_path=file_path
                    )
                    self.logger.warning(
                        f"Program number out of range",
                        extra={
                            'preset_id': preset.preset_id,
                            'pgm': preset.pgm,
                            'collection': collection_name
                        }
                    )

        self.logger.info(
            f"MIDI ranges validation completed",
            extra={
                'file_path': str(file_path),
                'midi_stats': {
                    'total_presets': midi_stats['total_presets'],
                    'cc_0_out_of_range': midi_stats['cc_0_out_of_range'],
                    'pgm_out_of_range': midi_stats['pgm_out_of_range'],
                    'unique_cc_0_values': len(midi_stats['cc_0_distribution']),
                    'unique_pgm_values': len(midi_stats['pgm_distribution'])
                }
            }
        )

        return valid

    def _validate_collection_consistency(self, device: DeviceModel, file_path: Path) -> bool:
        """Validate internal consistency of collections"""
        self.logger.debug("Validating collection consistency")

        consistency_issues = []

        for collection_name, collection in device.preset_collections.items():
            self.logger.debug(
                f"Checking consistency for collection: {collection_name}",
                extra={'collection_name': collection_name}
            )

            # Check if parent collections exist
            for parent in collection.metadata.parent_collections:
                if parent not in device.preset_collections:
                    issue = f"Collection '{collection_name}' references non-existent parent '{parent}'"
                    consistency_issues.append(issue)
                    self.logger.error(
                        f"Non-existent parent collection referenced",
                        extra={
                            'collection_name': collection_name,
                            'parent_collection': parent
                        }
                    )

            # Check readonly consistency
            if collection.metadata.readonly and collection.metadata.sync_status != 'synced':
                issue = f"Readonly collection '{collection_name}' has sync status '{collection.metadata.sync_status}'"
                consistency_issues.append(issue)
                self.logger.warning(
                    f"Readonly collection has unexpected sync status",
                    extra={
                        'collection_name': collection_name,
                        'sync_status': collection.metadata.sync_status
                    }
                )

        if consistency_issues:
            for issue in consistency_issues:
                self.add_error(issue, file_path=file_path)

            self.logger.error(
                f"Collection consistency validation failed with {len(consistency_issues)} issues",
                extra={
                    'file_path': str(file_path),
                    'consistency_issues': consistency_issues
                }
            )
            return False

        self.logger.info("Collection consistency validation passed")
        return True

    def _validate_naming_conventions(self, device: DeviceModel, file_path: Path) -> bool:
        """Validate naming conventions"""
        self.logger.debug("Validating naming conventions")

        naming_issues = []

        # Check for consistent naming patterns
        preset_name_patterns = defaultdict(int)
        category_distribution = defaultdict(int)

        for collection_name, collection in device.preset_collections.items():
            for preset in collection.presets:
                # Analyze preset name patterns
                name_words = preset.preset_name.lower().split()
                if name_words:
                    first_word = name_words[0]
                    preset_name_patterns[first_word] += 1

                # Track category distribution
                category_distribution[preset.category] += 1

                # Check for very long names
                if len(preset.preset_name) > 50:
                    naming_issues.append(f"Preset '{preset.preset_id}' has very long name: {preset.preset_name}")
                    self.logger.warning(
                        f"Very long preset name",
                        extra={
                            'preset_id': preset.preset_id,
                            'name_length': len(preset.preset_name),
                            'preset_name': preset.preset_name
                        }
                    )

        # Convert defaultdict to Counter for most_common method
        from collections import Counter
        name_patterns_counter = Counter(preset_name_patterns)

        self.logger.info(
            f"Naming convention analysis completed",
            extra={
                'file_path': str(file_path),
                'top_name_patterns': dict(name_patterns_counter.most_common(5)),
                'category_distribution': dict(category_distribution),
                'naming_issues_count': len(naming_issues)
            }
        )

        return len(naming_issues) == 0

    def _validate_data_integrity(self, device: DeviceModel, file_path: Path) -> bool:
        """Validate data integrity"""
        self.logger.debug("Validating data integrity")

        integrity_stats = {
            'empty_preset_names': 0,
            'empty_sendmidi_commands': 0,
            'missing_characters': 0,
            'future_dates': 0,
            'invalid_ratings': 0
        }

        for collection_name, collection in device.preset_collections.items():
            for preset in collection.presets:
                # Check for empty or whitespace-only names
                if not preset.preset_name.strip():
                    integrity_stats['empty_preset_names'] += 1

                # Check sendmidi commands
                if not preset.sendmidi_command.strip():
                    integrity_stats['empty_sendmidi_commands'] += 1

                # Check if preset has any characteristics
                if not preset.characters:
                    integrity_stats['missing_characters'] += 1

                # Check metadata dates
                preset_meta = collection.preset_metadata.get(preset.preset_id)
                if preset_meta:
                    from datetime import datetime
                    now = datetime.now()
                    if preset_meta.created_date.replace(tzinfo=None) > now:
                        integrity_stats['future_dates'] += 1

                # Check user ratings validity
                for rating_key, rating_value in preset.user_ratings.items():
                    if isinstance(rating_value, (int, float)):
                        if not (0 <= rating_value <= 10):
                            integrity_stats['invalid_ratings'] += 1

        self.logger.info(
            f"Data integrity validation completed",
            extra={
                'file_path': str(file_path),
                'integrity_stats': integrity_stats
            }
        )

        # Log warnings for integrity issues
        for issue_type, count in integrity_stats.items():
            if count > 0:
                self.logger.warning(
                    f"Data integrity issue: {issue_type}",
                    extra={
                        'issue_type': issue_type,
                        'count': count,
                        'file_path': str(file_path)
                    }
                )

        return True  # Data integrity issues are warnings, not errors
