"""
Advanced Group Management System for DecentSampler
Handles complex sample grouping scenarios including:
- Velocity layers (different samples based on velocity)
- Sample blending (multiple samples playing simultaneously with crossfade control)
- Multiple groups (completely separate sample sets)
- Tag-based organization (grouping samples by characteristics)
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QSpinBox, 
    QDoubleSpinBox, QComboBox, QCheckBox, QPushButton, QListWidget, 
    QListWidgetItem, QDialog, QDialogButtonBox, QFormLayout, QScrollArea,
    QFrame, QSplitter, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QTextEdit, QSlider
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPalette, QFont, QColor
from model import SampleZone

class SampleGroup:
    """Represents a DecentSampler sample group with all its properties"""
    
    def __init__(self, name="Group", enabled=True, volume=0.0, pan=0.0, 
                 attack=None, decay=None, sustain=None, release=None,
                 tags=None, group_fx=None):
        self.name = name
        self.enabled = enabled
        self.volume = volume  # Group volume in dB
        self.pan = pan        # Group pan (-1.0 to 1.0)
        
        # Group-level envelope (optional, overrides instrument envelope)
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        
        # Sample organization
        self.samples = []     # List of SampleZone objects
        self.tags = tags or []  # List of tags for this group
        
        # Group-specific effects
        self.group_fx = group_fx or []  # List of effect configs
        
    def add_sample(self, sample_zone):
        """Add a sample to this group"""
        if isinstance(sample_zone, SampleZone):
            self.samples.append(sample_zone)
        else:
            raise TypeError("Expected SampleZone object")
            
    def remove_sample(self, sample_zone):
        """Remove a sample from this group"""
        if sample_zone in self.samples:
            self.samples.remove(sample_zone)
            
    def get_samples_for_note(self, note, velocity=64):
        """Get all samples in this group that should trigger for a given note/velocity"""
        matching_samples = []
        for sample in self.samples:
            # Check note range
            if sample.loNote <= note <= sample.hiNote:
                # Check velocity range
                if hasattr(sample, 'velocityRange'):
                    vel_low, vel_high = sample.velocityRange
                    if vel_low <= velocity <= vel_high:
                        matching_samples.append(sample)
                else:
                    matching_samples.append(sample)
        return matching_samples

class GroupManagerWidget(QWidget):
    """Main widget for managing sample groups"""
    
    groupsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.groups = []  # List of SampleGroup objects
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Left side: Group list and controls
        left_panel = QVBoxLayout()
        
        # Group list header
        group_header = QHBoxLayout()
        group_header.addWidget(QLabel("Sample Groups"))
        group_header.addStretch()
        
        self.tutorial_btn = QPushButton("📚 Tutorial")
        self.tutorial_btn.clicked.connect(self.show_tutorial)
        self.tutorial_btn.setToolTip("Learn about velocity layers, sample blending, and simultaneous layers")
        group_header.addWidget(self.tutorial_btn)
        
        self.add_group_btn = QPushButton("Add Group")
        self.add_group_btn.clicked.connect(self.add_group)
        group_header.addWidget(self.add_group_btn)
        
        self.remove_group_btn = QPushButton("Remove Group")
        self.remove_group_btn.clicked.connect(self.remove_group)
        group_header.addWidget(self.remove_group_btn)
        
        left_panel.addLayout(group_header)
        
        # Group list
        self.group_list = QListWidget()
        self.group_list.currentItemChanged.connect(self.on_group_selected)
        left_panel.addWidget(self.group_list)
        
        # Quick setup buttons
        quick_setup = QGroupBox("Quick Setup")
        quick_layout = QVBoxLayout()
        
        self.velocity_layers_btn = QPushButton("Create Velocity Layers")
        self.velocity_layers_btn.clicked.connect(self.create_velocity_layers)
        self.velocity_layers_btn.setToolTip("Create multiple groups with different velocity ranges")
        quick_layout.addWidget(self.velocity_layers_btn)
        
        self.blend_layers_btn = QPushButton("Create Blend Layers")
        self.blend_layers_btn.clicked.connect(self.create_blend_layers)
        self.blend_layers_btn.setToolTip("Put multiple samples in the same group for blending")
        quick_layout.addWidget(self.blend_layers_btn)
        
        self.round_robin_btn = QPushButton("Setup Round-Robin")
        self.round_robin_btn.clicked.connect(self.setup_round_robin)
        self.round_robin_btn.setToolTip("Create round-robin alternation between samples")
        quick_layout.addWidget(self.round_robin_btn)
        
        quick_setup.setLayout(quick_layout)
        left_panel.addWidget(quick_setup)
        
        # Right side: Group details editor
        self.group_editor = GroupEditorWidget()
        self.group_editor.groupChanged.connect(self.on_group_edited)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.group_editor)
        
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        
    def show_tutorial(self):
        """Show the grouping tutorial"""
        try:
            from dialogs.grouping_tutorial import show_grouping_tutorial
            show_grouping_tutorial(self)
        except ImportError:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Tutorial", 
                "Tutorial system not available. Please refer to the SAMPLE_GROUPING_GUIDE.md file for detailed explanations.")
        
    def add_group(self):
        """Add a new sample group"""
        group_name = f"Group {len(self.groups) + 1}"
        new_group = SampleGroup(group_name)
        self.groups.append(new_group)
        
        item = QListWidgetItem(group_name)
        self.group_list.addItem(item)
        self.group_list.setCurrentItem(item)
        
        self.groupsChanged.emit()
        
    def remove_group(self):
        """Remove the selected group"""
        current_row = self.group_list.currentRow()
        if 0 <= current_row < len(self.groups):
            del self.groups[current_row]
            self.group_list.takeItem(current_row)
            self.groupsChanged.emit()
            
    def on_group_selected(self, current, previous):
        """Handle group selection"""
        if current:
            row = self.group_list.row(current)
            if 0 <= row < len(self.groups):
                self.group_editor.set_group(self.groups[row])
                
    def on_group_edited(self):
        """Handle group property changes"""
        current_row = self.group_list.currentRow()
        if 0 <= current_row < len(self.groups):
            # Update list item name if changed
            group = self.groups[current_row]
            self.group_list.item(current_row).setText(group.name)
            self.groupsChanged.emit()
            
    def create_velocity_layers(self):
        """Create velocity layer groups with wizard"""
        dialog = VelocityLayerWizard(self)
        if dialog.exec_() == QDialog.Accepted:
            # Create groups based on wizard settings
            config = dialog.get_config()
            self._create_velocity_groups(config)
            
    def create_blend_layers(self):
        """Create blend layer setup with wizard"""
        dialog = BlendLayerWizard(self)
        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_config()
            self._create_blend_group(config)
            
    def setup_round_robin(self):
        """Setup round-robin groups with wizard"""
        dialog = RoundRobinWizard(self)
        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_config()
            self._create_round_robin_groups(config)
            
    def _create_velocity_groups(self, config):
        """Create velocity layer groups based on configuration"""
        # Implementation for velocity layers
        num_layers = config['layers']
        velocity_ranges = []
        
        # Calculate velocity splits
        range_size = 127 // num_layers
        for i in range(num_layers):
            vel_start = i * range_size
            vel_end = (i + 1) * range_size - 1 if i < num_layers - 1 else 127
            velocity_ranges.append((vel_start, vel_end))
            
        for i, (vel_start, vel_end) in enumerate(velocity_ranges):
            group_name = f"Velocity Layer {i+1} ({vel_start}-{vel_end})"
            group = SampleGroup(group_name)
            group.tags = [f"velocity_layer_{i+1}"]
            self.groups.append(group)
            
            item = QListWidgetItem(group_name)
            self.group_list.addItem(item)
            
        self.groupsChanged.emit()
        
    def _create_blend_group(self, config):
        """Create a single group for blending multiple samples"""
        group_name = config.get('name', 'Blend Group')
        group = SampleGroup(group_name)
        group.tags = config.get('tags', [])
        self.groups.append(group)
        
        item = QListWidgetItem(group_name)
        self.group_list.addItem(item)
        self.group_list.setCurrentItem(item)
        
        self.groupsChanged.emit()
        
    def _create_round_robin_groups(self, config):
        """Create round-robin groups"""
        num_groups = config['variations']
        base_name = config.get('name', 'Round Robin')
        
        for i in range(num_groups):
            group_name = f"{base_name} {i+1}"
            group = SampleGroup(group_name)
            group.tags = [f"rr_variation_{i+1}"]
            self.groups.append(group)
            
            item = QListWidgetItem(group_name)
            self.group_list.addItem(item)
            
        self.groupsChanged.emit()
        
    def set_groups(self, groups):
        """Set the groups from external source"""
        self.groups = groups or []
        self.refresh_group_list()
        
    def get_groups(self):
        """Get the current groups"""
        return self.groups
        
    def refresh_group_list(self):
        """Refresh the group list display"""
        self.group_list.clear()
        for group in self.groups:
            item = QListWidgetItem(group.name)
            self.group_list.addItem(item)

class GroupEditorWidget(QGroupBox):
    """Editor for individual group properties"""
    
    groupChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Group Properties", parent)
        self.current_group = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tabs for different aspects
        tabs = QTabWidget()
        
        # Basic properties tab
        basic_tab = QWidget()
        self.init_basic_tab(basic_tab)
        tabs.addTab(basic_tab, "Basic")
        
        # Samples tab
        samples_tab = QWidget()
        self.init_samples_tab(samples_tab)
        tabs.addTab(samples_tab, "Samples")
        
        # Advanced tab
        advanced_tab = QWidget()
        self.init_advanced_tab(advanced_tab)
        tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
    def init_basic_tab(self, tab):
        layout = QFormLayout()
        
        # Group name
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.on_property_changed)
        layout.addRow("Name:", self.name_edit)
        
        # Enabled checkbox
        self.enabled_check = QCheckBox()
        self.enabled_check.toggled.connect(self.on_property_changed)
        layout.addRow("Enabled:", self.enabled_check)
        
        # Volume
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(-60.0, 20.0)
        self.volume_spin.setSingleStep(0.1)
        self.volume_spin.setDecimals(1)
        self.volume_spin.setSuffix(" dB")
        self.volume_spin.valueChanged.connect(self.on_property_changed)
        layout.addRow("Volume:", self.volume_spin)
        
        # Pan
        self.pan_spin = QDoubleSpinBox()
        self.pan_spin.setRange(-1.0, 1.0)
        self.pan_spin.setSingleStep(0.1)
        self.pan_spin.setDecimals(2)
        self.pan_spin.valueChanged.connect(self.on_property_changed)
        layout.addRow("Pan:", self.pan_spin)
        
        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Enter tags separated by commas")
        self.tags_edit.textChanged.connect(self.on_property_changed)
        layout.addRow("Tags:", self.tags_edit)
        
        tab.setLayout(layout)
        
    def init_samples_tab(self, tab):
        layout = QVBoxLayout()
        
        # Sample list header
        sample_header = QHBoxLayout()
        sample_header.addWidget(QLabel("Samples in this Group"))
        sample_header.addStretch()
        
        self.add_sample_btn = QPushButton("Add Sample")
        self.add_sample_btn.clicked.connect(self.add_sample_to_group)
        sample_header.addWidget(self.add_sample_btn)
        
        self.remove_sample_btn = QPushButton("Remove Sample")
        self.remove_sample_btn.clicked.connect(self.remove_sample_from_group)
        sample_header.addWidget(self.remove_sample_btn)
        
        layout.addLayout(sample_header)
        
        # Sample table
        self.sample_table = QTableWidget()
        self.sample_table.setColumnCount(5)
        self.sample_table.setHorizontalHeaderLabels([
            "File", "Key Range", "Velocity Range", "Tags", "Volume"
        ])
        self.sample_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.sample_table)
        
        # Sample blend controls (for samples with tags)
        blend_group = QGroupBox("Sample Blending")
        blend_layout = QVBoxLayout()
        
        blend_info = QLabel("Add blend controls to crossfade between tagged samples:")
        blend_info.setWordWrap(True)
        blend_layout.addWidget(blend_info)
        
        self.create_blend_btn = QPushButton("Create Blend Control")
        self.create_blend_btn.clicked.connect(self.create_blend_control)
        blend_layout.addWidget(self.create_blend_btn)
        
        blend_group.setLayout(blend_layout)
        layout.addWidget(blend_group)
        
        tab.setLayout(layout)
        
    def init_advanced_tab(self, tab):
        layout = QFormLayout()
        
        # Group-level envelope override
        envelope_group = QGroupBox("Group Envelope Override")
        envelope_layout = QFormLayout()
        
        self.use_group_envelope = QCheckBox("Override instrument envelope")
        self.use_group_envelope.toggled.connect(self.on_envelope_toggle)
        envelope_layout.addRow("", self.use_group_envelope)
        
        self.group_attack = QDoubleSpinBox()
        self.group_attack.setRange(0.0, 10.0)
        self.group_attack.setSingleStep(0.01)
        self.group_attack.setDecimals(3)
        self.group_attack.setSuffix(" sec")
        self.group_attack.valueChanged.connect(self.on_property_changed)
        envelope_layout.addRow("Attack:", self.group_attack)
        
        self.group_decay = QDoubleSpinBox()
        self.group_decay.setRange(0.0, 10.0)
        self.group_decay.setSingleStep(0.01)
        self.group_decay.setDecimals(3)
        self.group_decay.setSuffix(" sec")
        self.group_decay.valueChanged.connect(self.on_property_changed)
        envelope_layout.addRow("Decay:", self.group_decay)
        
        self.group_sustain = QDoubleSpinBox()
        self.group_sustain.setRange(0.0, 1.0)
        self.group_sustain.setSingleStep(0.01)
        self.group_sustain.setDecimals(3)
        self.group_sustain.valueChanged.connect(self.on_property_changed)
        envelope_layout.addRow("Sustain:", self.group_sustain)
        
        self.group_release = QDoubleSpinBox()
        self.group_release.setRange(0.0, 10.0)
        self.group_release.setSingleStep(0.01)
        self.group_release.setDecimals(3)
        self.group_release.setSuffix(" sec")
        self.group_release.valueChanged.connect(self.on_property_changed)
        envelope_layout.addRow("Release:", self.group_release)
        
        envelope_group.setLayout(envelope_layout)
        layout.addRow(envelope_group)
        
        tab.setLayout(layout)
        
    def set_group(self, group):
        """Set the group to edit"""
        self.current_group = group
        self.update_ui_from_group()
        
    def update_ui_from_group(self):
        """Update UI controls from group data"""
        if not self.current_group:
            return
            
        # Basic properties
        self.name_edit.setText(self.current_group.name)
        self.enabled_check.setChecked(self.current_group.enabled)
        self.volume_spin.setValue(self.current_group.volume)
        self.pan_spin.setValue(self.current_group.pan)
        self.tags_edit.setText(", ".join(self.current_group.tags))
        
        # Update sample table
        self.refresh_sample_table()
        
        # Advanced properties
        has_envelope = any(x is not None for x in [
            self.current_group.attack, self.current_group.decay,
            self.current_group.sustain, self.current_group.release
        ])
        self.use_group_envelope.setChecked(has_envelope)
        
        if has_envelope:
            self.group_attack.setValue(self.current_group.attack or 0.0)
            self.group_decay.setValue(self.current_group.decay or 0.0)
            self.group_sustain.setValue(self.current_group.sustain or 1.0)
            self.group_release.setValue(self.current_group.release or 0.0)
            
        self.on_envelope_toggle()
        
    def refresh_sample_table(self):
        """Refresh the sample table display"""
        if not self.current_group:
            self.sample_table.setRowCount(0)
            return
            
        samples = self.current_group.samples
        self.sample_table.setRowCount(len(samples))
        
        for row, sample in enumerate(samples):
            # File name
            self.sample_table.setItem(row, 0, QTableWidgetItem(sample.path))
            
            # Key range
            key_range = f"{sample.loNote}-{sample.hiNote} (root: {sample.rootNote})"
            self.sample_table.setItem(row, 1, QTableWidgetItem(key_range))
            
            # Velocity range
            if hasattr(sample, 'velocityRange'):
                vel_range = f"{sample.velocityRange[0]}-{sample.velocityRange[1]}"
            else:
                vel_range = "0-127"
            self.sample_table.setItem(row, 2, QTableWidgetItem(vel_range))
            
            # Tags
            tags_text = ", ".join(sample.tags) if hasattr(sample, 'tags') and sample.tags else ""
            self.sample_table.setItem(row, 3, QTableWidgetItem(tags_text))
            
            # Volume
            volume = getattr(sample, 'volume', 0.0)
            self.sample_table.setItem(row, 4, QTableWidgetItem(f"{volume:.1f} dB"))
            
    def on_property_changed(self):
        """Handle property changes"""
        if not self.current_group:
            return
            
        # Update group from UI
        self.current_group.name = self.name_edit.text()
        self.current_group.enabled = self.enabled_check.isChecked()
        self.current_group.volume = self.volume_spin.value()
        self.current_group.pan = self.pan_spin.value()
        
        # Parse tags
        tags_text = self.tags_edit.text().strip()
        if tags_text:
            self.current_group.tags = [tag.strip() for tag in tags_text.split(",")]
        else:
            self.current_group.tags = []
            
        # Update envelope if enabled
        if self.use_group_envelope.isChecked():
            self.current_group.attack = self.group_attack.value()
            self.current_group.decay = self.group_decay.value()
            self.current_group.sustain = self.group_sustain.value()
            self.current_group.release = self.group_release.value()
        else:
            self.current_group.attack = None
            self.current_group.decay = None
            self.current_group.sustain = None
            self.current_group.release = None
            
        self.groupChanged.emit()
        
    def on_envelope_toggle(self):
        """Enable/disable envelope controls"""
        enabled = self.use_group_envelope.isChecked()
        self.group_attack.setEnabled(enabled)
        self.group_decay.setEnabled(enabled)
        self.group_sustain.setEnabled(enabled)
        self.group_release.setEnabled(enabled)
        
    def add_sample_to_group(self):
        """Add a sample to the current group"""
        if not self.current_group:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Group Selected", "Please select a group first.")
            return
            
        # Open sample selection dialog
        dialog = SampleSelectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_samples = dialog.get_selected_samples()
            
            # Add selected samples to the current group
            for sample_data in selected_samples:
                # Convert sample data to SampleZone if needed
                if isinstance(sample_data, dict):
                    # Create SampleZone from mapping data
                    from model import SampleZone
                    
                    # Auto-detect tags from filename
                    tags = self._detect_sample_tags(sample_data.get("path", ""))
                    
                    sample_zone = SampleZone(
                        path=sample_data.get("path", ""),
                        rootNote=sample_data.get("root", 60),
                        loNote=sample_data.get("lo", 60),
                        hiNote=sample_data.get("hi", 60),
                        velocityRange=(0, 127),  # Default velocity range
                        tags=tags
                    )
                else:
                    # Convert SampleMapping to SampleZone
                    from model import SampleZone
                    
                    # Auto-detect tags from filename
                    tags = self._detect_sample_tags(getattr(sample_data, "path", ""))
                    
                    sample_zone = SampleZone(
                        path=getattr(sample_data, "path", ""),
                        rootNote=getattr(sample_data, "root", 60),
                        loNote=getattr(sample_data, "lo", 60),
                        hiNote=getattr(sample_data, "hi", 60),
                        velocityRange=(0, 127),
                        tags=tags
                    )
                
                self.current_group.add_sample(sample_zone)
            
            # Refresh the UI
            self.refresh_sample_table()
            self.groupChanged.emit()
            
            # Show success message
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Samples Added", 
                f"Added {len(selected_samples)} sample(s) to group '{self.current_group.name}'")
        
    def remove_sample_from_group(self):
        """Remove selected sample from group"""
        current_row = self.sample_table.currentRow()
        if current_row >= 0 and self.current_group:
            if current_row < len(self.current_group.samples):
                del self.current_group.samples[current_row]
                self.refresh_sample_table()
                self.groupChanged.emit()
                
    def create_blend_control(self):
        """Create a blend control for tagged samples"""
        if not self.current_group:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Group Selected", "Please select a group first.")
            return
            
        # Check if group has samples with tags that can be blended
        if not self.current_group.samples:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Samples", 
                "This group has no samples. Add samples first, then create blend controls.")
            return
            
        dialog = BlendControlDialog(self.current_group, self)
        if dialog.exec_() == QDialog.Accepted:
            # Get the blend control configuration
            config = dialog.get_config()
            self._create_ui_blend_control(config)
            
    def _create_ui_blend_control(self, config):
        """Create the actual UI blend control"""
        try:
            # Add the blend control to the main window's UI elements
            main_window = self.get_main_window()
            if main_window and hasattr(main_window, 'preset'):
                # Add to UI elements list for XML export
                if not hasattr(main_window.preset, 'ui_elements'):
                    main_window.preset.ui_elements = []
                
                # Create the blend control configuration
                blend_control = {
                    'type': 'labeled-knob',
                    'label': config['control_name'],
                    'x': 10,  # Default position
                    'y': 150,
                    'width': 90,
                    'height': 110,
                    'min': 0.0,
                    'max': 1.0,
                    'default': 0.5,
                    'tags': {
                        'tag1': config['tag1'],
                        'tag2': config['tag2']
                    }
                }
                
                main_window.preset.ui_elements.append(blend_control)
                
                # Refresh the UI
                if hasattr(main_window, 'preview_canvas'):
                    main_window.preview_canvas.set_preset(main_window.preset, "")
                
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Blend Control Created", 
                    f"Created blend control '{config['control_name']}' for tags '{config['tag1']}' and '{config['tag2']}'.\n\n"
                    "The control will crossfade between samples with these tags when you save and load the preset in DecentSampler.")
                    
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to create blend control: {str(e)}")
    
    def get_main_window(self):
        """Find the main window"""
        widget = self.parent()
        while widget and not hasattr(widget, 'preset'):
            widget = widget.parent()
        return widget
    
    def _detect_sample_tags(self, file_path):
        """Auto-detect tags from sample filename"""
        import os
        filename = os.path.basename(file_path).lower()
        tags = []
        
        # Common sample variations that should be tagged
        tag_patterns = {
            'mic_close': ['close', 'dry', 'direct', 'near'],
            'mic_distant': ['distant', 'far', 'wet', 'reverb', 'room', 'hall'],
            'velocity_soft': ['soft', 'pp', 'pianissimo', 'light'],
            'velocity_medium': ['medium', 'mp', 'mezzopiano', 'normal'],
            'velocity_loud': ['loud', 'ff', 'fortissimo', 'hard'],
            'articulation_muted': ['muted', 'mute'],
            'articulation_open': ['open'],
            'articulation_sustain': ['sustain', 'sus'],
            'articulation_staccato': ['staccato', 'stacc'],
            'round_robin_1': ['rr1', 'take1', 'var1'],
            'round_robin_2': ['rr2', 'take2', 'var2'],
            'round_robin_3': ['rr3', 'take3', 'var3'],
            'round_robin_4': ['rr4', 'take4', 'var4'],
        }
        
        # Check each pattern
        for tag, patterns in tag_patterns.items():
            if any(pattern in filename for pattern in patterns):
                tags.append(tag)
        
        return tags

# Wizard dialogs for quick setup
class VelocityLayerWizard(QDialog):
    """Wizard for setting up velocity layers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Velocity Layer Setup")
        self.setFixedSize(400, 200)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Create velocity layers with different samples for soft/loud playing:"))
        
        form = QFormLayout()
        
        self.layers_spin = QSpinBox()
        self.layers_spin.setRange(2, 8)
        self.layers_spin.setValue(3)
        form.addRow("Number of layers:", self.layers_spin)
        
        layout.addLayout(form)
        
        # Example
        example = QLabel("Example: 3 layers creates groups for velocities 0-42, 43-84, 85-127")
        example.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(example)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def get_config(self):
        return {'layers': self.layers_spin.value()}

