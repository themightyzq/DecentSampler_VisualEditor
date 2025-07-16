"""
Quality of Life improvements for DecentSampler Frontend
Includes auto-save, keyboard shortcuts, workflow helpers, and usability enhancements
"""

from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QProgressDialog, QShortcut
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSettings, QThread
from PyQt5.QtGui import QKeySequence, QFont
import os
import json
import time

class AutoSaveManager:
    """Manages automatic saving of work in progress"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_interval = 300000  # 5 minutes in milliseconds
        self.auto_save_enabled = True
        self.temp_save_dir = os.path.join(os.path.expanduser("~"), ".decentsampler_editor", "autosave")
        
        # Create temp directory if it doesn't exist
        os.makedirs(self.temp_save_dir, exist_ok=True)
        
    def start_auto_save(self):
        """Start the auto-save timer"""
        if self.auto_save_enabled:
            self.auto_save_timer.start(self.auto_save_interval)
            
    def stop_auto_save(self):
        """Stop the auto-save timer"""
        self.auto_save_timer.stop()
        
    def auto_save(self):
        """Perform automatic save"""
        if not self.main_window.preset:
            return
            
        try:
            timestamp = int(time.time())
            filename = f"autosave_{timestamp}.dspreset"
            path = os.path.join(self.temp_save_dir, filename)
            
            # Save current state
            self.main_window._update_preset_from_ui()
            self.main_window.preset.to_dspreset(path)
            
            # Clean up old auto-saves (keep last 5)
            self._cleanup_old_autosaves()
            
            # Notify user subtly
            if hasattr(self.main_window, 'status_manager'):
                self.main_window.status_manager.show_message("Auto-saved", "info", 1000)
                
        except Exception as e:
            print(f"Auto-save failed: {e}")
            
    def _cleanup_old_autosaves(self):
        """Remove old auto-save files, keeping only the most recent 5"""
        try:
            autosave_files = [f for f in os.listdir(self.temp_save_dir) if f.startswith("autosave_")]
            autosave_files.sort(key=lambda x: os.path.getctime(os.path.join(self.temp_save_dir, x)), reverse=True)
            
            # Remove files beyond the 5 most recent
            for old_file in autosave_files[5:]:
                os.remove(os.path.join(self.temp_save_dir, old_file))
                
        except Exception as e:
            print(f"Auto-save cleanup failed: {e}")
            
    def recover_auto_saves(self):
        """Return list of available auto-save files for recovery"""
        try:
            autosave_files = [f for f in os.listdir(self.temp_save_dir) if f.startswith("autosave_")]
            autosave_files.sort(key=lambda x: os.path.getctime(os.path.join(self.temp_save_dir, x)), reverse=True)
            
            recovery_list = []
            for filename in autosave_files:
                path = os.path.join(self.temp_save_dir, filename)
                mtime = os.path.getmtime(path)
                recovery_list.append({
                    'filename': filename,
                    'path': path,
                    'timestamp': mtime,
                    'human_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
                })
                
            return recovery_list
            
        except Exception as e:
            print(f"Error retrieving auto-saves: {e}")
            return []

class KeyboardShortcutManager:
    """Manages keyboard shortcuts for improved workflow"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.shortcuts = {}
        self._setup_shortcuts()
        
    def _setup_shortcuts(self):
        """Set up all keyboard shortcuts"""
        shortcuts_config = {
            'Ctrl+N': self.main_window.new_preset,
            'Ctrl+O': self.main_window.open_preset, 
            'Ctrl+S': self.main_window.save_preset,
            'Ctrl+Z': self.main_window.undo_stack.undo,
            'Ctrl+Y': self.main_window.undo_stack.redo,
            'Ctrl+Shift+S': self._save_as,
            'F5': self._refresh_preview,
            'Ctrl+I': self._import_samples_shortcut,
            'Ctrl+M': self._auto_map_shortcut,
            'Ctrl+P': self._toggle_preview_focus,
            'Ctrl+1': lambda: self._switch_to_tab(0),
            'Ctrl+2': lambda: self._switch_to_tab(1),
            'Ctrl+3': lambda: self._switch_to_tab(2),
            'F1': self._show_help,
            'Ctrl+,': self._show_preferences,
        }
        
        for key_seq, callback in shortcuts_config.items():
            try:
                shortcut = QShortcut(QKeySequence(key_seq), self.main_window)
                shortcut.activated.connect(callback)
                self.shortcuts[key_seq] = shortcut
            except Exception as e:
                print(f"Failed to set up shortcut {key_seq}: {e}")
                
    def _save_as(self):
        """Save As functionality"""
        # Temporarily modify save to force dialog
        if hasattr(self.main_window, 'preset') and self.main_window.preset:
            self.main_window.save_preset()
            
    def _refresh_preview(self):
        """Refresh the preview canvas"""
        if hasattr(self.main_window, 'preview_canvas') and self.main_window.preset:
            self.main_window.preview_canvas.set_preset(self.main_window.preset, os.getcwd())
            
    def _import_samples_shortcut(self):
        """Trigger sample import via keyboard"""
        if hasattr(self.main_window, 'sample_mapping_panel'):
            # Try to find and trigger the import button
            import_btn = self.main_window.sample_mapping_panel.findChild(QPushButton, "import_samples")
            if import_btn:
                import_btn.click()
                
    def _auto_map_shortcut(self):
        """Trigger auto-mapping via keyboard"""
        if hasattr(self.main_window, 'sample_mapping_panel'):
            # Try to find and trigger the auto-map button
            automap_btn = self.main_window.sample_mapping_panel.findChild(QPushButton, "auto_map")
            if automap_btn:
                automap_btn.click()
                
    def _toggle_preview_focus(self):
        """Toggle focus to preview panel"""
        if hasattr(self.main_window, 'preview_canvas'):
            self.main_window.preview_canvas.setFocus()
            
    def _switch_to_tab(self, tab_index):
        """Switch to a specific tab"""
        # Find tab widgets and switch to specified index
        tab_widgets = self.main_window.findChildren(type(self.main_window), "QTabWidget")
        for tab_widget in tab_widgets:
            if hasattr(tab_widget, 'setCurrentIndex'):
                if tab_index < tab_widget.count():
                    tab_widget.setCurrentIndex(tab_index)
                    break
                    
    def _show_help(self):
        """Show help dialog"""
        help_dialog = HelpDialog(self.main_window)
        help_dialog.exec_()
        
    def _show_preferences(self):
        """Show preferences dialog"""
        prefs_dialog = PreferencesDialog(self.main_window)
        prefs_dialog.exec_()

