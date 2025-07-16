"""
Responsive Layout Manager for DecentSampler Frontend
Provides adaptive layouts that work across different screen resolutions
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSplitter, 
    QScrollArea, QFrame, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont

class ResponsiveTabWidget(QTabWidget):
    """Tab widget that adapts to screen size and provides responsive layouts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_responsive_styling()
        
    def setup_responsive_styling(self):
        """Setup responsive styling for tabs"""
        self.setTabPosition(QTabWidget.North)
        self.setUsesScrollButtons(True)
        self.setElideMode(Qt.ElideRight)
        
        # Apply responsive tab styling
        self.apply_responsive_tab_styling()
    
    def apply_responsive_tab_styling(self):
        """Apply responsive tab styling based on screen size"""
        try:
            from utils.ui_consistency import TabStyler
            screen = QApplication.primaryScreen()
            if screen:
                screen_width = screen.size().width()
                self.setStyleSheet(TabStyler.get_tab_stylesheet(screen_width))
        except ImportError:
            # Fallback styling
            self.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #444;
                    background-color: #2a2a2a;
                }
                QTabBar::tab {
                    background-color: #3a3a3a;
                    color: #c0c0c0;
                    border: 1px solid #444;
                    border-bottom: none;
                    padding: 8px 16px;
                    margin-right: 2px;
                    font-size: 11px;
                    font-weight: 500;
                }
                QTabBar::tab:selected {
                    background-color: #4a7c59;
                    color: #ffffff;
                    font-weight: 600;
                }
                QTabBar::tab:hover:!selected {
                    background-color: #4a4a4a;
                    color: #ffffff;
                }
            """)

class ResponsivePanel(QWidget):
    """Base panel that adapts to available space"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_responsive_policy()
        
    def setup_responsive_policy(self):
        """Setup responsive size policies"""
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def get_minimum_size(self):
        """Get minimum size for this panel"""
        return QSize(400, 300)
        
    def get_preferred_size(self):
        """Get preferred size for this panel"""
        return QSize(800, 600)

