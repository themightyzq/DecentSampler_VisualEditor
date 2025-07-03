import os
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QPainter, QCursor, QPen, QBrush, QFont, QColor
from PyQt5.QtCore import Qt, QRect

# --- PaletteLabel (for palette, drag only, no resize) ---
class PaletteLabel(QLabel):
    def __init__(self, emoji, label, parent=None):
        super().__init__("", parent)
        self.emoji = emoji
        self.label = label
        self.setFixedSize(60, 60)
        self.setStyleSheet("background: #f8f8f8; border: 1px solid #bbb;")
        self.setToolTip(f"Drag to add a {label}")

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            from PyQt5.QtCore import QMimeData
            from PyQt5.QtGui import QDrag
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.label)
            drag.setMimeData(mime)
            drag.exec_(Qt.CopyAction)
            return

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        font = QFont()
        font.setPointSize(int(min(w, h*2/3) * 0.7))
        painter.setFont(font)
        painter.drawText(QRect(0, 0, w, h-18), Qt.AlignCenter, self.emoji)
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(QRect(0, h-18, w, 18), Qt.AlignHCenter | Qt.AlignBottom, self.label)

# --- Resizable/Draggable CanvasLabel base class ---
class ResizableDraggableLabel(QLabel):
    HANDLE_SIZE = 12

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.selected = False
        self.dragging = False
        self.resizing = False
        self.resize_dir = None
        self.offset = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            handle = self._hit_test_handle(event.pos())
            if handle:
                self.resizing = True
                self.resize_dir = handle
                self.dragging = False
                self._resize_orig_geom = self.geometry()
                self._resize_start_pos = event.globalPos()
            else:
                self.dragging = True
                self.resizing = False
                self.offset = event.pos()
            if hasattr(self.parent(), "select_element"):
                self.parent().select_element(self)
            self.update_style()
            # Do NOT call super() when handling drag/resize
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing and event.buttons() & Qt.LeftButton:
            self.setCursor(QCursor(self._cursor_for_handle(self.resize_dir)))
            self._resize_widget(event)
            return
        elif self.dragging and event.buttons() & Qt.LeftButton:
            new_pos = self.mapToParent(event.pos() - self.offset)
            # Clamp to parent bounds
            parent = self.parent()
            if parent:
                new_x = max(0, min(new_pos.x(), parent.width() - self.width()))
                new_y = max(0, min(new_pos.y(), parent.height() - self.height()))
                self.move(new_x, new_y)
            else:
                self.move(new_pos)
            if hasattr(self, "attrs"):
                self.attrs["x"] = self.x()
                self.attrs["y"] = self.y()
            if hasattr(self.parent(), "update_properties_panel"):
                self.parent().update_properties_panel(self)
            if hasattr(self.parent(), "update_xml_from_canvas"):
                self.parent().update_xml_from_canvas()
            return
        else:
            handle = self._hit_test_handle(event.pos())
            if handle:
                self.setCursor(QCursor(self._cursor_for_handle(handle)))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        self.resize_dir = None
        self.offset = None
        self.setCursor(QCursor(Qt.ArrowCursor))
        if hasattr(self.parent(), "update_properties_panel"):
            self.parent().update_properties_panel(self)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.selected:
            painter = QPainter(self)
            painter.setPen(QPen(QColor("#222")))  # High-contrast border for resize handles
            painter.setBrush(QBrush(QColor(Qt.white)))
            for handle, rect in self._handle_rects().items():
                painter.drawRect(rect)
            painter.end()

    def _handle_rects(self):
        s = self.HANDLE_SIZE
        w, h = self.width(), self.height()
        return {
            "tl": QRect(0, 0, s, s),
            "tm": QRect(w//2 - s//2, 0, s, s),
            "tr": QRect(w-s, 0, s, s),
            "mr": QRect(w-s, h//2 - s//2, s, s),
            "br": QRect(w-s, h-s, s, s),
            "bm": QRect(w//2 - s//2, h-s, s, s),
            "bl": QRect(0, h-s, s, s),
            "ml": QRect(0, h//2 - s//2, s, s),
        }

    def _hit_test_handle(self, pos):
        for handle, rect in self._handle_rects().items():
            if rect.contains(pos):
                return handle
        return None

    def _cursor_for_handle(self, handle):
        if handle in ("tl", "br"):
            return Qt.SizeFDiagCursor
        if handle in ("tr", "bl"):
            return Qt.SizeBDiagCursor
        if handle in ("tm", "bm"):
            return Qt.SizeVerCursor
        if handle in ("ml", "mr"):
            return Qt.SizeHorCursor
        return Qt.ArrowCursor

    def _resize_widget(self, event):
        min_w, min_h = 24, 24
        max_w, max_h = 1000, 1000
        if hasattr(self, "_resize_orig_geom") and hasattr(self, "_resize_start_pos"):
            orig_geom = self._resize_orig_geom
            start_pos = self._resize_start_pos
            delta = event.globalPos() - start_pos
            handle = self.resize_dir
            new_x, new_y, new_w, new_h = orig_geom.x(), orig_geom.y(), orig_geom.width(), orig_geom.height()
            if handle == "br":
                new_w = max(min_w, min(max_w, orig_geom.width() + delta.x()))
                new_h = max(min_h, min(max_h, orig_geom.height() + delta.y()))
            elif handle == "bm":
                new_h = max(min_h, min(max_h, orig_geom.height() + delta.y()))
            elif handle == "mr":
                new_w = max(min_w, min(max_w, orig_geom.width() + delta.x()))
            elif handle == "tr":
                new_w = max(min_w, min(max_w, orig_geom.width() + delta.x()))
                new_h = max(min_h, min(max_h, orig_geom.height() - delta.y()))
                new_y = orig_geom.y() + (orig_geom.height() - new_h)
            elif handle == "tm":
                new_h = max(min_h, min(max_h, orig_geom.height() - delta.y()))
                new_y = orig_geom.y() + (orig_geom.height() - new_h)
            elif handle == "ml":
                new_w = max(min_w, min(max_w, orig_geom.width() - delta.x()))
                new_x = orig_geom.x() + (orig_geom.width() - new_w)
            elif handle == "tl":
                new_w = max(min_w, min(max_w, orig_geom.width() - delta.x()))
                new_x = orig_geom.x() + (orig_geom.width() - new_w)
                new_h = max(min_h, min(max_h, orig_geom.height() - delta.y()))
                new_y = orig_geom.y() + (orig_geom.height() - new_h)
            elif handle == "bl":
                new_w = max(min_w, min(max_w, orig_geom.width() - delta.x()))
                new_x = orig_geom.x() + (orig_geom.width() - new_w)
                new_h = max(min_h, min(max_h, orig_geom.height() + delta.y()))
            # Clamp to parent bounds
            parent = self.parent()
            if parent:
                new_x = max(0, min(new_x, parent.width() - new_w))
                new_y = max(0, min(new_y, parent.height() - new_h))
            self.setGeometry(new_x, new_y, new_w, new_h)
            if hasattr(self, "attrs"):
                self.attrs["width"] = new_w
                self.attrs["height"] = new_h
                self.attrs["x"] = new_x
                self.attrs["y"] = new_y
            if hasattr(self.parent(), "update_properties_panel"):
                self.parent().update_properties_panel(self)
            if hasattr(self.parent(), "update_xml_from_canvas"):
                self.parent().update_xml_from_canvas()
            self.update()

# --- IconWidget for canvas widgets with emoji icons ---
class IconWidget(ResizableDraggableLabel):
    def __init__(self, emoji, label, default_attrs, parent=None):
        super().__init__("", parent)
        self.icon_emoji = emoji
        self.attrs = dict(default_attrs)
        self.attrs["label"] = label
        # Remove setFixedSize to allow dynamic resizing
        self.setMinimumSize(24, 24)
        self.setMaximumSize(1000, 1000)
        self.update_style()
        self.update_from_attrs()

    def update_style(self):
        # Use high-contrast border for accessibility
        self.setStyleSheet("background: #fff; border: 2px solid #222; padding: 2px;")

    def update_from_attrs(self):
        x = int(self.attrs.get("x", 0))
        y = int(self.attrs.get("y", 0))
        w = int(self.attrs.get("width", 80))
        h = int(self.attrs.get("height", 30))
        self.setGeometry(x, y, w, h)
        self.update()
        self.show()

    def paintEvent(self, event):
        super().paintEvent(event)
        w, h = self.width(), self.height()
        painter = QPainter(self)
        # Draw emoji icon, scaled to fit top 2/3 of widget
        icon_rect = self.rect().adjusted(0, 0, 0, -h//3)
        font = QFont()
        font.setPointSize(max(14, int(min(w, h*2/3) * 0.7)))  # Ensure minimum font size for accessibility
        painter.setFont(font)
        painter.drawText(icon_rect, Qt.AlignCenter, self.icon_emoji)
        # Draw label at bottom
        label = self.attrs.get("label", "")
        font.setPointSize(max(10, int(h * 0.18)))
        painter.setFont(font)
        painter.drawText(0, h - int(h*0.12), w, int(h*0.2), Qt.AlignHCenter | Qt.AlignBottom, label)
        # Draw resize handles if selected
        if self.selected:
            painter.setPen(QPen(Qt.black))
            painter.setBrush(QBrush(Qt.white))
            for handle, rect in self._handle_rects().items():
                painter.drawRect(rect)

# --- Canvas widget subclasses ---
class KnobWidget(IconWidget):
    def __init__(self, parent=None):
        super().__init__("🎛️", "Knob", {
            "type": "Knob", "x": 0, "y": 0, "width": 80, "height": 80
        }, parent)

class SliderWidget(IconWidget):
    def __init__(self, parent=None):
        super().__init__("🎚️", "Slider", {
            "type": "Slider", "x": 0, "y": 0, "width": 120, "height": 30
        }, parent)

class ButtonWidget(IconWidget):
    def __init__(self, parent=None):
        super().__init__("🔘", "Button", {
            "type": "Button", "x": 0, "y": 0, "width": 80, "height": 30
        }, parent)

class MenuWidget(IconWidget):
    def __init__(self, parent=None):
        super().__init__("📋", "Menu", {
            "type": "Menu", "x": 0, "y": 0, "width": 100, "height": 30
        }, parent)

class LabelWidget(IconWidget):
    def __init__(self, parent=None):
        super().__init__("🏷️", "Label", {
            "type": "Label", "x": 0, "y": 0, "width": 80, "height": 30
        }, parent)

# --- DraggableElementLabel (restored for proper dropEvent usage) ---
class DraggableElementLabel(ResizableDraggableLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any initialization needed for drag/drop

    def dropEvent(self, event):
        # Implement drop event logic as needed
        if hasattr(self.parent(), "handle_drop"):
            self.parent().handle_drop(event, self)
        event.accept()

# Backward compatibility for main.py and other imports
# DraggableElementLabel = IconWidget  # Removed alias; now restored as class above
