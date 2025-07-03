from PyQt5.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QSlider, QHBoxLayout, QSpinBox, QLabel
from PyQt5.QtCore import Qt

class GroupPropertiesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QHBoxLayout, QSpacerItem, QSizePolicy

        main_layout = QVBoxLayout()
        adsr_layout = QFormLayout()
        self.attack_spin = QDoubleSpinBox()
        self.attack_spin.setRange(0.0, 10.0)
        self.attack_spin.setSingleStep(0.01)
        self.attack_spin.setDecimals(3)
        self.decay_spin = QDoubleSpinBox()
        self.decay_spin.setRange(0.0, 10.0)
        self.decay_spin.setSingleStep(0.01)
        self.decay_spin.setDecimals(3)
        self.sustain_spin = QDoubleSpinBox()
        self.sustain_spin.setRange(0.0, 1.0)
        self.sustain_spin.setSingleStep(0.01)
        self.sustain_spin.setDecimals(3)
        self.release_spin = QDoubleSpinBox()
        self.release_spin.setRange(0.0, 10.0)
        self.release_spin.setSingleStep(0.01)
        self.release_spin.setDecimals(3)
        adsr_layout.addRow("Attack", self.attack_spin)
        adsr_layout.addRow("Decay", self.decay_spin)
        adsr_layout.addRow("Sustain", self.sustain_spin)
        adsr_layout.addRow("Release", self.release_spin)
        main_layout.addLayout(adsr_layout)

        # Velocity Map section
        vel_section = QVBoxLayout()
        vel_section.addWidget(QLabel("Velocity Map"))
        vel_layout = QHBoxLayout()
        self.lo_vel_label = QLabel("Low Velocity")
        self.lo_vel_slider = QSlider(Qt.Horizontal)
        self.lo_vel_slider.setRange(1, 127)
        self.lo_vel_slider.setValue(1)
        self.lo_vel_spin = QSpinBox()
        self.lo_vel_spin.setRange(1, 127)
        self.lo_vel_spin.setValue(1)
        self.hi_vel_label = QLabel("High Velocity")
        self.hi_vel_slider = QSlider(Qt.Horizontal)
        self.hi_vel_slider.setRange(1, 127)
        self.hi_vel_slider.setValue(127)
        self.hi_vel_spin = QSpinBox()
        self.hi_vel_spin.setRange(1, 127)
        self.hi_vel_spin.setValue(127)
        vel_layout.addWidget(self.lo_vel_label)
        vel_layout.addWidget(self.lo_vel_slider)
        vel_layout.addWidget(self.lo_vel_spin)
        vel_layout.addSpacing(10)
        vel_layout.addWidget(self.hi_vel_label)
        vel_layout.addWidget(self.hi_vel_slider)
        vel_layout.addWidget(self.hi_vel_spin)
        vel_section.addLayout(vel_layout)
        main_layout.addLayout(vel_section)

        # Add stretch to push everything up and avoid cut-off
        main_layout.addStretch()
        self.setLayout(main_layout)

        self.lo_vel_slider.valueChanged.connect(self.lo_vel_spin.setValue)
        self.lo_vel_spin.valueChanged.connect(self.lo_vel_slider.setValue)
        self.hi_vel_slider.valueChanged.connect(self.hi_vel_spin.setValue)
        self.hi_vel_spin.valueChanged.connect(self.hi_vel_slider.setValue)
        def clamp_lo(val):
            if val > self.hi_vel_slider.value():
                self.hi_vel_slider.setValue(val)
        def clamp_hi(val):
            if val < self.lo_vel_slider.value():
                self.lo_vel_slider.setValue(val)
        self.lo_vel_slider.valueChanged.connect(clamp_lo)
        self.lo_vel_spin.valueChanged.connect(clamp_lo)
        self.hi_vel_slider.valueChanged.connect(clamp_hi)
        self.hi_vel_spin.valueChanged.connect(clamp_hi)

    def set_adsr(self, attack, decay, sustain, release):
        self.attack_spin.setValue(attack)
        self.decay_spin.setValue(decay)
        self.sustain_spin.setValue(sustain)
        self.release_spin.setValue(release)

    def get_adsr(self):
        return (
            self.attack_spin.value(),
            self.decay_spin.value(),
            self.sustain_spin.value(),
            self.release_spin.value()
        )

    def set_velocity_range(self, lo, hi):
        self.lo_vel_slider.setValue(lo)
        self.hi_vel_slider.setValue(hi)

    def get_velocity_range(self):
        return self.lo_vel_slider.value(), self.hi_vel_slider.value()

    def set_buses(self, bus_names):
        # Stub: Accepts a list of bus names for compatibility with MainWindow.
        # Extend this method if bus routing controls are added to this panel.
        pass
