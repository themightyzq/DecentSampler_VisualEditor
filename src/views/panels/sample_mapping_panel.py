from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QFormLayout, QSpinBox, QFileDialog, QHBoxLayout, QProgressBar, QFrame, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMimeData, QSize
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QPainter, QColor, QBrush, QPen, QIcon
from utils.error_handling import ErrorHandler, with_error_handling
from utils.accessibility import (
    AccessibilityIndicator, AccessibilitySymbol, accessibility_settings,
    get_status_symbol, get_accessible_color
)
from widgets.loading_indicators import LoadingOverlay, ProgressButton, CircularProgress
import os
import re

def midi_note_name(n):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octave = (n // 12) - 1
    note = names[n % 12]
    return f"{note}{octave}"

class SmartFileDetector:
    """Intelligent filename analysis for automatic root note detection"""
    
    # Note name patterns with optional sharps/flats
    NOTE_PATTERNS = [
        r'([ABCDEFG][#b]?)(\d+)',  # Standard notation: C4, F#3, Bb2
        r'([ABCDEFG])([#b]?)(\d+)',  # Separated: C#4, Bb3
        r'_([ABCDEFG][#b]?)(\d+)',  # Underscore prefix: _C4, _F#3
        r'-([ABCDEFG][#b]?)(\d+)',  # Dash prefix: -C4, -F#3
        r'\.([ABCDEFG][#b]?)(\d+)',  # Dot prefix: .C4, .F#3
    ]
    
    # Velocity patterns
    VELOCITY_PATTERNS = [
        (r'_pp', (1, 31)),      # Pianissimo
        (r'_p', (32, 63)),      # Piano
        (r'_mp', (64, 79)),     # Mezzo-piano
        (r'_mf', (80, 95)),     # Mezzo-forte
        (r'_f', (96, 111)),     # Forte
        (r'_ff', (112, 127)),   # Fortissimo
        (r'_soft', (1, 63)),    # Soft
        (r'_medium', (64, 95)), # Medium
        (r'_hard', (96, 127)),  # Hard
        (r'v(\d+)', None),      # Velocity number: v100, v64
    ]
    
    # MIDI note mapping
    NOTE_TO_MIDI = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5,
        'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }
    
    @staticmethod
    def detect_root_note(filename):
        """Detect root note from filename. Returns MIDI note number or None."""
        base_name = os.path.splitext(os.path.basename(filename))[0]
        
        for pattern in SmartFileDetector.NOTE_PATTERNS:
            matches = re.findall(pattern, base_name, re.IGNORECASE)
            if matches:
                match = matches[0]
                if len(match) == 2:  # (note, octave)
                    note, octave = match
                elif len(match) == 3:  # (note, accidental, octave)
                    note, accidental, octave = match
                    note = note + accidental
                
                # Convert to MIDI note
                try:
                    octave = int(octave)
                    note_upper = note.upper()
                    if note_upper in SmartFileDetector.NOTE_TO_MIDI:
                        midi_note = SmartFileDetector.NOTE_TO_MIDI[note_upper] + (octave + 1) * 12
                        if 0 <= midi_note <= 127:
                            return midi_note
                except (ValueError, KeyError):
                    continue
        
        return None
    
    @staticmethod
    def detect_velocity_range(filename):
        """Detect velocity range from filename. Returns (low, high) or None."""
        base_name = os.path.basename(filename)
        
        for pattern, velocity_range in SmartFileDetector.VELOCITY_PATTERNS:
            if pattern.startswith('v'):
                # Handle velocity number pattern
                match = re.search(pattern, base_name, re.IGNORECASE)
                if match:
                    vel = int(match.group(1))
                    # Create a range around the velocity value
                    vel_range = 16  # ±16 velocity units
                    return (max(1, vel - vel_range), min(127, vel + vel_range))
            else:
                # Handle named velocity patterns
                if re.search(pattern, base_name, re.IGNORECASE):
                    return velocity_range
        
        return None  # No velocity information found
    
    @staticmethod
    def suggest_mapping_range(root_note, filename):
        """Suggest appropriate mapping range based on root note and filename."""
        if root_note is None:
            return 60, 60, 60  # Default C4
        
        # Default range: ±6 semitones (half octave)
        range_size = 6
        
        # Instrument-specific range adjustments
        base_name = os.path.basename(filename).lower()
        
        if any(word in base_name for word in ['piano', 'key', 'bell']):
            range_size = 12  # Full octave for keyboard instruments
        elif any(word in base_name for word in ['string', 'violin', 'cello']):
            range_size = 24  # Two octaves for strings
        elif any(word in base_name for word in ['kick', 'snare', 'hat', 'drum', 'perc']):
            range_size = 0   # Single note for drums/percussion
        elif any(word in base_name for word in ['bass', 'low']):
            range_size = 8   # Moderate range for bass
        elif any(word in base_name for word in ['pad', 'synth']):
            range_size = 12  # Full octave for synth sounds
        
        lo_note = max(0, root_note - range_size)
        hi_note = min(127, root_note + range_size)
        
        return lo_note, hi_note, root_note
    
    @staticmethod
    def analyze_sample_group(filenames):
        """Analyze a group of filenames to detect patterns and suggest grouping."""
        # Detect if samples are related (same instrument, different notes/velocities)
        common_prefix = os.path.commonprefix([os.path.basename(f) for f in filenames])
        
        # Group by detected notes
        note_groups = {}
        velocity_groups = {}
        
        for filename in filenames:
            root_note = SmartFileDetector.detect_root_note(filename)
            velocity_range = SmartFileDetector.detect_velocity_range(filename)
            
            if root_note is not None:
                if root_note not in note_groups:
                    note_groups[root_note] = []
                note_groups[root_note].append(filename)
            
            if velocity_range is not None:
                vel_key = f"{velocity_range[0]}-{velocity_range[1]}"
                if vel_key not in velocity_groups:
                    velocity_groups[vel_key] = []
                velocity_groups[vel_key].append(filename)
        
        return {
            'common_prefix': common_prefix,
            'note_groups': note_groups,
            'velocity_groups': velocity_groups,
            'has_velocity_layers': len(velocity_groups) > 1,
            'has_note_layers': len(note_groups) > 1
        }

class BatchImportWorker(QThread):
    """Background worker for batch sample import with progress updates"""
    
    progress_updated = pyqtSignal(int, str)  # progress, status_message
    import_completed = pyqtSignal(list)      # list of sample mappings
    error_occurred = pyqtSignal(str)         # error message
    
    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths
        
    def run(self):
        """Process files in background with progress updates"""
        try:
            mappings = []
            total_files = len(self.file_paths)
            
            # First analyze the group to detect patterns
            group_analysis = SmartFileDetector.analyze_sample_group(self.file_paths)
            
            for i, file_path in enumerate(self.file_paths):
                # Update progress
                progress = int((i / total_files) * 100)
                filename = os.path.basename(file_path)
                self.progress_updated.emit(progress, f"Processing: {filename}")
                
                # Detect root note and velocity
                root_note = SmartFileDetector.detect_root_note(file_path)
                velocity_range = SmartFileDetector.detect_velocity_range(file_path)
                lo_note, hi_note, final_root = SmartFileDetector.suggest_mapping_range(root_note, file_path)
                
                # Create mapping
                mapping = {
                    "path": file_path,
                    "lo": lo_note,
                    "hi": hi_note,
                    "root": final_root,
                    "auto_detected": root_note is not None,
                    "velocity_range": velocity_range if velocity_range else (0, 127),
                    "velocity_detected": velocity_range is not None
                }
                mappings.append(mapping)
                
                # Small delay to prevent UI freezing
                self.msleep(10)
            
            # Add group analysis to results
            self.progress_updated.emit(100, f"Completed: {total_files} files processed")
            self.import_completed.emit(mappings)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class SampleMappingPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.samples = []
        self.current_mapping = None
        self.batch_import_worker = None
        self.error_handler = ErrorHandler(self)
        
        # Accessibility settings
        self.accessibility_enabled = accessibility_settings.colorblind_mode
        self.accessibility_indicator = accessibility_settings.get_indicator_factory()
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Enhanced title with consistent styling
        from utils.ui_consistency import UIStyler
        title = UIStyler.create_header_label(
            "Samples & Mapping", 
            "Import samples: Click Import button, use Auto-Map, or drag & drop files/folders here"
        )
        layout.addWidget(title)
        
        # Drag & drop zone (initially hidden)
        self.drop_zone = QFrame()
        self.drop_zone.setFrameShape(QFrame.StyledPanel)
        self.drop_zone.setStyleSheet("""
            QFrame {
                background: #2a4d3a;
                border: 2px dashed #4a7c59;
                border-radius: 8px;
                margin: 4px;
                min-height: 60px;
            }
        """)
        drop_layout = QVBoxLayout()
        drop_label = QLabel("Drop sample files or folders here")
        drop_label.setAlignment(Qt.AlignCenter)
        drop_label.setStyleSheet("color: #7fa582; font-size: 14px; font-weight: bold;")
        drop_layout.addWidget(drop_label)
        self.drop_zone.setLayout(drop_layout)
        self.drop_zone.setVisible(False)
        layout.addWidget(self.drop_zone)
        
        # Progress bar for batch import (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #666;
                border-radius: 4px;
                text-align: center;
                background: #2a2a2a;
                color: #f0f0f0;
            }
            QProgressBar::chunk {
                background: #4a7c59;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.table_widget = QTableWidget()
        if self.accessibility_enabled:
            self.table_widget.setColumnCount(4)
            self.table_widget.setHorizontalHeaderLabels(["Indicator", "Filename", "Key Range (root)", "Status"])
        else:
            self.table_widget.setColumnCount(3)
            self.table_widget.setHorizontalHeaderLabels(["Filename", "Key Range (root)", "Status"])
        
        self.table_widget.setSelectionBehavior(self.table_widget.SelectRows)
        self.table_widget.setEditTriggers(self.table_widget.NoEditTriggers)
        self.table_widget.setToolTip("List of imported samples. Select to edit mapping.")
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        
        # Set column widths with better sizing for text visibility
        if self.accessibility_enabled:
            self.table_widget.setColumnWidth(0, 60)  # Indicator column - increased
            # Set minimum section sizes to prevent text cutoff
            self.table_widget.horizontalHeader().setMinimumSectionSize(80)
        else:
            # Set minimum section sizes for non-accessibility mode
            self.table_widget.horizontalHeader().setMinimumSectionSize(100)
        
        layout.addWidget(self.table_widget)
        
        # Audio preview widget
        from widgets.audio_preview import AudioPreviewWidget
        self.audio_preview = AudioPreviewWidget()
        layout.addWidget(self.audio_preview)

        # Dedicated zone mapping panel (always present, shown/hidden)
        from PyQt5.QtWidgets import QGridLayout, QSizePolicy
        self.zone_panel = QFrame()
        self.zone_panel.setFrameShape(QFrame.StyledPanel)
        self.zone_panel.setStyleSheet("""
            QFrame {
                background: #232323;
                border: 1px solid #666;
                border-radius: 6px;
                margin-top: 8px;
            }
            QLabel {
                color: #f0f0f0;
                font-size: 14px;
                font-weight: 600;
                min-width: 85px;
                padding-right: 8px;
            }
            QSpinBox {
                color: #f0f0f0;
                font-size: 14px;
                min-width: 80px;
                min-height: 28px;
                background: #181818;
                border: 1px solid #444;
                border-radius: 4px;
                selection-background-color: #444;
                selection-color: #fff;
                padding: 2px 8px;
            }
        """)
        self.zone_panel.setContentsMargins(0, 0, 0, 0)
        self.zone_panel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        grid = QGridLayout()
        grid.setContentsMargins(16, 12, 16, 12)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(16)

        self.lo_label = QLabel("Low Note")
        self.lo_spin = QSpinBox()
        self.lo_spin.setRange(0, 127)
        self.lo_spin.setToolTip("Low MIDI note (0–127)")
        self.lo_spin.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.lo_label, 0, 0, alignment=Qt.AlignVCenter | Qt.AlignLeft)
        grid.addWidget(self.lo_spin, 0, 1, alignment=Qt.AlignVCenter | Qt.AlignRight)

        self.hi_label = QLabel("High Note")
        self.hi_spin = QSpinBox()
        self.hi_spin.setRange(0, 127)
        self.hi_spin.setToolTip("High MIDI note (0–127)")
        self.hi_spin.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.hi_label, 1, 0, alignment=Qt.AlignVCenter | Qt.AlignLeft)
        grid.addWidget(self.hi_spin, 1, 1, alignment=Qt.AlignVCenter | Qt.AlignRight)

        self.root_label = QLabel("Root Note")
        self.root_spin = QSpinBox()
        self.root_spin.setRange(0, 127)
        self.root_spin.setToolTip("Root MIDI note (0–127)")
        self.root_spin.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.root_label, 2, 0, alignment=Qt.AlignVCenter | Qt.AlignLeft)
        grid.addWidget(self.root_spin, 2, 1, alignment=Qt.AlignVCenter | Qt.AlignRight)

        self.zone_panel.setLayout(grid)
        self.zone_panel.setVisible(False)
        layout.addWidget(self.zone_panel)

        # Connect spin boxes to mapping update
        self.lo_spin.valueChanged.connect(self.on_mapping_changed)
        self.hi_spin.valueChanged.connect(self.on_mapping_changed)
        self.root_spin.valueChanged.connect(self.on_mapping_changed)

        # Enhanced import buttons with batch support
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(8)
        
        # Add button styling to prevent text cutoff - enhanced sizing
        self.button_style = """
            QPushButton {
                min-height: 38px;
                min-width: 120px;
                padding: 8px 18px;
                font-size: 14px;
                font-weight: 500;
                text-align: center;
            }
        """
        
        import_btn = QPushButton("Import Files")
        import_btn.setToolTip("Import individual sample files (WAV, AIFF, FLAC)")
        import_btn.clicked.connect(self.import_samples)
        import_btn.setStyleSheet(self.button_style)
        btn_layout.addWidget(import_btn)
        
        batch_btn = QPushButton("Import Folder")
        batch_btn.setToolTip("Import all audio files from a folder with smart detection")
        batch_btn.clicked.connect(self.import_folder)
        batch_btn.setStyleSheet(self.button_style)
        btn_layout.addWidget(batch_btn)
        
        auto_map_btn = QPushButton("Auto-Map")
        auto_map_btn.setToolTip(
            "Intelligent auto-mapping with note detection:\n"
            "• Detects notes from filenames (C4, F#3, etc.)\n"
            "• Maps samples to detected notes\n"
            "• Fills adjacent keys between samples\n"
            "• Groups sample variations for layering"
        )
        auto_map_btn.clicked.connect(self.auto_map_folder)
        auto_map_btn.setStyleSheet(self.button_style)
        btn_layout.addWidget(auto_map_btn)
        
        # Visual mapping controls
        self.visual_map_btn = QPushButton("Visual Map")
        self.visual_map_btn.setToolTip("Enable visual mapping mode - click and drag on piano keyboard to set ranges")
        self.visual_map_btn.setCheckable(True)
        self.visual_map_btn.clicked.connect(self._toggle_visual_mapping)
        self.visual_map_btn.setStyleSheet(self.button_style)
        btn_layout.addWidget(self.visual_map_btn)
        
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.table_widget.selectionModel().selectionChanged.connect(self.on_table_selection_changed)
        
        # Visual mapping connection will be established in main window after all components are created
        
        # Show helpful hint after a short delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, self._show_import_hint)
    
    def _toggle_visual_mapping(self, checked):
        """Toggle visual mapping mode"""
        if hasattr(self.main_window, 'piano_keyboard'):
            self.main_window.piano_keyboard.set_mapping_mode(checked)
            
            if checked:
                self.visual_map_btn.setText("Exit Visual Map")
                self.visual_map_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4a7c59;
                        color: white;
                        min-height: 38px;
                        min-width: 140px;
                        padding: 8px 18px;
                        font-size: 14px;
                        font-weight: 500;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #5a8c69;
                    }
                """)
                
                # Show helpful status message
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage(
                        "Visual Mapping: Select a sample, then click and drag on the piano keyboard to set its range",
                        0  # Keep message until replaced
                    )
            else:
                self.visual_map_btn.setText("Visual Map")
                self.visual_map_btn.setStyleSheet(self.button_style)
                self.main_window.piano_keyboard.clear_range_selection()
                
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().clearMessage()
    
    def _on_range_selected(self, start_note, end_note):
        """Handle range selection from the piano keyboard"""
        # Check if a sample is selected
        indexes = self.table_widget.selectionModel().selectedRows()
        if not indexes:
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(
                    "Please select a sample first, then drag on the keyboard to set its range", 3000
                )
            return
        
        # Update the selected sample's range
        idx = indexes[0].row()
        if idx < 0 or idx >= len(self.samples):
            return
        
        mapping = self.samples[idx]
        
        # Suggest a root note (middle of the range)
        suggested_root = start_note + (end_note - start_note) // 2
        
        # Update the mapping
        if isinstance(mapping, dict):
            mapping["lo"] = start_note
            mapping["hi"] = end_note
            mapping["root"] = suggested_root
            mapping["auto_detected"] = False
        else:
            setattr(mapping, "lo", start_note)
            setattr(mapping, "hi", end_note) 
            setattr(mapping, "root", suggested_root)
            setattr(mapping, "auto_detected", False)
        
        # Update the UI
        self.set_samples(self.samples)
        
        # Select the same row again
        self.table_widget.selectRow(idx)
        
        # Update the live preview
        if hasattr(self.main_window, "preview_canvas") and hasattr(self.main_window, "preset"):
            self.main_window.preview_canvas.set_preset(self.main_window.preset, "")
        
        # Show success message
        if hasattr(self.main_window, 'statusBar'):
            note_range = f"{self.midi_note_name(start_note)}-{self.midi_note_name(end_note)}"
            filename = mapping.get("path", "").split("/")[-1] if isinstance(mapping, dict) else getattr(mapping, "path", "").split("/")[-1]
            self.main_window.statusBar().showMessage(
                f"Mapped '{filename}' to range {note_range} (root: {self.midi_note_name(suggested_root)})", 3000
            )
    
    @staticmethod
    def midi_note_name(n):
        """Convert MIDI note number to name"""
        names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (n // 12) - 1
        note = names[n % 12]
        return f"{note}{octave}"
    
    def _create_mapping_indicator_icon(self, mapping_index):
        """Create a visual indicator icon for a mapping"""
        if not self.accessibility_enabled:
            return None
        
        # Create a small pixmap with pattern and symbol
        pixmap = QPixmap(32, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get accessibility indicator components
        color, brush, symbol = self.accessibility_indicator.create_mapping_indicator(mapping_index)
        
        # Draw pattern background
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRect(pixmap.rect())
        
        # Draw symbol if available
        if symbol:
            painter.setPen(QPen(QColor("#FFFFFF"), 1))
            font = painter.font()
            font.setPixelSize(12)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, symbol)
        
        painter.end()
        return QIcon(pixmap)
    
    def _extract_mapping_info(self, mapping):
        """Extract lo, hi, root, path from mapping object or dict"""
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
    
    # Drag and Drop Event Handlers
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            # Check if any URLs are valid audio files or directories
            valid_files = False
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isdir(path) or self._is_audio_file(path):
                    valid_files = True
                    break
            
            if valid_files:
                event.acceptProposedAction()
                self.drop_zone.setVisible(True)
                self.drop_zone.setStyleSheet("""
                    QFrame {
                        background: #3a5d4a;
                        border: 2px dashed #6a9c79;
                        border-radius: 8px;
                        margin: 4px;
                        min-height: 60px;
                    }
                """)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Handle drag leave events"""
        self.drop_zone.setVisible(False)

    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        self.drop_zone.setVisible(False)
        
        if event.mimeData().hasUrls():
            file_paths = []
            folder_paths = []
            unsupported_files = []
            
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isfile(path):
                    if self._is_audio_file(path):
                        file_paths.append(path)
                    else:
                        unsupported_files.append(os.path.basename(path))
                elif os.path.isdir(path):
                    folder_paths.append(path)
            
            # Process folders first
            for folder_path in folder_paths:
                folder_files = self._get_audio_files_from_folder(folder_path)
                file_paths.extend(folder_files)
            
            if file_paths:
                # Show feedback about unsupported files if any
                if unsupported_files and hasattr(self.main_window, 'statusBar'):
                    if len(unsupported_files) <= 3:
                        unsupported_text = ", ".join(unsupported_files)
                    else:
                        unsupported_text = f"{', '.join(unsupported_files[:3])} + {len(unsupported_files) - 3} more"
                    
                    self.main_window.statusBar().showMessage(
                        f"Importing {len(file_paths)} audio files. Skipped unsupported: {unsupported_text}",
                        5000
                    )
                
                self._start_batch_import(file_paths)
                event.acceptProposedAction()
            else:
                # No valid files found
                if hasattr(self.main_window, 'statusBar'):
                    if unsupported_files:
                        self.main_window.statusBar().showMessage(
                            f"No supported audio files found. Supported formats: WAV, AIFF, FLAC, OGG",
                            5000
                        )
                    else:
                        self.main_window.statusBar().showMessage(
                            "No audio files found in dropped items",
                            3000
                        )
                event.ignore()

    def _is_audio_file(self, file_path):
        """Check if file is a supported audio format"""
        extensions = ['.wav', '.aiff', '.aif', '.flac', '.ogg', '.mp3']
        return any(file_path.lower().endswith(ext) for ext in extensions)

    def _get_audio_files_from_folder(self, folder_path):
        """Get all audio files from a folder recursively"""
        audio_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_audio_file(file_path):
                    audio_files.append(file_path)
        
        # Sort files naturally (handle numeric sequences properly)
        def natural_sort_key(path):
            import re
            def convert(text):
                return int(text) if text.isdigit() else text.lower()
            return [convert(c) for c in re.split('([0-9]+)', os.path.basename(path))]
        
        audio_files.sort(key=natural_sort_key)
        return audio_files

    def _start_batch_import(self, file_paths):
        """Start batch import process with progress tracking"""
        if self.batch_import_worker and self.batch_import_worker.isRunning():
            return  # Already running
        
        # Show loading overlay for large batches
        if len(file_paths) > 10:
            self.loading_overlay.showWithText(f"Importing {len(file_paths)} files...")
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Disable UI elements during import
        self.table_widget.setEnabled(False)
        for child in self.findChildren(QPushButton):
            child.setEnabled(False)
        
        # Create and start worker thread
        self.batch_import_worker = BatchImportWorker(file_paths)
        self.batch_import_worker.progress_updated.connect(self._on_import_progress)
        self.batch_import_worker.import_completed.connect(self._on_import_completed)
        self.batch_import_worker.error_occurred.connect(self._on_import_error)
        self.batch_import_worker.start()
    
    def _on_import_progress(self, progress, message):
        """Handle import progress updates"""
        self.progress_bar.setValue(progress)
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(message)
    
    def _on_import_completed(self, mappings):
        """Handle completed batch import"""
        # Hide loading indicators
        self.progress_bar.setVisible(False)
        self.loading_overlay.hide()
        
        # Re-enable UI elements
        self.table_widget.setEnabled(True)
        for child in self.findChildren(QPushButton):
            child.setEnabled(True)
        
        # Add new mappings to existing samples
        for mapping in mappings:
            self.samples.append(mapping)
        
        # Refresh the table
        self.set_samples(self.samples)
        
        # Show results
        auto_detected = sum(1 for m in mappings if m.get('auto_detected', False))
        total = len(mappings)
        
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(
                f"Imported {total} samples. Auto-detected {auto_detected} root notes.", 3000
            )
        
        # Offer intelligent mapping if multiple samples were imported
        if total > 1:
            self._offer_intelligent_mapping()
    
    def _on_import_error(self, error_message):
        """Handle import errors"""
        # Hide loading indicators
        self.progress_bar.setVisible(False)
        self.loading_overlay.hide()
        
        # Re-enable UI elements
        self.table_widget.setEnabled(True)
        for child in self.findChildren(QPushButton):
            child.setEnabled(True)
        
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(f"Import error: {error_message}", 5000)
    
    def _offer_intelligent_mapping(self):
        """Offer intelligent mapping after successful import"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self,
                "Intelligent Auto-Mapping",
                "Would you like to analyze the imported samples for automatic note detection and mapping?\n\n"
                "This will:\n"
                "• Detect notes from filenames (C4, F#3, etc.)\n" 
                "• Map samples to their detected notes\n"
                "• Fill adjacent keys between samples\n"
                "• Detect sample variations for layering\n\n"
                "You can review and customize the suggestions before applying.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Small delay to let the UI update
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(100, self._perform_intelligent_mapping)
                
        except Exception as e:
            self.error_handler.handle_error(
                e,
                "analyzing samples for intelligent mapping",
                show_dialog=True
            )

    def set_samples(self, samples):
        # Always store SampleMapping objects for bulletproof consistency
        from model import SampleMapping
        self.samples = []
        self.table_widget.setRowCount(0)
        for m in samples:
            if isinstance(m, dict):
                path = m.get("path", "")
                lo = m.get("lo", 0)
                hi = m.get("hi", 0)
                root = m.get("root", 0)
                auto_detected = m.get("auto_detected", False)
                mapping_obj = SampleMapping(path, lo, hi, root)
                # Store detection status for display
                setattr(mapping_obj, 'auto_detected', auto_detected)
            else:
                path = getattr(m, "path", str(m))
                lo = getattr(m, "lo", 0)
                hi = getattr(m, "hi", 0)
                root = getattr(m, "root", 0)
                auto_detected = getattr(m, "auto_detected", False)
                mapping_obj = m
                
            self.samples.append(mapping_obj)
            filename = path.split("/")[-1] if path else ""
            key_range = f"{midi_note_name(lo)}–{midi_note_name(hi)} (root {midi_note_name(root)})"
            
            # Status indicator with accessibility symbols
            if hasattr(mapping_obj, 'auto_detected') and mapping_obj.auto_detected:
                if self.accessibility_enabled:
                    status_symbol = get_status_symbol("success")
                    status = f"{status_symbol} Auto-detected"
                else:
                    status = "✓ Auto-detected"
            else:
                status = "Manual"
            
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)
            
            if self.accessibility_enabled:
                # Add visual indicator in first column
                indicator_icon = self._create_mapping_indicator_icon(len(self.samples) - 1)
                indicator_item = QTableWidgetItem()
                if indicator_icon:
                    indicator_item.setIcon(indicator_icon)
                self.table_widget.setItem(row, 0, indicator_item)
                
                # Shift other columns
                self.table_widget.setItem(row, 1, QTableWidgetItem(filename))
                self.table_widget.setItem(row, 2, QTableWidgetItem(key_range))
                self.table_widget.setItem(row, 3, QTableWidgetItem(status))
            else:
                self.table_widget.setItem(row, 0, QTableWidgetItem(filename))
                self.table_widget.setItem(row, 1, QTableWidgetItem(key_range))
                self.table_widget.setItem(row, 2, QTableWidgetItem(status))
            
            self.table_widget.setRowHeight(row, 28 if self.accessibility_enabled else 24)
        self.set_mapping(None)

    def set_mapping(self, mapping):
        self.current_mapping = mapping
        if mapping is None:
            self.zone_panel.setVisible(False)
            return
        if isinstance(mapping, dict):
            lo = mapping.get("lo", 0)
            hi = mapping.get("hi", 127)
            root = mapping.get("root", 60)
        else:
            lo = getattr(mapping, "lo", 0)
            hi = getattr(mapping, "hi", 127)
            root = getattr(mapping, "root", 60)
        self.lo_spin.blockSignals(True)
        self.hi_spin.blockSignals(True)
        self.root_spin.blockSignals(True)
        self.lo_spin.setValue(lo)
        self.hi_spin.setValue(hi)
        self.root_spin.setValue(root)
        self.lo_spin.blockSignals(False)
        self.hi_spin.blockSignals(False)
        self.root_spin.blockSignals(False)
        self.zone_panel.setVisible(True)

    def on_table_selection_changed(self, selected, deselected):
        indexes = self.table_widget.selectionModel().selectedRows()
        if indexes:
            idx = indexes[0].row()
            if idx < 0 or idx >= len(self.samples):
                self.set_mapping(None)
                self.audio_preview._clear()
                return
            mapping = self.samples[idx]
            self.set_mapping(mapping)
            
            # Load audio preview
            if isinstance(mapping, dict):
                file_path = mapping.get("path", "")
            else:
                file_path = getattr(mapping, "path", "")
            
            if file_path and os.path.exists(file_path):
                self.audio_preview.load_file(file_path)
            else:
                self.audio_preview._clear()
            
            # Show the selected sample's range on the keyboard
            if hasattr(self.main_window, 'piano_keyboard'):
                lo, hi, root, _ = self._extract_mapping_info(mapping)
                self.main_window.piano_keyboard.set_highlight_range(lo, hi)
        else:
            self.set_mapping(None)
            self.audio_preview._clear()

    def on_mapping_changed(self):
        indexes = self.table_widget.selectionModel().selectedRows()
        if indexes:
            idx = indexes[0].row()
            mapping = self.samples[idx]
            lo = self.lo_spin.value()
            hi = self.hi_spin.value()
            root = self.root_spin.value()
            if isinstance(mapping, dict):
                mapping["lo"] = lo
                mapping["hi"] = hi
                mapping["root"] = root
                # Mark as manually modified
                mapping["auto_detected"] = False
                filename = mapping["path"].split("/")[-1] if mapping["path"] else ""
                key_range = f"{midi_note_name(mapping['lo'])}–{midi_note_name(mapping['hi'])} (root {midi_note_name(mapping['root'])})"
                status = "Manual"
            else:
                setattr(mapping, "lo", lo)
                setattr(mapping, "hi", hi)
                setattr(mapping, "root", root)
                # Mark as manually modified
                setattr(mapping, "auto_detected", False)
                path = getattr(mapping, "path", "")
                filename = path.split("/")[-1] if path else ""
                key_range = f"{midi_note_name(lo)}–{midi_note_name(hi)} (root {midi_note_name(root)})"
                status = "Manual"
            
            # Update table items considering accessibility columns
            if self.accessibility_enabled:
                # Update indicator icon
                indicator_icon = self._create_mapping_indicator_icon(idx)
                indicator_item = self.table_widget.item(idx, 0)
                if indicator_item and indicator_icon:
                    indicator_item.setIcon(indicator_icon)
                
                self.table_widget.setItem(idx, 1, QTableWidgetItem(filename))
                self.table_widget.setItem(idx, 2, QTableWidgetItem(key_range))
                self.table_widget.setItem(idx, 3, QTableWidgetItem(status))
            else:
                self.table_widget.setItem(idx, 0, QTableWidgetItem(filename))
                self.table_widget.setItem(idx, 1, QTableWidgetItem(key_range))
                self.table_widget.setItem(idx, 2, QTableWidgetItem(status))
            # Live update preview
            if hasattr(self.main_window, "preview_canvas") and hasattr(self.main_window, "preset"):
                self.main_window.preview_canvas.set_preset(self.main_window.preset, "")

        else:
            self.zone_panel.setVisible(False)

    def import_samples(self):
        """Import individual sample files with smart detection"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Import Sample Files", 
            "", 
            "Audio Files (*.wav *.aiff *.aif *.flac *.ogg);;WAV Files (*.wav);;AIFF Files (*.aiff *.aif);;FLAC Files (*.flac);;All Files (*)"
        )
        if files:
            self._start_batch_import(files)

    def import_folder(self):
        """Import all audio files from a selected folder"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Sample Folder",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            audio_files = self._get_audio_files_from_folder(folder)
            if audio_files:
                self._start_batch_import(audio_files)
            else:
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage("No audio files found in selected folder", 3000)

    def auto_map_folder(self):
        """Intelligent auto-mapping with note detection and layering"""
        if not self.samples:
            folder = QFileDialog.getExistingDirectory(self, "Select Sample Folder")
            if folder:
                audio_files = self._get_audio_files_from_folder(folder)
                if audio_files:
                    self._start_batch_import(audio_files)
                    # Wait for import to complete, then trigger intelligent mapping
                    # This will be handled by the import completion callback
                    return
                else:
                    if hasattr(self.main_window, 'statusBar'):
                        self.main_window.statusBar().showMessage("No audio files found in selected folder", 3000)
                    return
        
        # Perform intelligent mapping on current samples
        self._perform_intelligent_mapping()
    
    def _perform_intelligent_mapping(self):
        """Perform intelligent mapping analysis on current samples"""
        if not self.samples:
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage("No samples to analyze. Import samples first.", 3000)
            return
        
        try:
            from utils.intelligent_mapping import SampleAnalyzer, SampleGrouper, IntelligentMappingDialog
            
            # Show loading overlay for analysis
            self.loading_overlay.showWithText(f"Analyzing {len(self.samples)} samples...")
            
            # Disable UI during analysis
            self.table_widget.setEnabled(False)
            for child in self.findChildren(QPushButton):
                child.setEnabled(False)
            
            # Process events to show overlay immediately
            QApplication.processEvents()
            
            # Analyze all samples
            analyses = []
            for i, sample in enumerate(self.samples):
                if isinstance(sample, dict):
                    file_path = sample.get("path", "")
                else:
                    file_path = getattr(sample, "path", "")
                
                # Update overlay text with progress
                if i % 5 == 0:  # Update every 5 files
                    self.loading_overlay.label.setText(f"Analyzing sample {i+1} of {len(self.samples)}...")
                    QApplication.processEvents()
                
                if file_path:
                    analysis = SampleAnalyzer.analyze_sample(file_path)
                    analyses.append(analysis)
            
            # Hide overlay before showing dialog
            self.loading_overlay.hide()
            
            # Re-enable UI
            self.table_widget.setEnabled(True)
            for child in self.findChildren(QPushButton):
                child.setEnabled(True)
            
            if not analyses:
                if hasattr(self.main_window, 'statusBar'):
                    self.main_window.statusBar().showMessage("No valid samples to analyze", 3000)
                return
            
            # Group samples and generate suggestions
            mapping_suggestions = SampleGrouper.group_samples(analyses)
            
            # Clear status
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().clearMessage()
            
            # Show confirmation dialog
            dialog = IntelligentMappingDialog(mapping_suggestions, self)
            
            if dialog.exec_() == dialog.Accepted:
                confirmed_notes, confirmed_layers, options = dialog.get_confirmed_mappings()
                self._apply_intelligent_mappings(confirmed_notes, confirmed_layers, options)
                
        except Exception as e:
            # Hide overlay on error
            self.loading_overlay.hide()
            
            # Re-enable UI
            self.table_widget.setEnabled(True)
            for child in self.findChildren(QPushButton):
                child.setEnabled(True)
            
            self.error_handler.handle_error(
                e,
                "creating intelligent mappings",
                show_dialog=True
            )
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"Intelligent mapping error: {str(e)}", 5000)
    
    def _apply_intelligent_mappings(self, note_mappings: dict, layer_groups: dict, options: dict):
        """Apply confirmed intelligent mappings"""
        try:
            
            applied_count = 0
            layered_count = 0
            
            # Create a mapping from file paths to sample objects
            path_to_sample = {}
            for i, sample in enumerate(self.samples):
                if isinstance(sample, dict):
                    path = sample.get("path", "")
                else:
                    path = getattr(sample, "path", "")
                if path:
                    path_to_sample[path] = (sample, i)
            
            # Apply single note mappings
            for midi_note, mapping_info in note_mappings.items():
                sample_analysis = mapping_info['primary_sample']
                sample_path = sample_analysis['path']
                
                if sample_path in path_to_sample:
                    sample, sample_index = path_to_sample[sample_path]
                    lo, hi, root = mapping_info['suggested_range']
                    
                    # The suggested_range already includes adjacent fill calculations
                    # No additional processing needed here
                    
                    # Update the sample
                    if isinstance(sample, dict):
                        sample["lo"] = lo
                        sample["hi"] = hi
                        sample["root"] = root
                        sample["auto_detected"] = True
                    else:
                        setattr(sample, "lo", lo)
                        setattr(sample, "hi", hi)
                        setattr(sample, "root", root)
                        setattr(sample, "auto_detected", True)
                    
                    applied_count += 1
            
            # Apply layer groups - map ALL samples in each group
            for midi_note, layer_info in layer_groups.items():
                lo, hi, root = layer_info['suggested_range']
                
                # Map ALL samples in the layer group to the same range
                for sample_analysis in layer_info['samples']:
                    sample_path = sample_analysis['path']
                    
                    if sample_path in path_to_sample:
                        sample, sample_index = path_to_sample[sample_path]
                        
                        # Update the sample
                        if isinstance(sample, dict):
                            sample["lo"] = lo
                            sample["hi"] = hi
                            sample["root"] = root
                            sample["auto_detected"] = True
                        else:
                            setattr(sample, "lo", lo)
                            setattr(sample, "hi", hi)
                            setattr(sample, "root", root)
                            setattr(sample, "auto_detected", True)
                        
                        layered_count += 1
            
            # Update the UI
            self.set_samples(self.samples)
            
            # CRITICAL: Update the main preset object with the new mappings
            if hasattr(self.main_window, "preset"):
                
                # Convert our samples back to the main preset format
                from model import SampleMapping
                preset_mappings = []
                for i, sample in enumerate(self.samples):
                    if isinstance(sample, dict):
                        path = sample.get("path", "")
                        lo = sample.get("lo", 0)
                        hi = sample.get("hi", 127)
                        root = sample.get("root", 60)
                        mapping = SampleMapping(path, lo, hi, root)
                    else:
                        # Handle SampleMapping objects
                        lo = getattr(sample, "lo", 0)
                        hi = getattr(sample, "hi", 127)  
                        root = getattr(sample, "root", 60)
                        path = getattr(sample, "path", "")
                        mapping = sample
                    preset_mappings.append(mapping)
                
                old_count = len(getattr(self.main_window.preset, 'mappings', []))
                self.main_window.preset.mappings = preset_mappings
                new_count = len(self.main_window.preset.mappings)
            
            # Update live preview
            if hasattr(self.main_window, "preview_canvas") and hasattr(self.main_window, "preset"):
                self.main_window.preview_canvas.set_preset(self.main_window.preset, "")
            
            # Show results
            if hasattr(self.main_window, 'statusBar'):
                total_applied = applied_count + layered_count
                self.main_window.statusBar().showMessage(
                    f"Applied intelligent mapping: {applied_count} note mappings, {layered_count} layer groups", 3000
                )
                
        except Exception as e:
            self.error_handler.handle_error(
                e,
                "applying intelligent mappings",
                show_dialog=True
            )
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"Error applying mappings: {str(e)}", 5000)
    
    def _show_import_hint(self):
        """Show helpful hint about new import features"""
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(
                "💡 Tip: Drag & drop sample folders here! Auto-detects root notes from filenames (C4, F#3, etc.) and velocity layers (_pp, _f, _hard)",
                10000  # Show for 10 seconds
            )
