"""
Custom UI Components for DecentSampler Frontend
Reusable, themed components for consistent UI
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFrame, QSizePolicy, QGraphicsDropShadowEffect, QSlider,
    QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QConicalGradient
from utils.theme_manager import ThemeColors, ThemeFonts, ThemeSpacing, theme_manager
import math


class LabeledKnob(QWidget):
    """A custom knob widget with label and value display"""
    valueChanged = pyqtSignal(float)
    
    def __init__(self, label_text: str = "", 
                 min_value: float = 0.0, 
                 max_value: float = 1.0, 
                 default_value: float = 0.5,
                 decimals: int = 2,
                 parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.min_value = min_value
        self.max_value = max_value
        self.decimals = decimals
        self._value = default_value
        self._angle = self._value_to_angle(default_value)
        self._dragging = False
        self._last_y = 0
        
        self.setMinimumSize(ThemeSpacing.KNOB_SIZE + 20, ThemeSpacing.KNOB_SIZE + 40)
        self.setMaximumSize(ThemeSpacing.KNOB_SIZE + 40, ThemeSpacing.KNOB_SIZE + 60)
        self.setCursor(Qt.PointingHandCursor)
        
    def _value_to_angle(self, value):
        """Convert value to knob angle (degrees)"""
        normalized = (value - self.min_value) / (self.max_value - self.min_value)
        return -135 + (normalized * 270)  # -135 to +135 degrees
        
    def _angle_to_value(self, angle):
        """Convert knob angle to value"""
        normalized = (angle + 135) / 270
        return self.min_value + (normalized * (self.max_value - self.min_value))
        
    def value(self):
        return self._value
        
    def setValue(self, value):
        value = max(self.min_value, min(self.max_value, value))
        if value != self._value:
            self._value = value
            self._angle = self._value_to_angle(value)
            self.update()
            self.valueChanged.emit(value)
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        knob_size = min(width - 20, height - 40, ThemeSpacing.KNOB_SIZE)
        center_x = width // 2
        center_y = height // 2 - 10
        
        # Draw knob background
        painter.setPen(QPen(QColor(ThemeColors.BORDER), 2))
        painter.setBrush(QBrush(QColor(ThemeColors.SECONDARY_BG)))
        painter.drawEllipse(center_x - knob_size//2, center_y - knob_size//2, 
                          knob_size, knob_size)
        
        # Draw knob indicator
        angle_rad = math.radians(self._angle - 90)
        indicator_length = knob_size * 0.35
        end_x = center_x + indicator_length * math.cos(angle_rad)
        end_y = center_y + indicator_length * math.sin(angle_rad)
        
        painter.setPen(QPen(QColor(ThemeColors.ACCENT), 3))
        painter.drawLine(center_x, center_y, int(end_x), int(end_y))
        
        # Draw value arc
        painter.setPen(QPen(QColor(ThemeColors.ACCENT), 3))
        painter.setBrush(Qt.NoBrush)
        start_angle = 225 * 16  # Qt uses 1/16th degree units
        span_angle = int(((self._angle + 135) / 270) * -270 * 16)
        painter.drawArc(center_x - knob_size//2 + 5, center_y - knob_size//2 + 5,
                       knob_size - 10, knob_size - 10, start_angle, span_angle)
        
        # Draw label
        if self.label_text:
            painter.setPen(QColor(ThemeColors.TEXT_PRIMARY))
            painter.setFont(theme_manager.create_font(ThemeFonts.SIZE_SMALL))
            label_rect = painter.boundingRect(0, 0, width, 20, Qt.AlignCenter, self.label_text)
            painter.drawText(label_rect.translated(0, height - 35), Qt.AlignCenter, self.label_text)
        
        # Draw value
        value_text = f"{self._value:.{self.decimals}f}"
        painter.setPen(QColor(ThemeColors.TEXT_SECONDARY))
        painter.setFont(theme_manager.create_font(ThemeFonts.SIZE_TINY))
        value_rect = painter.boundingRect(0, 0, width, 20, Qt.AlignCenter, value_text)
        painter.drawText(value_rect.translated(0, height - 20), Qt.AlignCenter, value_text)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._last_y = event.y()
            
    def mouseMoveEvent(self, event):
        if self._dragging:
            dy = self._last_y - event.y()
            self._last_y = event.y()
            
            # Adjust sensitivity
            new_angle = self._angle + dy * 1.5
            new_angle = max(-135, min(135, new_angle))
            
            new_value = self._angle_to_value(new_angle)
            self.setValue(new_value)
            
    def mouseReleaseEvent(self, event):
        self._dragging = False
        
    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        step = (self.max_value - self.min_value) / 100
        self.setValue(self._value + delta * step)


class CollapsiblePanel(QFrame):
    """A panel that can be collapsed/expanded with animation"""
    toggled = pyqtSignal(bool)
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self._is_collapsed = False
        self._content_widget = None
        self._animation = None
        
        self.setFrameStyle(QFrame.StyledPanel)
        self.setObjectName("CollapsiblePanel")
        
        # Main layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        
        # Header
        self._header = QPushButton(self.title)
        self._header.setObjectName("CollapsiblePanelHeader")
        self._header.setCheckable(True)
        self._header.setChecked(True)
        self._header.clicked.connect(self.toggle)
        self._header.setStyleSheet(f"""
            QPushButton#CollapsiblePanelHeader {{
                background-color: {ThemeColors.PANEL_BG};
                border: 1px solid {ThemeColors.BORDER};
                border-radius: {ThemeSpacing.RADIUS_MEDIUM}px;
                padding: {ThemeSpacing.SPACING_SMALL}px {ThemeSpacing.SPACING_MEDIUM}px;
                text-align: left;
                font-weight: {ThemeFonts.WEIGHT_SEMIBOLD};
                font-size: {ThemeFonts.SIZE_H3}px;
            }}
            QPushButton#CollapsiblePanelHeader:hover {{
                background-color: {ThemeColors.HOVER_BG};
                border-color: {ThemeColors.ACCENT};
            }}
            QPushButton#CollapsiblePanelHeader:checked {{
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
            }}
        """)
        
        self._layout.addWidget(self._header)
        
        # Content container
        self._content_container = QWidget()
        self._content_container.setObjectName("CollapsiblePanelContent")
        self._content_container.setStyleSheet(f"""
            QWidget#CollapsiblePanelContent {{
                background-color: {ThemeColors.SECONDARY_BG};
                border: 1px solid {ThemeColors.BORDER};
                border-top: none;
                border-bottom-left-radius: {ThemeSpacing.RADIUS_MEDIUM}px;
                border-bottom-right-radius: {ThemeSpacing.RADIUS_MEDIUM}px;
            }}
        """)
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(
            ThemeSpacing.SPACING_MEDIUM,
            ThemeSpacing.SPACING_MEDIUM,
            ThemeSpacing.SPACING_MEDIUM,
            ThemeSpacing.SPACING_MEDIUM
        )
        
        self._layout.addWidget(self._content_container)
        
        # Animation
        self._animation = QPropertyAnimation(self._content_container, b"maximumHeight")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def setContentWidget(self, widget: QWidget):
        """Set the content widget for the collapsible panel"""
        if self._content_widget:
            self._content_layout.removeWidget(self._content_widget)
            self._content_widget.deleteLater()
            
        self._content_widget = widget
        self._content_layout.addWidget(widget)
        
    def toggle(self):
        """Toggle collapsed/expanded state"""
        self._is_collapsed = not self._is_collapsed
        
        if self._is_collapsed:
            self._animation.setStartValue(self._content_container.height())
            self._animation.setEndValue(0)
        else:
            self._animation.setStartValue(0)
            self._animation.setEndValue(self._content_container.sizeHint().height())
            
        self._animation.start()
        self.toggled.emit(not self._is_collapsed)
        
        # Update header appearance
        self._header.setText(f"{'▶' if self._is_collapsed else '▼'} {self.title}")
        
    def isCollapsed(self):
        return self._is_collapsed
        
    def setCollapsed(self, collapsed: bool):
        if collapsed != self._is_collapsed:
            self.toggle()


class ParameterCard(QFrame):
    """A styled card for parameter controls with consistent theming"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        
        self.setObjectName("ParameterCard")
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame#ParameterCard {{
                background-color: {ThemeColors.PANEL_BG};
                border: 1px solid {ThemeColors.BORDER};
                border-radius: {ThemeSpacing.RADIUS_LARGE}px;
                padding: {ThemeSpacing.SPACING_MEDIUM}px;
            }}
            QFrame#ParameterCard:hover {{
                border-color: {ThemeColors.ACCENT};
                background-color: {ThemeColors.HOVER_BG};
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
        # Layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(
            ThemeSpacing.SPACING_MEDIUM,
            ThemeSpacing.SPACING_MEDIUM,
            ThemeSpacing.SPACING_MEDIUM,
            ThemeSpacing.SPACING_MEDIUM
        )
        
        # Title label
        if self.title:
            self._title_label = QLabel(self.title)
            self._title_label.setProperty("heading", "h3")
            self._layout.addWidget(self._title_label)
            self._layout.addSpacing(ThemeSpacing.SPACING_SMALL)
            
    def addContent(self, widget: QWidget):
        """Add content widget to the card"""
        self._layout.addWidget(widget)
        
    def setTitle(self, title: str):
        """Update the card title"""
        self.title = title
        if hasattr(self, '_title_label'):
            self._title_label.setText(title)