class BlendLayerWizard(QDialog):
    """Wizard for setting up blend layers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Blend Layer Setup")
        self.setFixedSize(400, 250)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Create a group for blending multiple samples (like close/distant mics):"))
        
        form = QFormLayout()
        
        self.name_edit = QLineEdit("Blend Group")
        form.addRow("Group name:", self.name_edit)
        
        self.tags_edit = QLineEdit("mic_close, mic_distant")
        self.tags_edit.setPlaceholderText("Tags for different sample types")
        form.addRow("Sample tags:", self.tags_edit)
        
        layout.addLayout(form)
        
        # Example
        example = QLabel("Example: BrokenPiano uses 'mic_close' and 'mic_distant' tags with a blend slider")
        example.setStyleSheet("color: gray; font-style: italic;")
        example.setWordWrap(True)
        layout.addWidget(example)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def get_config(self):
        tags = []
        if self.tags_edit.text().strip():
            tags = [tag.strip() for tag in self.tags_edit.text().split(",")]
        return {
            'name': self.name_edit.text(),
            'tags': tags
        }

class RoundRobinWizard(QDialog):
    """Wizard for setting up round-robin groups"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Round-Robin Setup")
        self.setFixedSize(400, 200)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Create round-robin groups for sample variation:"))
        
        form = QFormLayout()
        
        self.name_edit = QLineEdit("Round Robin")
        form.addRow("Base name:", self.name_edit)
        
        self.variations_spin = QSpinBox()
        self.variations_spin.setRange(2, 16)
        self.variations_spin.setValue(4)
        form.addRow("Number of variations:", self.variations_spin)
        
        layout.addLayout(form)
        
        # Example
        example = QLabel("Example: 4 variations creates 'Round Robin 1', 'Round Robin 2', etc.")
        example.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(example)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def get_config(self):
        return {
            'name': self.name_edit.text(),
            'variations': self.variations_spin.value()
        }

