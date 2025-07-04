import os
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QAction, QMessageBox, QSplitter, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPlainTextEdit, QDockWidget, QSizePolicy, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QUndoStack
import commands

from widgets import DraggableElementLabel
from canvas import VisualCanvas
from panels.sample_browser import SampleBrowserWidget
from panels.group_properties import GroupPropertiesWidget
from panels.bus_routing import BusRoutingWidget
from panels.piano_keyboard import PianoKeyboardWidget
from widget_palette import PaletteListWidget
import utils

from widgets import KnobWidget, SliderWidget, ButtonWidget, MenuWidget, LabelWidget, DraggableElementLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.undo_stack = QUndoStack(self)
        self.settings = QSettings("DecentSamplerEditor", "DecentSamplerEditorApp")
        self.setWindowTitle("Decent Sampler Visual Editor")
        self.setGeometry(100, 100, 1200, 900)
        # Advanced dock options for smooth docking
        self.setDockOptions(
            QMainWindow.AllowNestedDocks |
            QMainWindow.AnimatedDocks |
            QMainWindow.AllowTabbedDocks |
            QMainWindow.ForceTabbedDocks
        )
        # Restore window geometry if available
        geometry = self.settings.value("window_geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        # Restore advanced mode flag
        self.advanced_mode = self.settings.value("advanced_mode", False, type=bool)
        self._createCentralWidget()
        self._createMenuBar()
        # Connect undo/redo to sync method
        self.undo_stack.indexChanged.connect(self.sync_views_after_undo_redo)
        if not hasattr(self, "xml_root") or self.xml_root is None or not self.xml_editor.toPlainText().strip():
            self.new_project()

    def closeEvent(self, event):
        # Save window geometry and advanced mode flag
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("advanced_mode", self.advanced_mode)
        super().closeEvent(event)

    def set_advanced_mode(self, enabled: bool):
        self.advanced_mode = enabled
        self.settings.setValue("advanced_mode", enabled)

    def is_advanced_mode(self):
        return self.advanced_mode

    def _createMenuBar(self):
        menubar = self.menuBar()
        # --- Edit Menu for Undo/Redo ---
        edit_menu = menubar.addMenu("Edit")
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.undo_stack.undo)
        edit_menu.addAction(undo_action)
        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.undo_stack.redo)
        edit_menu.addAction(redo_action)
        # Global shortcuts
        from PyQt5.QtWidgets import QShortcut
        QShortcut(QKeySequence.Undo, self, activated=self.undo_stack.undo)
        QShortcut(QKeySequence.Redo, self, activated=self.undo_stack.redo)

        file_menu = menubar.addMenu("File")
        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Recent Files submenu
        self.recent_files_menu = file_menu.addMenu("Recent Files")
        self._update_recent_files_menu()

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Panels menu for showing/hiding dock widgets
        panels_menu = menubar.addMenu("Panels")
        self._panel_actions = []

        def add_panel_action(name, dock_widget):
            action = QAction(name, self, checkable=True)
            action.setChecked(dock_widget.isVisible())
            action.toggled.connect(lambda checked, w=dock_widget: w.setVisible(checked))
            dock_widget.visibilityChanged.connect(action.setChecked)
            panels_menu.addAction(action)
            self._panel_actions.append(action)

        add_panel_action("Widget Palette", self.widget_palette_dock)
        add_panel_action("Sample Mapping", self.sample_dock)
        add_panel_action("Group Envelope", self.group_dock)
        add_panel_action("Routing", self.bus_dock)
        add_panel_action("Piano Keyboard", self.piano_dock)
        add_panel_action("Help", self.help_dock)

    def _update_recent_files_menu(self):
        self.recent_files_menu.clear()
        recent_files = self.settings.value("recent_files", [], type=list)
        if not recent_files:
            self.recent_files_menu.addAction("(No Recent Files)").setEnabled(False)
        else:
            for path in recent_files:
                action = self.recent_files_menu.addAction(path)
                action.triggered.connect(lambda checked, p=path: self.open_recent_file(p))

    def _add_to_recent_files(self, path):
        recent_files = self.settings.value("recent_files", [], type=list)
        if path in recent_files:
            recent_files.remove(path)
        recent_files.insert(0, path)
        recent_files = recent_files[:10]  # Keep only 10 most recent
        self.settings.setValue("recent_files", recent_files)
        self._update_recent_files_menu()

    def open_recent_file(self, path):
        if os.path.exists(path):
            self.open_file_from_path(path)
        else:
            QMessageBox.warning(self, "File Not Found", f"The file does not exist:\n{path}")
            # Remove missing file from recent list
            recent_files = self.settings.value("recent_files", [], type=list)
            if path in recent_files:
                recent_files.remove(path)
                self.settings.setValue("recent_files", recent_files)
                self._update_recent_files_menu()

    def open_file_from_path(self, file_name):
        self.settings.setValue("last_open_folder", os.path.dirname(file_name))
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                xml_str = f.read()
                self.xml_editor.setPlainText(xml_str)
            self._last_save_path = file_name
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_str)
            # Load buses globally
            bus_elems = root.findall(".//bus")
            bus_names = [bus.attrib.get("name", "") for bus in bus_elems if bus.attrib.get("name", "")]
            if hasattr(self, "bus_routing"):
                self.bus_routing.set_buses(bus_names)
            if hasattr(self, "group_properties"):
                self.group_properties.set_buses(bus_names)
            # Load samples and zone mapping
            groups_elem = root.find(".//groups")
            self.sample_browser.sample_list.clear()
            self.sample_browser.zone_map.clear()
            if groups_elem is not None:
                for group in groups_elem.findall("group"):
                    for sample in group.findall("sample"):
                        path = sample.attrib.get("path", "")
                        lo = int(sample.attrib.get("loNote", 0))
                        hi = int(sample.attrib.get("hiNote", 127))
                        root_note = int(sample.attrib.get("rootNote", 60))
                        self.sample_browser.sample_list.addItem(path)
                        self.sample_browser.zone_map[path] = {
                            "loNote": lo, "hiNote": hi, "rootNote": root_note
                        }
            # Load UI elements and tabs
            ui_elem = root.find(".//ui")
            if ui_elem is not None:
                while self.tab_widget.count() > 0:
                    self.tab_widget.removeTab(0)
                self.visual_canvases.clear()
                tabs = [tab for tab in ui_elem if tab.tag == "tab"]
                if not tabs:
                    tabs = [ui_elem]
                for tab in tabs:
                    tab_name = tab.attrib.get("name", "main")
                    canvas = VisualCanvas(main_window=self)
                    canvas.properties_panel = self.properties_panel
                    # Set canvas size and background from <ui> attributes
                    ui_parent = tab.getparent() if hasattr(tab, "getparent") else ui_elem
                    ui_attrib = ui_parent.attrib if ui_parent is not None else ui_elem.attrib
                    try:
                        width = int(ui_attrib.get("width", 812))
                        height = int(ui_attrib.get("height", 375))
                    except Exception:
                        width, height = 812, 375
                    bg_image = ui_attrib.get("bgImage", None)
                    canvas.set_canvas_dimensions_and_bg(width, height, bg_image)
                    # Populate canvas with widgets from XML
                    for widget_el in tab:
                        try:
                            tag = widget_el.tag.lower()
                            attrs = dict(widget_el.attrib)
                            # Map DecentSampler XML tags to widget classes
                            from widgets import KnobWidget, SliderWidget, ButtonWidget, MenuWidget, LabelWidget, DraggableElementLabel
                            if tag == "labeled-knob":
                                widget_class = KnobWidget
                                attrs["type"] = "Knob"
                            elif tag == "control":
                                style = attrs.get("style", "").lower()
                                if "linear" in style:
                                    widget_class = SliderWidget
                                    attrs["type"] = "Slider"
                                else:
                                    widget_class = DraggableElementLabel
                                    attrs["type"] = "Unknown"
                            elif tag == "label":
                                widget_class = LabelWidget
                                attrs["type"] = "Label"
                            elif tag == "menu":
                                widget_class = MenuWidget
                                attrs["type"] = "Menu"
                            elif tag == "button":
                                widget_class = ButtonWidget
                                attrs["type"] = "Button"
                            else:
                                widget_class = DraggableElementLabel
                                attrs["type"] = tag.capitalize()
                            label = widget_class(tag.capitalize(), canvas) if widget_class is DraggableElementLabel else widget_class(canvas)
                            if hasattr(label, "attrs"):
                                label.attrs = dict(attrs)
                                if hasattr(label, "update_from_attrs"):
                                    label.update_from_attrs()
                            label.show()
                            if hasattr(label, "setToolTip"):
                                label.setToolTip(attrs.get("label", attrs.get("type", tag.capitalize())))
                            canvas.elements.append(label)
                        except Exception as e:
                            print(f"[MainWindow] Failed to instantiate widget '{tag}': {e}")
                    self.visual_canvases[tab_name] = canvas
                    self.tab_widget.addTab(canvas, tab_name)
                self.tab_widget.setCurrentIndex(0)
            QMessageBox.information(self, "File Opened", f"Successfully opened:\n{file_name}")
            self._add_to_recent_files(file_name)
        except Exception as e:
            self.show_error("Open", f"Failed to load .dspreset:\n{e}")

    def _createCentralWidget(self):
        self.central = QWidget()
        self.central_layout = QHBoxLayout()
        # --- Help Dock Widget ---
        from PyQt5.QtWidgets import QTextEdit, QDockWidget
        help_text = (
            "<h2>Welcome to Decent Sampler Visual Editor</h2>"
            "<ul>"
            "<li><b>Drag widgets</b> from the Widget Palette onto the canvas.</li>"
            "<li><b>Resize</b> and <b>move</b> widgets with your mouse.</li>"
            "<li><b>Edit properties</b> in the Properties Panel.</li>"
            "<li><b>Keyboard Shortcuts:</b>"
            "<ul>"
            "<li><b>Delete/Backspace</b>: Delete selected widget</li>"
            "<li><b>Ctrl+D</b>: Duplicate selected widget</li>"
            "<li><b>Ctrl+C</b>: Copy selected widget</li>"
            "<li><b>Ctrl+V</b>: Paste widget</li>"
            "</ul></li>"
            "<li><b>Panels</b> can be rearranged, docked, or floated.</li>"
            "<li>All controls have tooltips and are accessible via keyboard navigation.</li>"
            "<li>For more help, see the README or documentation.</li>"
            "</ul>"
        )
        self.help_text_widget = QTextEdit()
        self.help_text_widget.setReadOnly(True)
        self.help_text_widget.setHtml(help_text)
        self.help_text_widget.setToolTip("Onboarding and help information")
        self.help_text_widget.setAccessibleName("Help Panel")
        self.help_dock = QDockWidget("Help", self)
        self.help_dock.setWidget(self.help_text_widget)
        self.help_dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, self.help_dock)

        # Widget Palette Dock
        self.widget_palette = PaletteListWidget()
        self.widget_palette.setMinimumWidth(120)
        self.widget_palette.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.widget_palette.setToolTip("Drag UI elements onto the canvas")
        self.widget_palette_dock = QDockWidget("Widget Palette", self)
        self.widget_palette_dock.setWidget(self.widget_palette)
        self.widget_palette_dock.setMinimumWidth(120)
        self.widget_palette_dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.widget_palette_dock)

        # Sample Browser Dock
        self.sample_browser = SampleBrowserWidget()
        self.sample_browser.setMinimumWidth(180)
        self.sample_browser.setToolTip("Browse and import samples")
        self.sample_dock = QDockWidget("Sample Mapping", self)
        self.sample_dock.setWidget(self.sample_browser)
        self.sample_dock.setMinimumWidth(180)
        self.sample_dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sample_dock)

        # Group Properties Dock
        self.group_properties = GroupPropertiesWidget(main_window=self)
        self.group_properties.setMinimumWidth(180)
        self.group_properties.setToolTip("Edit group envelope and velocity mapping")
        self.group_dock = QDockWidget("Group Envelope", self)
        self.group_dock.setWidget(self.group_properties)
        self.group_dock.setMinimumWidth(180)
        self.group_dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.group_dock)

        # Bus Routing Dock
        self.bus_routing = BusRoutingWidget()
        self.bus_routing.setMinimumWidth(180)
        self.bus_routing.setToolTip("Bus routing and send levels")
        self.bus_dock = QDockWidget("Routing", self)
        self.bus_dock.setWidget(self.bus_routing)
        self.bus_dock.setMinimumWidth(180)
        self.bus_dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.bus_dock)

        # Piano Keyboard Dock
        self.piano_keyboard = PianoKeyboardWidget(main_window=self)
        self.piano_keyboard.setMinimumHeight(100)
        self.piano_keyboard.setToolTip("MIDI keyboard for auditioning zones")
        self.piano_dock = QDockWidget("Piano Keyboard", self)
        self.piano_dock.setWidget(self.piano_keyboard)
        self.piano_dock.setMinimumHeight(100)
        self.piano_dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.piano_dock)

        # Main Editor Area (Splitter)
        self.editor_tabs = QTabWidget()
        design_tab = QWidget()
        design_layout = QHBoxLayout()
        design_layout.setContentsMargins(5, 5, 5, 5)
        design_layout.setSpacing(10)
        self.tab_widget = QTabWidget()
        self.visual_canvases = {}
        self.properties_panel = QWidget()
        prop_layout = QFormLayout()
        prop_layout.addRow(QLabel("Properties Panel\n(Attributes for selected element)"))
        self.properties_panel.setLayout(prop_layout)
        self.properties_panel.setMaximumWidth(260)
        self.properties_panel.setMinimumWidth(180)
        self.properties_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.properties_panel.setToolTip("Edit properties of the selected element")
        canvas = VisualCanvas(main_window=self)
        canvas.setMinimumSize(812, 375)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas.setToolTip("Visual editor canvas")
        canvas.properties_panel = self.properties_panel
        self.tab_widget.addTab(canvas, "main")
        self.visual_canvases["main"] = canvas

        # Use a splitter for the design tab (canvas + properties panel)
        design_splitter = QSplitter(Qt.Horizontal)
        design_splitter.addWidget(self.tab_widget)
        design_splitter.addWidget(self.properties_panel)
        design_splitter.setStretchFactor(0, 3)
        design_splitter.setStretchFactor(1, 1)
        design_layout.addWidget(design_splitter)
        design_tab.setLayout(design_layout)

        # XML Tab
        xml_tab = QWidget()
        xml_layout = QVBoxLayout()
        xml_layout.setContentsMargins(5, 5, 5, 5)
        xml_layout.setSpacing(10)

        # --- Find/Replace Bar for XML Editor ---
        self.xml_find_bar = QHBoxLayout()
        self.xml_find_input = QLineEdit()
        self.xml_find_input.setPlaceholderText("Find")
        self.xml_replace_input = QLineEdit()
        self.xml_replace_input.setPlaceholderText("Replace")
        self.xml_find_next_btn = QPushButton("Find Next")
        self.xml_replace_btn = QPushButton("Replace")
        self.xml_replace_all_btn = QPushButton("Replace All")
        self.xml_find_bar.addWidget(QLabel("Find:"))
        self.xml_find_bar.addWidget(self.xml_find_input)
        self.xml_find_bar.addWidget(QLabel("Replace:"))
        self.xml_find_bar.addWidget(self.xml_replace_input)
        self.xml_find_bar.addWidget(self.xml_find_next_btn)
        self.xml_find_bar.addWidget(self.xml_replace_btn)
        self.xml_find_bar.addWidget(self.xml_replace_all_btn)
        xml_layout.addLayout(self.xml_find_bar)

        self.xml_editor = QPlainTextEdit()
        self.xml_editor.setAcceptDrops(False)
        xml_layout.addWidget(self.xml_editor)
        xml_tab.setLayout(xml_layout)

        # Find/Replace logic
        self._xml_find_pos = 0
        self.xml_find_next_btn.clicked.connect(self.find_next_in_xml)
        self.xml_replace_btn.clicked.connect(self.replace_in_xml)
        self.xml_replace_all_btn.clicked.connect(self.replace_all_in_xml)
        self.xml_find_input.returnPressed.connect(self.find_next_in_xml)
        self.xml_replace_input.returnPressed.connect(self.replace_in_xml)

        self.editor_tabs.addTab(design_tab, "Design")
        self.editor_tabs.addTab(xml_tab, "XML")
        # Tab change sync logic
        self.editor_tabs.currentChanged.connect(self._on_tab_changed)

        # Main splitter for central widget (editor tabs only, since docks are handled separately)
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(self.editor_tabs)
        main_splitter.setStretchFactor(0, 3)
        self.central_layout.setContentsMargins(5, 5, 5, 5)
        self.central_layout.setSpacing(10)
        self.central_layout.addWidget(main_splitter)
        self.central.setLayout(self.central_layout)
        self.setCentralWidget(self.central)
        self.setMinimumSize(1200, 900)

    def _on_tab_changed(self, idx):
        # 0 = Design, 1 = XML
        if not hasattr(self, "_last_xml_text"):
            self._last_xml_text = ""
        if idx == 1:
            # Before switching to XML tab, sync all canvases to XML
            for i in range(self.tab_widget.count()):
                canvas = self.tab_widget.widget(i)
                if hasattr(canvas, "update_xml_from_canvas"):
                    canvas.update_xml_from_canvas()
            # XML tab: make editor editable
            self.xml_editor.setReadOnly(False)
            # Track the XML text for undo/redo
            self._last_xml_text = self.xml_editor.toPlainText()
        else:
            # Leaving XML tab: if XML changed, push XmlEditCommand
            new_xml = self.xml_editor.toPlainText()
            old_xml = getattr(self, "_last_xml_text", "")
            if new_xml != old_xml and hasattr(self, "undo_stack"):
                import commands
                cmd = commands.XmlEditCommand(self, old_xml, new_xml)
                self.undo_stack.push(cmd)
                self._last_xml_text = new_xml
            # Design tab: try to parse XML and update xml_root and canvas
            xml_text = self.xml_editor.toPlainText()
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(xml_text)
                self.xml_root = root
                # Repopulate the canvas from XML
                ui_elem = root.find(".//ui")
                if ui_elem is not None:
                    widget_tags = {"knob", "slider", "button", "menu", "label", "labeled-knob", "control"}
                    # Find <tab> elements if present
                    tabs = [tab for tab in ui_elem if tab.tag == "tab"]
                    # Determine which tab to use (default to first if multiple)
                    if tabs:
                        # Use the currently selected tab index if possible
                        tab_idx = self.tab_widget.currentIndex() if self.tab_widget.count() > 0 else 0
                        tab_elem = tabs[tab_idx] if tab_idx < len(tabs) else tabs[0]
                        widget_parent = tab_elem
                    else:
                        widget_parent = ui_elem
                    for i in range(self.tab_widget.count()):
                        canvas = self.tab_widget.widget(i)
                        # Remove only widgets tracked in canvas.elements
                        for widget in list(canvas.elements):
                            widget.setParent(None)
                        canvas.elements.clear()
                        for widget_el in widget_parent:
                            if widget_el.tag.lower() not in widget_tags:
                                continue
                            try:
                                tag = widget_el.tag.lower()
                                attrs = dict(widget_el.attrib)
                                # Map DecentSampler XML tags to widget classes
                                if tag == "labeled-knob":
                                    widget_class = KnobWidget
                                    attrs["type"] = "Knob"
                                elif tag == "control":
                                    style = attrs.get("style", "").lower()
                                    if "linear" in style:
                                        widget_class = SliderWidget
                                        attrs["type"] = "Slider"
                                    else:
                                        widget_class = DraggableElementLabel
                                        attrs["type"] = "Unknown"
                                elif tag == "label":
                                    widget_class = LabelWidget
                                    attrs["type"] = "Label"
                                elif tag == "menu":
                                    widget_class = MenuWidget
                                    attrs["type"] = "Menu"
                                elif tag == "button":
                                    widget_class = ButtonWidget
                                    attrs["type"] = "Button"
                                elif tag == "slider":
                                    widget_class = SliderWidget
                                    attrs["type"] = "Slider"
                                elif tag == "knob":
                                    widget_class = KnobWidget
                                    attrs["type"] = "Knob"
                                else:
                                    widget_class = DraggableElementLabel
                                    attrs["type"] = tag.capitalize()
                                label = widget_class(tag.capitalize(), canvas) if widget_class is DraggableElementLabel else widget_class(canvas)
                                if hasattr(label, "attrs"):
                                    label.attrs = dict(attrs)
                                    if hasattr(label, "update_from_attrs"):
                                        label.update_from_attrs()
                                label.show()
                                if hasattr(label, "setToolTip"):
                                    label.setToolTip(attrs.get("label", attrs.get("type", tag.capitalize())))
                                canvas.elements.append(label)
                            except Exception as e:
                                print(f"[MainWindow] Failed to instantiate widget '{tag}': {e}")
            except Exception as e:
                QMessageBox.critical(self, "XML Parse Error", f"Failed to parse XML:\n{e}")
                # Revert editor to last valid xml_root
                import io
                buf = io.BytesIO()
                tree = ET.ElementTree(self.xml_root)
                tree.write(buf, encoding="utf-8", xml_declaration=True)
                xml_str = buf.getvalue().decode("utf-8")
                self.xml_editor.setPlainText(xml_str)

    def show_error(self, title, msg):
        utils.show_error(self, title, msg)

    def open_file(self):
        last_open_folder = self.settings.value("last_open_folder", "")
        file_name, _ = QFileDialog.getOpenFileName(self, "Open .dspreset File", last_open_folder, "Decent Sampler Preset (*.dspreset);;All Files (*)")
        if file_name:
            self.open_file_from_path(file_name)
            self._add_to_recent_files(file_name)

    def save_file(self):
        if not hasattr(self, "_last_save_path") or not self._last_save_path:
            return self.save_file_as()
        path = self._last_save_path
        self._save_to_path(path)

    def save_file_as(self):
        last_save_folder = self.settings.value("last_save_folder", "")
        path, _ = QFileDialog.getSaveFileName(self, "Save As .dspreset", last_save_folder, "Decent Sampler Preset (*.dspreset)")
        if not path:
            return
        self.settings.setValue("last_save_folder", os.path.dirname(path))
        self._last_save_path = path
        self._add_to_recent_files(path)
        self._save_to_path(path)

    def _save_to_path(self, path):
        try:
            xml_text = self.xml_editor.toPlainText()
            root = ET.fromstring(xml_text)
            groups_el = root.find(".//groups")
            if groups_el is None:
                groups_el = ET.SubElement(root, "groups")
            for group in list(groups_el):
                groups_el.remove(group)
            if hasattr(self, "bus_routing"):
                for bus_elem in root.findall(".//bus"):
                    parent = bus_elem.getparent() if hasattr(bus_elem, "getparent") else None
                    if parent is not None:
                        parent.remove(bus_elem)
                    else:
                        try:
                            root.remove(bus_elem)
                        except Exception:
                            pass
                for bus_name in self.bus_routing.get_buses():
                    ET.SubElement(root, "bus", {"name": bus_name})
            rr, random_mode = False, False
            if hasattr(self, "sample_browser"):
                rr, random_mode = self.sample_browser.get_play_modes()
            group_attrs = {"enabled": "true"}
            if rr:
                group_attrs["rr"] = "true"
            if random_mode:
                group_attrs["random"] = "true"
            group_el = ET.SubElement(groups_el, "group", group_attrs)
            if hasattr(self, "group_properties"):
                lo_vel, hi_vel = self.group_properties.get_velocity_range()
                ET.SubElement(
                    group_el, "velocity",
                    {
                        "low": str(lo_vel),
                        "high": str(hi_vel)
                    }
                )
            if hasattr(self, "group_properties"):
                send_levels = self.group_properties.get_send_levels()
                for bus, level in send_levels.items():
                    ET.SubElement(
                        group_el, "send",
                        {
                            "bus": bus,
                            "level": str(level)
                        }
                    )
            if hasattr(self, "group_properties"):
                attack, decay, sustain, release = self.group_properties.get_adsr()
                ET.SubElement(
                    group_el, "envelope",
                    {
                        "attack": str(attack),
                        "decay": str(decay),
                        "sustain": str(sustain),
                        "release": str(release)
                    }
                )
            for sample_path, zone in self.sample_browser.zone_map.items():
                ET.SubElement(group_el, "sample", {
                    "path": sample_path,
                    "rootNote": str(zone["rootNote"]),
                    "loNote": str(zone["loNote"]),
                    "hiNote": str(zone["hiNote"])
                })
            tree = ET.ElementTree(root)
            tree.write(path, encoding="utf-8", xml_declaration=True)
            QMessageBox.information(self, "File Saved", f"File saved successfully:\n{path}")
        except Exception as e:
            self.show_error("Save Error", f"Failed to save file:\n{path}\n\n{e}")

    def new_project(self):
        import xml.etree.ElementTree as ET
        root = ET.Element("DecentSampler", {"minVersion": "1.0.2", "presetName": "Untitled"})
        ui_elem = ET.SubElement(root, "ui", {"width": "812", "height": "375"})
        self.xml_root = root
        import io
        buf = io.BytesIO()
        tree = ET.ElementTree(root)
        tree.write(buf, encoding="utf-8", xml_declaration=True)
        xml_str = buf.getvalue().decode("utf-8")
        self.xml_editor.setPlainText(xml_str)
        while self.tab_widget.count() > 0:
            self.tab_widget.removeTab(0)
        self.visual_canvases.clear()
        canvas = VisualCanvas(main_window=self)
        canvas.properties_panel = self.properties_panel
        # No widgets to add for a new project
        self.tab_widget.addTab(canvas, "main")
        self.visual_canvases["main"] = canvas
        self.tab_widget.setCurrentIndex(0)

    def sync_views_after_undo_redo(self, idx):
        # Sync all canvases and XML editor after undo/redo
        for canvas in self.visual_canvases.values():
            if hasattr(canvas, "update_xml_from_canvas"):
                canvas.update_xml_from_canvas()
        # Optionally, update the XML editor with the main canvas's XML
        if "main" in self.visual_canvases:
            main_canvas = self.visual_canvases["main"]
            if hasattr(main_canvas, "main_window") and hasattr(main_canvas.main_window, "xml_editor"):
                # xml_editor is already updated by update_xml_from_canvas
                pass

    # --- Find/Replace Methods for XML Editor ---
    def find_next_in_xml(self):
        text = self.xml_editor.toPlainText()
        find_str = self.xml_find_input.text()
        if not find_str:
            return
        cursor = self.xml_editor.textCursor()
        start = cursor.selectionEnd() if cursor.hasSelection() else cursor.position()
        idx = text.find(find_str, start)
        if idx == -1 and start > 0:
            # Wrap around
            idx = text.find(find_str, 0)
        if idx != -1:
            cursor.setPosition(idx)
            cursor.setPosition(idx + len(find_str), cursor.KeepAnchor)
            self.xml_editor.setTextCursor(cursor)
            self.xml_editor.ensureCursorVisible()
            self._xml_find_pos = idx + len(find_str)
        else:
            # Not found, clear selection
            cursor.clearSelection()
            self.xml_editor.setTextCursor(cursor)

    def replace_in_xml(self):
        cursor = self.xml_editor.textCursor()
        find_str = self.xml_find_input.text()
        replace_str = self.xml_replace_input.text()
        if cursor.hasSelection() and cursor.selectedText() == find_str:
            cursor.insertText(replace_str)
        self.find_next_in_xml()

    def replace_all_in_xml(self):
        text = self.xml_editor.toPlainText()
        find_str = self.xml_find_input.text()
        replace_str = self.xml_replace_input.text()
        if not find_str:
            return
        new_text = text.replace(find_str, replace_str)
        if new_text != text:
            self.xml_editor.setPlainText(new_text)

def main():
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setAttribute(Qt.AA_DontShowIconsInMenus, True)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    import utils
    if hasattr(utils, "global_style"):
        app.setStyleSheet(utils.global_style)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
