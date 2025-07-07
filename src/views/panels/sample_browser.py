from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QFileDialog, QHBoxLayout
from PyQt5.QtCore import Qt
from commands.commands import SampleAutoMapCommand

class SamplePanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.samples = []
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Samples"))
        self.list_widget = QListWidget()
        self.list_widget.setToolTip("List of imported samples")
        layout.addWidget(self.list_widget)

        # (Keyzone mapping controls removed for streamlined layout)

        btn_layout = QHBoxLayout()
        import_btn = QPushButton("Import Samples")
        import_btn.clicked.connect(self.import_samples)
        btn_layout.addWidget(import_btn)
        auto_map_btn = QPushButton("Auto-Map Folder…")
        auto_map_btn.clicked.connect(self.auto_map_folder)
        btn_layout.addWidget(auto_map_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.list_widget.currentItemChanged.connect(self.on_sample_selected)
        # (Keyzone mapping controls removed, so spinbox signals not connected)

    def set_samples(self, samples):
        """samples: list of SampleMapping or dicts with path, lo, hi, root"""
        self.samples = samples
        self.list_widget.clear()
        for m in samples:
            # m can be a SampleMapping or dict
            path = getattr(m, "path", m.get("path", "")) if hasattr(m, "path") or isinstance(m, dict) else str(m)
            lo = getattr(m, "lo", m.get("lo", 0)) if hasattr(m, "lo" ) or isinstance(m, dict) else 0
            hi = getattr(m, "hi", m.get("hi", 0)) if hasattr(m, "hi" ) or isinstance(m, dict) else 0
            root = getattr(m, "root", m.get("root", 0)) if hasattr(m, "root" ) or isinstance(m, dict) else 0
            display = f"{self.midi_note_name(lo)} ({lo}) – {self.midi_note_name(hi)} ({hi}), root {self.midi_note_name(root)} ({root})"
            item_text = f"{display}\n{path}"
            self.list_widget.addItem(item_text)
            item = self.list_widget.item(self.list_widget.count() - 1)
            item.setToolTip(f"Sample: {path}\nLow MIDI note: {self.midi_note_name(lo)} ({lo})\nHigh MIDI note: {self.midi_note_name(hi)} ({hi})\nRoot note: {self.midi_note_name(root)} ({root})")
        # (Keyzone mapping controls removed, so no spinboxes to clear/disable)

    @staticmethod
    def midi_note_name(n):
        names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (n // 12) - 1
        note = names[n % 12]
        return f"{note}{octave}"

    def import_samples(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Import WAV Samples", "", "WAV Files (*.wav)")
        if files:
            # Add as dicts with default mapping
            for f in files:
                self.samples.append({"path": f, "lo": 0, "hi": 127, "root": 60})
            self.set_samples(self.samples)
            # TODO: Push undo command and update preset/mapping form

    def auto_map_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Sample Folder")
        if folder and hasattr(self.main_window, "preset"):
            old_mappings = list(self.main_window.preset.mappings)
            self.main_window.preset.auto_map(folder)
            new_mappings = list(self.main_window.preset.mappings)
            cmd = SampleAutoMapCommand(
                self.main_window.preset, old_mappings, new_mappings, update_callback=self.refresh_sample_list
            )
            if hasattr(self.main_window, "undo_stack"):
                self.main_window.undo_stack.push(cmd)
            else:
                self.refresh_sample_list()

    def refresh_sample_list(self):
        if hasattr(self.main_window, "preset"):
            # Always build dicts with path, lo, hi, root
            mappings = []
            for m in self.main_window.preset.mappings:
                # m may be a custom object or dict
                if isinstance(m, dict):
                    path = m.get("path", "")
                    lo = m.get("lo", 0)
                    hi = m.get("hi", 127)
                    root = m.get("root", 60)
                else:
                    path = getattr(m, "path", str(m))
                    lo = getattr(m, "lo", 0)
                    hi = getattr(m, "hi", 127)
                    root = getattr(m, "root", 60)
                mappings.append({"path": path, "lo": lo, "hi": hi, "root": root})
            self.set_samples(mappings)

    def on_sample_selected(self, curr, prev):
        # (Keyzone mapping controls removed; selection logic can be simplified or left as a placeholder)
        pass

    # (Keyzone mapping controls removed; _on_spin_changed and _on_change_sample_file are no longer needed)
