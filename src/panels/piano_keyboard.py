from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtMultimedia import QSound
import os

class PianoKeyboardWidget(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.setMaximumHeight(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.num_keys = 88  # Full piano
        self.start_note = 21  # A0
        self.main_window = main_window

    def paintEvent(self, event):
        painter = QPainter(self)
        key_w = self.width() / self.num_keys
        key_h = self.height()
        # Draw white keys
        for i in range(self.num_keys):
            midi_note = self.start_note + i
            if not self.is_black_key(midi_note):
                x = int(i * key_w)
                painter.setBrush(Qt.white)
                painter.setPen(Qt.black)
                painter.drawRect(x, 0, int(key_w), key_h)
        # Draw black keys
        for i in range(self.num_keys):
            midi_note = self.start_note + i
            if self.is_black_key(midi_note):
                x = int(i * key_w + key_w * 0.6)
                painter.setBrush(Qt.black)
                painter.setPen(Qt.black)
                painter.drawRect(x, 0, int(key_w * 0.8), int(key_h * 0.6))

    def mousePressEvent(self, event):
        key_w = self.width() / self.num_keys
        idx = int(event.x() // key_w)
        midi_note = self.start_note + idx
        self.play_note(midi_note)

    def play_note(self, midi_note):
        if not self.main_window or not hasattr(self.main_window, "preset"):
            return
        # Find a mapping that covers this note
        mappings = getattr(self.main_window.preset, "mappings", [])
        for m in mappings:
            if isinstance(m, dict):
                lo = m.get("lo", 0)
                hi = m.get("hi", 127)
                path = m.get("path", "")
            else:
                lo = getattr(m, "lo", 0)
                hi = getattr(m, "hi", 127)
                path = getattr(m, "path", "")
            if lo <= midi_note <= hi and path:
                if os.path.exists(path):
                    QSound.play(path)
                else:
                    abs_path = os.path.join(os.getcwd(), path)
                    if os.path.exists(abs_path):
                        QSound.play(abs_path)
                break

    @staticmethod
    def is_black_key(midi_note):
        return midi_note % 12 in [1, 3, 6, 8, 10]
