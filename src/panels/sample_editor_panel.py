from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QSpinBox, 
    QDoubleSpinBox, QComboBox, QCheckBox, QPushButton, QFormLayout, 
    QScrollArea, QFrame, QTabWidget, QSlider, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPalette
from model import SampleZone

class SampleZoneEditor(QGroupBox):
    """Enhanced sample zone editor with advanced features"""
    zoneChanged = pyqtSignal()
    
    def __init__(self, zone=None, parent=None):
        super().__init__("Sample Properties", parent)
        self.zone = zone
        self.init_ui()
        if self.zone:
            self.update_from_zone()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tab widget for different property categories
        tabs = QTabWidget()
        
        # Basic Properties Tab
        basic_tab = QWidget()
        self.init_basic_tab(basic_tab)
        tabs.addTab(basic_tab, "Basic")
        
        # Round-Robin/Sequencing Tab
        seq_tab = QWidget()
        self.init_sequence_tab(seq_tab)
        tabs.addTab(seq_tab, "Sequencing")
        
        # Loop Properties Tab
        loop_tab = QWidget()
        self.init_loop_tab(loop_tab)
        tabs.addTab(loop_tab, "Looping")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
    def init_basic_tab(self, tab):
        layout = QFormLayout()
        
        # File path (read-only)
        self.path_label = QLabel("No file selected")
        self.path_label.setStyleSheet("QLabel { color: gray; }")
        layout.addRow("File:", self.path_label)
        
        # Key range
        self.root_note_spin = QSpinBox()
        self.root_note_spin.setRange(0, 127)
        self.root_note_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Root Note:", self.root_note_spin)
        
        self.lo_note_spin = QSpinBox()
        self.lo_note_spin.setRange(0, 127)
        self.lo_note_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Low Note:", self.lo_note_spin)
        
        self.hi_note_spin = QSpinBox()
        self.hi_note_spin.setRange(0, 127)
        self.hi_note_spin.valueChanged.connect(self.on_changed)
        layout.addRow("High Note:", self.hi_note_spin)
        
        # Velocity range
        velocity_layout = QHBoxLayout()
        self.vel_low_spin = QSpinBox()
        self.vel_low_spin.setRange(0, 127)
        self.vel_low_spin.valueChanged.connect(self.on_changed)
        velocity_layout.addWidget(self.vel_low_spin)
        
        velocity_layout.addWidget(QLabel("to"))
        
        self.vel_high_spin = QSpinBox()
        self.vel_high_spin.setRange(0, 127)
        self.vel_high_spin.valueChanged.connect(self.on_changed)
        velocity_layout.addWidget(self.vel_high_spin)
        
        velocity_widget = QWidget()
        velocity_widget.setLayout(velocity_layout)
        layout.addRow("Velocity Range:", velocity_widget)
        
        # Volume offset
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(-60.0, 20.0)
        self.volume_spin.setSingleStep(0.1)
        self.volume_spin.setDecimals(1)
        self.volume_spin.setSuffix(" dB")
        self.volume_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Volume Offset:", self.volume_spin)
        
        # Pan
        self.pan_spin = QDoubleSpinBox()
        self.pan_spin.setRange(-1.0, 1.0)
        self.pan_spin.setSingleStep(0.1)
        self.pan_spin.setDecimals(2)
        self.pan_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Pan:", self.pan_spin)
        
        # Tune offset
        self.tune_spin = QDoubleSpinBox()
        self.tune_spin.setRange(-1200.0, 1200.0)
        self.tune_spin.setSingleStep(1.0)
        self.tune_spin.setDecimals(0)
        self.tune_spin.setSuffix(" cents")
        self.tune_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Tune Offset:", self.tune_spin)
        
        # Sample range
        self.start_spin = QSpinBox()
        self.start_spin.setRange(0, 999999999)
        self.start_spin.setSuffix(" samples")
        self.start_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Start Offset:", self.start_spin)
        
        self.end_spin = QSpinBox()
        self.end_spin.setRange(0, 999999999)
        self.end_spin.setSuffix(" samples")
        self.end_spin.setSpecialValueText("End of file")
        self.end_spin.valueChanged.connect(self.on_changed)
        layout.addRow("End Offset:", self.end_spin)
        
        tab.setLayout(layout)
        
    def init_sequence_tab(self, tab):
        layout = QFormLayout()
        
        # Sequence mode
        self.seq_mode_combo = QComboBox()
        self.seq_mode_combo.addItems([
            "round_robin", "random", "true_random", "always"
        ])
        self.seq_mode_combo.currentTextChanged.connect(self.on_seq_mode_changed)
        layout.addRow("Sequence Mode:", self.seq_mode_combo)
        
        # Sequence position (only for round-robin)
        self.seq_position_spin = QSpinBox()
        self.seq_position_spin.setRange(1, 32)
        self.seq_position_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Sequence Position:", self.seq_position_spin)
        
        # Add explanation labels
        explanation = QLabel(
            "Round-Robin: Cycles through samples in order\n"
            "Random: Random with repetition allowed\n"
            "True Random: Random without immediate repetition\n"
            "Always: Always plays this sample"
        )
        explanation.setStyleSheet("QLabel { color: gray; font-size: 10px; }")
        layout.addRow("", explanation)
        
        tab.setLayout(layout)
        
    def init_loop_tab(self, tab):
        layout = QFormLayout()
        
        # Loop enabled
        self.loop_enabled_check = QCheckBox()
        self.loop_enabled_check.toggled.connect(self.on_loop_enabled_changed)
        layout.addRow("Enable Looping:", self.loop_enabled_check)
        
        # Loop start
        self.loop_start_spin = QSpinBox()
        self.loop_start_spin.setRange(0, 999999999)
        self.loop_start_spin.setSuffix(" samples")
        self.loop_start_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Loop Start:", self.loop_start_spin)
        
        # Loop end
        self.loop_end_spin = QSpinBox()
        self.loop_end_spin.setRange(0, 999999999)
        self.loop_end_spin.setSuffix(" samples")
        self.loop_end_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Loop End:", self.loop_end_spin)
        
        # Loop crossfade
        self.loop_crossfade_spin = QDoubleSpinBox()
        self.loop_crossfade_spin.setRange(0.0, 10.0)
        self.loop_crossfade_spin.setSingleStep(0.001)
        self.loop_crossfade_spin.setDecimals(3)
        self.loop_crossfade_spin.setSuffix(" sec")
        self.loop_crossfade_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Crossfade Time:", self.loop_crossfade_spin)
        
        # Loop mode
        self.loop_mode_combo = QComboBox()
        self.loop_mode_combo.addItems([
            "forward", "backward", "bidirectional"
        ])
        self.loop_mode_combo.currentTextChanged.connect(self.on_changed)
        layout.addRow("Loop Mode:", self.loop_mode_combo)
        
        tab.setLayout(layout)
        
    def on_seq_mode_changed(self):
        # Enable/disable sequence position based on mode
        is_round_robin = self.seq_mode_combo.currentText() == "round_robin"
        self.seq_position_spin.setEnabled(is_round_robin)
        self.on_changed()
        
    def on_loop_enabled_changed(self):
        # Enable/disable loop controls based on loop enabled
        enabled = self.loop_enabled_check.isChecked()
        self.loop_start_spin.setEnabled(enabled)
        self.loop_end_spin.setEnabled(enabled)
        self.loop_crossfade_spin.setEnabled(enabled)
        self.loop_mode_combo.setEnabled(enabled)
        self.on_changed()
        
    def on_changed(self):
        if self.zone:
            self.update_zone_from_ui()
            self.zoneChanged.emit()
        
    def set_zone(self, zone):
        """Set the zone to edit"""
        self.zone = zone
        self.update_from_zone()
        
    def update_from_zone(self):
        """Update UI from zone data"""
        if not self.zone:
            return
            
        # Basic properties
        self.path_label.setText(self.zone.path)
        self.root_note_spin.setValue(self.zone.rootNote)
        self.lo_note_spin.setValue(self.zone.loNote)
        self.hi_note_spin.setValue(self.zone.hiNote)
        
        if hasattr(self.zone, "velocityRange"):
            self.vel_low_spin.setValue(self.zone.velocityRange[0])
            self.vel_high_spin.setValue(self.zone.velocityRange[1])
        
        if hasattr(self.zone, "volume"):
            self.volume_spin.setValue(self.zone.volume)
        if hasattr(self.zone, "pan"):
            self.pan_spin.setValue(self.zone.pan)
        if hasattr(self.zone, "tune"):
            self.tune_spin.setValue(self.zone.tune)
        if hasattr(self.zone, "start"):
            self.start_spin.setValue(self.zone.start)
        if hasattr(self.zone, "end") and self.zone.end is not None:
            self.end_spin.setValue(self.zone.end)
        else:
            self.end_spin.setValue(0)  # Special value for "end of file"
        
        # Sequence properties
        if hasattr(self.zone, "seqMode"):
            self.seq_mode_combo.setCurrentText(self.zone.seqMode)
        if hasattr(self.zone, "seqPosition"):
            self.seq_position_spin.setValue(self.zone.seqPosition)
        
        # Loop properties
        if hasattr(self.zone, "loopEnabled"):
            self.loop_enabled_check.setChecked(self.zone.loopEnabled)
        if hasattr(self.zone, "loopStart") and self.zone.loopStart is not None:
            self.loop_start_spin.setValue(self.zone.loopStart)
        if hasattr(self.zone, "loopEnd") and self.zone.loopEnd is not None:
            self.loop_end_spin.setValue(self.zone.loopEnd)
        if hasattr(self.zone, "loopCrossfade"):
            self.loop_crossfade_spin.setValue(self.zone.loopCrossfade)
        if hasattr(self.zone, "loopMode"):
            self.loop_mode_combo.setCurrentText(self.zone.loopMode)
        
        # Update enabled states
        self.on_seq_mode_changed()
        self.on_loop_enabled_changed()
        
    def update_zone_from_ui(self):
        """Update zone data from UI"""
        if not self.zone:
            return
            
        # Basic properties
        self.zone.rootNote = self.root_note_spin.value()
        self.zone.loNote = self.lo_note_spin.value()
        self.zone.hiNote = self.hi_note_spin.value()
        self.zone.velocityRange = (self.vel_low_spin.value(), self.vel_high_spin.value())
        self.zone.volume = self.volume_spin.value()
        self.zone.pan = self.pan_spin.value()
        self.zone.tune = self.tune_spin.value()
        self.zone.start = self.start_spin.value()
        self.zone.end = self.end_spin.value() if self.end_spin.value() > 0 else None
        
        # Sequence properties
        self.zone.seqMode = self.seq_mode_combo.currentText()
        self.zone.seqPosition = self.seq_position_spin.value()
        
        # Loop properties
        self.zone.loopEnabled = self.loop_enabled_check.isChecked()
        self.zone.loopStart = self.loop_start_spin.value() if self.loop_enabled_check.isChecked() else None
        self.zone.loopEnd = self.loop_end_spin.value() if self.loop_enabled_check.isChecked() else None
        self.zone.loopCrossfade = self.loop_crossfade_spin.value()
        self.zone.loopMode = self.loop_mode_combo.currentText()