class BlendControlDialog(QDialog):
    """Dialog for creating blend controls"""
    
    def __init__(self, group, parent=None):
        super().__init__(parent)
        self.group = group
        self.setWindowTitle("Create Blend Control")
        self.setFixedSize(500, 300)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(f"Create blend control for group: {self.group.name}"))
        
        form = QFormLayout()
        
        self.control_name = QLineEdit("Blend")
        form.addRow("Control name:", self.control_name)
        
        self.tag1_edit = QLineEdit()
        self.tag1_edit.setPlaceholderText("e.g., mic_close")
        form.addRow("First tag:", self.tag1_edit)
        
        self.tag2_edit = QLineEdit()
        self.tag2_edit.setPlaceholderText("e.g., mic_distant")
        form.addRow("Second tag:", self.tag2_edit)
        
        layout.addLayout(form)
        
        # Explanation
        explanation = QTextEdit()
        explanation.setMaximumHeight(100)
        explanation.setPlainText(
            "This will create a slider that crossfades between samples with different tags. "
            "When the slider is at 0%, only samples with the first tag play. "
            "When at 100%, only samples with the second tag play. "
            "In between, both play with varying volumes."
        )
        explanation.setReadOnly(True)
        layout.addWidget(explanation)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_config(self):
        """Get the blend control configuration"""
        return {
            'control_name': self.control_name.text(),
            'tag1': self.tag1_edit.text(),
            'tag2': self.tag2_edit.text()
        }

