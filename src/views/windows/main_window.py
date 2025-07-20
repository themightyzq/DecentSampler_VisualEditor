from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QMessageBox, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtWidgets import QUndoStack
from utils.error_handling import ErrorHandler, get_global_error_handler
from widgets.loading_indicators import LoadingOverlay, ProgressButton
from views.panels.sample_mapping_panel import SampleMappingPanel
from views.panels.global_options_panel import GlobalOptionsPanel
from panels.project_properties import ProjectPropertiesPanel
from views.panels.preview_canvas import PreviewCanvas
from panels.piano_keyboard import PianoKeyboardWidget
from panels.group_properties import GroupPropertiesWidget
from panels.modulation_panel import ModulationPanel
from panels.group_manager_panel import GroupManagerWidget
from utils.responsive_layout import AdaptiveLayoutManager, ResponsiveSizingMixin
from utils.modal_dialogs import show_advanced_settings, show_help_dialog, show_group_tutorial_modal
from utils.sample_streaming import get_streaming_manager
from utils.theme_manager import theme_manager, ThemeColors, ThemeSpacing

# Import enhanced UI components
from utils.enhanced_layout import LayoutGrid, create_section_separator
from widgets.smart_components import SmartTabWidget, WorkflowPanel, SmartButton
from utils.enhanced_typography import create_h2_label, create_body_label
from model import InstrumentPreset, SampleMapping, SampleZone
import controller
import os

# Import UI helpers for consistency
try:
    from utils.ui_helpers import StatusMessageManager, ErrorHandler
    from utils.tooltips import apply_tooltips_to_panel, MAIN_WINDOW_TOOLTIPS, get_workflow_help
    UI_HELPERS_AVAILABLE = True
except ImportError:
    UI_HELPERS_AVAILABLE = False
    print("Warning: UI helpers not available - using basic styling")

class PresetLoadWorker(QThread):
    """Background worker for preset loading"""
    preset_loaded = pyqtSignal(object)  # Loaded preset
    loading_error = pyqtSignal(str)     # Error message
    loading_progress = pyqtSignal(str)  # Progress message
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        """Load preset in background thread"""
        try:
            self.loading_progress.emit("Reading preset file...")
            
            # Validate file exists and is readable
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"File not found: {self.file_path}")
            if not os.access(self.file_path, os.R_OK):
                raise PermissionError(f"Cannot read file: {self.file_path}")
            
            self.loading_progress.emit("Parsing XML data...")
            
            # Load the preset
            preset = controller.load_preset(self.file_path)
            
            if not preset:
                raise ValueError("Invalid preset data")
            
            self.loading_progress.emit("Preset loaded successfully")
            self.preset_loaded.emit(preset)
            
        except Exception as e:
            self.loading_error.emit(str(e))

