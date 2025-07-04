from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QVBoxLayout, QLineEdit, QPushButton, QColorDialog, QLabel, QFileDialog, QComboBox, QDoubleSpinBox, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

class ProjectPropertiesWidget(QWidget):
    propertyChanged = pyqtSignal()
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window

        # Last-known values for undo/redo
        self._preset_name_last = ""
        self._min_version_last = ""
        self._plugin_version_last = ""
        self._cover_art_last = ""
        self._bg_image_last = ""
        self._bg_color_last = "#FFFFFFFF"
        self._text_color_last = "#FF000000"
        self._width_last = 812
        self._height_last = 375
        self._layout_mode_last = ""
        self._bg_mode_last = ""
        self._volume_last = 1.0
        self._global_tuning_last = 0.0
        self._glide_time_last = 0.0
        self._glide_mode_last = "legato"
        self._pan_last = 0.0
        self._amp_vel_track_last = 1.0

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Preset Name
        self.preset_name_edit = QLineEdit()
        self.preset_name_edit.setPlaceholderText("Enter preset name")
        self.preset_name_edit.setAccessibleName("Preset Name LineEdit")
        form_layout.addRow("Preset Name", self.preset_name_edit)

        # minVersion
        self.min_version_edit = QLineEdit()
        self.min_version_edit.setPlaceholderText("e.g. 1.0.0")
        self.min_version_edit.setAccessibleName("Min Version LineEdit")
        form_layout.addRow("Min Version", self.min_version_edit)

        # pluginVersion
        self.plugin_version_edit = QLineEdit()
        self.plugin_version_edit.setPlaceholderText("e.g. 1")
        self.plugin_version_edit.setAccessibleName("Plugin Version LineEdit")
        form_layout.addRow("Plugin Version", self.plugin_version_edit)

        # Cover Art
        cover_art_layout = QVBoxLayout()
        self.cover_art_edit = QLineEdit()
        self.cover_art_edit.setPlaceholderText("Path to cover art image")
        self.cover_art_edit.setAccessibleName("Cover Art LineEdit")
        self.cover_art_button = QPushButton("Browse...")
        cover_art_layout.addWidget(self.cover_art_edit)
        cover_art_layout.addWidget(self.cover_art_button)
        form_layout.addRow("Cover Art", cover_art_layout)

        # Background Image
        bg_image_layout = QVBoxLayout()
        self.bg_image_edit = QLineEdit()
        self.bg_image_edit.setPlaceholderText("Path to background image")
        self.bg_image_edit.setAccessibleName("Background Image LineEdit")
        self.bg_image_button = QPushButton("Browse...")
        bg_image_layout.addWidget(self.bg_image_edit)
        bg_image_layout.addWidget(self.bg_image_button)
        form_layout.addRow("Background Image", bg_image_layout)

        # Background Color
        self.bg_color_edit = QLineEdit()
        self.bg_color_edit.setPlaceholderText("#FFFFFFFF")
        self.bg_color_edit.setAccessibleName("Background Color LineEdit")
        self.bg_color_button = QPushButton("Pick Color")
        bg_color_layout = QVBoxLayout()
        bg_color_layout.addWidget(self.bg_color_edit)
        bg_color_layout.addWidget(self.bg_color_button)
        form_layout.addRow("Background Color", bg_color_layout)

        # Text Color
        self.text_color_edit = QLineEdit()
        self.text_color_edit.setPlaceholderText("#FF000000")
        self.text_color_edit.setAccessibleName("Text Color LineEdit")
        self.text_color_button = QPushButton("Pick Color")
        text_color_layout = QVBoxLayout()
        text_color_layout.addWidget(self.text_color_edit)
        text_color_layout.addWidget(self.text_color_button)
        form_layout.addRow("Text Color", text_color_layout)

        # Width
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 4096)
        self.width_spin.setValue(812)
        self.width_spin.setAccessibleName("UI Width SpinBox")
        form_layout.addRow("UI Width", self.width_spin)

        # Height
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 4096)
        self.height_spin.setValue(375)
        self.height_spin.setAccessibleName("UI Height SpinBox")
        form_layout.addRow("UI Height", self.height_spin)

        # Layout Mode
        self.layout_mode_combo = QComboBox()
        self.layout_mode_combo.addItems(["", "relative", "absolute"])
        self.layout_mode_combo.setAccessibleName("Layout Mode ComboBox")
        form_layout.addRow("Layout Mode", self.layout_mode_combo)

        # Background Mode
        self.bg_mode_combo = QComboBox()
        self.bg_mode_combo.addItems(["", "top_left", "center", "stretch"])
        self.bg_mode_combo.setAccessibleName("Background Mode ComboBox")
        form_layout.addRow("Background Mode", self.bg_mode_combo)

        # Volume
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(-60.0, 16.0)
        self.volume_spin.setDecimals(2)
        self.volume_spin.setSingleStep(0.01)
        self.volume_spin.setValue(1.0)
        self.volume_spin.setAccessibleName("Volume SpinBox")
        form_layout.addRow("Volume", self.volume_spin)

        # Global Tuning
        self.global_tuning_spin = QDoubleSpinBox()
        self.global_tuning_spin.setRange(-36.0, 36.0)
        self.global_tuning_spin.setDecimals(2)
        self.global_tuning_spin.setSingleStep(0.01)
        self.global_tuning_spin.setValue(0.0)
        self.global_tuning_spin.setAccessibleName("Global Tuning SpinBox")
        form_layout.addRow("Global Tuning", self.global_tuning_spin)

        # Glide Time
        self.glide_time_spin = QDoubleSpinBox()
        self.glide_time_spin.setRange(0.0, 10.0)
        self.glide_time_spin.setDecimals(3)
        self.glide_time_spin.setSingleStep(0.01)
        self.glide_time_spin.setValue(0.0)
        self.glide_time_spin.setAccessibleName("Glide Time SpinBox")
        form_layout.addRow("Glide Time", self.glide_time_spin)

        # Glide Mode
        self.glide_mode_combo = QComboBox()
        self.glide_mode_combo.addItems(["legato", "always", "off"])
        self.glide_mode_combo.setAccessibleName("Glide Mode ComboBox")
        form_layout.addRow("Glide Mode", self.glide_mode_combo)

        # Pan
        self.pan_spin = QDoubleSpinBox()
        self.pan_spin.setRange(-100.0, 100.0)
        self.pan_spin.setDecimals(2)
        self.pan_spin.setSingleStep(0.01)
        self.pan_spin.setValue(0.0)
        self.pan_spin.setAccessibleName("Pan SpinBox")
        form_layout.addRow("Pan", self.pan_spin)

        # Amp Velocity Track
        self.amp_vel_track_spin = QDoubleSpinBox()
        self.amp_vel_track_spin.setRange(0.0, 1.0)
        self.amp_vel_track_spin.setDecimals(2)
        self.amp_vel_track_spin.setSingleStep(0.01)
        self.amp_vel_track_spin.setValue(1.0)
        self.amp_vel_track_spin.setAccessibleName("Amp Velocity Track SpinBox")
        form_layout.addRow("Amp Velocity Track", self.amp_vel_track_spin)

        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

        # Undo/Redo support
        def push_edit_command(prop, old, new, setter):
            main_window = self.main_window
            undo_stack = main_window.undo_stack if main_window and hasattr(main_window, "undo_stack") else None
            if undo_stack and old != new:
                import commands
                cmd = commands.EditPropertyCommand(self, prop, old, new, setter=setter, description=f"Edit {prop}")
                undo_stack.push(cmd)

        # Helper: connect text field with undo/redo
        def connect_line_edit(edit, prop, last_attr):
            def setter(val): edit.setText(val)
            def changed(val):
                old = getattr(self, last_attr)
                push_edit_command(prop, old, val, setter)
                setattr(self, last_attr, val)
                self.propertyChanged.emit()
            edit.textChanged.connect(changed)

        connect_line_edit(self.preset_name_edit, "presetName", "_preset_name_last")
        connect_line_edit(self.min_version_edit, "minVersion", "_min_version_last")
        connect_line_edit(self.plugin_version_edit, "pluginVersion", "_plugin_version_last")
        connect_line_edit(self.cover_art_edit, "coverArt", "_cover_art_last")
        connect_line_edit(self.bg_image_edit, "bgImage", "_bg_image_last")
        connect_line_edit(self.bg_color_edit, "bgColor", "_bg_color_last")
        connect_line_edit(self.text_color_edit, "textColor", "_text_color_last")

        # File pickers
        import os

        def make_relative_path(path):
            # Make path relative to the current working directory (project root)
            if not path:
                return ""
            cwd = os.getcwd()
            try:
                rel = os.path.relpath(path, cwd)
                return rel
            except Exception:
                return path

        def browse_cover_art():
            path, _ = QFileDialog.getOpenFileName(self, "Select Cover Art", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
            if path:
                rel_path = make_relative_path(path)
                self.cover_art_edit.setText(rel_path)
        self.cover_art_button.clicked.connect(browse_cover_art)

        def browse_bg_image():
            path, _ = QFileDialog.getOpenFileName(self, "Select Background Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
            if path:
                rel_path = make_relative_path(path)
                self.bg_image_edit.setText(rel_path)
        self.bg_image_button.clicked.connect(browse_bg_image)

        # Color pickers
        def pick_bg_color():
            color = QColorDialog.getColor(QColor(self.bg_color_edit.text() or "#FFFFFFFF"), self, "Select Background Color")
            if color.isValid():
                self.bg_color_edit.setText(color.name(QColor.HexArgb))
        self.bg_color_button.clicked.connect(pick_bg_color)

        def pick_text_color():
            color = QColorDialog.getColor(QColor(self.text_color_edit.text() or "#FF000000"), self, "Select Text Color")
            if color.isValid():
                self.text_color_edit.setText(color.name(QColor.HexArgb))
        self.text_color_button.clicked.connect(pick_text_color)

        # Spinboxes and combos with undo/redo
        def connect_spinbox(spin, prop, last_attr):
            def setter(val): spin.setValue(val)
            def changed(val):
                old = getattr(self, last_attr)
                push_edit_command(prop, old, val, setter)
                setattr(self, last_attr, val)
                self.propertyChanged.emit()
            spin.valueChanged.connect(changed)

        connect_spinbox(self.width_spin, "width", "_width_last")
        connect_spinbox(self.height_spin, "height", "_height_last")
        connect_spinbox(self.volume_spin, "volume", "_volume_last")
        connect_spinbox(self.global_tuning_spin, "globalTuning", "_global_tuning_last")
        connect_spinbox(self.glide_time_spin, "glideTime", "_glide_time_last")
        connect_spinbox(self.pan_spin, "pan", "_pan_last")
        connect_spinbox(self.amp_vel_track_spin, "ampVelTrack", "_amp_vel_track_last")

        def connect_combo(combo, prop, last_attr):
            def setter(val): combo.setCurrentText(val)
            def changed(val):
                old = getattr(self, last_attr)
                new = combo.currentText()
                push_edit_command(prop, old, new, setter)
                setattr(self, last_attr, new)
                self.propertyChanged.emit()
            combo.currentTextChanged.connect(changed)

        connect_combo(self.layout_mode_combo, "layoutMode", "_layout_mode_last")
        connect_combo(self.bg_mode_combo, "bgMode", "_bg_mode_last")
        connect_combo(self.glide_mode_combo, "glideMode", "_glide_mode_last")

    def set_properties(self, props):
        self.preset_name_edit.setText(props.get("presetName", ""))
        self.min_version_edit.setText(props.get("minVersion", ""))
        self.plugin_version_edit.setText(props.get("pluginVersion", ""))
        self.cover_art_edit.setText(props.get("coverArt", ""))
        self.bg_image_edit.setText(props.get("bgImage", ""))
        self.bg_color_edit.setText(props.get("bgColor", "#FFFFFFFF"))
        self.text_color_edit.setText(props.get("textColor", "#FF000000"))
        self.width_spin.setValue(int(props.get("width", 812)))
        self.height_spin.setValue(int(props.get("height", 375)))
        self.layout_mode_combo.setCurrentText(props.get("layoutMode", ""))
        self.bg_mode_combo.setCurrentText(props.get("bgMode", ""))
        self.volume_spin.setValue(float(props.get("volume", 1.0)))
        self.global_tuning_spin.setValue(float(props.get("globalTuning", 0.0)))
        self.glide_time_spin.setValue(float(props.get("glideTime", 0.0)))
        self.glide_mode_combo.setCurrentText(props.get("glideMode", "legato"))
        self.pan_spin.setValue(float(props.get("pan", 0.0)))
        self.amp_vel_track_spin.setValue(float(props.get("ampVelTrack", 1.0)))

    def get_properties(self):
        return {
            "presetName": self.preset_name_edit.text(),
            "minVersion": self.min_version_edit.text(),
            "pluginVersion": self.plugin_version_edit.text(),
            "coverArt": self.cover_art_edit.text(),
            "bgImage": self.bg_image_edit.text(),
            "bgColor": self.bg_color_edit.text(),
            "textColor": self.text_color_edit.text(),
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "layoutMode": self.layout_mode_combo.currentText(),
            "bgMode": self.bg_mode_combo.currentText(),
            "volume": self.volume_spin.value(),
            "globalTuning": self.global_tuning_spin.value(),
            "glideTime": self.glide_time_spin.value(),
            "glideMode": self.glide_mode_combo.currentText(),
            "pan": self.pan_spin.value(),
            "ampVelTrack": self.amp_vel_track_spin.value(),
        }
