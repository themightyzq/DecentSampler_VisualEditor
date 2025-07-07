from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QMessageBox, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QUndoStack
from views.panels.sample_mapping_panel import SampleMappingPanel
from views.panels.global_options_panel import GlobalOptionsPanel
from panels.project_properties import ProjectPropertiesPanel
from views.panels.preview_canvas import PreviewCanvas
from panels.piano_keyboard import PianoKeyboardWidget
from model import InstrumentPreset
import controller
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DecentSampler Form Editor")
        self.setGeometry(100, 100, 900, 600)
        self.undo_stack = QUndoStack(self)
        self.preset = None

        self._create_menu()
        self._create_central()
        self._createGlobalOptionsPanel()
        self._connectSignals()
        self.new_preset()  # Always start with a blank preset

    def _create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_preset)
        file_menu.addAction(new_action)
        open_action = QAction("Open...", self)
        open_action.triggered.connect(self.open_preset)
        file_menu.addAction(open_action)
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_preset)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        edit_menu = menubar.addMenu("Edit")
        undo_action = self.undo_stack.createUndoAction(self, "Undo")
        undo_action.setShortcut("Ctrl+Z")
        redo_action = self.undo_stack.createRedoAction(self, "Redo")
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

    def _create_central(self):
        splitter = QSplitter(Qt.Horizontal)

        # Left: Sample list + mapping form merged in a vertical layout
        self.sample_mapping_panel = SampleMappingPanel(self)
        left_widget = self.sample_mapping_panel

        # Center: PreviewCanvas (fixed) + PianoKeyboardWidget (fixed height, fixed width, centered)
        center_widget = QWidget()
        center_layout = QVBoxLayout()
        self.preview_canvas = PreviewCanvas(self)
        self.preview_canvas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.preview_canvas.setFixedSize(812, 375)
        center_layout.addWidget(self.preview_canvas, alignment=Qt.AlignHCenter)
        self.piano_keyboard = PianoKeyboardWidget(main_window=self)
        self.piano_keyboard.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.piano_keyboard.setMinimumHeight(80)
        self.piano_keyboard.setMaximumHeight(120)
        self.piano_keyboard.setFixedWidth(812)
        center_layout.addWidget(self.piano_keyboard, alignment=Qt.AlignHCenter)
        center_widget.setLayout(center_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(center_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        central = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _createGlobalOptionsPanel(self):
        def show_error(parent, title, msg):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(parent, title, msg)
        try:
            self.global_options_panel = ProjectPropertiesPanel(self)
        except Exception as e:
            show_error(self, "Panel init failed", str(e))
            raise
        self.addDockWidget(Qt.RightDockWidgetArea, self.global_options_panel)

    def _connectSignals(self):
        # Placeholder for future signal connections
        pass

    def new_preset(self):
        self.preset = InstrumentPreset("Untitled")
        self.preset.ui_width = 812
        self.preset.ui_height = 375
        self.sample_mapping_panel.set_samples([])
        self.sample_mapping_panel.set_mapping(None)
        self.undo_stack.clear()
        self._set_options_panel_from_preset()
        self.preview_canvas.set_preset(self.preset, os.getcwd())
        # Status/help message
        self.statusBar().showMessage("Steps: 1) Import  2) Map  3) Preview  4) Save")

    def open_preset(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open .dspreset", "", "DecentSampler Preset (*.dspreset)")
        if not path:
            return
        try:
            self.preset = controller.load_preset(path)
            self.sample_mapping_panel.set_samples(list(self.preset.mappings))
            if self.preset.mappings:
                self.sample_mapping_panel.set_mapping(self.preset.mappings[0])
            else:
                self.sample_mapping_panel.set_mapping(None)
            self.undo_stack.clear()
            self._set_options_panel_from_preset()
            self.preview_canvas.set_preset(self.preset, os.path.dirname(path))
            # Optionally: push an InitialLoadCommand for undo
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load preset:\n{e}")

    def save_preset(self):
        if not self.preset:
            QMessageBox.warning(self, "No Preset", "No preset loaded.")
            return
        # Update preset from options panel before saving
        opts = self.global_options_panel.get_options()
        self.preset.bg_image = opts["bg_image"]
        self.preset.have_attack = opts["have_attack"]
        self.preset.have_decay = opts["have_decay"]
        self.preset.have_sustain = opts["have_sustain"]
        self.preset.have_release = opts["have_release"]
        self.preset.have_tone = opts["have_tone"]
        self.preset.have_chorus = opts["have_chorus"]
        self.preset.have_reverb = opts["have_reverb"]
        self.preset.have_midicc1 = opts["have_midicc1"]
        self.preset.cut_all_by_all = opts["cut_all_by_all"]
        self.preset.silencing_mode = opts["silencing_mode"]

        path, _ = QFileDialog.getSaveFileName(self, "Save .dspreset", "", "DecentSampler Preset (*.dspreset)")
        if not path:
            return
        try:
            controller.save_preset(path, self.preset)
            self.preview_canvas.set_preset(self.preset, os.path.dirname(path))
            QMessageBox.information(self, "Saved", f"Preset saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save preset:\n{e}")

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
        # If you have additional controls (attack, decay, etc.), set them here as well
