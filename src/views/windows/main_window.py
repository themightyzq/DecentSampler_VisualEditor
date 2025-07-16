from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QMessageBox, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QUndoStack
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
from model import InstrumentPreset, SampleMapping, SampleZone
import controller
import os

# Import UI helpers for consistency
try:
    from utils.ui_helpers import apply_dark_theme, StatusMessageManager, ErrorHandler
    from utils.tooltips import apply_tooltips_to_panel, MAIN_WINDOW_TOOLTIPS, get_workflow_help
    UI_HELPERS_AVAILABLE = True
except ImportError:
    UI_HELPERS_AVAILABLE = False
    print("Warning: UI helpers not available - using basic styling")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DecentSampler Preset Editor")
        self.setGeometry(100, 100, 1200, 800)
        self.undo_stack = QUndoStack(self)
        self.preset = None
        
        # Initialize status message manager
        if UI_HELPERS_AVAILABLE:
            self.status_manager = StatusMessageManager(self.statusBar())
        
        # Apply consistent dark theme
        if UI_HELPERS_AVAILABLE:
            apply_dark_theme(self)

        self._create_menu()
        self._create_central()
        self._createGlobalOptionsPanel()
        self._connectSignals()
        self._apply_tooltips()
        self.showMaximized()
        self.new_preset()  # Always start with a blank preset
        
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
        samples_tab_action.triggered.connect(lambda: self.layout_manager.set_active_tab("samples"))
        view_menu.addAction(samples_tab_action)
        
        properties_tab_action = QAction("Properties Tab", self)
        properties_tab_action.setShortcut("Ctrl+2")
        properties_tab_action.triggered.connect(lambda: self.layout_manager.set_active_tab("properties"))
        view_menu.addAction(properties_tab_action)
        
        modulation_tab_action = QAction("Modulation Tab", self)
        modulation_tab_action.setShortcut("Ctrl+3")
        modulation_tab_action.triggered.connect(lambda: self.layout_manager.set_active_tab("modulation"))
        view_menu.addAction(modulation_tab_action)
        
        groups_tab_action = QAction("Groups Tab", self)
        groups_tab_action.setShortcut("Ctrl+4")
        groups_tab_action.triggered.connect(lambda: self.layout_manager.set_active_tab("groups"))
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
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _create_central(self):
        # Create responsive layout manager
        self.layout_manager = AdaptiveLayoutManager()
        
        # Create and setup panels with responsive sizing
        self._create_panels()
        self._apply_responsive_sizing()
        self._organize_panels_in_tabs()
        
        # Set as central widget
        self.setCentralWidget(self.layout_manager)
        
    def _create_panels(self):
        """Create all UI panels with responsive capabilities"""
        # Sample mapping panel (goes in sidebar)
        self.sample_mapping_panel = SampleMappingPanel(self)
        if isinstance(self.sample_mapping_panel, ResponsiveSizingMixin):
            self.sample_mapping_panel.apply_responsive_sizing(self.layout_manager)
        
        # Preview canvas (responsive size)
        self.preview_canvas = PreviewCanvas(self)
        # Remove fixed size constraints for responsive design
        self.preview_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # Set optimal size based on screen size
        optimal_size = self.layout_manager.get_optimal_widget_size(812, 375)
        self.preview_canvas.setMinimumSize(400, 200)
        self.preview_canvas.resize(optimal_size)
        
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
        
        for panel in panels:
            if hasattr(panel, 'apply_responsive_sizing'):
                panel.apply_responsive_sizing(self.layout_manager)
        
    def _organize_panels_in_tabs(self):
        """Organize panels into logical workflow tabs"""
        # Add sample mapping to sidebar
        sidebar_layout = self.layout_manager.get_sidebar_container()
        sidebar_layout.addWidget(self.sample_mapping_panel)
        
        # Samples tab: Preview + Piano Keyboard + Legend
        self.layout_manager.add_to_samples_tab(self.preview_canvas)
        self.layout_manager.add_to_samples_tab(self.piano_keyboard)
        
        # Add keyboard legend
        from panels.piano_keyboard import KeyboardLegendWidget
        self.keyboard_legend = KeyboardLegendWidget()
        self.layout_manager.add_to_samples_tab(self.keyboard_legend)
        
        # Properties tab: ADSR controls (will show global options in dock)
        self.layout_manager.add_to_properties_tab(self.group_properties_panel_widget, "adsr")
        
        # Modulation tab: Modulation panel
        self.layout_manager.add_to_modulation_tab(self.modulation_panel)
        
        # Groups tab: Group manager
        self.layout_manager.add_to_groups_tab(self.group_manager)
        
        # Set default active tab
        self.layout_manager.set_active_tab("samples")
        
        # Connect visual mapping after all components are created
        self._connect_visual_mapping()
    
    def _connect_visual_mapping(self):
        """Connect visual mapping functionality between piano keyboard and sample panel"""
        try:
            if hasattr(self, 'piano_keyboard') and hasattr(self, 'sample_mapping_panel'):
                self.piano_keyboard.rangeSelected.connect(self.sample_mapping_panel._on_range_selected)
        except Exception as e:
            print(f"Warning: Could not connect visual mapping: {e}")

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
        
        # Make the options panel responsive
        screen_info = self.layout_manager.screen_info if hasattr(self, 'layout_manager') else None
        if screen_info:
            if self.layout_manager.layout_mode in ["large", "medium"]:
                # Standard docked panel for larger screens
                self.global_options_panel.setMinimumWidth(350)
                self.global_options_panel.setMaximumWidth(500)
            else:
                # Narrower panel for smaller screens
                self.global_options_panel.setMinimumWidth(250)
                self.global_options_panel.setMaximumWidth(350)
        else:
            # Fallback to medium size
            self.global_options_panel.setMinimumWidth(350)
            self.global_options_panel.setMaximumWidth(450)
            
        # Lock properties panel to prevent undocking on small screens
        if hasattr(self, 'layout_manager') and self.layout_manager.layout_mode in ["small", "compact"]:
            self.global_options_panel.setFeatures(self.global_options_panel.NoDockWidgetFeatures)

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
                
            # Connect layout manager changes for screen size adaptation
            if hasattr(self, 'layout_manager'):
                self.layout_manager.layoutChanged.connect(self._on_layout_changed)
                
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_validation_error("Signal Connections", e, self)
            else:
                print(f"Warning: Error connecting signals: {e}")
                
    def _on_layout_changed(self):
        """Handle layout changes when screen size changes"""
        try:
            # Recreate global options panel with new sizing if needed
            if hasattr(self, 'global_options_panel'):
                # Update panel sizing based on new layout mode
                if self.layout_manager.layout_mode in ["large", "medium"]:
                    self.global_options_panel.setMinimumWidth(350)
                    self.global_options_panel.setMaximumWidth(500)
                else:
                    self.global_options_panel.setMinimumWidth(250)
                    self.global_options_panel.setMaximumWidth(350)
                    
            if UI_HELPERS_AVAILABLE:
                self.status_manager.show_message("Layout adapted to screen size", "info", 2000)
                
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_validation_error("Layout Change", e, self)
            else:
                print(f"Warning: Error handling layout change: {e}")
                
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
            print(f"Warning: Error applying tooltips: {e}")
            
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
                print(f"Error updating ADSR {parameter_name}: {e}")
                
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
                print(f"Error updating modulation: {e}")
                
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
                print(f"Error updating groups: {e}")

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
            
        try:
            # Validate file exists and is readable
            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")
            if not os.access(path, os.R_OK):
                raise PermissionError(f"Cannot read file: {path}")
                
            # Load the preset
            self.preset = controller.load_preset(path)
            
            # Validate preset data
            if not self.preset:
                raise ValueError("Invalid preset data")
                
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
            self.preview_canvas.set_preset(self.preset, os.path.dirname(path))
            
            # Update keyboard visualization
            self._update_keyboard_visualization()
            
            # Success feedback
            if UI_HELPERS_AVAILABLE:
                self.status_manager.show_message(f"Successfully loaded: {os.path.basename(path)}", "success", 3000)
            else:
                self.statusBar().showMessage(f"Loaded: {os.path.basename(path)}", 3000)
                
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_file_error("loading", path, e, self)
            else:
                QMessageBox.critical(self, "Error Loading Preset", f"Failed to load preset:\n{str(e)}")

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
            
            # Save with progress indication
            if UI_HELPERS_AVAILABLE:
                self.status_manager.show_message("Saving preset...", "info", 0)
                
            controller.save_preset(path, self.preset)
            
            # Update preview with new path
            self.preview_canvas.set_preset(self.preset, os.path.dirname(path))
            
            # Success feedback
            if UI_HELPERS_AVAILABLE:
                self.status_manager.show_message(f"Successfully saved: {os.path.basename(path)}", "success", 3000)
            else:
                self.statusBar().showMessage(f"Saved: {os.path.basename(path)}", 3000)
                
            QMessageBox.information(self, "Preset Saved", f"Preset saved successfully to:\n{path}")
            
        except Exception as e:
            if UI_HELPERS_AVAILABLE:
                ErrorHandler.handle_file_error("saving", path if 'path' in locals() else "preset", e, self)
            else:
                QMessageBox.critical(self, "Error Saving Preset", f"Failed to save preset:\n{str(e)}")
                
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
                    print(f"Warning: Skipping invalid mapping: {e}")
                    
            self.preset.mappings = valid_mappings
            
            # Update modulation data
            if hasattr(self, 'modulation_panel'):
                lfos, routes = self.modulation_panel.get_modulation_data()
                self.preset.lfos = lfos
                self.preset.modulation_routes = routes
                
        except Exception as e:
            print(f"Warning: Error updating preset from UI: {e}")

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
                print(f"Error handling keyboard note click: {e}")
    
    def _on_keyboard_mapping_hovered(self, mapping_info):
        """Handle keyboard mapping hover events"""
        try:
            # Could show mapping info in status bar or update a detail panel
            if UI_HELPERS_AVAILABLE and mapping_info:
                sample_name = mapping_info.get('name', 'Unknown')
                self.status_manager.show_message(f"Hovering over: {sample_name}", "info", 1000)
                
        except Exception as e:
            print(f"Error handling keyboard mapping hover: {e}")
    
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
            print(f"Error updating keyboard visualization: {e}")
