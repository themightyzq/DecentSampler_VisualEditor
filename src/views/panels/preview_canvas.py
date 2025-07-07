from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPixmap
from PyQt5.QtCore import Qt, QRect

class PreviewCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.preset = None
        self.base_dir = ""
        self.bg_pixmap = None
        self.setMinimumHeight(180)
        self.setToolTip("Preview of sample mappings and UI background")

    def set_preset(self, preset, base_dir):
        self.preset = preset
        self.base_dir = base_dir
        self.bg_pixmap = None
        if preset and getattr(preset, "bg_image", None):
            import os
            img_path = preset.bg_image
            if not os.path.isabs(img_path):
                img_path = os.path.join(base_dir, img_path)
            self.bg_pixmap = QPixmap(img_path)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        # Fill BG color if set
        bg_color = None
        if self.preset and getattr(self.preset, "bg_color", None):
            bg_color = QColor(self.preset.bg_color)
        else:
            bg_color = QColor("#f0f0f0")
        painter.fillRect(self.rect(), bg_color)
        # Draw background image if available
        if self.bg_pixmap and not self.bg_pixmap.isNull():
            painter.drawPixmap(self.rect(), self.bg_pixmap)

        # Draw real UI controls
        if self.preset and hasattr(self.preset, "ui") and hasattr(self.preset.ui, "elements"):
            for el in self.preset.ui.elements:
                rect = QRect(el.x, el.y, el.width, el.height)
                if el.skin:
                    pixmap = QPixmap(el.skin)
                    if not pixmap.isNull():
                        painter.drawPixmap(rect, pixmap)
                    else:
                        painter.setPen(Qt.red)
                        painter.drawRect(rect)
                else:
                    painter.setPen(Qt.black)
                    painter.setBrush(Qt.NoBrush)
                    painter.drawRect(rect)
                    painter.setFont(self.font())
                    painter.drawText(rect, Qt.AlignCenter, el.label)

        # Draw preset name
        if self.preset:
            painter.setPen(Qt.black)
            painter.setFont(self.font())
            painter.drawText(10, 20, f"Preset: {self.preset.name}")
        # (Piano keyboard and mapping highlights removed; handled by PianoKeyboardWidget)
    # (is_black_key no longer needed)
