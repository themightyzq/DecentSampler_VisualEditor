from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QFont
from PyQt5.QtCore import Qt, QRect

class KnobWidget(QWidget):
    @classmethod
    def render_to_pixmap(
        cls,
        width,
        height,
        label,
        skin=None,
        textSize=16,
        trackForegroundColor="CC000000",
        trackBackgroundColor="66999999"
    ):
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        rect = QRect(0, 0, width, height)
        if skin:
            skin_pixmap = QPixmap(skin)
            if not skin_pixmap.isNull():
                painter.drawPixmap(rect, skin_pixmap)
            else:
                painter.setPen(Qt.red)
                painter.drawRect(rect)
        else:
            # Draw track background
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#" + trackBackgroundColor) if not trackBackgroundColor.startswith("0x") else QColor(int(trackBackgroundColor, 16)))
            painter.drawEllipse(rect)
            # Draw track foreground (border)
            pen = QPen(QColor("#" + trackForegroundColor) if not trackForegroundColor.startswith("0x") else QColor(int(trackForegroundColor, 16)))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(rect)
            # Draw label
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", textSize))
            painter.drawText(rect, Qt.AlignCenter, label)
        painter.end()
        return pixmap

class SliderWidget(QWidget):
    @classmethod
    def render_to_pixmap(cls, width, height, label, skin=None, orientation="horizontal"):
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        rect = QRect(0, 0, width, height)
        if skin:
            skin_pixmap = QPixmap(skin)
            if not skin_pixmap.isNull():
                painter.drawPixmap(rect, skin_pixmap)
            else:
                painter.setPen(Qt.red)
                painter.drawRect(rect)
        else:
            painter.setPen(Qt.darkGray)
            painter.setBrush(QColor(200, 200, 255))
            if orientation == "vertical":
                slider_rect = QRect(rect.x() + rect.width() // 2 - 6, rect.y(), 12, rect.height())
            else:
                slider_rect = QRect(rect.x(), rect.y() + rect.height() // 2 - 6, rect.width(), 12)
            painter.drawRect(slider_rect)
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", max(8, int(height * 0.18))))
            painter.drawText(rect, Qt.AlignCenter, label)
        painter.end()
        return pixmap

class ButtonWidget(QWidget):
    @classmethod
    def render_to_pixmap(cls, width, height, label, skin=None):
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        rect = QRect(0, 0, width, height)
        if skin:
            skin_pixmap = QPixmap(skin)
            if not skin_pixmap.isNull():
                painter.drawPixmap(rect, skin_pixmap)
            else:
                painter.setPen(Qt.red)
                painter.drawRect(rect)
        else:
            painter.setPen(Qt.darkGray)
            painter.setBrush(QColor(180, 255, 180))
            painter.drawRect(rect)
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", max(8, int(height * 0.18))))
            painter.drawText(rect, Qt.AlignCenter, label)
        painter.end()
        return pixmap

class MenuWidget(QWidget):
    @classmethod
    def render_to_pixmap(cls, width, height, label, skin=None):
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        rect = QRect(0, 0, width, height)
        if skin:
            skin_pixmap = QPixmap(skin)
            if not skin_pixmap.isNull():
                painter.drawPixmap(rect, skin_pixmap)
            else:
                painter.setPen(Qt.red)
                painter.drawRect(rect)
        else:
            painter.setPen(Qt.darkGray)
            painter.setBrush(QColor(255, 255, 180))
            painter.drawRect(rect)
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", max(8, int(height * 0.18))))
            painter.drawText(rect, Qt.AlignCenter, label)
        painter.end()
        return pixmap

class LabelWidget(QWidget):
    @classmethod
    def render_to_pixmap(cls, width, height, label, skin=None):
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        rect = QRect(0, 0, width, height)
        painter.setPen(Qt.black)
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.drawRect(rect)
        painter.setFont(QFont("Arial", max(10, int(height * 0.32))))
        painter.drawText(rect, Qt.AlignCenter, label)
        painter.end()
        return pixmap

# Fallback widget
class FallbackWidget(QWidget):
    @classmethod
    def render_to_pixmap(cls, width, height, label, skin=None):
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        rect = QRect(0, 0, width, height)
        painter.setPen(Qt.black)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(rect)
        painter.setFont(QFont("Arial", max(8, int(height * 0.18))))
        painter.drawText(rect, Qt.AlignCenter, label)
        painter.end()
        return pixmap

# Tag to widget class mapping
WIDGET_CLASS_MAP = {
    "Knob": KnobWidget,
    "Slider": SliderWidget,
    "Button": ButtonWidget,
    "Menu": MenuWidget,
    "Label": LabelWidget,
}

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QLineEdit, QDoubleSpinBox, QPushButton, QComboBox, QGroupBox
)

class ADSRParameterCard(QWidget):
    def __init__(self, param_name, value=0.0, value_range=(0.0, 10.0), value_step=0.01, value_decimals=3, type_options=None, parent=None):
        super().__init__(parent)
        self.param_name = param_name
        self.setObjectName(f"{param_name}_adsr_card")

        # Card styling for visual grouping
        self.setStyleSheet("""
            QWidget#{}_adsr_card {{
                border: 1.5px solid #cccccc;
                border-radius: 8px;
                background: #f8f8f8;
            }}
            QLineEdit {{
                background: #fff;
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 2px 6px;
            }}
            QDoubleSpinBox {{
                min-width: 60px;
                max-width: 80px;
            }}
            QPushButton {{
                min-width: 70px;
                max-width: 90px;
            }}
        """.format(param_name))

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(8)

        # Parameter label as a functional button (centered)
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(4)
        top_row.addStretch()
        self.label_btn = QPushButton(param_name)
        self.label_btn.setCheckable(True)
        self.label_btn.setChecked(False)
        self.label_btn.setFlat(False)
        self.label_btn.setCursor(Qt.PointingHandCursor)
        self.label_btn.setMinimumWidth(90)
        self.label_btn.setMaximumWidth(120)
        # Style to match "Settings" button, with blue highlight when checked
        self.label_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 15px;
                background: #e0e0e0;
                border: 1.5px solid #b0b0b0;
                border-radius: 6px;
                color: #222;
                padding: 4px 12px;
            }
            QPushButton:checked {
                background: #2979ff;
                color: #fff;
                border: 1.5px solid #1565c0;
            }
            QPushButton:!checked {
                background: #e0e0e0;
                color: #222;
                border: 1.5px solid #b0b0b0;
            }
        """)
        top_row.addWidget(self.label_btn)
        top_row.addStretch()
        card_layout.addLayout(top_row)

        # Value control (centered, no "Value:" label)
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(*value_range)
        self.value_spin.setSingleStep(value_step)
        self.value_spin.setDecimals(value_decimals)
        self.value_spin.setValue(value)
        self.value_spin.setAlignment(Qt.AlignCenter)
        self.value_spin.setFixedWidth(70)
        value_row = QHBoxLayout()
        value_row.setContentsMargins(0, 0, 0, 0)
        value_row.addStretch()
        value_row.addWidget(self.value_spin)
        value_row.addStretch()
        card_layout.addLayout(value_row)

        # X/Y and Width/Height controls (real-time, below value)
        from PyQt5.QtWidgets import QSpinBox

        # X/Y row
        xy_row = QHBoxLayout()
        xy_row.setContentsMargins(0, 0, 0, 0)
        xy_row.setSpacing(4)
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 2000)
        self.x_spin.setValue(getattr(self, "_adsr_x", 40))
        self.x_spin.setFixedWidth(48)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 2000)
        self.y_spin.setValue(getattr(self, "_adsr_y", 100))
        self.y_spin.setFixedWidth(48)
        xy_row.addStretch()
        xy_row.addWidget(QLabel("X:"))
        xy_row.addWidget(self.x_spin)
        xy_row.addWidget(QLabel("Y:"))
        xy_row.addWidget(self.y_spin)
        xy_row.addStretch()
        card_layout.addLayout(xy_row)

        # Width/Height row
        wh_row = QHBoxLayout()
        wh_row.setContentsMargins(0, 0, 0, 0)
        wh_row.setSpacing(4)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(16, 512)
        self.width_spin.setValue(getattr(self, "_adsr_width", 64))
        self.width_spin.setFixedWidth(48)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(16, 512)
        self.height_spin.setValue(getattr(self, "_adsr_height", 64))
        self.height_spin.setFixedWidth(48)
        wh_row.addStretch()
        wh_row.addWidget(QLabel("W:"))
        wh_row.addWidget(self.width_spin)
        wh_row.addWidget(QLabel("H:"))
        wh_row.addWidget(self.height_spin)
        wh_row.addStretch()
        card_layout.addLayout(wh_row)

        # Real-time update logic for X/Y/W/H
        def update_geom():
            self._adsr_x = self.x_spin.value()
            self._adsr_y = self.y_spin.value()
            self._adsr_width = self.width_spin.value()
            self._adsr_height = self.height_spin.value()
            # Notify parent/main window to update UI
            if hasattr(self.parent(), "on_adsr_advanced_changed"):
                self.parent().on_adsr_advanced_changed(self.param_name)
            elif hasattr(self, "on_advanced_changed"):
                self.on_advanced_changed(self.param_name)
        self.x_spin.valueChanged.connect(update_geom)
        self.y_spin.valueChanged.connect(update_geom)
        self.width_spin.valueChanged.connect(update_geom)
        self.height_spin.valueChanged.connect(update_geom)

        # Type selector (if present, centered below value)
        if type_options:
            self.type_combo = QComboBox()
            self.type_combo.addItems(type_options)
            type_row = QHBoxLayout()
            type_row.setContentsMargins(0, 0, 0, 0)
            type_row.addStretch()
            type_row.addWidget(self.type_combo)
            type_row.addStretch()
            card_layout.addLayout(type_row)
        else:
            self.type_combo = None

        # Settings button (centered)
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setFixedWidth(80)
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.addStretch()
        btn_row.addWidget(self.settings_btn)
        btn_row.addStretch()
        card_layout.addLayout(btn_row)

        card_layout.addStretch()
        self.setLayout(card_layout)

        # Optionally: connect label_btn to enable/disable logic or other functionality
        # Example: self.label_btn.clicked.connect(self.on_label_clicked)

        # Advanced options modal
        self.settings_btn.clicked.connect(self.open_advanced_options_dialog)

        # Provide enable_cb-like compatibility for parent logic
        self.enable_cb = self.label_btn

    def open_advanced_options_dialog(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QComboBox, QDoubleSpinBox
        dlg = QDialog(self)
        dlg.setWindowTitle(f"{self.param_name} Advanced Options")
        dlg.setMinimumWidth(320)
        layout = QVBoxLayout()

        # X position
        x_row = QHBoxLayout()
        x_row.addWidget(QLabel("X:"))
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 2000)
        self.x_spin.setValue(getattr(self, "_adsr_x", 40))
        x_row.addWidget(self.x_spin)
        layout.addLayout(x_row)

        # Y position
        y_row = QHBoxLayout()
        y_row.addWidget(QLabel("Y:"))
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 2000)
        self.y_spin.setValue(getattr(self, "_adsr_y", 100))
        y_row.addWidget(self.y_spin)
        layout.addLayout(y_row)

        # Width
        width_row = QHBoxLayout()
        width_row.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(16, 512)
        self.width_spin.setValue(getattr(self, "_adsr_width", 64))
        width_row.addWidget(self.width_spin)
        layout.addLayout(width_row)

        # Height
        height_row = QHBoxLayout()
        height_row.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(16, 512)
        self.height_spin.setValue(getattr(self, "_adsr_height", 64))
        height_row.addWidget(self.height_spin)
        layout.addLayout(height_row)

        # Type (Knob/Slider)
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Knob", "Slider"])
        self.type_combo.setCurrentText(getattr(self, "_adsr_type", "Knob"))
        type_row.addWidget(self.type_combo)
        layout.addLayout(type_row)

        # Orientation (only if slider)
        orientation_row = QHBoxLayout()
        orientation_row.addWidget(QLabel("Slider Orientation:"))
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["horizontal", "vertical"])
        self.orientation_combo.setCurrentText(getattr(self, "_adsr_orientation", "horizontal"))
        orientation_row.addWidget(self.orientation_combo)
        layout.addLayout(orientation_row)
        # Show/hide orientation based on type
        def update_orientation_visibility():
            self.orientation_combo.setVisible(self.type_combo.currentText() == "Slider")
        self.type_combo.currentTextChanged.connect(update_orientation_visibility)
        update_orientation_visibility()

        # Text size
        textsize_row = QHBoxLayout()
        textsize_row.addWidget(QLabel("Text Size:"))
        self.textsize_spin = QSpinBox()
        self.textsize_spin.setRange(6, 64)
        self.textsize_spin.setValue(getattr(self, "_adsr_text_size", 16))
        textsize_row.addWidget(self.textsize_spin)
        layout.addLayout(textsize_row)

        # Save/close
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        close_btn = QPushButton("Cancel")
        btn_row.addWidget(save_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        dlg.setLayout(layout)

        def save_and_close():
            self._adsr_x = self.x_spin.value()
            self._adsr_y = self.y_spin.value()
            self._adsr_width = self.width_spin.value()
            self._adsr_height = self.height_spin.value()
            self._adsr_type = self.type_combo.currentText()
            self._adsr_orientation = self.orientation_combo.currentText() if self._adsr_type == "Slider" else None
            self._adsr_text_size = self.textsize_spin.value()
            dlg.accept()
            # Notify parent/main window to update UI
            if hasattr(self.parent(), "on_adsr_advanced_changed"):
                self.parent().on_adsr_advanced_changed(self.param_name)
            elif hasattr(self, "on_advanced_changed"):
                self.on_advanced_changed(self.param_name)
            # Fallback: emit a custom signal or call a callback if needed

        save_btn.clicked.connect(save_and_close)
        close_btn.clicked.connect(dlg.reject)
        dlg.exec_()
