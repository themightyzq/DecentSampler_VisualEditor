"""
Audio Preview Widget for Sample Previewing
Provides quick audio preview functionality with waveform display
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, 
    QProgressBar, QFrame, QSizePolicy, QGraphicsOpacityEffect, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient
from utils.theme_manager import ThemeColors, ThemeFonts, ThemeSpacing, theme_manager
from utils.error_handling import ErrorHandler, with_error_handling
from utils.accessibility import (
    AccessibilityIndicator, AccessibilitySymbol, accessibility_settings,
    get_status_symbol
)
from widgets.loading_indicators import CircularProgress
import os
import wave
import threading
import time
import math
import random

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

class AudioPreviewEngine:
    """Simple audio preview engine using pygame or fallback"""
    
    def __init__(self):
        self.is_playing = False
        self.current_file = None
        self.position = 0
        self.error_handler = ErrorHandler()
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
            except Exception as e:
                self.error_handler.handle_error(e, "initializing pygame mixer", show_dialog=False)
        
    def load_file(self, file_path):
        """Load an audio file for preview"""
        try:
            if not PYGAME_AVAILABLE:
                self.error_handler.handle_error(
                    ImportError("pygame not available"),
                    "loading audio file",
                    show_dialog=False
                )
                return False
                
            if file_path.lower().endswith('.wav'):
                self.current_file = file_path
                return True
            else:
                # Non-WAV files not supported without additional libraries
                return False
        except Exception as e:
            self.error_handler.handle_error(e, "loading audio file", show_dialog=False)
            return False
    
    def play(self):
        """Start playback"""
        if not PYGAME_AVAILABLE:
            self.error_handler.handle_error(
                ImportError("pygame not available"),
                "playing audio",
                show_dialog=True
            )
            return False
            
        if self.current_file:
            try:
                pygame.mixer.music.load(self.current_file)
                pygame.mixer.music.play()
                self.is_playing = True
                return True
            except Exception as e:
                self.error_handler.handle_error(e, "playing audio file", show_dialog=True)
        return False
    
    def stop(self):
        """Stop playback"""
        if PYGAME_AVAILABLE:
            pygame.mixer.music.stop()
        self.is_playing = False
        self.position = 0
    
    def pause(self):
        """Pause playback"""
        if PYGAME_AVAILABLE:
            pygame.mixer.music.pause()
        self.is_playing = False
    
    def get_is_playing(self):
        """Check if currently playing"""
        if PYGAME_AVAILABLE:
            return pygame.mixer.music.get_busy()
        return False

class WaveformWorker(QThread):
    """Background worker for waveform loading"""
    waveform_loaded = pyqtSignal(list)  # Waveform data
    loading_progress = pyqtSignal(int)  # Progress percentage
    loading_error = pyqtSignal(str)     # Error message
    
    def __init__(self, file_path, widget_width):
        super().__init__()
        self.file_path = file_path
        self.widget_width = widget_width
        
    def run(self):
        """Load waveform in background thread"""
        try:
            self.loading_progress.emit(10)
            
            # Check if file exists
            if not os.path.exists(self.file_path):
                self.waveform_loaded.emit([])
                return
            
            self.loading_progress.emit(25)
            
            # Only process WAV files for now
            if not self.file_path.lower().endswith('.wav'):
                # For non-WAV files, generate a placeholder pattern
                import random
                random.seed(hash(os.path.basename(self.file_path)))
                num_points = 80
                waveform_data = []
                for i in range(num_points):
                    envelope = math.sin(i * math.pi / num_points)
                    noise = random.uniform(0.7, 1.3)
                    variation = math.sin(i * 0.3) * 0.5 + 1.0
                    value = int(envelope * noise * variation * 2500)
                    waveform_data.append(abs(value))
                self.waveform_loaded.emit(waveform_data)
                return
            
            self.loading_progress.emit(50)
            
            with wave.open(self.file_path, 'rb') as wav_file:
                frames = wav_file.readframes(-1)
                sample_width = wav_file.getsampwidth()
                channels = wav_file.getnchannels()
                frame_rate = wav_file.getframerate()
                
                self.loading_progress.emit(75)
                
                if NUMPY_AVAILABLE:
                    # Use numpy for efficient processing
                    if sample_width == 2:
                        samples = np.frombuffer(frames, dtype=np.int16)
                    elif sample_width == 3:
                        samples = np.frombuffer(frames, dtype=np.uint8)
                        samples = samples.reshape(-1, 3)
                        samples = np.array([s[0] | (s[1] << 8) | ((s[2] & 0x7F) << 16) - (0x800000 if s[2] & 0x80 else 0) for s in samples], dtype=np.int32)
                    else:
                        samples = np.frombuffer(frames, dtype=np.int8)
                    
                    if channels > 1:
                        samples = samples.reshape(-1, channels).mean(axis=1).astype(samples.dtype)
                    
                    # Calculate target points based on widget width
                    target_points = self.widget_width // 4
                    target_points = max(40, min(target_points, 200))
                    
                    # Handle edge cases
                    if len(samples) == 0:
                        self.waveform_loaded.emit([1000] * 50)  # Fallback data
                        return
                        
                    if len(samples) < target_points * 10:
                        target_points = max(10, len(samples) // 10)
                        
                    chunk_size = max(1, len(samples) // target_points)
                    if chunk_size <= 0:
                        chunk_size = 1  # Prevent division by zero
                    
                    waveform_data = []
                    for i in range(0, len(samples) - chunk_size, chunk_size):
                        chunk = samples[i:i + chunk_size]
                        if len(chunk) > 0:
                            peak = max(abs(chunk.min()), abs(chunk.max()))
                            waveform_data.append(float(peak))
                    
                    if len(waveform_data) > 0:
                        max_val = max(waveform_data) if max(waveform_data) > 0 else 1
                        waveform_data = [val / max_val * 32768 for val in waveform_data]
                else:
                    # Fallback without numpy
                    num_points = 100
                    bytes_per_sample = sample_width * channels
                    total_samples = len(frames) // bytes_per_sample
                    step = max(1, total_samples // num_points)
                    
                    waveform_data = []
                    for i in range(0, total_samples - 1, step):
                        byte_index = i * bytes_per_sample
                        if byte_index + sample_width <= len(frames):
                            if sample_width == 2:
                                value = int.from_bytes(frames[byte_index:byte_index+2], byteorder='little', signed=True)
                            elif sample_width == 1:
                                value = (frames[byte_index] - 128) * 256
                            else:
                                value = 1000
                            waveform_data.append(abs(value))
                
                self.loading_progress.emit(100)
                self.waveform_loaded.emit(waveform_data)
                
        except Exception as e:
            self.loading_error.emit(str(e))

class WaveformWidget(QWidget):
    """Simple waveform display widget"""
    
    def __init__(self):
        super().__init__()
        self.waveform_data = []
        self.is_loading = False
        self.worker = None
        self.setMinimumHeight(70)
        self.setMaximumHeight(90)
        self.setMinimumWidth(200)  # Ensure minimum width for calculations
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(f"""
            background-color: {ThemeColors.PRIMARY_BG};
            border: 1px solid {ThemeColors.BORDER};
            border-radius: {ThemeSpacing.RADIUS_MEDIUM}px;
        """)
        
        # Loading indicator
        self.loading_indicator = CircularProgress(32)
        self.loading_indicator.setParent(self)
        self.loading_indicator.hide()
    
    def load_waveform(self, file_path):
        """Load and analyze waveform from audio file asynchronously"""
        # Stop existing worker if running
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        # Clear existing data and show loading
        self.waveform_data = []
        self.is_loading = True
        self._show_loading_indicator()
        self.update()
        
        # Ensure we have a valid widget width for calculations
        widget_width = max(self.width(), self.minimumWidth(), 200)
        print(f"DEBUG: Loading waveform for {os.path.basename(file_path)}")
        print(f"DEBUG: Widget size: {self.width()}x{self.height()}, using width: {widget_width}")
        
        # Start worker thread
        self.worker = WaveformWorker(file_path, widget_width)
        self.worker.waveform_loaded.connect(self._on_waveform_loaded)
        self.worker.loading_progress.connect(self._on_loading_progress)
        self.worker.loading_error.connect(self._on_loading_error)
        self.worker.start()
    
    def _show_loading_indicator(self):
        """Show loading indicator centered in widget"""
        if self.loading_indicator:
            # Center the loading indicator
            center_x = (self.width() - self.loading_indicator.width()) // 2
            center_y = (self.height() - self.loading_indicator.height()) // 2
            self.loading_indicator.move(center_x, center_y)
            self.loading_indicator.setIndeterminate(True)
            self.loading_indicator.show()
    
    def _hide_loading_indicator(self):
        """Hide loading indicator"""
        if self.loading_indicator:
            self.loading_indicator.setIndeterminate(False)
            self.loading_indicator.hide()
    
    def _on_waveform_loaded(self, waveform_data):
        """Handle completed waveform loading"""
        self.waveform_data = waveform_data
        self.is_loading = False
        self._hide_loading_indicator()
        print(f"DEBUG: Waveform loaded: {len(waveform_data) if waveform_data else 0} points")
        # Force immediate repaint
        self.update()
        self.repaint()  # Ensure immediate visual update
    
    def _on_loading_progress(self, progress):
        """Handle loading progress updates"""
        if self.loading_indicator and not self.loading_indicator.isHidden():
            self.loading_indicator.setProgress(progress)
    
    def _on_loading_error(self, error_message):
        """Handle loading errors"""
        self.is_loading = False
        self._hide_loading_indicator()
        
        # Show flat line on error
        self.waveform_data = [1000] * 30
        self.update()
        
        # Log error silently - waveform is not critical
        if hasattr(self.parent(), 'error_handler'):
            self.parent().error_handler.handle_error(
                Exception(error_message), 
                "loading waveform",
                show_dialog=False
            )
    
    def resizeEvent(self, event):
        """Handle widget resize to reposition loading indicator"""
        super().resizeEvent(event)
        if self.is_loading:
            self._show_loading_indicator()
    
    def paintEvent(self, event):
        """Paint the waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background with subtle gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(ThemeColors.PRIMARY_BG))
        gradient.setColorAt(1, QColor(ThemeColors.SECONDARY_BG))
        painter.fillRect(self.rect(), gradient)
        
        if len(self.waveform_data) == 0:
            # No waveform - draw placeholder or loading state
            painter.setPen(QPen(QColor(ThemeColors.TEXT_DISABLED), 1))
            painter.setFont(theme_manager.create_font(ThemeFonts.SIZE_SMALL))
            if self.is_loading:
                painter.drawText(self.rect(), Qt.AlignCenter, "Loading waveform...")
            else:
                painter.drawText(self.rect(), Qt.AlignCenter, "No waveform data")
            return
        
        # Draw waveform
        width = self.width()
        height = self.height()
        center_y = height // 2
        
        # Draw center line
        painter.setPen(QPen(QColor(ThemeColors.BORDER), 1, Qt.DotLine))
        painter.drawLine(0, center_y, width, center_y)
        
        # Draw waveform with gradient
        if len(self.waveform_data) > 1:
            x_step = width / len(self.waveform_data)
            max_amplitude = max(self.waveform_data) if self.waveform_data else 1
            
            if max_amplitude > 0:
                # Draw filled waveform
                for i, amplitude in enumerate(self.waveform_data):
                    x = int(i * x_step)
                    bar_width = max(1, int(x_step))
                    y_offset = int((amplitude / max_amplitude) * (center_y - 10))
                    
                    # Create gradient effect with theme colors
                    if y_offset > 0:
                        # Upper half
                        gradient_color = QColor(ThemeColors.ACCENT)
                        gradient_color.setAlpha(180)
                        painter.fillRect(x, center_y - y_offset, bar_width, y_offset, gradient_color)
                        
                        # Lower half (mirror)
                        gradient_color.setAlpha(90)
                        painter.fillRect(x, center_y, bar_width, y_offset, gradient_color)
                
                # Draw peak outline
                painter.setPen(QPen(QColor(ThemeColors.ACCENT_HOVER), 2))
                for i in range(1, len(self.waveform_data)):
                    x1 = int((i - 1) * x_step)
                    x2 = int(i * x_step)
                    y1 = center_y - int((self.waveform_data[i - 1] / max_amplitude) * (center_y - 10))
                    y2 = center_y - int((self.waveform_data[i] / max_amplitude) * (center_y - 10))
                    painter.drawLine(x1, y1, x2, y2)

