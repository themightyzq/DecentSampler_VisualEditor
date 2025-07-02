import sys
import os
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QAction, QMessageBox, QListWidget, QSplitter, QTabWidget, QPlainTextEdit, QPushButton, QFormLayout, QSizePolicy, QLineEdit, QSpinBox, QGroupBox, QDockWidget
)
from PyQt5.QtCore import Qt, QPoint, QSettings
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QFont
from PyQt5.QtGui import QKeySequence

class DraggableElementLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("background: #fff; border: 1px solid #888; padding: 2px;")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.selected = False
        self.dragging = False
        self.offset = None
        self.attrs = {
            "type": text,
            "x": 0,
            "y": 0,
            "width": 80,
            "height": 30,
            "label": text
        }
        self.xml_elem = None  # Reference to the corresponding XML element
        self.setFixedSize(self.attrs["width"], self.attrs["height"])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.parent().select_element(self)
            self.update_style()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            new_pos = self.mapToParent(event.pos() - self.offset)
            self.move(new_pos)
            self.attrs["x"] = self.x()
            self.attrs["y"] = self.y()
            self.parent().update_properties_panel(self)
            self.parent().update_xml_from_canvas()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.offset = None
        super().mouseReleaseEvent(event)

    def update_style(self):
        if self.selected:
            self.setStyleSheet("background: #e0f7fa; border: 2px solid #00796b; padding: 2px;")
        else:
            self.setStyleSheet("background: #fff; border: 1px solid #888; padding: 2px;")

    def update_from_attrs(self):
        self.setText(self.attrs.get("label", self.attrs.get("type", "")))
        self.setFixedSize(int(self.attrs.get("width", 80)), int(self.attrs.get("height", 30)))
        self.move(int(self.attrs.get("x", 0)), int(self.attrs.get("y", 0)))