class PresetSaveWorker(QThread):
    """Background worker for preset saving"""
    preset_saved = pyqtSignal(str)      # Success message with file path
    saving_error = pyqtSignal(str)      # Error message
    saving_progress = pyqtSignal(str)   # Progress message
    
    def __init__(self, file_path, preset):
        super().__init__()
        self.file_path = file_path
        self.preset = preset
        
    def run(self):
        """Save preset in background thread"""
        try:
            self.saving_progress.emit("Validating preset data...")
            
            # Basic validation
            if not self.preset:
                raise ValueError("No preset data to save")
            
            self.saving_progress.emit("Generating XML...")
            
            # Save the preset
            controller.save_preset(self.file_path, self.preset)
            
            self.saving_progress.emit("Preset saved successfully")
            self.preset_saved.emit(self.file_path)
            
        except Exception as e:
            self.saving_error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DecentSampler Preset Editor")
        self.setGeometry(100, 100, 1200, 800)
        self.undo_stack = QUndoStack(self)
        self.preset = None
        
        # Set up error handling
        self.error_handler = get_global_error_handler(self)
        
        # Initialize streaming manager
        self.streaming_manager = get_streaming_manager(cache_size_mb=512)
        
        # Initialize status message manager
        if UI_HELPERS_AVAILABLE:
            self.status_manager = StatusMessageManager(self.statusBar())
        
        # Loading workers and overlay
        self.load_worker = None
        self.save_worker = None
        self.loading_overlay = LoadingOverlay(self)
        
        # Apply centralized theme - no need for individual theme application
        # Theme is now applied globally at application level

        self._create_menu()
        self._create_central()
        self._createGlobalOptionsPanel()
        self._connectSignals()
        self._apply_tooltips()
        self.showMaximized()
        self.new_preset()  # Always start with a blank preset
        
        # Apply UI fixes after all components are created
        from utils.ui_fixes import UIFixes
        UIFixes.apply_all_fixes(self)
        
        # Responsive design - panel sizing handled in _createGlobalOptionsPanel()
        # No fixed width/height constraints needed with responsive layout

    def _create_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_preset)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        open_action = QAction("Open...", self)
        open_action.triggered.connect(self.open_preset)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_preset)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        undo_action = self.undo_stack.createUndoAction(self, "Undo")
        undo_action.setShortcut("Ctrl+Z")
        redo_action = self.undo_stack.createRedoAction(self, "Redo")
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        preferences_action = QAction("Advanced Settings...", self)
        preferences_action.triggered.connect(self.show_advanced_settings)
        edit_menu.addAction(preferences_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        # Tab switching actions
        samples_tab_action = QAction("Samples Tab", self)
        samples_tab_action.setShortcut("Ctrl+1")
        samples_tab_action.triggered.connect(lambda: self.main_tabs.setCurrentIndex(0))
        view_menu.addAction(samples_tab_action)
        
        properties_tab_action = QAction("Properties Tab", self)
        properties_tab_action.setShortcut("Ctrl+2")
        properties_tab_action.triggered.connect(lambda: self.main_tabs.setCurrentIndex(1))
        view_menu.addAction(properties_tab_action)
        
        modulation_tab_action = QAction("Modulation Tab", self)
        modulation_tab_action.setShortcut("Ctrl+3")
        modulation_tab_action.triggered.connect(lambda: self.main_tabs.setCurrentIndex(2))
        view_menu.addAction(modulation_tab_action)
        
        groups_tab_action = QAction("Groups Tab", self)
        groups_tab_action.setShortcut("Ctrl+4")
        groups_tab_action.triggered.connect(lambda: self.main_tabs.setCurrentIndex(3))
        view_menu.addAction(groups_tab_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        help_action = QAction("Help & Documentation", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        tutorial_action = QAction("Sample Grouping Tutorial", self)
        tutorial_action.triggered.connect(self.show_group_tutorial)
        help_menu.addAction(tutorial_action)
        
        help_menu.addSeparator()
        
        # Check dependencies action
        check_deps_action = QAction("Check Dependencies...", self)
        check_deps_action.triggered.connect(self.check_dependencies)
        help_menu.addAction(check_deps_action)
        
        help_menu.addSeparator()
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _create_central(self):
        # Create simple enhanced layout without extra panels
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(LayoutGrid.SPACING_MEDIUM, LayoutGrid.SPACING_MEDIUM, 
                                     LayoutGrid.SPACING_MEDIUM, LayoutGrid.SPACING_MEDIUM)
        main_layout.setSpacing(LayoutGrid.SPACING_LARGE)
        
        # Create and setup panels with enhanced layout
        self._create_panels()
        self._setup_enhanced_layout(main_layout)
        
        # Set as central widget
        self.setCentralWidget(central_widget)
        
    def _create_panels(self):
        """Create all UI panels with responsive capabilities"""
        # Sample mapping panel (goes in sidebar)
        self.sample_mapping_panel = SampleMappingPanel(self)
        # Sample mapping panel is now handled by enhanced layout system
        
        # Preview canvas (responsive size)
        self.preview_canvas = PreviewCanvas(self)
        # Remove fixed size constraints for responsive design
        self.preview_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # Set minimum size for responsive design
        self.preview_canvas.setMinimumSize(400, 200)
        
        # Piano keyboard (responsive width)
        self.piano_keyboard = PianoKeyboardWidget(main_window=self)
        self.piano_keyboard.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.piano_keyboard.setMinimumHeight(80)
        self.piano_keyboard.setMaximumHeight(120)
        # Remove fixed width for responsive design
        
        # Group properties (ADSR) - responsive width
        self.group_properties_panel_widget = GroupPropertiesWidget(main_window=self)
        self.group_properties_panel_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # Remove fixed width constraint
        
        # Modulation panel - responsive width
        self.modulation_panel = ModulationPanel()
        self.modulation_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # Remove fixed width constraint
        
        # Group manager - responsive width
        self.group_manager = GroupManagerWidget()
        self.group_manager.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # Remove fixed width constraint
        
    def _apply_responsive_sizing(self):
        """Apply responsive sizing to all panels"""
        panels = [
            self.sample_mapping_panel,
            self.preview_canvas,
            self.piano_keyboard,
            self.group_properties_panel_widget,
            self.modulation_panel,
            self.group_manager
        ]
        
        # Responsive sizing is now handled by enhanced layout components
        pass
        
    def _setup_enhanced_layout(self, main_layout):
        """Setup enhanced layout with smart components"""
        # Create sidebar with sample mapping panel
        sidebar_panel = WorkflowPanel("Sample Management", help_text="Import and organize your audio samples")
        sidebar_panel.set_content(self.sample_mapping_panel)
        sidebar_panel.setMinimumWidth(LayoutGrid.SIDEBAR_MIN_WIDTH)
        sidebar_panel.setMaximumWidth(LayoutGrid.SIDEBAR_PREFERRED_WIDTH)
        main_layout.addWidget(sidebar_panel)
        
        # Create main content with smart tabs
        self.main_tabs = SmartTabWidget()
        
        # Samples tab with workflow panel
        samples_layout = QVBoxLayout()
        
        # Preview canvas with enhanced styling
        preview_header = create_h2_label("Instrument Preview")
        samples_layout.addWidget(preview_header)
        samples_layout.addWidget(self.preview_canvas)
        samples_layout.addWidget(create_section_separator())
        
        # Piano keyboard with enhanced layout
        keyboard_header = create_h2_label("Keyboard Mapping")
        samples_layout.addWidget(keyboard_header)
        samples_layout.addWidget(self.piano_keyboard)
        
        # Add keyboard legend
        from panels.piano_keyboard import KeyboardLegendWidget
        self.keyboard_legend = KeyboardLegendWidget()
        samples_layout.addWidget(self.keyboard_legend)
        
        samples_widget = QWidget()
        samples_widget.setLayout(samples_layout)
        
        # Add tabs with workflow optimization
        self.main_tabs.add_workflow_tab(
            samples_widget, "Main", "🎹", 
            "Sample visualization and keyboard mapping", "Ctrl+1"
        )
        
        # ADSR tab
        self.main_tabs.add_workflow_tab(
            self.group_properties_panel_widget, "ADSR", "📈", 
            "Envelope and dynamics controls", "Ctrl+2"
        )
        
        # Modulation tab
        self.main_tabs.add_workflow_tab(
            self.modulation_panel, "Modulation", "🌊", 
            "LFO and modulation controls", "Ctrl+3"
        )
        
        # Groups tab
        self.main_tabs.add_workflow_tab(
            self.group_manager, "Groups", "📁", 
            "Sample group management", "Ctrl+4"
        )
        
        main_layout.addWidget(self.main_tabs, 2)  # Give main tabs more space
        
        # Connect visual mapping after all components are created
        self._connect_visual_mapping()
    
    def _connect_visual_mapping(self):
        """Connect visual mapping functionality between piano keyboard and sample panel"""
        try:
            if hasattr(self, 'piano_keyboard') and hasattr(self, 'sample_mapping_panel'):
                # Ensure the signal isn't already connected to avoid duplicate connections
                try:
                    self.piano_keyboard.rangeSelected.disconnect()
                except TypeError:
                    # No connections exist yet, which is fine
                    pass
                
                # Connect the signal
                self.piano_keyboard.rangeSelected.connect(self.sample_mapping_panel._on_range_selected)
                
                # Also connect sample selection to update keyboard visualization
                if hasattr(self.sample_mapping_panel, 'table_widget'):
                    self.sample_mapping_panel.table_widget.selectionModel().selectionChanged.connect(
                        self._update_keyboard_visualization
                    )
                
                # Verify the connection was successful
                if self.piano_keyboard.receivers(self.piano_keyboard.rangeSelected) > 0:
                    # Connection successful - visual mapping is ready
                    pass
                else:
                    self.error_handler.handle_error(
                        Exception("Failed to connect visual mapping signal"),
                        "verifying visual mapping connection",
                        show_dialog=False
                    )
            else:
                # Log which component is missing for debugging
                missing = []
                if not hasattr(self, 'piano_keyboard'):
                    missing.append('piano_keyboard')
                if not hasattr(self, 'sample_mapping_panel'):
                    missing.append('sample_mapping_panel')
                if missing:
                    self.error_handler.handle_error(
                        Exception(f"Missing components: {', '.join(missing)}"),
                        "setting up visual mapping",
                        show_dialog=False
                    )
        except Exception as e:
            self.error_handler.handle_error(e, "connecting visual mapping signals", show_dialog=False)

    def _createGlobalOptionsPanel(self):
        def show_error(parent, title, msg):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(parent, title, msg)
        from PyQt5.QtWidgets import QDockWidget
        try:
            self.global_options_panel = ProjectPropertiesPanel(self)
        except Exception as e:
            show_error(self, "Panel init failed", str(e))
            raise
        self.addDockWidget(Qt.RightDockWidgetArea, self.global_options_panel)
        
        # Set responsive panel sizing
        self.global_options_panel.setMinimumWidth(350)
        self.global_options_panel.setMaximumWidth(450)

    def _connectSignals(self):
        # Enhanced signal connections with proper error handling
        try:
            # Connect ADSR changes with validation (now in Properties tab)
            if hasattr(self, 'group_properties_panel_widget'):
                self.group_properties_panel_widget.attack_card.value_spin.valueChanged.connect(
                    lambda: self._safe_adsr_update("attack"))
                self.group_properties_panel_widget.decay_card.value_spin.valueChanged.connect(
                    lambda: self._safe_adsr_update("decay"))
                self.group_properties_panel_widget.sustain_card.value_spin.valueChanged.connect(
                    lambda: self._safe_adsr_update("sustain"))
                self.group_properties_panel_widget.release_card.value_spin.valueChanged.connect(
                    lambda: self._safe_adsr_update("release"))
            
            # Connect modulation changes (now in Modulation tab)
            if hasattr(self, 'modulation_panel'):
                self.modulation_panel.modulationChanged.connect(self._safe_modulation_update)
                
            # Connect group manager changes (now in Groups tab)
            if hasattr(self, 'group_manager'):
                self.group_manager.groupsChanged.connect(self._groups_update)
                
            # Connect keyboard interaction signals
            if hasattr(self, 'piano_keyboard'):
                self.piano_keyboard.noteClicked.connect(self._on_keyboard_note_clicked)
                self.piano_keyboard.mappingHovered.connect(self._on_keyboard_mapping_hovered)
                
            # Layout adaptation is now handled by enhanced layout system
                
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_validation_error("Signal Connections", e, self)
            else:
                self.error_handler.handle_error(e, "connecting group manager signals", show_dialog=False)
                
    def _on_layout_changed(self):
        """Handle layout changes when screen size changes"""
        try:
            # Recreate global options panel with new sizing if needed
            # Panel sizing is now handled by enhanced responsive system
            pass
                    
            if UI_HELPERS_AVAILABLE:
                self.status_manager.show_message("Layout adapted to screen size", "info", 2000)
                
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_validation_error("Layout Change", e, self)
            else:
                self.error_handler.handle_error(e, "handling layout change", show_dialog=False)
                
    def _apply_tooltips(self):
        """Apply comprehensive tooltips to all UI elements"""
        if not UI_HELPERS_AVAILABLE:
            return
            
        try:
            # Apply tooltips to menu items
            for action in self.menuBar().actions():
                action_name = action.text().replace("&", "").lower().replace(" ", "_")
                tooltip = MAIN_WINDOW_TOOLTIPS.get(f"menu_{action_name}", "")
                if tooltip:
                    action.setToolTip(tooltip)
                    
            # Apply tooltips to panels
            if hasattr(self, 'sample_mapping_panel'):
                apply_tooltips_to_panel(self.sample_mapping_panel, 'sample_mapping')
            if hasattr(self, 'group_properties_panel_widget'):
                apply_tooltips_to_panel(self.group_properties_panel_widget, 'adsr')
            if hasattr(self, 'global_options_panel'):
                apply_tooltips_to_panel(self.global_options_panel, 'project')
            if hasattr(self, 'modulation_panel'):
                apply_tooltips_to_panel(self.modulation_panel, 'modulation')
                
        except Exception as e:
            self.error_handler.handle_error(e, "applying UI tooltips", show_dialog=False)
            
    def _safe_adsr_update(self, parameter_name):
        """Safely update ADSR with error handling and validation"""
        try:
            self._adsr_update(0)  # Call original method
            if UI_HELPERS_AVAILABLE:
                self.status_manager.show_message(f"Updated {parameter_name.title()} parameter", "success", 2000)
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_validation_error(f"ADSR {parameter_name.title()}", e, self)
            else:
                self.error_handler.handle_error(e, f"updating ADSR {parameter_name}", show_dialog=False)
                
    def _safe_modulation_update(self):
        """Safely update modulation with error handling"""
        try:
            self._modulation_update()
            if UI_HELPERS_AVAILABLE:
                self.status_manager.show_message("Modulation settings updated", "success", 2000)
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_validation_error("Modulation", e, self)
            else:
                self.error_handler.handle_error(e, "updating modulation settings", show_dialog=False)
                
    def _groups_update(self):
        """Update model groups data and preview"""
        if not self.preset or not hasattr(self, "group_manager"):
            return
        try:
            groups = self.group_manager.get_groups()
            self.preset.sample_groups = groups
            if hasattr(self, "preview_canvas"):
                self.preview_canvas.set_preset(self.preset, os.getcwd())
            if UI_HELPERS_AVAILABLE:
                self.status_manager.show_message("Sample groups updated", "success", 2000)
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_validation_error("Sample Groups", e, self)
            else:
                self.error_handler.handle_error(e, "updating group display", show_dialog=False)

    def new_preset(self):
        self.preset = InstrumentPreset("Untitled")
        self.preset.ui_width = 812
        self.preset.ui_height = 375
        # No test UI element; real controls will be added via the properties panel
        self.sample_mapping_panel.set_samples([])
        self.sample_mapping_panel.set_mapping(None)
        self.undo_stack.clear()
        self._set_options_panel_from_preset()
        self.modulation_panel.set_modulation_data(self.preset.lfos, self.preset.modulation_routes)
        self.group_manager.set_groups(getattr(self.preset, 'sample_groups', []))
        self.preview_canvas.set_preset(self.preset, os.getcwd())
        
        # Update keyboard visualization
        self._update_keyboard_visualization()
        
        # Status/help message with better guidance
        if UI_HELPERS_AVAILABLE:
            self.status_manager.show_message("Welcome! Start by importing samples, then map them to keys, configure effects, and save your preset.", "info", 5000)
        else:
            self.statusBar().showMessage("Steps: 1) Import samples  2) Map to keys  3) Configure effects  4) Preview  5) Save")

    def open_preset(self):
        """Open a preset file with comprehensive error handling"""
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open DecentSampler Preset", 
            "", 
            "DecentSampler Preset (*.dspreset);;All Files (*)"
        )
        if not path:
            return
        
        # Stop any existing load worker
        if self.load_worker and self.load_worker.isRunning():
            self.load_worker.terminate()
            self.load_worker.wait()
        
        # Show loading overlay
        self.loading_overlay.showWithText("Loading preset...")
        
        # Disable UI during loading
        self.menuBar().setEnabled(False)
        
        # Start async loading
        self.load_worker = PresetLoadWorker(path)
        self.load_worker.preset_loaded.connect(self._on_preset_loaded)
        self.load_worker.loading_error.connect(self._on_preset_load_error)
        self.load_worker.loading_progress.connect(self._on_preset_load_progress)
        self.load_worker.start()
    
    def _on_preset_loaded(self, preset):
        """Handle successful preset loading"""
        try:
            self.preset = preset
                
            # Update UI components safely
            sample_mappings = getattr(self.preset, 'mappings', [])
            self.sample_mapping_panel.set_samples(list(sample_mappings))
            
            if sample_mappings:
                self.sample_mapping_panel.set_mapping(sample_mappings[0])
            else:
                self.sample_mapping_panel.set_mapping(None)
                
            # Update panels with validation
            self.undo_stack.clear()
            self._set_options_panel_from_preset()
            
            # Update modulation data
            lfos = getattr(self.preset, 'lfos', [])
            routes = getattr(self.preset, 'modulation_routes', [])
            self.modulation_panel.set_modulation_data(lfos, routes)
            
            # Update groups data
            groups = getattr(self.preset, 'sample_groups', [])
            self.group_manager.set_groups(groups)
            
            # Update preview
            self.preview_canvas.set_preset(self.preset, os.path.dirname(self.load_worker.file_path))
            
            # Update keyboard visualization
            self._update_keyboard_visualization()
            
            # Hide loading overlay and re-enable UI
            self.loading_overlay.hide()
            self.menuBar().setEnabled(True)
            
            # Success feedback
            if UI_HELPERS_AVAILABLE:
                self.status_manager.show_message(f"Successfully loaded: {os.path.basename(self.load_worker.file_path)}", "success", 3000)
            else:
                self.statusBar().showMessage(f"Loaded: {os.path.basename(self.load_worker.file_path)}", 3000)
                
        except Exception as e:
            # Hide loading overlay and re-enable UI on error
            self.loading_overlay.hide()
            self.menuBar().setEnabled(True)
            
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_file_error("loading", self.load_worker.file_path, e, self)
            else:
                QMessageBox.critical(self, "Error Loading Preset", f"Failed to load preset:\n{str(e)}")
    
    def _on_preset_load_error(self, error_message):
        """Handle preset loading errors"""
        # Hide loading overlay and re-enable UI
        self.loading_overlay.hide()
        self.menuBar().setEnabled(True)
        
        QMessageBox.critical(self, "Error Loading Preset", f"Failed to load preset:\n{error_message}")
    
    def _on_preset_load_progress(self, message):
        """Handle preset loading progress updates"""
        self.loading_overlay.label.setText(message)

    def save_preset(self):
        """Save preset with comprehensive validation and error handling"""
        if not self.preset:
            QMessageBox.warning(self, "No Preset", "No preset loaded to save.")
            return
            
        try:
            # Pre-save validation
            validation_errors = self._validate_preset_for_save()
            if validation_errors:
                error_msg = "Please fix the following issues before saving:\n\n" + "\n".join(validation_errors)
                QMessageBox.warning(self, "Validation Errors", error_msg)
                return
            
            # Update preset from UI panels
            self._update_preset_from_ui()
            
            # Get save path with better default naming
            default_name = getattr(self.preset, 'name', 'Untitled').replace(' ', '_')
            if not default_name.endswith('.dspreset'):
                default_name += '.dspreset'
                
            path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save DecentSampler Preset", 
                default_name,
                "DecentSampler Preset (*.dspreset);;All Files (*)"
            )
            if not path:
                return
                
            # Ensure .dspreset extension
            if not path.lower().endswith('.dspreset'):
                path += '.dspreset'
            
            # Stop any existing save worker
            if self.save_worker and self.save_worker.isRunning():
                self.save_worker.terminate()
                self.save_worker.wait()
            
            # Show loading overlay
            self.loading_overlay.showWithText("Saving preset...")
            
            # Disable UI during saving
            self.menuBar().setEnabled(False)
            
            # Start async saving
            self.save_worker = PresetSaveWorker(path, self.preset)
            self.save_worker.preset_saved.connect(self._on_preset_saved)
            self.save_worker.saving_error.connect(self._on_preset_save_error)
            self.save_worker.saving_progress.connect(self._on_preset_save_progress)
            self.save_worker.start()
            
        except Exception as e:
            # Hide loading overlay and re-enable UI on error
            self.loading_overlay.hide()
            self.menuBar().setEnabled(True)
            
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_file_error("saving", path if 'path' in locals() else "preset", e, self)
            else:
                QMessageBox.critical(self, "Error Saving Preset", f"Failed to save preset:\n{str(e)}")
    
    def _on_preset_saved(self, file_path):
        """Handle successful preset saving"""
        # Hide loading overlay and re-enable UI
        self.loading_overlay.hide()
        self.menuBar().setEnabled(True)
        
        # Update preview with new path
        self.preview_canvas.set_preset(self.preset, os.path.dirname(file_path))
        
        # Success feedback
        if UI_HELPERS_AVAILABLE:
            self.status_manager.show_message(f"Successfully saved: {os.path.basename(file_path)}", "success", 3000)
        else:
            self.statusBar().showMessage(f"Saved: {os.path.basename(file_path)}", 3000)
    
    def _on_preset_save_error(self, error_message):
        """Handle preset saving errors"""
        # Hide loading overlay and re-enable UI
        self.loading_overlay.hide()
        self.menuBar().setEnabled(True)
        
        QMessageBox.critical(self, "Error Saving Preset", f"Failed to save preset:\n{error_message}")
    
    def _on_preset_save_progress(self, message):
        """Handle preset saving progress updates"""
        self.loading_overlay.label.setText(message)
                
    def _validate_preset_for_save(self):
        """Validate preset data before saving"""
        errors = []
        
        try:
            # Check basic preset data
            if not hasattr(self.preset, 'name') or not self.preset.name.strip():
                errors.append("• Preset name is required")
                
            # Check for samples
            mappings = getattr(self.preset, 'mappings', [])
            if not mappings:
                # Check sample manager as backup
                sample_manager = getattr(self.preset, 'sample_manager', None)
                if not sample_manager or not sample_manager.get_zones():
                    errors.append("• At least one sample must be imported and mapped")
                    
            # Validate sample files exist
            for mapping in mappings:
                if hasattr(mapping, 'path') and mapping.path:
                    if not os.path.exists(mapping.path):
                        errors.append(f"• Sample file not found: {os.path.basename(mapping.path)}")
                        
            # Check UI dimensions are reasonable
            if hasattr(self.preset, 'ui_width') and (self.preset.ui_width < 100 or self.preset.ui_width > 2000):
                errors.append("• UI width should be between 100 and 2000 pixels")
            if hasattr(self.preset, 'ui_height') and (self.preset.ui_height < 100 or self.preset.ui_height > 1500):
                errors.append("• UI height should be between 100 and 1500 pixels")
                
            # Validate modulation data
            lfos = getattr(self.preset, 'lfos', [])
            routes = getattr(self.preset, 'modulation_routes', [])
            if routes and not lfos:
                errors.append("• Modulation routes exist but no LFOs are defined")
                
        except Exception as e:
            errors.append(f"• Validation error: {str(e)}")
            
        return errors
        
    def _update_preset_from_ui(self):
        """Update preset object from all UI panels"""
        try:
            # Update from options panel
            if hasattr(self, 'global_options_panel'):
                opts = self.global_options_panel.get_options()
                self.preset.bg_image = opts.get("bg_image", "")
                self.preset.have_tone = opts.get("have_tone", False)
                self.preset.have_chorus = opts.get("have_chorus", False)  
                self.preset.have_reverb = opts.get("have_reverb", False)
                self.preset.have_midicc1 = opts.get("have_midicc1", False)
                self.preset.cut_all_by_all = opts.get("cut_all_by_all", False)
                self.preset.silencing_mode = opts.get("silencing_mode", "normal")
                
            # Update ADSR flags from group properties
            if hasattr(self, 'group_properties_panel_widget'):
                self.preset.have_attack = self.group_properties_panel_widget.attack_card.enable_cb.isChecked()
                self.preset.have_decay = self.group_properties_panel_widget.decay_card.enable_cb.isChecked()
                self.preset.have_sustain = self.group_properties_panel_widget.sustain_card.enable_cb.isChecked()
                self.preset.have_release = self.group_properties_panel_widget.release_card.enable_cb.isChecked()
                
            # Update sample mappings with better validation
            valid_mappings = []
            for m in getattr(self.sample_mapping_panel, 'samples', []):
                try:
                    if isinstance(m, dict):
                        if all(k in m for k in ("path", "lo", "hi", "root")):
                            valid_mappings.append(SampleMapping(m["path"], m["lo"], m["hi"], m["root"]))
                    elif hasattr(m, "path") and hasattr(m, "lo") and hasattr(m, "hi") and hasattr(m, "root"):
                        valid_mappings.append(m)
                except Exception as e:
                    self.error_handler.handle_error(e, "validating sample mapping", show_dialog=False)
                    
            self.preset.mappings = valid_mappings
            
            # Update modulation data
            if hasattr(self, 'modulation_panel'):
                lfos, routes = self.modulation_panel.get_modulation_data()
                self.preset.lfos = lfos
                self.preset.modulation_routes = routes
                
        except Exception as e:
            self.error_handler.handle_error(e, "updating preset from UI changes", show_dialog=False)

    def _set_options_panel_from_preset(self):
        if not self.preset:
            return
        panel = self.global_options_panel
        panel.preset_name_edit.setText(self.preset.name)
        panel.ui_width_spin.setValue(self.preset.ui_width)
        panel.ui_height_spin.setValue(self.preset.ui_height)
        panel.bg_color_edit.setText(getattr(self.preset, "bg_color", "") or "")
        if hasattr(panel, "bg_color_btn"):
            panel.bg_color_btn.setText(getattr(self.preset, "bg_color", "") or "")
        panel.bg_image_edit.setText(self.preset.bg_image or "")
        # Set ADSR controls from model envelope
        if hasattr(self, "group_properties_panel_widget") and hasattr(self.preset, "envelope"):
            env = self.preset.envelope
            self.group_properties_panel_widget.set_adsr(env.attack, env.decay, env.sustain, env.release)

    def _adsr_update(self, val):
        # Update model envelope and preview on ADSR change
        if not self.preset or not hasattr(self, "group_properties_panel_widget"):
            return
        attack, decay, sustain, release = self.group_properties_panel_widget.get_adsr()
        if hasattr(self.preset, "envelope"):
            self.preset.envelope.attack = attack
            self.preset.envelope.decay = decay
            self.preset.envelope.sustain = sustain
            self.preset.envelope.release = release
        if hasattr(self, "preview_canvas"):
            self.preview_canvas.set_preset(self.preset, os.getcwd())
            
    def _modulation_update(self):
        # Update model modulation data and preview
        if not self.preset or not hasattr(self, "modulation_panel"):
            return
        lfos, routes = self.modulation_panel.get_modulation_data()
        self.preset.lfos = lfos
        self.preset.modulation_routes = routes
        if hasattr(self, "preview_canvas"):
            self.preview_canvas.set_preset(self.preset, os.getcwd())
    
    # Modal Dialog Methods
    def show_advanced_settings(self):
        """Show advanced settings modal dialog"""
        try:
            current_settings = getattr(self, 'app_settings', {})
            new_settings = show_advanced_settings(self, current_settings)
            if new_settings is not None:
                self.app_settings = new_settings
                if UI_HELPERS_AVAILABLE:
                    self.status_manager.show_message("Settings updated", "success", 2000)
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_validation_error("Advanced Settings", e, self)
            else:
                QMessageBox.critical(self, "Error", f"Failed to open settings: {str(e)}")
    
    def show_help(self):
        """Show help and documentation modal dialog"""
        try:
            show_help_dialog(self)
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_validation_error("Help Dialog", e, self)
            else:
                QMessageBox.critical(self, "Error", f"Failed to open help: {str(e)}")
    
    def show_group_tutorial(self):
        """Show sample grouping tutorial modal dialog"""
        try:
            show_group_tutorial_modal(self)
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_validation_error("Group Tutorial", e, self)
            else:
                QMessageBox.critical(self, "Error", f"Failed to open tutorial: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        try:
            about_text = """
            <h2>DecentSampler Preset Editor</h2>
            <p><b>Version:</b> 2.0 Responsive Edition</p>
            <p><b>Description:</b> Professional sample instrument creation tool for DecentSampler</p>
            
            <h3>Features:</h3>
            <ul>
            <li>Responsive UI that adapts to any screen size</li>
            <li>Advanced sample grouping and organization</li>
            <li>Complete modulation system with LFOs</li>
            <li>Professional workflow with tabbed interface</li>
            <li>Comprehensive help and tutorial system</li>
            </ul>
            
            <p><i>Built with PyQt5 and modern UI/UX principles</i></p>
            """
            
            QMessageBox.about(self, "About DecentSampler Preset Editor", about_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show about dialog: {str(e)}")
    
    # Keyboard interaction handlers
    def _on_keyboard_note_clicked(self, midi_note):
        """Handle piano keyboard note clicks"""
        try:
            # Show which sample is triggered for this note
            if UI_HELPERS_AVAILABLE:
                note_name = self.piano_keyboard.midi_note_name(midi_note)
                self.status_manager.show_message(f"Playing {note_name} (MIDI {midi_note})", "info", 2000)
                
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_validation_error("Keyboard Note Click", e, self)
            else:
                self.error_handler.handle_error(e, "playing sample preview", show_dialog=True)
    
    def _on_keyboard_mapping_hovered(self, mapping_info):
        """Handle keyboard mapping hover events"""
        try:
            # Could show mapping info in status bar or update a detail panel
            if UI_HELPERS_AVAILABLE and mapping_info:
                sample_name = mapping_info.get('name', 'Unknown')
                self.status_manager.show_message(f"Hovering over: {sample_name}", "info", 1000)
                
        except Exception as e:
            self.error_handler.handle_error(e, "handling keyboard hover", show_dialog=False)
    
    def _update_keyboard_visualization(self):
        """Update keyboard visual indicators when mappings change"""
        try:
            if hasattr(self, 'piano_keyboard'):
                # Refresh the keyboard visualization
                self.piano_keyboard.refresh_mappings()
                
                # Update the legend
                if hasattr(self, 'keyboard_legend'):
                    legend_items = self.piano_keyboard.get_mapping_legend()
                    self.keyboard_legend.update_legend(legend_items)
                    
        except Exception as e:
            self.error_handler.handle_error(e, "updating keyboard visualization", show_dialog=False)
    
    def check_dependencies(self):
        """Show dialog with dependency check results"""
        self.error_handler.show_dependency_status()