class LabeledSlider(QWidget):
    """Horizontal or vertical slider with label and value display"""
    valueChanged = pyqtSignal(int)
    
    def __init__(self, label: str = "", 
                 min_value: int = 0, 
                 max_value: int = 100,
                 default_value: int = 50,
                 orientation: Qt.Orientation = Qt.Horizontal,
                 parent=None):
        super().__init__(parent)
        
        # Layout based on orientation
        if orientation == Qt.Horizontal:
            layout = QHBoxLayout(self)
        else:
            layout = QVBoxLayout(self)
            
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(ThemeSpacing.SPACING_SMALL)
        
        # Label
        if label:
            self.label = QLabel(label)
            self.label.setProperty("secondary", "true")
            layout.addWidget(self.label)
            
        # Slider
        self.slider = QSlider(orientation)
        self.slider.setRange(min_value, max_value)
        self.slider.setValue(default_value)
        layout.addWidget(self.slider)
        
        # Value display
        self.value_label = QLabel(str(default_value))
        self.value_label.setProperty("secondary", "true")
        self.value_label.setMinimumWidth(40)
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Connect signals
        self.slider.valueChanged.connect(self._on_value_changed)
        
    def _on_value_changed(self, value):
        self.value_label.setText(str(value))
        self.valueChanged.emit(value)
        
    def value(self):
        return self.slider.value()
        
    def setValue(self, value):
        self.slider.setValue(value)


