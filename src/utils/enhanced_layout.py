"""
Enhanced Layout System for DecentSampler Frontend
Implements a sophisticated grid system with visual grouping and responsive behavior
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QScrollArea, QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPainter, QColor, QPen
from utils.theme_manager import ThemeColors, ThemeSpacing
from utils.enhanced_typography import create_h2_label, create_h3_label


class LayoutGrid:
    """Enhanced layout grid system with consistent spacing and proportions"""
    
    # Base grid unit (8px) - all spacing should be multiples of this
    GRID_UNIT = 8
    
    # Spacing scale
    SPACING_NONE = 0
    SPACING_TINY = GRID_UNIT // 2      # 4px
    SPACING_SMALL = GRID_UNIT          # 8px
    SPACING_MEDIUM = GRID_UNIT * 2     # 16px
    SPACING_LARGE = GRID_UNIT * 3      # 24px
    SPACING_XLARGE = GRID_UNIT * 4     # 32px
    SPACING_SECTION = GRID_UNIT * 6    # 48px
    
    # Layout zones (responsive percentages)
    SIDEBAR_MIN_WIDTH = 280
    SIDEBAR_PREFERRED_WIDTH = 320
    PROPERTIES_MIN_WIDTH = 240
    PROPERTIES_PREFERRED_WIDTH = 280
    MAIN_CONTENT_MIN_WIDTH = 400
    
    # Component dimensions
    COMPONENT_HEIGHT_SMALL = GRID_UNIT * 4    # 32px
    COMPONENT_HEIGHT_MEDIUM = GRID_UNIT * 5   # 40px
    COMPONENT_HEIGHT_LARGE = GRID_UNIT * 6    # 48px
    COMPONENT_HEIGHT_XLARGE = GRID_UNIT * 8   # 64px
    
    # Control standards
    CONTROL_HEIGHT_BUTTON = COMPONENT_HEIGHT_SMALL
    CONTROL_HEIGHT_INPUT = COMPONENT_HEIGHT_SMALL - 4
    CONTROL_HEIGHT_SLIDER = COMPONENT_HEIGHT_SMALL - 8
    CONTROL_SIZE_KNOB = COMPONENT_HEIGHT_LARGE
    
    # Touch-friendly minimums
    TOUCH_TARGET_MIN = 44  # iOS/Android guideline
    
    @classmethod
    def calculate_responsive_width(cls, base_width, screen_width):
        """Calculate responsive width based on screen size"""
        if screen_width < 1200:
            return int(base_width * 0.8)
        elif screen_width < 1600:
            return int(base_width * 0.9)
        else:
            return base_width


class VisualGroup(QFrame):
    """Visual grouping container with semantic styling"""
    
    def __init__(self, title="", group_type="section", spacing=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.group_type = group_type
        self.spacing = spacing or LayoutGrid.SPACING_MEDIUM
        self._setup_group()
    
    def _setup_group(self):
        """Setup the visual group styling"""
        self.setFrameStyle(QFrame.NoFrame)
        
        # Style based on group type
        if self.group_type == "section":
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {ThemeColors.PANEL_BG};
                    border: 1px solid {ThemeColors.BORDER};
                    border-radius: {ThemeSpacing.RADIUS_LARGE}px;
                    margin: {LayoutGrid.SPACING_SMALL}px;
                }}
            """)
        elif self.group_type == "subsection":
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {ThemeColors.SECONDARY_BG};
                    border: 1px solid {ThemeColors.BORDER};
                    border-radius: {ThemeSpacing.RADIUS_MEDIUM}px;
                    margin: {LayoutGrid.SPACING_TINY}px;
                }}
            """)
        elif self.group_type == "inline":
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: transparent;
                    border: none;
                    margin: 0px;
                }}
            """)
        elif self.group_type == "highlight":
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {ThemeColors.PANEL_BG};
                    border: 2px solid {ThemeColors.ACCENT};
                    border-radius: {ThemeSpacing.RADIUS_LARGE}px;
                    margin: {LayoutGrid.SPACING_SMALL}px;
                }}
            """)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            self.spacing, self.spacing, self.spacing, self.spacing
        )
        self.main_layout.setSpacing(self.spacing)
        
        # Add title if provided
        if self.title:
            self._add_title()
    
    def _add_title(self):
        """Add title label to the group"""
        if self.group_type in ["section", "highlight"]:
            title_label = create_h2_label(self.title)
        else:
            title_label = create_h3_label(self.title)
        
        self.main_layout.addWidget(title_label)
        
        # Add separator line for sections
        if self.group_type == "section":
            separator = QFrame()
            separator.setFrameStyle(QFrame.HLine | QFrame.Plain)
            separator.setStyleSheet(f"""
                QFrame {{
                    color: {ThemeColors.BORDER};
                    background-color: {ThemeColors.BORDER};
                    height: 1px;
                    margin: {LayoutGrid.SPACING_SMALL}px 0px;
                }}
            """)
            self.main_layout.addWidget(separator)
    
    def add_widget(self, widget):
        """Add a widget to the group"""
        self.main_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Add a layout to the group"""
        self.main_layout.addLayout(layout)
    
    def add_stretch(self):
        """Add stretch to the group"""
        self.main_layout.addStretch()


