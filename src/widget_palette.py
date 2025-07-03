from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt

class PaletteListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(self.IconMode)
        self.setIconSize(QSize(32, 32))
        self.setSpacing(12)
        self.setResizeMode(self.Adjust)
        self.setMovement(self.Static)
        self.setFixedHeight(90)
        self.setToolTip("Drag UI elements onto the canvas")
        self.setAccessibleName("Widget Palette")
        self.setDragEnabled(True)
        # Add palette items
        items = [
            ("Knob", "🎛️", "Knob", "Drag to add a Knob control", "Knob widget for rotary control"),
            ("Slider", "🎚️", "Slider", "Drag to add a Slider control", "Slider widget for continuous control"),
            ("Button", "🔘", "Button", "Drag to add a Button control", "Button widget for triggering actions"),
            ("Menu", "📋", "Menu", "Drag to add a Menu control", "Menu widget for options"),
            ("Label", "🏷️", "Label", "Drag to add a Label", "Label widget for text display"),
        ]
        for name, emoji, label, tooltip, accessible in items:
            icon = QIcon(self._emoji_pixmap(emoji))
            item = QListWidgetItem()
            item.setText(label)
            item.setIcon(icon)
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignBottom)
            item.setToolTip(tooltip)
            item.setData(Qt.AccessibleTextRole, accessible)
            item.setData(256, name)  # Custom role for type
            item.setSizeHint(QSize(60, 60))
            self.addItem(item)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            from PyQt5.QtCore import QMimeData, Qt
            from PyQt5.QtGui import QDrag
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(item.text())
            drag.setMimeData(mime)
            if not item.icon().isNull():
                drag.setPixmap(item.icon().pixmap(32, 32))
            drag.exec_(Qt.CopyAction)

    def _emoji_pixmap(self, emoji):
        # Create a pixmap from emoji for icon fallback
        from PyQt5.QtGui import QPixmap, QPainter, QFont
        pix = QPixmap(48, 48)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        font = QFont()
        font.setPointSize(24)
        painter.setFont(font)
        painter.drawText(pix.rect(), Qt.AlignCenter, emoji)
        painter.end()
        return pix
