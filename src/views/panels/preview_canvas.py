from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPixmap
from PyQt5.QtCore import Qt, QRect, QSize

from .ui_widgets import WIDGET_CLASS_MAP, FallbackWidget

class PreviewCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.preset = None
        self.base_dir = ""
        self.bg_pixmap = None
        self.setMinimumSize(812, 375)
        self.setMaximumSize(812, 375)
        self.setToolTip("Preview of sample mappings and UI background")

    def sizeHint(self):
        return QSize(812, 375)

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

        # Draw real UI controls:
        # For each element in preset.ui.elements, select the widget class (KnobWidget, SliderWidget, ButtonWidget, MenuWidget, LabelWidget)
        # and render it to an off-screen QPixmap using its static render_to_pixmap method, then draw it at the correct position.
        # If no class matches, use FallbackWidget to draw a rectangle + centered label.
        if self.preset and hasattr(self.preset, "ui") and hasattr(self.preset.ui, "elements"):
            for idx, el in enumerate(self.preset.ui.elements):
                rect = QRect(el.x, el.y, el.width, el.height)
                # Prefer widget_type for rendering, fallback to tag, then "Knob"
                widget_type = getattr(el, "widget_type", None)
                tag = getattr(el, "tag", None)
                widget_key = None
                if widget_type in WIDGET_CLASS_MAP:
                    widget_key = widget_type
                elif tag in WIDGET_CLASS_MAP:
                    widget_key = tag
                else:
                    widget_key = "Knob"
                widget_cls = WIDGET_CLASS_MAP.get(widget_key, FallbackWidget)
                label = getattr(el, "label", "")
                skin = getattr(el, "skin", None)
                # Pass orientation for sliders
                if widget_key == "Slider":
                    orientation = getattr(el, "orientation", "horizontal")
                    pixmap = widget_cls.render_to_pixmap(rect.width(), rect.height(), label, skin, orientation)
                else:
                    if widget_cls.__name__ == "KnobWidget":
                        pixmap = widget_cls.render_to_pixmap(
                            rect.width(), rect.height(), label, skin,
                            textSize=16,
                            trackForegroundColor="CC000000",
                            trackBackgroundColor="66999999"
                        )
                    else:
                        pixmap = widget_cls.render_to_pixmap(rect.width(), rect.height(), label, skin)
                painter.drawPixmap(rect, pixmap)

        # (ADSR envelope preview removed from preview canvas; now shown in properties panel)

        # Draw preset name
        if self.preset:
            painter.setPen(Qt.black)
            painter.setFont(self.font())
            painter.drawText(8, 16, f"Preset: {self.preset.name}")
        # (Piano keyboard and mapping highlights removed; handled by PianoKeyboardWidget)
    # (is_black_key no longer needed)