class WorkflowHelper:
    """Provides contextual workflow guidance and tips"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_step = 0
        self.workflow_steps = [
            "Import samples using the Import button",
            "Map samples to keyboard ranges (Auto Map or manual)",
            "Configure ADSR envelope settings",
            "Add effects and modulation if desired",
            "Preview your preset in the center panel",
            "Save your preset as a .dspreset file"
        ]
        
    def get_current_step_hint(self):
        """Get hint for current workflow step"""
        if self.current_step < len(self.workflow_steps):
            return f"Next step: {self.workflow_steps[self.current_step]}"
        return "Workflow complete! Your preset is ready."
        
    def advance_step(self):
        """Advance to next workflow step"""
        if self.current_step < len(self.workflow_steps) - 1:
            self.current_step += 1
            
    def get_progress_percentage(self):
        """Get workflow completion percentage"""
        return int((self.current_step / len(self.workflow_steps)) * 100)

class HelpDialog(QDialog):
    """Comprehensive help dialog with searchable content"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DecentSampler Editor Help")
        self.setFixedSize(600, 500)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("DecentSampler Preset Editor Help")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Help content
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_content = self._get_help_content()
        help_text.setHtml(help_content)
        layout.addWidget(help_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
    def _get_help_content(self):
        """Generate comprehensive help content"""
        return """
        <h2>Quick Start Guide</h2>
        <p><b>1. Import Samples:</b> Click 'Import' to add WAV files to your preset</p>
        <p><b>2. Map Samples:</b> Use 'Auto Map' or manually assign key ranges</p>
        <p><b>3. Configure Envelope:</b> Adjust ADSR settings for your sound</p>
        <p><b>4. Add Effects:</b> Use the Properties panel to add reverb, delay, etc.</p>
        <p><b>5. Preview:</b> Check your preset in the center preview panel</p>
        <p><b>6. Save:</b> Export as .dspreset file for use in DecentSampler</p>
        
        <h2>Keyboard Shortcuts</h2>
        <table>
        <tr><td><b>Ctrl+N</b></td><td>New preset</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Open preset</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Save preset</td></tr>
        <tr><td><b>Ctrl+Z/Y</b></td><td>Undo/Redo</td></tr>
        <tr><td><b>Ctrl+I</b></td><td>Import samples</td></tr>
        <tr><td><b>Ctrl+M</b></td><td>Auto-map samples</td></tr>
        <tr><td><b>F5</b></td><td>Refresh preview</td></tr>
        <tr><td><b>F1</b></td><td>Show this help</td></tr>
        </table>
        
        <h2>Advanced Features</h2>
        <p><b>Modulation:</b> Use the Modulation panel to create LFOs and route them to parameters</p>
        <p><b>Round-Robin:</b> Import multiple samples for the same key for variation</p>
        <p><b>Velocity Layers:</b> Create dynamic response by mapping samples to velocity ranges</p>
        <p><b>Keyboard Colors:</b> Customize the visual keyboard with color ranges</p>
        <p><b>XY Pads:</b> Add 2D control surfaces for expressive parameter control</p>
        
        <h2>Tips & Tricks</h2>
        <ul>
        <li>Use descriptive names for your presets and samples</li>
        <li>Start with simple presets and add complexity gradually</li>
        <li>Test your presets in DecentSampler before finalizing</li>
        <li>Save frequently - auto-save is enabled but manual saves are safer</li>
        <li>Use the preview panel to check your UI layout</li>
        </ul>
        
        <h2>Troubleshooting</h2>
        <p><b>Samples not playing:</b> Check file paths and key mappings</p>
        <p><b>UI looks wrong:</b> Verify dimensions and control positions</p>
        <p><b>Export fails:</b> Ensure all required fields are filled</p>
        <p><b>Performance issues:</b> Reduce number of samples or effects</p>
        """

class PreferencesDialog(QDialog):
    """User preferences and settings dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setFixedSize(400, 300)
        self.settings = QSettings("DecentSampler", "PresetEditor")
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Auto-save settings
        autosave_group = QGroupBox("Auto-Save")
        autosave_layout = QVBoxLayout()
        
        self.autosave_enabled = QCheckBox("Enable auto-save")
        self.autosave_enabled.setChecked(self.settings.value("autosave_enabled", True, bool))
        autosave_layout.addWidget(self.autosave_enabled)
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Auto-save interval:"))
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(1, 60)
        self.autosave_interval.setValue(self.settings.value("autosave_interval", 5, int))
        self.autosave_interval.setSuffix(" minutes")
        interval_layout.addWidget(self.autosave_interval)
        autosave_layout.addLayout(interval_layout)
        
        autosave_group.setLayout(autosave_layout)
        layout.addWidget(autosave_group)
        
        # UI settings
        ui_group = QGroupBox("Interface")
        ui_layout = QVBoxLayout()
        
        self.dark_theme = QCheckBox("Use dark theme")
        self.dark_theme.setChecked(self.settings.value("dark_theme", True, bool))
        ui_layout.addWidget(self.dark_theme)
        
        self.show_tooltips = QCheckBox("Show tooltips")
        self.show_tooltips.setChecked(self.settings.value("show_tooltips", True, bool))
        ui_layout.addWidget(self.show_tooltips)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_preferences)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def save_preferences(self):
        """Save user preferences"""
        self.settings.setValue("autosave_enabled", self.autosave_enabled.isChecked())
        self.settings.setValue("autosave_interval", self.autosave_interval.value())
        self.settings.setValue("dark_theme", self.dark_theme.isChecked())
        self.settings.setValue("show_tooltips", self.show_tooltips.isChecked())
        
        # Apply changes immediately if possible
        if hasattr(self.parent(), 'auto_save_manager'):
            self.parent().auto_save_manager.auto_save_enabled = self.autosave_enabled.isChecked()
            self.parent().auto_save_manager.auto_save_interval = self.autosave_interval.value() * 60000
            
        self.close()

class ProgressTracker:
    """Tracks user progress and provides completion feedback"""
    
    def __init__(self):
        self.milestones = {
            'first_import': False,
            'first_mapping': False, 
            'first_effect': False,
            'first_modulation': False,
            'first_save': False,
        }
        
    def mark_milestone(self, milestone_name):
        """Mark a milestone as completed"""
        if milestone_name in self.milestones:
            self.milestones[milestone_name] = True
            
    def get_completion_percentage(self):
        """Get overall completion percentage"""
        completed = sum(1 for completed in self.milestones.values() if completed)
        return int((completed / len(self.milestones)) * 100)
        
    def get_next_milestone(self):
        """Get the next uncompleted milestone"""
        milestone_names = {
            'first_import': 'Import your first sample',
            'first_mapping': 'Map a sample to a key',
            'first_effect': 'Add an effect control',
            'first_modulation': 'Create a modulation route',
            'first_save': 'Save your first preset',
        }
        
        for milestone, completed in self.milestones.items():
            if not completed:
                return milestone_names.get(milestone, "Complete your preset")
                
        return "All milestones completed!"