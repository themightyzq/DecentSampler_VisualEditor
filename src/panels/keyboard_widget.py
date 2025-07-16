from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QColorDialog, QFormLayout, QGroupBox
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont
import math

class KeyboardColorRange:
    """Represents a color range for keyboard keys"""
    def __init__(self, lo_note=0, hi_note=127, color="FF444444", pressed_color="FF888888"):
        self.lo_note = lo_note
        self.hi_note = hi_note
        self.color = color  # Normal color (ARGB hex)
        self.pressed_color = pressed_color  # Pressed color (ARGB hex)

class DecentSamplerKeyboard(QWidget):
    """DecentSampler-style keyboard widget with color mapping support"""
    keyPressed = pyqtSignal(int)  # MIDI note number
    keyReleased = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color_ranges = [KeyboardColorRange()]  # Default range covers all keys
        self.pressed_keys = set()
        self.sample_mappings = []  # List of sample zones for visual feedback
        
        # Keyboard layout constants
        self.start_note = 21  # A0
        self.end_note = 108   # C8
        self.octave_width = 140  # Width of one octave in pixels
        self.white_key_height = 60
        self.black_key_height = 40
        
        # Calculate widget size
        num_octaves = (self.end_note - self.start_note + 1) / 12
        self.setFixedSize(int(num_octaves * self.octave_width), self.white_key_height + 10)
        self.setMouseTracking(True)
        
    def set_color_ranges(self, ranges):
        """Set the color ranges for the keyboard"""
        self.color_ranges = ranges or [KeyboardColorRange()]
        self.update()
        
    def set_sample_mappings(self, mappings):
        """Set sample mappings to show on keyboard"""
        self.sample_mappings = mappings
        self.update()
        
    def get_key_color(self, note, pressed=False):
        """Get the color for a specific note"""
        # Find the most specific range that contains this note
        applicable_ranges = [r for r in self.color_ranges if r.lo_note <= note <= r.hi_note]
        if not applicable_ranges:
            # Default colors
            return QColor("#888888" if pressed else "#444444")
        
        # Use the most specific range (smallest range)
        best_range = min(applicable_ranges, key=lambda r: r.hi_note - r.lo_note)
        color_str = best_range.pressed_color if pressed else best_range.color
        
        # Convert ARGB hex to QColor
        if color_str.startswith("FF"):
            # Remove alpha channel for RGB
            color_str = "#" + color_str[2:]
        elif not color_str.startswith("#"):
            color_str = "#" + color_str
            
        return QColor(color_str)
        
    def is_black_key(self, note):
        """Check if a note corresponds to a black key"""
        note_in_octave = note % 12
        return note_in_octave in [1, 3, 6, 8, 10]  # C#, D#, F#, G#, A#
        
    def get_white_key_index(self, note):
        """Get the index of a white key (0-based within the keyboard)"""
        octave = note // 12
        note_in_octave = note % 12
        
        # Map note to white key index within octave
        white_key_map = {0: 0, 2: 1, 4: 2, 5: 3, 7: 4, 9: 5, 11: 6}  # C, D, E, F, G, A, B
        if note_in_octave not in white_key_map:
            return None  # Black key
            
        white_in_octave = white_key_map[note_in_octave]
        return octave * 7 + white_in_octave
        
    def get_key_rect(self, note):
        """Get the rectangle for a specific key"""
        if self.is_black_key(note):
            return self.get_black_key_rect(note)
        else:
            return self.get_white_key_rect(note)
            
    def get_white_key_rect(self, note):
        """Get rectangle for a white key"""
        white_index = self.get_white_key_index(note)
        if white_index is None:
            return QRect()
            
        white_key_width = self.octave_width // 7
        x = white_index * white_key_width
        return QRect(x, 5, white_key_width - 1, self.white_key_height)
        
    def get_black_key_rect(self, note):
        """Get rectangle for a black key"""
        octave = note // 12
        note_in_octave = note % 12
        
        # Position within octave for black keys
        black_positions = {1: 0.7, 3: 1.3, 6: 2.7, 8: 3.3, 10: 4.3}  # Relative to white keys
        if note_in_octave not in black_positions:
            return QRect()
            
        white_key_width = self.octave_width // 7
        black_key_width = white_key_width * 0.6
        
        relative_pos = black_positions[note_in_octave]
        x = octave * self.octave_width + relative_pos * white_key_width - black_key_width / 2
        
        return QRect(int(x), 5, int(black_key_width), self.black_key_height)
        
    def note_at_position(self, pos):
        """Get the note number at a given position"""
        # Check black keys first (they're on top)
        for note in range(self.start_note, self.end_note + 1):
            if self.is_black_key(note):
                rect = self.get_black_key_rect(note)
                if rect.contains(pos):
                    return note
                    
        # Check white keys
        for note in range(self.start_note, self.end_note + 1):
            if not self.is_black_key(note):
                rect = self.get_white_key_rect(note)
                if rect.contains(pos):
                    return note
                    
        return None
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw white keys first
        for note in range(self.start_note, self.end_note + 1):
            if not self.is_black_key(note):
                rect = self.get_white_key_rect(note)
                if rect.isValid():
                    pressed = note in self.pressed_keys
                    color = self.get_key_color(note, pressed)
                    
                    # Check if this note has a sample mapping
                    has_sample = any(
                        mapping.lo <= note <= mapping.hi 
                        for mapping in self.sample_mappings 
                        if hasattr(mapping, 'lo') and hasattr(mapping, 'hi')
                    )
                    
                    # Draw key background
                    painter.fillRect(rect, QBrush(color))
                    
                    # Draw border
                    painter.setPen(QPen(QColor("#222222"), 1))
                    painter.drawRect(rect)
                    
                    # Draw sample indicator
                    if has_sample:
                        painter.setPen(QPen(QColor("#00FF00"), 2))
                        indicator_rect = QRect(rect.x() + 2, rect.bottom() - 8, rect.width() - 4, 4)
                        painter.drawRect(indicator_rect)
                        
        # Draw black keys on top
        for note in range(self.start_note, self.end_note + 1):
            if self.is_black_key(note):
                rect = self.get_black_key_rect(note)
                if rect.isValid():
                    pressed = note in self.pressed_keys
                    color = self.get_key_color(note, pressed)
                    
                    # Check if this note has a sample mapping
                    has_sample = any(
                        mapping.lo <= note <= mapping.hi 
                        for mapping in self.sample_mappings 
                        if hasattr(mapping, 'lo') and hasattr(mapping, 'hi')
                    )
                    
                    # Draw key background
                    painter.fillRect(rect, QBrush(color))
                    
                    # Draw border
                    painter.setPen(QPen(QColor("#000000"), 1))
                    painter.drawRect(rect)
                    
                    # Draw sample indicator
                    if has_sample:
                        painter.setPen(QPen(QColor("#00FF00"), 2))
                        indicator_rect = QRect(rect.x() + 1, rect.bottom() - 6, rect.width() - 2, 3)
                        painter.drawRect(indicator_rect)
                        
        # Draw note labels on white keys (C notes)
        painter.setPen(QPen(QColor("#666666")))
        painter.setFont(QFont("Arial", 8))
        for note in range(self.start_note, self.end_note + 1):
            if note % 12 == 0:  # C notes
                rect = self.get_white_key_rect(note)
                if rect.isValid():
                    octave = note // 12 - 1  # MIDI octave numbering
                    label = f"C{octave}"
                    painter.drawText(rect, Qt.AlignBottom | Qt.AlignHCenter, label)
                    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            note = self.note_at_position(event.pos())
            if note is not None:
                self.pressed_keys.add(note)
                self.keyPressed.emit(note)
                self.update()
                
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            note = self.note_at_position(event.pos())
            if note is not None and note in self.pressed_keys:
                self.pressed_keys.remove(note)
                self.keyReleased.emit(note)
                self.update()