class VelocityLayerManager(QGroupBox):
    """Manager for velocity layers within a key range"""
    layersChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Velocity Layers", parent)
        self.zones = []  # List of zones for the same key range
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header with add/remove buttons
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Layers for this key range:"))
        header_layout.addStretch()
        
        self.add_layer_btn = QPushButton("Add Layer")
        self.add_layer_btn.clicked.connect(self.add_layer)
        header_layout.addWidget(self.add_layer_btn)
        
        self.remove_layer_btn = QPushButton("Remove Layer")
        self.remove_layer_btn.clicked.connect(self.remove_layer)
        header_layout.addWidget(self.remove_layer_btn)
        
        layout.addLayout(header_layout)
        
        # Layer list with velocity ranges
        self.layer_info = QLabel("No layers configured")
        layout.addWidget(self.layer_info)
        
        # Crossfade controls
        crossfade_layout = QFormLayout()
        
        self.crossfade_enabled = QCheckBox()
        self.crossfade_enabled.toggled.connect(self.on_crossfade_changed)
        crossfade_layout.addRow("Enable Crossfade:", self.crossfade_enabled)
        
        self.crossfade_amount = QDoubleSpinBox()
        self.crossfade_amount.setRange(0.0, 50.0)
        self.crossfade_amount.setSingleStep(1.0)
        self.crossfade_amount.setDecimals(1)
        self.crossfade_amount.setSuffix(" velocity")
        self.crossfade_amount.valueChanged.connect(self.layersChanged.emit)
        crossfade_layout.addRow("Crossfade Amount:", self.crossfade_amount)
        
        layout.addLayout(crossfade_layout)
        self.setLayout(layout)
        
    def set_zones(self, zones):
        """Set the zones for this key range"""
        self.zones = zones
        self.update_layer_info()
        
    def add_layer(self):
        """Add a new velocity layer"""
        # Auto-assign velocity range based on existing layers
        if not self.zones:
            velocity_range = (0, 127)
        else:
            # Find the next available velocity range
            used_ranges = [zone.velocityRange for zone in self.zones]
            # Simple logic: split the remaining range
            velocity_range = (0, 63) if len(used_ranges) == 1 else (64, 127)
        
        # This would typically open a file dialog to select a sample
        # For now, we'll just create a placeholder
        new_zone = SampleZone(
            "new_sample.wav", 60, 60, 60, velocity_range
        )
        self.zones.append(new_zone)
        self.update_layer_info()
        self.layersChanged.emit()
        
    def remove_layer(self):
        """Remove the last velocity layer"""
        if self.zones:
            self.zones.pop()
            self.update_layer_info()
            self.layersChanged.emit()
            
    def update_layer_info(self):
        """Update the layer information display"""
        if not self.zones:
            self.layer_info.setText("No layers configured")
            return
            
        info_text = f"{len(self.zones)} layer(s):\n"
        for i, zone in enumerate(self.zones):
            vel_range = zone.velocityRange if hasattr(zone, "velocityRange") else (0, 127)
            info_text += f"  Layer {i+1}: Velocity {vel_range[0]}-{vel_range[1]}\n"
        
        self.layer_info.setText(info_text.strip())
        
    def on_crossfade_changed(self):
        """Handle crossfade enable/disable"""
        enabled = self.crossfade_enabled.isChecked()
        self.crossfade_amount.setEnabled(enabled)
        self.layersChanged.emit()