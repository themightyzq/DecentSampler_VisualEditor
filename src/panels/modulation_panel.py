from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QSpinBox, 
    QDoubleSpinBox, QComboBox, QCheckBox, QPushButton, QListWidget, 
    QListWidgetItem, QDialog, QDialogButtonBox, QFormLayout, QScrollArea,
    QFrame, QSplitter, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPalette
from model import LFO, ModulationRoute, ModulatorTarget

class LFOEditor(QGroupBox):
    """Widget for editing a single LFO"""
    lfoChanged = pyqtSignal()
    
    def __init__(self, lfo=None, parent=None):
        super().__init__("LFO Settings", parent)
        self.lfo = lfo or LFO("LFO1")
        self.init_ui()
        self.update_from_lfo()
        
    def init_ui(self):
        layout = QFormLayout()
        
        # Name
        self.name_edit = QComboBox()
        self.name_edit.setEditable(True)
        self.name_edit.addItems(["LFO1", "LFO2", "LFO3", "LFO4"])
        self.name_edit.currentTextChanged.connect(self.on_changed)
        layout.addRow("Name:", self.name_edit)
        
        # Frequency
        self.frequency_spin = QDoubleSpinBox()
        self.frequency_spin.setRange(0.01, 100.0)
        self.frequency_spin.setSingleStep(0.1)
        self.frequency_spin.setDecimals(2)
        self.frequency_spin.setSuffix(" Hz")
        self.frequency_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Frequency:", self.frequency_spin)
        
        # Waveform
        self.waveform_combo = QComboBox()
        self.waveform_combo.addItems([
            "sine", "triangle", "sawtooth", "square", "s&h", "envelope_follower"
        ])
        self.waveform_combo.setMinimumWidth(150)
        self.waveform_combo.currentTextChanged.connect(self.on_changed)
        layout.addRow("Waveform:", self.waveform_combo)
        
        # Amplitude
        self.amplitude_spin = QDoubleSpinBox()
        self.amplitude_spin.setRange(0.0, 10.0)
        self.amplitude_spin.setSingleStep(0.1)
        self.amplitude_spin.setDecimals(2)
        self.amplitude_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Amplitude:", self.amplitude_spin)
        
        # Offset
        self.offset_spin = QDoubleSpinBox()
        self.offset_spin.setRange(-10.0, 10.0)
        self.offset_spin.setSingleStep(0.1)
        self.offset_spin.setDecimals(2)
        self.offset_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Offset:", self.offset_spin)
        
        # Phase
        self.phase_spin = QDoubleSpinBox()
        self.phase_spin.setRange(0.0, 360.0)
        self.phase_spin.setSingleStep(1.0)
        self.phase_spin.setDecimals(1)
        self.phase_spin.setSuffix("°")
        self.phase_spin.valueChanged.connect(self.on_changed)
        layout.addRow("Phase:", self.phase_spin)
        
        # Sync
        self.sync_combo = QComboBox()
        self.sync_combo.addItems(["free", "tempo"])
        self.sync_combo.currentTextChanged.connect(self.on_sync_changed)
        layout.addRow("Sync:", self.sync_combo)
        
        # Sync Length (only for tempo sync)
        self.sync_length_combo = QComboBox()
        self.sync_length_combo.addItems([
            "1/64", "1/32", "1/16", "1/8", "1/4", "1/2", "1", "2", "4", "8", "16"
        ])
        self.sync_length_combo.setMinimumWidth(100)
        self.sync_length_combo.currentTextChanged.connect(self.on_changed)
        layout.addRow("Sync Length:", self.sync_length_combo)
        
        # Retrigger
        self.retrigger_check = QCheckBox()
        self.retrigger_check.toggled.connect(self.on_changed)
        layout.addRow("Retrigger:", self.retrigger_check)
        
        self.setLayout(layout)
        
    def on_sync_changed(self):
        # Enable/disable sync length based on sync mode
        is_tempo = self.sync_combo.currentText() == "tempo"
        self.sync_length_combo.setEnabled(is_tempo)
        if is_tempo:
            self.frequency_spin.setEnabled(False)
            self.frequency_spin.setSuffix(" (tempo sync)")
        else:
            self.frequency_spin.setEnabled(True)
            self.frequency_spin.setSuffix(" Hz")
        self.on_changed()
        
    def on_changed(self):
        self.update_lfo_from_ui()
        self.lfoChanged.emit()
        
    def update_from_lfo(self):
        """Update UI from LFO data"""
        self.name_edit.setCurrentText(self.lfo.name)
        self.frequency_spin.setValue(self.lfo.frequency)
        self.waveform_combo.setCurrentText(self.lfo.waveform)
        self.amplitude_spin.setValue(self.lfo.amplitude)
        self.offset_spin.setValue(self.lfo.offset)
        self.phase_spin.setValue(self.lfo.phase)
        self.sync_combo.setCurrentText(self.lfo.sync)
        self.sync_length_combo.setCurrentText(self.lfo.sync_length)
        self.retrigger_check.setChecked(self.lfo.retrigger)
        self.on_sync_changed()  # Update enabled state
        
    def update_lfo_from_ui(self):
        """Update LFO data from UI"""
        self.lfo.name = self.name_edit.currentText()
        self.lfo.frequency = self.frequency_spin.value()
        self.lfo.waveform = self.waveform_combo.currentText()
        self.lfo.amplitude = self.amplitude_spin.value()
        self.lfo.offset = self.offset_spin.value()
        self.lfo.phase = self.phase_spin.value()
        self.lfo.sync = self.sync_combo.currentText()
        self.lfo.sync_length = self.sync_length_combo.currentText()
        self.lfo.retrigger = self.retrigger_check.isChecked()

