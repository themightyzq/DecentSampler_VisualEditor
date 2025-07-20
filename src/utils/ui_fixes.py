"""
UI Fixes for DecentSampler Frontend
Addresses text cutoff, spacing issues, and sizing problems throughout the application
Final comprehensive fixes for all remaining text cutoff issues
"""

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, 
    QCheckBox, QLineEdit, QTextEdit, QGroupBox, QTabWidget, QTableWidget,
    QHeaderView, QListWidget, QSlider, QProgressBar, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics

class UIFixes:
    """Collection of UI fixes and improvements"""
    
    @staticmethod
    def fix_button_sizing(button: QPushButton, min_width: int = 80, min_height: int = 28):
        """Fix button sizing to prevent text cutoff"""
        button.setMinimumHeight(min_height)
        if min_width > 0:
            button.setMinimumWidth(min_width)
        
        # Ensure proper padding
        current_style = button.styleSheet()
        if "padding:" not in current_style:
            button.setStyleSheet(current_style + " padding: 4px 12px;")
    
    @staticmethod
    def fix_label_sizing(label: QLabel, min_width: int = 0):
        """Fix label sizing to prevent text cutoff"""
        # Calculate proper size based on text
        font_metrics = label.fontMetrics()
        text_width = font_metrics.horizontalAdvance(label.text()) + 16  # Add padding
        
        if min_width > 0:
            label.setMinimumWidth(max(min_width, text_width))
        else:
            label.setMinimumWidth(text_width)
    
    @staticmethod
    def fix_spinbox_sizing(spinbox: QSpinBox, min_width: int = 70):
        """Fix spinbox sizing for better usability"""
        spinbox.setMinimumWidth(min_width)
        spinbox.setMinimumHeight(24)
        
        # Ensure alignment
        spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    
    @staticmethod
    def fix_double_spinbox_sizing(spinbox: QDoubleSpinBox, min_width: int = 80):
        """Fix double spinbox sizing for better usability"""
        spinbox.setMinimumWidth(min_width)
        spinbox.setMinimumHeight(24)
        
        # Ensure alignment
        spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    
    @staticmethod
    def fix_combobox_sizing(combo: QComboBox, min_width: int = 100):
        """Fix combobox sizing to show full text"""
        combo.setMinimumWidth(min_width)
        combo.setMinimumHeight(28)  # Increased for better text visibility
        
        # Calculate width based on longest item
        font_metrics = combo.fontMetrics()
        max_width = min_width
        
        for i in range(combo.count()):
            text = combo.itemText(i)
            text_width = font_metrics.horizontalAdvance(text) + 50  # More space for dropdown arrow
            max_width = max(max_width, text_width)
        
        combo.setMinimumWidth(max_width)
        
        # Ensure proper text alignment
        combo.setStyleSheet(combo.styleSheet() + """
            QComboBox {
                padding: 4px 8px;
                text-align: left;
            }
            QComboBox::drop-down {
                width: 20px;
            }
        """)
    
    @staticmethod
    def fix_checkbox_sizing(checkbox: QCheckBox):
        """Fix checkbox sizing to prevent text cutoff"""
        if checkbox.text():
            font_metrics = checkbox.fontMetrics()
            text_width = font_metrics.horizontalAdvance(checkbox.text()) + 30  # Space for checkbox
            checkbox.setMinimumWidth(text_width)
        checkbox.setMinimumHeight(24)
    
    @staticmethod
    def fix_line_edit_sizing(line_edit: QLineEdit, min_width: int = 100):
        """Fix line edit sizing for better usability"""
        line_edit.setMinimumWidth(min_width)
        line_edit.setMinimumHeight(28)
        
        # Add padding for better text visibility
        line_edit.setStyleSheet(line_edit.styleSheet() + " padding: 4px 8px;")
    
    @staticmethod
    def fix_group_box_sizing(group_box: QGroupBox):
        """Fix group box title and content sizing"""
        # Ensure title text isn't cut off
        if group_box.title():
            font_metrics = group_box.fontMetrics()
            title_width = font_metrics.horizontalAdvance(group_box.title()) + 20
            if group_box.minimumWidth() < title_width:
                group_box.setMinimumWidth(title_width)
        
        # Add proper margin for title
        group_box.setStyleSheet(group_box.styleSheet() + """
            QGroupBox {
                font-weight: bold;
                margin-top: 12px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
            }
        """)
    
    @staticmethod
    def fix_table_sizing(table: QTableWidget):
        """Fix table header and cell sizing"""
        # Fix header sizing
        header = table.horizontalHeader()
        header.setDefaultSectionSize(120)  # Minimum column width
        header.setMinimumSectionSize(80)
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Fix row height
        table.setRowHeight(0, 32) if table.rowCount() > 0 else None
        table.verticalHeader().setDefaultSectionSize(32)
        
        # Ensure text fits in cells
        for col in range(table.columnCount()):
            if table.horizontalHeaderItem(col):
                header_text = table.horizontalHeaderItem(col).text()
                font_metrics = table.fontMetrics()
                header_width = font_metrics.horizontalAdvance(header_text) + 20
                if table.columnWidth(col) < header_width:
                    table.setColumnWidth(col, header_width)
    
    @staticmethod
    def fix_list_widget_sizing(list_widget: QListWidget):
        """Fix list widget item sizing"""
        list_widget.setMinimumHeight(100)
        
        # Ensure items have proper height
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item:
                list_widget.setItemWidget(item, None)  # Clear any custom widgets first
                font_metrics = list_widget.fontMetrics()
                text_height = font_metrics.height() + 8  # Add padding
                item.setSizeHint(item.sizeHint().expandedTo(Qt.QSize(0, text_height)))
    
    @staticmethod
    def fix_slider_sizing(slider: QSlider):
        """Fix slider sizing and labels"""
        if slider.orientation() == Qt.Horizontal:
            slider.setMinimumWidth(100)
            slider.setMinimumHeight(24)
        else:
            slider.setMinimumWidth(24)
            slider.setMinimumHeight(100)
    
    @staticmethod
    def fix_progress_bar_sizing(progress_bar: QProgressBar):
        """Fix progress bar sizing"""
        progress_bar.setMinimumHeight(24)
        progress_bar.setMinimumWidth(150)
    
    @staticmethod
    def apply_fixes_to_widget(widget: QWidget):
        """Apply fixes to all child widgets recursively"""
        # Fix the widget itself
        if isinstance(widget, QPushButton):
            UIFixes.fix_button_sizing(widget)
        elif isinstance(widget, QLabel):
            UIFixes.fix_label_sizing(widget)
        elif isinstance(widget, QDoubleSpinBox):
            UIFixes.fix_double_spinbox_sizing(widget)
        elif isinstance(widget, QSpinBox):
            UIFixes.fix_spinbox_sizing(widget)
        elif isinstance(widget, QComboBox):
            UIFixes.fix_combobox_sizing(widget)
        elif isinstance(widget, QCheckBox):
            UIFixes.fix_checkbox_sizing(widget)
        elif isinstance(widget, QLineEdit):
            UIFixes.fix_line_edit_sizing(widget)
        elif isinstance(widget, QGroupBox):
            UIFixes.fix_group_box_sizing(widget)
        elif isinstance(widget, QTableWidget):
            UIFixes.fix_table_sizing(widget)
        elif isinstance(widget, QListWidget):
            UIFixes.fix_list_widget_sizing(widget)
        elif isinstance(widget, QSlider):
            UIFixes.fix_slider_sizing(widget)
        elif isinstance(widget, QProgressBar):
            UIFixes.fix_progress_bar_sizing(widget)
        
        # Fix all children recursively
        for child in widget.findChildren(QWidget):
            if child.parent() == widget:  # Only direct children to avoid double processing
                UIFixes.apply_fixes_to_widget(child)
    
    @staticmethod
    def fix_sample_mapping_panel(panel):
        """Fix specific issues in sample mapping panel"""
        # Fix button sizes - increased widths for longer text
        for button in panel.findChildren(QPushButton):
            if button.text() in ["Import Files", "Import Folder", "Auto-Map", "Visual Map"]:
                UIFixes.fix_button_sizing(button, min_width=120, min_height=36)
            elif button.text() in ["Exit Visual Map"]:
                UIFixes.fix_button_sizing(button, min_width=140, min_height=36)
        
        # Fix table widget sizing
        if hasattr(panel, 'table_widget'):
            UIFixes.fix_table_sizing(panel.table_widget)
            # Set specific column widths for sample mapping table
            table = panel.table_widget
            if table.columnCount() >= 3:
                table.setColumnWidth(0, 200)  # Filename column
                table.setColumnWidth(1, 180)  # Key range column  
                table.setColumnWidth(2, 120)  # Status column
        
        # Fix zone panel spinboxes with better sizing
        if hasattr(panel, 'lo_spin'):
            UIFixes.fix_spinbox_sizing(panel.lo_spin, min_width=90)
        if hasattr(panel, 'hi_spin'):
            UIFixes.fix_spinbox_sizing(panel.hi_spin, min_width=90)
        if hasattr(panel, 'root_spin'):
            UIFixes.fix_spinbox_sizing(panel.root_spin, min_width=90)
        
        # Fix labels in zone panel with better minimum widths
        if hasattr(panel, 'lo_label'):
            UIFixes.fix_label_sizing(panel.lo_label, min_width=85)
        if hasattr(panel, 'hi_label'):
            UIFixes.fix_label_sizing(panel.hi_label, min_width=85)
        if hasattr(panel, 'root_label'):
            UIFixes.fix_label_sizing(panel.root_label, min_width=85)
        
        # Fix zone panel itself
        if hasattr(panel, 'zone_panel'):
            panel.zone_panel.setMinimumHeight(120)
            
        # Fix progress bar
        if hasattr(panel, 'progress_bar'):
            UIFixes.fix_progress_bar_sizing(panel.progress_bar)
    
    @staticmethod
    def fix_adsr_panel(panel):
        """Fix ADSR panel sizing issues"""
        # Fix parameter cards with better sizing
        for card in [panel.attack_card, panel.decay_card, panel.sustain_card, panel.release_card]:
            # Fix card minimum size
            card.setMinimumWidth(160)
            card.setMinimumHeight(200)
            
            if hasattr(card, 'label_btn'):
                UIFixes.fix_button_sizing(card.label_btn, min_width=120, min_height=32)
            if hasattr(card, 'value_spin'):
                UIFixes.fix_double_spinbox_sizing(card.value_spin, min_width=100)
            if hasattr(card, 'settings_btn'):
                UIFixes.fix_button_sizing(card.settings_btn, min_width=100, min_height=28)
            if hasattr(card, 'enable_cb'):
                UIFixes.fix_checkbox_sizing(card.enable_cb)
            
            # Fix X/Y/W/H spinboxes with better labels
            for spinbox_name in ['x_spin', 'y_spin', 'width_spin', 'height_spin']:
                if hasattr(card, spinbox_name):
                    spinbox = getattr(card, spinbox_name)
                    UIFixes.fix_spinbox_sizing(spinbox, min_width=70)
        
        # Fix velocity controls with better sizing
        if hasattr(panel, 'lo_vel_label'):
            UIFixes.fix_label_sizing(panel.lo_vel_label, min_width=110)
        if hasattr(panel, 'hi_vel_label'):
            UIFixes.fix_label_sizing(panel.hi_vel_label, min_width=110)
        if hasattr(panel, 'lo_vel_spin'):
            UIFixes.fix_spinbox_sizing(panel.lo_vel_spin, min_width=70)
        if hasattr(panel, 'hi_vel_spin'):
            UIFixes.fix_spinbox_sizing(panel.hi_vel_spin, min_width=70)
        if hasattr(panel, 'lo_vel_slider'):
            UIFixes.fix_slider_sizing(panel.lo_vel_slider)
        if hasattr(panel, 'hi_vel_slider'):
            UIFixes.fix_slider_sizing(panel.hi_vel_slider)
    
    @staticmethod
    def fix_modulation_panel(panel):
        """Fix modulation panel sizing issues"""
        # Fix buttons with specific sizing for modulation context
        for button in panel.findChildren(QPushButton):
            if button.text() in ["Add LFO", "Remove LFO", "Add Route", "Remove Route"]:
                UIFixes.fix_button_sizing(button, min_width=90, min_height=30)
            else:
                UIFixes.fix_button_sizing(button, min_width=80, min_height=28)
        
        # Fix combo boxes with better widths for modulation options
        for combo in panel.findChildren(QComboBox):
            # Special handling for waveform combos (longer text)
            if hasattr(combo, 'count') and combo.count() > 0:
                longest_text = max([combo.itemText(i) for i in range(combo.count())], key=len, default="")
                if len(longest_text) > 15:  # Likely a waveform combo
                    UIFixes.fix_combobox_sizing(combo, min_width=160)
                else:
                    UIFixes.fix_combobox_sizing(combo, min_width=120)
            else:
                UIFixes.fix_combobox_sizing(combo, min_width=120)
        
        # Fix spinboxes with appropriate widths
        for spinbox in panel.findChildren(QDoubleSpinBox):
            UIFixes.fix_double_spinbox_sizing(spinbox, min_width=90)
        
        # Fix LFO editors if present
        for lfo_editor in panel.findChildren(QWidget):
            if hasattr(lfo_editor, 'frequency_spin'):  # This identifies LFO editors
                lfo_editor.setMinimumWidth(300)
                lfo_editor.setMinimumHeight(250)
        
        # Fix modulation matrix if present
        for table in panel.findChildren(QTableWidget):
            UIFixes.fix_table_sizing(table)
    
    @staticmethod
    def fix_group_manager(panel):
        """Fix group manager panel sizing issues"""
        # Fix buttons with better sizing for longer text
        for button in panel.findChildren(QPushButton):
            if button.text() in ["Add Group", "Remove Group"]:
                UIFixes.fix_button_sizing(button, min_width=110, min_height=32)
            elif button.text() in ["Create Velocity Layers", "Create Blend Layers", "Setup Round-Robin"]:
                UIFixes.fix_button_sizing(button, min_width=160, min_height=34)
            elif button.text() in ["Group Tutorial", "Help", "Advanced"]:
                UIFixes.fix_button_sizing(button, min_width=100, min_height=30)
            else:
                UIFixes.fix_button_sizing(button, min_width=90, min_height=28)
        
        # Fix group list widget if present
        for list_widget in panel.findChildren(QListWidget):
            UIFixes.fix_list_widget_sizing(list_widget)
            list_widget.setMinimumHeight(150)
        
        # Fix tutorial button
        if hasattr(panel, 'tutorial_btn'):
            UIFixes.fix_button_sizing(panel.tutorial_btn, min_width=120, min_height=32)
    
    @staticmethod
    def fix_audio_preview(widget):
        """Fix audio preview widget sizing"""
        # Fix play/stop buttons with better sizing
        if hasattr(widget, 'play_btn'):
            widget.play_btn.setFixedSize(40, 40)  # Larger for better visibility
            current_style = widget.play_btn.styleSheet()
            if "font-size:" not in current_style:
                widget.play_btn.setStyleSheet(current_style + " font-size: 20px;")
        
        if hasattr(widget, 'stop_btn'):
            widget.stop_btn.setFixedSize(40, 40)  # Match play button size
            current_style = widget.stop_btn.styleSheet()
            if "font-size:" not in current_style:
                widget.stop_btn.setStyleSheet(current_style + " font-size: 18px;")
        
        # Fix file label
        if hasattr(widget, 'file_label'):
            UIFixes.fix_label_sizing(widget.file_label, min_width=200)
            widget.file_label.setMinimumHeight(24)
        
        # Fix status label  
        if hasattr(widget, 'status_label'):
            UIFixes.fix_label_sizing(widget.status_label, min_width=150)
            widget.status_label.setMinimumHeight(20)
        
        # Fix waveform display
        if hasattr(widget, 'waveform'):
            widget.waveform.setMinimumHeight(80)
            widget.waveform.setMaximumHeight(100)
            widget.waveform.setMinimumWidth(200)
    
    @staticmethod
    def fix_piano_keyboard(widget):
        """Fix piano keyboard sizing and labels"""
        # Ensure proper height for better label visibility
        widget.setFixedHeight(140)  # Increased height for better text display
        widget.setMinimumWidth(800)  # Ensure minimum width for all keys
        
        # Ensure proper sizing policy
        from PyQt5.QtWidgets import QSizePolicy
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
    @staticmethod
    def fix_project_properties_panel(panel):
        """Fix project properties panel sizing"""
        # Fix all buttons with better sizing
        for button in panel.findChildren(QPushButton):
            if button.text() in ["Add Control", "Browse..."]:
                UIFixes.fix_button_sizing(button, min_width=110, min_height=32)
            elif button.text() in ["Reset to Default", "Advanced Options"]:
                UIFixes.fix_button_sizing(button, min_width=130, min_height=30)
            else:
                UIFixes.fix_button_sizing(button, min_width=90, min_height=28)
        
        # Fix all input widgets
        for spinbox in panel.findChildren(QSpinBox):
            UIFixes.fix_spinbox_sizing(spinbox, min_width=80)
        
        for line_edit in panel.findChildren(QLineEdit):
            UIFixes.fix_line_edit_sizing(line_edit, min_width=150)
            
        for combo in panel.findChildren(QComboBox):
            UIFixes.fix_combobox_sizing(combo, min_width=120)
            
        for checkbox in panel.findChildren(QCheckBox):
            UIFixes.fix_checkbox_sizing(checkbox)
        
        # Fix panel width with better sizing
        panel.setMinimumWidth(420)
        panel.setMaximumWidth(480)
    
    @staticmethod
    def fix_main_window_spacing(main_window):
        """Fix overall main window spacing issues"""
        # Set consistent margins for all major panels
        if hasattr(main_window, 'sample_mapping_panel'):
            layout = main_window.sample_mapping_panel.layout()
            if layout:
                layout.setContentsMargins(12, 12, 12, 12)
                layout.setSpacing(12)
        
        # Fix global options panel spacing
        if hasattr(main_window, 'global_options_panel'):
            widget = main_window.global_options_panel.widget()
            if widget and widget.layout():
                widget.layout().setContentsMargins(12, 12, 12, 12)
                widget.layout().setSpacing(10)
        
        # Fix layout manager tab spacing if present
        if hasattr(main_window, 'layout_manager'):
            layout_manager = main_window.layout_manager
            # Set minimum spacing for tab content
            for i in range(getattr(layout_manager, 'count', lambda: 0)()):
                tab_widget = getattr(layout_manager, 'widget', lambda x: None)(i)
                if tab_widget and hasattr(tab_widget, 'layout') and tab_widget.layout():
                    tab_widget.layout().setContentsMargins(10, 10, 10, 10)
                    tab_widget.layout().setSpacing(8)
    
    @staticmethod 
    def fix_menu_items(main_window):
        """Fix menu item spacing and sizing"""
        if hasattr(main_window, 'menuBar'):
            menu_bar = main_window.menuBar()
            # Ensure menu items have proper padding
            menu_bar.setStyleSheet(menu_bar.styleSheet() + """
                QMenuBar::item {
                    padding: 4px 8px;
                    margin: 2px;
                }
                QMenu::item {
                    padding: 6px 12px;
                    min-height: 20px;
                }
            """)
    
    @staticmethod
    def fix_status_bar(main_window):
        """Fix status bar text cutoff"""
        if hasattr(main_window, 'statusBar'):
            status_bar = main_window.statusBar()
            status_bar.setMinimumHeight(24)
            # Ensure status messages aren't cut off
            status_bar.setStyleSheet(status_bar.styleSheet() + """
                QStatusBar {
                    padding: 2px 8px;
                }
                QStatusBar::item {
                    border: none;
                    padding: 0px 4px;
                }
            """)
    
    @staticmethod
    def fix_dialog_buttons(dialog):
        """Fix common dialog button sizing issues"""
        from PyQt5.QtWidgets import QDialogButtonBox
        for button_box in dialog.findChildren(QDialogButtonBox):
            for button in button_box.buttons():
                UIFixes.fix_button_sizing(button, min_width=80, min_height=32)
    
    @staticmethod
    def fix_tab_widget(tab_widget: QTabWidget):
        """Fix tab widget tab text cutoff"""
        tab_widget.setMinimumHeight(200)
        
        # Fix tab bar sizing
        tab_bar = tab_widget.tabBar()
        tab_bar.setMinimumHeight(32)
        
        # Calculate proper tab widths based on text
        font_metrics = tab_widget.fontMetrics()
        for i in range(tab_widget.count()):
            text = tab_widget.tabText(i)
            text_width = font_metrics.horizontalAdvance(text) + 24  # Add padding
            current_width = tab_bar.tabRect(i).width()
            if current_width < text_width:
                # Force minimum tab width
                tab_widget.setStyleSheet(tab_widget.styleSheet() + f"""
                    QTabBar::tab {{
                        min-width: {text_width}px;
                        padding: 6px 12px;
                    }}
                """)
                break
    
    @staticmethod
    def apply_all_fixes(main_window):
        """Apply all UI fixes to the main window - COMPREHENSIVE FINAL PASS"""
        print("Applying comprehensive UI fixes for text cutoff prevention...")
        
        # Fix menu and status bar first
        UIFixes.fix_menu_items(main_window)
        UIFixes.fix_status_bar(main_window)
        
        # Fix individual panels with enhanced sizing
        if hasattr(main_window, 'sample_mapping_panel'):
            UIFixes.fix_sample_mapping_panel(main_window.sample_mapping_panel)
        
        if hasattr(main_window, 'group_properties_panel_widget'):
            UIFixes.fix_adsr_panel(main_window.group_properties_panel_widget)
        
        if hasattr(main_window, 'modulation_panel'):
            UIFixes.fix_modulation_panel(main_window.modulation_panel)
        
        if hasattr(main_window, 'group_manager'):
            UIFixes.fix_group_manager(main_window.group_manager)
        
        if hasattr(main_window, 'global_options_panel'):
            UIFixes.fix_project_properties_panel(main_window.global_options_panel)
        
        if hasattr(main_window, 'piano_keyboard'):
            UIFixes.fix_piano_keyboard(main_window.piano_keyboard)
        
        # Fix audio preview widgets
        if hasattr(main_window, 'sample_mapping_panel') and hasattr(main_window.sample_mapping_panel, 'audio_preview'):
            UIFixes.fix_audio_preview(main_window.sample_mapping_panel.audio_preview)
        
        # Fix tab widgets
        for tab_widget in main_window.findChildren(QTabWidget):
            UIFixes.fix_tab_widget(tab_widget)
        
        # Fix overall spacing
        UIFixes.fix_main_window_spacing(main_window)
        
        # Apply fixes to all remaining widgets - final comprehensive pass
        UIFixes.apply_fixes_to_widget(main_window)
        
        print("✓ All UI text cutoff fixes applied successfully")