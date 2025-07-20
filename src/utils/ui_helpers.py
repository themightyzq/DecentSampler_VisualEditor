"""
UI Helper functions for consistent styling and behavior across the application
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor

# UI Constants for consistency
UI_CONSTANTS = {
    'primary_color': '#2b2b2b',
    'secondary_color': '#3c3c3c', 
    'accent_color': '#4a9eff',
    'text_color': '#ffffff',
    'disabled_color': '#666666',
    'error_color': '#ff6b6b',
    'success_color': '#51cf66',
    'warning_color': '#ffd43b',
    
    'font_size_small': 9,
    'font_size_normal': 11,
    'font_size_large': 13,
    'font_size_header': 16,
    
    'spacing_small': 4,
    'spacing_normal': 8,
    'spacing_large': 16,
    
    'border_radius': 4,
    'control_height': 24,
}

def apply_dark_theme(widget):
    """Apply consistent dark theme to a widget"""
    if hasattr(widget, 'setStyleSheet'):
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {UI_CONSTANTS['primary_color']};
                color: {UI_CONSTANTS['text_color']};
                font-size: {UI_CONSTANTS['font_size_normal']}px;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {UI_CONSTANTS['secondary_color']};
                border-radius: {UI_CONSTANTS['border_radius']}px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QPushButton {{
                background-color: {UI_CONSTANTS['secondary_color']};
                border: 1px solid {UI_CONSTANTS['accent_color']};
                border-radius: {UI_CONSTANTS['border_radius']}px;
                padding: 4px 8px;
                min-height: {UI_CONSTANTS['control_height']}px;
            }}
            QPushButton:hover {{
                background-color: {UI_CONSTANTS['accent_color']};
            }}
            QPushButton:pressed {{
                background-color: {UI_CONSTANTS['accent_color']};
                border-color: {UI_CONSTANTS['text_color']};
            }}
            QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {UI_CONSTANTS['secondary_color']};
                border: 1px solid {UI_CONSTANTS['disabled_color']};
                border-radius: {UI_CONSTANTS['border_radius']}px;
                padding: 2px;
                min-height: {UI_CONSTANTS['control_height']}px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {UI_CONSTANTS['accent_color']};
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                background-color: rgba(40, 40, 40, 0.8);
                border: 2px solid #666;
                border-radius: 4px;
            }}
            QCheckBox::indicator:hover {{
                border-color: #888;
                background-color: rgba(50, 50, 50, 0.8);
            }}
            QCheckBox::indicator:unchecked {{
                background-color: rgba(40, 40, 40, 0.8);
                border: 2px solid #666;
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {UI_CONSTANTS['accent_color']};
                border: 2px solid {UI_CONSTANTS['accent_color']};
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked::after {{
                content: "\u2713";
                position: absolute;
                color: white;
                font-size: 16px;
                font-weight: bold;
                top: -2px;
                left: 2px;
            }}
            QCheckBox {{
                spacing: 8px;
                font-size: 14px;
                color: #f0f0f0;
            }}
            QTabWidget::pane {{
                border: 1px solid {UI_CONSTANTS['secondary_color']};
                background-color: {UI_CONSTANTS['primary_color']};
            }}
            QTabBar::tab {{
                background-color: {UI_CONSTANTS['secondary_color']};
                padding: 8px 12px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {UI_CONSTANTS['accent_color']};
            }}
        """)

def create_tooltip_label(text, parent=None):
    """Create a consistently styled tooltip label"""
    label = QLabel(text, parent)
    label.setStyleSheet(f"""
        QLabel {{
            color: {UI_CONSTANTS['disabled_color']};
            font-style: italic;
            font-size: {UI_CONSTANTS['font_size_small']}px;
        }}
    """)
    label.setWordWrap(True)
    return label

def create_section_header(text, parent=None):
    """Create a consistently styled section header"""
    label = QLabel(text, parent)
    label.setStyleSheet(f"""
        QLabel {{
            color: {UI_CONSTANTS['text_color']};
            font-weight: bold;
            font-size: {UI_CONSTANTS['font_size_header']}px;
            padding: {UI_CONSTANTS['spacing_normal']}px 0px;
        }}
    """)
    return label

