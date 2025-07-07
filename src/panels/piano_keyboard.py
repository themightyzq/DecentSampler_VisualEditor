from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtMultimedia import QSound
import os

class PianoKeyboardWidget(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.setFixedWidth(812)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.num_keys = 88  # Full piano
        self.start_note = 21  # A0
        self.main_window = main_window

    def paintEvent(self, event):
        painter = QPainter(self)
        key_h = self.height()
        num_keys = 88
        start_note = 21  # A0
        white_key_count = 52  # 88-key piano has 52 white keys
        white_key_w = self.width() / white_key_count
        black_key_w = white_key_w * 0.7
        black_key_h = key_h * 0.6

        # Draw sample overlays (low-high range)
        if self.main_window and hasattr(self.main_window, "preset"):
            mappings = getattr(self.main_window.preset, "mappings", [])
            for m in mappings:
                lo = m.get("lo", 0) if isinstance(m, dict) else getattr(m, "lo", 0)
                hi = m.get("hi", 0) if isinstance(m, dict) else getattr(m, "hi", 0)
                root = m.get("root", 0) if isinstance(m, dict) else getattr(m, "root", 0)
                # Find white key positions for lo and hi
                lo_x = self._key_x(lo, white_key_w)
                hi_x = self._key_x(hi, white_key_w)
                painter.setBrush(QColor(100, 200, 255, 80))
                painter.setPen(Qt.NoPen)
                painter.drawRect(int(lo_x), 0, int(hi_x - lo_x + white_key_w), int(key_h))
                # Draw root note marker
                root_x = self._key_x(root, white_key_w)
                painter.setBrush(QColor(255, 100, 100, 180))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(int(root_x + white_key_w/4), int(key_h - 18), int(white_key_w/2), 12)

        # Draw white keys
        x = 0
        white_key_positions = []
        for i in range(num_keys):
            midi_note = start_note + i
            if not self.is_black_key(midi_note):
                painter.setBrush(Qt.white)
                painter.setPen(Qt.black)
                painter.drawRect(int(x), 0, int(white_key_w), key_h)
                white_key_positions.append((midi_note, x))
                x += white_key_w

        # Draw black keys
        x = 0
        for i in range(num_keys):
            midi_note = start_note + i
            if not self.is_black_key(midi_note):
                x_white = x
                x += white_key_w
            else:
                # Black keys are between white keys
                painter.setBrush(Qt.black)
                painter.setPen(Qt.black)
                painter.drawRect(int(x_white + white_key_w * 0.65), 0, int(black_key_w), int(black_key_h))

    def _key_x(self, midi_note, white_key_w):
        # Returns the x position of the left edge of the given midi_note key
        # Only for white keys and for overlays
        start_note = 21
        x = 0
        for i in range(midi_note - start_note):
            if not self.is_black_key(start_note + i):
                x += white_key_w
        return x


    def mousePressEvent(self, event):
        # Map click to key based on fixed white key width and centering
        white_key_w = 18
        key_h = self.height()
        num_white_keys = sum(1 for i in range(self.num_keys) if not self.is_black_key(self.start_note + i))
        total_white_width = num_white_keys * white_key_w
        x_offset = (self.width() - total_white_width) // 2 if self.width() > total_white_width else 0
        x = event.x() - x_offset
        # First check black keys (on top)
        for i in range(self.num_keys):
            midi_note = self.start_note + i
            if self.is_black_key(midi_note):
                # Find position between adjacent white keys
                idx = i
                prev_white = None
                next_white = None
                for j in range(idx - 1, -1, -1):
                    if not self.is_black_key(self.start_note + j):
                        prev_white = j
                        break
                for j in range(idx + 1, self.num_keys):
                    if not self.is_black_key(self.start_note + j):
                        next_white = j
                        break
                if prev_white is not None and next_white is not None:
                    prev_x = sum(white_key_w for k in range(prev_white - self.start_note + 1) if not self.is_black_key(self.start_note + k))
                    x_black = prev_x + white_key_w - 12 // 2
                elif prev_white is not None:
                    prev_x = sum(white_key_w for k in range(prev_white - self.start_note + 1) if not self.is_black_key(self.start_note + k))
                    x_black = prev_x + white_key_w - 12 // 2
                else:
                    continue
                if 0 <= x - x_black <= 12 and 0 <= event.y() <= int(key_h * 0.6):
                    self.play_note(midi_note)
                    return
        # Then check white keys
        x_pos = 0
        for i in range(self.num_keys):
            midi_note = self.start_note + i
            if not self.is_black_key(midi_note):
                if x_pos <= x < x_pos + white_key_w:
                    self.play_note(midi_note)
                    return
                x_pos += white_key_w

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
