from PyQt5.QtWidgets import QUndoCommand

class AddWidgetCommand(QUndoCommand):
    """
    Command to add a widget to a VisualCanvas.
    """
    def __init__(self, canvas, widget_class, attrs, select_after=True, description="Add Widget"):
        super().__init__(description)
        self.canvas = canvas
        self.widget_class = widget_class
        self.attrs = dict(attrs)
        self.widget = None
        self.select_after = select_after

    def redo(self):
        if self.widget is None:
            # Create the widget
            if self.widget_class.__name__ == "DraggableElementLabel":
                self.widget = self.widget_class(self.attrs.get("type", "Unknown"), self.canvas)
            else:
                self.widget = self.widget_class(self.canvas)
            if hasattr(self.widget, "attrs"):
                self.widget.attrs.update(self.attrs)
                if hasattr(self.widget, "update_from_attrs"):
                    self.widget.update_from_attrs()
            self.widget.move(self.attrs.get("x", 0), self.attrs.get("y", 0))
            self.widget.show()
        else:
            self.widget.setParent(self.canvas)
            self.widget.show()
        self.canvas.elements.append(self.widget)
        if self.select_after and hasattr(self.canvas, "select_element"):
            self.canvas.select_element(self.widget)
        if hasattr(self.canvas, "update_xml_from_canvas"):
            self.canvas.update_xml_from_canvas()

    def undo(self):
        if self.widget in self.canvas.elements:
            self.canvas.elements.remove(self.widget)
        self.widget.setParent(None)
        if hasattr(self.canvas, "update_xml_from_canvas"):
            self.canvas.update_xml_from_canvas()

class DeleteWidgetCommand(QUndoCommand):
    """
    Command to delete a widget from a VisualCanvas.
    """
    def __init__(self, canvas, widget, description="Delete Widget"):
        super().__init__(description)
        self.canvas = canvas
        self.widget = widget
        self.attrs = dict(widget.attrs) if hasattr(widget, "attrs") else {}
        self.widget_class = type(widget)
        self.index = self.canvas.elements.index(widget) if widget in self.canvas.elements else -1

    def redo(self):
        if self.widget in self.canvas.elements:
            self.canvas.elements.remove(self.widget)
        self.widget.setParent(None)
        if hasattr(self.canvas, "update_xml_from_canvas"):
            self.canvas.update_xml_from_canvas()

    def undo(self):
        if self.index < 0:
            self.canvas.elements.append(self.widget)
        else:
            self.canvas.elements.insert(self.index, self.widget)
        self.widget.setParent(self.canvas)
        self.widget.show()
        if hasattr(self.widget, "attrs"):
            self.widget.attrs.update(self.attrs)
            if hasattr(self.widget, "update_from_attrs"):
                self.widget.update_from_attrs()
        if hasattr(self.canvas, "update_xml_from_canvas"):
            self.canvas.update_xml_from_canvas()

class MoveWidgetCommand(QUndoCommand):
    """
    Command to move a widget on a VisualCanvas.
    """
    def __init__(self, widget, old_pos, new_pos, description="Move Widget"):
        super().__init__(description)
        self.widget = widget
        self.old_pos = old_pos
        self.new_pos = new_pos

    def redo(self):
        self.widget.move(*self.new_pos)
        if hasattr(self.widget, "attrs"):
            self.widget.attrs["x"], self.widget.attrs["y"] = self.new_pos
        if hasattr(self.widget.parent(), "update_xml_from_canvas"):
            self.widget.parent().update_xml_from_canvas()

    def undo(self):
        self.widget.move(*self.old_pos)
        if hasattr(self.widget, "attrs"):
            self.widget.attrs["x"], self.widget.attrs["y"] = self.old_pos
        if hasattr(self.widget.parent(), "update_xml_from_canvas"):
            self.widget.parent().update_xml_from_canvas()

