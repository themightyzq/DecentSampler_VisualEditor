from PyQt5.QtWidgets import QUndoCommand

class GlobalOptionEditCommand(QUndoCommand):
    def __init__(self, preset, option_name, old_value, new_value, update_callback=None):
        super().__init__(f"Edit {option_name}")
        self.preset = preset
        self.option_name = option_name
        self.old_value = old_value
        self.new_value = new_value
        self.update_callback = update_callback  # function to call after change (e.g., to refresh UI)

    def redo(self):
        setattr(self.preset, self.option_name, self.new_value)
        if self.update_callback:
            self.update_callback()

    def undo(self):
        setattr(self.preset, self.option_name, self.old_value)
        if self.update_callback:
            self.update_callback()

class SampleAutoMapCommand(QUndoCommand):
    def __init__(self, preset, old_mappings, new_mappings, update_callback=None):
        super().__init__("Auto-Map Folder")
        self.preset = preset
        self.old_mappings = old_mappings
        self.new_mappings = new_mappings
        self.update_callback = update_callback  # function to call after change (e.g., to refresh UI)

    def redo(self):
        self.preset.mappings = list(self.new_mappings)
        if self.update_callback:
            self.update_callback()

    def undo(self):
        self.preset.mappings = list(self.old_mappings)
        if self.update_callback:
            self.update_callback()
