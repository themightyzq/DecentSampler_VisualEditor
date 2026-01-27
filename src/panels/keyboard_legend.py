from PyQt5.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont, QPixmap
from utils.accessibility import (
    AccessibilityColors, accessibility_settings
)
from utils.theme_manager import ThemeColors
import os


class KeyboardLegendWidget(QWidget):
    """Legend widget showing color-coded sample mappings"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.legend_items = []
        self.accessibility_enabled = accessibility_settings.colorblind_mode
        self.accessibility_indicator = accessibility_settings.get_indicator_factory()
        self.init_ui()

    def init_ui(self):
        self.setMinimumHeight(90)
        self.setMaximumHeight(160)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Setup layout
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        # Header
        if self.accessibility_enabled:
            header_text = "Sample Mapping Legend (Accessible Mode)"
        else:
            header_text = "Sample Mapping Legend"

        header = QLabel(header_text)
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setStyleSheet(f"color: {ThemeColors.ACCENT}; padding: 2px;")
        layout.addWidget(header)

        # Scroll area for legend items
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setMaximumHeight(100)

        self.legend_container = QWidget()
        self.legend_layout = QHBoxLayout()
        self.legend_layout.setContentsMargins(2, 2, 2, 2)
        self.legend_layout.setSpacing(8)
        self.legend_container.setLayout(self.legend_layout)

        self.scroll_area.setWidget(self.legend_container)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

        # Apply dark theme
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ThemeColors.PRIMARY_BG};
                color: white;
            }}
            QScrollArea {{
                border: 1px solid {ThemeColors.BORDER_HOVER};
                border-radius: 3px;
                background-color: {ThemeColors.PANEL_BG};
            }}
        """)

    def update_legend(self, legend_items):
        """Update the legend with new items"""
        # Clear existing items
        for i in reversed(range(self.legend_layout.count())):
            self.legend_layout.itemAt(i).widget().setParent(None)

        self.legend_items = legend_items

        # Add new legend items
        for item in legend_items:
            legend_item = self.create_legend_item(item)
            self.legend_layout.addWidget(legend_item)

        # Add stretch to push items to the left
        self.legend_layout.addStretch()

    def create_legend_item(self, item):
        """Create a visual legend item with accessibility enhancements"""
        container = QFrame()
        container.setFrameStyle(QFrame.StyledPanel)

        if self.accessibility_enabled:
            container.setMinimumSize(120, 60)
            container.setMaximumSize(180, 80)
        else:
            container.setMinimumSize(100, 50)
            container.setMaximumSize(180, 80)

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(1)

        if self.accessibility_enabled:
            # Enhanced indicator with pattern and symbol
            indicator_layout = QHBoxLayout()
            indicator_layout.setContentsMargins(0, 0, 0, 0)

            # Get accessibility components
            mapping_index = self.legend_items.index(item) if item in self.legend_items else 0
            color, brush, symbol = self.accessibility_indicator.create_mapping_indicator(mapping_index)

            # Pattern indicator
            pattern_indicator = QLabel()
            pattern_pixmap = QPixmap(30, 12)
            pattern_pixmap.fill(Qt.transparent)

            painter = QPainter(pattern_pixmap)
            painter.setBrush(brush)
            painter.setPen(Qt.NoPen)
            painter.drawRect(pattern_pixmap.rect())
            painter.end()

            pattern_indicator.setPixmap(pattern_pixmap)
            indicator_layout.addWidget(pattern_indicator)

            # Symbol indicator
            if symbol:
                symbol_label = QLabel(symbol)
                symbol_label.setFont(QFont("Arial", 12, QFont.Bold))
                symbol_label.setStyleSheet("color: white; background-color: rgba(0,0,0,100); padding: 2px; border-radius: 2px;")
                symbol_label.setAlignment(Qt.AlignCenter)
                symbol_label.setFixedSize(20, 16)
                indicator_layout.addWidget(symbol_label)

            indicator_layout.addStretch()
            layout.addLayout(indicator_layout)
        else:
            # Original color bar
            color_bar = QFrame()
            color_bar.setFixedHeight(8)
            color_bar.setStyleSheet(f"""
                background-color: rgb({item['color'].red()}, {item['color'].green()}, {item['color'].blue()});
                border-radius: 2px;
            """)
            layout.addWidget(color_bar)

        # Sample name
        name_label = QLabel(item['name'])
        name_label.setFont(QFont("Arial", 11, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        fm = name_label.fontMetrics()
        elided = fm.elidedText(item['name'], Qt.ElideRight, 140)
        name_label.setText(elided)
        if elided != item['name']:
            name_label.setToolTip(item['name'])
        layout.addWidget(name_label)

        # Range info
        range_label = QLabel(item['range'])
        range_label.setFont(QFont("Arial", 10))
        range_label.setAlignment(Qt.AlignCenter)
        range_label.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY};")
        layout.addWidget(range_label)

        # Root note
        root_label = QLabel(f"Root: {item['root']}")
        root_label.setFont(QFont("Arial", 10))
        root_label.setAlignment(Qt.AlignCenter)
        root_label.setStyleSheet(f"color: {ThemeColors.TEXT_HINT};")
        layout.addWidget(root_label)

        container.setLayout(layout)

        # Enhanced tooltip for accessibility
        if self.accessibility_enabled:
            tooltip_text = (f"Sample: {item['name']}\n"
                          f"Range: {item['range']}\n"
                          f"Root: {item['root']}\n"
                          f"File: {os.path.basename(item['path'])}\n"
                          f"Accessibility: Pattern and symbol indicators included")
        else:
            tooltip_text = (f"Sample: {item['name']}\n"
                          f"Range: {item['range']}\n"
                          f"Root: {item['root']}\n"
                          f"File: {os.path.basename(item['path'])}")

        container.setToolTip(tooltip_text)

        return container

    def set_accessibility_mode(self, enabled):
        """Enable or disable accessibility mode for the legend"""
        self.accessibility_enabled = enabled
        self.accessibility_indicator = accessibility_settings.get_indicator_factory()

        # Update header
        if self.accessibility_enabled:
            header_text = "Sample Mapping Legend (Accessible Mode)"
        else:
            header_text = "Sample Mapping Legend"

        # Find and update header label
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and ("Legend" in widget.text()):
                widget.setText(header_text)
                break

        # Refresh legend items with current items
        if hasattr(self, 'legend_items'):
            current_items = self.legend_items.copy()
            self.update_legend(current_items)
