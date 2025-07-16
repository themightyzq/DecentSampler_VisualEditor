"""
Audio Preview Widget for Sample Previewing
Provides quick audio preview functionality with waveform display
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, 
    QProgressBar, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
import os
import wave
import threading
import time

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
        
        if PYGAME_AVAILABLE:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
        
    def load_file(self, file_path):
        """Load an audio file for preview"""
        try:
            if PYGAME_AVAILABLE and file_path.lower().endswith('.wav'):
                self.current_file = file_path
                return True
            return False
        except Exception as e:
            print(f"Error loading audio file: {e}")
            return False
    
    def play(self):
        """Start playback"""
        if PYGAME_AVAILABLE and self.current_file:
            try:
                pygame.mixer.music.load(self.current_file)
                pygame.mixer.music.play()
                self.is_playing = True
                return True
            except Exception as e:
                print(f"Error playing audio: {e}")
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

class WaveformWidget(QWidget):
    """Simple waveform display widget"""
    
    def __init__(self):
        super().__init__()
        self.waveform_data = []
        self.setMinimumHeight(60)
        self.setMaximumHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #444;")
    
    def load_waveform(self, file_path):
        """Load and analyze waveform from audio file"""
        try:
            if not file_path.lower().endswith('.wav'):
                self.waveform_data = []
                self.update()
                return
            
            with wave.open(file_path, 'rb') as wav_file:
                frames = wav_file.readframes(-1)
                if NUMPY_AVAILABLE:
                    # Convert to numpy array for analysis
                    samples = np.frombuffer(frames, dtype=np.int16)
                    
                    # Downsample for display (take every Nth sample)
                    target_points = 200
                    step = max(1, len(samples) // target_points)
                    self.waveform_data = samples[::step]
                else:
                    # Basic fallback - just create a simple representation
                    self.waveform_data = list(range(-1000, 1000, 100)) + list(range(1000, -1000, -100))
                
                self.update()
                
        except Exception as e:
            print(f"Error loading waveform: {e}")
            self.waveform_data = []
            self.update()
    
    def paintEvent(self, event):
        """Paint the waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if len(self.waveform_data) == 0:
            # No waveform - draw placeholder
            painter.setPen(QPen(QColor("#666"), 1))
            painter.drawText(self.rect(), Qt.AlignCenter, "No waveform data")
            return
        
        # Draw waveform
        width = self.width()
        height = self.height()
        center_y = height // 2
        
        painter.setPen(QPen(QColor("#4a7c59"), 1))
        
        if len(self.waveform_data) > 1:
            x_step = width / len(self.waveform_data)
            max_amplitude = max(abs(min(self.waveform_data)), abs(max(self.waveform_data)))
            
            if max_amplitude > 0:
                for i, amplitude in enumerate(self.waveform_data):
                    x = int(i * x_step)
                    y_offset = int((amplitude / max_amplitude) * (center_y - 5))
                    painter.drawLine(x, center_y, x, center_y - y_offset)

class AudioPreviewWidget(QWidget):
    """Complete audio preview widget with controls and waveform"""
    
    def __init__(self):
        super().__init__()
        self.engine = AudioPreviewEngine()
        self.current_file = None
        
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
        self.file_label.setStyleSheet("color: #f0f0f0; font-size: 12px;")
        layout.addWidget(self.file_label)
        
        # Waveform display
        self.waveform = WaveformWidget()
        layout.addWidget(self.waveform)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(30, 24)
        self.play_btn.setToolTip("Play/Pause preview")
        self.play_btn.clicked.connect(self._toggle_play)
        controls_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setFixedSize(30, 24)
        self.stop_btn.setToolTip("Stop preview")
        self.stop_btn.clicked.connect(self._stop)
        controls_layout.addWidget(self.stop_btn)
        
        # Engine status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #999; font-size: 10px;")
        controls_layout.addWidget(self.status_label)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        self.setLayout(layout)
        
        # Initial state
        self._update_engine_status()
        
    def load_file(self, file_path):
        """Load a file for preview"""
        if not file_path or not os.path.exists(file_path):
            self._clear()
            return
        
        self.current_file = file_path
        filename = os.path.basename(file_path)
        self.file_label.setText(f"📁 {filename}")
        
        # Load waveform
        self.waveform.load_waveform(file_path)
        
        # Load in engine
        if self.engine.load_file(file_path):
            self.status_label.setText("Ready to play")
        else:
            self.status_label.setText("Unsupported format")
    
    def _clear(self):
        """Clear the preview"""
        self.current_file = None
        self.file_label.setText("No file loaded")
        self.waveform.waveform_data = []
        self.waveform.update()
        self.status_label.setText("No file")
        self.play_btn.setText("▶")
    
    def _toggle_play(self):
        """Toggle play/pause"""
        if self.engine.get_is_playing():
            self.engine.pause()
            self.play_btn.setText("▶")
        else:
            if self.engine.play():
                self.play_btn.setText("⏸")
            else:
                self.status_label.setText("Playback failed")
    
    def _stop(self):
        """Stop playback"""
        self.engine.stop()
        self.play_btn.setText("▶")
    
    def _update_status(self):
        """Update playback status"""
        if not self.engine.get_is_playing() and self.play_btn.text() == "⏸":
            # Playback ended
            self.play_btn.setText("▶")
    
    def _update_engine_status(self):
        """Update engine availability status"""
        if PYGAME_AVAILABLE:
            self.setToolTip("Audio preview available (pygame)")
        else:
            self.setToolTip("Audio preview unavailable - install pygame for audio preview")
            self.status_label.setText("pygame not available")