class KeyboardColorEditor(QGroupBox):
    """Editor for keyboard color ranges"""
    colorsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Keyboard Colors", parent)
        self.color_ranges = [KeyboardColorRange()]
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header with add/remove buttons
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Color Ranges:"))
        header_layout.addStretch()
        
        self.add_range_btn = QPushButton("Add Range")
        self.add_range_btn.clicked.connect(self.add_range)
        header_layout.addWidget(self.add_range_btn)
        
        self.remove_range_btn = QPushButton("Remove Range")
        self.remove_range_btn.clicked.connect(self.remove_range)
        header_layout.addWidget(self.remove_range_btn)
        
        layout.addLayout(header_layout)
        
        # Range selector
        self.range_combo = QComboBox()
        self.range_combo.currentIndexChanged.connect(self.on_range_selected)
        layout.addWidget(self.range_combo)
        
        # Range editor
        range_form = QFormLayout()
        
        # Note range
        note_layout = QHBoxLayout()
        
        self.lo_note_spin = QComboBox()
        self.lo_note_spin.setEditable(True)
        self.hi_note_spin = QComboBox()
        self.hi_note_spin.setEditable(True)
        
        # Populate with MIDI note names
        note_names = []
        for note in range(128):
            octave = note // 12 - 1
            note_name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][note % 12]
            note_names.append(f"{note_name}{octave} ({note})")
            
        self.lo_note_spin.addItems(note_names)
        self.hi_note_spin.addItems(note_names)
        
        self.lo_note_spin.currentIndexChanged.connect(self.on_range_changed)
        self.hi_note_spin.currentIndexChanged.connect(self.on_range_changed)
        
        note_layout.addWidget(self.lo_note_spin)
        note_layout.addWidget(QLabel("to"))
        note_layout.addWidget(self.hi_note_spin)
        
        note_widget = QWidget()
        note_widget.setLayout(note_layout)
        range_form.addRow("Note Range:", note_widget)
        
        # Colors
        color_layout = QHBoxLayout()
        
        self.normal_color_btn = QPushButton("Normal Color")
        self.normal_color_btn.clicked.connect(self.choose_normal_color)
        color_layout.addWidget(self.normal_color_btn)
        
        self.pressed_color_btn = QPushButton("Pressed Color")
        self.pressed_color_btn.clicked.connect(self.choose_pressed_color)
        color_layout.addWidget(self.pressed_color_btn)
        
        color_widget = QWidget()
        color_widget.setLayout(color_layout)
        range_form.addRow("Colors:", color_widget)
        
        layout.addLayout(range_form)
        self.setLayout(layout)
        
        self.update_range_list()
        
    def add_range(self):
        """Add a new color range"""
        new_range = KeyboardColorRange(60, 71, "FFFF0000", "FFFF8888")  # Red C4-B4
        self.color_ranges.append(new_range)
        self.update_range_list()
        self.range_combo.setCurrentIndex(len(self.color_ranges) - 1)
        self.colorsChanged.emit()
        
    def remove_range(self):
        """Remove the selected color range"""
        current_index = self.range_combo.currentIndex()
        if 0 <= current_index < len(self.color_ranges) and len(self.color_ranges) > 1:
            del self.color_ranges[current_index]
            self.update_range_list()
            self.colorsChanged.emit()
            
    def update_range_list(self):
        """Update the range combo box"""
        self.range_combo.clear()
        for i, range_obj in enumerate(self.color_ranges):
            label = f"Range {i+1}: {range_obj.lo_note}-{range_obj.hi_note}"
            self.range_combo.addItem(label)
            
        if self.color_ranges:
            self.on_range_selected(0)
            
    def on_range_selected(self, index):
        """Handle range selection"""
        if 0 <= index < len(self.color_ranges):
            range_obj = self.color_ranges[index]
            self.lo_note_spin.setCurrentIndex(range_obj.lo_note)
            self.hi_note_spin.setCurrentIndex(range_obj.hi_note)
            self.update_color_buttons(range_obj)
            
    def on_range_changed(self):
        """Handle range parameter changes"""
        current_index = self.range_combo.currentIndex()
        if 0 <= current_index < len(self.color_ranges):
            range_obj = self.color_ranges[current_index]
            range_obj.lo_note = self.lo_note_spin.currentIndex()
            range_obj.hi_note = self.hi_note_spin.currentIndex()
            self.update_range_list()
            self.range_combo.setCurrentIndex(current_index)
            self.colorsChanged.emit()
            
    def choose_normal_color(self):
        """Choose normal color"""
        current_index = self.range_combo.currentIndex()
        if 0 <= current_index < len(self.color_ranges):
            range_obj = self.color_ranges[current_index]
            current_color = QColor("#" + range_obj.color[2:] if range_obj.color.startswith("FF") else range_obj.color)
            color = QColorDialog.getColor(current_color, self, "Choose Normal Color")
            if color.isValid():
                range_obj.color = "FF" + color.name()[1:]  # Add alpha, remove #
                self.update_color_buttons(range_obj)
                self.colorsChanged.emit()
                
    def choose_pressed_color(self):
        """Choose pressed color"""
        current_index = self.range_combo.currentIndex()
        if 0 <= current_index < len(self.color_ranges):
            range_obj = self.color_ranges[current_index]
            current_color = QColor("#" + range_obj.pressed_color[2:] if range_obj.pressed_color.startswith("FF") else range_obj.pressed_color)
            color = QColorDialog.getColor(current_color, self, "Choose Pressed Color")
            if color.isValid():
                range_obj.pressed_color = "FF" + color.name()[1:]  # Add alpha, remove #
                self.update_color_buttons(range_obj)
                self.colorsChanged.emit()
                
    def update_color_buttons(self, range_obj):
        """Update color button appearances"""
        normal_color = "#" + range_obj.color[2:] if range_obj.color.startswith("FF") else range_obj.color
        pressed_color = "#" + range_obj.pressed_color[2:] if range_obj.pressed_color.startswith("FF") else range_obj.pressed_color
        
        self.normal_color_btn.setStyleSheet(f"QPushButton {{ background-color: {normal_color}; }}")
        self.pressed_color_btn.setStyleSheet(f"QPushButton {{ background-color: {pressed_color}; }}")
        
    def get_color_ranges(self):
        """Get the current color ranges"""
        return self.color_ranges
        
    def set_color_ranges(self, ranges):
        """Set the color ranges"""
        self.color_ranges = ranges or [KeyboardColorRange()]
        self.update_range_list()

class KeyboardControlPanel(QWidget):
    """Complete keyboard control panel with keyboard and color editor"""
    keyboardChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Keyboard widget
        self.keyboard = DecentSamplerKeyboard()
        layout.addWidget(self.keyboard)
        
        # Color editor
        self.color_editor = KeyboardColorEditor()
        self.color_editor.colorsChanged.connect(self.on_colors_changed)
        layout.addWidget(self.color_editor)
        
        self.setLayout(layout)
        
    def on_colors_changed(self):
        """Handle color range changes"""
        ranges = self.color_editor.get_color_ranges()
        self.keyboard.set_color_ranges(ranges)
        self.keyboardChanged.emit()
        
    def set_sample_mappings(self, mappings):
        """Set sample mappings for visual feedback"""
        self.keyboard.set_sample_mappings(mappings)
        
    def get_keyboard_config(self):
        """Get keyboard configuration for export"""
        return self.color_editor.get_color_ranges()
        
    def set_keyboard_config(self, ranges):
        """Set keyboard configuration from import"""
        self.color_editor.set_color_ranges(ranges)
        self.keyboard.set_color_ranges(ranges)