class SignalFlowLayout(QWidget):
    """Layout organized by signal flow (Input → Processing → Output)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sections = {}
        self._setup_layout()
    
    def _setup_layout(self):
        """Setup the signal flow layout"""
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(LayoutGrid.SPACING_LARGE)
        
        # Create main sections
        self.input_section = VisualGroup("INPUT", "section")
        self.processing_section = VisualGroup("PROCESSING", "section")
        self.output_section = VisualGroup("OUTPUT", "section")
        
        # Add sections to layout
        self.main_layout.addWidget(self.input_section, 1)
        self.main_layout.addWidget(self.processing_section, 2)
        self.main_layout.addWidget(self.output_section, 1)
        
        # Store sections for easy access
        self.sections = {
            'input': self.input_section,
            'processing': self.processing_section,
            'output': self.output_section
        }
    
    def add_to_section(self, section_name, widget):
        """Add widget to a specific section"""
        if section_name in self.sections:
            self.sections[section_name].add_widget(widget)
    
    def add_subsection(self, section_name, title, widgets):
        """Add a subsection with multiple widgets"""
        if section_name in self.sections:
            subsection = VisualGroup(title, "subsection")
            for widget in widgets:
                subsection.add_widget(widget)
            self.sections[section_name].add_widget(subsection)


class WorkflowLayout(QWidget):
    """Layout optimized for common workflows"""
    
    def __init__(self, workflow_type="standard", parent=None):
        super().__init__(parent)
        self.workflow_type = workflow_type
        self.workflow_steps = []
        self._setup_workflow()
    
    def _setup_workflow(self):
        """Setup the workflow-specific layout"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(LayoutGrid.SPACING_MEDIUM)
        
        if self.workflow_type == "sample_mapping":
            self._setup_sample_mapping_workflow()
        elif self.workflow_type == "modulation":
            self._setup_modulation_workflow()
        elif self.workflow_type == "effects":
            self._setup_effects_workflow()
        else:
            self._setup_standard_workflow()
    
    def _setup_sample_mapping_workflow(self):
        """Setup sample mapping workflow layout"""
        # Step 1: Import
        import_group = VisualGroup("1. Import Samples", "highlight")
        self.main_layout.addWidget(import_group)
        
        # Step 2: Map
        mapping_group = VisualGroup("2. Sample Mapping", "section")
        self.main_layout.addWidget(mapping_group)
        
        # Step 3: Preview
        preview_group = VisualGroup("3. Preview & Test", "section")
        self.main_layout.addWidget(preview_group)
        
        # Step 4: Refine
        refine_group = VisualGroup("4. Fine-tune", "section")
        self.main_layout.addWidget(refine_group)
        
        self.workflow_steps = [import_group, mapping_group, preview_group, refine_group]
    
    def _setup_modulation_workflow(self):
        """Setup modulation workflow layout"""
        # Source section
        source_group = VisualGroup("Modulation Sources", "section")
        self.main_layout.addWidget(source_group)
        
        # Routing section
        routing_group = VisualGroup("Routing & Amount", "section")
        self.main_layout.addWidget(routing_group)
        
        # Destinations section
        dest_group = VisualGroup("Destinations", "section")
        self.main_layout.addWidget(dest_group)
        
        self.workflow_steps = [source_group, routing_group, dest_group]
    
    def _setup_effects_workflow(self):
        """Setup effects workflow layout"""
        # Insert effects
        insert_group = VisualGroup("Insert Effects", "section")
        self.main_layout.addWidget(insert_group)
        
        # Send effects
        send_group = VisualGroup("Send Effects", "section")
        self.main_layout.addWidget(send_group)
        
        # Master effects
        master_group = VisualGroup("Master Effects", "section")
        self.main_layout.addWidget(master_group)
        
        self.workflow_steps = [insert_group, send_group, master_group]
    
    def _setup_standard_workflow(self):
        """Setup standard workflow layout"""
        content_group = VisualGroup("Content", "section")
        self.main_layout.addWidget(content_group)
        self.workflow_steps = [content_group]
    
    def get_step(self, index):
        """Get a workflow step by index"""
        if 0 <= index < len(self.workflow_steps):
            return self.workflow_steps[index]
        return None
    
    def highlight_step(self, index):
        """Highlight a specific workflow step"""
        for i, step in enumerate(self.workflow_steps):
            if i == index:
                step.group_type = "highlight"
                step._setup_group()
            else:
                step.group_type = "section"
                step._setup_group()


