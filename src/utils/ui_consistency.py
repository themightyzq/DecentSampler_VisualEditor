"""
UI Consistency and Styling Module
Provides consistent styling across all panels and controls
"""

from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class UIConstants:
    """Constants for consistent UI styling"""
    
    # Header styling
    HEADER_FONT_SIZE = 14
    HEADER_FONT_WEIGHT = "bold"
    HEADER_COLOR = "#f0f0f0"
    HEADER_MARGIN_BOTTOM = 8
    
    # Subheader styling  
    SUBHEADER_FONT_SIZE = 12
    SUBHEADER_FONT_WEIGHT = "600"
    SUBHEADER_COLOR = "#d0d0d0"
    
    # Body text
    BODY_FONT_SIZE = 11
    BODY_COLOR = "#c0c0c0"
    
    # Button styling
    BUTTON_HEIGHT = 28
    BUTTON_FONT_SIZE = 11
    
    # Input styling
    INPUT_HEIGHT = 24
    INPUT_FONT_SIZE = 11
    
    # Panel spacing
    PANEL_MARGIN = 8
    PANEL_SPACING = 6
    
    # Resolution breakpoints
    BREAKPOINT_SMALL = 1400
    BREAKPOINT_MEDIUM = 1600
    BREAKPOINT_LARGE = 1900

class UIStyler:
    """Utility class for applying consistent styling"""
    
    @staticmethod
    def create_header_label(text: str, tooltip: str = "") -> QLabel:
        """Create a consistently styled header label"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                font-size: {UIConstants.HEADER_FONT_SIZE}px;
                font-weight: {UIConstants.HEADER_FONT_WEIGHT};
                color: {UIConstants.HEADER_COLOR};
                margin-bottom: {UIConstants.HEADER_MARGIN_BOTTOM}px;
                padding: 4px 0px;
            }}
        """)
        if tooltip:
            label.setToolTip(tooltip)
        return label
    
    @staticmethod
    def create_subheader_label(text: str, tooltip: str = "") -> QLabel:
        """Create a consistently styled subheader label"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                font-size: {UIConstants.SUBHEADER_FONT_SIZE}px;
                font-weight: {UIConstants.SUBHEADER_FONT_WEIGHT};
                color: {UIConstants.SUBHEADER_COLOR};
                margin-bottom: 4px;
                padding: 2px 0px;
            }}
        """)
        if tooltip:
            label.setToolTip(tooltip)
        return label
    
    @staticmethod
    def create_body_label(text: str, tooltip: str = "") -> QLabel:
        """Create a consistently styled body text label"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                font-size: {UIConstants.BODY_FONT_SIZE}px;
                color: {UIConstants.BODY_COLOR};
            }}
        """)
        if tooltip:
            label.setToolTip(tooltip)
        return label
    
    @staticmethod
    def apply_panel_styling(widget: QWidget):
        """Apply consistent panel styling"""
        widget.setContentsMargins(
            UIConstants.PANEL_MARGIN,
            UIConstants.PANEL_MARGIN, 
            UIConstants.PANEL_MARGIN,
            UIConstants.PANEL_MARGIN
        )
    
    @staticmethod
    def get_responsive_font_size(base_size: int, screen_width: int) -> int:
        """Get responsive font size based on screen width"""
        if screen_width < UIConstants.BREAKPOINT_SMALL:
            return max(9, base_size - 2)  # Smaller screens
        elif screen_width < UIConstants.BREAKPOINT_MEDIUM:
            return max(10, base_size - 1)  # Medium screens
        elif screen_width < UIConstants.BREAKPOINT_LARGE:
            return base_size  # Standard size
        else:
            return base_size + 1  # Large screens
    
    @staticmethod
    def get_responsive_spacing(base_spacing: int, screen_width: int) -> int:
        """Get responsive spacing based on screen width"""
        if screen_width < UIConstants.BREAKPOINT_SMALL:
            return max(2, base_spacing - 2)
        elif screen_width < UIConstants.BREAKPOINT_MEDIUM:
            return max(4, base_spacing - 1)
        else:
            return base_spacing
    
    @staticmethod
    def apply_responsive_styling(widget: QWidget, screen_width: int):
        """Apply responsive styling based on screen size"""
        # Get responsive values
        font_size = UIStyler.get_responsive_font_size(UIConstants.BODY_FONT_SIZE, screen_width)
        spacing = UIStyler.get_responsive_spacing(UIConstants.PANEL_SPACING, screen_width)
        margin = UIStyler.get_responsive_spacing(UIConstants.PANEL_MARGIN, screen_width)
        
        # Apply to widget
        widget.setContentsMargins(margin, margin, margin, margin)
        
        # Apply font size to widget and children
        font = widget.font()
        font.setPointSize(font_size)
        widget.setFont(font)

