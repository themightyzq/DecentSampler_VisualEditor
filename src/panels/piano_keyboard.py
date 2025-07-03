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
        self.num_keys = 24  # 2 octaves
        self.start_note = 60  # Middle C
        self.main_window = main_window

    def paintEvent(self, event):
        painter = QPainter(self)
        key_w = self.width() // self.num_keys
        key_h = self.height()
        # Draw white keys
        for i in range(self.num_keys):
            x = i * key_w
            painter.setBrush(Qt.white)
            painter.setPen(Qt.black)
            painter.drawRect(x, 0, key_w, key_h)
        # Draw black keys
        black_offsets = [1, 3, 6, 8, 10]
        for i in range(self.num_keys):
            note = (self.start_note + i) % 12
            if note in black_offsets:
                x = i * key_w + int(0.7 * key_w)
                painter.setBrush(Qt.black)
                painter.setPen(Qt.black)
                painter.drawRect(x, 0, int(0.6 * key_w), int(0.6 * key_h))

    def mousePressEvent(self, event):
        key_w = self.width() // self.num_keys
        idx = event.x() // key_w
        midi_note = self.start_note + idx
        self.play_note(midi_note)

    def play_note(self, midi_note):
        if not self.main_window:
            return
        zone_map = getattr(self.main_window.sample_browser, "zone_map", {})
        for path, zone in zone_map.items():
            if zone["loNote"] <= midi_note <= zone["hiNote"]:
                if os.path.exists(path):
                    QSound.play(path)
                else:
                    abs_path = os.path.join(os.getcwd(), path)
                    if os.path.exists(abs_path):
                        QSound.play(abs_path)
                break
