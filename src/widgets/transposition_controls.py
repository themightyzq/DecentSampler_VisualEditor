"""
Transposition Control Widgets for Sample Mapping
Provides UI controls for setting transposition and tuning parameters
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QSpinBox, 
    QDoubleSpinBox, QPushButton, QSlider, QComboBox, QCheckBox, QFrame,
    QFormLayout, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
from utils.audio_transposition import get_transposition_engine, SampleTranspositionWidget

class TranspositionControlWidget(QGroupBox):
    """Widget for controlling sample transposition and tuning"""
    
    transpositionChanged = pyqtSignal(dict)  # Emit transposition parameters
    
    def __init__(self, parent=None):
        super().__init__("🎵 Transposition & Tuning", parent)
        self.current_mapping = None
        self.transposition_engine = get_transposition_engine()
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._update_preview)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Root note section
        root_section = self.create_root_note_section()
        layout.addWidget(root_section)
        
        # Tuning section
        tuning_section = self.create_tuning_section()
        layout.addWidget(tuning_section)
        
        # Preview section
        preview_section = self.create_preview_section()
        layout.addWidget(preview_section)
        
        # Capabilities info
        capabilities_section = self.create_capabilities_section()
        layout.addWidget(capabilities_section)
        
        self.setLayout(layout)
        
        # Apply styling
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #4a9eff;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
    def create_root_note_section(self):
        """Create root note selection controls"""
        section = QGroupBox("Root Note")
        layout = QFormLayout()
        
        # Root note selector
        self.root_note_spin = QSpinBox()
        self.root_note_spin.setRange(0, 127)
        self.root_note_spin.setValue(60)  # C4
        self.root_note_spin.valueChanged.connect(self._on_root_note_changed)
        self.root_note_spin.setToolTip("MIDI note number of the original sample (C4 = 60)")
        
        self.root_note_label = QLabel("C4")
        self.root_note_label.setStyleSheet("font-weight: bold; color: #4a9eff;")
        
        root_layout = QHBoxLayout()
        root_layout.addWidget(self.root_note_spin)
        root_layout.addWidget(self.root_note_label)
        root_layout.addStretch()
        
        layout.addRow("MIDI Note:", root_layout)
        
        # Auto-detect button
        self.auto_detect_btn = QPushButton("Auto-Detect")
        self.auto_detect_btn.clicked.connect(self._auto_detect_root_note)
        self.auto_detect_btn.setToolTip("Attempt to automatically detect the root note from the sample")
        layout.addRow("", self.auto_detect_btn)
        
        section.setLayout(layout)
        return section
        
    def create_tuning_section(self):
        """Create fine-tuning controls"""
        section = QGroupBox("Fine Tuning")
        layout = QFormLayout()
        
        # Cents adjustment
        self.cents_spin = QDoubleSpinBox()
        self.cents_spin.setRange(-1200, 1200)  # ±1 octave in cents
        self.cents_spin.setValue(0)
        self.cents_spin.setDecimals(1)
        self.cents_spin.setSingleStep(1.0)
        self.cents_spin.setSuffix(" cents")
        self.cents_spin.valueChanged.connect(self._on_tuning_changed)
        self.cents_spin.setToolTip("Fine tuning in cents (100 cents = 1 semitone)")
        layout.addRow("Cents:", self.cents_spin)
        
        # Semitone offset (coarse tuning)
        self.semitone_spin = QSpinBox()
        self.semitone_spin.setRange(-24, 24)  # ±2 octaves
        self.semitone_spin.setValue(0)
        self.semitone_spin.valueChanged.connect(self._on_semitone_changed)
        self.semitone_spin.setToolTip("Coarse tuning in semitones")
        layout.addRow("Semitones:", self.semitone_spin)
        
        # Reset button
        self.reset_tuning_btn = QPushButton("Reset")
        self.reset_tuning_btn.clicked.connect(self._reset_tuning)
        layout.addRow("", self.reset_tuning_btn)
        
        section.setLayout(layout)
        return section
        
    def create_preview_section(self):
        """Create transposition preview controls"""
        section = QGroupBox("Transposition Preview")
        layout = QVBoxLayout()
        
        # Preview controls
        preview_layout = QHBoxLayout()
        
        self.preview_note_spin = QSpinBox()
        self.preview_note_spin.setRange(0, 127)
        self.preview_note_spin.setValue(60)
        self.preview_note_spin.valueChanged.connect(self._on_preview_note_changed)
        
        self.preview_note_label = QLabel("C4")
        self.preview_note_label.setStyleSheet("font-weight: bold;")
        
        self.preview_play_btn = QPushButton("▶ Play")
        self.preview_play_btn.clicked.connect(self._play_preview)
        
        preview_layout.addWidget(QLabel("Test Note:"))
        preview_layout.addWidget(self.preview_note_spin)
        preview_layout.addWidget(self.preview_note_label)
        preview_layout.addStretch()
        preview_layout.addWidget(self.preview_play_btn)
        
        layout.addLayout(preview_layout)
        
        # Transposition info display
        self.transposition_info = QLabel("No transposition")
        self.transposition_info.setStyleSheet("padding: 5px; background-color: #333; border-radius: 3px;")
        self.transposition_info.setWordWrap(True)
        layout.addWidget(self.transposition_info)
        
        section.setLayout(layout)
        return section
        
    def create_capabilities_section(self):
        """Create capabilities info section"""
        section = QFrame()
        section.setFrameStyle(QFrame.StyledPanel)
        section.setMaximumHeight(60)
        
        layout = QVBoxLayout()
        
        # Get capabilities
        capabilities = self.transposition_engine.get_capabilities()
        
        # Status label
        self.capabilities_label = QLabel(f"Engine: {capabilities['quality']}")
        self.capabilities_label.setFont(QFont("Arial", 8))
        
        if capabilities['can_transpose']:
            self.capabilities_label.setStyleSheet("color: #51cf66;")  # Green
        else:
            self.capabilities_label.setStyleSheet("color: #ff6b6b;")  # Red
            
        layout.addWidget(self.capabilities_label)
        
        # Recommendations
        if capabilities['recommendations']:
            rec_text = capabilities['recommendations'][0]  # Show first recommendation
            rec_label = QLabel(rec_text)
            rec_label.setFont(QFont("Arial", 7))
            rec_label.setStyleSheet("color: #888;")
            rec_label.setWordWrap(True)
            layout.addWidget(rec_label)
        
        section.setLayout(layout)
        return section
        
    def set_mapping(self, mapping):
        """Set the current mapping to edit"""
        self.current_mapping = mapping
        
        if mapping:
            # Extract current values
            lo, hi, root, path = self._extract_mapping_info(mapping)
            tune_cents = getattr(mapping, 'tune', 0.0)
            
            # Update controls
            self.root_note_spin.setValue(root)
            self.cents_spin.setValue(tune_cents)
            
            # Update preview
            self._update_preview()
        else:
            # Reset to defaults
            self.root_note_spin.setValue(60)
            self.cents_spin.setValue(0.0)
            self.semitone_spin.setValue(0)
            self.transposition_info.setText("No mapping selected")
    
    def _extract_mapping_info(self, mapping):
        """Extract mapping information"""
        if isinstance(mapping, dict):
            lo = mapping.get("lo", 0)
            hi = mapping.get("hi", 127)
            root = mapping.get("root", 60)
            path = mapping.get("path", "")
        else:
            lo = getattr(mapping, "lo", getattr(mapping, "loNote", 0))
            hi = getattr(mapping, "hi", getattr(mapping, "hiNote", 127))
            root = getattr(mapping, "root", getattr(mapping, "rootNote", 60))
            path = getattr(mapping, "path", "")
            
        return lo, hi, root, path
    
    def _on_root_note_changed(self):
        """Handle root note changes"""
        note_num = self.root_note_spin.value()
        note_name = SampleTranspositionWidget.get_note_name(note_num)
        self.root_note_label.setText(note_name)
        
        self._emit_changes()
        self.preview_timer.start(100)  # Delayed preview update
    
    def _on_tuning_changed(self):
        """Handle tuning changes"""
        self._emit_changes()
        self.preview_timer.start(100)
        
    def _on_semitone_changed(self):
        """Handle semitone offset changes"""
        # Convert semitones to cents and update
        semitones = self.semitone_spin.value()
        current_cents = self.cents_spin.value() % 100  # Keep fractional cents
        total_cents = (semitones * 100) + current_cents
        
        self.cents_spin.setValue(total_cents)
        
    def _on_preview_note_changed(self):
        """Handle preview note changes"""
        note_num = self.preview_note_spin.value()
        note_name = SampleTranspositionWidget.get_note_name(note_num)
        self.preview_note_label.setText(note_name)
        
        self.preview_timer.start(100)
        
    def _auto_detect_root_note(self):
        """Attempt to auto-detect root note from filename or other clues"""
        if not self.current_mapping:
            return
            
        lo, hi, root, path = self._extract_mapping_info(self.current_mapping)
        
        # Simple heuristics for auto-detection
        filename = os.path.basename(path).lower()
        
        # Look for note names in filename
        note_map = {
            'c': 0, 'c#': 1, 'db': 1, 'd': 2, 'd#': 3, 'eb': 3, 'e': 4,
            'f': 5, 'f#': 6, 'gb': 6, 'g': 7, 'g#': 8, 'ab': 8, 'a': 9,
            'a#': 10, 'bb': 10, 'b': 11
        }
        
        detected_root = None
        
        # Search for note patterns like "C4", "F#3", etc.
        import re
        pattern = r'([a-g][#b]?)(\d+)'
        matches = re.findall(pattern, filename)
        
        if matches:
            note_name, octave = matches[0]
            if note_name.lower() in note_map:
                note_offset = note_map[note_name.lower()]
                detected_root = (int(octave) + 1) * 12 + note_offset
        
        # Fallback: use middle of range
        if detected_root is None:
            detected_root = (lo + hi) // 2
            
        self.root_note_spin.setValue(detected_root)
        
    def _reset_tuning(self):
        """Reset tuning to default values"""
        self.cents_spin.setValue(0.0)
        self.semitone_spin.setValue(0)
        
    def _play_preview(self):
        """Play preview with current transposition settings"""
        if not self.current_mapping:
            return
            
        lo, hi, root, path = self._extract_mapping_info(self.current_mapping)
        preview_note = self.preview_note_spin.value()
        tune_cents = self.cents_spin.value()
        
        # Use transposition engine
        self.transposition_engine.play_transposed_sample(
            path, preview_note, root, tune_cents, 1.0
        )
        
    def _update_preview(self):
        """Update the transposition preview information"""
        if not self.current_mapping:
            return
            
        root_note = self.root_note_spin.value()
        preview_note = self.preview_note_spin.value()
        tune_cents = self.cents_spin.value()
        
        # Get transposition info
        info = self.transposition_engine.get_transposition_info(
            preview_note, root_note, tune_cents
        )
        
        # Format info text
        if info['direction'] == 'none':
            info_text = "🎵 Original pitch (no transposition)"
        else:
            direction = "↑" if info['direction'] == 'up' else "↓"
            info_text = f"🎵 {direction} {info['semitones']} semitones"
            info_text += f"\\nPitch ratio: {info['pitch_ratio']:.3f}"
            info_text += f"\\nEngine: {info['quality']}"
            
            if abs(info['cents_total']) > 50:
                info_text += f"\\nTotal cents: {info['cents_total']:+.0f}"
        
        self.transposition_info.setText(info_text)
        
    def _emit_changes(self):
        """Emit transposition parameter changes"""
        if not self.current_mapping:
            return
            
        changes = {
            'root_note': self.root_note_spin.value(),
            'tune_cents': self.cents_spin.value()
        }
        
        self.transpositionChanged.emit(changes)
        
    def get_transposition_params(self):
        """Get current transposition parameters"""
        return {
            'root_note': self.root_note_spin.value(),
            'tune_cents': self.cents_spin.value()
        }

class MiniTranspositionWidget(QWidget):
    """Compact transposition widget for inclusion in other panels"""
    
    transpositionChanged = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Root note
        layout.addWidget(QLabel("Root:"))
        self.root_spin = QSpinBox()
        self.root_spin.setRange(0, 127)
        self.root_spin.setValue(60)
        self.root_spin.setMaximumWidth(60)
        self.root_spin.valueChanged.connect(self._emit_changes)
        layout.addWidget(self.root_spin)
        
        # Tune
        layout.addWidget(QLabel("Tune:"))
        self.tune_spin = QDoubleSpinBox()
        self.tune_spin.setRange(-1200, 1200)
        self.tune_spin.setValue(0)
        self.tune_spin.setDecimals(1)
        self.tune_spin.setSuffix("¢")
        self.tune_spin.setMaximumWidth(80)
        self.tune_spin.valueChanged.connect(self._emit_changes)
        layout.addWidget(self.tune_spin)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def set_values(self, root_note, tune_cents):
        """Set transposition values"""
        self.root_spin.setValue(root_note)
        self.tune_spin.setValue(tune_cents)
        
    def get_values(self):
        """Get current values"""
        return {
            'root_note': self.root_spin.value(),
            'tune_cents': self.tune_spin.value()
        }
        
    def _emit_changes(self):
        """Emit changes"""
        self.transpositionChanged.emit(self.get_values())