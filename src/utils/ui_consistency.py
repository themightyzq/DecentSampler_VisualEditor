"""
UI Consistency and Styling Module
Provides consistent styling across all panels and controls
Now integrated with the centralized theme system
"""

from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .theme_manager import ThemeColors, ThemeFonts, ThemeSpacing, theme_manager

class UIConstants:
    """Constants for consistent UI styling - now references theme system"""
    
    # Header styling
    HEADER_FONT_SIZE = ThemeFonts.SIZE_H2
    HEADER_FONT_WEIGHT = str(ThemeFonts.WEIGHT_BOLD)
    HEADER_COLOR = ThemeColors.TEXT_PRIMARY
    HEADER_MARGIN_BOTTOM = ThemeSpacing.SPACING_MEDIUM
    
    # Subheader styling  
    SUBHEADER_FONT_SIZE = ThemeFonts.SIZE_H3
    SUBHEADER_FONT_WEIGHT = str(ThemeFonts.WEIGHT_SEMIBOLD)
    SUBHEADER_COLOR = ThemeColors.TEXT_PRIMARY
    
    # Body text
    BODY_FONT_SIZE = ThemeFonts.SIZE_SMALL
    BODY_COLOR = ThemeColors.TEXT_SECONDARY
    
    # Button styling
    BUTTON_HEIGHT = ThemeSpacing.HEIGHT_BUTTON
    BUTTON_FONT_SIZE = ThemeFonts.SIZE_SMALL
    
    # Input styling
    INPUT_HEIGHT = ThemeSpacing.HEIGHT_INPUT
    INPUT_FONT_SIZE = ThemeFonts.SIZE_SMALL
    
    # Panel spacing
    PANEL_MARGIN = ThemeSpacing.SPACING_MEDIUM
    PANEL_SPACING = ThemeSpacing.SPACING_SMALL + 2
    
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
        label.setProperty("heading", "h2")
        if tooltip:
            label.setToolTip(tooltip)
        return label
    
    @staticmethod
    def create_subheader_label(text: str, tooltip: str = "") -> QLabel:
        """Create a consistently styled subheader label"""
        label = QLabel(text)
        label.setProperty("heading", "h3")
        if tooltip:
            label.setToolTip(tooltip)
        return label
    
    @staticmethod
    def create_body_label(text: str, tooltip: str = "") -> QLabel:
        """Create a consistently styled body text label"""
        label = QLabel(text)
        label.setProperty("secondary", "true")
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