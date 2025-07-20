"""
Intelligent Auto-Mapping System
Provides advanced sample analysis and automatic mapping with note detection and layering
"""

import os
import re
from collections import defaultdict
from typing import List, Dict, Tuple, Optional
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QTextEdit, QHBoxLayout, QGroupBox, QSpinBox
from PyQt5.QtCore import Qt

class SampleAnalyzer:
    """Advanced sample filename analysis with note detection and classification"""
    
    # Enhanced note patterns for precise detection
    NOTE_PATTERNS = [
        r'([ABCDEFG][#b]?)([0-9]+)',  # Standard: C4, F#3, Bb2
        r'([ABCDEFG])([#b]?)([0-9]+)',  # Separated: C#4, Bb3
        r'([ABCDEFG])(sharp|flat)?([0-9]+)',  # Word form: Csharp4, Bflat3
        r'([ABCDEFG])(s|b)?([0-9]+)',  # Short form: Cs4, Bb3
        r'([ABCDEFG])([0-9]+)',  # Simple: C0, D1, E2 (most common)
    ]
    
    # MIDI note mapping
    NOTE_TO_MIDI = {
        'C': 0, 'C#': 1, 'CS': 1, 'CSHARP': 1, 'DB': 1, 'DFLAT': 1,
        'D': 2, 'D#': 3, 'DS': 3, 'DSHARP': 3, 'EB': 3, 'EFLAT': 3,
        'E': 4, 'F': 5, 'F#': 6, 'FS': 6, 'FSHARP': 6, 'GB': 6, 'GFLAT': 6,
        'G': 7, 'G#': 8, 'GS': 8, 'GSHARP': 8, 'AB': 8, 'AFLAT': 8,
        'A': 9, 'A#': 10, 'AS': 10, 'ASHARP': 10, 'BB': 10, 'BFLAT': 10,
        'B': 11
    }
    
    # Sample variation patterns
    VARIATION_PATTERNS = [
        r'(close|near|dry|direct)',
        r'(distant|far|wet|reverb|room)',
        r'(soft|pp|pianissimo)',
        r'(medium|mp|mezzopiano)',
        r'(loud|ff|fortissimo)',
        r'(muted|mute)',
        r'(open)',
        r'(sustain|sus)',
        r'(staccato|stacc)',
        r'(pizzicato|pizz)',
        r'(tremolo|trem)',
        r'(vibrato|vib)',
        r'(attack|hard)',
        r'(smooth|legato)',
        r'(round|rr)(\d+)',  # Round robin variations
        r'(vel)(\d+)',       # Velocity layers
        r'(layer|lyr)(\d+)', # Layer numbers
        r'(take|tk)(\d+)',   # Different takes
    ]
    
    @classmethod
    def analyze_sample(cls, file_path: str) -> Dict:
        """Analyze a sample file and extract musical information"""
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        analysis = {
            'path': file_path,
            'filename': base_name,
            'detected_note': None,
            'midi_note': None,
            'variations': [],
            'instrument_type': None,
            'velocity_layer': None,
            'round_robin': None,
            'confidence': 0.0
        }
        
        # Detect note
        note_info = cls._detect_note(base_name)
        if note_info:
            analysis['detected_note'] = note_info['note_name']
            analysis['midi_note'] = note_info['midi_note']
            analysis['confidence'] += 0.8
        
        # Detect variations
        variations = cls._detect_variations(base_name)
        analysis['variations'] = variations
        if variations:
            analysis['confidence'] += 0.1
        
        # Detect instrument type
        instrument = cls._detect_instrument_type(base_name)
        analysis['instrument_type'] = instrument
        if instrument:
            analysis['confidence'] += 0.1
        
        return analysis
    
    @classmethod
    def _detect_note(cls, filename: str) -> Optional[Dict]:
        """Detect musical note from filename"""
        filename_upper = filename.upper()
        
        for pattern in cls.NOTE_PATTERNS:
            matches = re.findall(pattern, filename_upper, re.IGNORECASE)
            if matches:
                match = matches[0]
                
                if len(match) == 2:  # (note, octave)
                    note, octave = match
                elif len(match) == 3:  # (note, accidental, octave)
                    note, accidental, octave = match
                    if accidental.upper() in ['#', 'S', 'SHARP']:
                        note = note + '#'
                    elif accidental.upper() in ['B', 'FLAT']:
                        note = note + 'B'
                
                # Convert to MIDI note
                try:
                    octave = int(octave)
                    note_upper = note.upper()
                    if note_upper in cls.NOTE_TO_MIDI:
                        midi_note = cls.NOTE_TO_MIDI[note_upper] + (octave + 1) * 12
                        if 0 <= midi_note <= 127:
                            return {
                                'note_name': f"{note}{octave}",
                                'midi_note': midi_note
                            }
                except (ValueError, KeyError):
                    continue
        return None
    
    @classmethod
    def _detect_variations(cls, filename: str) -> List[str]:
        """Detect sample variations (close/distant, velocity, etc.)"""
        variations = []
        filename_lower = filename.lower()
        
        for pattern in cls.VARIATION_PATTERNS:
            matches = re.findall(pattern, filename_lower)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        variations.append(''.join(match))
                    else:
                        variations.append(match)
        
        return variations
    
    @classmethod
    def _detect_instrument_type(cls, filename: str) -> Optional[str]:
        """Detect instrument type from filename"""
        filename_lower = filename.lower()
        
        instruments = {
            'piano': ['piano', 'key', 'grand', 'upright'],
            'guitar': ['guitar', 'gtr', 'acoustic', 'electric'],
            'violin': ['violin', 'vln', 'string'],
            'cello': ['cello', 'vc'],
            'bass': ['bass', 'contrabass', 'upright'],
            'drums': ['kick', 'snare', 'hat', 'cymbal', 'tom', 'drum'],
            'brass': ['trumpet', 'trombone', 'horn', 'tuba'],
            'woodwinds': ['flute', 'clarinet', 'oboe', 'sax', 'saxophone'],
            'organ': ['organ', 'hammond'],
            'synth': ['synth', 'pad', 'lead', 'arp']
        }
        
        for instrument_type, keywords in instruments.items():
            if any(keyword in filename_lower for keyword in keywords):
                return instrument_type
        
        return None

