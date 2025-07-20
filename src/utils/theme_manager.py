"""
Theme Manager for DecentSampler Frontend
Handles centralized theming, color palette, and dynamic style updates
"""

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtWidgets import QApplication
import os
from typing import Dict, Optional, Any


class ThemeColors:
    """Centralized color palette for the application"""
    # Background colors
    PRIMARY_BG = "#1a1a1a"
    SECONDARY_BG = "#252525"
    PANEL_BG = "#2a2a2a"
    HOVER_BG = "#353535"
    PRESSED_BG = "#303030"
    
    # Border colors
    BORDER = "#3a3a3a"
    BORDER_HOVER = "#4a4a4a"
    BORDER_FOCUS = "#4a9eff"
    
    # Accent colors
    ACCENT = "#4a9eff"
    ACCENT_HOVER = "#6bb3ff"
    ACCENT_PRESSED = "#3a8eee"
    
    # Status colors
    SUCCESS = "#4caf50"
    WARNING = "#ff9800"
    ERROR = "#f44336"
    INFO = "#2196f3"
    
    # Accessibility colors (colorblind-safe)
    ACCESSIBLE_BLUE = "#0173B2"
    ACCESSIBLE_ORANGE = "#DE8F05"
    ACCESSIBLE_GREEN = "#029E73"
    ACCESSIBLE_RED = "#D55E00"
    ACCESSIBLE_PURPLE = "#CC78BC"
    ACCESSIBLE_BROWN = "#CA9161"
    ACCESSIBLE_PINK = "#FBAFE4"
    ACCESSIBLE_GRAY = "#949494"
    ACCESSIBLE_YELLOW = "#ECE133"
    ACCESSIBLE_LIGHT_BLUE = "#56B4E9"
    
    # Text colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b0b0b0"
    TEXT_DISABLED = "#666666"
    TEXT_HINT = "#888888"
    
    # Special colors
    SELECTION_BG = "#4a9eff"
    SELECTION_FG = "#ffffff"
    SHADOW = "rgba(0, 0, 0, 0.3)"
    OVERLAY = "rgba(0, 0, 0, 0.5)"


class ThemeFonts:
    """Centralized font definitions"""
    FAMILY = "Arial, Helvetica, sans-serif"
    
    # Font sizes
    SIZE_H1 = 18
    SIZE_H2 = 14
    SIZE_H3 = 12
    SIZE_BODY = 12
    SIZE_SMALL = 11
    SIZE_TINY = 10
    
    # Font weights
    WEIGHT_BOLD = 700
    WEIGHT_SEMIBOLD = 600
    WEIGHT_MEDIUM = 500
    WEIGHT_REGULAR = 400
    WEIGHT_LIGHT = 300


class ThemeSpacing:
    """Centralized spacing and sizing constants"""
    # Grid system (8px base)
    GRID_UNIT = 8
    
    # Spacing
    SPACING_TINY = 2
    SPACING_SMALL = 4
    SPACING_MEDIUM = 8
    SPACING_LARGE = 16
    SPACING_XLARGE = 24
    
    # Component heights
    HEIGHT_BUTTON = 28
    HEIGHT_INPUT = 32
    HEIGHT_SMALL_BUTTON = 24
    HEIGHT_LARGE_BUTTON = 36
    
    # Border radius
    RADIUS_SMALL = 3
    RADIUS_MEDIUM = 4
    RADIUS_LARGE = 8
    
    # Component sizes
    KNOB_SIZE = 48
    SLIDER_HEIGHT = 24
    ICON_SIZE_SMALL = 16
    ICON_SIZE_MEDIUM = 20
    ICON_SIZE_LARGE = 24


