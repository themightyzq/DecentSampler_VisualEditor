from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QFormLayout, QSpinBox, QFileDialog, QHBoxLayout
)
from PyQt5.QtCore import Qt

def midi_note_name(n):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octave = (n // 12) - 1
    note = names[n % 12]
    return f"{note}{octave}"

class SampleMappingPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.samples = []
        self.current_mapping = None

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        title = QLabel("Samples & Mapping")
        title.setToolTip("Import your samples here and map them to keyzones")
        layout.addWidget(title)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Filename", "Key Range (root)"])
        self.table_widget.setSelectionBehavior(self.table_widget.SelectRows)
        self.table_widget.setEditTriggers(self.table_widget.NoEditTriggers)
        self.table_widget.setToolTip("List of imported samples. Select to edit mapping.")
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_widget)

        # Dedicated zone mapping panel (always present, shown/hidden)
        from PyQt5.QtWidgets import QFrame, QGridLayout, QSizePolicy
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
                font-size: 16px;
                font-weight: 600;
                min-width: 110px;
                padding-right: 12px;
            }
            QSpinBox {
                color: #f0f0f0;
                font-size: 16px;
                min-width: 70px;
                min-height: 32px;
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

        # Import/Auto-map buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(8)
        import_btn = QPushButton("Import Samples")
        import_btn.setToolTip("Import one or more WAV files")
        import_btn.clicked.connect(self.import_samples)
        btn_layout.addWidget(import_btn)
        auto_map_btn = QPushButton("Auto-Map Folder…")
        auto_map_btn.setToolTip("Automatically map all samples in a folder")
        auto_map_btn.clicked.connect(self.auto_map_folder)
        btn_layout.addWidget(auto_map_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.table_widget.selectionModel().selectionChanged.connect(self.on_table_selection_changed)

    def set_samples(self, samples):
        self.samples = samples
        self.table_widget.setRowCount(0)
        for m in samples:
            if isinstance(m, dict):
                path = m.get("path", "")
                lo = m.get("lo", 0)
                hi = m.get("hi", 0)
                root = m.get("root", 0)
            else:
                path = getattr(m, "path", str(m))
                lo = getattr(m, "lo", 0)
                hi = getattr(m, "hi", 0)
                root = getattr(m, "root", 0)
            filename = path.split("/")[-1] if path else ""
            key_range = f"{midi_note_name(lo)}–{midi_note_name(hi)} (root {midi_note_name(root)})"
            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)
            self.table_widget.setItem(row, 0, QTableWidgetItem(filename))
            self.table_widget.setItem(row, 1, QTableWidgetItem(key_range))
            self.table_widget.setRowHeight(row, 24)
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
                return
            mapping = self.samples[idx]
            self.set_mapping(mapping)
        else:
            self.set_mapping(None)

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
                filename = mapping["path"].split("/")[-1] if mapping["path"] else ""
                key_range = f"{midi_note_name(mapping['lo'])}–{midi_note_name(mapping['hi'])} (root {midi_note_name(mapping['root'])})"
            else:
                setattr(mapping, "lo", lo)
                setattr(mapping, "hi", hi)
                setattr(mapping, "root", root)
                path = getattr(mapping, "path", "")
                filename = path.split("/")[-1] if path else ""
                key_range = f"{midi_note_name(lo)}–{midi_note_name(hi)} (root {midi_note_name(root)})"
            self.table_widget.setItem(idx, 0, QTableWidgetItem(filename))
            self.table_widget.setItem(idx, 1, QTableWidgetItem(key_range))
            # Live update preview
            if hasattr(self.main_window, "preview_canvas") and hasattr(self.main_window, "preset"):
                self.main_window.preview_canvas.set_preset(self.main_window.preset, "")

        else:
            self.zone_panel.setVisible(False)

    def import_samples(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Import WAV Samples", "", "WAV Files (*.wav)")
        if files:
            for f in files:
                self.samples.append({"path": f, "lo": 0, "hi": 127, "root": 60})
            self.set_samples(self.samples)
            # Live update preview
            if hasattr(self.main_window, "preview_canvas") and hasattr(self.main_window, "preset"):
                self.main_window.preview_canvas.set_preset(self.main_window.preset, "")

    def auto_map_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Sample Folder")
        if folder and hasattr(self.main_window, "preset"):
            old_mappings = list(self.main_window.preset.mappings)
            self.main_window.preset.auto_map(folder)
            new_mappings = list(self.main_window.preset.mappings)
            # TODO: Push undo command if needed
            self.set_samples(new_mappings)
            # Live update preview
            if hasattr(self.main_window, "preview_canvas") and hasattr(self.main_window, "preset"):
                self.main_window.preview_canvas.set_preset(self.main_window.preset, "")

    # (Inline zone editor helpers removed)
