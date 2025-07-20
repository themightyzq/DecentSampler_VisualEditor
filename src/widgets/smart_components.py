"""
Smart Component Library for DecentSampler Frontend
Standardized, reusable UI components with consistent styling and behavior
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame,
    QGroupBox, QSlider, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
    QButtonGroup, QSizePolicy, QScrollArea, QTabWidget, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QIcon
from utils.enhanced_typography import (
    TypographyStyles, StyledLabel, TypographyHelper, 
    create_h2_label, create_h3_label, create_body_label, create_small_label
)
from utils.theme_manager import ThemeColors, ThemeSpacing


class SmartButton(QPushButton):
    """Enhanced button with automatic sizing and consistent styling"""
    
    def __init__(self, text="", button_type="primary", icon=None, parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.icon_text = icon
        self._setup_button()
    
    def _setup_button(self):
        """Setup button styling and behavior"""
        # Calculate optimal size based on text
        style = TypographyStyles.button_primary if self.button_type == "primary" else TypographyStyles.button_secondary
        optimal_width = TypographyHelper.calculate_optimal_width(self.text(), style)
        optimal_height = max(ThemeSpacing.HEIGHT_BUTTON, TypographyHelper.calculate_optimal_height(style))
        
        self.setMinimumSize(optimal_width, optimal_height)
        self.setCursor(Qt.PointingHandCursor)
        
        # Apply styling based on button type
        if self.button_type == "primary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ThemeColors.ACCENT};
                    color: {ThemeColors.TEXT_PRIMARY};
                    border: none;
                    border-radius: {ThemeSpacing.RADIUS_MEDIUM}px;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 11px;
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
        elif self.button_type == "secondary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ThemeColors.PANEL_BG};
                    color: {ThemeColors.TEXT_PRIMARY};
                    border: 1px solid {ThemeColors.BORDER};
                    border-radius: {ThemeSpacing.RADIUS_MEDIUM}px;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 11px;
                    min-height: 32px;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {ThemeColors.HOVER_BG};
                    border-color: {ThemeColors.ACCENT};
                }}
                QPushButton:pressed {{
                    background-color: {ThemeColors.PRESSED_BG};
                }}
            """)
        elif self.button_type == "icon":
            self.setFixedSize(32, 32)
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {ThemeColors.TEXT_SECONDARY};
                    border: 1px solid transparent;
                    border-radius: {ThemeSpacing.RADIUS_MEDIUM}px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {ThemeColors.HOVER_BG};
                    border-color: {ThemeColors.BORDER};
                    color: {ThemeColors.TEXT_PRIMARY};
                }}
            """)


class SmartButtonGroup(QWidget):
    """Intelligent button group with overflow handling and consistent spacing"""
    
    def __init__(self, buttons=None, orientation=Qt.Horizontal, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.buttons = []
        self._setup_layout()
        
        if buttons:
            for button in buttons:
                self.add_button(button)
    
    def _setup_layout(self):
        """Setup the layout based on orientation"""
        if self.orientation == Qt.Horizontal:
            self.layout = QHBoxLayout(self)
        else:
            self.layout = QVBoxLayout(self)
        
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(ThemeSpacing.SPACING_SMALL)
    
    def add_button(self, button_config):
        """Add a button to the group"""
        if isinstance(button_config, dict):
            button = SmartButton(
                text=button_config.get('text', ''),
                button_type=button_config.get('type', 'secondary'),
                icon=button_config.get('icon')
            )
            if 'callback' in button_config:
                button.clicked.connect(button_config['callback'])
        else:
            button = button_config
        
        self.buttons.append(button)
        self.layout.addWidget(button)
    
    def add_stretch(self):
        """Add stretch to the layout"""
        self.layout.addStretch()


class ParameterControl(QWidget):
    """Unified parameter control with label, control, and value display"""
    valueChanged = pyqtSignal(float)
    
    def __init__(self, label="", control_type="slider", value_range=(0, 100), 
                 default_value=0, decimals=0, units="", parent=None):
        super().__init__(parent)
        self.label_text = label
        self.control_type = control_type
        self.value_range = value_range
        self.decimals = decimals
        self.units = units
        self._setup_control(default_value)
    
    def _setup_control(self, default_value):
        """Setup the parameter control UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(ThemeSpacing.SPACING_SMALL)
        
        # Label
        if self.label_text:
            self.label = create_small_label(self.label_text)
            layout.addWidget(self.label)
        
        # Control widget
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(ThemeSpacing.SPACING_SMALL)
        
        if self.control_type == "slider":
            self.control = QSlider(Qt.Horizontal)
            self.control.setRange(int(self.value_range[0] * (10 ** self.decimals)), 
                                int(self.value_range[1] * (10 ** self.decimals)))
            self.control.setValue(int(default_value * (10 ** self.decimals)))
            self.control.valueChanged.connect(self._on_slider_changed)
            
        elif self.control_type == "spinbox":
            if self.decimals > 0:
                self.control = QDoubleSpinBox()
                self.control.setDecimals(self.decimals)
            else:
                self.control = QSpinBox()
            
            self.control.setRange(self.value_range[0], self.value_range[1])
            self.control.setValue(default_value)
            if self.units:
                self.control.setSuffix(f" {self.units}")
            self.control.valueChanged.connect(self.valueChanged.emit)
        
        elif self.control_type == "combo":
            self.control = QComboBox()
            # Populate with range values if they're strings
            if isinstance(self.value_range, list):
                self.control.addItems([str(item) for item in self.value_range])
            self.control.currentIndexChanged.connect(self._on_combo_changed)
        
        control_layout.addWidget(self.control)
        
        # Value display for sliders
        if self.control_type == "slider":
            self.value_display = create_small_label(f"{default_value:.{self.decimals}f}")
            self.value_display.setMinimumWidth(40)
            self.value_display.setAlignment(Qt.AlignCenter)
            control_layout.addWidget(self.value_display)
        
        layout.addLayout(control_layout)
    
    def _on_slider_changed(self, value):
        """Handle slider value changes"""
        actual_value = value / (10 ** self.decimals)
        if hasattr(self, 'value_display'):
            display_text = f"{actual_value:.{self.decimals}f}"
            if self.units:
                display_text += f" {self.units}"
            self.value_display.setText(display_text)
        self.valueChanged.emit(actual_value)
    
    def _on_combo_changed(self, index):
        """Handle combo box changes"""
        self.valueChanged.emit(float(index))
    
    def value(self):
        """Get current value"""
        if self.control_type == "slider":
            return self.control.value() / (10 ** self.decimals)
        else:
            return float(self.control.value())
    
    def setValue(self, value):
        """Set current value"""
        if self.control_type == "slider":
            self.control.setValue(int(value * (10 ** self.decimals)))
        else:
            self.control.setValue(value)


