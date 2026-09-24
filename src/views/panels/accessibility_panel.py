"""
Accessibility Settings Panel
Provides user interface for configuring colorblind-friendly and accessibility options
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, 
    QPushButton, QGroupBox, QSlider, QSpinBox, QFrame, QGridLayout,
    QMessageBox, QButtonGroup, QRadioButton, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QIcon

from utils.accessibility import (
    AccessibilitySettings, ColorVisionType, PatternType, AccessibilityColors,
    AccessibilityIndicator, ColorVisionSimulator, accessibility_settings
)
from utils.theme_manager import theme_manager, ThemeColors, ThemeFonts
from utils.error_handling import ErrorHandler


class ColorVisionTestWidget(QWidget):
    """Widget for testing color vision accessibility"""
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(100)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Test description
        description = QLabel("Color Discrimination Test:")
        description.setFont(QFont(ThemeFonts.FAMILY, ThemeFonts.SIZE_BODY, ThemeFonts.WEIGHT_MEDIUM))
        layout.addWidget(description)
        
        # Color test area
        test_layout = QHBoxLayout()
        
        # Create test color pairs
        test_pairs = [
            (AccessibilityColors.RED, AccessibilityColors.GREEN),
            (AccessibilityColors.BLUE, AccessibilityColors.PURPLE),
            (AccessibilityColors.ORANGE, AccessibilityColors.YELLOW)
        ]
        
        self.test_labels = []
        for i, (color1, color2) in enumerate(test_pairs):
            test_frame = QFrame()
            test_frame.setFixedSize(80, 40)
            test_frame.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 {color1}, stop: 1 {color2});
                    border: 1px solid {ThemeColors.BORDER};
                    border-radius: 4px;
                }}
            """)
            test_frame.setToolTip(f"Test {i+1}: Can you distinguish these colors?")
            test_layout.addWidget(test_frame)
            
            label = QLabel(f"Test {i+1}")
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont(ThemeFonts.FAMILY, ThemeFonts.SIZE_TINY))
            self.test_labels.append(label)
        
        test_layout.addStretch()
        layout.addLayout(test_layout)
        
        # Add labels below
        label_layout = QHBoxLayout()
        for label in self.test_labels:
            label_layout.addWidget(label)
        label_layout.addStretch()
        layout.addLayout(label_layout)
        
        self.setLayout(layout)
    
    def update_for_vision_type(self, vision_type: ColorVisionType):
        """Update test display for specific color vision type"""
        # Simulate how colors appear for this vision type
        pass  # Implementation would show simulated colors


class PatternPreviewWidget(QWidget):
    """Widget showing pattern examples"""
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(60)
        self.patterns = [
            PatternType.SOLID,
            PatternType.DOTS,
            PatternType.LINES_HORIZONTAL,
            PatternType.LINES_DIAGONAL,
            PatternType.CROSS_HATCH
        ]
        self.indicator = AccessibilityIndicator(colorblind_mode=True)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw pattern examples
        pattern_width = self.width() // len(self.patterns)
        
        for i, pattern_type in enumerate(self.patterns):
            x = i * pattern_width
            rect = event.rect().adjusted(x, 0, x + pattern_width - 1, 0)
            
            # Get pattern components
            color, brush, symbol = self.indicator.create_mapping_indicator(i)
            
            # Draw pattern
            painter.fillRect(rect, brush)
            
            # Draw symbol if available
            if symbol:
                painter.setPen(QColor(AccessibilityColors.WHITE))
                font = painter.font()
                font.setPixelSize(16)
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(rect, Qt.AlignCenter, symbol)


