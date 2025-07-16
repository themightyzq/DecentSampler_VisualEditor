from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QSpinBox, QPushButton, QColorDialog, QFileDialog, QHBoxLayout, QCheckBox,
    QGroupBox, QDoubleSpinBox, QComboBox, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter, QColor

from utils.effects_catalog import EFFECTS_CATALOG

from PyQt5.QtWidgets import QDialog, QDialogButtonBox

class AddControlDialog(QDialog):
    def __init__(self, parent=None, existing_controls=None, edit_index=None):
        super().__init__(parent)
        self.setWindowTitle("Add DSP Control")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.existing_controls = existing_controls or []
        self.edit_index = edit_index
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")

        # Only allow these effect types
        self.effect_names = [
            "Reverb", "Delay", "Chorus", "Phaser", "Convolution",
            "Lowpass", "Highpass", "Bandpass", "Notch", "Peak", "Gain", "Wave Folder"
        ]
        self.widget_types = ["Knob", "Slider"]

        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        # Label
        self.label_edit = QLineEdit()
        self.label_edit.setMaxLength(12)
        self.form_layout.addRow("Label:", self.label_edit)

        # Effect type dropdown
        self.effect_combo = QComboBox()
        self.effect_combo.addItems(self.effect_names)
        self.effect_combo.currentIndexChanged.connect(self._update_param_dropdown)
        self.form_layout.addRow("Effect Type:", self.effect_combo)

        # Parameter dropdown (updates based on effect)
        self.param_combo = QComboBox()
        self.form_layout.addRow("Parameter:", self.param_combo)

        # Control type dropdown
        self.widget_combo = QComboBox()
        self.widget_combo.addItems(self.widget_types)
        self.form_layout.addRow("Control Type:", self.widget_combo)

        # X/Y position
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 2000)
        self.x_spin.setValue(100)
        self.form_layout.addRow("X Position:", self.x_spin)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 2000)
        self.y_spin.setValue(100)
        self.form_layout.addRow("Y Position:", self.y_spin)

        # Width/Height
        self.width_spin = QSpinBox()
        self.width_spin.setRange(16, 512)
        self.width_spin.setValue(64)
        self.form_layout.addRow("Width:", self.width_spin)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(16, 512)
        self.height_spin.setValue(64)
        self.form_layout.addRow("Height:", self.height_spin)

        # Min/Max/Default value
        self.min_spin = QDoubleSpinBox()
        self.min_spin.setRange(-99999, 99999)
        self.min_spin.setValue(0.0)
        self.min_spin.setSingleStep(0.01)
        self.min_spin.valueChanged.connect(self._update_default_value)
        self.form_layout.addRow("Min Value:", self.min_spin)

        self.max_spin = QDoubleSpinBox()
        self.max_spin.setRange(-99999, 99999)
        self.max_spin.setValue(1.0)
        self.max_spin.setSingleStep(0.01)
        self.max_spin.valueChanged.connect(self._update_default_value)
        self.form_layout.addRow("Max Value:", self.max_spin)

        self.default_spin = QDoubleSpinBox()
        self.default_spin.setRange(-99999, 99999)
        self.default_spin.setValue(0.5)
        self.default_spin.setSingleStep(0.01)
        self.form_layout.addRow("Default Value:", self.default_spin)

        # MIDI CC (optional)
        self.midi_cc_spin = QSpinBox()
        self.midi_cc_spin.setRange(-1, 127)
        self.midi_cc_spin.setValue(-1)
        self.midi_cc_spin.setSpecialValueText("None")
        self.form_layout.addRow("MIDI CC (optional):", self.midi_cc_spin)

        # Orientation (for sliders only)
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["horizontal", "vertical"])
        self.form_layout.addRow("Slider Orientation:", self.orientation_combo)
        self.orientation_combo.setVisible(False)
        self.widget_combo.currentTextChanged.connect(self._on_widget_type_changed)
        self._on_widget_type_changed(self.widget_combo.currentText())

        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.error_label)

        # Dialog buttons
        buttons = QDialogButtonBox()
        self.create_btn = buttons.addButton("Create", QDialogButtonBox.AcceptRole)
        self.cancel_btn = buttons.addButton("Cancel", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)
        self.setLayout(self.layout)

        self._update_param_dropdown()
        self._update_default_value()

    def _validate_and_accept(self):
        # Reset error state
        self.error_label.setText("")
        for widget in [self.label_edit, self.min_spin, self.max_spin, self.default_spin]:
            widget.setStyleSheet("")
        valid = True
        errors = []

        label = self.label_edit.text().strip()
        effect = self.effect_combo.currentText()
        param = self.param_combo.currentText()
        min_val = self.min_spin.value()
        max_val = self.max_spin.value()
        default_val = self.default_spin.value()

        # Check for duplicate Label+Effect+Parameter
        for idx, ctrl in enumerate(self.existing_controls):
            if self.edit_index is not None and idx == self.edit_index:
                continue
            if (
                getattr(ctrl, "label", "") == label and
                getattr(ctrl, "effect_type", "") == effect and
                getattr(ctrl, "parameter", "") == param
            ):
                valid = False
                errors.append("Duplicate Label + Effect Type + Parameter.")
                self.label_edit.setStyleSheet("background-color: #ffcccc;")
                break

        # Min < Max
        if min_val >= max_val:
            valid = False
            errors.append("Min must be less than Max.")
            self.min_spin.setStyleSheet("background-color: #ffcccc;")
            self.max_spin.setStyleSheet("background-color: #ffcccc;")

        # Default in range
        if not (min_val <= default_val <= max_val):
            valid = False
            errors.append("Default Value must be within Min–Max range.")
            self.default_spin.setStyleSheet("background-color: #ffcccc;")

        if not label:
            valid = False
            errors.append("Label is required.")
            self.label_edit.setStyleSheet("background-color: #ffcccc;")

        if not valid:
            self.error_label.setText("\n".join(errors))
            return
        self.accept()

    def _on_widget_type_changed(self, widget_type):
        # Show orientation only for sliders
        self.orientation_combo.setVisible(widget_type.lower() == "slider")

    def _update_param_dropdown(self):
        self.param_combo.clear()
        effect = self.effect_combo.currentText()
        if not effect:
            return
        # Use "simple" params by default
        param_defs = EFFECTS_CATALOG.get(effect, {}).get("simple", [])
        param_names = [param["name"] for param in param_defs]
        self.param_combo.addItems(param_names)
        # Optionally update min/max/default based on first param
        if param_defs:
            p = param_defs[0]
            self.min_spin.setValue(p.get("min", 0.0))
            self.max_spin.setValue(p.get("max", 1.0))
            midpoint = (self.min_spin.value() + self.max_spin.value()) / 2.0
            self.default_spin.setValue(p.get("default", midpoint))
        self._update_default_value()

    def _update_default_value(self):
        min_val = self.min_spin.value()
        max_val = self.max_spin.value()
        midpoint = (min_val + max_val) / 2.0
        if self.default_spin.value() < min_val or self.default_spin.value() > max_val:
            self.default_spin.setValue(midpoint)

class ProjectPropertiesPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Use consistent header styling
        try:
            from utils.ui_consistency import UIStyler
            self.setWindowTitle("")  # Remove default title
            # We'll add a proper header widget instead
        except ImportError:
            self.setWindowTitle("Project Properties")
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Add consistent header
        try:
            from utils.ui_consistency import UIStyler
            header = UIStyler.create_header_label("Project Properties", "Configure preset name, dimensions, colors, and effects")
            layout.addWidget(header)
        except ImportError:
            pass

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
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(8)
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

        # Simple/Advanced toggle
        # Mini envelope plot
        # (Removed duplicate MiniEnvelopePlot from the form layout to avoid duplicate previews)
        # (This duplicate class and instantiation have been removed to fix the set_adsr signature error)

        # (Advanced Mode UI removed)

        # Controls sub-panel: widget type selectors for each effect
        controls_group = QGroupBox("Effects Controls")
        self.controls_layout = QVBoxLayout()
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_layout.setSpacing(0)
        controls_group.setLayout(self.controls_layout)
        form_layout.addRow(controls_group)

        layout.addLayout(form_layout)
        widget.setLayout(layout)
        self.setWidget(widget)

        # State for effect controls
        self.effect_names = list(EFFECTS_CATALOG.keys())
        self.adsr_names = ["Attack", "Decay", "Sustain", "Release"]
        self.widget_types = ["Knob", "Slider"]
        self.widget_type_combos = {}
        self.x_spinboxes = {}
        self.y_spinboxes = {}
        self.enable_checkboxes = {}
        self.checked_state = {}  # Store checked state for all controls

        # Build effect controls
        self._rebuild_effect_controls()

        # Connect live update signals for all properties
        self.preset_name_edit.textChanged.connect(self._live_update)
        self.ui_width_spin.valueChanged.connect(self._live_update)
        self.ui_height_spin.valueChanged.connect(self._live_update)
        self.bg_image_edit.textChanged.connect(self._live_update)
        # (ADSR signal connections removed)

    def _rebuild_effect_controls(self):
        # Remove all widgets from the layout
        while self.controls_layout.count():
            item = self.controls_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Header row
        header_row = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 0, 8, 0)
        header_layout.setSpacing(8)
        header_labels = ["Label", "X", "Y", "Width", "Height", "Edit"]
        for text in header_labels:
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight: bold;")
            lbl.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(lbl)
        header_row.setLayout(header_layout)
        self.controls_layout.addWidget(header_row)

        # Add a row for each control element
        mw = self.parent()
        if hasattr(mw, "preset") and hasattr(mw.preset, "ui") and hasattr(mw.preset.ui, "elements"):
            # Exclude ADSR controls from the populated control element list
            filtered_elements = [
                el for el in mw.preset.ui.elements
                if str(getattr(el, "label", "")).lower() not in ["attack", "decay", "sustain", "release"]
            ]
            for idx, el in enumerate(filtered_elements):
                row_widget = QWidget()
                row_layout = QHBoxLayout()
                row_layout.setContentsMargins(8, 2, 8, 2)
                row_layout.setSpacing(8)
                row_widget.setStyleSheet("""
                    background: #f7f7fa;
                    border: 1px solid #e0e0e0;
                """)

                # Label (not editable here, truncated to 12 chars with ellipsis)
                label_val = str(getattr(el, "label", ""))
                if len(label_val) > 12:
                    label_val = label_val[:9] + "..."
                label_widget = QLabel(label_val)
                label_widget.setMinimumWidth(100)
                label_widget.setMaximumWidth(120)
                label_widget.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                row_layout.addWidget(label_widget)

                # X position (editable)
                x_spin = QSpinBox()
                x_spin.setRange(0, 812)
                x_spin.setValue(getattr(el, "x", 0))
                x_spin.setMinimumWidth(48)
                x_spin.setMaximumWidth(56)
                x_spin.setAlignment(Qt.AlignVCenter)
                x_spin.valueChanged.connect(lambda value, i=idx: self._update_control_property(i, "x", value))
                row_layout.addWidget(x_spin)

                # Y position (editable)
                y_spin = QSpinBox()
                y_spin.setRange(0, 812)
                y_spin.setValue(getattr(el, "y", 0))
                y_spin.setMinimumWidth(48)
                y_spin.setMaximumWidth(56)
                y_spin.setAlignment(Qt.AlignVCenter)
                y_spin.valueChanged.connect(lambda value, i=idx: self._update_control_property(i, "y", value))
                row_layout.addWidget(y_spin)

                # Width (editable)
                width_spin = QSpinBox()
                width_spin.setRange(16, 812)
                width_spin.setValue(getattr(el, "width", 64))
                width_spin.setMinimumWidth(48)
                width_spin.setMaximumWidth(56)
                width_spin.setAlignment(Qt.AlignVCenter)
                width_spin.valueChanged.connect(lambda value, i=idx: self._update_control_property(i, "width", value))
                row_layout.addWidget(width_spin)

                # Height (editable)
                height_spin = QSpinBox()
                height_spin.setRange(16, 812)
                height_spin.setValue(getattr(el, "height", 64))
                height_spin.setMinimumWidth(48)
                height_spin.setMaximumWidth(56)
                height_spin.setAlignment(Qt.AlignVCenter)
                height_spin.valueChanged.connect(lambda value, i=idx: self._update_control_property(i, "height", value))
                row_layout.addWidget(height_spin)

                # Edit and Remove buttons (truly square, E/X centered, 4px margin)
                edit_btn = QPushButton("E")
                edit_btn.setFixedSize(28, 28)
                edit_btn.setToolTip("Edit")
                edit_btn.setStyleSheet("""
                    font-size: 16px; font-weight: bold; text-align: center;
                    background: #e6eaff;
                """)
                edit_btn.clicked.connect(lambda _, i=idx: self._edit_control(i))
                del_btn = QPushButton("✖")
                del_btn.setFixedSize(28, 28)
                del_btn.setToolTip("Delete")
                del_btn.setStyleSheet("""
                    font-size: 16px; font-weight: bold; text-align: center;
                    background: #ffeaea;
                    margin-left: 4px;
                """)
                del_btn.clicked.connect(lambda _, i=idx: self._delete_control(i))
                btns_widget = QWidget()
                btns_layout = QHBoxLayout()
                btns_layout.setContentsMargins(0, 0, 0, 0)
                btns_layout.setSpacing(4)
                btns_layout.addWidget(edit_btn)
                btns_layout.addWidget(del_btn)
                btns_widget.setLayout(btns_layout)
                btns_widget.setMaximumWidth(68)
                btns_widget.setMinimumWidth(60)
                row_layout.addWidget(btns_widget)

                row_widget.setLayout(row_layout)
                self.controls_layout.addWidget(row_widget)

        # Add vertical spacing (24px) before the "Add Control" button
        self.controls_layout.addSpacing(24)
        self.add_control_btn = QPushButton("Add Control")
        self.add_control_btn.setMinimumHeight(28)
        self.add_control_btn.setStyleSheet("font-size: 13px;")
        self.add_control_btn.clicked.connect(self._open_add_control_modal)
        self.controls_layout.addWidget(self.add_control_btn)
        # Set the properties panel width to a compact value
        self.setMinimumWidth(380)
        self.setMaximumWidth(420)

    def _update_control_property(self, idx, prop, value):
        mw = self.parent()
        if hasattr(mw, "preset") and hasattr(mw.preset, "ui") and hasattr(mw.preset.ui, "elements"):
            elements = mw.preset.ui.elements
            if 0 <= idx < len(elements):
                setattr(elements[idx], prop, value)
                if hasattr(mw, "preview_canvas"):
                    mw.preview_canvas.set_preset(mw.preset, "")
        # No need to call _rebuild_effect_controls() here to avoid losing focus on spinboxes

    def _open_add_control_modal(self):
        mw = self.parent()
        existing_controls = []
        if hasattr(mw, "preset") and hasattr(mw.preset, "ui") and hasattr(mw.preset.ui, "elements"):
            existing_controls = mw.preset.ui.elements
        dialog = AddControlDialog(self, existing_controls=existing_controls)
        if dialog.exec_() == QDialog.Accepted:
            label = dialog.label_edit.text()
            effect = dialog.effect_combo.currentText()
            param = dialog.param_combo.currentText()
            widget_type = dialog.widget_combo.currentText()
            x = dialog.x_spin.value()
            y = dialog.y_spin.value()
            width = dialog.width_spin.value()
            height = dialog.height_spin.value()
            min_val = dialog.min_spin.value()
            max_val = dialog.max_spin.value()
            default_val = dialog.default_spin.value()
            midi_cc = dialog.midi_cc_spin.value()
            if midi_cc == -1:
                midi_cc = None
            orientation = dialog.orientation_combo.currentText() if widget_type.lower() == "slider" else None
            self._add_new_control(
                label=label,
                effect=effect,
                param=param,
                widget_type=widget_type,
                x=x,
                y=y,
                width=width,
                height=height,
                min_val=min_val,
                max_val=max_val,
                default_val=default_val,
                midi_cc=midi_cc,
                orientation=orientation
            )

    def _add_new_control(self, label, effect, param, widget_type, x, y, width, height, min_val, max_val, default_val, edit_index=None, midi_cc=None, orientation=None):
        # Add or update the control in the model and UI
        from model import UIElement
        mw = self.parent()
        if hasattr(mw, "preset") and hasattr(mw.preset, "ui") and hasattr(mw.preset.ui, "elements"):
            if edit_index is not None:
                # Edit existing control
                el = mw.preset.ui.elements[edit_index]
                el.x = x
                el.y = y
                el.width = width
                el.height = height
                el.label = label
                el.tag = widget_type
                el.widget_type = widget_type
                el.effect_type = effect
                el.parameter = param
                el.min = min_val
                el.max = max_val
                el.default = default_val
            else:
                # Add new control
                # Build binding for amp/ADSR or effect
                bindings = []
                if label.lower() in ["attack", "decay", "sustain", "release"]:
                    param_map = {
                        "attack": "ENV_ATTACK",
                        "decay": "ENV_DECAY",
                        "sustain": "ENV_SUSTAIN",
                        "release": "ENV_RELEASE"
                    }
                    param_name = param_map[label.lower()]
                    binding = {
                        "type": "amp",
                        "level": "instrument",
                        "position": "0",
                        "parameter": param_name
                    }
                    bindings = [binding]
                    target = param_name
                elif effect and param:
                    # Map to DecentSampler parameter using EFFECTS_CATALOG
                    from utils.effects_catalog import EFFECTS_CATALOG
                    ds_param = None
                    if effect in EFFECTS_CATALOG:
                        param_defs = EFFECTS_CATALOG[effect].get("simple", []) + EFFECTS_CATALOG[effect].get("advanced", [])
                        for pdef in param_defs:
                            if pdef["name"] == param and "ds_param" in pdef:
                                ds_param = pdef["ds_param"]
                                break
                        if not ds_param:
                            ds_param = param
                    else:
                        ds_param = param
                    # Find effect index (position) in preset.effects
                    effect_index = 0
                    for idx, (ename, params) in enumerate(getattr(mw.preset, "effects", {}).items()):
                        if ename.lower() == effect.lower():
                            effect_index = idx
                            break
                    binding = {
                        "type": "effect",
                        "level": "instrument",
                        "position": str(effect_index),
                        "parameter": ds_param,
                        "effectType": EFFECTS_CATALOG[effect]["type"] if effect in EFFECTS_CATALOG else effect.lower(),
                        "translation": "linear",
                        "translationOutputMin": 0,
                        "translationOutputMax": 1
                    }
                    bindings = [binding]
                    target = ds_param
                else:
                    bindings = []
                    target = None

                # Set tag to "labeled-slider" for sliders, "labeled-knob" for knobs
                tag_value = "labeled-slider" if widget_type.lower() == "slider" else "labeled-knob"
                el = UIElement(
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    label=label,
                    skin=None,
                    tag=tag_value,
                    widget_type=widget_type,
                    target=target,
                    min_val=min_val,
                    max_val=max_val,
                    bindings=bindings,
                    midi_cc=midi_cc,
                    orientation=orientation
                )
                el.effect_type = effect
                el.parameter = param
                el.min = min_val
                el.max = max_val
                el.default = default_val
                mw.preset.ui.elements.append(el)
            if hasattr(mw, "preview_canvas"):
                mw.preview_canvas.set_preset(mw.preset, "")
            self._rebuild_effect_controls()
        # Optionally, refresh the controls panel or UI as needed
        # self._rebuild_effect_controls()

    # (Advanced mode methods removed)

    def _clear_advanced_controls_list(self):
        while self.advanced_controls_layout.count():
            item = self.advanced_controls_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _refresh_advanced_controls_list(self):
        self._clear_advanced_controls_list()
        mw = self.parent()
        if not (hasattr(mw, "preset") and hasattr(mw.preset, "ui") and hasattr(mw.preset.ui, "elements")):
            return
        for idx, el in enumerate(mw.preset.ui.elements):
            row = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(6)
            # Enable/disable checkbox
            enable_checkbox = QCheckBox()
            # Default to enabled if not present
            is_enabled = getattr(el, "enabled", True)
            enable_checkbox.setChecked(is_enabled)
            enable_checkbox.stateChanged.connect(lambda state, i=idx: self._toggle_control_enabled(i, state))
            row_layout.addWidget(enable_checkbox)
            # Label
            row_layout.addWidget(QLabel(str(getattr(el, "label", ""))))
            # Effect Type
            row_layout.addWidget(QLabel(str(getattr(el, "effect_type", ""))))
            # Parameter
            row_layout.addWidget(QLabel(str(getattr(el, "parameter", ""))))
            # Control Type
            row_layout.addWidget(QLabel(str(getattr(el, "widget_type", ""))))
            # X/Y
            row_layout.addWidget(QLabel(f"({getattr(el, 'x', 0)}, {getattr(el, 'y', 0)})"))
            # Edit icon
            edit_btn = QPushButton("✎")
            edit_btn.setFixedWidth(28)
            edit_btn.setToolTip("Edit")
            edit_btn.clicked.connect(lambda _, i=idx: self._edit_control(i))
            row_layout.addWidget(edit_btn)
            # Delete icon
            del_btn = QPushButton("🗑")
            del_btn.setFixedWidth(28)
            del_btn.setToolTip("Delete")
            del_btn.clicked.connect(lambda _, i=idx: self._delete_control(i))
            row_layout.addWidget(del_btn)
            row.setLayout(row_layout)
            self.advanced_controls_layout.addWidget(row)

    def _toggle_control_enabled(self, idx, state):
        mw = self.parent()
        if not (hasattr(mw, "preset") and hasattr(mw.preset, "ui") and hasattr(mw.preset.ui, "elements")):
            return
        elements = mw.preset.ui.elements
        if 0 <= idx < len(elements):
            el = elements[idx]
            if state == Qt.Checked:
                el.enabled = True
            else:
                el.enabled = False
        # Remove disabled controls from elements
        mw.preset.ui.elements = [el for el in elements if getattr(el, "enabled", True)]
        if hasattr(mw, "preview_canvas"):
            mw.preview_canvas.set_preset(mw.preset, "")
        self._rebuild_effect_controls()

    def _edit_control(self, idx):
        mw = self.parent()
        if not (hasattr(mw, "preset") and hasattr(mw.preset, "ui") and hasattr(mw.preset.ui, "elements")):
            return
        el = mw.preset.ui.elements[idx]
        dialog = AddControlDialog(
            self,
            existing_controls=mw.preset.ui.elements,
            edit_index=idx
        )
        # Pre-fill dialog with current values
        dialog.label_edit.setText(str(getattr(el, "label", "")))
        effect_type = getattr(el, "effect_type", "Reverb")
        if effect_type in dialog.effect_names:
            dialog.effect_combo.setCurrentText(effect_type)
        dialog._update_param_dropdown()
        param = getattr(el, "parameter", "")
        if param in [dialog.param_combo.itemText(i) for i in range(dialog.param_combo.count())]:
            dialog.param_combo.setCurrentText(param)
        dialog.widget_combo.setCurrentText(str(getattr(el, "widget_type", "Knob")))
        dialog.x_spin.setValue(getattr(el, "x", 0))
        dialog.y_spin.setValue(getattr(el, "y", 0))
        dialog.min_spin.setValue(getattr(el, "min", 0.0))
        dialog.max_spin.setValue(getattr(el, "max", 1.0))
        dialog.default_spin.setValue(getattr(el, "default", 0.5))
        if dialog.exec_() == QDialog.Accepted:
            label = dialog.label_edit.text()
            effect = dialog.effect_combo.currentText()
            param = dialog.param_combo.currentText()
            widget_type = dialog.widget_combo.currentText()
            x = dialog.x_spin.value()
            y = dialog.y_spin.value()
            width = dialog.width_spin.value() if hasattr(dialog, "width_spin") else getattr(el, "width", 64)
            height = dialog.height_spin.value() if hasattr(dialog, "height_spin") else getattr(el, "height", 64)
            min_val = dialog.min_spin.value()
            max_val = dialog.max_spin.value()
            default_val = dialog.default_spin.value()
            midi_cc = dialog.midi_cc_spin.value() if hasattr(dialog, "midi_cc_spin") else getattr(el, "midi_cc", None)
            if midi_cc == -1:
                midi_cc = None
            orientation = dialog.orientation_combo.currentText() if hasattr(dialog, "orientation_combo") and widget_type.lower() == "slider" else getattr(el, "orientation", None)
            self._add_new_control(
                label=label,
                effect=effect,
                param=param,
                widget_type=widget_type,
                x=x,
                y=y,
                width=width,
                height=height,
                min_val=min_val,
                max_val=max_val,
                default_val=default_val,
                edit_index=idx,
                midi_cc=midi_cc,
                orientation=orientation
            )

    def _delete_control(self, idx):
        mw = self.parent()
        if not (hasattr(mw, "preset") and hasattr(mw.preset, "ui") and hasattr(mw.preset.ui, "elements")):
            return
        del mw.preset.ui.elements[idx]
        if hasattr(mw, "preview_canvas"):
            mw.preview_canvas.set_preset(mw.preset, "")
        self._rebuild_effect_controls()

    def set_flags_from_preset(self, preset):
        # Set effect checkboxes from preset
        for name in self.adsr_names + self.effect_names:
            if name in self.enable_checkboxes:
                checked = getattr(preset, f"have_{name.lower()}", False) if name in ["Reverb", "Tone", "Chorus"] else True
                self.enable_checkboxes[name].setChecked(checked)
        # Set ADSR preview from envelope if present
        env = getattr(preset, "envelope", None)
        if env:
            self.env_plot.set_adsr(getattr(env, "attack", 0.01), getattr(env, "decay", 0.01), getattr(env, "sustain", 1.0), getattr(env, "release", 0.01))

    def _on_adsr_control_changed(self):
        # Update preview and sync enabled ADSR controls to preset.ui.elements
        enabled = [
            self.attack_checkbox.isChecked(),
            self.decay_checkbox.isChecked(),
            self.sustain_checkbox.isChecked(),
            self.release_checkbox.isChecked(),
        ]
        self.env_plot.set_adsr(
            self.attack_spin.value(),
            self.decay_spin.value(),
            self.sustain_spin.value(),
            self.release_spin.value(),
            enabled=enabled
        )
        self._sync_adsr_controls_to_elements()

    def _sync_adsr_controls_to_elements(self):
        # Ensure enabled ADSR controls are present in preset.ui.elements, with correct type and position
        mw = self.parent()
        if not (hasattr(mw, "preset") and hasattr(mw.preset, "ui") and hasattr(mw.preset.ui, "elements")):
            return
        elements = mw.preset.ui.elements
        adsr_names = ["Attack", "Decay", "Sustain", "Release"]
        spins = [self.attack_spin, self.decay_spin, self.sustain_spin, self.release_spin]
        checkboxes = [self.attack_checkbox, self.decay_checkbox, self.sustain_checkbox, self.release_checkbox]
        for i, name in enumerate(adsr_names):
            # Remove any existing element for this ADSR if present
            elements[:] = [el for el in elements if el.label != name]
            if checkboxes[i].isChecked():
                # Add UIElement for enabled ADSR
                widget_type = self.adsr_widget_types[name].currentText()
                orientation = self.adsr_orientations[name].currentText() if widget_type.lower() == "slider" else None
                x = self.adsr_x_spins[name].value()
                y = self.adsr_y_spins[name].value()
                value = spins[i].value()
                el = type("UIElement", (), {})()  # Dummy UIElement if import fails
                try:
                    from model import UIElement as RealUIElement
                    tag_value = "labeled-slider" if widget_type.lower() == "slider" else "labeled-knob"
                    el = RealUIElement(
                        x=x,
                        y=y,
                        width=64,
                        height=64,
                        label=name,
                        skin=None,
                        tag=tag_value,
                        widget_type=widget_type,
                        orientation=orientation
                    )
                except Exception:
                    el.x = x
                    el.y = y
                    el.width = 64
                    el.height = 64
                    el.label = name
                    el.skin = None
                    el.tag = "labeled-slider" if widget_type.lower() == "slider" else "labeled-knob"
                    el.widget_type = widget_type
                    el.orientation = orientation
                el.effect_type = None
                el.parameter = None
                el.min = 0.0
                el.max = 1.0
                el.default = value
                # Set DecentSampler target and binding for standard envelope controls
                if name == "Attack":
                    el.target = "ENV_ATTACK"
                    el.bindings = [{
                        "type": "amp",
                        "level": "instrument",
                        "position": "0",
                        "parameter": "ENV_ATTACK"
                    }]
                elif name == "Decay":
                    el.target = "ENV_DECAY"
                    el.bindings = [{
                        "type": "amp",
                        "level": "instrument",
                        "position": "0",
                        "parameter": "ENV_DECAY"
                    }]
                elif name == "Sustain":
                    el.target = "ENV_SUSTAIN"
                    el.bindings = [{
                        "type": "amp",
                        "level": "instrument",
                        "position": "0",
                        "parameter": "ENV_SUSTAIN"
                    }]
                elif name == "Release":
                    el.target = "ENV_RELEASE"
                    el.bindings = [{
                        "type": "amp",
                        "level": "instrument",
                        "position": "0",
                        "parameter": "ENV_RELEASE"
                    }]
                elements.append(el)
        if hasattr(mw, "preview_canvas"):
            mw.preview_canvas.set_preset(mw.preset, "")

    def _flag_update(self):
        mw = self.parent()
        if hasattr(mw, "preset"):
            # Set effect flags from checkboxes (for legacy compatibility)
            for name in ["Reverb", "Tone", "Chorus"]:
                if name in self.enable_checkboxes:
                    setattr(mw.preset, f"have_{name.lower()}", self.enable_checkboxes[name].isChecked())
            # Add/remove UIElements for each effect
            from model import UIElement
            effect_map = {name: self.enable_checkboxes[name].isChecked() for name in self.adsr_names + self.effect_names}
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
                            x=self.x_spinboxes[effect].value(),
                            y=self.y_spinboxes[effect].value(),
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

    def _on_enable_checkbox(self, effect, state):
        # Unified handler for all enable checkboxes (ADSR and effects)
        self.checked_state[effect] = (state == 2)
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
        # After updating model/preview, rebuild controls to show/hide parameter controls
        self._rebuild_effect_controls()

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
            # No longer update envelope from spinboxes (they were removed)
        if hasattr(mw, "preview_canvas") and hasattr(mw, "preset"):
            # Resize preview_canvas and keyboard_widget if needed
            mw.preview_canvas.setFixedSize(mw.preset.ui_width, mw.preset.ui_height)
            if hasattr(mw, "keyboard_widget"):
                mw.keyboard_widget.setFixedWidth(mw.preset.ui_width)
            mw.preview_canvas.set_preset(mw.preset, "")

    # def _adsr_update(self):
    #     # Called when any ADSR spinbox changes
    #     a = self.attack_spin.value()
    #     d = self.decay_spin.value()
    #     s = self.sustain_spin.value()
    #     r = self.release_spin.value()
    #     self.env_plot.set_adsr(a, d, s, r)
    #     self._live_update()

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
            "cut_all_by_all": False,
            "silencing_mode": "normal",
            "widget_types": {effect: combo.currentText() for effect, combo in self.widget_type_combos.items()},
        }
