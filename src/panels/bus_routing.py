from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, QInputDialog, QLabel, QSpinBox, QSlider

class BusRoutingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.bus_list = QListWidget()
        self.layout.addWidget(QLabel("Buses"))
        self.layout.addWidget(self.bus_list)
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Bus")
        self.remove_btn = QPushButton("Remove Bus")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)
        self.add_btn.clicked.connect(self.add_bus)
        self.remove_btn.clicked.connect(self.remove_bus)

    def set_buses(self, bus_names):
        self.bus_list.clear()
        for name in bus_names:
            self.bus_list.addItem(name)

    def get_buses(self):
        return [self.bus_list.item(i).text() for i in range(self.bus_list.count())]

    def add_bus(self):
        name, ok = QInputDialog.getText(self, "Add Bus", "Bus name:")
        if ok and name and name not in self.get_buses():
            self.bus_list.addItem(name)

    def remove_bus(self):
        row = self.bus_list.currentRow()
        if row >= 0:
            self.bus_list.takeItem(row)