class WorkflowPanel(QFrame):
    """Standardized panel with header, content area, and optional footer"""
    
    def __init__(self, title="", collapsible=False, help_text="", parent=None):
        super().__init__(parent)
        self.title = title
        self.collapsible = collapsible
        self.help_text = help_text
        self.content_widget = None
        self.is_collapsed = False
        self._setup_panel()
    
    def _setup_panel(self):
        """Setup the panel structure"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeColors.PANEL_BG};
                border: 1px solid {ThemeColors.BORDER};
                border-radius: {ThemeSpacing.RADIUS_LARGE}px;
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self._create_header()
        main_layout.addWidget(self.header_widget)
        
        # Content area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(
            ThemeSpacing.SPACING_LARGE, 
            ThemeSpacing.SPACING_MEDIUM,
            ThemeSpacing.SPACING_LARGE, 
            ThemeSpacing.SPACING_LARGE
        )
        
        main_layout.addWidget(self.content_area)
        
        # Animation for collapsible panels
        if self.collapsible:
            self._setup_animation()
    
    def _create_header(self):
        """Create the panel header"""
        self.header_widget = QWidget()
        self.header_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {ThemeColors.SECONDARY_BG};
                border-bottom: 1px solid {ThemeColors.BORDER};
                border-top-left-radius: {ThemeSpacing.RADIUS_LARGE}px;
                border-top-right-radius: {ThemeSpacing.RADIUS_LARGE}px;
            }}
        """)
        
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(
            ThemeSpacing.SPACING_LARGE,
            ThemeSpacing.SPACING_MEDIUM,
            ThemeSpacing.SPACING_LARGE,
            ThemeSpacing.SPACING_MEDIUM
        )
        
        # Title
        if self.title:
            self.title_label = create_h3_label(self.title)
            header_layout.addWidget(self.title_label)
        
        # Help button
        if self.help_text:
            self.help_button = SmartButton("?", "icon")
            self.help_button.setToolTip(self.help_text)
            header_layout.addWidget(self.help_button)
        
        # Collapse button
        if self.collapsible:
            self.collapse_button = SmartButton("▼", "icon")
            self.collapse_button.clicked.connect(self.toggle_collapse)
            header_layout.addWidget(self.collapse_button)
        
        header_layout.addStretch()
    
    def _setup_animation(self):
        """Setup collapse/expand animation"""
        self.animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
    
    def set_content(self, widget):
        """Set the content widget"""
        if self.content_widget:
            self.content_layout.removeWidget(self.content_widget)
            self.content_widget.deleteLater()
        
        self.content_widget = widget
        self.content_layout.addWidget(widget)
    
    def toggle_collapse(self):
        """Toggle collapsed state"""
        if not self.collapsible:
            return
        
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            self.animation.setStartValue(self.content_area.height())
            self.animation.setEndValue(0)
            self.collapse_button.setText("▶")
        else:
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.content_area.sizeHint().height())
            self.collapse_button.setText("▼")
        
        self.animation.start()


