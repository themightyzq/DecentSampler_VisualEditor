from PyQt5.QtWidgets import QWidget, QSizePolicy, QLineEdit, QPushButton, QFormLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from widgets import DraggableElementLabel

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
        self._out_of_bounds_warned = False

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        try:
            text = event.mimeData().text()
            # Map text to widget class
            from widgets import KnobWidget, SliderWidget, ButtonWidget, MenuWidget, LabelWidget
            widget_map = {
                "Knob": KnobWidget,
                "Slider": SliderWidget,
                "Button": ButtonWidget,
                "Menu": MenuWidget,
                "Label": LabelWidget,
            }
            widget_class = widget_map.get(text, DraggableElementLabel)
            pos = event.pos()
            attrs = {
                "type": text,
                "x": pos.x(),
                "y": pos.y(),
            }
            w = widget_class(text, self) if widget_class is DraggableElementLabel else widget_class(self)
            if hasattr(w, "attrs"):
                w.attrs.update(attrs)
                if hasattr(w, "update_from_attrs"):
                    w.update_from_attrs()
            w.move(pos)
            w.show()
            w.raise_()
            self.elements.append(w)
            self.select_element(w)
            self.update_xml_from_canvas()
            if self.main_window and hasattr(self.main_window, "visual_canvases"):
                if "main" not in self.main_window.visual_canvases.values():
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
        base_keys = ["x", "y", "width", "height", "label"]
        shown_keys = set()
        for key in base_keys:
            edit = QLineEdit(str(element.attrs.get(key, "")))
            layout.addRow(f"{key}:", edit)
            fields[key] = edit
            shown_keys.add(key)
        for key in sorted(element.attrs.keys()):
            if key in shown_keys or key == "type":
                continue
            edit = QLineEdit(str(element.attrs.get(key, "")))
            layout.addRow(f"{key}:", edit)
            fields[key] = edit
        def on_attr_change():
            try:
                for key, edit in fields.items():
                    val = edit.text()
                    if key in ["x", "y", "width", "height"]:
                        try:
                            val = int(val)
                        except Exception:
                            QMessageBox.warning(self, "Invalid Value", f"{key} must be an integer.")
                            val = 0
                    element.attrs[key] = val
                element.update_from_attrs()
                self.update_xml_from_canvas()
            except Exception as e:
                QMessageBox.critical(self, "Edit Error", f"Failed to update element:\n{e}")
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
            # Use the same widget class as in dropEvent
            from widgets import KnobWidget, SliderWidget, ButtonWidget, MenuWidget, LabelWidget, DraggableElementLabel
            widget_map = {
                "Knob": KnobWidget,
                "Slider": SliderWidget,
                "Button": ButtonWidget,
                "Menu": MenuWidget,
                "Label": LabelWidget,
            }
            widget_type = attrs.get("type", "")
            widget_class = widget_map.get(widget_type, DraggableElementLabel)
            label = widget_class(widget_type, self) if widget_class is DraggableElementLabel else widget_class(self)
            if hasattr(label, "attrs"):
                label.attrs = dict(attrs)
                if hasattr(label, "update_from_attrs"):
                    label.update_from_attrs()
            label.show()
            if hasattr(label, "setToolTip"):
                label.setToolTip(f"{widget_type} (duplicated)")
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
            # Use the same widget class as in dropEvent
            from widgets import KnobWidget, SliderWidget, ButtonWidget, MenuWidget, LabelWidget, DraggableElementLabel
            widget_map = {
                "Knob": KnobWidget,
                "Slider": SliderWidget,
                "Button": ButtonWidget,
                "Menu": MenuWidget,
                "Label": LabelWidget,
            }
            widget_type = attrs.get("type", "")
            widget_class = widget_map.get(widget_type, DraggableElementLabel)
            label = widget_class(widget_type, self) if widget_class is DraggableElementLabel else widget_class(self)
            if hasattr(label, "attrs"):
                label.attrs = dict(attrs)
                if hasattr(label, "update_from_attrs"):
                    label.update_from_attrs()
            label.show()
            if hasattr(label, "setToolTip"):
                label.setToolTip(f"{widget_type} (pasted)")
            self.elements.append(label)
            self.select_element(label)
            self.update_xml_from_canvas()

    def update_xml_from_canvas(self):
        """
        Sync the current canvas elements to the XML and update the xml_editor in MainWindow.
        Uses main_window.xml_root as the source of truth, not the possibly-edited xml_editor text.
        """
        if not self.main_window or not hasattr(self.main_window, "xml_editor") or not hasattr(self.main_window, "xml_root"):
            return
        import xml.etree.ElementTree as ET

        # Use the in-memory XML root as the source of truth
        root = self.main_window.xml_root
        if root is None:
            return

        # Find or create the <ui> or <tab> element
        ui_elem = root.find(".//ui")
        if ui_elem is None:
            ui_elem = ET.SubElement(root, "ui", {"width": "812", "height": "375"})

        # Remove all existing child elements (widgets) from <ui> or <tab>
        for child in list(ui_elem):
            ui_elem.remove(child)

        # Add current canvas elements as XML children
        for elem in self.elements:
            widget_el = ET.SubElement(ui_elem, elem.attrs["type"].lower())
            for k, v in elem.attrs.items():
                if k == "type":
                    continue
                widget_el.set(k, str(v))

        # Write the updated XML back to the xml_editor
        import io
        buf = io.BytesIO()
        tree = ET.ElementTree(root)
        tree.write(buf, encoding="utf-8", xml_declaration=True)
        xml_str = buf.getvalue().decode("utf-8")
        self.main_window.xml_editor.setPlainText(xml_str)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        out_of_bounds = []
        for elem in self.elements:
            if (
                elem.x() + elem.width() > self.width()
                or elem.y() + elem.height() > self.height()
                or elem.x() < 0
                or elem.y() < 0
            ):
                out_of_bounds.append(elem)
        if out_of_bounds and not self._out_of_bounds_warned:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Widget(s) Out of View",
                "One or more widgets are outside the visible canvas area. "
                "Resize or move them to bring them back into view."
            )
            self._out_of_bounds_warned = True
        elif not out_of_bounds:
            self._out_of_bounds_warned = False