class IconButton(QPushButton):
    """A button optimized for icon display with hover effects"""
    
    def __init__(self, icon_text: str = "", tooltip: str = "", parent=None):
        super().__init__(icon_text, parent)
        
        if tooltip:
            self.setToolTip(tooltip)
            
        self.setObjectName("IconButton")
        self.setCursor(Qt.PointingHandCursor)
        
        # Fixed size for icon buttons
        self.setFixedSize(ThemeSpacing.HEIGHT_BUTTON, ThemeSpacing.HEIGHT_BUTTON)
        
        self.setStyleSheet(f"""
            QPushButton#IconButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: {ThemeSpacing.RADIUS_SMALL}px;
                color: {ThemeColors.TEXT_SECONDARY};
                font-size: {ThemeFonts.SIZE_BODY}px;
            }}
            QPushButton#IconButton:hover {{
                background-color: {ThemeColors.HOVER_BG};
                border-color: {ThemeColors.BORDER};
                color: {ThemeColors.TEXT_PRIMARY};
            }}
            QPushButton#IconButton:pressed {{
                background-color: {ThemeColors.PRESSED_BG};
                border-color: {ThemeColors.ACCENT};
                color: {ThemeColors.ACCENT};
            }}
        """)


class ValueSpinBox(QWidget):
    """Enhanced spin box with better styling and optional label"""
    valueChanged = pyqtSignal(float)
    
    def __init__(self, label: str = "",
                 min_value: float = 0.0,
                 max_value: float = 100.0,
                 default_value: float = 0.0,
                 decimals: int = 2,
                 step: float = 1.0,
                 suffix: str = "",
                 parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(ThemeSpacing.SPACING_SMALL)
        
        # Label
        if label:
            self.label = QLabel(label)
            self.label.setProperty("secondary", "true")
            layout.addWidget(self.label)
            
        # Spin box
        if decimals > 0:
            self.spin_box = QDoubleSpinBox()
            self.spin_box.setDecimals(decimals)
        else:
            self.spin_box = QSpinBox()
            
        self.spin_box.setRange(min_value, max_value)
        self.spin_box.setValue(default_value)
        self.spin_box.setSingleStep(step)
        
        if suffix:
            self.spin_box.setSuffix(suffix)
            
        layout.addWidget(self.spin_box)
        
        # Connect signal
        self.spin_box.valueChanged.connect(self.valueChanged.emit)
        
    def value(self):
        return self.spin_box.value()
        
    def setValue(self, value):
        self.spin_box.setValue(value)