class AdaptiveLayoutManager(QWidget):
    """Main layout manager that adapts to screen size and organizes workflow"""
    
    layoutChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.screen_info = self.get_screen_info()
        self.layout_mode = self.determine_layout_mode()
        self.init_responsive_ui()
        
    def get_screen_info(self):
        """Get current screen resolution and available space"""
        desktop = QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        available_rect = desktop.availableGeometry()
        
        return {
            'width': screen_rect.width(),
            'height': screen_rect.height(),
            'available_width': available_rect.width(),
            'available_height': available_rect.height(),
            'dpi': desktop.logicalDpiX()
        }
        
    def determine_layout_mode(self):
        """Determine the best layout mode based on screen size"""
        width = self.screen_info['available_width']
        height = self.screen_info['available_height']
        
        if width >= 1920 and height >= 1200:
            return "large"  # Large desktop screens
        elif width >= 1400 and height >= 900:
            return "medium"  # Medium screens, laptops, MacBook Pro
        elif width >= 1000 and height >= 700:
            return "small"  # Small laptops, tablets
        else:
            return "compact"  # Very small screens
            
    def init_responsive_ui(self):
        """Initialize responsive UI based on layout mode"""
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Create workflow tabs
        self.workflow_tabs = ResponsiveTabWidget()
        self.setup_workflow_tabs()
        
        # Add to splitter based on layout mode
        if self.layout_mode in ["large", "medium"]:
            # Horizontal layout with sidebar
            self.main_splitter.addWidget(self.create_sidebar())
            self.main_splitter.addWidget(self.workflow_tabs)
            
            # Set splitter proportions
            if self.layout_mode == "large":
                self.main_splitter.setSizes([350, 1250])  # More space for main content
            else:
                self.main_splitter.setSizes([300, 900])
                
        else:
            # Vertical or compact layout for small screens
            self.main_splitter.setOrientation(Qt.Vertical)
            self.main_splitter.addWidget(self.create_compact_sidebar())
            self.main_splitter.addWidget(self.workflow_tabs)
            self.main_splitter.setSizes([200, 400])
            
        layout.addWidget(self.main_splitter)
        self.setLayout(layout)
        
    def create_sidebar(self):
        """Create responsive sidebar for sample management"""
        sidebar = QFrame()
        sidebar.setFrameStyle(QFrame.StyledPanel)
        sidebar.setMinimumWidth(250)
        sidebar.setMaximumWidth(400)
        
        # This will contain the sample mapping panel
        layout = QVBoxLayout()
        sidebar.setLayout(layout)
        
        return sidebar
        
    def create_compact_sidebar(self):
        """Create compact sidebar for small screens"""
        sidebar = QFrame()
        sidebar.setFrameStyle(QFrame.StyledPanel)
        sidebar.setMinimumHeight(150)
        sidebar.setMaximumHeight(250)
        
        layout = QHBoxLayout()
        sidebar.setLayout(layout)
        
        return sidebar
        
    def setup_workflow_tabs(self):
        """Setup the main workflow tabs"""
        # Tab 1: Core Editing (Samples + Preview + Keyboard)
        samples_tab = self.create_samples_tab()
        self.workflow_tabs.addTab(samples_tab, "📝 Samples")
        
        # Tab 2: Properties (ADSR + Global Options)  
        properties_tab = self.create_properties_tab()
        self.workflow_tabs.addTab(properties_tab, "⚙️ Properties")
        
        # Tab 3: Modulation (LFOs + Routes)
        modulation_tab = self.create_modulation_tab()
        self.workflow_tabs.addTab(modulation_tab, "🌊 Modulation")
        
        # Tab 4: Groups (Sample Grouping)
        groups_tab = self.create_groups_tab()
        self.workflow_tabs.addTab(groups_tab, "📁 Groups")
        
    def create_samples_tab(self):
        """Create the main samples editing tab"""
        tab = ResponsivePanel()
        layout = QVBoxLayout()
        
        # Main content area for preview and keyboard
        content_area = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)
        
        # This will contain preview canvas and piano keyboard
        content_area.setLayout(content_layout)
        
        # Add scroll area for small screens
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_area)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        
        # Store reference for later population
        tab.content_layout = content_layout
        
        return tab
        
    def create_properties_tab(self):
        """Create the properties editing tab"""
        tab = ResponsivePanel()
        layout = QVBoxLayout()
        
        # Create splitter for large screens to show side-by-side
        if self.layout_mode == "large":
            splitter = QSplitter(Qt.Horizontal)
            
            # ADSR section
            adsr_area = QWidget()
            splitter.addWidget(adsr_area)
            
            # Global options section  
            options_area = QWidget()
            splitter.addWidget(options_area)
            
            splitter.setSizes([400, 400])
            layout.addWidget(splitter)
            
            # Store references
            tab.adsr_layout = QVBoxLayout()
            adsr_area.setLayout(tab.adsr_layout)
            tab.options_layout = QVBoxLayout()
            options_area.setLayout(tab.options_layout)
            
        else:
            # Vertical layout for smaller screens
            scroll_area = QScrollArea()
            content_widget = QWidget()
            content_layout = QVBoxLayout()
            
            content_widget.setLayout(content_layout)
            scroll_area.setWidget(content_widget)
            scroll_area.setWidgetResizable(True)
            
            layout.addWidget(scroll_area)
            
            # Store reference
            tab.content_layout = content_layout
            
        tab.setLayout(layout)
        return tab
        
    def create_modulation_tab(self):
        """Create the modulation editing tab"""
        tab = ResponsivePanel()
        layout = QVBoxLayout()
        
        # Scroll area for modulation content
        scroll_area = QScrollArea()
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 8, 8, 8)
        
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        
        # Store reference
        tab.content_layout = content_layout
        
        return tab
        
    def create_groups_tab(self):
        """Create the groups management tab"""
        tab = ResponsivePanel()
        layout = QVBoxLayout()
        
        # Groups content
        scroll_area = QScrollArea()
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 8, 8, 8)
        
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        
        # Store reference
        tab.content_layout = content_layout
        
        return tab
        
    def get_sidebar_container(self):
        """Get the sidebar container for adding sample panel"""
        if self.layout_mode in ["large", "medium"]:
            sidebar = self.main_splitter.widget(0)
        else:
            sidebar = self.main_splitter.widget(0)
        return sidebar.layout()
        
    def get_tab_by_name(self, name):
        """Get a specific tab by its name"""
        for i in range(self.workflow_tabs.count()):
            if name.lower() in self.workflow_tabs.tabText(i).lower():
                return self.workflow_tabs.widget(i)
        return None
        
    def add_to_samples_tab(self, widget):
        """Add widget to samples tab"""
        samples_tab = self.get_tab_by_name("samples")
        if samples_tab and hasattr(samples_tab, 'content_layout'):
            samples_tab.content_layout.addWidget(widget)
            
    def add_to_properties_tab(self, widget, section="main"):
        """Add widget to properties tab"""
        properties_tab = self.get_tab_by_name("properties")
        if properties_tab:
            if hasattr(properties_tab, 'adsr_layout') and section == "adsr":
                properties_tab.adsr_layout.addWidget(widget)
            elif hasattr(properties_tab, 'options_layout') and section == "options":
                properties_tab.options_layout.addWidget(widget)
            elif hasattr(properties_tab, 'content_layout'):
                properties_tab.content_layout.addWidget(widget)
                
    def add_to_modulation_tab(self, widget):
        """Add widget to modulation tab"""
        modulation_tab = self.get_tab_by_name("modulation")
        if modulation_tab and hasattr(modulation_tab, 'content_layout'):
            modulation_tab.content_layout.addWidget(widget)
            
    def add_to_groups_tab(self, widget):
        """Add widget to groups tab"""
        groups_tab = self.get_tab_by_name("groups")
        if groups_tab and hasattr(groups_tab, 'content_layout'):
            groups_tab.content_layout.addWidget(widget)
            
    def set_active_tab(self, name):
        """Set the active tab by name"""
        for i in range(self.workflow_tabs.count()):
            if name.lower() in self.workflow_tabs.tabText(i).lower():
                self.workflow_tabs.setCurrentIndex(i)
                break
                
    def adapt_to_screen_change(self):
        """Adapt layout when screen size changes"""
        old_screen_info = self.screen_info
        self.screen_info = self.get_screen_info()
        old_layout_mode = self.layout_mode
        self.layout_mode = self.determine_layout_mode()
        
        # Rebuild UI if layout mode changed significantly
        if old_layout_mode != self.layout_mode:
            self.layoutChanged.emit()
            
    def get_optimal_widget_size(self, base_width, base_height):
        """Get optimal widget size based on screen size and layout mode"""
        if self.layout_mode == "large":
            # Scale up for large screens
            return QSize(
                int(min(base_width * 1.2, self.screen_info['available_width'] * 0.6)),
                int(min(base_height * 1.1, self.screen_info['available_height'] * 0.5))
            )
        elif self.layout_mode == "medium":
            # Standard size
            return QSize(
                int(min(base_width, self.screen_info['available_width'] * 0.7)),
                int(min(base_height, self.screen_info['available_height'] * 0.6))
            )
        elif self.layout_mode == "small":
            # Scale down for small screens
            return QSize(
                int(min(base_width * 0.8, self.screen_info['available_width'] * 0.8)),
                int(min(base_height * 0.9, self.screen_info['available_height'] * 0.7))
            )
        else:
            # Compact mode - fit to screen
            return QSize(
                int(min(base_width * 0.6, self.screen_info['available_width'] * 0.95)),
                int(min(base_height * 0.7, self.screen_info['available_height'] * 0.8))
            )

class ResponsiveSizingMixin:
    """Mixin to add responsive sizing capabilities to widgets"""
    
    def apply_responsive_sizing(self, layout_manager):
        """Apply responsive sizing based on layout manager"""
        if hasattr(self, 'setFixedWidth'):
            # Remove fixed width constraints
            self.setMinimumWidth(0)
            self.setMaximumWidth(16777215)  # Qt max
            
        if hasattr(self, 'setFixedHeight'):
            # Remove fixed height constraints where appropriate
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
            
        # Set responsive size policy
        if hasattr(self, 'setSizePolicy'):
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)