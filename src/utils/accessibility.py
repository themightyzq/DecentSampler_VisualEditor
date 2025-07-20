"""
Accessibility module for colorblind-friendly UI enhancements
Provides patterns, textures, symbols, and accessibility utilities
"""

from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QPolygon, QPainterPath
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from enum import Enum
from typing import Dict, List, Tuple, Optional
import math


class ColorVisionType(Enum):
    """Types of color vision deficiency"""
    NORMAL = "normal"
    PROTANOPIA = "protanopia"  # Red-blind
    DEUTERANOPIA = "deuteranopia"  # Green-blind
    TRITANOPIA = "tritanopia"  # Blue-blind
    PROTANOMALY = "protanomaly"  # Red-weak
    DEUTERANOMALY = "deuteranomaly"  # Green-weak
    TRITANOMALY = "tritanomaly"  # Blue-weak


class PatternType(Enum):
    """Visual pattern types for colorblind accessibility"""
    SOLID = "solid"
    DOTS = "dots"
    LINES_HORIZONTAL = "lines_horizontal"
    LINES_VERTICAL = "lines_vertical"
    LINES_DIAGONAL = "lines_diagonal"
    CROSS_HATCH = "cross_hatch"
    ZIGZAG = "zigzag"
    CHECKERBOARD = "checkerboard"
    WAVES = "waves"
    TRIANGLES = "triangles"
    CIRCLES = "circles"
    GRID = "grid"


class AccessibilitySymbol(Enum):
    """Symbols for status and categorization"""
    # Status symbols
    SUCCESS = "✓"
    WARNING = "⚠"
    ERROR = "✗"
    INFO = "ℹ"
    
    # Musical symbols  
    NOTE = "♪"
    SHARP = "♯"
    FLAT = "♭"
    
    # Directional symbols
    UP_ARROW = "↑"
    DOWN_ARROW = "↓"
    LEFT_ARROW = "←"
    RIGHT_ARROW = "→"
    UP_DOUBLE = "⇈"
    DOWN_DOUBLE = "⇊"
    
    # Shape symbols
    CIRCLE = "●"
    SQUARE = "■"
    TRIANGLE = "▲"
    DIAMOND = "♦"
    STAR = "★"
    HEART = "♥"
    
    # Velocity/intensity symbols
    SOFT = "pp"
    MEDIUM = "mf"
    LOUD = "ff"
    
    # File/data symbols
    FOLDER = "📁"
    FILE = "📄"
    AUDIO = "🔊"
    PLAY = "▶"
    PAUSE = "⏸"
    STOP = "⏹"


class AccessibilityColors:
    """Colorblind-friendly color palette"""
    
    # High contrast pairs
    BLACK = "#000000"
    WHITE = "#FFFFFF"
    
    # Colorblind-safe palette (based on Paul Tol's schemes)
    BLUE = "#0173B2"        # Safe blue
    ORANGE = "#DE8F05"      # Safe orange  
    GREEN = "#029E73"       # Safe green
    RED = "#D55E00"         # Safe red
    PURPLE = "#CC78BC"      # Safe purple
    BROWN = "#CA9161"       # Safe brown
    PINK = "#FBAFE4"        # Safe pink
    GRAY = "#949494"        # Safe gray
    YELLOW = "#ECE133"      # Safe yellow
    LIGHT_BLUE = "#56B4E9"  # Safe light blue
    
    # Pattern-based combinations (color + pattern for redundancy)
    MAPPING_COLORS = [
        (BLUE, PatternType.SOLID),
        (ORANGE, PatternType.DOTS),
        (GREEN, PatternType.LINES_HORIZONTAL),
        (RED, PatternType.LINES_VERTICAL),
        (PURPLE, PatternType.LINES_DIAGONAL),
        (BROWN, PatternType.CROSS_HATCH),
        (PINK, PatternType.ZIGZAG),
        (GRAY, PatternType.CHECKERBOARD),
        (YELLOW, PatternType.WAVES),
        (LIGHT_BLUE, PatternType.TRIANGLES)
    ]
    
    # Status colors with high contrast
    STATUS_SUCCESS = GREEN
    STATUS_WARNING = ORANGE
    STATUS_ERROR = RED
    STATUS_INFO = BLUE