class ResizeWidgetCommand(QUndoCommand):
    """
    Command to resize a widget on a VisualCanvas.
    """
    def __init__(self, widget, old_geom, new_geom, description="Resize Widget"):
        super().__init__(description)
        self.widget = widget
        self.old_geom = old_geom  # (x, y, w, h)
        self.new_geom = new_geom

    def redo(self):
        self.widget.setGeometry(*self.new_geom)
        if hasattr(self.widget, "attrs"):
            self.widget.attrs["x"], self.widget.attrs["y"], self.widget.attrs["width"], self.widget.attrs["height"] = self.new_geom
        if hasattr(self.widget.parent(), "update_xml_from_canvas"):
            self.widget.parent().update_xml_from_canvas()

    def undo(self):
        self.widget.setGeometry(*self.old_geom)
        if hasattr(self.widget, "attrs"):
            self.widget.attrs["x"], self.widget.attrs["y"], self.widget.attrs["width"], self.widget.attrs["height"] = self.old_geom
        if hasattr(self.widget.parent(), "update_xml_from_canvas"):
            self.widget.parent().update_xml_from_canvas()

class EditPropertyCommand(QUndoCommand):
    """
    Command to edit a property (attribute) of a widget or panel.
    """
    def __init__(self, target, prop_name, old_value, new_value, setter=None, description="Edit Property"):
        super().__init__(description)
        self.target = target
        self.prop_name = prop_name
        self.old_value = old_value
        self.new_value = new_value
        self.setter = setter  # Optional: function to set the property

    def redo(self):
        if self.setter:
            self.setter(self.new_value)
        else:
            setattr(self.target, self.prop_name, self.new_value)
        if hasattr(self.target, "update_from_attrs"):
            self.target.update_from_attrs()
        if hasattr(self.target, "parent") and hasattr(self.target.parent(), "update_xml_from_canvas"):
            self.target.parent().update_xml_from_canvas()

    def undo(self):
        if self.setter:
            self.setter(self.old_value)
        else:
            setattr(self.target, self.prop_name, self.old_value)
        if hasattr(self.target, "update_from_attrs"):
            self.target.update_from_attrs()
        if hasattr(self.target, "parent") and hasattr(self.target.parent(), "update_xml_from_canvas"):
            self.target.parent().update_xml_from_canvas()

# Stubs for other commands
class ImportSamplesCommand(QUndoCommand):
    pass

class ZoneMappingCommand(QUndoCommand):
    pass

class EnvelopeEditCommand(QUndoCommand):
    pass

class RoutingCommand(QUndoCommand):
    pass

class XmlEditCommand(QUndoCommand):
    """
    Command to edit the XML in the XML editor and sync canvases.
    """
    def __init__(self, main_window, old_xml, new_xml, description="Edit XML"):
        super().__init__(description)
        self.main_window = main_window
        self.old_xml = old_xml
        self.new_xml = new_xml

    def redo(self):
        self._apply_xml(self.new_xml)

    def undo(self):
        self._apply_xml(self.old_xml)

    def _apply_xml(self, xml_text):
        if not self.main_window:
            return
        self.main_window.xml_editor.setPlainText(xml_text)
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(xml_text)
            self.main_window.xml_root = root
            ui_elem = root.find(".//ui")
            if ui_elem is not None:
                widget_tags = {"knob", "slider", "button", "menu", "label", "labeled-knob", "control"}
                tabs = [tab for tab in ui_elem if tab.tag == "tab"]
                if tabs:
                    tab_idx = self.main_window.tab_widget.currentIndex() if self.main_window.tab_widget.count() > 0 else 0
                    tab_elem = tabs[tab_idx] if tab_idx < len(tabs) else tabs[0]
                    widget_parent = tab_elem
                else:
                    widget_parent = ui_elem
                for i in range(self.main_window.tab_widget.count()):
                    canvas = self.main_window.tab_widget.widget(i)
                    for widget in list(canvas.elements):
                        widget.setParent(None)
                    canvas.elements.clear()
                    for widget_el in widget_parent:
                        if widget_el.tag.lower() not in widget_tags:
                            continue
                        try:
                            tag = widget_el.tag.lower()
                            attrs = dict(widget_el.attrib)
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
                            print(f"[XmlEditCommand] Failed to instantiate widget '{tag}': {e}")
        except Exception as e:
            print(f"[XmlEditCommand] Failed to parse XML: {e}")
