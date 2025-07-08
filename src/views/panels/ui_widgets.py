from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QFont
from PyQt5.QtCore import Qt, QRect

class KnobWidget(QWidget):
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
            painter.setBrush(QColor(220, 220, 220))
            painter.drawEllipse(rect)
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", max(8, int(height * 0.18))))
            painter.drawText(rect, Qt.AlignCenter, label)
        painter.end()
        return pixmap

class SliderWidget(QWidget):
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
            painter.setBrush(QColor(200, 200, 255))
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