class SampleSelectionDialog(QDialog):
    """Dialog for selecting samples to add to groups"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Samples for Group")
        self.setModal(True)
        self.resize(600, 400)
        self.selected_samples = []
        self.init_ui()
        self.load_available_samples()
        
    def init_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Select samples to add to the current group:")
        header.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Sample table
        self.sample_table = QTableWidget()
        self.sample_table.setColumnCount(4)
        self.sample_table.setHorizontalHeaderLabels([
            "Select", "Sample", "Note Range", "Root Note"
        ])
        self.sample_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.sample_table)
        
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
        
        ok_btn = QPushButton("Add Selected")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("background-color: #4a7c59; color: white; font-weight: bold;")
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_available_samples(self):
        """Load available samples from the main window"""
        # Get samples from the main sample mapping panel
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, "sample_mapping_panel"):
            samples = main_window.sample_mapping_panel.samples
            
            self.sample_table.setRowCount(len(samples))
            
            for row, sample in enumerate(samples):
                # Checkbox for selection
                checkbox = QCheckBox()
                self.sample_table.setCellWidget(row, 0, checkbox)
                
                # Sample filename
                if isinstance(sample, dict):
                    path = sample.get("path", "")
                    lo = sample.get("lo", 0)
                    hi = sample.get("hi", 127)
                    root = sample.get("root", 60)
                else:
                    path = getattr(sample, "path", "")
                    lo = getattr(sample, "lo", 0)
                    hi = getattr(sample, "hi", 127)
                    root = getattr(sample, "root", 60)
                
                filename = path.split("/")[-1] if path else ""
                self.sample_table.setItem(row, 1, QTableWidgetItem(filename))
                
                # Note range
                lo_name = self._midi_to_note_name(lo)
                hi_name = self._midi_to_note_name(hi)
                range_text = f"{lo_name} - {hi_name}"
                self.sample_table.setItem(row, 2, QTableWidgetItem(range_text))
                
                # Root note
                root_name = self._midi_to_note_name(root)
                self.sample_table.setItem(row, 3, QTableWidgetItem(root_name))
                
                # Store sample data
                setattr(checkbox, "sample_data", sample)
            
            # Resize columns
            self.sample_table.resizeColumnsToContents()
        else:
            # No samples available
            self.sample_table.setRowCount(1)
            self.sample_table.setItem(0, 1, QTableWidgetItem("No samples available"))
            for col in [0, 2, 3]:
                self.sample_table.setItem(0, col, QTableWidgetItem(""))
    
    def get_main_window(self):
        """Find the main window"""
        widget = self.parent()
        while widget and not hasattr(widget, "sample_mapping_panel"):
            widget = widget.parent()
        return widget
    
    def _select_all(self):
        """Select all samples"""
        for row in range(self.sample_table.rowCount()):
            checkbox = self.sample_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)
    
    def _select_none(self):
        """Deselect all samples"""
        for row in range(self.sample_table.rowCount()):
            checkbox = self.sample_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
    
    def get_selected_samples(self):
        """Get the selected sample data"""
        selected = []
        for row in range(self.sample_table.rowCount()):
            checkbox = self.sample_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked() and hasattr(checkbox, "sample_data"):
                selected.append(checkbox.sample_data)
        return selected
    
    def _midi_to_note_name(self, midi_note):
        """Convert MIDI note to name"""
        names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (midi_note // 12) - 1
        note = names[midi_note % 12]
        return f"{note}{octave}"

