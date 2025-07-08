from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPixmap
from PyQt5.QtCore import Qt, QRect

from .ui_widgets import WIDGET_CLASS_MAP, FallbackWidget

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

        # Draw real UI controls:
        # For each element in preset.ui.elements, select the widget class (KnobWidget, SliderWidget, ButtonWidget, MenuWidget, LabelWidget)
        # and render it to an off-screen QPixmap using its static render_to_pixmap method, then draw it at the correct position.
        # If no class matches, use FallbackWidget to draw a rectangle + centered label.
        if self.preset and hasattr(self.preset, "ui") and hasattr(self.preset.ui, "elements"):
            print("DEBUG: Entering UI element rendering loop")
            print(f"DEBUG: preset.ui.elements = {self.preset.ui.elements} (len={len(self.preset.ui.elements)})")
            for idx, el in enumerate(self.preset.ui.elements):
                print(f"DEBUG: Rendering element {idx}: {el.__dict__}")
                rect = QRect(el.x, el.y, el.width, el.height)
                # Draw a debug rectangle to show where the element should be
                painter.setPen(Qt.red)
                painter.drawRect(rect)
                tag = getattr(el, "tag", None) or getattr(el, "widget_type", "Knob")
                widget_cls = WIDGET_CLASS_MAP.get(tag, FallbackWidget)
                label = getattr(el, "label", "")
                skin = getattr(el, "skin", None)
                pixmap = widget_cls.render_to_pixmap(rect.width(), rect.height(), label, skin)
                painter.drawPixmap(rect, pixmap)

        # Draw ADSR envelope diagram in corner
        if self.preset and hasattr(self.preset, "envelope"):
            env = self.preset.envelope
            # Diagram area: bottom right, 120x60 px
            margin = 8
            w, h = 120, 60
            x0 = self.width() - w - margin
            y0 = self.height() - h - margin
            painter.setPen(Qt.black)
            painter.setBrush(QColor(245, 245, 245, 220))
            painter.drawRect(x0, y0, w, h)
            # Draw envelope curve
            atk = max(env.attack, 0.01)
            dec = max(env.decay, 0.01)
            sus = max(env.sustain, 0.01)
            rel = max(env.release, 0.01)
            total = atk + dec + rel + 0.01
            x_atk = x0 + int(w * atk / total * 0.4)
            x_dec = x_atk + int(w * dec / total * 0.3)
            x_rel = x0 + w - int(w * rel / total * 0.3)
            y_top = y0 + 10
            y_sus = y0 + int(h * (1 - sus) * 0.7)
            y_base = y0 + h - 10
            points = [
                (x0 + 10, y_base),  # start
                (x_atk, y_top),     # attack peak
                (x_dec, y_sus),     # decay to sustain
                (x_rel, y_sus),     # sustain
                (x0 + w - 10, y_base)  # release
            ]
            painter.setPen(QColor(100, 100, 255))
            for i in range(len(points) - 1):
                painter.drawLine(int(points[i][0]), int(points[i][1]), int(points[i+1][0]), int(points[i+1][1]))
            painter.setPen(Qt.black)
            painter.setFont(self.font())
            painter.drawText(x0 + 5, y0 + 15, "ADSR")

        # Draw preset name
        if self.preset:
            painter.setPen(Qt.black)
            painter.setFont(self.font())
            painter.drawText(8, 16, f"Preset: {self.preset.name}")
        # (Piano keyboard and mapping highlights removed; handled by PianoKeyboardWidget)
    # (is_black_key no longer needed)
