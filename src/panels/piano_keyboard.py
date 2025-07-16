from PyQt5.QtWidgets import QWidget, QSizePolicy, QToolTip, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetrics, QLinearGradient
from PyQt5.QtMultimedia import QSound
from utils.audio_transposition import get_transposition_engine, SampleTranspositionWidget
import os
import colorsys
import math

class PianoKeyboardWidget(QWidget):
    """Enhanced piano keyboard with sophisticated sample mapping visualization"""
    
    noteClicked = pyqtSignal(int)  # MIDI note number
    mappingHovered = pyqtSignal(dict)  # Sample mapping info
    rangeSelected = pyqtSignal(int, int)  # start_note, end_note for visual mapping
    
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.setFixedHeight(120)  # Increased height for better visualization
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Responsive width
        self.num_keys = 88  # Full piano
        self.start_note = 21  # A0
        self.main_window = main_window
        
        # Visual settings
        self.show_mapping_colors = True
        self.show_velocity_layers = True
        self.show_sample_names = True
        self.animation_enabled = True
        
        # Color management
        self.mapping_colors = {}  # Cache for mapping colors
        self.color_palette = self._generate_color_palette()
        
        # Interaction state
        self.hovered_note = None
        self.pressed_note = None
        self.tooltip_timer = QTimer()
        self.tooltip_timer.setSingleShot(True)
        self.tooltip_timer.timeout.connect(self._show_tooltip)
        
        # Visual mapping mode state
        self.mapping_mode = False
        self.range_selection_active = False
        self.range_start_note = None
        self.range_end_note = None
        self.highlight_range = None
        
        
        # Transposition engine
        self.transposition_engine = get_transposition_engine()
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Setup responsive behavior
        self.setMinimumWidth(600)
        self.setMaximumHeight(150)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        key_h = self.height()
        white_key_count = 52  # 88-key piano has 52 white keys
        white_key_w = self.width() / white_key_count
        black_key_w = white_key_w * 0.7
        black_key_h = key_h * 0.6
        
        # Get sample mappings
        mappings = self._get_sample_mappings()
        
        # Calculate key positions
        white_key_positions = self._calculate_white_key_positions(white_key_w, key_h)
        black_key_positions = self._calculate_black_key_positions(white_key_w, black_key_w, black_key_h)
        
        # Draw sample mapping overlays BEFORE keys
        if self.show_mapping_colors and mappings:
            self._draw_sample_mapping_overlays(painter, mappings, white_key_w, key_h)
        
        # Draw highlight range if active
        if hasattr(self, 'highlight_range') and self.highlight_range:
            self._draw_highlight_range(painter, white_key_w, key_h)
        
        # Draw white keys with mapping indicators
        self._draw_white_keys(painter, white_key_positions, mappings)
        
        # Draw black keys with mapping indicators  
        self._draw_black_keys(painter, black_key_positions, mappings)
        
        # Draw velocity layer indicators
        if self.show_velocity_layers and mappings:
            self._draw_velocity_indicators(painter, mappings, white_key_w, key_h)
        
        # Draw root note markers
        self._draw_root_note_markers(painter, mappings, white_key_w, key_h)
        
        # Draw key labels
        self._draw_key_labels(painter, white_key_positions, white_key_w, key_h)
        
        # Draw sample name overlays
        if self.show_sample_names and mappings:
            self._draw_sample_name_overlays(painter, mappings, white_key_w, key_h)
        
        # Draw transposition indicators
        self._draw_transposition_indicators(painter, mappings, white_key_w, key_h)
        
        # Draw hover and press effects
        self._draw_interaction_effects(painter, white_key_w, key_h)
    
    def _get_sample_mappings(self):
        """Get sample mappings from main window"""
        if not self.main_window or not hasattr(self.main_window, "preset"):
            return []
            
        mappings = getattr(self.main_window.preset, "mappings", [])
        
        # Also check sample manager for additional zones
        if hasattr(self.main_window.preset, 'sample_manager'):
            sample_manager = self.main_window.preset.sample_manager
            if hasattr(sample_manager, 'get_zones'):
                zones = sample_manager.get_zones()
                mappings.extend(zones)
        
        return mappings
    
    def _generate_color_palette(self):
        """Generate a pleasing color palette for sample mappings"""
        colors = []
        num_colors = 12  # Generate 12 distinct colors
        
        for i in range(num_colors):
            hue = i / num_colors  # 0 to 1
            saturation = 0.7 + (i % 3) * 0.1  # Vary saturation slightly
            value = 0.8 + (i % 2) * 0.1  # Vary brightness slightly
            
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            color = QColor(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            colors.append(color)
        
        return colors
    
    def _get_mapping_color(self, mapping_index):
        """Get a unique color for a sample mapping"""
        if mapping_index not in self.mapping_colors:
            color_index = len(self.mapping_colors) % len(self.color_palette)
            self.mapping_colors[mapping_index] = self.color_palette[color_index]
        
        return self.mapping_colors[mapping_index]
    
    def _calculate_white_key_positions(self, white_key_w, key_h):
        """Calculate positions of all white keys"""
        positions = []
        x = 0
        
        for i in range(self.num_keys):
            midi_note = self.start_note + i
            if not self.is_black_key(midi_note):
                positions.append({
                    'note': midi_note,
                    'x': x,
                    'width': white_key_w,
                    'height': key_h,
                    'rect': QRect(int(x), 0, int(white_key_w), int(key_h))
                })
                x += white_key_w
        
        return positions
    
    def _calculate_black_key_positions(self, white_key_w, black_key_w, black_key_h):
        """Calculate positions of all black keys"""
        positions = []
        white_x = 0
        
        for i in range(self.num_keys):
            midi_note = self.start_note + i
            if self.is_black_key(midi_note):
                # Position between white keys
                black_x = white_x - (black_key_w / 2)
                positions.append({
                    'note': midi_note,
                    'x': black_x,
                    'width': black_key_w,
                    'height': black_key_h,
                    'rect': QRect(int(black_x), 0, int(black_key_w), int(black_key_h))
                })
            else:
                white_x += white_key_w
        
        return positions
    
    def _draw_sample_mapping_overlays(self, painter, mappings, white_key_w, key_h):
        """Draw colored overlays showing sample mapping ranges"""
        for i, mapping in enumerate(mappings):
            lo, hi, root, path = self._extract_mapping_info(mapping)
            
            # Calculate range boundaries
            lo_x = self._note_to_x_position(lo, white_key_w)
            hi_x = self._note_to_x_position(hi, white_key_w)
            range_width = hi_x - lo_x + white_key_w
            
            # Get mapping color with transparency
            base_color = self._get_mapping_color(i)
            overlay_color = QColor(base_color)
            overlay_color.setAlpha(60)  # Semi-transparent
            
            # Create gradient overlay
            gradient = QLinearGradient(lo_x, 0, lo_x + range_width, 0)
            gradient.setColorAt(0.0, overlay_color)
            gradient.setColorAt(0.5, QColor(overlay_color.red(), overlay_color.green(), overlay_color.blue(), 80))
            gradient.setColorAt(1.0, overlay_color)
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(lo_x), 0, int(range_width), int(key_h))
            
            # Draw range border
            border_color = QColor(base_color)
            border_color.setAlpha(150)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(border_color, 2))
            painter.drawRect(int(lo_x), 0, int(range_width), int(key_h))
    
    def _draw_white_keys(self, painter, positions, mappings):
        """Draw white keys with mapping indicators"""
        for pos in positions:
            # Determine if this key is mapped
            is_mapped = any(self._note_in_mapping_range(pos['note'], m) for m in mappings)
            is_hovered = pos['note'] == self.hovered_note
            is_pressed = pos['note'] == self.pressed_note
            
            # Choose key color
            if is_pressed:
                key_color = QColor(200, 200, 200)
            elif is_hovered:
                key_color = QColor(245, 245, 245)
            elif is_mapped:
                key_color = QColor(250, 250, 250)  # Slightly off-white for mapped keys
            else:
                key_color = Qt.white
            
            # Draw key
            painter.setBrush(key_color)
            painter.setPen(QPen(Qt.black, 1))
            painter.drawRect(pos['rect'])
            
            # Draw mapping indicator stripe at bottom
            if is_mapped:
                mapping = next(m for m in mappings if self._note_in_mapping_range(pos['note'], m))
                mapping_index = mappings.index(mapping)
                stripe_color = self._get_mapping_color(mapping_index)
                stripe_color.setAlpha(180)
                
                stripe_height = 8
                stripe_rect = QRect(
                    int(pos['x'] + 2), 
                    int(pos['height'] - stripe_height - 2), 
                    int(pos['width'] - 4), 
                    stripe_height
                )
                painter.setBrush(stripe_color)
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(stripe_rect, 2, 2)
    
    def _draw_black_keys(self, painter, positions, mappings):
        """Draw black keys with mapping indicators"""
        for pos in positions:
            is_mapped = any(self._note_in_mapping_range(pos['note'], m) for m in mappings)
            is_hovered = pos['note'] == self.hovered_note
            is_pressed = pos['note'] == self.pressed_note
            
            # Choose key color
            if is_pressed:
                key_color = QColor(60, 60, 60)
            elif is_hovered:
                key_color = QColor(40, 40, 40)
            else:
                key_color = Qt.black
            
            # Draw key
            painter.setBrush(key_color)
            painter.setPen(QPen(QColor(80, 80, 80), 1))
            painter.drawRect(pos['rect'])
            
            # Draw mapping indicator for black keys
            if is_mapped:
                mapping = next(m for m in mappings if self._note_in_mapping_range(pos['note'], m))
                mapping_index = mappings.index(mapping)
                indicator_color = self._get_mapping_color(mapping_index)
                
                # Small indicator at top of black key
                indicator_size = 6
                indicator_x = pos['x'] + (pos['width'] - indicator_size) / 2
                indicator_y = 5
                
                painter.setBrush(indicator_color)
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(int(indicator_x), int(indicator_y), indicator_size, indicator_size)
    
    def _draw_velocity_indicators(self, painter, mappings, white_key_w, key_h):
        """Draw indicators for velocity layers"""
        # Group mappings by velocity ranges
        velocity_groups = {}
        for mapping in mappings:
            lo, hi, root, path = self._extract_mapping_info(mapping)
            vel_range = getattr(mapping, 'velocityRange', (0, 127))
            
            if vel_range not in velocity_groups:
                velocity_groups[vel_range] = []
            velocity_groups[vel_range].append(mapping)
        
        # Draw velocity layer indicators
        if len(velocity_groups) > 1:
            layer_height = 3
            y_offset = key_h - 20
            
            for i, (vel_range, group_mappings) in enumerate(velocity_groups.items()):
                layer_color = self.color_palette[i % len(self.color_palette)]
                layer_color.setAlpha(120)
                
                for mapping in group_mappings:
                    lo, hi, root, path = self._extract_mapping_info(mapping)
                    lo_x = self._note_to_x_position(lo, white_key_w)
                    hi_x = self._note_to_x_position(hi, white_key_w)
                    
                    painter.setBrush(layer_color)
                    painter.setPen(Qt.NoPen)
                    painter.drawRect(
                        int(lo_x), 
                        int(y_offset + i * layer_height), 
                        int(hi_x - lo_x + white_key_w), 
                        layer_height
                    )
    
    def _draw_root_note_markers(self, painter, mappings, white_key_w, key_h):
        """Draw root note markers"""
        for mapping in mappings:
            lo, hi, root, path = self._extract_mapping_info(mapping)
            
            root_x = self._note_to_x_position(root, white_key_w)
            
            # Draw root note diamond marker
            diamond_size = 8
            center_x = root_x + white_key_w / 2
            center_y = key_h - 30
            
            # Create diamond points
            points = [
                (center_x, center_y - diamond_size),  # Top
                (center_x + diamond_size, center_y),  # Right
                (center_x, center_y + diamond_size),  # Bottom
                (center_x - diamond_size, center_y)   # Left
            ]
            
            # Draw filled diamond  
            from PyQt5.QtGui import QPolygon
            from PyQt5.QtCore import QPoint
            
            diamond_points = [QPoint(int(point[0]), int(point[1])) for point in points]
            polygon = QPolygon(diamond_points)
            
            painter.setBrush(QColor(255, 50, 50, 200))
            painter.setPen(QPen(QColor(200, 0, 0), 2))
            painter.drawPolygon(polygon)
    
    def _draw_highlight_range(self, painter, white_key_w, key_h):
        """Draw highlighted range for preview/selection"""
        if not self.highlight_range:
            return
            
        lo = self.highlight_range['lo']
        hi = self.highlight_range['hi']
        color = self.highlight_range['color']
        
        lo_x = self._note_to_x_position(lo, white_key_w)
        hi_x = self._note_to_x_position(hi, white_key_w)
        range_width = hi_x - lo_x + white_key_w
        
        painter.setBrush(color)
        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 200), 3))
        painter.drawRect(int(lo_x), 0, int(range_width), int(key_h))
    
    def _draw_transposition_indicators(self, painter, mappings, white_key_w, key_h):
        """Draw transposition indicators showing pitch direction"""
        if not mappings:
            return
            
        painter.setFont(QFont("Arial", 6))
        
        for mapping in mappings:
            lo, hi, root, path = self._extract_mapping_info(mapping)
            
            # Draw indicators for each note in the range
            for note in range(lo, hi + 1):
                if note == root:
                    continue  # Skip root note (already has diamond marker)
                
                # Calculate transposition
                semitone_diff = note - root
                if semitone_diff == 0:
                    continue
                
                # Get note position
                note_x = self._note_to_x_position(note, white_key_w)
                
                # Choose indicator based on transposition direction and amount
                if abs(semitone_diff) <= 12:  # Within one octave
                    if semitone_diff > 0:
                        # Up arrow for higher notes
                        indicator = "↑"
                        color = QColor(0, 150, 0, 180)  # Green
                    else:
                        # Down arrow for lower notes  
                        indicator = "↓"
                        color = QColor(150, 0, 0, 180)  # Red
                else:
                    # Double arrows for more than octave
                    if semitone_diff > 0:
                        indicator = "⇈"
                        color = QColor(0, 100, 0, 180)  # Dark green
                    else:
                        indicator = "⇊"
                        color = QColor(100, 0, 0, 180)  # Dark red
                
                # Position indicator
                if self.is_black_key(note):
                    # Black key - position at bottom
                    indicator_x = note_x + (white_key_w * 0.35)
                    indicator_y = key_h * 0.5
                else:
                    # White key - position at top right
                    indicator_x = note_x + white_key_w - 15
                    indicator_y = 15
                
                # Draw indicator
                painter.setPen(color)
                painter.drawText(int(indicator_x), int(indicator_y), indicator)
    
    def _draw_key_labels(self, painter, white_key_positions, white_key_w, key_h):
        """Draw key labels (C notes)"""
        painter.setPen(Qt.black)
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        
        for pos in white_key_positions:
            if (pos['note'] % 12) == 0:  # C key
                label = self.midi_note_name(pos['note'])
                text_rect = QRect(int(pos['x']), int(key_h - 20), int(white_key_w), 15)
                painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, label)
    
    def _draw_sample_name_overlays(self, painter, mappings, white_key_w, key_h):
        """Draw sample names on mapped ranges"""
        painter.setPen(Qt.black)
        font = QFont()
        font.setPointSize(7)
        painter.setFont(font)
        
        for mapping in mappings:
            lo, hi, root, path = self._extract_mapping_info(mapping)
            
            # Get sample name from path
            sample_name = os.path.splitext(os.path.basename(path))[0] if path else "Sample"
            if len(sample_name) > 12:
                sample_name = sample_name[:12] + "..."
            
            # Calculate text position
            lo_x = self._note_to_x_position(lo, white_key_w)
            hi_x = self._note_to_x_position(hi, white_key_w)
            range_width = hi_x - lo_x + white_key_w
            
            if range_width > 60:  # Only show text if range is wide enough
                text_rect = QRect(int(lo_x + 5), 5, int(range_width - 10), 20)
                painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignTop, sample_name)
    
    def _draw_interaction_effects(self, painter, white_key_w, key_h):
        """Draw hover and press visual effects"""
        if self.hovered_note is not None:
            # Draw subtle glow effect for hovered note
            note_x = self._note_to_x_position(self.hovered_note, white_key_w)
            
            glow_color = QColor(100, 150, 255, 50)
            painter.setBrush(glow_color)
            painter.setPen(Qt.NoPen)
            
            if self.is_black_key(self.hovered_note):
                # Black key glow
                painter.drawRect(int(note_x - 5), -2, int(white_key_w * 0.7 + 10), int(key_h * 0.6 + 4))
            else:
                # White key glow
                painter.drawRect(int(note_x - 2), -2, int(white_key_w + 4), int(key_h + 4))
    
    # Helper Methods
    def _extract_mapping_info(self, mapping):
        """Extract lo, hi, root, path from mapping object or dict"""
        if isinstance(mapping, dict):
            lo = mapping.get("lo", 0)
            hi = mapping.get("hi", 127)
            root = mapping.get("root", 60)
            path = mapping.get("path", "")
        else:
            lo = getattr(mapping, "lo", getattr(mapping, "loNote", 0))
            hi = getattr(mapping, "hi", getattr(mapping, "hiNote", 127))
            root = getattr(mapping, "root", getattr(mapping, "rootNote", 60))
            path = getattr(mapping, "path", "")
        
        return lo, hi, root, path
    
    def _note_in_mapping_range(self, note, mapping):
        """Check if a note is within a mapping's range"""
        lo, hi, root, path = self._extract_mapping_info(mapping)
        return lo <= note <= hi
    
    def _note_to_x_position(self, midi_note, white_key_w):
        """Convert MIDI note to X position on keyboard"""
        # Count white keys from start to this note
        white_keys_before = 0
        for i in range(midi_note - self.start_note):
            if not self.is_black_key(self.start_note + i):
                white_keys_before += 1
        
        return white_keys_before * white_key_w
    
    def _get_note_at_position(self, x, y, white_key_w, key_h):
        """Get MIDI note at given position"""
        black_key_h = key_h * 0.6
        black_key_w = white_key_w * 0.7
        
        # Check black keys first (they're on top)
        if y <= black_key_h:
            white_key_index = int(x // white_key_w)
            white_keys_checked = 0
            
            for i in range(self.num_keys):
                midi_note = self.start_note + i
                if not self.is_black_key(midi_note):
                    if white_keys_checked == white_key_index:
                        # Check if there's a black key to the right
                        if i + 1 < self.num_keys and self.is_black_key(self.start_note + i + 1):
                            black_key_x = (white_keys_checked + 1) * white_key_w - black_key_w / 2
                            if black_key_x <= x <= black_key_x + black_key_w:
                                return self.start_note + i + 1
                        break
                    white_keys_checked += 1
        
        # Check white keys
        white_key_index = int(x // white_key_w)
        white_keys_checked = 0
        
        for i in range(self.num_keys):
            midi_note = self.start_note + i
            if not self.is_black_key(midi_note):
                if white_keys_checked == white_key_index:
                    return midi_note
                white_keys_checked += 1
        
        return None
    
    # Visual Mapping Methods
    def set_mapping_mode(self, enabled):
        """Enable or disable visual mapping mode"""
        self.mapping_mode = enabled
        if not enabled:
            self.range_selection_active = False
            self.range_start_note = None
            self.range_end_note = None
            self.highlight_range = None
        self.update()
    
    def clear_range_selection(self):
        """Clear any active range selection"""
        self.range_selection_active = False
        self.range_start_note = None
        self.range_end_note = None
        self.highlight_range = None
        self.update()
    
    def set_highlight_range(self, start_note, end_note):
        """Set a range to highlight (for visual feedback)"""
        self.highlight_range = (start_note, end_note)
        self.update()
    
    def _draw_highlight_range(self, painter, white_key_w, key_h):
        """Draw the highlighted range for visual mapping"""
        if not self.highlight_range:
            return
        
        start_note, end_note = self.highlight_range
        
        # Calculate range bounds
        start_x = self._note_to_x_position(start_note, white_key_w)
        end_x = self._note_to_x_position(end_note, white_key_w)
        
        # Create highlight color
        if self.range_selection_active:
            # Active selection - bright blue
            highlight_color = QColor(100, 150, 255, 80)
            border_color = QColor(100, 150, 255, 200)
        else:
            # Completed selection - green
            highlight_color = QColor(100, 255, 150, 60)
            border_color = QColor(100, 255, 150, 150)
        
        # Draw highlight rectangle
        painter.setBrush(highlight_color)
        painter.setPen(QPen(border_color, 2))
        
        range_rect = QRect(
            int(start_x), 
            0, 
            int(end_x - start_x + white_key_w), 
            key_h
        )
        painter.drawRect(range_rect)
        
        # Draw range indicators
        painter.setPen(QPen(border_color, 3))
        painter.drawLine(int(start_x), 0, int(start_x), key_h)  # Start line
        painter.drawLine(int(end_x + white_key_w), 0, int(end_x + white_key_w), key_h)  # End line

    def _key_x(self, midi_note, white_key_w):
        # Returns the x position of the left edge of the given midi_note key
        # Only for white keys and for overlays
        start_note = self.start_note
        x = 0
        for i in range(midi_note - start_note):
            if not self.is_black_key(start_note + i):
                x += white_key_w
        return x

    @staticmethod
    def midi_note_name(n):
        # Returns e.g. "C4"
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (n // 12) - 1
        name = note_names[n % 12]
        return f"{name}{octave}"

    def mousePressEvent(self, event):
        """Handle mouse press events for note playing and range selection"""
        white_key_w = self.width() / 52  # 52 white keys
        key_h = self.height()
        
        # Get the note at the clicked position
        clicked_note = self._get_note_at_position(event.x(), event.y(), white_key_w, key_h)
        
        if clicked_note is not None:
            if self.mapping_mode:
                # Start range selection
                self.range_selection_active = True
                self.range_start_note = clicked_note
                self.range_end_note = clicked_note
                self.highlight_range = (clicked_note, clicked_note)
                self.update()
            else:
                # Normal note playing
                self.pressed_note = clicked_note
                self.play_note(clicked_note)
                self.noteClicked.emit(clicked_note)
                self.update()  # Trigger repaint to show pressed state
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if self.mapping_mode and self.range_selection_active:
            # Complete range selection
            self.range_selection_active = False
            if self.range_start_note is not None and self.range_end_note is not None:
                # Ensure start <= end
                start = min(self.range_start_note, self.range_end_note)
                end = max(self.range_start_note, self.range_end_note)
                self.rangeSelected.emit(start, end)
                # Keep highlight for visual feedback
                self.highlight_range = (start, end)
            self.update()
        elif self.pressed_note is not None:
            self.pressed_note = None
            self.update()  # Trigger repaint to remove pressed state
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for hover effects, tooltips, and range selection"""
        white_key_w = self.width() / 52
        key_h = self.height()
        
        # Get the note under the mouse
        hovered_note = self._get_note_at_position(event.x(), event.y(), white_key_w, key_h)
        
        if self.mapping_mode and self.range_selection_active and hovered_note is not None:
            # Update range selection
            self.range_end_note = hovered_note
            start = min(self.range_start_note, self.range_end_note)
            end = max(self.range_start_note, self.range_end_note)
            self.highlight_range = (start, end)
            self.update()
        
        if hovered_note != self.hovered_note:
            self.hovered_note = hovered_note
            self.update()  # Trigger repaint for hover effect
            
            # Setup tooltip timer (only if not in mapping mode)
            if not self.mapping_mode and hovered_note is not None:
                self.tooltip_timer.start(500)  # Show tooltip after 500ms
            else:
                self.tooltip_timer.stop()
                QToolTip.hideText()
    
    def leaveEvent(self, event):
        """Handle mouse leave events"""
        self.hovered_note = None
        self.pressed_note = None
        self.tooltip_timer.stop()
        QToolTip.hideText()
        self.update()
    
    def _show_tooltip(self):
        """Show tooltip for hovered note"""
        if self.hovered_note is None:
            return
            
        # Get mapping info for this note
        mappings = self._get_sample_mappings()
        note_mappings = [m for m in mappings if self._note_in_mapping_range(self.hovered_note, m)]
        
        if note_mappings:
            tooltip_text = self._generate_tooltip_text(self.hovered_note, note_mappings)
            
            # Calculate tooltip position
            white_key_w = self.width() / 52
            note_x = self._note_to_x_position(self.hovered_note, white_key_w)
            
            # Convert to global coordinates
            global_pos = self.mapToGlobal(self.pos())
            tooltip_x = global_pos.x() + int(note_x + white_key_w / 2)
            tooltip_y = global_pos.y() - 10
            
            QToolTip.showText(self.cursor().pos(), tooltip_text, self)
        else:
            # Show basic note info
            note_name = self.midi_note_name(self.hovered_note)
            QToolTip.showText(self.cursor().pos(), f"{note_name} (MIDI {self.hovered_note})", self)
    
    def _generate_tooltip_text(self, note, mappings):
        """Generate tooltip text for a note with mappings"""
        note_name = self.midi_note_name(note)
        tooltip_lines = [f"<b>{note_name} (MIDI {note})</b>"]
        
        for i, mapping in enumerate(mappings):
            lo, hi, root, path = self._extract_mapping_info(mapping)
            
            # Sample info
            sample_name = os.path.splitext(os.path.basename(path))[0] if path else "Unknown"
            tooltip_lines.append(f"<b>Sample {i+1}:</b> {sample_name}")
            
            # Range info
            lo_name = self.midi_note_name(lo)
            hi_name = self.midi_note_name(hi)
            root_name = self.midi_note_name(root)
            tooltip_lines.append(f"Range: {lo_name} - {hi_name} (Root: {root_name})")
            
            # Velocity info
            if hasattr(mapping, 'velocityRange'):
                vel_range = mapping.velocityRange
                tooltip_lines.append(f"Velocity: {vel_range[0]} - {vel_range[1]}")
            
            # Additional info
            if hasattr(mapping, 'volume') and mapping.volume != 0:
                tooltip_lines.append(f"Volume: {mapping.volume:+.1f} dB")
            
            # Transposition info
            tune_cents = getattr(mapping, 'tune', 0.0)
            transposition_info = self.transposition_engine.get_transposition_info(note, root, tune_cents)
            
            if transposition_info['direction'] != 'none':
                direction_text = "↑" if transposition_info['direction'] == 'up' else "↓"
                tooltip_lines.append(f"<b>Transposition:</b> {direction_text} {transposition_info['semitones']} semitones")
                tooltip_lines.append(f"Pitch Ratio: {transposition_info['pitch_ratio']:.3f}")
                
                if abs(transposition_info['cents_total']) > 50:
                    tooltip_lines.append(f"Total Cents: {transposition_info['cents_total']:+.0f}")
            else:
                tooltip_lines.append("<b>Transposition:</b> Original pitch")
            
            if i < len(mappings) - 1:
                tooltip_lines.append("")  # Separator
        
        return "<br>".join(tooltip_lines)

    def play_note(self, midi_note):
        """Play a note with proper transposition"""
        if not self.main_window or not hasattr(self.main_window, "preset"):
            return
            
        # Find a mapping that covers this note
        mappings = self._get_sample_mappings()
        
        for mapping in mappings:
            lo, hi, root, path = self._extract_mapping_info(mapping)
            
            if lo <= midi_note <= hi and path:
                # Get additional parameters
                tune_cents = getattr(mapping, 'tune', 0.0)
                volume = getattr(mapping, 'volume', 0.0)  # Volume in dB
                
                # Convert dB to linear scale
                volume_linear = 10 ** (volume / 20) if volume != 0 else 1.0
                
                # Try to find the file
                sample_path = None
                if os.path.exists(path):
                    sample_path = path
                else:
                    abs_path = os.path.join(os.getcwd(), path)
                    if os.path.exists(abs_path):
                        sample_path = abs_path
                
                if sample_path:
                    # Use transposition engine for proper pitch shifting
                    success = self.transposition_engine.play_transposed_sample(
                        sample_path, midi_note, root, tune_cents, volume_linear
                    )
                    
                    if success:
                        break  # Successfully played, stop looking for more mappings
                    else:
                        # Fallback to direct playback
                        QSound.play(sample_path)
                        break

    @staticmethod
    def is_black_key(midi_note):
        return midi_note % 12 in [1, 3, 6, 8, 10]
    
    # Public methods for controlling visualization
    def refresh_mappings(self):
        """Refresh the keyboard visualization when mappings change"""
        # Clear color cache to regenerate colors
        self.mapping_colors.clear()
        self.update()  # Trigger repaint
    
    def set_visualization_options(self, show_colors=True, show_velocity=True, show_names=True):
        """Configure what visual elements to show"""
        self.show_mapping_colors = show_colors
        self.show_velocity_layers = show_velocity
        self.show_sample_names = show_names
        self.update()
    
    def highlight_note_range(self, lo_note, hi_note, color=None):
        """Highlight a specific note range (for preview/selection)"""
        if color is None:
            color = QColor(255, 255, 0, 100)  # Yellow highlight
        
        # Store highlight info for paint event
        self.highlight_range = {
            'lo': lo_note,
            'hi': hi_note,
            'color': color
        }
        self.update()
    
    def clear_highlight(self):
        """Clear any range highlighting"""
        self.highlight_range = None
        self.update()
    
    def get_mapping_legend(self):
        """Get legend information for all current mappings"""
        mappings = self._get_sample_mappings()
        legend_items = []
        
        for i, mapping in enumerate(mappings):
            lo, hi, root, path = self._extract_mapping_info(mapping)
            color = self._get_mapping_color(i)
            
            sample_name = os.path.splitext(os.path.basename(path))[0] if path else f"Sample {i+1}"
            lo_name = self.midi_note_name(lo)
            hi_name = self.midi_note_name(hi)
            root_name = self.midi_note_name(root)
            
            legend_items.append({
                'name': sample_name,
                'range': f"{lo_name} - {hi_name}",
                'root': root_name,
                'color': color,
                'path': path
            })
        
        return legend_items


class KeyboardLegendWidget(QWidget):
    """Legend widget showing color-coded sample mappings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.legend_items = []
        self.init_ui()
    
    def init_ui(self):
        self.setFixedHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Setup layout
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)
        
        # Header
        header = QLabel("📊 Sample Mapping Legend")
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setStyleSheet("color: #4a9eff; padding: 2px;")
        layout.addWidget(header)
        
        # Scroll area for legend items
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setMaximumHeight(70)
        
        self.legend_container = QWidget()
        self.legend_layout = QHBoxLayout()
        self.legend_layout.setContentsMargins(2, 2, 2, 2)
        self.legend_layout.setSpacing(8)
        self.legend_container.setLayout(self.legend_layout)
        
        self.scroll_area.setWidget(self.legend_container)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
        # Apply dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: white;
            }
            QScrollArea {
                border: 1px solid #444;
                border-radius: 3px;
                background-color: #333;
            }
        """)
    
    def update_legend(self, legend_items):
        """Update the legend with new items"""
        # Clear existing items
        for i in reversed(range(self.legend_layout.count())):
            self.legend_layout.itemAt(i).widget().setParent(None)
        
        self.legend_items = legend_items
        
        # Add new legend items
        for item in legend_items:
            legend_item = self.create_legend_item(item)
            self.legend_layout.addWidget(legend_item)
        
        # Add stretch to push items to the left
        self.legend_layout.addStretch()
    
    def create_legend_item(self, item):
        """Create a visual legend item"""
        container = QFrame()
        container.setFrameStyle(QFrame.StyledPanel)
        container.setFixedSize(120, 50)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(1)
        
        # Color indicator
        color_bar = QFrame()
        color_bar.setFixedHeight(8)
        color_bar.setStyleSheet(f"""
            background-color: rgb({item['color'].red()}, {item['color'].green()}, {item['color'].blue()});
            border-radius: 2px;
        """)
        layout.addWidget(color_bar)
        
        # Sample name
        name_label = QLabel(item['name'])
        name_label.setFont(QFont("Arial", 8, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        if len(item['name']) > 12:
            name_label.setText(item['name'][:12] + "...")
            name_label.setToolTip(item['name'])
        layout.addWidget(name_label)
        
        # Range info
        range_label = QLabel(item['range'])
        range_label.setFont(QFont("Arial", 7))
        range_label.setAlignment(Qt.AlignCenter)
        range_label.setStyleSheet("color: #ccc;")
        layout.addWidget(range_label)
        
        # Root note
        root_label = QLabel(f"Root: {item['root']}")
        root_label.setFont(QFont("Arial", 7))
        root_label.setAlignment(Qt.AlignCenter)
        root_label.setStyleSheet("color: #aaa;")
        layout.addWidget(root_label)
        
        container.setLayout(layout)
        container.setToolTip(f"Sample: {item['name']}\nRange: {item['range']}\nRoot: {item['root']}\nFile: {os.path.basename(item['path'])}")
        
        return container