class SampleGrouper:
    """Groups samples by detected notes and variations for intelligent mapping"""
    
    @classmethod
    def group_samples(cls, analyses: List[Dict]) -> Dict:
        """Group samples by note and create layering suggestions"""
        note_groups = defaultdict(list)
        orphan_samples = []
        
        # Group by detected notes
        for analysis in analyses:
            if analysis['midi_note'] is not None:
                note_groups[analysis['midi_note']].append(analysis)
            else:
                orphan_samples.append(analysis)
        
        # Process groups to detect layering opportunities
        mapping_suggestions = {
            'note_mappings': {},
            'layer_groups': {},
            'range_suggestions': {},
            'orphan_samples': orphan_samples
        }
        
        for midi_note, samples in note_groups.items():
            if len(samples) == 1:
                # Single sample - direct mapping
                sample = samples[0]
                mapping_suggestions['note_mappings'][midi_note] = {
                    'primary_sample': sample,
                    'mapping_type': 'single',
                    'suggested_range': cls._suggest_single_range(midi_note, sample)
                }
            else:
                # Multiple samples - check for layering potential
                layer_analysis = cls._analyze_layering_potential(samples)
                
                if layer_analysis['can_layer']:
                    mapping_suggestions['layer_groups'][midi_note] = {
                        'samples': samples,
                        'layer_type': layer_analysis['layer_type'],
                        'mapping_type': 'layered',
                        'suggested_range': cls._suggest_single_range(midi_note, samples[0])
                    }
                else:
                    # Multiple samples but can't layer - use primary
                    primary = cls._select_primary_sample(samples)
                    mapping_suggestions['note_mappings'][midi_note] = {
                        'primary_sample': primary,
                        'alternatives': [s for s in samples if s != primary],
                        'mapping_type': 'single_with_alternatives',
                        'suggested_range': cls._suggest_single_range(midi_note, primary)
                    }
        
        # Calculate range suggestions for adjacent note mapping
        if note_groups:
            sorted_notes = sorted(note_groups.keys())
            range_suggestions = cls._calculate_range_suggestions(sorted_notes)
            
            # Apply range suggestions to existing mappings
            for midi_note in note_groups:
                if midi_note in range_suggestions:
                    suggestion = range_suggestions[midi_note]
                    if midi_note in mapping_suggestions['note_mappings']:
                        mapping_suggestions['note_mappings'][midi_note]['suggested_range'] = (
                            suggestion['lo'], suggestion['hi'], suggestion['root']
                        )
                    elif midi_note in mapping_suggestions['layer_groups']:
                        mapping_suggestions['layer_groups'][midi_note]['suggested_range'] = (
                            suggestion['lo'], suggestion['hi'], suggestion['root']
                        )
        
        return mapping_suggestions
    
    @classmethod
    def _analyze_layering_potential(cls, samples: List[Dict]) -> Dict:
        """Analyze if samples can be layered together"""
        variations = [s['variations'] for s in samples]
        
        # Check for close/distant pairs
        close_distant = cls._has_close_distant_pair(variations)
        if close_distant:
            return {'can_layer': True, 'layer_type': 'close_distant'}
        
        # Check for velocity layers
        velocity_layers = cls._has_velocity_layers(variations)
        if velocity_layers:
            return {'can_layer': True, 'layer_type': 'velocity'}
        
        # Check for round robin
        round_robin = cls._has_round_robin(variations)
        if round_robin:
            return {'can_layer': True, 'layer_type': 'round_robin'}
        
        # Check for different articulations
        articulations = cls._has_different_articulations(variations)
        if articulations:
            return {'can_layer': True, 'layer_type': 'articulation'}
        
        return {'can_layer': False, 'layer_type': None}
    
    @classmethod
    def _has_close_distant_pair(cls, variations_list: List[List[str]]) -> bool:
        """Check for close/distant sample pairs"""
        has_close = any('close' in var or 'dry' in var or 'direct' in var 
                       for variations in variations_list for var in variations)
        has_distant = any('distant' in var or 'wet' in var or 'reverb' in var or 'room' in var
                         for variations in variations_list for var in variations)
        return has_close and has_distant
    
    @classmethod
    def _has_velocity_layers(cls, variations_list: List[List[str]]) -> bool:
        """Check for velocity layer indicators"""
        velocity_indicators = ['soft', 'pp', 'medium', 'mp', 'loud', 'ff', 'vel']
        return any(any(indicator in var for var in variations) 
                  for variations in variations_list for indicator in velocity_indicators)
    
    @classmethod
    def _has_round_robin(cls, variations_list: List[List[str]]) -> bool:
        """Check for round robin indicators"""
        return any(any('rr' in var or 'round' in var or 'take' in var for var in variations)
                  for variations in variations_list)
    
    @classmethod
    def _has_different_articulations(cls, variations_list: List[List[str]]) -> bool:
        """Check for different articulations"""
        articulations = ['sustain', 'staccato', 'pizzicato', 'tremolo', 'vibrato', 'muted', 'open']
        found_articulations = set()
        
        for variations in variations_list:
            for var in variations:
                for art in articulations:
                    if art in var:
                        found_articulations.add(art)
        
        return len(found_articulations) > 1
    
    @classmethod
    def _select_primary_sample(cls, samples: List[Dict]) -> Dict:
        """Select the primary sample from a group"""
        # Prefer samples with higher confidence
        samples_by_confidence = sorted(samples, key=lambda s: s['confidence'], reverse=True)
        
        # Among high confidence samples, prefer "clean" variations
        clean_variations = ['sustain', 'open', 'medium']
        for sample in samples_by_confidence:
            if any(clean in sample['variations'] for clean in clean_variations):
                return sample
        
        # Fall back to highest confidence
        return samples_by_confidence[0]
    
    @classmethod
    def _suggest_single_range(cls, midi_note: int, sample: Dict) -> Tuple[int, int, int]:
        """Suggest mapping range for a single note sample"""
        # For single note samples, suggest a small range centered on the note
        lo = max(0, midi_note - 1)
        hi = min(127, midi_note + 1)
        root = midi_note
        return lo, hi, root
    
    @classmethod
    def _calculate_range_suggestions(cls, sorted_notes: List[int]) -> Dict:
        """Calculate suggested ranges for adjacent note mapping"""
        if len(sorted_notes) < 2:
            return {}
        
        suggestions = {}
        
        for i, note in enumerate(sorted_notes):
            prev_note = sorted_notes[i-1] if i > 0 else None
            next_note = sorted_notes[i+1] if i < len(sorted_notes) - 1 else None
            
            # Calculate range based on adjacent notes
            if prev_note is None:
                # First note - extend down to start of keyboard
                lo = max(0, note - (next_note - note) // 2) if next_note else 0
            else:
                # Use midpoint between previous and current
                lo = prev_note + (note - prev_note) // 2
            
            if next_note is None:
                # Last note - extend up to end of keyboard
                hi = min(127, note + (note - prev_note) // 2) if prev_note else 127
            else:
                # Use midpoint between current and next
                hi = note + (next_note - note) // 2
            
            suggestions[note] = {
                'lo': lo,
                'hi': hi,
                'root': note,
                'type': 'adjacent_fill'
            }
        
        return suggestions

class IntelligentMappingDialog(QDialog):
    """Dialog for confirming and customizing intelligent mapping suggestions"""
    
    def __init__(self, mapping_suggestions: Dict, parent=None):
        super().__init__(parent)
        self.mapping_suggestions = mapping_suggestions
        self.confirmed_mappings = {}
        self.confirmed_layers = {}
        
        self.setWindowTitle("Intelligent Auto-Mapping")
        self.setModal(True)
        self.resize(800, 600)
        
        self._setup_ui()
        self._populate_suggestions()
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Intelligent Mapping Analysis")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Summary
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(self.summary_label)
        
        # Note mappings section
        note_group = QGroupBox("Detected Note Mappings")
        note_layout = QVBoxLayout()
        
        self.note_table = QTableWidget()
        self.note_table.setColumnCount(5)
        self.note_table.setHorizontalHeaderLabels([
            "Note", "Sample", "Suggested Range", "Action", "Confirm"
        ])
        note_layout.addWidget(self.note_table)
        note_group.setLayout(note_layout)
        layout.addWidget(note_group)
        
        # Layer groups section
        layer_group = QGroupBox("Detected Sample Layers")
        layer_layout = QVBoxLayout()
        
        self.layer_table = QTableWidget()
        self.layer_table.setColumnCount(4)
        self.layer_table.setHorizontalHeaderLabels([
            "Note", "Samples", "Layer Type", "Confirm"
        ])
        layer_layout.addWidget(self.layer_table)
        layer_group.setLayout(layer_layout)
        layout.addWidget(layer_group)
        
        # Options
        options_group = QGroupBox("Mapping Options")
        options_layout = QVBoxLayout()
        
        self.adjacent_fill_cb = QCheckBox("Fill adjacent notes between detected samples")
        self.adjacent_fill_cb.setChecked(True)
        self.adjacent_fill_cb.setToolTip("Automatically map ranges to fill gaps between detected notes")
        options_layout.addWidget(self.adjacent_fill_cb)
        
        self.preserve_existing_cb = QCheckBox("Preserve existing mappings")
        self.preserve_existing_cb.setChecked(True)
        self.preserve_existing_cb.setToolTip("Don't overwrite samples that are already mapped")
        options_layout.addWidget(self.preserve_existing_cb)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        button_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self._select_none)
        button_layout.addWidget(select_none_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("Apply Mappings")
        apply_btn.clicked.connect(self.accept)
        apply_btn.setStyleSheet("background-color: #4a7c59; color: white; font-weight: bold;")
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _populate_suggestions(self):
        """Populate the dialog with mapping suggestions"""
        suggestions = self.mapping_suggestions
        
        # Update summary
        note_count = len(suggestions.get('note_mappings', {}))
        layer_count = len(suggestions.get('layer_groups', {}))
        orphan_count = len(suggestions.get('orphan_samples', []))
        
        summary_text = f"Found {note_count} note mappings, {layer_count} layer groups, {orphan_count} unrecognized samples"
        self.summary_label.setText(summary_text)
        
        # Populate note mappings
        note_mappings = suggestions.get('note_mappings', {})
        self.note_table.setRowCount(len(note_mappings))
        
        for row, (midi_note, mapping_info) in enumerate(note_mappings.items()):
            sample = mapping_info['primary_sample']
            lo, hi, root = mapping_info['suggested_range']
            
            # Note name
            note_name = self._midi_to_note_name(midi_note)
            self.note_table.setItem(row, 0, QTableWidgetItem(note_name))
            
            # Sample filename
            filename = os.path.basename(sample['path'])
            self.note_table.setItem(row, 1, QTableWidgetItem(filename))
            
            # Suggested range
            range_text = f"{self._midi_to_note_name(lo)}-{self._midi_to_note_name(hi)}"
            self.note_table.setItem(row, 2, QTableWidgetItem(range_text))
            
            # Action
            action_text = mapping_info['mapping_type'].replace('_', ' ').title()
            self.note_table.setItem(row, 3, QTableWidgetItem(action_text))
            
            # Confirm checkbox
            confirm_cb = QCheckBox()
            confirm_cb.setChecked(True)
            self.note_table.setCellWidget(row, 4, confirm_cb)
        
        # Populate layer groups
        layer_groups = suggestions.get('layer_groups', {})
        self.layer_table.setRowCount(len(layer_groups))
        
        for row, (midi_note, layer_info) in enumerate(layer_groups.items()):
            samples = layer_info['samples']
            
            # Note name
            note_name = self._midi_to_note_name(midi_note)
            self.layer_table.setItem(row, 0, QTableWidgetItem(note_name))
            
            # Sample list
            sample_names = [os.path.basename(s['path']) for s in samples]
            samples_text = ", ".join(sample_names[:3])
            if len(sample_names) > 3:
                samples_text += f" + {len(sample_names) - 3} more"
            self.layer_table.setItem(row, 1, QTableWidgetItem(samples_text))
            
            # Layer type
            layer_type = layer_info['layer_type'].replace('_', ' ').title()
            self.layer_table.setItem(row, 2, QTableWidgetItem(layer_type))
            
            # Confirm checkbox
            confirm_cb = QCheckBox()
            confirm_cb.setChecked(True)
            self.layer_table.setCellWidget(row, 3, confirm_cb)
        
        # Resize columns
        self.note_table.resizeColumnsToContents()
        self.layer_table.resizeColumnsToContents()
    
    def _select_all(self):
        """Select all mappings"""
        for row in range(self.note_table.rowCount()):
            cb = self.note_table.cellWidget(row, 4)
            if cb:
                cb.setChecked(True)
        
        for row in range(self.layer_table.rowCount()):
            cb = self.layer_table.cellWidget(row, 3)
            if cb:
                cb.setChecked(True)
    
    def _select_none(self):
        """Deselect all mappings"""
        for row in range(self.note_table.rowCount()):
            cb = self.note_table.cellWidget(row, 4)
            if cb:
                cb.setChecked(False)
        
        for row in range(self.layer_table.rowCount()):
            cb = self.layer_table.cellWidget(row, 3)
            if cb:
                cb.setChecked(False)
    
    def get_confirmed_mappings(self) -> Tuple[Dict, Dict, Dict]:
        """Get the confirmed mappings from the dialog"""
        note_mappings = self.mapping_suggestions.get('note_mappings', {})
        layer_groups = self.mapping_suggestions.get('layer_groups', {})
        
        confirmed_notes = {}
        confirmed_layers = {}
        
        # Get confirmed note mappings
        for row in range(self.note_table.rowCount()):
            cb = self.note_table.cellWidget(row, 4)
            if cb and cb.isChecked():
                note_name = self.note_table.item(row, 0).text()
                midi_note = self._note_name_to_midi(note_name)
                if midi_note in note_mappings:
                    confirmed_notes[midi_note] = note_mappings[midi_note]
        
        # Get confirmed layer groups
        for row in range(self.layer_table.rowCount()):
            cb = self.layer_table.cellWidget(row, 3)
            if cb and cb.isChecked():
                note_name = self.layer_table.item(row, 0).text()
                midi_note = self._note_name_to_midi(note_name)
                if midi_note in layer_groups:
                    confirmed_layers[midi_note] = layer_groups[midi_note]
        
        # Get options
        options = {
            'adjacent_fill': self.adjacent_fill_cb.isChecked(),
            'preserve_existing': self.preserve_existing_cb.isChecked()
        }
        
        
        return confirmed_notes, confirmed_layers, options
    
    def _midi_to_note_name(self, midi_note: int) -> str:
        """Convert MIDI note to name"""
        names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (midi_note // 12) - 1
        note = names[midi_note % 12]
        return f"{note}{octave}"
    
    def _note_name_to_midi(self, note_name: str) -> int:
        """Convert note name to MIDI number"""
        # Simple reverse lookup - this could be more robust
        for midi_note in range(128):
            if self._midi_to_note_name(midi_note) == note_name:
                return midi_note
        return 60  # Default to C4