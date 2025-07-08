from PyQt5.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QSlider, QHBoxLayout, QSpinBox, QLabel
from PyQt5.QtCore import Qt

class GroupPropertiesWidget(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QHBoxLayout, QSpacerItem, QSizePolicy

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        adsr_layout = QFormLayout()
        adsr_layout.setContentsMargins(0, 0, 0, 0)
        adsr_layout.setSpacing(8)
        self.attack_spin = QDoubleSpinBox()
        self.attack_spin.setRange(0.0, 10.0)
        self.attack_spin.setSingleStep(0.01)
        self.attack_spin.setDecimals(3)
        self.attack_spin.setToolTip("Attack time (seconds)")
        self.attack_spin.setAccessibleName("Attack SpinBox")
        self._attack_last = self.attack_spin.value()
        self.decay_spin = QDoubleSpinBox()
        self.decay_spin.setRange(0.0, 10.0)
        self.decay_spin.setSingleStep(0.01)
        self.decay_spin.setDecimals(3)
        self.decay_spin.setToolTip("Decay time (seconds)")
        self.decay_spin.setAccessibleName("Decay SpinBox")
        self._decay_last = self.decay_spin.value()
        self.sustain_spin = QDoubleSpinBox()
        self.sustain_spin.setRange(0.0, 1.0)
        self.sustain_spin.setSingleStep(0.01)
        self.sustain_spin.setDecimals(3)
        self.sustain_spin.setToolTip("Sustain level (0-1)")
        self.sustain_spin.setAccessibleName("Sustain SpinBox")
        self._sustain_last = self.sustain_spin.value()
        self.release_spin = QDoubleSpinBox()
        self.release_spin.setRange(0.0, 10.0)
        self.release_spin.setSingleStep(0.01)
        self.release_spin.setDecimals(3)
        self.release_spin.setToolTip("Release time (seconds)")
        self.release_spin.setAccessibleName("Release SpinBox")
        self._release_last = self.release_spin.value()
        adsr_layout.addRow("Attack", self.attack_spin)
        adsr_layout.addRow("Decay", self.decay_spin)
        adsr_layout.addRow("Sustain", self.sustain_spin)
        adsr_layout.addRow("Release", self.release_spin)
        main_layout.addLayout(adsr_layout)

        # Velocity Map section
        vel_section = QVBoxLayout()
        vel_section.setContentsMargins(0, 0, 0, 0)
        vel_section.setSpacing(8)
        vel_section.addWidget(QLabel("Velocity Map"))
        vel_layout = QHBoxLayout()
        vel_layout.setContentsMargins(0, 0, 0, 0)
        vel_layout.setSpacing(8)
        self.lo_vel_label = QLabel("Low Velocity")
        self.lo_vel_label.setToolTip("Lowest velocity for this group")
        self.lo_vel_label.setAccessibleName("Low Velocity Label")
        self.lo_vel_slider = QSlider(Qt.Horizontal)
        self.lo_vel_slider.setRange(1, 127)
        self.lo_vel_slider.setValue(1)
        self.lo_vel_slider.setToolTip("Adjust the lowest velocity for this group")
        self.lo_vel_slider.setAccessibleName("Low Velocity Slider")
        self.lo_vel_spin = QSpinBox()
        self.lo_vel_spin.setRange(1, 127)
        self.lo_vel_spin.setValue(1)
        self.lo_vel_spin.setToolTip("Set the lowest velocity for this group")
        self.lo_vel_spin.setAccessibleName("Low Velocity SpinBox")
        self.hi_vel_label = QLabel("High Velocity")
        self.hi_vel_label.setToolTip("Highest velocity for this group")
        self.hi_vel_label.setAccessibleName("High Velocity Label")
        self.hi_vel_slider = QSlider(Qt.Horizontal)
        self.hi_vel_slider.setRange(1, 127)
        self.hi_vel_slider.setValue(127)
        self.hi_vel_slider.setToolTip("Adjust the highest velocity for this group")
        self.hi_vel_slider.setAccessibleName("High Velocity Slider")
        self.hi_vel_spin = QSpinBox()
        self.hi_vel_spin.setRange(1, 127)
        self.hi_vel_spin.setValue(127)
        self.hi_vel_spin.setToolTip("Set the highest velocity for this group")
        self.hi_vel_spin.setAccessibleName("High Velocity SpinBox")
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
        self._lo_vel_last = self.lo_vel_slider.value()
        self._hi_vel_last = self.hi_vel_slider.value()
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

        # --- Undo/Redo for property changes ---
        def push_edit_command(prop, old, new, setter):
            main_window = self.main_window
            undo_stack = main_window.undo_stack if main_window and hasattr(main_window, "undo_stack") else None
            if undo_stack and old != new:
                import commands
                cmd = commands.EditPropertyCommand(self, prop, old, new, setter=setter, description=f"Edit {prop}")
                undo_stack.push(cmd)

        def attack_setter(val): self.attack_spin.setValue(val)
        def decay_setter(val): self.decay_spin.setValue(val)
        def sustain_setter(val): self.sustain_spin.setValue(val)
        def release_setter(val): self.release_spin.setValue(val)
        def lo_vel_setter(val): self.lo_vel_slider.setValue(val)
        def hi_vel_setter(val): self.hi_vel_slider.setValue(val)

        def attack_changed(val):
            old = self._attack_last
            push_edit_command("attack", old, val, attack_setter)
            self._attack_last = val
        def decay_changed(val):
            old = self._decay_last
            push_edit_command("decay", old, val, decay_setter)
            self._decay_last = val
        def sustain_changed(val):
            old = self._sustain_last
            push_edit_command("sustain", old, val, sustain_setter)
            self._sustain_last = val
        def release_changed(val):
            old = self._release_last
            push_edit_command("release", old, val, release_setter)
            self._release_last = val
        def lo_vel_changed(val):
            old = self._lo_vel_last
            push_edit_command("lo_velocity", old, val, lo_vel_setter)
            self._lo_vel_last = val
        def hi_vel_changed(val):
            old = self._hi_vel_last
            push_edit_command("hi_velocity", old, val, hi_vel_setter)
            self._hi_vel_last = val

        self.attack_spin.valueChanged.connect(attack_changed)
        self.decay_spin.valueChanged.connect(decay_changed)
        self.sustain_spin.valueChanged.connect(sustain_changed)
        self.release_spin.valueChanged.connect(release_changed)
        self.lo_vel_slider.valueChanged.connect(lo_vel_changed)
        self.hi_vel_slider.valueChanged.connect(hi_vel_changed)

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
