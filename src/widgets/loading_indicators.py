"""
Loading Indicators and Progress Components
Provides visual feedback for async operations
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, pyqtSignal, QSize
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QConicalGradient
from utils.theme_manager import ThemeColors, ThemeFonts, ThemeSpacing, theme_manager
import math


class CircularProgress(QWidget):
    """Circular progress indicator with smooth animation"""
    
    def __init__(self, size: int = 64, parent=None):
        super().__init__(parent)
        self.size = size
        self._progress = 0
        self._max_progress = 100
        self._thickness = 4
        self._animation_timer = None
        
        self.setFixedSize(size, size)
        
    def setProgress(self, value: int):
        """Set progress value (0-100)"""
        self._progress = max(0, min(100, value))
        self.update()
        
    def setIndeterminate(self, indeterminate: bool = True):
        """Set indeterminate mode (spinning animation)"""
        if indeterminate:
            if not self._animation_timer:
                self._animation_timer = QTimer()
                self._animation_timer.timeout.connect(self._animate_spin)
                self._animation_timer.start(50)
        else:
            if self._animation_timer:
                self._animation_timer.stop()
                self._animation_timer = None
                
    def _animate_spin(self):
        """Animate spinning for indeterminate mode"""
        self._progress = (self._progress + 5) % 360
        self.update()
        
    def paintEvent(self, event):
        """Paint the circular progress"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate dimensions
        rect = QRect(self._thickness, self._thickness, 
                    self.size - 2 * self._thickness, 
                    self.size - 2 * self._thickness)
        
        # Draw background circle
        painter.setPen(QPen(QColor(ThemeColors.BORDER), self._thickness))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(rect)
        
        # Draw progress arc
        if self._animation_timer:  # Indeterminate mode
            # Create gradient for spinning effect
            gradient = QConicalGradient(self.size / 2, self.size / 2, self._progress)
            gradient.setColorAt(0, QColor(ThemeColors.ACCENT))
            gradient.setColorAt(0.5, QColor(ThemeColors.ACCENT_HOVER))
            gradient.setColorAt(1, QColor(ThemeColors.ACCENT).darker(150))
            
            pen = QPen(QBrush(gradient), self._thickness)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rect, 0, 360 * 16)
        else:  # Determinate mode
            pen = QPen(QColor(ThemeColors.ACCENT), self._thickness)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            
            start_angle = 90 * 16  # Start from top
            span_angle = -int(self._progress * 3.6 * 16)  # Convert to 1/16 degrees
            painter.drawArc(rect, start_angle, span_angle)
            
            # Draw percentage text
            painter.setPen(QColor(ThemeColors.TEXT_PRIMARY))
            painter.setFont(theme_manager.create_font(ThemeFonts.SIZE_SMALL))
            painter.drawText(rect, Qt.AlignCenter, f"{self._progress}%")


class LoadingOverlay(QWidget):
    """Semi-transparent overlay with loading indicator"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # Setup UI
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Loading indicator
        self.spinner = CircularProgress(64)
        self.spinner.setIndeterminate(True)
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        
        # Loading text
        self.label = QLabel("Loading...")
        self.label.setStyleSheet(f"""
            color: {ThemeColors.TEXT_PRIMARY};
            font-size: {ThemeFonts.SIZE_BODY}px;
            font-weight: {ThemeFonts.WEIGHT_MEDIUM};
            padding: 8px;
        """)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        
        # Style the overlay
        self.setStyleSheet(f"""
            LoadingOverlay {{
                background-color: rgba(0, 0, 0, 180);
            }}
        """)
        
        self.hide()
        
    def showWithText(self, text: str = "Loading..."):
        """Show overlay with custom text"""
        self.label.setText(text)
        if self.parent():
            self.resize(self.parent().size())
        self.show()
        self.raise_()
        
    def resizeEvent(self, event):
        """Ensure overlay covers parent widget"""
        if self.parent():
            self.resize(self.parent().size())


class ProgressButton(QWidget):
    """Button with integrated progress indicator"""
    clicked = pyqtSignal()
    
    def __init__(self, text: str = "Submit", parent=None):
        super().__init__(parent)
        self.text = text
        self._progress = 0
        self._is_loading = False
        
        # Setup UI
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: transparent;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {ThemeColors.ACCENT};
                border-radius: 2px;
            }}
        """)
        self.progress_bar.hide()
        
        # Button
        from PyQt5.QtWidgets import QPushButton
        self.button = QPushButton(self.text)
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeColors.ACCENT};
                color: {ThemeColors.TEXT_PRIMARY};
                border: none;
                border-radius: {ThemeSpacing.RADIUS_MEDIUM}px;
                padding: 8px 16px;
                font-weight: {ThemeFonts.WEIGHT_MEDIUM};
                min-height: {ThemeSpacing.HEIGHT_BUTTON}px;
            }}
            QPushButton:hover {{
                background-color: {ThemeColors.ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {ThemeColors.ACCENT_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {ThemeColors.BORDER};
                color: {ThemeColors.TEXT_DISABLED};
            }}
        """)
        self.button.clicked.connect(self.clicked.emit)
        
        # Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.button)
        main_layout.addWidget(self.progress_bar)
        
        self.setLayout(main_layout)
        
    def setLoading(self, loading: bool):
        """Set loading state"""
        self._is_loading = loading
        self.button.setEnabled(not loading)
        
        if loading:
            self.button.setText("Processing...")
            self.progress_bar.show()
            self.progress_bar.setRange(0, 0)  # Indeterminate
        else:
            self.button.setText(self.text)
            self.progress_bar.hide()
            self.progress_bar.setRange(0, 100)
            
    def setProgress(self, value: int):
        """Set progress value (0-100)"""
        if not self._is_loading:
            self.setLoading(True)
            
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(value)
        
        if value >= 100:
            QTimer.singleShot(500, lambda: self.setLoading(False))


class SkeletonLoader(QWidget):
    """Skeleton loading placeholder for content"""
    
    def __init__(self, width: int = 200, height: int = 20, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        
        # Animation
        self._animation = QPropertyAnimation(self, b"pos")
        self._animation.setDuration(1500)
        self._animation.setLoopCount(-1)  # Infinite
        
        # Start animation
        self._start_shimmer()
        
    def _start_shimmer(self):
        """Start shimmer animation"""
        if self.parent():
            start_pos = self.pos()
            end_pos = start_pos + QSize(self.width(), 0)
            self._animation.setStartValue(start_pos)
            self._animation.setEndValue(end_pos)
            self._animation.start()
            
    def paintEvent(self, event):
        """Paint skeleton loader"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Base color
        base_color = QColor(ThemeColors.PANEL_BG)
        painter.fillRect(self.rect(), base_color)
        
        # Shimmer gradient
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, base_color)
        gradient.setColorAt(0.5, QColor(ThemeColors.HOVER_BG))
        gradient.setColorAt(1, base_color)
        
        painter.fillRect(self.rect(), QBrush(gradient))