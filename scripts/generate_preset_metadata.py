#!/usr/bin/env python3
import json
import os
from datetime import datetime

def generate_preset_metadata():
    # Path to the JSON file
    json_file_path = os.path.join('devices', 'expressivee', 'expressivee_osmose.json')
    
    # Load the JSON file
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    # Get the presets
    presets = data['preset_collections']['factory_presets']['presets']
    
    # Create a new preset_metadata dictionary
    preset_metadata = {}
    
    # Generate metadata for each preset
    for preset in presets:
        cc_0 = preset.get('cc_0')
        pgm = preset.get('pgm')
        preset_name = preset.get('preset_name')
        
        # Generate a unique identifier for the preset
        preset_id = f"osmose_cc{cc_0}_pgm{pgm}"
        
        # Create metadata for the preset
        preset_metadata[preset_id] = {
            "version": "1.0",
            "created_date": "2024-05-01T00:00:00Z",
            "modified_date": "2024-05-01T00:00:00Z",
            "validation_status": "factory_verified",
            "source": "factory",
            "derived_from": None,
            "midi_learn_source": None
        }
    
    # Replace the preset_metadata in the JSON file
    data['preset_collections']['factory_presets']['preset_metadata'] = preset_metadata
    
    # Save the modified JSON file
    with open(json_file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Generated metadata for {len(presets)} presets")

if __name__ == "__main__":
    generate_preset_metadata()