class VisualCanvas(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet("background: #f0f0f0; border: 1px solid #bbb;")
        self.setMinimumSize(400, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.elements = []
        self.selected_element = None
        self.properties_panel = None
        self.clipboard = None
        self.xml_ui_elem = None  # Reference to the <ui> or <tab> XML element
        self.main_window = main_window  # Reference to MainWindow for XML sync

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        try:
            text = event.mimeData().text()
            label = DraggableElementLabel(text, self)
            pos = event.pos()
            label.attrs.update({
                "type": text,
                "x": pos.x(),
                "y": pos.y(),
            })
            label.update_from_attrs()
            label.show()
            label.raise_()
            self.elements.append(label)
            self.select_element(label)
            self.update_xml_from_canvas()
            # Ensure this canvas is registered in the main window's visual_canvases
            if self.main_window and hasattr(self.main_window, "visual_canvases"):
                if "main" not in self.main_window.visual_canvases.values():
                    # If not present, add it as "main" or with a unique name
                    self.main_window.visual_canvases["main"] = self
            event.acceptProposedAction()
        except Exception as e:
            import traceback
            print("Exception in dropEvent:", e)
            traceback.print_exc()

    def mousePressEvent(self, event):
        self.setFocus()
        super().mousePressEvent(event)

    def select_element(self, element):
        if self.selected_element and self.selected_element is not element:
            self.selected_element.selected = False
            self.selected_element.update_style()
        self.selected_element = element
        element.selected = True
        element.update_style()
        self.update_properties_panel(element)

    def update_properties_panel(self, element):
        if not self.properties_panel:
            return
        for i in reversed(range(self.properties_panel.layout().count())):
            widget = self.properties_panel.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        layout = self.properties_panel.layout()
        layout.addWidget(QLabel("Properties Panel\n(Attributes for selected element)"))
        fields = {}
        for key in ["x", "y", "width", "height", "label"]:
            edit = QLineEdit(str(element.attrs.get(key, "")))
            layout.addRow(f"{key}:", edit)
            fields[key] = edit
        def on_attr_change():
            for key, edit in fields.items():
                val = edit.text()
                if key in ["x", "y", "width", "height"]:
                    try:
                        val = int(val)
                    except Exception:
                        val = 0
                element.attrs[key] = val
            element.update_from_attrs()
            self.update_xml_from_canvas()
        for edit in fields.values():
            edit.editingFinished.connect(on_attr_change)
        del_btn = QPushButton("Delete Element")
        def on_delete():
            self.delete_selected_element()
        del_btn.clicked.connect(on_delete)
        layout.addRow(del_btn)

    def keyPressEvent(self, event):
        ctrl = (event.modifiers() & Qt.ControlModifier) or (event.modifiers() & Qt.MetaModifier)
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.delete_selected_element()
        elif event.key() == Qt.Key_D and ctrl:
            self.duplicate_selected_element()
        elif event.key() == Qt.Key_C and ctrl:
            self.copy_selected_element()
        elif event.key() == Qt.Key_V and ctrl:
            self.paste_element()
        else:
            super().keyPressEvent(event)

    def delete_selected_element(self):
        if self.selected_element:
            self.selected_element.setParent(None)
            if self.selected_element in self.elements:
                self.elements.remove(self.selected_element)
            self.selected_element = None
            if self.properties_panel:
                for i in reversed(range(self.properties_panel.layout().count())):
                    widget = self.properties_panel.layout().itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
            self.update_xml_from_canvas()

    def duplicate_selected_element(self):
        if self.selected_element:
            attrs = dict(self.selected_element.attrs)
            attrs["x"] = int(attrs.get("x", 0)) + 20
            attrs["y"] = int(attrs.get("y", 0)) + 20
            label = DraggableElementLabel(attrs.get("type", ""), self)
            label.attrs = dict(attrs)
            label.update_from_attrs()
            label.show()
            self.elements.append(label)
            self.select_element(label)
            self.update_xml_from_canvas()

    def copy_selected_element(self):
        if self.selected_element:
            self.clipboard = dict(self.selected_element.attrs)

    def paste_element(self):
        if self.clipboard:
            attrs = dict(self.clipboard)
            attrs["x"] = int(attrs.get("x", 0)) + 20
            attrs["y"] = int(attrs.get("y", 0)) + 20
            label = DraggableElementLabel(attrs.get("type", ""), self)
            label.attrs = dict(attrs)
            label.update_from_attrs()
            label.show()
            self.elements.append(label)
            self.select_element(label)
            self.update_xml_from_canvas()

    def update_xml_from_canvas(self):
        try:
            # If no XML tree exists, create a new one
            if self.xml_ui_elem is None or not hasattr(self.main_window, "xml_root") or self.main_window.xml_root is None:
                # Create a new root and <ui> element
                root = ET.Element("DecentSampler", {"minVersion": "1.0.2", "presetName": "Untitled"})
                ui_elem = ET.SubElement(root, "ui", {
                    "width": "812",
                    "height": "375"
                })
                self.xml_ui_elem = ui_elem
                # Register the root on the main window for global access
                if self.main_window:
                    self.main_window.xml_root = root
                    if hasattr(self.main_window, "visual_canvases") and "main" not in self.main_window.visual_canvases:
                        self.main_window.visual_canvases["main"] = self
            # Remove all existing UI children
            for child in list(self.xml_ui_elem):
                self.xml_ui_elem.remove(child)
            # Add current elements as XML
            for el in self.elements:
                attrib = {
                    "x": str(el.attrs.get("x", 0)),
                    "y": str(el.attrs.get("y", 0)),
                    "width": str(el.attrs.get("width", 80)),
                    "height": str(el.attrs.get("height", 30)),
                    "label": el.attrs.get("label", el.attrs.get("type", ""))
                }
                ET.SubElement(self.xml_ui_elem, el.attrs.get("type", "control"), attrib)
            # Update the XML editor in the main window
            if self.main_window and hasattr(self.main_window, "xml_editor") and self.main_window.xml_editor:
                # Always serialize from the root <DecentSampler> element
                root = getattr(self.main_window, "xml_root", None)
                if root is None:
                    # fallback: just use self.xml_ui_elem
                    root = self.xml_ui_elem
                try:
                    tree = ET.ElementTree(root)
                    import io
                    buf = io.BytesIO()
                    tree.write(buf, encoding="utf-8", xml_declaration=True)
                    xml_str = buf.getvalue().decode("utf-8")
                except Exception:
                    # Fallback: just dump the xml_ui_elem
                    xml_str = ET.tostring(self.xml_ui_elem, encoding="unicode")
                self.main_window.xml_editor.setPlainText(xml_str)
        except Exception as e:
            import traceback
            print("Exception in update_xml_from_canvas:", e)
            traceback.print_exc()

class SampleBrowserWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.zone_map = {}  # path -> {loNote, hiNote, rootNote}
        self.layout = QVBoxLayout()
        self.sample_list = QListWidget()
        self.layout.addWidget(QLabel("Samples"))
        self.layout.addWidget(self.sample_list)
        import_btn = QPushButton("Import Samples")
        import_btn.clicked.connect(self.import_samples)
        self.layout.addWidget(import_btn)

        # Zone mapping panel
        self.zone_group = QGroupBox("Keyzone Mapping")
        zone_layout = QFormLayout()
        self.lo_spin = QSpinBox()
        self.lo_spin.setRange(0, 127)
        self.hi_spin = QSpinBox()
        self.hi_spin.setRange(0, 127)
        self.root_spin = QSpinBox()
        self.root_spin.setRange(0, 127)
        zone_layout.addRow("Low Note", self.lo_spin)
        zone_layout.addRow("High Note", self.hi_spin)
        zone_layout.addRow("Root Note", self.root_spin)
        self.zone_group.setLayout(zone_layout)
        self.layout.addWidget(self.zone_group)
        self.setLayout(self.layout)

        self.sample_list.currentItemChanged.connect(self.on_sample_selected)
        self.lo_spin.valueChanged.connect(self._on_spin_changed)
        self.hi_spin.valueChanged.connect(self._on_spin_changed)
        self.root_spin.valueChanged.connect(self._on_spin_changed)

    def import_samples(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Import WAV Samples", "", "WAV Files (*.wav)")
        for f in files:
            rel_path = os.path.relpath(f, os.getcwd())
            self.sample_list.addItem(rel_path)
            self.zone_map[rel_path] = {"loNote": 0, "hiNote": 127, "rootNote": 60}

    def on_sample_selected(self, curr, prev):
        if curr:
            path = curr.text()
            zone = self.zone_map.get(path, {"loNote": 0, "hiNote": 127, "rootNote": 60})
            self.lo_spin.blockSignals(True)
            self.hi_spin.blockSignals(True)
            self.root_spin.blockSignals(True)
            self.lo_spin.setValue(zone["loNote"])
            self.hi_spin.setValue(zone["hiNote"])
            self.root_spin.setValue(zone["rootNote"])
            self.lo_spin.blockSignals(False)
            self.hi_spin.blockSignals(False)
            self.root_spin.blockSignals(False)

    def _on_spin_changed(self):
        curr = self.sample_list.currentItem()
        if curr:
            path = curr.text()
            self.zone_map[path] = {
                "loNote": self.lo_spin.value(),
                "hiNote": self.hi_spin.value(),
                "rootNote": self.root_spin.value()
            }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Decent Sampler Visual Editor")
        self.setGeometry(100, 100, 1200, 800)
        self._createMenuBar()
        self._createCentralWidget()

    def _createMenuBar(self):
        self.settings = QSettings("DecentSamplerEditor", "DecentSamplerEditorApp")
        menubar = self.menuBar()
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
        self._recent_files = self._load_recent_files()
        self._recent_files_menu = file_menu.addMenu("Recent Files")
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

    def _update_recent_files_menu(self):
        self._recent_files_menu.clear()
        if not self._recent_files:
            empty_action = QAction("(No Recent Files)", self)
            empty_action.setEnabled(False)
            self._recent_files_menu.addAction(empty_action)
        else:
            for path in self._recent_files:
                action = QAction(path, self)
                action.triggered.connect(lambda checked, p=path: self.open_file_from_path(p))
                self._recent_files_menu.addAction(action)

    def _add_to_recent_files(self, path):
        if not path:
            return
        if path in self._recent_files:
            self._recent_files.remove(path)
        self._recent_files.insert(0, path)
        self._recent_files = self._recent_files[:10]
        self._save_recent_files()
        self.settings.setValue("recentFiles", self._recent_files)
        self.settings.sync()
        self._update_recent_files_menu()

    def _save_recent_files(self):
        self.settings.setValue("recentFiles", self._recent_files)

    def _load_recent_files(self):
        # Retrieve the recentFiles key as a list directly
        files = self.settings.value("recentFiles", [], type=list)
        # Ensure we have a Python list
        if not isinstance(files, list):
            files = [files] if files else []
        return files

    def open_file_from_path(self, path):
        self._open_file_internal(path)
        self._add_to_recent_files(path)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open .dspreset File", "", "Decent Sampler Preset (*.dspreset);;All Files (*)")
        if file_name:
            self._open_file_internal(file_name)
            self._add_to_recent_files(file_name)

    def _open_file_internal(self, file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                self.xml_editor.setPlainText(f.read())
            self._last_save_path = file_name
            tree = ET.parse(file_name)
            root = tree.getroot()
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
                    bg_color = ui_elem.attrib.get("bgColor", None)
                    bg_image = ui_elem.attrib.get("bgImage", None)
                    width = int(ui_elem.attrib.get("width", 812))
                    height = int(ui_elem.attrib.get("height", 375))
                    style = "border: 1px solid #bbb;"
                    if bg_color:
                        style += f"background: #{bg_color[-6:]};"
                    canvas.setStyleSheet(style)
                    canvas.setFixedSize(width, height)
                    if bg_image:
                        dspreset_dir = os.path.dirname(file_name)
                        image_path = os.path.join(dspreset_dir, bg_image)
                        img_url = image_path.replace("\\", "/")
                        canvas.setStyleSheet(
                            f"background-image: url({img_url}); "
                            "background-repeat: no-repeat; "
                            "background-position: top left; "
                            "border: 1px solid #bbb;"
                        )
                    else:
                        canvas.setStyleSheet("background: #f0f0f0; border: 1px solid #bbb;")
                    for el in list(canvas.elements):
                        el.setParent(None)
                    canvas.elements.clear()
                    canvas.selected_element = None
                    for child in tab:
                        raw = child.attrib
                        attrs = {k: v for k, v in raw.items()}
                        attrs["type"] = child.tag
                        attrs["x"] = int(raw.get("x", 0))
                        attrs["y"] = int(raw.get("y", 0))
                        attrs["width"] = int(raw.get("width", 80))
                        attrs["height"] = int(raw.get("height", 30))
                        attrs["label"] = raw.get("label", child.tag)
                        # WYSIWYG: use custom widgets for each type
                        w = DraggableElementLabel(attrs["label"], canvas)
                        w.attrs = attrs
                        w.update_from_attrs()
                        w.show()
                        w.raise_()
                        canvas.elements.append(w)
                    self.visual_canvases[tab_name] = canvas
                    self.tab_widget.addTab(canvas, tab_name)
                self.tab_widget.setCurrentIndex(0)
            self._add_to_recent_files(file_name)
        except Exception as e:
            QMessageBox.critical(self, "Open", f"Failed to load .dspreset:\n{e}")

    def _createCentralWidget(self):
        self.central = QWidget()
        self.central_layout = QHBoxLayout()

        # Sample browser and zone-mapping sidebar (dockable)
        self.sample_browser = SampleBrowserWidget()
        self.sample_dock = QDockWidget("Sample Mapping", self)
        self.sample_dock.setWidget(self.sample_browser)
        self.sample_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sample_dock)

        # Drag-and-drop palette
        class PaletteListWidget(QListWidget):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.setDragEnabled(True)
            def startDrag(self, supportedActions):
                item = self.currentItem()
                if item:
                    from PyQt5.QtCore import QMimeData
                    from PyQt5.QtGui import QDrag
                    mime = QMimeData()
                    mime.setText(item.text())
                    drag = QDrag(self)
                    drag.setMimeData(mime)
                    drag.exec_(Qt.CopyAction)
        self.palette = PaletteListWidget()
        self.palette.addItems([
            "Knob", "Slider", "Button", "Menu", "Label"
        ])
        self.palette.setMaximumWidth(140)
        self.palette.setMinimumWidth(100)
        self.palette.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # Main editor tabs (Design, XML)
        self.editor_tabs = QTabWidget()
        design_tab = QWidget()
        design_layout = QHBoxLayout()
        self.tab_widget = QTabWidget()
        self.visual_canvases = {}
        self.properties_panel = QWidget()
        prop_layout = QFormLayout()
        prop_layout.addRow(QLabel("Properties Panel\n(Attributes for selected element)"))
        self.properties_panel.setLayout(prop_layout)
        self.properties_panel.setMaximumWidth(220)
        self.properties_panel.setMinimumWidth(160)
        self.properties_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        # Default tab
        canvas = VisualCanvas(main_window=self)
        canvas.properties_panel = self.properties_panel
        self.tab_widget.addTab(canvas, "main")
        self.visual_canvases["main"] = canvas

        # Layout: palette | tabbed canvas | properties
        design_layout.addWidget(self.palette)
        design_layout.addWidget(self.tab_widget)
        design_layout.addWidget(self.properties_panel)
        design_tab.setLayout(design_layout)

        xml_tab = QWidget()
        xml_layout = QVBoxLayout()
        self.xml_editor = QPlainTextEdit()
        xml_layout.addWidget(self.xml_editor)
        xml_tab.setLayout(xml_layout)

        self.editor_tabs.addTab(design_tab, "Design")
        self.editor_tabs.addTab(xml_tab, "XML")

        self.editor_tabs.currentChanged.connect(self.on_tab_changed)

        splitter = QSplitter()
        splitter.addWidget(self.editor_tabs)
        self.central_layout.addWidget(splitter)
        self.central.setLayout(self.central_layout)
        self.setCentralWidget(self.central)

    def new_project(self):
        QMessageBox.information(self, "New Project", "New project functionality coming soon.")

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open .dspreset File", "", "Decent Sampler Preset (*.dspreset);;All Files (*)")
        if file_name:
            self._last_save_path = file_name
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    self.xml_editor.setPlainText(f.read())
                tree = ET.parse(file_name)
                root = tree.getroot()
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
                        bg_color = ui_elem.attrib.get("bgColor", None)
                        bg_image = ui_elem.attrib.get("bgImage", None)
                        width = int(ui_elem.attrib.get("width", 812))
                        height = int(ui_elem.attrib.get("height", 375))
                        style = "border: 1px solid #bbb;"
                        if bg_color:
                            style += f"background: #{bg_color[-6:]};"
                        canvas.setStyleSheet(style)
                        canvas.setFixedSize(width, height)
                        if bg_image:
                            dspreset_dir = os.path.dirname(file_name)
                            image_path = os.path.join(dspreset_dir, bg_image)
                            img_url = image_path.replace("\\", "/")
                            canvas.setStyleSheet(
                                f"background-image: url({img_url}); "
                                "background-repeat: no-repeat; "
                                "background-position: top left; "
                                "border: 1px solid #bbb;"
                            )
                        else:
                            canvas.setStyleSheet("background: #f0f0f0; border: 1px solid #bbb;")
                        for el in list(canvas.elements):
                            el.setParent(None)
                        canvas.elements.clear()
                        canvas.selected_element = None
                        for child in tab:
                            raw = child.attrib
                            attrs = {k: v for k, v in raw.items()}
                            attrs["type"] = child.tag
                            attrs["x"] = int(raw.get("x", 0))
                            attrs["y"] = int(raw.get("y", 0))
                            attrs["width"] = int(raw.get("width", 80))
                            attrs["height"] = int(raw.get("height", 30))
                            attrs["label"] = raw.get("label", child.tag)
                            # WYSIWYG: use custom widgets for each type
                            w = DraggableElementLabel(attrs["label"], canvas)
                            w.attrs = attrs
                            w.update_from_attrs()
                            w.show()
                            w.raise_()
                            canvas.elements.append(w)
                        self.visual_canvases[tab_name] = canvas
                        self.tab_widget.addTab(canvas, tab_name)
                    self.tab_widget.setCurrentIndex(0)
            except Exception as e:
                QMessageBox.critical(self, "Open", f"Failed to load .dspreset:\n{e}")

    def save_file(self):
        # Save to last used path, or prompt if not set
        if not hasattr(self, "_last_save_path") or not self._last_save_path:
            return self.save_file_as()
        path = self._last_save_path
        self._save_to_path(path)

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save As .dspreset", "", "Decent Sampler Preset (*.dspreset)")
        if not path:
            return
        self._last_save_path = path
        self._add_to_recent_files(path)
        self._save_to_path(path)

    def _save_to_path(self, path):
        # Get XML from the editor (which is always in sync with the UI)
        xml_text = self.xml_editor.toPlainText()
        try:
            root = ET.fromstring(xml_text)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Cannot save: XML is invalid.\n\n{e}")
            return
        # Update sample mapping in the XML before saving
        groups_el = root.find(".//groups")
        if groups_el is None:
            groups_el = ET.SubElement(root, "groups")
        # Remove all existing group/sample children
        for group in list(groups_el):
            groups_el.remove(group)
        group_el = ET.SubElement(groups_el, "group", {"enabled": "true"})
        for sample_path, zone in self.sample_browser.zone_map.items():
            ET.SubElement(group_el, "sample", {
                "path": sample_path,
                "rootNote": str(zone["rootNote"]),
                "loNote": str(zone["loNote"]),
                "hiNote": str(zone["hiNote"])
            })
        # Add to recent files before writing
        self._add_to_recent_files(self._last_save_path)
        # Write the updated XML to file
        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)

    def export_canvas_as_image(self):
        pass  # Feature removed

    def on_tab_changed(self, idx):
        # If switching to Design tab, update visual canvases from XML editor
        if self.editor_tabs.tabText(idx) == "Design":
            xml_text = self.xml_editor.toPlainText()
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_text)
                # Load UI elements and tabs as in open_file
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
                        bg_color = ui_elem.attrib.get("bgColor", None)
                        bg_image = ui_elem.attrib.get("bgImage", None)
                        width = int(ui_elem.attrib.get("width", 812))
                        height = int(ui_elem.attrib.get("height", 375))
                        style = "border: 1px solid #bbb;"
                        if bg_color:
                            style += f"background: #{bg_color[-6:]};"
                        canvas.setStyleSheet(style)
                        canvas.setFixedSize(width, height)
                        if bg_image:
                            dspreset_dir = os.getcwd()
                            image_path = os.path.join(dspreset_dir, bg_image)
                            img_url = image_path.replace("\\", "/")
                            canvas.setStyleSheet(
                                f"background-image: url({img_url}); "
                                "background-repeat: no-repeat; "
                                "background-position: top left; "
                                "border: 1px solid #bbb;"
                            )
                        else:
                            canvas.setStyleSheet("background: #f0f0f0; border: 1px solid #bbb;")
                        for el in list(canvas.elements):
                            el.setParent(None)
                        canvas.elements.clear()
                        canvas.selected_element = None
                        for child in tab:
                            raw = child.attrib
                            attrs = {k: v for k, v in raw.items()}
                            attrs["type"] = child.tag
                            attrs["x"] = int(raw.get("x", 0))
                            attrs["y"] = int(raw.get("y", 0))
                            attrs["width"] = int(raw.get("width", 80))
                            attrs["height"] = int(raw.get("height", 30))
                            attrs["label"] = raw.get("label", child.tag)
                            w = DraggableElementLabel(attrs["label"], canvas)
                            w.attrs = attrs
                            w.update_from_attrs()
                            w.show()
                            w.raise_()
                            canvas.elements.append(w)
                        self.visual_canvases[tab_name] = canvas
                        self.tab_widget.addTab(canvas, tab_name)
                    self.tab_widget.setCurrentIndex(0)
            except Exception as e:
                QMessageBox.critical(self, "XML Parse Error", f"Failed to parse XML and update UI:\n{e}")

def main():
    QApplication.setAttribute(Qt.AA_DontShowIconsInMenus, True)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
