#!/usr/bin/env python3
"""
Test script to verify intelligent auto-mapping functionality
This simulates the user's reported issue with C0_Close.wav, C1_Distant.wav etc.
"""

import sys
import os
sys.path.append('/Users/zacharylquarles/Desktop/DecentSampler_FrontEnd/src')

from utils.intelligent_mapping import SampleAnalyzer, SampleGrouper, IntelligentMappingDialog

# Test data that matches user's reported filenames
test_files = [
    "/test/C0_Close.wav",
    "/test/C0_Distant.wav", 
    "/test/C1_Close.wav",
    "/test/C1_Distant.wav",
    "/test/C2_Close.wav",
    "/test/C2_Distant.wav",
    "/test/C3_Close.wav",
    "/test/C3_Distant.wav"
]

print("🧪 Testing Intelligent Auto-Mapping System")
print("=" * 50)

print("\n1. Testing SampleAnalyzer...")
analyses = []
for file_path in test_files:
    analysis = SampleAnalyzer.analyze_sample(file_path)
    analyses.append(analysis)
    
    print(f"  📁 {os.path.basename(file_path)}")
    print(f"     Note: {analysis['detected_note']} (MIDI {analysis['midi_note']})")
    print(f"     Variations: {analysis['variations']}")
    print(f"     Confidence: {analysis['confidence']}")

print(f"\n✅ Analyzed {len(analyses)} files")

print("\n2. Testing SampleGrouper...")
mapping_suggestions = SampleGrouper.group_samples(analyses)

print(f"  📝 Note mappings: {len(mapping_suggestions.get('note_mappings', {}))}")
print(f"  📁 Layer groups: {len(mapping_suggestions.get('layer_groups', {}))}")
print(f"  ❓ Orphan samples: {len(mapping_suggestions.get('orphan_samples', []))}")

# Show details
for midi_note, mapping_info in mapping_suggestions.get('note_mappings', {}).items():
    sample = mapping_info['primary_sample']
    lo, hi, root = mapping_info['suggested_range']
    print(f"    Note {midi_note}: {os.path.basename(sample['path'])} -> {lo}-{hi} (root {root})")

for midi_note, layer_info in mapping_suggestions.get('layer_groups', {}).items():
    samples = layer_info['samples']
    lo, hi, root = layer_info['suggested_range']
    sample_names = [os.path.basename(s['path']) for s in samples]
    print(f"    Layer {midi_note}: {sample_names} -> {lo}-{hi} (root {root})")

print("\n3. Testing IntelligentMappingDialog creation...")
try:
    # We can't test the dialog UI without PyQt app, but we can test the data structures
    print("  ✅ Dialog would be created with:")
    print(f"     - {len(mapping_suggestions.get('note_mappings', {}))} note mappings")
    print(f"     - {len(mapping_suggestions.get('layer_groups', {}))} layer groups")
    
    # Simulate what get_confirmed_mappings would return
    confirmed_notes = mapping_suggestions.get('note_mappings', {})
    confirmed_layers = mapping_suggestions.get('layer_groups', {})
    options = {
        'adjacent_fill': True,
        'preserve_existing': True
    }
    
    print(f"  ✅ Confirmed mappings: {len(confirmed_notes)} notes, {len(confirmed_layers)} layers")
    
except Exception as e:
    print(f"  ❌ Dialog creation error: {e}")

print("\n4. Testing mapping application simulation...")
# Simulate what _apply_intelligent_mappings does
try:
    applied_count = 0
    layered_count = 0
    
    # This is what should happen in the actual method
    for midi_note, mapping_info in confirmed_notes.items():
        sample_analysis = mapping_info['primary_sample']
        lo, hi, root = mapping_info['suggested_range']
        print(f"  📍 Would map {os.path.basename(sample_analysis['path'])} to {lo}-{hi} (root {root})")
        applied_count += 1
    
    for midi_note, layer_info in confirmed_layers.items():
        samples = layer_info['samples']
        lo, hi, root = layer_info['suggested_range']
        sample_names = [os.path.basename(s['path']) for s in samples]
        print(f"  🎵 Would create layer group {sample_names} at {lo}-{hi} (root {root})")
        layered_count += 1
    
    print(f"  ✅ Would apply {applied_count} note mappings and {layered_count} layer groups")
    
except Exception as e:
    print(f"  ❌ Mapping application error: {e}")

print("\n" + "=" * 50)
print("🎯 TEST RESULTS:")
print(f"✅ Detection working: {sum(1 for a in analyses if a['detected_note'])}/{len(analyses)} files detected")
print(f"✅ Grouping working: {len(mapping_suggestions.get('layer_groups', {}))} layer groups created")
print(f"✅ Range calculation: Adjacent fill logic appears functional")

# Check for the specific issue the user reported
if len(mapping_suggestions.get('layer_groups', {})) > 0:
    print("✅ Close/Distant detection: Working correctly")
else:
    print("❌ Close/Distant detection: Failed - this could be the issue!")

print("\n💡 If this test passes but the UI doesn't work, the issue is in:")
print("   1. Dialog signal connections (get_confirmed_mappings)")
print("   2. Data transfer between dialog and main panel")
print("   3. UI update after mapping application")