class SmartTabWidget(QTabWidget):
    """Enhanced tab widget with icons, better styling, and workflow optimization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_styling()
    
    def _setup_styling(self):
        """Setup enhanced tab styling"""
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {ThemeColors.SECONDARY_BG};
                border: 1px solid {ThemeColors.BORDER};
                border-radius: {ThemeSpacing.RADIUS_MEDIUM}px;
                top: -1px;
            }}
            
            QTabBar::tab {{
                background-color: {ThemeColors.PANEL_BG};
                color: {ThemeColors.TEXT_SECONDARY};
                padding: 12px 20px;
                margin-right: 2px;
                border: 1px solid {ThemeColors.BORDER};
                border-bottom: none;
                border-top-left-radius: {ThemeSpacing.RADIUS_MEDIUM}px;
                border-top-right-radius: {ThemeSpacing.RADIUS_MEDIUM}px;
                min-width: 100px;
                font-weight: 500;
            }}
            
            QTabBar::tab:selected {{
                background-color: {ThemeColors.SECONDARY_BG};
                color: {ThemeColors.TEXT_PRIMARY};
                border-color: {ThemeColors.BORDER};
                font-weight: 600;
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {ThemeColors.HOVER_BG};
                color: {ThemeColors.TEXT_PRIMARY};
            }}
        """)
    
    def add_workflow_tab(self, widget, title, icon_text=None, tooltip=None, shortcut=None):
        """Add a tab with workflow-optimized features"""
        tab_text = title
        if icon_text:
            tab_text = f"{icon_text} {title}"
        
        index = self.addTab(widget, tab_text)
        
        if tooltip:
            self.setTabToolTip(index, tooltip)
        
        if shortcut:
            # Add keyboard shortcut handling
            widget.setToolTip(f"{tooltip or title} (Shortcut: {shortcut})")
        
        return index


class ParameterMapper(QWidget):
    """Visual parameter mapping interface"""
    
    def __init__(self, sources=None, destinations=None, parent=None):
        super().__init__(parent)
        self.sources = sources or []
        self.destinations = destinations or []
        self.mappings = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the parameter mapper UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = create_h3_label("Parameter Mapping")
        layout.addWidget(header)
        
        # Mapping area
        self.mapping_area = QScrollArea()
        self.mapping_widget = QWidget()
        self.mapping_layout = QVBoxLayout(self.mapping_widget)
        
        self.mapping_area.setWidget(self.mapping_widget)
        self.mapping_area.setWidgetResizable(True)
        layout.addWidget(self.mapping_area)
        
        # Add mapping button
        add_button = SmartButton("Add Mapping", "primary")
        add_button.clicked.connect(self.add_mapping)
        layout.addWidget(add_button)
    
    def add_mapping(self):
        """Add a new parameter mapping"""
        mapping_widget = QWidget()
        mapping_layout = QHBoxLayout(mapping_widget)
        
        # Source combo
        source_combo = QComboBox()
        source_combo.addItems(self.sources)
        mapping_layout.addWidget(QLabel("Source:"))
        mapping_layout.addWidget(source_combo)
        
        # Arrow
        mapping_layout.addWidget(QLabel("→"))
        
        # Destination combo
        dest_combo = QComboBox()
        dest_combo.addItems(self.destinations)
        mapping_layout.addWidget(QLabel("Destination:"))
        mapping_layout.addWidget(dest_combo)
        
        # Remove button
        remove_button = SmartButton("✗", "icon")
        remove_button.clicked.connect(lambda: self.remove_mapping(mapping_widget))
        mapping_layout.addWidget(remove_button)
        
        self.mapping_layout.addWidget(mapping_widget)
        self.mappings.append(mapping_widget)
    
    def remove_mapping(self, mapping_widget):
        """Remove a parameter mapping"""
        self.mapping_layout.removeWidget(mapping_widget)
        mapping_widget.deleteLater()
        if mapping_widget in self.mappings:
            self.mappings.remove(mapping_widget)


# Convenience functions for creating common components
def create_primary_button(text, callback=None):
    """Create a primary action button"""
    button = SmartButton(text, "primary")
    if callback:
        button.clicked.connect(callback)
    return button

def create_secondary_button(text, callback=None):
    """Create a secondary action button"""
    button = SmartButton(text, "secondary")
    if callback:
        button.clicked.connect(callback)
    return button

def create_icon_button(icon_text, callback=None, tooltip=""):
    """Create an icon button"""
    button = SmartButton(icon_text, "icon")
    if callback:
        button.clicked.connect(callback)
    if tooltip:
        button.setToolTip(tooltip)
    return button

def create_parameter_group(title, parameters):
    """Create a group of parameter controls"""
    panel = WorkflowPanel(title)
    
    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)
    
    for param_config in parameters:
        param_control = ParameterControl(**param_config)
        content_layout.addWidget(param_control)
    
    panel.set_content(content_widget)
    return panel