class ResponsiveContainer(QWidget):
    """Container that adapts to screen size and content"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_mode = "desktop"
        self.breakpoints = {
            'mobile': 768,
            'tablet': 1024,
            'desktop': 1440,
            'large': 1920
        }
        self._setup_container()
    
    def _setup_container(self):
        """Setup the responsive container"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for resizable areas
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # Sidebar
        self.sidebar = QScrollArea()
        self.sidebar.setWidgetResizable(True)
        self.sidebar.setMinimumWidth(LayoutGrid.SIDEBAR_MIN_WIDTH)
        self.sidebar.setMaximumWidth(int(LayoutGrid.SIDEBAR_PREFERRED_WIDTH * 1.5))
        
        # Main content
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setMinimumWidth(LayoutGrid.MAIN_CONTENT_MIN_WIDTH)
        
        # Properties panel
        self.properties_panel = QScrollArea()
        self.properties_panel.setWidgetResizable(True)
        self.properties_panel.setMinimumWidth(LayoutGrid.PROPERTIES_MIN_WIDTH)
        self.properties_panel.setMaximumWidth(int(LayoutGrid.PROPERTIES_PREFERRED_WIDTH * 1.5))
        
        # Add to splitter
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.content_area)
        self.splitter.addWidget(self.properties_panel)
        
        # Set initial proportions
        self.splitter.setSizes([
            LayoutGrid.SIDEBAR_PREFERRED_WIDTH,
            800,  # Main content gets most space
            LayoutGrid.PROPERTIES_PREFERRED_WIDTH
        ])
    
    def set_sidebar_content(self, widget):
        """Set the sidebar content"""
        self.sidebar.setWidget(widget)
    
    def set_main_content(self, widget):
        """Set the main content"""
        self.content_area.setWidget(widget)
    
    def set_properties_content(self, widget):
        """Set the properties panel content"""
        self.properties_panel.setWidget(widget)
    
    def resizeEvent(self, event):
        """Handle resize events for responsive behavior"""
        super().resizeEvent(event)
        width = event.size().width()
        
        # Determine layout mode based on width
        if width < self.breakpoints['tablet']:
            self._switch_to_mobile_layout()
        elif width < self.breakpoints['desktop']:
            self._switch_to_tablet_layout()
        else:
            self._switch_to_desktop_layout()
    
    def _switch_to_mobile_layout(self):
        """Switch to mobile layout (stacked)"""
        if self.layout_mode != "mobile":
            self.layout_mode = "mobile"
            self.splitter.setOrientation(Qt.Vertical)
            self.properties_panel.hide()
    
    def _switch_to_tablet_layout(self):
        """Switch to tablet layout (reduced sidebar)"""
        if self.layout_mode != "tablet":
            self.layout_mode = "tablet"
            self.splitter.setOrientation(Qt.Horizontal)
            self.properties_panel.show()
            self.sidebar.setMaximumWidth(240)
    
    def _switch_to_desktop_layout(self):
        """Switch to desktop layout (full features)"""
        if self.layout_mode != "desktop":
            self.layout_mode = "desktop"
            self.splitter.setOrientation(Qt.Horizontal)
            self.properties_panel.show()
            self.sidebar.setMaximumWidth(int(LayoutGrid.SIDEBAR_PREFERRED_WIDTH * 1.5))


# Utility functions for creating common layouts
def create_horizontal_group(title="", widgets=None, spacing=None):
    """Create a horizontal group of widgets"""
    group = VisualGroup(title, "subsection", spacing)
    
    if widgets:
        h_layout = QHBoxLayout()
        h_layout.setSpacing(spacing or LayoutGrid.SPACING_SMALL)
        
        for widget in widgets:
            h_layout.addWidget(widget)
        
        h_layout.addStretch()
        group.add_layout(h_layout)
    
    return group

def create_vertical_group(title="", widgets=None, spacing=None):
    """Create a vertical group of widgets"""
    group = VisualGroup(title, "subsection", spacing)
    
    if widgets:
        for widget in widgets:
            group.add_widget(widget)
    
    return group

def create_grid_group(title="", widgets=None, columns=2, spacing=None):
    """Create a grid group of widgets"""
    group = VisualGroup(title, "subsection", spacing)
    
    if widgets:
        grid_layout = QGridLayout()
        grid_layout.setSpacing(spacing or LayoutGrid.SPACING_SMALL)
        
        for i, widget in enumerate(widgets):
            row = i // columns
            col = i % columns
            grid_layout.addWidget(widget, row, col)
        
        group.add_layout(grid_layout)
    
    return group

def create_section_separator():
    """Create a visual section separator"""
    separator = QFrame()
    separator.setFrameStyle(QFrame.HLine | QFrame.Plain)
    separator.setStyleSheet(f"""
        QFrame {{
            color: {ThemeColors.BORDER};
            background-color: {ThemeColors.BORDER};
            height: 1px;
            margin: {LayoutGrid.SPACING_MEDIUM}px 0px;
        }}
    """)
    separator.setMaximumHeight(1)
    return separator