class ModulationMatrixWidget(QWidget):
    """Widget for editing modulation routes"""
    routesChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.routes = []
        self.available_lfos = []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Modulation Matrix"))
        header_layout.addStretch()
        
        self.add_route_btn = QPushButton("Add Route")
        self.add_route_btn.clicked.connect(self.add_route)
        header_layout.addWidget(self.add_route_btn)
        
        self.remove_route_btn = QPushButton("Remove Route")
        self.remove_route_btn.clicked.connect(self.remove_route)
        header_layout.addWidget(self.remove_route_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "LFO", "Target Type", "Parameter", "Level", "Amount", "Invert"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def set_available_lfos(self, lfos):
        """Set the list of available LFOs"""
        self.available_lfos = [lfo.name for lfo in lfos]
        self.refresh_table()
        
    def set_routes(self, routes):
        """Set the modulation routes"""
        self.routes = routes
        self.refresh_table()
        
    def get_routes(self):
        """Get the current modulation routes"""
        return self.routes
        
    def refresh_table(self):
        """Refresh the table display"""
        self.table.setRowCount(len(self.routes))
        
        for row, route in enumerate(self.routes):
            # LFO combo
            lfo_combo = QComboBox()
            lfo_combo.addItems(self.available_lfos)
            lfo_combo.setCurrentText(route.modulator_name)
            lfo_combo.currentTextChanged.connect(lambda text, r=route: setattr(r, 'modulator_name', text))
            lfo_combo.currentTextChanged.connect(self.routesChanged.emit)
            self.table.setCellWidget(row, 0, lfo_combo)
            
            # Target Type combo
            type_combo = QComboBox()
            type_combo.addItems(["amp", "effect", "general"])
            type_combo.setCurrentText(route.target.target_type)
            type_combo.currentTextChanged.connect(lambda text, r=route: setattr(r.target, 'target_type', text))
            type_combo.currentTextChanged.connect(self.routesChanged.emit)
            self.table.setCellWidget(row, 1, type_combo)
            
            # Parameter combo
            param_combo = QComboBox()
            param_combo.setEditable(True)
            param_combo.addItems([
                "ENV_ATTACK", "ENV_DECAY", "ENV_SUSTAIN", "ENV_RELEASE",
                "AMP_VOLUME", "FX_MIX", "FX_FILTER_FREQUENCY", "FX_REVERB_WET_LEVEL",
                "FX_CHORUS_MIX", "FX_DELAY_TIME", "FX_DELAY_FEEDBACK"
            ])
            param_combo.setMinimumWidth(180)
            param_combo.setCurrentText(route.target.parameter)
            param_combo.currentTextChanged.connect(lambda text, r=route: setattr(r.target, 'parameter', text))
            param_combo.currentTextChanged.connect(self.routesChanged.emit)
            self.table.setCellWidget(row, 2, param_combo)
            
            # Level combo
            level_combo = QComboBox()
            level_combo.addItems(["instrument", "group", "tag"])
            level_combo.setCurrentText(route.target.level)
            level_combo.currentTextChanged.connect(lambda text, r=route: setattr(r.target, 'level', text))
            level_combo.currentTextChanged.connect(self.routesChanged.emit)
            self.table.setCellWidget(row, 3, level_combo)
            
            # Amount spin
            amount_spin = QDoubleSpinBox()
            amount_spin.setRange(-10.0, 10.0)
            amount_spin.setSingleStep(0.1)
            amount_spin.setDecimals(2)
            amount_spin.setValue(route.amount)
            amount_spin.valueChanged.connect(lambda val, r=route: setattr(r, 'amount', val))
            amount_spin.valueChanged.connect(self.routesChanged.emit)
            self.table.setCellWidget(row, 4, amount_spin)
            
            # Invert checkbox
            invert_check = QCheckBox()
            invert_check.setChecked(route.invert)
            invert_check.toggled.connect(lambda checked, r=route: setattr(r, 'invert', checked))
            invert_check.toggled.connect(self.routesChanged.emit)
            self.table.setCellWidget(row, 5, invert_check)
            
    def add_route(self):
        """Add a new modulation route"""
        if not self.available_lfos:
            return
            
        target = ModulatorTarget("amp", "ENV_ATTACK")
        route = ModulationRoute(self.available_lfos[0], target, 1.0, False)
        self.routes.append(route)
        self.refresh_table()
        self.routesChanged.emit()
        
    def remove_route(self):
        """Remove selected modulation route"""
        current_row = self.table.currentRow()
        if 0 <= current_row < len(self.routes):
            del self.routes[current_row]
            self.refresh_table()
            self.routesChanged.emit()

class ModulationPanel(QWidget):
    """Main modulation panel widget"""
    modulationChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lfos = []
        self.modulation_routes = []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # LFO tab
        self.lfo_tab = QWidget()
        self.init_lfo_tab()
        self.tabs.addTab(self.lfo_tab, "LFOs")
        
        # Modulation Matrix tab
        self.matrix_tab = QWidget()
        self.init_matrix_tab()
        self.tabs.addTab(self.matrix_tab, "Modulation Matrix")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
    def init_lfo_tab(self):
        layout = QVBoxLayout()
        
        # LFO management
        lfo_header = QHBoxLayout()
        lfo_header.addWidget(QLabel("LFOs"))
        lfo_header.addStretch()
        
        self.add_lfo_btn = QPushButton("Add LFO")
        self.add_lfo_btn.clicked.connect(self.add_lfo)
        lfo_header.addWidget(self.add_lfo_btn)
        
        self.remove_lfo_btn = QPushButton("Remove LFO")
        self.remove_lfo_btn.clicked.connect(self.remove_lfo)
        lfo_header.addWidget(self.remove_lfo_btn)
        
        layout.addLayout(lfo_header)
        
        # LFO list and editor
        lfo_splitter = QSplitter(Qt.Horizontal)
        
        # LFO list
        self.lfo_list = QListWidget()
        self.lfo_list.currentItemChanged.connect(self.on_lfo_selected)
        lfo_splitter.addWidget(self.lfo_list)
        
        # LFO editor (in scroll area)
        scroll = QScrollArea()
        self.lfo_editor = LFOEditor()
        self.lfo_editor.lfoChanged.connect(self.on_lfo_changed)
        scroll.setWidget(self.lfo_editor)
        scroll.setWidgetResizable(True)
        lfo_splitter.addWidget(scroll)
        
        lfo_splitter.setSizes([200, 400])
        layout.addWidget(lfo_splitter)
        
        self.lfo_tab.setLayout(layout)
        
    def init_matrix_tab(self):
        layout = QVBoxLayout()
        
        self.matrix_widget = ModulationMatrixWidget()
        self.matrix_widget.routesChanged.connect(self.on_routes_changed)
        layout.addWidget(self.matrix_widget)
        
        self.matrix_tab.setLayout(layout)
        
    def add_lfo(self):
        """Add a new LFO"""
        lfo_count = len(self.lfos) + 1
        lfo = LFO(f"LFO{lfo_count}")
        self.lfos.append(lfo)
        
        item = QListWidgetItem(lfo.name)
        self.lfo_list.addItem(item)
        self.lfo_list.setCurrentItem(item)
        
        self.update_matrix_lfos()
        self.modulationChanged.emit()
        
    def remove_lfo(self):
        """Remove selected LFO"""
        current_row = self.lfo_list.currentRow()
        if 0 <= current_row < len(self.lfos):
            lfo_name = self.lfos[current_row].name
            
            # Remove LFO
            del self.lfos[current_row]
            self.lfo_list.takeItem(current_row)
            
            # Remove associated modulation routes
            self.modulation_routes = [r for r in self.modulation_routes if r.modulator_name != lfo_name]
            
            self.update_matrix_lfos()
            self.matrix_widget.set_routes(self.modulation_routes)
            self.modulationChanged.emit()
            
    def on_lfo_selected(self, current, previous):
        """Handle LFO selection"""
        if current:
            row = self.lfo_list.row(current)
            if 0 <= row < len(self.lfos):
                self.lfo_editor.lfo = self.lfos[row]
                self.lfo_editor.update_from_lfo()
                
    def on_lfo_changed(self):
        """Handle LFO property changes"""
        current_row = self.lfo_list.currentRow()
        if 0 <= current_row < len(self.lfos):
            # Update list item name
            self.lfo_list.item(current_row).setText(self.lfo_editor.lfo.name)
            self.update_matrix_lfos()
            self.modulationChanged.emit()
            
    def on_routes_changed(self):
        """Handle modulation route changes"""
        self.modulation_routes = self.matrix_widget.get_routes()
        self.modulationChanged.emit()
        
    def update_matrix_lfos(self):
        """Update available LFOs in matrix"""
        self.matrix_widget.set_available_lfos(self.lfos)
        
    def set_modulation_data(self, lfos, routes):
        """Set modulation data from preset"""
        self.lfos = lfos or []
        self.modulation_routes = routes or []
        
        # Update LFO list
        self.lfo_list.clear()
        for lfo in self.lfos:
            item = QListWidgetItem(lfo.name)
            self.lfo_list.addItem(item)
            
        # Update matrix
        self.update_matrix_lfos()
        self.matrix_widget.set_routes(self.modulation_routes)
        
        # Select first LFO if available
        if self.lfos:
            self.lfo_list.setCurrentRow(0)
            
    def get_modulation_data(self):
        """Get current modulation data"""
        return self.lfos, self.modulation_routes