class AudioPreviewWidget(QWidget):
    """Complete audio preview widget with controls and waveform"""
    
    def __init__(self):
        super().__init__()
        self.engine = AudioPreviewEngine()
        self.current_file = None
        self.error_handler = ErrorHandler(self)
        
        # Accessibility settings
        self.accessibility_enabled = accessibility_settings.colorblind_mode
        self.accessibility_indicator = accessibility_settings.get_indicator_factory()
        
        # Connect engine error handler to widget
        if hasattr(self.engine, 'error_handler'):
            self.engine.error_handler.parent_widget = self
        
        # Status check timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(100)  # Update every 100ms
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # File info
        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet(f"""
            color: {ThemeColors.TEXT_PRIMARY};
            font-size: {ThemeFonts.SIZE_BODY}px;
            padding: 4px;
            font-weight: {ThemeFonts.WEIGHT_MEDIUM};
        """)
        layout.addWidget(self.file_label)
        
        # Waveform display
        self.waveform = WaveformWidget()
        layout.addWidget(self.waveform)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        # Play button with animation
        play_symbol = get_status_symbol("play") if self.accessibility_enabled else "▶"
        self.play_btn = QPushButton(play_symbol)
        self.play_btn.setFixedSize(36, 36)
        self.play_btn.setToolTip("Play/Pause preview")
        self.play_btn.setCursor(Qt.PointingHandCursor)
        self.play_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeColors.ACCENT};
                color: {ThemeColors.TEXT_PRIMARY};
                border: none;
                border-radius: 18px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ThemeColors.ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {ThemeColors.ACCENT_PRESSED};
            }}
        """)
        self.play_btn.clicked.connect(self._toggle_play)
        
        # Add animation effect to play button
        self._play_btn_animation = QPropertyAnimation(self.play_btn, b"geometry")
        self._play_btn_animation.setDuration(100)
        self._play_btn_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        controls_layout.addWidget(self.play_btn)
        
        # Stop button with animation
        stop_symbol = get_status_symbol("stop") if self.accessibility_enabled else "⏹"
        self.stop_btn = QPushButton(stop_symbol)
        self.stop_btn.setFixedSize(36, 36)
        self.stop_btn.setToolTip("Stop preview")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeColors.PANEL_BG};
                color: {ThemeColors.TEXT_SECONDARY};
                border: 1px solid {ThemeColors.BORDER};
                border-radius: 18px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {ThemeColors.HOVER_BG};
                color: {ThemeColors.TEXT_PRIMARY};
                border-color: {ThemeColors.ACCENT};
            }}
            QPushButton:pressed {{
                background-color: {ThemeColors.PRESSED_BG};
            }}
        """)
        self.stop_btn.clicked.connect(self._stop)
        controls_layout.addWidget(self.stop_btn)
        
        # Engine status with themed styling
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"""
            color: {ThemeColors.TEXT_SECONDARY};
            font-size: {ThemeFonts.SIZE_TINY}px;
            padding: 0 8px;
        """)
        controls_layout.addWidget(self.status_label)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        self.setLayout(layout)
        
        # Initial state
        self._update_engine_status()
        
    def _animate_button_press(self, button):
        """Animate button press effect"""
        # Scale down and back up
        original_size = button.size()
        original_pos = button.pos()
        
        # Calculate scaled geometry (95% size)
        scaled_width = int(original_size.width() * 0.95)
        scaled_height = int(original_size.height() * 0.95)
        offset_x = (original_size.width() - scaled_width) // 2
        offset_y = (original_size.height() - scaled_height) // 2
        
        self._play_btn_animation.setStartValue(button.geometry())
        self._play_btn_animation.setEndValue(
            button.geometry().adjusted(offset_x, offset_y, -offset_x, -offset_y)
        )
        self._play_btn_animation.setDirection(QPropertyAnimation.Forward)
        self._play_btn_animation.finished.connect(
            lambda: self._play_btn_animation.setDirection(QPropertyAnimation.Backward)
        )
        self._play_btn_animation.start()
        
    def load_file(self, file_path):
        """Load a file for preview"""
        if not file_path or not os.path.exists(file_path):
            self._clear()
            return
        
        self.current_file = file_path
        filename = os.path.basename(file_path)
        
        # Use accessibility symbol if enabled
        if self.accessibility_enabled:
            file_symbol = get_status_symbol("file")
        else:
            file_symbol = "📁"
        
        self.file_label.setText(f"{file_symbol} {filename}")
        
        # Load waveform
        self.waveform.load_waveform(file_path)
        
        # Load in engine
        if self.engine.load_file(file_path):
            ready_symbol = get_status_symbol("play") if self.accessibility_enabled else ""
            self.status_label.setText(f"{ready_symbol} Ready to play")
            
            # Use accessible status color if enabled
            status_color = theme_manager.get_status_color("success") if self.accessibility_enabled else ThemeColors.TEXT_SECONDARY
            self.status_label.setStyleSheet(f"""
                color: {status_color};
                font-size: {ThemeFonts.SIZE_TINY}px;
                padding: 0 8px;
            """)
        else:
            if not PYGAME_AVAILABLE:
                warning_symbol = get_status_symbol("warning") if self.accessibility_enabled else ""
                self.status_label.setText(f"{warning_symbol} Install pygame for audio")
                
                status_color = theme_manager.get_status_color("warning") if self.accessibility_enabled else ThemeColors.WARNING
                self.status_label.setStyleSheet(f"""
                    color: {status_color};
                    font-size: {ThemeFonts.SIZE_TINY}px;
                    padding: 0 8px;
                """)
            else:
                error_symbol = get_status_symbol("error") if self.accessibility_enabled else ""
                self.status_label.setText(f"{error_symbol} Unsupported format")
                
                status_color = theme_manager.get_status_color("error") if self.accessibility_enabled else ThemeColors.TEXT_DISABLED
                self.status_label.setStyleSheet(f"""
                    color: {status_color};
                    font-size: {ThemeFonts.SIZE_TINY}px;
                    padding: 0 8px;
                """)
    
    def _clear(self):
        """Clear the preview"""
        self.current_file = None
        self.file_label.setText("No file loaded")
        self.waveform.waveform_data = []
        self.waveform.update()
        self.status_label.setText("No file")
        self.play_btn.setText("▶")
    
    def _toggle_play(self):
        """Toggle play/pause with animation"""
        # Animate button press
        self._animate_button_press(self.play_btn)
        if self.engine.get_is_playing():
            self.engine.pause()
            play_symbol = get_status_symbol("play") if self.accessibility_enabled else "▶"
            self.play_btn.setText(play_symbol)
        else:
            if self.engine.play():
                pause_symbol = get_status_symbol("pause") if self.accessibility_enabled else "⏸"
                self.play_btn.setText(pause_symbol)
            else:
                error_symbol = get_status_symbol("error") if self.accessibility_enabled else ""
                self.status_label.setText(f"{error_symbol} Playback failed")
    
    def _stop(self):
        """Stop playback"""
        self.engine.stop()
        play_symbol = get_status_symbol("play") if self.accessibility_enabled else "▶"
        self.play_btn.setText(play_symbol)
    
    def _update_status(self):
        """Update playback status"""
        pause_symbol = get_status_symbol("pause") if self.accessibility_enabled else "⏸"
        if not self.engine.get_is_playing() and self.play_btn.text() == pause_symbol:
            # Playback ended
            play_symbol = get_status_symbol("play") if self.accessibility_enabled else "▶"
            self.play_btn.setText(play_symbol)
    
    def _update_engine_status(self):
        """Update engine availability status"""
        if PYGAME_AVAILABLE:
            self.setToolTip("Audio preview available (pygame)")
            self.play_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
        else:
            self.setToolTip("Audio preview unavailable - install pygame for audio preview")
            self.status_label.setText("Install pygame for audio")
            self.status_label.setStyleSheet(f"""
                color: {ThemeColors.WARNING};
                font-size: {ThemeFonts.SIZE_TINY}px;
                padding: 0 8px;
            """)
            self.play_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)