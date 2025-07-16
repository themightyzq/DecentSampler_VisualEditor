from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QFormLayout, QGroupBox, QColorDialog, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPointF
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont, QLinearGradient
import math

class XYPad(QWidget):
    """2D XY control pad widget"""
    valueChanged = pyqtSignal(float, float)  # x_value, y_value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Value ranges
        self.x_min = 0.0
        self.x_max = 1.0
        self.y_min = 0.0
        self.y_max = 1.0
        
        # Current values
        self.x_value = 0.5
        self.y_value = 0.5
        
        # Visual properties
        self.pad_color = QColor("#333333")
        self.border_color = QColor("#666666")
        self.handle_color = QColor("#FFFFFF")
        self.handle_pressed_color = QColor("#00AAFF")
        self.grid_color = QColor("#555555")
        
        # Interaction state
        self.dragging = False
        self.handle_radius = 8
        
        # Labels
        self.x_label = "X"
        self.y_label = "Y"
        
        self.setMinimumSize(150, 150)
        self.setMouseTracking(True)
        
    def set_ranges(self, x_min, x_max, y_min, y_max):
        """Set the value ranges for X and Y axes"""
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.update()
        
    def set_values(self, x_value, y_value):
        """Set the current X and Y values"""
        self.x_value = max(self.x_min, min(self.x_max, x_value))
        self.y_value = max(self.y_min, min(self.y_max, y_value))
        self.update()
        
    def get_values(self):
        """Get the current X and Y values"""
        return self.x_value, self.y_value
        
    def set_labels(self, x_label, y_label):
        """Set the axis labels"""
        self.x_label = x_label
        self.y_label = y_label
        self.update()
        
    def value_to_position(self, x_value, y_value):
        """Convert values to pixel position"""
        pad_rect = self.get_pad_rect()
        
        # Normalize values to 0-1 range
        x_norm = (x_value - self.x_min) / (self.x_max - self.x_min)
        y_norm = (y_value - self.y_min) / (self.y_max - self.y_min)
        
        # Convert to pixel coordinates (Y is inverted)
        x_pos = pad_rect.left() + x_norm * pad_rect.width()
        y_pos = pad_rect.bottom() - y_norm * pad_rect.height()
        
        return QPointF(x_pos, y_pos)
        
    def position_to_value(self, pos):
        """Convert pixel position to values"""
        pad_rect = self.get_pad_rect()
        
        # Clamp position to pad area
        x_pos = max(pad_rect.left(), min(pad_rect.right(), pos.x()))
        y_pos = max(pad_rect.top(), min(pad_rect.bottom(), pos.y()))
        
        # Normalize to 0-1 range
        x_norm = (x_pos - pad_rect.left()) / pad_rect.width()
        y_norm = (pad_rect.bottom() - y_pos) / pad_rect.height()  # Y is inverted
        
        # Convert to value ranges
        x_value = self.x_min + x_norm * (self.x_max - self.x_min)
        y_value = self.y_min + y_norm * (self.y_max - self.y_min)
        
        return x_value, y_value
        
    def get_pad_rect(self):
        """Get the rectangle for the pad area (excluding labels)"""
        margin = 20
        return QRect(
            margin, margin,
            self.width() - 2 * margin,
            self.height() - 2 * margin
        )
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pad_rect = self.get_pad_rect()
        
        # Draw gradient background
        gradient = QLinearGradient(pad_rect.topLeft(), pad_rect.bottomRight())
        gradient.setColorAt(0, self.pad_color.lighter(120))
        gradient.setColorAt(1, self.pad_color.darker(120))
        painter.fillRect(pad_rect, QBrush(gradient))
        
        # Draw border
        painter.setPen(QPen(self.border_color, 2))
        painter.drawRect(pad_rect)
        
        # Draw grid lines
        painter.setPen(QPen(self.grid_color, 1))
        
        # Vertical grid lines
        for i in range(1, 4):
            x = pad_rect.left() + (pad_rect.width() * i / 4)
            painter.drawLine(x, pad_rect.top(), x, pad_rect.bottom())
            
        # Horizontal grid lines
        for i in range(1, 4):
            y = pad_rect.top() + (pad_rect.height() * i / 4)
            painter.drawLine(pad_rect.left(), y, pad_rect.right(), y)
            
        # Draw axis labels
        painter.setPen(QPen(QColor("#CCCCCC")))
        painter.setFont(QFont("Arial", 10))
        
        # X label (bottom center)
        x_label_rect = QRect(pad_rect.left(), pad_rect.bottom() + 5, pad_rect.width(), 15)
        painter.drawText(x_label_rect, Qt.AlignCenter, self.x_label)
        
        # Y label (left center, rotated)
        painter.save()
        painter.translate(5, pad_rect.center().y())
        painter.rotate(-90)
        painter.drawText(-50, 0, 100, 15, Qt.AlignCenter, self.y_label)
        painter.restore()
        
        # Draw value indicators
        painter.setPen(QPen(QColor("#AAAAAA")))
        painter.setFont(QFont("Arial", 8))
        
        # X value range
        x_min_text = f"{self.x_min:.2f}"
        x_max_text = f"{self.x_max:.2f}"
        painter.drawText(pad_rect.left(), pad_rect.bottom() + 20, x_min_text)
        painter.drawText(pad_rect.right() - 30, pad_rect.bottom() + 20, x_max_text)
        
        # Y value range
        y_min_text = f"{self.y_min:.2f}"
        y_max_text = f"{self.y_max:.2f}"
        painter.drawText(pad_rect.left() - 35, pad_rect.bottom(), y_min_text)
        painter.drawText(pad_rect.left() - 35, pad_rect.top() + 5, y_max_text)
        
        # Draw handle
        handle_pos = self.value_to_position(self.x_value, self.y_value)
        handle_color = self.handle_pressed_color if self.dragging else self.handle_color
        
        # Handle shadow
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.setBrush(QBrush(QColor("#000000")))
        painter.drawEllipse(handle_pos.x() - self.handle_radius + 1, 
                          handle_pos.y() - self.handle_radius + 1,
                          self.handle_radius * 2, self.handle_radius * 2)
        
        # Handle
        painter.setPen(QPen(QColor("#333333"), 2))
        painter.setBrush(QBrush(handle_color))
        painter.drawEllipse(handle_pos.x() - self.handle_radius, 
                          handle_pos.y() - self.handle_radius,
                          self.handle_radius * 2, self.handle_radius * 2)
        
        # Draw crosshairs
        painter.setPen(QPen(handle_color.darker(150), 1))
        painter.drawLine(handle_pos.x() - 4, handle_pos.y(), handle_pos.x() + 4, handle_pos.y())
        painter.drawLine(handle_pos.x(), handle_pos.y() - 4, handle_pos.x(), handle_pos.y() + 4)
        
        # Draw current values
        painter.setPen(QPen(QColor("#FFFFFF")))
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        value_text = f"({self.x_value:.3f}, {self.y_value:.3f})"
        value_rect = QRect(pad_rect.left(), pad_rect.top() - 15, pad_rect.width(), 15)
        painter.drawText(value_rect, Qt.AlignCenter, value_text)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pad_rect = self.get_pad_rect()
            if pad_rect.contains(event.pos()):
                self.dragging = True
                x_value, y_value = self.position_to_value(event.pos())
                self.set_values(x_value, y_value)
                self.valueChanged.emit(self.x_value, self.y_value)
                
    def mouseMoveEvent(self, event):
        if self.dragging:
            x_value, y_value = self.position_to_value(event.pos())
            self.set_values(x_value, y_value)
            self.valueChanged.emit(self.x_value, self.y_value)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.update()

