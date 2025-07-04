from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from panels.project_properties import ProjectPropertiesWidget

class ProjectPropertiesDialog(QDialog):
    def __init__(self, parent=None, main_window=None, initial_properties=None):
        super().__init__(parent)
        self.setWindowTitle("Project Properties")
        self.setModal(True)
        self.main_window = main_window

        self.widget = ProjectPropertiesWidget(main_window=main_window)
        if initial_properties:
            self.widget.set_properties(initial_properties)

        layout = QVBoxLayout()
        layout.addWidget(self.widget)

        # Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.apply_button.clicked.connect(self.apply)
        self.ok_button.clicked.connect(self.ok)
        self.cancel_button.clicked.connect(self.cancel)

        self._applied = False

    def get_properties(self):
        return self.widget.get_properties()

    def apply(self):
        if self.main_window:
            self.main_window.apply_project_properties(self.get_properties())
        self._applied = True

    def ok(self):
        self.apply()
        self.accept()

    def cancel(self):
        self.reject()