class AccessibilityPanel(QWidget):
    """Main accessibility settings panel"""
    
    settingsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_handler = ErrorHandler(self)
        self._setup_ui()
        self._connect_signals()
        self._load_current_settings()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("Accessibility Settings")
        header.setFont(QFont(ThemeFonts.FAMILY, ThemeFonts.SIZE_H1, ThemeFonts.WEIGHT_BOLD))
        header.setStyleSheet(f"color: {ThemeColors.ACCENT}; padding-bottom: 8px;")
        layout.addWidget(header)
        
        # Description
        description = QLabel(
            "Configure visual accessibility options to make the application easier to use. "
            "These settings help users with color vision deficiencies and those who prefer "
            "high contrast interfaces."
        )
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY}; padding-bottom: 8px;")
        layout.addWidget(description)
        
        # Main settings group
        main_group = self._create_main_settings_group()
        layout.addWidget(main_group)
        
        # Color vision settings group
        color_vision_group = self._create_color_vision_group()
        layout.addWidget(color_vision_group)
        
        # Visual indicators group
        visual_group = self._create_visual_indicators_group()
        layout.addWidget(visual_group)
        
        # Preview and test section
        preview_group = self._create_preview_group()
        layout.addWidget(preview_group)
        
        # Action buttons
        button_layout = self._create_action_buttons()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _create_main_settings_group(self):
        """Create main accessibility settings group"""
        group = QGroupBox("General Accessibility")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: {ThemeFonts.WEIGHT_SEMIBOLD};
                padding-top: 16px;
                color: {ThemeColors.TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Enable colorblind mode
        self.colorblind_mode_cb = QCheckBox("Enable colorblind-friendly mode")
        self.colorblind_mode_cb.setToolTip(
            "Use patterns, symbols, and colorblind-safe colors throughout the interface"
        )
        layout.addWidget(self.colorblind_mode_cb)
        
        # High contrast mode
        self.high_contrast_cb = QCheckBox("Enable high contrast mode")
        self.high_contrast_cb.setToolTip(
            "Increase contrast between interface elements for better visibility"
        )
        layout.addWidget(self.high_contrast_cb)
        
        # Enhanced status indicators
        self.enhanced_status_cb = QCheckBox("Use enhanced status indicators")
        self.enhanced_status_cb.setToolTip(
            "Add symbols and icons to status messages and indicators"
        )
        layout.addWidget(self.enhanced_status_cb)
        
        group.setLayout(layout)
        return group
    
    def _create_color_vision_group(self):
        """Create color vision settings group"""
        group = QGroupBox("Color Vision Support")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: {ThemeFonts.WEIGHT_SEMIBOLD};
                padding-top: 16px;
                color: {ThemeColors.TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Vision type selection
        vision_layout = QHBoxLayout()
        vision_layout.addWidget(QLabel("Color vision type:"))
        
        self.vision_type_combo = QComboBox()
        vision_types = [
            ("Normal color vision", ColorVisionType.NORMAL),
            ("Protanopia (red-blind)", ColorVisionType.PROTANOPIA),
            ("Deuteranopia (green-blind)", ColorVisionType.DEUTERANOPIA),
            ("Tritanopia (blue-blind)", ColorVisionType.TRITANOPIA),
            ("Protanomaly (red-weak)", ColorVisionType.PROTANOMALY),
            ("Deuteranomaly (green-weak)", ColorVisionType.DEUTERANOMALY),
            ("Tritanomaly (blue-weak)", ColorVisionType.TRITANOMALY)
        ]
        
        for name, vision_type in vision_types:
            self.vision_type_combo.addItem(name, vision_type)
        
        vision_layout.addWidget(self.vision_type_combo)
        vision_layout.addStretch()
        layout.addLayout(vision_layout)
        
        # Color vision test
        self.color_test_widget = ColorVisionTestWidget()
        layout.addWidget(self.color_test_widget)
        
        group.setLayout(layout)
        return group
    
    def _create_visual_indicators_group(self):
        """Create visual indicators settings group"""
        group = QGroupBox("Visual Indicators")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: {ThemeFonts.WEIGHT_SEMIBOLD};
                padding-top: 16px;
                color: {ThemeColors.TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Use patterns
        self.use_patterns_cb = QCheckBox("Use visual patterns")
        self.use_patterns_cb.setToolTip(
            "Add patterns like dots, lines, and hatching to distinguish elements"
        )
        layout.addWidget(self.use_patterns_cb)
        
        # Use symbols
        self.use_symbols_cb = QCheckBox("Use symbols and icons")
        self.use_symbols_cb.setToolTip(
            "Add symbols to complement color-coded information"
        )
        layout.addWidget(self.use_symbols_cb)
        
        # Pattern density
        density_layout = QHBoxLayout()
        density_layout.addWidget(QLabel("Pattern density:"))
        
        self.pattern_density_slider = QSlider(Qt.Horizontal)
        self.pattern_density_slider.setRange(30, 100)
        self.pattern_density_slider.setValue(70)
        self.pattern_density_slider.setToolTip("Adjust how dense visual patterns appear")
        density_layout.addWidget(self.pattern_density_slider)
        
        self.density_label = QLabel("70%")
        self.density_label.setMinimumWidth(40)
        density_layout.addWidget(self.density_label)
        
        layout.addLayout(density_layout)
        
        # Symbol size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Symbol size:"))
        
        self.symbol_size_spin = QSpinBox()
        self.symbol_size_spin.setRange(8, 24)
        self.symbol_size_spin.setValue(16)
        self.symbol_size_spin.setSuffix(" px")
        self.symbol_size_spin.setToolTip("Adjust the size of accessibility symbols")
        size_layout.addWidget(self.symbol_size_spin)
        
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_preview_group(self):
        """Create preview and test group"""
        group = QGroupBox("Preview & Testing")
        group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: {ThemeFonts.WEIGHT_SEMIBOLD};
                padding-top: 16px;
                color: {ThemeColors.TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Pattern preview
        preview_label = QLabel("Pattern Preview:")
        layout.addWidget(preview_label)
        
        self.pattern_preview = PatternPreviewWidget()
        layout.addWidget(self.pattern_preview)
        
        # Test button
        test_layout = QHBoxLayout()
        self.test_accessibility_btn = QPushButton("Test Current Settings")
        self.test_accessibility_btn.setToolTip(
            "Apply current settings temporarily to test them"
        )
        test_layout.addWidget(self.test_accessibility_btn)
        test_layout.addStretch()
        layout.addLayout(test_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_action_buttons(self):
        """Create action buttons layout"""
        layout = QHBoxLayout()
        
        # Reset to defaults
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.setToolTip("Reset all accessibility settings to default values")
        layout.addWidget(self.reset_btn)
        
        layout.addStretch()
        
        # Apply settings
        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.setToolTip("Apply current accessibility settings")
        self.apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeColors.ACCENT};
                color: {ThemeColors.TEXT_PRIMARY};
                font-weight: {ThemeFonts.WEIGHT_SEMIBOLD};
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {ThemeColors.ACCENT_HOVER};
            }}
        """)
        layout.addWidget(self.apply_btn)
        
        return layout
    
    def _connect_signals(self):
        """Connect widget signals"""
        # Main settings
        self.colorblind_mode_cb.toggled.connect(self._on_colorblind_mode_changed)
        self.high_contrast_cb.toggled.connect(self._on_high_contrast_changed)
        self.enhanced_status_cb.toggled.connect(self._on_enhanced_status_changed)
        
        # Color vision
        self.vision_type_combo.currentIndexChanged.connect(self._on_vision_type_changed)
        
        # Visual indicators
        self.use_patterns_cb.toggled.connect(self._on_patterns_changed)
        self.use_symbols_cb.toggled.connect(self._on_symbols_changed)
        self.pattern_density_slider.valueChanged.connect(self._on_density_changed)
        self.symbol_size_spin.valueChanged.connect(self._on_symbol_size_changed)
        
        # Buttons
        self.test_accessibility_btn.clicked.connect(self._test_settings)
        self.reset_btn.clicked.connect(self._reset_to_defaults)
        self.apply_btn.clicked.connect(self._apply_settings)
    
    def _load_current_settings(self):
        """Load current accessibility settings"""
        settings = accessibility_settings
        
        # Update UI to reflect current settings
        self.colorblind_mode_cb.setChecked(settings.colorblind_mode)
        self.high_contrast_cb.setChecked(settings.high_contrast)
        self.enhanced_status_cb.setChecked(settings.status_indicators_enhanced)
        
        # Set vision type
        for i in range(self.vision_type_combo.count()):
            if self.vision_type_combo.itemData(i) == settings.vision_type:
                self.vision_type_combo.setCurrentIndex(i)
                break
        
        self.use_patterns_cb.setChecked(settings.use_patterns)
        self.use_symbols_cb.setChecked(settings.use_symbols)
        self.pattern_density_slider.setValue(int(settings.pattern_density * 100))
        self.symbol_size_spin.setValue(settings.symbol_size)
        
        self._update_dependent_controls()
    
    def _update_dependent_controls(self):
        """Update controls that depend on other settings"""
        colorblind_enabled = self.colorblind_mode_cb.isChecked()
        
        # Enable/disable dependent controls
        self.use_patterns_cb.setEnabled(colorblind_enabled)
        self.use_symbols_cb.setEnabled(colorblind_enabled)
        self.pattern_density_slider.setEnabled(colorblind_enabled and self.use_patterns_cb.isChecked())
        self.symbol_size_spin.setEnabled(colorblind_enabled and self.use_symbols_cb.isChecked())
        
        # Update density label
        density_value = self.pattern_density_slider.value()
        self.density_label.setText(f"{density_value}%")
    
    def _on_colorblind_mode_changed(self, checked):
        """Handle colorblind mode change"""
        self._update_dependent_controls()
        if checked:
            # Auto-enable patterns and symbols when colorblind mode is enabled
            self.use_patterns_cb.setChecked(True)
            self.use_symbols_cb.setChecked(True)
    
    def _on_high_contrast_changed(self, checked):
        """Handle high contrast mode change"""
        pass  # Handled in apply
    
    def _on_enhanced_status_changed(self, checked):
        """Handle enhanced status indicators change"""
        pass  # Handled in apply
    
    def _on_vision_type_changed(self, index):
        """Handle vision type change"""
        vision_type = self.vision_type_combo.itemData(index)
        self.color_test_widget.update_for_vision_type(vision_type)
        
        # Auto-enable colorblind mode for non-normal vision
        if vision_type != ColorVisionType.NORMAL:
            self.colorblind_mode_cb.setChecked(True)
    
    def _on_patterns_changed(self, checked):
        """Handle pattern usage change"""
        self._update_dependent_controls()
    
    def _on_symbols_changed(self, checked):
        """Handle symbol usage change"""
        self._update_dependent_controls()
    
    def _on_density_changed(self, value):
        """Handle pattern density change"""
        self.density_label.setText(f"{value}%")
        self.pattern_preview.update()
    
    def _on_symbol_size_changed(self, value):
        """Handle symbol size change"""
        self.pattern_preview.update()
    
    def _test_settings(self):
        """Test current settings temporarily"""
        # Apply settings temporarily for testing
        self._apply_settings_to_global(test_mode=True)
        
        # Show information dialog
        QMessageBox.information(
            self,
            "Testing Settings",
            "Settings have been applied temporarily for testing. "
            "Click 'Apply Settings' to make them permanent, or adjust and test again."
        )
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Reset all accessibility settings to their default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to defaults
            self.colorblind_mode_cb.setChecked(False)
            self.high_contrast_cb.setChecked(False)
            self.enhanced_status_cb.setChecked(True)
            self.vision_type_combo.setCurrentIndex(0)  # Normal vision
            self.use_patterns_cb.setChecked(True)
            self.use_symbols_cb.setChecked(True)
            self.pattern_density_slider.setValue(70)
            self.symbol_size_spin.setValue(16)
            
            self._update_dependent_controls()
    
    def _apply_settings(self):
        """Apply current settings"""
        try:
            self._apply_settings_to_global(test_mode=False)
            
            # Emit signal for other components to update
            self.settingsChanged.emit()
            
            # Show success message
            QMessageBox.information(
                self,
                "Settings Applied",
                "Accessibility settings have been applied successfully. "
                "You may need to refresh some views to see all changes."
            )
            
        except Exception as e:
            self.error_handler.handle_error(
                e, "applying accessibility settings", show_dialog=True
            )
    
    def _apply_settings_to_global(self, test_mode=False):
        """Apply settings to global accessibility settings"""
        # Update global settings
        accessibility_settings.colorblind_mode = self.colorblind_mode_cb.isChecked()
        accessibility_settings.high_contrast = self.high_contrast_cb.isChecked()
        accessibility_settings.status_indicators_enhanced = self.enhanced_status_cb.isChecked()
        
        # Vision type
        vision_type = self.vision_type_combo.currentData()
        accessibility_settings.vision_type = vision_type
        
        # Visual indicators
        accessibility_settings.use_patterns = self.use_patterns_cb.isChecked()
        accessibility_settings.use_symbols = self.use_symbols_cb.isChecked()
        accessibility_settings.pattern_density = self.pattern_density_slider.value() / 100.0
        accessibility_settings.symbol_size = self.symbol_size_spin.value()
        
        # Apply theme changes
        theme_manager.enable_accessibility_mode(accessibility_settings.colorblind_mode)
        theme_manager.enable_high_contrast_mode(accessibility_settings.high_contrast)
        
        if not test_mode:
            # Save settings persistently (would integrate with app settings)
            pass


def show_accessibility_settings(parent=None):
    """Show accessibility settings dialog"""
    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
    
    dialog = QDialog(parent)
    dialog.setWindowTitle("Accessibility Settings")
    dialog.setMinimumSize(600, 700)
    dialog.setModal(True)
    
    layout = QVBoxLayout()
    
    # Add accessibility panel
    panel = AccessibilityPanel(dialog)
    layout.addWidget(panel)
    
    # Add dialog buttons
    button_box = QDialogButtonBox(QDialogButtonBox.Close)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)
    
    dialog.setLayout(layout)
    
    # Apply current theme
    dialog.setStyleSheet(f"""
        QDialog {{
            background-color: {ThemeColors.PRIMARY_BG};
            color: {ThemeColors.TEXT_PRIMARY};
        }}
    """)
    
    return dialog.exec_()