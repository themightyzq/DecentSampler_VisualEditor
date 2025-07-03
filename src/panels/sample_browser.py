from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QGroupBox, QFormLayout, QSpinBox, QFileDialog
import os

class SampleBrowserWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.zone_map = {}  # path -> {loNote, hiNote, rootNote}
        self.layout = QVBoxLayout()
        self.sample_list = QListWidget()
        self.layout.addWidget(QLabel("Samples"))
        self.layout.addWidget(self.sample_list)
        import_btn = QPushButton("Import Samples")
        import_btn.clicked.connect(self.import_samples)
        self.layout.addWidget(import_btn)

        # Zone mapping panel
        self.zone_group = QGroupBox("Keyzone Mapping")
        zone_layout = QFormLayout()
        self.lo_spin = QSpinBox()
        self.lo_spin.setRange(0, 127)
        self.hi_spin = QSpinBox()
        self.hi_spin.setRange(0, 127)
        self.root_spin = QSpinBox()
        self.root_spin.setRange(0, 127)
        zone_layout.addRow("Low Note", self.lo_spin)
        zone_layout.addRow("High Note", self.hi_spin)
        zone_layout.addRow("Root Note", self.root_spin)
        self.zone_group.setLayout(zone_layout)
        self.layout.addWidget(self.zone_group)
        self.setLayout(self.layout)

        self.sample_list.currentItemChanged.connect(self.on_sample_selected)
        self.lo_spin.valueChanged.connect(self._on_spin_changed)
        self.hi_spin.valueChanged.connect(self._on_spin_changed)
        self.root_spin.valueChanged.connect(self._on_spin_changed)

    def import_samples(self):
        from PyQt5.QtCore import QSettings
        settings = QSettings("DecentSamplerEditor", "DecentSamplerEditorApp")
        last_folder = settings.value("last_sample_import_folder", "")
        files, _ = QFileDialog.getOpenFileNames(self, "Import WAV Samples", last_folder, "WAV Files (*.wav)")
        if files:
            settings.setValue("last_sample_import_folder", os.path.dirname(files[0]))
        for f in files:
            rel_path = os.path.relpath(f, os.getcwd())
            self.sample_list.addItem(rel_path)
            self.zone_map[rel_path] = {"loNote": 0, "hiNote": 127, "rootNote": 60}

    def on_sample_selected(self, curr, prev):
        if curr:
            path = curr.text()
            zone = self.zone_map.get(path, {"loNote": 0, "hiNote": 127, "rootNote": 60})
            self.lo_spin.blockSignals(True)
            self.hi_spin.blockSignals(True)
            self.root_spin.blockSignals(True)
            self.lo_spin.setValue(zone["loNote"])
            self.hi_spin.setValue(zone["hiNote"])
            self.root_spin.setValue(zone["rootNote"])
            self.lo_spin.blockSignals(False)
            self.hi_spin.blockSignals(False)
            self.root_spin.blockSignals(False)

    def _on_spin_changed(self):
        curr = self.sample_list.currentItem()
        if curr:
            path = curr.text()
            self.zone_map[path] = {
                "loNote": self.lo_spin.value(),
                "hiNote": self.hi_spin.value(),
                "rootNote": self.root_spin.value()
            }
