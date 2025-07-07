from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QSpinBox, QPushButton, QColorDialog, QFileDialog, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

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

        layout.addLayout(form_layout)

        widget.setLayout(layout)
        self.setWidget(widget)

        # Connect live update signals for all properties
        self.preset_name_edit.textChanged.connect(self._live_update)
        self.ui_width_spin.valueChanged.connect(self._live_update)
        self.ui_height_spin.valueChanged.connect(self._live_update)
        self.bg_image_edit.textChanged.connect(self._live_update)

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
        if hasattr(mw, "preview_canvas") and hasattr(mw, "preset"):
            # Resize preview_canvas if needed
            mw.preview_canvas.setFixedSize(mw.preset.ui_width, mw.preset.ui_height)
            mw.preview_canvas.set_preset(mw.preset, "")
