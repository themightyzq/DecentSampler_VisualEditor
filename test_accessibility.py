#!/usr/bin/env python3
"""
Accessibility Testing Script for DecentSampler Frontend
Tests colorblind-friendly features and accessibility enhancements
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QPushButton, QTabWidget, QGroupBox, QGridLayout,
    QCheckBox, QComboBox, QMessageBox, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QPixmap, QIcon

from utils.accessibility import (
    AccessibilityIndicator, AccessibilityColors, PatternType, ColorVisionType,
    ColorVisionSimulator, accessibility_settings, AccessibilitySettings
)
from utils.theme_manager import theme_manager, ThemeColors
from panels.piano_keyboard import PianoKeyboardWidget, KeyboardLegendWidget
from widgets.audio_preview import AudioPreviewWidget
from views.panels.accessibility_panel import AccessibilityPanel


class ColorVisionDemoWidget(QWidget):
    """Demonstrates how colors appear with different types of color vision deficiency"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Color Vision Simulation")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet(f"color: {ThemeColors.ACCENT}; padding: 8px;")
        layout.addWidget(header)
        
        # Vision type selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Simulate vision type:"))
        
        self.vision_combo = QComboBox()
        vision_types = [
            ("Normal Vision", ColorVisionType.NORMAL),
            ("Protanopia (Red-blind)", ColorVisionType.PROTANOPIA),
            ("Deuteranopia (Green-blind)", ColorVisionType.DEUTERANOPIA),
            ("Tritanopia (Blue-blind)", ColorVisionType.TRITANOPIA),
            ("Protanomaly (Red-weak)", ColorVisionType.PROTANOMALY),
            ("Deuteranomaly (Green-weak)", ColorVisionType.DEUTERANOMALY),
            ("Tritanomaly (Blue-weak)", ColorVisionType.TRITANOMALY)
        ]
        
        for name, vision_type in vision_types:
            self.vision_combo.addItem(name, vision_type)
        
        self.vision_combo.currentIndexChanged.connect(self.update_simulation)
        selector_layout.addWidget(self.vision_combo)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)
        
        # Color demonstration grid
        self.color_grid = self.create_color_grid()
        layout.addWidget(self.color_grid)
        
        self.setLayout(layout)
    
    def create_color_grid(self):
        """Create grid showing original and simulated colors"""
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        grid_layout = QGridLayout()
        
        # Test colors (problematic pairs for colorblind users)
        test_colors = [
            ("Red", QColor(AccessibilityColors.RED)),
            ("Green", QColor(AccessibilityColors.GREEN)),
            ("Blue", QColor(AccessibilityColors.BLUE)),
            ("Orange", QColor(AccessibilityColors.ORANGE)),
            ("Purple", QColor(AccessibilityColors.PURPLE)),
            ("Yellow", QColor(AccessibilityColors.YELLOW)),
            ("Brown", QColor(AccessibilityColors.BROWN)),
            ("Pink", QColor(AccessibilityColors.PINK)),
        ]
        
        # Headers
        grid_layout.addWidget(QLabel("<b>Color</b>"), 0, 0)
        grid_layout.addWidget(QLabel("<b>Original</b>"), 0, 1)
        grid_layout.addWidget(QLabel("<b>Simulated</b>"), 0, 2)
        grid_layout.addWidget(QLabel("<b>Accessible Alt</b>"), 0, 3)
        
        self.color_widgets = []
        for i, (name, color) in enumerate(test_colors, 1):
            # Color name
            name_label = QLabel(name)
            grid_layout.addWidget(name_label, i, 0)
            
            # Original color
            original_widget = self.create_color_swatch(color)
            grid_layout.addWidget(original_widget, i, 1)
            
            # Simulated color (will be updated)
            simulated_widget = self.create_color_swatch(color)
            grid_layout.addWidget(simulated_widget, i, 2)
            
            # Accessible alternative (with pattern)
            accessible_widget = self.create_accessible_swatch(i-1, color)
            grid_layout.addWidget(accessible_widget, i, 3)
            
            self.color_widgets.append((original_widget, simulated_widget, accessible_widget))
        
        scroll_widget.setLayout(grid_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(400)
        
        return scroll_area
    
    def create_color_swatch(self, color):
        """Create a simple color swatch widget"""
        widget = QFrame()
        widget.setFixedSize(60, 40)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: rgb({color.red()}, {color.green()}, {color.blue()});
                border: 1px solid #666;
                border-radius: 4px;
            }}
        """)
        widget.setToolTip(f"RGB: {color.red()}, {color.green()}, {color.blue()}")
        return widget
    
    def create_accessible_swatch(self, index, color):
        """Create an accessible swatch with pattern"""
        widget = QLabel()
        widget.setFixedSize(60, 40)
        
        # Create pixmap with pattern
        pixmap = QPixmap(60, 40)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        
        # Get accessibility indicator
        indicator = AccessibilityIndicator(colorblind_mode=True)
        color_acc, brush, symbol = indicator.create_mapping_indicator(index)
        
        # Draw pattern background
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRect(pixmap.rect())
        
        # Draw symbol
        if symbol:
            painter.setPen(QColor(AccessibilityColors.WHITE))
            font = painter.font()
            font.setPixelSize(16)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, symbol)
        
        painter.end()
        
        widget.setPixmap(pixmap)
        widget.setToolTip(f"Accessible version with pattern and symbol: {symbol}")
        return widget
    
    def update_simulation(self):
        """Update color simulation based on selected vision type"""
        vision_type = self.vision_combo.currentData()
        
        test_colors = [
            QColor(AccessibilityColors.RED),
            QColor(AccessibilityColors.GREEN),
            QColor(AccessibilityColors.BLUE),
            QColor(AccessibilityColors.ORANGE),
            QColor(AccessibilityColors.PURPLE),
            QColor(AccessibilityColors.YELLOW),
            QColor(AccessibilityColors.BROWN),
            QColor(AccessibilityColors.PINK),
        ]
        
        for i, (original_widget, simulated_widget, accessible_widget) in enumerate(self.color_widgets):
            if i < len(test_colors):
                original_color = test_colors[i]
                simulated_color = ColorVisionSimulator.simulate_color_blindness(original_color, vision_type)
                
                # Update simulated color widget
                simulated_widget.setStyleSheet(f"""
                    QFrame {{
                        background-color: rgb({simulated_color.red()}, {simulated_color.green()}, {simulated_color.blue()});
                        border: 1px solid #666;
                        border-radius: 4px;
                    }}
                """)
                simulated_widget.setToolTip(
                    f"Original RGB: {original_color.red()}, {original_color.green()}, {original_color.blue()}\n"
                    f"Simulated RGB: {simulated_color.red()}, {simulated_color.green()}, {simulated_color.blue()}"
                )


class PatternDemoWidget(QWidget):
    """Demonstrates different visual patterns for accessibility"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Visual Pattern Examples")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet(f"color: {ThemeColors.ACCENT}; padding: 8px;")
        layout.addWidget(header)
        
        # Description
        desc = QLabel(
            "These patterns help distinguish elements when colors alone are not sufficient. "
            "Each pattern is paired with a unique symbol for maximum accessibility."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY}; padding: 8px;")
        layout.addWidget(desc)
        
        # Pattern grid
        patterns_widget = self.create_pattern_grid()
        layout.addWidget(patterns_widget)
        
        self.setLayout(layout)
    
    def create_pattern_grid(self):
        """Create grid showing different patterns"""
        widget = QWidget()
        grid_layout = QGridLayout()
        
        patterns = [
            (PatternType.SOLID, "Solid", "●"),
            (PatternType.DOTS, "Dots", "■"),
            (PatternType.LINES_HORIZONTAL, "Horizontal Lines", "▲"),
            (PatternType.LINES_VERTICAL, "Vertical Lines", "♦"),
            (PatternType.LINES_DIAGONAL, "Diagonal Lines", "★"),
            (PatternType.CROSS_HATCH, "Cross Hatch", "♥"),
            (PatternType.ZIGZAG, "Zigzag", "◆"),
            (PatternType.CHECKERBOARD, "Checkerboard", "▼"),
            (PatternType.WAVES, "Waves", "◄"),
            (PatternType.TRIANGLES, "Triangles", "►")
        ]
        
        # Headers
        grid_layout.addWidget(QLabel("<b>Pattern Type</b>"), 0, 0)
        grid_layout.addWidget(QLabel("<b>Visual</b>"), 0, 1)
        grid_layout.addWidget(QLabel("<b>Symbol</b>"), 0, 2)
        
        indicator = AccessibilityIndicator(colorblind_mode=True)
        
        for i, (pattern_type, name, symbol) in enumerate(patterns, 1):
            # Pattern name
            name_label = QLabel(name)
            grid_layout.addWidget(name_label, i, 0)
            
            # Pattern visual
            pattern_widget = QLabel()
            pattern_widget.setFixedSize(80, 30)
            
            # Create pattern pixmap
            pixmap = QPixmap(80, 30)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            color, brush, _ = indicator.create_mapping_indicator(i-1)
            painter.setBrush(brush)
            painter.setPen(Qt.NoPen)
            painter.drawRect(pixmap.rect())
            painter.end()
            
            pattern_widget.setPixmap(pixmap)
            grid_layout.addWidget(pattern_widget, i, 1)
            
            # Symbol
            symbol_label = QLabel(symbol)
            symbol_label.setFont(QFont("Arial", 16, QFont.Bold))
            symbol_label.setAlignment(Qt.AlignCenter)
            symbol_label.setStyleSheet(f"color: {ThemeColors.ACCENT};")
            grid_layout.addWidget(symbol_label, i, 2)
        
        widget.setLayout(grid_layout)
        return widget