class ThemeManager(QObject):
    """
    Manages application theming and provides dynamic style updates
    """
    themeChanged = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._current_theme = "dark"
        self._custom_styles: Dict[str, str] = {}
        self._stylesheet_path = None
        self._accessibility_mode = False
        self._high_contrast_mode = False
        
    def initialize(self, app: QApplication):
        """Initialize theme manager with application instance"""
        self.app = app
        self.load_theme()
        
    def load_theme(self, theme_name: str = "dark"):
        """Load and apply theme stylesheet"""
        self._current_theme = theme_name
        
        # Get stylesheet path
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        stylesheet_path = os.path.join(base_path, "styles", "main_theme.qss")
        
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r') as f:
                stylesheet = f.read()
                
            # Apply custom style overrides
            for selector, style in self._custom_styles.items():
                stylesheet += f"\n{selector} {{ {style} }}"
                
            self.app.setStyleSheet(stylesheet)
            self._stylesheet_path = stylesheet_path
            self.themeChanged.emit()
        else:
            print(f"Warning: Theme stylesheet not found at {stylesheet_path}")
    
    def reload_theme(self):
        """Reload current theme (useful for development)"""
        self.load_theme(self._current_theme)
    
    def set_custom_style(self, selector: str, style: str):
        """Add custom style override for specific selector"""
        self._custom_styles[selector] = style
        self.reload_theme()
    
    def remove_custom_style(self, selector: str):
        """Remove custom style override"""
        if selector in self._custom_styles:
            del self._custom_styles[selector]
            self.reload_theme()
    
    def apply_widget_style(self, widget, style_class: str):
        """Apply a specific style class to a widget"""
        widget.setProperty("class", style_class)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
    
    def set_widget_accent(self, widget, accent_color: str = None):
        """Set accent color for a specific widget"""
        if accent_color is None:
            accent_color = ThemeColors.ACCENT
        widget.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                border-color: {accent_color};
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(accent_color, 20)};
                border-color: {self.lighten_color(accent_color, 20)};
            }}
        """)
    
    @staticmethod
    def lighten_color(hex_color: str, percent: int) -> str:
        """Lighten a hex color by a percentage"""
        color = QColor(hex_color)
        h, s, l, a = color.getHsl()
        l = min(255, l + int(255 * percent / 100))
        color.setHsl(h, s, l, a)
        return color.name()
    
    @staticmethod
    def darken_color(hex_color: str, percent: int) -> str:
        """Darken a hex color by a percentage"""
        color = QColor(hex_color)
        h, s, l, a = color.getHsl()
        l = max(0, l - int(255 * percent / 100))
        color.setHsl(h, s, l, a)
        return color.name()
    
    @staticmethod
    def create_font(size: int = ThemeFonts.SIZE_BODY, 
                   weight: int = ThemeFonts.WEIGHT_REGULAR,
                   family: str = ThemeFonts.FAMILY) -> QFont:
        """Create a QFont with theme settings"""
        font = QFont(family)
        font.setPixelSize(size)
        font.setWeight(weight)
        return font
    
    def get_color(self, color_name: str) -> str:
        """Get color value by name from ThemeColors"""
        return getattr(ThemeColors, color_name, ThemeColors.TEXT_PRIMARY)
    
    def get_spacing(self, spacing_name: str) -> int:
        """Get spacing value by name from ThemeSpacing"""
        return getattr(ThemeSpacing, spacing_name, ThemeSpacing.SPACING_MEDIUM)
    
    def create_shadow_style(self, elevation: int = 2) -> str:
        """Create box-shadow style based on elevation level"""
        if elevation == 1:
            return f"box-shadow: 0 1px 3px {ThemeColors.SHADOW};"
        elif elevation == 2:
            return f"box-shadow: 0 2px 6px {ThemeColors.SHADOW};"
        elif elevation == 3:
            return f"box-shadow: 0 4px 12px {ThemeColors.SHADOW};"
        else:
            return ""
    
    def get_responsive_value(self, base_value: int, screen_size: str) -> int:
        """Get responsive value based on screen size"""
        multipliers = {
            "large": 1.0,
            "medium": 0.9,
            "small": 0.8,
            "compact": 0.7
        }
        return int(base_value * multipliers.get(screen_size, 1.0))
    
    def enable_accessibility_mode(self, enabled: bool = True):
        """Enable accessibility features in theme"""
        self._accessibility_mode = enabled
        if enabled:
            # Override status colors with accessible alternatives
            self.set_custom_style("/* Accessibility Status Colors */", f"""
                .status-success {{ background-color: {ThemeColors.ACCESSIBLE_GREEN}; }}
                .status-warning {{ background-color: {ThemeColors.ACCESSIBLE_ORANGE}; }}
                .status-error {{ background-color: {ThemeColors.ACCESSIBLE_RED}; }}
                .status-info {{ background-color: {ThemeColors.ACCESSIBLE_BLUE}; }}
            """)
        else:
            self.remove_custom_style("/* Accessibility Status Colors */")
        
        self.themeChanged.emit()
    
    def enable_high_contrast_mode(self, enabled: bool = True):
        """Enable high contrast mode"""
        self._high_contrast_mode = enabled
        if enabled:
            # High contrast overrides
            high_contrast_styles = f"""
                /* High Contrast Mode */
                QWidget {{
                    background-color: {ThemeColors.PRIMARY_BG};
                    color: {ThemeColors.TEXT_PRIMARY};
                    border: 1px solid {ThemeColors.TEXT_PRIMARY};
                }}
                QPushButton {{
                    background-color: {ThemeColors.TEXT_PRIMARY};
                    color: {ThemeColors.PRIMARY_BG};
                    border: 2px solid {ThemeColors.TEXT_PRIMARY};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {ThemeColors.ACCENT};
                    border-color: {ThemeColors.ACCENT};
                }}
                QLabel {{
                    color: {ThemeColors.TEXT_PRIMARY};
                    font-weight: bold;
                }}
            """
            self.set_custom_style("/* High Contrast Mode */", high_contrast_styles)
        else:
            self.remove_custom_style("/* High Contrast Mode */")
        
        self.themeChanged.emit()
    
    def get_accessible_color_palette(self) -> list:
        """Get colorblind-safe color palette"""
        return [
            ThemeColors.ACCESSIBLE_BLUE,
            ThemeColors.ACCESSIBLE_ORANGE,
            ThemeColors.ACCESSIBLE_GREEN,
            ThemeColors.ACCESSIBLE_RED,
            ThemeColors.ACCESSIBLE_PURPLE,
            ThemeColors.ACCESSIBLE_BROWN,
            ThemeColors.ACCESSIBLE_PINK,
            ThemeColors.ACCESSIBLE_GRAY,
            ThemeColors.ACCESSIBLE_YELLOW,
            ThemeColors.ACCESSIBLE_LIGHT_BLUE
        ]
    
    def get_status_color(self, status: str, accessible: bool = None) -> str:
        """Get status color, optionally accessible version"""
        if accessible is None:
            accessible = self._accessibility_mode
        
        if accessible:
            status_map = {
                "success": ThemeColors.ACCESSIBLE_GREEN,
                "warning": ThemeColors.ACCESSIBLE_ORANGE,
                "error": ThemeColors.ACCESSIBLE_RED,
                "info": ThemeColors.ACCESSIBLE_BLUE
            }
        else:
            status_map = {
                "success": ThemeColors.SUCCESS,
                "warning": ThemeColors.WARNING,
                "error": ThemeColors.ERROR,
                "info": ThemeColors.INFO
            }
        
        return status_map.get(status, ThemeColors.INFO)
    
    def is_accessibility_mode(self) -> bool:
        """Check if accessibility mode is enabled"""
        return self._accessibility_mode
    
    def is_high_contrast_mode(self) -> bool:
        """Check if high contrast mode is enabled"""
        return self._high_contrast_mode


# Global theme manager instance
theme_manager = ThemeManager()


def apply_theme(app: QApplication):
    """Convenience function to apply theme to application"""
    theme_manager.initialize(app)


def get_theme_color(color_name: str) -> str:
    """Convenience function to get theme color"""
    return theme_manager.get_color(color_name)


def get_theme_spacing(spacing_name: str) -> int:
    """Convenience function to get theme spacing"""
    return theme_manager.get_spacing(spacing_name)