class XYPadEditor(QGroupBox):
    """Editor for XY pad properties"""
    padChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("XY Pad Settings", parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # XY Pad preview
        self.xy_pad = XYPad()
        self.xy_pad.valueChanged.connect(self.on_pad_changed)
        layout.addWidget(self.xy_pad)
        
        # Settings form
        form_layout = QFormLayout()
        
        # X axis settings
        x_layout = QHBoxLayout()
        
        self.x_min_spin = QDoubleSpinBox()
        self.x_min_spin.setRange(-1000.0, 1000.0)
        self.x_min_spin.setDecimals(3)
        self.x_min_spin.setValue(0.0)
        self.x_min_spin.valueChanged.connect(self.update_ranges)
        x_layout.addWidget(QLabel("Min:"))
        x_layout.addWidget(self.x_min_spin)
        
        self.x_max_spin = QDoubleSpinBox()
        self.x_max_spin.setRange(-1000.0, 1000.0)
        self.x_max_spin.setDecimals(3)
        self.x_max_spin.setValue(1.0)
        self.x_max_spin.valueChanged.connect(self.update_ranges)
        x_layout.addWidget(QLabel("Max:"))
        x_layout.addWidget(self.x_max_spin)
        
        x_widget = QWidget()
        x_widget.setLayout(x_layout)
        form_layout.addRow("X Range:", x_widget)
        
        # Y axis settings
        y_layout = QHBoxLayout()
        
        self.y_min_spin = QDoubleSpinBox()
        self.y_min_spin.setRange(-1000.0, 1000.0)
        self.y_min_spin.setDecimals(3)
        self.y_min_spin.setValue(0.0)
        self.y_min_spin.valueChanged.connect(self.update_ranges)
        y_layout.addWidget(QLabel("Min:"))
        y_layout.addWidget(self.y_min_spin)
        
        self.y_max_spin = QDoubleSpinBox()
        self.y_max_spin.setRange(-1000.0, 1000.0)
        self.y_max_spin.setDecimals(3)
        self.y_max_spin.setValue(1.0)
        self.y_max_spin.valueChanged.connect(self.update_ranges)
        y_layout.addWidget(QLabel("Max:"))
        y_layout.addWidget(self.y_max_spin)
        
        y_widget = QWidget()
        y_widget.setLayout(y_layout)
        form_layout.addRow("Y Range:", y_widget)
        
        # Color settings
        color_layout = QHBoxLayout()
        
        self.pad_color_btn = QPushButton("Pad Color")
        self.pad_color_btn.clicked.connect(self.choose_pad_color)
        self.pad_color_btn.setStyleSheet("QPushButton { background-color: #333333; }")
        color_layout.addWidget(self.pad_color_btn)
        
        self.handle_color_btn = QPushButton("Handle Color")
        self.handle_color_btn.clicked.connect(self.choose_handle_color)
        self.handle_color_btn.setStyleSheet("QPushButton { background-color: #FFFFFF; color: #000000; }")
        color_layout.addWidget(self.handle_color_btn)
        
        color_widget = QWidget()
        color_widget.setLayout(color_layout)
        form_layout.addRow("Colors:", color_widget)
        
        layout.addLayout(form_layout)
        self.setLayout(layout)
        
    def update_ranges(self):
        """Update XY pad ranges"""
        x_min = self.x_min_spin.value()
        x_max = self.x_max_spin.value()
        y_min = self.y_min_spin.value()
        y_max = self.y_max_spin.value()
        
        if x_max <= x_min:
            x_max = x_min + 0.001
            self.x_max_spin.setValue(x_max)
        if y_max <= y_min:
            y_max = y_min + 0.001
            self.y_max_spin.setValue(y_max)
            
        self.xy_pad.set_ranges(x_min, x_max, y_min, y_max)
        self.padChanged.emit()
        
    def on_pad_changed(self, x_value, y_value):
        """Handle pad value changes"""
        self.padChanged.emit()
        
    def choose_pad_color(self):
        """Choose pad background color"""
        color = QColorDialog.getColor(self.xy_pad.pad_color, self, "Choose Pad Color")
        if color.isValid():
            self.xy_pad.pad_color = color
            self.pad_color_btn.setStyleSheet(f"QPushButton {{ background-color: {color.name()}; }}")
            self.xy_pad.update()
            self.padChanged.emit()
            
    def choose_handle_color(self):
        """Choose handle color"""
        color = QColorDialog.getColor(self.xy_pad.handle_color, self, "Choose Handle Color")
        if color.isValid():
            self.xy_pad.handle_color = color
            text_color = "#000000" if color.lightness() > 128 else "#FFFFFF"
            self.handle_color_btn.setStyleSheet(f"QPushButton {{ background-color: {color.name()}; color: {text_color}; }}")
            self.xy_pad.update()
            self.padChanged.emit()
            
    def get_pad_config(self):
        """Get XY pad configuration"""
        x_value, y_value = self.xy_pad.get_values()
        return {
            "x_min": self.x_min_spin.value(),
            "x_max": self.x_max_spin.value(),
            "y_min": self.y_min_spin.value(),
            "y_max": self.y_max_spin.value(),
            "x_value": x_value,
            "y_value": y_value,
            "pad_color": self.xy_pad.pad_color.name(),
            "handle_color": self.xy_pad.handle_color.name()
        }
        
    def set_pad_config(self, config):
        """Set XY pad configuration"""
        self.x_min_spin.setValue(config.get("x_min", 0.0))
        self.x_max_spin.setValue(config.get("x_max", 1.0))
        self.y_min_spin.setValue(config.get("y_min", 0.0))
        self.y_max_spin.setValue(config.get("y_max", 1.0))
        
        x_value = config.get("x_value", 0.5)
        y_value = config.get("y_value", 0.5)
        self.xy_pad.set_values(x_value, y_value)
        
        if "pad_color" in config:
            self.xy_pad.pad_color = QColor(config["pad_color"])
            self.pad_color_btn.setStyleSheet(f"QPushButton {{ background-color: {config['pad_color']}; }}")
            
        if "handle_color" in config:
            self.xy_pad.handle_color = QColor(config["handle_color"])
            color = QColor(config["handle_color"])
            text_color = "#000000" if color.lightness() > 128 else "#FFFFFF"
            self.handle_color_btn.setStyleSheet(f"QPushButton {{ background-color: {config['handle_color']}; color: {text_color}; }}")
            
        self.update_ranges()

class XYPadControlPanel(QWidget):
    """Complete XY pad control panel"""
    xyPadChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.xy_pads = []  # List of XY pad configurations
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("XY Pads"))
        header_layout.addStretch()
        
        self.add_pad_btn = QPushButton("Add XY Pad")
        self.add_pad_btn.clicked.connect(self.add_xy_pad)
        header_layout.addWidget(self.add_pad_btn)
        
        layout.addLayout(header_layout)
        
        # XY Pad editor
        self.pad_editor = XYPadEditor()
        self.pad_editor.padChanged.connect(self.xyPadChanged.emit)
        layout.addWidget(self.pad_editor)
        
        self.setLayout(layout)
        
    def add_xy_pad(self):
        """Add a new XY pad"""
        config = self.pad_editor.get_pad_config()
        self.xy_pads.append(config)
        self.xyPadChanged.emit()
        
    def get_xy_pads(self):
        """Get all XY pad configurations"""
        return self.xy_pads
        
    def set_xy_pads(self, pads):
        """Set XY pad configurations"""
        self.xy_pads = pads or []
        if self.xy_pads:
            self.pad_editor.set_pad_config(self.xy_pads[0])