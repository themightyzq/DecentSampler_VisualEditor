from PyQt5.QtWidgets import QWidget, QFormLayout, QSpinBox, QLineEdit, QPushButton, QFileDialog, QLabel
from PyQt5.QtCore import Qt

class MappingForm(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.mapping = None
        layout = QFormLayout()
        self.path_edit = QLineEdit()
        self.browse_btn = QPushButton("Browse…")
        self.browse_btn.clicked.connect(self.browse_path)
        path_row = QWidget()
        path_layout = QFormLayout()
        path_layout.addRow(self.path_edit, self.browse_btn)
        path_row.setLayout(path_layout)
        layout.addRow("Sample Path", path_row)
        self.lo_spin = QSpinBox()
        self.lo_spin.setRange(0, 127)
        self.lo_spin.setToolTip("Lowest MIDI note for this sample mapping")
        layout.addRow("Low Note", self.lo_spin)
        self.hi_spin = QSpinBox()
        self.hi_spin.setRange(0, 127)
        self.hi_spin.setToolTip("Highest MIDI note for this sample mapping")
        layout.addRow("High Note", self.hi_spin)
        self.root_spin = QSpinBox()
        self.root_spin.setRange(0, 127)
        self.root_spin.setToolTip("Root MIDI note (the original pitch of the sample)")
        layout.addRow("Root Note", self.root_spin)
        self.setLayout(layout)
        # TODO: Connect valueChanged signals to update mapping and push undo commands

    def set_mapping(self, mapping):
        self.mapping = mapping
        if mapping is None:
            self.path_edit.setText("")
            self.lo_spin.setValue(0)
            self.hi_spin.setValue(127)
            self.root_spin.setValue(60)
            return
        self.path_edit.setText(mapping.path)
        self.lo_spin.setValue(mapping.lo)
        self.hi_spin.setValue(mapping.hi)
        self.root_spin.setValue(mapping.root)

    def browse_path(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Sample", "", "WAV Files (*.wav)")
        if file:
            self.path_edit.setText(file)
            # TODO: Update mapping and push undo command