class AccessibilityTestWindow(QMainWindow):
    """Main window for testing accessibility features"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setWindowTitle("DecentSampler Accessibility Testing")
        self.setGeometry(100, 100, 1000, 700)
        
        # Apply dark theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {ThemeColors.PRIMARY_BG};
                color: {ThemeColors.TEXT_PRIMARY};
            }}
            QTabWidget::pane {{
                border: 1px solid {ThemeColors.BORDER};
                background-color: {ThemeColors.SECONDARY_BG};
            }}
            QTabBar::tab {{
                background-color: {ThemeColors.PANEL_BG};
                color: {ThemeColors.TEXT_SECONDARY};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {ThemeColors.ACCENT};
                color: {ThemeColors.TEXT_PRIMARY};
            }}
        """)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🔧 DecentSampler Accessibility Testing Suite")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet(f"color: {ThemeColors.ACCENT}; padding: 16px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.toggle_accessibility_btn = QPushButton("Toggle Accessibility Mode")
        self.toggle_accessibility_btn.clicked.connect(self.toggle_accessibility_mode)
        self.toggle_accessibility_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeColors.ACCENT};
                color: {ThemeColors.TEXT_PRIMARY};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ThemeColors.ACCENT_HOVER};
            }}
        """)
        control_layout.addWidget(self.toggle_accessibility_btn)
        
        self.show_settings_btn = QPushButton("Accessibility Settings")
        self.show_settings_btn.clicked.connect(self.show_accessibility_settings)
        control_layout.addWidget(self.show_settings_btn)
        
        control_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("Status: Normal mode")
        self.status_label.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY}; padding: 8px;")
        control_layout.addWidget(self.status_label)
        
        layout.addLayout(control_layout)
        
        # Tab widget for different test areas
        self.tab_widget = QTabWidget()
        
        # Piano keyboard test
        keyboard_tab = self.create_keyboard_test_tab()
        self.tab_widget.addTab(keyboard_tab, "Piano Keyboard")
        
        # Color vision test
        color_vision_tab = ColorVisionDemoWidget()
        self.tab_widget.addTab(color_vision_tab, "Color Vision Simulation")
        
        # Pattern demo
        pattern_tab = PatternDemoWidget()
        self.tab_widget.addTab(pattern_tab, "Visual Patterns")
        
        # Audio preview test
        audio_tab = self.create_audio_test_tab()
        self.tab_widget.addTab(audio_tab, "Audio Preview")
        
        # Settings panel
        settings_tab = AccessibilityPanel()
        settings_tab.settingsChanged.connect(self.on_settings_changed)
        self.tab_widget.addTab(settings_tab, "Settings Panel")
        
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)
        
        # Initialize components
        self.update_status()
    
    def create_keyboard_test_tab(self):
        """Create piano keyboard test tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "This piano keyboard demonstrates colorblind-friendly sample mapping visualization. "
            "Toggle accessibility mode to see patterns, symbols, and enhanced indicators."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY}; padding: 8px; background-color: {ThemeColors.PANEL_BG}; border-radius: 4px;")
        layout.addWidget(instructions)
        
        # Piano keyboard
        self.piano_keyboard = PianoKeyboardWidget()
        
        # Add some test mappings
        self.create_test_mappings()
        
        layout.addWidget(self.piano_keyboard)
        
        # Legend
        self.legend_widget = KeyboardLegendWidget()
        layout.addWidget(self.legend_widget)
        
        widget.setLayout(layout)
        return widget
    
    def create_audio_test_tab(self):
        """Create audio preview test tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Audio preview widget with accessibility enhancements. "
            "Status indicators include symbols in addition to colors."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY}; padding: 8px; background-color: {ThemeColors.PANEL_BG}; border-radius: 4px;")
        layout.addWidget(instructions)
        
        # Audio preview
        self.audio_preview = AudioPreviewWidget()
        layout.addWidget(self.audio_preview)
        
        # Test buttons
        test_layout = QHBoxLayout()
        
        load_test_btn = QPushButton("Simulate File Load")
        load_test_btn.clicked.connect(self.simulate_audio_load)
        test_layout.addWidget(load_test_btn)
        
        error_test_btn = QPushButton("Simulate Error")
        error_test_btn.clicked.connect(self.simulate_audio_error)
        test_layout.addWidget(error_test_btn)
        
        test_layout.addStretch()
        layout.addLayout(test_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_test_mappings(self):
        """Create test sample mappings for the keyboard"""
        # Simulate some sample mappings
        test_mappings = [
            {"path": "samples/piano_c4.wav", "lo": 60, "hi": 67, "root": 60},
            {"path": "samples/piano_c5.wav", "lo": 68, "hi": 75, "root": 72},
            {"path": "samples/strings_g3.wav", "lo": 55, "hi": 59, "root": 55},
            {"path": "samples/bass_e2.wav", "lo": 40, "hi": 54, "root": 40},
        ]
        
        # Update legend
        legend_items = []
        for i, mapping in enumerate(test_mappings):
            lo_name = self.piano_keyboard.midi_note_name(mapping["lo"])
            hi_name = self.piano_keyboard.midi_note_name(mapping["hi"])
            root_name = self.piano_keyboard.midi_note_name(mapping["root"])
            
            legend_item = {
                'name': os.path.splitext(os.path.basename(mapping["path"]))[0],
                'range': f"{lo_name} - {hi_name}",
                'root': root_name,
                'color': self.piano_keyboard._get_mapping_color(i),
                'path': mapping["path"]
            }
            legend_items.append(legend_item)
        
        self.legend_widget.update_legend(legend_items)
        
        # Store mappings in keyboard (simplified for testing)
        if hasattr(self.piano_keyboard, 'test_mappings'):
            self.piano_keyboard.test_mappings = test_mappings
        
        # Force repaint
        self.piano_keyboard.update()
    
    def simulate_audio_load(self):
        """Simulate loading an audio file"""
        # This would normally load a real file
        # For testing, we'll just update the display
        self.audio_preview.file_label.setText("🎵 test_sample.wav")
        
        if self.audio_preview.accessibility_enabled:
            from utils.accessibility import get_status_symbol
            symbol = get_status_symbol("play")
            self.audio_preview.status_label.setText(f"{symbol} Ready to play")
        else:
            self.audio_preview.status_label.setText("Ready to play")
    
    def simulate_audio_error(self):
        """Simulate an audio error"""
        if self.audio_preview.accessibility_enabled:
            from utils.accessibility import get_status_symbol
            symbol = get_status_symbol("error")
            self.audio_preview.status_label.setText(f"{symbol} Playback failed")
        else:
            self.audio_preview.status_label.setText("Playback failed")
    
    def toggle_accessibility_mode(self):
        """Toggle accessibility mode for all components"""
        current_mode = accessibility_settings.colorblind_mode
        new_mode = not current_mode
        
        # Update global settings
        accessibility_settings.enable_colorblind_mode(new_mode)
        
        # Update theme
        theme_manager.enable_accessibility_mode(new_mode)
        
        # Update components
        self.piano_keyboard.set_accessibility_options(
            enabled=new_mode,
            show_patterns=True,
            show_symbols=True
        )
        
        # Update legend
        self.legend_widget.set_accessibility_mode(new_mode)
        
        # Update audio preview
        self.audio_preview.accessibility_enabled = new_mode
        self.audio_preview.accessibility_indicator = accessibility_settings.get_indicator_factory()
        
        # Refresh everything
        self.update_status()
        self.piano_keyboard.update()
        
        # Show message
        mode_text = "Accessibility Mode" if new_mode else "Normal Mode"
        QMessageBox.information(
            self,
            "Mode Changed",
            f"Switched to {mode_text}\n\n"
            f"Accessibility features {'enabled' if new_mode else 'disabled'}:\n"
            f"• Visual patterns: {'✓' if new_mode else '✗'}\n"
            f"• Symbol indicators: {'✓' if new_mode else '✗'}\n"
            f"• Colorblind-safe colors: {'✓' if new_mode else '✗'}\n"
            f"• Enhanced status indicators: {'✓' if new_mode else '✗'}"
        )
    
    def show_accessibility_settings(self):
        """Show accessibility settings dialog"""
        from views.panels.accessibility_panel import show_accessibility_settings
        show_accessibility_settings(self)
    
    def on_settings_changed(self):
        """Handle settings changes from the settings panel"""
        # Refresh all components with new settings
        self.toggle_accessibility_mode()
        self.update_status()
    
    def update_status(self):
        """Update status display"""
        if accessibility_settings.colorblind_mode:
            status_text = "Status: Accessibility Mode (Colorblind-friendly)"
            self.status_label.setStyleSheet(f"color: {ThemeColors.SUCCESS}; padding: 8px; font-weight: bold;")
        else:
            status_text = "Status: Normal Mode"
            self.status_label.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY}; padding: 8px;")
        
        self.status_label.setText(status_text)


def main():
    """Run the accessibility test application"""
    app = QApplication(sys.argv)
    app.setApplicationName("DecentSampler Accessibility Test")
    
    # Initialize theme
    theme_manager.initialize(app)
    
    # Create and show test window
    window = AccessibilityTestWindow()
    window.show()
    
    # Show welcome message
    QTimer.singleShot(1000, lambda: QMessageBox.information(
        window,
        "Accessibility Testing Suite",
        "Welcome to the DecentSampler Accessibility Testing Suite!\n\n"
        "This application demonstrates colorblind-friendly features:\n"
        "• Visual patterns and textures\n"
        "• Symbol indicators\n"
        "• Colorblind-safe color palettes\n"
        "• High contrast options\n"
        "• Enhanced status indicators\n\n"
        "Use the 'Toggle Accessibility Mode' button to see the differences.\n"
        "Check the different tabs to test various components."
    ))
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()