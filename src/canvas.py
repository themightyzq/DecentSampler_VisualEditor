from PyQt5.QtWidgets import (
    QWidget, QSizePolicy, QLineEdit, QPushButton, QFormLayout, QLabel,
    QHBoxLayout, QColorDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor
from widgets import DraggableElementLabel

class VisualCanvas(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet("border: 1px solid #bbb;")
        self.setMinimumSize(400, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.elements = []
        self.selected_element = None
        self.properties_panel = None
        self.clipboard = None
        self.xml_ui_elem = None  # Reference to the <ui> or <tab> XML element
        self.main_window = main_window  # Reference to MainWindow for XML sync
        self._out_of_bounds_warned = False
        self._bg_image = None
        self._bg_pixmap = None
        self._bg_color = "#f0f0f0"
        self._text_color = None

    def set_canvas_dimensions_and_bg(self, width, height, bg_image=None, bg_color=None):
        """
        Set the canvas to the exact dimensions specified in the .dspreset <ui>.
        Uses QPixmap for robust image rendering. Handles relative/absolute paths.
        Optionally sets background color.
        """
        self.setFixedSize(width, height)
        self._bg_image = None
        self._bg_pixmap = None
        if bg_color:
            self._bg_color = bg_color
        else:
            self._bg_color = "#f0f0f0"
        if bg_image:
            import os
            orig_bg_image = bg_image
            resolved = False
            preset_path = getattr(self.main_window, "_last_save_path", None)
            if preset_path:
                preset_dir = os.path.dirname(preset_path)
                candidate = os.path.join(preset_dir, bg_image)
                if os.path.exists(candidate):
                    bg_image = candidate
                    resolved = True
            if not resolved and os.path.exists(bg_image):
                resolved = True
            if resolved:
                from PyQt5.QtGui import QPixmap
                self._bg_pixmap = QPixmap(bg_image)
                if self._bg_pixmap.isNull():
                    print(f"[VisualCanvas] QPixmap failed to load image: {bg_image}")
                    self._bg_pixmap = None
                else:
                    print(f"[VisualCanvas] Loaded background image: {bg_image}")
                    self._bg_image = bg_image
            else:
                print(f"[VisualCanvas] Background image not found: {orig_bg_image} (tried: {bg_image})")
        self.update()

    def set_default_text_color(self, color):
        """Set the default text color for the canvas (stub for future use)."""
        self._text_color = color
        # If you have child widgets that should use this color, propagate here
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw background image if available, else fill with solid color
        if self._bg_pixmap:
            painter.drawPixmap(self.rect(), self._bg_pixmap)
        else:
            painter.fillRect(self.rect(), QColor(self._bg_color))
        super().paintEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        try:
            text = event.mimeData().text()
            from widgets import KnobWidget, SliderWidget, ButtonWidget, MenuWidget, LabelWidget
            import commands
            widget_map = {
                "Knob": KnobWidget,
                "Slider": SliderWidget,
                "Button": ButtonWidget,
                "Menu": MenuWidget,
                "Label": LabelWidget,
            }
            widget_class = widget_map.get(text, DraggableElementLabel)
            pos = event.pos()
            x = pos.x()
            y = pos.y()
            if widget_class.__name__ == "KnobWidget":
                knob_height = 100
                max_y = max(0, self.height() - knob_height)
                y = min(y, max_y)
            attrs = {
                "type": text,
                "x": x,
                "y": y,
            }
            if self.main_window and hasattr(self.main_window, "undo_stack"):
                cmd = commands.AddWidgetCommand(self, widget_class, attrs, select_after=True)
                self.main_window.undo_stack.push(cmd)
            else:
                # fallback: direct add (should not happen)
                w = widget_class(text, self) if widget_class is DraggableElementLabel else widget_class(self)
                if hasattr(w, "attrs"):
                    w.attrs.update(attrs)
                    if hasattr(w, "update_from_attrs"):
                        w.update_from_attrs()
                w.move(x, y)
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
        def clear_layout(layout):
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                child_layout = item.layout()
                if widget is not None:
                    widget.setParent(None)
                elif child_layout is not None:
                    clear_layout(child_layout)
        clear_layout(self.properties_panel.layout())
        layout = self.properties_panel.layout()
        layout.addWidget(QLabel("Properties Panel\n(Attributes for selected element)"))
        fields = {}
        base_keys = ["x", "y", "width", "height", "label"]
        shown_keys = set()
        for key in base_keys:
            edit = QLineEdit()
            edit.setText(str(element.attrs.get(key, "")))
            layout.addRow(f"{key}:", edit)
            fields[key] = edit
            shown_keys.add(key)
        for key in sorted(element.attrs.keys()):
            if key in shown_keys or key == "type" or key == "textColorOverride":
                continue
            edit = QLineEdit()
            edit.setText(str(element.attrs.get(key, "")))
            layout.addRow(f"{key}:", edit)
            fields[key] = edit

        # --- Text Color Override Color Picker ---
        # Only show for widgets that support text color
        text_color_supported = any(
            k in element.attrs for k in ["textColor", "textColorOverride", "label", "text"]
        )
        if text_color_supported:
            color_layout = QHBoxLayout()
            color_edit = QLineEdit()
            color_edit.setPlaceholderText("#RRGGBB or #AARRGGBB")
            color_edit.setText(str(element.attrs.get("textColorOverride") or ""))
            color_btn = QPushButton("Text Color…")
            color_layout.addWidget(color_edit)
            color_layout.addWidget(color_btn)
            layout.addRow("Text Color Override", color_layout)

            def pick_text_color():
                current = color_edit.text().strip()
                if current:
                    try:
                        color = QColor(current)
                    except Exception:
                        color = QColor("#000000")
                else:
                    color = QColor("#000000")
                color = QColorDialog.getColor(color, self, "Select Text Color")
                if color.isValid():
                    # Use ARGB hex if alpha < 255, else RGB hex
                    if color.alpha() < 255:
                        hex_str = color.name(QColor.HexArgb)
                    else:
                        hex_str = color.name(QColor.HexRgb)
                    color_edit.setText(hex_str)
                    element.attrs["textColorOverride"] = hex_str.lstrip("#")
                    if hasattr(element, "update"):
                        element.update()
                    if hasattr(element.parent(), "update_xml_from_canvas"):
                        element.parent().update_xml_from_canvas()
            color_btn.clicked.connect(pick_text_color)

            def on_color_edit():
                val = color_edit.text().strip()
                if val == "":
                    element.attrs["textColorOverride"] = None
                else:
                    element.attrs["textColorOverride"] = val.lstrip("#")
                if hasattr(element, "update"):
                    element.update()
                if hasattr(element.parent(), "update_xml_from_canvas"):
                    element.parent().update_xml_from_canvas()
            color_edit.editingFinished.connect(on_color_edit)

            # --- Text Size Override ---
            from PyQt5.QtWidgets import QSpinBox
            text_size_spin = QSpinBox()
            text_size_spin.setRange(6, 96)
            text_size_spin.setValue(int(element.attrs.get("textSize", 14)))
            layout.addRow("Text Size", text_size_spin)
            def on_text_size_change(val):
                element.attrs["textSize"] = val
                if hasattr(element, "update"):
                    element.update()
                if hasattr(element.parent(), "update_xml_from_canvas"):
                    element.parent().update_xml_from_canvas()
            text_size_spin.valueChanged.connect(on_text_size_change)
        def on_attr_change():
            try:
                import commands
                main_window = self.main_window if hasattr(self, "main_window") else None
                undo_stack = main_window.undo_stack if main_window and hasattr(main_window, "undo_stack") else None
                for key, edit in fields.items():
                    old_val = element.attrs.get(key, "")
                    val = edit.text()
                    if key in ["x", "y", "width", "height"]:
                        try:
                            val_int = int(val)
                        except Exception:
                            from PyQt5.QtWidgets import QMessageBox
                            QMessageBox.warning(self, "Invalid Value", f"{key} must be an integer.")
                            # Revert to previous value
                            edit.blockSignals(True)
                            edit.setText(str(old_val))
                            edit.blockSignals(False)
                            continue
                        val = val_int
                    if val != old_val and undo_stack:
                        # Push an EditPropertyCommand for this property change
                        def setter(v, k=key, elem=element):
                            elem.attrs[k] = v
                            if hasattr(elem, "update_from_attrs"):
                                elem.update_from_attrs()
                        cmd = commands.EditPropertyCommand(
                            element, key, old_val, val, setter=setter, description=f"Edit {key}"
                        )
                        undo_stack.push(cmd)
                    else:
                        element.attrs[key] = val
                        if hasattr(element, "update_from_attrs"):
                            element.update_from_attrs()
                self.update_xml_from_canvas()
                # Do NOT refresh the Properties Panel here to avoid deleting widgets during signal handling
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Edit Error", f"Failed to update element:\n{e}")
        # Only connect editingFinished after all QLineEdits are set up
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
            import commands
            if self.main_window and hasattr(self.main_window, "undo_stack"):
                cmd = commands.DeleteWidgetCommand(self, self.selected_element)
                self.main_window.undo_stack.push(cmd)
            else:
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
            if widget_class.__name__ == "KnobWidget":
                knob_height = 100
                max_y = max(0, self.height() - knob_height)
                attrs["y"] = min(attrs["y"], max_y)
            import commands
            if self.main_window and hasattr(self.main_window, "undo_stack"):
                cmd = commands.AddWidgetCommand(self, widget_class, attrs, select_after=True)
                self.main_window.undo_stack.push(cmd)
            else:
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
            if widget_class.__name__ == "KnobWidget":
                knob_height = 100
                max_y = max(0, self.height() - knob_height)
                attrs["y"] = min(attrs["y"], max_y)
            import commands
            if self.main_window and hasattr(self.main_window, "undo_stack"):
                cmd = commands.AddWidgetCommand(self, widget_class, attrs, select_after=True)
                self.main_window.undo_stack.push(cmd)
            else:
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
        Ensures output matches Decent Sampler's formatting and structure.
        """
        if not self.main_window or not hasattr(self.main_window, "xml_editor") or not hasattr(self.main_window, "xml_root"):
            return
        import xml.etree.ElementTree as ET

        # Use the in-memory XML root as the source of truth
        root = self.main_window.xml_root
        if root is None:
            return

        # Find or create the <ui> element
        ui_elem = root.find(".//ui")
        if ui_elem is None:
            ui_elem = ET.SubElement(root, "ui", {"width": "812", "height": "375"})

        # Remove only widget elements, not non-widget children like <keyboard>
        widget_tags = {"knob", "slider", "button", "menu", "label", "labeled-knob", "control"}
        for child in list(ui_elem):
            if child.tag.lower() in widget_tags:
                ui_elem.remove(child)

        # Add current canvas elements as XML children
        for elem in self.elements:
            widget_el = ET.SubElement(ui_elem, elem.attrs["type"].lower())
            # Order attributes: x, y, width, height, label, then others alphabetically
            attr_keys = ["x", "y", "width", "height", "label"]
            attr_keys += sorted([k for k in elem.attrs if k not in attr_keys and k != "type"])
            for k in attr_keys:
                if k == "textColorOverride":
                    # Write as textColor if set, skip writing textColorOverride as its own attribute
                    val = elem.attrs.get("textColorOverride")
                    if val:
                        widget_el.set("textColor", str(val))
                    continue
                if k == "textColor":
                    # Only write textColor if textColorOverride is not set
                    if elem.attrs.get("textColorOverride"):
                        continue
                if k in elem.attrs and k != "type":
                    widget_el.set(k, str(elem.attrs[k]))

        # Pretty-print function for ElementTree (in-place)
        def indent(elem, level=0):
            i = "\n" + level * "  "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "  "
                for child in elem:
                    indent(child, level + 1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i

        indent(root)

        # Write the updated XML back to the xml_editor with declaration and pretty-printing
        import io
        buf = io.BytesIO()
        tree = ET.ElementTree(root)
        tree.write(buf, encoding="utf-8", xml_declaration=True)
        xml_str = buf.getvalue().decode("utf-8")
        self.main_window.xml_editor.setPlainText(xml_str)

        # Ensure the in-memory XML root is always in sync with the editor
        try:
            new_root = ET.fromstring(xml_str)
            self.main_window.xml_root = new_root
        except Exception as e:
            print(f"[update_xml_from_canvas] Failed to re-parse XML: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        out_of_bounds = []
        tolerance = 10  # Allow up to 10px out of bounds before warning
        for elem in self.elements:
            # Only check elements with attrs
            if not hasattr(elem, "attrs"):
                continue
            x, y, w, h = elem.x(), elem.y(), elem.width(), elem.height()
            if (
                x + w > self.width() + tolerance
                or y + h > self.height() + tolerance
                or x < -tolerance
                or y < -tolerance
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