class TabStyler:
    """Consistent styling for tab widgets"""
    
    @staticmethod
    def get_tab_stylesheet(screen_width: int) -> str:
        """Get consistent tab styling for the screen size"""
        # Responsive font size
        font_size = UIStyler.get_responsive_font_size(11, screen_width)
        padding = UIStyler.get_responsive_spacing(8, screen_width)
        
        return f"""
            QTabWidget::pane {{
                border: 1px solid #444;
                background-color: #2a2a2a;
            }}
            
            QTabBar::tab {{
                background-color: #3a3a3a;
                color: #c0c0c0;
                border: 1px solid #444;
                border-bottom: none;
                padding: {padding}px {padding * 2}px;
                margin-right: 2px;
                font-size: {font_size}px;
                font-weight: 500;
            }}
            
            QTabBar::tab:selected {{
                background-color: #4a7c59;
                color: #ffffff;
                font-weight: 600;
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: #4a4a4a;
                color: #ffffff;
            }}
        """

class ButtonStyler:
    """Consistent button styling"""
    
    @staticmethod
    def get_primary_button_style(screen_width: int) -> str:
        """Get primary button styling"""
        font_size = UIStyler.get_responsive_font_size(UIConstants.BUTTON_FONT_SIZE, screen_width)
        height = UIStyler.get_responsive_spacing(UIConstants.BUTTON_HEIGHT, screen_width)
        padding = UIStyler.get_responsive_spacing(6, screen_width)
        
        return f"""
            QPushButton {{
                background-color: #4a7c59;
                color: white;
                border: 1px solid #3a6b49;
                border-radius: 4px;
                padding: {padding}px {padding * 2}px;
                font-size: {font_size}px;
                font-weight: 500;
                min-height: {height}px;
            }}
            QPushButton:hover {{
                background-color: #5a8c69;
            }}
            QPushButton:pressed {{
                background-color: #3a6b49;
            }}
            QPushButton:disabled {{
                background-color: #666;
                color: #999;
            }}
        """
    
    @staticmethod
    def get_secondary_button_style(screen_width: int) -> str:
        """Get secondary button styling"""
        font_size = UIStyler.get_responsive_font_size(UIConstants.BUTTON_FONT_SIZE, screen_width)
        height = UIStyler.get_responsive_spacing(UIConstants.BUTTON_HEIGHT, screen_width)
        padding = UIStyler.get_responsive_spacing(6, screen_width)
        
        return f"""
            QPushButton {{
                background-color: #4a4a4a;
                color: #f0f0f0;
                border: 1px solid #666;
                border-radius: 4px;
                padding: {padding}px {padding * 2}px;
                font-size: {font_size}px;
                font-weight: 500;
                min-height: {height}px;
            }}
            QPushButton:hover {{
                background-color: #5a5a5a;
            }}
            QPushButton:pressed {{
                background-color: #3a3a3a;
            }}
            QPushButton:disabled {{
                background-color: #333;
                color: #777;
            }}
        """