def create_separator(parent=None):
    """Create a horizontal separator line"""
    line = QFrame(parent)
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    line.setStyleSheet(f"""
        QFrame {{
            color: {UI_CONSTANTS['secondary_color']};
        }}
    """)
    return line

class StatusMessageManager:
    """Manages temporary status messages with consistent styling"""
    
    def __init__(self, status_bar):
        self.status_bar = status_bar
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.clear_message)
        
    def show_message(self, message, message_type="info", duration=3000):
        """Show a temporary status message"""
        colors = {
            "info": UI_CONSTANTS['text_color'],
            "success": UI_CONSTANTS['success_color'], 
            "warning": UI_CONSTANTS['warning_color'],
            "error": UI_CONSTANTS['error_color']
        }
        
        color = colors.get(message_type, UI_CONSTANTS['text_color'])
        self.status_bar.setStyleSheet(f"color: {color};")
        self.status_bar.showMessage(message, duration)
        
        if duration > 0:
            self.timer.start(duration)
            
    def clear_message(self):
        """Clear the status message and reset styling"""
        self.status_bar.clearMessage()
        self.status_bar.setStyleSheet("")

def add_tooltips_to_widget(widget, tooltip_map):
    """Add tooltips to multiple child widgets using a mapping"""
    for child_name, tooltip_text in tooltip_map.items():
        child = widget.findChild(QWidget, child_name)
        if child:
            child.setToolTip(tooltip_text)

def validate_numeric_input(value, min_val=None, max_val=None, default=0):
    """Safely validate and convert numeric input"""
    try:
        num_val = float(value)
        if min_val is not None and num_val < min_val:
            return min_val
        if max_val is not None and num_val > max_val:
            return max_val
        return num_val
    except (ValueError, TypeError):
        return default

def safe_color_conversion(color_str, default_color="#000000"):
    """Safely convert color string to hex format"""
    try:
        if color_str.startswith("FF"):
            return "#" + color_str[2:]
        elif color_str.startswith("#"):
            return color_str
        else:
            return "#" + color_str
    except (AttributeError, TypeError):
        return default_color

class ErrorHandler:
    """Centralized error handling with user-friendly messages"""
    
    @staticmethod
    def handle_file_error(operation, filename, error, parent=None):
        """Handle file operation errors with user-friendly messages"""
        from PyQt5.QtWidgets import QMessageBox
        
        error_messages = {
            "FileNotFoundError": f"File not found: {filename}",
            "PermissionError": f"Permission denied accessing: {filename}",
            "OSError": f"System error accessing: {filename}",
            "ValueError": f"Invalid data in file: {filename}",
            "XMLSyntaxError": f"Invalid XML format in: {filename}"
        }
        
        error_type = type(error).__name__
        message = error_messages.get(error_type, f"Error {operation} {filename}: {str(error)}")
        
        QMessageBox.critical(parent, f"File {operation.title()} Error", message)
        
    @staticmethod 
    def handle_validation_error(field_name, error, parent=None):
        """Handle validation errors with helpful guidance"""
        from PyQt5.QtWidgets import QMessageBox
        
        message = f"Invalid value for {field_name}: {str(error)}\n\nPlease check the input and try again."
        QMessageBox.warning(parent, "Validation Error", message)

def create_collapsible_group(title, widget, parent=None, collapsed=False):
    """Create a collapsible group box"""
    from PyQt5.QtWidgets import QPushButton, QVBoxLayout
    
    group = QGroupBox(parent)
    group.setCheckable(True)
    group.setChecked(not collapsed)
    
    # Create toggle button in title
    toggle_btn = QPushButton(f"{'▼' if not collapsed else '▶'} {title}")
    toggle_btn.setFlat(True)
    toggle_btn.clicked.connect(lambda: toggle_group(group, widget, toggle_btn))
    
    layout = QVBoxLayout()
    layout.addWidget(toggle_btn)
    layout.addWidget(widget)
    group.setLayout(layout)
    
    # Hide widget if collapsed
    widget.setVisible(not collapsed)
    
    return group

def toggle_group(group, widget, button):
    """Toggle visibility of collapsible group"""
    visible = widget.isVisible()
    widget.setVisible(not visible)
    button.setText(button.text().replace('▼' if visible else '▶', '▶' if visible else '▼'))