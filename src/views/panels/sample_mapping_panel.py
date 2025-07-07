from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QLineEdit, QPushButton, QFormLayout, QSpinBox, QFileDialog, QHBoxLayout
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
        title = QLabel("Samples & Mapping")
        title.setToolTip("Import your samples here and map them to keyzones")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setToolTip("List of imported samples. Select to edit mapping.")
        layout.addWidget(self.list_widget)

        # Mapping form
        form = QFormLayout()

        self.lo_spin = QSpinBox()
        self.lo_spin.setRange(0, 127)
        self.lo_spin.setToolTip("Low MIDI note (0–127)")
        form.addRow("Low Note", self.lo_spin)
        self.hi_spin = QSpinBox()
        self.hi_spin.setRange(0, 127)
        self.hi_spin.setToolTip("High MIDI note (0–127)")
        form.addRow("High Note", self.hi_spin)
        self.root_spin = QSpinBox()
        self.root_spin.setRange(0, 127)
        self.root_spin.setToolTip("Root MIDI note (0–127)")
        form.addRow("Root Note", self.root_spin)

        layout.addLayout(form)

        # Import/Auto-map buttons
        btn_layout = QHBoxLayout()
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

        self.list_widget.currentItemChanged.connect(self.on_sample_selected)
        self.lo_spin.valueChanged.connect(self.on_mapping_changed)
        self.hi_spin.valueChanged.connect(self.on_mapping_changed)
        self.root_spin.valueChanged.connect(self.on_mapping_changed)

    def set_samples(self, samples):
        self.samples = samples
        self.list_widget.clear()
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
            display = f"{filename} — {midi_note_name(lo)}–{midi_note_name(hi)} (root {midi_note_name(root)})"
            self.list_widget.addItem(display)
            item = self.list_widget.item(self.list_widget.count() - 1)
            item.setToolTip(path)
        # Clear mapping form
        self.set_mapping(None)

    def set_mapping(self, mapping):
        self.current_mapping = mapping
        if mapping is None:
            self.lo_spin.setValue(0)
            self.hi_spin.setValue(127)
            self.root_spin.setValue(60)
            return
        if isinstance(mapping, dict):
            path = mapping.get("path", "")
            lo = mapping.get("lo", 0)
            hi = mapping.get("hi", 127)
            root = mapping.get("root", 60)
        else:
            path = getattr(mapping, "path", str(mapping))
            lo = getattr(mapping, "lo", 0)
            hi = getattr(mapping, "hi", 127)
            root = getattr(mapping, "root", 60)
        self.lo_spin.setValue(lo)
        self.hi_spin.setValue(hi)
        self.root_spin.setValue(root)

    def on_sample_selected(self, curr, prev):
        if curr:
            idx = self.list_widget.row(curr)
            if idx < 0 or idx >= len(self.samples):
                self.set_mapping(None)
                return
            mapping = self.samples[idx]
            self.set_mapping(mapping)
        else:
            self.set_mapping(None)

    def on_mapping_changed(self):
        curr = self.list_widget.currentItem()
        if curr:
            idx = self.list_widget.row(curr)
            mapping = self.samples[idx]
            lo = self.lo_spin.value()
            hi = self.hi_spin.value()
            root = self.root_spin.value()
            if isinstance(mapping, dict):
                mapping["lo"] = lo
                mapping["hi"] = hi
                mapping["root"] = root
                filename = mapping["path"].split("/")[-1] if mapping["path"] else ""
                display = f"{filename} — {midi_note_name(mapping['lo'])}–{midi_note_name(mapping['hi'])} (root {midi_note_name(mapping['root'])})"
                curr.setText(display)
                curr.setToolTip(mapping["path"])
            else:
                setattr(mapping, "lo", lo)
                setattr(mapping, "hi", hi)
                setattr(mapping, "root", root)
                path = getattr(mapping, "path", "")
                filename = path.split("/")[-1] if path else ""
                display = f"{filename} — {midi_note_name(lo)}–{midi_note_name(hi)} (root {midi_note_name(root)})"
                curr.setText(display)
                curr.setToolTip(path)
            # Live update preview
            if hasattr(self.main_window, "preview_canvas") and hasattr(self.main_window, "preset"):
                self.main_window.preview_canvas.set_preset(self.main_window.preset, "")


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
