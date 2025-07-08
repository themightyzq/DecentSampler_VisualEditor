from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QSpinBox, QPushButton, QColorDialog, QFileDialog, QHBoxLayout, QCheckBox,
    QGroupBox, QDoubleSpinBox, QComboBox, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter, QColor

class ProjectPropertiesPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Project Properties", parent)
        widget = QWidget()
        layout = QVBoxLayout()

        # Preset name
        self.preset_name_edit = QLineEdit()
        self.preset_name_edit.setToolTip("Name of the current preset")
        # UI width/height
        self.ui_width_spin = QSpinBox()
        self.ui_width_spin.setRange(100, 2000)
        self.ui_width_spin.setValue(812)
        self.ui_width_spin.setToolTip("UI width in pixels (100–2000)")
        self.ui_height_spin = QSpinBox()
        self.ui_height_spin.setRange(100, 2000)
        self.ui_height_spin.setValue(375)
        self.ui_height_spin.setToolTip("UI height in pixels (100–2000)")

        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Preset Name:"), self.preset_name_edit)
        form_layout.addRow(QLabel("UI Width:"), self.ui_width_spin)
        form_layout.addRow(QLabel("UI Height:"), self.ui_height_spin)

        # Background color
        self.bg_color_btn = QPushButton("Pick BG Color")
        self.bg_color_btn.setToolTip("Select background color for the preset")
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        self.bg_color_edit = QLineEdit(self)
        self.bg_color_edit.setVisible(False)
        form_layout.addRow(QLabel("BG Color:"), self.bg_color_btn)

        # Background image
        self.bg_image_edit = QLineEdit()
        self.bg_image_edit.setToolTip("Path to background image file")
        self.bg_image_btn = QPushButton("Browse BG Image...")
        self.bg_image_btn.setToolTip("Select background image for the preset")
        self.bg_image_btn.clicked.connect(self.browse_bg)
        form_layout.addRow(QLabel("BG Image:"), self.bg_image_edit)
        form_layout.addRow("", self.bg_image_btn)

        # (Effect toggle buttons removed; all controls now in the unified controls panel below)
        # ADSR controls
        # (imports moved to top)
        adsr_group = QGroupBox("ADSR Envelope")
        adsr_layout = QHBoxLayout()
        self.attack_spin = QDoubleSpinBox()
        self.attack_spin.setRange(0.001, 10.0)
        self.attack_spin.setSingleStep(0.01)
        self.attack_spin.setDecimals(3)
        self.attack_spin.setSuffix(" s")
        self.attack_spin.setToolTip("Attack time (seconds)")
        self.decay_spin = QDoubleSpinBox()
        self.decay_spin.setRange(0.001, 10.0)
        self.decay_spin.setSingleStep(0.01)
        self.decay_spin.setDecimals(3)
        self.decay_spin.setSuffix(" s")
        self.decay_spin.setToolTip("Decay time (seconds)")
        self.sustain_spin = QDoubleSpinBox()
        self.sustain_spin.setRange(0.0, 1.0)
        self.sustain_spin.setSingleStep(0.01)
        self.sustain_spin.setDecimals(2)
        self.sustain_spin.setToolTip("Sustain level (0–1)")
        self.release_spin = QDoubleSpinBox()
        self.release_spin.setRange(0.001, 10.0)
        self.release_spin.setSingleStep(0.01)
        self.release_spin.setDecimals(3)
        self.release_spin.setSuffix(" s")
        self.release_spin.setToolTip("Release time (seconds)")
        adsr_layout.addWidget(QLabel("A:"))
        adsr_layout.addWidget(self.attack_spin)
        adsr_layout.addWidget(QLabel("D:"))
        adsr_layout.addWidget(self.decay_spin)
        adsr_layout.addWidget(QLabel("S:"))
        adsr_layout.addWidget(self.sustain_spin)
        adsr_layout.addWidget(QLabel("R:"))
        adsr_layout.addWidget(self.release_spin)
        adsr_group.setLayout(adsr_layout)
        form_layout.addRow(adsr_group)

        # Mini envelope plot
        class MiniEnvelopePlot(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setFixedSize(120, 60)
                self.attack = 0.01
                self.decay = 0.01
                self.sustain = 1.0
                self.release = 0.01
            def set_adsr(self, a, d, s, r):
                self.attack, self.decay, self.sustain, self.release = a, d, s, r
                self.update()
            def paintEvent(self, event):
                painter = QPainter(self)
                w, h = self.width(), self.height()
                margin = 10
                x0, y0 = margin, h - margin
                x1 = x0 + int(w * self.attack / (self.attack + self.decay + self.release + 0.01) * 0.4)
                x2 = x1 + int(w * self.decay / (self.attack + self.decay + self.release + 0.01) * 0.3)
                x3 = w - margin - int(w * self.release / (self.attack + self.decay + self.release + 0.01) * 0.3)
                y_top = margin
                y_sus = y0 - int((h - 2 * margin) * self.sustain * 0.7)
                points = [
                    (x0, y0),
                    (x1, y_top),
                    (x2, y_sus),
                    (x3, y_sus),
                    (w - margin, y0)
                ]
                painter.setPen(QColor(100, 100, 255))
                for i in range(len(points) - 1):
                    painter.drawLine(int(points[i][0]), int(points[i][1]), int(points[i+1][0]), int(points[i+1][1]))
                painter.setPen(Qt.black)
                painter.drawText(5, 15, "ADSR")
        self.env_plot = MiniEnvelopePlot()
        form_layout.addRow(self.env_plot)

        # Controls sub-panel: widget type selectors for each effect
        from PyQt5.QtWidgets import QComboBox, QGridLayout
        controls_group = QGroupBox("Controls")
        controls_layout = QGridLayout()
        self.effect_names = ["Reverb", "Tone", "Chorus"]
        self.adsr_names = ["Attack", "Decay", "Sustain", "Release"]
        self.widget_types = ["Knob", "Slider"]
        self.widget_type_combos = {}
        self.x_spinboxes = {}
        self.y_spinboxes = {}
        self.enable_checkboxes = {}

        all_names = self.adsr_names + self.effect_names
        for i, name in enumerate(all_names):
            from PyQt5.QtWidgets import QCheckBox
            row = i
            enable = QCheckBox()
            enable.setChecked(False)
            enable.setToolTip(f"Enable {name} control")
            controls_layout.addWidget(enable, row, 0)
            self.enable_checkboxes[name] = enable
            enable.stateChanged.connect(lambda state, eff=name: self._enable_update(eff, state))

            label = QLabel(name)
            controls_layout.addWidget(label, row, 1)
            combo = QComboBox()
            combo.addItems(self.widget_types)
            combo.setToolTip(f"Select widget type for {name} control")
            controls_layout.addWidget(combo, row, 2)
            self.widget_type_combos[name] = combo
            combo.currentIndexChanged.connect(self._widget_type_update)
            # X/Y position spinboxes
            x_spin = QSpinBox()
            x_spin.setRange(0, 2000)
            x_spin.setValue(100 + 80 * i)
            x_spin.setToolTip(f"X position for {name}")
            controls_layout.addWidget(QLabel("X:"), row, 3)
            controls_layout.addWidget(x_spin, row, 4)
            self.x_spinboxes[name] = x_spin
            x_spin.valueChanged.connect(lambda val, eff=name: self._xy_update(eff, "x", val))
            y_spin = QSpinBox()
            y_spin.setRange(0, 2000)
            y_spin.setValue(100)
            y_spin.setToolTip(f"Y position for {name}")
            controls_layout.addWidget(QLabel("Y:"), row, 5)
            controls_layout.addWidget(y_spin, row, 6)
            self.y_spinboxes[name] = y_spin
            y_spin.valueChanged.connect(lambda val, eff=name: self._xy_update(eff, "y", val))
        controls_group.setLayout(controls_layout)
        form_layout.addRow(controls_group)

        layout.addLayout(form_layout)

        widget.setLayout(layout)
        self.setWidget(widget)

        # Connect live update signals for all properties
        self.preset_name_edit.textChanged.connect(self._live_update)
        self.ui_width_spin.valueChanged.connect(self._live_update)
        self.ui_height_spin.valueChanged.connect(self._live_update)
        self.bg_image_edit.textChanged.connect(self._live_update)
        self.attack_spin.valueChanged.connect(self._adsr_update)
        self.decay_spin.valueChanged.connect(self._adsr_update)
        self.sustain_spin.valueChanged.connect(self._adsr_update)
        self.release_spin.valueChanged.connect(self._adsr_update)

    def set_flags_from_preset(self, preset):
        # Set effect checkboxes from preset
        for name in ["Reverb", "Tone", "Chorus"]:
            if name in self.enable_checkboxes:
                self.enable_checkboxes[name].setChecked(getattr(preset, f"have_{name.lower()}", False))
        # Set ADSR values
        env = getattr(preset, "envelope", None)
        if env:
            self.attack_spin.setValue(getattr(env, "attack", 0.01))
            self.decay_spin.setValue(getattr(env, "decay", 0.01))
            self.sustain_spin.setValue(getattr(env, "sustain", 1.0))
            self.release_spin.setValue(getattr(env, "release", 0.01))
            self.env_plot.set_adsr(getattr(env, "attack", 0.01), getattr(env, "decay", 0.01), getattr(env, "sustain", 1.0), getattr(env, "release", 0.01))

    def _flag_update(self):
        mw = self.parent()
        if hasattr(mw, "preset"):
            # Set effect flags from checkboxes (for legacy compatibility)
            for name in ["Reverb", "Tone", "Chorus"]:
                if name in self.enable_checkboxes:
                    setattr(mw.preset, f"have_{name.lower()}", self.enable_checkboxes[name].isChecked())
            # Add/remove UIElements for each effect
            from model import UIElement
            effect_map = {
                "Reverb": self.enable_checkboxes["Reverb"].isChecked(),
                "Tone": self.enable_checkboxes["Tone"].isChecked(),
                "Chorus": self.enable_checkboxes["Chorus"].isChecked(),
            }
            # Remove elements for effects that are now off
            mw.preset.ui.elements = [
                el for el in mw.preset.ui.elements
                if el.label not in effect_map or effect_map[el.label]
            ]
            # Add elements for effects that are now on and not present
            for effect, enabled in effect_map.items():
                if enabled and not any(el.label == effect for el in mw.preset.ui.elements):
                    widget_type = self.widget_type_combos[effect].currentText()
                    mw.preset.ui.elements.append(
                        UIElement(
                            x=100 + 80 * list(effect_map.keys()).index(effect),
                            y=100,
                            width=64,
                            height=64,
                            label=effect,
                            skin=None,
                            tag=widget_type,
                            widget_type=widget_type
                        )
                    )
        if hasattr(mw, "preview_canvas") and hasattr(mw, "preset"):
            mw.preview_canvas.set_preset(mw.preset, "")

    def _enable_update(self, effect, state):
        mw = self.parent()
        if hasattr(mw, "preset") and hasattr(mw.preset, "ui") and hasattr(mw.preset.ui, "elements"):
            enabled = state == 2
            # Remove if not enabled
            mw.preset.ui.elements = [el for el in mw.preset.ui.elements if el.label.lower() != effect.lower()]
            if enabled:
                from model import UIElement
                x = self.x_spinboxes[effect].value()
                y = self.y_spinboxes[effect].value()
                widget_type = self.widget_type_combos[effect].currentText()
                mw.preset.ui.elements.append(
                    UIElement(
                        x=x,
                        y=y,
                        width=64,
                        height=64,
                        label=effect,
                        skin=None,
                        tag=widget_type,
                        widget_type=widget_type
                    )
                )
            if hasattr(mw, "preview_canvas"):
                mw.preview_canvas.set_preset(mw.preset, "")

    def _widget_type_update(self):
        # Update preset.ui.elements with selected widget types
        mw = self.parent()
        if hasattr(mw, "preset") and hasattr(mw.preset, "ui") and hasattr(mw.preset.ui, "elements"):
            for effect, combo in self.widget_type_combos.items():
                for el in mw.preset.ui.elements:
                    if el.label.lower() == effect.lower():
                        el.widget_type = combo.currentText()
            if hasattr(mw, "preview_canvas"):
                mw.preview_canvas.set_preset(mw.preset, "")

    def _xy_update(self, effect, axis, value):
        mw = self.parent()
        if hasattr(mw, "preset") and hasattr(mw.preset, "ui") and hasattr(mw.preset.ui, "elements"):
            for el in mw.preset.ui.elements:
                if el.label.lower() == effect.lower():
                    if axis == "x":
                        el.x = value
                    elif axis == "y":
                        el.y = value
            if hasattr(mw, "preview_canvas"):
                mw.preview_canvas.set_preset(mw.preset, "")

    def browse_bg(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Background Image", "", "PNG Files (*.png)")
        if file:
            self.bg_image_edit.setText(file)
            self._live_update()

    def choose_bg_color(self):
        from PyQt5.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            self.bg_color_btn.setText(hex_color)
            self.bg_color_edit.setText(hex_color)
            self._live_update()

    def _live_update(self):
        mw = self.parent()
        if hasattr(mw, "preset"):
            mw.preset.name = self.preset_name_edit.text()
            mw.preset.ui_width = self.ui_width_spin.value()
            mw.preset.ui_height = self.ui_height_spin.value()
            mw.preset.bg_image = self.bg_image_edit.text()
            mw.preset.bg_color = self.bg_color_edit.text()
            for name in ["Reverb", "Tone", "Chorus"]:
                if name in self.enable_checkboxes:
                    setattr(mw.preset, f"have_{name.lower()}", self.enable_checkboxes[name].isChecked())
            # Update envelope if present
            if hasattr(mw.preset, "envelope"):
                mw.preset.envelope.attack = self.attack_spin.value()
                mw.preset.envelope.decay = self.decay_spin.value()
                mw.preset.envelope.sustain = self.sustain_spin.value()
                mw.preset.envelope.release = self.release_spin.value()
        if hasattr(mw, "preview_canvas") and hasattr(mw, "preset"):
            # Resize preview_canvas and keyboard_widget if needed
            mw.preview_canvas.setFixedSize(mw.preset.ui_width, mw.preset.ui_height)
            if hasattr(mw, "keyboard_widget"):
                mw.keyboard_widget.setFixedWidth(mw.preset.ui_width)
            mw.preview_canvas.set_preset(mw.preset, "")

    def _adsr_update(self):
        # Called when any ADSR spinbox changes
        a = self.attack_spin.value()
        d = self.decay_spin.value()
        s = self.sustain_spin.value()
        r = self.release_spin.value()
        self.env_plot.set_adsr(a, d, s, r)
        self._live_update()

    def get_options(self):
        """
        Returns a dictionary of all current preset options as shown in the panel.
        """
        return {
            "preset_name": self.preset_name_edit.text(),
            "ui_width": self.ui_width_spin.value(),
            "ui_height": self.ui_height_spin.value(),
            "bg_color": self.bg_color_edit.text(),
            "bg_image": self.bg_image_edit.text(),
            "have_reverb": self.enable_checkboxes["Reverb"].isChecked() if "Reverb" in self.enable_checkboxes else False,
            "have_tone": self.enable_checkboxes["Tone"].isChecked() if "Tone" in self.enable_checkboxes else False,
            "have_chorus": self.enable_checkboxes["Chorus"].isChecked() if "Chorus" in self.enable_checkboxes else False,
            "have_midicc1": False,
            "have_attack": True,
            "have_decay": True,
            "have_sustain": True,
            "have_release": True,
            "cut_all_by_all": False,
            "silencing_mode": "normal",
            "attack": self.attack_spin.value(),
            "decay": self.decay_spin.value(),
            "sustain": self.sustain_spin.value(),
            "release": self.release_spin.value(),
            "widget_types": {effect: combo.currentText() for effect, combo in self.widget_type_combos.items()},
        }
