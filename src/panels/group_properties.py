from PyQt5.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QSlider, QHBoxLayout, QSpinBox, QLabel
from PyQt5.QtCore import Qt
from views.panels.ui_widgets import ADSRParameterCard

class GroupPropertiesWidget(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QHBoxLayout, QSpacerItem, QSizePolicy

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        # Modular ADSR section (now in a group box for clarity)
        from PyQt5.QtWidgets import QGroupBox
        adsr_group = QGroupBox("ADSR Envelope")
        adsr_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 8px; }")
        adsr_group_layout = QHBoxLayout()
        adsr_group_layout.setContentsMargins(12, 12, 12, 12)
        adsr_group_layout.setSpacing(16)
        self.attack_card = ADSRParameterCard("Attack", value=0.0, value_range=(0.0, 10.0), value_step=0.01, value_decimals=3)
        self.decay_card = ADSRParameterCard("Decay", value=0.0, value_range=(0.0, 10.0), value_step=0.01, value_decimals=3)
        self.sustain_card = ADSRParameterCard("Sustain", value=1.0, value_range=(0.0, 1.0), value_step=0.01, value_decimals=3)
        self.release_card = ADSRParameterCard("Release", value=0.0, value_range=(0.0, 10.0), value_step=0.01, value_decimals=3)
        # Connect toggles and advanced changed
        self.attack_card.enable_cb.toggled.connect(lambda _: self.update_adsr_elements())
        self.decay_card.enable_cb.toggled.connect(lambda _: self.update_adsr_elements())
        self.sustain_card.enable_cb.toggled.connect(lambda _: self.update_adsr_elements())
        self.release_card.enable_cb.toggled.connect(lambda _: self.update_adsr_elements())
        self.attack_card.on_advanced_changed = lambda _: self.update_adsr_elements()
        self.decay_card.on_advanced_changed = lambda _: self.update_adsr_elements()
        self.sustain_card.on_advanced_changed = lambda _: self.update_adsr_elements()
        self.release_card.on_advanced_changed = lambda _: self.update_adsr_elements()
        adsr_group_layout.addStretch()
        adsr_group_layout.addWidget(self.attack_card)
        adsr_group_layout.addStretch()
        adsr_group_layout.addWidget(self.decay_card)
        adsr_group_layout.addStretch()
        adsr_group_layout.addWidget(self.sustain_card)
        adsr_group_layout.addStretch()
        adsr_group_layout.addWidget(self.release_card)
        adsr_group_layout.addStretch()
        adsr_group.setLayout(adsr_group_layout)
        main_layout.addWidget(adsr_group)

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

        def lo_vel_setter(val): self.lo_vel_slider.setValue(val)
        def hi_vel_setter(val): self.hi_vel_slider.setValue(val)

        def lo_vel_changed(val):
            old = self._lo_vel_last
            push_edit_command("lo_velocity", old, val, lo_vel_setter)
            self._lo_vel_last = val
        def hi_vel_changed(val):
            old = self._hi_vel_last
            push_edit_command("hi_velocity", old, val, hi_vel_setter)
            self._hi_vel_last = val

        self.lo_vel_slider.valueChanged.connect(lo_vel_changed)
        self.hi_vel_slider.valueChanged.connect(hi_vel_changed)

    def set_adsr(self, attack, decay, sustain, release):
        self.attack_card.value_spin.setValue(attack)
        self.decay_card.value_spin.setValue(decay)
        self.sustain_card.value_spin.setValue(sustain)
        self.release_card.value_spin.setValue(release)

    def get_adsr(self):
        return (
            self.attack_card.value_spin.value(),
            self.decay_card.value_spin.value(),
            self.sustain_card.value_spin.value(),
            self.release_card.value_spin.value()
        )

    def update_adsr_elements(self):
        """
        Update preset.ui.elements to reflect enabled ADSR cards and their advanced options.
        
        NOTE: This panel has exclusive ownership of ADSR UI elements creation.
        The Project Properties panel filters out ADSR controls to avoid duplication.
        This ensures a clear separation of concerns:
        - Group Properties: Manages ADSR envelope values and UI controls
        - Project Properties: Manages effects controls only
        """
        mw = self.main_window
        if not hasattr(mw, "preset") or not hasattr(mw.preset, "ui") or not hasattr(mw.preset.ui, "elements"):
            return
        elements = mw.preset.ui.elements
        # Remove all existing ADSR elements
        adsr_names = ["Attack", "Decay", "Sustain", "Release"]
        elements[:] = [el for el in elements if getattr(el, "label", None) not in adsr_names]
        # Add enabled ADSR cards
        for card in [self.attack_card, self.decay_card, self.sustain_card, self.release_card]:
            if card.enable_cb.isChecked():
                label = card.param_name
                x = getattr(card, "_adsr_x", 40)
                y = getattr(card, "_adsr_y", 100)
                width = getattr(card, "_adsr_width", 64)
                height = getattr(card, "_adsr_height", 64)
                widget_type = getattr(card, "_adsr_type", "Knob")
                orientation = getattr(card, "_adsr_orientation", "horizontal") if widget_type == "Slider" else None
                text_size = getattr(card, "_adsr_text_size", 16)
                value = card.value_spin.value()
                tag_value = "labeled-slider" if widget_type == "Slider" else "labeled-knob"
                # DecentSampler-specific: min/max/type per parameter
                param_map = {
                    "Attack": ("ENV_ATTACK", 0.0, 10.0),
                    "Decay": ("ENV_DECAY", 0.0, 25.0),
                    "Sustain": ("ENV_SUSTAIN", 0.0, 1.0),
                    "Release": ("ENV_RELEASE", 0.0, 25.0)
                }
                param_name, min_val, max_val = param_map[label]
                # Use float for all ADSR
                value_type = "float"
                # Set up UIElement with all required DecentSampler attributes
                try:
                    from model import UIElement as RealUIElement
                    el = RealUIElement(
                        x=x,
                        y=y,
                        width=width,
                        height=height,
                        label=label,
                        skin=None,
                        tag=tag_value,
                        widget_type=widget_type,
                        target=param_name,
                        min_val=min_val,
                        max_val=max_val,
                        bindings=[{
                            "type": "amp",
                            "level": "instrument",
                            "position": "0",
                            "parameter": param_name
                        }],
                        options=[],
                        midi_cc=None,
                        orientation=orientation
                    )
                except Exception:
                    el = type("UIElement", (), {})()
                    el.x = x
                    el.y = y
                    el.width = width
                    el.height = height
                    el.label = label
                    el.skin = None
                    el.tag = tag_value
                    el.widget_type = widget_type
                    el.target = param_name
                    el.min_val = min_val
                    el.max_val = max_val
                    el.bindings = [{
                        "type": "amp",
                        "level": "instrument",
                        "position": "0",
                        "parameter": param_name
                    }]
                    el.options = []
                    el.midi_cc = None
                    el.orientation = orientation
                el.text_size = text_size
                el.value = value
                el.effect_type = None
                el.parameter = None
                el.min = min_val
                el.max = max_val
                el.default = value
                el.type = value_type
                # Add DecentSampler visual attributes (defaults, can be customized)
                el.textColor = "FF000000"
                el.textSize = str(text_size)
                el.trackForegroundColor = "CC000000"
                el.trackBackgroundColor = "66999999"
                elements.append(el)
        # Update preview
        if hasattr(mw, "preview_canvas"):
            mw.preview_canvas.set_preset(mw.preset, "")

    def set_velocity_range(self, lo, hi):
        self.lo_vel_slider.setValue(lo)
        self.hi_vel_slider.setValue(hi)

    def get_velocity_range(self):
        return self.lo_vel_slider.value(), self.hi_vel_slider.value()

    def set_buses(self, bus_names):
        # Stub: Accepts a list of bus names for compatibility with MainWindow.
        # Extend this method if bus routing controls are added to this panel.
        pass
