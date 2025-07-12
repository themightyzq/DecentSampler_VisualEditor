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
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(6)

        # Enable checkbox and label field
        top_row = QHBoxLayout()
        self.enable_cb = QCheckBox()
        self.enable_cb.setChecked(True)
        top_row.addWidget(self.enable_cb)
        self.label_edit = QLineEdit(param_name)
        self.label_edit.setFixedWidth(70)
        top_row.addWidget(self.label_edit)
        top_row.addStretch()
        card_layout.addLayout(top_row)

        # Value control and type selector
        mid_row = QHBoxLayout()
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(*value_range)
        self.value_spin.setSingleStep(value_step)
        self.value_spin.setDecimals(value_decimals)
        self.value_spin.setValue(value)
        self.value_spin.setFixedWidth(70)
        mid_row.addWidget(QLabel("Value:"))
        mid_row.addWidget(self.value_spin)
        if type_options:
            self.type_combo = QComboBox()
            self.type_combo.addItems(type_options)
            mid_row.addWidget(QLabel("Type:"))
            mid_row.addWidget(self.type_combo)
        else:
            self.type_combo = None
        card_layout.addLayout(mid_row)

        # Settings button
        bottom_row = QHBoxLayout()
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setFixedWidth(80)
        bottom_row.addStretch()
        bottom_row.addWidget(self.settings_btn)
        card_layout.addLayout(bottom_row)

        self.setLayout(card_layout)

        # Advanced options modal
        self.settings_btn.clicked.connect(self.open_advanced_options_dialog)

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
