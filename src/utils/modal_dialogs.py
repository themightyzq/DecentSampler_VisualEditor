"""
Modal Dialog System for DecentSampler Frontend
Provides modal dialogs for advanced features to reduce UI clutter
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,
    QWidget, QScrollArea, QFrame, QGroupBox, QDialogButtonBox, QApplication,
    QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

class ResponsiveDialog(QDialog):
    """Base responsive dialog that adapts to screen size"""
    
    def __init__(self, parent=None, title="Dialog", min_size=(400, 300)):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.min_size = min_size
        self.setup_responsive_dialog()
        
    def setup_responsive_dialog(self):
        """Setup responsive dialog sizing and styling"""
        # Get screen info
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry()
        
        # Calculate responsive size
        width_ratio = min(0.8, max(0.4, 800 / screen_rect.width()))
        height_ratio = min(0.8, max(0.4, 600 / screen_rect.height()))
        
        dialog_width = int(screen_rect.width() * width_ratio)
        dialog_height = int(screen_rect.height() * height_ratio)
        
        # Ensure minimum size
        dialog_width = max(dialog_width, self.min_size[0])
        dialog_height = max(dialog_height, self.min_size[1])
        
        self.resize(dialog_width, dialog_height)
        
        # Center on screen
        x = (screen_rect.width() - dialog_width) // 2
        y = (screen_rect.height() - dialog_height) // 2
        self.move(x, y)
        
        # Set modal
        self.setModal(True)
        
        # Apply dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
            }
            
            QLabel {
                color: white;
            }
            
            QPushButton {
                background-color: #404040;
                color: white;
                border: 1px solid #555;
                padding: 6px 12px;
                border-radius: 3px;
            }
            
            QPushButton:hover {
                background-color: #505050;
            }
            
            QPushButton:pressed {
                background-color: #353535;
            }
            
            QGroupBox {
                color: white;
                border: 1px solid #555;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                color: #4a9eff;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

class AdvancedSettingsDialog(ResponsiveDialog):
    """Dialog for advanced application settings"""
    
    settingsChanged = pyqtSignal(dict)
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent, "Advanced Settings", (500, 400))
        self.current_settings = current_settings or {}
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("⚙️ Advanced Settings")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #4a9eff; padding: 10px;")
        layout.addWidget(header)
        
        # Settings tabs
        tabs = QTabWidget()
        
        # Performance tab
        performance_tab = self.create_performance_tab()
        tabs.addTab(performance_tab, "Performance")
        
        # UI Behavior tab
        ui_tab = self.create_ui_tab()
        tabs.addTab(ui_tab, "UI Behavior")
        
        # Audio tab
        audio_tab = self.create_audio_tab()
        tabs.addTab(audio_tab, "Audio")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
        
    def create_performance_tab(self):
        """Create performance settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Auto-save settings
        autosave_group = QGroupBox("Auto-Save")
        autosave_layout = QVBoxLayout()
        
        autosave_info = QLabel("Configure automatic saving behavior to prevent data loss.")
        autosave_info.setWordWrap(True)
        autosave_layout.addWidget(autosave_info)
        
        autosave_group.setLayout(autosave_layout)
        layout.addWidget(autosave_group)
        
        # Memory settings
        memory_group = QGroupBox("Memory Management")
        memory_layout = QVBoxLayout()
        
        memory_info = QLabel("Adjust memory usage for large sample libraries.")
        memory_info.setWordWrap(True)
        memory_layout.addWidget(memory_info)
        
        memory_group.setLayout(memory_layout)
        layout.addWidget(memory_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
        
    def create_ui_tab(self):
        """Create UI behavior settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Layout settings
        layout_group = QGroupBox("Layout Behavior")
        layout_layout = QVBoxLayout()
        
        layout_info = QLabel("Control how the interface adapts to different screen sizes.")
        layout_info.setWordWrap(True)
        layout_layout.addWidget(layout_info)
        
        layout_group.setLayout(layout_layout)
        layout.addWidget(layout_group)
        
        # Tooltips settings
        tooltip_group = QGroupBox("Help & Tooltips")
        tooltip_layout = QVBoxLayout()
        
        tooltip_info = QLabel("Configure help system and tooltip behavior.")
        tooltip_info.setWordWrap(True)
        tooltip_layout.addWidget(tooltip_info)
        
        tooltip_group.setLayout(tooltip_layout)
        layout.addWidget(tooltip_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
        
    def create_audio_tab(self):
        """Create audio settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Preview settings
        preview_group = QGroupBox("Audio Preview")
        preview_layout = QVBoxLayout()
        
        preview_info = QLabel("Configure audio preview and playback settings.")
        preview_info.setWordWrap(True)
        preview_layout.addWidget(preview_info)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
        
    def restore_defaults(self):
        """Restore default settings"""
        reply = QMessageBox.question(
            self, "Restore Defaults",
            "Are you sure you want to restore all settings to their default values?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to defaults
            self.current_settings = {}
            # Update UI controls here
            
    def get_settings(self):
        """Get the current settings"""
        return self.current_settings

class HelpDialog(ResponsiveDialog):
    """Comprehensive help dialog with tutorials and documentation"""
    
    def __init__(self, parent=None, section="overview"):
        super().__init__(parent, "Help & Documentation", (700, 500))
        self.section = section
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📚 Help & Documentation")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #4a9eff; padding: 10px;")
        layout.addWidget(header)
        
        # Help content tabs
        tabs = QTabWidget()
        
        # Overview tab
        overview_tab = self.create_overview_tab()
        tabs.addTab(overview_tab, "Getting Started")
        
        # Workflow tab
        workflow_tab = self.create_workflow_tab()
        tabs.addTab(workflow_tab, "Workflows")
        
        # Shortcuts tab
        shortcuts_tab = self.create_shortcuts_tab()
        tabs.addTab(shortcuts_tab, "Shortcuts")
        
        # Troubleshooting tab
        troubleshooting_tab = self.create_troubleshooting_tab()
        tabs.addTab(troubleshooting_tab, "Troubleshooting")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("QPushButton { background-color: #51cf66; font-weight: bold; padding: 8px 16px; }")
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def create_overview_tab(self):
        """Create getting started tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        scroll_area = QScrollArea()
        content = QWidget()
        content_layout = QVBoxLayout()
        
        # Welcome section
        welcome = QLabel("""
        <h2>🎵 Welcome to DecentSampler Preset Editor</h2>
        
        <p>This application helps you create professional sample instruments for DecentSampler. Here's how to get started:</p>
        
        <h3>📝 Basic Workflow:</h3>
        <ol>
        <li><b>Import Samples:</b> Use the sidebar to add your audio files</li>
        <li><b>Map to Keys:</b> Assign samples to keyboard ranges</li>
        <li><b>Configure Properties:</b> Set up ADSR, effects, and modulation</li>
        <li><b>Organize Groups:</b> Create velocity layers or sample blending</li>
        <li><b>Preview & Test:</b> Use the preview canvas to test your instrument</li>
        <li><b>Save:</b> Export your .dspreset file</li>
        </ol>
        
        <h3>🎯 The Four Main Tabs:</h3>
        <ul>
        <li><b>📝 Samples:</b> Core editing with preview and keyboard</li>
        <li><b>⚙️ Properties:</b> ADSR envelope and instrument settings</li>
        <li><b>🌊 Modulation:</b> LFOs and parameter modulation</li>
        <li><b>📁 Groups:</b> Advanced sample organization</li>
        </ul>
        
        <h3>💡 Tips:</h3>
        <ul>
        <li>Start with the Samples tab for basic editing</li>
        <li>Use tooltips for detailed help on any control</li>
        <li>The interface adapts to your screen size automatically</li>
        <li>Save frequently to prevent data loss</li>
        </ul>
        """)
        welcome.setWordWrap(True)
        welcome.setOpenExternalLinks(True)
        content_layout.addWidget(welcome)
        
        content.setLayout(content_layout)
        scroll_area.setWidget(content)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab
        
    def create_workflow_tab(self):
        """Create workflow guide tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        scroll_area = QScrollArea()
        content = QWidget()
        content_layout = QVBoxLayout()
        
        workflow_text = QLabel("""
        <h2>🔄 Common Workflows</h2>
        
        <h3>🎹 Creating a Simple Piano:</h3>
        <ol>
        <li>Import piano samples for different notes</li>
        <li>Map each sample to its corresponding key</li>
        <li>Adjust ADSR for realistic piano response</li>
        <li>Add reverb and tone controls if desired</li>
        <li>Test with different velocities</li>
        </ol>
        
        <h3>🥁 Building a Drum Kit:</h3>
        <ol>
        <li>Import individual drum samples</li>
        <li>Map each drum to its own key range</li>
        <li>Set up velocity layers for dynamic response</li>
        <li>Use round-robin for variation</li>
        <li>Configure appropriate ADSR for each drum type</li>
        </ol>
        
        <h3>🎸 Guitar with Multiple Mic Positions:</h3>
        <ol>
        <li>Import close and distant mic samples</li>
        <li>Put both samples in the same group</li>
        <li>Tag samples as "mic_close" and "mic_distant"</li>
        <li>Create blend control for crossfading</li>
        <li>Test different blend positions</li>
        </ol>
        
        <h3>🎼 Orchestral Ensemble:</h3>
        <ol>
        <li>Import samples for different instrument sections</li>
        <li>Create simultaneous layers for rich texture</li>
        <li>Balance volumes between sections</li>
        <li>Add appropriate modulation for expression</li>
        <li>Use velocity layers for dynamics</li>
        </ol>
        """)
        workflow_text.setWordWrap(True)
        content_layout.addWidget(workflow_text)
        
        content.setLayout(content_layout)
        scroll_area.setWidget(content)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab
        
    def create_shortcuts_tab(self):
        """Create keyboard shortcuts tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        shortcuts_text = QLabel("""
        <h2>⌨️ Keyboard Shortcuts</h2>
        
        <h3>File Operations:</h3>
        <ul>
        <li><b>Ctrl+N:</b> New preset</li>
        <li><b>Ctrl+O:</b> Open preset</li>
        <li><b>Ctrl+S:</b> Save preset</li>
        <li><b>Ctrl+Z:</b> Undo</li>
        <li><b>Ctrl+Y:</b> Redo</li>
        </ul>
        
        <h3>Navigation:</h3>
        <ul>
        <li><b>Tab:</b> Switch between main tabs</li>
        <li><b>F1:</b> Show this help dialog</li>
        <li><b>Escape:</b> Close dialogs</li>
        </ul>
        
        <h3>Editing:</h3>
        <ul>
        <li><b>Enter:</b> Confirm changes</li>
        <li><b>Delete:</b> Remove selected items</li>
        <li><b>Ctrl+A:</b> Select all</li>
        </ul>
        
        <p><i>More shortcuts are available throughout the interface - look for underlined letters in menus and buttons.</i></p>
        """)
        shortcuts_text.setWordWrap(True)
        layout.addWidget(shortcuts_text)
        
        tab.setLayout(layout)
        return tab
        
    def create_troubleshooting_tab(self):
        """Create troubleshooting guide tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        scroll_area = QScrollArea()
        content = QWidget()
        content_layout = QVBoxLayout()
        
        troubleshooting_text = QLabel("""
        <h2>🔧 Troubleshooting</h2>
        
        <h3>Common Issues:</h3>
        
        <h4>Samples Not Playing:</h4>
        <ul>
        <li>Check that sample files exist and are accessible</li>
        <li>Verify samples are mapped to the correct key ranges</li>
        <li>Ensure velocity ranges don't conflict</li>
        <li>Check that groups are enabled</li>
        </ul>
        
        <h4>UI Elements Overlapping:</h4>
        <ul>
        <li>Try resizing the window</li>
        <li>Switch to a different tab to reduce clutter</li>
        <li>Use the responsive layout on larger screens</li>
        <li>Check screen resolution settings</li>
        </ul>
        
        <h4>Performance Issues:</h4>
        <ul>
        <li>Close unused tabs to free memory</li>
        <li>Reduce number of simultaneously loaded samples</li>
        <li>Use smaller sample files when possible</li>
        <li>Check Advanced Settings for optimization options</li>
        </ul>
        
        <h4>Export/Import Problems:</h4>
        <ul>
        <li>Ensure all sample paths are valid</li>
        <li>Check file permissions</li>
        <li>Verify preset contains required elements</li>
        <li>Use absolute paths for sample files when possible</li>
        </ul>
        
        <h3>Getting Help:</h3>
        <p>If you continue to experience issues:</p>
        <ul>
        <li>Check tooltips for context-sensitive help</li>
        <li>Use the Group Tutorial for sample organization help</li>
        <li>Consult the DecentSampler documentation</li>
        <li>Try creating a simple test preset to isolate issues</li>
        </ul>
        """)
        troubleshooting_text.setWordWrap(True)
        content_layout.addWidget(troubleshooting_text)
        
        content.setLayout(content_layout)
        scroll_area.setWidget(content)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        tab.setLayout(layout)
        return tab

def show_advanced_settings(parent=None, current_settings=None):
    """Show the advanced settings dialog"""
    dialog = AdvancedSettingsDialog(parent, current_settings)
    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_settings()
    return None

def show_help_dialog(parent=None, section="overview"):
    """Show the help dialog"""
    dialog = HelpDialog(parent, section)
    dialog.exec_()

def show_group_tutorial_modal(parent=None):
    """Show the group tutorial in a modal dialog"""
    try:
        from dialogs.grouping_tutorial import GroupingTutorialDialog
        dialog = GroupingTutorialDialog(parent)
        dialog.exec_()
    except ImportError:
        QMessageBox.information(parent, "Tutorial", 
            "Tutorial system not available. Please refer to the SAMPLE_GROUPING_GUIDE.md file for detailed explanations.")