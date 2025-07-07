from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QFileDialog, QComboBox, QLineEdit
)
from commands.commands import GlobalOptionEditCommand

class GlobalOptionsPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        # Background image
        bg_layout = QHBoxLayout()
        bg_layout.addWidget(QLabel("Background Image:"))
        self.bg_edit = QLineEdit()
        bg_layout.addWidget(self.bg_edit)
        self.bg_edit.editingFinished.connect(lambda: self._option_changed("bg_image", self._last_bg_image, self.bg_edit.text()))
        self.bg_btn = QPushButton("Browse…")
        self.bg_btn.clicked.connect(self.browse_bg)
        bg_layout.addWidget(self.bg_btn)
        layout.addLayout(bg_layout)
        self._last_bg_image = ""

        # Controls
        self.attack_cb = QCheckBox("Attack")
        self.decay_cb = QCheckBox("Decay")
        self.sustain_cb = QCheckBox("Sustain")
        self.release_cb = QCheckBox("Release")
        self.tone_cb = QCheckBox("Tone")
        self.chorus_cb = QCheckBox("Chorus")
        self.reverb_cb = QCheckBox("Reverb")
        self.midicc1_cb = QCheckBox("Map Tone to MIDI CC1")
        for cb, name in [
            (self.attack_cb, "have_attack"),
            (self.decay_cb, "have_decay"),
            (self.sustain_cb, "have_sustain"),
            (self.release_cb, "have_release"),
            (self.tone_cb, "have_tone"),
            (self.chorus_cb, "have_chorus"),
            (self.reverb_cb, "have_reverb"),
            (self.midicc1_cb, "have_midicc1"),
        ]:
            layout.addWidget(cb)
            cb.stateChanged.connect(lambda state, n=name, c=cb: self._option_changed(n, not c.isChecked(), c.isChecked()))

        # Cut group options
        self.cutgroup_cb = QCheckBox("Cut all by all")
        layout.addWidget(self.cutgroup_cb)
        self.cutgroup_cb.stateChanged.connect(lambda state: self._option_changed("cut_all_by_all", not self.cutgroup_cb.isChecked(), self.cutgroup_cb.isChecked()))
        silencing_layout = QHBoxLayout()
        silencing_layout.addWidget(QLabel("Silencing Mode:"))
        self.silencing_combo = QComboBox()
        self.silencing_combo.addItems(["normal", "fast"])
        silencing_layout.addWidget(self.silencing_combo)
        layout.addLayout(silencing_layout)
        self.silencing_combo.currentTextChanged.connect(lambda val: self._option_changed("silencing_mode", self._last_silencing_mode, val))
        self._last_silencing_mode = "normal"

        self.setLayout(layout)

    def browse_bg(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Background Image", "", "PNG Files (*.png)")
        if file:
            old = self.bg_edit.text()
            self.bg_edit.setText(file)
            self._option_changed("bg_image", old, file)

    def get_options(self):
        return {
            "bg_image": self.bg_edit.text(),
            "have_attack": self.attack_cb.isChecked(),
            "have_decay": self.decay_cb.isChecked(),
            "have_sustain": self.sustain_cb.isChecked(),
            "have_release": self.release_cb.isChecked(),
            "have_tone": self.tone_cb.isChecked(),
            "have_chorus": self.chorus_cb.isChecked(),
            "have_reverb": self.reverb_cb.isChecked(),
            "have_midicc1": self.midicc1_cb.isChecked(),
            "cut_all_by_all": self.cutgroup_cb.isChecked(),
            "silencing_mode": self.silencing_combo.currentText()
        }

    def _option_changed(self, name, old, new):
        if old == new:
            return
        # Push undo command to main window's undo stack
        if hasattr(self.main_window, "undo_stack") and hasattr(self.main_window, "preset"):
            cmd = GlobalOptionEditCommand(
                self.main_window.preset, name, old, new, update_callback=self.main_window._set_options_panel_from_preset
            )
            self.main_window.undo_stack.push(cmd)
        # Update last value for next change
        if name == "bg_image":
            self._last_bg_image = new
        elif name == "silencing_mode":
            self._last_silencing_mode = new
