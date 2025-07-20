"""
Enhanced Typography System for DecentSampler Frontend
Implements a comprehensive typography hierarchy with consistent styling
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QLabel, QWidget
from utils.theme_manager import ThemeColors


class Typography:
    """Enhanced typography system with semantic font definitions"""
    
    # Font family stack (cross-platform compatible)
    FONT_FAMILY = "Arial, Helvetica, sans-serif"
    
    # Typography scale based on 1.25 ratio (Major Third)
    SCALE_RATIO = 1.25
    BASE_SIZE = 11  # Base font size
    
    # Calculated font sizes
    SIZE_DISPLAY = int(BASE_SIZE * (SCALE_RATIO ** 3))  # 21px - Major headings
    SIZE_H1 = int(BASE_SIZE * (SCALE_RATIO ** 2.5))    # 19px - Section headers
    SIZE_H2 = int(BASE_SIZE * (SCALE_RATIO ** 2))      # 17px - Panel headers
    SIZE_H3 = int(BASE_SIZE * (SCALE_RATIO ** 1.5))    # 15px - Subheaders
    SIZE_H4 = int(BASE_SIZE * SCALE_RATIO)             # 14px - Group headers
    SIZE_BODY = BASE_SIZE                              # 11px - Body text
    SIZE_SMALL = int(BASE_SIZE * 0.9)                  # 10px - Small text
    SIZE_CAPTION = int(BASE_SIZE * 0.8)                # 9px - Captions
    
    # Font weights
    WEIGHT_THIN = 100
    WEIGHT_LIGHT = 300
    WEIGHT_REGULAR = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700
    WEIGHT_HEAVY = 800
    
    # Line heights (as multipliers)
    LINE_HEIGHT_TIGHT = 1.2
    LINE_HEIGHT_NORMAL = 1.4
    LINE_HEIGHT_RELAXED = 1.6
    
    @classmethod
    def create_font(cls, size=None, weight=None, family=None):
        """Create a QFont with specified parameters"""
        font = QFont()
        font.setFamily(family or cls.FONT_FAMILY)
        font.setPixelSize(size or cls.SIZE_BODY)
        if weight:
            font.setWeight(weight)
        font.setHintingPreference(QFont.PreferDefaultHinting)
        return font


class TypographyStyles:
    """Pre-defined typography styles for common UI elements"""
    
    @staticmethod
    def display(text=""):
        """Large display text for major headings"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_DISPLAY, 
                Typography.WEIGHT_BOLD
            ),
            'color': ThemeColors.TEXT_PRIMARY,
            'line_height': Typography.LINE_HEIGHT_TIGHT
        }
    
    @staticmethod
    def heading_1(text=""):
        """Primary section headings"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_H1, 
                Typography.WEIGHT_SEMIBOLD
            ),
            'color': ThemeColors.TEXT_PRIMARY,
            'line_height': Typography.LINE_HEIGHT_TIGHT
        }
    
    @staticmethod
    def heading_2(text=""):
        """Panel and dialog headers"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_H2, 
                Typography.WEIGHT_SEMIBOLD
            ),
            'color': ThemeColors.TEXT_PRIMARY,
            'line_height': Typography.LINE_HEIGHT_NORMAL
        }
    
    @staticmethod
    def heading_3(text=""):
        """Subsection headers"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_H3, 
                Typography.WEIGHT_MEDIUM
            ),
            'color': ThemeColors.TEXT_PRIMARY,
            'line_height': Typography.LINE_HEIGHT_NORMAL
        }
    
    @staticmethod
    def heading_4(text=""):
        """Group headers and labels"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_H4, 
                Typography.WEIGHT_MEDIUM
            ),
            'color': ThemeColors.TEXT_SECONDARY,
            'line_height': Typography.LINE_HEIGHT_NORMAL
        }
    
    @staticmethod
    def body_text(text=""):
        """Standard body text"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_BODY, 
                Typography.WEIGHT_REGULAR
            ),
            'color': ThemeColors.TEXT_PRIMARY,
            'line_height': Typography.LINE_HEIGHT_NORMAL
        }
    
    @staticmethod
    def body_secondary(text=""):
        """Secondary body text"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_BODY, 
                Typography.WEIGHT_REGULAR
            ),
            'color': ThemeColors.TEXT_SECONDARY,
            'line_height': Typography.LINE_HEIGHT_NORMAL
        }
    
    @staticmethod
    def small_text(text=""):
        """Small supporting text"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_SMALL, 
                Typography.WEIGHT_REGULAR
            ),
            'color': ThemeColors.TEXT_SECONDARY,
            'line_height': Typography.LINE_HEIGHT_NORMAL
        }
    
    @staticmethod
    def caption(text=""):
        """Captions and helper text"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_CAPTION, 
                Typography.WEIGHT_REGULAR
            ),
            'color': ThemeColors.TEXT_DISABLED,
            'line_height': Typography.LINE_HEIGHT_RELAXED
        }
    
    @staticmethod
    def button_primary(text=""):
        """Primary button text"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_BODY, 
                Typography.WEIGHT_MEDIUM
            ),
            'color': ThemeColors.TEXT_PRIMARY,
            'line_height': Typography.LINE_HEIGHT_TIGHT
        }
    
    @staticmethod
    def button_secondary(text=""):
        """Secondary button text"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_SMALL, 
                Typography.WEIGHT_MEDIUM
            ),
            'color': ThemeColors.TEXT_SECONDARY,
            'line_height': Typography.LINE_HEIGHT_TIGHT
        }
    
    @staticmethod
    def control_label(text=""):
        """Labels for controls and inputs"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_SMALL, 
                Typography.WEIGHT_MEDIUM
            ),
            'color': ThemeColors.TEXT_PRIMARY,
            'line_height': Typography.LINE_HEIGHT_NORMAL
        }
    
    @staticmethod
    def status_text(text=""):
        """Status messages and notifications"""
        return {
            'font': Typography.create_font(
                Typography.SIZE_SMALL, 
                Typography.WEIGHT_REGULAR
            ),
            'color': ThemeColors.TEXT_SECONDARY,
            'line_height': Typography.LINE_HEIGHT_NORMAL
        }


class StyledLabel(QLabel):
    """Enhanced QLabel with typography style support"""
    
    def __init__(self, text="", style_func=None, parent=None):
        super().__init__(text, parent)
        self.style_func = style_func or TypographyStyles.body_text
        self.apply_style()
    
    def apply_style(self):
        """Apply the typography style to this label"""
        style = self.style_func(self.text())
        
        # Apply font
        self.setFont(style['font'])
        
        # Apply color via stylesheet
        self.setStyleSheet(f"""
            QLabel {{
                color: {style['color']};
                background-color: transparent;
            }}
        """)
        
        # Set text alignment
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    
    def setText(self, text):
        """Override setText to reapply style"""
        super().setText(text)
        self.apply_style()
    
    def set_style(self, style_func):
        """Change the typography style"""
        self.style_func = style_func
        self.apply_style()


class TypographyHelper:
    """Utility functions for typography management"""
    
    @staticmethod
    def get_text_width(text, font):
        """Calculate the width of text with given font"""
        metrics = QFontMetrics(font)
        return metrics.horizontalAdvance(text)
    
    @staticmethod
    def get_text_height(font):
        """Calculate the height of text with given font"""
        metrics = QFontMetrics(font)
        return metrics.height()
    
    @staticmethod
    def calculate_optimal_width(text, style_func):
        """Calculate optimal width for text with padding"""
        style = style_func(text)
        width = TypographyHelper.get_text_width(text, style['font'])
        return width + 16  # Add padding
    
    @staticmethod
    def calculate_optimal_height(style_func, line_count=1):
        """Calculate optimal height for text with line height"""
        style = style_func("")
        height = TypographyHelper.get_text_height(style['font'])
        line_height = style.get('line_height', Typography.LINE_HEIGHT_NORMAL)
        return int(height * line_height * line_count) + 8  # Add padding
    
    @staticmethod
    def apply_style_to_widget(widget, style_func, text=""):
        """Apply typography style to any widget"""
        style = style_func(text)
        
        if hasattr(widget, 'setFont'):
            widget.setFont(style['font'])
        
        if hasattr(widget, 'setStyleSheet'):
            widget.setStyleSheet(f"""
                {widget.__class__.__name__} {{
                    color: {style['color']};
                }}
            """)


# Convenient style functions for quick access
def create_display_label(text, parent=None):
    return StyledLabel(text, TypographyStyles.display, parent)

def create_h1_label(text, parent=None):
    return StyledLabel(text, TypographyStyles.heading_1, parent)

def create_h2_label(text, parent=None):
    return StyledLabel(text, TypographyStyles.heading_2, parent)

def create_h3_label(text, parent=None):
    return StyledLabel(text, TypographyStyles.heading_3, parent)

def create_body_label(text, parent=None):
    return StyledLabel(text, TypographyStyles.body_text, parent)

def create_small_label(text, parent=None):
    return StyledLabel(text, TypographyStyles.small_text, parent)

def create_caption_label(text, parent=None):
    return StyledLabel(text, TypographyStyles.caption, parent)