class PatternGenerator:
    """Generates accessible visual patterns for UI elements"""
    
    @staticmethod
    def create_pattern_brush(pattern_type: PatternType, color: QColor, 
                           pattern_size: int = 8, density: float = 0.5) -> QBrush:
        """Create a pattern brush with specified parameters"""
        pixmap = QPixmap(pattern_size, pattern_size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set pen and brush colors
        pen_color = QColor(color)
        pen_color.setAlpha(255)
        painter.setPen(QPen(pen_color, 1))
        painter.setBrush(QBrush(pen_color))
        
        # Generate pattern based on type
        if pattern_type == PatternType.DOTS:
            PatternGenerator._draw_dots(painter, pattern_size, density)
        elif pattern_type == PatternType.LINES_HORIZONTAL:
            PatternGenerator._draw_horizontal_lines(painter, pattern_size, density)
        elif pattern_type == PatternType.LINES_VERTICAL:
            PatternGenerator._draw_vertical_lines(painter, pattern_size, density)
        elif pattern_type == PatternType.LINES_DIAGONAL:
            PatternGenerator._draw_diagonal_lines(painter, pattern_size, density)
        elif pattern_type == PatternType.CROSS_HATCH:
            PatternGenerator._draw_cross_hatch(painter, pattern_size, density)
        elif pattern_type == PatternType.ZIGZAG:
            PatternGenerator._draw_zigzag(painter, pattern_size, density)
        elif pattern_type == PatternType.CHECKERBOARD:
            PatternGenerator._draw_checkerboard(painter, pattern_size)
        elif pattern_type == PatternType.WAVES:
            PatternGenerator._draw_waves(painter, pattern_size, density)
        elif pattern_type == PatternType.TRIANGLES:
            PatternGenerator._draw_triangles(painter, pattern_size, density)
        elif pattern_type == PatternType.CIRCLES:
            PatternGenerator._draw_circles(painter, pattern_size, density)
        elif pattern_type == PatternType.GRID:
            PatternGenerator._draw_grid(painter, pattern_size, density)
        
        painter.end()
        return QBrush(pixmap)
    
    @staticmethod
    def _draw_dots(painter: QPainter, size: int, density: float):
        """Draw dot pattern"""
        dot_size = max(1, int(size * density * 0.3))
        spacing = max(2, int(size * 0.5))
        for x in range(0, size, spacing):
            for y in range(0, size, spacing):
                painter.drawEllipse(x, y, dot_size, dot_size)
    
    @staticmethod
    def _draw_horizontal_lines(painter: QPainter, size: int, density: float):
        """Draw horizontal line pattern"""
        line_spacing = max(2, int(size * (1 - density) * 0.5))
        for y in range(0, size, line_spacing):
            painter.drawLine(0, y, size, y)
    
    @staticmethod
    def _draw_vertical_lines(painter: QPainter, size: int, density: float):
        """Draw vertical line pattern"""
        line_spacing = max(2, int(size * (1 - density) * 0.5))
        for x in range(0, size, line_spacing):
            painter.drawLine(x, 0, x, size)
    
    @staticmethod
    def _draw_diagonal_lines(painter: QPainter, size: int, density: float):
        """Draw diagonal line pattern"""
        line_spacing = max(2, int(size * (1 - density) * 0.7))
        # Draw diagonal lines from top-left to bottom-right
        for offset in range(-size, size * 2, line_spacing):
            painter.drawLine(offset, 0, offset + size, size)
    
    @staticmethod
    def _draw_cross_hatch(painter: QPainter, size: int, density: float):
        """Draw cross-hatch pattern"""
        line_spacing = max(2, int(size * (1 - density) * 0.5))
        # Horizontal lines
        for y in range(0, size, line_spacing):
            painter.drawLine(0, y, size, y)
        # Vertical lines
        for x in range(0, size, line_spacing):
            painter.drawLine(x, 0, x, size)
    
    @staticmethod
    def _draw_zigzag(painter: QPainter, size: int, density: float):
        """Draw zigzag pattern"""
        step = max(2, int(size * 0.25))
        amplitude = int(size * density * 0.3)
        
        path = QPainterPath()
        for y in range(0, size, step * 2):
            path.moveTo(0, y)
            x = 0
            while x < size:
                path.lineTo(x + step, y + amplitude)
                path.lineTo(x + step * 2, y)
                x += step * 2
        
        painter.drawPath(path)
    
    @staticmethod
    def _draw_checkerboard(painter: QPainter, size: int):
        """Draw checkerboard pattern"""
        square_size = max(2, size // 4)
        for x in range(0, size, square_size):
            for y in range(0, size, square_size):
                if (x // square_size + y // square_size) % 2 == 0:
                    painter.fillRect(x, y, square_size, square_size, painter.brush())
    
    @staticmethod
    def _draw_waves(painter: QPainter, size: int, density: float):
        """Draw wave pattern"""
        wavelength = max(4, int(size * 0.5))
        amplitude = int(size * density * 0.3)
        
        path = QPainterPath()
        for y in range(0, size, wavelength):
            path.moveTo(0, y + amplitude)
            for x in range(0, size, 2):
                wave_y = y + amplitude * math.sin(2 * math.pi * x / wavelength)
                path.lineTo(x, wave_y)
        
        painter.drawPath(path)
    
    @staticmethod
    def _draw_triangles(painter: QPainter, size: int, density: float):
        """Draw triangle pattern"""
        triangle_size = max(3, int(size * density * 0.4))
        spacing = max(4, int(size * 0.4))
        
        for x in range(0, size, spacing):
            for y in range(0, size, spacing):
                triangle = QPolygon([
                    QPoint(x + triangle_size // 2, y),
                    QPoint(x, y + triangle_size),
                    QPoint(x + triangle_size, y + triangle_size)
                ])
                painter.drawPolygon(triangle)
    
    @staticmethod
    def _draw_circles(painter: QPainter, size: int, density: float):
        """Draw circle pattern"""
        circle_size = max(2, int(size * density * 0.4))
        spacing = max(3, int(size * 0.4))
        
        for x in range(0, size, spacing):
            for y in range(0, size, spacing):
                painter.drawEllipse(x, y, circle_size, circle_size)
    
    @staticmethod
    def _draw_grid(painter: QPainter, size: int, density: float):
        """Draw grid pattern"""
        grid_spacing = max(2, int(size * (1 - density) * 0.3))
        # Draw vertical lines
        for x in range(0, size, grid_spacing):
            painter.drawLine(x, 0, x, size)
        # Draw horizontal lines
        for y in range(0, size, grid_spacing):
            painter.drawLine(0, y, size, y)


class AccessibilityIndicator:
    """Creates accessible indicators combining color, pattern, and symbols"""
    
    def __init__(self, colorblind_mode: bool = False, high_contrast: bool = False):
        self.colorblind_mode = colorblind_mode
        self.high_contrast = high_contrast
        self._pattern_cache = {}
    
    def create_status_indicator(self, status: str, size: QSize = QSize(16, 16)) -> QPixmap:
        """Create a status indicator with symbol and color/pattern"""
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get status configuration
        symbol, color, pattern = self._get_status_config(status)
        
        # Draw background with pattern if in colorblind mode
        if self.colorblind_mode and pattern != PatternType.SOLID:
            pattern_brush = PatternGenerator.create_pattern_brush(
                pattern, QColor(color), 8, 0.6
            )
            painter.fillRect(pixmap.rect(), pattern_brush)
        else:
            # Solid color background
            painter.fillRect(pixmap.rect(), QColor(color))
        
        # Draw symbol
        painter.setPen(QColor(AccessibilityColors.WHITE if not self.high_contrast 
                            else AccessibilityColors.BLACK))
        painter.setFont(painter.font())
        painter.drawText(pixmap.rect(), Qt.AlignCenter, symbol)
        
        painter.end()
        return pixmap
    
    def create_mapping_indicator(self, mapping_index: int, 
                               size: QSize = QSize(32, 16)) -> Tuple[QColor, QBrush, str]:
        """Create mapping indicator with color, pattern, and symbol"""
        # Get color and pattern from palette
        color_str, pattern_type = AccessibilityColors.MAPPING_COLORS[
            mapping_index % len(AccessibilityColors.MAPPING_COLORS)
        ]
        
        color = QColor(color_str)
        
        # Create pattern brush if in colorblind mode
        if self.colorblind_mode:
            brush = PatternGenerator.create_pattern_brush(pattern_type, color, 12, 0.7)
        else:
            brush = QBrush(color)
        
        # Get symbol for mapping
        symbols = ["●", "■", "▲", "♦", "★", "♥", "◆", "▼", "◄", "►"]
        symbol = symbols[mapping_index % len(symbols)]
        
        return color, brush, symbol
    
    def create_velocity_indicator(self, velocity_layer: int, 
                                size: QSize = QSize(16, 8)) -> QPixmap:
        """Create velocity layer indicator"""
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Velocity-specific patterns and symbols
        velocity_configs = [
            (AccessibilityColors.BLUE, PatternType.DOTS, "pp"),      # Soft
            (AccessibilityColors.GREEN, PatternType.LINES_HORIZONTAL, "mp"), # Medium-soft
            (AccessibilityColors.ORANGE, PatternType.LINES_DIAGONAL, "mf"),  # Medium-loud
            (AccessibilityColors.RED, PatternType.CROSS_HATCH, "ff")         # Loud
        ]
        
        config_index = min(velocity_layer, len(velocity_configs) - 1)
        color_str, pattern, symbol = velocity_configs[config_index]
        
        color = QColor(color_str)
        
        # Draw pattern background if in colorblind mode
        if self.colorblind_mode:
            pattern_brush = PatternGenerator.create_pattern_brush(pattern, color, 6, 0.8)
            painter.fillRect(pixmap.rect(), pattern_brush)
        else:
            painter.fillRect(pixmap.rect(), color)
        
        # Draw velocity symbol if space allows
        if size.width() >= 16:
            painter.setPen(QColor(AccessibilityColors.WHITE))
            font = painter.font()
            font.setPixelSize(8)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, symbol)
        
        painter.end()
        return pixmap
    
    def create_transposition_indicator(self, semitones: int, 
                                     size: QSize = QSize(12, 12)) -> QPixmap:
        """Create transposition direction indicator"""
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Determine symbol and color based on transposition
        if semitones == 0:
            symbol = "="
            color = AccessibilityColors.GRAY
        elif semitones > 0:
            symbol = "↑" if abs(semitones) <= 12 else "⇈"
            color = AccessibilityColors.GREEN
        else:
            symbol = "↓" if abs(semitones) <= 12 else "⇊"
            color = AccessibilityColors.RED
        
        # Draw background
        if self.high_contrast:
            painter.fillRect(pixmap.rect(), QColor(AccessibilityColors.WHITE))
            painter.setPen(QColor(color))
        else:
            painter.fillRect(pixmap.rect(), QColor(color))
            painter.setPen(QColor(AccessibilityColors.WHITE))
        
        # Draw symbol
        font = painter.font()
        font.setPixelSize(size.height() - 2)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, symbol)
        
        painter.end()
        return pixmap
    
    def _get_status_config(self, status: str) -> Tuple[str, str, PatternType]:
        """Get symbol, color, and pattern for status"""
        status_configs = {
            "success": (AccessibilitySymbol.SUCCESS.value, 
                       AccessibilityColors.STATUS_SUCCESS, PatternType.SOLID),
            "warning": (AccessibilitySymbol.WARNING.value, 
                       AccessibilityColors.STATUS_WARNING, PatternType.LINES_DIAGONAL),
            "error": (AccessibilitySymbol.ERROR.value, 
                     AccessibilityColors.STATUS_ERROR, PatternType.CROSS_HATCH),
            "info": (AccessibilitySymbol.INFO.value, 
                    AccessibilityColors.STATUS_INFO, PatternType.DOTS),
            "ready": (AccessibilitySymbol.PLAY.value, 
                     AccessibilityColors.GREEN, PatternType.SOLID),
            "playing": (AccessibilitySymbol.PAUSE.value, 
                       AccessibilityColors.BLUE, PatternType.WAVES),
            "stopped": (AccessibilitySymbol.STOP.value, 
                       AccessibilityColors.GRAY, PatternType.SOLID)
        }
        
        return status_configs.get(status, 
                                (AccessibilitySymbol.INFO.value, 
                                 AccessibilityColors.GRAY, PatternType.SOLID))


class ColorVisionSimulator:
    """Simulates different types of color vision deficiency for testing"""
    
    # Color transformation matrices for different types of color blindness
    MATRICES = {
        ColorVisionType.PROTANOPIA: [
            [0.567, 0.433, 0.000],
            [0.558, 0.442, 0.000],
            [0.000, 0.242, 0.758]
        ],
        ColorVisionType.DEUTERANOPIA: [
            [0.625, 0.375, 0.000],
            [0.700, 0.300, 0.000],
            [0.000, 0.300, 0.700]
        ],
        ColorVisionType.TRITANOPIA: [
            [0.950, 0.050, 0.000],
            [0.000, 0.433, 0.567],
            [0.000, 0.475, 0.525]
        ]
    }
    
    @staticmethod
    def simulate_color_blindness(color: QColor, 
                               vision_type: ColorVisionType) -> QColor:
        """Simulate how a color appears to someone with color vision deficiency"""
        if vision_type == ColorVisionType.NORMAL:
            return color
        
        if vision_type not in ColorVisionSimulator.MATRICES:
            return color
        
        # Convert to RGB values (0-1)
        r, g, b = color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0
        
        # Apply transformation matrix
        matrix = ColorVisionSimulator.MATRICES[vision_type]
        new_r = matrix[0][0] * r + matrix[0][1] * g + matrix[0][2] * b
        new_g = matrix[1][0] * r + matrix[1][1] * g + matrix[1][2] * b
        new_b = matrix[2][0] * r + matrix[2][1] * g + matrix[2][2] * b
        
        # Clamp values and convert back to 0-255
        new_r = max(0, min(1, new_r)) * 255
        new_g = max(0, min(1, new_g)) * 255
        new_b = max(0, min(1, new_b)) * 255
        
        return QColor(int(new_r), int(new_g), int(new_b))
    
    @staticmethod
    def test_color_accessibility(color1: QColor, color2: QColor) -> Dict[str, bool]:
        """Test if two colors are distinguishable across different color vision types"""
        results = {}
        
        for vision_type in ColorVisionType:
            sim_color1 = ColorVisionSimulator.simulate_color_blindness(color1, vision_type)
            sim_color2 = ColorVisionSimulator.simulate_color_blindness(color2, vision_type)
            
            # Calculate color difference (simple Euclidean distance in RGB space)
            diff = math.sqrt(
                (sim_color1.red() - sim_color2.red()) ** 2 +
                (sim_color1.green() - sim_color2.green()) ** 2 +
                (sim_color1.blue() - sim_color2.blue()) ** 2
            )
            
            # Consider colors distinguishable if difference > threshold
            threshold = 50  # Adjust based on requirements
            results[vision_type.value] = diff > threshold
        
        return results


class AccessibilitySettings:
    """Manages accessibility preferences"""
    
    def __init__(self):
        self.colorblind_mode = False
        self.high_contrast = False
        self.use_patterns = True
        self.use_symbols = True
        self.pattern_density = 0.7
        self.symbol_size = 16
        self.vision_type = ColorVisionType.NORMAL
        self.status_indicators_enhanced = True
    
    def enable_colorblind_mode(self, enabled: bool = True):
        """Enable or disable colorblind-friendly mode"""
        self.colorblind_mode = enabled
        if enabled:
            self.use_patterns = True
            self.use_symbols = True
    
    def enable_high_contrast(self, enabled: bool = True):
        """Enable or disable high contrast mode"""
        self.high_contrast = enabled
    
    def set_vision_type(self, vision_type: ColorVisionType):
        """Set the type of color vision deficiency to accommodate"""
        self.vision_type = vision_type
        if vision_type != ColorVisionType.NORMAL:
            self.enable_colorblind_mode(True)
    
    def get_indicator_factory(self) -> AccessibilityIndicator:
        """Get configured accessibility indicator factory"""
        return AccessibilityIndicator(
            colorblind_mode=self.colorblind_mode,
            high_contrast=self.high_contrast
        )


# Global accessibility settings instance
accessibility_settings = AccessibilitySettings()


# Convenience functions
def get_accessible_color(color_name: str) -> str:
    """Get accessible color from palette"""
    return getattr(AccessibilityColors, color_name.upper(), AccessibilityColors.GRAY)


def create_accessible_brush(color: QColor, pattern: PatternType = PatternType.SOLID) -> QBrush:
    """Create accessible brush with optional pattern"""
    if accessibility_settings.use_patterns and pattern != PatternType.SOLID:
        return PatternGenerator.create_pattern_brush(pattern, color)
    return QBrush(color)


def get_status_symbol(status: str) -> str:
    """Get symbol for status type"""
    symbol_map = {
        "success": AccessibilitySymbol.SUCCESS.value,
        "warning": AccessibilitySymbol.WARNING.value,
        "error": AccessibilitySymbol.ERROR.value,
        "info": AccessibilitySymbol.INFO.value,
        "play": AccessibilitySymbol.PLAY.value,
        "pause": AccessibilitySymbol.PAUSE.value,
        "stop": AccessibilitySymbol.STOP.value
    }
    return symbol_map.get(status, AccessibilitySymbol.INFO.value)